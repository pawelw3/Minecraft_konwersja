#!/usr/bin/env python3
"""Convert the IC2 Task 5A 1.7.10 test world to a 1.18.2 patch."""
from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[2]
SCENARIO_DIR = Path(__file__).resolve().parent
DEFAULT_WORLD = PROJECT_ROOT / "lightweigh_map_templates" / "1710_modded" / "ic2_task5a_world"
DEFAULT_SOURCE_PATCH = SCENARIO_DIR / "ic2_task5a_source_patch_1710.json"
DEFAULT_OUT_PATCH = SCENARIO_DIR / "ic2_task5a_converted_patch_1182.json"
DEFAULT_REPORT = SCENARIO_DIR / "ic2_task5a_conversion_report.json"

sys.path.insert(0, str(PROJECT_ROOT))
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from minecraft_map_parser.anvil_parser import AnvilParser  # noqa: E402
from src.converters.ic2.ic2_converter import IC2Converter  # noqa: E402
from src.converters.mekanism.analyze_map_coverage import get_block_at, nbt_to_python  # noqa: E402


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


def convert_world(world: Path, source_patch_path: Path, out_patch_path: Path, report_path: Path) -> None:
    source_patch = load_json(source_patch_path)
    samples = source_patch.get("metadata", {}).get("samples", [])
    converter = IC2Converter()
    chunk_cache: dict[tuple[int, int], Any] = {}
    read_failures: list[str] = []
    target_edits: list[dict[str, Any]] = []
    sample_results: list[dict[str, Any]] = []

    for sample in samples:
        x, y, z = int(sample["x"]), int(sample["y"]), int(sample["z"])
        block_id_str = sample["block"]
        metadata = int(sample["meta"])
        name = sample["name"]
        has_te = sample["has_te"]

        chunk_key = (x >> 4, z >> 4)
        chunk = chunk_cache.get(chunk_key)
        if chunk is None:
            chunk = load_chunk(world, x, z)
            chunk_cache[chunk_key] = chunk
        if chunk is None:
            read_failures.append(f"Missing chunk for {name} at {(x, y, z)}")
            continue

        numeric_id, read_meta = get_block_at(chunk, x, y, z)
        if numeric_id != int(sample["numeric_id"]) or read_meta != metadata:
            read_failures.append(
                f"Block mismatch for {name} at {(x, y, z)}: "
                f"got {numeric_id}:{read_meta}, expected {sample['numeric_id']}:{metadata}"
            )
            continue

        nbt = find_te(chunk, x, y, z) if has_te else None
        if has_te and nbt is None:
            read_failures.append(f"Missing TE for {name} at {(x, y, z)}")
            continue

        result = converter.convert_block(block_id_str, metadata, nbt, (x, y, z))
        converted = result.converted
        sample_results.append(
            {
                "name": name,
                "source": {"numeric_id": numeric_id, "block_id": block_id_str, "metadata": metadata, "position": [x, y, z], "te_id": nbt.get("id") if nbt else None},
                "target": {"block_id": converted.block_id_1182, "has_nbt": converted.nbt_1182 is not None},
                "success": converted.success,
                "warnings": converted.warnings,
                "errors": converted.errors,
            }
        )
        if converted.success and converted.block_id_1182:
            target_edit: dict[str, Any] = {
                "op": "set_block",
                "x": x,
                "y": y,
                "z": z,
                "block_id": converted.block_id_1182,
                "properties": converted.blockstate_props,
            }
            if converted.nbt_1182:
                target_edit["nbt"] = converted.nbt_1182
            target_edits.append(target_edit)

    out_patch = {"edits": target_edits}
    write_json(out_patch_path, out_patch)

    report = {
        "mod": "IC2",
        "task": "5A",
        "world": str(world),
        "samples": sample_results,
        "stats": converter.stats,
        "read_failures": read_failures,
        "event_count": len(converter.events),
    }
    write_json(report_path, report)

    print(f"Converted {len(target_edits)} blocks -> {out_patch_path}")
    print(f"Report -> {report_path}")
    print(f"Stats: {converter.stats}")
    if read_failures:
        print(f"Read failures ({len(read_failures)}):")
        for f in read_failures:
            print(f"  {f}")


def main() -> None:
    convert_world(DEFAULT_WORLD, DEFAULT_SOURCE_PATCH, DEFAULT_OUT_PATCH, DEFAULT_REPORT)


if __name__ == "__main__":
    main()
