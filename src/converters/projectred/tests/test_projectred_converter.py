"""
Tests for ProjectRed Converter

Testy jednostkowe i snapshotowe dla konwertera ProjectRed.
Zgodnie z SKILL.md - testy pokrywają:
- Różne metadata (0-15 gdzie ma znaczenie)
- Puste sloty/inventory
- Brakujące pola w NBT
- Nieznane warianty
"""

import unittest
import sys
import os

# Dodaj ścieżkę do src
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..'))

from src.converters.projectred import (
    ProjectRedConverter,
    get_block_mapping,
    get_all_mappings,
    get_removed_blocks,
    GATE_TYPE_NAMES,
    get_gate_block_id_1182,
    get_wire_block_id_1182
)
from src.converters.projectred.nbt_converters import (
    BatteryBoxConverter,
    ChargingBenchConverter,
    ElectrotineGeneratorConverter,
    FrameMotorConverter,
    GatePartConverter,
    RedwirePartConverter,
    BundledCablePartConverter
)


class TestBlockMappings(unittest.TestCase):
    """Testy mapowania bloków"""

    def test_battery_box_mapping(self):
        """Test mapowania BatteryBox (machine2 meta=5)"""
        mapping = get_block_mapping(
            "ProjRed|Expansion:projectred.expansion.machine2",
            metadata=5
        )
        self.assertIsNotNone(mapping)
        self.assertEqual(mapping.id_1182, "projectred_expansion:battery_box")
        self.assertTrue(mapping.has_block_entity)
        self.assertEqual(mapping.nbt_converter, "battery_box")

    def test_removed_block_mapping(self):
        """Test mapowania usuniętego bloku (TileItemImporter meta=1)"""
        mapping = get_block_mapping(
            "ProjRed|Expansion:projectred.expansion.machine2",
            metadata=1
        )
        self.assertIsNotNone(mapping)
        self.assertTrue(mapping.removed)
        self.assertEqual(mapping.id_1182, "")

    def test_ore_mappings(self):
        """Test mapowania rud z różnymi metadata"""
        ore_id = "ProjRed|Exploration:projectred.exploration.ore"

        # Ruby (meta=0)
        mapping = get_block_mapping(ore_id, 0)
        self.assertEqual(mapping.id_1182, "projectred_exploration:ruby_ore")

        # Sapphire (meta=1)
        mapping = get_block_mapping(ore_id, 1)
        self.assertEqual(mapping.id_1182, "projectred_exploration:sapphire_ore")

        # Copper (meta=3) -> vanilla
        mapping = get_block_mapping(ore_id, 3)
        self.assertEqual(mapping.id_1182, "minecraft:copper_ore")

        # Electrotine (meta=6)
        mapping = get_block_mapping(ore_id, 6)
        self.assertEqual(mapping.id_1182, "projectred_exploration:electrotine_ore")

    def test_stone_mappings(self):
        """Test mapowania bloków dekoracyjnych"""
        stone_id = "ProjRed|Exploration:projectred.exploration.stone"

        # Marble (meta=0)
        mapping = get_block_mapping(stone_id, 0)
        self.assertEqual(mapping.id_1182, "projectred_exploration:marble")

        # Ruby Block (meta=5)
        mapping = get_block_mapping(stone_id, 5)
        self.assertEqual(mapping.id_1182, "projectred_exploration:ruby_block")

    def test_all_mappings_count(self):
        """Test że mamy wystarczającą ilość mapowań"""
        all_mappings = get_all_mappings()
        # machine1 (2) + machine2 (13) + ore (7) + stone (12) + ic_block (2) + frame (1) + lamps (32)
        self.assertGreater(len(all_mappings), 50)

    def test_removed_blocks_list(self):
        """Test listy usuniętych bloków"""
        removed = get_removed_blocks()
        self.assertGreater(len(removed), 0)

        # Sprawdź że TileInductiveFurnace jest na liście
        notes = [m.notes for m in removed]
        self.assertTrue(any("TileInductiveFurnace" in n for n in notes))


class TestBatteryBoxConverter(unittest.TestCase):
    """Testy konwertera BatteryBox"""

    def setUp(self):
        self.converter = BatteryBoxConverter()

    def test_basic_conversion(self):
        """Test podstawowej konwersji BatteryBox"""
        nbt_1710 = {
            "storage": 5000
        }

        result = self.converter.convert(nbt_1710)

        self.assertTrue(result.success)
        self.assertEqual(result.converted_nbt["storage"], 5000)
        self.assertIn("vCap", result.converted_nbt)
        self.assertIn("iCap", result.converted_nbt)
        self.assertIn("chargeFlow", result.converted_nbt)

    def test_empty_storage(self):
        """Test z pustym storage"""
        nbt_1710 = {}

        result = self.converter.convert(nbt_1710)

        self.assertTrue(result.success)
        self.assertEqual(result.converted_nbt["storage"], 0)
        self.assertEqual(result.converted_nbt["vCap"], 0.0)

    def test_overflow_storage(self):
        """Test z przepełnionym storage (>8000)"""
        nbt_1710 = {
            "storage": 10000  # Powyżej limitu
        }

        result = self.converter.convert(nbt_1710)

        self.assertTrue(result.success)
        self.assertEqual(result.converted_nbt["storage"], 8000)
        self.assertGreater(len(result.warnings), 0)

    def test_with_inventory(self):
        """Test z inwentarzem"""
        nbt_1710 = {
            "storage": 1000,
            "items": [
                {"Slot": 0, "id": "minecraft:redstone", "Count": 64}
            ]
        }

        result = self.converter.convert(nbt_1710)

        self.assertTrue(result.success)
        self.assertIn("inventory", result.converted_nbt)
        self.assertIn("Items", result.converted_nbt["inventory"])


class TestChargingBenchConverter(unittest.TestCase):
    """Testy konwertera ChargingBench"""

    def setUp(self):
        self.converter = ChargingBenchConverter()

    def test_basic_conversion(self):
        """Test podstawowej konwersji ChargingBench"""
        nbt_1710 = {
            "storage": 3000,
            "srr": 2  # slotRoundRobin
        }

        result = self.converter.convert(nbt_1710)

        self.assertTrue(result.success)
        self.assertEqual(result.converted_nbt["storage"], 3000)
        # srr -> chargeSlot (zmiana nazwy)
        self.assertEqual(result.converted_nbt["chargeSlot"], 2)

    def test_missing_srr(self):
        """Test z brakującym srr"""
        nbt_1710 = {
            "storage": 1000
        }

        result = self.converter.convert(nbt_1710)

        self.assertTrue(result.success)
        self.assertEqual(result.converted_nbt["chargeSlot"], 0)


class TestElectrotineGeneratorConverter(unittest.TestCase):
    """Testy konwertera ElectrotineGenerator"""

    def setUp(self):
        self.converter = ElectrotineGeneratorConverter()

    def test_basic_conversion(self):
        """Test podstawowej konwersji"""
        nbt_1710 = {
            "storage": 2000,
            "btime": 100  # burnTimeRemaining
        }

        result = self.converter.convert(nbt_1710)

        self.assertTrue(result.success)
        # storage -> stored (zmiana nazwy!)
        self.assertEqual(result.converted_nbt["stored"], 2000)
        # btime -> burnTime (zmiana nazwy!)
        self.assertEqual(result.converted_nbt["burnTime"], 100)

    def test_short_to_int_conversion(self):
        """Test konwersji btime z Short na int"""
        nbt_1710 = {
            "storage": 0,
            "btime": -1  # Short może być ujemny
        }

        result = self.converter.convert(nbt_1710)

        self.assertTrue(result.success)
        self.assertEqual(result.converted_nbt["burnTime"], -1)


class TestFrameMotorConverter(unittest.TestCase):
    """Testy konwertera FrameMotor"""

    def setUp(self):
        self.converter = FrameMotorConverter()

    def test_basic_conversion(self):
        """Test podstawowej konwersji FrameMotor"""
        nbt_1710 = {
            "ch": True,   # isCharged
            "pow": False  # isPowered
        }

        result = self.converter.convert(nbt_1710)

        self.assertTrue(result.success)
        self.assertEqual(result.converted_nbt["powered"], False)
        # isCharged -> vCap (przybliżenie)
        self.assertEqual(result.converted_nbt["vCap"], 600.0)

    def test_not_charged(self):
        """Test gdy nie naładowany"""
        nbt_1710 = {
            "ch": False,
            "pow": False
        }

        result = self.converter.convert(nbt_1710)

        self.assertTrue(result.success)
        self.assertEqual(result.converted_nbt["vCap"], 0.0)


class TestGatePartConverter(unittest.TestCase):
    """Testy konwertera bramek logicznych"""

    def setUp(self):
        self.converter = GatePartConverter()

    def test_and_gate_conversion(self):
        """Test konwersji bramki AND"""
        nbt_1710 = {
            "orient": 0x23,  # side=2, rotation=3
            "subID": 3,      # AND gate
            "shape": 0,
            "connMap": 0xF,
            "nolegacy": True,
            "schedTime": 0
        }

        result = self.converter.convert(nbt_1710)

        self.assertTrue(result.success)
        self.assertEqual(result.converted_nbt["orient"], 0x23)
        self.assertEqual(result.converted_nbt["shape"], 0)
        self.assertEqual(result.converted_nbt["connMap"], 0xF)
        self.assertEqual(result.converted_nbt["__gate_type"], "and")

    def test_legacy_connmap(self):
        """Test obsługi legacy connMap"""
        nbt_1710 = {
            "orient": 0,
            "subID": 0,
            "shape": 0,
            "connMap": 0x00FF,
            "nolegacy": False,  # Legacy format
            "schedTime": 0
        }

        result = self.converter.convert(nbt_1710)

        self.assertTrue(result.success)
        # Legacy: connMap | 0xF000
        self.assertEqual(result.converted_nbt["connMap"], 0xF0FF)

    def test_blockstate_extraction(self):
        """Test ekstrakcji orientacji do blockstate"""
        nbt_1710 = {
            "orient": 0x23,  # side=2 (bits 4-6), rotation=3 (bits 0-1)
            "subID": 0,
            "shape": 0,
            "connMap": 0,
            "schedTime": 0
        }

        result = self.converter.convert(nbt_1710)

        self.assertTrue(result.success)
        self.assertEqual(result.blockstate_props["side"], "2")
        self.assertEqual(result.blockstate_props["rotation"], "3")


class TestRedwirePartConverter(unittest.TestCase):
    """Testy konwertera przewodów Red Alloy"""

    def setUp(self):
        self.converter = RedwirePartConverter()

    def test_basic_conversion(self):
        """Test podstawowej konwersji"""
        nbt_1710 = {
            "signal": 255
        }

        result = self.converter.convert(nbt_1710)

        self.assertTrue(result.success)
        self.assertEqual(result.converted_nbt["signal"], 255)

    def test_zero_signal(self):
        """Test z zerowym sygnałem"""
        nbt_1710 = {
            "signal": 0
        }

        result = self.converter.convert(nbt_1710)

        self.assertTrue(result.success)
        self.assertEqual(result.converted_nbt["signal"], 0)


class TestBundledCablePartConverter(unittest.TestCase):
    """Testy konwertera przewodów Bundled"""

    def setUp(self):
        self.converter = BundledCablePartConverter()

    def test_basic_conversion(self):
        """Test podstawowej konwersji"""
        nbt_1710 = {
            "signal": [0, 15, 0, 0, 255, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            "colour": 5  # Lime
        }

        result = self.converter.convert(nbt_1710)

        self.assertTrue(result.success)
        self.assertEqual(len(result.converted_nbt["signal"]), 16)
        self.assertEqual(result.converted_nbt["signal"][1], 15)
        self.assertEqual(result.converted_nbt["signal"][4], 255)
        self.assertEqual(result.converted_nbt["__colour"], 5)

    def test_short_signal_array(self):
        """Test z krótszą tablicą sygnałów"""
        nbt_1710 = {
            "signal": [100, 50],  # Tylko 2 elementy
            "colour": -1
        }

        result = self.converter.convert(nbt_1710)

        self.assertTrue(result.success)
        # Powinno być dopełnione do 16
        self.assertEqual(len(result.converted_nbt["signal"]), 16)
        self.assertEqual(result.converted_nbt["signal"][0], 100)
        self.assertEqual(result.converted_nbt["signal"][2], 0)


class TestGateBlockIdGeneration(unittest.TestCase):
    """Testy generowania ID bloków dla bramek"""

    def test_and_gate_id(self):
        """Test ID dla bramki AND"""
        block_id = get_gate_block_id_1182(3, "pr_sgate")
        self.assertEqual(block_id, "projectred_integration:and_gate")

    def test_timer_gate_id(self):
        """Test ID dla bramki Timer"""
        block_id = get_gate_block_id_1182(15, "pr_igate")
        self.assertEqual(block_id, "projectred_integration:timer_gate")

    def test_unknown_gate_id(self):
        """Test ID dla nieznanej bramki"""
        block_id = get_gate_block_id_1182(999, "pr_sgate")
        self.assertIn("unknown", block_id)


class TestWireBlockIdGeneration(unittest.TestCase):
    """Testy generowania ID bloków dla przewodów"""

    def test_redwire_id(self):
        """Test ID dla Red Alloy Wire"""
        block_id = get_wire_block_id_1182("redwire")
        self.assertEqual(block_id, "projectred_transmission:red_alloy_wire")

    def test_insulated_wire_id(self):
        """Test ID dla Insulated Wire z kolorem"""
        block_id = get_wire_block_id_1182("insulated", 1)  # Orange
        self.assertEqual(block_id, "projectred_transmission:orange_insulated_wire")

    def test_bundled_cable_id(self):
        """Test ID dla Bundled Cable"""
        block_id = get_wire_block_id_1182("bundled", -1)  # Neutralny
        self.assertEqual(block_id, "projectred_transmission:bundled_cable")


class TestProjectRedConverterIntegration(unittest.TestCase):
    """Testy integracyjne głównego konwertera"""

    def setUp(self):
        self.converter = ProjectRedConverter()

    def test_battery_box_full_conversion(self):
        """Test pełnej konwersji BatteryBox"""
        result = self.converter.convert_block(
            "ProjRed|Expansion:projectred.expansion.machine2",
            nbt_1710={"storage": 4000},
            metadata=5,
            position=(100, 64, 100)
        )

        self.assertTrue(result.converted.success)
        self.assertEqual(result.converted.block_id_1182, "projectred_expansion:battery_box")
        self.assertEqual(result.converted.nbt_1182["storage"], 4000)

    def test_removed_block_conversion(self):
        """Test konwersji usuniętego bloku"""
        result = self.converter.convert_block(
            "ProjRed|Expansion:projectred.expansion.machine2",
            nbt_1710={},
            metadata=1,  # TileItemImporter
            position=(100, 64, 100)
        )

        self.assertTrue(result.converted.success)
        self.assertTrue(result.converted.removed)
        self.assertIsNone(result.converted.block_id_1182)

    def test_gate_multipart_conversion(self):
        """Test konwersji bramki jako multipart"""
        result = self.converter.convert_multipart(
            "pr_sgate",
            nbt_1710={
                "orient": 0,
                "subID": 3,  # AND
                "shape": 0,
                "connMap": 0,
                "schedTime": 0
            },
            position=(100, 64, 100)
        )

        self.assertTrue(result.converted.success)
        self.assertEqual(result.converted.block_id_1182, "projectred_integration:and_gate")

    def test_wire_multipart_conversion(self):
        """Test konwersji przewodu jako multipart"""
        result = self.converter.convert_multipart(
            "pr_redwire",
            nbt_1710={"signal": 128},
            position=(100, 64, 100)
        )

        self.assertTrue(result.converted.success)
        self.assertEqual(result.converted.block_id_1182, "projectred_transmission:red_alloy_wire")

    def test_is_projectred_block(self):
        """Test rozpoznawania bloków ProjectRed"""
        self.assertTrue(self.converter.is_projectred_block(
            "ProjRed|Expansion:projectred.expansion.machine2"
        ))
        self.assertFalse(self.converter.is_projectred_block(
            "minecraft:stone"
        ))

    def test_is_projectred_multipart(self):
        """Test rozpoznawania multipart ProjectRed"""
        self.assertTrue(self.converter.is_projectred_multipart("pr_sgate"))
        self.assertTrue(self.converter.is_projectred_multipart("pr_redwire"))
        self.assertFalse(self.converter.is_projectred_multipart("ae2_cable"))

    def test_conversion_report(self):
        """Test generowania raportu"""
        report = self.converter.get_conversion_report()

        self.assertEqual(report["source_version"], "1.7.10")
        self.assertEqual(report["target_version"], "1.18.2")
        self.assertGreater(report["supported_blocks"], 0)
        self.assertIn("source_mapping", report)


class TestEdgeCases(unittest.TestCase):
    """Testy przypadków brzegowych"""

    def setUp(self):
        self.converter = ProjectRedConverter()

    def test_empty_nbt(self):
        """Test z pustym NBT"""
        result = self.converter.convert_block(
            "ProjRed|Expansion:projectred.expansion.machine2",
            nbt_1710={},
            metadata=5,  # BatteryBox
            position=(0, 0, 0)
        )

        self.assertTrue(result.converted.success)

    def test_none_nbt(self):
        """Test z None jako NBT"""
        result = self.converter.convert_block(
            "ProjRed|Expansion:projectred.expansion.machine2",
            nbt_1710=None,
            metadata=5,
            position=(0, 0, 0)
        )

        self.assertTrue(result.converted.success)

    def test_unknown_block(self):
        """Test z nieznanym blokiem"""
        result = self.converter.convert_block(
            "ProjRed|Unknown:unknown.block",
            nbt_1710={},
            metadata=0,
            position=(0, 0, 0)
        )

        self.assertFalse(result.converted.success)
        self.assertGreater(len(result.converted.errors), 0)

    def test_invalid_metadata(self):
        """Test z nieprawidłową metadata"""
        result = self.converter.convert_block(
            "ProjRed|Expansion:projectred.expansion.machine2",
            nbt_1710={},
            metadata=99,  # Nieistniejąca metadata
            position=(0, 0, 0)
        )

        # Powinno zwrócić błąd lub None
        self.assertFalse(result.converted.success)


if __name__ == "__main__":
    unittest.main()
