"""
Scan Map for Enchanting Plus Blocks

Skanuje mapę 1.7.10 w poszukiwaniu bloków Enchanting Plus.
Używane do weryfikacji czy na mapie są jakiekolwiek bloki EP
które wymagają konwersji.
"""

import sys
import json
from pathlib import Path
from collections import defaultdict

sys.path.insert(0, 'src')

from minecraft_map_parser.anvil_parser import AnvilParser
from minecraft_map_parser.nbt_parser import NBTTag


# ID bloków Enchanting Plus w 1.7.10
EP_BLOCK_IDS = {
    'EnchantingPlus:enchanting_table',
    'EnchantingPlus:advanced_table',
    'EnchantingPlus:arcane_inscriber',
}


def scan_region_file(region_path: Path) -> list:
    """
    Skanuje pojedynczy plik regionu w poszukiwaniu bloków EP.
    
    Args:
        region_path: Ścieżka do pliku .mca
        
    Returns:
        Lista znalezionych bloków EP
    """
    found_blocks = []
    
    try:
        parser = AnvilParser(str(region_path))
        
        for cx in range(32):
            for cz in range(32):
                try:
                    chunk = parser.get_chunk(cx, cz)
                    if not chunk:
                        continue
                    
                    # Pobierz Tile Entities
                    level = chunk.nbt.get('Level', {})
                    if isinstance(level, NBTTag):
                        level = level.value
                    
                    te_list = level.get('TileEntities', [])
                    if isinstance(te_list, NBTTag):
                        te_list = te_list.value
                    
                    for te in te_list:
                        if isinstance(te, NBTTag):
                            te = te.value
                        
                        te_id = te.get('id', '')
                        if isinstance(te_id, NBTTag):
                            te_id = te_id.value
                        
                        # Sprawdź czy to blok EP
                        if te_id in EP_BLOCK_IDS:
                            x = te.get('x', 0)
                            y = te.get('y', 0)
                            z = te.get('z', 0)
                            
                            if isinstance(x, NBTTag): x = x.value
                            if isinstance(y, NBTTag): y = y.value
                            if isinstance(z, NBTTag): z = z.value
                            
                            found_blocks.append({
                                'id': te_id,
                                'x': x,
                                'y': y,
                                'z': z,
                                'region': region_path.name,
                                'chunk': (cx, cz)
                            })
                            
                except Exception as e:
                    # Ignoruj błędy pojedynczych chunków
                    pass
                    
    except Exception as e:
        print(f"  Błąd odczytu regionu {region_path.name}: {e}")
    
    return found_blocks


def scan_world(world_path: Path, output_dir: Path = None) -> dict:
    """
    Skanuje cały świat w poszukiwaniu bloków Enchanting Plus.
    
    Args:
        world_path: Ścieżka do folderu świata
        output_dir: Opcjonalna ścieżka do zapisu raportu
        
    Returns:
        Słownik z wynikami skanowania
    """
    print("=" * 60)
    print("SKANOWANIE MAPY - Enchanting Plus Blocks")
    print("=" * 60)
    print(f"Świat: {world_path}")
    print()
    
    region_dir = world_path / 'region'
    if not region_dir.exists():
        print(f"BŁĄD: Nie znaleziono folderu region: {region_dir}")
        return {'error': 'Region folder not found'}
    
    # Znajdź wszystkie pliki regionów
    region_files = list(region_dir.glob('*.mca'))
    print(f"Znaleziono {len(region_files)} plików regionów")
    print()
    
    # Skanuj każdy region
    all_found_blocks = []
    blocks_by_type = defaultdict(list)
    
    for i, region_file in enumerate(region_files, 1):
        print(f"  [{i}/{len(region_files)}] Skanowanie {region_file.name}...", end=' ')
        
        found = scan_region_file(region_file)
        all_found_blocks.extend(found)
        
        for block in found:
            blocks_by_type[block['id']].append(block)
        
        print(f"znaleziono {len(found)} bloków EP")
    
    # Podsumowanie
    print()
    print("=" * 60)
    print("PODSUMOWANIE")
    print("=" * 60)
    
    total_blocks = len(all_found_blocks)
    print(f"Łącznie znaleziono bloków EP: {total_blocks}")
    print()
    
    if total_blocks > 0:
        print("Rozkład według typów:")
        for block_id, blocks in sorted(blocks_by_type.items()):
            print(f"  {block_id}: {len(blocks)}")
        print()
        
        print("Lokalizacje:")
        for block in sorted(all_found_blocks, key=lambda b: (b['id'], b['x'], b['y'], b['z'])):
            print(f"  {block['id']} at ({block['x']}, {block['y']}, {block['z']}) in {block['region']}")
    else:
        print("Na tej mapie nie ma bloków Enchanting Plus.")
        print("Mod był prawdopodobnie zainstalowany ale nieużywany.")
    
    # Przygotuj raport
    report = {
        'world_path': str(world_path),
        'total_regions_scanned': len(region_files),
        'total_ep_blocks_found': total_blocks,
        'blocks_by_type': {
            block_id: len(blocks)
            for block_id, blocks in blocks_by_type.items()
        },
        'all_blocks': all_found_blocks,
        'conclusion': 'blocks_found' if total_blocks > 0 else 'no_blocks'
    }
    
    # Zapisz raport
    if output_dir:
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        
        report_file = output_dir / 'ep_map_scan_report.json'
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)
        
        print()
        print(f"Raport zapisany: {report_file}")
    
    return report


def main():
    """Główna funkcja skanująca mapę główną"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Skanuj mapę w poszukiwaniu bloków Enchanting Plus')
    parser.add_argument('--world', type=str, default='mapa_1710',
                       help='Ścieżka do świata 1.7.10 (domyślnie: mapa_1710)')
    parser.add_argument('--output', type=str, default='output/ep_scan',
                       help='Folder do zapisu raportu (domyślnie: output/ep_scan)')
    
    args = parser.parse_args()
    
    world_path = Path(args.world)
    if not world_path.exists():
        print(f"BŁĄD: Świat nie istnieje: {world_path}")
        print(f"Absolutna ścieżka: {world_path.absolute()}")
        sys.exit(1)
    
    report = scan_world(world_path, args.output)
    
    # Kod wyjścia
    if report.get('error'):
        sys.exit(1)
    
    # Zwróć kod wyjścia na podstawie wyników
    if report['total_ep_blocks_found'] > 0:
        print("\n⚠️  Znaleziono bloki EP - konwersja wymagana!")
        sys.exit(0)
    else:
        print("\n✅ Brak bloków EP - konwersja nie jest potrzebna.")
        sys.exit(0)


if __name__ == '__main__':
    main()
