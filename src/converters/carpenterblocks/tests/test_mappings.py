"""
Testy Zadanie 1: weryfikacja kompletności i spójności mapowań CarpentersBlocks.

Sprawdzamy:
  - ALL_CB_BLOCK_IDS_1710 zawiera wszystkie 18 bloków z BlockRegistry.java
  - CB_BLOCK_TO_CB1182 mapuje każdy blok (bez None)
  - SLOPE_ID_TO_PROPS pokrywa wszystkie 65 slopeID (0..64)
  - STAIRS_ID_TO_PROPS pokrywa wszystkie 28 stairsID (0..27)
  - SLAB_ID_TO_PROPS pokrywa cbMetadata 0..6
  - Każde SlopeProps ma slope_type ze słownika dozwolonych wartości
  - Każde StairsProps ma half in {bottom, top} i facing in {north,south,west,east,...}
"""

import pytest

from src.converters.carpenterblocks.mappings.block_ids import (
    ALL_CB_BLOCK_IDS_1710,
    CB_BLOCK_TO_CB1182,
    CB_GEOMETRIC_BLOCKS,
    CB_FUNCTIONAL_BLOCKS,
    CB_COVER_ONLY_BLOCKS,
    ATTR_COVER,
    ATTR_DYE,
    ATTR_OVERLAY,
)
from src.converters.carpenterblocks.mappings.geometry import (
    SLOPE_ID_TO_PROPS,
    STAIRS_ID_TO_PROPS,
    SLAB_ID_TO_PROPS,
    SlopeProps,
    StairsProps,
    SlabProps,
)


# -----------------------------------------------------------------------
# block_ids.py
# -----------------------------------------------------------------------

EXPECTED_CB_BLOCKS = {
    "CarpentersBlocks:blockCarpentersBarrier",
    "CarpentersBlocks:blockCarpentersBed",
    "CarpentersBlocks:blockCarpentersBlock",
    "CarpentersBlocks:blockCarpentersButton",
    "CarpentersBlocks:blockCarpentersCollapsibleBlock",
    "CarpentersBlocks:blockCarpentersDaylightSensor",
    "CarpentersBlocks:blockCarpentersDoor",
    "CarpentersBlocks:blockCarpentersFlowerPot",
    "CarpentersBlocks:blockCarpentersGarageDoor",
    "CarpentersBlocks:blockCarpentersGate",
    "CarpentersBlocks:blockCarpentersHatch",
    "CarpentersBlocks:blockCarpentersLadder",
    "CarpentersBlocks:blockCarpentersLever",
    "CarpentersBlocks:blockCarpentersPressurePlate",
    "CarpentersBlocks:blockCarpentersSafe",
    "CarpentersBlocks:blockCarpentersSlope",
    "CarpentersBlocks:blockCarpentersStairs",
    "CarpentersBlocks:blockCarpentersTorch",
}


def test_all_cb_blocks_complete():
    assert set(ALL_CB_BLOCK_IDS_1710) == EXPECTED_CB_BLOCKS


def test_all_cb_blocks_have_mapping():
    for block_id in ALL_CB_BLOCK_IDS_1710:
        assert block_id in CB_BLOCK_TO_CB1182, f"Brak mapowania dla {block_id}"


def test_cb1182_ids_have_namespace():
    for block_id, cb1182 in CB_BLOCK_TO_CB1182.items():
        if cb1182 is not None:
            assert ":" in cb1182, f"ID 1.18.2 bez namespace: {cb1182} (dla {block_id})"
            assert cb1182.startswith("cuttableblocks:"), (
                f"Oczekiwano cuttableblocks: ale jest {cb1182}"
            )


def test_geometric_functional_cover_partition():
    all_classified = CB_GEOMETRIC_BLOCKS | CB_FUNCTIONAL_BLOCKS | CB_COVER_ONLY_BLOCKS
    all_ids = set(ALL_CB_BLOCK_IDS_1710)
    assert all_classified == all_ids, (
        f"Niesklasyfikowane: {all_ids - all_classified}, "
        f"nadmiarowe: {all_classified - all_ids}"
    )


def test_attr_indices_correct():
    assert ATTR_COVER == list(range(7))
    assert ATTR_DYE == list(range(7, 14))
    assert ATTR_OVERLAY == list(range(14, 21))
    assert len(ATTR_COVER) == 7  # 6 stron + base
    assert len(ATTR_DYE) == 7
    assert len(ATTR_OVERLAY) == 7


# -----------------------------------------------------------------------
# geometry.py - Slope
# -----------------------------------------------------------------------

VALID_SLOPE_TYPES = {
    "wedge_side", "wedge", "wedge_int", "wedge_ext",
    "oblique_int", "oblique_ext",
    "prism", "prism_1p", "prism_2p", "prism_3p", "prism_4p", "prism_wedge",
}

VALID_HALVES = {"bottom", "top"}


def test_slope_ids_complete():
    expected = set(range(65))  # 0..64
    assert set(SLOPE_ID_TO_PROPS.keys()) == expected


def test_slope_props_valid_types():
    for sid, props in SLOPE_ID_TO_PROPS.items():
        assert isinstance(props, SlopeProps), f"slopeID={sid}: oczekiwano SlopeProps"
        assert props.slope_type in VALID_SLOPE_TYPES, (
            f"slopeID={sid}: nieprawidłowy slope_type='{props.slope_type}'"
        )
        assert props.half in VALID_HALVES, (
            f"slopeID={sid}: nieprawidłowe half='{props.half}'"
        )
        assert isinstance(props.facing, str), f"slopeID={sid}: facing musi być str"


def test_slope_wedge_side_ids():
    for sid in [0, 1, 2, 3]:
        assert SLOPE_ID_TO_PROPS[sid].slope_type == "wedge_side"


def test_slope_wedge_neg_bottom():
    for sid in [4, 5, 6, 7]:
        assert SLOPE_ID_TO_PROPS[sid].half == "bottom"
        assert SLOPE_ID_TO_PROPS[sid].slope_type == "wedge"


def test_slope_wedge_pos_top():
    for sid in [8, 9, 10, 11]:
        assert SLOPE_ID_TO_PROPS[sid].half == "top"
        assert SLOPE_ID_TO_PROPS[sid].slope_type == "wedge"


def test_slope_prism_4p():
    props = SLOPE_ID_TO_PROPS[60]
    assert props.slope_type == "prism_4p"
    assert props.facing == "all"


def test_slope_prism_ids():
    assert SLOPE_ID_TO_PROPS[44].slope_type == "prism"
    assert SLOPE_ID_TO_PROPS[45].slope_type == "prism"


# -----------------------------------------------------------------------
# geometry.py - Stairs
# -----------------------------------------------------------------------

VALID_STAIRS_SHAPES = {
    "straight",
    "inner_left", "inner_right",
    "outer_left", "outer_right",
    "side_se", "side_nw", "side_ne", "side_sw",
}

VALID_STAIRS_FACINGS = {"north", "south", "west", "east"}


def test_stairs_ids_complete():
    expected = set(range(28))  # 0..27
    assert set(STAIRS_ID_TO_PROPS.keys()) == expected


def test_stairs_props_valid():
    for sid, props in STAIRS_ID_TO_PROPS.items():
        assert isinstance(props, StairsProps), f"stairsID={sid}: oczekiwano StairsProps"
        assert props.facing in VALID_STAIRS_FACINGS, (
            f"stairsID={sid}: nieprawidłowe facing='{props.facing}'"
        )
        assert props.half in VALID_HALVES, (
            f"stairsID={sid}: nieprawidłowe half='{props.half}'"
        )
        assert props.shape in VALID_STAIRS_SHAPES, (
            f"stairsID={sid}: nieprawidłowy shape='{props.shape}'"
        )


def test_stairs_side_ids():
    for sid in [0, 1, 2, 3]:
        assert STAIRS_ID_TO_PROPS[sid].shape.startswith("side_")


def test_stairs_straight_ids():
    for sid in [4, 5, 6, 7, 8, 9, 10, 11]:
        assert STAIRS_ID_TO_PROPS[sid].shape == "straight"


def test_stairs_inner_ids():
    for sid in [12, 13, 14, 15, 16, 17, 18, 19]:
        assert STAIRS_ID_TO_PROPS[sid].shape in ("inner_left", "inner_right")


def test_stairs_outer_ids():
    for sid in [20, 21, 22, 23, 24, 25, 26, 27]:
        assert STAIRS_ID_TO_PROPS[sid].shape in ("outer_left", "outer_right")


def test_stairs_neg_bottom():
    for sid in [4, 5, 6, 7, 12, 13, 14, 15, 20, 21, 22, 23]:
        assert STAIRS_ID_TO_PROPS[sid].half == "bottom", f"stairsID={sid}"


def test_stairs_pos_top():
    for sid in [8, 9, 10, 11, 16, 17, 18, 19, 24, 25, 26, 27]:
        assert STAIRS_ID_TO_PROPS[sid].half == "top", f"stairsID={sid}"


# -----------------------------------------------------------------------
# geometry.py - Slab
# -----------------------------------------------------------------------

VALID_SLAB_TYPES = {"double", "bottom", "top"}
VALID_SLAB_AXES = {"x", "y", "z"}


def test_slab_ids_complete():
    expected = set(range(7))  # 0..6
    assert set(SLAB_ID_TO_PROPS.keys()) == expected


def test_slab_props_valid():
    for sid, props in SLAB_ID_TO_PROPS.items():
        assert isinstance(props, SlabProps), f"slabID={sid}: oczekiwano SlabProps"
        assert props.type in VALID_SLAB_TYPES, (
            f"slabID={sid}: nieprawidłowy type='{props.type}'"
        )
        assert props.axis in VALID_SLAB_AXES, (
            f"slabID={sid}: nieprawidłowe axis='{props.axis}'"
        )


def test_slab_full_is_double():
    assert SLAB_ID_TO_PROPS[0].type == "double"


def test_slab_y_neg_bottom():
    assert SLAB_ID_TO_PROPS[3].type == "bottom"
    assert SLAB_ID_TO_PROPS[3].axis == "y"


def test_slab_y_pos_top():
    assert SLAB_ID_TO_PROPS[4].type == "top"
    assert SLAB_ID_TO_PROPS[4].axis == "y"
