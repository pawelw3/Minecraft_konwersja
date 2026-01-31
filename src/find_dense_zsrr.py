"""
Znajdowanie najgęstszego fragmentu 100x100 ze strefy ZSRR.
"""

import sys
from pathlib import Path
from collections import defaultdict

sys.path.insert(0, str(Path(__file__).parent))

from minecraft_map_parser import ModBlockExtractor
from minecraft_map_parser.anvil_parser import AnvilParser, get_region_for_block


def find_dense_area():
    project_root = Path(__file__).parent.parent
    
    # Strefa ZSRR
    x_min, x_max = -2948, -2086
    z_min, z_max = -2857, -1759
    
    print("=" * 60)
    print("SZUKANIE NAJGĘSTSZEGO FRAGMENTU W STREFIE ZSRR")
    print("=" * 60)
    print(f"Obszar: X({x_min} to {x_max}), Z({z_min} to {z_max})")
    
    # Znajdź wszystkie regiony
    regions = set()
    for x in range(x_min, x_max + 1, 512):
        for z in range(z_min, z_max + 1, 512):
            regions.add(get_region_for_block(x, z))
    
    print(f"\nRegiony do przeskanowania: {len(regions)}")
    
    extractor = ModBlockExtractor()
    
    # Zbierz wszystkie bloki z modów z całej strefy
    all_blocks = []
    all_te = []
    
    for rx, rz in sorted(regions):
        region_file = project_root / 'mapa_1710' / 'region' / f'r.{rx}.{rz}.mca'
        if not region_file.exists():
            continue
        
        print(f"\nPrzetwarzanie r.{rx}.{rz}.mca...")
        
        try:
            data = extractor.extract_from_region(
                str(region_file),
                x_min=x_min, x_max=x_max,
                z_min=z_min, z_max=z_max,
                include_vanilla=False,
                include_entities=False,
            )
            
            blocks = data['blocks']
            te = data['tile_entities']
            
            print(f"  Bloki z modów: {len(blocks)}")
            print(f"  Tile entities: {len(te)}")
            
            all_blocks.extend(blocks)
            all_te.extend(te)
            
        except Exception as e:
            print(f"  Błąd: {e}")
    
    print(f"\n{'='*60}")
    print(f"RAZEM: {len(all_blocks)} bloków, {len(all_te)} tile entities")
    print(f"{'='*60}")
    
    # Podziel na siatkę 100x100 i znajdź najgęstszy fragment
    grid_size = 100
    grid = defaultdict(lambda: {'blocks': [], 'te': []})
    
    # Przypisz bloki do komórek siatki
    for block in all_blocks:
        grid_x = (block.x - x_min) // grid_size
        grid_z = (block.z - z_min) // grid_size
        grid[(grid_x, grid_z)]['blocks'].append(block)
    
    # Przypisz tile entities do komórek
    for te in all_te:
        grid_x = (te.x - x_min) // grid_size
        grid_z = (te.z - z_min) // grid_size
        grid[(grid_x, grid_z)]['te'].append(te)
    
    # Znajdź najgęstsze komórki
    cell_stats = []
    for (gx, gz), data in grid.items():
        real_x = x_min + gx * grid_size
        real_z = z_min + gz * grid_size
        cell_stats.append({
            'grid': (gx, gz),
            'pos': (real_x, real_z),
            'blocks': len(data['blocks']),
            'te': len(data['te']),
            'total': len(data['blocks']) + len(data['te']),
        })
    
    # Sortuj po całkowitej liczbie elementów
    cell_stats.sort(key=lambda x: x['total'], reverse=True)
    
    print("\nTop 10 najgęstszych fragmentów 100x100:")
    print("-" * 80)
    for i, cell in enumerate(cell_stats[:10], 1):
        print(f"{i}. Fragment @ ({cell['pos'][0]}, {cell['pos'][1]})")
        print(f"   Bloki: {cell['blocks']}, Tile Entities: {cell['te']}, TOTAL: {cell['total']}")
    
    # Zwróć najgęstszy
    if cell_stats:
        best = cell_stats[0]
        print(f"\n{'='*60}")
        print("NAJGĘSTSZY FRAGMENT:")
        print(f"  Pozycja: X={best['pos'][0]}..{best['pos'][0]+99}, Z={best['pos'][1]}..{best['pos'][1]+99}")
        print(f"  Bloki: {best['blocks']}")
        print(f"  Tile Entities: {best['te']}")
        print(f"{'='*60}")
        return best['pos'][0], best['pos'][1], best['blocks'], best['te']
    
    return None


if __name__ == '__main__':
    find_dense_area()
