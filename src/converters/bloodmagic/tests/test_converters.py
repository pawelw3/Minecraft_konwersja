"""
Testy jednostkowe dla konwerterów Blood Magic

Testy obejmują:
- Mapowanie ID bloków
- Konwersję blockstates (metadata -> properties)
- Konwersję NBT Blood Altar
- Konwersję NBT Master Ritual Stone
- Konwersję Soul Network
- Konwersję Blood Orbs
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..'))

import unittest
from uuid import UUID, uuid4

from src.converters.bloodmagic import (
    BloodMagicConverter,
    map_block_id,
    get_blockstate_props,
    BloodAltarConverter,
    MasterRitualStoneConverter,
    SoulNetworkConverter,
    BloodOrbConverter,
)


class TestBlockMappings(unittest.TestCase):
    """Testy mapowania bloków"""
    
    def test_map_blood_altar(self):
        """Test mapowania Blood Altar"""
        new_id, warning = map_block_id("AWWayofTime:Altar")
        self.assertEqual(new_id, "bloodmagic:altar")
        self.assertIsNone(warning)
    
    def test_map_blood_rune(self):
        """Test mapowania Blood Rune"""
        new_id, warning = map_block_id("AWWayofTime:rune")
        self.assertEqual(new_id, "bloodmagic:blood_rune")
        self.assertIsNone(warning)
    
    def test_map_ritual_stone(self):
        """Test mapowania Ritual Stone"""
        new_id, warning = map_block_id("AWWayofTime:ritualStone")
        self.assertEqual(new_id, "bloodmagic:ritual_stone")
        self.assertIsNone(warning)
    
    def test_map_master_ritual_stone(self):
        """Test mapowania Master Ritual Stone"""
        new_id, warning = map_block_id("AWWayofTime:masterStone")
        self.assertEqual(new_id, "bloodmagic:master_ritual_stone")
        self.assertIsNone(warning)
    
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
        self.assertIn("Nieznany blok", warning)


class TestBlockstateProps(unittest.TestCase):
    """Testy konwersji blockstate properties"""
    
    def test_blood_rune_blank(self):
        """Test mapowania Blank Rune (metadata 0)"""
        props, warning = get_blockstate_props("AWWayofTime:rune", 0)
        self.assertEqual(props["type"], "blank")
        self.assertIsNone(warning)
    
    def test_blood_rune_speed(self):
        """Test mapowania Speed Rune (metadata 1)"""
        props, warning = get_blockstate_props("AWWayofTime:rune", 1)
        self.assertEqual(props["type"], "speed")
        self.assertIsNone(warning)
    
    def test_blood_rune_all_types(self):
        """Test mapowania wszystkich typów run"""
        expected_types = [
            (0, "blank"),
            (1, "speed"),
            (2, "efficiency"),
            (3, "sacrifice"),
            (4, "self_sacrifice"),
            (5, "displacement"),
            (6, "capacity"),
            (7, "orb"),
        ]
        for metadata, expected_type in expected_types:
            props, warning = get_blockstate_props("AWWayofTime:rune", metadata)
            self.assertEqual(props["type"], expected_type, f"Failed for metadata {metadata}")
    
    def test_blood_rune_unknown_metadata(self):
        """Test mapowania nieznanej metadata runy"""
        props, warning = get_blockstate_props("AWWayofTime:rune", 99)
        self.assertEqual(props["type"], "blank")
        self.assertIn("UNKNOWN-META", warning)
    
    def test_ritual_stone_types(self):
        """Test mapowania typów Ritual Stone"""
        expected_types = [
            (0, "raw"),
            (1, "fire"),
            (2, "water"),
            (3, "earth"),
            (4, "air"),
            (5, "dusk"),
            (6, "dawn"),
        ]
        for metadata, expected_type in expected_types:
            props, warning = get_blockstate_props("AWWayofTime:ritualStone", metadata)
            self.assertEqual(props["type"], expected_type)


class TestBloodAltarConverter(unittest.TestCase):
    """Testy konwertera Blood Altar"""
    
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
        
        self.assertEqual(nbt_1182["currentEssence"], 15000)
        self.assertEqual(nbt_1182["altarTier"], "THREE")
        self.assertEqual(nbt_1182["altarActive"], False)
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
            self.assertEqual(nbt_1182["altarTier"], expected_new)
    
    def test_unknown_tier_warning(self):
        """Test ostrzeżenia o nieznanym tierze"""
        nbt_1710 = {"upgradeLevel": 99}
        nbt_1182, warnings = self.converter.convert(nbt_1710)
        
        self.assertEqual(nbt_1182["altarTier"], "ONE")
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
    
    def test_multipliers_preservation(self):
        """Test zachowania multiplikatorów"""
        nbt_1710 = {
            "consumptionMultiplier": 0.4,
            "efficiencyMultiplier": 0.85,
            "sacrificeEfficiencyMultiplier": 0.2,
            "selfSacrificeEfficiencyMultiplier": 0.1,
            "capacityMultiplier": 1.2,
            "orbCapacityMultiplier": 1.04,
            "dislocationMultiplier": 1.2,
            "accelerationUpgrades": 2,
        }
        
        nbt_1182, _ = self.converter.convert(nbt_1710)
        
        self.assertEqual(nbt_1182["consumptionMultiplier"], 0.4)
        self.assertEqual(nbt_1182["efficiencyMultiplier"], 0.85)
        self.assertEqual(nbt_1182["sacrificeMultiplier"], 0.2)
        self.assertEqual(nbt_1182["selfSacrificeMultiplier"], 0.1)
        self.assertEqual(nbt_1182["capacityMultiplier"], 1.2)
        self.assertEqual(nbt_1182["orbCapacityMultiplier"], 1.04)
        self.assertEqual(nbt_1182["dislocationMultiplier"], 1.2)
        self.assertEqual(nbt_1182["accelerationUpgrades"], 2)
    
    def test_with_owner_uuid(self):
        """Test konwersji z podanym UUID właściciela"""
        test_uuid = uuid4()
        nbt_1710 = {"owner": "OldPlayerName"}
        
        nbt_1182, warnings = self.converter.convert(nbt_1710, owner_uuid=test_uuid)
        
        self.assertEqual(nbt_1182["owner"], str(test_uuid))
        self.assertEqual(len(warnings), 0)


class TestMasterRitualStoneConverter(unittest.TestCase):
    """Testy konwertera Master Ritual Stone"""
    
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
        
        self.assertEqual(nbt_1182["ritualID"], "bloodmagic:water")
        self.assertEqual(nbt_1182["owner"], "Player123")
        self.assertEqual(nbt_1182["active"], False)
        self.assertEqual(nbt_1182["willDrain"], 0)
    
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
            self.assertEqual(nbt_1182["ritualID"], expected_new)
    
    def test_unknown_ritual_warning(self):
        """Test ostrzeżenia o nieznanym rytuale"""
        nbt_1710 = {"ritualType": "unknownRitual"}
        nbt_1182, warnings = self.converter.convert(nbt_1710)
        
        self.assertEqual(nbt_1182["ritualID"], "bloodmagic:unknownRitual")
        self.assertTrue(any("RITUAL-UNKNOWN" in w for w in warnings))
    
    def test_active_ritual_warning(self):
        """Test ostrzeżenia o aktywnym rytuale"""
        nbt_1710 = {
            "ritualType": "suffering",
            "isActive": True,
        }
        
        nbt_1182, warnings = self.converter.convert(nbt_1710)
        
        self.assertTrue(any("RITUAL-ACTIVE" in w for w in warnings))
    
    def test_reagent_warning(self):
        """Test ostrzeżenia o reagentach (1.7.10) vs Demon Will (1.18.2)"""
        nbt_1710 = {"ritualType": "suffering"}
        nbt_1182, warnings = self.converter.convert(nbt_1710)
        
        self.assertTrue(any("RITUAL-REAGENTS" in w for w in warnings))


class TestSoulNetworkConverter(unittest.TestCase):
    """Testy konwertera Soul Network"""
    
    def setUp(self):
        self.converter = SoulNetworkConverter()
    
    def test_basic_conversion(self):
        """Test podstawowej konwersji Soul Network"""
        nbt_1710 = {
            "currentEssence": 50000,
            "maxOrb": 3,
        }
        
        nbt_1182, warnings = self.converter.convert_player_network("Player123", nbt_1710)
        
        self.assertEqual(nbt_1182["currentEssence"], 50000)
        self.assertEqual(nbt_1182["orbTier"], 3)
        self.assertEqual(nbt_1182["playerName"], "Player123")
    
    def test_uuid_resolution(self):
        """Test rozwiązywania UUID"""
        test_uuid = uuid4()
        mapping = {"Player123": test_uuid}
        self.converter.set_name_to_uuid_mapping(mapping)
        
        nbt_1710 = {"currentEssence": 1000, "maxOrb": 1}
        nbt_1182, warnings = self.converter.convert_player_network("Player123", nbt_1710)
        
        self.assertEqual(nbt_1182["ownerUUID"], str(test_uuid))
        self.assertEqual(len(warnings), 0)
    
    def test_no_uuid_warning(self):
        """Test ostrzeżenia o braku UUID"""
        nbt_1710 = {"currentEssence": 1000, "maxOrb": 1}
        nbt_1182, warnings = self.converter.convert_player_network("UnknownPlayer", nbt_1710)
        
        self.assertTrue(any("NETWORK-NO-UUID" in w for w in warnings))
    
    def test_overflow_warning(self):
        """Test ostrzeżenia o przepełnieniu LP"""
        # Tier 1 orb ma max 5000 LP
        nbt_1710 = {"currentEssence": 10000, "maxOrb": 1}
        nbt_1182, warnings = self.converter.convert_player_network("Player123", nbt_1710)
        
        self.assertTrue(any("NETWORK-OVERFLOW" in w for w in warnings))


class TestBloodOrbConverter(unittest.TestCase):
    """Testy konwertera Blood Orbs"""
    
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
        """Test konwersji zbindowanego orba"""
        test_uuid = uuid4()
        mapping = {"Player123": test_uuid}
        self.converter.set_name_to_uuid_mapping(mapping)
        
        item_nbt = {
            "id": "AWWayofTime:weakBloodOrb",
            "Count": 1,
            "tag": {"ownerName": "Player123"}
        }
        
        result, warnings = self.converter.convert_orb_item(item_nbt)
        
        self.assertEqual(result["tag"]["binding"]["ownerUUID"], str(test_uuid))
        self.assertEqual(result["tag"]["binding"]["ownerName"], "Player123")
        self.assertEqual(len(warnings), 0)
    
    def test_unbound_orb_conversion(self):
        """Test konwersji niezbindowanego orba"""
        item_nbt = {
            "id": "AWWayofTime:weakBloodOrb",
            "Count": 1,
        }
        
        result, warnings = self.converter.convert_orb_item(item_nbt)
        
        self.assertNotIn("tag", result)
    
    def test_orb_no_uuid_warning(self):
        """Test ostrzeżenia o braku UUID dla orba"""
        item_nbt = {
            "id": "AWWayofTime:weakBloodOrb",
            "Count": 1,
            "tag": {"ownerName": "UnknownPlayer"}
        }
        
        result, warnings = self.converter.convert_orb_item(item_nbt)
        
        self.assertTrue(any("ORB-NO-UUID" in w for w in warnings))


class TestBloodMagicConverter(unittest.TestCase):
    """Testy głównego konwertera Blood Magic"""
    
    def setUp(self):
        self.converter = BloodMagicConverter()
    
    def test_convert_blood_altar_block(self):
        """Test konwersji bloku Blood Altar z TE"""
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
        self.assertEqual(result.be_nbt_1182["altarTier"], "FOUR")
    
    def test_convert_blood_rune(self):
        """Test konwersji Blood Rune"""
        result = self.converter.convert_block(
            block_id_1710="AWWayofTime:rune",
            metadata=2,  # Efficiency Rune
            pos=(101, 64, -200)
        )
        
        self.assertTrue(result.is_success())
        self.assertEqual(result.block_id_1182, "bloodmagic:blood_rune")
        self.assertEqual(result.blockstate_props["type"], "efficiency")
    
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
        """Test konwersji Master Ritual Stone"""
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
        self.assertEqual(result.be_nbt_1182["ritualID"], "bloodmagic:well_of_suffering")
    
    def test_get_supported_blocks(self):
        """Test pobierania listy obsługiwanych bloków"""
        blocks = self.converter.get_supported_blocks()
        
        self.assertIn("AWWayofTime:Altar", blocks)
        self.assertIn("AWWayofTime:rune", blocks)
        self.assertIn("AWWayofTime:masterStone", blocks)
    
    def test_conversion_stats(self):
        """Test generowania statystyk konwersji"""
        results = [
            self.converter.convert_block("AWWayofTime:Altar", 0),
            self.converter.convert_block("AWWayofTime:rune", 1),
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
    suite.addTests(loader.loadTestsFromTestCase(TestBlockstateProps))
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
