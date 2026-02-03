"""
Testy integracyjne dla konwertera Better Storage.

Testuje konwersję z prawdziwymi plikami z mapy 1.7.10.
"""

import os
import sys
import unittest
from pathlib import Path

# Dodaj src do path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / 'src'))

from converters.betterstorage import BetterStorageConverter
from converters.betterstorage.crate_pile_simulation import CratePileLoader
from converters.betterstorage.nbt_parser import parse_nbt_file


class TestCratePileWithRealFiles(unittest.TestCase):
    """Testy Crate Pile z prawdziwymi plikami z mapy"""
    
    @classmethod
    def setUpClass(cls):
        """Ustawia ścieżkę do mapy"""
        cls.world_path = Path(__file__).parent.parent.parent.parent / 'mapa_1710'
        cls.crates_dir = cls.world_path / 'data' / 'crates'
        
    def test_real_crate_files_exist(self):
        """Sprawdza czy pliki crates istnieją"""
        self.assertTrue(self.crates_dir.exists(), f"Folder crates nie istnieje: {self.crates_dir}")
        
        files = list(self.crates_dir.glob('*.dat'))
        self.assertGreater(len(files), 0, "Brak plików .dat w folderze crates")
        print(f"\nZnaleziono {len(files)} plików Crate Pile")
        
    def test_parse_real_crate_files(self):
        """Parsuje prawdziwe pliki crates"""
        files = list(self.crates_dir.glob('*.dat'))
        
        parsed_count = 0
        for file_path in files:
            with self.subTest(file=file_path.name):
                data = parse_nbt_file(str(file_path))
                self.assertIsNotNone(data, f"Nie udało się sparsować {file_path.name}")
                
                # Sprawdzamy strukturę - w prawdziwych plikach jest 'data' -> 'stacks'
                # Struktura: {'data': {'stacks': [...], 'numCrates': N, ...}}
                self.assertIn('data', data, f"Brak 'data' w {file_path.name}")
                inner_data = data['data']
                self.assertIn('stacks', inner_data, f"Brak 'stacks' w {file_path.name}")
                self.assertIn('numCrates', inner_data, f"Brak 'numCrates' w {file_path.name}")
                
                parsed_count += 1
                inner_data = data['data']
                print(f"  {file_path.name}: {inner_data['numCrates']} crates, {len(inner_data['stacks'])} stacks")
        
        self.assertEqual(parsed_count, len(files), "Nie wszystkie pliki zostały sparsowane")
        
    def test_crate_pile_loader_with_real_files(self):
        """Testuje CratePileLoader z prawdziwymi plikami"""
        loader = CratePileLoader(str(self.world_path))
        
        # Ładujemy wszystkie pile
        piles = loader.load_all_piles()
        
        self.assertGreater(len(piles), 0, "Nie udało się załadować żadnych pile")
        print(f"\nZaładowano {len(piles)} Crate Pile")
        
        for pile_id, pile_data in piles.items():
            with self.subTest(pile_id=pile_id):
                self.assertIsNotNone(pile_data)
                self.assertEqual(pile_data.pile_id, pile_id)
                self.assertGreaterEqual(pile_data.num_crates, 0)
                self.assertIsInstance(pile_data.items, list)


class TestBetterStorageConverterIntegration(unittest.TestCase):
    """Testy integracyjne pełnego konwertera"""
    
    @classmethod
    def setUpClass(cls):
        """Inicjalizuje konwerter z prawdziwą ścieżką"""
        cls.world_path = Path(__file__).parent.parent.parent.parent / 'mapa_1710'
        cls.converter = BetterStorageConverter(str(cls.world_path))
        
    def test_converter_initialization(self):
        """Testuje inicjalizację konwertera"""
        self.assertIsNotNone(self.converter)
        self.assertIsNotNone(self.converter.crate_loader)
        self.assertIsNotNone(self.converter.crate_converter)
        
    def test_convert_reinforced_chest(self):
        """Testuje konwersję Reinforced Chest"""
        nbt_data = {
            'Items': [
                {'id': 'minecraft:diamond', 'Count': 10, 'Slot': 0},
                {'id': 'minecraft:iron_ingot', 'Count': 32, 'Slot': 1},
            ],
            'Material': 'gold',
            'orientation': 2,
            'CustomName': 'My Chest'
        }
        
        result = self.converter.convert_tile_entity(
            'betterstorage:reinforcedChest',
            nbt_data,
            x=100, y=64, z=200
        )
        
        self.assertIn('block_id', result)
        # Konwersja Crate Pile zwraca 'target_block' zamiast 'block_id'
        if 'target_block' in result:
            result['block_id'] = result['target_block']
        self.assertIn('nbt', result)
        self.assertIn('warnings', result)
        
        # Powinien być Iron Chest
        self.assertTrue(
            result['block_id'].startswith('ironchest:'),
            f"Oczekiwano ironchest:, otrzymano {result['block_id']}"
        )
        
        # Sprawdzamy czy itemy są
        self.assertIn('Items', result['nbt'])
        self.assertEqual(len(result['nbt']['Items']), 2)
        
    def test_convert_locker(self):
        """Testuje konwersję Locker"""
        nbt_data = {
            'Items': [{'id': 'minecraft:stone', 'Count': 64, 'Slot': 0}],
            'orientation': 3,
            'mirror': False
        }
        
        result = self.converter.convert_tile_entity(
            'betterstorage:locker',
            nbt_data,
            x=100, y=64, z=200
        )
        
        # Locker → Barrel lub Iron Chest
        self.assertIn(result['block_id'], ['minecraft:barrel', 'ironchest:iron_chest'])
        
    def test_convert_crate_with_real_data(self):
        """Testuje konwersję Crate z prawdziwymi danymi z mapy"""
        # Najpierw ładujemy wszystkie pile
        self.converter.crate_loader.load_all_piles()
        
        # Testujemy z mockowym crateId (może nie być w mapie)
        # W rzeczywistej konwersji użylibyśmy prawdziwego crateId z chunka
        nbt_data = {'crateId': 9416}  # Istniejący crate w mapie
        
        # Rejestrujemy lokalizację
        self.converter.crate_loader.register_crate_location(100, 64, 200, 9416)
        
        result = self.converter.convert_tile_entity(
            'betterstorage:crate',
            nbt_data,
            x=100, y=64, z=200
        )
        
        self.assertIn('block_id', result)
        self.assertIn('nbt', result)
        
        # Powinien być minecraft:chest lub ironchest:iron_chest
        self.assertTrue(
            result['block_id'] in ['minecraft:chest', 'ironchest:iron_chest'],
            f"Nieoczekiwany block_id: {result['block_id']}"
        )
        
    def test_convert_ender_backpack(self):
        """Testuje konwersję Ender Backpack"""
        result = self.converter.convert_tile_entity(
            'betterstorage:enderBackpack',
            {},
            x=100, y=64, z=200
        )
        
        self.assertEqual(result['block_id'], 'minecraft:ender_chest')
        
    def test_convert_armor_stand(self):
        """Testuje konwersję Armor Stand (z overflow)"""
        nbt_data = {
            'Items': [
                {'id': 'minecraft:diamond_helmet', 'Count': 1, 'Slot': 0},
                {'id': 'minecraft:diamond_chestplate', 'Count': 1, 'Slot': 1},
                {'id': 'minecraft:diamond_leggings', 'Count': 1, 'Slot': 2},
                {'id': 'minecraft:diamond_boots', 'Count': 1, 'Slot': 3},
            ]
        }
        
        result = self.converter.convert_tile_entity(
            'betterstorage:armorStand',
            nbt_data,
            x=100, y=64, z=200
        )
        
        self.assertEqual(result['block_id'], 'minecraft:armor_stand')
        # Zawartość powinna być w overflow
        self.assertIn('overflow', result)
        self.assertEqual(len(result['overflow']), 4)


class TestCraftingStationNBT(unittest.TestCase):
    """Testy weryfikujące format NBT Crafting Station"""
    
    def test_crafting_station_nbt_structure(self):
        """Sprawdza strukturę NBT Crafting Station z 1.7.10"""
        # Przykładowe dane jakie mogą wystąpić
        nbt_1710 = {
            'Items': [
                {'id': 'minecraft:planks', 'Count': 1, 'Slot': 0},
                {'id': 'minecraft:stick', 'Count': 1, 'Slot': 4},
                # ...inne sloty crafting grid
                {'id': 'minecraft:wooden_pickaxe', 'Count': 1, 'Slot': 9},  # Wynik
            ]
        }
        
        # Format 1.18.2 powinien być podobny
        # Ale musimy zweryfikować w rzeczywistym teście
        self.assertEqual(len(nbt_1710['Items']), 3)  # 3 itemy w przykładzie
        
        # Sprawdzamy czy Slot 9 to wynik
        result_slot = [i for i in nbt_1710['Items'] if i.get('Slot') == 9]
        self.assertEqual(len(result_slot), 1)


class TestItemConversion(unittest.TestCase):
    """Testy konwersji itemów"""
    
    @classmethod
    def setUpClass(cls):
        cls.world_path = Path(__file__).parent.parent.parent.parent / 'mapa_1710'
        cls.converter = BetterStorageConverter(str(cls.world_path))
    
    def test_convert_item_with_damage(self):
        """Testuje konwersję itemu z obrażeniami"""
        item = {
            'id': 'minecraft:diamond_pickaxe',
            'Count': 1,
            'Slot': 0,
            'Damage': 50  # Uszkodzenie w 1.7.10
        }
        
        # Wywołujemy prywatną metodę przez konwerter
        result = self.converter._convert_item(item)
        
        self.assertEqual(result['id'], 'minecraft:diamond_pickaxe')
        self.assertEqual(result['Count'], 1)
        self.assertEqual(result['Slot'], 0)
        
        # Damage powinien być w tagu
        self.assertIn('tag', result)
        self.assertEqual(result['tag']['Damage'], 50)
        
    def test_convert_item_with_tags(self):
        """Testuje konwersję itemu z tagami"""
        item = {
            'id': 'minecraft:diamond_sword',
            'Count': 1,
            'Slot': 5,
            'tag': {
                'display': {'Name': 'My Sword'},
                'ench': [{'id': 16, 'lvl': 5}]  # Sharpness
            }
        }
        
        result = self.converter._convert_item(item)
        
        self.assertIn('tag', result)
        self.assertEqual(result['tag']['display']['Name'], 'My Sword')


class TestEdgeCases(unittest.TestCase):
    """Testy przypadków brzegowych"""
    
    @classmethod
    def setUpClass(cls):
        cls.world_path = Path(__file__).parent.parent.parent.parent / 'mapa_1710'
        cls.converter = BetterStorageConverter(str(cls.world_path))
    
    def test_unknown_block(self):
        """Testuje obsługę nieznanego bloku"""
        result = self.converter.convert_tile_entity(
            'betterstorage:unknownBlock',
            {'Items': []},
            x=0, y=0, z=0
        )
        
        # Powinien zwrócić generic chest
        self.assertEqual(result['block_id'], 'minecraft:chest')
        self.assertTrue(any('Nieznany blok' in w for w in result['warnings']))
        
    def test_empty_reinforced_chest(self):
        """Testuje pustą skrzynię"""
        result = self.converter.convert_tile_entity(
            'betterstorage:reinforcedChest',
            {'Items': [], 'Material': 'iron'},
            x=0, y=0, z=0
        )
        
        self.assertEqual(len(result['nbt'].get('Items', [])), 0)
        
    def test_crate_without_world_path(self):
        """Testuje Crate bez ścieżki do świata"""
        converter = BetterStorageConverter(world_path=None)
        
        result = converter.convert_tile_entity(
            'betterstorage:crate',
            {'crateId': 123},
            x=0, y=0, z=0
        )
        
        # Powinien zwrócić pustą skrzynię z ostrzeżeniem
        self.assertEqual(result['block_id'], 'minecraft:chest')
        self.assertTrue(any('Brak CratePileLoader' in w for w in result['warnings']))


def run_tests():
    """Uruchamia wszystkie testy integracyjne"""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Dodajemy wszystkie testy
    suite.addTests(loader.loadTestsFromTestCase(TestCratePileWithRealFiles))
    suite.addTests(loader.loadTestsFromTestCase(TestBetterStorageConverterIntegration))
    suite.addTests(loader.loadTestsFromTestCase(TestCraftingStationNBT))
    suite.addTests(loader.loadTestsFromTestCase(TestItemConversion))
    suite.addTests(loader.loadTestsFromTestCase(TestEdgeCases))
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return result.wasSuccessful()


if __name__ == '__main__':
    success = run_tests()
    sys.exit(0 if success else 1)
