"""Tests for AE2 block-only converter."""

import pytest

from src.converters.ae2.block_only_converter import convert_block_only


class TestAE2BlockOnly:
    @pytest.mark.parametrize("reg,expected", [
        ("appliedenergistics2:tile.BlockQuartz", "ae2:quartz_block"),
        ("appliedenergistics2:tile.BlockQuartzChiseled", "ae2:quartz_block"),
        ("appliedenergistics2:tile.BlockQuartzGlass", "ae2:quartz_glass"),
        ("appliedenergistics2:tile.BlockFluix", "ae2:fluix_block"),
        ("appliedenergistics2:tile.BlockSkyStone", "ae2:sky_stone_block"),
        ("appliedenergistics2:tile.BlockTinyTNT", "ae2:tiny_tnt"),
        ("appliedenergistics2:tile.BlockQuartzTorch", "ae2:quartz_fixture"),
        ("appliedenergistics2:tile.BlockLightDetector", "ae2:light_detector"),
        ("appliedenergistics2:tile.BlockMatrixFrame", "ae2:matrix_frame"),
    ])
    def test_direct_blocks(self, reg, expected):
        result = convert_block_only(1000, reg, 0, (0, 0, 0))
        assert result.success is True
        assert result.target_block == expected

    @pytest.mark.parametrize("reg,expected", [
        ("appliedenergistics2:tile.ChiseledQuartzStairs", "ae2:chiseled_quartz_stairs"),
        ("appliedenergistics2:tile.SkyStoneStairs", "ae2:sky_stone_stairs"),
        ("appliedenergistics2:tile.SkyStoneBrickStairs", "ae2:sky_stone_brick_stairs"),
        ("appliedenergistics2:tile.SkyStoneSmallBrickStairs", "ae2:sky_stone_small_brick_stairs"),
        ("appliedenergistics2:tile.QuartzStairs", "ae2:quartz_stairs"),
        ("appliedenergistics2:tile.SkyStoneBlockStairs", "ae2:sky_stone_block_stairs"),
        ("appliedenergistics2:tile.QuartzPillarStairs", "ae2:quartz_pillar_stairs"),
        ("appliedenergistics2:tile.FluixStairs", "ae2:fluix_stairs"),
    ])
    def test_stairs(self, reg, expected):
        result = convert_block_only(1001, reg, 3, (0, 0, 0))
        assert result.success is True
        assert result.target_block == expected
        assert result.blockstate_props.get("legacy_meta") == "3"

    @pytest.mark.parametrize("meta,axis", [
        (0, "y"),
        (1, "x"),
        (2, "z"),
    ])
    def test_quartz_pillar_axis(self, meta, axis):
        result = convert_block_only(1002, "appliedenergistics2:tile.BlockQuartzPillar", meta, (0, 0, 0))
        assert result.success is True
        assert result.target_block == "ae2:quartz_pillar"
        assert result.blockstate_props.get("axis") == axis

    @pytest.mark.parametrize("meta,expected", [
        (0, "ae2:sky_stone_block"),
        (1, "ae2:smooth_sky_stone_block"),
        (2, "ae2:sky_stone_brick"),
        (3, "ae2:sky_stone_small_brick"),
    ])
    def test_sky_stone_variants(self, meta, expected):
        result = convert_block_only(1003, "appliedenergistics2:tile.BlockSkyStone", meta, (0, 0, 0))
        assert result.success is True
        assert result.target_block == expected

    def test_sky_stone_unknown_metadata(self):
        result = convert_block_only(1003, "appliedenergistics2:tile.BlockSkyStone", 15, (0, 0, 0))
        assert result.success is True
        assert result.target_block == "ae2:sky_stone_block"
        assert result.confidence == "low"

    def test_ore_surface(self):
        result = convert_block_only(1004, "appliedenergistics2:tile.OreQuartz", 0, (10, 64, 10))
        assert result.success is True
        assert result.target_block == "ae2:quartz_ore"

    def test_ore_deepslate(self):
        result = convert_block_only(1004, "appliedenergistics2:tile.OreQuartz", 0, (10, -10, 10))
        assert result.success is True
        assert result.target_block == "ae2:deepslate_quartz_ore"

    def test_unknown_registry(self):
        result = convert_block_only(9999, "appliedenergistics2:tile.Unknown", 0, (0, 0, 0))
        assert result.success is False
        assert result.errors
