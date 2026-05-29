from converters.reliquary.block_only_converter import convert_block_only


def test_fertile_lily_pad_maps_directly():
    result = convert_block_only(3192, "xreliquary:lilypad", 0, (0, 64, 0))
    assert result.success
    assert result.target_block == "reliquary:fertile_lily_pad"
    assert result.confidence == "high"


def test_altar_rejected_for_te_path():
    result = convert_block_only(3189, "xreliquary:altar", 0, (0, 64, 0))
    assert not result.success
    assert "REQUIRES-BLOCK-ENTITY" in result.errors[0]
