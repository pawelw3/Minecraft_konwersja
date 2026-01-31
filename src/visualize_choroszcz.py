"""
Skrypt do wizualizacji strefy Choroszcz na mapie Minecraft 1.7.10.
Generuje SVG z blokami i tile entities z modów.
"""

import json
import sys
from pathlib import Path

# Dodaj rodzicielski katalog do ścieżki
sys.path.insert(0, str(Path(__file__).parent))

from minecraft_map_parser import ModBlockExtractor, MapVisualizer
from minecraft_map_parser.anvil_parser import get_region_for_block


def load_zone_coords(zone_name: str) -> dict:
    """Wczytuje współrzędne strefy z pliku JSON."""
    coords_file = Path(__file__).parent.parent / 'strefy' / zone_name / 'coords.json'
    with open(coords_file, 'r') as f:
        return json.load(f)


def get_region_files_for_zone(zone_coords: dict, map_dir: Path) -> list:
    """Znajduje pliki regionów dla danej strefy."""
    coords = zone_coords['minecraftCoordinates']
    
    # Znajdź min/max
    x_coords = [c['x'] for c in coords]
    z_coords = [c['z'] for c in coords]
    
    x_min, x_max = min(x_coords), max(x_coords)
    z_min, z_max = min(z_coords), max(z_coords)
    
    print(f"Strefa obejmuje X: {x_min} do {x_max}, Z: {z_min} do {z_max}")
    
    # Znajdź wszystkie regiony
    regions = set()
    for x in range(x_min, x_max + 1, 512):
        for z in range(z_min, z_max + 1, 512):
            region_x, region_z = get_region_for_block(x, z)
            regions.add((region_x, region_z))
    
    print(f"Potrzebne regiony: {sorted(regions)}")
    
    # Zbuduj ścieżki do plików
    region_files = []
    for rx, rz in regions:
        filename = f"r.{rx}.{rz}.mca"
        filepath = map_dir / 'region' / filename
        if filepath.exists():
            region_files.append((filepath, (rx, rz)))
            print(f"  [OK] Znaleziono: {filename}")
        else:
            print(f"  [MISSING] Brak: {filename}")
    
    return region_files, (x_min, x_max, z_min, z_max)


def main():
    # Ścieżki
    project_root = Path(__file__).parent.parent
    map_dir = project_root / 'mapa_1710'
    output_dir = project_root / 'docs' / 'visualizations'
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Wczytaj współrzędne strefy
    print("=" * 60)
    print("WIZUALIZACJA STREFY CHOROSZCZ")
    print("=" * 60)
    
    zone_coords = load_zone_coords('choroszcz')
    print(f"Strefa: {zone_coords['name']}")
    
    # Znajdź pliki regionów
    region_files, bounds = get_region_files_for_zone(zone_coords, map_dir)
    x_min, x_max, z_min, z_max = bounds
    
    if not region_files:
        print("Nie znaleziono plików regionów!")
        return
    
    # Inicjalizuj ekstraktor
    print("\n" + "=" * 60)
    print("EKSTRAKCJA DANYCH")
    print("=" * 60)
    
    extractor = ModBlockExtractor()
    all_blocks = []
    all_tile_entities = []
    all_entities = []
    
    for region_file, (rx, rz) in region_files:
        print(f"\nPrzetwarzanie regionu ({rx}, {rz}): {region_file.name}")
        
        try:
            data = extractor.extract_from_region(
                str(region_file),
                x_min=x_min,
                x_max=x_max,
                z_min=z_min,
                z_max=z_max,
                include_vanilla=False,  # Tylko mody
                include_entities=True,
            )
            
            blocks = data['blocks']
            tile_entities = data['tile_entities']
            entities = data['entities']
            
            print(f"  Bloki z modów: {len(blocks)}")
            print(f"  Tile entities: {len(tile_entities)}")
            print(f"  Entities: {len(entities)}")
            
            all_blocks.extend(blocks)
            all_tile_entities.extend(tile_entities)
            all_entities.extend(entities)
            
        except Exception as e:
            print(f"  Błąd podczas przetwarzania: {e}")
            import traceback
            traceback.print_exc()
    
    # Statystyki
    print("\n" + "=" * 60)
    print("PODSUMOWANIE")
    print("=" * 60)
    
    stats = extractor.get_stats()
    print(f"Łącznie bloków z modów: {stats['modded_blocks']:,}")
    print(f"Łącznie vanilla bloków: {stats['vanilla_blocks']:,}")
    print(f"Łącznie tile entities z modów: {stats['modded_tile_entities']}")
    print(f"Łącznie vanilla tile entities: {stats['vanilla_tile_entities']}")
    print(f"Łącznie entities z modów: {stats['modded_entities']}")
    print(f"Łącznie vanilla entities: {stats['vanilla_entities']}")
    
    # Unikalne typy
    unique_block_ids = set(b.block_id for b in all_blocks)
    unique_te_types = set(te.id for te in all_tile_entities)
    
    print(f"\nUnikalne ID bloków: {sorted(unique_block_ids)[:20]}..." if len(unique_block_ids) > 20 else f"\nUnikalne ID bloków: {sorted(unique_block_ids)}")
    print(f"Typy tile entities: {sorted(unique_te_types)[:10]}..." if len(unique_te_types) > 10 else f"Typy tile entities: {sorted(unique_te_types)}")
    
    # Generuj wizualizację
    print("\n" + "=" * 60)
    print("GENEROWANIE WIZUALIZACJI SVG")
    print("=" * 60)
    
    if not all_blocks and not all_tile_entities:
        print("Brak danych do wizualizacji!")
        return
    
    visualizer = MapVisualizer(pixel_size=2)
    
    svg = visualizer.generate_svg(
        all_blocks,
        all_tile_entities,
        all_entities,
        title=f"Strefa Choroszcz - Bloki i Tile Entities z Modów",
        show_legend=True,
        show_grid=True,
        grid_spacing=32,
    )
    
    # Zapisz SVG
    svg_path = output_dir / 'choroszcz_mod_blocks.svg'
    with open(svg_path, 'w', encoding='utf-8') as f:
        f.write(svg)
    print(f"Zapisano wizualizację: {svg_path}")
    
    # Generuj HTML podsumowania
    html = visualizer.generate_summary_html(all_blocks, all_tile_entities, all_entities)
    html_path = output_dir / 'choroszcz_summary.html'
    with open(html_path, 'w', encoding='utf-8') as f:
        f.write(html)
    print(f"Zapisano podsumowanie: {html_path}")
    
    print("\n" + "=" * 60)
    print("GOTOWE!")
    print("=" * 60)
    print(f"Otwórz plik w przeglądarce: {svg_path.absolute()}")


if __name__ == '__main__':
    main()
