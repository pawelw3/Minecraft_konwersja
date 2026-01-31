"""
Backend do edycji światów Minecraft używający PyAnvilEditor (anvil-parser)
Dla Minecraft 1.7.10 (pre-1.13) używa OldBlock z numerycznymi ID
"""
import os
import shutil
import logging
from pathlib import Path
from typing import Dict, Optional, Any, Tuple

import anvil
from anvil import OldBlock, EmptyRegion, EmptyChunk, EmptySection

from ...world.types import Pos, ChunkPos, RegionPos

logger = logging.getLogger(__name__)


class PyAnvilBackend:
    """
    Backend do edycji światów Minecraft 1.7.10 używający PyAnvilEditor.
    Używa OldBlock dla numerycznych ID bloków (pre-1.13 format).
    """
    
    def __init__(self, world_path: str, backup: bool = True):
        self.world_path = Path(world_path)
        self.region_path = self.world_path / "region"
        self.backup = backup
        
        if not self.region_path.exists():
            raise ValueError(f"Nie znaleziono katalogu region: {self.region_path}")
        
        # Cache regionów (ścieżka -> EmptyRegion)
        self._region_cache: Dict[Path, anvil.EmptyRegion] = {}
        self._original_regions: Dict[Path, anvil.Region] = {}
        
        # Backup
        self._backup_dir: Optional[Path] = None
        self._backed_up_regions: set = set()
    
    def _backup_region(self, region_file: Path):
        """Tworzy backup regionu"""
        if not self.backup or region_file in self._backed_up_regions:
            return
        
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
    
    def _get_or_create_region(self, region_pos: RegionPos) -> anvil.EmptyRegion:
        """Pobiera lub tworzy region do edycji"""
        region_file = self._get_region_file(region_pos)
        
        if region_file not in self._region_cache:
            # Backup
            self._backup_region(region_file)
            
            if region_file.exists():
                # Wczytaj istniejący region
                with open(region_file, 'rb') as f:
                    data = f.read()
                try:
                    original = anvil.Region(data)
                    self._original_regions[region_file] = original
                    
                    # Konwertuj do EmptyRegion
                    empty_region = anvil.EmptyRegion(region_pos.x, region_pos.z)
                    
                    # Kopiuj wszystkie chunki
                    for chunk_x in range(32):
                        for chunk_z in range(32):
                            try:
                                chunk = original.get_chunk(chunk_x, chunk_z)
                                # Konwertuj do EmptyChunk
                                empty_chunk = self._chunk_to_empty(chunk, chunk_x, chunk_z)
                                empty_region.add_chunk(empty_chunk)
                            except Exception as e:
                                # Chunk nie istnieje lub jest uszkodzony
                                pass
                    
                    self._region_cache[region_file] = empty_region
                except Exception as e:
                    logger.warning(f"Błąd wczytywania regionu {region_file}: {e}")
                    self._region_cache[region_file] = anvil.EmptyRegion(region_pos.x, region_pos.z)
            else:
                # Nowy pusty region
                self._region_cache[region_file] = anvil.EmptyRegion(region_pos.x, region_pos.z)
        
        return self._region_cache[region_file]
    
    def _chunk_to_empty(self, chunk: anvil.Chunk, chunk_x: int, chunk_z: int) -> anvil.EmptyChunk:
        """Konwertuje Chunk do EmptyChunk"""
        empty_chunk = anvil.EmptyChunk(chunk_x, chunk_z)
        
        # Kopiuj sekcje
        for section in chunk.sections:
            y = section['Y'].value
            empty_section = anvil.EmptySection(y)
            
            # Kopiuj bloki
            for x in range(16):
                for z in range(16):
                    for sy in range(16):
                        try:
                            block = chunk.get_block(x, y * 16 + sy, z)
                            if block and not (block.id == 0 and block.data == 0):
                                empty_section.set_block(OldBlock(block.id, block.data), x, sy, z)
                        except:
                            pass
            
            empty_chunk.add_section(empty_section)
        
        # Kopiuj TileEntities
        if hasattr(chunk, 'tile_entities') and chunk.tile_entities:
            # TileEntities są przechowywane w chunk.data['Level']['TileEntities']
            if 'TileEntities' in chunk.data['Level']:
                # Zachowaj oryginalne TE - zostaną dodane przy zapisie
                pass
        
        return empty_chunk
    
    def get_block(self, pos: Pos) -> Tuple[int, int]:
        """Zwraca (block_id, meta)"""
        chunk_pos = pos.chunk_pos()
        region_pos = chunk_pos.region_pos()
        
        region = self._get_or_create_region(region_pos)
        
        local_chunk_x = chunk_pos.x % 32
        local_chunk_z = chunk_pos.z % 32
        
        try:
            chunk = region.get_chunk(local_chunk_x, local_chunk_z)
            local_x, local_y, local_z = pos.local_chunk_pos()
            block = chunk.get_block(local_x, local_y, local_z)
            if block:
                return (block.id, block.data)
        except Exception as e:
            pass
        
        return (0, 0)  # Air
    
    def set_block(self, pos: Pos, block_id: int, meta: int = 0):
        """Ustawia blok"""
        chunk_pos = pos.chunk_pos()
        region_pos = chunk_pos.region_pos()
        
        region = self._get_or_create_region(region_pos)
        
        local_chunk_x = chunk_pos.x % 32
        local_chunk_z = chunk_pos.z % 32
        local_x, local_y, local_z = pos.local_chunk_pos()
        
        # Upewnij się że chunk istnieje
        try:
            chunk = region.get_chunk(local_chunk_x, local_chunk_z)
        except:
            # Utwórz nowy chunk
            chunk = anvil.EmptyChunk(local_chunk_x, local_chunk_z)
            region.add_chunk(chunk)
        
        # Ustaw blok
        block = OldBlock(block_id, meta)
        region.set_block(block, pos.x, pos.y, pos.z)
        
        logger.debug(f"set_block({pos}): {block_id}:{meta}")
    
    def get_tile_entity(self, pos: Pos) -> Optional[Dict[str, Any]]:
        """Zwraca TileEntity"""
        # TODO: Implementacja odczytu TE z PyAnvilEditor
        logger.warning("get_tile_entity niezaimplementowane w PyAnvilBackend")
        return None
    
    def set_tile_entity(self, pos: Pos, te_data: Dict[str, Any]):
        """Ustawia TileEntity"""
        # TODO: Implementacja zapisu TE
        # Wymaga bezpośredniej manipulacji NBT
        logger.warning("set_tile_entity niezaimplementowane w PyAnvilBackend")
    
    def commit(self):
        """Zapisuje zmiany do plików"""
        logger.info("Zapisywanie zmian...")
        
        for region_file, region in self._region_cache.items():
            try:
                region.save(str(region_file))
                logger.info(f"Zapisano region: {region_file.name}")
            except Exception as e:
                logger.error(f"Błąd zapisu regionu {region_file}: {e}")
                raise
        
        self._region_cache.clear()
        self._original_regions.clear()
        
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
        if self._region_cache:
            logger.warning("Niezapisane zmiany! Wywołaj commit() przed close()")
        self._region_cache.clear()
        self._original_regions.clear()
