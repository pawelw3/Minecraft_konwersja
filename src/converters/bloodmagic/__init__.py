"""
Pakiet konwerterów Blood Magic dla Minecraft 1.7.10 -> 1.18.2

Ten pakiet zawiera konwertery dla wszystkich elementów Blood Magic:
- Bloki (mapowanie ID - w 1.18.2 każda Blood Rune to osobny blok)
- Tile Entities / Block Entities (NBT conversion)
- Soul Network (dane graczy)
- Blood Orbs (item NBT)

WAŻNE: W 1.18.2 Blood Runes są osobnymi blokami (nie używają blockstate "type").

Użycie:
    from src.converters.bloodmagic import BloodMagicConverter
    
    converter = BloodMagicConverter()
    result = converter.convert_block(
        block_id_1710="AWWayofTime:Altar",
        metadata=0,
        te_nbt_1710={"currentEssence": 10000, "upgradeLevel": 3, ...},
        pos=(100, 64, -200)  # Wymagane dla BlockEntity
    )
"""

from .block_mappings import (
    map_block_id,
    map_blood_rune,
    map_te_id,
    BloodRuneType,
    RUNE_BLOCK_MAPPING,
    BLOOD_RUNE_META_MAPPING,
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
    "map_blood_rune",
    "map_te_id",
    "BloodRuneType",
    "RUNE_BLOCK_MAPPING",
    "BLOOD_RUNE_META_MAPPING",
    
    # Konwertery NBT
    "BloodAltarConverter",
    "MasterRitualStoneConverter",
    "SoulNetworkConverter",
    "BloodOrbConverter",
    "SoulNetworkData",
]
