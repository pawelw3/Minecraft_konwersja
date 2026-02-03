"""
Testy jednostkowe dla konwertera EnderStorage

Testy obejmują:
- Konwersję frequency (int -> EnumColour)
- Konwersję TileEnderChest
- Konwersję TileEnderTank
- Konwersję itemów (EnderPouch)
- Mapowania bloków
"""

import sys
import os
import unittest
import uuid

# Dodaj ścieżkę do src dla importów
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..'))

from converters.enderstorage import (
    EnderStorageConverter,
    EnumColour,
    Frequency,
    convert_block_id,
    convert_item_id,
    EnderChestNBTConverter,
    EnderTankNBTConverter,
)


class TestFrequencyConversion(unittest.TestCase):
    """Testy konwersji frequency między formatami 1.7.10 i 1.18.2"""
    
    def test_int_to_frequency_white(self):
        """Test konwersji int 0 (WHITE-WHITE-WHITE)"""
        freq = Frequency.from_int(0)
        self.assertEqual(freq.left, EnumColour.WHITE)
        self.assertEqual(freq.middle, EnumColour.WHITE)
        self.assertEqual(freq.right, EnumColour.WHITE)
    
    def test_int_to_frequency_red_green_blue(self):
        """Test konwersji RGB (RED-GREEN-BLUE)"""
        # RED=14, GREEN=13, BLUE=11
        # freq = (14 << 8) | (13 << 4) | 11 = 3584 + 208 + 11 = 3803
        freq_int = 3803
        freq = Frequency.from_int(freq_int)
        self.assertEqual(freq.left, EnumColour.RED)
        self.assertEqual(freq.middle, EnumColour.GREEN)
        self.assertEqual(freq.right, EnumColour.BLUE)
    
    def test_frequency_to_int(self):
        """Test konwersji Frequency -> int"""
        freq = Frequency(EnumColour.RED, EnumColour.GREEN, EnumColour.BLUE)
        self.assertEqual(freq.to_int(), 3803)
    
    def test_roundtrip_conversion(self):
        """Test pełnej konwersji int -> Frequency -> int"""
        for test_int in [0, 100, 1000, 2048, 3803, 4095]:
            freq = Frequency.from_int(test_int)
            result_int = freq.to_int()
            self.assertEqual(test_int, result_int, f"Failed for int {test_int}")
    
    def test_frequency_to_nbt_1182(self):
        """Test konwersji Frequency do formatu NBT 1.18.2"""
        freq = Frequency(EnumColour.RED, EnumColour.GREEN, EnumColour.BLUE)
        nbt = freq.to_nbt_1182()
        
        self.assertEqual(nbt['left'], 'red')
        self.assertEqual(nbt['middle'], 'green')
        self.assertEqual(nbt['right'], 'blue')
    
    def test_frequency_from_nbt_1182(self):
        """Test tworzenia Frequency z formatu NBT 1.18.2"""
        nbt = {
            'left': 'yellow',
            'middle': 'purple',
            'right': 'cyan'
        }
        freq = Frequency.from_nbt_1182(nbt)
        
        self.assertEqual(freq.left, EnumColour.YELLOW)
        self.assertEqual(freq.middle, EnumColour.PURPLE)
        self.assertEqual(freq.right, EnumColour.CYAN)
    
    def test_all_colours(self):
        """Test wszystkich 16 kolorów"""
        self.assertEqual(len(EnumColour), 16)
        
        for colour in EnumColour:
            freq = Frequency(colour, colour, colour)
            expected_int = (colour.value << 8) | (colour.value << 4) | colour.value
            self.assertEqual(freq.to_int(), expected_int)


class TestBlockMappings(unittest.TestCase):
    """Testy mapowań bloków"""
    
    def test_chest_block_mapping(self):
        """Test mapowania bloku skrzyni (metadata 0)"""
        result = convert_block_id("EnderStorage:blockEnderStorage", 0)
        self.assertEqual(result, "enderstorage:ender_chest")
    
    def test_tank_block_mapping(self):
        """Test mapowania bloku zbiornika (metadata 1)"""
        result = convert_block_id("EnderStorage:blockEnderStorage", 1)
        self.assertEqual(result, "enderstorage:ender_tank")
    
    def test_enderpouch_item_mapping(self):
        """Test mapowania itemu EnderPouch"""
        result = convert_item_id("EnderStorage:enderPouch")
        self.assertEqual(result, "enderstorage:ender_pouch")


class TestEnderChestNBTConverter(unittest.TestCase):
    """Testy konwertera NBT dla TileEnderChest"""
    
    def setUp(self):
        self.converter = EnderChestNBTConverter()
    
    def test_basic_conversion(self):
        """Test podstawowej konwersji skrzyni"""
        nbt_1710 = {
            'freq': 3803,  # RED-GREEN-BLUE
            'owner': 'global',
            'rotation': 2
        }
        
        result = self.converter.convert(nbt_1710)
        
        self.assertTrue(result.success)
        self.assertIn('Frequency', result.converted_nbt)
        self.assertEqual(result.converted_nbt['Frequency']['left'], 'red')
        self.assertEqual(result.converted_nbt['Frequency']['middle'], 'green')
        self.assertEqual(result.converted_nbt['Frequency']['right'], 'blue')
        self.assertEqual(result.converted_nbt['rotation'], 2)
        self.assertEqual(result.converted_nbt['id'], 'enderstorage:ender_chest')
    
    def test_conversion_with_items(self):
        """Test konwersji skrzyni z itemami"""
        nbt_1710 = {
            'freq': 0,  # WHITE-WHITE-WHITE
            'owner': 'global',
            'rotation': 0,
            'Items': [
                {'Slot': 0, 'id': 'minecraft:diamond', 'Count': 32, 'Damage': 0},
                {'Slot': 5, 'id': 'minecraft:iron_ingot', 'Count': 16, 'Damage': 0}
            ]
        }
        
        result = self.converter.convert(nbt_1710)
        
        self.assertTrue(result.success)
        self.assertIn('Items', result.converted_nbt)
        self.assertEqual(len(result.converted_nbt['Items']), 2)
        
        # Sprawdź czy itemy są poprawnie przekonwertowane
        item0 = result.converted_nbt['Items'][0]
        self.assertEqual(item0['id'], 'minecraft:diamond')
        self.assertEqual(item0['Count'], 32)
        self.assertEqual(item0['Slot'], 0)
    
    def test_conversion_with_damage(self):
        """Test konwersji itemu z damage (metadata)"""
        nbt_1710 = {
            'freq': 0,
            'owner': 'global',
            'Items': [
                {'Slot': 0, 'id': 'minecraft:iron_pickaxe', 'Count': 1, 'Damage': 15}
            ]
        }
        
        result = self.converter.convert(nbt_1710)
        
        self.assertTrue(result.success)
        item = result.converted_nbt['Items'][0]
        # W 1.18.2 damage jest w tag, nie jako osobne pole
        self.assertIn('tag', item)
        self.assertEqual(item['tag']['Damage'], 15)


class TestEnderTankNBTConverter(unittest.TestCase):
    """Testy konwertera NBT dla TileEnderTank"""
    
    def setUp(self):
        self.converter = EnderTankNBTConverter()
    
    def test_basic_conversion(self):
        """Test podstawowej konwersji zbiornika"""
        nbt_1710 = {
            'freq': 0,
            'owner': 'global',
            'invert_redstone': False
        }
        
        result = self.converter.convert(nbt_1710)
        
        self.assertTrue(result.success)
        self.assertIn('Frequency', result.converted_nbt)
        self.assertIn('pressure_state', result.converted_nbt)
        self.assertEqual(result.converted_nbt['pressure_state']['invert_redstone'], False)
        self.assertEqual(result.converted_nbt['id'], 'enderstorage:ender_tank')
    
    def test_invert_redstone_conversion(self):
        """Test konwersji z invert_redstone = True"""
        nbt_1710 = {
            'freq': 100,
            'owner': 'global',
            'invert_redstone': True
        }
        
        result = self.converter.convert(nbt_1710)
        
        self.assertTrue(result.success)
        self.assertEqual(result.converted_nbt['pressure_state']['invert_redstone'], True)


class TestEnderStorageConverter(unittest.TestCase):
    """Testy głównego konwertera EnderStorage"""
    
    def setUp(self):
        self.converter = EnderStorageConverter()
    
    def test_convert_chest_block(self):
        """Test konwersji bloku skrzyni"""
        nbt_1710 = {
            'freq': 3803,
            'owner': 'global',
            'rotation': 2
        }
        
        result = self.converter.convert_block(
            block_id="EnderStorage:blockEnderStorage",
            metadata=0,
            nbt=nbt_1710
        )
        
        self.assertTrue(result.success)
        self.assertEqual(result.block_id_1182, "enderstorage:ender_chest")
        self.assertIn('Frequency', result.nbt_1182)
    
    def test_convert_tank_block(self):
        """Test konwersji bloku zbiornika"""
        nbt_1710 = {
            'freq': 100,
            'owner': 'global',
            'invert_redstone': False
        }
        
        result = self.converter.convert_block(
            block_id="EnderStorage:blockEnderStorage",
            metadata=1,
            nbt=nbt_1710
        )
        
        self.assertTrue(result.success)
        self.assertEqual(result.block_id_1182, "enderstorage:ender_tank")
        self.assertIn('Frequency', result.nbt_1182)
    
    def test_convert_block_without_nbt(self):
        """Test konwersji bloku bez NBT"""
        result = self.converter.convert_block(
            block_id="EnderStorage:blockEnderStorage",
            metadata=0
        )
        
        self.assertTrue(result.success)
        self.assertEqual(result.block_id_1182, "enderstorage:ender_chest")
        self.assertIsNone(result.nbt_1182)
    
    def test_invalid_block(self):
        """Test konwersji nieprawidłowego bloku"""
        result = self.converter.convert_block(
            block_id="minecraft:stone",
            metadata=0
        )
        
        self.assertFalse(result.success)
        self.assertTrue(len(result.errors) > 0)
    
    def test_stats_tracking(self):
        """Test śledzenia statystyk"""
        self.converter.reset_stats()
        
        # Konwertuj kilka bloków
        self.converter.convert_block("EnderStorage:blockEnderStorage", 0, {'freq': 0})
        self.converter.convert_block("EnderStorage:blockEnderStorage", 1, {'freq': 0})
        self.converter.convert_block("minecraft:stone", 0)  # nieprawidłowy
        
        stats = self.converter.get_stats()
        self.assertEqual(stats['processed'], 3)
        self.assertEqual(stats['converted'], 2)
        self.assertEqual(stats['failed'], 1)


class TestItemConversion(unittest.TestCase):
    """Testy konwersji itemów"""
    
    def setUp(self):
        self.converter = EnderStorageConverter()
    
    def test_convert_enderpouch(self):
        """Test konwersji EnderPouch z damage (freq)"""
        # damage = 3803 (RED-GREEN-BLUE)
        result = self.converter.convert_item(
            item_id="EnderStorage:enderPouch",
            damage=3803
        )
        
        self.assertTrue(result.success)
        self.assertEqual(result.block_id_1182, "enderstorage:ender_pouch")
        self.assertIn('Frequency', result.nbt_1182)
        self.assertEqual(result.nbt_1182['Frequency']['left'], 'red')
        self.assertEqual(result.nbt_1182['Frequency']['middle'], 'green')
        self.assertEqual(result.nbt_1182['Frequency']['right'], 'blue')
    
    def test_convert_enderpouch_white(self):
        """Test konwersji EnderPouch z freq=0 (WHITE)"""
        result = self.converter.convert_item(
            item_id="EnderStorage:enderPouch",
            damage=0
        )
        
        self.assertTrue(result.success)
        self.assertEqual(result.nbt_1182['Frequency']['left'], 'white')
        self.assertEqual(result.nbt_1182['Frequency']['middle'], 'white')
        self.assertEqual(result.nbt_1182['Frequency']['right'], 'white')


def run_tests():
    """Uruchamia wszystkie testy"""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Dodaj wszystkie klasy testowe
    suite.addTests(loader.loadTestsFromTestCase(TestFrequencyConversion))
    suite.addTests(loader.loadTestsFromTestCase(TestBlockMappings))
    suite.addTests(loader.loadTestsFromTestCase(TestEnderChestNBTConverter))
    suite.addTests(loader.loadTestsFromTestCase(TestEnderTankNBTConverter))
    suite.addTests(loader.loadTestsFromTestCase(TestEnderStorageConverter))
    suite.addTests(loader.loadTestsFromTestCase(TestItemConversion))
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return result.wasSuccessful()


if __name__ == '__main__':
    success = run_tests()
    sys.exit(0 if success else 1)
