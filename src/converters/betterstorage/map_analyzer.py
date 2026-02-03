"""
Analizator mapy dla Better Storage - Zadanie 4

Sprawdza pokrycie kodu konwertera na rzeczywistej mapie 1.7.10.
Wersja zoptymalizowana - próbkowanie chunków.
"""

import json
import sys
from pathlib import Path
from typing import Dict, List, Set, Tuple, Optional, Any, Union
from collections import defaultdict
import re

# Dodaj root projektu do ścieżki
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from src.minecraft_map_parser.anvil_parser import AnvilParser
from src.minecraft_map_parser.nbt_parser import NBTTag


# Wzorce dla Better Storage (block ID i TE ID)
# UWAGA: Wzorce musza byc specyficzne - unikamy ogolnych slow jak 'crate' ktore lapia TileNPCCrate
BS_PATTERNS = [
    r'^betterstorage\.',
    r'^BetterStorage',
    r'^container\.betterstorage\.',
    r'^betterstorage\.crate',
    r'^container\.betterstorage\.crate',
    r'^betterstorage\.locker',
    r'^container\.betterstorage\.locker',
    r'^betterstorage\.reinforced',
    r'^container\.betterstorage\.reinforced',
    r'^betterstorage\.cardboard',
    r'^container\.betterstorage\.cardboard',
    r'^betterstorage\.armorstand',
    r'^betterstorage\.armorStand',
    r'^container\.betterstorage\.armorStand',
    r'^betterstorage\.backpack',
    r'^container\.betterstorage\.backpack',
    r'^betterstorage\.present',
    r'^container\.betterstorage\.present',
    r'^betterstorage\.flintBlock',
    r'^container\.betterstorage\.flintBlock',
    r'^betterstorage\.craftingStation',
    r'^container\.betterstorage\.craftingStation',
    r'^betterstorage\.thaumium',
    r'^container\.betterstorage\.thaumium',
    r'^betterstorage\.thaumcraft',
    r'^container\.betterstorage\.thaumcraft',
    r'^betterstorage\.Frienderman',  # To jest entity, nie blok
    r'^betterstorage\.enderBackpack',
    r'^container\.betterstorage\.enderBackpack',
]


def to_str(value: Union[str, NBTTag, Any]) -> str:
    """Konwertuje wartość na string (obsługuje NBTTag)"""
    if isinstance(value, NBTTag):
        return str(value.value) if value.value is not None else ''
    if value is None:
        return ''
    return str(value)


def world_to_region_coords(world_x: int, world_z: int) -> Tuple[int, int]:
    """Konwertuje współrzędne świata na współrzędne regionu"""
    return world_x // 512, world_z // 512


def get_regions_for_zone(zone_coords: List[Dict[str, int]]) -> Set[Tuple[int, int]]:
    """Zwraca zestaw regionów (.mca) dla danej strefy"""
    regions = set()
    
    # Znajdź min/max X i Z
    xs = [c['x'] for c in zone_coords]
    zs = [c['z'] for c in zone_coords]
    
    min_x, max_x = min(xs), max(xs)
    min_z, max_z = min(zs), max(zs)
    
    # Konwertuj na regiony
    min_rx, min_rz = world_to_region_coords(min_x, min_z)
    max_rx, max_rz = world_to_region_coords(max_x, max_z)
    
    # Dodaj wszystkie regiony w zakresie (z marginesem)
    for rx in range(min_rx - 1, max_rx + 2):
        for rz in range(min_rz - 1, max_rz + 2):
            regions.add((rx, rz))
    
    return regions


def load_zone_definitions(zones_dir: str = 'strefy') -> Dict[str, Set[Tuple[int, int]]]:
    """Ładuje definicje stref i zwraca mapę regionów per strefa"""
    zones = {}
    zones_path = Path(zones_dir)
    
    for zone_file in zones_path.glob('*/coords.json'):
        zone_name = zone_file.parent.name
        with open(zone_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            coords = data.get('minecraftCoordinates', [])
            regions = get_regions_for_zone(coords)
            zones[zone_name] = regions
    
    return zones


def is_better_storage_te(te_id: str) -> bool:
    """Sprawdza czy TE ID należy do Better Storage"""
    if not te_id:
        return False
    
    te_id_lower = te_id.lower()
    
    for pattern in BS_PATTERNS:
        # Uzywamy regex dla precyzyjnego dopasowania
        if re.search(pattern, te_id, re.IGNORECASE):
            return True
    
    return False


class BetterStorageMapAnalyzer:
    """Analizator mapy dla Better Storage"""
    
    def __init__(self, world_path: str):
        self.world_path = Path(world_path)
        self.region_path = self.world_path / 'region'
        
        # Wyniki analizy
        self.found_te_ids: Set[str] = set()
        self.found_block_ids: Set[str] = set()
        self.blocks_by_zone: Dict[str, List[Dict]] = defaultdict(list)
        self.all_blocks: List[Dict] = []
        
        # Statystyki
        self.stats = {
            'regions_scanned': 0,
            'chunks_scanned': 0,
            'te_found': 0,
            'bs_blocks_found': 0,
        }
    
    def analyze_region(self, region_x: int, region_z: int, sample_chunks: Optional[int] = None) -> List[Dict]:
        """Analizuje pojedynczy plik regionu"""
        region_file = self.region_path / f"r.{region_x}.{region_z}.mca"
        
        if not region_file.exists():
            return []
        
        results = []
        
        try:
            parser = AnvilParser(str(region_file))
            
            # Jeśli sample_chunks, próbkuj co N-ty chunk
            chunk_coords = [(cx, cz) for cz in range(32) for cx in range(32)]
            if sample_chunks and len(chunk_coords) > sample_chunks:
                step = len(chunk_coords) // sample_chunks
                chunk_coords = chunk_coords[::step][:sample_chunks]
            
            for cx, cz in chunk_coords:
                chunk = parser.get_chunk(cx, cz)
                if not chunk:
                    continue
                
                self.stats['chunks_scanned'] += 1
                
                # Pobierz TileEntities - ChunkData ma metodę get_tile_entities()
                tile_entities = chunk.get_tile_entities()
                
                for te in tile_entities:
                    te_id = to_str(te.get('id', ''))
                    block_id = to_str(te.get('block_id', ''))
                    
                    self.found_te_ids.add(te_id)
                    if block_id:
                        self.found_block_ids.add(block_id)
                    
                    self.stats['te_found'] += 1
                    
                    # Sprawdź czy to Better Storage
                    if is_better_storage_te(te_id):
                        result = {
                            'x': te.get('x', 0),
                            'y': te.get('y', 0),
                            'z': te.get('z', 0),
                            'te_id': te_id,
                            'block_id': block_id,
                            'nbt_keys': [to_str(k) for k in te.keys()],
                            'region': (region_x, region_z),
                            'chunk': (cx, cz),
                        }
                        results.append(result)
                        self.stats['bs_blocks_found'] += 1
            
            self.stats['regions_scanned'] += 1
            
        except Exception as e:
            print(f"  Blad podczas analizy {region_file}: {e}")
        
        return results
    
    def analyze_zones(self, zones: Dict[str, Set[Tuple[int, int]]], sample_per_region: int = 10):
        """Analizuje wszystkie strefy (z próbkowaniem dla szybkości)"""
        for zone_name, regions in zones.items():
            print(f"\n=== Analiza strefy: {zone_name} ===")
            print(f"Regiony do przeskanowania: {len(regions)}")
            
            # Skanujemy wszystkie regiony w strefie (bez limitu)
            regions_list = sorted(regions)
            
            for rx, rz in regions_list:
                # Pełny skan bez próbkowania
                blocks = self.analyze_region(rx, rz, sample_chunks=None)
                if blocks:
                    self.blocks_by_zone[zone_name].extend(blocks)
                    print(f"  r.{rx}.{rz}.mca: {len(blocks)} blokow BS")
            
            total = len(self.blocks_by_zone[zone_name])
            print(f"Strefa {zone_name}: {total} blokow BS")
    
    def analyze_additional_regions(self, regions: List[Tuple[int, int]], sample_per_region: int = 10):
        """Analizuje dodatkowe regiony (spawn, okolice)"""
        print("\n=== Analiza dodatkowych regionow ===")
        
        for rx, rz in regions:
            blocks = self.analyze_region(rx, rz, sample_chunks=sample_per_region)
            if blocks:
                self.blocks_by_zone['additional'].extend(blocks)
                print(f"  r.{rx}.{rz}.mca: {len(blocks)} blokow BS")
    
    def get_bs_te_ids(self) -> Set[str]:
        """Zwraca TE ID które wyglądają na Better Storage"""
        bs_ids = set()
        for te_id in self.found_te_ids:
            if is_better_storage_te(te_id):
                bs_ids.add(te_id)
        return bs_ids
    
    def get_coverage_report(self) -> Dict[str, Any]:
        """Generuje raport pokrycia"""
        bs_te_ids = self.get_bs_te_ids()
        
        # Znane TE ID z kodu konwertera (batch_converter.BS_BLOCK_IDS)
        # UWAGA: Na mapie uzywany jest format 'container.betterstorage.xxx' a nie 'betterstorage:xxx'
        known_block_ids = {
            'betterstorage:crate',
            'betterstorage:reinforcedChest',
            'betterstorage:reinforcedLocker',
            'betterstorage:locker',
            'betterstorage:cardboardBox',
            'betterstorage:craftingStation',
            'betterstorage:armorStand',
            'betterstorage:backpack',
            'betterstorage:enderBackpack',
            'betterstorage:present',
            'betterstorage:lockableDoor',
            'betterstorage:flintBlock',
            'betterstorage:thaumiumChest',
            'betterstorage:thaumcraftBackpack',
            # Format z mapy (container.betterstorage.xxx)
            'container.betterstorage.crate',
            'container.betterstorage.reinforcedChest',
            'container.betterstorage.reinforcedLocker',
            'container.betterstorage.locker',
            'container.betterstorage.cardboardBox',
            'container.betterstorage.craftingStation',
            'container.betterstorage.armorStand',
            'container.betterstorage.backpack',
            'container.betterstorage.enderBackpack',
            'container.betterstorage.present',
            'container.betterstorage.lockableDoor',
            'container.betterstorage.flintBlock',
            'container.betterstorage.thaumiumChest',
            'container.betterstorage.thaumcraftBackpack',
        }
        
        # Sprawdź które są obsługiwane
        covered = bs_te_ids & known_block_ids
        not_covered = bs_te_ids - known_block_ids
        
        return {
            'total_bs_blocks': self.stats['bs_blocks_found'],
            'unique_te_ids_found': sorted(bs_te_ids),
            'covered_by_converter': sorted(covered),
            'not_covered': sorted(not_covered),
            'coverage_percent': len(covered) / len(bs_te_ids) * 100 if bs_te_ids else 100,
        }
    
    def save_report(self, output_path: str):
        """Zapisuje raport do pliku"""
        # Konwertuj wszystkie wartości na JSON-serializowalne
        def convert_value(v):
            if isinstance(v, NBTTag):
                return str(v.value) if v.value is not None else None
            if isinstance(v, (list, tuple)):
                return [convert_value(x) for x in v]
            if isinstance(v, dict):
                return {k: convert_value(val) for k, val in v.items()}
            return v
        
        report = {
            'stats': self.stats,
            'found_te_ids': sorted(self.found_te_ids),
            'found_block_ids': sorted(self.found_block_ids),
            'bs_blocks_by_zone': {
                zone: [
                    {
                        'x': convert_value(b['x']), 
                        'y': convert_value(b['y']), 
                        'z': convert_value(b['z']),
                        'te_id': b['te_id'], 
                        'block_id': b['block_id']
                    }
                    for b in blocks
                ]
                for zone, blocks in self.blocks_by_zone.items()
            },
            'coverage': self.get_coverage_report(),
        }
        
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        print(f"\nRaport zapisany do: {output_path}")


def main():
    """Główna funkcja analizy"""
    print("=" * 70)
    print("ANALIZA POKRYCIA - BETTER STORAGE (Zadanie 4)")
    print("Wersja z probkowaniem (szybka)")
    print("=" * 70)
    
    world_path = 'mapa_1710'
    
    # Inicjalizacja analizatora
    analyzer = BetterStorageMapAnalyzer(world_path)
    
    # Załaduj definicje stref
    zones = load_zone_definitions()
    print(f"\nZnaleziono {len(zones)} stref:")
    for name, regions in zones.items():
        print(f"  - {name}: {len(regions)} regionow")
    
    # Analizuj strefy (PEŁNY skan - bez próbkowania)
    analyzer.analyze_zones(zones, sample_per_region=None)
    
    # Analizuj dodatkowe regiony
    additional_regions = [
        (0, 0),    # Spawn
        (1, 1),    # Okolice spawnu
        (-1, -1),
    ]
    analyzer.analyze_additional_regions(additional_regions, sample_per_region=None)
    
    # Podsumowanie
    print("\n" + "=" * 70)
    print("PODSUMOWANIE")
    print("=" * 70)
    print(f"Przeskanowane regiony: {analyzer.stats['regions_scanned']}")
    print(f"Przeskanowane chunki: {analyzer.stats['chunks_scanned']}")
    print(f"Wszystkich TileEntities: {analyzer.stats['te_found']}")
    print(f"Znaleziono blokow BS: {analyzer.stats['bs_blocks_found']}")
    
    # Unikalne TE ID
    bs_te_ids = analyzer.get_bs_te_ids()
    print(f"\nUnikalne TE ID Better Storage: {len(bs_te_ids)}")
    for te_id in sorted(bs_te_ids):
        print(f"  - {te_id}")
    
    # Raport pokrycia
    coverage = analyzer.get_coverage_report()
    print(f"\n--- RAPORT POKRYCIA ---")
    print(f"Obslugiwane przez konwerter: {len(coverage['covered_by_converter'])}/{len(bs_te_ids)} ({coverage['coverage_percent']:.1f}%)")
    
    if coverage['not_covered']:
        print(f"\nNIEobslugiwane TE ID:")
        for te_id in coverage['not_covered']:
            print(f"  [WARN] {te_id}")
    else:
        print("\n[OK] Wszystkie znalezione TE ID sa obslugiwane przez konwerter")
    
    # Zapisz raport
    analyzer.save_report('output/betterstorage_coverage_report.json')
    
    return analyzer


if __name__ == '__main__':
    analyzer = main()
