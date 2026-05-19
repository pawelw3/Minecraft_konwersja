#!/usr/bin/env python3
"""Generate streamed 1.18.2 set_block events for vanilla blocks in the ZSRR slice.

The source 1.7.10 world is read-only. The output is JSONL on purpose: one
event per line lets the JVM worker apply millions of terrain blocks without
loading the full event list into memory.
"""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parents[2]
SCENARIO_DIR = Path(__file__).resolve().parent
DEFAULT_WORLD = PROJECT_ROOT / "lightweigh_map_templates" / "1710_modded" / "zsrr_ae2_mek_300"
DEFAULT_EVENTS = SCENARIO_DIR / "zsrr_ae2_mek_vanilla_blocks_1182.jsonl"
DEFAULT_REPORT = SCENARIO_DIR / "zsrr_ae2_mek_vanilla_blocks_report.json"

sys.path.insert(0, str(PROJECT_ROOT))
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from minecraft_map_parser.anvil_parser import AnvilParser  # noqa: E402
from src.converters.mekanism.analyze_map_coverage import (  # noqa: E402
    get_nibble,
    section_arrays,
)


COLORS = [
    "white",
    "orange",
    "magenta",
    "light_blue",
    "yellow",
    "lime",
    "pink",
    "gray",
    "light_gray",
    "cyan",
    "purple",
    "blue",
    "brown",
    "green",
    "red",
    "black",
]

WOOD = ["oak", "spruce", "birch", "jungle"]
WOOD2 = ["acacia", "dark_oak"]
STONE_VARIANTS = [
    "minecraft:stone",
    "minecraft:granite",
    "minecraft:polished_granite",
    "minecraft:diorite",
    "minecraft:polished_diorite",
    "minecraft:andesite",
    "minecraft:polished_andesite",
]
DIRT_VARIANTS = ["minecraft:dirt", "minecraft:coarse_dirt", "minecraft:podzol"]
SANDSTONE_VARIANTS = ["minecraft:sandstone", "minecraft:chiseled_sandstone", "minecraft:cut_sandstone"]
STONEBRICK_VARIANTS = [
    "minecraft:stone_bricks",
    "minecraft:mossy_stone_bricks",
    "minecraft:cracked_stone_bricks",
    "minecraft:chiseled_stone_bricks",
]
FLOWERS = [
    "minecraft:poppy",
    "minecraft:blue_orchid",
    "minecraft:allium",
    "minecraft:azure_bluet",
    "minecraft:red_tulip",
    "minecraft:orange_tulip",
    "minecraft:white_tulip",
    "minecraft:pink_tulip",
    "minecraft:oxeye_daisy",
]
PRISMARINE = ["minecraft:prismarine", "minecraft:prismarine_bricks", "minecraft:dark_prismarine"]
QUARTZ = ["minecraft:quartz_block", "minecraft:chiseled_quartz_block", "minecraft:quartz_pillar"]
DOUBLE_PLANT = ["sunflower", "lilac", "tall_grass", "large_fern", "rose_bush", "peony"]

DIRECT: dict[int, str] = {
    2: "minecraft:grass_block",
    4: "minecraft:cobblestone",
    7: "minecraft:bedrock",
    8: "minecraft:water",
    9: "minecraft:water",
    10: "minecraft:lava",
    11: "minecraft:lava",
    13: "minecraft:gravel",
    14: "minecraft:gold_ore",
    15: "minecraft:iron_ore",
    16: "minecraft:coal_ore",
    19: "minecraft:wet_sponge",
    20: "minecraft:glass",
    21: "minecraft:lapis_ore",
    22: "minecraft:lapis_block",
    23: "minecraft:dispenser",
    25: "minecraft:note_block",
    26: "minecraft:red_bed",
    27: "minecraft:powered_rail",
    28: "minecraft:detector_rail",
    29: "minecraft:sticky_piston",
    30: "minecraft:cobweb",
    32: "minecraft:dead_bush",
    33: "minecraft:piston",
    35: "minecraft:white_wool",
    37: "minecraft:dandelion",
    39: "minecraft:brown_mushroom",
    40: "minecraft:red_mushroom",
    41: "minecraft:gold_block",
    42: "minecraft:iron_block",
    45: "minecraft:bricks",
    46: "minecraft:tnt",
    47: "minecraft:bookshelf",
    48: "minecraft:mossy_cobblestone",
    49: "minecraft:obsidian",
    50: "minecraft:torch",
    51: "minecraft:fire",
    52: "minecraft:spawner",
    53: "minecraft:oak_stairs",
    54: "minecraft:chest",
    55: "minecraft:redstone_wire",
    56: "minecraft:diamond_ore",
    57: "minecraft:diamond_block",
    58: "minecraft:crafting_table",
    59: "minecraft:wheat",
    60: "minecraft:farmland",
    61: "minecraft:furnace",
    62: "minecraft:furnace",
    63: "minecraft:oak_sign",
    64: "minecraft:oak_door",
    65: "minecraft:ladder",
    66: "minecraft:rail",
    67: "minecraft:cobblestone_stairs",
    68: "minecraft:oak_wall_sign",
    69: "minecraft:lever",
    70: "minecraft:stone_pressure_plate",
    71: "minecraft:iron_door",
    72: "minecraft:oak_pressure_plate",
    73: "minecraft:redstone_ore",
    74: "minecraft:redstone_ore",
    75: "minecraft:redstone_torch",
    76: "minecraft:redstone_torch",
    77: "minecraft:stone_button",
    78: "minecraft:snow",
    79: "minecraft:ice",
    80: "minecraft:snow_block",
    81: "minecraft:cactus",
    82: "minecraft:clay",
    83: "minecraft:sugar_cane",
    84: "minecraft:jukebox",
    85: "minecraft:oak_fence",
    86: "minecraft:pumpkin",
    87: "minecraft:netherrack",
    88: "minecraft:soul_sand",
    89: "minecraft:glowstone",
    90: "minecraft:nether_portal",
    91: "minecraft:jack_o_lantern",
    92: "minecraft:cake",
    93: "minecraft:repeater",
    94: "minecraft:repeater",
    96: "minecraft:oak_trapdoor",
    101: "minecraft:iron_bars",
    102: "minecraft:glass_pane",
    103: "minecraft:melon",
    104: "minecraft:pumpkin_stem",
    105: "minecraft:melon_stem",
    106: "minecraft:vine",
    107: "minecraft:oak_fence_gate",
    108: "minecraft:brick_stairs",
    109: "minecraft:stone_brick_stairs",
    110: "minecraft:mycelium",
    111: "minecraft:lily_pad",
    112: "minecraft:nether_bricks",
    113: "minecraft:nether_brick_fence",
    114: "minecraft:nether_brick_stairs",
    115: "minecraft:nether_wart",
    116: "minecraft:enchanting_table",
    117: "minecraft:brewing_stand",
    118: "minecraft:cauldron",
    120: "minecraft:end_portal_frame",
    121: "minecraft:end_stone",
    122: "minecraft:dragon_egg",
    123: "minecraft:redstone_lamp",
    124: "minecraft:redstone_lamp",
    127: "minecraft:cocoa",
    128: "minecraft:sandstone_stairs",
    129: "minecraft:emerald_ore",
    130: "minecraft:ender_chest",
    131: "minecraft:tripwire_hook",
    132: "minecraft:tripwire",
    133: "minecraft:emerald_block",
    134: "minecraft:spruce_stairs",
    135: "minecraft:birch_stairs",
    136: "minecraft:jungle_stairs",
    137: "minecraft:command_block",
    138: "minecraft:beacon",
    140: "minecraft:flower_pot",
    141: "minecraft:carrots",
    142: "minecraft:potatoes",
    143: "minecraft:oak_button",
    144: "minecraft:skeleton_skull",
    145: "minecraft:anvil",
    146: "minecraft:trapped_chest",
    147: "minecraft:light_weighted_pressure_plate",
    148: "minecraft:heavy_weighted_pressure_plate",
    149: "minecraft:comparator",
    150: "minecraft:comparator",
    151: "minecraft:daylight_detector",
    152: "minecraft:redstone_block",
    153: "minecraft:nether_quartz_ore",
    154: "minecraft:hopper",
    156: "minecraft:quartz_stairs",
    157: "minecraft:activator_rail",
    158: "minecraft:dropper",
    165: "minecraft:slime_block",
    166: "minecraft:barrier",
    167: "minecraft:iron_trapdoor",
    169: "minecraft:sea_lantern",
    170: "minecraft:hay_block",
    172: "minecraft:terracotta",
    173: "minecraft:coal_block",
    174: "minecraft:packed_ice",
}


def axis_from_log_meta(meta: int) -> str:
    return {0: "y", 4: "x", 8: "z", 12: "y"}.get(meta & 12, "y")


def target_for(numeric_id: int, meta: int) -> tuple[str, dict[str, str]] | None:
    if numeric_id == 0:
        return None
    if numeric_id == 1:
        return STONE_VARIANTS[meta] if 0 <= meta < len(STONE_VARIANTS) else "minecraft:stone", {}
    if numeric_id == 3:
        return DIRT_VARIANTS[meta] if 0 <= meta < len(DIRT_VARIANTS) else "minecraft:dirt", {}
    if numeric_id == 5:
        return f"minecraft:{WOOD[meta & 3]}_planks", {}
    if numeric_id == 6:
        return f"minecraft:{WOOD[meta & 3]}_sapling", {}
    if numeric_id == 12:
        return ("minecraft:red_sand" if meta == 1 else "minecraft:sand"), {}
    if numeric_id == 17:
        return f"minecraft:{WOOD[meta & 3]}_log", {"axis": axis_from_log_meta(meta)}
    if numeric_id == 18:
        return f"minecraft:{WOOD[meta & 3]}_leaves", {"persistent": "true"}
    if numeric_id == 24:
        return SANDSTONE_VARIANTS[meta] if 0 <= meta < len(SANDSTONE_VARIANTS) else "minecraft:sandstone", {}
    if numeric_id == 31:
        return ("minecraft:fern" if meta == 2 else "minecraft:grass"), {}
    if numeric_id == 35:
        return f"minecraft:{COLORS[meta & 15]}_wool", {}
    if numeric_id == 38:
        return FLOWERS[meta] if 0 <= meta < len(FLOWERS) else "minecraft:poppy", {}
    if numeric_id == 43:
        return "minecraft:smooth_stone", {}
    if numeric_id == 44:
        return "minecraft:smooth_stone_slab", {}
    if numeric_id == 95:
        return f"minecraft:{COLORS[meta & 15]}_stained_glass", {}
    if numeric_id == 97:
        variants = ["stone", "cobblestone", "stone_bricks", "mossy_stone_bricks", "cracked_stone_bricks", "chiseled_stone_bricks"]
        return f"minecraft:infested_{variants[meta] if 0 <= meta < len(variants) else 'stone'}", {}
    if numeric_id == 98:
        return STONEBRICK_VARIANTS[meta] if 0 <= meta < len(STONEBRICK_VARIANTS) else "minecraft:stone_bricks", {}
    if numeric_id in {99, 100}:
        return ("minecraft:brown_mushroom_block" if numeric_id == 99 else "minecraft:red_mushroom_block"), {}
    if numeric_id == 125:
        return f"minecraft:{WOOD[meta & 3]}_planks", {}
    if numeric_id == 126:
        return f"minecraft:{WOOD[meta & 3]}_slab", {}
    if numeric_id == 139:
        return ("minecraft:mossy_cobblestone_wall" if meta == 1 else "minecraft:cobblestone_wall"), {}
    if numeric_id == 155:
        return QUARTZ[meta] if 0 <= meta < len(QUARTZ) else "minecraft:quartz_block", {}
    if numeric_id == 159:
        return f"minecraft:{COLORS[meta & 15]}_terracotta", {}
    if numeric_id == 160:
        return f"minecraft:{COLORS[meta & 15]}_stained_glass_pane", {}
    if numeric_id == 161:
        return f"minecraft:{WOOD2[meta & 1]}_leaves", {"persistent": "true"}
    if numeric_id == 162:
        return f"minecraft:{WOOD2[meta & 1]}_log", {"axis": axis_from_log_meta(meta)}
    if numeric_id == 163:
        return "minecraft:acacia_stairs", {}
    if numeric_id == 164:
        return "minecraft:dark_oak_stairs", {}
    if numeric_id == 168:
        return PRISMARINE[meta] if 0 <= meta < len(PRISMARINE) else "minecraft:prismarine", {}
    if numeric_id == 171:
        return f"minecraft:{COLORS[meta & 15]}_carpet", {}
    if numeric_id == 175:
        return f"minecraft:{DOUBLE_PLANT[meta] if 0 <= meta < len(DOUBLE_PLANT) else 'sunflower'}", {}
    block = DIRECT.get(numeric_id)
    if block:
        return block, {}
    return None


def iter_vanilla_blocks(world: Path):
    for region_file in sorted((world / "region").glob("r.*.*.mca")):
        parser = AnvilParser(str(region_file))
        for chunk in parser.get_all_chunks():
            chunk_x0 = chunk.x * 16
            chunk_z0 = chunk.z * 16
            for section in chunk.get_sections():
                section_y, blocks, add, data = section_arrays(section)
                if blocks is None:
                    continue
                max_index = min(4096, len(blocks))
                base_y = section_y * 16
                for index in range(max_index):
                    numeric_id = (get_nibble(add, index) << 8) | (blocks[index] & 0xFF)
                    if numeric_id == 0 or numeric_id > 175:
                        continue
                    meta = get_nibble(data, index)
                    target = target_for(numeric_id, meta)
                    if target is None:
                        yield None, numeric_id, meta, None
                        continue
                    local_x = index & 0x0F
                    local_z = (index >> 4) & 0x0F
                    local_y = (index >> 8) & 0x0F
                    x = chunk_x0 + local_x
                    y = base_y + local_y
                    z = chunk_z0 + local_z
                    block, state = target
                    yield (x, y, z, block, state), numeric_id, meta, region_file.name


def write_json(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def generate(world: Path, out_events: Path, report_path: Path) -> dict[str, Any]:
    out_events.parent.mkdir(parents=True, exist_ok=True)
    stats = Counter()
    by_source = Counter()
    by_target = Counter()
    unsupported = Counter()
    regions = Counter()

    with out_events.open("w", encoding="utf-8", newline="\n") as fh:
        for item, numeric_id, meta, region_name in iter_vanilla_blocks(world):
            source_key = f"{numeric_id}:{meta}"
            by_source[source_key] += 1
            if item is None:
                unsupported[source_key] += 1
                stats["unsupported"] += 1
                continue
            x, y, z, block, state = item
            event = {
                "op": "set_block",
                "pos": [x, y, z],
                "block": block,
                "blockstate": state,
                "source": {
                    "mod": "minecraft",
                    "numeric_id": numeric_id,
                    "metadata": meta,
                    "stage": "zsrr_ae2_mek_vanilla_blocks",
                },
            }
            fh.write(json.dumps(event, ensure_ascii=False, separators=(",", ":")) + "\n")
            stats["events"] += 1
            by_target[block] += 1
            if region_name:
                regions[region_name] += 1

    report = {
        "source_world": str(world),
        "events_file": str(out_events),
        "event_count": stats["events"],
        "unsupported_count": stats["unsupported"],
        "top_source_numeric_meta": dict(by_source.most_common(50)),
        "top_target_blocks": dict(by_target.most_common(50)),
        "top_unsupported_numeric_meta": dict(unsupported.most_common(50)),
        "events_by_region": dict(regions),
    }
    write_json(report_path, report)
    return report


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--world", type=Path, default=DEFAULT_WORLD)
    parser.add_argument("--out-events", type=Path, default=DEFAULT_EVENTS)
    parser.add_argument("--report", type=Path, default=DEFAULT_REPORT)
    args = parser.parse_args()

    report = generate(args.world, args.out_events, args.report)
    print(f"Vanilla block events: {report['event_count']}")
    print(f"Unsupported vanilla variants skipped: {report['unsupported_count']}")
    print(f"Events file: {args.out_events}")
    print(f"Report: {args.report}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
