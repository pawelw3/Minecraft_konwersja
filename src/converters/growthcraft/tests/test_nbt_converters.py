"""
Testy jednostkowe dla konwerterów NBT GrowthCraft

Testuje konwersję NBT dla poszczególnych maszyn GrowthCraft.
"""

import sys
import os
import unittest

# Dodaj ścieżkę do src
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..'))

from converters.growthcraft.nbt_converters import (
    FermentationBarrelNBTConverter,
    BrewKettleNBTConverter,
    BeeBoxNBTConverter,
    MixingVatNBTConverter,
)


class TestFermentationBarrelConverter(unittest.TestCase):
    """Testy dla FermentationBarrelNBTConverter"""
    
    def setUp(self):
        self.converter = FermentationBarrelNBTConverter()
    
    def test_basic_conversion(self):
        """Test podstawowej konwersji NBT"""
        nbt_1710 = {
            "id": "grccellar:ferment_barrel",
            "time": 1200,
            "Tank": {
                "FluidName": "grccellar:apple_juice",
                "Amount": 2000
            },
            "items": [
                {"id": "grccellar:yeast", "Count": 2, "Slot": 0}
            ],
            "lid_on": False
        }
        
        result = self.converter.convert(nbt_1710)
        
        self.assertTrue(result.success)
        self.assertIsNotNone(result.converted_nbt)
        
        nbt_1182 = result.converted_nbt
        self.assertEqual(nbt_1182["id"], "growthcraft:fermentation_barrel")
        self.assertEqual(nbt_1182["CurrentProcessTicks"], 1200)
        self.assertIn("MaxProcessTicks", nbt_1182)
        self.assertIn("fluid_tank_input_0", nbt_1182)
        self.assertIn("inventory", nbt_1182)
    
    def test_fluid_conversion(self):
        """Test konwersji płynu"""
        nbt_1710 = {
            "id": "grccellar:ferment_barrel",
            "time": 0,
            "Tank": {
                "FluidName": "grccellar:grape_juice",
                "Amount": 3000
            }
        }
        
        result = self.converter.convert(nbt_1710)
        nbt_1182 = result.converted_nbt
        
        fluid = nbt_1182["fluid_tank_input_0"]
        self.assertEqual(fluid["FluidName"], "growthcraft:grape_juice")
        self.assertEqual(fluid["Amount"], 3000)
    
    def test_empty_barrel(self):
        """Test konwersji pustej beczki"""
        nbt_1710 = {
            "id": "grccellar:ferment_barrel",
            "time": 0
        }
        
        result = self.converter.convert(nbt_1710)
        
        self.assertTrue(result.success)
        self.assertEqual(result.converted_nbt["CurrentProcessTicks"], 0)
    
    def test_max_ticks_calculation(self):
        """Test obliczania MaxProcessTicks"""
        nbt_1710 = {
            "id": "grccellar:ferment_barrel",
            "time": 0,
            "Tank": {
                "FluidName": "grccellar:apple_juice",
                "Amount": 2000  # 2000mB = 2x mnożnik
            }
        }
        
        result = self.converter.convert(nbt_1710)
        nbt_1182 = result.converted_nbt
        
        # 2400 * 2 = 4800
        self.assertEqual(nbt_1182["MaxProcessTicks"], 4800)


class TestBrewKettleConverter(unittest.TestCase):
    """Testy dla BrewKettleNBTConverter"""
    
    def setUp(self):
        self.converter = BrewKettleNBTConverter()
    
    def test_basic_conversion(self):
        """Test podstawowej konwersji NBT"""
        nbt_1710 = {
            "id": "grccellar:brew_kettle",
            "brew_kettle": {
                "time": 600.0,
                "time_max": 1200.0,
                "heat_multiplier": 1.0
            },
            "TankInput": {
                "FluidName": "minecraft:water",
                "Amount": 1000
            },
            "TankOutput": {
                "FluidName": "grccellar:wort",
                "Amount": 0
            },
            "items": [
                {"id": "grccellar:grain", "Count": 1, "Slot": 0},
                {"id": "minecraft:wheat", "Count": 1, "Slot": 1}
            ]
        }
        
        result = self.converter.convert(nbt_1710)
        
        self.assertTrue(result.success)
        nbt_1182 = result.converted_nbt
        
        self.assertEqual(nbt_1182["id"], "growthcraft:brew_kettle")
        self.assertEqual(nbt_1182["CurrentProcessTicks"], 600)
        self.assertEqual(nbt_1182["MaxProcessTicks"], 1200)
        self.assertIn("fluid_tank_input_0", nbt_1182)
        self.assertIn("fluid_tank_output_0", nbt_1182)
        self.assertIn("inventory", nbt_1182)
    
    def test_slot_mapping(self):
        """Test mapowania slotów inventory"""
        nbt_1710 = {
            "id": "grccellar:brew_kettle",
            "brew_kettle": {"time": 0, "time_max": 1200},
            "items": [
                {"id": "grccellar:grain", "Count": 1, "Slot": 0},  # input
                {"id": "minecraft:wheat", "Count": 1, "Slot": 1}   # byproduct
            ]
        }
        
        result = self.converter.convert(nbt_1710)
        nbt_1182 = result.converted_nbt
        
        inventory = nbt_1182["inventory"]
        items = inventory["Items"]
        
        # Sprawdź mapowanie slotów
        slot_1_item = next((i for i in items if i["Slot"] == 1), None)
        slot_2_item = next((i for i in items if i["Slot"] == 2), None)
        
        self.assertIsNotNone(slot_1_item)
        self.assertEqual(slot_1_item["id"], "growthcraft:grain")
        
        self.assertIsNotNone(slot_2_item)
        self.assertEqual(slot_2_item["id"], "minecraft:wheat")
    
    def test_heat_multiplier_warning(self):
        """Test ostrzeżenia o heat_multiplier"""
        nbt_1710 = {
            "id": "grccellar:brew_kettle",
            "brew_kettle": {
                "time": 0,
                "time_max": 1200,
                "heat_multiplier": 1.5
            }
        }
        
        result = self.converter.convert(nbt_1710)
        
        self.assertTrue(len(result.warnings) > 0)
        self.assertTrue(any("heat_multiplier" in w for w in result.warnings))


class TestBeeBoxConverter(unittest.TestCase):
    """Testy dla BeeBoxNBTConverter"""
    
    def setUp(self):
        self.converter = BeeBoxNBTConverter()
    
    def test_basic_conversion(self):
        """Test podstawowej konwersji NBT"""
        nbt_1710 = {
            "id": "grcbees:bee_box",
            "bee_box": {
                "bee_count": 3,
                "bonus_time": 0,
                "version": 3
            },
            "items": [
                {"id": "grcbees:bee", "Count": 3, "Slot": 0},
                {"id": "grcbees:honey_comb_full", "Count": 5, "Slot": 1},
                {"id": "grcbees:honey_comb", "Count": 10, "Slot": 2}
            ]
        }
        
        result = self.converter.convert(nbt_1710)
        
        self.assertTrue(result.success)
        nbt_1182 = result.converted_nbt
        
        self.assertEqual(nbt_1182["id"], "growthcraft:bee_box")
        self.assertEqual(nbt_1182["CurrentProcessTicks"], 0)
        self.assertIn("inventory", nbt_1182)
        
        inventory = nbt_1182["inventory"]
        self.assertEqual(inventory["Size"], 28)
        self.assertEqual(len(inventory["Items"]), 3)
    
    def test_bee_slot_conversion(self):
        """Test konwersji slotu pszczół"""
        nbt_1710 = {
            "id": "grcbees:bee_box",
            "items": [
                {"id": "grcbees:bee", "Count": 5, "Slot": 0}
            ]
        }
        
        result = self.converter.convert(nbt_1710)
        nbt_1182 = result.converted_nbt
        
        items = nbt_1182["inventory"]["Items"]
        bee_item = next((i for i in items if i["Slot"] == 0), None)
        
        self.assertIsNotNone(bee_item)
        self.assertEqual(bee_item["id"], "growthcraft:bee")
        self.assertEqual(bee_item["Count"], 5)
        # Pszczoły powinny mieć tag BEE
        self.assertIn("tag", bee_item)
        self.assertEqual(bee_item["tag"]["BEE"], 1)
    
    def test_comb_conversion(self):
        """Test konwersji plastrów miodu"""
        nbt_1710 = {
            "id": "grcbees:bee_box",
            "items": [
                {"id": "grcbees:honey_comb_full", "Count": 8, "Slot": 5}
            ]
        }
        
        result = self.converter.convert(nbt_1710)
        nbt_1182 = result.converted_nbt
        
        items = nbt_1182["inventory"]["Items"]
        comb_item = next((i for i in items if i["Slot"] == 5), None)
        
        self.assertIsNotNone(comb_item)
        self.assertEqual(comb_item["id"], "growthcraft:honey_comb_full")


class TestMixingVatConverter(unittest.TestCase):
    """Testy dla MixingVatNBTConverter"""
    
    def setUp(self):
        self.converter = MixingVatNBTConverter()
    
    def test_basic_conversion(self):
        """Test podstawowej konwersji NBT"""
        nbt_1710 = {
            "id": "grcmilk:cheese_vat",
            "progress": 1200.0,
            "progress_max": 2400,
            "vat_state": "preparing_cheese",
            "heat_component": {
                "heat_multiplier": 1.0
            },
            "TankPrimary": {
                "FluidName": "grcmilk:milk",
                "Amount": 1000
            },
            "TankWaste": {
                "FluidName": "grcmilk:whey",
                "Amount": 0
            },
            "items": [
                {"id": "grcmilk:rennet", "Count": 1, "Slot": 0},
                {"id": "growthcraft:salt", "Count": 1, "Slot": 1}
            ]
        }
        
        result = self.converter.convert(nbt_1710)
        
        self.assertTrue(result.success)
        nbt_1182 = result.converted_nbt
        
        self.assertEqual(nbt_1182["id"], "growthcraft:mixing_vat")
        self.assertEqual(nbt_1182["CurrentProcessTicks"], 1200)
        self.assertEqual(nbt_1182["MaxProcessTicks"], 2400)
        self.assertTrue(nbt_1182["RequiresHeatSource"])
        self.assertTrue(nbt_1182["IsActivated"])
    
    def test_activation_system(self):
        """Test systemu aktywacji"""
        # Test dla aktywnego procesu
        nbt_1710_active = {
            "id": "grcmilk:cheese_vat",
            "vat_state": "preparing_cheese",
            "heat_component": {"heat_multiplier": 1.0},
            "TankPrimary": {"FluidName": "grcmilk:milk", "Amount": 1000}
        }
        
        result = self.converter.convert(nbt_1710_active)
        nbt_1182 = result.converted_nbt
        
        self.assertTrue(nbt_1182["IsActivated"])
        self.assertIn("ActivationTool", nbt_1182)
        self.assertIn("ResultActivationTool", nbt_1182)
        self.assertEqual(nbt_1182["ActivationTool"]["id"], "minecraft:wooden_sword")
    
    def test_idle_state_not_activated(self):
        """Test że idle nie jest aktywowane"""
        nbt_1710_idle = {
            "id": "grcmilk:cheese_vat",
            "vat_state": "idle",
            "heat_component": {"heat_multiplier": 0.0},
            "TankPrimary": {"FluidName": "grcmilk:milk", "Amount": 0}
        }
        
        result = self.converter.convert(nbt_1710_idle)
        nbt_1182 = result.converted_nbt
        
        self.assertFalse(nbt_1182["IsActivated"])
        self.assertNotIn("ActivationTool", nbt_1182)
    
    def test_tank_conversion(self):
        """Test konwersji zbiorników"""
        nbt_1710 = {
            "id": "grcmilk:cheese_vat",
            "TankPrimary": {"FluidName": "grcmilk:milk", "Amount": 2000},
            "TankWaste": {"FluidName": "grcmilk:whey", "Amount": 500}
        }
        
        result = self.converter.convert(nbt_1710)
        nbt_1182 = result.converted_nbt
        
        self.assertIn("InputFluidTank", nbt_1182)
        self.assertIn("ReagentFluidTank", nbt_1182)
        
        input_tank = nbt_1182["InputFluidTank"]
        self.assertEqual(input_tank["FluidName"], "growthcraft:milk")
        self.assertEqual(input_tank["Amount"], 2000)


def run_tests():
    """Uruchamia wszystkie testy"""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    suite.addTests(loader.loadTestsFromTestCase(TestFermentationBarrelConverter))
    suite.addTests(loader.loadTestsFromTestCase(TestBrewKettleConverter))
    suite.addTests(loader.loadTestsFromTestCase(TestBeeBoxConverter))
    suite.addTests(loader.loadTestsFromTestCase(TestMixingVatConverter))
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)
