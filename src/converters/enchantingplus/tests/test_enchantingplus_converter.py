"""
Tests for Enchanting Plus Converter

Testy jednostkowe dla konwertera Enchanting Plus.
"""

import unittest
import sys
import os

# Dodaj parent directory do path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..'))

from converters.enchantingplus import EnchantingPlusConverter
from converters.enchantingplus.mappings.block_mappings import (
    get_block_mapping,
    BLOCK_MAPPINGS_1710_TO_1182,
    is_enchantingplus_block,
)


class TestBlockMappings(unittest.TestCase):
    """Testy dla mapowań bloków"""
    
    def test_enchanting_table_mapping(self):
        """Test mapowania podstawowego stołu"""
        mapping = get_block_mapping('EnchantingPlus:enchanting_table')
        self.assertIsNotNone(mapping)
        self.assertEqual(mapping.id_1182, 'enchantinginfuser:enchanting_infuser')
        self.assertTrue(mapping.has_tile_entity)
    
    def test_advanced_table_mapping(self):
        """Test mapowania zaawansowanego stołu"""
        mapping = get_block_mapping('EnchantingPlus:advanced_table')
        self.assertIsNotNone(mapping)
        self.assertEqual(mapping.id_1182, 'enchantinginfuser:advanced_enchanting_infuser')
        self.assertTrue(mapping.has_tile_entity)
    
    def test_arcane_inscriber_mapping(self):
        """Test mapowania Arcane Inscriber (do usunięcia)"""
        mapping = get_block_mapping('EnchantingPlus:arcane_inscriber')
        self.assertIsNotNone(mapping)
        self.assertEqual(mapping.id_1182, 'minecraft:air')
    
    def test_invalid_block(self):
        """Test nieistniejącego bloku"""
        mapping = get_block_mapping('EnchantingPlus:invalid_block')
        self.assertIsNone(mapping)
    
    def test_is_enchantingplus_block(self):
        """Test funkcji sprawdzającej blok EP"""
        self.assertTrue(is_enchantingplus_block('EnchantingPlus:enchanting_table'))
        self.assertTrue(is_enchantingplus_block('EnchantingPlus:advanced_table'))
        self.assertTrue(is_enchantingplus_block('EnchantingPlus:arcane_inscriber'))
        self.assertFalse(is_enchantingplus_block('minecraft:stone'))
        self.assertFalse(is_enchantingplus_block('ae2:controller'))


class TestEnchantingPlusConverter(unittest.TestCase):
    """Testy dla głównego konwertera"""
    
    def setUp(self):
        """Inicjalizacja konwertera przed każdym testem"""
        self.converter = EnchantingPlusConverter()
    
    def test_converter_initialization(self):
        """Test inicjalizacji konwertera"""
        self.assertEqual(self.converter.SOURCE_MOD, 'Enchanting Plus')
        self.assertEqual(self.converter.TARGET_MOD, 'Enchanting Infuser')
        self.assertEqual(self.converter.SOURCE_VERSION, '1.7.10')
        self.assertEqual(self.converter.TARGET_VERSION, '1.18.2')
    
    def test_convert_enchanting_table(self):
        """Test konwersji podstawowego stołu"""
        result = self.converter.convert_block(
            'EnchantingPlus:enchanting_table',
            position=(100, 64, 100)
        )
        
        self.assertTrue(result.converted.success)
        self.assertEqual(result.original_id, 'EnchantingPlus:enchanting_table')
        self.assertEqual(result.converted.block_id_1182, 'enchantinginfuser:enchanting_infuser')
        self.assertEqual(result.original_pos, (100, 64, 100))
    
    def test_convert_advanced_table(self):
        """Test konwersji zaawansowanego stołu"""
        result = self.converter.convert_block(
            'EnchantingPlus:advanced_table',
            position=(101, 64, 100)
        )
        
        self.assertTrue(result.converted.success)
        self.assertEqual(result.original_id, 'EnchantingPlus:advanced_table')
        self.assertEqual(result.converted.block_id_1182, 'enchantinginfuser:advanced_enchanting_infuser')
    
    def test_convert_arcane_inscriber(self):
        """Test konwersji Arcane Inscriber (powinien być usunięty)"""
        result = self.converter.convert_block(
            'EnchantingPlus:arcane_inscriber',
            position=(102, 64, 100)
        )
        
        # Konwersja "udana" - blok zostaje usunięty
        self.assertTrue(result.converted.success)
        self.assertEqual(result.converted.block_id_1182, 'minecraft:air')
        self.assertGreater(len(result.converted.warnings), 0)
    
    def test_convert_invalid_block(self):
        """Test konwersji nieprawidłowego bloku"""
        result = self.converter.convert_block(
            'minecraft:stone',
            position=(100, 64, 100)
        )
        
        self.assertFalse(result.converted.success)
        self.assertGreater(len(result.converted.errors), 0)
    
    def test_convert_with_nbt(self):
        """Test konwersji z NBT"""
        nbt_data = {
            'id': 'EnchantingPlus:enchanting_table',
            'x': 100,
            'y': 64,
            'z': 100,
            'some_custom_data': 'test_value'
        }
        
        result = self.converter.convert_block(
            'EnchantingPlus:enchanting_table',
            nbt_1710=nbt_data,
            position=(100, 64, 100)
        )
        
        self.assertTrue(result.converted.success)
        # NBT powinien być oczyszczony z pól specyficznych dla 1.7.10
        if result.converted.nbt_1182:
            self.assertNotIn('id', result.converted.nbt_1182)
            self.assertNotIn('x', result.converted.nbt_1182)
            self.assertNotIn('y', result.converted.nbt_1182)
            self.assertNotIn('z', result.converted.nbt_1182)
    
    def test_batch_convert(self):
        """Test batch conversion"""
        blocks = [
            {'id': 'EnchantingPlus:enchanting_table', 'pos': (100, 64, 100)},
            {'id': 'EnchantingPlus:advanced_table', 'pos': (101, 64, 100)},
            {'id': 'EnchantingPlus:arcane_inscriber', 'pos': (102, 64, 100)},
        ]
        
        results = self.converter.batch_convert(blocks)
        
        self.assertEqual(len(results), 3)
        self.assertEqual(results[0].converted.block_id_1182, 'enchantinginfuser:enchanting_infuser')
        self.assertEqual(results[1].converted.block_id_1182, 'enchantinginfuser:advanced_enchanting_infuser')
        self.assertEqual(results[2].converted.block_id_1182, 'minecraft:air')
    
    def test_get_supported_blocks(self):
        """Test pobierania listy obsługiwanych bloków"""
        blocks = self.converter.get_supported_blocks()
        self.assertEqual(len(blocks), 3)
        self.assertIn('EnchantingPlus:enchanting_table', blocks)
        self.assertIn('EnchantingPlus:advanced_table', blocks)
        self.assertIn('EnchantingPlus:arcane_inscriber', blocks)
    
    def test_get_conversion_report(self):
        """Test generowania raportu konwersji"""
        report = self.converter.get_conversion_report()
        
        self.assertEqual(report['source_mod'], 'Enchanting Plus')
        self.assertEqual(report['target_mod'], 'Enchanting Infuser')
        self.assertEqual(report['supported_blocks'], 3)
        self.assertEqual(report['blocks_converted'], 2)
        self.assertEqual(report['blocks_removed'], 1)


class TestIntegration(unittest.TestCase):
    """Testy integracyjne"""
    
    def test_full_conversion_workflow(self):
        """Test pełnego workflow konwersji"""
        converter = EnchantingPlusConverter()
        
        # Symulacja rzeczywistych danych z mapy
        blocks_from_map = [
            {
                'id': 'EnchantingPlus:enchanting_table',
                'pos': (100, 64, 100),
                'nbt': {
                    'id': 'EnchantingPlus:enchanting_table',
                    'x': 100, 'y': 64, 'z': 100
                },
                'metadata': 0
            },
            {
                'id': 'EnchantingPlus:advanced_table',
                'pos': (101, 64, 100),
                'nbt': {
                    'id': 'EnchantingPlus:advanced_table',
                    'x': 101, 'y': 64, 'z': 100
                },
                'metadata': 0
            },
        ]
        
        results = converter.batch_convert(blocks_from_map)
        
        # Weryfikacja wyników
        self.assertEqual(len(results), 2)
        
        # Wszystkie konwersje powinny być udane
        for result in results:
            self.assertTrue(result.converted.success)
            self.assertIsNotNone(result.converted.block_id_1182)
        
        # Sprawdzenie poprawności mapowania
        self.assertEqual(results[0].converted.block_id_1182, 'enchantinginfuser:enchanting_infuser')
        self.assertEqual(results[1].converted.block_id_1182, 'enchantinginfuser:advanced_enchanting_infuser')


def run_tests():
    """Uruchamia wszystkie testy"""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Dodaj testy
    suite.addTests(loader.loadTestsFromTestCase(TestBlockMappings))
    suite.addTests(loader.loadTestsFromTestCase(TestEnchantingPlusConverter))
    suite.addTests(loader.loadTestsFromTestCase(TestIntegration))
    
    # Uruchom testy
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return result.wasSuccessful()


if __name__ == '__main__':
    success = run_tests()
    sys.exit(0 if success else 1)
