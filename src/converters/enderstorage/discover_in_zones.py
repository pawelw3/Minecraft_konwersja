"""
Skanuje dokładnie wszystkie regiony w strefach w poszukiwaniu EnderStorage.
"""

import sys
import os
import json
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from minecraft_map_parser.anvil_parser import AnvilParser
from pathlib import Path
from collections import Counter

def get_regions_for_zone(zone_coords):
    """Zwraca regiony dla strefy"""
    min_x = min(c["x"] for c in zone_coords)
    max_x = max(c["x"] for c in zone_coords)
    min_z = min(c["z"] for c in zone_coords)
    max_z = max(c["z"] for c in zone_coords)
    
    min_cx = min_x >> 4
    max_cx = max_x >> 4
    min_cz = min_z >> 4
    max_cz = max_z >> 4
    
    min_rx = min_cx >> 5
    max_rx = max_cx >> 5
    min_rz = min_cz >> 5
    max_rz = max_cz >> 5
    
    regions = set()
    for rx in range(min_rx, max_rx + 1):
        for rz in range(min_rz, max_rz + 1):
            regions.add((rx, rz))
    return regions

def scan_zones_detailed(world_path: str):
    """Szczegółowe skanowanie stref"""
    zones_dir = Path("strefy")
    
    all_te_ids = Counter()
    ender_storage_candidates = []
    
    for zone_file in zones_dir.glob("*/coords.json"):
        with open(zone_file, 'r') as f:
            zone_data = json.load(f)
        
        zone_name = zone_data.get("name", zone_file.parent.name)
        coords = zone_data.get("minecraftCoordinates", [])
        
        regions = get_regions_for_zone(coords)
        print(f"\nStrefa: {zone_name}")
        print(f"  Regiony do przeskanowania: {len(regions)}")
        
        for rx, rz in regions:
            region_file = f"r.{rx}.{rz}.mca"
            region_path = Path(world_path) / "region" / region_file
            
            if not region_path.exists():
                continue
            
            try:
                parser = AnvilParser(str(region_path))
                
                for cz in range(32):
                    for cx in range(32):
                        chunk = parser.get_chunk(cx, cz)
                        if not chunk:
                            continue
                        
                        for te in chunk.get_tile_entities():
                            te_id = te.get("id", "UNKNOWN")
                            all_te_ids[te_id] += 1
                            
                            # Sprawdź czy to może być EnderStorage
                            if "ender" in te_id.lower():
                                ender_storage_candidates.append({
                                    "zone": zone_name,
                                    "te_id": te_id,
                                    "x": te.get("x"),
                                    "y": te.get("y"),
                                    "z": te.get("z"),
                                    "region": region_file
                                })
                                
            except Exception as e:
                pass
    
    print("\n" + "=" * 70)
    print("WSZYSTKIE TE ID W STREFACH (top 30):")
    print("=" * 70)
    for te_id, count in all_te_ids.most_common(30):
        print(f"  {te_id}: {count}")
    
    print("\n" + "=" * 70)
    print("KANDYDACI NA ENDERSTORAGE ('ender' w nazwie):")
    print("=" * 70)
    if ender_storage_candidates:
        for cand in ender_storage_candidates[:20]:
            print(f"  {cand['te_id']} @ ({cand['x']}, {cand['y']}, {cand['z']}) w {cand['zone']}")
    else:
        print("  Nie znaleziono żadnych TE z 'ender' w nazwie w strefach!")
    
    # Zapisz
    output_file = Path("output") / "zone_te_discovery.json"
    output_file.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump({
            "all_te_ids": dict(all_te_ids.most_common()),
            "ender_candidates": ender_storage_candidates
        }, f, indent=2, ensure_ascii=False)
    
    print(f"\nWyniki zapisano do: {output_file}")

if __name__ == "__main__":
    scan_zones_detailed("mapa_1710")
