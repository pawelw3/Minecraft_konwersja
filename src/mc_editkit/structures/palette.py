"""
Paleta bloków dla struktur
"""
from typing import Dict, Tuple, Optional, Any
from dataclasses import dataclass


@dataclass
class BlockEntry:
    """Wpis w palecie bloków"""
    block_id: int
    meta: int = 0
    tile_entity: Optional[Dict[str, Any]] = None
    
    def __repr__(self):
        te_info = f" +TE" if self.tile_entity else ""
        return f"Block({self.block_id}:{self.meta}{te_info})"


class BlockPalette:
    """
    Paleta bloków dla struktur (analogiczna do schematów Minecraft).
    Mapuje indeksy na (block_id, meta, TE).
    """
    
    def __init__(self):
        self._entries: Dict[int, BlockEntry] = {}
        self._next_index = 1  # 0 = air
    
    def add(self, block_id: int, meta: int = 0, 
            tile_entity: Optional[Dict[str, Any]] = None) -> int:
        """
        Dodaje blok do palety i zwraca jego indeks.
        """
        # Sprawdź czy taki blok już istnieje
        for idx, entry in self._entries.items():
            if (entry.block_id == block_id and 
                entry.meta == meta and
                entry.tile_entity == tile_entity):
                return idx
        
        # Dodaj nowy
        idx = self._next_index
        self._entries[idx] = BlockEntry(block_id, meta, tile_entity)
        self._next_index += 1
        return idx
    
    def get(self, index: int) -> BlockEntry:
        """Zwraca wpis dla danego indeksu"""
        if index == 0:
            return BlockEntry(0, 0, None)  # Air
        return self._entries.get(index, BlockEntry(0, 0, None))
    
    def __getitem__(self, index: int) -> BlockEntry:
        return self.get(index)
    
    def __len__(self):
        return len(self._entries) + 1  # +1 dla air (0)
