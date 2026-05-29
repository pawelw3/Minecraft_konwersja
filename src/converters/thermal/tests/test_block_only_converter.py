from converters.thermal.block_only_converter import convert_block_only


def test_thermal_foundation_ore_maps_directly():
    result = convert_block_only(962, "ThermalFoundation:Ore", 1, (0, 64, 0))
    assert result.success
    assert result.target_block == "thermal:tin_ore"


def test_thermal_rockwool_uses_color_metadata():
    result = convert_block_only(3451, "ThermalExpansion:Rockwool", 14, (0, 64, 0))
    assert result.success
    assert result.target_block == "thermal:red_rockwool"


def test_thermal_machine_rejected_for_te_path():
    result = convert_block_only(3438, "ThermalExpansion:Machine", 1, (0, 64, 0))
    assert not result.success
    assert "REQUIRES-BLOCK-ENTITY" in result.errors[0]
