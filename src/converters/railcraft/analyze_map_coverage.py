"""
Skanuje całą mapę 1.7.10 w poszukiwaniu Railcraft Tile Entities.
Porównuje znalezione TE IDs z inwentarzem konwertera.
"""

import json
import sys
import time
from pathlib import Path
from collections import Counter

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from minecraft_map_parser.anvil_parser import AnvilParser

# Inwentarz TE IDs z block_inventory.py
from converters.railcraft.mappings.block_inventory import (
    RAILCRAFT_MACHINE_ALPHA,
    RAILCRAFT_MACHINE_BETA,
    RAILCRAFT_MACHINE_GAMMA,
    RAILCRAFT_MACHINE_DELTA,
    RAILCRAFT_MACHINE_EPSILON,
    RAILCRAFT_SIGNALS,
    RAILCRAFT_DETECTORS,
    RAILCRAFT_TRACK_TE,
)

# RCHiddenTile jest w TileHidden.java, rejestrowany jako "RCHiddenTile"
KNOWN_TE_IDS = set(RAILCRAFT_TRACK_TE.keys())
for lst in [RAILCRAFT_MACHINE_ALPHA, RAILCRAFT_MACHINE_BETA,
            RAILCRAFT_MACHINE_GAMMA, RAILCRAFT_MACHINE_DELTA,
            RAILCRAFT_MACHINE_EPSILON, RAILCRAFT_SIGNALS, RAILCRAFT_DETECTORS]:
    for item in lst:
        if "te_id" in item:
            KNOWN_TE_IDS.add(item["te_id"])

# RCHiddenTile
KNOWN_TE_IDS.add("RCHiddenTile")

def scan_all_regions(region_dir: Path):
    files = list(region_dir.glob("*.mca"))
    total_files = len(files)
    print(f"Scanning {total_files} region files...")

    all_te_counter = Counter()
    railcraft_te_counter = Counter()
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
                    if te_id in KNOWN_TE_IDS or (te_id and ("RC" in te_id or "railcraft" in te_id.lower())):
                        railcraft_te_counter[te_id] += 1
        except Exception as e:
            errors.append((str(fpath.name), str(e)))

        if i % 50 == 0 or i == total_files:
            elapsed = time.time() - t0
            rate = i / elapsed
            remaining = (total_files - i) / rate if rate > 0 else 0
            print(f"  [{i}/{total_files}] {elapsed:.1f}s elapsed, ~{remaining:.0f}s remaining")

    t1 = time.time()
    print(f"\nDone in {t1-t0:.1f}s. {chunk_total} chunks scanned. {len(errors)} errors.")

    # Find unknown Railcraft TEs
    unknown_rc = {}
    for te_id, count in railcraft_te_counter.items():
        if te_id not in KNOWN_TE_IDS:
            unknown_rc[te_id] = count

    result = {
        "scan_time_sec": round(t1 - t0, 2),
        "region_files": total_files,
        "chunks_scanned": chunk_total,
        "errors": errors[:10],
        "railcraft_te_counts": dict(railcraft_te_counter.most_common()),
        "unknown_railcraft_te": unknown_rc,
        "known_te_ids_count": len(KNOWN_TE_IDS),
    }
    return result


if __name__ == "__main__":
    region_dir = Path("mapa_1710/region")
    result = scan_all_regions(region_dir)

    out_path = Path("output/railcraft_task4/map_coverage_railcraft.json")
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2, ensure_ascii=False)

    print(f"\nSaved report to {out_path}")
    print("\n=== RAILCRAFT TE SUMMARY ===")
    for te_id, count in Counter(result["railcraft_te_counts"]).most_common():
        status = "✅ known" if te_id in KNOWN_TE_IDS else "❌ UNKNOWN"
        print(f"  {te_id}: {count} ({status})")
    if result["unknown_railcraft_te"]:
        print("\n⚠️  UNKNOWN Railcraft TE IDs found:")
        for te_id, count in result["unknown_railcraft_te"].items():
            print(f"  {te_id}: {count}")
    else:
        print("\n✅ All Railcraft TE IDs on the map are covered by the converter!")
