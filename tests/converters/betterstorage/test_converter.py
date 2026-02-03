"""
Testy dla konwertera Better Storage

Testują:
- Konwersję Reinforced Chest
- Konwersję Locker
- Konwersję Crate Pile
- Konwersję Cardboard Box
- Konwersję Crafting Station
- Konwersję Armor Stand
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..'))

import unittest
from src.converters.betterstorage import (
    BetterStorageConverter,
    CratePileData,
    CratePileRegion,
    CratePileLoader,
    BLOCK_MAPPING,
    ITEM_MAPPING,
)


class TestReinforcedChestConversion(unittest.TestCase):
    """Testy konwersji Reinforced Chest"""
    
    def setUp(self):
        self.converter = BetterStorageConverter()
    
    def test_iron_material_cosmetic(self):
        """Materiał iron jest tylko kosmetyczny"""
        nbt = {
            'Items': [],
            'Material': 'iron',
            'orientation': 2
        }
        
        result = self.converter.convert_tile_entity(
            'betterstorage:reinforcedChest', nbt
        )
        
        # Powinien być Iron Chest (54 sloty) dla 39 slotów BS
        self.assertEqual(result['block_id'], 'ironchest:iron_chest')
        # Iron to poprawny materiał - nie powinno być ostrzeżenia
        # (w przeciwieństwie do emerald/silver/tin/zinc/steel)
    
    def test_emerald_material_warning(self):
        """Materiał emerald daje ostrzeżenie (brak w Iron Chests)"""
        nbt = {
            'Items': [],
            'Material': 'emerald',
            'orientation': 2
        }
        
        result = self.converter.convert_tile_entity(
            'betterstorage:reinforcedChest', nbt
        )
        
        # Powinno być ostrzeżenie o braku emerald w Iron Chests
        warning_text = ' '.join(result['warnings']).lower()
        self.assertIn('emerald', warning_text)
    
    def test_capacity_mapping_27_slots(self):
        """27 slotów BS → Copper Chest"""
        # To wymaga symulacji configu z 9 kolumnami
        # W prawdziwym teście trzeba by mockować config
        pass
    
    def test_items_conversion(self):
        """Konwersja itemów w skrzyni"""
        nbt = {
            'Items': [
                {'Slot': 0, 'id': 'minecraft:stone', 'Count': 64, 'Damage': 0},
                {'Slot': 1, 'id': 'minecraft:diamond', 'Count': 16, 'Damage': 0}
            ],
            'Material': 'iron'
        }
        
        result = self.converter.convert_tile_entity(
            'betterstorage:reinforcedChest', nbt
        )
        
        items = result['nbt']['Items']
        self.assertEqual(len(items), 2)
        self.assertEqual(items[0]['id'], 'minecraft:stone')
        self.assertEqual(items[0]['Count'], 64)
    
    def test_orientation_conversion(self):
        """Konwersja orientacji"""
        # 2 = north w BS
        nbt = {'Items': [], 'orientation': 2}
        
        result = self.converter.convert_tile_entity(
            'betterstorage:reinforcedChest', nbt
        )
        
        self.assertEqual(result['nbt']['facing'], 'north')


class TestLockerConversion(unittest.TestCase):
    """Testy konwersji Locker"""
    
    def setUp(self):
        self.converter = BetterStorageConverter()
    
    def test_locker_to_barrel(self):
        """Mały locker → Barrel"""
        nbt = {
            'Items': [{'Slot': 0, 'id': 'minecraft:stone', 'Count': 1}],
            'orientation': 2
        }
        
        result = self.converter.convert_tile_entity(
            'betterstorage:locker', nbt
        )
        
        self.assertEqual(result['block_id'], 'minecraft:barrel')
    
    def test_full_locker_to_iron_chest(self):
        """Pełny locker (>27 slotów) → Iron Chest"""
        items = [{'Slot': i, 'id': 'minecraft:stone', 'Count': 64} for i in range(30)]
        nbt = {'Items': items, 'orientation': 2}
        
        result = self.converter.convert_tile_entity(
            'betterstorage:locker', nbt
        )
        
        self.assertEqual(result['block_id'], 'ironchest:iron_chest')
    
    def test_mirror_warning(self):
        """Mirror daje ostrzeżenie"""
        nbt = {'Items': [], 'mirror': True}
        
        result = self.converter.convert_tile_entity(
            'betterstorage:locker', nbt
        )
        
        warning_text = ' '.join(result['warnings']).lower()
        self.assertIn('mirror', warning_text)


class TestCratePileSimulation(unittest.TestCase):
    """Testy symulacji Crate Pile"""
    
    def test_crate_pile_data_creation(self):
        """Tworzenie CratePileData"""
        pile = CratePileData(
            pile_id=0,
            items=[{'Slot': 0, 'id': 'minecraft:stone'}],
            num_crates=2,
            region=CratePileRegion(0, 64, 0, 1, 64, 0)
        )
        
        self.assertEqual(pile.pile_id, 0)
        self.assertEqual(pile.num_crates, 2)
    
    def test_get_items_for_crate(self):
        """Rozdział itemów dla konkretnego crate'a"""
        pile = CratePileData(
            pile_id=0,
            items=[
                {'Slot': 0, 'id': 'minecraft:stone'},   # Crate 0
                {'Slot': 18, 'id': 'minecraft:dirt'},   # Crate 1
                {'Slot': 19, 'id': 'minecraft:wood'}    # Crate 1
            ],
            num_crates=2
        )
        
        # Crate 0 powinien mieć tylko slot 0
        items_0 = pile.get_items_for_crate(0)
        self.assertEqual(len(items_0), 1)
        self.assertEqual(items_0[0]['id'], 'minecraft:stone')
        
        # Crate 1 powinien mieć sloty 0 i 1 (przesunięte z 18, 19)
        items_1 = pile.get_items_for_crate(1)
        self.assertEqual(len(items_1), 2)
        self.assertEqual(items_1[0]['Slot'], 0)  # Przesunięty z 18
        self.assertEqual(items_1[1]['Slot'], 1)  # Przesunięty z 19
    
    def test_crate_pile_region_volume(self):
        """Obliczanie objętości regionu"""
        region = CratePileRegion(0, 64, 0, 2, 66, 2)
        # 3x3x3 = 27 bloków
        self.assertEqual(region.volume, 27)
        
        region2 = CratePileRegion(0, 64, 0, 1, 64, 0)
        # 2x1x1 = 2 bloki
        self.assertEqual(region2.volume, 2)


class TestCardboardBoxConversion(unittest.TestCase):
    """Testy konwersji Cardboard Box"""
    
    def setUp(self):
        self.converter = BetterStorageConverter()
    
    def test_used_box_to_packing_tape(self):
        """Używane pudełko → Packing Tape"""
        nbt = {
            'Items': [{'Slot': 0, 'id': 'minecraft:stone', 'Count': 32}],
            'uses': 5,
            'color': 14  # Red
        }
        
        result = self.converter.convert_tile_entity(
            'betterstorage:cardboardBox', nbt
        )
        
        self.assertEqual(result['block_id'], 'packingtape:packed')
        self.assertIn('packed', result['nbt'])
    
    def test_depleted_box_to_chest(self):
        """Zużyte pudełko (uses=0) → Chest z wypakowaniem"""
        nbt = {
            'Items': [{'Slot': 0, 'id': 'minecraft:stone', 'Count': 32}],
            'uses': 0
        }
        
        result = self.converter.convert_tile_entity(
            'betterstorage:cardboardBox', nbt
        )
        
        self.assertEqual(result['block_id'], 'minecraft:chest')
    
    def test_color_conversion(self):
        """Konwersja koloru int → dye color"""
        nbt = {
            'Items': [],
            'uses': 5,
            'color': 11  # Blue
        }
        
        result = self.converter.convert_tile_entity(
            'betterstorage:cardboardBox', nbt
        )
        
        self.assertEqual(result['nbt']['color'], 'blue')


class TestArmorStandConversion(unittest.TestCase):
    """Testy konwersji Armor Stand"""
    
    def setUp(self):
        self.converter = BetterStorageConverter()
    
    def test_armor_stand_to_vanilla(self):
        """Armor Stand → Vanilla Armor Stand z overflow"""
        nbt = {
            'Items': [
                {'Slot': 0, 'id': 'minecraft:iron_helmet', 'Count': 1},
                {'Slot': 1, 'id': 'minecraft:iron_chestplate', 'Count': 1}
            ]
        }
        
        result = self.converter.convert_tile_entity(
            'betterstorage:armorStand', nbt
        )
        
        # Vanilla armor stand
        self.assertEqual(result['block_id'], 'minecraft:armor_stand')
        # Itemy w overflow (vanilla nie ma Items w BE)
        self.assertEqual(len(result['overflow']), 2)


class TestEnderBackpackConversion(unittest.TestCase):
    """Testy konwersji Ender Backpack"""
    
    def setUp(self):
        self.converter = BetterStorageConverter()
    
    def test_ender_backpack_to_vanilla(self):
        """Ender Backpack → Vanilla Ender Chest"""
        nbt = {}  # Ender Backpack nie ma własnych danych
        
        result = self.converter.convert_tile_entity(
            'betterstorage:enderBackpack', nbt
        )
        
        self.assertEqual(result['block_id'], 'minecraft:ender_chest')
        # Vanilla ender chest nie ma danych w BlockEntity
        self.assertEqual(result['nbt'], {})


class TestCraftingStationConversion(unittest.TestCase):
    """Testy konwersji Crafting Station"""
    
    def setUp(self):
        self.converter = BetterStorageConverter()
    
    def test_crafting_station_items(self):
        """Konwersja itemów Crafting Station"""
        # 10 slotów: 0-8 crafting grid, 9 wynik
        nbt = {
            'Items': [
                {'Slot': 0, 'id': 'minecraft:stick', 'Count': 1},
                {'Slot': 1, 'id': 'minecraft:stick', 'Count': 1},
                {'Slot': 9, 'id': 'minecraft:wooden_sword', 'Count': 1}
            ]
        }
        
        result = self.converter.convert_tile_entity(
            'betterstorage:craftingStation', nbt
        )
        
        self.assertEqual(result['block_id'], 'craftingstation:crafting_station')
        self.assertEqual(len(result['nbt']['Items']), 3)


class TestItemConversion(unittest.TestCase):
    """Testy konwersji itemów"""
    
    def setUp(self):
        self.converter = BetterStorageConverter()
    
    def test_damage_in_tag(self):
        """Damage przenoszone do tagu"""
        item = {'id': 'minecraft:stone', 'Count': 1, 'Slot': 0, 'Damage': 5}
        
        converted = self.converter._convert_item(item)
        
        # Damage nie powinno być na głównym poziomie
        self.assertNotIn('Damage', converted)
        # Tylko w tagu
        self.assertEqual(converted['tag']['Damage'], 5)
    
    def test_zero_damage_ignored(self):
        """Damage=0 jest ignorowane"""
        item = {'id': 'minecraft:stone', 'Count': 1, 'Slot': 0, 'Damage': 0}
        
        converted = self.converter._convert_item(item)
        
        # Bez tagu dla Damage=0
        self.assertNotIn('tag', converted)
    
    def test_bs_enchants_removed(self):
        """Enchanty BS (170-176) są usuwane"""
        item = {
            'id': 'minecraft:iron_sword',
            'Count': 1,
            'Slot': 0,
            'tag': {
                'ench': [
                    {'id': 170, 'lvl': 3},  # BS enchant - usunąć
                    {'id': 16, 'lvl': 5}     # Sharpness - zostawić
                ]
            }
        }
        
        converted = self.converter._convert_item(item)
        
        # Tylko Sharpness powinien zostać
        enchants = converted['tag'].get('Enchantments', [])
        self.assertEqual(len(enchants), 1)
        self.assertEqual(enchants[0]['id'], 16)


class TestMappings(unittest.TestCase):
    """Testy poprawności mapowań"""
    
    def test_reinforced_chest_mapping(self):
        """Reinforced Chest mapuje na Iron Chests"""
        target, params = BLOCK_MAPPING['betterstorage:reinforcedChest']
        
        self.assertIn('ironchest', target)
        self.assertTrue(params['material_is_cosmetic'])
    
    def test_crate_mapping(self):
        """Crate mapuje na Chest (nie Drawers!)"""
        target, params = BLOCK_MAPPING['betterstorage:crate']
        
        self.assertEqual(target, 'minecraft:chest')
        self.assertTrue(params['use_crate_pile_loader'])
    
    def test_emerald_material_warning(self):
        """Materiał emerald ma ostrzeżenie"""
        from src.converters.betterstorage.mapping import get_material_info
        
        info = get_material_info('emerald')
        
        self.assertIn('warning', info)
        self.assertIn('emerald', info['warning'].lower())


def run_tests():
    """Uruchamia wszystkie testy"""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Dodajemy wszystkie testy
    suite.addTests(loader.loadTestsFromTestCase(TestReinforcedChestConversion))
    suite.addTests(loader.loadTestsFromTestCase(TestLockerConversion))
    suite.addTests(loader.loadTestsFromTestCase(TestCratePileSimulation))
    suite.addTests(loader.loadTestsFromTestCase(TestCardboardBoxConversion))
    suite.addTests(loader.loadTestsFromTestCase(TestArmorStandConversion))
    suite.addTests(loader.loadTestsFromTestCase(TestEnderBackpackConversion))
    suite.addTests(loader.loadTestsFromTestCase(TestCraftingStationConversion))
    suite.addTests(loader.loadTestsFromTestCase(TestItemConversion))
    suite.addTests(loader.loadTestsFromTestCase(TestMappings))
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return result.wasSuccessful()


if __name__ == '__main__':
    success = run_tests()
    sys.exit(0 if success else 1)
