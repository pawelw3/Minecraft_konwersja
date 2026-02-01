"""
AE2 Mappings - Mapowanie bloków i itemów AE2 między wersjami 1.7.10 i 1.18.2
"""

from .block_mappings import BLOCK_MAPPINGS_1710_TO_1182, get_block_mapping
from .item_mappings import ITEM_MAPPINGS_1710_TO_1182, get_item_mapping

__all__ = [
    'BLOCK_MAPPINGS_1710_TO_1182',
    'ITEM_MAPPINGS_1710_TO_1182',
    'get_block_mapping',
    'get_item_mapping',
]
