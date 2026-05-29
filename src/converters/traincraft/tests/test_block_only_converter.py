from converters.traincraft.block_only_converter import convert_block_only


def test_stopper_maps_to_fence():
    result = convert_block_only(550, "tc:stopper", 0, (0, 64, 0))
    assert result.success
    assert result.target_block == "minecraft:oak_fence"


def test_ore_uses_controlled_fallback_not_air():
    result = convert_block_only(553, "tc:oreTC", 5, (0, 64, 0))
    assert result.success
    assert result.target_block != "minecraft:air"


def test_traincraft_rail_rejected_for_track_converter():
    result = convert_block_only(559, "tc:tcRail", 0, (0, 64, 0))
    assert not result.success
    assert "REQUIRES-BLOCK-ENTITY" in result.errors[0]
