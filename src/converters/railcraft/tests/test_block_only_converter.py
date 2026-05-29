from converters.railcraft.block_only_converter import convert_block_only


def test_railcraft_lantern_maps_to_vanilla_lantern():
    result = convert_block_only(1495, "Railcraft:lantern.stone", 0, (0, 64, 0))
    assert result.success
    assert result.target_block == "minecraft:lantern"


def test_railcraft_brick_uses_material_fallback():
    result = convert_block_only(1504, "Railcraft:brick.nether", 3, (0, 64, 0))
    assert result.success
    assert result.target_block == "minecraft:nether_bricks"


def test_railcraft_machine_rejected_for_te_path():
    result = convert_block_only(1489, "Railcraft:machine.beta", 0, (0, 64, 0))
    assert not result.success
    assert "REQUIRES-BLOCK-ENTITY" in result.errors[0]
