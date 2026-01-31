"""
Backend OFFLINE do edycji regionów Anvil (.mca) dla Minecraft 1.7.10
Używa nbtlib do parsowania NBT - bez amulet, bez PyAnvilEditor
"""
import os
import shutil
import struct
import zlib
import logging
from pathlib import Path
from typing import Dict, Optional, Any, List, Tuple
from dataclasses import dataclass
from io import BytesIO

try:
    import nbtlib
except ImportError:
    raise ImportError("nbtlib nie jest zainstalowany. Uruchom: pip install nbtlib")

from ...world.types import Pos, ChunkPos, RegionPos, EditOperation

logger = logging.getLogger(__name__)


class AnvilBackend:
    """
    Backend do edycji światów Minecraft 1.7.10 OFFLINE.
    Bezpośrednio modyfikuje pliki .mca używając nbtlib.
    """
    
    SECTOR_SIZE = 4096
    
    def __init__(self, world_path: str, backup: bool = True):
        self.world_path = Path(world_path)
        self.region_path = self.world_path / "region"
        self.backup = backup
        
        if not self.region_path.exists():
            raise ValueError(f"Nie znaleziono katalogu region: {self.region_path}")
        
        # Cache regionów (ścieżka -> dane)
        self._region_cache: Dict[Path, bytearray] = {}
        self._modified_regions: set = set()
        
        # Backup
        self._backup_dir: Optional[Path] = None
        self._backed_up_regions: set = set()
    
    def _backup_region(self, region_file: Path):
        """Tworzy backup regionu (tylko jeśli plik istnieje)"""
        if not self.backup or region_file in self._backed_up_regions:
            return
        
        # Nie backupuj plików które nie istnieją (zostaną utworzone)
        if not region_file.exists():
            return
        
        if self._backup_dir is None:
            import time
            self._backup_dir = self.world_path / "backups" / f"edit_{int(time.time())}"
            self._backup_dir.mkdir(parents=True, exist_ok=True)
        
        backup_file = self._backup_dir / region_file.name
        shutil.copy2(region_file, backup_file)
        self._backed_up_regions.add(region_file)
        logger.info(f"Backup: {region_file.name} -> {backup_file}")
    
    def _get_region_file(self, region_pos: RegionPos) -> Path:
        """Zwraca ścieżkę do pliku regionu"""
        return self.region_path / f"r.{region_pos.x}.{region_pos.z}.mca"
    
    def _load_region(self, region_file: Path) -> bytearray:
        """Ładuje plik regionu do pamięci"""
        if region_file not in self._region_cache:
            if region_file.exists():
                with open(region_file, 'rb') as f:
                    self._region_cache[region_file] = bytearray(f.read())
            else:
                # Utwórz pusty region
                self._region_cache[region_file] = bytearray(self.SECTOR_SIZE * 2)  # Header + puste
        return self._region_cache[region_file]
    
    def _get_chunk_location(self, region_data: bytearray, local_x: int, local_z: int) -> Tuple[int, int]:
        """Zwraca lokalizację chunka w regionie (offset, rozmiar w sektorach)"""
        index = local_x + local_z * 32
        offset = index * 4
        
        if offset + 4 > len(region_data):
            return (0, 0)
        
        data = region_data[offset:offset + 4]
        sector_offset = ((data[0] << 16) | (data[1] << 8) | data[2])
        sector_count = data[3]
        
        return (sector_offset, sector_count)
    
    def _set_chunk_location(self, region_data: bytearray, local_x: int, local_z: int, 
                            sector_offset: int, sector_count: int):
        """Ustawia lokalizację chunka w nagłówku regionu"""
        index = local_x + local_z * 32
        offset = index * 4
        
        # Zapewnij że mamy wystarczająco dużo danych
        while len(region_data) < offset + 4:
            region_data.extend(b'\x00' * self.SECTOR_SIZE)
        
        region_data[offset] = (sector_offset >> 16) & 0xFF
        region_data[offset + 1] = (sector_offset >> 8) & 0xFF
        region_data[offset + 2] = sector_offset & 0xFF
        region_data[offset + 3] = sector_count
    
    def _read_chunk_nbt(self, region_data: bytearray, local_x: int, local_z: int) -> Optional[nbtlib.Compound]:
        """Odczytuje NBT chunka z regionu"""
        sector_offset, sector_count = self._get_chunk_location(region_data, local_x, local_z)
        
        if sector_offset == 0:
            return None  # Chunk nie istnieje
        
        byte_offset = sector_offset * self.SECTOR_SIZE
        
        if byte_offset + 5 > len(region_data):
            return None
        
        # Długość danych (4 bajty) + typ kompresji (1 bajt)
        length = struct.unpack('>I', region_data[byte_offset:byte_offset + 4])[0]
        compression_type = region_data[byte_offset + 4]
        
        if byte_offset + 5 + length - 1 > len(region_data):
            return None
        
        compressed_data = region_data[byte_offset + 5:byte_offset + 5 + length - 1]
        
        try:
            if compression_type == 2:  # zlib
                data = zlib.decompress(compressed_data)
            elif compression_type == 1:  # gzip
                import gzip
                data = gzip.decompress(compressed_data)
            else:
                data = compressed_data
            
            # nbtlib 2.x wymaga ścieżki do pliku - użyj tymczasowego
            import tempfile
            import os
            with tempfile.NamedTemporaryFile(delete=False) as tmp:
                tmp.write(data)
                tmp_path = tmp.name
            
            try:
                nbt = nbtlib.load(tmp_path, byteorder='big')
                return nbt
            finally:
                os.unlink(tmp_path)
                
        except Exception as e:
            logger.warning(f"Błąd odczytu chunka ({local_x}, {local_z}): {e}")
            return None
    
    def _write_chunk_nbt(self, region_data: bytearray, local_x: int, local_z: int, 
                         nbt_data: nbtlib.Compound) -> bool:
        """Zapisuje NBT chunka do regionu"""
        # Serializuj NBT (nbtlib 2.x używa write)
        buffer = BytesIO()
        nbt_data.write(buffer, byteorder='big')
        nbt_bytes = buffer.getvalue()
        
        # Kompresja zlib
        compressed = zlib.compress(nbt_bytes)
        chunk_data = struct.pack('>I', len(compressed) + 1) + b'\x02' + compressed
        
        # Zaokrąglij do wielokrotności sektora
        padding = (self.SECTOR_SIZE - (len(chunk_data) % self.SECTOR_SIZE)) % self.SECTOR_SIZE
        chunk_data_padded = chunk_data + b'\x00' * padding
        new_sector_count = len(chunk_data_padded) // self.SECTOR_SIZE
        
        # Znajdź lub przydziel miejsce
        sector_offset, old_sector_count = self._get_chunk_location(region_data, local_x, local_z)
        
        if sector_offset == 0 or new_sector_count > old_sector_count:
            # Potrzebne nowe miejsce - dopisz na końcu
            sector_offset = len(region_data) // self.SECTOR_SIZE
            if len(region_data) % self.SECTOR_SIZE != 0:
                sector_offset += 1
        
        # Zapisz dane
        byte_offset = sector_offset * self.SECTOR_SIZE
        
        # Rozszerz bufor jeśli potrzeba
        end_offset = byte_offset + len(chunk_data_padded)
        if end_offset > len(region_data):
            region_data.extend(b'\x00' * (end_offset - len(region_data)))
        
        region_data[byte_offset:end_offset] = chunk_data_padded
        
        # Aktualizuj nagłówek
        self._set_chunk_location(region_data, local_x, local_z, sector_offset, new_sector_count)
        
        return True
    
    def _get_or_create_chunk(self, region_file: Path, local_x: int, local_z: int) -> nbtlib.Compound:
        """Pobiera lub tworzy nowy chunk (zawsze zwraca z 'Level' wrapper)"""
        region_data = self._load_region(region_file)
        
        nbt = self._read_chunk_nbt(region_data, local_x, local_z)
        if nbt is not None:
            # Sprawdź czy chunk ma poprawny format z 'Level'
            if 'Level' in nbt and 'xPos' in nbt['Level']:
                # Już ma poprawny format
                return nbt
            elif 'xPos' in nbt:
                # Bezpośredni format - opakuj w Level
                nbt = nbtlib.Compound({
                    'Level': nbt,
                    'DataVersion': nbtlib.Int(0)
                })
            return nbt
        
        # Utwórz nowy chunk
        chunk_x = ((region_file.stem.split('.')[1] if len(region_file.stem.split('.')) > 1 else '0')[1:] 
                   if region_file.stem.split('.')[1].startswith('r') else region_file.stem.split('.')[1])
        chunk_z = region_file.stem.split('.')[2] if len(region_file.stem.split('.')) > 2 else '0'
        
        # Parsuj współrzędne regionu
        rx = int(region_file.stem.split('.')[1])
        rz = int(region_file.stem.split('.')[2])
        
        global_x = rx * 32 + local_x
        global_z = rz * 32 + local_z
        
        # Pusty chunk
        nbt = nbtlib.Compound({
            'Level': nbtlib.Compound({
                'xPos': nbtlib.Int(global_x),
                'zPos': nbtlib.Int(global_z),
                'LastUpdate': nbtlib.Long(0),
                'TerrainPopulated': nbtlib.Byte(1),
                'Sections': nbtlib.List[nbtlib.Compound]([]),
                'Biomes': nbtlib.ByteArray([1] * 256),
                'Entities': nbtlib.List[nbtlib.Compound]([]),
                'TileEntities': nbtlib.List[nbtlib.Compound]([]),
            }),
            'DataVersion': nbtlib.Int(0)
        })
        
        return nbt
    
    def _get_level(self, chunk_nbt: nbtlib.Compound) -> nbtlib.Compound:
        """Pobiera Level z chunka (obsługuje dwa formaty)"""
        if 'Level' in chunk_nbt:
            return chunk_nbt['Level']
        return chunk_nbt
    
    def _get_section(self, chunk_nbt: nbtlib.Compound, y: int) -> Optional[nbtlib.Compound]:
        """Pobiera sekcję chunka lub None"""
        level = self._get_level(chunk_nbt)
        sections = level.get('Sections', [])
        
        for section in sections:
            if section.get('Y') == y:
                return section
        return None
    
    def _create_section(self, y: int) -> nbtlib.Compound:
        """Tworzy nową sekcję"""
        return nbtlib.Compound({
            'Y': nbtlib.Byte(y),
            'Blocks': nbtlib.ByteArray([0] * 4096),
            'Data': nbtlib.ByteArray([0] * 2048),
            'SkyLight': nbtlib.ByteArray([0xFF] * 2048),
            'BlockLight': nbtlib.ByteArray([0] * 2048),
        })
    
    def get_block(self, pos: Pos) -> Tuple[int, int]:
        """Zwraca (block_id, meta)"""
        chunk_pos = pos.chunk_pos()
        region_pos = chunk_pos.region_pos()
        region_file = self._get_region_file(region_pos)
        
        local_x, local_z = chunk_pos.local_region_pos()
        
        region_data = self._load_region(region_file)
        nbt = self._read_chunk_nbt(region_data, local_x, local_z)
        
        if nbt is None:
            return (0, 0)  # Air
        
        section = self._get_section(nbt, pos.section_y())
        if section is None:
            return (0, 0)
        
        local_x, local_y, local_z = pos.local_chunk_pos()
        local_y_section = local_y % 16  # Y w obrębie sekcji (0-15)
        index = local_y_section * 256 + local_z * 16 + local_x
        
        blocks = section.get('Blocks', [0] * 4096)
        data = section.get('Data', [0] * 2048)
        
        if index >= len(blocks):
            return (0, 0)
        
        block_id = blocks[index]
        meta = (data[index // 2] >> 4) if index % 2 == 1 else (data[index // 2] & 0x0F)
        
        return (block_id, meta)
    
    def set_block(self, pos: Pos, block_id: int, meta: int = 0):
        """Ustawia blok"""
        chunk_pos = pos.chunk_pos()
        region_pos = chunk_pos.region_pos()
        region_file = self._get_region_file(region_pos)
        
        # Backup
        self._backup_region(region_file)
        
        local_x, local_z = chunk_pos.local_region_pos()
        
        region_data = self._load_region(region_file)
        nbt = self._get_or_create_chunk(region_file, local_x, local_z)
        
        # Pobierz lub utwórz sekcję
        section_y = pos.section_y()
        section = self._get_section(nbt, section_y)
        
        if section is None:
            section = self._create_section(section_y)
            level = self._get_level(nbt)
            level['Sections'].append(section)
        
        local_x, local_y, local_z = pos.local_chunk_pos()
        local_y_section = local_y % 16  # Y w obrębie sekcji (0-15)
        index = local_y_section * 256 + local_z * 16 + local_x
        
        # Pobierz aktualne dane i stwórz nowe mutable array
        import numpy as np
        
        blocks = np.array(section['Blocks'], dtype=np.uint8).copy()
        data = np.array(section['Data'], dtype=np.uint8).copy()
        
        # Ustaw blok
        blocks[index] = block_id
        
        # Ustaw metadata (nibble per block)
        data_index = index // 2
        old_data = data[data_index]
        if index % 2 == 0:
            data[data_index] = (old_data & 0xF0) | (meta & 0x0F)
        else:
            data[data_index] = (old_data & 0x0F) | ((meta & 0x0F) << 4)
        
        # Zapisz z powrotem jako nbtlib arrays
        section['Blocks'] = nbtlib.ByteArray(blocks.tolist())
        section['Data'] = nbtlib.ByteArray(data.tolist())
        
        # Zapisz chunk
        self._write_chunk_nbt(region_data, local_x, local_z, nbt)
        self._modified_regions.add(region_file)
        
        logger.debug(f"set_block({pos}): {block_id}:{meta}")
    
    def get_tile_entity(self, pos: Pos) -> Optional[Dict[str, Any]]:
        """Zwraca TileEntity"""
        chunk_pos = pos.chunk_pos()
        region_pos = chunk_pos.region_pos()
        region_file = self._get_region_file(region_pos)
        
        local_x, local_z = chunk_pos.local_region_pos()
        
        region_data = self._load_region(region_file)
        nbt = self._read_chunk_nbt(region_data, local_x, local_z)
        
        if nbt is None:
            return None
        
        level = self._get_level(nbt)
        tile_entities = level.get('TileEntities', [])
        
        for te in tile_entities:
            if te.get('x') == pos.x and te.get('y') == pos.y and te.get('z') == pos.z:
                return dict(te)
        
        return None
    
    def set_tile_entity(self, pos: Pos, te_data: Dict[str, Any]):
        """Ustawia TileEntity"""
        chunk_pos = pos.chunk_pos()
        region_pos = chunk_pos.region_pos()
        region_file = self._get_region_file(region_pos)
        
        # Backup
        self._backup_region(region_file)
        
        local_x, local_z = chunk_pos.local_region_pos()
        
        region_data = self._load_region(region_file)
        nbt = self._get_or_create_chunk(region_file, local_x, local_z)
        
        level = self._get_level(nbt)
        if 'TileEntities' not in level:
            level['TileEntities'] = nbtlib.List[nbtlib.Compound]([])
        
        # Usuń istniejące TE na tej pozycji
        level['TileEntities'] = nbtlib.List[nbtlib.Compound]([
            te for te in level['TileEntities']
            if not (te.get('x') == pos.x and te.get('y') == pos.y and te.get('z') == pos.z)
        ])
        
        # Dodaj nowe TE - konwertuj na odpowiednie typy nbtlib
        te_nbt = nbtlib.Compound()
        for key, value in te_data.items():
            if key in ('x', 'y', 'z'):
                te_nbt[key] = nbtlib.Int(value)
            elif key == 'id':
                te_nbt[key] = nbtlib.String(value)
            elif key == 'Command':
                te_nbt[key] = nbtlib.String(value)
            elif key == 'CustomName':
                te_nbt[key] = nbtlib.String(value)
            elif key == 'TrackOutput':
                te_nbt[key] = nbtlib.Byte(value)
            else:
                # Domyślnie string dla innych pól
                te_nbt[key] = nbtlib.String(str(value))
        
        # Upewnij się że mamy współrzędne
        if 'x' not in te_nbt:
            te_nbt['x'] = nbtlib.Int(pos.x)
        if 'y' not in te_nbt:
            te_nbt['y'] = nbtlib.Int(pos.y)
        if 'z' not in te_nbt:
            te_nbt['z'] = nbtlib.Int(pos.z)
        
        level['TileEntities'].append(te_nbt)
        
        # Zapisz chunk
        self._write_chunk_nbt(region_data, local_x, local_z, nbt)
        self._modified_regions.add(region_file)
        
        logger.info(f"set_tile_entity({pos}): {te_data.get('id', 'unknown')}")
    
    def clear_tile_entity(self, pos: Pos):
        """Usuwa TileEntity"""
        chunk_pos = pos.chunk_pos()
        region_pos = chunk_pos.region_pos()
        region_file = self._get_region_file(region_pos)
        
        local_x, local_z = chunk_pos.local_region_pos()
        
        region_data = self._load_region(region_file)
        nbt = self._read_chunk_nbt(region_data, local_x, local_z)
        
        if nbt is None:
            return
        
        level = nbt.get('Level', {})
        if 'TileEntities' not in level:
            return
        
        level['TileEntities'] = nbtlib.List[nbtlib.Compound]([
            te for te in level['TileEntities']
            if not (te.get('x') == pos.x and te.get('y') == pos.y and te.get('z') == pos.z)
        ])
        
        self._write_chunk_nbt(region_data, local_x, local_z, nbt)
        self._modified_regions.add(region_file)
    
    def apply(self, operations: List[EditOperation]):
        """Stosuje listę operacji"""
        logger.info(f"Stosowanie {len(operations)} operacji...")
        for op in operations:
            self.set_block(op.pos, op.block_id, op.meta)
            if op.tile_entity:
                self.set_tile_entity(op.pos, op.tile_entity)
        logger.info(f"Zastosowano {len(operations)} operacji")
    
    def commit(self):
        """Zapisuje zmiany do plików"""
        logger.info("Zapisywanie zmian...")
        
        for region_file in self._modified_regions:
            if region_file in self._region_cache:
                with open(region_file, 'wb') as f:
                    f.write(self._region_cache[region_file])
                logger.info(f"Zapisano region: {region_file.name}")
        
        self._region_cache.clear()
        self._modified_regions.clear()
        
        logger.info("Zmiany zapisane")
    
    def rollback(self):
        """Przywraca backup"""
        if self._backup_dir and self._backup_dir.exists():
            logger.info("Przywracanie z backup...")
            for backup_file in self._backup_dir.glob("r.*.mca"):
                target = self.region_path / backup_file.name
                shutil.copy2(backup_file, target)
                logger.info(f"Przywrócono: {target.name}")
            logger.info("Przywracanie zakończone")
    
    def close(self):
        """Zamyka backend"""
        self._region_cache.clear()
        logger.info("Edytor zamknięty")
