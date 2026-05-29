"""Tests for BuildCraft block-only converter."""

import pytest

from src.converters.buildcraft.block_only_converter import convert_block_only


class TestBuildCraftBlockOnly:
    def test_block_frame(self):
        result = convert_block_only(1200, "BuildCraft|Builders:blockFrame", 0, (0, 0, 0))
        assert result.success is True
        assert result.target_block == "minecraft:iron_bars"
        assert result.confidence == "low"
        assert any("Frame" in w for w in result.warnings)

    def test_block_spring(self):
        result = convert_block_only(1201, "BuildCraft|Core:spring", 0, (0, 0, 0))
        assert result.success is True
        assert result.target_block == "minecraft:water"
        assert result.confidence == "low"

    def test_block_build_tool(self):
        result = convert_block_only(1202, "BuildCraft|Core:blockBuildTool", 0, (0, 0, 0))
        assert result.success is True
        assert result.target_block == "minecraft:air"
        assert result.confidence == "high"
        assert result.warnings == []

    def test_block_plain_pipe(self):
        result = convert_block_only(1203, "BuildCraft|Factory:blockPlainPipe", 0, (0, 0, 0))
        assert result.success is True
        assert result.target_block == "minecraft:iron_bars"
        assert result.confidence == "low"

    def test_unknown_registry(self):
        result = convert_block_only(9999, "BuildCraft|Factory:unknown", 0, (0, 0, 0))
        assert result.success is False
        assert result.errors
