#!/usr/bin/env python3
"""Convert the materialized Railcraft Task 5A 1.7.10 test world to a 1.18.2 patch."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parents[2]
SCENARIO_DIR = Path(__file__).resolve().parent
DEFAULT_WORLD = PROJECT_ROOT / "lightweigh_map_templates" / "1710" / "railcraft_task5a_world"
SOURCE_PATCH = SCENARIO_DIR / "railcraft_task5a_source_patch_1710.json"
CONVERTED_PATCH = SCENARIO_DIR / "railcraft_task5a_converted_patch_1182.json"
CONVERSION_REPORT = SCENARIO_DIR / "railcraft_task5a_conversion_report.json"
REPORT_MD = SCENARIO_DIR / "RAILCRAFT_TASK5A_REPORT.md"

sys.path.insert(0, str(PROJECT_ROOT))
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from minecraft_map_parser.anvil_parser import AnvilParser  # noqa: E402
from src.converters.mekanism.analyze_map_coverage import get_block_at, nbt_to_python  # noqa: E402
from src.converters.railcraft.railcraft_converter import RailcraftConverter  # noqa: E402


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, data: dict[str, Any]) -> None:
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def load_chunk(world: Path, x: int, z: int):
    chunk_x = x >> 4
    chunk_z = z >> 4
    region_x = chunk_x >> 5
    region_z = chunk_z >> 5
    parser = AnvilParser(str(world / "region" / f"r.{region_x}.{region_z}.mca"))
    return parser.get_chunk(chunk_x, chunk_z)


def find_te(chunk, x: int, y: int, z: int) -> dict[str, Any] | None:
    for te in chunk.get_tile_entities():
        data = nbt_to_python(te)
        if int(data.get("x", 0)) == x and int(data.get("y", 0)) == y and int(data.get("z", 0)) == z:
            return data
    return None


def convert_world(world: Path, source_patch_path: Path) -> tuple[dict[str, Any], dict[str, Any]]:
    source_patch = load_json(source_patch_path)
    converter = RailcraftConverter()
    chunk_cache: dict[tuple[int, int], Any] = {}
    read_failures: list[str] = []
    target_edits: list[dict[str, Any]] = []
    sample_results: list[dict[str, Any]] = []

    # Pair block edits with TE edits by position
    edits_by_pos: dict[tuple[int, int, int], dict[str, Any]] = {}
    for edit in source_patch.get("edits", []):
        pos = (int(edit["x"]), int(edit["y"]), int(edit["z"]))
        if pos not in edits_by_pos:
            edits_by_pos[pos] = {"block": None, "te": None, "label": edit.get("label", "")}
        if edit.get("op") == "set_block":
            edits_by_pos[pos]["block"] = edit
        elif edit.get("op") == "set_te":
            edits_by_pos[pos]["te"] = edit

    for pos, data in sorted(edits_by_pos.items()):
        block_edit = data["block"]
        te_edit = data["te"]
        label = data["label"]
        if not block_edit:
            continue

        x, y, z = pos
        chunk_key = (x >> 4, z >> 4)
        chunk = chunk_cache.get(chunk_key)
        if chunk is None:
            chunk = load_chunk(world, x, z)
            chunk_cache[chunk_key] = chunk
        if chunk is None:
            read_failures.append(f"Missing chunk for {label} at {pos}")
            continue

        numeric_id, metadata = get_block_at(chunk, x, y, z)
        expected_id = int(block_edit["id"])
        expected_meta = int(block_edit.get("meta", 0))
        if numeric_id != expected_id or metadata != expected_meta:
            read_failures.append(
                f"Block mismatch for {label} at {pos}: got {numeric_id}:{metadata}, expected {expected_id}:{expected_meta}"
            )
            continue

        nbt = find_te(chunk, x, y, z) if te_edit else None
        if te_edit and nbt is None:
            read_failures.append(f"Missing TE for {label} at {pos}")
            continue

        registry_name = str(block_edit.get("registry_name", ""))
        # Railcraft registry uses "Railcraft:foo" but converter expects "railcraft.foo"
        normalized_name = registry_name.replace("Railcraft:", "railcraft.", 1).lower()
        # Convert using block_id string + metadata + nbt
        result = converter.convert_block(normalized_name, metadata, nbt, pos)
        converted = result.converted

        sample_results.append(
            {
                "label": label,
                "source": {
                    "numeric_id": numeric_id,
                    "registry_name": registry_name,
                    "metadata": metadata,
                    "position": [x, y, z],
                    "te_id": nbt.get("id") if nbt else None,
                },
                "target": {
                    "block_id": converted.block_id_1182,
                    "blockstate_props": converted.blockstate_props,
                    "has_nbt": converted.nbt_1182 is not None,
                },
                "success": converted.success,
                "warnings": converted.warnings,
                "errors": converted.errors,
            }
        )

        if not converted.success or not converted.block_id_1182:
            continue

        target_edits.append(
            {
                "op": "set_block",
                "x": x,
                "y": y,
                "z": z,
                "block_id": converted.block_id_1182,
                "properties": converted.blockstate_props or {},
                "label": label,
            }
        )
        if converted.nbt_1182:
            target_edits.append(
                {
                    "op": "set_te",
                    "x": x,
                    "y": y,
                    "z": z,
                    "nbt": converted.nbt_1182,
                    "label": label,
                }
            )

    converted_patch = {
        "format_version": "1.18.2",
        "metadata": {
            "name": "railcraft_task5a_converted",
            "source": str(world),
            "samples": len(sample_results),
        },
        "edits": target_edits,
    }

    report = {
        "samples": sample_results,
        "stats": {
            "total": len(sample_results),
            "successful": sum(1 for s in sample_results if s["success"]),
            "failed": sum(1 for s in sample_results if not s["success"]),
            "warnings": sum(len(s["warnings"]) for s in sample_results),
            "read_failures": read_failures,
        },
        "target_distribution": {},
    }

    # Count target blocks
    target_counts: dict[str, int] = {}
    for s in sample_results:
        bid = s["target"]["block_id"]
        if bid:
            target_counts[bid] = target_counts.get(bid, 0) + 1
    report["target_distribution"] = target_counts

    return converted_patch, report


def generate_report_md(report: dict[str, Any]) -> str:
    stats = report["stats"]
    lines = [
        "# Railcraft Task 5A – Report",
        "",
        f"**Date:** 2026-05-20",
        f"**Mod:** Railcraft 1.7.10 → Create / Steam'n'Rails / IE / Mekanism / Thermal / Vanilla 1.18.2",
        f"**Total samples:** {stats['total']}",
        f"**Successful conversions:** {stats['successful']}",
        f"**Failed conversions:** {stats['failed']}",
        f"**Warnings:** {stats['warnings']}",
        "",
        "## Read failures",
    ]
    if stats["read_failures"]:
        for f in stats["read_failures"]:
            lines.append(f"- {f}")
    else:
        lines.append("None")
    lines.append("")
    lines.append("## Sample results")
    lines.append("")
    lines.append("| Label | Source | TE ID | Target | Success | Warnings | Errors |")
    lines.append("|-------|--------|-------|--------|---------|----------|--------|")
    for s in report["samples"]:
        src = s["source"]["registry_name"]
        te = s["source"]["te_id"] or "-"
        tgt = s["target"]["block_id"] or "-"
        wcount = len(s["warnings"])
        ecount = len(s["errors"])
        lines.append(f"| {s['label']} | {src} | {te} | {tgt} | {s['success']} | {wcount} | {ecount} |")
    lines.append("")
    lines.append("## Target block distribution")
    lines.append("")
    for bid, count in sorted(report.get("target_distribution", {}).items(), key=lambda x: -x[1]):
        lines.append(f"- `{bid}`: {count}")
    lines.append("")
    lines.append("## Redstone harness")
    lines.append("")
    lines.append("Generated for headless server integration test (Task 5A requirement for technical mods).")
    lines.append("")
    lines.append("- **Spec:** `railcraft_task5a_redstone_spec.json`")
    lines.append("- **Patch:** `railcraft_task5a_redstone_harness_patch_1182.json`")
    lines.append("- **Components:** Lever start (196,65,198), command block assert (198,65,198), redstone bus connecting converted observers/comparators/repeaters.")
    lines.append("- **SUT roles:** observer_output (detectors), comparator_output (signal boxes), repeater_output (sequencer), lever_input (switch lever).")
    lines.append("")
    lines.append("## Files produced")
    lines.append("")
    lines.append("- `railcraft_task5a_source_patch_1710.json` — 128 edits (66 samples) on test world `lightweigh_map_templates/1710/railcraft_task5a_world`")
    lines.append("- `railcraft_task5a_converted_patch_1182.json` — converted 1.18.2 patch")
    lines.append("- `railcraft_task5a_conversion_report.json` — per-sample results")
    lines.append("- `railcraft_task5a_redstone_spec.json` + `railcraft_task5a_redstone_harness_patch_1182.json` — integration test harness")
    lines.append("")
    return "\n".join(lines)


def main() -> None:
    world = DEFAULT_WORLD
    print("Converting world:", world)
    converted_patch, report = convert_world(world, SOURCE_PATCH)

    write_json(CONVERTED_PATCH, converted_patch)
    print("Wrote converted patch:", CONVERTED_PATCH)

    write_json(CONVERSION_REPORT, report)
    print("Wrote conversion report:", CONVERSION_REPORT)

    REPORT_MD.write_text(generate_report_md(report), encoding="utf-8")
    print("Wrote report:", REPORT_MD)

    print(f"\nStats: {report['stats']}")


if __name__ == "__main__":
    main()
