"""
Scan a range of region files for Railcraft TEs.
Usage: python analyze_map_coverage_range.py <start_idx> <end_idx> <out_json>
"""
import json
import sys
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

def main(start_idx, end_idx, out_path):
    files = sorted(Path("mapa_1710/region").glob("*.mca"))[start_idx:end_idx]
    rc_counter = Counter()
    chunk_total = 0
    errors = []
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
        if i % 20 == 0:
            print(f"  {i}/{len(files)} files, {chunk_total} chunks")
    result = {
        "start_idx": start_idx, "end_idx": end_idx,
        "files": len(files), "chunks": chunk_total,
        "errors": errors[:10],
        "railcraft_te_counts": dict(rc_counter.most_common()),
        "unknown": {k:v for k,v in rc_counter.items() if k not in KNOWN_TE_IDS},
    }
    Path(out_path).parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2)
    print(f"Saved {out_path}")
    for te_id, count in rc_counter.most_common():
        status = "known" if te_id in KNOWN_TE_IDS else "UNKNOWN"
        print(f"  {te_id}: {count} ({status})")

if __name__ == "__main__":
    main(int(sys.argv[1]), int(sys.argv[2]), sys.argv[3])
