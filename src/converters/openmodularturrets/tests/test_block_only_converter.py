from converters.openmodularturrets.block_only_converter import convert_block_only


def test_hard_wall_maps_to_defensive_fallback():
    result = convert_block_only(4013, "openmodularturrets:hardWallTierOne", 0, (0, 64, 0))
    assert result.success
    assert result.target_block == "minecraft:obsidian"


def test_fence_maps_to_iron_bars():
    result = convert_block_only(4001, "openmodularturrets:fenceTierOne", 0, (0, 64, 0))
    assert result.success
    assert result.target_block == "minecraft:iron_bars"


def test_turret_base_rejected_for_te_path():
    result = convert_block_only(3999, "openmodularturrets:baseTierWood", 0, (0, 64, 0))
    assert not result.success
    assert "REQUIRES-BLOCK-ENTITY" in result.errors[0]
