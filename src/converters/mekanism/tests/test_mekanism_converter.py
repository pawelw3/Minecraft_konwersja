import unittest

from src.converters.mekanism import MekanismConverter, get_block_mapping, get_mapping_for_te_id


class TestMekanismMappings(unittest.TestCase):
    def test_machine_block_mapping(self):
        mapping = get_block_mapping("Mekanism:MachineBlock", 0)
        self.assertIsNotNone(mapping)
        self.assertEqual(mapping.target_block_id, "mekanism:enrichment_chamber")
        self.assertTrue(mapping.has_block_entity)

    def test_factory_mapping_uses_recipe_type(self):
        mapping = get_block_mapping("Mekanism:MachineBlock", 7, {"recipeType": 2})
        self.assertIsNotNone(mapping)
        self.assertEqual(mapping.target_block_id, "mekanism:elite_crushing_factory")
        self.assertEqual(mapping.nbt_converter, "factory")

    def test_te_id_without_namespace_resolves(self):
        mapping = get_mapping_for_te_id("UltimateSmeltingFactory", nbt={"recipeType": 0})
        self.assertIsNotNone(mapping)
        self.assertEqual(mapping.target_block_id, "mekanism:elite_smelting_factory")

    def test_copper_goes_to_vanilla_with_note(self):
        mapping = get_block_mapping("Mekanism:OreBlock", 1)
        self.assertEqual(mapping.target_block_id, "minecraft:copper_ore")
        self.assertIn("vanilla", mapping.notes)

    def test_map_coverage_gap_blocks_are_mapped(self):
        expected = {
            ("Mekanism:BoundingBlock", 0): "mekanism:bounding_block",
            ("Mekanism:BoundingBlock", 1): "mekanism:bounding_block",
            ("Mekanism:ObsidianTNT", 0): "minecraft:tnt",
            ("Mekanism:PlasticBlock", 7): "minecraft:light_gray_concrete",
            ("Mekanism:PlasticBlock", 8): "minecraft:gray_concrete",
            ("Mekanism:PlasticBlock", 12): "minecraft:light_blue_concrete",
            ("Mekanism:PlasticBlock", 15): "minecraft:white_concrete",
            ("Mekanism:RoadPlasticBlock", 3): "minecraft:brown_concrete",
            ("Mekanism:SaltBlock", 0): "mekanism:block_salt",
            ("Mekanism:SlickPlasticBlock", 8): "minecraft:gray_concrete",
            ("Mekanism:SlickPlasticBlock", 15): "minecraft:white_concrete",
            ("Mekanism:GlowPlasticBlock", 14): "minecraft:orange_concrete",
            ("Mekanism:ReinforcedPlasticBlock", 2): "minecraft:green_concrete",
            ("Mekanism:PlasticFence", 4): "minecraft:oak_fence",
            ("Mekanism:CardboardBox", 0): "mekanism:cardboard_box",
            ("Mekanism:MachineBlock3", 2): "mekanism:chemical_oxidizer",
            ("Mekanism:BasicBlock2", 4): "mekanism:basic_induction_provider",
        }
        for (block_id, metadata), target_id in expected.items():
            with self.subTest(block_id=block_id, metadata=metadata):
                mapping = get_block_mapping(block_id, metadata)
                self.assertIsNotNone(mapping)
                self.assertEqual(mapping.target_block_id, target_id)


class TestMekanismConverter(unittest.TestCase):
    def setUp(self):
        self.converter = MekanismConverter()

    def test_basic_machine_conversion(self):
        result = self.converter.convert_block(
            "Mekanism:MachineBlock",
            metadata=0,
            nbt_1710={
                "id": "EnrichmentChamber",
                "x": 1,
                "y": 64,
                "z": 2,
                "facing": 3,
                "electricityStored": 1200.0,
                "operatingTicks": 42,
                "Items": [{"Slot": 0, "id": "Mekanism:OsmiumDust", "Count": 1}],
            },
            position=(1, 64, 2),
        )
        self.assertTrue(result.converted.success)
        self.assertEqual(result.converted.block_id_1182, "mekanism:enrichment_chamber")
        self.assertEqual(result.converted.blockstate_props, {"facing": "south"})
        self.assertEqual(result.converted.nbt_1182["id"], "mekanism:enrichment_chamber")
        self.assertEqual(result.converted.nbt_1182["Items"][0]["id"], "mekanism:dust_osmium")
        self.assertIn("energyContainers", result.converted.nbt_1182)

    def test_factory_conversion_preserves_progress(self):
        result = self.converter.convert_block(
            "Mekanism:MachineBlock",
            metadata=7,
            nbt_1710={
                "id": "UltimateSmeltingFactory",
                "recipeType": 1,
                "recipeTicks": 12,
                "progress0": 199,
                "progress1": 5,
                "electricityStored": 500.0,
            },
        )
        self.assertTrue(result.converted.success)
        self.assertEqual(result.converted.block_id_1182, "mekanism:elite_enriching_factory")
        self.assertEqual(result.converted.nbt_1182["factoryTier"], "elite")
        self.assertEqual(result.converted.nbt_1182["factoryRecipe"], "enriching")
        self.assertEqual(result.converted.nbt_1182["progress"]["progress0"], 199)

    def test_energy_cube_conversion(self):
        result = self.converter.convert_block(
            "Mekanism:EnergyCube",
            metadata=1,
            nbt_1710={"id": "EnergyCube", "tier": "advanced", "electricityStored": 4_000_000.0},
        )
        self.assertTrue(result.converted.success)
        self.assertEqual(result.converted.block_id_1182, "mekanism:advanced_energy_cube")
        self.assertEqual(result.converted.nbt_1182["tier"], "advanced")
        self.assertEqual(result.converted.nbt_1182["energyContainers"][0]["stored"], "4000000.0")

    def test_gas_tank_to_chemical_tank(self):
        result = self.converter.convert_block(
            "Mekanism:GasTank",
            metadata=0,
            nbt_1710={
                "id": "GasTank",
                "tier": 0,
                "dumping": 2,
                "gasTank": {"stored": {"gasName": "gas:hydrogen_chloride", "amount": 32000}},
            },
        )
        self.assertTrue(result.converted.success)
        self.assertEqual(result.converted.block_id_1182, "mekanism:basic_chemical_tank")
        self.assertEqual(result.converted.nbt_1182["chemicalTank"]["stored"]["chemical"], "mekanism:hydrogen_chloride")
        self.assertEqual(result.converted.nbt_1182["dumping"], 2)

    def test_digital_miner_resets_running_cache(self):
        result = self.converter.convert_block(
            "Mekanism:MachineBlock",
            metadata=4,
            nbt_1710={
                "id": "DigitalMiner",
                "radius": 10,
                "minY": 0,
                "maxY": 60,
                "running": True,
                "silkTouch": True,
                "inverse": False,
                "filters": [{"type": "tag", "value": "forge:ores/osmium"}],
                "oresToMine": {"legacy": "cache"},
            },
        )
        self.assertTrue(result.converted.success)
        self.assertEqual(result.converted.block_id_1182, "mekanism:digital_miner")
        self.assertFalse(result.converted.nbt_1182["running"])
        self.assertNotIn("oresToMine", result.converted.nbt_1182)
        self.assertTrue(any("DIGITAL-MINER-RUNNING" in w for w in result.converted.warnings))

    def test_frequency_owner_warning(self):
        result = self.converter.convert_block(
            "Mekanism:MachineBlock",
            metadata=11,
            nbt_1710={"id": "MekanismTeleporter", "frequency": "Baza", "owner": "pawel"},
        )
        self.assertTrue(result.converted.success)
        self.assertEqual(result.converted.nbt_1182["frequency"], {"name": "Baza"})
        self.assertEqual(result.converted.nbt_1182["ownerNameLegacy"], "pawel")
        self.assertTrue(any("OWNER-UUID-MISSING" in w for w in result.converted.warnings))

    def test_event_shape(self):
        result = self.converter.convert_block("Mekanism:OreBlock", metadata=0, position=(5, 70, -2))
        event = result.converted.event.to_dict()
        self.assertEqual(event["mod"], "mekanism")
        self.assertEqual(event["source"]["position"], (5, 70, -2))
        self.assertEqual(event["target"]["block_id"], "mekanism:osmium_ore")

    def test_unknown_block_fails(self):
        result = self.converter.convert_block("Other:Block", metadata=0)
        self.assertFalse(result.converted.success)
        self.assertTrue(result.converted.errors)

    def test_non_block_entity_target_drops_legacy_nbt(self):
        result = self.converter.convert_block(
            "Mekanism:ObsidianTNT",
            metadata=0,
            nbt_1710={"id": "ObsidianTNT", "x": 1, "y": 2, "z": 3},
        )
        self.assertTrue(result.converted.success)
        self.assertEqual(result.converted.block_id_1182, "minecraft:tnt")
        self.assertIsNone(result.converted.nbt_1182)


if __name__ == "__main__":
    unittest.main()
