"""Testy jednostkowe dla BiggerReactorsConverter."""

from __future__ import annotations

import pytest

from converters.bigreactors.biggerreactors_converter import BiggerReactorsConverter


@pytest.fixture
def converter() -> BiggerReactorsConverter:
    return BiggerReactorsConverter()


class TestConverterBlockMappings:
    def test_reactor_casing(self, converter: BiggerReactorsConverter):
        nbt = {"id": "BRReactorPart", "x": 1, "y": 2, "z": 3}
        result = converter.convert_block("BigReactors:BRReactorPart", metadata=0, nbt_1710=nbt, position=(1, 2, 3))
        assert result.converted.success is True
        assert result.converted.block_id_1182 == "biggerreactors:reactor_casing"
        assert result.converted.nbt_1182 is not None
        assert result.converted.nbt_1182.get("id") == "biggerreactors:reactor_casing"

    def test_reactor_terminal(self, converter: BiggerReactorsConverter):
        result = converter.convert_block("BigReactors:BRReactorPart", metadata=1)
        assert result.converted.block_id_1182 == "biggerreactors:reactor_terminal"

    def test_reactor_control_rod(self, converter: BiggerReactorsConverter):
        result = converter.convert_block("BigReactors:BRReactorPart", metadata=2)
        assert result.converted.block_id_1182 == "biggerreactors:reactor_control_rod"

    def test_reactor_power_tap(self, converter: BiggerReactorsConverter):
        result = converter.convert_block("BigReactors:BRReactorPart", metadata=3)
        assert result.converted.block_id_1182 == "biggerreactors:reactor_power_tap"

    def test_reactor_access_port(self, converter: BiggerReactorsConverter):
        result = converter.convert_block("BigReactors:BRReactorPart", metadata=4)
        assert result.converted.block_id_1182 == "biggerreactors:reactor_access_port"

    def test_reactor_coolant_port(self, converter: BiggerReactorsConverter):
        result = converter.convert_block("BigReactors:BRReactorPart", metadata=5)
        assert result.converted.block_id_1182 == "biggerreactors:reactor_coolant_port"

    def test_reactor_rednet_fallback(self, converter: BiggerReactorsConverter):
        result = converter.convert_block("BigReactors:BRReactorPart", metadata=6)
        assert result.converted.block_id_1182 == "biggerreactors:reactor_redstone_port"
        assert any("RedNet" in w for w in result.converted.warnings)

    def test_reactor_computer_port(self, converter: BiggerReactorsConverter):
        result = converter.convert_block("BigReactors:BRReactorPart", metadata=7)
        assert result.converted.block_id_1182 == "biggerreactors:reactor_computer_port"

    def test_turbine_casing(self, converter: BiggerReactorsConverter):
        result = converter.convert_block("BigReactors:BRTurbinePart", metadata=0)
        assert result.converted.block_id_1182 == "biggerreactors:turbine_casing"

    def test_turbine_terminal(self, converter: BiggerReactorsConverter):
        result = converter.convert_block("BigReactors:BRTurbinePart", metadata=1)
        assert result.converted.block_id_1182 == "biggerreactors:turbine_terminal"

    def test_fuel_rod(self, converter: BiggerReactorsConverter):
        result = converter.convert_block("BigReactors:YelloriumFuelRod", metadata=0)
        assert result.converted.block_id_1182 == "biggerreactors:reactor_fuel_rod"

    def test_uranium_ore(self, converter: BiggerReactorsConverter):
        result = converter.convert_block("BigReactors:YelloriteOre", metadata=0)
        assert result.converted.block_id_1182 == "biggerreactors:uranium_ore"
        assert result.converted.nbt_1182 is None  # no block entity

    def test_metal_blocks(self, converter: BiggerReactorsConverter):
        expected = {
            0: "biggerreactors:uranium_block",
            1: "biggerreactors:cyanite_block",
            2: "biggerreactors:graphite_block",
            3: "biggerreactors:blutonium_block",
            4: "biggerreactors:ludicrite_block",
        }
        for meta, target in expected.items():
            result = converter.convert_block("BigReactors:BRMetalBlock", metadata=meta)
            assert result.converted.block_id_1182 == target, f"meta={meta}"

    def test_creative_removed(self, converter: BiggerReactorsConverter):
        result = converter.convert_block("BigReactors:BRMultiblockCreativePart", metadata=0)
        assert result.converted.block_id_1182 == "minecraft:air"

    def test_cyanite_reprocessor(self, converter: BiggerReactorsConverter):
        result = converter.convert_block("BigReactors:BRDevice", metadata=0)
        assert result.converted.block_id_1182 == "biggerreactors:cyanite_reprocessor"


class TestConverterNBT:
    def test_control_rod_insertion_preserved(self, converter: BiggerReactorsConverter):
        nbt = {"id": "BRReactorControlRod", "x": 10, "y": 64, "z": -5, "controlRodInsertion": 75}
        result = converter.convert_block("BRReactorControlRod", metadata=0, nbt_1710=nbt)
        assert result.converted.success is True
        nbt_out = result.converted.nbt_1182
        assert nbt_out is not None
        assert nbt_out.get("insertion") == 75
        assert nbt_out.get("x") == 10

    def test_access_port_inventory(self, converter: BiggerReactorsConverter):
        nbt = {
            "id": "BRReactorAccessPort",
            "x": 0, "y": 0, "z": 0,
            "Items": [
                {"Slot": 0, "id": "BigReactors:ingotYellorium", "Count": 16},
                {"Slot": 1, "id": "BigReactors:ingotBlutonium", "Count": 4},
            ],
        }
        result = converter.convert_block("BigReactors:BRReactorPart", metadata=4, nbt_1710=nbt)
        nbt_out = result.converted.nbt_1182
        assert nbt_out is not None
        items = nbt_out.get("Items", [])
        assert len(items) == 2
        assert items[0]["id"] == "biggerreactors:uranium_ingot"
        assert items[1]["id"] == "biggerreactors:blutonium_ingot"
        assert any("inventory" in w.lower() for w in result.converted.warnings)

    def test_power_tap_energy(self, converter: BiggerReactorsConverter):
        nbt = {"id": "BRReactorPowerTap", "x": 1, "y": 2, "z": 3, "energyStored": 50000}
        result = converter.convert_block("BRReactorPowerTap", metadata=0, nbt_1710=nbt)
        nbt_out = result.converted.nbt_1182
        assert nbt_out is not None
        assert nbt_out.get("energy") == 50000
        assert any("RF" in w for w in result.converted.warnings)

    def test_reprocessor_full_nbt(self, converter: BiggerReactorsConverter):
        nbt = {
            "id": "BRCyaniteReprocessor",
            "x": 5, "y": 70, "z": 10,
            "energyStored": 1000,
            "cookTime": 42,
            "Items": [
                {"Slot": 0, "id": "BigReactors:ingotCyanite", "Count": 2},
            ],
        }
        result = converter.convert_block("BRCyaniteReprocessor", metadata=0, nbt_1710=nbt)
        nbt_out = result.converted.nbt_1182
        assert nbt_out is not None
        assert nbt_out.get("energy") == 1000
        assert nbt_out.get("progress") == 42
        assert nbt_out["Items"][0]["id"] == "biggerreactors:cyanite_ingot"

    def test_identity_converter_facing(self, converter: BiggerReactorsConverter):
        nbt = {"id": "BRReactorPart", "x": 0, "y": 0, "z": 0, "facing": 3}
        result = converter.convert_block("BigReactors:BRReactorPart", metadata=0, nbt_1710=nbt)
        nbt_out = result.converted.nbt_1182
        assert nbt_out is not None
        assert nbt_out.get("facing") == 3

    def test_no_nbt_for_simple_block(self, converter: BiggerReactorsConverter):
        result = converter.convert_block("BigReactors:BRMetalBlock", metadata=0)
        assert result.converted.nbt_1182 is None


class TestConverterTEByID:
    def test_te_id_without_block_id(self, converter: BiggerReactorsConverter):
        result = converter.convert_tile_entity("BRReactorPowerTap", nbt_1710={"id": "BRReactorPowerTap"}, metadata=0)
        assert result.converted.success is True
        assert result.converted.block_id_1182 == "biggerreactors:reactor_power_tap"

    def test_te_fuel_rod(self, converter: BiggerReactorsConverter):
        result = converter.convert_tile_entity("BRFuelRod", nbt_1710={"id": "BRFuelRod"}, metadata=0)
        assert result.converted.block_id_1182 == "biggerreactors:reactor_fuel_rod"


class TestConverterItems:
    def test_item_yellorium(self, converter: BiggerReactorsConverter):
        result = converter.convert_item("BigReactors:ingotYellorium")
        assert result.block_id_1182 == "biggerreactors:uranium_ingot"

    def test_item_unknown(self, converter: BiggerReactorsConverter):
        result = converter.convert_item("SomeOtherMod:item")
        assert result.block_id_1182 == "SomeOtherMod:item"


class TestConverterStats:
    def test_stats_increment(self, converter: BiggerReactorsConverter):
        converter.convert_block("BigReactors:BRReactorPart", metadata=0)
        assert converter.stats["processed"] == 1
        assert converter.stats["converted"] == 1

    def test_stats_failed(self, converter: BiggerReactorsConverter):
        converter.convert_block("BigReactors:UnknownBlock", metadata=0)
        assert converter.stats["processed"] == 1
        assert converter.stats["failed"] == 1


class TestConverterToDict:
    def test_to_dict(self, converter: BiggerReactorsConverter):
        result = converter.convert_block("BigReactors:BRReactorPart", metadata=0, position=(1, 2, 3))
        d = result.to_dict()
        assert d["original_id"] == "BigReactors:BRReactorPart"
        assert d["metadata"] == 0
        assert d["new_id"] == "biggerreactors:reactor_casing"
        assert d["original_pos"] == (1, 2, 3)
