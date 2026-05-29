from converters.growthcraft.block_only_converter import convert_block_only


def test_bamboo_stalk_uses_safe_vanilla_fallback():
    result = convert_block_only(2598, "Growthcraft|Bamboo:grc.bambooStalk", 3, (0, 64, 0))
    assert result.success
    assert result.target_block == "minecraft:bamboo"
    assert result.confidence == "low"
    assert result.warnings


def test_rice_crop_uses_safe_vanilla_fallback():
    result = convert_block_only(2679, "Growthcraft|Rice:grc.riceBlock", 7, (0, 64, 0))
    assert result.success
    assert result.target_block == "minecraft:wheat"


def test_ferment_barrel_is_rejected_for_te_path():
    result = convert_block_only(2584, "Growthcraft|Cellar:grc.fermentBarrel", 0, (0, 64, 0))
    assert not result.success
    assert "REQUIRES-BLOCK-ENTITY" in result.errors[0]


def test_unknown_growthcraft_block_never_air():
    result = convert_block_only(9999, "Growthcraft|Bamboo:grc.unknown", 1, (0, 64, 0))
    assert result.success
    assert result.target_block != "minecraft:air"
