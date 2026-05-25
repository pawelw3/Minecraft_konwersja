from converters.router import convert_te_to_events
from converters.thermal_dynamics.mappings import get_mapping_for_te_id
from converters.thermal_dynamics.thermal_dynamics_converter import ThermalDynamicsConverter


def test_te_id_lookup_uses_default_metadata_for_specific_te():
    assert get_mapping_for_te_id("thermaldynamics.ItemDuctEnder").target_block_id == "mekanism:elite_logistical_transporter"
    assert get_mapping_for_te_id("thermaldynamics.FluidDuctSuper").target_block_id == "thermal:fluid_duct_windowed"


def test_convert_tile_entity_uses_resolved_mapping_metadata():
    converter = ThermalDynamicsConverter()

    ender = converter.convert_tile_entity(
        "thermaldynamics.ItemDuctEnder",
        {"id": "thermaldynamics.ItemDuctEnder", "x": 1, "y": 2, "z": 3},
        metadata=0,
        position=(1, 2, 3),
    )
    super_fluid = converter.convert_tile_entity(
        "thermaldynamics.FluidDuctSuper",
        {"id": "thermaldynamics.FluidDuctSuper", "x": 1, "y": 2, "z": 4},
        metadata=0,
        position=(1, 2, 4),
    )

    assert ender.converted.block_id_1182 == "mekanism:elite_logistical_transporter"
    assert ender.converted.nbt_1182["id"] == "mekanism:elite_logistical_transporter"
    assert super_fluid.converted.block_id_1182 == "thermal:fluid_duct_windowed"
    assert super_fluid.converted.nbt_1182["id"] == "thermal:fluid_duct_windowed"


def test_router_thermal_dynamics_preserves_specific_te_target_and_nbt_id():
    events = convert_te_to_events(
        {"id": "thermaldynamics.ItemDuctEnder", "x": 1, "y": 2, "z": 3},
        block_numeric_id=0,
        metadata=0,
        global_pos=(1, 2, 3),
    )

    assert events[0]["block"] == "mekanism:elite_logistical_transporter"
    assert events[0]["nbt"]["id"] == "mekanism:elite_logistical_transporter"
