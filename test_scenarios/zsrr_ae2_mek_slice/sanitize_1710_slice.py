#!/usr/bin/env python3
"""Remove crash-prone non-target BlockEntities from the 1.7.10 ZSRR slice."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parents[2]
SCENARIO_DIR = Path(__file__).resolve().parent
DEFAULT_WORLD = PROJECT_ROOT / "lightweigh_map_templates" / "1710_modded" / "zsrr_ae2_mek_300"
DEFAULT_PATCH = SCENARIO_DIR / "zsrr_ae2_mek_300_sanitize_1710_patch.json"
DEFAULT_REPORT = SCENARIO_DIR / "zsrr_ae2_mek_300_sanitize_1710_report.json"

sys.path.insert(0, str(PROJECT_ROOT))
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from minecraft_map_parser.anvil_parser import AnvilParser  # noqa: E402
from src.converters.mekanism.analyze_map_coverage import nbt_to_python  # noqa: E402


CRASH_PRONE_TE_IDS = {
    "wiredmodem",
    "computer",
    "diskdrive",
    "monitor",
    "printer",
    "turtle",
    "wirelessmodem",
}


def write_json(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def build_patch(world: Path) -> tuple[dict[str, Any], dict[str, Any]]:
    edits: list[dict[str, Any]] = []
    found: list[dict[str, Any]] = []
    for region_file in sorted((world / "region").glob("r.*.*.mca")):
        parser = AnvilParser(str(region_file))
        for chunk in parser.get_all_chunks():
            for raw_te in chunk.get_tile_entities():
                te = nbt_to_python(raw_te)
                te_id = str(te.get("id") or "")
                if te_id not in CRASH_PRONE_TE_IDS:
                    continue
                x, y, z = int(te["x"]), int(te["y"]), int(te["z"])
                edits.append({"op": "set_block", "x": x, "y": y, "z": z, "id": 0, "meta": 0})
                edits.append({"op": "remove_te", "x": x, "y": y, "z": z})
                found.append({"id": te_id, "pos": [x, y, z], "region": region_file.name, "chunk": [chunk.x, chunk.z]})

    patch = {
        "format_version": "1.7.10",
        "metadata": {
            "name": "zsrr_ae2_mek_300_sanitize_1710",
            "reason": "ComputerCraft tiles can crash when this slice is loaded without full neighboring context or when their numeric block id resolves to another mod block.",
            "source_world": str(world),
        },
        "edits": edits,
    }
    report = {
        "world": str(world),
        "removed_tile_entities": len(found),
        "edits": len(edits),
        "crash_prone_te_ids": sorted(CRASH_PRONE_TE_IDS),
        "sample": found[:100],
    }
    return patch, report


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--world", type=Path, default=DEFAULT_WORLD)
    parser.add_argument("--patch", type=Path, default=DEFAULT_PATCH)
    parser.add_argument("--report", type=Path, default=DEFAULT_REPORT)
    args = parser.parse_args()

    patch, report = build_patch(args.world)
    write_json(args.patch, patch)
    write_json(args.report, report)
    print(f"Crash-prone TEs: {report['removed_tile_entities']}")
    print(f"Patch edits: {report['edits']}")
    print(f"Patch: {args.patch}")
    print(f"Report: {args.report}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
