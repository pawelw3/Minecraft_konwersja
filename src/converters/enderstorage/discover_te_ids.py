"""
Skrypt do odkrycia rzeczywistych TileEntity ID na mapie.
Szuka wszystkich unikalnych TE ID aby zidentyfikować format EnderStorage.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from minecraft_map_parser.anvil_parser import AnvilParser
from pathlib import Path
from collections import Counter

def discover_te_ids(world_path: str, max_regions: int = 50):
    """
    Skanuje mapę w poszukiwaniu wszystkich TileEntity ID.
    
    Args:
        world_path: Ścieżka do folderu z mapą
        max_regions: Maksymalna liczba regionów do przeskanowania
    """
    region_path = Path(world_path) / "region"
    
    all_te_ids = Counter()
    ender_related = Counter()
    
    region_files = list(region_path.glob("r.*.*.mca"))[:max_regions]
    
    print(f"Skanowanie {len(region_files)} regionów...")
    
    for i, region_file in enumerate(region_files):
        if i % 10 == 0:
            print(f"  Przetworzono {i}/{len(region_files)} regionów...")
        
        try:
            parser = AnvilParser(str(region_file))
            
            for cz in range(32):
                for cx in range(32):
                    try:
                        chunk = parser.get_chunk(cx, cz)
                        if not chunk:
                            continue
                        
                        for te in chunk.get_tile_entities():
                            te_id = te.get("id", "UNKNOWN")
                            all_te_ids[te_id] += 1
                            
                            # Sprawdź czy zawiera "ender"
                            if "ender" in te_id.lower():
                                ender_related[te_id] += 1
                                
                    except Exception:
                        pass
                        
        except Exception as e:
            print(f"  Błąd w {region_file}: {e}")
    
    print("\n" + "=" * 70)
    print("WSZYSTKIE TILE ENTITY ID (top 50):")
    print("=" * 70)
    for te_id, count in all_te_ids.most_common(50):
        print(f"  {te_id}: {count}")
    
    print("\n" + "=" * 70)
    print("TE ID ZAWIERAJĄCE 'ender':")
    print("=" * 70)
    for te_id, count in ender_related.most_common():
        print(f"  {te_id}: {count}")
    
    # Zapisz do pliku
    output_file = Path("output") / "discovered_te_ids.txt"
    output_file.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("# Odkryte TileEntity ID na mapie\n\n")
        f.write("## Wszystkie ID (posortowane po liczbie wystąpień):\n\n")
        for te_id, count in all_te_ids.most_common():
            f.write(f"{te_id}: {count}\n")
        
        f.write("\n## ID zawierające 'ender':\n\n")
        for te_id, count in ender_related.most_common():
            f.write(f"{te_id}: {count}\n")
    
    print(f"\nWyniki zapisano do: {output_file}")

if __name__ == "__main__":
    discover_te_ids("mapa_1710", max_regions=100)
