#!/usr/bin/env python3
"""
convert_area.py

Converts the custom area (X=-1800..-1161, Z=-1007..-574) from the 1.7.10
modded map to a fresh 1.18.2 test world.

Pipeline
--------
1. Copy a 1.18.2 template world to tasks/custom_area_1800_574/world/
2. Amulet  — bulk-copy ALL chunks (vanilla blocks translated, unknown mod blocks -> air)
3. AnvilParser — scan 1.7.10 TileEntities, route each to a mod converter via router.py;
                 unsupported mods fall back to conversion_placeholders mod
4. JVM Worker  — apply the generated events.jsonl to the 1.18.2 world (Hephaistos)
5. Patch level.dat — spawn at area centre, creative mode, peaceful

Run
---
    python tasks/custom_area_1800_574/convert_area.py

Requirements
------------
    pip install amulet-core nbtlib
    Java 17+ in PATH (for JVM Worker)
"""

from __future__ import annotations

import io
import json
import math
import os
import shutil
import struct
import subprocess
import sys
import threading
import time
import zlib
from pathlib import Path

# ── project root on sys.path so src/ imports work ──────────────────────────
SCRIPT_DIR = Path(__file__).resolve().parent
ROOT = SCRIPT_DIR.parents[1]  # tasks/custom_area_1800_574/ -> tasks/ -> root
sys.path.insert(0, str(ROOT / "src"))

from minecraft_map_parser.anvil_parser import AnvilParser
from converters.router import convert_te_to_events, detect_mod, VANILLA_TE_IDS

# ── constants ───────────────────────────────────────────────────────────────

SRC_WORLD   = ROOT / "mapa_1710"
DST_AMULET_SOURCE = SCRIPT_DIR / "source_area_1710_for_amulet"
DST_WORLD   = SCRIPT_DIR / "world"

# Template preference order — first one with level.dat wins
_TEMPLATES = [
    ROOT / "lightweigh_map_templates" / "118_modded" / "ae2_1",
    ROOT / "lightweigh_map_templates" / "118_modded" / "konwersja3",
    ROOT / "headless_server"          / "1.18.2"     / "world",
]

EVENTS_FILE = SCRIPT_DIR / "events.jsonl"
WORKER_JAR  = ROOT / "jvm" / "worker" / "build" / "libs" / "mc-editkit-worker-1.0-SNAPSHOT.jar"
PROGRESS_INTERVAL_SECONDS = 60.0
AMULET_LOAD_TIMEOUT_SECONDS = 180.0

# Chunk range covering the requested area
CHUNK_X_MIN = -113   # chunk -113 starts at X = -1808
CHUNK_X_MAX = -73    # chunk -73 ends   at X = -1153
CHUNK_Z_MIN = -63    # chunk -63 starts at Z = -1008
CHUNK_Z_MAX = -36    # chunk -36 ends   at Z = -561

# Block bounding box of the copied chunks
X_MIN = CHUNK_X_MIN * 16         # -1808
X_MAX = CHUNK_X_MAX * 16 + 15   # -1153
Z_MIN = CHUNK_Z_MIN * 16         # -1008
Z_MAX = CHUNK_Z_MAX * 16 + 15   # -561

# Spawn: centre of the converted area
SPAWN_X = (X_MIN + X_MAX) // 2   # -1480
SPAWN_Y = 70
SPAWN_Z = (Z_MIN + Z_MAX) // 2   # -784


# ── helpers ──────────────────────────────────────────────────────────────────

class ProgressReporter:
    """Periodic progress logger for long operations that can otherwise be silent."""

    def __init__(self, label: str, total: int | None = None, interval: float = PROGRESS_INTERVAL_SECONDS):
        self.label = label
        self.total = total
        self.interval = interval
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
        status = "failed" if exc_type else "done"
        print(self._format(status), flush=True)
        return False

    def update(self, done: int | None = None, total: int | None = None, detail: str | None = None):
        with self._lock:
            if done is not None:
                self.done = done
            if total is not None:
                self.total = total
            if detail is not None:
                self.detail = detail

    def _run(self):
        while not self._stop.wait(self.interval):
            print(self._format("progress"), flush=True)

    def _format(self, status: str) -> str:
        with self._lock:
            done = self.done
            total = self.total
            detail = self.detail
        elapsed = time.monotonic() - self.started
        if total:
            pct = min(100.0, done * 100.0 / total)
            msg = f"      [{status}] {self.label}: {done}/{total} ({pct:.1f}%), elapsed {elapsed:.0f}s"
            if done > 0 and status == "progress":
                rate = done / elapsed if elapsed else 0.0
                remaining = max(0, total - done)
                eta = remaining / rate if rate else 0.0
                msg += f", rate {rate:.2f}/s, eta {eta:.0f}s"
        else:
            msg = f"      [{status}] {self.label}: elapsed {elapsed:.0f}s"
        if detail:
            msg += f" | {detail}"
        return msg


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


def _count_existing_chunks(world: Path) -> tuple[int, int]:
    """Return (existing_chunk_slots, requested_chunks) for the area."""
    existing = 0
    total = 0
    for gcx, gcz in _chunks_in_area():
        total += 1
        rx, rz = gcx // 32, gcz // 32
        region_file = world / "region" / f"r.{rx}.{rz}.mca"
        if not region_file.exists():
            continue

        lcx, lcz = _global_to_local_chunk(gcx, gcz)
        idx = lcx + lcz * 32
        with open(region_file, "rb") as f:
            f.seek(idx * 4)
            loc = f.read(4)
        if len(loc) == 4 and loc[:3] != b"\x00\x00\x00":
            existing += 1
    return existing, total


def _run_amulet_load_preflight(world: Path, label: str):
    """Verify that Amulet can open a world without letting it hang forever.

    Amulet's load_level does not expose per-chunk callbacks. If this step is
    slow, it is still opening the world provider, not loading area chunks.
    """
    existing, total = _count_existing_chunks(world)
    detail = (
        f"world_open=0/1, chunk_slots_in_area={existing}/{total}; "
        "Amulet has not started per-chunk copying yet"
    )
    code = (
        "import sys, amulet\n"
        "level = amulet.load_level(sys.argv[1])\n"
        "level.close()\n"
        "print('OK', flush=True)\n"
    )

    process = subprocess.Popen(
        [sys.executable, "-u", "-c", code, str(world)],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        encoding="utf-8",
        errors="replace",
    )

    with ProgressReporter(f"Amulet preflight {label}", total=1) as progress:
        progress.update(done=0, detail=f"{detail}; timeout={AMULET_LOAD_TIMEOUT_SECONDS:.0f}s")
        started = time.monotonic()
        while process.poll() is None:
            elapsed = time.monotonic() - started
            progress.update(
                done=0,
                detail=f"{detail}; elapsed={elapsed:.0f}s; timeout={AMULET_LOAD_TIMEOUT_SECONDS:.0f}s",
            )
            if elapsed >= AMULET_LOAD_TIMEOUT_SECONDS:
                process.kill()
                stdout, stderr = process.communicate(timeout=10)
                raise TimeoutError(
                    f"Amulet could not open {world} within {AMULET_LOAD_TIMEOUT_SECONDS:.0f}s. "
                    f"This is before chunk copying, so progress is still 0/{total} chunks. "
                    f"STDOUT: {stdout[-500:]} STDERR: {stderr[-1000:]}"
                )
            time.sleep(1.0)

        stdout, stderr = process.communicate(timeout=10)
        if process.returncode != 0:
            raise RuntimeError(
                f"Amulet preflight failed for {world} with code {process.returncode}. "
                f"STDOUT: {stdout[-500:]} STDERR: {stderr[-1000:]}"
            )
        progress.update(done=1, detail=f"world_open=1/1, chunk_slots_in_area={existing}/{total}")


def _hard_timeout_guard(label: str, seconds: float, detail: str):
    """Return a cancel event for a last-resort timeout guard."""
    cancel = threading.Event()

    def _watchdog():
        if cancel.wait(seconds):
            return
        print(
            f"      [timeout] {label}: exceeded {seconds:.0f}s | {detail}",
            flush=True,
        )
        os._exit(124)

    threading.Thread(target=_watchdog, daemon=True).start()
    return cancel


def _prepare_amulet_source_world() -> Path:
    """Create a tiny read-only source world copy for Amulet.

    Loading the full 1.7.10 modded world through Amulet/PyMCTranslate can spend
    a very long time initializing. For this task Amulet only needs vanilla block
    data from the requested region files, so we give it a minimal world folder.
    The real source map remains untouched and step 3 still reads TE data from it.
    """
    if DST_AMULET_SOURCE.exists():
        shutil.rmtree(DST_AMULET_SOURCE)

    (DST_AMULET_SOURCE / "region").mkdir(parents=True, exist_ok=True)
    shutil.copy2(SRC_WORLD / "level.dat", DST_AMULET_SOURCE / "level.dat")
    level_old = SRC_WORLD / "level.dat_old"
    if level_old.exists():
        shutil.copy2(level_old, DST_AMULET_SOURCE / "level.dat_old")

    copied = 0
    for rx, rz in sorted(_regions_needed()):
        src_region = SRC_WORLD / "region" / f"r.{rx}.{rz}.mca"
        if src_region.exists():
            shutil.copy2(src_region, DST_AMULET_SOURCE / "region" / src_region.name)
            copied += 1

    if copied == 0:
        raise FileNotFoundError(f"No source region files found for {sorted(_regions_needed())}")

    return DST_AMULET_SOURCE


def _sanitize_event(obj):
    """Convert nbtlib tags and other non-JSON-serializable objects to plain Python types."""
    if isinstance(obj, dict):
        return {str(k): _sanitize_event(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [_sanitize_event(v) for v in obj]
    if isinstance(obj, (str, int, float, bool)) or obj is None:
        return obj
    if isinstance(obj, bytes):
        return obj.decode('utf-8', errors='replace')
    if hasattr(obj, 'unpack'):
        return obj.unpack()
    return str(obj)


def _global_to_local_chunk(gcx: int, gcz: int) -> tuple[int, int]:
    """Global chunk coords -> local (0-31) coords within their region file."""
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

    amulet_source = _prepare_amulet_source_world()
    source_existing, source_total = _count_existing_chunks(amulet_source)
    target_existing, target_total = _count_existing_chunks(DST_WORLD)
    print(f"      source   : {amulet_source} ({len(_regions_needed())} region files)")
    print(f"      source chunk slots in area: {source_existing}/{source_total}")
    print(f"      target chunk slots in area: {target_existing}/{target_total}")

    _run_amulet_load_preflight(amulet_source, "source world")
    _run_amulet_load_preflight(DST_WORLD, "target world")

    with ProgressReporter("Amulet load source world", total=1) as progress:
        progress.update(
            done=0,
            detail=f"world_open=0/1, chunk_slots_in_area={source_existing}/{source_total}; chunks copied=0/{source_total}",
        )
        guard = _hard_timeout_guard(
            "Amulet load source world",
            AMULET_LOAD_TIMEOUT_SECONDS,
            f"world_open=0/1, chunks copied=0/{source_total}",
        )
        try:
            src = amulet.load_level(str(amulet_source))
        finally:
            guard.set()
        progress.update(
            done=1,
            detail=f"world_open=1/1, chunk_slots_in_area={source_existing}/{source_total}; chunks copied=0/{source_total}",
        )
    with ProgressReporter("Amulet load target world", total=1) as progress:
        progress.update(
            done=0,
            detail=f"world_open=0/1, chunk_slots_in_area={target_existing}/{target_total}; chunks copied=0/{source_total}",
        )
        guard = _hard_timeout_guard(
            "Amulet load target world",
            AMULET_LOAD_TIMEOUT_SECONDS,
            f"world_open=0/1, chunks copied=0/{source_total}",
        )
        try:
            dst = amulet.load_level(str(DST_WORLD))
        finally:
            guard.set()
        progress.update(
            done=1,
            detail=f"world_open=1/1, chunk_slots_in_area={target_existing}/{target_total}; chunks copied=0/{source_total}",
        )

    copied = skipped = 0
    total = (CHUNK_X_MAX - CHUNK_X_MIN + 1) * (CHUNK_Z_MAX - CHUNK_Z_MIN + 1)
    report_every = max(1, total // 20)

    with ProgressReporter("Amulet copy chunks", total=total) as progress:
        for gcx, gcz in _chunks_in_area():
            try:
                chunk = src.get_chunk(gcx, gcz, "minecraft:overworld")
                dst.put_chunk(chunk, "minecraft:overworld")
                copied += 1
            except Exception:
                skipped += 1
            done = copied + skipped
            progress.update(done=done, detail=f"chunk=({gcx},{gcz}) copied={copied} skipped={skipped}")
            if done % report_every == 0:
                print(f"      progress: {done}/{total} (copied {copied}, skipped {skipped})", flush=True)

    with ProgressReporter("Amulet save target world"):
        dst.save()
    src.close()
    dst.close()

    print(f"      chunks copied: {copied}, missing/error: {skipped}")
    print("      Vanilla blocks translated; unknown mod blocks -> air (handled in step 3).")


# ── step 2b: replace minecraft:numerical with air ────────────────────────────

def step2b_replace_numerical_with_air():
    """Replace minecraft:numerical palette entries with minecraft:air."""
    import nbtlib  # type: ignore

    print(f"\n[2b/5] Replacing minecraft:numerical with air in copied chunks")

    chunks_patched = 0
    sections_patched = 0
    total_chunks = (CHUNK_X_MAX - CHUNK_X_MIN + 1) * (CHUNK_Z_MAX - CHUNK_Z_MIN + 1)
    chunks_checked = 0

    with ProgressReporter("Patch minecraft:numerical palettes", total=total_chunks) as progress:
        for rx, rz in sorted(_regions_needed()):
            region_file = DST_WORLD / "region" / f"r.{rx}.{rz}.mca"
            if not region_file.exists():
                continue

            with open(region_file, "rb") as f:
                region_data = bytearray(f.read())

            region_dirty = False

            for gcx, gcz in _chunks_in_area():
                if gcx // 32 != rx or gcz // 32 != rz:
                    continue

                chunks_checked += 1
                progress.update(
                    done=chunks_checked,
                    detail=f"region=({rx},{rz}) chunk=({gcx},{gcz}) patched={chunks_patched}",
                )

                lcx, lcz = _global_to_local_chunk(gcx, gcz)
                idx = lcx + lcz * 32

                loc = region_data[idx * 4 : idx * 4 + 4]
                sector_off = (loc[0] << 16) | (loc[1] << 8) | loc[2]
                if sector_off == 0:
                    continue

                byte_off = sector_off * 4096
                length = struct.unpack(">I", bytes(region_data[byte_off : byte_off + 4]))[0]
                comp_type = region_data[byte_off + 4]
                if comp_type != 2:
                    continue

                compressed = bytes(region_data[byte_off + 5 : byte_off + 5 + length - 1])
                raw = zlib.decompress(compressed)
                nbt_file = nbtlib.File.from_fileobj(io.BytesIO(raw), byteorder="big")

                root = nbt_file.get("Level", nbt_file)
                sections = root.get("sections") or root.get("Sections") or []

                chunk_dirty = False
                for section in sections:
                    bs = section.get("block_states")
                    if bs is None:
                        continue
                    palette = bs.get("palette")
                    if palette is None:
                        continue

                    for i, entry in enumerate(palette):
                        name = str(entry.get("Name", ""))
                        if "numerical" not in name:
                            continue
                        palette[i] = nbtlib.Compound({"Name": nbtlib.String("minecraft:air")})
                        sections_patched += 1
                        chunk_dirty = True

                if not chunk_dirty:
                    continue

                buf = io.BytesIO()
                nbt_file.write(buf)
                new_raw = buf.getvalue()
                new_comp = zlib.compress(new_raw)
                new_len = len(new_comp) + 1

                old_sector_count = region_data[idx * 4 + 3]
                new_sector_count = math.ceil((new_len + 4) / 4096)

                if new_sector_count <= old_sector_count:
                    region_data[byte_off : byte_off + 4] = struct.pack(">I", new_len)
                    region_data[byte_off + 4] = 2
                    region_data[byte_off + 5 : byte_off + 5 + len(new_comp)] = new_comp
                else:
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

                chunks_patched += 1
                region_dirty = True

            if region_dirty:
                with open(region_file, "wb") as f:
                    f.write(region_data)

    print(f"      Chunks patched : {chunks_patched}")
    print(f"      Sections patched: {sections_patched}  (numerical->air palette entries)")


# ── step 3: generate mod events ──────────────────────────────────────────────

def step3_generate_mod_events():
    print(f"\n[3/5] Generating mod conversion events")
    EVENTS_FILE.parent.mkdir(parents=True, exist_ok=True)

    stats = {"total": 0, "converted": 0, "placeholder": 0, "skipped_vanilla": 0, "no_id": 0}
    mod_counts: dict[str, int] = {}

    total_regions = len(_regions_needed())
    region_idx = 0
    total_chunks = (CHUNK_X_MAX - CHUNK_X_MIN + 1) * (CHUNK_Z_MAX - CHUNK_Z_MIN + 1)
    chunks_checked = 0

    with ProgressReporter("Generate mod events", total=total_chunks) as progress:
        with EVENTS_FILE.open("w", encoding="utf-8") as out:
            for rx, rz in sorted(_regions_needed()):
                region_idx += 1
                region_file = SRC_WORLD / "region" / f"r.{rx}.{rz}.mca"
                if not region_file.exists():
                    print(f"      warn: {region_file.name} not found, skipping region ({rx},{rz})")
                    continue

                parser = AnvilParser(str(region_file))

                for gcx, gcz in _chunks_in_area():
                    if gcx // 32 != rx or gcz // 32 != rz:
                        continue

                    chunks_checked += 1
                    progress.update(
                        done=chunks_checked,
                        detail=(
                            f"region=({rx},{rz}) chunk=({gcx},{gcz}) "
                            f"events={stats['total']} converted={stats['converted']} placeholders={stats['placeholder']}"
                        ),
                    )

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
                            out.write(json.dumps(_sanitize_event(ev), ensure_ascii=False) + "\n")

                        is_placeholder = any(
                            ev.get("block", "").startswith("conversion_placeholders")
                            for ev in events
                        )
                        if is_placeholder:
                            stats["placeholder"] += 1
                        else:
                            stats["converted"] += 1

                print(f"      region {region_idx}/{total_regions} ({rx},{rz}) done", flush=True)

    print(f"      mod TEs found      : {stats['total']}")
    print(f"      fully converted    : {stats['converted']}")
    print(f"      placeholder (stub) : {stats['placeholder']}")
    print(f"      vanilla (skipped)  : {stats['skipped_vanilla']}")
    if mod_counts:
        print("      by mod:")
        for mod, n in sorted(mod_counts.items(), key=lambda x: -x[1]):
            print(f"        {mod:<20} {n}")
    print(f"      events file: {EVENTS_FILE}")


# ── step 3b: convert Backpack mod data ──────────────────────────────────────

def step3b_convert_backpacks():
    print(f"\n[3b] Converting Backpack mod data (-> Sophisticated Backpacks 1.18.2)")

    backpacks_dir = SRC_WORLD / "backpacks" / "backpacks"
    if not backpacks_dir.exists():
        print(f"      No backpacks dir found at {backpacks_dir}, skipping.")
        return

    from converters.backpack.backpack_converter import BackpackBatchConverter

    converter = BackpackBatchConverter(source_world=SRC_WORLD, target_world=DST_WORLD)
    report = converter.convert_all()

    if "error" in report:
        print(f"      ERROR: {report['error']}")
        return

    pd = report.get("playerdata", {})
    print(f"      Backpacks converted : {report.get('converted', 0)}/{report.get('total_files', 0)}  (failed: {report.get('failed', 0)}, items: {report.get('total_items', 0)})")
    print(f"      Playerdata backpacks: {pd.get('converted_backpacks', 0)} in {pd.get('converted_players', 0)} players")
    print(f"      Output: {report.get('output_paths', {}).get('nbt', '')}")


# ── step 4: apply events via JVM Worker ─────────────────────────────────────

def step4_apply_events():
    print(f"\n[4/5] Applying mod events (JVM Worker / Hephaistos)")

    if not EVENTS_FILE.exists() or EVENTS_FILE.stat().st_size == 0:
        print("      No events to apply, skipping.")
        return

    if not WORKER_JAR.exists():
        raise FileNotFoundError(f"Worker JAR not found: {WORKER_JAR}")

    event_count = sum(1 for _ in EVENTS_FILE.open("r", encoding="utf-8"))
    with ProgressReporter("JVM Worker apply events", total=event_count) as progress:
        progress.update(done=0, detail=f"events_file={EVENTS_FILE.name}")
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
        progress.update(done=event_count, detail="worker process finished")

    for line in result.stdout.splitlines():
        print(f"      {line}")

    if result.returncode != 0:
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
    data["LevelName"]    = nbtlib.String("Custom Area Conversion")

    level.save()

    print(f"      spawn    : ({SPAWN_X}, {SPAWN_Y}, {SPAWN_Z})")
    print(f"      gamemode : Creative")
    print(f"      name     : Custom Area Conversion")


# ── entry point ──────────────────────────────────────────────────────────────

def main():
    print("=" * 60)
    cx = CHUNK_X_MAX - CHUNK_X_MIN + 1
    cz = CHUNK_Z_MAX - CHUNK_Z_MIN + 1
    print("Custom Area Converter  --  1.7.10 -> 1.18.2")
    print(f"Area  : X={X_MIN}..{X_MAX}  Z={Z_MIN}..{Z_MAX}")
    print(f"Chunks: X {CHUNK_X_MIN}..{CHUNK_X_MAX}  Z {CHUNK_Z_MIN}..{CHUNK_Z_MAX}  ({cx}x{cz}={cx*cz} total)")
    print(f"Output: {SCRIPT_DIR}")
    print("=" * 60)

    step1_prepare_world()
    step2_amulet_vanilla_copy()
    step2b_replace_numerical_with_air()
    step3_generate_mod_events()
    step3b_convert_backpacks()
    step4_apply_events()
    step5_configure_world()

    print("\n" + "=" * 60)
    print("Conversion complete!")
    print(f"World : {DST_WORLD}")
    print(f"Copy this directory to your 1.18.2 modded server's worlds folder")
    print(f"and set level-name=world in server.properties.")
    print("=" * 60)


if __name__ == "__main__":
    main()
