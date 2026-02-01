"""
Analiza bloków AE2 w strefach głównej mapy (mapa_1710).
Tylko odczyt - bez żadnych modyfikacji mapy!
"""

import json
import sys
from pathlib import Path
from typing import Dict, List, Set, Tuple, Any
from collections import defaultdict

# Dodaj src do path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from minecraft_map_parser.anvil_parser import AnvilParser
# parse_nbt_file nie jest dostępne, używamy parse_nbt z anvil_parser


# Strefy z coords.json
ZONES = {
    "billund": {"x_range": (280, 602), "z_range": (-364, -81)},
    "choroszcz": {"x_range": (763, 916), "z_range": (-787, -636)},
    "iii_rzesza": {"x_range": (455, 966), "z_range": (2955, 3477)},
    "rzym": {"x_range": (301, 1005), "z_range": (163, 929)},
    "zsrr": {"x_range": (-2948, -2086), "z_range": (-2857, -1759)},
}

# ID bloków AE2 do wykrycia
AE2_BLOCK_PATTERNS = [
    "appliedenergistics2",
]


def get_region_coords(x: int, z: int) -> Tuple[int, int]:
    """Konwertuje współrzędne świata na współrzędne regionu"""
    return (x >> 5, z >> 5)


def analyze_zone(zone_name: str, zone_data: dict, map_path: Path) -> Dict[str, Any]:
    """Analizuje strefę pod kątem bloków AE2"""
    
    x_range = zone_data["x_range"]
    z_range = zone_data["z_range"]
    
    # Znajdź regiony do sprawdzenia
    regions_to_check = set()
    for x in range(x_range[0], x_range[1] + 1, 512):  # co region (512 bloki)
        for z in range(z_range[0], z_range[1] + 1, 512):
            rx, rz = get_region_coords(x, z)
            regions_to_check.add((rx, rz))
    
    print(f"\n{'='*60}")
    print(f"Strefa: {zone_name}")
    print(f"Zakres X: {x_range}, Z: {z_range}")
    print(f"Regiony do sprawdzenia: {len(regions_to_check)}")
    print(f"{'='*60}")
    
    # Statystyki
    stats = {
        "zone": zone_name,
        "regions_checked": 0,
        "chunks_checked": 0,
        "ae2_blocks_found": defaultdict(int),
        "ae2_tile_entities": defaultdict(int),
        "errors": []
    }
    
    for rx, rz in sorted(regions_to_check):
        region_file = map_path / f"region/r.{rx}.{rz}.mca"
        
        if not region_file.exists():
            continue
            
        stats["regions_checked"] += 1
        
        try:
            parser = AnvilParser(str(region_file))
            chunks = parser.get_all_chunks()
            
            for chunk in chunks:
                stats["chunks_checked"] += 1
                
                # Sprawdź tile entities (AE2 używa TE dla wszystkich urządzeń)
                for te in chunk.get_tile_entities():
                    te_id = te.get('id', '')
                    if 'appliedenergistics2' in te_id.lower():
                        stats["ae2_tile_entities"][te_id] += 1
                        
        except Exception as e:
            stats["errors"].append(f"Region {rx},{rz}: {str(e)}")
    
    return stats


def analyze_all_zones():
    """Analizuje wszystkie strefy"""
    map_path = Path("mapa_1710")
    
    if not map_path.exists():
        print(f"BŁĄD: Nie znaleziono mapy w {map_path}")
        return
    
    all_results = []
    
    for zone_name, zone_data in ZONES.items():
        result = analyze_zone(zone_name, zone_data, map_path)
        all_results.append(result)
        
        # Podsumowanie strefy
        print(f"\n--- Podsumowanie strefy {zone_name} ---")
        print(f"Sprawdzone regiony: {result['regions_checked']}")
        print(f"Sprawdzone chunki: {result['chunks_checked']}")
        
        if result['ae2_tile_entities']:
            print(f"\nZnalezione Tile Entities AE2:")
            for te_id, count in sorted(result['ae2_tile_entities'].items()):
                print(f"  - {te_id}: {count}")
        else:
            print("\nBrak Tile Entities AE2 w tej strefie")
            
        if result['errors']:
            print(f"\nBłędy ({len(result['errors'])}):")
            for err in result['errors'][:5]:
                print(f"  ! {err}")
    
    # Zapisz raport
    save_report(all_results)


def save_report(results: List[Dict]):
    """Zapisuje raport do pliku"""
    output_dir = Path("output/ae2_analysis")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Podsumowanie wszystkich stref
    summary = {
        "total_regions": sum(r['regions_checked'] for r in results),
        "total_chunks": sum(r['chunks_checked'] for r in results),
        "zones_with_ae2": [],
        "all_ae2_te": defaultdict(int),
        "coverage_report": {}
    }
    
    for r in results:
        if r['ae2_tile_entities']:
            summary["zones_with_ae2"].append(r['zone'])
            for te_id, count in r['ae2_tile_entities'].items():
                summary["all_ae2_te"][te_id] += count
    
    # Konwertuj defaultdict do dict dla JSON
    summary["all_ae2_te"] = dict(summary["all_ae2_te"])
    
    # Sprawdź pokrycie kodu konwersji
    from converters.ae2.mappings.block_mappings import ALL_AE2_BLOCK_IDS_1710
    
    found_te_ids = set(summary["all_ae2_te"].keys())
    mapped_ids = set(ALL_AE2_BLOCK_IDS_1710)
    
    # Mapowanie TE -> bloki (uproszczone)
    te_to_block = {
        'TileController': 'BlockController',
        'TileDrive': 'BlockDrive',
        'TileChest': 'BlockChest',
        'TileEnergyAcceptor': 'BlockEnergyAcceptor',
        'TileEnergyCell': 'BlockEnergyCell',
        'TileDenseEnergyCell': 'BlockDenseEnergyCell',
        'TileCraftingUnit': 'BlockCraftingUnit',
        'TileCraftingStorage': 'BlockCraftingStorage',
        'TileCraftingMonitor': 'BlockCraftingMonitor',
        'TileMolecularAssembler': 'BlockMolecularAssembler',
        'TileInterface': 'BlockInterface',
        'TileIOPort': 'BlockIOPort',
        'TileQuantumBridge': 'BlockQuantumRing',
        'TileQuantumLinkChamber': 'BlockQuantumLinkChamber',
        'TileSpatialIOPort': 'BlockSpatialIOPort',
        'TileSpatialPylon': 'BlockSpatialPylon',
        'TileCharger': 'BlockCharger',
        'TileInscriber': 'BlockInscriber',
        'TileVibrationChamber': 'BlockVibrationChamber',
        'TileQuartzGrowthAccelerator': 'BlockQuartzGrowthAccelerator',
        'TileCondenser': 'BlockCondenser',
        'TileGrinder': 'BlockGrinder',
        'TileCrank': 'BlockCrank',
        'TileSkyChest': 'BlockSkyChest',
        'TileTinyTNT': 'BlockTinyTNT',
        'TileLightDetector': 'BlockLightDetector',
        'TileQuartzFixture': 'BlockQuartzFixture',
        'TileWireless': 'BlockWireless',
        'TileSecurity': 'BlockSecurity',
        'TileCableBus': 'BlockCableBus',
    }
    
    coverage = {
        "found_on_map": list(found_te_ids),
        "supported_by_converter": [],
        "not_supported": [],
        "not_found_on_map_but_supported": []
    }
    
    for te_id in found_te_ids:
        # Wyciągnij nazwę z TileEntity (np. TileController -> BlockController)
        block_name = None
        for te_suffix, block_suffix in te_to_block.items():
            if te_suffix in te_id:
                block_name = f"appliedenergistics2:tile.{block_suffix}"
                break
        
        if block_name and block_name in mapped_ids:
            coverage["supported_by_converter"].append(te_id)
        else:
            coverage["not_supported"].append(te_id)
    
    summary["coverage_report"] = coverage
    
    # Zapisz JSON
    report_file = output_dir / "zone_analysis_report.json"
    with open(report_file, 'w', encoding='utf-8') as f:
        json.dump({
            "summary": summary,
            "zones": results
        }, f, indent=2, ensure_ascii=False)
    
    # Zapisz tekstowy raport
    text_report = output_dir / "zone_analysis_report.txt"
    with open(text_report, 'w', encoding='utf-8') as f:
        f.write("="*60 + "\n")
        f.write("RAPORT ANALIZY AE2 W STREFACH MAPY 1.7.10\n")
        f.write("="*60 + "\n\n")
        
        f.write(f"Całkowita liczba regionów: {summary['total_regions']}\n")
        f.write(f"Całkowita liczba chunków: {summary['total_chunks']}\n")
        f.write(f"Strefy z AE2: {', '.join(summary['zones_with_ae2']) if summary['zones_with_ae2'] else 'Brak'}\n\n")
        
        f.write("-"*60 + "\n")
        f.write("ZNALEZIONE TILE ENTITIES AE2:\n")
        f.write("-"*60 + "\n")
        for te_id, count in sorted(summary['all_ae2_te'].items()):
            status = "✅" if te_id in coverage["supported_by_converter"] else "❌"
            f.write(f"{status} {te_id}: {count}\n")
        
        f.write("\n" + "-"*60 + "\n")
        f.write("RAPORT POKRYCIA KODU KONWERSJI:\n")
        f.write("-"*60 + "\n")
        f.write(f"Wspierane przez konwerter: {len(coverage['supported_by_converter'])}\n")
        f.write(f"NIE wspierane: {len(coverage['not_supported'])}\n")
        
        if coverage['not_supported']:
            f.write("\nNieobsługiwane TE:\n")
            for te_id in coverage['not_supported']:
                f.write(f"  - {te_id}\n")
    
    print(f"\n{'='*60}")
    print("Raport zapisano do:")
    print(f"  - {report_file}")
    print(f"  - {text_report}")
    print(f"{'='*60}")
    
    # Wyświetl podsumowanie
    print("\n" + "="*60)
    print("PODSUMOWANIE POKRYCIA KODU:")
    print("="*60)
    total_te = len(coverage['supported_by_converter']) + len(coverage['not_supported'])
    if total_te > 0:
        coverage_pct = len(coverage['supported_by_converter']) / total_te * 100
        print(f"Pokrycie: {coverage_pct:.1f}% ({len(coverage['supported_by_converter'])}/{total_te})")
    else:
        print("Nie znaleziono żadnych bloków AE2 na mapie")


if __name__ == "__main__":
    print("="*60)
    print("ANALIZA AE2 W STREFACH GŁÓWNEJ MAPY")
    print("TRYB: TYLKO ODCZYT (brak modyfikacji mapy)")
    print("="*60)
    
    analyze_all_zones()
