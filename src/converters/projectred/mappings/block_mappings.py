"""
Block Mappings for ProjectRed - 1.7.10 to 1.18.2

Mapowanie ID bloków i tile entities ProjectRed.

Source mapping:
- 1.7.10: docs/mod_mapping_indepth/from/projectred_1710_bloki_i_te.md
- 1.18.2: docs/mod_mapping_indepth/from/projectred_1182_bloki_i_be.md
- Porównanie: docs/mod_mapping_indepth/from/projectred_porownanie_1710_vs_1182.md

W 1.7.10 ProjectRed używa systemu metadanych dla wariantów bloków.
W 1.18.2 każdy wariant ma osobny block ID.
"""

from typing import Dict, Optional, List
from dataclasses import dataclass


@dataclass
class BlockMapping:
    """Reprezentuje mapowanie bloku między wersjami"""
    id_1710: str
    id_1182: str
    has_block_entity: bool = False
    nbt_converter: Optional[str] = None
    notes: str = ""
    removed: bool = False  # True jeśli blok został usunięty w 1.18.2


# ============================================================================
# EXPANSION MODULE - Maszyny
# ============================================================================

# machine1 block (1.7.10) - Inductive Furnace i Electrotine Generator
MACHINE1_MAPPINGS: Dict[int, BlockMapping] = {
    0: BlockMapping(
        id_1710="ProjRed|Expansion:projectred.expansion.machine1",
        id_1182="",  # USUNIĘTY - TileInductiveFurnace
        has_block_entity=True,
        nbt_converter=None,
        notes="TileInductiveFurnace - USUNIĘTY w 1.18.2",
        removed=True
    ),
    1: BlockMapping(
        id_1710="ProjRed|Expansion:projectred.expansion.machine1",
        id_1182="projectred_core:electrotine_generator",  # Przeniesiony do Core
        has_block_entity=True,
        nbt_converter="electrotine_generator",
        notes="TileElectrotineGenerator - przeniesiony do Core"
    ),
}

# machine2 block (1.7.10) - Główne maszyny Expansion
MACHINE2_MAPPINGS: Dict[int, BlockMapping] = {
    0: BlockMapping(
        id_1710="ProjRed|Expansion:projectred.expansion.machine2",
        id_1182="projectred_expansion:block_breaker",
        has_block_entity=True,
        nbt_converter="block_breaker",
        notes="TileBlockBreaker"
    ),
    1: BlockMapping(
        id_1710="ProjRed|Expansion:projectred.expansion.machine2",
        id_1182="",  # USUNIĘTY
        has_block_entity=True,
        nbt_converter=None,
        notes="TileItemImporter - USUNIĘTY w 1.18.2",
        removed=True
    ),
    2: BlockMapping(
        id_1710="ProjRed|Expansion:projectred.expansion.machine2",
        id_1182="projectred_expansion:deployer",  # Zastąpiony przez Deployer
        has_block_entity=True,
        nbt_converter="deployer",
        notes="TileBlockPlacer - zastąpiony przez Deployer"
    ),
    3: BlockMapping(
        id_1710="ProjRed|Expansion:projectred.expansion.machine2",
        id_1182="",  # USUNIĘTY
        has_block_entity=True,
        nbt_converter=None,
        notes="TileFilteredImporter - USUNIĘTY w 1.18.2",
        removed=True
    ),
    4: BlockMapping(
        id_1710="ProjRed|Expansion:projectred.expansion.machine2",
        id_1182="projectred_expansion:fire_starter",
        has_block_entity=True,
        nbt_converter="fire_starter",
        notes="TileFireStarter"
    ),
    5: BlockMapping(
        id_1710="ProjRed|Expansion:projectred.expansion.machine2",
        id_1182="projectred_expansion:battery_box",
        has_block_entity=True,
        nbt_converter="battery_box",
        notes="TileBatteryBox"
    ),
    6: BlockMapping(
        id_1710="ProjRed|Expansion:projectred.expansion.machine2",
        id_1182="projectred_expansion:charging_bench",
        has_block_entity=True,
        nbt_converter="charging_bench",
        notes="TileChargingBench"
    ),
    7: BlockMapping(
        id_1710="ProjRed|Expansion:projectred.expansion.machine2",
        id_1182="",  # USUNIĘTY
        has_block_entity=True,
        nbt_converter=None,
        notes="TileTeleposer - USUNIĘTY w 1.18.2",
        removed=True
    ),
    8: BlockMapping(
        id_1710="ProjRed|Expansion:projectred.expansion.machine2",
        id_1182="projectred_expansion:frame_motor",
        has_block_entity=True,
        nbt_converter="frame_motor",
        notes="TileFrameMotor"
    ),
    9: BlockMapping(
        id_1710="ProjRed|Expansion:projectred.expansion.machine2",
        id_1182="projectred_expansion:frame_actuator",
        has_block_entity=True,
        nbt_converter="frame_actuator",
        notes="TileFrameActuator"
    ),
    10: BlockMapping(
        id_1710="ProjRed|Expansion:projectred.expansion.machine2",
        id_1182="projectred_expansion:project_bench",
        has_block_entity=True,
        nbt_converter="project_bench",
        notes="TileProjectBench"
    ),
    11: BlockMapping(
        id_1710="ProjRed|Expansion:projectred.expansion.machine2",
        id_1182="projectred_expansion:auto_crafter",
        has_block_entity=True,
        nbt_converter="auto_crafter",
        notes="TileAutoCrafter"
    ),
    12: BlockMapping(
        id_1710="ProjRed|Expansion:projectred.expansion.machine2",
        id_1182="projectred_expansion:block_breaker",  # Zastąpiony zwykłym BlockBreaker
        has_block_entity=True,
        nbt_converter="block_breaker",
        notes="TileDiamondBlockBreaker - zastąpiony zwykłym BlockBreaker"
    ),
}

# ============================================================================
# EXPLORATION MODULE - Rudy i bloki dekoracyjne
# ============================================================================

# ore block (1.7.10) - Rudy
ORE_MAPPINGS: Dict[int, BlockMapping] = {
    0: BlockMapping(
        id_1710="ProjRed|Exploration:projectred.exploration.ore",
        id_1182="projectred_exploration:ruby_ore",
        has_block_entity=False,
        notes="Ruby Ore"
    ),
    1: BlockMapping(
        id_1710="ProjRed|Exploration:projectred.exploration.ore",
        id_1182="projectred_exploration:sapphire_ore",
        has_block_entity=False,
        notes="Sapphire Ore"
    ),
    2: BlockMapping(
        id_1710="ProjRed|Exploration:projectred.exploration.ore",
        id_1182="projectred_exploration:peridot_ore",
        has_block_entity=False,
        notes="Peridot Ore"
    ),
    3: BlockMapping(
        id_1710="ProjRed|Exploration:projectred.exploration.ore",
        id_1182="minecraft:copper_ore",  # Vanilla copper w 1.18.2
        has_block_entity=False,
        notes="Copper Ore - zastąpiony vanilla copper"
    ),
    4: BlockMapping(
        id_1710="ProjRed|Exploration:projectred.exploration.ore",
        id_1182="projectred_exploration:tin_ore",
        has_block_entity=False,
        notes="Tin Ore"
    ),
    5: BlockMapping(
        id_1710="ProjRed|Exploration:projectred.exploration.ore",
        id_1182="projectred_exploration:silver_ore",
        has_block_entity=False,
        notes="Silver Ore"
    ),
    6: BlockMapping(
        id_1710="ProjRed|Exploration:projectred.exploration.ore",
        id_1182="projectred_exploration:electrotine_ore",
        has_block_entity=False,
        notes="Electrotine Ore"
    ),
}

# stone block (1.7.10) - Bloki dekoracyjne
STONE_MAPPINGS: Dict[int, BlockMapping] = {
    0: BlockMapping(
        id_1710="ProjRed|Exploration:projectred.exploration.stone",
        id_1182="projectred_exploration:marble",
        has_block_entity=False,
        notes="Marble"
    ),
    1: BlockMapping(
        id_1710="ProjRed|Exploration:projectred.exploration.stone",
        id_1182="projectred_exploration:marble_brick",
        has_block_entity=False,
        notes="Marble Brick"
    ),
    2: BlockMapping(
        id_1710="ProjRed|Exploration:projectred.exploration.stone",
        id_1182="projectred_exploration:basalt",
        has_block_entity=False,
        notes="Basalt"
    ),
    3: BlockMapping(
        id_1710="ProjRed|Exploration:projectred.exploration.stone",
        id_1182="projectred_exploration:basalt_cobble",
        has_block_entity=False,
        notes="Basalt Cobble"
    ),
    4: BlockMapping(
        id_1710="ProjRed|Exploration:projectred.exploration.stone",
        id_1182="projectred_exploration:basalt_brick",
        has_block_entity=False,
        notes="Basalt Brick"
    ),
    5: BlockMapping(
        id_1710="ProjRed|Exploration:projectred.exploration.stone",
        id_1182="projectred_exploration:ruby_block",
        has_block_entity=False,
        notes="Ruby Block"
    ),
    6: BlockMapping(
        id_1710="ProjRed|Exploration:projectred.exploration.stone",
        id_1182="projectred_exploration:sapphire_block",
        has_block_entity=False,
        notes="Sapphire Block"
    ),
    7: BlockMapping(
        id_1710="ProjRed|Exploration:projectred.exploration.stone",
        id_1182="projectred_exploration:peridot_block",
        has_block_entity=False,
        notes="Peridot Block"
    ),
    8: BlockMapping(
        id_1710="ProjRed|Exploration:projectred.exploration.stone",
        id_1182="minecraft:copper_block",  # Vanilla copper w 1.18.2
        has_block_entity=False,
        notes="Copper Block - zastąpiony vanilla copper block"
    ),
    9: BlockMapping(
        id_1710="ProjRed|Exploration:projectred.exploration.stone",
        id_1182="projectred_exploration:tin_block",
        has_block_entity=False,
        notes="Tin Block"
    ),
    10: BlockMapping(
        id_1710="ProjRed|Exploration:projectred.exploration.stone",
        id_1182="projectred_exploration:silver_block",
        has_block_entity=False,
        notes="Silver Block"
    ),
    11: BlockMapping(
        id_1710="ProjRed|Exploration:projectred.exploration.stone",
        id_1182="projectred_exploration:electrotine_block",
        has_block_entity=False,
        notes="Electrotine Block"
    ),
}

# ============================================================================
# FABRICATION MODULE - IC Workbench i stoły
# ============================================================================

IC_BLOCK_MAPPINGS: Dict[int, BlockMapping] = {
    0: BlockMapping(
        id_1710="ProjRed|Fabrication:projectred.fabrication.icblock",
        id_1182="projectred_fabrication:ic_workbench",
        has_block_entity=True,
        nbt_converter="ic_workbench",
        notes="TileICWorkbench"
    ),
    1: BlockMapping(
        id_1710="ProjRed|Fabrication:projectred.fabrication.icblock",
        id_1182="",  # ZASTĄPIONY przez 3 nowe stoły
        has_block_entity=True,
        nbt_converter=None,
        notes="TileICPrinter - ZASTĄPIONY przez plotting_table, lithography_table, packaging_table",
        removed=True
    ),
}

# ============================================================================
# EXPLORATION MODULE - Lily (USUNIĘTE w 1.18.2)
# ============================================================================

# W 1.7.10 Lily to kolorowe kwiaty (metadata 0-15 dla kolorów)
# W 1.18.2 zostały usunięte - zamiana na vanilla flowers
LILY_MAPPING = BlockMapping(
    id_1710="ProjRed|Exploration:projectred.exploration.lily",
    id_1182="",  # USUNIĘTY w 1.18.2
    has_block_entity=True,  # TileLily
    nbt_converter=None,
    notes="BlockLily/TileLily - USUNIĘTY w 1.18.2. Zastąpić vanilla flowers.",
    removed=True
)

# ============================================================================
# EXPANSION MODULE - Frame (blok ramki bez BE)
# ============================================================================

FRAME_MAPPING = BlockMapping(
    id_1710="ProjRed|Expansion:projectred.expansion.frame",
    id_1182="projectred_expansion:frame",
    has_block_entity=False,
    notes="Frame block - bez BlockEntity w 1.18.2"
)

# ============================================================================
# ILLUMINATION MODULE - Lampy (struktura zmieniona)
# ============================================================================

# W 1.7.10 lampy używają metadata dla kolorów (0-15)
# W 1.18.2 są osobne bloki dla każdego koloru
LAMP_COLORS = [
    "white", "orange", "magenta", "light_blue",
    "yellow", "lime", "pink", "gray",
    "light_gray", "cyan", "purple", "blue",
    "brown", "green", "red", "black"
]


def get_lamp_mapping(metadata: int, lamp_type: str = "lamp") -> BlockMapping:
    """
    Generuje mapowanie dla lamp z kolorem.

    Args:
        metadata: Kolor (0-15)
        lamp_type: Typ lampy ("lamp", "inverted_lamp", "illumar_smart_lamp")
    """
    color = LAMP_COLORS[metadata & 0xF]
    return BlockMapping(
        id_1710=f"ProjRed|Illumination:projectred.illumination.{lamp_type}",
        id_1182=f"projectred_illumination:{color}_{lamp_type}",
        has_block_entity=True,
        nbt_converter="lamp",
        notes=f"{color.title()} {lamp_type.replace('_', ' ').title()}"
    )


# ============================================================================
# Funkcje pomocnicze
# ============================================================================

def get_block_mapping(block_id_1710: str, metadata: int = 0) -> Optional[BlockMapping]:
    """
    Zwraca mapowanie dla bloku 1.7.10 z uwzględnieniem metadata.

    Args:
        block_id_1710: ID bloku w wersji 1.7.10
        metadata: Metadata bloku (0-15)

    Returns:
        BlockMapping lub None jeśli nie znaleziono
    """
    # Normalizuj ID (usuń prefiks numeryczny jeśli istnieje)
    normalized_id = block_id_1710

    # Machine1 (Expansion)
    if "projectred.expansion.machine1" in normalized_id:
        return MACHINE1_MAPPINGS.get(metadata)

    # Machine2 (Expansion)
    if "projectred.expansion.machine2" in normalized_id:
        return MACHINE2_MAPPINGS.get(metadata)

    # Ore (Exploration)
    if "projectred.exploration.ore" in normalized_id:
        return ORE_MAPPINGS.get(metadata)

    # Stone (Exploration)
    if "projectred.exploration.stone" in normalized_id:
        return STONE_MAPPINGS.get(metadata)

    # IC Block (Fabrication)
    if "projectred.fabrication.icblock" in normalized_id:
        return IC_BLOCK_MAPPINGS.get(metadata)

    # Frame (Expansion)
    if "projectred.expansion.frame" in normalized_id:
        return FRAME_MAPPING

    # Lily (Exploration) - USUNIĘTY w 1.18.2
    if "projectred.exploration.lily" in normalized_id:
        return LILY_MAPPING

    # Lampy (Illumination)
    if "projectred.illumination.lamp" in normalized_id:
        return get_lamp_mapping(metadata, "lamp")
    if "projectred.illumination.invertedlamp" in normalized_id:
        return get_lamp_mapping(metadata, "inverted_lamp")

    return None


def get_all_mappings() -> List[BlockMapping]:
    """Zwraca wszystkie mapowania bloków"""
    all_mappings = []

    # Machine1
    all_mappings.extend(MACHINE1_MAPPINGS.values())

    # Machine2
    all_mappings.extend(MACHINE2_MAPPINGS.values())

    # Ore
    all_mappings.extend(ORE_MAPPINGS.values())

    # Stone
    all_mappings.extend(STONE_MAPPINGS.values())

    # IC Block
    all_mappings.extend(IC_BLOCK_MAPPINGS.values())

    # Frame
    all_mappings.append(FRAME_MAPPING)

    # Lily (usunięty)
    all_mappings.append(LILY_MAPPING)

    # Lampy (wszystkie kolory)
    for meta in range(16):
        all_mappings.append(get_lamp_mapping(meta, "lamp"))
        all_mappings.append(get_lamp_mapping(meta, "inverted_lamp"))

    return all_mappings


def get_removed_blocks() -> List[BlockMapping]:
    """Zwraca listę bloków usuniętych w 1.18.2"""
    return [m for m in get_all_mappings() if m.removed]


# Zestaw ID bloków 1.7.10 obsługiwanych przez konwerter
ALL_PROJECTRED_BLOCK_IDS_1710 = {
    "ProjRed|Expansion:projectred.expansion.machine1",
    "ProjRed|Expansion:projectred.expansion.machine2",
    "ProjRed|Exploration:projectred.exploration.ore",
    "ProjRed|Exploration:projectred.exploration.stone",
    "ProjRed|Exploration:projectred.exploration.lily",  # Usunięty w 1.18.2
    "ProjRed|Fabrication:projectred.fabrication.icblock",
    "ProjRed|Expansion:projectred.expansion.frame",
    "ProjRed|Illumination:projectred.illumination.lamp",
    "ProjRed|Illumination:projectred.illumination.invertedlamp",
}
