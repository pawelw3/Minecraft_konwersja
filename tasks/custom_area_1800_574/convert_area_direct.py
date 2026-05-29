#!/usr/bin/env python3
"""Direct converter for custom_area_1800_574.

This bypasses Amulet, which hangs while opening the 1.7.10 world on this area.
It writes 1.18.2 MCA chunks directly for vanilla/safe blocks, then applies the
already generated mod conversion events through the JVM worker.
"""

from __future__ import annotations

import io
import json
import math
import shutil
import struct
import subprocess
import sys
import threading
import time
import zlib
from collections import defaultdict
from pathlib import Path

import nbtlib  # type: ignore

SCRIPT_DIR = Path(__file__).resolve().parent
ROOT = SCRIPT_DIR.parents[1]
sys.path.insert(0, str(ROOT / "src"))

from minecraft_map_parser.anvil_parser import AnvilParser  # noqa: E402

SRC_WORLD = ROOT / "mapa_1710"
DST_WORLD = SCRIPT_DIR / "world"
EVENTS_FILE = SCRIPT_DIR / "events.jsonl"
WORKER_JAR = ROOT / "jvm" / "worker" / "build" / "libs" / "mc-editkit-worker-1.0-SNAPSHOT.jar"
LOG_FILE = SCRIPT_DIR / "direct_conversion.log"

TEMPLATES = [
    ROOT / "lightweigh_map_templates" / "118_modded" / "ae2_1",
    ROOT / "lightweigh_map_templates" / "118_modded" / "konwersja3",
    ROOT / "headless_server" / "1.18.2" / "world",
]

CHUNK_X_MIN = -113
CHUNK_X_MAX = -73
CHUNK_Z_MIN = -63
CHUNK_Z_MAX = -36
X_MIN = CHUNK_X_MIN * 16
X_MAX = CHUNK_X_MAX * 16 + 15
Z_MIN = CHUNK_Z_MIN * 16
Z_MAX = CHUNK_Z_MAX * 16 + 15
SPAWN_X = (X_MIN + X_MAX) // 2
SPAWN_Y = 80
SPAWN_Z = (Z_MIN + Z_MAX) // 2

DATA_VERSION_1182 = 2975
PROGRESS_INTERVAL_SECONDS = 60.0


class Tee:
    def __init__(self, *streams):
        self.streams = streams

    def write(self, data):
        for stream in self.streams:
            stream.write(data)
            stream.flush()

    def flush(self):
        for stream in self.streams:
            stream.flush()


class ProgressReporter:
    def __init__(self, label: str, total: int | None = None):
        self.label = label
        self.total = total
        self.done = 0
        self.detail = ""
        self.started = time.monotonic()
        self._lock = threading.Lock()
        self._stop = threading.Event()
        self._thread = threading.Thread(target=self._run, daemon=True)

    def __enter__(self):
        print(self._format("started"), flush=True)
        self._thread.start()
        return self

    def __exit__(self, exc_type, exc, tb):
        self._stop.set()
        self._thread.join(timeout=2.0)
        print(self._format("failed" if exc_type else "done"), flush=True)
        return False

    def update(self, done: int | None = None, detail: str | None = None):
        with self._lock:
            if done is not None:
                self.done = done
            if detail is not None:
                self.detail = detail

    def _run(self):
        while not self._stop.wait(PROGRESS_INTERVAL_SECONDS):
            print(self._format("progress"), flush=True)

    def _format(self, status: str) -> str:
        elapsed = time.monotonic() - self.started
        with self._lock:
            done = self.done
            total = self.total
            detail = self.detail
        if total:
            pct = min(100.0, done * 100.0 / total)
            msg = f"[{status}] {self.label}: {done}/{total} ({pct:.1f}%), elapsed {elapsed:.0f}s"
            if done > 0 and status == "progress":
                rate = done / elapsed if elapsed else 0.0
                eta = (total - done) / rate if rate else 0.0
                msg += f", rate {rate:.2f}/s, eta {eta:.0f}s"
        else:
            msg = f"[{status}] {self.label}: elapsed {elapsed:.0f}s"
        if detail:
            msg += f" | {detail}"
        return "      " + msg


def chunks_in_area():
    for cx in range(CHUNK_X_MIN, CHUNK_X_MAX + 1):
        for cz in range(CHUNK_Z_MIN, CHUNK_Z_MAX + 1):
            yield cx, cz


def regions_needed() -> set[tuple[int, int]]:
    return {(cx // 32, cz // 32) for cx, cz in chunks_in_area()}


def global_to_local_chunk(gcx: int, gcz: int) -> tuple[int, int]:
    rx, rz = gcx // 32, gcz // 32
    return gcx - rx * 32, gcz - rz * 32


def find_template() -> Path:
    for template in TEMPLATES:
        if (template / "level.dat").exists():
            return template
    raise FileNotFoundError("No 1.18.2 template world found")


def prepare_world():
    template = find_template()
    print(f"\n[1/6] Preparing world from template: {template}")
    if DST_WORLD.exists():
        shutil.rmtree(DST_WORLD)
    shutil.copytree(template, DST_WORLD)
    region_dir = DST_WORLD / "region"
    region_dir.mkdir(exist_ok=True)
    for path in region_dir.glob("*.mca"):
        path.unlink()
    print(f"      target: {DST_WORLD}")


def source_region_parsers() -> dict[tuple[int, int], AnvilParser]:
    parsers = {}
    for rx, rz in sorted(regions_needed()):
        path = SRC_WORLD / "region" / f"r.{rx}.{rz}.mca"
        if path.exists():
            parsers[(rx, rz)] = AnvilParser(str(path))
    if not parsers:
        raise FileNotFoundError("No source region files found for requested area")
    return parsers


VANILLA_BLOCKS: dict[tuple[int, int | None], str] = {
    (0, None): "minecraft:air",
    (1, 0): "minecraft:stone",
    (1, 1): "minecraft:granite",
    (1, 2): "minecraft:polished_granite",
    (1, 3): "minecraft:diorite",
    (1, 4): "minecraft:polished_diorite",
    (1, 5): "minecraft:andesite",
    (1, 6): "minecraft:polished_andesite",
    (2, None): "minecraft:grass_block",
    (3, 0): "minecraft:dirt",
    (3, 1): "minecraft:coarse_dirt",
    (3, 2): "minecraft:podzol",
    (4, None): "minecraft:cobblestone",
    (5, 0): "minecraft:oak_planks",
    (5, 1): "minecraft:spruce_planks",
    (5, 2): "minecraft:birch_planks",
    (5, 3): "minecraft:jungle_planks",
    (5, 4): "minecraft:acacia_planks",
    (5, 5): "minecraft:dark_oak_planks",
    (7, None): "minecraft:bedrock",
    (8, None): "minecraft:water",
    (9, None): "minecraft:water",
    (10, None): "minecraft:lava",
    (11, None): "minecraft:lava",
    (12, 0): "minecraft:sand",
    (12, 1): "minecraft:red_sand",
    (13, None): "minecraft:gravel",
    (14, None): "minecraft:gold_ore",
    (15, None): "minecraft:iron_ore",
    (16, None): "minecraft:coal_ore",
    (17, 0): "minecraft:oak_log",
    (17, 1): "minecraft:spruce_log",
    (17, 2): "minecraft:birch_log",
    (17, 3): "minecraft:jungle_log",
    (18, 0): "minecraft:oak_leaves",
    (18, 1): "minecraft:spruce_leaves",
    (18, 2): "minecraft:birch_leaves",
    (18, 3): "minecraft:jungle_leaves",
    (20, None): "minecraft:glass",
    (21, None): "minecraft:lapis_ore",
    (22, None): "minecraft:lapis_block",
    (24, 0): "minecraft:sandstone",
    (24, 1): "minecraft:chiseled_sandstone",
    (24, 2): "minecraft:cut_sandstone",
    (31, 1): "minecraft:grass",
    (31, 2): "minecraft:fern",
    (32, None): "minecraft:dead_bush",
    (35, None): "minecraft:white_wool",
    (37, None): "minecraft:dandelion",
    (38, None): "minecraft:poppy",
    (39, None): "minecraft:brown_mushroom",
    (40, None): "minecraft:red_mushroom",
    (41, None): "minecraft:gold_block",
    (42, None): "minecraft:iron_block",
    (44, None): "minecraft:smooth_stone_slab",
    (45, None): "minecraft:bricks",
    (46, None): "minecraft:tnt",
    (47, None): "minecraft:bookshelf",
    (48, None): "minecraft:mossy_cobblestone",
    (49, None): "minecraft:obsidian",
    (50, None): "minecraft:torch",
    (56, None): "minecraft:diamond_ore",
    (57, None): "minecraft:diamond_block",
    (60, None): "minecraft:farmland",
    (79, None): "minecraft:ice",
    (80, None): "minecraft:snow_block",
    (81, None): "minecraft:cactus",
    (82, None): "minecraft:clay",
    (86, None): "minecraft:pumpkin",
    (87, None): "minecraft:netherrack",
    (88, None): "minecraft:soul_sand",
    (89, None): "minecraft:glowstone",
    (98, 0): "minecraft:stone_bricks",
    (98, 1): "minecraft:mossy_stone_bricks",
    (98, 2): "minecraft:cracked_stone_bricks",
    (98, 3): "minecraft:chiseled_stone_bricks",
    (103, None): "minecraft:melon",
    (110, None): "minecraft:mycelium",
    (112, None): "minecraft:nether_bricks",
    (121, None): "minecraft:end_stone",
    (129, None): "minecraft:emerald_ore",
    (133, None): "minecraft:emerald_block",
    (152, None): "minecraft:redstone_block",
    (155, 0): "minecraft:quartz_block",
    (155, 1): "minecraft:chiseled_quartz_block",
    (155, 2): "minecraft:quartz_pillar",
    (159, None): "minecraft:white_terracotta",
    (162, 0): "minecraft:acacia_log",
    (162, 1): "minecraft:dark_oak_log",
    (161, 0): "minecraft:acacia_leaves",
    (161, 1): "minecraft:dark_oak_leaves",
    (172, None): "minecraft:terracotta",
    (173, None): "minecraft:coal_block",
    (174, None): "minecraft:packed_ice",
    (179, 0): "minecraft:red_sandstone",
    (179, 1): "minecraft:chiseled_red_sandstone",
    (179, 2): "minecraft:cut_red_sandstone",
}


def map_block(block_id: int, meta: int) -> str:
    if block_id == 0:
        return "minecraft:air"
    return (
        VANILLA_BLOCKS.get((block_id, meta & 0xF))
        or VANILLA_BLOCKS.get((block_id, None))
        or "minecraft:air"
    )


def to_signed_long(value: int) -> int:
    value &= (1 << 64) - 1
    if value >= (1 << 63):
        value -= 1 << 64
    return value


def pack_values(values: list[int], bits: int) -> list[int]:
    values_per_long = 64 // bits
    mask = (1 << bits) - 1
    longs = [0] * math.ceil(len(values) / values_per_long)
    for i, value in enumerate(values):
        long_index = i // values_per_long
        bit_index = (i % values_per_long) * bits
        longs[long_index] |= (value & mask) << bit_index
    return [to_signed_long(v) for v in longs]


def make_palette_entry(name: str):
    return nbtlib.Compound({"Name": nbtlib.String(name)})


def make_section(section_y: int, names: list[str]):
    palette_names: list[str] = []
    palette_index: dict[str, int] = {}
    indices: list[int] = []
    for name in names:
        idx = palette_index.get(name)
        if idx is None:
            idx = len(palette_names)
            palette_names.append(name)
            palette_index[name] = idx
        indices.append(idx)

    block_states = nbtlib.Compound({
        "palette": nbtlib.List[nbtlib.Compound]([make_palette_entry(n) for n in palette_names])
    })
    if len(palette_names) > 1:
        bits = max(4, math.ceil(math.log2(len(palette_names))))
        block_states["data"] = nbtlib.LongArray(pack_values(indices, bits))

    return nbtlib.Compound({
        "Y": nbtlib.Byte(section_y),
        "block_states": block_states,
        "biomes": nbtlib.Compound({
            "palette": nbtlib.List[nbtlib.String]([nbtlib.String("minecraft:plains")])
        }),
    })


def make_empty_section(section_y: int):
    return make_section(section_y, ["minecraft:air"] * 4096)


def make_heightmap(heights: list[int]) -> nbtlib.LongArray:
    return nbtlib.LongArray(pack_values(heights, 9))


def build_chunk_nbt(gcx: int, gcz: int, block_meta: dict[tuple[int, int, int], tuple[int, int]]):
    sections = []
    heightmap = [0] * 256

    for section_y in range(-4, 20):
        if section_y < 0 or section_y > 15:
            sections.append(make_empty_section(section_y))
            continue

        names = []
        non_air = False
        for y_in_section in range(16):
            y = section_y * 16 + y_in_section
            for z in range(16):
                for x in range(16):
                    block_id, meta = block_meta.get((x, y, z), (0, 0))
                    name = map_block(block_id, meta)
                    names.append(name)
                    if name != "minecraft:air":
                        non_air = True
                        idx = z * 16 + x
                        heightmap[idx] = max(heightmap[idx], y + 1)
        sections.append(make_section(section_y, names) if non_air else make_empty_section(section_y))

    root = nbtlib.Compound({
        "DataVersion": nbtlib.Int(DATA_VERSION_1182),
        "xPos": nbtlib.Int(gcx),
        "zPos": nbtlib.Int(gcz),
        "yPos": nbtlib.Int(-4),
        "Status": nbtlib.String("minecraft:full"),
        "LastUpdate": nbtlib.Long(0),
        "InhabitedTime": nbtlib.Long(0),
        "isLightOn": nbtlib.Byte(0),
        "sections": nbtlib.List[nbtlib.Compound](sections),
        "block_entities": nbtlib.List[nbtlib.Compound]([]),
        "entities": nbtlib.List[nbtlib.Compound]([]),
        "fluid_ticks": nbtlib.List[nbtlib.Compound]([]),
        "block_ticks": nbtlib.List[nbtlib.Compound]([]),
        "PostProcessing": nbtlib.List[nbtlib.List[nbtlib.Short]]([]),
        "Heightmaps": nbtlib.Compound({
            "MOTION_BLOCKING": make_heightmap(heightmap),
            "MOTION_BLOCKING_NO_LEAVES": make_heightmap(heightmap),
            "WORLD_SURFACE": make_heightmap(heightmap),
            "WORLD_SURFACE_WG": make_heightmap(heightmap),
        }),
        "structures": nbtlib.Compound({
            "starts": nbtlib.Compound({}),
            "References": nbtlib.Compound({}),
        }),
    })
    return nbtlib.File(root)


def chunk_to_bytes(chunk_file: nbtlib.File) -> bytes:
    raw = io.BytesIO()
    chunk_file.write(raw)
    compressed = zlib.compress(raw.getvalue())
    return struct.pack(">I", len(compressed) + 1) + b"\x02" + compressed


def write_region_file(region_path: Path, chunks: dict[tuple[int, int], bytes]):
    header = bytearray(8192)
    body = bytearray()
    sector = 2
    for (lcx, lcz), chunk_bytes in sorted(chunks.items(), key=lambda kv: kv[0][0] + kv[0][1] * 32):
        sectors = math.ceil(len(chunk_bytes) / 4096)
        padded = chunk_bytes + b"\x00" * (sectors * 4096 - len(chunk_bytes))
        idx = lcx + lcz * 32
        header[idx * 4 : idx * 4 + 4] = bytes([
            (sector >> 16) & 0xFF,
            (sector >> 8) & 0xFF,
            sector & 0xFF,
            sectors & 0xFF,
        ])
        timestamp_offset = 4096 + idx * 4
        header[timestamp_offset : timestamp_offset + 4] = struct.pack(">I", int(time.time()))
        body.extend(padded)
        sector += sectors
    region_path.parent.mkdir(parents=True, exist_ok=True)
    with region_path.open("wb") as f:
        f.write(header)
        f.write(body)


def write_vanilla_terrain():
    print("\n[2/6] Writing 1.18.2 terrain chunks directly")
    parsers = source_region_parsers()
    region_chunks: dict[tuple[int, int], dict[tuple[int, int], bytes]] = defaultdict(dict)
    total = (CHUNK_X_MAX - CHUNK_X_MIN + 1) * (CHUNK_Z_MAX - CHUNK_Z_MIN + 1)
    done = 0
    written = 0
    missing = 0
    with ProgressReporter("Direct terrain conversion", total=total) as progress:
        for gcx, gcz in chunks_in_area():
            rx, rz = gcx // 32, gcz // 32
            parser = parsers.get((rx, rz))
            done += 1
            if parser is None:
                missing += 1
                progress.update(done, f"chunk=({gcx},{gcz}) written={written} missing={missing}")
                continue
            lcx, lcz = global_to_local_chunk(gcx, gcz)
            src_chunk = parser.get_chunk(lcx, lcz)
            if src_chunk is None:
                missing += 1
                progress.update(done, f"chunk=({gcx},{gcz}) written={written} missing={missing}")
                continue

            chunk_nbt = build_chunk_nbt(gcx, gcz, src_chunk.get_blocks_and_metadata_at_positions())
            region_chunks[(rx, rz)][(lcx, lcz)] = chunk_to_bytes(chunk_nbt)
            written += 1
            progress.update(done, f"chunk=({gcx},{gcz}) written={written} missing={missing}")

    for (rx, rz), chunks in sorted(region_chunks.items()):
        path = DST_WORLD / "region" / f"r.{rx}.{rz}.mca"
        write_region_file(path, chunks)
        print(f"      wrote {path.name}: {len(chunks)} chunks")
    print(f"      chunks written: {written}, missing: {missing}")


def patch_level_dat():
    print("\n[3/6] Patching level.dat")
    level_dat = DST_WORLD / "level.dat"
    level = nbtlib.load(str(level_dat), gzipped=True)
    data = level["Data"]
    data["SpawnX"] = nbtlib.Int(SPAWN_X)
    data["SpawnY"] = nbtlib.Int(SPAWN_Y)
    data["SpawnZ"] = nbtlib.Int(SPAWN_Z)
    data["GameType"] = nbtlib.Int(1)
    data["allowCommands"] = nbtlib.Byte(1)
    data["Difficulty"] = nbtlib.Byte(0)
    data["LevelName"] = nbtlib.String("Custom Area 1800 574 Direct")
    level.save()
    print(f"      spawn: ({SPAWN_X}, {SPAWN_Y}, {SPAWN_Z})")


def apply_mod_events():
    print("\n[4/6] Applying mod conversion events")
    if not EVENTS_FILE.exists() or EVENTS_FILE.stat().st_size == 0:
        print("      no events file, skipping")
        return
    if not WORKER_JAR.exists():
        raise FileNotFoundError(f"Worker JAR not found: {WORKER_JAR}")
    event_count = sum(1 for _ in EVENTS_FILE.open("r", encoding="utf-8"))
    with ProgressReporter("JVM Worker apply events", total=event_count) as progress:
        progress.update(0, f"events_file={EVENTS_FILE.name}")
        result = subprocess.run(
            [
                "java",
                "-jar",
                str(WORKER_JAR),
                "--apply-events",
                str(EVENTS_FILE),
                "--target-world",
                str(DST_WORLD),
            ],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
        )
        progress.update(event_count, "worker process finished")
    print(result.stdout)
    if result.returncode != 0:
        print(result.stderr[-2000:])
        raise RuntimeError(f"JVM worker failed with code {result.returncode}")


def convert_backpacks():
    print("\n[5/6] Converting Backpack mod data")
    backpacks_dir = SRC_WORLD / "backpacks" / "backpacks"
    if not backpacks_dir.exists():
        print("      no backpacks dir, skipping")
        return
    from converters.backpack.backpack_converter import BackpackBatchConverter  # noqa: E402

    report = BackpackBatchConverter(source_world=SRC_WORLD, target_world=DST_WORLD).convert_all()
    print(json.dumps(report, indent=2, ensure_ascii=False)[:4000])


def verify_output():
    print("\n[6/6] Verifying output files")
    region_files = sorted((DST_WORLD / "region").glob("*.mca"))
    print(f"      region files: {len(region_files)}")
    for path in region_files:
        print(f"      {path.name}: {path.stat().st_size} bytes")
    print(f"      world: {DST_WORLD}")


def main():
    with LOG_FILE.open("w", encoding="utf-8") as log:
        old_stdout = sys.stdout
        old_stderr = sys.stderr
        sys.stdout = Tee(old_stdout, log)
        sys.stderr = Tee(old_stderr, log)
        try:
            print("=" * 70)
            print("Direct Custom Area Converter 1.7.10 -> 1.18.2")
            print(f"Area: X={X_MIN}..{X_MAX}, Z={Z_MIN}..{Z_MAX}")
            print(f"Chunks: {(CHUNK_X_MAX - CHUNK_X_MIN + 1) * (CHUNK_Z_MAX - CHUNK_Z_MIN + 1)}")
            print(f"Log: {LOG_FILE}")
            print("=" * 70)
            prepare_world()
            write_vanilla_terrain()
            patch_level_dat()
            apply_mod_events()
            convert_backpacks()
            verify_output()
            print("\nDONE")
        finally:
            sys.stdout = old_stdout
            sys.stderr = old_stderr


if __name__ == "__main__":
    main()
