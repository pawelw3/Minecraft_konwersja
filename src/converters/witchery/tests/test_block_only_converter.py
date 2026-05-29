from converters.witchery.block_only_converter import convert_block_only


def test_shaded_glass_maps_to_tinted_glass():
    result = convert_block_only(3687, "witchery:shadedglass", 0, (0, 64, 0))
    assert result.success
    assert result.target_block == "minecraft:tinted_glass"


def test_witchery_crop_uses_controlled_fallback():
    result = convert_block_only(3686, "witchery:belladonna", 3, (0, 64, 0))
    assert result.success
    assert result.target_block != "minecraft:air"
    assert result.confidence == "low"


def test_witchery_altar_rejected_for_te_path():
    result = convert_block_only(3841, "witchery:altar", 0, (0, 64, 0))
    assert not result.success
    assert "REQUIRES-BLOCK-ENTITY" in result.errors[0]
