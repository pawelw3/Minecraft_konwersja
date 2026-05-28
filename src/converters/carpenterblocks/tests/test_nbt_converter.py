"""
Testy Zadanie 2: konwerter NBT CarpentersBlocks 1.7.10 -> CuttableBlocks 1.18.2.

Pokrycie:
  - parse_te_base: parsowanie cbAttrList, cbMetadata, cbDesign
  - resolve_cover_material: mapowanie materiałów vanilla
  - CBBlockConverter.convert: wszystkie 18 typów bloków
    * geometria (slope, stairs, slab, collapsible)
    * funkcjonalne (barrier, gate, hatch, door, ladder, lever, button,
                    pressure_plate, torch, daylight_sensor)
    * cover-only (safe, flower_pot, bed, garage_door)
  - Obsługa błędów: nieznany blok, slopeID OOB, brak cover
"""

import pytest
from src.converters.carpenterblocks.nbt_converter import (
    CBBlockConverter,
    CBConversionResult,
    parse_te_base,
    ParsedTEBase,
)
from src.converters.carpenterblocks.mappings.cover_materials import resolve_cover_material


# -------------------------------------------------------------------
# Helpery budujące syntetyczne NBT
# -------------------------------------------------------------------

def _attr(attr_id: int, cb_unique_id: str, damage: int = 0) -> dict:
    """Buduje wpis cbAttrList jak TEBase.writeToNBT."""
    return {
        "cbAttribute": attr_id,
        "cbUniqueId": cb_unique_id,
        "Damage": damage,
        "Count": 1,
    }


def _base_te(
    cb_metadata: int = 0,
    cover_base: str = "minecraft:oak_planks",
    cover_damage: int = 0,
    cb_design: str = "",
) -> dict:
    """Buduje minimalny NBT TEBase z base cover[6]."""
    return {
        "cbMetadata": cb_metadata,
        "cbDesign": cb_design,
        "cbOwner": "",
        "cbAttrList": [_attr(6, cover_base, cover_damage)],
    }


CONVERTER = CBBlockConverter()


# -------------------------------------------------------------------
# resolve_cover_material
# -------------------------------------------------------------------

class TestResolveCoverMaterial:
    def test_oak_log(self):
        assert resolve_cover_material("minecraft:log", 0) == "minecraft:oak_log"

    def test_spruce_log(self):
        assert resolve_cover_material("minecraft:log", 1) == "minecraft:spruce_log"

    def test_jungle_log(self):
        assert resolve_cover_material("minecraft:log", 3) == "minecraft:jungle_log"

    def test_log2_acacia(self):
        assert resolve_cover_material("minecraft:log2", 0) == "minecraft:acacia_log"

    def test_oak_planks(self):
        assert resolve_cover_material("minecraft:planks", 0) == "minecraft:oak_planks"

    def test_dark_oak_planks(self):
        assert resolve_cover_material("minecraft:planks", 5) == "minecraft:dark_oak_planks"

    def test_stone_variants(self):
        assert resolve_cover_material("minecraft:stone", 0) == "minecraft:stone"
        assert resolve_cover_material("minecraft:stone", 1) == "minecraft:granite"
        assert resolve_cover_material("minecraft:stone", 3) == "minecraft:diorite"

    def test_wool_white(self):
        assert resolve_cover_material("minecraft:wool", 0) == "minecraft:white_wool"

    def test_wool_black(self):
        assert resolve_cover_material("minecraft:wool", 15) == "minecraft:black_wool"

    def test_stained_glass(self):
        assert resolve_cover_material("minecraft:stained_glass", 0) == "minecraft:white_stained_glass"
        assert resolve_cover_material("minecraft:stained_glass", 14) == "minecraft:red_stained_glass"

    def test_hardened_clay(self):
        assert resolve_cover_material("minecraft:hardened_clay", 0) == "minecraft:terracotta"
        assert resolve_cover_material("minecraft:stained_hardened_clay", 2) == "minecraft:magenta_terracotta"

    def test_quartz(self):
        assert resolve_cover_material("minecraft:quartz_block", 2) == "minecraft:quartz_pillar"

    def test_cobblestone_nodamage(self):
        assert resolve_cover_material("minecraft:cobblestone", 0) == "minecraft:cobblestone"

    def test_fallback_damage_zero(self):
        # Nieznana kombinacja damage→0 fallback
        assert resolve_cover_material("minecraft:stone", 99) == "minecraft:stone"

    def test_fallback_minecraft_prefix(self):
        # Nieznany minecraft: blok → zwróć ID bez modyfikacji
        result = resolve_cover_material("minecraft:unknown_block", 0)
        assert result == "minecraft:unknown_block"

    def test_unknown_mod_returns_none(self):
        result = resolve_cover_material("somemod:some_block", 0)
        assert result is None


# -------------------------------------------------------------------
# parse_te_base
# -------------------------------------------------------------------

class TestParseTEBase:
    def test_basic_parse(self):
        nbt = _base_te(cb_metadata=5, cover_base="minecraft:log", cover_damage=1)
        te = parse_te_base(nbt)
        assert te.cb_metadata == 5
        assert te.cb_design == ""
        assert 6 in te.attrs
        assert te.attrs[6].cb_unique_id == "minecraft:log"
        assert te.attrs[6].damage == 1
        assert te.attrs[6].resolved_id == "minecraft:spruce_log"

    def test_base_cover_property(self):
        nbt = _base_te(cover_base="minecraft:planks", cover_damage=2)
        te = parse_te_base(nbt)
        assert te.base_cover is not None
        assert te.base_cover.resolved_id == "minecraft:birch_planks"

    def test_cb_design_preserved(self):
        nbt = _base_te()
        nbt["cbDesign"] = "tile"
        te = parse_te_base(nbt)
        assert te.cb_design == "tile"

    def test_multiple_attrs(self):
        nbt = {
            "cbMetadata": 0,
            "cbDesign": "",
            "cbOwner": "Steve",
            "cbAttrList": [
                _attr(6, "minecraft:planks", 0),   # base cover
                _attr(0, "minecraft:stone", 0),     # cover DOWN
                _attr(7, "minecraft:dye", 0),       # dye DOWN
            ],
        }
        te = parse_te_base(nbt)
        assert len(te.attrs) == 3
        assert 6 in te.attrs
        assert 0 in te.attrs
        assert 7 in te.attrs

    def test_illuminator_attr(self):
        nbt = _base_te()
        nbt["cbAttrList"].append(_attr(21, "minecraft:glowstone", 0))
        te = parse_te_base(nbt)
        assert te.has_illuminator is True

    def test_empty_attrs(self):
        nbt = {"cbMetadata": 0, "cbDesign": "", "cbOwner": "", "cbAttrList": []}
        te = parse_te_base(nbt)
        assert te.base_cover is None

    def test_no_namespace_unique_id(self):
        # Stary format bez ":" w cbUniqueId
        nbt = {
            "cbMetadata": 0, "cbDesign": "", "cbOwner": "",
            "cbAttrList": [{"cbAttribute": 6, "cbUniqueId": "planks", "Damage": 0, "Count": 1}],
        }
        te = parse_te_base(nbt)
        assert te.base_cover.cb_unique_id == "minecraft:planks"


# -------------------------------------------------------------------
# CBBlockConverter - wynik ogólny
# -------------------------------------------------------------------

class TestCBBlockConverterGeneral:
    def test_unknown_block_fails(self):
        result = CONVERTER.convert("SomeMod:unknownBlock", {})
        assert not result.success
        assert any("CB-E-UNKNOWN_BLOCK" in e for e in result.errors)

    def test_known_block_success(self):
        nbt = _base_te(cb_metadata=9)  # slope: slopeID=9 = WEDGE_POS_S
        result = CONVERTER.convert("CarpentersBlocks:blockCarpentersSlope", nbt)
        assert result.success
        assert result.block_id_1182 == "cuttableblocks:carpenter_slope"

    def test_cover_material_in_nbt(self):
        nbt = _base_te(cover_base="minecraft:planks", cover_damage=3)
        result = CONVERTER.convert("CarpentersBlocks:blockCarpentersSlope", nbt)
        assert result.nbt_1182["coverBlock"] == "minecraft:jungle_planks"

    def test_no_cover_warning(self):
        nbt = {"cbMetadata": 0, "cbDesign": "", "cbOwner": "", "cbAttrList": []}
        result = CONVERTER.convert("CarpentersBlocks:blockCarpentersBlock", nbt)
        assert any("CB-W-NO_COVER" in w for w in result.warnings)
        assert result.nbt_1182["coverBlock"] == "minecraft:oak_planks"  # fallback

    def test_design_in_nbt(self):
        nbt = _base_te()
        nbt["cbDesign"] = "tile"
        result = CONVERTER.convert("CarpentersBlocks:blockCarpentersBlock", nbt)
        assert result.nbt_1182.get("cbDesign") == "tile"

    def test_illuminator_in_nbt(self):
        nbt = _base_te()
        nbt["cbAttrList"].append(_attr(21, "minecraft:glowstone"))
        result = CONVERTER.convert("CarpentersBlocks:blockCarpentersBlock", nbt)
        assert result.nbt_1182.get("illuminator") is True

    def test_side_covers_in_nbt(self):
        nbt = _base_te()
        nbt["cbAttrList"].append(_attr(0, "minecraft:stone", 0))  # cover DOWN
        result = CONVERTER.convert("CarpentersBlocks:blockCarpentersBlock", nbt)
        assert "sideCovers" in result.nbt_1182
        assert result.nbt_1182["sideCovers"][0] == "minecraft:stone"


# -------------------------------------------------------------------
# Slope
# -------------------------------------------------------------------

class TestSlopeConverter:
    def test_wedge_pos_n(self):
        result = CONVERTER.convert("CarpentersBlocks:blockCarpentersSlope", _base_te(8))
        assert result.blockstate_props["slope_type"] == "wedge"
        assert result.blockstate_props["facing"] == "north"
        assert result.blockstate_props["half"] == "top"

    def test_wedge_neg_s(self):
        result = CONVERTER.convert("CarpentersBlocks:blockCarpentersSlope", _base_te(5))
        assert result.blockstate_props["half"] == "bottom"
        assert result.blockstate_props["facing"] == "south"

    def test_wedge_side_se(self):
        result = CONVERTER.convert("CarpentersBlocks:blockCarpentersSlope", _base_te(0))
        assert result.blockstate_props["slope_type"] == "wedge_side"
        assert result.blockstate_props["facing"] == "south_east"

    def test_prism_4p(self):
        result = CONVERTER.convert("CarpentersBlocks:blockCarpentersSlope", _base_te(60))
        assert result.blockstate_props["slope_type"] == "prism_4p"
        assert result.blockstate_props["facing"] == "all"

    def test_slope_id_oob_error(self):
        result = CONVERTER.convert("CarpentersBlocks:blockCarpentersSlope", _base_te(99))
        assert any("CB-E-GEOM_OOB" in e for e in result.errors)


# -------------------------------------------------------------------
# Stairs
# -------------------------------------------------------------------

class TestStairsConverter:
    def test_straight_bottom_north(self):
        result = CONVERTER.convert("CarpentersBlocks:blockCarpentersStairs", _base_te(4))
        assert result.blockstate_props["facing"] == "north"
        assert result.blockstate_props["half"] == "bottom"
        assert result.blockstate_props["shape"] == "straight"

    def test_inner_pos_nw(self):
        result = CONVERTER.convert("CarpentersBlocks:blockCarpentersStairs", _base_te(17))
        assert result.blockstate_props["half"] == "top"
        assert result.blockstate_props["shape"] == "inner_left"

    def test_outer_neg_se(self):
        result = CONVERTER.convert("CarpentersBlocks:blockCarpentersStairs", _base_te(20))
        assert result.blockstate_props["half"] == "bottom"
        assert result.blockstate_props["shape"] == "outer_right"

    def test_side_nw(self):
        result = CONVERTER.convert("CarpentersBlocks:blockCarpentersStairs", _base_te(1))
        assert result.blockstate_props["shape"] == "side_nw"

    def test_stairs_id_oob_error(self):
        result = CONVERTER.convert("CarpentersBlocks:blockCarpentersStairs", _base_te(50))
        assert any("CB-E-GEOM_OOB" in e for e in result.errors)


# -------------------------------------------------------------------
# Block (slab)
# -------------------------------------------------------------------

class TestBlockConverter:
    def test_full_block(self):
        result = CONVERTER.convert("CarpentersBlocks:blockCarpentersBlock", _base_te(0))
        assert result.blockstate_props["type"] == "double"
        assert result.blockstate_props["axis"] == "y"

    def test_slab_y_bottom(self):
        result = CONVERTER.convert("CarpentersBlocks:blockCarpentersBlock", _base_te(3))
        assert result.blockstate_props["type"] == "bottom"
        assert result.blockstate_props["axis"] == "y"

    def test_slab_y_top(self):
        result = CONVERTER.convert("CarpentersBlocks:blockCarpentersBlock", _base_te(4))
        assert result.blockstate_props["type"] == "top"
        assert result.blockstate_props["axis"] == "y"

    def test_slab_x_neg(self):
        result = CONVERTER.convert("CarpentersBlocks:blockCarpentersBlock", _base_te(1))
        assert result.blockstate_props["type"] == "bottom"
        assert result.blockstate_props["axis"] == "x"


# -------------------------------------------------------------------
# Collapsible
# -------------------------------------------------------------------

class TestCollapsibleConverter:
    def test_all_max_depth(self):
        # Ustaw direction=UP (1), wszystkie quady = 16
        # depth_xzpp  bits 7:3  = 16 = 0b10000 → data |= (16 << 3) = 128
        # depth_xzpn  bits 12:8 = 16 →  data |= (16 << 8) = 4096
        # depth_xznp  bits 17:13 = 16 → data |= (16 << 13) = 131072
        # depth_xznn  bits 22:18 = 16 → data |= (16 << 18) = 4194304
        # direction = UP = 1
        data = 1 | (16 << 3) | (16 << 8) | (16 << 13) | (16 << 18)
        result = CONVERTER.convert("CarpentersBlocks:blockCarpentersCollapsibleBlock", _base_te(data))
        assert result.blockstate_props["facing"] == "up"
        assert result.nbt_1182["quadDepths"] == [16, 16, 16, 16]

    def test_zero_depth(self):
        result = CONVERTER.convert("CarpentersBlocks:blockCarpentersCollapsibleBlock", _base_te(0))
        assert result.nbt_1182["quadDepths"] == [0, 0, 0, 0]

    def test_asymmetric_quads(self):
        # quad XZNN (bits 22:18) = 8, reszta = 0, direction = DOWN (0)
        data = (8 << 18)
        result = CONVERTER.convert("CarpentersBlocks:blockCarpentersCollapsibleBlock", _base_te(data))
        depths = result.nbt_1182["quadDepths"]
        assert depths[0] == 8   # XZNN
        assert depths[1] == 0   # XZNP
        assert depths[2] == 0   # XZPN
        assert depths[3] == 0   # XZPP

    def test_direction_north(self):
        # direction = NORTH = 2
        result = CONVERTER.convert("CarpentersBlocks:blockCarpentersCollapsibleBlock", _base_te(2))
        assert result.blockstate_props["facing"] == "north"


# -------------------------------------------------------------------
# Barrier
# -------------------------------------------------------------------

class TestBarrierConverter:
    def test_vanilla_no_post(self):
        # type=0, post=0
        result = CONVERTER.convert("CarpentersBlocks:blockCarpentersBarrier", _base_te(0))
        assert result.blockstate_props["barrier_type"] == "vanilla"
        assert result.blockstate_props["post"] == "false"

    def test_picket_with_post(self):
        # type=4, post=1 → data = 4 | (1 << 4) = 20
        result = CONVERTER.convert("CarpentersBlocks:blockCarpentersBarrier", _base_te(4 | (1 << 4)))
        assert result.blockstate_props["barrier_type"] == "picket"
        assert result.blockstate_props["post"] == "true"

    def test_wall_type(self):
        result = CONVERTER.convert("CarpentersBlocks:blockCarpentersBarrier", _base_te(6))
        assert result.blockstate_props["barrier_type"] == "wall"


# -------------------------------------------------------------------
# Gate
# -------------------------------------------------------------------

class TestGateConverter:
    def test_vanilla_closed_on_x(self):
        # type=0, dir_open=0, facing=0(X), state=0(closed)
        result = CONVERTER.convert("CarpentersBlocks:blockCarpentersGate", _base_te(0))
        assert result.blockstate_props["gate_type"] == "vanilla"
        assert result.blockstate_props["open"] == "false"
        assert result.blockstate_props["facing"] == "west"

    def test_open_on_z(self):
        # facing=1(Z), state=1(open) → data = (1<<5) | (1<<6) = 96
        result = CONVERTER.convert("CarpentersBlocks:blockCarpentersGate", _base_te(96))
        assert result.blockstate_props["open"] == "true"
        assert result.blockstate_props["facing"] == "north"


# -------------------------------------------------------------------
# Hatch
# -------------------------------------------------------------------

class TestHatchConverter:
    def test_hidden_closed_low_north(self):
        # type=0, pos=0, state=0, dir=0(north), rigid=0
        result = CONVERTER.convert("CarpentersBlocks:blockCarpentersHatch", _base_te(0))
        assert result.blockstate_props["hatch_type"] == "hidden"
        assert result.blockstate_props["facing"] == "north"
        assert result.blockstate_props["half"] == "bottom"
        assert result.blockstate_props["open"] == "false"

    def test_window_open_high_east(self):
        # type=1, pos=1, state=1, dir=3(east) → data = 1|(1<<3)|(1<<4)|(3<<5) = 1+8+16+96 = 121
        data = 1 | (1 << 3) | (1 << 4) | (3 << 5)
        result = CONVERTER.convert("CarpentersBlocks:blockCarpentersHatch", _base_te(data))
        assert result.blockstate_props["hatch_type"] == "window"
        assert result.blockstate_props["facing"] == "east"
        assert result.blockstate_props["half"] == "top"
        assert result.blockstate_props["open"] == "true"

    def test_rigid_in_nbt(self):
        # rigid=1 → data = (1<<7) = 128; FLAG_RIGID = 0x08
        result = CONVERTER.convert("CarpentersBlocks:blockCarpentersHatch", _base_te(128))
        assert result.nbt_1182.get("flags", 0) & 0x08  # FLAG_RIGID


# -------------------------------------------------------------------
# Door
# -------------------------------------------------------------------

class TestDoorConverter:
    def test_panels_closed_bottom_north(self):
        # type=2(panels), hinge=0(left), facing=3(north)→ZN, state=0, piece=0(bottom)
        # data = 2 | (0<<3) | (3<<4) | (0<<6) | (0<<7) = 2 | 48 = 50
        data = 2 | (3 << 4)
        result = CONVERTER.convert("CarpentersBlocks:blockCarpentersDoor", _base_te(data))
        assert result.blockstate_props["door_type"] == "panels"
        assert result.blockstate_props["facing"] == "north"
        assert result.blockstate_props["half"] == "lower"
        assert result.blockstate_props["hinge"] == "left"
        assert result.blockstate_props["open"] == "false"

    def test_open_top_right_hinge(self):
        # state=1(open), piece=1(top), hinge=1(right)
        # data = (1<<3) | (1<<6) | (1<<7) = 8 | 64 | 128 = 200
        data = (1 << 3) | (1 << 6) | (1 << 7)
        result = CONVERTER.convert("CarpentersBlocks:blockCarpentersDoor", _base_te(data))
        assert result.blockstate_props["open"] == "true"
        assert result.blockstate_props["half"] == "upper"
        assert result.blockstate_props["hinge"] == "right"

    def test_rigid_door(self):
        data = 1 << 8
        result = CONVERTER.convert("CarpentersBlocks:blockCarpentersDoor", _base_te(data))
        assert result.nbt_1182.get("flags", 0) & 0x08  # FLAG_RIGID


# -------------------------------------------------------------------
# Ladder
# -------------------------------------------------------------------

class TestLadderConverter:
    def test_default_north(self):
        # dir=NORTH=2, type=DEFAULT=0 → data=2
        result = CONVERTER.convert("CarpentersBlocks:blockCarpentersLadder", _base_te(2))
        assert result.blockstate_props["facing"] == "north"
        assert result.blockstate_props["ladder_type"] == "default"

    def test_rail_east(self):
        # dir=EAST=5, type=RAIL=1 → data = 5 | (1<<3) = 13
        result = CONVERTER.convert("CarpentersBlocks:blockCarpentersLadder", _base_te(5 | (1 << 3)))
        assert result.blockstate_props["facing"] == "east"
        assert result.blockstate_props["ladder_type"] == "rail"


# -------------------------------------------------------------------
# Lever
# -------------------------------------------------------------------

class TestLeverConverter:
    def test_off_wall_north(self):
        # dir=NORTH=2, state=0, polarity=0 → data=2
        result = CONVERTER.convert("CarpentersBlocks:blockCarpentersLever", _base_te(2))
        assert result.blockstate_props["facing"] == "north"
        assert result.blockstate_props["powered"] == "false"
        assert result.blockstate_props["face"] == "wall"

    def test_on_floor(self):
        # dir=UP=1, state=1 → data = 1 | (1<<3) = 9
        result = CONVERTER.convert("CarpentersBlocks:blockCarpentersLever", _base_te(1 | (1 << 3)))
        assert result.blockstate_props["powered"] == "true"
        assert result.blockstate_props["face"] == "floor"

    def test_negative_polarity_in_nbt(self):
        # polarity_neg=1 → data = (1<<4) = 16; FLAG_POLARITY_NEG = 0x10
        result = CONVERTER.convert("CarpentersBlocks:blockCarpentersLever", _base_te(1 << 4))
        assert result.nbt_1182.get("flags", 0) & 0x10  # FLAG_POLARITY_NEG


# -------------------------------------------------------------------
# Button
# -------------------------------------------------------------------

class TestButtonConverter:
    def test_off_wall_east(self):
        result = CONVERTER.convert("CarpentersBlocks:blockCarpentersButton", _base_te(5))
        assert result.blockstate_props["facing"] == "east"
        assert result.blockstate_props["powered"] == "false"

    def test_on_ceiling(self):
        # dir=DOWN=0, state=1 → data = (1<<3) = 8
        result = CONVERTER.convert("CarpentersBlocks:blockCarpentersButton", _base_te(1 << 3))
        assert result.blockstate_props["powered"] == "true"
        assert result.blockstate_props["face"] == "ceiling"


# -------------------------------------------------------------------
# Pressure plate
# -------------------------------------------------------------------

class TestPressurePlateConverter:
    def test_not_powered(self):
        # dir=UP=1, powered=0
        result = CONVERTER.convert("CarpentersBlocks:blockCarpentersPressurePlate", _base_te(1))
        assert result.blockstate_props["facing"] == "up"
        assert result.blockstate_props["powered"] == "false"

    def test_powered(self):
        # dir=UP=1, powered=1 → data = 1|(1<<3) = 9
        result = CONVERTER.convert("CarpentersBlocks:blockCarpentersPressurePlate", _base_te(1 | (1 << 3)))
        assert result.blockstate_props["powered"] == "true"


# -------------------------------------------------------------------
# Torch
# -------------------------------------------------------------------

class TestTorchConverter:
    def test_vanilla_lit_up(self):
        # dir=UP=1, state=LIT=0, type=VANILLA=0 → data=1
        result = CONVERTER.convert("CarpentersBlocks:blockCarpentersTorch", _base_te(1))
        assert result.blockstate_props["facing"] == "up"
        assert result.blockstate_props["lit"] == "true"
        assert result.blockstate_props["torch_type"] == "vanilla"

    def test_unlit_north(self):
        # dir=NORTH=2, state=UNLIT=2 → data = 2 | (2<<3) = 18
        result = CONVERTER.convert("CarpentersBlocks:blockCarpentersTorch", _base_te(2 | (2 << 3)))
        assert result.blockstate_props["lit"] == "false"
        assert result.blockstate_props["facing"] == "north"

    def test_lantern_type(self):
        # type=LANTERN=1, dir=UP=1 → data = 1 | (1<<5) = 33
        result = CONVERTER.convert("CarpentersBlocks:blockCarpentersTorch", _base_te(1 | (1 << 5)))
        assert result.blockstate_props["torch_type"] == "lantern"

    def test_smoldering_in_nbt(self):
        # state=SMOLDERING=1, dir=UP=1 → data = 1 | (1<<3) = 9; FLAG_SMOLDERING = 0x20
        result = CONVERTER.convert("CarpentersBlocks:blockCarpentersTorch", _base_te(1 | (1 << 3)))
        assert result.nbt_1182.get("flags", 0) & 0x20  # FLAG_SMOLDERING


# -------------------------------------------------------------------
# Daylight Sensor
# -------------------------------------------------------------------

class TestDaylightSensorConverter:
    def test_default_positive_dynamic(self):
        # light=0, polarity=0, sensitivity=2(dynamic), dir=UP=1 → data = (1<<7) | (2<<5) = 128+64 = 192
        data = (1 << 7) | (2 << 5)
        result = CONVERTER.convert("CarpentersBlocks:blockCarpentersDaylightSensor", _base_te(data))
        assert result.blockstate_props["inverted"] == "false"
        assert result.blockstate_props["sensitivity"] == "dynamic"
        assert result.blockstate_props["facing"] == "up"

    def test_inverted_sleep(self):
        # polarity=1(neg), sensitivity=0(sleep) → data = (1<<4) = 16
        result = CONVERTER.convert("CarpentersBlocks:blockCarpentersDaylightSensor", _base_te(1 << 4))
        assert result.blockstate_props["inverted"] == "true"
        assert result.blockstate_props["sensitivity"] == "sleep"

    def test_light_level(self):
        # light_level=13 → data=13
        result = CONVERTER.convert("CarpentersBlocks:blockCarpentersDaylightSensor", _base_te(13))
        assert result.blockstate_props["power"] == "13"


# -------------------------------------------------------------------
# Safe (cover-only)
# -------------------------------------------------------------------

class TestSafeConverter:
    def test_safe_cover_material(self):
        nbt = _base_te(cover_base="minecraft:iron_block")
        result = CONVERTER.convert("CarpentersBlocks:blockCarpentersSafe", nbt)
        assert result.success
        assert result.block_id_1182 == "cuttableblocks:carpenter_safe"
        assert result.nbt_1182["coverBlock"] == "minecraft:iron_block"


# -------------------------------------------------------------------
# FlowerPot
# -------------------------------------------------------------------

class TestFlowerPotConverter:
    def test_with_plant(self):
        nbt = _base_te()
        nbt["cbAttrList"].append(_attr(22, "minecraft:tallgrass", 1))
        result = CONVERTER.convert("CarpentersBlocks:blockCarpentersFlowerPot", nbt)
        assert result.success
        assert "plantBlock" in result.nbt_1182


# -------------------------------------------------------------------
# Multiblock (Bed, GarageDoor)
# -------------------------------------------------------------------

class TestMultiblockConverters:
    def test_bed_warning(self):
        result = CONVERTER.convert("CarpentersBlocks:blockCarpentersBed", _base_te(5))
        assert any("CB-W-MULTIBLOCK" in w for w in result.warnings)
        assert result.nbt_1182.get("cbMetadataRaw") == 5

    def test_garage_door_warning(self):
        result = CONVERTER.convert("CarpentersBlocks:blockCarpentersGarageDoor", _base_te(3))
        assert any("CB-W-MULTIBLOCK" in w for w in result.warnings)
        assert result.nbt_1182.get("cbMetadataRaw") == 3

    def test_multiblock_still_has_cover(self):
        nbt = _base_te(cover_base="minecraft:planks", cover_damage=1)
        result = CONVERTER.convert("CarpentersBlocks:blockCarpentersBed", nbt)
        assert result.nbt_1182["coverBlock"] == "minecraft:spruce_planks"


# -------------------------------------------------------------------
# convert_bulk
# -------------------------------------------------------------------

class TestConvertBulk:
    def test_bulk_all_18_blocks(self):
        from src.converters.carpenterblocks.mappings.block_ids import ALL_CB_BLOCK_IDS_1710
        blocks = [(bid, _base_te()) for bid in ALL_CB_BLOCK_IDS_1710]
        results = CONVERTER.convert_bulk(blocks)
        assert len(results) == 18
        for r in results:
            assert r.block_id_1182 is not None, f"Brak block_id_1182 dla {r.block_id_1710}"

    def test_bulk_empty(self):
        assert CONVERTER.convert_bulk([]) == []
