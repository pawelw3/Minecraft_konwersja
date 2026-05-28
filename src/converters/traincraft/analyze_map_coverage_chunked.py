"""
Skanuje całą mapę 1.7.10 w poszukiwaniu Traincraft Tile Entities.
Wersja chunked – iteruje chunk-by-chunk zamiast ładować cały region.
"""

import json
import sys
import time
from pathlib import Path
from collections import Counter

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from minecraft_map_parser.anvil_parser import AnvilParser
from converters.traincraft.mappings.block_mappings import TRAINCRAFT_TE_IDS

KNOWN_TE_IDS = set(TRAINCRAFT_TE_IDS)


def scan_region_file(fpath: Path):
    """Scan a single region file, returning counters."""
    tc_te_counter = Counter()
    track_type_counter = Counter()
    chunk_count = 0

    try:
        parser = AnvilParser(str(fpath))
        rx, rz = parser.get_region_coordinates()

        for cx in range(32):
            for cz in range(32):
                chunk = parser.get_chunk(cx, cz)
                if chunk is None:
                    continue
                chunk_count += 1
                for te in chunk.get_tile_entities():
                    te_id = te.get("id", "")
                    if te_id in KNOWN_TE_IDS:
                        tc_te_counter[te_id] += 1
                        if te_id == "tileTCRail":
                            track_type_counter[te.get("type", "UNKNOWN")] += 1
    except Exception as e:
        return {"error": str(e), "chunks": chunk_count}, tc_te_counter, track_type_counter

    return {"chunks": chunk_count}, tc_te_counter, track_type_counter


def scan_all_regions(region_dir: Path, checkpoint_path: Path | None = None):
    files = sorted(region_dir.glob("*.mca"))
    total_files = len(files)
    print(f"Scanning {total_files} region files for Traincraft blocks (chunked mode)...")

    global_tc_counter = Counter()
    global_track_counter = Counter()
    chunk_total = 0
    errors = []

    # Resume from checkpoint
    processed = 0
    if checkpoint_path and checkpoint_path.exists():
        with open(checkpoint_path, "r", encoding="utf-8") as f:
            ck = json.load(f)
        processed = ck.get("processed", 0)
        global_tc_counter.update(ck.get("tc_counts", {}))
        global_track_counter.update(ck.get("track_counts", {}))
        chunk_total = ck.get("chunks", 0)
        errors = ck.get("errors", [])
        print(f"Resuming from checkpoint: {processed} files already done.")

    t0 = time.time()
    for i, fpath in enumerate(files[processed:], start=processed + 1):
        info, tc_counter, track_counter = scan_region_file(fpath)
        chunk_total += info.get("chunks", 0)
        if "error" in info:
            errors.append((str(fpath.name), info["error"]))

        global_tc_counter.update(tc_counter)
        global_track_counter.update(track_counter)

        if i % 50 == 0 or i == total_files:
            elapsed = time.time() - t0
            rate = (i - processed) / elapsed if elapsed > 0 else 0
            remaining = (total_files - i) / rate if rate > 0 else 0
            print(f"  [{i}/{total_files}] chunks={chunk_total} tc={sum(global_tc_counter.values())} "
                  f"{elapsed:.1f}s elapsed, ~{remaining:.0f}s remaining")

            if checkpoint_path:
                with open(checkpoint_path, "w", encoding="utf-8") as f:
                    json.dump({
                        "processed": i,
                        "tc_counts": dict(global_tc_counter),
                        "track_counts": dict(global_track_counter),
                        "chunks": chunk_total,
                        "errors": errors,
                    }, f, indent=2)

    t1 = time.time()
    print(f"\nDone in {t1-t0:.1f}s. {chunk_total} chunks scanned. {len(errors)} errors.")

    unknown_tc = {k: v for k, v in global_tc_counter.items() if k not in KNOWN_TE_IDS}

    result = {
        "scan_time_sec": round(t1 - t0, 2),
        "region_files": total_files,
        "chunks_scanned": chunk_total,
        "errors": errors[:20],
        "traincraft_te_counts": dict(global_tc_counter.most_common()),
        "unknown_traincraft_te": unknown_tc,
        "known_te_ids_count": len(KNOWN_TE_IDS),
        "track_type_counts": dict(global_track_counter.most_common()),
    }
    return result


if __name__ == "__main__":
    region_dir = Path("mapa_1710/region")
    checkpoint = Path("output/traincraft_task4/coverage_checkpoint.json")
    out_path = Path("output/traincraft_task4/coverage_traincraft.json")
    out_path.parent.mkdir(parents=True, exist_ok=True)

    result = scan_all_regions(region_dir, checkpoint_path=checkpoint)

    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2, ensure_ascii=False)

    print(f"\nSaved report to {out_path}")
    print("\n=== TRAINCRAFT TE SUMMARY ===")
    for te_id, count in Counter(result["traincraft_te_counts"]).most_common():
        status = "OK" if te_id in KNOWN_TE_IDS else "UNKNOWN"
        print(f"  {te_id}: {count} ({status})")

    print("\n=== TRACK TYPE BREAKDOWN ===")
    for tt, count in Counter(result["track_type_counts"]).most_common():
        print(f"  {tt}: {count}")

    if result["unknown_traincraft_te"]:
        print("\nWARNING: UNKNOWN Traincraft-like TE IDs found:")
        for te_id, count in result["unknown_traincraft_te"].items():
            print(f"  {te_id}: {count}")
    else:
        print("\nOK: All Traincraft TE IDs on the map are covered by the converter!")

    # Clean up checkpoint
    if checkpoint.exists():
        checkpoint.unlink()
