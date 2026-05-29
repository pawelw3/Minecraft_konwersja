from converters.jammyfurniture.block_only_converter import convert_block_only


def test_supplementaries_target_is_kept_when_installed():
    result = convert_block_only(2697, "JammyFurniture:WoodBlocksOne", 0, (0, 64, 0))
    assert result.success
    assert result.target_block == "supplementaries:clock_block"


def test_missing_target_mod_falls_back_to_placeholder():
    result = convert_block_only(2710, "JammyFurniture:ArmChair", 0, (0, 64, 0))
    assert result.success
    assert result.target_block == "conversion_placeholders:block_entity_placeholder"
    assert result.confidence == "low"


def test_inventory_mapping_is_rejected_for_te_path():
    result = convert_block_only(2698, "JammyFurniture:WoodBlocksTwo", 0, (0, 64, 0))
    assert not result.success
    assert "REQUIRES-INVENTORY" in result.errors[0]


def test_unknown_jammy_block_never_air():
    result = convert_block_only(9999, "JammyFurniture:UnknownBlock", 9, (0, 64, 0))
    assert result.success
    assert result.target_block != "minecraft:air"
