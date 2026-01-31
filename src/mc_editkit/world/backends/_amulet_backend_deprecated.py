"""
Backend OFFLINE do edycji regionów Anvil (.mca)
Używa amulet-core do read/write
"""
import os
import shutil
import logging
from pathlib import Path
from typing import Dict, Optional, Any, List, Tuple
from dataclasses import dataclass

try:
    import amulet
    from amulet.api.block import Block
except ImportError:
    raise ImportError("amulet-core nie jest zainstalowany. Uruchom: pip install amulet-core")

from ...world.types import Pos, ChunkPos, RegionPos, EditOperation

logger = logging.getLogger(__name__)


class AmuletBackend:
    """
    Backend do edycji światów Minecraft przez amulet-core.
    Pracuje OFFLINE na plikach regionów.
    """
    
    def __init__(self, world_path: str, backup: bool = True):
        """
        Inicjalizuje backend.
        
        Args:
            world_path: Ścieżka do katalogu świata
            backup: Czy tworzyć backup przed edycją
        """
        self.world_path = Path(world_path)
        self.region_path = self.world_path / "region"
        self.backup = backup
        
        if not self.region_path.exists():
            raise ValueError(f"Nie znaleziono katalogu region: {self.region_path}")
        
        # Otwórz świat przez amulet
        self._world = amulet.load_level(str(world_path))
        self._dimension = "minecraft:overworld"
        self._version = ("java", (1, 7, 10))
        
        # Backup
        self._backup_dir: Optional[Path] = None
        self._backed_up_regions: set = set()
        
        logger.info(f"Otwarto świat: {self._world.level_wrapper.platform} {self._world.level_wrapper.version}")
    
    def _backup_region(self, region_pos: RegionPos):
        """Tworzy backup regionu przed modyfikacją"""
        if not self.backup:
            return
        
        if region_pos in self._backed_up_regions:
            return
        
        region_file = self.region_path / f"r.{region_pos.x}.{region_pos.z}.mca"
        if not region_file.exists():
            return
        
        if self._backup_dir is None:
            import time
            self._backup_dir = self.world_path / "backups" / f"edit_{int(time.time())}"
            self._backup_dir.mkdir(parents=True, exist_ok=True)
        
        backup_file = self._backup_dir / region_file.name
        shutil.copy2(region_file, backup_file)
        self._backed_up_regions.add(region_pos)
        logger.info(f"Backup regionu r.{region_pos.x}.{region_pos.z}.mca -> {backup_file}")
    
    def get_block(self, pos: Pos) -> Tuple[int, int]:
        """
        Zwraca (block_id, meta) dla danej pozycji.
        """
        try:
            block = self._world.get_block(pos.x, pos.y, pos.z, self._dimension)
            # Amulet zwraca blok w formacie uniwersalnym - musimy przekonwertować
            # Dla uproszczenia zakładamy że to vanilla block
            block_id = 1  # Domyślnie stone
            meta = 0
            return (block_id, meta)
        except:
            return (0, 0)  # Air
    
    def set_block(self, pos: Pos, block_id: int, meta: int = 0):
        """
        Ustawia blok na danej pozycji.
        """
        chunk_pos = pos.chunk_pos()
        self._backup_region(chunk_pos.region_pos())
        
        # Mapuj block_id na nazwę bloku (uproszczone - tylko podstawowe bloki)
        block_name = self._id_to_name(block_id)
        block = Block("minecraft", block_name)
        
        self._world.set_version_block(
            pos.x, pos.y, pos.z,
            self._dimension,
            self._version,
            block
        )
        
        logger.debug(f"set_block({pos}): {block_id}:{meta}")
    
    def _id_to_name(self, block_id: int) -> str:
        """Mapuje ID bloku na nazwę (uproszczone)"""
        mapping = {
            0: "air",
            1: "stone",
            2: "grass_block",
            3: "dirt",
            4: "cobblestone",
            55: "redstone_wire",
            93: "repeater",
            137: "command_block",
            152: "redstone_block",
            158: "dropper",
            149: "comparator",
            154: "hopper",
            54: "chest",
        }
        return mapping.get(block_id, "stone")
    
    def get_tile_entity(self, pos: Pos) -> Optional[Dict[str, Any]]:
        """
        Zwraca TileEntity dla danej pozycji lub None.
        """
        try:
            chunk = self._world.get_chunk(pos.x >> 4, pos.z >> 4, self._dimension)
            # Pobierz TE z chunka
            for te in chunk.block_entities:
                if te.x == pos.x and te.y == pos.y and te.z == pos.z:
                    return dict(te.nbt)
        except:
            pass
        return None
    
    def set_tile_entity(self, pos: Pos, te_data: Dict[str, Any]):
        """
        Ustawia TileEntity na danej pozycji.
        """
        chunk_pos = pos.chunk_pos()
        self._backup_region(chunk_pos.region_pos())
        
        # Upewnij się że TE ma poprawne współrzędne
        te_copy = dict(te_data)
        te_copy['x'] = pos.x
        te_copy['y'] = pos.y
        te_copy['z'] = pos.z
        
        # Dodaj TE przez block entity
        from amulet.api.block_entity import BlockEntity
        import amulet_nbt
        
        # Konwertuj dict na NBT
        compound = amulet_nbt.TAG_Compound()
        for key, value in te_copy.items():
            if isinstance(value, str):
                compound[key] = amulet_nbt.TAG_String(value)
            elif isinstance(value, int):
                compound[key] = amulet_nbt.TAG_Int(value)
            elif isinstance(value, bool):
                compound[key] = amulet_nbt.TAG_Byte(1 if value else 0)
        
        be = BlockEntity(
            "minecraft",
            te_copy.get('id', 'Control').lower(),
            pos.x, pos.y, pos.z,  # osobne współrzędne
            amulet_nbt.NamedTag(compound)
        )
        
        chunk = self._world.get_chunk(pos.x >> 4, pos.z >> 4, self._dimension)
        chunk.block_entities[(pos.x, pos.y, pos.z)] = be
        
        logger.info(f"set_tile_entity({pos}): {te_copy.get('id', 'unknown')}")
    
    def clear_tile_entity(self, pos: Pos):
        """Usuwa TileEntity z danej pozycji"""
        try:
            chunk_pos = pos.chunk_pos()
            self._backup_region(chunk_pos.region_pos())
            
            chunk = self._world.get_chunk(pos.x >> 4, pos.z >> 4, self._dimension)
            to_remove = None
            for be in chunk.block_entities:
                if be.x == pos.x and be.y == pos.y and be.z == pos.z:
                    to_remove = be
                    break
            
            if to_remove:
                chunk.block_entities.remove(to_remove)
                logger.debug(f"clear_tile_entity({pos})")
        except:
            pass
    
    def apply(self, operations: List[EditOperation]):
        """
        Stosuje listę operacji (batch).
        """
        logger.info(f"Stosowanie {len(operations)} operacji...")
        
        for op in operations:
            self.set_block(op.pos, op.block_id, op.meta)
            if op.tile_entity:
                self.set_tile_entity(op.pos, op.tile_entity)
        
        logger.info(f"Zastosowano {len(operations)} operacji")
    
    def commit(self):
        """
        Zapisuje wszystkie zmiany do plików.
        """
        logger.info("Zapisywanie zmian...")
        self._world.save()
        self._world.close()
        logger.info("Zmiany zapisane")
    
    def rollback(self):
        """
        Cofa zmiany (przywraca backup).
        """
        if self._backup_dir and self._backup_dir.exists():
            logger.info("Przywracanie z backup...")
            
            for backup_file in self._backup_dir.glob("r.*.mca"):
                target = self.region_path / backup_file.name
                shutil.copy2(backup_file, target)
                logger.info(f"Przywrócono {target}")
            
            logger.info("Przywracanie zakończone")
        else:
            logger.warning("Brak backup do przywrócenia")
    
    def close(self):
        """Zamyka backend bez zapisywania zmian"""
        self._world.close()
        logger.info("Edytor zamknięty")
