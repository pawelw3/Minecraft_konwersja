"""Tests for Big Reactors block-only converter."""

import pytest

from src.converters.bigreactors.block_only_converter import convert_block_only
from src.converters.common.block_only import BlockOnlyResult


class TestBigReactorsBlockOnly:
    def test_yellorite_ore_surface(self):
        result = convert_block_only(1234, "bigreactors:YelloriteOre", 0, (100, 64, 200))
        assert result.success is True
        assert result.target_block == "biggerreactors:uranium_ore"
        assert result.confidence == "high"

    def test_yellorite_ore_deepslate(self):
        result = convert_block_only(1234, "bigreactors:YelloriteOre", 0, (100, -10, 200))
        assert result.success is True
        assert result.target_block == "biggerreactors:deepslate_uranium_ore"
        assert result.confidence == "high"

    @pytest.mark.parametrize("meta,expected", [
        (0, "biggerreactors:uranium_block"),
        (1, "biggerreactors:cyanite_block"),
        (2, "biggerreactors:graphite_block"),
        (3, "biggerreactors:blutonium_block"),
        (4, "biggerreactors:ludicrite_block"),
    ])
    def test_metal_block_variants(self, meta, expected):
        result = convert_block_only(1235, "bigreactors:BRMetalBlock", meta, (0, 0, 0))
        assert result.success is True
        assert result.target_block == expected
        assert result.confidence == "high"

    def test_metal_block_unknown_metadata_fallback(self):
        result = convert_block_only(1235, "bigreactors:BRMetalBlock", 15, (0, 0, 0))
        assert result.success is True
        assert result.target_block == "biggerreactors:graphite_block"
        assert result.confidence == "low"
        assert any("Unknown BRMetalBlock metadata" in w for w in result.warnings)

    def test_unknown_registry_fail(self):
        result = convert_block_only(9999, "bigreactors:UnknownBlock", 0, (0, 0, 0))
        assert result.success is False
        assert result.errors

    def test_no_nbt_returned(self):
        result = convert_block_only(1234, "bigreactors:YelloriteOre", 0, (0, 0, 0))
        assert result.blockstate_props == {}
