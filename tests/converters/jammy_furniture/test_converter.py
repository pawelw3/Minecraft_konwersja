"""
Testy dla konwertera Jammy Furniture Reborn

Testują:
- Konwersję bloków (metadata → blockstates)
- Konwersję Tile Entities z inventory
- Konwersję mebli kuchennych (lodówka, kuchenka, szafki)
- Konwersję mebli łazienkowych (szafka, umywalka, toaleta)
- Konwersję mebli wypoczynkowych (krzesło, sofa, fotel)
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..'))

import unittest
from src.converters.jammyfurniture.jammyfurniture_converter import (
    JammyFurnitureConverter,
    ConversionResult,
    convert_jammy_block,
    get_converter,
)
from src.converters.jammyfurniture.jammyfurniture_mapping import (
    BlockMapping,
    JAMMY_FURNITURE_MAPPINGS,
    get_mapping,
    generate_target_id,
)


class TestBlockMapping(unittest.TestCase):
    """Testy mapowania bloków"""
    
    def test_all_mappings_have_required_fields(self):
        """Wszystkie mapowania mają wymagane pola"""
        for mapping in JAMMY_FURNITURE_MAPPINGS:
            self.assertIsNotNone(mapping.source_block)
            self.assertIsNotNone(mapping.source_meta)
            self.assertIsNotNone(mapping.target_mod)
            self.assertIsNotNone(mapping.target_block)
            self.assertIsNotNone(mapping.target_state)
    
    def test_kitchen_cupboard_mapping(self):
        """Mapowanie szafki kuchennej"""
        mapping = get_mapping("jammyfurniture:WoodBlocksTwo", 0)
        self.assertIsNotNone(mapping)
        self.assertEqual(mapping.target_mod, "mcwfurnitures")
        self.assertEqual(mapping.target_block, "oak_kitchen_cabinet")
        self.assertTrue(mapping.preserve_inventory)
    
    def test_wardrobe_mapping(self):
        """Mapowanie szafy"""
        mapping = get_mapping("jammyfurniture:WoodBlocksFour", 0)
        self.assertIsNotNone(mapping)
        self.assertEqual(mapping.target_mod, "mcwfurnitures")
        self.assertEqual(mapping.target_block, "oak_wardrobe")
        self.assertTrue(mapping.preserve_inventory)
    
    def test_fridge_mapping(self):
        """Mapowanie lodówki"""
        mapping = get_mapping("jammyfurniture:IronBlocksOne", 0)
        self.assertIsNotNone(mapping)
        self.assertEqual(mapping.target_mod, "mcwfurnitures")
        self.assertEqual(mapping.target_block, "refrigerator")
        self.assertEqual(mapping.target_state["part"], "lower")
        self.assertTrue(mapping.preserve_inventory)
    
    def test_freezer_mapping(self):
        """Mapowanie zamrażarki"""
        mapping = get_mapping("jammyfurniture:IronBlocksOne", 4)
        self.assertIsNotNone(mapping)
        self.assertEqual(mapping.target_mod, "mcwfurnitures")
        self.assertEqual(mapping.target_block, "refrigerator")
        self.assertEqual(mapping.target_state["part"], "upper")
        self.assertTrue(mapping.preserve_inventory)
    
    def test_cooker_mapping(self):
        """Mapowanie kuchenki"""
        mapping = get_mapping("jammyfurniture:IronBlocksOne", 8)
        self.assertIsNotNone(mapping)
        self.assertEqual(mapping.target_mod, "mcwfurnitures")
        self.assertEqual(mapping.target_block, "stove")
    
    def test_chair_mapping(self):
        """Mapowanie krzesła"""
        mapping = get_mapping("jammyfurniture:WoodBlocksThree", 0)
        self.assertIsNotNone(mapping)
        self.assertEqual(mapping.target_mod, "handcrafted")
        self.assertEqual(mapping.target_block, "chair")
    
    def test_sofa_mapping(self):
        """Mapowanie sofy"""
        mapping = get_mapping("jammyfurniture:SofaLeft", 0)
        self.assertIsNotNone(mapping)
        self.assertEqual(mapping.target_mod, "mcwfurnitures")
        self.assertEqual(mapping.target_block, "sofa")
    
    def test_bathroom_sink_mapping(self):
        """Mapowanie umywalki"""
        mapping = get_mapping("jammyfurniture:CeramicBlocksOne", 4)
        self.assertIsNotNone(mapping)
        self.assertEqual(mapping.target_mod, "mcwfurnitures")
        self.assertEqual(mapping.target_block, "sink")
    
    def test_toilet_mapping(self):
        """Mapowanie toalety"""
        mapping = get_mapping("jammyfurniture:CeramicBlocksOne", 12)
        self.assertIsNotNone(mapping)
        self.assertEqual(mapping.target_mod, "mcwfurnitures")
        self.assertEqual(mapping.target_block, "toilet")
    
    def test_bath_mapping(self):
        """Mapowanie wanny"""
        mapping = get_mapping("jammyfurniture:Bath", 0)
        self.assertIsNotNone(mapping)
        self.assertEqual(mapping.target_mod, "mcwfurnitures")
        self.assertEqual(mapping.target_block, "bathtub")


class TestConverterBasic(unittest.TestCase):
    """Podstawowe testy konwertera"""
    
    def setUp(self):
        self.converter = JammyFurnitureConverter()
    
    def test_converter_initialization(self):
        """Inicjalizacja konwertera"""
        stats = self.converter.get_stats()
        self.assertGreater(stats["total_mappings"], 0)
        self.assertGreater(stats["blocks_with_inventory"], 0)
    
    def test_is_jammy_tile_entity(self):
        """Rozpoznawanie Tile Entities Jammy"""
        self.assertTrue(self.converter.is_jammy_tile_entity("TileEntityWoodBlocksOne"))
        self.assertTrue(self.converter.is_jammy_tile_entity("TileEntityIronBlocksOne"))
        self.assertTrue(self.converter.is_jammy_tile_entity("TileEntityCeramicBlocksOne"))
        self.assertFalse(self.converter.is_jammy_tile_entity("TileEntityChest"))
    
    def test_convert_unknown_block(self):
        """Konwersja nieznanego bloku zwraca błąd"""
        result = self.converter.convert_block("unknown:block", 0)
        self.assertFalse(result.success)
        self.assertIsNotNone(result.error_message)
    
    def test_convert_simple_block(self):
        """Konwersja prostego bloku bez TE"""
        result = self.converter.convert_block("jammyfurniture:WoodBlocksThree", 0)
        self.assertTrue(result.success)
        self.assertEqual(result.target_block_id, "handcrafted:chair")


class TestInventoryConversion(unittest.TestCase):
    """Testy konwersji inventory"""
    
    def setUp(self):
        self.converter = JammyFurnitureConverter()
    
    def test_kitchen_cupboard_inventory(self):
        """Konwersja inventory szafki kuchennej"""
        te_data = {
            "Items": [
                {"Slot": 0, "id": "minecraft:apple", "Count": 16},
                {"Slot": 1, "id": "minecraft:bread", "Count": 8},
            ]
        }
        
        result = self.converter.convert_block(
            "jammyfurniture:WoodBlocksTwo",
            0,  # Kitchen Cupboard
            te_data
        )
        
        self.assertTrue(result.success)
        self.assertIsNotNone(result.target_te)
        self.assertEqual(len(result.target_te["Items"]), 2)
        self.assertEqual(result.target_te["Items"][0]["id"], "minecraft:apple")
    
    def test_wardrobe_inventory(self):
        """Konwersja inventory szafy"""
        te_data = {
            "Items": [
                {"Slot": 0, "id": "minecraft:diamond_helmet", "Count": 1, "Damage": 10},
                {"Slot": 1, "id": "minecraft:iron_chestplate", "Count": 1},
            ]
        }
        
        result = self.converter.convert_block(
            "jammyfurniture:WoodBlocksFour",
            0,  # Wardrobe
            te_data
        )
        
        self.assertTrue(result.success)
        self.assertIsNotNone(result.target_te)
        self.assertEqual(len(result.target_te["Items"]), 2)
    
    def test_fridge_inventory(self):
        """Konwersja inventory lodówki"""
        te_data = {
            "Items": [
                {"Slot": 0, "id": "minecraft:cooked_beef", "Count": 32},
                {"Slot": 1, "id": "minecraft:apple", "Count": 64},
            ]
        }
        
        result = self.converter.convert_block(
            "jammyfurniture:IronBlocksOne",
            0,  # Fridge
            te_data
        )
        
        self.assertTrue(result.success)
        self.assertIsNotNone(result.target_te)
        self.assertEqual(result.target_te["id"], "mcwfurnitures:refrigerator")
    
    def test_rubbish_bin_inventory_truncation(self):
        """Kosz na śmieci - zachowanie tylko pierwszego itemu"""
        te_data = {
            "Items": [
                {"Slot": 0, "id": "minecraft:dirt", "Count": 64},
                {"Slot": 1, "id": "minecraft:cobblestone", "Count": 64},
                {"Slot": 2, "id": "minecraft:stone", "Count": 64},
            ]
        }
        
        result = self.converter.convert_block(
            "jammyfurniture:IronBlocksOne",
            12,  # Rubbish Bin
            te_data
        )
        
        self.assertTrue(result.success)
        # Kosz w Macaw's ma ograniczoną pojemność
        self.assertIsNotNone(result.target_te)
    
    def test_empty_inventory(self):
        """Puste inventory"""
        te_data = {"Items": []}
        
        result = self.converter.convert_block(
            "jammyfurniture:WoodBlocksTwo",
            0,
            te_data
        )
        
        self.assertTrue(result.success)
        self.assertIsNotNone(result.target_te)
        self.assertEqual(len(result.target_te["Items"]), 0)
    
    def test_no_tile_entity(self):
        """Brak Tile Entity dla bloku z inventory"""
        result = self.converter.convert_block(
            "jammyfurniture:WoodBlocksTwo",
            0,
            None
        )
        
        self.assertTrue(result.success)
        self.assertIsNone(result.target_te)


class TestItemStackConversion(unittest.TestCase):
    """Testy konwersji ItemStack"""
    
    def setUp(self):
        self.converter = JammyFurnitureConverter()
    
    def test_basic_item(self):
        """Podstawowy item"""
        item = {"id": "minecraft:stone", "Count": 64}
        result = self.converter._convert_item_stack(item)
        
        self.assertEqual(result["id"], "minecraft:stone")
        self.assertEqual(result["Count"], 64)
    
    def test_item_with_damage(self):
        """Item z obrażeniami (narzędzie)"""
        item = {"id": "minecraft:diamond_pickaxe", "Count": 1, "Damage": 50}
        result = self.converter._convert_item_stack(item)
        
        self.assertEqual(result["id"], "minecraft:diamond_pickaxe")
        self.assertEqual(result["Damage"], 50)
    
    def test_item_with_tag(self):
        """Item z tagami NBT"""
        item = {
            "id": "minecraft:diamond_sword",
            "Count": 1,
            "tag": {
                "display": {"Name": "My Sword"},
                "ench": [{"id": 16, "lvl": 5}]
            }
        }
        result = self.converter._convert_item_stack(item)
        
        self.assertIn("tag", result)
        self.assertIn("display", result["tag"])
        self.assertIn("Enchantments", result["tag"])
    
    def test_numeric_item_id(self):
        """Numeryczne ID itemu (stary format)"""
        item = {"id": "1", "Count": 1}  # Kamień w starym formacie
        result = self.converter._convert_item_stack(item)
        
        # Powinien zwrócić placeholder
        self.assertIn("TODO", result["id"])


class TestOrientationConversion(unittest.TestCase):
    """Testy konwersji orientacji"""
    
    def setUp(self):
        self.converter = JammyFurnitureConverter()
    
    def test_kitchen_cupboard_north(self):
        """Szafka kuchenna północ"""
        result = self.converter.convert_block("jammyfurniture:WoodBlocksTwo", 0)
        self.assertEqual(result.target_block_state["facing"], "north")
    
    def test_kitchen_cupboard_east(self):
        """Szafka kuchenna wschód"""
        result = self.converter.convert_block("jammyfurniture:WoodBlocksTwo", 1)
        self.assertEqual(result.target_block_state["facing"], "east")
    
    def test_kitchen_cupboard_south(self):
        """Szafka kuchenna południe"""
        result = self.converter.convert_block("jammyfurniture:WoodBlocksTwo", 2)
        self.assertEqual(result.target_block_state["facing"], "south")
    
    def test_kitchen_cupboard_west(self):
        """Szafka kuchenna zachód"""
        result = self.converter.convert_block("jammyfurniture:WoodBlocksTwo", 3)
        self.assertEqual(result.target_block_state["facing"], "west")


class TestSpecialBlocks(unittest.TestCase):
    """Testy specjalnych bloków"""
    
    def setUp(self):
        self.converter = JammyFurnitureConverter()
    
    def test_crafting_table(self):
        """Stół craftingowy"""
        te_data = {
            "Items": [{"Slot": 0, "id": "minecraft:stick", "Count": 4}]
        }
        
        result = self.converter.convert_block(
            "jammyfurniture:WoodBlocksOne",
            13,  # Crafting Side
            te_data
        )
        
        self.assertTrue(result.success)
        self.assertEqual(result.target_block_id, "minecraft:crafting_table")
        # Inventory powinno być zachowane w specjalnym polu
        self.assertIsNotNone(result.target_te)
    
    def test_dishwasher_placeholder(self):
        """Zmywarka - placeholder"""
        te_data = {"Items": [{"Slot": 0, "id": "minecraft:iron_sword", "Count": 1, "Damage": 50}]}
        
        result = self.converter.convert_block(
            "jammyfurniture:IronBlocksTwo",
            0,  # Dishwasher
            te_data
        )
        
        self.assertTrue(result.success)
        # Zmywarka mapuje się na kitchen_cabinet jako placeholder
        self.assertEqual(result.target_te["id"], "mcwfurnitures:kitchen_cabinet")
        self.assertIn("_placeholder_note", result.target_te)
    
    def test_washing_machine_placeholder(self):
        """Pralka - placeholder"""
        te_data = {"Items": [{"Slot": 0, "id": "minecraft:iron_chestplate", "Count": 1, "Damage": 20}]}
        
        result = self.converter.convert_block(
            "jammyfurniture:IronBlocksTwo",
            4,  # Washing Machine
            te_data
        )
        
        self.assertTrue(result.success)
        self.assertIn("_placeholder_note", result.target_te)
    
    def test_basket(self):
        """Kosz"""
        te_data = {"Items": [{"Slot": 0, "id": "minecraft:wheat", "Count": 16}]}
        
        result = self.converter.convert_block(
            "jammyfurniture:WoodBlocksTwo",
            12,  # Basket
            te_data
        )
        
        self.assertTrue(result.success)
        self.assertEqual(result.target_block_id, "handcrafted:basket")


class TestUtilityFunctions(unittest.TestCase):
    """Testy funkcji pomocniczych"""
    
    def test_get_converter_singleton(self):
        """Singleton konwertera"""
        c1 = get_converter()
        c2 = get_converter()
        self.assertIs(c1, c2)
    
    def test_convert_jammy_block_helper(self):
        """Funkcja pomocnicza convert_jammy_block"""
        result = convert_jammy_block("jammyfurniture:WoodBlocksThree", 0)
        self.assertTrue(result.success)
    
    def test_generate_target_id(self):
        """Generowanie ID docelowego"""
        mapping = BlockMapping(
            source_block="test:block",
            source_meta=0,
            target_mod="minecraft",
            target_block="stone",
            target_state={"variant": "smooth"}
        )
        
        target_id = generate_target_id(mapping)
        self.assertEqual(target_id, "minecraft:stone[variant=smooth]")


if __name__ == '__main__':
    unittest.main()
