"""
Testy jednostkowe symulacji BuildCraft.

Uruchomienie:
    pytest src/converters/buildcraft/tests/test_buildcraft_simulations.py -v
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))

from converters.buildcraft.simulations.engine_simulation import (
    EngineState1710,
    simulate_engine_conversion,
    MJ_TO_FE,
)
from converters.buildcraft.simulations.factory_simulation import (
    TankState1710,
    PumpState1710,
    RefineryState1710,
    simulate_tank_conversion,
    simulate_pump_conversion,
    simulate_refinery_conversion,
)
from converters.buildcraft.simulations.pipe_simulation import (
    PipeState1710,
    simulate_pipe_conversion,
)
from converters.buildcraft.simulations.assembly_laser_simulation import (
    AssemblyTableState1710,
    LaserState1710,
    ZonePlanState1710,
    simulate_assembly_table_conversion,
    simulate_laser_conversion,
    simulate_zone_plan_conversion,
)


class TestEngineSimulation:
    """Testy konwersji silnikow BC."""

    def test_wood_engine_remove(self):
        nbt = {
            "id": "net.minecraft.src.buildcraft.energy.TileEngineWood",
            "x": 10, "y": 64, "z": 10,
            "orientation": 0,
            "heat": 20.0,
            "energy": 0,
        }
        state = EngineState1710.from_nbt(nbt)
        result = simulate_engine_conversion(state)
        assert result["action"] == "REMOVE"
        assert "Redstone Engine" in result["reason"]

    def test_stone_engine_convert(self):
        nbt = {
            "id": "net.minecraft.src.buildcraft.energy.TileEngineStone",
            "x": 11, "y": 64, "z": 10,
            "orientation": 3,
            "heat": 25.0,
            "energy": 100,
            "burnTime": 800,
            "totalBurnTime": 1600,
            "Items": [{"Slot": 0, "id": 263, "Count": 16, "Damage": 0}],
        }
        state = EngineState1710.from_nbt(nbt)
        result = simulate_engine_conversion(state)
        assert result["action"] == "CONVERT"
        assert result["target"].block_id == "thermal:dynamo_steam"
        assert result["target"].facing == "south"
        assert result["target"].energy_fe == 100 * MJ_TO_FE
        assert len(result["target"].inventory) == 1

    def test_iron_engine_convert(self):
        nbt = {
            "id": "net.minecraft.src.buildcraft.energy.TileEngineIron",
            "x": 12, "y": 64, "z": 10,
            "orientation": 5,
            "heat": 40.0,
            "energy": 500,
            "tankFuel": {"FluidName": "fuel", "Amount": 2000},
            "tankCoolant": {"FluidName": "water", "Amount": 1000},
        }
        state = EngineState1710.from_nbt(nbt)
        result = simulate_engine_conversion(state)
        assert result["action"] == "CONVERT"
        assert result["target"].block_id == "thermal:dynamo_compression"
        assert result["target"].facing == "east"
        assert len(result["target"].fluid_tanks) == 2

    def test_energy_conversion_mj_to_fe(self):
        nbt = {
            "id": "net.minecraft.src.buildcraft.energy.TileEngineStone",
            "x": 0, "y": 0, "z": 0,
            "orientation": 1,
            "energy": 123,
        }
        state = EngineState1710.from_nbt(nbt)
        result = simulate_engine_conversion(state)
        assert result["target"].energy_fe == 1230


class TestFactorySimulation:
    """Testy konwersji maszyn fabrycznych BC."""

    def test_empty_tank(self):
        nbt = {
            "id": "net.minecraft.src.buildcraft.factory.TileTank",
            "x": 20, "y": 64, "z": 20,
            "tank": {"Empty": ""},
        }
        state = TankState1710.from_nbt(nbt)
        result = simulate_tank_conversion(state)
        assert result["action"] == "CONVERT"
        assert result["target"].block_id == "mekanism:basic_fluid_tank"
        assert len(result["target"].fluid_tanks) == 0

    def test_water_tank(self):
        nbt = {
            "id": "net.minecraft.src.buildcraft.factory.TileTank",
            "x": 21, "y": 64, "z": 20,
            "tank": {"FluidName": "water", "Amount": 4000},
        }
        state = TankState1710.from_nbt(nbt)
        result = simulate_tank_conversion(state)
        assert result["target"].fluid_tanks[0]["FluidName"] == "minecraft:water"
        assert result["target"].fluid_tanks[0]["Amount"] == 4000

    def test_pump_conversion(self):
        nbt = {
            "id": "net.minecraft.src.buildcraft.factory.TilePump",
            "x": 22, "y": 64, "z": 20,
            "battery": {"energy": 300, "maxEnergy": 1000},
            "tank": {"FluidName": "water", "Amount": 500},
        }
        state = PumpState1710.from_nbt(nbt)
        result = simulate_pump_conversion(state)
        assert result["action"] == "CONVERT"
        assert result["target"].block_id == "mekanism:electric_pump"
        assert result["target"].energy_fe == 3000

    def test_refinery_with_oil(self):
        nbt = {
            "id": "net.minecraft.src.buildcraft.factory.Refinery",
            "x": 23, "y": 64, "z": 20,
            "tank1": {"acceptedFluid": "oil", "Empty": ""},
            "tank2": {"acceptedFluid": "oil", "FluidName": "oil", "Amount": 200},
            "result": {"acceptedFluid": "fuel", "Empty": ""},
            "battery": {"energy": 0, "maxEnergy": 10000},
        }
        state = RefineryState1710.from_nbt(nbt)
        result = simulate_refinery_conversion(state)
        assert result["action"] == "CONVERT"
        assert result["target"].block_id == "thermal:machine_refinery"

    def test_refinery_without_oil_convert(self):
        nbt = {
            "id": "net.minecraft.src.buildcraft.factory.Refinery",
            "x": 24, "y": 64, "z": 20,
            "tank1": {"acceptedFluid": "oil", "Empty": ""},
            "tank2": {"acceptedFluid": "oil", "Empty": ""},
            "result": {"acceptedFluid": "fuel", "Empty": ""},
            "battery": {"energy": 0, "maxEnergy": 10000},
        }
        state = RefineryState1710.from_nbt(nbt)
        result = simulate_refinery_conversion(state)
        assert result["action"] == "CONVERT"
        assert result["target"].block_id == "thermal:machine_refinery"


class TestPipeSimulation:
    """Testy konwersji rur BC."""

    def test_plain_pipe_universal(self):
        nbt = {
            "id": "net.minecraft.src.buildcraft.transport.GenericPipe",
            "x": 30, "y": 64, "z": 30,
            "pipeId": 4163,
            "inputOpen": 63,
            "outputOpen": 63,
            "wireSet[0]": 0,
            "travelingEntities": [],
        }
        state = PipeState1710.from_nbt(nbt)
        result = simulate_pipe_conversion(state)
        assert result["action"] == "UNIVERSAL_PIPE"
        assert result["replacement_block"] == "pipez:universal_pipe"

    def test_pipe_with_wire_universal(self):
        nbt = {
            "id": "net.minecraft.src.buildcraft.transport.GenericPipe",
            "x": 31, "y": 64, "z": 30,
            "pipeId": 4100,
            "wireSet[0]": 1,
            "travelingEntities": [],
        }
        state = PipeState1710.from_nbt(nbt)
        result = simulate_pipe_conversion(state)
        assert result["action"] == "UNIVERSAL_PIPE"
        assert "logika gates/wires" in result["reason"]

    def test_critical_fluid_pipe(self):
        nbt = {
            "id": "net.minecraft.src.buildcraft.transport.GenericPipe",
            "x": 32, "y": 64, "z": 30,
            "pipeId": 4201,
            "outputOpen": 12,
            "travelingEntities": [],
        }
        state = PipeState1710.from_nbt(nbt)
        result = simulate_pipe_conversion(state, neighbors_have_fluid=True, is_critical_connection=True)
        assert result["action"] == "FLUID_PIPE"
        assert result["replacement_block"] == "pipez:fluid_pipe"

    def test_critical_energy_pipe(self):
        nbt = {
            "id": "net.minecraft.src.buildcraft.transport.GenericPipe",
            "x": 33, "y": 64, "z": 30,
            "pipeId": 4163,
            "outputOpen": 3,
            "travelingEntities": [],
        }
        state = PipeState1710.from_nbt(nbt)
        result = simulate_pipe_conversion(state, neighbors_have_power=True, is_critical_connection=True)
        assert result["action"] == "ENERGY_PIPE"
        assert result["replacement_block"] == "pipez:energy_pipe"


class TestAssemblyLaserSimulation:
    """Testy konwersji specjalnych maszyn BC."""

    def test_assembly_table_remove_with_items(self):
        nbt = {
            "id": "net.minecraft.src.buildcraft.factory.TileAssemblyTable",
            "x": 40, "y": 64, "z": 40,
            "inv": [{"Slot": 0, "id": 331, "Count": 10, "Damage": 0}],
            "plannedIds": [],
            "energy": 1000,
        }
        state = AssemblyTableState1710.from_nbt(nbt)
        result = simulate_assembly_table_conversion(state)
        assert result["action"] == "REMOVE"
        assert len(result["items_to_drop"]) == 1
        assert "Wydropi" in result["recommendation"]

    def test_laser_remove(self):
        nbt = {
            "id": "net.minecraft.src.buildcraft.factory.TileLaser",
            "x": 41, "y": 64, "z": 40,
            "battery": {"maxEnergy": 10000, "maxReceive": 250, "maxExtract": 0, "energy": 5000},
        }
        state = LaserState1710.from_nbt(nbt)
        result = simulate_laser_conversion(state)
        assert result["action"] == "REMOVE"
        assert "dekoracyjn" in result["alternative"]

    def test_zone_plan_remove(self):
        nbt = {
            "id": "net.minecraft.src.buildcraft.commander.TileZonePlan",
            "x": 42, "y": 64, "z": 40,
            "inv": {"Items": []},
            "selectedArea[0]": {"x": 5, "z": 5, "fullSet": 1},
        }
        state = ZonePlanState1710.from_nbt(nbt)
        result = simulate_zone_plan_conversion(state)
        assert result["action"] == "REMOVE"
        assert result["original"]["selected_chunks"] == 1
