from converters.projectred.block_only_converter import convert_block_only


def test_projectred_ore_maps_to_projectred_target():
    result = convert_block_only(
        3575,
        "ProjRed|Exploration:projectred.exploration.ore",
        0,
        (0, 64, 0),
    )
    assert result.success
    assert result.target_block == "projectred_exploration:ruby_ore"


def test_projectred_wall_uses_vanilla_wall_fallback():
    result = convert_block_only(
        3577,
        "ProjRed|Exploration:projectred.exploration.stonewalls",
        2,
        (0, 64, 0),
    )
    assert result.success
    assert result.target_block == "minecraft:blackstone_wall"


def test_projectred_machine_rejected_for_te_path():
    result = convert_block_only(
        584,
        "ProjRed|Expansion:projectred.expansion.machine2",
        0,
        (0, 64, 0),
    )
    assert not result.success
    assert "REQUIRES-BLOCK-ENTITY" in result.errors[0]
