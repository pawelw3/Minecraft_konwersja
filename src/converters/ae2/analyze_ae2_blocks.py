"""
Szczegółowa analiza bloków AE2 w strefie Choroszcz.
"""

import sys
from pathlib import Path
from collections import defaultdict, Counter

sys.path.insert(0, str(Path(__file__).parent))

from minecraft_map_parser import ModBlockExtractor


def analyze_ae2():
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
    
    blocks = data['blocks']
    
    # Filtruj tylko AE2
    ae2_blocks = [b for b in blocks if b.mod_name == 'AE2']
    
    print("=" * 60)
    print("ANALIZA BLOKÓW AE2 - SZCZEGÓŁY")
    print("=" * 60)
    
    print(f"\n1. Łączna liczba bloków AE2: {len(ae2_blocks)}")
    
    # Analiza ID bloków
    id_counts = Counter(b.block_id for b in ae2_blocks)
    print("\n2. Rozkład ID bloków AE2:")
    for block_id, count in id_counts.most_common():
        percentage = (count / len(ae2_blocks)) * 100
        print(f"   ID {block_id}: {count} bloków ({percentage:.1f}%)")
    
    # Analiza metadata per ID
    print("\n3. Metadata dla głównych ID:")
    for block_id, count in id_counts.most_common(5):
        meta_counts = Counter(b.metadata for b in ae2_blocks if b.block_id == block_id)
        print(f"   ID {block_id}:")
        for meta, meta_count in sorted(meta_counts.items()):
            print(f"     metadata {meta}: {meta_count} bloków")
    
    # Analiza pozycji - czy to są duże płaszczyzny?
    print("\n4. Analiza przestrzenna najczęstszego bloku:")
    main_id = id_counts.most_common(1)[0][0]
    main_blocks = [b for b in ae2_blocks if b.block_id == main_id]
    
    # Sprawdź czy tworzą płaszczyzny
    y_levels = defaultdict(list)
    for b in main_blocks:
        y_levels[b.y].append((b.x, b.z))
    
    print(f"   Główny blok ID {main_id} występuje na {len(y_levels)} poziomach Y")
    
    for y in sorted(y_levels.keys()):
        coords = y_levels[y]
        xs = [c[0] for c in coords]
        zs = [c[1] for c in coords]
        width = max(xs) - min(xs) if len(xs) > 1 else 0
        depth = max(zs) - min(zs) if len(zs) > 1 else 0
        print(f"     Y={y}: {len(coords)} bloków, zakres X({min(xs)}-{max(xs)}), Z({min(zs)}-{max(zs)}), wymiary {width}x{depth}")
    
    # Sprawdź czy to są kwarcowe bloki (dekoracyjne)
    print("\n5. Sprawdzenie czy to Certus Quartz Block / Fluix Block:")
    # W AE2 1.7.10:
    # - Certus Quartz Block: zazwyczaj meta 0
    # - Fluix Block: zazwyczaj meta 1
    # - ME Cable: różne meta w zależności od koloru/typu
    
    for block_id, count in id_counts.most_common(3):
        blocks_with_id = [b for b in ae2_blocks if b.block_id == block_id]
        meta_dist = Counter(b.metadata for b in blocks_with_id)
        print(f"   ID {block_id} - rozkład metadanych:")
        for meta, cnt in sorted(meta_dist.items()):
            print(f"     meta={meta}: {cnt}")
    
    # Szukaj wzorca - czy to są ściany/podłogi?
    print("\n6. Czy to struktura wielopoziomowa?")
    all_y = sorted(set(b.y for b in ae2_blocks))
    print(f"   Poziomy Y z blokami AE2: {all_y}")
    
    # Sprawdź odległości między poziomami
    if len(all_y) > 1:
        diffs = [all_y[i+1] - all_y[i] for i in range(len(all_y)-1)]
        print(f"   Odległości między poziomami: {set(diffs)}")


if __name__ == '__main__':
    analyze_ae2()
