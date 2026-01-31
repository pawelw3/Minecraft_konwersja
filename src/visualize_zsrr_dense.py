"""
Wizualizacja najgęstszego fragmentu 100x100 ze strefy ZSRR.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from minecraft_map_parser import ModBlockExtractor, MapVisualizer
from minecraft_map_parser.anvil_parser import get_region_for_block


def main():
    project_root = Path(__file__).parent.parent
    output_dir = project_root / 'docs' / 'visualizations'
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Najgęstszy fragment
    x_min, x_max = -2748, -2649
    z_min, z_max = -2057, -1958
    
    print("=" * 60)
    print("WIZUALIZACJA NAJGĘSTSZEGO FRAGMENTU ZSRR")
    print("=" * 60)
    print(f"Fragment: X({x_min} to {x_max}), Z({z_min} to {z_max})")
    print(f"Rozmiar: 100x100 bloków")
    
    # Znajdź regiony
    regions = set()
    for x in [x_min, x_max]:
        for z in [z_min, z_max]:
            regions.add(get_region_for_block(x, z))
    
    print(f"\nRegiony: {sorted(regions)}")
    
    extractor = ModBlockExtractor()
    all_blocks = []
    all_te = []
    
    for rx, rz in sorted(regions):
        region_file = project_root / 'mapa_1710' / 'region' / f'r.{rx}.{rz}.mca'
        if not region_file.exists():
            continue
        
        print(f"\nPrzetwarzanie r.{rx}.{rz}.mca...")
        
        data = extractor.extract_from_region(
            str(region_file),
            x_min=x_min, x_max=x_max,
            z_min=z_min, z_max=z_max,
            include_vanilla=False,
            include_entities=True,
        )
        
        all_blocks.extend(data['blocks'])
        all_te.extend(data['tile_entities'])
        
        print(f"  Bloki: {len(data['blocks'])}")
        print(f"  Tile entities: {len(data['tile_entities'])}")
    
    print(f"\n{'='*60}")
    print(f"RAZEM: {len(all_blocks)} bloków, {len(all_te)} tile entities")
    
    # Analiza modów
    from collections import Counter
    mod_counts = Counter(b.mod_name or 'Unknown' for b in all_blocks)
    te_mod_counts = Counter(te.mod_name or 'Unknown' for te in all_te)
    
    print(f"\nBloki per mod:")
    for mod, count in mod_counts.most_common(10):
        print(f"  {mod}: {count}")
    
    print(f"\nTile entities per mod:")
    for mod, count in te_mod_counts.most_common(10):
        print(f"  {mod}: {count}")
    
    # Generuj wizualizację
    print(f"\n{'='*60}")
    print("Generowanie wizualizacji SVG...")
    
    visualizer = MapVisualizer(pixel_size=4)  # Większe piksele dla czytelności
    
    svg = visualizer.generate_svg(
        all_blocks,
        all_te,
        [],
        title=f"ZSRR - Najgęstszy fragment 100x100 @ ({x_min}, {z_min})",
        show_legend=True,
        show_grid=True,
        grid_spacing=10,
    )
    
    # Zapisz
    svg_path = output_dir / 'zsrr_dense_fragment.svg'
    with open(svg_path, 'w', encoding='utf-8') as f:
        f.write(svg)
    print(f"Zapisano: {svg_path}")
    
    # HTML podsumowanie
    html = visualizer.generate_summary_html(all_blocks, all_te, [])
    html_path = output_dir / 'zsrr_dense_summary.html'
    with open(html_path, 'w', encoding='utf-8') as f:
        f.write(html)
    print(f"Zapisano: {html_path}")
    
    print(f"\n{'='*60}")
    print("GOTOWE!")
    print(f"{'='*60}")


if __name__ == '__main__':
    main()
