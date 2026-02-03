"""
Better Storage Converter - Moduł konwersji z 1.7.10 na 1.18.2

Zawiera konwerter dla modu Better Storage obsługujący:
- Crate Pile (z osobnych plików data/crates/)
- Reinforced Chest → Iron Chests
- Locker → Barrel/Chest
- Cardboard Box → Packing Tape
- Crafting Station
- Armor Stand
"""

from .nbt_converter import BetterStorageConverter
from .crate_pile_simulation import CratePileLoader, CratePileData, CratePileRegion
from .mapping import BLOCK_MAPPING, ITEM_MAPPING, COLOR_MAPPING, ORIENTATION_MAPPING

__all__ = [
    'BetterStorageConverter',
    'CratePileLoader',
    'CratePileData',
    'BLOCK_MAPPING',
    'ITEM_MAPPING',
    'COLOR_MAPPING',
    'ORIENTATION_MAPPING',
]
