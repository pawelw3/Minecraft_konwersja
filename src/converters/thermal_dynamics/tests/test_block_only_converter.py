from converters.thermal_dynamics.block_only_converter import convert_block_only


def test_structural_duct_maps_to_machine_frame():
    result = convert_block_only(3307, "ThermalDynamics:ThermalDynamics_48", 0, (0, 64, 0))
    assert result.success
    assert result.target_block == "thermal:machine_frame"


def test_transport_duct_maps_to_rail_fallback():
    result = convert_block_only(3308, "ThermalDynamics:ThermalDynamics_64", 1, (0, 64, 0))
    assert result.success
    assert result.target_block == "minecraft:rail"


def test_energy_duct_rejected_for_network_path():
    result = convert_block_only(3304, "ThermalDynamics:ThermalDynamics_0", 0, (0, 64, 0))
    assert not result.success
    assert "REQUIRES-BLOCK-ENTITY" in result.errors[0]
