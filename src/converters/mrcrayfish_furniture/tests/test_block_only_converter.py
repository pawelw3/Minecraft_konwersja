from converters.mrcrayfish_furniture.block_only_converter import convert_block_only


def test_couch_color_uses_wool_fallback():
    result = convert_block_only(2739, "cfm:couch", 14, (0, 64, 0))
    assert result.success
    assert result.target_block == "minecraft:red_wool"
    assert result.confidence == "medium"


def test_white_glass_maps_to_stained_glass():
    result = convert_block_only(2792, "cfm:whiteGlass", 0, (0, 64, 0))
    assert result.success
    assert result.target_block == "minecraft:white_stained_glass"


def test_unknown_cfm_never_air():
    result = convert_block_only(9999, "cfm:definitely_missing", 0, (0, 64, 0))
    assert result.success
    assert result.target_block != "minecraft:air"
