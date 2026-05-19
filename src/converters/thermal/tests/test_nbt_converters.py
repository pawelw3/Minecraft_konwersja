"""Testy konwerterow NBT Thermal Series."""

import pytest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent.parent))

from converters.thermal.nbt_converters.base_converter import (
    convert_facing,
    convert_tier,
    convert_energy,
    convert_inventory,
    convert_redstone_control,
)
from converters.thermal.nbt_converters.machine_converter import convert_machine_nbt
from converters.thermal.nbt_converters.storage_converter import convert_cell_nbt, convert_tank_nbt
from converters.thermal.nbt_converters.dynamo_converter import convert_dynamo_nbt
from converters.thermal.nbt_converters.duct_converter import convert_energy_duct_nbt, convert_tesseract_nbt


class TestBaseConverters:
    def test_facing_conversion(self):
        assert convert_facing({"Facing": 2}) == "north"
        assert convert_facing({"Facing": 5}) == "east"
        assert convert_facing({}) == "south"

    def test_tier_conversion(self):
        assert convert_tier({"Type": 0}) == "basic"
        assert convert_tier({"Type": 3}) == "resonant"
        assert convert_tier({"Type": 4}) == "creative"

    def test_energy_conversion_int(self):
        result = convert_energy({"Energy": 15000})
        assert result["Stored"] == 15000
        assert result["Capacity"] == 40000

    def test_energy_conversion_dict(self):
        result = convert_energy({"Energy": {"Storage": 8000, "Capacity": 20000}})
        assert result["Stored"] == 8000
        assert result["Capacity"] == 20000

    def test_redstone_control(self):
        assert convert_redstone_control({"RedstoneControl": 0}) == "ignored"
        assert convert_redstone_control({"RedstoneControl": 2}) == "high"

    def test_inventory_conversion(self):
        nbt = {
            "Items": [
                {"Slot": 0, "id": "minecraft:iron_ingot", "Count": 16, "Damage": 0},
                {"Slot": 1, "id": "thermalexpansion:machine_frame", "Count": 1, "Damage": 0},
            ]
        }
        result = convert_inventory(nbt)
        assert len(result) == 2
        assert result[0]["id"] == "minecraft:iron_ingot"
        assert result[1]["id"] == "thermal:machine_frame"


class TestMachineNBTConverter:
    def test_furnace_nbt(self):
        nbt = {
            "id": "thermalexpansion.Furnace",
            "x": 100, "y": 64, "z": 200,
            "Facing": 3,
            "Type": 1,
            "Energy": 20000,
            "Process": 50,
            "ProcessMax": 200,
            "Items": [
                {"Slot": 0, "id": "minecraft:iron_ore", "Count": 8, "Damage": 0},
            ],
            "RedstoneControl": 0,
        }
        result = convert_machine_nbt(nbt, "thermal:machine_furnace")
        assert result["id"] == "thermal:machine_furnace"
        assert result["facing"] == "south"
        assert result["tier"] == "hardened"
        assert result["process"] == 50
        assert len(result["Items"]) == 1
        assert result["redstone_control"] == "ignored"


class TestStorageNBTConverter:
    def test_cell_nbt(self):
        nbt = {
            "id": "thermalexpansion.Cell",
            "x": 10, "y": 64, "z": 10,
            "Type": 2,
            "Energy": 15000000,
            "Send": 8000,
        }
        result = convert_cell_nbt(nbt, "thermal:energy_cell")
        assert result["id"] == "thermal:energy_cell"
        assert result["tier"] == "reinforced"
        assert result["output_rate"] == 8000
        assert result["energy"]["Stored"] == 15000000
        assert "Items" not in result

    def test_tank_nbt(self):
        nbt = {
            "id": "thermalexpansion.Tank",
            "x": 10, "y": 64, "z": 10,
            "Type": 1,
            "Mode": 0,
            "Tank": {"FluidName": "water", "Amount": 2000},
        }
        result = convert_tank_nbt(nbt, "thermal:fluid_cell")
        assert result["id"] == "thermal:fluid_cell"
        assert result["tier"] == "hardened"
        assert result["tank"]["FluidName"] == "water"
        assert result["tank"]["Amount"] == 2000


class TestDynamoNBTConverter:
    def test_dynamo_nbt(self):
        nbt = {
            "id": "thermalexpansion.DynamoMagmatic",
            "x": 5, "y": 64, "z": 5,
            "Type": 0,
            "Energy": 30000,
            "Fuel": 500,
            "FuelMax": 1000,
            "FuelFluid": {"FluidName": "lava", "Amount": 500},
        }
        result = convert_dynamo_nbt(nbt, "thermal:dynamo_magmatic")
        assert result["id"] == "thermal:dynamo_magmatic"
        assert result["fuel"] == 500
        assert result["fuel_fluid"]["FluidName"] == "lava"
        assert "Items" not in result


class TestDuctNBTConverter:
    def test_energy_duct(self):
        nbt = {
            "id": "thermaldynamics.FluxDuct",
            "x": 0, "y": 64, "z": 0,
            "Con": 0b00110011,  # polaczenia w kilka stron
        }
        result = convert_energy_duct_nbt(nbt, "thermal:energy_duct")
        assert result["id"] == "thermal:energy_duct"
        assert result["connections"] == 0b00110011
        assert "energy" not in result

    def test_tesseract_to_quantum(self):
        nbt = {
            "id": "thermalexpansion.Tesseract",
            "x": 100, "y": 70, "z": 100,
            "Frequency": 42,
            "ModeItem": 1,
            "ModeFluid": 0,
            "ModeEnergy": 1,
            "Access": 0,
        }
        result = convert_tesseract_nbt(nbt, "mekanism:quantum_entangloporter")
        assert result["id"] == "mekanism:quantum_entangloporter"
        assert result["frequency"]["name"] == "thermal_tesseract_42"
        assert result["mode_item"] is True
        assert result["mode_fluid"] is False
        assert result["mode_energy"] is True
        assert result["security_mode"] == "PUBLIC"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
