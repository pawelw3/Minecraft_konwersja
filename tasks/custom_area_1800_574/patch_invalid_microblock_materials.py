#!/usr/bin/env python3
"""Patch invalid CBMultipart microblock material strings in events and world."""

from __future__ import annotations

import io
import json
import math
import re
import struct
import sys
import zlib
from pathlib import Path

import nbtlib  # type: ignore

SCRIPT_DIR = Path(__file__).resolve().parent
ROOT = SCRIPT_DIR.parents[1]
sys.path.insert(0, str(ROOT / "src"))

from converters.forge_multipart.mappings import map_microblock_material as converter_safe_material  # noqa: E402

WORLD = SCRIPT_DIR / "world"
EVENTS = SCRIPT_DIR / "events.jsonl"
RESOURCE_LOCATION_RE = re.compile(r"^[a-z0-9_.-]+:[a-z0-9_/.-]+$")

MATERIAL_MAP = {
    "projred|exploration:projectred.exploration.stone": "minecraft:stone",
    "projectred|exploration:projectred.exploration.stone": "minecraft:stone",
    "tile.extrautils:colorstonebrick": "minecraft:stone_bricks",
    "tile.extrautils:color_lightgem": "minecraft:glowstone",
    "tile.extrautils:decorativeblock1": "minecraft:stone",
    "tile.extrautils:cobblestone_compressed": "minecraft:cobblestone",
    "thermalfoundation:storage": "minecraft:iron_block",
    "mekanism:basicblock": "minecraft:iron_block",
    "mekanism:basicblock2": "minecraft:iron_block",
    "minecraft:brick_block": "minecraft:bricks",
    "minecraft:stonebrick": "minecraft:stone_bricks",
    "minecraft:log": "minecraft:oak_log",
    "minecraft:log_1": "minecraft:spruce_log",
    "minecraft:log_2": "minecraft:birch_log",
    "minecraft:log_3": "minecraft:jungle_log",
    "minecraft:planks": "minecraft:oak_planks",
    "minecraft:planks_1": "minecraft:spruce_planks",
    "minecraft:planks_2": "minecraft:birch_planks",
    "minecraft:planks_3": "minecraft:jungle_planks",
    "minecraft:planks_4": "minecraft:acacia_planks",
    "minecraft:planks_5": "minecraft:dark_oak_planks",
    "minecraft:wool": "minecraft:white_wool",
    "minecraft:wool_4": "minecraft:yellow_wool",
    "minecraft:wool_7": "minecraft:gray_wool",
    "minecraft:wool_11": "minecraft:blue_wool",
    "minecraft:wool_13": "minecraft:green_wool",
    "minecraft:wool_14": "minecraft:red_wool",
    "minecraft:stained_hardened_clay": "minecraft:white_terracotta",
    "minecraft:stained_hardened_clay_4": "minecraft:yellow_terracotta",
    "minecraft:stained_hardened_clay_5": "minecraft:lime_terracotta",
    "minecraft:stained_hardened_clay_13": "minecraft:green_terracotta",
    "minecraft:stained_hardened_clay_14": "minecraft:red_terracotta",
    "minecraft:stained_hardened_clay_15": "minecraft:black_terracotta",
}

VALID_VANILLA = {
    "minecraft:air",
    "minecraft:andesite",
    "minecraft:birch_log",
    "minecraft:birch_planks",
    "minecraft:black_terracotta",
    "minecraft:blue_wool",
    "minecraft:bookshelf",
    "minecraft:bricks",
    "minecraft:cobblestone",
    "minecraft:coal_block",
    "minecraft:dark_oak_planks",
    "minecraft:diamond_block",
    "minecraft:emerald_block",
    "minecraft:glass",
    "minecraft:glowstone",
    "minecraft:gold_block",
    "minecraft:green_terracotta",
    "minecraft:green_wool",
    "minecraft:gray_wool",
    "minecraft:iron_block",
    "minecraft:jungle_planks",
    "minecraft:lapis_block",
    "minecraft:lime_terracotta",
    "minecraft:oak_log",
    "minecraft:oak_planks",
    "minecraft:quartz_block",
    "minecraft:red_terracotta",
    "minecraft:red_wool",
    "minecraft:sandstone",
    "minecraft:spruce_log",
    "minecraft:spruce_planks",
    "minecraft:stone",
    "minecraft:stone_bricks",
    "minecraft:terracotta",
    "minecraft:white_concrete",
    "minecraft:white_terracotta",
    "minecraft:white_wool",
    "minecraft:yellow_terracotta",
    "minecraft:yellow_wool",
}


def strip_trailing_meta(value: str) -> str:
    head, sep, tail = value.rpartition("_")
    if sep and tail.isdigit():
        return head
    return value


def map_chisel_material(value: str) -> str:
    name = value.split(":", 1)[1] if ":" in value else value
    if "glowstone" in name:
        return "minecraft:glowstone"
    if "gold" in name:
        return "minecraft:gold_block"
    if "iron" in name:
        return "minecraft:iron_block"
    if "emerald" in name:
        return "minecraft:emerald_block"
    if "lapis" in name:
        return "minecraft:lapis_block"
    if "glass" in name:
        return "minecraft:glass"
    if "brick" in name:
        return "minecraft:stone_bricks"
    if "cobblestone" in name:
        return "minecraft:cobblestone"
    if "sandstone" in name:
        return "minecraft:sandstone"
    if "spruce_planks" in name:
        return "minecraft:spruce_planks"
    if "birch_planks" in name:
        return "minecraft:birch_planks"
    if "dark_oak_planks" in name:
        return "minecraft:dark_oak_planks"
    if "oak_planks" in name or "planks" in name:
        return "minecraft:oak_planks"
    if "concrete" in name:
        return "minecraft:white_concrete"
    if "woolen_clay" in name:
        return "minecraft:terracotta"
    if "marble" in name:
        return "minecraft:quartz_block"
    return "minecraft:stone"


def safe_material(value: str) -> str:
    if not value:
        return "minecraft:stone"
    key = str(value).strip().lower()
    no_meta = strip_trailing_meta(key)
    if key in MATERIAL_MAP:
        return MATERIAL_MAP[key]
    if no_meta in MATERIAL_MAP:
        return MATERIAL_MAP[no_meta]
    if key.startswith("chisel:"):
        return map_chisel_material(key)
    if key.startswith("tile.extrautils:"):
        return MATERIAL_MAP.get(no_meta, "minecraft:stone")
    if key in VALID_VANILLA:
        return key
    if key.startswith("minecraft:"):
        return MATERIAL_MAP.get(key, MATERIAL_MAP.get(no_meta, "minecraft:stone"))
    if key.startswith(("thermalfoundation:", "mekanism:")):
        return MATERIAL_MAP.get(no_meta, "minecraft:iron_block")
    if RESOURCE_LOCATION_RE.match(key) and key in VALID_VANILLA:
        return key
    return "minecraft:stone"


def patch_json_materials(obj) -> int:
    changed = 0
    if isinstance(obj, dict):
        for key, value in list(obj.items()):
            if key == "material" and isinstance(value, str):
                new_value = converter_safe_material(value)
                if new_value != value:
                    obj[key] = new_value
                    changed += 1
            elif isinstance(value, (dict, list)):
                changed += patch_json_materials(value)
    elif isinstance(obj, list):
        for item in obj:
            changed += patch_json_materials(item)
    return changed


def patch_events() -> int:
    if not EVENTS.exists():
        return 0
    tmp = EVENTS.with_suffix(".jsonl.tmp")
    changed = 0
    with EVENTS.open("r", encoding="utf-8") as src, tmp.open("w", encoding="utf-8", newline="\n") as dst:
        for line in src:
            if not line.strip():
                continue
            obj = json.loads(line)
            changed += patch_json_materials(obj)
            dst.write(json.dumps(obj, ensure_ascii=False, separators=(",", ":")) + "\n")
    tmp.replace(EVENTS)
    return changed


def patch_nbt_materials(obj) -> int:
    changed = 0
    if isinstance(obj, nbtlib.Compound):
        for key in list(obj.keys()):
            value = obj[key]
            if str(key) == "material" and isinstance(value, nbtlib.String):
                old = str(value)
                new = converter_safe_material(old)
                if new != old:
                    obj[key] = nbtlib.String(new)
                    changed += 1
            else:
                changed += patch_nbt_materials(value)
    elif isinstance(obj, nbtlib.List):
        for item in obj:
            changed += patch_nbt_materials(item)
    return changed


def rewrite_chunk(region_data: bytearray, idx: int, nbt_file: nbtlib.File) -> tuple[bytearray, bool]:
    loc = region_data[idx * 4 : idx * 4 + 4]
    sector_off = (loc[0] << 16) | (loc[1] << 8) | loc[2]
    old_sector_count = loc[3]
    byte_off = sector_off * 4096

    buf = io.BytesIO()
    nbt_file.write(buf)
    new_comp = zlib.compress(buf.getvalue())
    new_len = len(new_comp) + 1
    new_sector_count = math.ceil((new_len + 4) / 4096)

    if new_sector_count <= old_sector_count:
        region_data[byte_off : byte_off + 4] = struct.pack(">I", new_len)
        region_data[byte_off + 4] = 2
        region_data[byte_off + 5 : byte_off + 5 + len(new_comp)] = new_comp
        return region_data, True

    if len(region_data) % 4096 != 0:
        region_data.extend(b"\x00" * (4096 - len(region_data) % 4096))
    new_start = len(region_data) // 4096
    chunk_bytes = struct.pack(">I", new_len) + b"\x02" + new_comp
    chunk_bytes += b"\x00" * (new_sector_count * 4096 - len(chunk_bytes))
    region_data.extend(chunk_bytes)
    region_data[idx * 4 : idx * 4 + 4] = bytes([
        (new_start >> 16) & 0xFF,
        (new_start >> 8) & 0xFF,
        new_start & 0xFF,
        new_sector_count,
    ])
    return region_data, True


def patch_world() -> int:
    changed = 0
    for path in sorted((WORLD / "region").glob("*.mca")):
        region_data = bytearray(path.read_bytes())
        region_dirty = False
        for idx in range(1024):
            loc = region_data[idx * 4 : idx * 4 + 4]
            sector_off = (loc[0] << 16) | (loc[1] << 8) | loc[2]
            if sector_off == 0:
                continue
            byte_off = sector_off * 4096
            length = struct.unpack(">I", bytes(region_data[byte_off : byte_off + 4]))[0]
            comp_type = region_data[byte_off + 4]
            if comp_type != 2:
                continue
            raw = zlib.decompress(bytes(region_data[byte_off + 5 : byte_off + 5 + length - 1]))
            nbt_file = nbtlib.File.from_fileobj(io.BytesIO(raw), byteorder="big")
            chunk_changes = patch_nbt_materials(nbt_file)
            if chunk_changes:
                changed += chunk_changes
                region_data, _ = rewrite_chunk(region_data, idx, nbt_file)
                region_dirty = True
        if region_dirty:
            path.write_bytes(region_data)
            print(f"patched {path.name}")
    return changed


def main():
    event_changes = patch_events()
    world_changes = patch_world()
    print(f"events material changes: {event_changes}")
    print(f"world material changes : {world_changes}")


if __name__ == "__main__":
    main()
