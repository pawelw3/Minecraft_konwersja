"""
POPRAWIONA analiza bloków AE2 na mapie 1.7.10.

Poprzednia analiza nie wykrywała AE2, ponieważ szukała 'appliedenergistics2' w ID Tile Entity,
ale AE2 1.7.10 używa ID bez prefiksu: "BlockDrive", "BlockController", "BlockInterface", itp.
"""

import sys
import json
from pathlib import Path
from typing import Dict, List, Set, Tuple, Any
from collections import defaultdict

sys.path.insert(0, 'src')

from minecraft_map_parser.anvil_parser import AnvilParser, get_region_for_block
from minecraft_map_parser.nbt_parser import NBTTag


# Wszystkie możliwe ID Tile Entity dla AE2 w 1.7.10
# (bez prefiksu "appliedenergistics2:tile." - tak są zapisane w NBT!)
AE2_TE_PATTERNS_1710 = {
    # Core network
    'BlockController', 'TileController',
    'BlockDrive', 'TileDrive',
    'BlockChest', 'TileChest',
    'BlockEnergyAcceptor', 'TileEnergyAcceptor',
    'BlockEnergyCell', 'TileEnergyCell',
    'BlockDenseEnergyCell', 'TileDenseEnergyCell',
    
    # Crafting
    'BlockCraftingUnit', 'TileCraftingUnit',
    'BlockCraftingStorage', 'TileCraftingStorage',
    'BlockCraftingMonitor', 'TileCraftingMonitor',
    'BlockMolecularAssembler', 'TileMolecularAssembler',
    
    # Interface & IO
    'BlockInterface', 'TileInterface',
    'BlockIOPort', 'TileIOPort',
    
    # Quantum
    'BlockQuantumRing', 'TileQuantumRing',
    'BlockQuantumLinkChamber', 'TileQuantumLinkChamber',
    
    # Spatial
    'BlockSpatialIOPort', 'TileSpatialIOPort',
    'BlockSpatialPylon', 'TileSpatialPylon',
    
    # Utility
    'BlockCharger', 'TileCharger',
    'BlockInscriber', 'TileInscriber',
    'BlockVibrationChamber', 'TileVibrationChamber',
    'BlockQuartzGrowthAccelerator', 'TileQuartzGrowthAccelerator',
    'BlockCondenser', 'TileCondenser',
    'BlockGrinder', 'TileGrinder',
    'BlockCrank', 'TileCrank',
    'BlockSkyChest', 'TileSkyChest',
    'BlockTinyTNT', 'TileTinyTNT',
    'BlockLightDetector', 'TileLightDetector',
    'BlockQuartzFixture', 'TileQuartzFixture',
    
    # Wireless & Security
    'BlockWireless', 'TileWireless',
    'BlockSecurity', 'TileSecurity',
    
    # Cable Bus (multipart)
    'BlockCableBus', 'TileCableBus',
    
    # Ogólne klasy bazowe (fallback)
    'AEBaseTile', 'AEBaseInvTile',
}


def get_nbt_value(value):
    """Wyciąga wartość z NBTTag lub zwraca bezpośrednio"""
    if isinstance(value, NBTTag):
        return value.value
    return value


def is_ae2_tile_entity(te_id: str) -> bool:
    """Sprawdza czy ID Tile Entity należy do AE2"""
    if not isinstance(te_id, str):
        return False
    
    te_id = te_id.strip()
    
    # Bezpośrednie dopasowanie do znanych wzorców AE2
    if te_id in AE2_TE_PATTERNS_1710:
        return True
    
    # Sprawdź czy zawiera charakterystyczne nazwy AE2
    te_lower = te_id.lower()
    ae2_patterns = [
        'blockcontroller', 'blockdrive', 'blockinterface', 'blockchest',
        'blockenergy', 'blockcrafting', 'blockmolecular', 'blockquantum',
        'blockspatial', 'blockcharger', 'blockinscriber', 'blockcable',
        'tilecontroller', 'tiledrive', 'tileinterface', 'tilechest',
        'tileenergy', 'tilecrafting', 'tilemolecular', 'tilequantum',
        'tilespatial', 'tilecharger', 'tileinscriber', 'tilecable',
        'aebasetile', 'appliedenergistics'
    ]
    
    return any(pattern in te_lower for pattern in ae2_patterns)


def analyze_region_for_ae2(region_file: Path) -> Dict[str, Any]:
    """Analizuje pojedynczy region pod kątem AE2"""
    stats = {
        'region_file': region_file.name,
        'chunks_checked': 0,
        'ae2_te_found': defaultdict(list),  # te_id -> lista pozycji
        'errors': []
    }
    
    try:
        parser = AnvilParser(str(region_file))
        chunks = parser.get_all_chunks()
        
        for chunk in chunks:
            stats['chunks_checked'] += 1
            
            for te in chunk.get_tile_entities():
                te_id = get_nbt_value(te.get('id', ''))
                
                if is_ae2_tile_entity(te_id):
                    # Pobierz pozycję
                    x = get_nbt_value(te.get('x', 0))
                    y = get_nbt_value(te.get('y', 0))
                    z = get_nbt_value(te.get('z', 0))
                    
                    stats['ae2_te_found'][te_id].append({
                        'x': x, 'y': y, 'z': z,
                        'chunk_x': chunk.x,
                        'chunk_z': chunk.z
                    })
                    
    except Exception as e:
        stats['errors'].append(str(e))
    
    return stats


def analyze_all_regions():
    """Analizuje wszystkie regiony na mapie"""
    map_path = Path("mapa_1710/region")
    
    if not map_path.exists():
        print(f"BŁĄD: Nie znaleziono folderu {map_path}")
        return
    
    region_files = sorted(map_path.glob("r.*.*.mca"))
    print(f"Znaleziono {len(region_files)} plików regionów")
    
    # Globalne statystyki
    global_stats = {
        'regions_with_ae2': 0,
        'total_ae2_te': 0,
        'te_by_type': defaultdict(int),
        'te_by_region': defaultdict(int),
        'all_positions': [],
        'errors': []
    }
    
    print("\nAnalizowanie regionów...")
    
    for i, region_file in enumerate(region_files):
        if i % 100 == 0 and i > 0:
            print(f"  Przetworzono {i}/{len(region_files)} regionów...")
        
        result = analyze_region_for_ae2(region_file)
        
        if result['ae2_te_found']:
            global_stats['regions_with_ae2'] += 1
            region_te_count = sum(len(v) for v in result['ae2_te_found'].values())
            global_stats['te_by_region'][result['region_file']] = region_te_count
            global_stats['total_ae2_te'] += region_te_count
            
            for te_id, positions in result['ae2_te_found'].items():
                global_stats['te_by_type'][te_id] += len(positions)
                global_stats['all_positions'].extend([
                    {'id': te_id, **pos} for pos in positions
                ])
        
        if result['errors']:
            global_stats['errors'].extend(result['errors'])
    
    return global_stats


def export_to_csv(positions: List[Dict], output_file: Path):
    """Eksportuje pozycje do CSV"""
    import csv
    
    with open(output_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['id', 'x', 'y', 'z', 'chunk_x', 'chunk_z'])
        
        for pos in positions:
            writer.writerow([
                pos['id'],
                pos['x'],
                pos['y'],
                pos['z'],
                pos['chunk_x'],
                pos['chunk_z']
            ])


def main():
    print("="*60)
    print("POPRAWIONA ANALIZA AE2 NA MAPIE 1.7.10")
    print("="*60)
    print(f"\nWzorce AE2 do wykrycia: {len(AE2_TE_PATTERNS_1710)}")
    
    stats = analyze_all_regions()
    
    if not stats:
        return
    
    # Wyświetl wyniki
    print("\n" + "="*60)
    print("WYNIKI ANALIZY")
    print("="*60)
    
    print(f"\nRegiony z AE2: {stats['regions_with_ae2']}")
    print(f"Całkowita liczba TE AE2: {stats['total_ae2_te']}")
    
    if stats['te_by_type']:
        print(f"\nTile Entities AE2 według typu:")
        for te_id, count in sorted(stats['te_by_type'].items(), key=lambda x: -x[1]):
            print(f"  {te_id}: {count}")
    
    if stats['regions_with_ae2'] > 0:
        print(f"\nRegiony z największą ilością AE2:")
        top_regions = sorted(stats['te_by_region'].items(), key=lambda x: -x[1])[:10]
        for region, count in top_regions:
            print(f"  {region}: {count} TE")
    
    # Zapisz raport
    output_dir = Path("output/ae2_analysis")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # JSON
    report_file = output_dir / "ae2_analysis_fixed.json"
    with open(report_file, 'w', encoding='utf-8') as f:
        json.dump({
            'regions_with_ae2': stats['regions_with_ae2'],
            'total_ae2_te': stats['total_ae2_te'],
            'te_by_type': dict(stats['te_by_type']),
            'te_by_region': dict(stats['te_by_region'])
        }, f, indent=2, ensure_ascii=False)
    
    # CSV
    if stats['all_positions']:
        csv_file = output_dir / "ae2_block_entities_all.csv"
        export_to_csv(stats['all_positions'], csv_file)
        print(f"\nZapisano {len(stats['all_positions'])} pozycji do {csv_file}")
    
    print(f"\nRaport JSON: {report_file}")
    
    # Porównanie z istniejącym CSV
    existing_csv = Path("src/converters/ae2/ae2_block_entities_r.0.0.csv")
    if existing_csv.exists():
        print("\n" + "="*60)
        print("PORÓWNANIE Z ISTNIEJĄCYM CSV (r.0.0)")
        print("="*60)
        
        # Zlicz TE w regionie r.0.0
        r00_tes = [p for p in stats['all_positions'] 
                   if 0 <= p['x'] < 512 and 0 <= p['z'] < 512]
        
        print(f"Wykryto w r.0.0: {len(r00_tes)} TE")
        
        # Zlicz według typu w r.0.0
        r00_by_type = defaultdict(int)
        for p in r00_tes:
            r00_by_type[p['id']] += 1
        
        print("\nWedług typu w regionie r.0.0:")
        for te_id, count in sorted(r00_by_type.items(), key=lambda x: -x[1]):
            print(f"  {te_id}: {count}")


if __name__ == "__main__":
    main()
