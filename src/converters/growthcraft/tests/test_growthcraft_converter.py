"""
Testy integracyjne dla GrowthcraftConverter

Testuje główną klasę konwertera i integrację wszystkich komponentów.
"""

import sys
import os
import unittest

# Dodaj ścieżkę do src
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..'))

from converters.growthcraft.growthcraft_converter import (
    GrowthcraftConverter,
    convert_growthcraft_te,
    get_converter_for_te,
)
from converters.growthcraft.mappings import GROWTHCRAFT_CE_EXPERIMENTAL, STRICT_1182_FUNCTIONAL


class TestGrowthcraftConverter(unittest.TestCase):
    """Testy dla głównej klasy GrowthcraftConverter"""
    
    def setUp(self):
        self.converter = GrowthcraftConverter()
    
    def test_converter_initialization(self):
        """Test inicjalizacji konwertera"""
        self.assertIsNotNone(self.converter)
        self.assertEqual(self.converter.profile, STRICT_1182_FUNCTIONAL)
        self.assertEqual(self.converter.stats["processed"], 0)
        self.assertEqual(self.converter.stats["converted"], 0)
    
    def test_is_growthcraft_block(self):
        """Test rozpoznawania bloków GrowthCraft"""
        self.assertTrue(self.converter.is_growthcraft_block("grccellar:ferment_barrel"))
        self.assertTrue(self.converter.is_growthcraft_block("grcmilk:cheese_vat"))
        self.assertTrue(self.converter.is_growthcraft_block("grcbees:bee_box"))
        self.assertTrue(self.converter.is_growthcraft_block("growthcraft:salt_block"))
        
        self.assertFalse(self.converter.is_growthcraft_block("minecraft:stone"))
        self.assertFalse(self.converter.is_growthcraft_block("ae2:controller"))
    
    def test_is_growthcraft_item(self):
        """Test rozpoznawania itemów GrowthCraft"""
        self.assertTrue(self.converter.is_growthcraft_item("grccellar:yeast"))
        self.assertTrue(self.converter.is_growthcraft_item("grcmilk:rennet"))
        self.assertTrue(self.converter.is_growthcraft_item("grcbees:bee"))
        
        self.assertFalse(self.converter.is_growthcraft_item("minecraft:stone"))
    
    def test_convert_fermentation_barrel(self):
        """Test konwersji FermentationBarrel"""
        nbt_1710 = {
            "id": "grccellar:ferment_barrel",
            "time": 1200,
            "Tank": {"FluidName": "grccellar:apple_juice", "Amount": 2000},
            "items": [{"id": "grccellar:yeast", "Count": 1, "Slot": 0}]
        }
        
        result = self.converter.convert_block(
            block_id="grccellar:ferment_barrel",
            metadata=0,
            nbt=nbt_1710
        )
        
        self.assertTrue(result.success)
        self.assertEqual(result.block_id_1182, "brewinandchewin:keg")
        self.assertIsNotNone(result.nbt_1182)
        self.assertEqual(result.nbt_1182["id"], "brewinandchewin:keg")
        self.assertIn("legacy_growthcraft", result.nbt_1182)
        self.assertTrue(any("GC-W-FUNCTIONAL-REBUILD" in w for w in result.warnings))
    
    def test_convert_brew_kettle(self):
        """Test konwersji BrewKettle"""
        nbt_1710 = {
            "id": "grccellar:brew_kettle",
            "brew_kettle": {"time": 600, "time_max": 1200},
            "TankInput": {"FluidName": "minecraft:water", "Amount": 1000}
        }
        
        result = self.converter.convert_block(
            block_id="grccellar:brew_kettle",
            metadata=0,
            nbt=nbt_1710
        )
        
        self.assertTrue(result.success)
        self.assertEqual(result.block_id_1182, "brewinandchewin:keg")
    
    def test_convert_bee_box(self):
        """Test konwersji BeeBox"""
        nbt_1710 = {
            "id": "grcbees:bee_box",
            "bee_box": {"bee_count": 3, "version": 3},
            "items": [{"id": "grcbees:bee", "Count": 3, "Slot": 0}]
        }
        
        result = self.converter.convert_block(
            block_id="grcbees:bee_box",
            metadata=0,
            nbt=nbt_1710
        )
        
        self.assertTrue(result.success)
        self.assertEqual(result.block_id_1182, "minecraft:beehive")
    
    def test_convert_mixing_vat(self):
        """Test konwersji MixingVat (CheeseVat)"""
        nbt_1710 = {
            "id": "grcmilk:cheese_vat",
            "progress": 1200,
            "vat_state": "preparing_cheese",
            "heat_component": {"heat_multiplier": 1.0},
            "TankPrimary": {"FluidName": "grcmilk:milk", "Amount": 1000}
        }
        
        result = self.converter.convert_block(
            block_id="grcmilk:cheese_vat",
            metadata=0,
            nbt=nbt_1710
        )
        
        self.assertTrue(result.success)
        self.assertEqual(result.block_id_1182, "farmersdelight:cooking_pot")
        self.assertEqual(result.nbt_1182["legacy_growthcraft"]["vat_state"], "preparing_cheese")
    
    def test_convert_block_without_nbt(self):
        """Test konwersji bloku bez NBT"""
        result = self.converter.convert_block(
            block_id="grccellar:ferment_barrel",
            metadata=0,
            nbt=None
        )
        
        self.assertTrue(result.success)
        self.assertEqual(result.block_id_1182, "brewinandchewin:keg")
        self.assertIsNone(result.nbt_1182)
    
    def test_convert_non_growthcraft_block(self):
        """Test odmowy konwersji nie-GrowthCraft bloku"""
        result = self.converter.convert_block(
            block_id="minecraft:stone",
            metadata=0,
            nbt=None
        )
        
        self.assertFalse(result.success)
        self.assertTrue(len(result.errors) > 0)
    
    def test_get_supported_blocks(self):
        """Test pobierania listy obsługiwanych bloków"""
        blocks = self.converter.get_supported_blocks()
        
        self.assertIn("grccellar:ferment_barrel", blocks)
        self.assertIn("grccellar:brew_kettle", blocks)
        self.assertIn("grcbees:bee_box", blocks)
        self.assertIn("grcmilk:cheese_vat", blocks)
    
    def test_stats_tracking(self):
        """Test śledzenia statystyk"""
        self.converter.reset_stats()
        self.assertEqual(self.converter.stats["processed"], 0)
        
        # Przetwórz kilka bloków
        self.converter.convert_block("grccellar:ferment_barrel", 0, None)
        self.converter.convert_block("grcbees:bee_box", 0, None)
        self.converter.convert_block("minecraft:stone", 0, None)  # Nie GrowthCraft
        
        stats = self.converter.get_stats()
        self.assertEqual(stats["processed"], 3)
        self.assertEqual(stats["converted"], 2)
        self.assertEqual(stats["failed"], 1)
    
    def test_reset_stats(self):
        """Test resetowania statystyk"""
        self.converter.convert_block("grccellar:ferment_barrel", 0, None)
        self.assertGreater(self.converter.stats["processed"], 0)
        
        self.converter.reset_stats()
        self.assertEqual(self.converter.stats["processed"], 0)
        self.assertEqual(self.converter.stats["converted"], 0)


class TestHelperFunctions(unittest.TestCase):
    """Testy funkcji pomocniczych"""
    
    def test_convert_growthcraft_te(self):
        """Test funkcji convert_growthcraft_te"""
        nbt_1710 = {
            "id": "grccellar:ferment_barrel",
            "time": 1200,
            "Tank": {"FluidName": "grccellar:apple_juice", "Amount": 2000}
        }
        
        new_id, new_nbt, warnings = convert_growthcraft_te(
            te_id="grccellar:ferment_barrel",
            nbt=nbt_1710,
            metadata=0
        )
        
        self.assertEqual(new_id, "brewinandchewin:keg")
        self.assertIsNotNone(new_nbt)
        self.assertEqual(new_nbt["id"], "brewinandchewin:keg")
        self.assertIn("legacy_growthcraft", new_nbt)
    
    def test_get_converter_for_te(self):
        """Test funkcji get_converter_for_te"""
        converter_class = get_converter_for_te("grccellar:ferment_barrel")
        self.assertIsNotNone(converter_class)
        
        from converters.growthcraft.nbt_converters import FermentationBarrelNBTConverter
        self.assertEqual(converter_class, FermentationBarrelNBTConverter)
        
        # Nieistniejący konwerter
        none_converter = get_converter_for_te("grccellar:nonexistent")
        self.assertIsNone(none_converter)


class TestInventoryConversion(unittest.TestCase):
    """Testy konwersji inventory"""
    
    def setUp(self):
        self.converter = GrowthcraftConverter(profile=GROWTHCRAFT_CE_EXPERIMENTAL)
    
    def test_item_conversion_in_nbt(self):
        """Test konwersji itemów w NBT"""
        nbt_1710 = {
            "id": "grccellar:ferment_barrel",
            "items": [
                {"id": "grccellar:yeast", "Count": 5, "Slot": 0}
            ]
        }
        
        result = self.converter.convert_block("grccellar:ferment_barrel", 0, nbt_1710)
        nbt_1182 = result.nbt_1182
        
        items = nbt_1182["inventory"]["Items"]
        self.assertEqual(items[0]["id"], "growthcraft_cellar:yeast")
        self.assertEqual(items[0]["Count"], 5)
    
    def test_fluid_conversion_in_nbt(self):
        """Test konwersji płynów w NBT"""
        nbt_1710 = {
            "id": "grccellar:ferment_barrel",
            "Tank": {"FluidName": "grccellar:grape_juice", "Amount": 3000}
        }
        
        result = self.converter.convert_block("grccellar:ferment_barrel", 0, nbt_1710)
        nbt_1182 = result.nbt_1182
        
        fluid = nbt_1182["fluid_tank_input_0"]
        self.assertEqual(fluid["FluidName"], "growthcraft_cellar:grape_juice")


class TestEdgeCases(unittest.TestCase):
    """Testy przypadków brzegowych"""
    
    def setUp(self):
        self.converter = GrowthcraftConverter(profile=GROWTHCRAFT_CE_EXPERIMENTAL)
    
    def test_empty_nbt(self):
        """Test konwersji pustego NBT"""
        result = self.converter.convert_block("grccellar:ferment_barrel", 0, {})
        self.assertTrue(result.success)
    
    def test_none_nbt(self):
        """Test konwersji z None NBT"""
        result = self.converter.convert_block("grccellar:ferment_barrel", 0, None)
        self.assertTrue(result.success)
        self.assertIsNone(result.nbt_1182)
    
    def test_missing_fields_in_nbt(self):
        """Test konwersji NBT z brakującymi polami"""
        nbt_1710 = {
            "id": "grccellar:ferment_barrel"
            # Brak time, Tank, items
        }
        
        result = self.converter.convert_block("grccellar:ferment_barrel", 0, nbt_1710)
        self.assertTrue(result.success)
        self.assertEqual(result.nbt_1182["CurrentProcessTicks"], 0)
    
    def test_damage_conversion(self):
        """Test konwersji damage/metadata itemu"""
        nbt_1710 = {
            "id": "grccellar:ferment_barrel",
            "items": [
                {"id": "grccellar:yeast", "Count": 1, "Slot": 0, "Damage": 5}
            ]
        }
        
        result = self.converter.convert_block("grccellar:ferment_barrel", 0, nbt_1710)
        nbt_1182 = result.nbt_1182
        
        item = nbt_1182["inventory"]["Items"][0]
        self.assertIn("tag", item)
        self.assertEqual(item["tag"]["Damage"], 5)


def run_integration_tests():
    """Uruchamia wszystkie testy integracyjne"""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    suite.addTests(loader.loadTestsFromTestCase(TestGrowthcraftConverter))
    suite.addTests(loader.loadTestsFromTestCase(TestHelperFunctions))
    suite.addTests(loader.loadTestsFromTestCase(TestInventoryConversion))
    suite.addTests(loader.loadTestsFromTestCase(TestEdgeCases))
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_integration_tests()
    sys.exit(0 if success else 1)
