#!/usr/bin/env python3
"""Convert Big Reactors Task 5A 1.7.10 test patch to 1.18.2 patch."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[2]
SCENARIO_DIR = Path(__file__).resolve().parent
SOURCE_PATCH = SCENARIO_DIR / "bigreactors_task5a_source_patch_1710.json"
CONVERTED_PATCH = SCENARIO_DIR / "bigreactors_task5a_converted_patch_1182.json"
CONVERSION_REPORT = SCENARIO_DIR / "bigreactors_task5a_conversion_report.json"

sys.path.insert(0, str(PROJECT_ROOT))
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from src.converters.bigreactors.biggerreactors_converter import BiggerReactorsConverter  # noqa: E402


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, data: dict[str, Any]) -> None:
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def convert_patch() -> None:
    source = load_json(SOURCE_PATCH)
    converter = BiggerReactorsConverter()
    target_edits: list[dict[str, Any]] = []
    results: list[dict[str, Any]] = []

    # Group edits by position
    edits_by_pos: dict[tuple[int, int, int], dict[str, Any]] = {}
    for edit in source["edits"]:
        pos = (edit["x"], edit["y"], edit["z"])
        if pos not in edits_by_pos:
            edits_by_pos[pos] = {}
        if edit["op"] == "set_block":
            edits_by_pos[pos]["block"] = edit
        elif edit["op"] == "set_te":
            edits_by_pos[pos]["te"] = edit

    # Numeric ID to block name mapping (reverse of BLOCK_IDS in generator)
    numeric_to_name = {
        974: "BigReactors:YelloriteOre",
        977: "BigReactors:BRReactorPart",
        978: "BigReactors:BRMultiblockGlass",
        980: "BigReactors:BRTurbinePart",
        982: "BigReactors:BRDevice",
        1139: "BigReactors:BRMultiblockCreativePart",
        1195: "BigReactors:BRMetalBlock",
        1317: "BigReactors:YelloriumFuelRod",
        1410: "BigReactors:BRTurbineRotorPart",
        1579: "BigReactors:BRReactorRedstonePort",
    }

    for pos, group in edits_by_pos.items():
        block_edit = group.get("block")
        te_edit = group.get("te")

        if not block_edit:
            continue

        numeric_id = block_edit["id"]
        if numeric_id == 1:  # stone markers — skip
            continue
        block_name = numeric_to_name.get(numeric_id, f"unknown:{numeric_id}")
        metadata = block_edit["meta"]
        x, y, z = pos
        nbt = te_edit["nbt"] if te_edit else None

        result = converter.convert_block(block_name, metadata, nbt, pos)
        c = result.converted

        results.append({
            "source_block": block_name,
            "metadata": metadata,
            "position": [x, y, z],
            "source_te_id": nbt.get("id") if nbt else None,
            "target_block_id": c.block_id_1182,
            "success": c.success,
            "warnings": c.warnings,
            "errors": c.errors,
        })

        if c.success and c.block_id_1182:
            target_edit: dict[str, Any] = {
                "op": "set_block",
                "x": x,
                "y": y,
                "z": z,
                "block_id": c.block_id_1182,
                "properties": c.blockstate_props,
            }
            if c.nbt_1182:
                target_edit["nbt"] = c.nbt_1182
            target_edits.append(target_edit)

    out_patch = {"edits": target_edits}
    write_json(CONVERTED_PATCH, out_patch)

    report = {
        "mod": "BigReactors",
        "task": "5A",
        "samples": results,
        "stats": converter.stats,
    }
    write_json(CONVERSION_REPORT, report)

    print(f"Converted {len(target_edits)} blocks -> {CONVERTED_PATCH}")
    print(f"Report -> {CONVERSION_REPORT}")
    print(f"Stats: {converter.stats}")

    # Warnings summary
    all_warnings = [w for r in results for w in r.get("warnings", [])]
    if all_warnings:
        print(f"\nWarnings ({len(all_warnings)}):")
        for w in all_warnings[:10]:
            print(f"  {w}")
        if len(all_warnings) > 10:
            print(f"  ... and {len(all_warnings) - 10} more")


if __name__ == "__main__":
    convert_patch()
