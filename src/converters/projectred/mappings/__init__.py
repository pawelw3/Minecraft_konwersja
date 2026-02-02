"""
ProjectRed Block and Item Mappings

Eksportuje mapowania bloków i itemów dla ProjectRed.
"""

from .block_mappings import (
    BlockMapping,
    get_block_mapping,
    get_all_mappings,
    get_removed_blocks,
    get_lamp_mapping,
    ALL_PROJECTRED_BLOCK_IDS_1710,
    MACHINE1_MAPPINGS,
    MACHINE2_MAPPINGS,
    ORE_MAPPINGS,
    STONE_MAPPINGS,
    IC_BLOCK_MAPPINGS,
    FRAME_MAPPING,
    LAMP_COLORS
)

__all__ = [
    'BlockMapping',
    'get_block_mapping',
    'get_all_mappings',
    'get_removed_blocks',
    'get_lamp_mapping',
    'ALL_PROJECTRED_BLOCK_IDS_1710',
    'MACHINE1_MAPPINGS',
    'MACHINE2_MAPPINGS',
    'ORE_MAPPINGS',
    'STONE_MAPPINGS',
    'IC_BLOCK_MAPPINGS',
    'FRAME_MAPPING',
    'LAMP_COLORS'
]
