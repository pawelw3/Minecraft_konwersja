"""Tests for direct_terrain_writer block-only scanning pipeline."""

from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from converters.direct_terrain_writer import (
    scan_world_for_block_only,
    write_events_to_jsonl,
    _iter_blocks_in_chunk,
)


class FakeNBTTag:
    def __init__(self, value):
        self.value = value


class FakeChunkData:
    def __init__(self, x: int, z: int, sections: list[dict]):
        self.x = x
        self.z = z
        self._sections = sections

    def get_sections(self):
        return self._sections


def _make_section(y: int, blocks: list[int], data: list[int] | None = None, add: list[int] | None = None):
    sec = {"Y": FakeNBTTag(y), "Blocks": FakeNBTTag(blocks)}
    if data is not None:
        sec["Data"] = FakeNBTTag(data)
    if add is not None:
        sec["Add"] = FakeNBTTag(add)
    return sec


def test_iter_blocks_in_chunk_skips_air():
    chunk = FakeChunkData(0, 0, [
        _make_section(4, [0] * 4096),
    ])
    results = list(_iter_blocks_in_chunk(chunk, 0, 0))
    assert len(results) == 0


def test_iter_blocks_in_chunk_reads_single_block():
    blocks = [0] * 4096
    blocks[0] = 1  # stone at (0, 64, 0) in section Y=4
    chunk = FakeChunkData(0, 0, [
        _make_section(4, blocks),
    ])
    results = list(_iter_blocks_in_chunk(chunk, 0, 0))
    assert len(results) == 1
    x, y, z, nid, meta = results[0]
    assert (x, y, z) == (0, 64, 0)
    assert nid == 1
    assert meta == 0


def test_iter_blocks_in_chunk_with_add_array():
    blocks = [0] * 4096
    blocks[0] = 0xAB  # low byte
    add = [0] * 2048
    add[0] = 0x0C  # high nibble for block 0 -> full_id = 0xCAB = 3243
    chunk = FakeChunkData(0, 0, [
        _make_section(4, blocks, add=add),
    ])
    results = list(_iter_blocks_in_chunk(chunk, 0, 0))
    assert len(results) == 1
    assert results[0][3] == 0xCAB  # (12 << 8) | 171 = 3243


def test_iter_blocks_in_chunk_metadata():
    blocks = [0] * 4096
    blocks[0] = 5  # planks
    data = [0] * 2048
    data[0] = 0x23  # meta 3 for block 0 (lower nibble), meta 2 for block 1
    chunk = FakeChunkData(0, 0, [
        _make_section(4, blocks, data=data),
    ])
    results = list(_iter_blocks_in_chunk(chunk, 0, 0))
    assert len(results) == 1
    assert results[0][3] == 5
    assert results[0][4] == 3  # lower nibble


@patch("converters.direct_terrain_writer.load_item_id_mapping")
@patch("converters.direct_terrain_writer.AnvilParser")
def test_scan_world_routes_mod_blocks(mock_parser_cls, mock_load_mapping, tmp_path):
    """End-to-end: one chunk with a mod block -> set_block event."""
    mock_load_mapping.return_value = {"999": "chisel:andesite"}

    blocks = [0] * 4096
    blocks[0] = 0xE7  # 231 low byte
    add = [0] * 2048
    add[0] = 0x03  # high nibble for block 0 -> (3 << 8) | 231 = 999
    chunk = FakeChunkData(0, 0, [
        _make_section(4, blocks, add=add),
    ])

    mock_parser = MagicMock()
    mock_parser.get_all_chunks.return_value = [chunk]
    mock_parser_cls.return_value = mock_parser

    # Create a fake region file so _iter_regions finds it
    region_dir = tmp_path / "region"
    region_dir.mkdir()
    (region_dir / "r.0.0.mca").write_text("fake")

    events = list(scan_world_for_block_only(
        str(tmp_path),
        str(tmp_path / "level.dat"),
        region_filter=[(0, 0)],
    ))

    set_blocks = [e for e in events if e.get("op") == "set_block"]
    audits = [e for e in events if e.get("op") == "audit_warn"]

    assert len(set_blocks) == 1
    assert set_blocks[0]["block"] == "rechiseled:andesite_1"
    assert set_blocks[0]["pos"] == [0, 64, 0]
    assert len(audits) == 0


@patch("converters.direct_terrain_writer.load_item_id_mapping")
@patch("converters.direct_terrain_writer.AnvilParser")
def test_scan_world_skips_vanilla(mock_parser_cls, mock_load_mapping, tmp_path):
    """Vanilla blocks are skipped when skip_vanilla_by_registry=True."""
    mock_load_mapping.return_value = {"1": "minecraft:stone"}

    blocks = [0] * 4096
    blocks[0] = 1  # stone
    chunk = FakeChunkData(0, 0, [
        _make_section(4, blocks),
    ])

    mock_parser = MagicMock()
    mock_parser.get_all_chunks.return_value = [chunk]
    mock_parser_cls.return_value = mock_parser

    region_dir = tmp_path / "region"
    region_dir.mkdir()
    (region_dir / "r.0.0.mca").write_text("fake")

    events = list(scan_world_for_block_only(
        str(tmp_path),
        str(tmp_path / "level.dat"),
        region_filter=[(0, 0)],
    ))

    assert len(events) == 0


@patch("converters.direct_terrain_writer.load_item_id_mapping")
@patch("converters.direct_terrain_writer.AnvilParser")
def test_scan_world_unknown_mod_fallback(mock_parser_cls, mock_load_mapping, tmp_path):
    """Unknown mod blocks fall back to stone with a warning (never air)."""
    mock_load_mapping.return_value = {"999": "SomeMod:unknown_block"}

    blocks = [0] * 4096
    add = [0] * 2048
    add[0] = 0x03
    blocks[0] = 0xE7  # full_id = 999
    chunk = FakeChunkData(0, 0, [
        _make_section(4, blocks, add=add),
    ])

    mock_parser = MagicMock()
    mock_parser.get_all_chunks.return_value = [chunk]
    mock_parser_cls.return_value = mock_parser

    region_dir = tmp_path / "region"
    region_dir.mkdir()
    (region_dir / "r.0.0.mca").write_text("fake")

    events = list(scan_world_for_block_only(
        str(tmp_path),
        str(tmp_path / "level.dat"),
        region_filter=[(0, 0)],
    ))

    set_blocks = [e for e in events if e.get("op") == "set_block"]
    audits = [e for e in events if e.get("op") == "audit_warn"]

    assert len(set_blocks) == 1
    assert set_blocks[0]["block"] == "minecraft:stone"
    assert "BO-W-UNKNOWN-MOD-BLOCK" in str(set_blocks[0].get("warnings", []))
    assert len(audits) == 0  # fallback is explicit, not an audit failure


def test_write_events_to_jsonl(tmp_path):
    events = [
        {"op": "set_block", "pos": [0, 64, 0], "block": "minecraft:stone"},
        {"op": "audit_warn", "pos": [1, 64, 0], "reason": "test"},
    ]
    out = tmp_path / "events.jsonl"
    write_events_to_jsonl(iter(events), str(out))

    lines = out.read_text(encoding="utf-8").strip().split("\n")
    assert len(lines) == 2
    assert json.loads(lines[0])["block"] == "minecraft:stone"
    assert json.loads(lines[1])["op"] == "audit_warn"
