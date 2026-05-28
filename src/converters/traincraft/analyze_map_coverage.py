"""
Skanuje całą mapę 1.7.10 w poszukiwaniu Traincraft Tile Entities.
Porównuje znalezione TE IDs z inwentarzem konwertera.
"""

import json
import sys
import time
from pathlib import Path
from collections import Counter

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from minecraft_map_parser.anvil_parser import AnvilParser

# Inwentarz TE IDs z block_mappings.py
from converters.traincraft.mappings.block_mappings import TRAINCRAFT_TE_IDS

KNOWN_TE_IDS = set(TRAINCRAFT_TE_IDS)

# Dodatkowe TE które mogą występować ale nie są w TRAINCRAFT_TE_IDS (np. stare wersje)
KNOWN_TE_IDS.add("tileTCRail")      # redundant but explicit
KNOWN_TE_IDS.add("tileTCRailGag")   # redundant but explicit


def scan_all_regions(region_dir: Path):
    files = list(region_dir.glob("*.mca"))
    total_files = len(files)
    print(f"Scanning {total_files} region files for Traincraft blocks...")

    all_te_counter = Counter()
    tc_te_counter = Counter()
    chunk_total = 0
    errors = []

    t0 = time.time()
    for i, fpath in enumerate(files, 1):
        try:
            parser = AnvilParser(str(fpath))
            chunks = parser.get_all_chunks()
            chunk_total += len(chunks)
            for chunk in chunks:
                for te in chunk.get_tile_entities():
                    te_id = te.get("id", "UNKNOWN")
                    all_te_counter[te_id] += 1
                    if te_id in KNOWN_TE_IDS:
                        tc_te_counter[te_id] += 1
        except Exception as e:
            errors.append((str(fpath.name), str(e)))

        if i % 50 == 0 or i == total_files:
            elapsed = time.time() - t0
            rate = i / elapsed
            remaining = (total_files - i) / rate if rate > 0 else 0
            print(f"  [{i}/{total_files}] {elapsed:.1f}s elapsed, ~{remaining:.0f}s remaining")

    t1 = time.time()
    print(f"\nDone in {t1-t0:.1f}s. {chunk_total} chunks scanned. {len(errors)} errors.")

    # Find unknown Traincraft-like TEs
    unknown_tc = {}
    for te_id, count in tc_te_counter.items():
        if te_id not in KNOWN_TE_IDS:
            unknown_tc[te_id] = count

    # Track type breakdown for tcRail
    track_type_counter = Counter()
    for fpath in files:
        try:
            parser = AnvilParser(str(fpath))
            for chunk in parser.get_all_chunks():
                for te in chunk.get_tile_entities():
                    if te.get("id") == "tileTCRail":
                        track_type_counter[te.get("type", "UNKNOWN")] += 1
        except Exception:
            pass

    result = {
        "scan_time_sec": round(t1 - t0, 2),
        "region_files": total_files,
        "chunks_scanned": chunk_total,
        "errors": errors[:10],
        "traincraft_te_counts": dict(tc_te_counter.most_common()),
        "unknown_traincraft_te": unknown_tc,
        "known_te_ids_count": len(KNOWN_TE_IDS),
        "track_type_counts": dict(track_type_counter.most_common()),
    }
    return result


if __name__ == "__main__":
    region_dir = Path("mapa_1710/region")
    result = scan_all_regions(region_dir)

    out_path = Path("output/traincraft_task4/coverage_traincraft.json")
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2, ensure_ascii=False)

    print(f"\nSaved report to {out_path}")
    print("\n=== TRAINCRAFT TE SUMMARY ===")
    for te_id, count in Counter(result["traincraft_te_counts"]).most_common():
        status = "✅ known" if te_id in KNOWN_TE_IDS else "❌ UNKNOWN"
        print(f"  {te_id}: {count} ({status})")

    print("\n=== TRACK TYPE BREAKDOWN ===")
    for tt, count in Counter(result["track_type_counts"]).most_common():
        print(f"  {tt}: {count}")

    if result["unknown_traincraft_te"]:
        print("\n⚠️  UNKNOWN Traincraft-like TE IDs found:")
        for te_id, count in result["unknown_traincraft_te"].items():
            print(f"  {te_id}: {count}")
    else:
        print("\n✅ All Traincraft TE IDs on the map are covered by the converter!")
