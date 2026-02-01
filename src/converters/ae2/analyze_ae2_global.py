"""
Globalna analiza bloków AE2 na całej mapie 1.7.10.
Tylko odczyt - szukamy wszystkich regionów z blokami AE2.
"""

import json
import sys
from pathlib import Path
from typing import Dict, List, Set
from collections import defaultdict

sys.path.insert(0, 'src')

from minecraft_map_parser.anvil_parser import AnvilParser
from minecraft_map_parser.nbt_parser import NBTTag


def get_nbt_value(value):
    """Wyciąga wartość z NBTTag lub zwraca bezpośrednio"""
    if isinstance(value, NBTTag):
        return value.value
    return value


def analyze_map_for_ae2():
    """Przeszukuje całą mapę w poszukiwaniu bloków AE2"""
    map_path = Path("mapa_1710")
    region_path = map_path / "region"
    
    if not region_path.exists():
        print(f"BŁĄD: Nie znaleziono folderu regionów w {region_path}")
        return
    
    # Znajdź wszystkie pliki regionów
    region_files = list(region_path.glob("r.*.*.mca"))
    print(f"Znaleziono {len(region_files)} plików regionów")
    
    # Statystyki
    stats = {
        "regions_with_ae2": 0,
        "total_chunks_checked": 0,
        "ae2_te_found": defaultdict(int),
        "ae2_te_by_region": defaultdict(list),
        "errors": []
    }
    
    # Sprawdź tylko pierwsze 50 regionów jako próbkę (wydajność)
    # W pełnej analizie usunąć limit
    sample_size = min(100, len(region_files))
    print(f"Analizowanie próbki {sample_size} regionów...")
    
    for i, region_file in enumerate(region_files[:sample_size]):
        if i % 20 == 0:
            print(f"  Przetworzono {i}/{sample_size} regionów...")
        
        try:
            parser = AnvilParser(str(region_file))
            chunks = parser.get_all_chunks()
            
            region_has_ae2 = False
            region_coords = parser.get_region_coordinates()
            
            for chunk in chunks:
                stats["total_chunks_checked"] += 1
                
                # Sprawdź tile entities
                for te in chunk.get_tile_entities():
                    te_id = get_nbt_value(te.get('id', ''))
                    if isinstance(te_id, str) and 'appliedenergistics2' in te_id.lower():
                        stats["ae2_te_found"][te_id] += 1
                        if not region_has_ae2:
                            region_has_ae2 = True
                            stats["regions_with_ae2"] += 1
                        stats["ae2_te_by_region"][region_coords].append({
                            "te_id": te_id,
                            "chunk": (chunk.x, chunk.z)
                        })
                        
        except Exception as e:
            stats["errors"].append(f"{region_file.name}: {str(e)}")
    
    # Zapisz raport
    save_global_report(stats, sample_size, len(region_files))
    
    return stats


def save_global_report(stats: dict, sample_size: int, total_regions: int):
    """Zapisuje raport globalny"""
    output_dir = Path("output/ae2_analysis")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Konwertuj defaultdict do dict dla JSON
    report = {
        "sample_size": sample_size,
        "total_regions": total_regions,
        "regions_with_ae2": stats["regions_with_ae2"],
        "total_chunks_checked": stats["total_chunks_checked"],
        "ae2_te_found": dict(stats["ae2_te_found"]),
        "errors_count": len(stats["errors"])
    }
    
    json_file = output_dir / "global_ae2_analysis.json"
    with open(json_file, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    
    # Raport tekstowy
    text_file = output_dir / "global_ae2_analysis.txt"
    with open(text_file, 'w', encoding='utf-8') as f:
        f.write("="*60 + "\n")
        f.write("GLOBALNA ANALIZA AE2 NA MAPIE 1.7.10\n")
        f.write("="*60 + "\n\n")
        
        f.write(f"Próbka: {sample_size}/{total_regions} regionów\n")
        f.write(f"Regiony z AE2: {stats['regions_with_ae2']}\n")
        f.write(f"Sprawdzone chunki: {stats['total_chunks_checked']}\n\n")
        
        f.write("-"*60 + "\n")
        f.write("ZNALEZIONE TILE ENTITIES AE2:\n")
        f.write("-"*60 + "\n")
        
        if stats["ae2_te_found"]:
            for te_id, count in sorted(stats["ae2_te_found"].items(), key=lambda x: -x[1]):
                f.write(f"  {te_id}: {count}\n")
        else:
            f.write("  Brak Tile Entities AE2 w próbce\n")
        
        f.write("\n" + "-"*60 + "\n")
        f.write("REGIONY Z AE2:\n")
        f.write("-"*60 + "\n")
        
        if stats["ae2_te_by_region"]:
            for region, tes in sorted(stats["ae2_te_by_region"].items()):
                f.write(f"  Region {region}: {len(tes)} TE\n")
        
        if stats["errors"]:
            f.write(f"\nBłędy ({len(stats['errors'])}):\n")
            for err in stats["errors"][:10]:
                f.write(f"  ! {err}\n")
    
    print(f"\n{'='*60}")
    print("RAPORT GLOBALNY:")
    print(f"{'='*60}")
    print(f"Próbka: {sample_size}/{total_regions} regionów")
    print(f"Regiony z AE2: {stats['regions_with_ae2']}")
    print(f"Sprawdzone chunki: {stats['total_chunks_checked']}")
    
    if stats["ae2_te_found"]:
        print(f"\nZnalezione Tile Entities AE2:")
        for te_id, count in sorted(stats["ae2_te_found"].items(), key=lambda x: -x[1]):
            print(f"  - {te_id}: {count}")
    else:
        print("\nBrak Tile Entities AE2 w próbce")
    
    print(f"\nRaport zapisano do:")
    print(f"  - {json_file}")
    print(f"  - {text_file}")


if __name__ == "__main__":
    print("="*60)
    print("GLOBALNA ANALIZA AE2 NA MAPIE 1.7.10")
    print("TRYB: TYLKO ODCZYT (próbka regionów)")
    print("="*60)
    
    analyze_map_for_ae2()
