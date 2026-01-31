"""
Analiza Tile Entities z Railcrafta w strefie Choroszcz.
"""

import sys
from pathlib import Path
from collections import defaultdict

sys.path.insert(0, str(Path(__file__).parent))

from minecraft_map_parser import ModBlockExtractor


def analyze_railcraft():
    project_root = Path(__file__).parent.parent
    region_file = project_root / 'mapa_1710' / 'region' / 'r.1.-2.mca'
    
    extractor = ModBlockExtractor()
    
    data = extractor.extract_from_region(
        str(region_file),
        x_min=763, x_max=916,
        z_min=-787, z_max=-636,
        include_vanilla=False,
        include_entities=False,
    )
    
    te_list = data['tile_entities']
    
    # Filtruj tylko Railcraft
    railcraft_te = [te for te in te_list if te.mod_name == 'Railcraft']
    
    print("=" * 60)
    print("ANALIZA TILE ENTITIES RAILCRAFTA - CHOROSZCZ")
    print("=" * 60)
    print(f"\nLiczba TE Railcrafta: {len(railcraft_te)}")
    
    # Typy
    types = defaultdict(int)
    for te in railcraft_te:
        types[te.id] += 1
    
    print("\nTypy TE:")
    for te_type, count in sorted(types.items()):
        print(f"  {te_type}: {count}")
    
    # Analiza pozycji - czy są losowe czy w linii?
    print("\n" + "=" * 60)
    print("ROZMIESZCZENIE PRZESTRZENNE")
    print("=" * 60)
    
    # Grupuj po Y
    by_y = defaultdict(list)
    for te in railcraft_te:
        by_y[te.y].append(te)
    
    print("\nRozkład po wysokości (Y):")
    for y in sorted(by_y.keys()):
        count = len(by_y[y])
        print(f"  Y={y}: {count} TE")
    
    # Sprawdź czy tworzą linie (tory)
    print("\n" + "=" * 60)
    print("ANALIZA WZORCÓW (czy to tory?)")
    print("=" * 60)
    
    # Dla każdego poziomu Y sprawdź rozmieszczenie X/Z
    for y in sorted(by_y.keys()):
        tes = by_y[y]
        if len(tes) < 5:
            continue
            
        xs = [te.x for te in tes]
        zs = [te.z for te in tes]
        
        print(f"\nY={y} ({len(tes)} TE):")
        print(f"  X: {min(xs)} do {max(xs)} (zakres: {max(xs)-min(xs)})")
        print(f"  Z: {min(zs)} do {max(zs)} (zakres: {max(zs)-min(zs)})")
        
        # Czy są w linii X czy Z?
        unique_x = len(set(xs))
        unique_z = len(set(zs))
        
        if unique_x < len(tes) * 0.3:
            print(f"  -> Prawdopodobnie linia wzdłuż Z (powtarzające się X)")
        elif unique_z < len(tes) * 0.3:
            print(f"  -> Prawdopodobnie linia wzdłuż X (powtarzające się Z)")
        else:
            print(f"  -> Rozproszone losowo (unikalne X:{unique_x}, Z:{unique_z})")
        
        # Pokaż pierwsze 5 pozycji
        print(f"  Przykładowe pozycje:")
        for te in tes[:5]:
            print(f"    ({te.x}, {te.y}, {te.z})")
    
    # Sprawdź odległości między sąsiednimi TE
    print("\n" + "=" * 60)
    print("ODLEGŁOŚCI MIĘDZY TE")
    print("=" * 60)
    
    for y in sorted(by_y.keys()):
        tes = by_y[y]
        if len(tes) < 2:
            continue
        
        # Posortuj po X, potem Z
        tes_sorted = sorted(tes, key=lambda t: (t.x, t.z))
        
        distances = []
        for i in range(1, len(tes_sorted)):
            dx = tes_sorted[i].x - tes_sorted[i-1].x
            dz = tes_sorted[i].z - tes_sorted[i-1].z
            dist = (dx**2 + dz**2) ** 0.5
            distances.append(dist)
        
        if distances:
            avg_dist = sum(distances) / len(distances)
            min_dist = min(distances)
            max_dist = max(distances)
            print(f"\nY={y}:")
            print(f"  Średnia odległość: {avg_dist:.1f}")
            print(f"  Min odległość: {min_dist:.1f}")
            print(f"  Max odległość: {max_dist:.1f}")
            
            # Czy to regularne (co kilka bloków)?
            regular = all(1 <= d <= 5 for d in distances)
            if regular:
                print(f"  -> Regularne rozmieszczenie (jak tory kolejowe!)")
            else:
                print(f"  -> Nieregularne rozmieszczenie")


if __name__ == '__main__':
    analyze_railcraft()
