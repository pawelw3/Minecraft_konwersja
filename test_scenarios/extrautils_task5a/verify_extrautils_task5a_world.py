#!/usr/bin/env python3
"""Verify that the Extra Utilities Task 5A source patch was written to a 1.7.10 world."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT))
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from minecraft_map_parser.anvil_parser import AnvilParser  # noqa: E402
from src.converters.mekanism.analyze_map_coverage import get_block_at  # noqa: E402


DEFAULT_WORLD = PROJECT_ROOT / "lightweigh_map_templates/1710_modded/extrautils_task5a_world"
DEFAULT_PATCH = Path(__file__).resolve().parent / "extrautils_task5a_source_patch_1710.json"


def load_chunk(world: Path, x: int, z: int):
    chunk_x = x >> 4
    chunk_z = z >> 4
    region_x = chunk_x >> 5
    region_z = chunk_z >> 5
    region_file = world / "region" / f"r.{region_x}.{region_z}.mca"
    parser = AnvilParser(str(region_file))
    return parser.get_chunk(chunk_x, chunk_z)


def find_te(chunk, x: int, y: int, z: int) -> dict[str, Any] | None:
    for te in chunk.get_tile_entities():
        if int(te.get("x", 0)) == x and int(te.get("y", 0)) == y and int(te.get("z", 0)) == z:
            return te
    return None


def expected_nested_keys(nbt: dict[str, Any]) -> list[str]:
    keys = []
    for key, value in nbt.items():
        if isinstance(value, (dict, list)):
            keys.append(key)
    return keys


def verify(world: Path, patch_path: Path) -> dict[str, Any]:
    patch = json.loads(patch_path.read_text(encoding="utf-8"))
    failures: list[str] = []
    checked_blocks = 0
    checked_tes = 0
    nested_te_keys = 0

    block_edits = {}
    te_edits = {}
    for edit in patch["edits"]:
        pos = (int(edit["x"]), int(edit["y"]), int(edit["z"]))
        if edit["op"] == "set_block":
            block_edits[pos] = edit
        elif edit["op"] == "set_te":
            te_edits[pos] = edit

    chunk_cache = {}
    for pos, edit in block_edits.items():
        x, y, z = pos
        chunk_key = (x >> 4, z >> 4)
        chunk = chunk_cache.get(chunk_key)
        if chunk is None:
            chunk = load_chunk(world, x, z)
            chunk_cache[chunk_key] = chunk
        if chunk is None:
            failures.append(f"Missing chunk for block at {pos}")
            continue
        block_id, meta = get_block_at(chunk, x, y, z)
        checked_blocks += 1
        if block_id != int(edit["id"]) or meta != int(edit.get("meta", 0)):
            failures.append(f"Block mismatch at {pos}: got {block_id}:{meta}, expected {edit['id']}:{edit.get('meta', 0)}")

    for pos, edit in te_edits.items():
        x, y, z = pos
        chunk_key = (x >> 4, z >> 4)
        chunk = chunk_cache.get(chunk_key)
        if chunk is None:
            chunk = load_chunk(world, x, z)
            chunk_cache[chunk_key] = chunk
        if chunk is None:
            failures.append(f"Missing chunk for TE at {pos}")
            continue
        te = find_te(chunk, x, y, z)
        checked_tes += 1
        if te is None:
            failures.append(f"Missing TE at {pos}")
            continue
        expected_nbt = edit["nbt"]
        if te.get("id") != expected_nbt.get("id"):
            failures.append(f"TE id mismatch at {pos}: got {te.get('id')}, expected {expected_nbt.get('id')}")
        for key in expected_nested_keys(expected_nbt):
            nested_te_keys += 1
            if key not in te:
                failures.append(f"Nested TE key missing at {pos}: {key}")

    return {
        "world": str(world),
        "patch": str(patch_path),
        "checked_blocks": checked_blocks,
        "checked_tile_entities": checked_tes,
        "checked_nested_te_keys": nested_te_keys,
        "failure_count": len(failures),
        "failures": failures,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--world", type=Path, default=DEFAULT_WORLD)
    parser.add_argument("--patch", type=Path, default=DEFAULT_PATCH)
    parser.add_argument("--report", type=Path, default=Path(__file__).resolve().parent / "extrautils_task5a_world_verify_report.json")
    args = parser.parse_args()

    report = verify(args.world, args.patch)
    args.report.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Checked blocks: {report['checked_blocks']}")
    print(f"Checked tile entities: {report['checked_tile_entities']}")
    print(f"Checked nested TE keys: {report['checked_nested_te_keys']}")
    print(f"Failures: {report['failure_count']}")
    print(f"Report: {args.report}")
    return 0 if report["failure_count"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
