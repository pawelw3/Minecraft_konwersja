"""Traincraft 1.7.10 → 1.18.2 block and tile entity mappings.

Traincraft blocks registry (from TCBlocks.java / BlockIDs enum):
- tc:distilIdle, tc:distilActive
- tc:assemblyTableI, tc:assemblyTableII, tc:assemblyTableIII
- tc:trainWorkbench
- tc:stopper
- tc:openFurnaceIdle, tc:openFurnaceActive
- tc:oreTC
- tc:lantern
- tc:switchStand
- tc:waterWheel, tc:windMill
- tc:generatorDiesel
- tc:tcRail, tc:tcRailGag
- tc:bridgePillar
- tc:diesel, tc:refinedFuel (fluids)

Traincraft TE registry (from CommonProxy.java):
- TileCrafterTierI, TileCrafterTierII, TileCrafterTierIII
- TileTrainWbench
- TileEntityDistil ("Tile Distil")
- TileEntityOpenHearthFurnace ("Tile OpenHearthFurnace")
- TileStopper
- TileSignal ("TileTrainSignal")
- TileLantern ("tileLantern")
- TileSwitchStand ("tileSwitchStand")
- TileWaterWheel ("tileWaterWheel")
- TileWindMill ("tileWindMill")
- TileGeneratorDiesel ("tileGeneratorDiesel")
- TileBook ("tileBook")
- TileTCRailGag ("tileTCRailGag")
- TileTCRail ("tileTCRail")  ⭐ KEY
- TileBridgePillar ("tileTCBridgePillar")
"""

from __future__ import annotations

from typing import Any

# ── Traincraft TE ids (exact registry strings from CommonProxy.java) ──
TRAINCRAFT_TE_IDS = frozenset([
    "TileCrafterTierI",
    "TileCrafterTierII",
    "TileCrafterTierIII",
    "TileTrainWbench",
    "Tile Distil",
    "Tile OpenHearthFurnace",
    "TileStopper",
    "TileTrainSignal",
    "tileLantern",
    "tileSwitchStand",
    "tileWaterWheel",
    "tileWindMill",
    "tileGeneratorDiesel",
    "tileBook",
    "tileTCRailGag",
    "tileTCRail",
    "tileTCBridgePillar",
    # MTC (optional)
    "tileInfoTransmitterSpeed",
    "tileInfoTransmitterMTC",
    "tileATOTransmitterStopPoint",
    "tileInfoReceiverMTC",
    "tileInfoReceiverDestination",
    "tilePDMInstructionRadio",
])

# tcRail track types (from ItemTCRail.TrackTypes)
STRAIGHT_TRACK_TYPES = frozenset([
    "SMALL_STRAIGHT",
    "MEDIUM_STRAIGHT",
    "LONG_STRAIGHT",
    "SMALL_ROAD_CROSSING",
    "SMALL_ROAD_CROSSING_1",
    "SMALL_ROAD_CROSSING_2",
])

TURN_TRACK_TYPES = frozenset([
    "MEDIUM_TURN",
    "MEDIUM_RIGHT_TURN",
    "MEDIUM_LEFT_TURN",
    "LARGE_TURN",
    "LARGE_RIGHT_TURN",
    "LARGE_LEFT_TURN",
    "VERY_LARGE_TURN",
    "VERY_LARGE_RIGHT_TURN",
    "VERY_LARGE_LEFT_TURN",
])

SWITCH_TRACK_TYPES = frozenset([
    "MEDIUM_SWITCH",
    "MEDIUM_RIGHT_SWITCH",
    "MEDIUM_LEFT_SWITCH",
    "LARGE_SWITCH",
    "LARGE_RIGHT_SWITCH",
    "LARGE_LEFT_SWITCH",
    "MEDIUM_PARALLEL_SWITCH",
    "MEDIUM_RIGHT_PARALLEL_SWITCH",
    "MEDIUM_LEFT_PARALLEL_SWITCH",
])

SLOPE_TRACK_TYPES = frozenset([
    "SLOPE_WOOD",
    "SLOPE_GRAVEL",
    "SLOPE_BALLAST",
    "LARGE_SLOPE_WOOD",
    "LARGE_SLOPE_GRAVEL",
    "LARGE_SLOPE_BALLAST",
    "VERY_LARGE_SLOPE_WOOD",
    "VERY_LARGE_SLOPE_GRAVEL",
    "VERY_LARGE_SLOPE_BALLAST",
])

CROSSING_TRACK_TYPES = frozenset([
    "TWO_WAYS_CROSSING",
])

# facingMeta (0=S, 1=W, 2=N, 3=E in original code context, but let's map carefully)
# From ItemTCRail.java:
# l==0 -> south (+z), l==1 -> west (-x), l==2 -> north (-z), l==3 -> east (+x)
# For vanilla/create tracks:
# shape=zo goes north-south (along Z), shape=xo goes east-west (along X)
FACING_TO_STRAIGHT_SHAPE = {
    0: "zo",  # south
    1: "xo",  # west
    2: "zo",  # north
    3: "xo",  # east
}

# For ascending tracks (slope), facingMeta indicates direction of ascent
# In Create: AN=ascending north, AS=ascending south, AW=ascending west, AE=ascending east
FACING_TO_ASCENDING_SHAPE = {
    0: "as",  # ascending south (train goes towards +z, rises)
    1: "aw",  # ascending west
    2: "an",  # ascending north
    3: "ae",  # ascending east
}


def is_traincraft_te_id(te_id: str) -> bool:
    return te_id in TRAINCRAFT_TE_IDS


def is_traincraft_block_id(block_id: str) -> bool:
    return block_id.startswith("tc:") or block_id.startswith("Traincraft:")


def classify_track_type(track_type: str | None) -> str:
    """Classify a Traincraft track type into category."""
    if not track_type:
        return "unknown"
    if track_type in STRAIGHT_TRACK_TYPES:
        return "straight"
    if track_type in TURN_TRACK_TYPES:
        return "turn"
    if track_type in SWITCH_TRACK_TYPES:
        return "switch"
    if track_type in SLOPE_TRACK_TYPES:
        return "slope"
    if track_type in CROSSING_TRACK_TYPES:
        return "crossing"
    return "unknown"


def get_track_target(track_type: str, facing_meta: int) -> tuple[str, dict[str, str], dict[str, Any] | None]:
    """
    Map a Traincraft track type to Create / Steam'n'Rails target.
    Returns: (block_id_1182, blockstate_props, nbt_1182 or None)
    """
    category = classify_track_type(track_type)

    if category == "straight":
        shape = FACING_TO_STRAIGHT_SHAPE.get(facing_meta, "zo")
        return "create:track", {"shape": shape, "turn": "false"}, None

    if category == "slope":
        shape = FACING_TO_ASCENDING_SHAPE.get(facing_meta, "an")
        return "create:track", {"shape": shape, "turn": "false"}, None

    if category == "crossing":
        return "create:track", {"shape": "cr_o", "turn": "false"}, None

    if category == "turn":
        # Turns are intentionally NOT converted — too complex (BezierConnection).
        # The player will need to rebuild curves manually in 1.18.2.
        return "minecraft:air", {}, None

    if category == "switch":
        # Switches are approximated as straight tracks (switch block skipped).
        # The player will need to rebuild switches manually in 1.18.2.
        shape = FACING_TO_STRAIGHT_SHAPE.get(facing_meta, "zo")
        return "create:track", {"shape": shape, "turn": "false"}, None

    return "conversion_placeholders:block_entity_placeholder", {}, None


# Simple non-rail block mappings (blocks that don't have complex TE logic)
NON_RAIL_BLOCK_MAPPINGS: dict[str, tuple[str | None, dict[str, str]]] = {
    # Machines -> placeholder (no direct equivalent in Create)
    "tc:distilIdle": ("conversion_placeholders:block_entity_placeholder", {}),
    "tc:distilActive": ("conversion_placeholders:block_entity_placeholder", {}),
    "tc:assemblyTableI": ("conversion_placeholders:block_entity_placeholder", {}),
    "tc:assemblyTableII": ("conversion_placeholders:block_entity_placeholder", {}),
    "tc:assemblyTableIII": ("conversion_placeholders:block_entity_placeholder", {}),
    "tc:trainWorkbench": ("conversion_placeholders:block_entity_placeholder", {}),
    "tc:openFurnaceIdle": ("conversion_placeholders:block_entity_placeholder", {}),
    "tc:openFurnaceActive": ("conversion_placeholders:block_entity_placeholder", {}),
    "tc:generatorDiesel": ("conversion_placeholders:block_entity_placeholder", {}),
    # Decorative / simple blocks
    "tc:stopper": ("minecraft:oak_fence", {}),  # approximate visual
    "tc:lantern": ("minecraft:lantern", {}),
    "tc:switchStand": ("minecraft:lever", {}),
    "tc:bridgePillar": ("minecraft:oak_log", {}),
    "tc:waterWheel": ("minecraft:air", {}),
    "tc:windMill": ("minecraft:air", {}),
    # Ores
    "tc:oreTC": ("minecraft:iron_ore", {}),
    # Fluids
    "tc:diesel": ("minecraft:water", {}),
    "tc:refinedFuel": ("minecraft:water", {}),
}


def get_non_rail_mapping(block_id: str, metadata: int = 0) -> tuple[str | None, dict[str, str]]:
    """Return target block_id and blockstate for non-rail Traincraft blocks."""
    mapping = NON_RAIL_BLOCK_MAPPINGS.get(block_id)
    if mapping:
        return mapping
    if block_id == "tc:tcRailGag":
        return "minecraft:air", {}
    return None, {}
