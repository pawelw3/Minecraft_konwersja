"""Testy jednostkowe CBMaterializer i dict_to_snbt."""

import pytest
from ..materializer import CBMaterializer, MaterializeEvent, dict_to_snbt, _snbt_value

# ─────────────────────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────────────────────

MAT = CBMaterializer()

def _te(cb_metadata: int = 0, cover: str = "minecraft:planks", damage: int = 0) -> dict:
    """Minimalny TEBase dict dla testów."""
    return {
        "cbAttrList": [
            {"cbAttribute": 6, "cbUniqueId": cover, "Damage": damage, "Count": 1}
        ],
        "cbMetadata": cb_metadata,
        "cbDesign": "",
        "cbOwner": "",
    }


# ─────────────────────────────────────────────────────────────────────────────
# TestSnbtValue
# ─────────────────────────────────────────────────────────────────────────────

class TestSnbtValue:
    def test_bool_true(self):
        assert _snbt_value(True) == "1b"

    def test_bool_false(self):
        assert _snbt_value(False) == "0b"

    def test_int(self):
        assert _snbt_value(42) == "42"

    def test_negative_int(self):
        assert _snbt_value(-1) == "-1"

    def test_string(self):
        assert _snbt_value("hello") == '"hello"'

    def test_string_with_quotes(self):
        assert _snbt_value('say "hi"') == '"say \\"hi\\""'

    def test_string_minecraft_id(self):
        assert _snbt_value("minecraft:oak_log") == '"minecraft:oak_log"'

    def test_int_list_becomes_int_array(self):
        assert _snbt_value([0, 8, 16, 4]) == "[I;0,8,16,4]"

    def test_empty_list(self):
        assert _snbt_value([]) == "[]"

    def test_dict(self):
        result = _snbt_value({"facing": "north"})
        assert result == '{"facing":"north"}'

    def test_nested_dict(self):
        result = _snbt_value({"geom": {"facing": "north", "half": "bottom"}})
        assert '"facing":"north"' in result
        assert '"half":"bottom"' in result


class TestDictToSnbt:
    def test_empty(self):
        assert dict_to_snbt({}) == "{}"

    def test_single_string(self):
        assert dict_to_snbt({"coverMaterial": "minecraft:oak_log"}) == \
            '{"coverMaterial":"minecraft:oak_log"}'

    def test_bool_field(self):
        result = dict_to_snbt({"illuminator": True})
        assert result == '{"illuminator":1b}'

    def test_int_array_field(self):
        result = dict_to_snbt({"quadDepths": [16, 16, 8, 4]})
        assert result == '{"quadDepths":[I;16,16,8,4]}'

    def test_compound_field(self):
        result = dict_to_snbt({"geom": {"facing": "north"}})
        assert '{"facing":"north"}' in result

    def test_multiple_fields_order(self):
        d = {"coverMaterial": "minecraft:stone", "cbDesign": "", "illuminator": False}
        snbt = dict_to_snbt(d)
        assert '"coverMaterial":"minecraft:stone"' in snbt
        assert '"cbDesign":""' in snbt
        assert '"illuminator":0b' in snbt


# ─────────────────────────────────────────────────────────────────────────────
# TestMaterializeBlock
# ─────────────────────────────────────────────────────────────────────────────

class TestMaterializeBlock:
    def test_slope_basic(self):
        event = MAT.materialize_block(
            (10, 64, -5),
            "CarpentersBlocks:blockCarpentersSlope",
            _te(cb_metadata=0),
        )
        assert event.success
        assert event.block_id == "cuttableblocks:carpenter_slope"
        assert event.be_type == "coverable"
        assert event.pos == (10, 64, -5)

    def test_slope_nbt_has_cover_material(self):
        event = MAT.materialize_block(
            (0, 0, 0),
            "CarpentersBlocks:blockCarpentersSlope",
            _te(cover="minecraft:log", damage=0),
        )
        assert '"coverBlock"' in event.nbt_snbt
        assert "minecraft:oak_log" in event.nbt_snbt  # log damage=0 → oak_log

    def test_slope_nbt_has_facing_int(self):
        event = MAT.materialize_block(
            (0, 0, 0),
            "CarpentersBlocks:blockCarpentersSlope",
            _te(),
        )
        assert event.be_type == "coverable"
        assert '"facing"' in event.nbt_snbt
        assert '"shape"' in event.nbt_snbt

    def test_slope_nbt_has_source_id(self):
        event = MAT.materialize_block(
            (0, 0, 0),
            "CarpentersBlocks:blockCarpentersSlope",
            _te(cb_metadata=4),
        )
        assert '"sourceCarpentersTeId"' in event.nbt_snbt
        assert "blockCarpentersSlope" in event.nbt_snbt

    def test_stairs_be_type(self):
        event = MAT.materialize_block(
            (0, 0, 0),
            "CarpentersBlocks:blockCarpentersStairs",
            _te(cb_metadata=0),
        )
        assert event.be_type == "coverable"
        assert event.block_id == "cuttableblocks:carpenter_stairs"

    def test_collapsible_be_type(self):
        event = MAT.materialize_block(
            (0, 0, 0),
            "CarpentersBlocks:blockCarpentersCollapsibleBlock",
            _te(cb_metadata=0),
        )
        assert event.be_type == "collapsible"
        assert event.block_id == "cuttableblocks:collapsible_block"

    def test_collapsible_has_quad_depths(self):
        # cbMetadata bits: depth XZPP = 16 (bits 7:3 = 16 << 3 = 128)
        # All max: bits 7:3=11111=31? No wait - bits 7:3 store value 0..16 so max is 16
        # Let's encode: XZPP=16 → bits[7:3] = 16 → raw bits = 16 << 3 = 128
        meta = (16 << 3)  # XZPP depth = 16, others = 0, dir = 0
        event = MAT.materialize_block(
            (0, 0, 0),
            "CarpentersBlocks:blockCarpentersCollapsibleBlock",
            _te(cb_metadata=meta),
        )
        assert '"quadDepths"' in event.nbt_snbt
        assert "[I;" in event.nbt_snbt

    def test_hatch_be_type(self):
        event = MAT.materialize_block(
            (0, 0, 0),
            "CarpentersBlocks:blockCarpentersHatch",
            _te(),
        )
        assert event.be_type == "hatch"

    def test_door_be_type(self):
        event = MAT.materialize_block(
            (0, 0, 0),
            "CarpentersBlocks:blockCarpentersDoor",
            _te(),
        )
        assert event.be_type == "door"

    def test_lever_be_type(self):
        event = MAT.materialize_block(
            (0, 0, 0),
            "CarpentersBlocks:blockCarpentersLever",
            _te(),
        )
        assert event.be_type == "lever"

    def test_button_be_type(self):
        event = MAT.materialize_block(
            (0, 0, 0),
            "CarpentersBlocks:blockCarpentersButton",
            _te(),
        )
        assert event.be_type == "button"

    def test_flower_pot_be_type(self):
        event = MAT.materialize_block(
            (0, 0, 0),
            "CarpentersBlocks:blockCarpentersFlowerPot",
            _te(),
        )
        assert event.be_type == "flower_pot"

    def test_bed_be_type(self):
        event = MAT.materialize_block(
            (0, 0, 0),
            "CarpentersBlocks:blockCarpentersBed",
            _te(),
        )
        assert event.be_type == "multiblock"
        assert event.block_id == "cuttableblocks:carpenter_bed"

    def test_garage_door_be_type(self):
        event = MAT.materialize_block(
            (0, 0, 0),
            "CarpentersBlocks:blockCarpentersGarageDoor",
            _te(),
        )
        assert event.be_type == "multiblock"

    def test_unknown_block_fails(self):
        event = MAT.materialize_block(
            (0, 0, 0),
            "UnknownMod:someBlock",
            _te(),
        )
        assert not event.success
        assert event.block_id == "minecraft:air"
        assert event.nbt_snbt is None
        assert any("CB-E-" in e for e in event.errors)


# ─────────────────────────────────────────────────────────────────────────────
# TestSetblockCommand
# ─────────────────────────────────────────────────────────────────────────────

class TestSetblockCommand:
    def test_command_format(self):
        event = MAT.materialize_block(
            (10, 64, -5),
            "CarpentersBlocks:blockCarpentersSlope",
            _te(),
        )
        cmd = event.to_setblock_command()
        assert cmd.startswith("setblock 10 64 -5 cuttableblocks:carpenter_slope")
        assert cmd.endswith(" replace")

    def test_command_has_nbt(self):
        event = MAT.materialize_block(
            (0, 0, 0),
            "CarpentersBlocks:blockCarpentersSlope",
            _te(),
        )
        cmd = event.to_setblock_command()
        assert "{" in cmd  # NBT present
        assert '"coverBlock"' in cmd

    def test_failed_event_command(self):
        event = MAT.materialize_block(
            (1, 2, 3),
            "BadMod:block",
            _te(),
        )
        cmd = event.to_setblock_command()
        assert "minecraft:air" in cmd
        assert cmd.endswith(" replace")

    def test_command_has_blockstate_props_in_block_string(self):
        """Block string MUST contain '[' with blockstate props for 1.18.2."""
        event = MAT.materialize_block(
            (0, 0, 0),
            "CarpentersBlocks:blockCarpentersSlope",
            _te(),
        )
        cmd = event.to_setblock_command()
        block_part = cmd.split("{")[0]  # before NBT
        assert "[" in block_part
        assert "slope_type=" in block_part


# ─────────────────────────────────────────────────────────────────────────────
# TestMaterializeBulk
# ─────────────────────────────────────────────────────────────────────────────

class TestMaterializeBulk:
    def test_bulk_all_18_blocks(self):
        blocks = [
            {"pos": (i, 64, 0), "block_id": bid, "nbt": _te()}
            for i, bid in enumerate([
                "CarpentersBlocks:blockCarpentersSlope",
                "CarpentersBlocks:blockCarpentersStairs",
                "CarpentersBlocks:blockCarpentersBlock",
                "CarpentersBlocks:blockCarpentersCollapsibleBlock",
                "CarpentersBlocks:blockCarpentersBarrier",
                "CarpentersBlocks:blockCarpentersGate",
                "CarpentersBlocks:blockCarpentersHatch",
                "CarpentersBlocks:blockCarpentersDoor",
                "CarpentersBlocks:blockCarpentersLadder",
                "CarpentersBlocks:blockCarpentersLever",
                "CarpentersBlocks:blockCarpentersButton",
                "CarpentersBlocks:blockCarpentersPressurePlate",
                "CarpentersBlocks:blockCarpentersTorch",
                "CarpentersBlocks:blockCarpentersDaylightSensor",
                "CarpentersBlocks:blockCarpentersSafe",
                "CarpentersBlocks:blockCarpentersFlowerPot",
                "CarpentersBlocks:blockCarpentersBed",
                "CarpentersBlocks:blockCarpentersGarageDoor",
            ])
        ]
        events = MAT.materialize_bulk(blocks)
        assert len(events) == 18
        assert all(e.success for e in events)

    def test_bulk_empty(self):
        assert MAT.materialize_bulk([]) == []

    def test_to_setblock_commands_filters_failed(self):
        blocks = [
            {"pos": (0, 64, 0), "block_id": "CarpentersBlocks:blockCarpentersSlope", "nbt": _te()},
            {"pos": (1, 64, 0), "block_id": "BadMod:badBlock", "nbt": _te()},
        ]
        events = MAT.materialize_bulk(blocks)
        cmds = MAT.to_setblock_commands(events)
        assert len(cmds) == 1
        assert "cuttableblocks:carpenter_slope" in cmds[0]

    def test_to_setblock_commands_include_failed(self):
        blocks = [
            {"pos": (0, 64, 0), "block_id": "CarpentersBlocks:blockCarpentersSlope", "nbt": _te()},
            {"pos": (1, 64, 0), "block_id": "BadMod:badBlock", "nbt": _te()},
        ]
        events = MAT.materialize_bulk(blocks)
        cmds = MAT.to_setblock_commands(events, include_failed=True)
        assert len(cmds) == 2
        assert "minecraft:air" in cmds[1]


# ─────────────────────────────────────────────────────────────────────────────
# TestStats
# ─────────────────────────────────────────────────────────────────────────────

class TestStats:
    def test_stats_basic(self):
        blocks = [
            {"pos": (0, 64, 0), "block_id": "CarpentersBlocks:blockCarpentersSlope", "nbt": _te()},
            {"pos": (1, 64, 0), "block_id": "CarpentersBlocks:blockCarpentersCollapsibleBlock", "nbt": _te()},
            {"pos": (2, 64, 0), "block_id": "BadMod:block", "nbt": _te()},
        ]
        events = MAT.materialize_bulk(blocks)
        s = MAT.stats(events)
        assert s["total"] == 3
        assert s["success"] == 2
        assert s["failed"] == 1
        assert s["by_be_type"]["coverable"] == 1
        assert s["by_be_type"]["collapsible"] == 1
        assert s["by_be_type"]["error"] == 1


# ─────────────────────────────────────────────────────────────────────────────
# TestBeTypeMapping — weryfikacja kompletności tabeli
# ─────────────────────────────────────────────────────────────────────────────

class TestBeTypeMapping:
    def test_all_18_blocks_have_be_type(self):
        from ..materializer import _CB_BLOCK_TO_BE_TYPE
        from ..mappings.block_ids import ALL_CB_BLOCK_IDS_1710
        for block_id in ALL_CB_BLOCK_IDS_1710:
            # ALL_CB_BLOCK_IDS_1710 already contains full IDs e.g. "CarpentersBlocks:blockCarpentersSlope"
            assert block_id in _CB_BLOCK_TO_BE_TYPE, \
                f"{block_id} missing from _CB_BLOCK_TO_BE_TYPE"

    def test_be_types_are_valid_values(self):
        from ..materializer import _CB_BLOCK_TO_BE_TYPE
        valid = {"coverable", "collapsible", "hatch", "door", "lever",
                 "button", "flower_pot", "multiblock"}
        for block_id, be_type in _CB_BLOCK_TO_BE_TYPE.items():
            assert be_type in valid, f"{block_id} has unknown beType '{be_type}'"
