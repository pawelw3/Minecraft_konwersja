from converters.ic2.block_only_converter import convert_block_only


def test_copper_ore_maps_to_vanilla():
    result = convert_block_only(466, "IC2:blockOreCopper", 0, (0, 64, 0))
    assert result.success
    assert result.target_block == "minecraft:copper_ore"


def test_metal_metadata_maps_deterministically():
    result = convert_block_only(485, "IC2:blockMetal", 2, (0, 64, 0))
    assert result.success
    assert result.target_block == "indreb:tin_block"


def test_machine_is_rejected_for_te_path():
    result = convert_block_only(497, "IC2:blockMachine", 3, (0, 64, 0))
    assert not result.success
    assert "REQUIRES-BLOCK-ENTITY" in result.errors[0]


def test_unknown_ic2_block_never_air():
    result = convert_block_only(9999, "IC2:blockMystery", 6, (0, 64, 0))
    assert result.success
    assert result.target_block != "minecraft:air"
    assert result.confidence == "low"
