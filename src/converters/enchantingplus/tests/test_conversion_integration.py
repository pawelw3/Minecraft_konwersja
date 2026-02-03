"""
Integration Test for Enchanting Plus Converter

Test integracyjny symulujący konwersję bloków Enchanting Plus.
Ponieważ bloki EP nie występują na mapie głównej, test tworzy
symulowane dane i weryfikuje poprawność konwersji.
"""

import unittest
import sys
import os
import json
from pathlib import Path

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..'))

from converters.enchantingplus import EnchantingPlusConverter


class TestConversionIntegration(unittest.TestCase):
    """Test integracyjny konwersji"""
    
    def setUp(self):
        """Inicjalizacja"""
        self.converter = EnchantingPlusConverter()
        self.test_results_dir = Path(__file__).parent / 'test_results'
        self.test_results_dir.mkdir(exist_ok=True)
    
    def test_simulated_world_conversion(self):
        """
        Test konwersji symulowanego świata z blokami EP.
        
        Symuluje rzeczywiste użycie moda - stół enchantujący
        w typowej bazie gracza.
        """
        # Symulowane dane ze świata (jakie pojawiłyby się z parsera NBT)
        simulated_world_blocks = [
            {
                'id': 'EnchantingPlus:enchanting_table',
                'pos': (100, 64, 100),
                'nbt': {
                    'id': 'EnchantingPlus:enchanting_table',
                    'x': 100, 'y': 64, 'z': 100,
                    # EP ma proste NBT - głównie tylko podstawowe pola TileEntity
                },
                'metadata': 0,
                'description': 'Podstawowy stół w bazie gracza'
            },
            {
                'id': 'EnchantingPlus:advanced_table',
                'pos': (101, 64, 100),
                'nbt': {
                    'id': 'EnchantingPlus:advanced_table',
                    'x': 101, 'y': 64, 'z': 100,
                },
                'metadata': 0,
                'description': 'Zaawansowany stół obok podstawowego'
            },
            {
                'id': 'EnchantingPlus:arcane_inscriber',
                'pos': (102, 64, 100),
                'nbt': {
                    'id': 'EnchantingPlus:arcane_inscriber',
                    'x': 102, 'y': 64, 'z': 100,
                },
                'metadata': 0,
                'description': 'Arcane Inscriber (do usunięcia)'
            },
            {
                'id': 'EnchantingPlus:enchanting_table',
                'pos': (200, 70, 200),
                'nbt': {
                    'id': 'EnchantingPlus:enchanting_table',
                    'x': 200, 'y': 70, 'z': 200,
                },
                'metadata': 0,
                'description': 'Drugi stół w innym miejscu na mapie'
            },
            {
                'id': 'EnchantingPlus:advanced_table',
                'pos': (-50, 65, -100),
                'nbt': {
                    'id': 'EnchantingPlus:advanced_table',
                    'x': -50, 'y': 65, 'z': -100,
                },
                'metadata': 0,
                'description': 'Stół w ujemnych koordynatach'
            },
        ]
        
        # Konwersja
        results = self.converter.batch_convert(simulated_world_blocks)
        
        # Weryfikacja liczby wyników
        self.assertEqual(len(results), len(simulated_world_blocks))
        
        # Weryfikacja poprawności konwersji
        successful_conversions = 0
        removed_blocks = 0
        errors = []
        
        for i, result in enumerate(results):
            original = simulated_world_blocks[i]
            
            # Sprawdź czy pozycja jest zachowana
            self.assertEqual(result.original_pos, original['pos'])
            
            # Sprawdź czy ID źródłowe jest zachowane
            self.assertEqual(result.original_id, original['id'])
            
            if result.converted.success:
                successful_conversions += 1
                
                # Sprawdź poprawność mapowania
                if original['id'] == 'EnchantingPlus:enchanting_table':
                    self.assertEqual(
                        result.converted.block_id_1182,
                        'enchantinginfuser:enchanting_infuser'
                    )
                elif original['id'] == 'EnchantingPlus:advanced_table':
                    self.assertEqual(
                        result.converted.block_id_1182,
                        'enchantinginfuser:advanced_enchanting_infuser'
                    )
                elif original['id'] == 'EnchantingPlus:arcane_inscriber':
                    # Ten blok powinien być usunięty
                    self.assertEqual(result.converted.block_id_1182, 'minecraft:air')
                    removed_blocks += 1
                    self.assertGreater(len(result.converted.warnings), 0)
            else:
                errors.append({
                    'block': original['id'],
                    'pos': original['pos'],
                    'errors': result.converted.errors
                })
        
        # Raport
        print("\n" + "=" * 60)
        print("SYMULOWANA KONWERSJA ŚWIATA - RAPORT")
        print("=" * 60)
        print(f"Łącznie bloków: {len(simulated_world_blocks)}")
        print(f"Udanych konwersji: {successful_conversions}")
        print(f"Usuniętych bloków: {removed_blocks}")
        print(f"Błędów: {len(errors)}")
        
        # Wszystkie konwersje powinny być udane
        self.assertEqual(successful_conversions, len(simulated_world_blocks))
        self.assertEqual(removed_blocks, 1)  # Tylko Arcane Inscriber
        self.assertEqual(len(errors), 0)
        
        # Zapisz raport
        report = {
            'test_name': 'simulated_world_conversion',
            'total_blocks': len(simulated_world_blocks),
            'successful': successful_conversions,
            'removed': removed_blocks,
            'errors': errors,
            'conversions': [
                {
                    'original_id': r.original_id,
                    'position': r.original_pos,
                    'new_id': r.converted.block_id_1182,
                    'success': r.converted.success,
                    'warnings': r.converted.warnings
                }
                for r in results
            ]
        }
        
        report_file = self.test_results_dir / 'simulated_conversion_report.json'
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)
        
        print(f"\nRaport zapisany: {report_file}")
    
    def test_edge_cases(self):
        """Test przypadków brzegowych"""
        
        # Test 1: Blok bez NBT
        result = self.converter.convert_block(
            'EnchantingPlus:enchanting_table',
            position=(0, 0, 0),
            nbt_1710=None
        )
        self.assertTrue(result.converted.success)
        self.assertIsNone(result.converted.nbt_1182)
        
        # Test 2: Blok z pustym NBT
        result = self.converter.convert_block(
            'EnchantingPlus:enchanting_table',
            position=(0, 0, 0),
            nbt_1710={}
        )
        self.assertTrue(result.converted.success)
        
        # Test 3: Nietypowe koordynaty
        edge_coords = [
            (0, 0, 0),  # Origin
            (-1000, 10, -1000),  # Daleko w ujemnych
            (1000000, 100, 1000000),  # Daleko w dodatnich
            (0, 255, 0),  # Wysoko (max Y w 1.7.10)
            (0, 1, 0),  # Nisko
        ]
        
        for pos in edge_coords:
            result = self.converter.convert_block(
                'EnchantingPlus:enchanting_table',
                position=pos
            )
            self.assertTrue(result.converted.success)
            self.assertEqual(result.original_pos, pos)
    
    def test_conversion_report_generation(self):
        """Test generowania raportu konwersji"""
        report = self.converter.get_conversion_report()
        
        # Weryfikacja struktury raportu
        self.assertIn('source_mod', report)
        self.assertIn('target_mod', report)
        self.assertIn('supported_blocks', report)
        self.assertIn('blocks_converted', report)
        self.assertIn('blocks_removed', report)
        
        # Weryfikacja wartości
        self.assertEqual(report['source_mod'], 'Enchanting Plus')
        self.assertEqual(report['target_mod'], 'Enchanting Infuser')
        self.assertEqual(report['supported_blocks'], 3)
        self.assertEqual(report['blocks_converted'], 2)
        self.assertEqual(report['blocks_removed'], 1)
        
        # Zapisz raport
        report_file = self.test_results_dir / 'conversion_capabilities_report.json'
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)
        
        print(f"\nRaport możliwości konwersji zapisany: {report_file}")
    
    def test_nbt_data_preservation(self):
        """Test zachowania danych NBT podczas konwersji"""
        
        # NBT z dodatkowymi danymi (jeśli EP miałby customowe dane)
        custom_nbt = {
            'id': 'EnchantingPlus:enchanting_table',
            'x': 100, 'y': 64, 'z': 100,
            'custom_data': 'test_value',
            'some_number': 42,
            'nested': {'key': 'value'}
        }
        
        result = self.converter.convert_block(
            'EnchantingPlus:enchanting_table',
            position=(100, 64, 100),
            nbt_1710=custom_nbt
        )
        
        self.assertTrue(result.converted.success)
        
        # Sprawdź czy NBT zostało przekonwertowane
        if result.converted.nbt_1182:
            # Pola specyficzne dla 1.7.10 powinny być usunięte
            self.assertNotIn('id', result.converted.nbt_1182)
            self.assertNotIn('x', result.converted.nbt_1182)
            self.assertNotIn('y', result.converted.nbt_1182)
            self.assertNotIn('z', result.converted.nbt_1182)
            
            # Customowe dane powinny być zachowane (przez IdentityConverter)
            self.assertIn('custom_data', result.converted.nbt_1182)
            self.assertEqual(result.converted.nbt_1182['custom_data'], 'test_value')


class TestRealWorldScenario(unittest.TestCase):
    """Test scenariusza z rzeczywistego użycia"""
    
    def setUp(self):
        self.converter = EnchantingPlusConverter()
    
    def test_player_base_setup(self):
        """
        Test konwersji typowego setupu bazy gracza.
        
        Scenariusz: Gracz ma stół EP w swojej bazie wraz z
        bookshelfvami i innymi blokami (vanilla).
        """
        # Bloki które mogłyby wystąpić w bazie gracza
        base_setup = [
            # Główny stół enchantujący
            {
                'id': 'EnchantingPlus:enchanting_table',
                'pos': (10, 64, 10),
                'nbt': {'id': 'EnchantingPlus:enchanting_table', 'x': 10, 'y': 64, 'z': 10}
            },
            # Zaawansowany stół (jeśli gracz miał lepszy setup)
            {
                'id': 'EnchantingPlus:advanced_table',
                'pos': (12, 64, 10),
                'nbt': {'id': 'EnchantingPlus:advanced_table', 'x': 12, 'y': 64, 'z': 10}
            },
        ]
        
        results = self.converter.batch_convert(base_setup)
        
        # Weryfikacja
        self.assertEqual(len(results), 2)
        
        # Stół podstawowy
        self.assertEqual(
            results[0].converted.block_id_1182,
            'enchantinginfuser:enchanting_infuser'
        )
        
        # Stół zaawansowany
        self.assertEqual(
            results[1].converted.block_id_1182,
            'enchantinginfuser:advanced_enchanting_infuser'
        )
        
        print("\n" + "=" * 60)
        print("SCENARIUSZ: BAZA GRACZA")
        print("=" * 60)
        print(f"Przekonwertowano {len(results)} bloków w bazie gracza")
        print("- Stół podstawowy: EnchantingPlus -> Enchanting Infuser")
        print("- Stół zaawansowany: EnchantingPlus -> Advanced Enchanting Infuser")
        print("\nUWAGA: Wokół stołów należy ustawić bookshelfvy (vanilla)")
        print("aby odblokować wyższe poziomy enchantów.")


def run_integration_tests():
    """Uruchamia testy integracyjne"""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    suite.addTests(loader.loadTestsFromTestCase(TestConversionIntegration))
    suite.addTests(loader.loadTestsFromTestCase(TestRealWorldScenario))
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return result.wasSuccessful()


if __name__ == '__main__':
    success = run_integration_tests()
    sys.exit(0 if success else 1)
