from converters.mekanism.block_only_converter import convert_block_only


def test_ore_maps_to_existing_target():
    result = convert_block_only(2159, "Mekanism:OreBlock", 1, (0, 64, 0))
    assert result.success
    assert result.target_block == "minecraft:copper_ore"
    assert result.confidence in {"medium", "high"}


def test_plastic_metadata_is_deterministic_color_fallback():
    result = convert_block_only(2166, "Mekanism:SlickPlasticBlock", 8, (0, 64, 0))
    assert result.success
    assert result.target_block == "minecraft:gray_concrete"
    assert result.warnings


def test_machine_block_is_rejected_for_te_path():
    result = convert_block_only(2156, "Mekanism:MachineBlock", 3, (0, 64, 0))
    assert not result.success
    assert result.target_block == ""
    assert "REQUIRES-BLOCK-ENTITY" in result.errors[0]


def test_unknown_mekanism_block_never_air():
    result = convert_block_only(9999, "Mekanism:DefinitelyMissing", 9, (0, 64, 0))
    assert result.success
    assert result.target_block != "minecraft:air"
    assert result.confidence == "low"
