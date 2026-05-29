"""Direct terrain writer pipeline for block-only conversions.

Scans a 1.7.10 world chunk-by-chunk, resolves numeric block IDs to registry
names via FML ItemData, routes mod blocks through the block-only converter
router, and writes the resulting events to a JSONL audit stream.

Usage:
    from converters.direct_terrain_writer import scan_world_for_block_only

    events = scan_world_for_block_only(
        world_path="mapa_1710/world",
        level_dat_path="mapa_1710/level.dat",
    )
    # events is a generator yielding Event JSON dicts

The caller is responsible for persisting events (e.g. to a .jsonl file) and
applying them to the 1.18.2 world via a separate writer (Hephaistos/JVM or
Amulet).
"""

from __future__ import annotations

import gzip
import json
import os
import struct
import zlib
from pathlib import Path
from typing import Iterator

from converters.block_only_router import convert_block_only_to_event
from converters.common.item_id_resolver import load_item_id_mapping
from minecraft_map_parser.anvil_parser import AnvilParser, ChunkData


# Vanilla numeric IDs (0-255 range) that never need mod resolution.
# These are handled by the vanilla fast-path layer.
_VANILLA_NUMERIC_IDS: set[int] = set(range(256))


def _iter_regions(world_path: str) -> Iterator[Path]:
    region_dir = Path(world_path) / "region"
    if not region_dir.exists():
        return
    for path in sorted(region_dir.glob("r.*.*.mca")):
        yield path


def _iter_blocks_in_chunk(
    chunk: ChunkData,
    region_x: int,
    region_z: int,
) -> Iterator[tuple[int, int, int, int, int]]:
    """Yield (global_x, global_y, global_z, numeric_id, metadata) for each block.

    Skips air (numeric_id == 0) and empty sections.
    """
    chunk_x_global = region_x * 32 + chunk.x
    chunk_z_global = region_z * 32 + chunk.z

    for section in chunk.get_sections():
        if not isinstance(section, dict):
            continue

        section_y = section.get("Y", 0)
        if hasattr(section_y, "value"):
            section_y = section_y.value
        section_y = int(section_y) if section_y else 0

        blocks = section.get("Blocks")
        add = section.get("Add") or section.get("AddBlocks")
        data_arr = section.get("Data")

        if blocks is None:
            continue

        if hasattr(blocks, "value"):
            blocks = blocks.value
        if hasattr(add, "value"):
            add = add.value
        if hasattr(data_arr, "value"):
            data_arr = data_arr.value

        if not isinstance(blocks, (bytes, bytearray, list)):
            continue

        for y_in_section in range(16):
            for z in range(16):
                for x in range(16):
                    i = y_in_section * 256 + z * 16 + x
                    if i >= len(blocks):
                        break

                    low = blocks[i] & 0xFF
                    if low == 0 and not add:
                        # Fast skip air when no Add array
                        continue

                    high = 0
                    if add and i // 2 < len(add):
                        if i % 2 == 0:
                            high = add[i // 2] & 0x0F
                        else:
                            high = (add[i // 2] >> 4) & 0x0F

                    full_id = (high << 8) | low
                    if full_id == 0:
                        continue

                    meta = 0
                    if data_arr and i // 2 < len(data_arr):
                        if i % 2 == 0:
                            meta = data_arr[i // 2] & 0x0F
                        else:
                            meta = (data_arr[i // 2] >> 4) & 0x0F

                    global_x = chunk_x_global * 16 + x
                    global_y = section_y * 16 + y_in_section
                    global_z = chunk_z_global * 16 + z
                    yield (global_x, global_y, global_z, full_id, meta)


def scan_world_for_block_only(
    world_path: str,
    level_dat_path: str,
    *,
    skip_vanilla_by_registry: bool = True,
    audit_unknown: bool = True,
    region_filter: list[tuple[int, int]] | None = None,
) -> Iterator[dict]:
    """Scan a 1.7.10 world and yield Event JSON dicts for block-only conversions.

    Args:
        world_path: Path to the 1.7.10 world directory (must contain region/).
        level_dat_path: Path to the 1.7.10 level.dat (for FML ItemData lookup).
        skip_vanilla_by_registry: If True, blocks whose resolved registry name
            starts with "minecraft:" are skipped (handled by vanilla layer).
        audit_unknown: If True, yield audit events for unknown mod blocks.

    Yields:
        Event JSON dicts with keys:
        - op: "set_block"
        - pos: [x, y, z]
        - block: target_block_id
        - blockstate: dict (optional)
        - confidence: str (optional)
        - warnings: list (optional)

        And optionally audit events for unknown blocks:
        - op: "audit_warn"
        - pos: [x, y, z]
        - source_numeric_id: int
        - source_registry: str
        - source_metadata: int
        - reason: str
    """
    id_mapping = load_item_id_mapping(level_dat_path)

    for region_path in _iter_regions(world_path):
        # Parse region coordinates from filename r.X.Z.mca
        stem = region_path.stem
        parts = stem.split(".")
        if len(parts) != 3:
            continue
        try:
            region_x = int(parts[1])
            region_z = int(parts[2])
        except ValueError:
            continue

        if region_filter is not None and (region_x, region_z) not in region_filter:
            continue

        parser = AnvilParser(str(region_path))
        for chunk in parser.get_all_chunks():
            for global_x, global_y, global_z, numeric_id, meta in _iter_blocks_in_chunk(
                chunk, region_x, region_z
            ):
                registry_name = id_mapping.get(str(numeric_id), "")
                if not registry_name:
                    if audit_unknown:
                        yield {
                            "op": "audit_warn",
                            "pos": [global_x, global_y, global_z],
                            "source_numeric_id": numeric_id,
                            "source_registry": "",
                            "source_metadata": meta,
                            "reason": "no_fml_registry_mapping",
                        }
                    continue

                if skip_vanilla_by_registry and registry_name.startswith("minecraft:"):
                    continue

                event = convert_block_only_to_event(
                    numeric_id=numeric_id,
                    registry_name=registry_name,
                    metadata=meta,
                    position=(global_x, global_y, global_z),
                )
                if event is not None:
                    yield event
                elif audit_unknown:
                    yield {
                        "op": "audit_warn",
                        "pos": [global_x, global_y, global_z],
                        "source_numeric_id": numeric_id,
                        "source_registry": registry_name,
                        "source_metadata": meta,
                        "reason": "block_only_converter_returned_empty",
                    }


def write_events_to_jsonl(events: Iterator[dict], output_path: str) -> None:
    """Write an event stream to a newline-delimited JSON file."""
    with open(output_path, "w", encoding="utf-8") as f:
        for event in events:
            f.write(json.dumps(event, ensure_ascii=False) + "\n")


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 4:
        print(
            "Usage: python -m converters.direct_terrain_writer "
            "<world_path> <level_dat_path> <output_jsonl_path>"
        )
        sys.exit(1)

    world_path = sys.argv[1]
    level_dat_path = sys.argv[2]
    output_path = sys.argv[3]

    print(f"Scanning {world_path} ...")
    event_count = 0
    audit_count = 0
    with open(output_path, "w", encoding="utf-8") as f:
        for event in scan_world_for_block_only(world_path, level_dat_path):
            f.write(json.dumps(event, ensure_ascii=False) + "\n")
            if event.get("op") == "audit_warn":
                audit_count += 1
            else:
                event_count += 1
            if (event_count + audit_count) % 100_000 == 0:
                print(f"  Processed {event_count + audit_count} blocks...")

    print(f"Done. Events: {event_count}, Audit warnings: {audit_count}")
    print(f"Output written to {output_path}")
