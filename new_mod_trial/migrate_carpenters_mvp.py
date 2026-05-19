#!/usr/bin/env python3
"""
Builds a CuttableBlocks MVP migration report from exported Carpenter's Blocks TE data.

This script intentionally does not edit .mca files. It is the safe first step for
the migration path: feed it a small JSON export from a test world, inspect the
planned replacements, then hand the output to a world patcher.

Input shape:
[
  {
    "x": 0, "y": 64, "z": 0,
    "te_id": "TileEntityCarpentersBlock",
    "block": "CarpentersBlocks:blockCarpentersSlope",
    "metadata": 2,
    "cover_block": "minecraft:planks",
    "cover_meta": 0,
    "facing": 2,
    "shape": 0
  }
]
"""

import argparse
import json
from pathlib import Path


MVP_TARGETS = {
    "block": "cuttableblocks:carpenter_block",
    "slope": "cuttableblocks:carpenter_slope",
    "stairs": "cuttableblocks:carpenter_stairs",
    "barrier": "cuttableblocks:carpenter_barrier",
    "door": "cuttableblocks:carpenter_door",
}


def detect_kind(entry):
    raw = " ".join(
        str(entry.get(key, ""))
        for key in ("block", "block_id", "te_id", "name", "type")
    ).lower()
    if "garage" in raw:
        return None
    if "slope" in raw or "wedge" in raw:
        return "slope"
    if "stair" in raw:
        return "stairs"
    if "barrier" in raw or "fence" in raw:
        return "barrier"
    if "door" in raw:
        return "door"
    if "carpenter" in raw or "carpenters" in raw:
        return "block"
    return None


def convert_entry(entry):
    kind = detect_kind(entry)
    if kind not in MVP_TARGETS:
        return {
            "status": "unsupported",
            "source": entry,
            "reason": "not_in_mvp_or_unknown_shape",
        }

    converted = {
        "status": "converted",
        "target_block": MVP_TARGETS[kind],
        "x": entry.get("x"),
        "y": entry.get("y"),
        "z": entry.get("z"),
        "tile_entity": {
            "id": "CoverableTE",
            "coverBlock": entry.get("cover_block", entry.get("coverBlock", "minecraft:planks")),
            "coverMeta": int(entry.get("cover_meta", entry.get("coverMeta", 0))),
            "facing": int(entry.get("facing", entry.get("metadata", 2))) if str(entry.get("facing", entry.get("metadata", 2))).isdigit() else 2,
            "shape": int(entry.get("shape", 0)) if str(entry.get("shape", 0)).isdigit() else 0,
            "flags": int(entry.get("flags", 0)) if str(entry.get("flags", 0)).isdigit() else 0,
            "sourceCarpentersTeId": entry.get("te_id", entry.get("id", "")),
        },
        "source": entry,
    }
    return converted


def main():
    parser = argparse.ArgumentParser(description="Create a CuttableBlocks MVP migration report.")
    parser.add_argument("input_json", help="JSON array with exported Carpenter's Blocks tile entities")
    parser.add_argument("output_json", help="Path for the generated migration report")
    args = parser.parse_args()

    source = json.loads(Path(args.input_json).read_text(encoding="utf-8-sig"))
    if not isinstance(source, list):
        raise SystemExit("Input JSON must be a list of tile entity entries")

    results = [convert_entry(entry) for entry in source]
    converted = [entry for entry in results if entry["status"] == "converted"]
    unsupported = [entry for entry in results if entry["status"] != "converted"]
    report = {
        "summary": {
            "total": len(results),
            "converted": len(converted),
            "unsupported": len(unsupported),
            "supported_targets": MVP_TARGETS,
        },
        "results": results,
    }
    Path(args.output_json).write_text(json.dumps(report, indent=2, sort_keys=True), encoding="utf-8")
    print("Converted: {0}/{1}; unsupported: {2}".format(len(converted), len(results), len(unsupported)))


if __name__ == "__main__":
    main()
