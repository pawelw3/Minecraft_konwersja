from converters.common.placeholders import PLACEHOLDER_BLOCK_ID
from src.converters.chisel.chisel_converter import ChiselConverter
from src.converters.chisel.mappings import DynamicChiselIdEntry


def test_convert_named_chisel_family_to_visual_rechiseled_target():
    converter = ChiselConverter()

    result = converter.convert_block("chisel:andesite", metadata=2, position=(1, 64, 2))
    events = converter.to_events(result)

    assert result.converted.success
    assert result.converted.block_id_1182.startswith(("rechiseled:andesite_", "minecraft:polished_andesite"))
    assert events[0]["op"] == "set_block"
    assert events[0]["pos"] == [1, 64, 2]
    assert events[0]["block"] == result.converted.block_id_1182
    assert any("VISUAL-MAPPING" in warning for warning in result.converted.warnings)


def test_convert_dynamic_numeric_id_uses_family_and_meta_variant_hint():
    converter = ChiselConverter(
        dynamic_id_map={
            2001: DynamicChiselIdEntry(
                numeric_id=2001,
                family="factory",
                meta_variants={7: "rust_plate"},
            )
        }
    )

    result = converter.convert_block(2001, metadata=7, position=(0, 70, 0))

    assert result.converted.success
    assert result.converted.block_id_1182 in {
        "rechiseled:iron_block_plating",
        "rechiseled:iron_block_bricks",
        "minecraft:stone",
    }
    assert result.original_id == "2001"


def test_unknown_numeric_id_is_rejected_without_dynamic_map():
    converter = ChiselConverter()

    result = converter.convert_block(9999, metadata=0, position=(0, 64, 0))

    assert not result.converted.success
    assert result.converted.errors == ["CHISEL-E-NOT-CHISEL-BLOCK: 9999 meta=0"]


def test_non_chisel_block_is_rejected():
    converter = ChiselConverter()

    result = converter.convert_block("minecraft:stone", metadata=0)

    assert not result.converted.success
    assert result.converted.errors == ["CHISEL-E-NOT-CHISEL-BLOCK: minecraft:stone meta=0"]


def test_tile_entity_becomes_data_rescue_placeholder():
    converter = ChiselConverter()
    nbt = {
        "id": "TileEntityAutoChisel",
        "x": 10,
        "y": 64,
        "z": -3,
        "Items": [{"id": "chisel:stone_raw", "Count": 12, "Slot": 0}],
    }

    result = converter.convert_tile_entity("TileEntityAutoChisel", nbt, metadata=0, position=(10, 64, -3))
    events = converter.to_events(result)

    assert result.converted.success
    assert events[0]["op"] == "set_block_entity"
    assert events[0]["block"] == PLACEHOLDER_BLOCK_ID or events[0]["block"].endswith("inventory_placeholder")
    assert events[0]["nbt"]["original_nbt"]["Items"][0]["id"] == "chisel:stone_raw"
    assert events[0]["nbt"]["extra"]["recommended_manual_action"].startswith("Recover input/output")


def test_convert_block_with_chisel_te_dispatches_to_placeholder():
    converter = ChiselConverter()
    nbt = {"id": "TileEntityPresent", "gift": "data"}

    result = converter.convert_block("chisel:present", metadata=1, nbt_1710=nbt, position=(3, 4, 5))
    events = converter.to_events(result)

    assert result.converted.success
    assert events[0]["op"] == "set_block_entity"
    assert events[0]["nbt"]["source_te_id"] == "TileEntityPresent"


def test_legacy_present_te_alias_becomes_placeholder():
    converter = ChiselConverter()
    nbt = {"id": "tile.chisel.present", "Items": [{"id": "minecraft:diamond", "Count": 1, "Slot": 0}]}

    result = converter.convert_tile_entity("tile.chisel.present", nbt, metadata=0, position=(4, 65, 6))
    events = converter.to_events(result)

    assert result.converted.success
    assert events[0]["op"] == "set_block_entity"
    assert events[0]["nbt"]["source_te_id"] == "tile.chisel.present"


def test_router_detects_and_converts_chisel_te():
    from converters.router import convert_te_to_events, detect_mod

    te = {"id": "TileEntityAutoChisel", "Items": [{"id": "chisel:stone_raw", "Count": 1}]}

    assert detect_mod("TileEntityAutoChisel") == "chisel"
    events = convert_te_to_events(te, block_numeric_id=0, metadata=0, global_pos=(8, 65, 9))

    assert len(events) == 1
    assert events[0]["op"] == "set_block_entity"
    assert events[0]["pos"] == [8, 65, 9]
    assert events[0]["nbt"]["source_mod"] == "chisel"
    assert events[0]["nbt"]["source_te_id"] == "TileEntityAutoChisel"
