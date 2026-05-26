#!/usr/bin/env python3
"""Convert the ComputerCraft Task 5A 1.7.10 test world to a 1.18.2 patch."""
from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[2]
SCENARIO_DIR = Path(__file__).resolve().parent
DEFAULT_WORLD = PROJECT_ROOT / "lightweigh_map_templates" / "1710_modded" / "computercraft_task5a_world"
DEFAULT_PATCH = SCENARIO_DIR / "computercraft_task5a_patch.json"
DEFAULT_OUT_PATCH = SCENARIO_DIR / "computercraft_task5a_converted_1182.json"
DEFAULT_REPORT = SCENARIO_DIR / "computercraft_task5a_report.json"

sys.path.insert(0, str(PROJECT_ROOT))
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from minecraft_map_parser.anvil_parser import AnvilParser
from minecraft_map_parser.nbt_parser import NBTTag
from converters.computercraft.computercraft_converter import ComputerCraftConverter
from converters.computercraft.mappings import get_block_mapping


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, data: dict[str, Any]) -> None:
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def nbt_to_python(value: Any) -> Any:
    if isinstance(value, NBTTag):
        if value.type == NBTTag.TAG_COMPOUND:
            return {key: nbt_to_python(inner) for key, inner in value.value.items()}
        if value.type == NBTTag.TAG_LIST:
            return [nbt_to_python(inner) for inner in value.value]
        return value.value
    if isinstance(value, dict):
        return {key: nbt_to_python(inner) for key, inner in value.items()}
    if isinstance(value, list):
        return [nbt_to_python(inner) for inner in value]
    return value


def load_chunk(world: Path, x: int, z: int):
    chunk_x = x >> 4
    chunk_z = z >> 4
    region_x = chunk_x >> 5
    region_z = chunk_z >> 5
    parser = AnvilParser(str(world / "region" / f"r.{region_x}.{region_z}.mca"))
    return parser.get_chunk(chunk_x, chunk_z)


def get_block_at(chunk, x: int, y: int, z: int) -> tuple[int, int]:
    """Read numeric block ID and metadata from chunk at given coordinates."""
    root = nbt_to_python(chunk.nbt)
    level = root.get("Level", {})
    sections = level.get("Sections", [])

    section_y = y >> 4
    local_y = y & 15
    local_x = x & 15
    local_z = z & 15

    for section in sections:
        if section.get("Y", -1) != section_y:
            continue
        blocks = section.get("Blocks", b"")
        data = section.get("Data", b"")
        add = section.get("Add", b"")

        idx = local_y * 256 + local_z * 16 + local_x
        block_id = blocks[idx] & 0xFF
        if add:
            block_id |= ((add[idx >> 1] >> (0 if (idx & 1) == 0 else 4)) & 0x0F) << 8
        meta = (data[idx >> 1] >> (0 if (idx & 1) == 0 else 4)) & 0x0F
        return block_id, meta

    return 0, 0


def find_te(chunk, x: int, y: int, z: int) -> dict[str, Any] | None:
    level = chunk.nbt.get("Level", {})
    if isinstance(level, NBTTag):
        level = level.value
    te_list = level.get("TileEntities", [])
    if isinstance(te_list, NBTTag):
        te_list = te_list.value
    for te in te_list:
        data = nbt_to_python(te)
        if (
            int(data.get("x", 0)) == x
            and int(data.get("y", 0)) == y
            and int(data.get("z", 0)) == z
        ):
            return data
    return None


def resolve_block_id_str(numeric_id: int) -> str:
    """Resolve numeric block ID to registry string using FML ItemData."""
    # Hard-coded mapping for ComputerCraft blocks on this map
    mapping = {
        574: "computercraft:turtle_expanded",
        575: "computercraft:command_computer",
        576: "computercraft:computer",
        577: "computercraft:peripheral",
        578: "computercraft:cable",
        579: "computercraft:turtle",
        580: "computercraft:turtle_advanced",
    }
    return mapping.get(numeric_id, f"unknown:{numeric_id}")


def convert_world(
    world: Path, patch_path: Path, out_patch_path: Path, report_path: Path
) -> None:
    source_patch = load_json(patch_path)
    samples = source_patch.get("metadata", {}).get("samples", [])
    converter = ComputerCraftConverter()
    chunk_cache: dict[tuple[int, int], Any] = {}
    read_failures: list[str] = []
    target_edits: list[dict[str, Any]] = []
    sample_results: list[dict[str, Any]] = []

    for sample in samples:
        x, y, z = int(sample["x"]), int(sample["y"]), int(sample["z"])
        numeric_id = int(sample["block"])
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

        read_numeric_id, read_meta = get_block_at(chunk, x, y, z)
        if read_numeric_id != numeric_id or read_meta != metadata:
            read_failures.append(
                f"Block mismatch for {name} at {(x, y, z)}: "
                f"got {read_numeric_id}:{read_meta}, expected {numeric_id}:{metadata}"
            )
            continue

        nbt = find_te(chunk, x, y, z) if has_te else None
        if has_te and nbt is None:
            read_failures.append(f"Missing TE for {name} at {(x, y, z)}")
            continue

        block_id_str = resolve_block_id_str(numeric_id)
        result = converter.convert_block(block_id_str, metadata, nbt, (x, y, z))
        converted = result.converted
        sample_results.append(
            {
                "name": name,
                "source": {
                    "numeric_id": numeric_id,
                    "block_id": block_id_str,
                    "metadata": metadata,
                    "position": [x, y, z],
                    "te_id": nbt.get("id") if nbt else None,
                },
                "target": {
                    "block_id": converted.block_id_1182,
                    "blockstate": dict(converted.blockstate_props) if converted.blockstate_props else None,
                    "has_nbt": converted.nbt_1182 is not None,
                    "nbt": converted.nbt_1182,
                },
                "success": converted.success,
                "warnings": list(converted.warnings),
                "errors": list(converted.errors),
            }
        )
        if converted.success and converted.block_id_1182:
            target_edit: dict[str, Any] = {
                "op": "set_block",
                "x": x,
                "y": y,
                "z": z,
                "block_id": converted.block_id_1182,
                "properties": dict(converted.blockstate_props) if converted.blockstate_props else {},
            }
            if converted.nbt_1182:
                target_edit["nbt"] = converted.nbt_1182
            target_edits.append(target_edit)

    out_patch = {"edits": target_edits}
    write_json(out_patch_path, out_patch)

    report = {
        "mod": "computercraft",
        "task": "5A",
        "world": str(world),
        "samples": sample_results,
        "stats": converter.stats,
        "read_failures": read_failures,
        "converted_count": len(target_edits),
    }
    write_json(report_path, report)

    print(f"Converted {len(target_edits)} blocks -> {out_patch_path}")
    print(f"Report -> {report_path}")
    print(f"Stats: {converter.stats}")
    if read_failures:
        print(f"Read failures ({len(read_failures)}):")
        for f in read_failures:
            print(f"  {f}")

    # Print summary table
    print("\n" + "=" * 80)
    print(f"{'Sample':<30} {'Source':<25} {'Target':<30} {'Status'}")
    print("=" * 80)
    for r in sample_results:
        src = f"{r['source']['block_id']}:{r['source']['metadata']}"
        tgt = r["target"]["block_id"] or "N/A"
        status = "PASS" if r["success"] else "FAIL"
        print(f"{r['name']:<30} {src:<25} {tgt:<30} {status}")
    print("=" * 80)


def main() -> None:
    convert_world(DEFAULT_WORLD, DEFAULT_PATCH, DEFAULT_OUT_PATCH, DEFAULT_REPORT)


if __name__ == "__main__":
    main()
