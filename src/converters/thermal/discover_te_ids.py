import sys
sys.path.insert(0, 'src')

from pathlib import Path
import re
import json
from minecraft_map_parser.anvil_parser import AnvilParser

THERMAL_PATTERNS = [
    r"thermalexpansion",
    r"thermaldynamics",
    r"thermalfoundation",
    r"ThermalExpansion",
    r"ThermalDynamics",
    r"ThermalFoundation",
]

REGIONS_TO_SCAN = [
    # Strefy
    "r.0.-1.mca",   # billund
    "r.1.-2.mca",   # choroszcz
    "r.0.5.mca", "r.0.6.mca", "r.1.5.mca", "r.1.6.mca",  # iii_rzesza
    "r.0.0.mca", "r.0.1.mca", "r.1.0.mca", "r.1.1.mca",  # rzym
    "r.-6.-6.mca", "r.-6.-5.mca", "r.-5.-6.mca", "r.-5.-5.mca",  # zsrr
    # Dodatkowe
    "r.-1.-1.mca",
    "r.10.10.mca",
    "r.-10.-10.mca",
]

def scan_region(region_path):
    found_te_ids = {}
    found_block_ids = {}
    chunk_count = 0
    
    if not region_path.exists():
        return found_te_ids, found_block_ids, chunk_count, "missing"
    
    try:
        parser = AnvilParser(str(region_path))
    except Exception as e:
        return found_te_ids, found_block_ids, chunk_count, f"error: {e}"
    
    for cz in range(32):
        for cx in range(32):
            try:
                chunk = parser.get_chunk(cx, cz)
                if not chunk:
                    continue
                chunk_count += 1
                
                # Scan TileEntities
                for te in chunk.get_tile_entities():
                    te_id = te.get("id", "")
                    for pattern in THERMAL_PATTERNS:
                        if re.search(pattern, te_id, re.IGNORECASE):
                            found_te_ids[te_id] = found_te_ids.get(te_id, 0) + 1
                            break
                
                # Scan block IDs in sections
                level = chunk.nbt.get('Level', {})
                if hasattr(level, 'get'):
                    sections = level.get('Sections', [])
                    if sections:
                        for sec in sections:
                            if hasattr(sec, 'get'):
                                blocks = sec.get('Blocks', None)
                                if blocks:
                                    # Check Add array for IDs > 255
                                    add_arr = sec.get('Add', None)
                                    for i in range(len(blocks)):
                                        block_id = blocks[i] & 0xFF
                                        if add_arr and i < len(add_arr):
                                            block_id |= (add_arr[i] & 0xFF) << 8
                                        if block_id > 0:
                                            # We'll need registry lookup to know if it's thermal
                                            pass
            except Exception:
                continue
    
    return found_te_ids, found_block_ids, chunk_count, "ok"

world_path = Path("mapa_1710")
region_path = world_path / "region"

all_te_ids = {}
stats = []

for region_name in REGIONS_TO_SCAN:
    rp = region_path / region_name
    te_ids, block_ids, chunk_count, status = scan_region(rp)
    stats.append({
        "region": region_name,
        "chunks": chunk_count,
        "status": status,
        "te_types": len(te_ids),
        "te_total": sum(te_ids.values()),
    })
    for te_id, count in te_ids.items():
        all_te_ids[te_id] = all_te_ids.get(te_id, 0) + count

print("=== Thermal TE IDs found on map ===")
for te_id in sorted(all_te_ids.keys()):
    print(f"  {te_id}: {all_te_ids[te_id]}")

print("\n=== Region stats ===")
for s in stats:
    print(f"  {s['region']}: chunks={s['chunks']}, status={s['status']}, te_types={s['te_types']}, te_total={s['te_total']}")

# Save results
output = {
    "te_ids": all_te_ids,
    "region_stats": stats,
}
out_path = Path("output/thermal_te_discovery.json")
out_path.parent.mkdir(parents=True, exist_ok=True)
with open(out_path, 'w') as f:
    json.dump(output, f, indent=2)
print(f"\nSaved to {out_path}")
