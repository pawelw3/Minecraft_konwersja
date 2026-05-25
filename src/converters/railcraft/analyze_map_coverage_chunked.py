"""
Chunked map scanner for Railcraft TE coverage.
Processes region files in batches to avoid hangs.
"""

import json
import sys
import time
from pathlib import Path
from collections import Counter

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from minecraft_map_parser.anvil_parser import AnvilParser

from converters.railcraft.mappings.block_inventory import (
    RAILCRAFT_MACHINE_ALPHA, RAILCRAFT_MACHINE_BETA,
    RAILCRAFT_MACHINE_GAMMA, RAILCRAFT_MACHINE_DELTA,
    RAILCRAFT_MACHINE_EPSILON, RAILCRAFT_SIGNALS,
    RAILCRAFT_DETECTORS, RAILCRAFT_TRACK_TE,
)

KNOWN_TE_IDS = set(RAILCRAFT_TRACK_TE.keys())
for lst in [RAILCRAFT_MACHINE_ALPHA, RAILCRAFT_MACHINE_BETA,
            RAILCRAFT_MACHINE_GAMMA, RAILCRAFT_MACHINE_DELTA,
            RAILCRAFT_MACHINE_EPSILON, RAILCRAFT_SIGNALS, RAILCRAFT_DETECTORS]:
    for item in lst:
        if "te_id" in item:
            KNOWN_TE_IDS.add(item["te_id"])
KNOWN_TE_IDS.add("RCHiddenTile")

def scan_batch(files, batch_num):
    rc_counter = Counter()
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
                    if te_id in KNOWN_TE_IDS or (te_id and ("RC" in te_id or "railcraft" in te_id.lower())):
                        rc_counter[te_id] += 1
        except Exception as e:
            errors.append((fpath.name, str(e)))
        if i % 10 == 0:
            print(f"  batch {batch_num}: {i}/{len(files)} files, {chunk_total} chunks, {rc_counter.total()} RC TE", flush=True)
    elapsed = time.time() - t0
    print(f"  batch {batch_num} DONE: {len(files)} files in {elapsed:.1f}s", flush=True)
    return dict(rc_counter), chunk_total, errors

if __name__ == "__main__":
    region_dir = Path("mapa_1710/region")
    all_files = sorted(region_dir.glob("*.mca"))
    batch_size = 200
    total_files = len(all_files)
    print(f"Total files: {total_files}, batch size: {batch_size}", flush=True)

    all_rc = Counter()
    total_chunks = 0
    all_errors = []

    for batch_idx in range(0, total_files, batch_size):
        batch_files = all_files[batch_idx:batch_idx+batch_size]
        batch_num = batch_idx // batch_size + 1
        print(f"\n=== BATCH {batch_num} ({len(batch_files)} files) ===", flush=True)
        rc, chunks, errs = scan_batch(batch_files, batch_num)
        for k, v in rc.items():
            all_rc[k] += v
        total_chunks += chunks
        all_errors.extend(errs)

    unknown = {k:v for k,v in all_rc.items() if k not in KNOWN_TE_IDS}
    result = {
        "region_files": total_files,
        "chunks_scanned": total_chunks,
        "errors": all_errors[:20],
        "railcraft_te_counts": dict(all_rc.most_common()),
        "unknown_railcraft_te": unknown,
    }

    out_path = Path("output/railcraft_task4/map_coverage_railcraft.json")
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2, ensure_ascii=False)

    print(f"\n=== FINAL SUMMARY ===", flush=True)
    for te_id, count in all_rc.most_common():
        status = "known" if te_id in KNOWN_TE_IDS else "UNKNOWN"
        print(f"  {te_id}: {count} ({status})")
    if unknown:
        print(f"\nUNKNOWN TE IDs: {list(unknown.keys())}")
    else:
        print("\nAll Railcraft TE IDs are covered!")
