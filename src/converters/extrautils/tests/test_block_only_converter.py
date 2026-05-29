from converters.extrautils.block_only_converter import convert_block_only


def test_angel_block_maps_directly():
    result = convert_block_only(1955, "ExtraUtilities:angelBlock", 0, (0, 64, 0))
    assert result.success
    assert result.target_block == "angelblockrenewed:angel_block"


def test_colored_block_preserves_legacy_color():
    result = convert_block_only(1963, "ExtraUtilities:colorStoneBrick", 14, (0, 64, 0))
    assert result.success
    assert result.target_block == "minecraft:orange_concrete"
    assert result.confidence == "medium"


def test_filing_cabinet_is_rejected_for_te_path():
    result = convert_block_only(2216, "ExtraUtilities:filing", 4, (0, 64, 0))
    assert not result.success
    assert "REQUIRES-BLOCK-ENTITY" in result.errors[0]


def test_unknown_extrautils_block_never_air():
    result = convert_block_only(1999, "ExtraUtilities:unknownDecor", 3, (0, 64, 0))
    assert result.success
    assert result.target_block != "minecraft:air"
    assert result.confidence == "low"
