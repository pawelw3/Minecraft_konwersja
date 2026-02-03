"""
Testy jednostkowe dla konwerterów Blood Magic

Testy obejmują:
- Mapowanie ID bloków (w tym Blood Runes jako osobne bloki)
- Konwersję NBT Master Ritual Stone (zgodnie ze źródłem 1.18.2)
- Konwersję NBT Blood Altar (zgodnie ze źródłem 1.18.2)
- Konwersję Soul Network (zgodnie ze źródłem 1.18.2)
- Konwersję Blood Orbs (zgodnie ze źródłem 1.18.2)

Source mapping weryfikowany:
- 1.18.2: wayoftime/bloodmagic/common/tile/TileMasterRitualStone.java
- 1.18.2: wayoftime/bloodmagic/altar/BloodAltar.java
- 1.18.2: wayoftime/bloodmagic/core/data/SoulNetwork.java
- 1.18.2: wayoftime/bloodmagic/core/data/Binding.java
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..'))

import unittest
from uuid import UUID, uuid4

from src.converters.bloodmagic import (
    BloodMagicConverter,
    map_block_id,
    map_blood_rune,
    map_te_id,
    BloodAltarConverter,
    MasterRitualStoneConverter,
    SoulNetworkConverter,
    BloodOrbConverter,
    RUNE_BLOCK_MAPPING,
    BLOOD_RUNE_META_MAPPING,
)


class TestBlockMappings(unittest.TestCase):
    """Testy mapowania bloków"""
    
    def test_map_blood_altar(self):
        """Test mapowania Blood Altar"""
        new_id, warning = map_block_id("AWWayofTime:Altar")
        self.assertEqual(new_id, "bloodmagic:altar")
        self.assertIsNone(warning)
    
    def test_map_master_ritual_stone(self):
        """Test mapowania Master Ritual Stone"""
        new_id, warning = map_block_id("AWWayofTime:masterStone")
        self.assertEqual(new_id, "bloodmagic:master_ritual_stone")
        self.assertIsNone(warning)
    
    def test_map_speed_rune(self):
        """Test mapowania Speed Rune (osobny blok)"""
        new_id, warning = map_block_id("AWWayofTime:speedRune")
        self.assertEqual(new_id, "bloodmagic:speed_rune")
        self.assertIsNone(warning)
    
    def test_map_sacrifice_rune(self):
        """Test mapowania Sacrifice Rune (osobny blok)"""
        new_id, warning = map_block_id("AWWayofTime:runeOfSacrifice")
        self.assertEqual(new_id, "bloodmagic:sacrifice_rune")
        self.assertIsNone(warning)
    
    def test_map_self_sacrifice_rune(self):
        """Test mapowania Self-Sacrifice Rune (osobny blok)"""
        new_id, warning = map_block_id("AWWayofTime:runeOfSelfSacrifice")
        self.assertEqual(new_id, "bloodmagic:self_sacrifice_rune")
        self.assertIsNone(warning)
    
    def test_map_blood_rune_with_metadata(self):
        """Test mapowania BloodRune z metadanymi (0-5)"""
        test_cases = [
            (0, "bloodmagic:blank_rune"),
            (1, "bloodmagic:dislocation_rune"),
            (2, "bloodmagic:capacity_rune"),
            (3, "bloodmagic:better_capacity_rune"),
            (4, "bloodmagic:orb_rune"),
            (5, "bloodmagic:acceleration_rune"),
        ]
        
        for metadata, expected_block in test_cases:
            new_id, warning = map_blood_rune(metadata)
            self.assertEqual(new_id, expected_block, f"Failed for metadata {metadata}")
            self.assertIsNone(warning)
    
    def test_map_blood_rune_unknown_metadata(self):
        """Test mapowania BloodRune z nieznaną metadata"""
        new_id, warning = map_blood_rune(99)
        self.assertIsNone(new_id)
        self.assertIn("UNKNOWN-META", warning)
    
    def test_map_removed_soul_forge(self):
        """Test mapowania usuniętego Soul Forge"""
        new_id, warning = map_block_id("AWWayofTime:soulForge")
        self.assertIsNone(new_id)
        self.assertIn("SOULFORGE-REMOVED", warning)
    
    def test_map_removed_demon_portal(self):
        """Test mapowania usuniętego Demon Portal"""
        new_id, warning = map_block_id("AWWayofTime:demonPortal")
        self.assertIsNone(new_id)
        self.assertIn("DEMONPORTAL-REMOVED", warning)
    
    def test_map_unknown_block(self):
        """Test mapowania nieznanego bloku"""
        new_id, warning = map_block_id("AWWayofTime:unknownBlock")
        self.assertIsNone(new_id)
        self.assertIn("UNKNOWN-BLOCK", warning)


class TestBloodAltarConverter(unittest.TestCase):
    """Testy konwertera Blood Altar - zgodnie ze źródłem 1.18.2"""
    
    def setUp(self):
        self.converter = BloodAltarConverter()
    
    def test_basic_conversion(self):
        """Test podstawowej konwersji Blood Altar"""
        nbt_1710 = {
            "id": "Altar",
            "x": 100, "y": 64, "z": -200,
            "currentEssence": 15000,
            "upgradeLevel": 3,
            "isActive": False,
            "progress": 0,
            "liquidRequired": 0,
            "canBeFilled": True,
        }
        
        nbt_1182, warnings = self.converter.convert(nbt_1710)
        
        # Sprawdź strukturę zagnieżdżoną
        self.assertIn("bloodAltar", nbt_1182)
        altar_data = nbt_1182["bloodAltar"]
        
        # Kluczowe pola (zgodnie z Constants.NBT w 1.18.2)
        self.assertEqual(altar_data["upgradeLevel"], "THREE")
        self.assertEqual(altar_data["isActive"], False)
        self.assertEqual(altar_data["progress"], 0)
        self.assertEqual(altar_data["liquidRequired"], 0)
        self.assertEqual(altar_data["fillable"], True)
        
        self.assertEqual(len(warnings), 0)
    
    def test_tier_conversion(self):
        """Test konwersji wszystkich tierów"""
        expected_tiers = [
            (1, "ONE"),
            (2, "TWO"),
            (3, "THREE"),
            (4, "FOUR"),
            (5, "FIVE"),
            (6, "SIX"),
        ]
        
        for old_tier, expected_new in expected_tiers:
            nbt_1710 = {"upgradeLevel": old_tier}
            nbt_1182, _ = self.converter.convert(nbt_1710)
            self.assertEqual(nbt_1182["bloodAltar"]["upgradeLevel"], expected_new)
    
    def test_unknown_tier_warning(self):
        """Test ostrzeżenia o nieznanym tierze"""
        nbt_1710 = {"upgradeLevel": 99}
        nbt_1182, warnings = self.converter.convert(nbt_1710)
        
        self.assertEqual(nbt_1182["bloodAltar"]["upgradeLevel"], "ONE")
        self.assertTrue(any("TIER-UNKNOWN" in w for w in warnings))
    
    def test_active_crafting_warning(self):
        """Test ostrzeżenia o aktywnym craftingu"""
        nbt_1710 = {
            "isActive": True,
            "progress": 500,
            "liquidRequired": 2000,
        }
        
        nbt_1182, warnings = self.converter.convert(nbt_1710)
        
        self.assertTrue(any("ALTAR-ACTIVE" in w for w in warnings))
    
    def test_nbt_keys_match_source(self):
        """Test czy klucze NBT zgadzają się ze źródłem 1.18.2"""
        nbt_1710 = {
            "currentEssence": 10000,
            "upgradeLevel": 2,
            "isActive": True,
            "progress": 100,
            "liquidRequired": 500,
            "canBeFilled": False,
        }
        
        nbt_1182, _ = self.converter.convert(nbt_1710)
        altar_data = nbt_1182["bloodAltar"]
        
        # Klucze z Constants.NBT w 1.18.2
        expected_keys = [
            "upgradeLevel", "isActive", "liquidRequired", "fillable",
            "progress", "consumptionMultiplier", "efficiencyMultiplier",
            "sacrificeMultiplier", "selfSacrificeMultiplier",
            "capacityMultiplier", "orbCapacityMultiplier", "dislocationMultiplier",
        ]
        
        for key in expected_keys:
            self.assertIn(key, altar_data, f"Missing key: {key}")


class TestMasterRitualStoneConverter(unittest.TestCase):
    """Testy konwertera Master Ritual Stone - zgodnie ze źródłem 1.18.2"""
    
    def setUp(self):
        self.converter = MasterRitualStoneConverter()
    
    def test_basic_conversion(self):
        """Test podstawowej konwersji Master Ritual Stone"""
        nbt_1710 = {
            "id": "MasterStone",
            "x": 100, "y": 64, "z": -200,
            "ritualType": "water",
            "owner": "Player123",
            "isActive": False,
            "cooldown": 0,
            "runningTime": 0,
        }
        
        nbt_1182, warnings = self.converter.convert(nbt_1710)
        
        # Klucze zgodne z TileMasterRitualStone.serialize()
        self.assertEqual(nbt_1182["currentRitual"], "bloodmagic:water")
        self.assertEqual(nbt_1182["isRunning"], False)
        self.assertEqual(nbt_1182["runtime"], 0)
        self.assertEqual(nbt_1182["direction"], 2)  # NORTH
        self.assertEqual(nbt_1182["isStoned"], False)
        self.assertIn("currentRitualTag", nbt_1182)
    
    def test_ritual_type_mapping(self):
        """Test mapowania typów rytuałów"""
        test_cases = [
            ("water", "bloodmagic:water"),
            ("suffering", "bloodmagic:well_of_suffering"),
            ("greenGrove", "bloodmagic:growth"),
            ("highJump", "bloodmagic:jumping"),
            ("speed", "bloodmagic:speed"),
            ("crushing", "bloodmagic:crushing"),
            ("featheredKnife", "bloodmagic:feathered_knife"),
        ]
        
        for old_type, expected_new in test_cases:
            nbt_1710 = {"ritualType": old_type}
            nbt_1182, _ = self.converter.convert(nbt_1710)
            self.assertEqual(nbt_1182["currentRitual"], expected_new)
    
    def test_running_time_conversion(self):
        """Test konwersji runningTime -> runtime"""
        nbt_1710 = {
            "ritualType": "water",
            "isActive": True,
            "runningTime": 1500,
        }
        
        nbt_1182, _ = self.converter.convert(nbt_1710)
        self.assertEqual(nbt_1182["runtime"], 1500)
        self.assertEqual(nbt_1182["isRunning"], True)
    
    def test_nbt_keys_match_source(self):
        """Test czy klucze NBT zgadzają się ze źródłem 1.18.2"""
        nbt_1710 = {
            "ritualType": "water",
            "owner": "Player123",
            "isActive": True,
            "runningTime": 100,
        }
        
        nbt_1182, _ = self.converter.convert(nbt_1710)
        
        # Klucze z Constants.NBT w 1.18.2
        expected_keys = [
            "currentRitual", "owner", "isRunning", "runtime", 
            "direction", "isStoned", "currentRitualTag"
        ]
        
        for key in expected_keys:
            self.assertIn(key, nbt_1182, f"Missing key: {key}")
        
        # Niepoprawne klucze (używane wcześniej błędnie)
        incorrect_keys = ["ritualID", "active", "ownerUUID", "willDrain"]
        for key in incorrect_keys:
            self.assertNotIn(key, nbt_1182, f"Should not have key: {key}")


class TestSoulNetworkConverter(unittest.TestCase):
    """Testy konwertera Soul Network - zgodnie ze źródłem 1.18.2"""
    
    def setUp(self):
        self.converter = SoulNetworkConverter()
    
    def test_basic_conversion(self):
        """Test podstawowej konwersji Soul Network"""
        nbt_1710 = {
            "currentEssence": 50000,
            "maxOrb": 3,
        }
        
        nbt_1182, warnings = self.converter.convert_player_network("Player123", nbt_1710)
        
        # Klucze z SoulNetwork.serializeNBT()
        self.assertEqual(nbt_1182["currentEssence"], 50000)
        self.assertEqual(nbt_1182["orbTier"], 3)
        self.assertIn("playerId", nbt_1182)
    
    def test_uuid_resolution(self):
        """Test rozwiązywania UUID"""
        test_uuid = uuid4()
        mapping = {"Player123": test_uuid}
        self.converter.set_name_to_uuid_mapping(mapping)
        
        nbt_1710 = {"currentEssence": 1000, "maxOrb": 1}
        nbt_1182, warnings = self.converter.convert_player_network("Player123", nbt_1710)
        
        self.assertEqual(nbt_1182["playerId"], str(test_uuid))
    
    def test_nbt_keys_match_source(self):
        """Test czy klucze NBT zgadzają się ze źródłem 1.18.2"""
        nbt_1710 = {"currentEssence": 1000, "maxOrb": 1}
        nbt_1182, _ = self.converter.convert_player_network("Player123", nbt_1710)
        
        # Klucze z SoulNetwork.serializeNBT()
        expected_keys = ["playerId", "currentEssence", "orbTier"]
        
        for key in expected_keys:
            self.assertIn(key, nbt_1182, f"Missing key: {key}")


class TestBloodOrbConverter(unittest.TestCase):
    """Testy konwertera Blood Orbs - zgodnie ze źródłem 1.18.2"""
    
    def setUp(self):
        self.converter = BloodOrbConverter()
    
    def test_orb_id_mapping(self):
        """Test mapowania ID orbów"""
        test_cases = [
            ("AWWayofTime:weakBloodOrb", "bloodmagic:weak_blood_orb"),
            ("AWWayofTime:apprenticeBloodOrb", "bloodmagic:apprentice_blood_orb"),
            ("AWWayofTime:magicianBloodOrb", "bloodmagic:magician_blood_orb"),
            ("AWWayofTime:masterBloodOrb", "bloodmagic:master_blood_orb"),
            ("AWWayofTime:archmageBloodOrb", "bloodmagic:archmage_blood_orb"),
            ("AWWayofTime:transcendentBloodOrb", "bloodmagic:archmage_blood_orb"),
        ]
        
        for old_id, expected_new in test_cases:
            item_nbt = {"id": old_id, "Count": 1}
            result, _ = self.converter.convert_orb_item(item_nbt)
            self.assertEqual(result["id"], expected_new)
    
    def test_bound_orb_conversion(self):
        """Test konwersji zbindowanego orba - zgodnie z Binding.serializeNBT()"""
        test_uuid = uuid4()
        mapping = {"Player123": test_uuid}
        self.converter.set_name_to_uuid_mapping(mapping)
        
        item_nbt = {
            "id": "AWWayofTime:weakBloodOrb",
            "Count": 1,
            "tag": {"ownerName": "Player123"}
        }
        
        result, warnings = self.converter.convert_orb_item(item_nbt)
        
        # Format z Binding.serializeNBT(): "binding" -> {"id": UUID, "name": string}
        self.assertIn("binding", result["tag"])
        binding = result["tag"]["binding"]
        self.assertEqual(binding["id"], str(test_uuid))
        self.assertEqual(binding["name"], "Player123")
    
    def test_unbound_orb_conversion(self):
        """Test konwersji niezbindowanego orba"""
        item_nbt = {
            "id": "AWWayofTime:weakBloodOrb",
            "Count": 1,
        }
        
        result, warnings = self.converter.convert_orb_item(item_nbt)
        
        # Niezbindowany orb nie ma tagu binding
        self.assertNotIn("tag", result)
    
    def test_binding_keys_match_source(self):
        """Test czy klucze bindingu zgadzają się ze źródłem 1.18.2"""
        test_uuid = uuid4()
        mapping = {"Player123": test_uuid}
        self.converter.set_name_to_uuid_mapping(mapping)
        
        item_nbt = {
            "id": "AWWayofTime:weakBloodOrb",
            "Count": 1,
            "tag": {"ownerName": "Player123"}
        }
        
        result, _ = self.converter.convert_orb_item(item_nbt)
        binding = result["tag"]["binding"]
        
        # Klucze z Binding.serializeNBT()
        self.assertIn("id", binding)
        self.assertIn("name", binding)


class TestBloodMagicConverter(unittest.TestCase):
    """Testy głównego konwertera Blood Magic"""
    
    def setUp(self):
        self.converter = BloodMagicConverter()
    
    def test_convert_blood_altar_block(self):
        """Test konwersji bloku Blood Altar z TE i pozycją"""
        te_nbt = {
            "id": "Altar",
            "currentEssence": 20000,
            "upgradeLevel": 4,
            "isActive": False,
        }
        
        result = self.converter.convert_block(
            block_id_1710="AWWayofTime:Altar",
            metadata=0,
            te_nbt_1710=te_nbt,
            pos=(100, 64, -200)
        )
        
        self.assertTrue(result.is_success())
        self.assertEqual(result.block_id_1182, "bloodmagic:altar")
        self.assertIsNotNone(result.be_nbt_1182)
        
        # Sprawdź czy pozycja została dodana
        self.assertEqual(result.be_nbt_1182["x"], 100)
        self.assertEqual(result.be_nbt_1182["y"], 64)
        self.assertEqual(result.be_nbt_1182["z"], -200)
        
        # Sprawdź ID BE
        self.assertEqual(result.be_nbt_1182["id"], "bloodmagic:altar")
    
    def test_convert_speed_rune(self):
        """Test konwersji Speed Rune (osobny blok)"""
        result = self.converter.convert_block(
            block_id_1710="AWWayofTime:speedRune",
            metadata=0,
            pos=(101, 64, -200)
        )
        
        self.assertTrue(result.is_success())
        self.assertEqual(result.block_id_1182, "bloodmagic:speed_rune")
        # Runy nie mają blockstate "type"
        self.assertEqual(result.blockstate_props, {})
    
    def test_convert_blood_rune_blank(self):
        """Test konwersji BloodRune (metadata 0 = blank)"""
        result = self.converter.convert_block(
            block_id_1710="AWWayofTime:bloodRune",
            metadata=0,
            pos=(101, 64, -200)
        )
        
        self.assertTrue(result.is_success())
        self.assertEqual(result.block_id_1182, "bloodmagic:blank_rune")
    
    def test_convert_removed_block(self):
        """Test konwersji usuniętego bloku"""
        result = self.converter.convert_block(
            block_id_1710="AWWayofTime:soulForge",
            metadata=0,
            pos=(100, 64, -200)
        )
        
        self.assertTrue(result.skipped)
        self.assertIsNone(result.block_id_1182)
        self.assertTrue(any("SOULFORGE-REMOVED" in w for w in result.warnings))
    
    def test_convert_master_ritual_stone(self):
        """Test konwersji Master Ritual Stone z pozycją"""
        te_nbt = {
            "id": "MasterStone",
            "ritualType": "suffering",
            "owner": "Player123",
            "isActive": False,
        }
        
        result = self.converter.convert_block(
            block_id_1710="AWWayofTime:masterStone",
            metadata=0,
            te_nbt_1710=te_nbt,
            pos=(100, 64, -200)
        )
        
        self.assertTrue(result.is_success())
        self.assertEqual(result.block_id_1182, "bloodmagic:master_ritual_stone")
        self.assertEqual(result.be_nbt_1182["currentRitual"], "bloodmagic:well_of_suffering")
        
        # Sprawdź czy pozycja została dodana
        self.assertEqual(result.be_nbt_1182["x"], 100)
        self.assertEqual(result.be_nbt_1182["y"], 64)
        self.assertEqual(result.be_nbt_1182["z"], -200)
    
    def test_get_supported_blocks(self):
        """Test pobierania listy obsługiwanych bloków"""
        blocks = self.converter.get_supported_blocks()
        
        self.assertIn("AWWayofTime:Altar", blocks)
        self.assertIn("AWWayofTime:speedRune", blocks)
        self.assertIn("AWWayofTime:runeOfSacrifice", blocks)
        self.assertIn("AWWayofTime:bloodRune", blocks)
        self.assertIn("AWWayofTime:masterStone", blocks)
    
    def test_conversion_stats(self):
        """Test generowania statystyk konwersji"""
        results = [
            self.converter.convert_block("AWWayofTime:Altar", 0),
            self.converter.convert_block("AWWayofTime:speedRune", 0),
            self.converter.convert_block("AWWayofTime:soulForge", 0),  # Skipped
        ]
        
        stats = self.converter.get_conversion_stats(results)
        
        self.assertEqual(stats["total_blocks"], 3)
        self.assertEqual(stats["converted"], 2)
        self.assertEqual(stats["skipped"], 1)
        self.assertEqual(stats["failed"], 0)


def run_tests():
    """Uruchom wszystkie testy"""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Dodaj wszystkie testy
    suite.addTests(loader.loadTestsFromTestCase(TestBlockMappings))
    suite.addTests(loader.loadTestsFromTestCase(TestBloodAltarConverter))
    suite.addTests(loader.loadTestsFromTestCase(TestMasterRitualStoneConverter))
    suite.addTests(loader.loadTestsFromTestCase(TestSoulNetworkConverter))
    suite.addTests(loader.loadTestsFromTestCase(TestBloodOrbConverter))
    suite.addTests(loader.loadTestsFromTestCase(TestBloodMagicConverter))
    
    # Uruchom testy
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)
