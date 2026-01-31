"""
Typy pomocnicze dla edycji świata
"""
from dataclasses import dataclass
from typing import NamedTuple, Optional, Dict, Any


class Pos(NamedTuple):
    """Pozycja w świecie (bloki)"""
    x: int
    y: int
    z: int
    
    def chunk_pos(self) -> 'ChunkPos':
        """Zwraca pozycję chunka"""
        return ChunkPos(
            self.x >> 4 if self.x >= 0 else (self.x - 15) >> 4,
            self.z >> 4 if self.z >= 0 else (self.z - 15) >> 4
        )
    
    def region_pos(self) -> 'RegionPos':
        """Zwraca pozycję regionu"""
        chunk = self.chunk_pos()
        return RegionPos(
            chunk.x >> 5 if chunk.x >= 0 else (chunk.x - 31) >> 5,
            chunk.z >> 5 if chunk.z >= 0 else (chunk.z - 31) >> 5
        )
    
    def local_chunk_pos(self) -> tuple:
        """Zwraca lokalną pozycję w chunku (0-15)"""
        return (self.x & 15, self.y, self.z & 15)
    
    def section_y(self) -> int:
        """Zwraca indeks sekcji Y (0-15 dla MC 1.7.10)"""
        return self.y >> 4


class ChunkPos(NamedTuple):
    """Pozycja chunka"""
    x: int
    z: int
    
    def region_pos(self) -> 'RegionPos':
        """Zwraca pozycję regionu"""
        return RegionPos(
            self.x >> 5 if self.x >= 0 else (self.x - 31) >> 5,
            self.z >> 5 if self.z >= 0 else (self.z - 31) >> 5
        )
    
    def local_region_pos(self) -> tuple:
        """Zwraca lokalną pozycję w regionie (0-31)"""
        return (self.x & 31, self.z & 31)


class RegionPos(NamedTuple):
    """Pozycja regionu"""
    x: int
    z: int


@dataclass
class EditOperation:
    """Operacja edycji bloku"""
    pos: Pos
    block_id: int
    meta: int = 0
    tile_entity: Optional[Dict[str, Any]] = None
    
    def __repr__(self):
        te_info = f" +TE({self.tile_entity.get('id', '?')})" if self.tile_entity else ""
        return f"Edit({self.pos}: {self.block_id}:{self.meta}{te_info})"
