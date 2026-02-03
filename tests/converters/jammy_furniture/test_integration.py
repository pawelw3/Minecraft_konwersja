"""
Testy integracyjne dla konwertera Jammy Furniture Reborn

Testują pełne scenariusze konwersji:
- Kuchnia (szafki, lodówka, kuchenka, zlew)
- Łazienka (szafka, umywalka, toaleta, wanna)
- Salon (krzesła, stół, sofa, fotel)
- Sypialnia (szafa, zegar)
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..'))

import unittest
from src.converters.jammy_furniture_converter import JammyFurnitureConverter
from src.jammy_furniture.simulations.fridge_freezer_simulation import (
    FridgeFreezerSimulator,
    FridgeType,
    ItemStack as FridgeItemStack,
)
from src.jammy_furniture.simulations.cooker_simulation import (
    CookerSimulator,
    ItemStack as CookerItemStack,
)
from src.jammy_furniture.simulations.crafting_cupboard_simulation import (
    CraftingSideSimulator,
    WardrobeSimulator,
    ItemStack as WardrobeItemStack,
)
from src.jammy_furniture.simulations.dishwasher_washingmachine_simulation import (
    ApplianceSimulator,
    ApplianceType,
    ItemStack as ApplianceItemStack,
)
from src.jammy_furniture.simulations.rubbishbin_clock_simulation import (
    RubbishBinSimulator,
    ItemStack as BinItemStack,
)


class TestKitchenConversion(unittest.TestCase):
    """Testy konwersji kuchni"""
    
    def setUp(self):
        self.converter = JammyFurnitureConverter()
    
    def test_full_kitchen_setup(self):
        """Pełna konwersja zestawu kuchennego"""
        kitchen_blocks = [
            # Szafki kuchenne
            ("jammyfurniture:WoodBlocksTwo", 0, {"Items": [{"Slot": 0, "id": "minecraft:bowl", "Count": 4}]}),
            ("jammyfurniture:WoodBlocksTwo", 1, {"Items": []}),
            # Lodówka (dolna)
            ("jammyfurniture:IronBlocksOne", 0, {"FriFreItems": [
                {"Slot": 0, "id": "minecraft:cooked_porkchop", "Count": 16},
                {"Slot": 1, "id": "minecraft:apple", "Count": 32},
            ]}),
            # Zamrażarka (górna)
            ("jammyfurniture:IronBlocksOne", 4, {"FriFreItems": [
                {"Slot": 0, "id": "minecraft:beef", "Count": 8},
            ]}),
            # Kuchenka
            ("jammyfurniture:IronBlocksOne", 8, None),
            # Zlew kuchenny
            ("jammyfurniture:CeramicBlocksOne", 8, None),
        ]
        
        converted = []
        for block_name, meta, te in kitchen_blocks:
            result = self.converter.convert_block(block_name, meta, te)
            self.assertTrue(result.success, f"Failed to convert {block_name}:{meta}")
            converted.append(result)
        
        # Sprawdź wyniki
        self.assertEqual(converted[0].target_block_id, "mcwfurnitures:oak_kitchen_cabinet")
        self.assertEqual(converted[2].target_block_id, "mcwfurnitures:refrigerator")
        self.assertEqual(converted[4].target_block_id, "mcwfurnitures:stove")
        self.assertEqual(converted[5].target_block_id, "mcwfurnitures:kitchen_sink")
    
    def test_fridge_with_simulated_inventory(self):
        """Lodówka z inventory ze symulacji"""
        # Stwórz symulację lodówki
        fridge_sim = FridgeFreezerSimulator(
            fridge_type=FridgeType.FRIDGE,
            facing="north"
        )
        
        # Dodaj itemy
        fridge_sim.inventory.add_item(FridgeItemStack("minecraft:apple", count=16))
        fridge_sim.inventory.add_item(FridgeItemStack("minecraft:bread", count=8))
        fridge_sim.inventory.add_item(FridgeItemStack("minecraft:cooked_beef", count=32))
        
        # Konwertuj
        nbt_1710 = fridge_sim.to_nbt_1710()
        result = self.converter.convert_block(
            "jammyfurniture:IronBlocksOne",
            0,
            nbt_1710
        )
        
        self.assertTrue(result.success)
        self.assertEqual(result.target_block_id, "mcwfurnitures:refrigerator")
        # Inventory jest w FriFreItems w NBT
        self.assertIsNotNone(result.target_te)
    
    def test_freezer_with_simulated_inventory(self):
        """Zamrażarka z inventory ze symulacji"""
        freezer_sim = FridgeFreezerSimulator(
            fridge_type=FridgeType.FREEZER,
            facing="east"
        )
        
        # Dodaj itemy
        freezer_sim.inventory.add_item(FridgeItemStack("minecraft:beef", count=16))
        freezer_sim.inventory.add_item(FridgeItemStack("minecraft:porkchop", count=8))
        
        # Konwertuj
        nbt_1710 = freezer_sim.to_nbt_1710()
        result = self.converter.convert_block(
            "jammyfurniture:IronBlocksOne",
            4,
            nbt_1710
        )
        
        self.assertTrue(result.success)
        self.assertEqual(result.target_block_id, "mcwfurnitures:refrigerator")
        self.assertEqual(result.target_block_state["part"], "upper")
        self.assertIsNotNone(result.target_te)
    
    def test_cooker_with_simulated_state(self):
        """Kuchenka z symulowanym stanem"""
        cooker_sim = CookerSimulator(
            facing="north"
        )
        
        # Dodaj przedmioty do gotowania (bezpośrednio do state.slots)
        cooker_sim.state.slots[0] = CookerItemStack("minecraft:porkchop", count=1)
        cooker_sim.state.slots[1] = CookerItemStack("minecraft:coal", count=8)
        
        # Symuluj kilka ticków
        for _ in range(10):
            cooker_sim.tick()
        
        # Konwertuj
        nbt_1710 = cooker_sim.to_nbt_1710()
        result = self.converter.convert_block(
            "jammyfurniture:IronBlocksOne",
            8,
            nbt_1710
        )
        
        self.assertTrue(result.success)
        self.assertEqual(result.target_block_id, "mcwfurnitures:stove")


class TestBathroomConversion(unittest.TestCase):
    """Testy konwersji łazienki"""
    
    def setUp(self):
        self.converter = JammyFurnitureConverter()
    
    def test_full_bathroom_setup(self):
        """Pełna konwersja łazienki"""
        bathroom_blocks = [
            # Szafka łazienkowa
            ("jammyfurniture:CeramicBlocksOne", 0, {"Items": [
                {"Slot": 0, "id": "minecraft:paper", "Count": 16},
            ]}),
            # Umywalka
            ("jammyfurniture:CeramicBlocksOne", 4, None),
            # Toaleta
            ("jammyfurniture:CeramicBlocksOne", 12, None),
            # Wanna
            ("jammyfurniture:Bath", 0, None),
        ]
        
        converted = []
        for block_name, meta, te in bathroom_blocks:
            result = self.converter.convert_block(block_name, meta, te)
            self.assertTrue(result.success)
            converted.append(result)
        
        self.assertEqual(converted[0].target_block_id, "mcwfurnitures:bathroom_cabinet")
        self.assertEqual(converted[1].target_block_id, "mcwfurnitures:sink")
        self.assertEqual(converted[2].target_block_id, "mcwfurnitures:toilet")
        self.assertEqual(converted[3].target_block_id, "mcwfurnitures:bathtub")


class TestLivingRoomConversion(unittest.TestCase):
    """Testy konwersji salonu"""
    
    def setUp(self):
        self.converter = JammyFurnitureConverter()
    
    def test_full_living_room_setup(self):
        """Pełna konwersja salonu"""
        living_room_blocks = [
            # Krzesła
            ("jammyfurniture:WoodBlocksThree", 0, None),  # North
            ("jammyfurniture:WoodBlocksThree", 2, None),  # South
            # Stół
            ("jammyfurniture:WoodBlocksOne", 15, None),
            # Fotel
            ("jammyfurniture:ArmChair", 0, None),
            # Sofa
            ("jammyfurniture:SofaLeft", 0, None),
            ("jammyfurniture:SofaCenter", 0, None),
            ("jammyfurniture:SofaRight", 0, None),
            # TV (placeholder)
            ("jammyfurniture:WoodBlocksTwo", 8, None),
        ]
        
        converted = []
        for block_name, meta, te in living_room_blocks:
            result = self.converter.convert_block(block_name, meta, te)
            self.assertTrue(result.success, f"Failed to convert {block_name}:{meta}")
            converted.append(result)
        
        self.assertEqual(converted[0].target_block_id, "handcrafted:chair")
        self.assertEqual(converted[2].target_block_id, "handcrafted:table")
        self.assertEqual(converted[3].target_block_id, "handcrafted:couch")
        self.assertEqual(converted[4].target_block_id, "mcwfurnitures:sofa")
    
    def test_sofa_variants(self):
        """Wszystkie warianty sofy"""
        sofa_parts = [
            ("jammyfurniture:SofaLeft", 0, {"shape": "left"}),
            ("jammyfurniture:SofaCenter", 0, {"shape": "straight"}),
            ("jammyfurniture:SofaRight", 0, {"shape": "right"}),
            ("jammyfurniture:SofaCorner", 0, {"shape": "inner_left"}),
        ]
        
        for block_name, meta, expected_state in sofa_parts:
            result = self.converter.convert_block(block_name, meta)
            self.assertTrue(result.success)
            self.assertEqual(result.target_block_id, "mcwfurnitures:sofa")
            for key, value in expected_state.items():
                self.assertEqual(result.target_block_state[key], value)


class TestBedroomConversion(unittest.TestCase):
    """Testy konwersji sypialni"""
    
    def setUp(self):
        self.converter = JammyFurnitureConverter()
    
    def test_wardrobe_with_inventory(self):
        """Szafa z pełnym inventory"""
        # Stwórz symulację szafy
        wardrobe_sim = WardrobeSimulator(
            facing="north"
        )
        
        # Dodaj ubrania (bezpośrednio do slots)
        wardrobe_sim.inventory.slots[0] = WardrobeItemStack("minecraft:leather_helmet", count=1)
        wardrobe_sim.inventory.slots[1] = WardrobeItemStack("minecraft:leather_chestplate", count=1)
        wardrobe_sim.inventory.slots[2] = WardrobeItemStack("minecraft:leather_leggings", count=1)
        wardrobe_sim.inventory.slots[3] = WardrobeItemStack("minecraft:leather_boots", count=1)
        
        # Konwertuj
        nbt_1710 = wardrobe_sim.to_nbt_1710()
        result = self.converter.convert_block(
            "jammyfurniture:WoodBlocksFour",
            0,
            nbt_1710
        )
        
        self.assertTrue(result.success)
        self.assertEqual(result.target_block_id, "mcwfurnitures:oak_wardrobe")
        self.assertIsNotNone(result.target_te)
        self.assertEqual(len(result.target_te["Items"]), 4)


class TestApplianceConversion(unittest.TestCase):
    """Testy konwersji urządzeń AGD"""
    
    def setUp(self):
        self.converter = JammyFurnitureConverter()
    
    def test_dishwasher_with_tools(self):
        """Zmywarka z narzędziami"""
        # Użyj ręcznie stworzonego NBT (konwerter oczekuje formatu z Items)
        nbt_1710 = {
            "Items": [
                {"Slot": 0, "id": "minecraft:iron_sword", "Count": 1, "Damage": 50},
                {"Slot": 1, "id": "minecraft:diamond_pickaxe", "Count": 1, "Damage": 100},
            ]
        }
        
        result = self.converter.convert_block(
            "jammyfurniture:IronBlocksTwo",
            0,
            nbt_1710
        )
        
        self.assertTrue(result.success)
        # Zmywarka mapuje się na placeholder
        self.assertEqual(result.target_te["id"], "mcwfurnitures:kitchen_cabinet")
        self.assertIn("_placeholder_note", result.target_te)
        # Inventory powinno być zachowane
        self.assertEqual(len(result.target_te["Items"]), 2)
    
    def test_washing_machine_with_armor(self):
        """Pralka z zbroją"""
        washer_sim = ApplianceSimulator(
            appliance_type=ApplianceType.WASHING_MACHINE,
            facing="north"
        )
        
        # Dodaj zbroję (bezpośrednio do state.slots)
        washer_sim.state.slots[0] = ApplianceItemStack(
            "minecraft:iron_chestplate", count=1, damage=30
        )
        washer_sim.state.slots[2] = ApplianceItemStack(
            "minecraft:golden_helmet", count=1, damage=20
        )
        
        # Konwertuj
        nbt_1710 = washer_sim.to_nbt_1710()
        result = self.converter.convert_block(
            "jammyfurniture:IronBlocksTwo",
            4,
            nbt_1710
        )
        
        self.assertTrue(result.success)
        self.assertIn("_placeholder_note", result.target_te)


class TestStorageConversion(unittest.TestCase):
    """Testy konwersji storage"""
    
    def setUp(self):
        self.converter = JammyFurnitureConverter()
    
    def test_rubbish_bin_full(self):
        """Pełny kosz na śmieci"""
        # Stwórz symulację kosza
        bin_sim = RubbishBinSimulator(
            facing="north"
        )
        
        # Wypełnij śmieciami (9 slotów w Jammy) - bezpośrednio do slots
        for slot in range(9):
            bin_sim.inventory.slots[slot] = BinItemStack("minecraft:dirt", count=64)
        
        # Konwertuj
        nbt_1710 = bin_sim.to_nbt_1710()
        result = self.converter.convert_block(
            "jammyfurniture:IronBlocksOne",
            12,
            nbt_1710
        )
        
        self.assertTrue(result.success)
        self.assertEqual(result.target_block_id, "mcwfurnitures:trash_can")
        self.assertIsNotNone(result.target_te)
    
    def test_crafting_cupboard_with_grid(self):
        """Szafka craftingowa z gridem"""
        crafting_sim = CraftingSideSimulator(
            facing="north"
        )
        
        # Wypełnij crafting grid (3x2 = 6 slotów) - bezpośrednio do slots
        crafting_sim.inventory.slots[0] = WardrobeItemStack("minecraft:oak_planks", count=1)
        crafting_sim.inventory.slots[1] = WardrobeItemStack("minecraft:oak_planks", count=1)
        crafting_sim.inventory.slots[2] = WardrobeItemStack("minecraft:oak_planks", count=1)
        crafting_sim.inventory.slots[3] = WardrobeItemStack("minecraft:stick", count=1)
        crafting_sim.inventory.slots[4] = WardrobeItemStack("minecraft:stick", count=1)
        
        # Konwertuj
        nbt_1710 = crafting_sim.to_nbt_1710()
        result = self.converter.convert_block(
            "jammyfurniture:WoodBlocksOne",
            13,
            nbt_1710
        )
        
        self.assertTrue(result.success)
        self.assertEqual(result.target_block_id, "minecraft:crafting_table")
        self.assertIsNotNone(result.target_te)
        self.assertIn("_saved_inventory", result.target_te)


class TestEdgeCases(unittest.TestCase):
    """Testy przypadków brzegowych"""
    
    def setUp(self):
        self.converter = JammyFurnitureConverter()
    
    def test_unknown_block(self):
        """Nieznany blok"""
        result = self.converter.convert_block("unknown:mod", 0)
        self.assertFalse(result.success)
        self.assertIsNotNone(result.error_message)
    
    def test_invalid_metadata(self):
        """Nieprawidłowe metadata"""
        result = self.converter.convert_block("jammyfurniture:WoodBlocksTwo", 99)
        self.assertFalse(result.success)
    
    def test_none_tile_entity(self):
        """None jako Tile Entity"""
        result = self.converter.convert_block(
            "jammyfurniture:WoodBlocksTwo",
            0,
            None
        )
        self.assertTrue(result.success)
        # Dla bloku z inventory, ale bez TE - nie powinno być target_te
        # lub powinno być puste
    
    def test_empty_string_block_name(self):
        """Pusty string jako nazwa bloku"""
        result = self.converter.convert_block("", 0)
        self.assertFalse(result.success)
    
    def test_minecraft_prefix_fix(self):
        """Naprawa podwójnego prefixu minecraft:"""
        result = self.converter.convert_block(
            "minecraft:jammyfurniture:WoodBlocksOne",
            0
        )
        self.assertTrue(result.success)


class TestPerformance(unittest.TestCase):
    """Testy wydajnościowe"""
    
    def setUp(self):
        self.converter = JammyFurnitureConverter()
    
    def test_bulk_conversion(self):
        """Masowa konwersja bloków"""
        blocks_to_convert = [
            ("jammyfurniture:WoodBlocksTwo", i % 4) for i in range(100)
        ]
        
        results = []
        for block_name, meta in blocks_to_convert:
            result = self.converter.convert_block(block_name, meta)
            results.append(result)
        
        # Wszystkie powinny się udać
        successful = sum(1 for r in results if r.success)
        self.assertEqual(successful, 100)


if __name__ == '__main__':
    unittest.main()
