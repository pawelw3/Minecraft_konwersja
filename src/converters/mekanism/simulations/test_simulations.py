import unittest

from .common import ItemStack, Tier, Version
from .digital_miner import (
    BlockSample,
    DigitalMiner1710,
    DigitalMiner1182,
    MinerFilter,
    MinerFilterType,
    compare_digital_miner_scan,
)
from .factory_simulation import (
    FACTORY_PROCESSES_1182,
    FACTORY_PROCESSES_1710,
    Factory1710,
    FactoryLane,
    FactoryRecipeType,
    compare_factory_progress,
    factory_target_id,
)
from .ore_processing import IRON, OSMIUM, OreProcessingRun, ProcessingTier, compare_yield
from .storage_frequency import (
    DumpingMode,
    EnergyCube1710,
    Frequency1710,
    GasTank1710,
    compare_storage_roundtrip,
    gas_to_chemical_id,
)


class OreProcessingTests(unittest.TestCase):
    def test_yields_match_for_all_multipliers(self):
        for tier in ProcessingTier:
            with self.subTest(tier=tier):
                legacy, modern = compare_yield(OSMIUM, tier, ore_count=3)
                self.assertEqual(legacy.count, tier.value * 3)
                self.assertEqual(modern.count, tier.value * 3)

    def test_x5_records_chemical_steps(self):
        run = OreProcessingRun(Version.V1182, ProcessingTier.X5, IRON, ore_count=1)
        result = run.run()
        self.assertEqual(result, ItemStack("minecraft:iron_ingot", 5))
        self.assertEqual(run.events[0].step, "chemical_dissolution_chamber")
        self.assertEqual(run.events[1].step, "chemical_washer")
        self.assertEqual(run.events[2].step, "chemical_crystallizer")


class FactoryTests(unittest.TestCase):
    def test_lane_counts_are_source_derived(self):
        self.assertEqual(FACTORY_PROCESSES_1710[Tier.BASIC], 3)
        self.assertEqual(FACTORY_PROCESSES_1710[Tier.ADVANCED], 5)
        self.assertEqual(FACTORY_PROCESSES_1710[Tier.ELITE], 7)
        self.assertEqual(FACTORY_PROCESSES_1182[Tier.ULTIMATE], 9)

    def test_legacy_progress_finishes_after_200_ticks(self):
        legacy, modern = compare_factory_progress()
        self.assertEqual(legacy.lanes[0].output_stack, ItemStack("Mekanism:Ingot:1", 1))
        self.assertEqual(legacy.lanes[0].progress, 0)
        self.assertEqual(modern.target_block_id, "mekanism:elite_smelting_factory")

    def test_partial_progress_survives_conversion(self):
        legacy = Factory1710(
            Tier.BASIC,
            FactoryRecipeType.CRUSHING,
            [FactoryLane(ItemStack("Mekanism:OsmiumClump", 1), progress=123)],
            energy=100,
        )
        modern = legacy.to_1182()
        self.assertEqual(legacy.legacy_nbt_summary()["progress0"], 123)
        self.assertEqual(modern.lanes[0].progress, 123)

    def test_factory_target_id_uses_recipe_type_not_old_te_name(self):
        self.assertEqual(factory_target_id(Tier.ELITE, FactoryRecipeType.SMELTING), "mekanism:elite_smelting_factory")
        self.assertEqual(factory_target_id(Tier.BASIC, FactoryRecipeType.ENRICHING), "mekanism:basic_enriching_factory")


class StorageAndFrequencyTests(unittest.TestCase):
    def test_energy_cube_preserves_fill_ratio(self):
        converted = EnergyCube1710(Tier.BASIC, 1_000_000).to_1182(target_capacity=4_000_000)
        self.assertEqual(converted.block_id, "mekanism:basic_energy_cube")
        self.assertEqual(converted.energy, 2_000_000)

    def test_gas_tank_becomes_chemical_tank(self):
        converted = GasTank1710(Tier.ULTIMATE, "gas:sulfuric_acid", 100_000, DumpingMode.DUMPING_EXCESS).to_1182()
        self.assertEqual(converted.block_id, "mekanism:ultimate_chemical_tank")
        self.assertEqual(converted.chemical_tank.content_id, "mekanism:sulfuric_acid")
        self.assertEqual(converted.dumping, DumpingMode.DUMPING_EXCESS)

    def test_frequency_flags_missing_uuid(self):
        converted = Frequency1710("Teleporty", "pawel").to_1182()
        self.assertEqual(converted.owner_name_legacy, "pawel")
        self.assertIn("missing_owner_uuid", converted.warnings)

    def test_gas_aliases(self):
        self.assertEqual(gas_to_chemical_id("gas:hydrogen_chloride"), "mekanism:hydrogen_chloride")
        self.assertEqual(gas_to_chemical_id("Mekanism:SulfuricAcid"), "mekanism:sulfuric_acid")

    def test_smoke_roundtrip(self):
        cube, tank, freq = compare_storage_roundtrip()
        self.assertEqual(cube.block_id, "mekanism:advanced_energy_cube")
        self.assertEqual(tank.chemical_tank.fill_ratio, 0.5)
        self.assertFalse(freq.public)


class DigitalMinerTests(unittest.TestCase):
    def test_tag_filter_scan_survives_conversion(self):
        legacy_scan, modern_scan, modern = compare_digital_miner_scan()
        self.assertEqual(legacy_scan, modern_scan)
        self.assertEqual(legacy_scan[0].block_id, "mekanism:osmium_ore")
        self.assertFalse(modern.running)
        self.assertIn("running_reset_for_recalculation", modern.warnings)

    def test_inverse_mode_selects_non_matching_blocks_in_range(self):
        miner = DigitalMiner1710(
            radius=4,
            min_y=0,
            max_y=64,
            inverse=True,
            filters=[MinerFilter(MinerFilterType.MOD_ID, "minecraft")],
        )
        blocks = [
            BlockSample(0, 20, 0, "minecraft:stone"),
            BlockSample(0, 20, 0, "mekanism:osmium_ore"),
            BlockSample(5, 20, 0, "mekanism:tin_ore"),
        ]
        self.assertEqual(miner.scan(blocks), [blocks[1]])

    def test_1182_inverse_replacement_can_block_mining(self):
        miner = DigitalMiner1182(
            inverse=True,
            inverse_requires_replacement=True,
            inverse_replace_target=None,
            filters=[MinerFilter(MinerFilterType.ITEM_STACK, "minecraft:stone")],
        )
        block = BlockSample(0, 10, 0, "mekanism:osmium_ore")
        self.assertFalse(miner.can_mine(block))
        miner.inverse_replace_target = "minecraft:cobblestone"
        self.assertTrue(miner.can_mine(block))


if __name__ == "__main__":
    unittest.main()
