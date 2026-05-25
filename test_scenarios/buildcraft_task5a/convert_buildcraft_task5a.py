"""Convert BuildCraft Task 5A 1.7.10 test world to 1.18.2 patch."""
from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[2]
SCENARIO_DIR = Path(__file__).resolve().parent
WORLD_PATH = SCENARIO_DIR / "buildcraft_task5a_world"
SOURCE_PATCH = SCENARIO_DIR / "buildcraft_task5a_source_patch_1710.json"
OUT_PATCH = SCENARIO_DIR / "buildcraft_task5a_converted_patch_1182.json"
OUT_EVENTS = SCENARIO_DIR / "buildcraft_task5a_events_1182.json"
REPORT = SCENARIO_DIR / "buildcraft_task5a_conversion_report.json"

sys.path.insert(0, str(PROJECT_ROOT))
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from minecraft_map_parser.anvil_parser import AnvilParser
from converters.router import convert_te_to_events
from converters.mekanism.analyze_map_coverage import get_block_at, nbt_to_python


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


def convert_world() -> None:
    source_patch = load_json(SOURCE_PATCH)
    samples = source_patch.get("metadata", {}).get("samples", [])

    target_edits: list[dict[str, Any]] = []
    sample_results: list[dict[str, Any]] = []
    all_events: list[dict[str, Any]] = []

    for sample in samples:
        x, y, z = int(sample["x"]), int(sample["y"]), int(sample["z"])
        numeric_id = int(sample["numeric_id"])
        metadata = int(sample["meta"])
        name = sample["name"]
        te_id = sample.get("te_id", "")

        chunk = load_chunk(WORLD_PATH, x, z)
        if chunk is None:
            sample_results.append({"name": name, "status": "error", "reason": "chunk missing", "pos": [x, y, z]})
            continue

        read_numeric_id, read_meta = get_block_at(chunk, x, y, z)
        if read_numeric_id != numeric_id or read_meta != metadata:
            sample_results.append({
                "name": name, "status": "error",
                "reason": f"block mismatch: got {read_numeric_id}:{read_meta}, expected {numeric_id}:{metadata}",
                "pos": [x, y, z]
            })
            continue

        te_nbt = find_te(chunk, x, y, z) if sample.get("has_te") else None

        events = convert_te_to_events(
            te_nbt=te_nbt or {},
            block_numeric_id=read_numeric_id,
            metadata=read_meta,
            global_pos=(x, y, z),
        )

        if not events:
            sample_results.append({"name": name, "status": "error", "reason": "converter returned empty", "pos": [x, y, z]})
            continue

        for ev in events:
            target_edits.append(ev)
            all_events.append({"sample": name, "event": ev})

        sample_results.append({
            "name": name, "status": "ok",
            "events": len(events),
            "pos": [x, y, z],
            "te_id": te_nbt.get("id") if te_nbt else None,
        })

    write_json(OUT_PATCH, {"edits": target_edits})
    write_json(OUT_EVENTS, {"events": all_events})
    write_json(REPORT, {
        "total_samples": len(samples),
        "converted": sum(1 for r in sample_results if r["status"] == "ok"),
        "errors": sum(1 for r in sample_results if r["status"] == "error"),
        "results": sample_results,
    })
    print(f"Converted {sum(1 for r in sample_results if r['status'] == 'ok')}/{len(samples)} samples")
    print(f"  -> {OUT_PATCH}")
    print(f"  -> {REPORT}")


if __name__ == "__main__":
    convert_world()
