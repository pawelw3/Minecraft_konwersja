"""
Analiza kształtu struktur w strefie Choroszcz.
"""

import sys
from pathlib import Path
from collections import defaultdict

sys.path.insert(0, str(Path(__file__).parent))

from minecraft_map_parser import ModBlockExtractor
from minecraft_map_parser.anvil_parser import AnvilParser


def analyze_shape():
    project_root = Path(__file__).parent.parent
    region_file = project_root / 'mapa_1710' / 'region' / 'r.1.-2.mca'
    
    extractor = ModBlockExtractor()
    
    # Ekstrahuj wszystko z obszaru Choroszcz
    data = extractor.extract_from_region(
        str(region_file),
        x_min=763, x_max=916,
        z_min=-787, z_max=-636,
        include_vanilla=False,
        include_entities=True,
    )
    
    blocks = data['blocks']
    tile_entities = data['tile_entities']
    
    print("=" * 60)
    print("ANALIZA KSZTAŁTU - STREFA CHOROSZCZ")
    print("=" * 60)
    
    # Analiza rozkładu w osi Y (wysokość)
    y_distribution = defaultdict(int)
    y_by_mod = defaultdict(lambda: defaultdict(int))
    
    for block in blocks:
        y_distribution[block.y] += 1
        y_by_mod[block.mod_name or 'Unknown'][block.y] += 1
    
    print("\n1. Rozkład wysokościowy (Y) bloków:")
    for y in sorted(y_distribution.keys()):
        count = y_distribution[y]
        if count > 100:  # Pokaż tylko istotne warstwy
            print(f"   Y={y}: {count} bloków")
    
    # Analiza klastrów - podziel na sektory 32x32
    print("\n2. Gęstość bloków w sektorach 32x32:")
    sectors = defaultdict(lambda: defaultdict(int))
    
    for block in blocks:
        sec_x = (block.x - 763) // 32
        sec_z = (block.z - (-787)) // 32
        mod = block.mod_name or 'Unknown'
        sectors[(sec_x, sec_z)][mod] += 1
    
    # Znajdź najbardziej zaludnione sektory
    sector_totals = [(pos, sum(mods.values())) for pos, mods in sectors.items()]
    sector_totals.sort(key=lambda x: x[1], reverse=True)
    
    print("   Top 10 najgęstszych sektorów:")
    for (sec_x, sec_z), total in sector_totals[:10]:
        x_start = 763 + sec_x * 32
        z_start = -787 + sec_z * 32
        mods_in_sector = sectors[(sec_x, sec_z)]
        mod_str = ", ".join([f"{m}={c}" for m, c in sorted(mods_in_sector.items(), key=lambda x: -x[1])[:3]])
        print(f"     Sektor ({sec_x}, {sec_z}) @ ({x_start}, {z_start}): {total} bloków ({mod_str})")
    
    # Analiza tile entities - Carpenter's Blocks
    print("\n3. Analiza Carpenter's Blocks (dekoracje/architektura):")
    carp_te = [te for te in tile_entities if 'CarpentersBlock' in te.id]
    print(f"   Liczba tile entities Carpenter's: {len(carp_te)}")
    
    if carp_te:
        y_carp = [te.y for te in carp_te]
        print(f"   Wysokość: min={min(y_carp)}, max={max(y_carp)}")
        
        # Rozkład w osi Y
        y_carp_dist = defaultdict(int)
        for y in y_carp:
            y_carp_dist[y] += 1
        
        print("   Rozkład Y:")
        for y in sorted(y_carp_dist.keys()):
            if y_carp_dist[y] > 50:
                print(f"     Y={y}: {y_carp_dist[y]} bloków")
    
    # Analiza ForgeMicroblocks
    print("\n4. Analiza ForgeMicroblocks (płytki/dekoracje):")
    micro_te = [te for te in tile_entities if 'savedMultipart' in te.id]
    print(f"   Liczba microblocks: {len(micro_te)}")
    
    if micro_te:
        y_micro = [te.y for te in micro_te]
        print(f"   Wysokość: min={min(y_micro)}, max={max(y_micro)}")
        
        y_micro_dist = defaultdict(int)
        for y in y_micro:
            y_micro_dist[y] += 1
        
        print("   Rozkład Y:")
        for y in sorted(y_micro_dist.keys()):
            if y_micro_dist[y] > 100:
                print(f"     Y={y}: {y_micro_dist[y]} bloków")
    
    # Szukaj patternów - np. linie (rury BC)
    print("\n5. Analiza BuildCraft (prawdopodobnie rury):")
    bc_blocks = [b for b in blocks if b.mod_name == 'BC']
    print(f"   Liczba bloków BC: {len(bc_blocks)}")
    
    if bc_blocks:
        # Sprawdź czy tworzą linie (podobne Y i X lub Z)
        y_bc_dist = defaultdict(int)
        for b in bc_blocks:
            y_bc_dist[b.y] += 1
        
        print("   Rozkład Y dla BC:")
        for y in sorted(y_bc_dist.keys()):
            print(f"     Y={y}: {y_bc_dist[y]} bloków")
    
    # Analiza AE2 (maszyny, kable)
    print("\n6. Analiza AE2 (maszyny i sieć):")
    ae2_blocks = [b for b in blocks if b.mod_name == 'AE2']
    print(f"   Liczba bloków AE2: {len(ae2_blocks)}")
    
    if ae2_blocks:
        y_ae2_dist = defaultdict(int)
        for b in ae2_blocks:
            y_ae2_dist[b.y] += 1
        
        print("   Rozkład Y dla AE2:")
        for y in sorted(y_ae2_dist.keys()):
            if y_ae2_dist[y] > 50:
                print(f"     Y={y}: {y_ae2_dist[y]} bloków")
    
    # Analiza IC2
    print("\n7. Analiza IC2 (maszyny przemysłowe):")
    ic2_blocks = [b for b in blocks if b.mod_name == 'IC2']
    print(f"   Liczba bloków IC2: {len(ic2_blocks)}")
    
    if ic2_blocks:
        y_ic2_dist = defaultdict(int)
        for b in ic2_blocks:
            y_ic2_dist[b.y] += 1
        
        print("   Rozkład Y dla IC2:")
        for y in sorted(y_ic2_dist.keys()):
            if y_ic2_dist[y] > 10:
                print(f"     Y={y}: {y_ic2_dist[y]} bloków")
    
    print("\n8. Podsumowanie przestrzenne:")
    all_x = [b.x for b in blocks]
    all_z = [b.z for b in blocks]
    all_y = [b.y for b in blocks]
    
    print(f"   Zakres X: {min(all_x)} do {max(all_x)} (szerokość: {max(all_x)-min(all_x)})")
    print(f"   Zakres Z: {min(all_z)} do {max(all_z)} (głębokość: {max(all_z)-min(all_z)})")
    print(f"   Zakres Y: {min(all_y)} do {max(all_y)} (wysokość: {max(all_y)-min(all_y)})")
    
    # Centroidy
    center_x = sum(all_x) / len(all_x)
    center_z = sum(all_z) / len(all_z)
    center_y = sum(all_y) / len(all_y)
    
    print(f"   Środek ciężkości: X={center_x:.1f}, Z={center_z:.1f}, Y={center_y:.1f}")
    
    # Czy to płaska struktura czy 3D?
    y_range = max(all_y) - min(all_y)
    xz_range = max((max(all_x)-min(all_x)), (max(all_z)-min(all_z)))
    
    if y_range < 10:
        print(f"\n   >> Struktura PŁASKA (Y range: {y_range}, X/Z range: {xz_range})")
        print("   >> Prawdopodobnie: platforma, droga, lub poziom fabryki")
    elif y_range < 30:
        print(f"\n   >> Struktura NISKOBUDYNKOWA (Y range: {y_range}, X/Z range: {xz_range})")
        print("   >> Prawdopodobnie: fabryka, baza, przemysłowa hala")
    else:
        print(f"\n   >> Struktura WYSOKA (Y range: {y_range}, X/Z range: {xz_range})")
        print("   >> Prawdopodobnie: wieża, silos, lub wielopoziomowa baza")


if __name__ == '__main__':
    analyze_shape()
