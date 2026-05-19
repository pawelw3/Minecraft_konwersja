#!/usr/bin/env python3
"""
convert_zsrr_fragment.py

Converts the densest ZSRR area (X=-2748..-2649, Z=-2057..-1958) from the 1.7.10
modded map to a fresh 1.18.2 test world.

Pipeline
--------
1. Copy a 1.18.2 template world to test_worlds/zsrr_conversion_test/
2. Amulet  — bulk-copy ALL chunks (vanilla blocks translated, unknown mod blocks → air)
3. AnvilParser — scan 1.7.10 TileEntities, route each to a mod converter via router.py;
                 unsupported mods fall back to conversion_placeholders mod
4. JVM Worker  — apply the generated events.jsonl to the 1.18.2 world (Hephaistos)
5. Patch level.dat — spawn at area centre, creative mode, peaceful

Run
---
    python convert_zsrr_fragment.py

Requirements
------------
    pip install amulet-core nbtlib
    Java 17+ in PATH (for JVM Worker)
"""

from __future__ import annotations

import json
import shutil
import subprocess
import sys
from pathlib import Path

# ── project root on sys.path so src/ imports work ──────────────────────────
ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "src"))

from minecraft_map_parser.anvil_parser import AnvilParser
from converters.router import convert_te_to_events, detect_mod, VANILLA_TE_IDS

# ── constants ───────────────────────────────────────────────────────────────

SRC_WORLD   = ROOT / "mapa_1710"
DST_WORLD   = ROOT / "test_worlds" / "zsrr_conversion_test"

# Template preference order — first one with level.dat wins
_TEMPLATES = [
    ROOT / "lightweigh_map_templates" / "118_modded" / "ae2_1",
    ROOT / "lightweigh_map_templates" / "118_modded" / "konwersja3",
    ROOT / "headless_server"          / "1.18.2"     / "world",
]

EVENTS_FILE = ROOT / "output" / "zsrr_events.jsonl"
WORKER_JAR  = ROOT / "jvm" / "worker" / "build" / "libs" / "mc-editkit-worker-1.0-SNAPSHOT.jar"

# Bounding box (block coordinates, inclusive)
X_MIN, X_MAX = -2748, -2649
Z_MIN, Z_MAX = -2057, -1958

# Chunk range (Python floor division handles negatives correctly)
CHUNK_X_MIN = X_MIN // 16   # -172
CHUNK_X_MAX = X_MAX // 16   # -166
CHUNK_Z_MIN = Z_MIN // 16   # -129
CHUNK_Z_MAX = Z_MAX // 16   # -123

# Spawn: centre of the converted area, comfortable height
SPAWN_X = (X_MIN + X_MAX) // 2   # -2699
SPAWN_Y = 70
SPAWN_Z = (Z_MIN + Z_MAX) // 2   # -2007


# ── helpers ──────────────────────────────────────────────────────────────────

def _find_template() -> Path:
    for t in _TEMPLATES:
        if (t / "level.dat").exists():
            return t
    raise FileNotFoundError(
        "No usable 1.18.2 template found. Expected one of:\n"
        + "\n".join(f"  {t}" for t in _TEMPLATES)
    )


def _chunks_in_area():
    """Yield (global_cx, global_cz) for every chunk that overlaps the area."""
    for cx in range(CHUNK_X_MIN, CHUNK_X_MAX + 1):
        for cz in range(CHUNK_Z_MIN, CHUNK_Z_MAX + 1):
            yield cx, cz


def _regions_needed() -> set[tuple[int, int]]:
    return {(cx // 32, cz // 32) for cx, cz in _chunks_in_area()}


def _global_to_local_chunk(gcx: int, gcz: int) -> tuple[int, int]:
    """Global chunk coords → local (0-31) coords within their region file."""
    rx, rz = gcx // 32, gcz // 32
    lx = gcx - rx * 32
    lz = gcz - rz * 32
    if lx < 0:
        lx += 32
    if lz < 0:
        lz += 32
    return lx, lz


# ── step 1: create test world ────────────────────────────────────────────────

def step1_prepare_world():
    template = _find_template()
    print(f"\n[1/5] Preparing 1.18.2 test world")
    print(f"      template : {template}")
    print(f"      target   : {DST_WORLD}")

    if DST_WORLD.exists():
        shutil.rmtree(DST_WORLD)
    shutil.copytree(template, DST_WORLD)
    print("      done.")


# ── step 2: Amulet vanilla bulk copy ────────────────────────────────────────

def step2_amulet_vanilla_copy():
    print(f"\n[2/5] Amulet: bulk-copying chunks from 1.7.10")
    print(f"      chunks X {CHUNK_X_MIN}..{CHUNK_X_MAX}, Z {CHUNK_Z_MIN}..{CHUNK_Z_MAX}")

    import amulet  # type: ignore

    src = amulet.load_level(str(SRC_WORLD))
    dst = amulet.load_level(str(DST_WORLD))

    copied = skipped = 0
    for gcx, gcz in _chunks_in_area():
        try:
            chunk = src.get_chunk(gcx, gcz, "minecraft:overworld")
            dst.put_chunk(chunk, "minecraft:overworld")
            copied += 1
        except Exception:
            skipped += 1

    dst.save()
    src.close()
    dst.close()

    print(f"      chunks copied: {copied}, missing/error: {skipped}")
    print("      Vanilla blocks translated; unknown mod blocks → air (handled in step 3).")


# ── step 3: generate mod events ──────────────────────────────────────────────

def step3_generate_mod_events():
    print(f"\n[3/5] Generating mod conversion events")
    EVENTS_FILE.parent.mkdir(parents=True, exist_ok=True)

    stats = {"total": 0, "converted": 0, "placeholder": 0, "skipped_vanilla": 0, "no_id": 0}
    mod_counts: dict[str, int] = {}

    with EVENTS_FILE.open("w", encoding="utf-8") as out:
        for rx, rz in sorted(_regions_needed()):
            region_file = SRC_WORLD / "region" / f"r.{rx}.{rz}.mca"
            if not region_file.exists():
                print(f"      warn: {region_file.name} not found, skipping region ({rx},{rz})")
                continue

            parser = AnvilParser(str(region_file))

            for gcx, gcz in _chunks_in_area():
                if gcx // 32 != rx or gcz // 32 != rz:
                    continue

                lcx, lcz = _global_to_local_chunk(gcx, gcz)
                chunk = parser.get_chunk(lcx, lcz)
                if chunk is None:
                    continue

                block_meta = chunk.get_blocks_and_metadata_at_positions()

                for te in chunk.get_tile_entities():
                    te_id = str(te.get("id", ""))

                    if not te_id:
                        stats["no_id"] += 1
                        continue

                    te_x = int(te.get("x", 0))
                    te_y = int(te.get("y", 0))
                    te_z = int(te.get("z", 0))

                    # Filter to bounding box (TE coords are global world coords)
                    if not (X_MIN <= te_x <= X_MAX and Z_MIN <= te_z <= Z_MAX):
                        continue

                    mod = detect_mod(te_id)
                    if mod == "vanilla":
                        stats["skipped_vanilla"] += 1
                        continue

                    stats["total"] += 1
                    mod_counts[mod] = mod_counts.get(mod, 0) + 1

                    # Metadata from the chunk's Data nibble array
                    local_bx = te_x % 16
                    local_bz = te_z % 16
                    if local_bx < 0:
                        local_bx += 16
                    if local_bz < 0:
                        local_bz += 16
                    block_id, meta = block_meta.get((local_bx, te_y, local_bz), (0, 0))

                    events = convert_te_to_events(
                        te_nbt=te,
                        block_numeric_id=block_id,
                        metadata=meta,
                        global_pos=(te_x, te_y, te_z),
                    )

                    for ev in events:
                        out.write(json.dumps(ev, ensure_ascii=False) + "\n")

                    is_placeholder = any(
                        ev.get("block", "").startswith("conversion_placeholders")
                        for ev in events
                    )
                    if is_placeholder:
                        stats["placeholder"] += 1
                    else:
                        stats["converted"] += 1

    print(f"      mod TEs found      : {stats['total']}")
    print(f"      fully converted    : {stats['converted']}")
    print(f"      placeholder (stub) : {stats['placeholder']}")
    print(f"      vanilla (skipped)  : {stats['skipped_vanilla']}")
    if mod_counts:
        print("      by mod:")
        for mod, n in sorted(mod_counts.items(), key=lambda x: -x[1]):
            print(f"        {mod:<20} {n}")
    print(f"      events file: {EVENTS_FILE}")


# ── step 4: apply events via JVM Worker ─────────────────────────────────────

def step4_apply_events():
    print(f"\n[4/5] Applying mod events (JVM Worker / Hephaistos)")

    if not EVENTS_FILE.exists() or EVENTS_FILE.stat().st_size == 0:
        print("      No events to apply, skipping.")
        return

    if not WORKER_JAR.exists():
        raise FileNotFoundError(f"Worker JAR not found: {WORKER_JAR}")

    result = subprocess.run(
        [
            "java", "-jar", str(WORKER_JAR),
            "--apply-events", str(EVENTS_FILE),
            "--target-world", str(DST_WORLD),
        ],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )

    # Print worker output (it reports per-region saves)
    for line in result.stdout.splitlines():
        print(f"      {line}")

    if result.returncode != 0:
        # JVM Worker exits non-zero when some events fail.  Parse the JSON
        # summary from stdout to show statistics; don't abort the pipeline.
        print(f"      JVM Worker exited with code {result.returncode} (some events may have failed).")
        print(f"      STDERR snippet: {result.stderr[:400]}")
    else:
        print("      Events applied successfully.")


# ── step 5: configure level.dat ─────────────────────────────────────────────

def step5_configure_world():
    print(f"\n[5/5] Patching level.dat")
    import nbtlib  # type: ignore

    level_dat = DST_WORLD / "level.dat"
    level = nbtlib.load(str(level_dat), gzipped=True)
    data = level["Data"]

    data["SpawnX"]       = nbtlib.Int(SPAWN_X)
    data["SpawnY"]       = nbtlib.Int(SPAWN_Y)
    data["SpawnZ"]       = nbtlib.Int(SPAWN_Z)
    data["GameType"]     = nbtlib.Int(1)       # 1 = Creative
    data["allowCommands"] = nbtlib.Byte(1)
    data["Difficulty"]   = nbtlib.Byte(0)      # 0 = Peaceful
    data["LevelName"]    = nbtlib.String("ZSRR Conversion Test")

    level.save()

    print(f"      spawn    : ({SPAWN_X}, {SPAWN_Y}, {SPAWN_Z})")
    print(f"      gamemode : Creative")
    print(f"      name     : ZSRR Conversion Test")


# ── entry point ──────────────────────────────────────────────────────────────

def main():
    print("=" * 60)
    print("ZSRR Fragment Converter  --  1.7.10 -> 1.18.2")
    print(f"Area : X={X_MIN}..{X_MAX}  Z={Z_MIN}..{Z_MAX}")
    print(f"Chunks: X {CHUNK_X_MIN}..{CHUNK_X_MAX}  Z {CHUNK_Z_MIN}..{CHUNK_Z_MAX}  ({(CHUNK_X_MAX-CHUNK_X_MIN+1)*(CHUNK_Z_MAX-CHUNK_Z_MIN+1)} total)")
    print("=" * 60)

    step1_prepare_world()
    step2_amulet_vanilla_copy()
    step3_generate_mod_events()
    step4_apply_events()
    step5_configure_world()

    print("\n" + "=" * 60)
    print("Conversion complete!")
    print(f"World : {DST_WORLD}")
    print(f"Copy this directory to your 1.18.2 modded server's worlds folder")
    print(f"and set level-name=zsrr_conversion_test in server.properties.")
    print("=" * 60)


if __name__ == "__main__":
    main()
