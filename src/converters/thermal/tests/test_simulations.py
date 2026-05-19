"""Testy symulacji Thermal Series."""

import pytest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent.parent))

from converters.thermal.simulations.machine_simulation import (
    MachineState,
    simulate_ore_processing_line,
    simulate_induction_smelter,
)
from converters.thermal.simulations.dynamo_simulation import (
    DynamoState,
    simulate_dynamo_array,
)
from converters.thermal.simulations.duct_simulation import (
    simulate_energy_grid,
    simulate_item_transport,
)


class TestMachineSimulation:
    def test_furnace_process(self):
        furnace = MachineState("furnace", energy_stored=5000)
        assert furnace.insert_item("minecraft:iron_ore") is True
        ticks = 0
        while furnace.progress < furnace.progress_max and ticks < 500:
            furnace.tick()
            ticks += 1
        assert furnace.output_item == "minecraft:iron_ingot"
        assert ticks == 200

    def test_ore_processing_line(self):
        result = simulate_ore_processing_line("minecraft:iron_ore")
        assert result["pulverizer_output"] is not None
        assert result["furnace_output"] == "minecraft:iron_ingot"
        assert result["energy_consumed"] > 0

    def test_induction_smelter(self):
        result = simulate_induction_smelter()
        assert result["output"] == "thermal:invar_ingot"
        assert result["energy_consumed"] > 0

    def test_cannot_insert_invalid_item(self):
        furnace = MachineState("furnace")
        assert furnace.insert_item("minecraft:dirt") is False


class TestDynamoSimulation:
    def test_steam_dynamo_tick(self):
        d = DynamoState("steam")
        d.insert_fuel(fluid="water", amount=1000)
        produced = d.tick()
        assert produced > 0

    def test_dynamo_array(self):
        specs = [
            {"type": "steam", "fuel_fluid": "water", "amount": 5000},
            {"type": "magmatic", "fuel_fluid": "lava", "amount": 5000},
        ]
        result = simulate_dynamo_array(specs, ticks=100)
        assert result["total_rf"] > 0
        assert result["avg_rf_per_tick"] > 0

    def test_no_fuel_no_output(self):
        d = DynamoState("steam")
        produced = d.tick()
        assert produced == 0


class TestDuctSimulation:
    def test_energy_grid(self):
        result = simulate_energy_grid(
            sources=[(0, 0, 0)],
            sinks=[(5, 0, 0)],
            total_rf=5000,
        )
        assert result["transferred"] > 0
        assert result["transferred"] <= 5000

    def test_item_transport(self):
        result = simulate_item_transport(
            source=(0, 0, 0),
            sinks=[(3, 0, 0)],
            items=["minecraft:iron_ingot"] * 32,
        )
        assert result["items_sent"] == 32
        assert result["items_delivered"] == 32


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
