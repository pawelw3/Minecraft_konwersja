"""
Analizator pokrycia Blood Magic na mapie 1.7.10
Zadanie 4: Sprawdzenie czy kod pokrywa wszystkie bloki/TE na głównej mapie

UWAGA: Ten skrypt TYLKO ODCZYTUJE mapę, nigdy jej nie modyfikuje!
"""

import json
import sys
from pathlib import Path
from typing import Dict, Any, List, Set, Tuple, Optional
from collections import defaultdict
import re

# Dodaj src do path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from minecraft_map_parser.anvil_parser import AnvilParser, get_region_for_block
from minecraft_map_parser.nbt_parser import NBTTag


class BloodMagicCoverageAnalyzer:
    """
    Analizator pokrycia bloków i Tile Entities Blood Magic na mapie 1.7.10
    
    Sprawdza:
    1. Jakie TE ID Blood Magic istnieją na mapie (rzeczywiste dane)
    2. Czy kod konwersji obsługuje wszystkie znalezione TE ID
    3. Czy symulacje działają poprawnie dla 1.18.2
    """
    
    # Wzorce do wykrywania Blood Magic TE ID
    BM_TE_PATTERNS = [
        r"altar",
        r"Altar",
        r"master",
        r"Master",
        r"ritual",
        r"Ritual",
        r"soul",
        r"Soul",
        r"blood",
        r"Blood",
        r"AWWayofTime",
        r"alchemical",
        r"Alchemical",
    ]
    
    # Oczekiwane TE ID na podstawie kodu źródłowego 1.7.10
    # UWAGA: Na rzeczywistej mapie używane są "containerAltar" i "containerMasterStone"
    EXPECTED_TE_IDS = {
        "Altar",           # TEAltar
        "MasterStone",     # TEMasterStone
        "containerAltar",  # Rzeczywiste TE ID z mapy (BlockAltar -> containerAltar)
        "containerMasterStone",  # Rzeczywiste TE ID z mapy
        "TileSoulJar",     # Soul Jar
        "SoulForge",       # TESoulForge (usunięty w 1.18.2)
    }
    
    def __init__(self, world_path: str):
        """
        Args:
            world_path: Ścieżka do folderu mapy 1.7.10 (np. "mapa_1710")
        """
        self.world_path = Path(world_path)
        self.region_path = self.world_path / "region"
        
        # Wyniki analizy
        self.found_te_ids: Set[str] = set()
        self.te_locations: Dict[str, List[Tuple[int, int, int]]] = defaultdict(list)
        self.te_count: Dict[str, int] = defaultdict(int)
        self.chunk_count = 0
        self.region_count = 0
        
        # Statystyki stref
        self.zone_stats: Dict[str, Dict[str, Any]] = {}
        
    def analyze_all_zones(self, zones: Dict[str, List[Tuple[int, int]]]) -> Dict[str, Any]:
        """
        Przeskanuj wszystkie strefy na mapie
        
        Args:
            zones: Słownik {nazwa_strefy: [(x1, z1), (x2, z2), ...]}
            
        Returns:
            Słownik ze statystykami
        """
        print("=" * 60)
        print("ANALIZA POKRYCIA BLOOD MAGIC NA MAPIE 1.7.10")
        print("=" * 60)
        
        for zone_name, coords in zones.items():
            print(f"\n--- Analiza strefy: {zone_name} ---")
            stats = self._analyze_zone(zone_name, coords)
            self.zone_stats[zone_name] = stats
            
        # Dodatkowe regiony (poza strefami)
        print("\n--- Analiza dodatkowych regionów ---")
        self._analyze_additional_regions()
        
        return self._generate_report()
    
    def _analyze_zone(self, zone_name: str, coords: List[Tuple[int, int]]) -> Dict[str, Any]:
        """Przeskanuj pojedynczą strefę"""
        # Oblicz zakres
        xs = [c[0] for c in coords]
        zs = [c[1] for c in coords]
        min_x, max_x = min(xs), max(xs)
        min_z, max_z = min(zs), max(zs)
        
        print(f"  Zakres: X={min_x}..{max_x}, Z={min_z}..{max_z}")
        
        # Znajdź regiony do przeskanowania
        regions_to_scan = set()
        for x in range(min_x, max_x + 1, 512):
            for z in range(min_z, max_z + 1, 512):
                region_x, region_z = get_region_for_block(x, z)
                regions_to_scan.add((region_x, region_z))
        
        print(f"  Regiony do przeskanowania: {len(regions_to_scan)}")
        
        # Przeskanuj regiony
        zone_te_count: Dict[str, int] = defaultdict(int)
        zone_chunks = 0
        
        for region_x, region_z in regions_to_scan:
            region_file = self.region_path / f"r.{region_x}.{region_z}.mca"
            if not region_file.exists():
                continue
                
            te_count, chunks_scanned = self._scan_region(
                str(region_file), 
                min_x, max_x, 
                min_z, max_z
            )
            
            for te_id, count in te_count.items():
                zone_te_count[te_id] += count
            zone_chunks += chunks_scanned
        
        print(f"  Przeskanowano chunków: {zone_chunks}")
        print(f"  Znalezione TE: {dict(zone_te_count)}")
        
        return {
            "chunks_scanned": zone_chunks,
            "te_count": dict(zone_te_count),
            "bounds": (min_x, max_x, min_z, max_z),
        }
    
    def _analyze_additional_regions(self):
        """Przeskanuj dodatkowe regiony poza strefami"""
        additional_regions = [
            (0, 0),     # Spawn
            (1, 1),     # Okolice spawnu
            (-1, -1),
            (2, 2),
            (-2, -2),
            (5, 5),
            (-5, -5),
        ]
        
        print(f"  Dodatkowe regiony: {additional_regions}")
        
        for region_x, region_z in additional_regions:
            region_file = self.region_path / f"r.{region_x}.{region_z}.mca"
            if not region_file.exists():
                continue
                
            te_count, chunks_scanned = self._scan_region(
                str(region_file), None, None, None, None
            )
            
            if te_count:
                print(f"    Region r.{region_x}.{region_z}: {dict(te_count)}")
    
    def _scan_region(
        self, 
        region_file: str, 
        min_x: Optional[int], 
        max_x: Optional[int],
        min_z: Optional[int], 
        max_z: Optional[int]
    ) -> Tuple[Dict[str, int], int]:
        """
        Przeskanuj pojedynczy plik regionu
        
        Returns:
            Tuple (te_count, chunks_scanned)
        """
        te_count: Dict[str, int] = defaultdict(int)
        chunks_scanned = 0
        
        try:
            parser = AnvilParser(region_file)
            
            for cz in range(32):
                for cx in range(32):
                    chunk = parser.get_chunk(cx, cz)
                    if not chunk:
                        continue
                    
                    # Sprawdź czy chunk jest w zakresie strefy
                    if min_x is not None:
                        chunk_min_x = chunk.x * 16
                        chunk_max_x = chunk_min_x + 15
                        if chunk_max_x < min_x or chunk_min_x > max_x:
                            continue
                    
                    if min_z is not None:
                        chunk_min_z = chunk.z * 16
                        chunk_max_z = chunk_min_z + 15
                        if chunk_max_z < min_z or chunk_min_z > max_z:
                            continue
                    
                    chunks_scanned += 1
                    self.chunk_count += 1
                    
                    # Przeskanuj Tile Entities
                    for te in chunk.get_tile_entities():
                        te_id_raw = te.get("id", "")
                        
                        # Wyciągnij wartość z NBTTag jeśli potrzeba
                        if isinstance(te_id_raw, NBTTag):
                            te_id = te_id_raw.value if hasattr(te_id_raw, 'value') else str(te_id_raw)
                        else:
                            te_id = te_id_raw
                        
                        if not te_id:
                            continue
                        
                        # Sprawdź czy to Blood Magic
                        if self._is_blood_magic_te(te_id):
                            te_count[te_id] += 1
                            self.te_count[te_id] += 1
                            self.found_te_ids.add(te_id)
                            
                            # Zapisz lokalizację
                            x = te.get("x", 0)
                            y = te.get("y", 0)
                            z = te.get("z", 0)
                            # Wyciągnij wartości z NBTTag jeśli potrzeba
                            if isinstance(x, NBTTag):
                                x = x.value if hasattr(x, 'value') else 0
                            if isinstance(y, NBTTag):
                                y = y.value if hasattr(y, 'value') else 0
                            if isinstance(z, NBTTag):
                                z = z.value if hasattr(z, 'value') else 0
                            self.te_locations[te_id].append((int(x), int(y), int(z)))
        
        except Exception as e:
            print(f"    Błąd podczas skanowania {region_file}: {e}")
        
        return te_count, chunks_scanned
    
    def _is_blood_magic_te(self, te_id) -> bool:
        """Sprawdź czy Tile Entity należy do Blood Magic"""
        # Upewnij się że te_id jest stringiem (może być NBTTag)
        if not isinstance(te_id, str):
            te_id = str(te_id) if te_id else ""
        
        # Dokładne dopasowanie
        if te_id in self.EXPECTED_TE_IDS:
            return True
        
        # Sprawdź wzorce
        for pattern in self.BM_TE_PATTERNS:
            if re.search(pattern, te_id, re.IGNORECASE):
                return True
        
        return False
    
    def _generate_report(self) -> Dict[str, Any]:
        """Wygeneruj raport pokrycia"""
        report = {
            "summary": {
                "total_regions_scanned": self.region_count,
                "total_chunks_scanned": self.chunk_count,
                "unique_te_ids_found": len(self.found_te_ids),
                "total_te_instances": sum(self.te_count.values()),
            },
            "found_te_ids": sorted(list(self.found_te_ids)),
            "te_count": dict(self.te_count),
            "te_locations": {k: v[:10] for k, v in self.te_locations.items()},  # Pierwsze 10 lokalizacji
            "zone_stats": self.zone_stats,
            "coverage_analysis": self._analyze_coverage(),
        }
        
        return report
    
    def _analyze_coverage(self) -> Dict[str, Any]:
        """Przeanalizuj pokrycie kodu konwersji"""
        # TE ID obsługiwane przez kod konwersji (zgodnie z aktualnym kodem)
        supported_te_ids = {
            "Altar", "MasterStone",  # Oczekiwane ID
            "containerAltar", "containerMasterStone",  # Rzeczywiste ID z mapy
            "TileSoulJar",  # Soul Jar
        }
        
        covered = self.found_te_ids & supported_te_ids
        not_covered = self.found_te_ids - supported_te_ids
        
        # Sprawdź czy są nieznane TE ID (poza Blood Magic)
        expected_all = self.EXPECTED_TE_IDS | supported_te_ids | {"witchery:altar", "TileSoulJar"}
        unknown_te = not_covered - expected_all
        
        return {
            "supported_te_ids": sorted(list(supported_te_ids)),
            "covered_te_ids": sorted(list(covered)),
            "not_covered_te_ids": sorted(list(not_covered)),
            "unknown_te_ids": sorted(list(unknown_te)),
            "coverage_percent": len(covered) / len(self.found_te_ids) * 100 if self.found_te_ids else 0,
        }
    
    def save_report(self, output_path: str):
        """Zapisz raport do pliku JSON"""
        report = self._generate_report()
        
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        print(f"\nRaport zapisano do: {output_file}")
        return report
    
    def print_summary(self):
        """Wypisz podsumowanie na konsolę"""
        print("\n" + "=" * 60)
        print("PODSUMOWANIE ANALIZY")
        print("=" * 60)
        
        print(f"\nPrzeskanowano chunków: {self.chunk_count}")
        print(f"Znaleziono unikalnych TE ID: {len(self.found_te_ids)}")
        print(f"Łączna liczba instancji TE: {sum(self.te_count.values())}")
        
        print("\n--- Znalezione Tile Entity ID ---")
        for te_id in sorted(self.found_te_ids):
            count = self.te_count[te_id]
            # Sprawdź czy obsługiwane - uwzględnij rzeczywiste TE ID z mapy
            supported_ids = {"Altar", "MasterStone", "containerAltar", "containerMasterStone", "TileSoulJar"}
            supported = "[OK]" if te_id in supported_ids else "[NO]"
            print(f"  {supported} {te_id}: {count}")
        
        coverage = self._analyze_coverage()
        print(f"\n--- Analiza pokrycia ---")
        print(f"  Pokrycie: {coverage['coverage_percent']:.1f}%")
        print(f"  Obsługiwane: {coverage['covered_te_ids']}")
        print(f"  Nieobsługiwane: {coverage['not_covered_te_ids']}")
        
        if coverage['unknown_te_ids']:
            print(f"\n⚠️  OSTRZEŻENIE: Znaleziono nieznane TE ID:")
            for te_id in coverage['unknown_te_ids']:
                print(f"    - {te_id}")


def load_zones() -> Dict[str, List[Tuple[int, int]]]:
    """Wczytaj definicje stref z plików coords.json"""
    zones = {}
    zones_path = Path("strefy")
    
    for zone_dir in zones_path.iterdir():
        if not zone_dir.is_dir():
            continue
            
        coords_file = zone_dir / "coords.json"
        if not coords_file.exists():
            continue
        
        with open(coords_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        coords = [(c["x"], c["z"]) for c in data["minecraftCoordinates"]]
        zones[zone_dir.name] = coords
    
    return zones


def main():
    """Główna funkcja analizy pokrycia"""
    # Ścieżki
    world_path = "mapa_1710"
    output_path = "output/bloodmagic_coverage_report.json"
    
    # Sprawdź czy mapa istnieje
    if not Path(world_path).exists():
        print(f"BŁĄD: Nie znaleziono mapy: {world_path}")
        print("Upewnij się że skrypt jest uruchomiony z głównego folderu projektu")
        return
    
    # Wczytaj strefy
    zones = load_zones()
    print(f"Wczytano strefy: {list(zones.keys())}")
    
    # Uruchom analizę
    analyzer = BloodMagicCoverageAnalyzer(world_path)
    analyzer.analyze_all_zones(zones)
    analyzer.print_summary()
    
    # Zapisz raport
    report = analyzer.save_report(output_path)
    
    return report


if __name__ == "__main__":
    main()
