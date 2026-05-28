#!/usr/bin/env python3
"""Convert the applied Extra Utilities Task 5A 1.7.10 test world into a 1.18.2 patch.

This script reads the actual `.mca` data from the small test world copy,
not the synthetic in-memory samples from the generator. It verifies that the
batch conversion path sees the same data that was written by the worker.
"""

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
from converters.extrautils.extrautils_converter import ExtraUtilsConverter  # noqa: E402
from src.converters.mekanism.analyze_map_coverage import get_block_at, nbt_to_python  # noqa: E402


SCENARIO_DIR = Path(__file__).resolve().parent
DEFAULT_WORLD = PROJECT_ROOT / "lightweigh_map_templates/1710_modded/extrautils_task5a_world"
DEFAULT_SOURCE_PATCH = SCENARIO_DIR / "extrautils_task5a_source_patch_1710.json"
DEFAULT_EXPECTED_PATCH = SCENARIO_DIR / "extrautils_task5a_converted_patch_1182.json"
DEFAULT_OUTPUT_PATCH = SCENARIO_DIR / "extrautils_task5a_realworld_converted_patch_1182.json"
DEFAULT_REPORT = SCENARIO_DIR / "extrautils_task5a_realworld_conversion_report.json"


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, data: dict[str, Any]) -> None:
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


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
        te_data = nbt_to_python(te)
        if int(te_data.get("x", 0)) == x and int(te_data.get("y", 0)) == y and int(te_data.get("z", 0)) == z:
            return te_data
    return None


def split_source_edits(source_patch: dict[str, Any]) -> tuple[list[dict[str, Any]], dict[tuple[int, int, int], dict[str, Any]]]:
    blocks: list[dict[str, Any]] = []
    tile_entities: dict[tuple[int, int, int], dict[str, Any]] = {}
    for edit in source_patch.get("edits", []):
        pos = (int(edit["x"]), int(edit["y"]), int(edit["z"]))
        if edit.get("op") == "set_block":
            blocks.append(edit)
        elif edit.get("op") == "set_te":
            tile_entities[pos] = edit
    return blocks, tile_entities


def normalize_patch(patch: dict[str, Any]) -> list[dict[str, Any]]:
    normalized: list[dict[str, Any]] = []
    for edit in patch.get("edits", []):
        item = {
            "op": edit.get("op"),
            "x": edit.get("x"),
            "y": edit.get("y"),
            "z": edit.get("z"),
        }
        if edit.get("op") == "set_block":
            item["block_id"] = edit.get("block_id")
            item["properties"] = edit.get("properties") or {}
        elif edit.get("op") == "set_te":
            item["nbt"] = edit.get("nbt") or {}
        normalized.append(item)
    return sorted(normalized, key=lambda e: (e["x"], e["y"], e["z"], e["op"]))


def compare_patches(actual: dict[str, Any], expected: dict[str, Any]) -> list[str]:
    actual_norm = normalize_patch(actual)
    expected_norm = normalize_patch(expected)
    failures: list[str] = []
    if len(actual_norm) != len(expected_norm):
        failures.append(f"Edit count mismatch: actual {len(actual_norm)}, expected {len(expected_norm)}")
    for index, (actual_edit, expected_edit) in enumerate(zip(actual_norm, expected_norm)):
        if actual_edit != expected_edit:
            failures.append(
                "Edit mismatch at normalized index "
                f"{index}: actual={json.dumps(actual_edit, sort_keys=True)}, "
                f"expected={json.dumps(expected_edit, sort_keys=True)}"
            )
    return failures


def convert_world(world: Path, source_patch_path: Path, expected_patch_path: Path | None) -> tuple[dict[str, Any], dict[str, Any]]:
    source_patch = load_json(source_patch_path)
    expected_patch = load_json(expected_patch_path) if expected_patch_path and expected_patch_path.exists() else None
    source_blocks, expected_tes = split_source_edits(source_patch)

    converter = ExtraUtilsConverter()
    chunk_cache: dict[tuple[int, int], Any] = {}
    target_edits: list[dict[str, Any]] = []
    sample_results: list[dict[str, Any]] = []
    read_failures: list[str] = []

    for edit in source_blocks:
        x, y, z = int(edit["x"]), int(edit["y"]), int(edit["z"])
        chunk_key = (x >> 4, z >> 4)
        chunk = chunk_cache.get(chunk_key)
        if chunk is None:
            chunk = load_chunk(world, x, z)
            chunk_cache[chunk_key] = chunk
        if chunk is None:
            read_failures.append(f"Missing chunk for {edit.get('label', '?')} at {(x, y, z)}")
            continue

        block_id, metadata = get_block_at(chunk, x, y, z)
        if block_id != int(edit["id"]) or metadata != int(edit.get("meta", 0)):
            read_failures.append(
                f"Source block mismatch for {edit.get('label', '?')} at {(x, y, z)}: "
                f"got {block_id}:{metadata}, expected {edit['id']}:{edit.get('meta', 0)}"
            )
            continue

        pos = (x, y, z)
        expected_te = expected_tes.get(pos)
        nbt = find_te(chunk, x, y, z) if expected_te else None
        if expected_te and nbt is None:
            read_failures.append(f"Missing source TE for {edit.get('label', '?')} at {pos}")
            continue

        registry_name = str(edit["registry_name"])
        result = converter.convert_block(registry_name, metadata, nbt, pos)
        sample_results.append(
            {
                "label": edit.get("label"),
                "source": {
                    "numeric_id": block_id,
                    "registry_name": registry_name,
                    "metadata": metadata,
                    "position": [x, y, z],
                    "te_id": nbt.get("id") if nbt else None,
                },
                "target": {
                    "block_id": result.block_id_1182,
                    "has_nbt": result.nbt_1182 is not None,
                },
                "success": result.success,
                "warnings": result.warnings,
                "errors": result.errors,
            }
        )
        if not result.success or not result.block_id_1182:
            continue
        target_edits.append(
            {
                "op": "set_block",
                "x": x,
                "y": y,
                "z": z,
                "block_id": result.block_id_1182,
                "properties": result.blockstate_props,
                "label": edit.get("label"),
            }
        )
        if result.nbt_1182 is not None:
            target_edits.append(
                {
                    "op": "set_te",
                    "x": x,
                    "y": y,
                    "z": z,
                    "nbt": result.nbt_1182,
                    "label": edit.get("label"),
                }
            )

    target_patch = {
        "format_version": "1.18.2",
        "metadata": {
            "name": "extrautils_task5a_realworld_converted",
            "generated_by": "convert_extrautils_task5a.py",
            "source_world": str(world.relative_to(PROJECT_ROOT) if world.is_relative_to(PROJECT_ROOT) else world),
            "source_patch": str(source_patch_path.relative_to(PROJECT_ROOT) if source_patch_path.is_relative_to(PROJECT_ROOT) else source_patch_path),
        },
        "edits": target_edits,
    }
    patch_mismatches = compare_patches(target_patch, expected_patch) if expected_patch else []
    report = {
        "name": "Extra Utilities Task 5A real-world conversion report",
        "source_world": str(world),
        "source_patch": str(source_patch_path),
        "expected_patch": str(expected_patch_path) if expected_patch_path else None,
        "checked_blocks": len(source_blocks),
        "converted_samples": len(sample_results),
        "target_edits": len(target_edits),
        "read_failure_count": len(read_failures),
        "patch_mismatch_count": len(patch_mismatches),
        "failure_count": len(read_failures) + len(patch_mismatches) + sum(1 for item in sample_results if not item["success"]),
        "read_failures": read_failures,
        "patch_mismatches": patch_mismatches,
        "samples": sample_results,
    }
    return target_patch, report


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--world", type=Path, default=DEFAULT_WORLD)
    parser.add_argument("--source-patch", type=Path, default=DEFAULT_SOURCE_PATCH)
    parser.add_argument("--expected-patch", type=Path, default=DEFAULT_EXPECTED_PATCH)
    parser.add_argument("--out-patch", type=Path, default=DEFAULT_OUTPUT_PATCH)
    parser.add_argument("--report", type=Path, default=DEFAULT_REPORT)
    args = parser.parse_args()

    target_patch, report = convert_world(args.world, args.source_patch, args.expected_patch)
    write_json(args.out_patch, target_patch)
    write_json(args.report, report)
    print(f"Checked blocks: {report['checked_blocks']}")
    print(f"Converted samples: {report['converted_samples']}")
    print(f"Target edits: {report['target_edits']}")
    print(f"Read failures: {report['read_failure_count']}")
    print(f"Patch mismatches: {report['patch_mismatch_count']}")
    print(f"Failures: {report['failure_count']}")
    print(f"Patch: {args.out_patch}")
    print(f"Report: {args.report}")
    return 0 if report["failure_count"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
