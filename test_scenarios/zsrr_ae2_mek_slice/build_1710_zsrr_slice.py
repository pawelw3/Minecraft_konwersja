"""Build a small 1.7.10 save containing the selected ZSRR 300x300 slice.

The output keeps original world coordinates. Region files are compacted and
contain only chunks intersecting the selected rectangle. The original
``mapa_1710`` world is never modified.
"""

from __future__ import annotations

import json
import shutil
import struct
from pathlib import Path
from typing import Iterable

import nbtlib
from nbtlib import Byte, Int, String


ROOT = Path(__file__).resolve().parents[2]
SOURCE_WORLD = ROOT / "mapa_1710"
TARGET_WORLD = ROOT / "lightweigh_map_templates" / "1710_modded" / "zsrr_ae2_mek_300"

MIN_X = -2565
MAX_X = -2266
MIN_Z = -2301
MAX_Z = -2002

SPAWN_X = -2416
SPAWN_Y = 72
SPAWN_Z = -2152

SECTOR_SIZE = 4096


def floor_chunk(value: int) -> int:
    return value // 16


def floor_region_from_chunk(chunk: int) -> int:
    return chunk // 32


MIN_CHUNK_X = floor_chunk(MIN_X)
MAX_CHUNK_X = floor_chunk(MAX_X)
MIN_CHUNK_Z = floor_chunk(MIN_Z)
MAX_CHUNK_Z = floor_chunk(MAX_Z)


def chunk_ranges() -> tuple[range, range]:
    return (
        range(MIN_CHUNK_X, MAX_CHUNK_X + 1),
        range(MIN_CHUNK_Z, MAX_CHUNK_Z + 1),
    )


def needed_regions() -> list[tuple[int, int]]:
    regions = set()
    xs, zs = chunk_ranges()
    for cx in xs:
        for cz in zs:
            regions.add((floor_region_from_chunk(cx), floor_region_from_chunk(cz)))
    return sorted(regions)


def copy_support_files() -> None:
    if TARGET_WORLD.exists():
        root = (ROOT / "lightweigh_map_templates" / "1710_modded").resolve()
        target = TARGET_WORLD.resolve()
        if root not in target.parents:
            raise RuntimeError(f"Refusing to delete outside templates: {target}")
        shutil.rmtree(target)

    TARGET_WORLD.mkdir(parents=True)

    excluded_dirs = {"region", "playerdata", "players", "stats", "NEI"}
    for source_dir in sorted(p for p in SOURCE_WORLD.iterdir() if p.is_dir()):
        if source_dir.name in excluded_dirs:
            continue
        shutil.copytree(source_dir, TARGET_WORLD / source_dir.name)

    excluded_files = {
        "session.lock",
        "forcedchunks.dat",
        "level.dat",
        "level.dat_old",
    }
    for source_file in sorted(p for p in SOURCE_WORLD.iterdir() if p.is_file()):
        if source_file.name in excluded_files:
            continue
        shutil.copy2(source_file, TARGET_WORLD / source_file.name)


def patch_level_dat() -> None:
    for name in ("level.dat", "level.dat_old"):
        source = SOURCE_WORLD / name
        target = TARGET_WORLD / name
        nbt_file = nbtlib.load(source)
        data = nbt_file["Data"]
        data["LevelName"] = String("zsrr_ae2_mek_300")
        data["SpawnX"] = Int(SPAWN_X)
        data["SpawnY"] = Int(SPAWN_Y)
        data["SpawnZ"] = Int(SPAWN_Z)
        data["GameType"] = Int(1)
        data["allowCommands"] = Byte(1)
        nbt_file.save(target, gzipped=True)


def read_chunk_payload(region_data: bytes, local_x: int, local_z: int) -> tuple[bytes, int] | None:
    index = local_x + local_z * 32
    location_offset = index * 4
    location = region_data[location_offset:location_offset + 4]
    sector_offset = (location[0] << 16) | (location[1] << 8) | location[2]
    sector_count = location[3]
    if sector_offset == 0 or sector_count == 0:
        return None

    byte_offset = sector_offset * SECTOR_SIZE
    if byte_offset + 5 > len(region_data):
        return None
    length = struct.unpack(">I", region_data[byte_offset:byte_offset + 4])[0]
    if length <= 1:
        return None
    raw = region_data[byte_offset:byte_offset + 4 + length]

    timestamp_offset = SECTOR_SIZE + index * 4
    timestamp = struct.unpack(">I", region_data[timestamp_offset:timestamp_offset + 4])[0]
    return raw, timestamp


def write_compact_region(source_region: Path, target_region: Path, keep_chunks: set[tuple[int, int]]) -> int:
    data = source_region.read_bytes()
    header = bytearray(SECTOR_SIZE * 2)
    body = bytearray()
    kept = 0

    for local_z in range(32):
        for local_x in range(32):
            if (local_x, local_z) not in keep_chunks:
                continue
            payload = read_chunk_payload(data, local_x, local_z)
            if payload is None:
                continue
            raw, timestamp = payload
            sector_offset = 2 + len(body) // SECTOR_SIZE
            padding = (SECTOR_SIZE - (len(raw) % SECTOR_SIZE)) % SECTOR_SIZE
            raw_padded = raw + (b"\x00" * padding)
            sector_count = len(raw_padded) // SECTOR_SIZE
            if sector_count > 255:
                raise RuntimeError(f"Chunk too large for region table: {source_region} {local_x},{local_z}")

            index = local_x + local_z * 32
            header[index * 4] = (sector_offset >> 16) & 0xFF
            header[index * 4 + 1] = (sector_offset >> 8) & 0xFF
            header[index * 4 + 2] = sector_offset & 0xFF
            header[index * 4 + 3] = sector_count
            struct.pack_into(">I", header, SECTOR_SIZE + index * 4, timestamp)
            body.extend(raw_padded)
            kept += 1

    target_region.parent.mkdir(parents=True, exist_ok=True)
    target_region.write_bytes(bytes(header) + bytes(body))
    return kept


def build_regions() -> dict[str, int]:
    result = {}
    target_region_dir = TARGET_WORLD / "region"
    target_region_dir.mkdir(parents=True, exist_ok=True)
    chunk_xs, chunk_zs = chunk_ranges()
    keep_global = {(cx, cz) for cx in chunk_xs for cz in chunk_zs}

    for rx, rz in needed_regions():
        keep_local = {
            (cx & 31, cz & 31)
            for cx, cz in keep_global
            if floor_region_from_chunk(cx) == rx and floor_region_from_chunk(cz) == rz
        }
        source_region = SOURCE_WORLD / "region" / f"r.{rx}.{rz}.mca"
        if not source_region.exists():
            continue
        target_region = target_region_dir / source_region.name
        kept = write_compact_region(source_region, target_region, keep_local)
        result[source_region.name] = kept

    return result


def write_report(region_counts: dict[str, int]) -> None:
    report = {
        "source_world": str(SOURCE_WORLD.relative_to(ROOT)).replace("\\", "/"),
        "target_world": str(TARGET_WORLD.relative_to(ROOT)).replace("\\", "/"),
        "block_bounds": {"min_x": MIN_X, "max_x": MAX_X, "min_z": MIN_Z, "max_z": MAX_Z},
        "chunk_bounds": {
            "min_chunk_x": MIN_CHUNK_X,
            "max_chunk_x": MAX_CHUNK_X,
            "min_chunk_z": MIN_CHUNK_Z,
            "max_chunk_z": MAX_CHUNK_Z,
        },
        "spawn": {"x": SPAWN_X, "y": SPAWN_Y, "z": SPAWN_Z},
        "gamemode": "creative",
        "regions": region_counts,
        "total_chunks": sum(region_counts.values()),
        "notes": [
            "Chunk-aligned crop: the loaded terrain is slightly larger than 300x300.",
            "playerdata/players/stats are intentionally not copied so new joins use spawn and creative gamemode.",
            "forcedchunks.dat is intentionally not copied to avoid loading chunks outside the slice.",
        ],
    }
    out = TARGET_WORLD / "SLICE_REPORT.json"
    out.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")


def main() -> None:
    copy_support_files()
    patch_level_dat()
    region_counts = build_regions()
    write_report(region_counts)
    print(f"Created {TARGET_WORLD}")
    print(f"Regions: {region_counts}")
    print(f"Total chunks: {sum(region_counts.values())}")
    print(f"Spawn: {SPAWN_X} {SPAWN_Y} {SPAWN_Z}; gamemode creative")


if __name__ == "__main__":
    main()
