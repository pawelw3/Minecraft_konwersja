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

from .nbt_converter import BetterStorageConverter, convert_single_block
from .crate_pile_simulation import (
    CratePileLoader, CratePileData, CratePileRegion, 
    CratePileConverter, CrateLocation
)
from .mapping import (
    BLOCK_MAPPING, ITEM_MAPPING, COLOR_MAPPING, ORIENTATION_MAPPING,
    convert_color_to_dye_color, convert_orientation,
    get_iron_chest_type_for_capacity, get_container_slots
)
from .batch_converter import (
    BetterStorageBatchConverter, ConversionResult, BatchStats,
    quick_convert_block
)
from .cache import (
    SimpleCache, CratePileCache, ConversionCache,
    cached_conversion, OptimizedCratePileLoader,
    get_global_cache, clear_global_cache
)
from .item_id_mapping import (
    convert_numeric_id, convert_crate_stack,
    ALL_MINECRAFT_IDS, MINECRAFT_BLOCK_IDS, MINECRAFT_ITEM_IDS
)
from .nbt_parser import parse_nbt_file, parse_nbt_bytes

__version__ = '1.0.0'

__all__ = [
    # Główny konwerter
    'BetterStorageConverter',
    'convert_single_block',
    
    # Crate Pile
    'CratePileLoader',
    'CratePileData',
    'CratePileRegion',
    'CratePileConverter',
    'CrateLocation',
    
    # Batch conversion
    'BetterStorageBatchConverter',
    'ConversionResult',
    'BatchStats',
    'quick_convert_block',
    
    # Cache
    'SimpleCache',
    'CratePileCache',
    'ConversionCache',
    'cached_conversion',
    'OptimizedCratePileLoader',
    'get_global_cache',
    'clear_global_cache',
    
    # Mapowania
    'BLOCK_MAPPING',
    'ITEM_MAPPING',
    'COLOR_MAPPING',
    'ORIENTATION_MAPPING',
    'convert_color_to_dye_color',
    'convert_orientation',
    'get_iron_chest_type_for_capacity',
    'get_container_slots',
    
    # Item ID mapping
    'convert_numeric_id',
    'convert_crate_stack',
    'ALL_MINECRAFT_IDS',
    'MINECRAFT_BLOCK_IDS',
    'MINECRAFT_ITEM_IDS',
    
    # NBT Parser
    'parse_nbt_file',
    'parse_nbt_bytes',
]
