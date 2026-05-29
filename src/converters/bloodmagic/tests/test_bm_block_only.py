"""Tests for Blood Magic block-only converter."""

import pytest

from src.converters.bloodmagic.block_only_converter import convert_block_only


class TestBloodMagicBlockOnly:
    @pytest.mark.parametrize("meta,expected", [
        (0, "bloodmagic:blank_rune"),
        (1, "bloodmagic:dislocation_rune"),
        (2, "bloodmagic:capacity_rune"),
        (3, "bloodmagic:better_capacity_rune"),
        (4, "bloodmagic:orb_rune"),
        (5, "bloodmagic:acceleration_rune"),
    ])
    def test_blood_rune_variants(self, meta, expected):
        result = convert_block_only(1400, "AWWayofTime:bloodRune", meta, (0, 0, 0))
        assert result.success is True
        assert result.target_block == expected
        assert result.confidence == "high"

    def test_blood_rune_unknown_metadata(self):
        result = convert_block_only(1400, "AWWayofTime:bloodRune", 15, (0, 0, 0))
        assert result.success is True
        assert result.target_block == "bloodmagic:blank_rune"
        assert result.confidence == "low"
        assert any("Unknown BloodRune metadata" in w for w in result.warnings)

    @pytest.mark.parametrize("reg,expected", [
        ("AWWayofTime:speedRune", "bloodmagic:speed_rune"),
        ("AWWayofTime:efficiencyRune", "bloodmagic:efficiency_rune"),
        ("AWWayofTime:runeOfSacrifice", "bloodmagic:sacrifice_rune"),
        ("AWWayofTime:runeOfSelfSacrifice", "bloodmagic:self_sacrifice_rune"),
    ])
    def test_separate_runes(self, reg, expected):
        result = convert_block_only(1401, reg, 0, (0, 0, 0))
        assert result.success is True
        assert result.target_block == expected
        assert result.confidence == "high"

    @pytest.mark.parametrize("meta,expected", [
        (0, "bloodmagic:ritual_stone"),
        (1, "bloodmagic:fire_ritual_stone"),
        (2, "bloodmagic:water_ritual_stone"),
        (3, "bloodmagic:earth_ritual_stone"),
        (4, "bloodmagic:air_ritual_stone"),
        (5, "bloodmagic:dusk_ritual_stone"),
    ])
    def test_ritual_stone_variants(self, meta, expected):
        result = convert_block_only(1402, "AWWayofTime:ritualStone", meta, (0, 0, 0))
        assert result.success is True
        assert result.target_block == expected

    def test_ritual_stone_unknown_metadata(self):
        result = convert_block_only(1402, "AWWayofTime:ritualStone", 15, (0, 0, 0))
        assert result.success is True
        assert result.target_block == "bloodmagic:ritual_stone"
        assert result.confidence == "low"

    @pytest.mark.parametrize("reg,expected,confidence", [
        ("AWWayofTime:imperfectRitualStone", "bloodmagic:imperfect_ritual_stone", "high"),
        ("AWWayofTime:bloodStoneBrick", "bloodmagic:bloodstone_brick", "high"),
        ("AWWayofTime:largeBloodStoneBrick", "bloodmagic:large_bloodstone_brick", "high"),
        ("AWWayofTime:crystal", "minecraft:amethyst_block", "low"),
        ("AWWayofTime:enchantmentGlyph", "bloodmagic:blank_rune", "low"),
        ("AWWayofTime:stabilityGlyph", "bloodmagic:blank_rune", "low"),
        ("AWWayofTime:bloodLight", "minecraft:torch", "low"),
    ])
    def test_direct_blocks(self, reg, expected, confidence):
        result = convert_block_only(1403, reg, 0, (0, 0, 0))
        assert result.success is True
        assert result.target_block == expected
        assert result.confidence == confidence

    def test_unknown_registry(self):
        result = convert_block_only(9999, "AWWayofTime:unknown", 0, (0, 0, 0))
        assert result.success is False
        assert result.errors
