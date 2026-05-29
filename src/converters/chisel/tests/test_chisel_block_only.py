"""Tests for Chisel block-only converter."""

import pytest

from src.converters.chisel.block_only_converter import convert_block_only


class TestChiselBlockOnly:
    @pytest.mark.parametrize("reg,meta,expected_prefix", [
        ("chisel:andesite", 0, "rechiseled:andesite_1"),
        ("chisel:andesite", 5, "rechiseled:andesite_6"),
        ("chisel:basalt", 0, "rechiseled:basalt_1"),
        ("chisel:granite", 3, "rechiseled:granite_4"),
        ("chisel:diorite", 7, "rechiseled:diorite_8"),
        ("chisel:cobblestone", 2, "rechiseled:cobblestone_3"),
        ("chisel:stonebrick", 1, "rechiseled:stone_bricks_2"),
        ("chisel:sandstone", 4, "rechiseled:sandstone_5"),
        ("chisel:endstone", 0, "rechiseled:end_stone_1"),
        ("chisel:obsidian", 3, "rechiseled:obsidian_4"),
        ("chisel:dirt", 0, "rechiseled:dirt_1"),
        ("chisel:ice", 2, "rechiseled:ice_3"),
        ("chisel:iron", 0, "rechiseled:iron_block_1"),
        ("chisel:gold", 1, "rechiseled:gold_block_2"),
        ("chisel:diamond", 0, "rechiseled:diamond_block_1"),
        ("chisel:oak", 0, "rechiseled:oak_1"),
        ("chisel:spruce", 0, "rechiseled:spruce_1"),
    ])
    def test_known_families(self, reg, meta, expected_prefix):
        result = convert_block_only(1500, reg, meta, (0, 0, 0))
        assert result.success is True
        assert result.target_block == expected_prefix
        assert result.confidence in ("high", "medium")
        assert any("visual verification" in w for w in result.warnings)

    def test_auto_chisel_has_te(self):
        result = convert_block_only(1501, "chisel:autoChisel", 0, (0, 0, 0))
        assert result.success is False
        assert any("TileEntity" in e for e in result.errors)

    def test_present_has_te(self):
        result = convert_block_only(1502, "chisel:present", 0, (0, 0, 0))
        assert result.success is False
        assert any("TileEntity" in e for e in result.errors)

    def test_unknown_family_glass_fallback(self):
        result = convert_block_only(1503, "chisel:some_glass", 0, (0, 0, 0))
        assert result.success is True
        assert result.target_block == "minecraft:glass"
        assert result.confidence == "low"

    def test_unknown_family_metal_fallback(self):
        result = convert_block_only(1504, "chisel:custom_metal", 0, (0, 0, 0))
        assert result.success is True
        assert result.target_block == "minecraft:iron_block"
        assert result.confidence == "low"

    def test_unknown_family_stone_fallback(self):
        result = convert_block_only(1505, "chisel:weird_stone", 0, (0, 0, 0))
        assert result.success is True
        assert result.target_block == "minecraft:stone"
        assert result.confidence == "low"

    def test_unknown_family_global_fallback(self):
        result = convert_block_only(1506, "chisel:abc_xyz", 0, (0, 0, 0))
        assert result.success is True
        assert result.target_block == "minecraft:stone"
        assert result.confidence == "low"

    def test_no_air_fallback(self):
        result = convert_block_only(1507, "chisel:unknown", 0, (0, 0, 0))
        assert result.target_block != "minecraft:air"
