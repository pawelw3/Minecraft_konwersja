"""Testy mappingow Thermal Series."""

import pytest
import sys
from pathlib import Path

# Dodaj src/ do path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent.parent))

from converters.thermal.mappings import (
    get_mapping,
    get_mapping_by_te_id,
    THERMAL_TIER_BY_META,
    DUCT_MAPPINGS,
)


class TestMachineMappings:
    def test_furnace(self):
        m = get_mapping("ThermalExpansion:Machine", 0)
        assert m.target_block_id == "thermal:machine_furnace"
        assert m.has_block_entity is True

    def test_pulverizer(self):
        m = get_mapping("ThermalExpansion:Machine", 1)
        assert m.target_block_id == "thermal:machine_pulverizer"

    def test_insolator(self):
        m = get_mapping("ThermalExpansion:Machine", 11)
        assert m.target_block_id == "thermal:machine_insolator"

    def test_nonexistent_machine(self):
        m = get_mapping("ThermalExpansion:Machine", 99)
        assert m is None


class TestDeviceMappings:
    def test_pump_to_mekanism(self):
        m = get_mapping("ThermalExpansion:Device", 1)
        assert m.target_block_id == "mekanism:electric_pump"
        assert "fallback" in m.notes.lower()

    def test_collector(self):
        m = get_mapping("ThermalExpansion:Device", 4)
        assert m.target_block_id == "thermal:device_collector"

    def test_buffer(self):
        m = get_mapping("ThermalExpansion:Device", 6)
        assert m.target_block_id == "thermal:item_buffer"


class TestDynamoMappings:
    def test_steam_dynamo(self):
        m = get_mapping("ThermalExpansion:Dynamo", 0)
        assert m.target_block_id == "thermal:dynamo_stirling"

    def test_reactant_fallback(self):
        m = get_mapping("ThermalExpansion:Dynamo", 3)
        assert m.target_block_id == "thermal:dynamo_compression"
        assert "fallback" in m.notes.lower()


class TestStorageMappings:
    def test_cell_tiers(self):
        for meta, tier in THERMAL_TIER_BY_META.items():
            m = get_mapping("ThermalExpansion:Cell", meta)
            assert m is not None
            assert m.target_block_id == "thermal:energy_cell"

    def test_strongbox(self):
        m = get_mapping("ThermalExpansion:Strongbox", 0)
        assert m.target_block_id == "thermal:item_cell"


class TestSpecialMappings:
    def test_tesseract_to_mekanism(self):
        m = get_mapping("ThermalExpansion:Tesseract", 0)
        assert m.target_block_id == "mekanism:quantum_entangloporter"
        assert "fallback" in m.notes.lower()

    def test_te_id_lookup(self):
        m = get_mapping_by_te_id("thermalexpansion.Furnace")
        assert m is not None
        assert m.target_block_id == "thermal:machine_furnace"

    def test_te_id_tesseract(self):
        m = get_mapping_by_te_id("thermalexpansion.Tesseract")
        assert m.target_block_id == "mekanism:quantum_entangloporter"


class TestDuctMappings:
    def test_energy_duct(self):
        m = get_mapping("ThermalDynamics:FluxDuct", 0)
        assert m.target_block_id == "thermal:energy_duct"

    def test_item_duct_to_buffer(self):
        m = get_mapping("ThermalDynamics:ItemDuct", 0)
        assert m.target_block_id == "thermal:item_buffer"

    def test_ender_item_duct_to_mekanism(self):
        m = get_mapping("ThermalDynamics:ItemDuct", 1)
        assert m.target_block_id == "mekanism:basic_logistical_transporter"


class TestFoundationMappings:
    def test_copper_ore(self):
        m = get_mapping("ThermalFoundation:Ore", 0)
        assert m.target_block_id == "thermal:copper_ore"

    def test_tin_storage(self):
        m = get_mapping("ThermalFoundation:Storage", 1)
        assert m.target_block_id == "thermal:tin_block"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
