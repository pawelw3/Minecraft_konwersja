"""
Enchanting Plus Mappings

Mapowania bloków i itemów między wersjami 1.7.10 a 1.18.2.
"""

from .block_mappings import (
    get_block_mapping,
    BLOCK_MAPPINGS_1710_TO_1182,
    ALL_EP_BLOCK_IDS_1710,
)

__all__ = [
    'get_block_mapping',
    'BLOCK_MAPPINGS_1710_TO_1182',
    'ALL_EP_BLOCK_IDS_1710',
]
