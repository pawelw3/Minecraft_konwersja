"""
Pakiet konwerterów Blood Magic dla Minecraft 1.7.10 -> 1.18.2

Ten pakiet zawiera konwertery dla wszystkich elementów Blood Magic:
- Bloki (mapowanie ID, metadata -> blockstates)
- Tile Entities / Block Entities (NBT conversion)
- Soul Network (dane graczy)
- Blood Orbs (item NBT)

Użycie:
    from src.converters.bloodmagic import BloodMagicConverter
    
    converter = BloodMagicConverter()
    result = converter.convert_block(
        block_id="AWWayofTime:Altar",
        metadata=0,
        te_nbt={"currentEssence": 10000, "upgradeLevel": 3, ...},
        pos=(100, 64, -200)
    )
"""

from .block_mappings import (
    map_block_id,
    get_blockstate_props,
    map_te_id,
    BloodRuneType,
    RitualStoneType,
)
from .altar_converter import BloodAltarConverter
from .ritual_converter import MasterRitualStoneConverter
from .soul_network_converter import (
    SoulNetworkConverter,
    BloodOrbConverter,
    SoulNetworkData,
)
from .converter import BloodMagicConverter, ConversionResult

__all__ = [
    # Główny konwerter
    "BloodMagicConverter",
    "ConversionResult",
    
    # Mapowania
    "map_block_id",
    "get_blockstate_props",
    "map_te_id",
    "BloodRuneType",
    "RitualStoneType",
    
    # Konwertery NBT
    "BloodAltarConverter",
    "MasterRitualStoneConverter",
    "SoulNetworkConverter",
    "BloodOrbConverter",
    "SoulNetworkData",
]
