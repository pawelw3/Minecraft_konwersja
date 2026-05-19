"""
Tests for AE2 Converter

Testy jednostkowe dla konwertera AE2.
"""

import unittest
import sys
import os

# Dodaj parent dir do path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..'))

from src.converters.ae2 import AE2Converter
from src.converters.ae2.mappings import get_block_mapping, get_item_mapping
from src.converters.ae2.mappings.block_mappings import (
    normalize_block_id,
    resolve_crafting_storage_variant,
)
from src.converters.ae2.nbt_converters import PatternData


class TestBlockMappings(unittest.TestCase):
    """Testy mapowań bloków"""
    
    def test_core_blocks_mapped(self):
        """Sprawdza czy core bloki sa zmapowane"""
        core_blocks = [
            'appliedenergistics2:tile.BlockController',
            'appliedenergistics2:tile.BlockDrive',
            'appliedenergistics2:tile.BlockInterface',
            'appliedenergistics2:tile.BlockCraftingUnit',
        ]
        
        for block_id in core_blocks:
            mapping = get_block_mapping(block_id)
            self.assertIsNotNone(mapping, f"Brak mapowania dla {block_id}")
            self.assertTrue(mapping.id_1182.startswith('ae2:'))
    
    def test_controller_mapping(self):
        """Sprawdza mapowanie Controller"""
        mapping = get_block_mapping('appliedenergistics2:tile.BlockController')
        self.assertEqual(mapping.id_1182, 'ae2:controller')
        self.assertTrue(mapping.has_tile_entity)
    
    def test_drive_mapping(self):
        """Sprawdza mapowanie Drive"""
        mapping = get_block_mapping('appliedenergistics2:tile.BlockDrive')
        self.assertEqual(mapping.id_1182, 'ae2:drive')
        self.assertEqual(mapping.nbt_converter, 'drive')

    def test_raw_nbt_id_alias_mapping(self):
        """Sprawdza aliasy surowych ID TileEntity z mapy"""
        self.assertEqual(
            normalize_block_id('BlockDrive'),
            'appliedenergistics2:tile.BlockDrive'
        )
        mapping = get_block_mapping('BlockCableBus')
        self.assertIsNotNone(mapping)
        self.assertEqual(mapping.id_1182, 'ae2:fluix_block')

    def test_quartz_torch_fixture_alias(self):
        """1.7.10 zapisuje Quartz Fixture jako BlockQuartzTorch"""
        self.assertEqual(
            normalize_block_id('appliedenergistics2:tile.BlockQuartzFixture'),
            'appliedenergistics2:tile.BlockQuartzTorch'
        )
        mapping = get_block_mapping('appliedenergistics2:tile.BlockQuartzTorch')
        self.assertIsNotNone(mapping)
        self.assertEqual(mapping.id_1182, 'ae2:quartz_fixture')


class TestCraftingStorageVariants(unittest.TestCase):
    """Testy wariantow Crafting Storage"""
    
    def test_crafting_storage_variants(self):
        """Sprawdza rozwiazywanie wariantow"""
        test_cases = [
            (0, 'ae2:1k_crafting_storage'),
            (1, 'ae2:4k_crafting_storage'),
            (2, 'ae2:16k_crafting_storage'),
            (3, 'ae2:64k_crafting_storage'),
            (4, 'ae2:1k_crafting_storage'),
            (7, 'ae2:64k_crafting_storage'),
        ]
        
        for metadata, expected_id in test_cases:
            result = resolve_crafting_storage_variant(
                'appliedenergistics2:tile.BlockCraftingStorage',
                metadata
            )
            self.assertEqual(result, expected_id)

    def test_crafting_unit_accelerator_variant(self):
        """Sprawdza metadata Crafting Unit -> Crafting Accelerator"""
        converter = AE2Converter()
        result = converter.convert_block(
            'BlockCraftingUnit',
            {'core': False},
            metadata=1,
            position=(0, 0, 0)
        )

        self.assertTrue(result.converted.success)
        self.assertEqual(result.converted.block_id_1182, 'ae2:crafting_accelerator')


class TestNBTConverters(unittest.TestCase):
    """Testy konwerterów NBT (snapshot)"""
    
    def test_drive_converter_snapshot(self):
        """Test DriveConverter z NBT snapshot - poprawny format compound inventory"""
        from src.converters.ae2.nbt_converters import DriveConverter
        
        converter = DriveConverter()
        
        # NBT wejściowe 1.7.10 - format compound z item0, item1, ...
        nbt_1710 = {
            'priority': 5,
            'inv': {
                'item0': {'id': 'appliedenergistics2:item.ItemBasicStorageCell.64k', 
                 'Count': 1, 'tag': {'StorageCell': {'items': [], 'itemCount': 0}}},
                'item1': {},  # Pusty slot
            },
            'forward': 2,
            'up': 1
        }
        
        result = converter.convert(nbt_1710)
        
        self.assertTrue(result.success)
        self.assertNotIn('visual', result.converted_nbt)  # Nie ma 'visual'!
        self.assertEqual(result.converted_nbt.get('priority'), 5)
        
        # Sprawdź format inventory - powinien być compound z item0, item1
        inv = result.converted_nbt.get('inv', {})
        self.assertIn('item0', inv)
        self.assertIn('item1', inv)
        
    def test_storage_cell_converter_snapshot(self):
        """Test StorageCellConverter z NBT snapshot"""
        from src.converters.ae2.nbt_converters import StorageCellConverter
        
        converter = StorageCellConverter()
        
        nbt_1710 = {
            'StorageCell': {
                'items': [
                    {'id': 'minecraft:stone', 'Damage': 0, 'Count': 64}
                ],
                'itemCount': 64
            },
            'priority': 0,
            'fuzzyMode': 0
        }
        
        result = converter.convert(nbt_1710)
        
        self.assertTrue(result.success)
        # Sprawdź konwersję struktury
        storage = result.converted_nbt.get('storage', {})
        self.assertIn('items', storage)
        self.assertIn('count', storage)


class TestAE2Converter(unittest.TestCase):
    """Testy glownego konwertera"""
    
    def setUp(self):
        self.converter = AE2Converter()
    
    def test_converter_initialization(self):
        """Sprawdza inicjalizacje konwertera"""
        self.assertIsNotNone(self.converter.id_resolver)
        self.assertIn('drive', self.converter.nbt_converters)
        self.assertIn('interface', self.converter.nbt_converters)
    
    def test_is_ae2_block(self):
        """Sprawdza detekcje blokow AE2"""
        self.assertTrue(
            self.converter.is_ae2_block('appliedenergistics2:tile.BlockController')
        )
        self.assertFalse(
            self.converter.is_ae2_block('minecraft:stone')
        )
    
    def test_convert_controller(self):
        """Test konwersji Controller"""
        result = self.converter.convert_block(
            'BlockController',
            {'forward': 2, 'up': 1},
            position=(0, 0, 0)
        )
        
        self.assertTrue(result.converted.success)
        self.assertEqual(result.converted.block_id_1182, 'ae2:controller')

    def test_convert_crafting_storage_1182_ids(self):
        """Test poprawnych ID wariantow Crafting Storage z AE2 11.7.6"""
        result = self.converter.convert_block(
            'BlockCraftingStorage',
            {'customName': 'CPU storage'},
            metadata=6,
            position=(0, 0, 0)
        )

        self.assertTrue(result.converted.success)
        self.assertEqual(result.converted.block_id_1182, 'ae2:16k_crafting_storage')
        self.assertEqual(result.converted.nbt_1182.get('size_variant'), 2)
        self.assertTrue(result.converted.nbt_1182.get('formed'))
    
    def test_convert_drive(self):
        """Test konwersji Drive"""
        drive_nbt = {
            'priority': 5,
            'inv': [],
            'fuzzyMode': 0,
            'forward': 2,
            'up': 1
        }
        
        result = self.converter.convert_block(
            'appliedenergistics2:tile.BlockDrive',
            drive_nbt,
            position=(100, 64, 100)
        )
        
        self.assertTrue(result.converted.success)
        self.assertEqual(result.converted.block_id_1182, 'ae2:drive')
        self.assertIsNotNone(result.converted.nbt_1182)
        self.assertEqual(result.converted.nbt_1182.get('priority'), 5)
    
    def test_convert_unknown_block(self):
        """Test konwersji nieznanego bloku"""
        result = self.converter.convert_block(
            'unknown:mod.SomeBlock',
            {},
            position=(0, 0, 0)
        )
        
        self.assertFalse(result.converted.success)
        self.assertTrue(len(result.converted.errors) > 0)

    def test_interface_patterns_create_pattern_provider(self):
        """Interface z patternami tworzy dodatkowy Pattern Provider"""
        result = self.converter.convert_block(
            'BlockInterface',
            {
                'patterns': [
                    {
                        'id': 'appliedenergistics2:item.ItemEncodedPattern',
                        'Count': 1,
                        'tag': {
                            'crafting': False,
                            'in': [{'id': 'minecraft:iron_ingot', 'Count': 1}],
                            'out': [{'id': 'minecraft:gold_ingot', 'Count': 1}]
                        }
                    }
                ],
                'forward': 5,
            },
            position=(10, 64, 10)
        )

        self.assertTrue(result.converted.success)
        self.assertEqual(result.converted.block_id_1182, 'ae2:interface')
        self.assertEqual(len(result.converted.additional_blocks), 1)
        provider = result.converted.additional_blocks[0]
        self.assertEqual(provider.converted.block_id_1182, 'ae2:pattern_provider')
        self.assertEqual(provider.original_pos, (11, 64, 10))
        self.assertNotIn('__patterns_for_provider', result.converted.nbt_1182)

    def test_sky_chest_converter_registered(self):
        """SkyChest zachowuje inventory i ma zarejestrowany konwerter"""
        result = self.converter.convert_block(
            'BlockSkyChest',
            {
                'inv': {
                    'item0': {'id': 'minecraft:diamond', 'Count': 3},
                },
            },
            position=(0, 0, 0)
        )

        self.assertTrue(result.converted.success)
        self.assertEqual(result.converted.block_id_1182, 'ae2:sky_stone_chest')
        self.assertIn('inv', result.converted.nbt_1182)

    def test_lossy_fallbacks(self):
        """Crank i Grinder maja jawne fallbacki poza AE2"""
        crank = self.converter.convert_block('BlockCrank', {}, position=(0, 0, 0))
        grinder = self.converter.convert_block('BlockGrinder', {}, position=(0, 0, 0))

        self.assertTrue(crank.converted.success)
        self.assertEqual(crank.converted.block_id_1182, 'minecraft:lever')
        self.assertTrue(any('LOSSY' in warning for warning in crank.converted.warnings))
        self.assertTrue(grinder.converted.success)
        self.assertEqual(grinder.converted.block_id_1182, 'minecraft:grindstone')

    def test_real_map_utility_converters_accept_metadata(self):
        """Realne typy utility z mapy przechodza przez glowny konwerter"""
        cases = {
            'BlockQuantumLinkChamber': 'ae2:quantum_link',
            'BlockSecurity': 'ae2:security_station',
            'BlockWireless': 'ae2:wireless_access_point',
        }

        for block_id, target in cases.items():
            with self.subTest(block_id=block_id):
                result = self.converter.convert_block(
                    block_id,
                    {'id': block_id, 'x': 0, 'y': 64, 'z': 0},
                    metadata=0,
                    position=(0, 64, 0)
                )

                self.assertTrue(result.converted.success)
                self.assertEqual(result.converted.block_id_1182, target)


class TestItemConversion(unittest.TestCase):
    """Testy konwersji itemow"""
    
    def setUp(self):
        self.converter = AE2Converter()
    
    def test_convert_storage_cell(self):
        """Test konwersji Storage Cell"""
        result = self.converter.convert_item(
            'appliedenergistics2:item.ItemBasicStorageCell.64k'
        )
        
        self.assertTrue(result.success)
        self.assertEqual(result.block_id_1182, 'ae2:item_storage_cell_64k')


class TestMetadataFlow(unittest.TestCase):
    """Testy przeplywu metadata do konwerterow"""
    
    def test_metadata_passed_to_converter(self):
        """Sprawdza czy metadata jest przekazywana do konwertera"""
        from src.converters.ae2.nbt_converters import CraftingStorageConverter
        
        converter = CraftingStorageConverter()
        
        # Test dla roznych wartosci metadata
        for metadata in [0, 1, 2, 3]:
            nbt_1710 = {'customName': f'Test{metadata}'}
            result = converter.convert(nbt_1710, metadata=metadata)
            
            self.assertTrue(result.success)
            self.assertEqual(result.converted_nbt.get('size_variant'), metadata)


class TestStrictMode(unittest.TestCase):
    """Testy trybu strict"""
    
    def test_strict_mode_unknown_block(self):
        """Test trybu strict dla nieznanego bloku"""
        converter = AE2Converter()
        
        result = converter.convert_block(
            'unknown:mod.SomeBlock',
            {},
            position=(0, 0, 0),
            strict=True
        )
        
        self.assertFalse(result.converted.success)
        # Sprawdź czy jest kod błędu
        self.assertTrue(any('AE2C-E' in err for err in result.converted.errors))


class TestPatternConverter(unittest.TestCase):
    """Testy konwersji patternów (Iteracja 2)"""
    
    def test_processing_pattern_parsing(self):
        """Test parsowania processing pattern 1.7.10"""
        from src.converters.ae2.nbt_converters import PatternConverter
        
        converter = PatternConverter()
        
        nbt_1710 = {
            'crafting': False,  # Processing
            'in': [
                {'id': 'minecraft:iron_ingot', 'Count': 1, 'Damage': 0},
                {'id': 'minecraft:coal', 'Count': 1, 'Damage': 0}
            ],
            'out': [
                {'id': 'minecraft:steel_ingot', 'Count': 1, 'Damage': 0}
            ],
            'substitute': True
        }
        
        data = converter.convert_pattern(nbt_1710)
        
        self.assertIsNotNone(data)
        self.assertEqual(data.pattern_type, 'processing')
        self.assertEqual(len(data.inputs), 2)
        self.assertEqual(len(data.outputs), 1)
        self.assertTrue(data.can_substitute)
    
    def test_crafting_pattern_parsing(self):
        """Test parsowania crafting pattern 1.7.10"""
        from src.converters.ae2.nbt_converters import PatternConverter
        
        converter = PatternConverter()
        
        nbt_1710 = {
            'crafting': True,  # Crafting
            'in': [
                {'id': 'minecraft:oak_planks', 'Count': 1, 'Damage': 0},
                None,  # Pusty slot
                None,
                {'id': 'minecraft:oak_planks', 'Count': 1, 'Damage': 0},
            ],
            'out': [
                {'id': 'minecraft:crafting_table', 'Count': 1, 'Damage': 0}
            ],
            'substitute': False
        }
        
        data = converter.convert_pattern(nbt_1710)
        
        self.assertIsNotNone(data)
        self.assertEqual(data.pattern_type, 'crafting')
        self.assertEqual(len(data.inputs), 2)  # Tylko niepuste
        self.assertEqual(len(data.outputs), 1)
    
    def test_processing_pattern_conversion(self):
        """Test konwersji processing pattern do 1.18.2"""
        from src.converters.ae2.nbt_converters import PatternConverter
        
        converter = PatternConverter()
        
        data = PatternData(
            pattern_type='processing',
            inputs=[
                {'id': 'minecraft:iron_ingot', 'Count': 1},
                {'id': 'minecraft:coal', 'Count': 1}
            ],
            outputs=[
                {'id': 'minecraft:steel_ingot', 'Count': 1}
            ],
            can_substitute=False
        )
        
        item_id, component = converter.convert_to_1182(data)
        
        self.assertEqual(item_id, 'ae2:processing_pattern')
        self.assertIn('inputs', component)
        self.assertIn('outputs', component)
        self.assertEqual(len(component['inputs']), 2)
        self.assertEqual(len(component['outputs']), 1)
    
    def test_crafting_pattern_without_recipe_resolver(self):
        """Test ze crafting pattern bez recipe resolver - powinien dac ostrzezenie"""
        from src.converters.ae2.nbt_converters import PatternConverter
        
        converter = PatternConverter()
        
        data = PatternData(
            pattern_type='crafting',
            inputs=[{'id': 'minecraft:oak_planks', 'Count': 4}],
            outputs=[{'id': 'minecraft:crafting_table', 'Count': 1}],
            can_substitute=False
        )
        
        item_id, component = converter.convert_to_1182(data)
        
        self.assertEqual(item_id, 'ae2:crafting_pattern')
        # Bez resolvera, recipeId bedzie 'minecraft:unknown'
        self.assertEqual(component['recipeId'], 'minecraft:unknown')
        # I powinno byc ostrzezenie
        self.assertTrue(len(converter.warnings) > 0)


def run_tests():
    """Uruchamia testy"""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Dodaj wszystkie testy
    suite.addTests(loader.loadTestsFromTestCase(TestBlockMappings))
    suite.addTests(loader.loadTestsFromTestCase(TestCraftingStorageVariants))
    suite.addTests(loader.loadTestsFromTestCase(TestNBTConverters))
    suite.addTests(loader.loadTestsFromTestCase(TestAE2Converter))
    suite.addTests(loader.loadTestsFromTestCase(TestItemConversion))
    suite.addTests(loader.loadTestsFromTestCase(TestMetadataFlow))
    suite.addTests(loader.loadTestsFromTestCase(TestStrictMode))
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return result.wasSuccessful()


if __name__ == '__main__':
    success = run_tests()
    exit(0 if success else 1)
