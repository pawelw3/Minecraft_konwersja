"""
ProjectRed Converter Module

Konwerter dla moda ProjectRed (1.7.10 -> 1.18.2).

Moduły:
- mappings: Mapowania bloków i itemów
- nbt_converters: Konwertery NBT dla TileEntity/BlockEntity
- simulations: Symulacje funkcjonalności (z Zadania 2)

Użycie:
    from src.converters.projectred import ProjectRedConverter

    converter = ProjectRedConverter()
    result = converter.convert_block(
        "ProjRed|Expansion:projectred.expansion.machine2",
        nbt_1710={"storage": 5000},
        metadata=5,  # BatteryBox
        position=(100, 64, 100)
    )

    print(result.converted.block_id_1182)  # projectred_expansion:battery_box
"""

from .projectred_converter import (
    ProjectRedConverter,
    ConversionResult,
    ProjectRedBlockConversion
)

from .mappings import (
    get_block_mapping,
    get_all_mappings,
    get_removed_blocks,
    BlockMapping,
    ALL_PROJECTRED_BLOCK_IDS_1710
)

from .nbt_converters import (
    BaseNBTConverter,
    NBTConversionResult,
    GATE_TYPE_NAMES,
    get_gate_block_id_1182,
    get_wire_block_id_1182
)

__all__ = [
    # Main converter
    'ProjectRedConverter',
    'ConversionResult',
    'ProjectRedBlockConversion',

    # Mappings
    'get_block_mapping',
    'get_all_mappings',
    'get_removed_blocks',
    'BlockMapping',
    'ALL_PROJECTRED_BLOCK_IDS_1710',

    # NBT
    'BaseNBTConverter',
    'NBTConversionResult',
    'GATE_TYPE_NAMES',
    'get_gate_block_id_1182',
    'get_wire_block_id_1182'
]

__version__ = "1.0.0"
