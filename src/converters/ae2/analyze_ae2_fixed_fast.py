"""
SZYBKA analiza bloków AE2 - tylko kluczowe regiony.
"""

import sys
import json
import csv
from pathlib import Path
from typing import Dict, List, Set, Tuple, Any
from collections import defaultdict

sys.path.insert(0, 'src')

from minecraft_map_parser.anvil_parser import AnvilParser
from minecraft_map_parser.nbt_parser import NBTTag


# Wzorce ID Tile Entity AE2 w 1.7.10 (bez prefiksu!)
AE2_PATTERNS = [
    'BlockController', 'BlockDrive', 'BlockChest', 'BlockEnergy',
    'BlockCrafting', 'BlockMolecular', 'BlockQuantum', 'BlockSpatial',
    'BlockInterface', 'BlockIOPort', 'BlockCharger', 'BlockInscriber',
    'BlockCable', 'BlockCondenser', 'BlockSecurity', 'BlockWireless',
    'TileController', 'TileDrive', 'TileChest', 'TileEnergy',
    'TileCrafting', 'TileMolecular', 'TileQuantum', 'TileSpatial',
    'TileInterface', 'TileIOPort', 'TileCharger', 'TileInscriber',
    'TileCable', 'AEBaseTile'
]


def get_nbt_value(value):
    if isinstance(value, NBTTag):
        return value.value
    return value


def is_ae2_te(te_id: str) -> bool:
    if not isinstance(te_id, str):
        return False
    return any(pattern in te_id for pattern in AE2_PATTERNS)


def analyze_region(region_file: Path) -> Dict:
    """Analizuje pojedynczy region"""
    result = {
        'file': region_file.name,
        'found': [],
        'error': None
    }
    
    try:
        parser = AnvilParser(str(region_file))
        for chunk in parser.get_all_chunks():
            for te in chunk.get_tile_entities():
                te_id = get_nbt_value(te.get('id', ''))
                if is_ae2_te(te_id):
                    result['found'].append({
                        'id': te_id,
                        'x': get_nbt_value(te.get('x', 0)),
                        'y': get_nbt_value(te.get('y', 0)),
                        'z': get_nbt_value(te.get('z', 0)),
                        'chunk_x': chunk.x,
                        'chunk_z': chunk.z
                    })
    except Exception as e:
        result['error'] = str(e)
    
    return result


def main():
    print("="*60)
    print("SZYBKA ANALIZA AE2 - KLUCZOWE REGIONY")
    print("="*60)
    
    map_path = Path("mapa_1710/region")
    
    # Sprawdź czy istnieje CSV z r.0.0 - jeśli tak, zacznij od tego regionu
    existing_csv = Path("src/converters/ae2/ae2_block_entities_r.0.0.csv")
    priority_regions = []
    
    if existing_csv.exists():
        print(f"\nZnaleziono istniejący CSV: {existing_csv}")
        priority_regions.append(map_path / "r.0.0.mca")
    
    # Dodaj regiony ze stref (zdefiniowanych w coords.json)
    zones = {
        'billund': ((280, 602), (-364, -81)),
        'choroszcz': ((763, 916), (-787, -636)),
        'iii_rzesza': ((455, 966), (2955, 3477)),
        'rzym': ((301, 1005), (163, 929)),
        'zsrr': ((-2948, -2086), (-2857, -1759)),
    }
    
    def get_region_coords(x, z):
        return (x // 512, z // 512)
    
    regions_to_check = set()
    for zone_name, (x_range, z_range) in zones.items():
        rx1, rz1 = get_region_coords(x_range[0], z_range[0])
        rx2, rz2 = get_region_coords(x_range[1], z_range[1])
        for rx in range(rx1, rx2 + 1):
            for rz in range(rz1, rz2 + 1):
                regions_to_check.add((rx, rz))
    
    print(f"\nRegiony do sprawdzenia (ze stref): {len(regions_to_check)}")
    print(f"Priorytetowe regiony: {[r.name for r in priority_regions]}")
    
    # Sprawdź priorytetowe regiony
    all_found = []
    
    for region_file in priority_regions:
        print(f"\nSprawdzam priorytetowy: {region_file.name}")
        if region_file.exists():
            result = analyze_region(region_file)
            if result['found']:
                print(f"  Znaleziono {len(result['found'])} TE AE2!")
                all_found.extend(result['found'])
            else:
                print(f"  Nie znaleziono TE AE2")
        else:
            print(f"  Plik nie istnieje!")
    
    # Sprawdź regiony ze stref
    print(f"\nSprawdzanie {len(regions_to_check)} regionów ze stref...")
    checked = 0
    
    for rx, rz in sorted(regions_to_check):
        region_file = map_path / f"r.{rx}.{rz}.mca"
        if region_file.exists() and region_file not in priority_regions:
            result = analyze_region(region_file)
            checked += 1
            if result['found']:
                print(f"  {region_file.name}: {len(result['found'])} TE AE2")
                all_found.extend(result['found'])
            if checked % 20 == 0:
                print(f"  ...sprawdzono {checked}/{len(regions_to_check)} regionów...")
    
    # Podsumowanie
    print("\n" + "="*60)
    print("PODSUMOWANIE")
    print("="*60)
    
    print(f"\nŁącznie znaleziono: {len(all_found)} Tile Entities AE2")
    
    if all_found:
        # Zlicz według typu
        by_type = defaultdict(int)
        for te in all_found:
            by_type[te['id']] += 1
        
        print("\nWedług typu:")
        for te_id, count in sorted(by_type.items(), key=lambda x: -x[1]):
            print(f"  {te_id}: {count}")
        
        # Zapisz wyniki
        output_dir = Path("output/ae2_analysis")
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # CSV
        csv_file = output_dir / "ae2_found_fixed.csv"
        with open(csv_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['id', 'x', 'y', 'z', 'chunk_x', 'chunk_z'])
            for te in all_found:
                writer.writerow([
                    te['id'], te['x'], te['y'], te['z'],
                    te['chunk_x'], te['chunk_z']
                ])
        print(f"\nZapisano do: {csv_file}")
        
        # Porównanie z istniejącym CSV
        if existing_csv.exists():
            print("\n" + "="*60)
            print("PORÓWNANIE Z ISTNIEJĄCYM CSV")
            print("="*60)
            
            # Wczytaj istniejący CSV
            existing_data = []
            with open(existing_csv, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    existing_data.append(row)
            
            print(f"Istniejący CSV: {len(existing_data)} wpisów")
            print(f"Wykryte przez analizę: {len(all_found)} wpisów")
            
            # Zlicz w r.0.0
            r00_found = [te for te in all_found 
                        if 0 <= te['x'] < 512 and 0 <= te['z'] < 512]
            print(f"W regionie r.0.0 wykryte: {len(r00_found)}")
            
            # Porównanie typów
            existing_types = defaultdict(int)
            for row in existing_data:
                existing_types[row['id']] += 1
            
            found_types = defaultdict(int)
            for te in r00_found:
                found_types[te['id']] += 1
            
            print("\nPorównanie typów (istniejący CSV vs wykryte):")
            all_types = set(existing_types.keys()) | set(found_types.keys())
            for te_type in sorted(all_types):
                existing = existing_types.get(te_type, 0)
                found = found_types.get(te_type, 0)
                status = "✓" if existing == found else f"różnica ({found-existing:+d})"
                print(f"  {te_type}: CSV={existing}, Wykryte={found} {status}")


if __name__ == "__main__":
    main()
