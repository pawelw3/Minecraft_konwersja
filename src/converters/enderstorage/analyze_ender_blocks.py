"""
Szczegółowa analiza bloków 'Ender Chest' na mapie.
"""

import sys
import os
import json
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from minecraft_map_parser.anvil_parser import AnvilParser
from pathlib import Path

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

def analyze_ender_chests(world_path: str):
    """Analizuje szczegóły bloków Ender Chest w strefach"""
    
    ender_chests = []
    
    # Pobierz regiony ze wszystkich stref
    zones_dir = Path("strefy")
    all_regions = set()
    
    for zone_file in zones_dir.glob("*/coords.json"):
        with open(zone_file, 'r') as f:
            zone_data = json.load(f)
        coords = zone_data.get("minecraftCoordinates", [])
        all_regions.update(get_regions_for_zone(coords))
    
    print(f"Regiony do przeskanowania: {len(all_regions)}")
    
    region_path = Path(world_path) / "region"
    
    print(f"Skanowanie {len(all_regions)} regionów w poszukiwaniu 'Ender Chest'...")
    
    for i, (rx, rz) in enumerate(all_regions):
        region_file = region_path / f"r.{rx}.{rz}.mca"
        
        if not region_file.exists():
            continue
            
        if i % 5 == 0:
            print(f"  Przetworzono {i}/{len(all_regions)} regionów...")
        
        try:
            parser = AnvilParser(str(region_file))
            
            for cz in range(32):
                for cx in range(32):
                    chunk = parser.get_chunk(cx, cz)
                    if not chunk:
                        continue
                    
                    for te in chunk.get_tile_entities():
                        te_id = te.get("id", "")
                        
                        if te_id == "Ender Chest":  # Ze spacją!
                            ender_chests.append({
                                "x": te.get("x"),
                                "y": te.get("y"),
                                "z": te.get("z"),
                                "te_id": te_id,
                                "all_keys": list(te.keys()),
                                "has_freq": "freq" in te,
                                "has_owner": "owner" in te,
                                "has_rot": "rot" in te,
                                "freq_value": te.get("freq"),
                                "owner_value": te.get("owner"),
                                "rot_value": te.get("rot"),
                                "full_nbt": te,
                            })
                        
                        if te_id == "EnderChest":  # Vanilla
                            ender_chests.append({
                                "x": te.get("x"),
                                "y": te.get("y"),
                                "z": te.get("z"),
                                "te_id": te_id,
                                "note": "Vanilla EnderChest"
                            })
                        
        except Exception as e:
            pass
    
    print(f"\nZnaleziono {len(ender_chests)} bloków 'Ender Chest'/'EnderChest'")
    
    # Podziel na typy
    vanilla = [b for b in ender_chests if b["te_id"] == "EnderChest"]
    modded = [b for b in ender_chests if b["te_id"] == "Ender Chest"]
    
    print(f"  Vanilla 'EnderChest': {len(vanilla)}")
    print(f"  Modded 'Ender Chest': {len(modded)}")
    
    print("\n" + "=" * 70)
    print("SZCZEGOLY 'Ender Chest' (prawdopodobnie EnderStorage):")
    print("=" * 70)
    
    for chest in modded[:10]:
        print(f"\n  Pozycja: ({chest['x']}, {chest['y']}, {chest['z']})")
        print(f"  Klucze NBT: {chest['all_keys']}")
        print(f"  Ma freq: {chest['has_freq']} ({chest['freq_value']})")
        print(f"  Ma owner: {chest['has_owner']} ({chest['owner_value']})")
        print(f"  Ma rot: {chest['has_rot']} ({chest['rot_value']})")
    
    # Zapisz
    output_file = Path("output") / "ender_chest_analysis.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump({
            "vanilla_enderchest": vanilla,
            "modded_ender_chest": modded
        }, f, indent=2, default=str)
    
    print(f"\nWyniki zapisano do: {output_file}")
    
    return modded

if __name__ == "__main__":
    analyze_ender_chests("mapa_1710")
