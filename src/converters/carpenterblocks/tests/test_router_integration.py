"""Testy integracyjne routera dla CarpentersBlocks."""

import pytest
from converters.router import convert_te_to_events, detect_mod


def _te(cb_metadata: int = 0, cover: str = "minecraft:planks", damage: int = 0) -> dict:
    return {
        "id": "TileEntityCarpentersBlock",
        "cbAttrList": [
            {"cbAttribute": 6, "cbUniqueId": cover, "Damage": damage, "Count": 1}
        ],
        "cbMetadata": cb_metadata,
        "cbDesign": "",
        "cbOwner": "",
        "x": 10, "y": 64, "z": -5,
    }


class TestRouterDetection:
    def test_detects_cb_te(self):
        assert detect_mod("TileEntityCarpentersBlock") == "carpentersblocks"


class TestRouterConversion:
    def test_slope_wedge_bottom_north(self):
        te = _te(cb_metadata=4)
        events = convert_te_to_events(te, block_numeric_id=415, metadata=4, global_pos=(10, 64, -5))
        assert len(events) == 1
        ev = events[0]
        assert ev["block"] == "cuttableblocks:carpenter_slope"
        assert ev["op"] == "set_block_entity"
        assert ev["blockstate"]["slope_type"] == "wedge"
        assert ev["blockstate"]["facing"] == "north"
        assert ev["blockstate"]["half"] == "bottom"
        assert ev["nbt"]["coverBlock"] == "minecraft:oak_planks"

    def test_stairs_straight_bottom_south(self):
        te = _te(cb_metadata=5)
        events = convert_te_to_events(te, block_numeric_id=416, metadata=5, global_pos=(0, 0, 0))
        assert len(events) == 1
        ev = events[0]
        assert ev["block"] == "cuttableblocks:carpenter_stairs"
        assert ev["blockstate"]["facing"] == "south"
        assert ev["blockstate"]["half"] == "bottom"
        assert ev["blockstate"]["shape"] == "straight"

    def test_block_slab_y_bottom(self):
        te = _te(cb_metadata=3)
        events = convert_te_to_events(te, block_numeric_id=247, metadata=3, global_pos=(1, 2, 3))
        assert len(events) == 1
        ev = events[0]
        assert ev["block"] == "cuttableblocks:carpenter_block"
        assert ev["blockstate"]["type"] == "bottom"
        assert ev["blockstate"]["axis"] == "y"

    def test_barrier_vanilla_no_post(self):
        te = _te(cb_metadata=0)
        events = convert_te_to_events(te, block_numeric_id=248, metadata=0, global_pos=(5, 6, 7))
        assert len(events) == 1
        ev = events[0]
        assert ev["block"] == "cuttableblocks:carpenter_barrier"
        assert ev["blockstate"]["barrier_type"] == "vanilla"
        assert ev["blockstate"]["post"] == "false"

    def test_unknown_numeric_id_placeholder(self):
        te = _te()
        events = convert_te_to_events(te, block_numeric_id=999, metadata=0, global_pos=(0, 0, 0))
        assert len(events) == 1
        assert events[0]["block"] == "conversion_placeholders:block_entity_placeholder"
        assert "unknown_cb_numeric_id:999" in events[0]["nbt"]["conversion_reason"]

    def test_cover_material_resolved(self):
        te = _te(cover="minecraft:log", damage=1)
        events = convert_te_to_events(te, block_numeric_id=415, metadata=4, global_pos=(0, 0, 0))
        assert events[0]["nbt"]["coverBlock"] == "minecraft:spruce_log"

    def test_door_conversion(self):
        # panels, left hinge, north, closed, bottom, nonrigid
        data = 2 | (0 << 3) | (3 << 4) | (0 << 6) | (0 << 7)
        te = _te(cb_metadata=data)
        events = convert_te_to_events(te, block_numeric_id=253, metadata=0, global_pos=(0, 0, 0))
        assert len(events) == 1
        ev = events[0]
        assert ev["block"] == "cuttableblocks:carpenter_door"
        assert ev["blockstate"]["door_type"] == "panels"
        assert ev["blockstate"]["facing"] == "north"
        assert ev["blockstate"]["half"] == "lower"

    def test_bed_multiblock_warning(self):
        te = _te(cb_metadata=5)
        events = convert_te_to_events(te, block_numeric_id=249, metadata=0, global_pos=(0, 0, 0))
        assert len(events) == 1
        ev = events[0]
        assert ev["block"] == "cuttableblocks:carpenter_bed"
        assert any("CB-W-MULTIBLOCK" in str(w) for w in ev.get("warnings", []))
