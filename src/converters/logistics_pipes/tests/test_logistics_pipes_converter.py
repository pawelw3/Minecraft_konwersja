import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))

from converters.logistics_pipes.logistics_pipes_converter import LogisticsPipesConverter
from converters.router import convert_te_to_events, detect_mod


def test_provider_pipe_to_pretty_pipe_with_extraction_module() -> None:
    conv = LogisticsPipesConverter()
    result = conv.convert_tile_entity(
        te_id="logisticspipes.pipes.basic.LogisticsTileGenericPipe",
        nbt_1710={"id": "logisticspipes.pipes.basic.LogisticsTileGenericPipe", "pipeClass": "PipeItemsProviderLogistics"},
        position=(10, 64, 10),
    )
    assert result.converted.success is True
    assert result.converted.block_id_1182 == "prettypipes:pipe"
    assert result.converted.nbt_1182["modules"]["Items"][0]["id"] == "prettypipes:high_extraction_module"
    assert conv.stats["converted"] == 1


def test_chassis_overflow_warning_is_emitted() -> None:
    conv = LogisticsPipesConverter()
    result = conv.convert_tile_entity(
        te_id="logisticspipes.pipes.basic.LogisticsTileGenericPipe",
        nbt_1710={
            "id": "logisticspipes.pipes.basic.LogisticsTileGenericPipe",
            "pipeClass": "PipeLogisticsChassiMk5",
            "chassi": [
                {"moduleClass": "ModuleProvider"},
                {"moduleClass": "ModuleActiveSupplier"},
                {"moduleClass": "ModuleCrafter"},
                {"moduleClass": "ModulePassiveSupplier"},
            ],
        },
        position=(11, 64, 10),
    )
    assert result.converted.block_id_1182 == "prettypipes:pipe"
    assert len(result.converted.nbt_1182["modules"]["Items"]) == 3
    assert any("CHASSIS-OVERFLOW" in warning for warning in result.converted.warnings)


def test_unknown_numeric_pipe_id_preserves_plain_pipe_and_warns() -> None:
    conv = LogisticsPipesConverter()
    result = conv.convert_tile_entity(
        te_id="logisticspipes.pipes.basic.LogisticsTileGenericPipe",
        nbt_1710={"id": "logisticspipes.pipes.basic.LogisticsTileGenericPipe", "pipeId": 5100},
        position=(12, 64, 10),
    )
    assert result.converted.block_id_1182 == "prettypipes:pipe"
    assert any("DYNAMIC-PIPE-ID" in warning for warning in result.converted.warnings)


def test_real_pipe_id_provider_mk2_uses_lookup() -> None:
    conv = LogisticsPipesConverter()
    result = conv.convert_tile_entity(
        te_id="logisticspipes.pipes.basic.LogisticsTileGenericPipe",
        nbt_1710={"id": "logisticspipes.pipes.basic.LogisticsTileGenericPipe", "pipeId": 8763},
        position=(12, 64, 10),
    )
    assert result.converted.block_id_1182 == "prettypipes:pipe"
    assert result.converted.nbt_1182["modules"]["Items"][0]["id"] == "prettypipes:high_extraction_module"
    assert not any("DYNAMIC-PIPE-ID" in warning for warning in result.converted.warnings)
    assert result.converted.nbt_1182["conversion_source"]["source_pipe_class"] == "PipeItemsProviderLogisticsMk2"


def test_real_pipe_id_request_becomes_item_terminal() -> None:
    conv = LogisticsPipesConverter()
    result = conv.convert_tile_entity(
        te_id="logisticspipes.pipes.basic.LogisticsTileGenericPipe",
        nbt_1710={"id": "logisticspipes.pipes.basic.LogisticsTileGenericPipe", "pipeId": 8750},
        position=(12, 64, 10),
    )
    assert result.converted.block_id_1182 == "prettypipes:item_terminal"
    assert result.converted.nbt_1182["id"] == "prettypipes:item_terminal"


def test_real_pipe_id_request_table_becomes_item_terminal() -> None:
    conv = LogisticsPipesConverter()
    result = conv.convert_tile_entity(
        te_id="logisticspipes.pipes.basic.LogisticsTileGenericPipe",
        nbt_1710={"id": "logisticspipes.pipes.basic.LogisticsTileGenericPipe", "pipeId": 8779},
        position=(12, 64, 10),
    )
    assert result.converted.block_id_1182 == "prettypipes:item_terminal"
    assert result.converted.nbt_1182["conversion_source"]["source_pipe_class"] == "PipeBlockRequestTable"


def test_real_pipe_id_chassis_mk4_is_resolved() -> None:
    conv = LogisticsPipesConverter()
    result = conv.convert_tile_entity(
        te_id="logisticspipes.pipes.basic.LogisticsTileGenericPipe",
        nbt_1710={
            "id": "logisticspipes.pipes.basic.LogisticsTileGenericPipe",
            "pipeId": 8758,
            "chassi": [{"moduleClass": "ModuleProvider"}],
        },
        position=(12, 64, 10),
    )
    assert result.converted.block_id_1182 == "prettypipes:pipe"
    assert result.converted.nbt_1182["conversion_source"]["source_pipe_class"] == "PipeLogisticsChassiMk4"
    assert not any("DYNAMIC-PIPE-ID" in warning for warning in result.converted.warnings)


def test_crafting_table_to_ae2_pattern_provider_shell() -> None:
    conv = LogisticsPipesConverter()
    result = conv.convert_tile_entity(
        te_id="logisticspipes.blocks.crafting.LogisticsCraftingTableTileEntity",
        nbt_1710={"id": "logisticspipes.blocks.crafting.LogisticsCraftingTableTileEntity", "fuzzy": True},
        metadata=4,
        position=(13, 64, 10),
    )
    assert result.converted.block_id_1182 == "ae2:pattern_provider"
    assert result.converted.nbt_1182["id"] == "ae2:pattern_provider"
    assert any("FUZZY-CRAFTING" in warning for warning in result.converted.warnings)


def test_power_provider_to_pressurizer_shell() -> None:
    conv = LogisticsPipesConverter()
    result = conv.convert_tile_entity(
        te_id="logisticspipes.blocks.powertile.LogisticsRFPowerProviderTileEntity",
        nbt_1710={"id": "logisticspipes.blocks.powertile.LogisticsRFPowerProviderTileEntity", "energy": 1200},
        metadata=11,
        position=(14, 64, 10),
    )
    assert result.converted.block_id_1182 == "prettypipes:pressurizer"
    assert result.converted.nbt_1182["energy"] == 1200
    assert any("POWER-NOT-LOSSLESS" in warning for warning in result.converted.warnings)


def test_security_station_to_placeholder() -> None:
    conv = LogisticsPipesConverter()
    result = conv.convert_tile_entity(
        te_id="logisticspipes.blocks.LogisticsSecurityTileEntity",
        nbt_1710={"id": "logisticspipes.blocks.LogisticsSecurityTileEntity", "owner": "legacy"},
        metadata=2,
        position=(15, 64, 10),
    )
    assert result.converted.block_id_1182 == "conversion_placeholders:block_entity_placeholder"
    assert result.converted.nbt_1182["source_te_id"] == "logisticspipes.blocks.LogisticsSecurityTileEntity"


def test_router_detects_and_converts_logistics_pipes() -> None:
    assert detect_mod("logisticspipes.pipes.basic.LogisticsTileGenericPipe") == "logisticspipes"
    events = convert_te_to_events(
        te_nbt={"id": "logisticspipes.pipes.basic.LogisticsTileGenericPipe", "pipeClass": "PipeItemsProviderLogistics"},
        block_numeric_id=0,
        metadata=0,
        global_pos=(16, 64, 10),
    )
    assert events[0]["op"] == "set_block_entity"
    assert events[0]["block"] == "prettypipes:pipe"
    assert events[0]["nbt"]["modules"]["Items"][0]["id"] == "prettypipes:high_extraction_module"
