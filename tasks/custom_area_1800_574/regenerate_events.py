"""Regenerate events.jsonl from mapa_1710 using updated router (no Amulet needed)."""
import json
import sys
import time
from pathlib import Path

# Fix import path
SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR.parent.parent / "src"))

from minecraft_map_parser.anvil_parser import AnvilParser
from converters.router import detect_mod, convert_te_to_events

# ------------------------------------------------------------------
# Area definition (same as convert_area.py)
# ------------------------------------------------------------------
CENTER_X, CENTER_Z = -1482, -787
CHUNK_RADIUS_X = 32
CHUNK_RADIUS_Z = 27

CX_MIN = -113
CX_MAX = -73
CZ_MIN = -63
CZ_MAX = -36

X_MIN = CX_MIN * 16
X_MAX = CX_MAX * 16 + 15
Z_MIN = CZ_MIN * 16
Z_MAX = CZ_MAX * 16 + 15

MAP_1710 = SCRIPT_DIR.parent.parent / "mapa_1710"
MCA_DIR = MAP_1710 / "region"
EVENTS_FILE = SCRIPT_DIR / "events.jsonl"


def _sanitize_event(ev):
    """Ensure event dict is JSON-serializable."""
    return json.loads(json.dumps(ev, default=str))


def main():
    print(f"Target area: X={X_MIN}..{X_MAX}, Z={Z_MIN}..{Z_MAX}")
    print(f"Chunks:      cx={CX_MIN}..{CX_MAX}, cz={CZ_MIN}..{CZ_MAX}")
    print(f"MCA dir:     {MCA_DIR}")
    print(f"Output:      {EVENTS_FILE}")

    regions = [
        (rx, rz)
        for rx in range(CX_MIN >> 5, (CX_MAX >> 5) + 1)
        for rz in range(CZ_MIN >> 5, (CZ_MAX >> 5) + 1)
    ]
    total_regions = len(regions)
    print(f"Regions to scan: {total_regions}")

    stats = {"total": 0, "converted": 0, "placeholder": 0,
             "skipped_vanilla": 0, "no_id": 0, "errors": 0}
    mod_counts = {}

    t0 = time.time()

    with EVENTS_FILE.open("w", encoding="utf-8") as out:
        for region_idx, (rx, rz) in enumerate(regions, start=1):
            region_file = MCA_DIR / f"r.{rx}.{rz}.mca"
            if not region_file.exists():
                continue

            try:
                parser = AnvilParser(str(region_file))
            except Exception as e:
                print(f"      WARN: cannot open {region_file.name}: {e}")
                continue

            for chunk in parser.get_all_chunks():
                cx = chunk.x
                cz = chunk.z
                if not (CX_MIN <= cx <= CX_MAX and CZ_MIN <= cz <= CZ_MAX):
                    continue

                try:
                    block_meta = chunk.get_blocks_and_metadata_at_positions()
                except Exception as e:
                    print(f"      WARN: block_meta error at ({cx},{cz}): {e}")
                    block_meta = {}

                for te in chunk.get_tile_entities():
                    te_id = str(te.get("id", ""))
                    if not te_id:
                        stats["no_id"] += 1
                        continue

                    te_x = int(te.get("x", 0))
                    te_y = int(te.get("y", 0))
                    te_z = int(te.get("z", 0))

                    if not (X_MIN <= te_x <= X_MAX and Z_MIN <= te_z <= Z_MAX):
                        continue

                    mod = detect_mod(te_id)
                    if mod == "vanilla":
                        stats["skipped_vanilla"] += 1
                        continue

                    stats["total"] += 1
                    mod_counts[mod] = mod_counts.get(mod, 0) + 1

                    local_bx = te_x % 16
                    local_bz = te_z % 16
                    if local_bx < 0:
                        local_bx += 16
                    if local_bz < 0:
                        local_bz += 16
                    block_id, meta = block_meta.get((local_bx, te_y, local_bz), (0, 0))

                    try:
                        events = convert_te_to_events(
                            te_nbt=te,
                            block_numeric_id=block_id,
                            metadata=meta,
                            global_pos=(te_x, te_y, te_z),
                        )
                    except Exception as e:
                        stats["errors"] += 1
                        print(f"ERROR converting {te_id} at ({te_x},{te_y},{te_z}): {e}")
                        continue

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

    elapsed = time.time() - t0
    print(f"\nDone in {elapsed:.1f}s")
    print(f"  mod TEs found      : {stats['total']}")
    print(f"  fully converted    : {stats['converted']}")
    print(f"  placeholder (stub) : {stats['placeholder']}")
    print(f"  vanilla (skipped)  : {stats['skipped_vanilla']}")
    print(f"  errors             : {stats['errors']}")
    if mod_counts:
        print("  per-mod:")
        for mod, cnt in sorted(mod_counts.items(), key=lambda x: -x[1]):
            print(f"    {mod}: {cnt}")


if __name__ == "__main__":
    main()
