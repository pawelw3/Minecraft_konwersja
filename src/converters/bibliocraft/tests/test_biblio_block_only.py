"""Tests for BiblioCraft block-only converter."""

import pytest

from src.converters.bibliocraft.block_only_converter import convert_block_only


class TestBiblioCraftBlockOnly:
    def test_bell(self):
        result = convert_block_only(1300, "BiblioCraft:bell", 0, (0, 0, 0))
        assert result.success is True
        assert result.target_block == "minecraft:bell"
        assert result.confidence == "medium"
        assert any("redstone sound" in w for w in result.warnings)

    @pytest.mark.parametrize("meta,expected", [
        (0, "minecraft:oak_stairs"),
        (1, "minecraft:spruce_stairs"),
        (2, "minecraft:birch_stairs"),
        (3, "minecraft:jungle_stairs"),
        (4, "minecraft:acacia_stairs"),
        (5, "minecraft:dark_oak_stairs"),
    ])
    def test_seat_variants(self, meta, expected):
        result = convert_block_only(1301, "BiblioCraft:seat", meta, (0, 0, 0))
        assert result.success is True
        assert result.target_block == expected
        assert result.confidence == "medium"

    def test_seat_unknown_metadata_fallback(self):
        result = convert_block_only(1301, "BiblioCraft:seat", 15, (0, 0, 0))
        assert result.success is True
        assert result.target_block == "minecraft:oak_stairs"
        assert result.confidence == "low"
        assert any("Unknown" in w for w in result.warnings)

    def test_mapframe(self):
        result = convert_block_only(1302, "BiblioCraft:mapFrame", 0, (0, 0, 0))
        assert result.success is True
        assert result.target_block == "supplementaries:frame"
        assert result.confidence == "medium"

    def test_unknown_registry(self):
        result = convert_block_only(9999, "BiblioCraft:unknown", 0, (0, 0, 0))
        assert result.success is False
        assert result.errors
