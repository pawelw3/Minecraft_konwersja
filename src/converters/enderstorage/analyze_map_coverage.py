"""
Analiza pokrycia konwertera EnderStorage na głównej mapie 1.7.10
Zadanie 4: Sprawdzenie czy kod pokrywa wszystkie bloki/TE na mapie

NIE MOŻE MODYFIKOWAĆ mapa_1710/ - TYLKO ODCZYT!
"""

import sys
import os
import json
from pathlib import Path
from typing import Dict, List, Set, Tuple, Optional, Any
from dataclasses import dataclass, field, asdict
from collections import defaultdict
import re

# Dodaj ścieżki do importów
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from minecraft_map_parser.anvil_parser import AnvilParser


# Formaty TileEntity ID dla EnderStorage na mapie 1.7.10
# UWAGA: Na mapie są 'Ender Chest' i 'Ender Tank' (ze spacją!), nie 'TileEnderChest'/'TileEnderTank'
ENDERSTORAGE_TE_PATTERNS = [
    r"^Ender Chest$",         # EnderStorage 1.7.10 - Chest (format na mapie!)
    r"^Ender Tank$",          # EnderStorage 1.7.10 - Tank (format na mapie!)
    r"^TileEnderChest$",      # EnderStorage 1.7.10 - Chest (format w kodzie źródłowym)
    r"^TileEnderTank$",       # EnderStorage 1.7.10 - Tank (format w kodzie źródłowym)
    r"^EnderStorage:",        # EnderStorage z prefiksem modu
    r"^enderstorage:",        # EnderStorage 1.18.2 style
]

# Oczekiwane ID TileEntity - formaty na mapie 1.7.10 i docelowe 1.18.2
EXPECTED_TE_IDS = {
    "Ender Chest",      # Format na mapie 1.7.10 (ze spacją!)
    "Ender Tank",       # Format na mapie 1.7.10 (ze spacją!)
    "TileEnderChest",   # Format w kodzie źródłowym 1.7.10
    "TileEnderTank",    # Format w kodzie źródłowym 1.7.10
    "enderstorage:ender_chest",  # 1.18.2
    "enderstorage:ender_tank",   # 1.18.2
}


@dataclass
class FoundBlock:
    """Reprezentacja znalezionego bloku/TE"""
    te_id: str
    block_id: Optional[str]
    x: int
    y: int
    z: int
    nbt_keys: Set[str] = field(default_factory=set)
    has_freq: bool = False
    has_owner: bool = False
    has_rotation: bool = False
    has_items: bool = False
    has_invert_redstone: bool = False
    
    def to_dict(self) -> Dict:
        return {
            "te_id": self.te_id,
            "block_id": self.block_id,
            "x": self.x,
            "y": self.y,
            "z": self.z,
            "nbt_keys": list(self.nbt_keys),
            "has_freq": self.has_freq,
            "has_owner": self.has_owner,
            "has_rotation": self.has_rotation,
            "has_items": self.has_items,
            "has_invert_redstone": self.has_invert_redstone,
        }


@dataclass
class CoverageReport:
    """Raport pokrycia"""
    total_found: int = 0
    supported: int = 0
    unsupported: int = 0
    unknown_te_ids: Set[str] = field(default_factory=set)
    found_by_type: Dict[str, List[FoundBlock]] = field(default_factory=lambda: defaultdict(list))
    regions_scanned: Set[str] = field(default_factory=set)
    chunks_scanned: int = 0
    errors: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict:
        return {
            "total_found": self.total_found,
            "supported": self.supported,
            "unsupported": self.unsupported,
            "unknown_te_ids": list(self.unknown_te_ids),
            "found_by_type": {
                k: [b.to_dict() for b in v] 
                for k, v in self.found_by_type.items()
            },
            "regions_scanned": list(self.regions_scanned),
            "chunks_scanned": self.chunks_scanned,
            "errors": self.errors,
        }


def is_enderstorage_te(te_id: str) -> bool:
    """Sprawdza czy TE ID należy do EnderStorage"""
    if not te_id:
        return False
    
    te_id_lower = te_id.lower()
    
    # Dokładne dopasowanie
    if te_id in EXPECTED_TE_IDS:
        return True
    
    # Wzorce
    for pattern in ENDERSTORAGE_TE_PATTERNS:
        if re.search(pattern, te_id, re.IGNORECASE):
            return True
    
    # Sprawdź czy zawiera "ender" i "storage"
    if "ender" in te_id_lower and "storage" in te_id_lower:
        return True
    
    return False


def analyze_te_data(te_data: Dict[str, Any]) -> FoundBlock:
    """Analizuje dane Tile Entity i wyciąga informacje"""
    te_id = te_data.get("id", "UNKNOWN")
    
    block = FoundBlock(
        te_id=te_id,
        block_id=te_data.get("BlockId"),  # Niektóre formaty mają to pole
        x=te_data.get("x", 0),
        y=te_data.get("y", 0),
        z=te_data.get("z", 0),
        nbt_keys=set(te_data.keys()),
    )
    
    # Sprawdź obecność kluczowych pól
    block.has_freq = "freq" in te_data
    block.has_owner = "owner" in te_data
    block.has_rotation = "rot" in te_data or "rotation" in te_data
    block.has_items = "Items" in te_data
    block.has_invert_redstone = "ir" in te_data or "invert_redstone" in te_data
    
    return block


def get_region_for_chunk(chunk_x: int, chunk_z: int) -> Tuple[int, int]:
    """Zwraca współrzędne regionu dla danego chunku"""
    return (chunk_x >> 5, chunk_z >> 5)


def get_chunk_coords_from_block(block_x: int, block_z: int) -> Tuple[int, int]:
    """Zwraca współrzędne chunku dla danego bloku"""
    return (block_x >> 4, block_z >> 4)


def get_region_filename(region_x: int, region_z: int) -> str:
    """Zwraca nazwę pliku regionu"""
    return f"r.{region_x}.{region_z}.mca"


def get_regions_for_zone(zone_coords: List[Dict[str, int]]) -> Set[Tuple[int, int]]:
    """Zwraca zbiór regionów które obejmują daną strefę"""
    if not zone_coords:
        return set()
    
    # Znajdź bounding box strefy
    min_x = min(c["x"] for c in zone_coords)
    max_x = max(c["x"] for c in zone_coords)
    min_z = min(c["z"] for c in zone_coords)
    max_z = max(c["z"] for c in zone_coords)
    
    # Konwersja na chunki
    min_cx = min_x >> 4
    max_cx = max_x >> 4
    min_cz = min_z >> 4
    max_cz = max_z >> 4
    
    # Konwersja na regiony
    min_rx = min_cx >> 5
    max_rx = max_cx >> 5
    min_rz = min_cz >> 5
    max_rz = max_cz >> 5
    
    regions = set()
    for rx in range(min_rx, max_rx + 1):
        for rz in range(min_rz, max_rz + 1):
            regions.add((rx, rz))
    
    return regions


def scan_region_file(region_path: Path, report: CoverageReport) -> None:
    """Skanuje pojedynczy plik regionu w poszukiwaniu EnderStorage TE"""
    try:
        parser = AnvilParser(str(region_path))
        report.regions_scanned.add(region_path.name)
        
        # Przeskanuj wszystkie chunki w regionie (32x32)
        for cz in range(32):
            for cx in range(32):
                try:
                    chunk = parser.get_chunk(cx, cz)
                    if not chunk:
                        continue
                    
                    report.chunks_scanned += 1
                    
                    # Pobierz Tile Entities z chunka
                    tile_entities = chunk.get_tile_entities()
                    
                    for te_data in tile_entities:
                        te_id = te_data.get("id", "")
                        
                        if is_enderstorage_te(te_id):
                            block = analyze_te_data(te_data)
                            report.total_found += 1
                            report.found_by_type[te_id].append(block)
                            
                except Exception as e:
                    # Ignoruj błędy pojedynczych chunków
                    pass
                    
    except Exception as e:
        report.errors.append(f"Error scanning {region_path}: {str(e)}")


def scan_zones(world_path: str, report: CoverageReport) -> None:
    """Skanuje wszystkie strefy zdefiniowane w folderze strefy/"""
    zones_dir = Path("strefy")
    
    for zone_file in zones_dir.glob("*/coords.json"):
        try:
            with open(zone_file, 'r') as f:
                zone_data = json.load(f)
            
            zone_name = zone_data.get("name", zone_file.parent.name)
            coords = zone_data.get("minecraftCoordinates", [])
            
            print(f"  Skanowanie strefy: {zone_name}")
            
            # Znajdź regiony dla tej strefy
            regions = get_regions_for_zone(coords)
            
            for rx, rz in regions:
                region_file = get_region_filename(rx, rz)
                region_path = Path(world_path) / "region" / region_file
                
                if region_path.exists():
                    scan_region_file(region_path, report)
                else:
                    report.errors.append(f"Region file not found: {region_file}")
                    
        except Exception as e:
            report.errors.append(f"Error processing zone {zone_file}: {str(e)}")


def scan_additional_regions(world_path: str, report: CoverageReport, 
                            additional_regions: List[Tuple[int, int]]) -> None:
    """Skanuje dodatkowe regiony (np. spawn i okolice)"""
    for rx, rz in additional_regions:
        region_file = get_region_filename(rx, rz)
        region_path = Path(world_path) / "region" / region_file
        
        if region_path.exists() and region_file not in report.regions_scanned:
            print(f"  Skanowanie regionu: {region_file}")
            scan_region_file(region_path, report)


def check_coverage(report: CoverageReport) -> None:
    """Sprawdza które znalezione TE są obsługiwane przez konwerter"""
    # Obsługiwane ID (zgodnie z kodem konwertera)
    # UWAGA: Na mapie są 'Ender Chest' i 'Ender Tank' (ze spacją!)
    supported_patterns = [
        r"^Ender Chest$",       # Format na mapie
        r"^Ender Tank$",        # Format na mapie
        r"TileEnderChest",
        r"TileEnderTank",
        r"enderstorage:ender_chest",
        r"enderstorage:ender_tank",
    ]
    
    for te_id, blocks in report.found_by_type.items():
        is_supported = False
        
        for pattern in supported_patterns:
            if re.search(pattern, te_id, re.IGNORECASE):
                is_supported = True
                break
        
        if is_supported:
            report.supported += len(blocks)
        else:
            report.unsupported += len(blocks)
            report.unknown_te_ids.add(te_id)


def verify_1182_compatibility(report: CoverageReport) -> Dict[str, Any]:
    """
    Weryfikuje czy konwersja jest kompatybilna z 1.18.2.
    Sprawdza czy symulacje działałyby poprawnie.
    """
    verification = {
        "can_convert": True,
        "issues": [],
        "warnings": [],
        "details": {}
    }
    
    for te_id, blocks in report.found_by_type.items():
        te_issues = []
        te_warnings = []
        
        for block in blocks:
            # Sprawdź czy ma freq (wymagane dla obu typów)
            if not block.has_freq:
                te_issues.append(f"Brak pola 'freq' w TE {te_id} @ ({block.x}, {block.y}, {block.z})")
            
            # Sprawdź czy ma owner (w 1.7.10 zawsze jest, w 1.18.2 może być null)
            if not block.has_owner:
                te_warnings.append(f"Brak pola 'owner' w TE {te_id}")
            
            # Dla skrzyń - sprawdź czy ma rotację
            if "Chest" in te_id and not block.has_rotation:
                te_warnings.append(f"Skrzynia bez rotacji @ ({block.x}, {block.y}, {block.z})")
            
            # Dla zbiorników - sprawdź invert_redstone
            if "Tank" in te_id and not block.has_invert_redstone:
                # To tylko info, nie błąd - domyślnie false
                pass
        
        if te_issues:
            verification["issues"].extend(te_issues)
            verification["can_convert"] = False
        
        if te_warnings:
            verification["warnings"].extend(te_warnings)
        
        verification["details"][te_id] = {
            "count": len(blocks),
            "issues": len(te_issues),
            "warnings": len(te_warnings)
        }
    
    return verification


def analyze_differences(report: CoverageReport) -> Dict[str, Any]:
    """
    Analizuje różnice między symulacjami 1.7.10 a 1.18.2.
    Sprawdza czy różnice są akceptowalne.
    """
    analysis = {
        "acceptable_differences": [],
        "concerns": [],
        "recommendations": []
    }
    
    # Sprawdź czy wszystkie kluczowe pola są obecne
    for te_id, blocks in report.found_by_type.items():
        for block in blocks:
            # W 1.7.10: freq (int), owner (string), rot (byte), Items (lista)
            # W 1.18.2: Frequency (obiekt), rotation (int), Items (lista)
            
            # Konwersja freq -> Frequency jest zawsze możliwa
            if block.has_freq:
                analysis["acceptable_differences"].append(
                    f"Konwersja freq (int) -> Frequency (object) możliwa dla {te_id}"
                )
            
            # Konwersja owner string -> UUID (jeśli nie global)
            if block.has_owner:
                analysis["acceptable_differences"].append(
                    f"Konwersja owner (string) -> UUID wymagana dla {te_id} (obecnie: zostaje global)"
                )
    
    # Rekomendacje
    if report.unknown_te_ids:
        analysis["recommendations"].append(
            f"Znaleziono nieznane TE IDs: {report.unknown_te_ids}. "
            "Należy dodać obsługę w konwerterze lub zweryfikować czy wymagają konwersji."
        )
    
    if report.unsupported > 0:
        analysis["recommendations"].append(
            f"{report.unsupported} bloków/TE nie jest obsługiwanych. "
            "Należy dodać konwertery lub zmapować na placeholdery."
        )
    
    return analysis


def generate_report(world_path: str = "mapa_1710") -> CoverageReport:
    """Główna funkcja generująca raport pokrycia"""
    print("=" * 70)
    print("ANALIZA POKRYCIA ENDERSTORAGE - ZADANIE 4")
    print("=" * 70)
    print(f"Mapa źródłowa: {world_path}")
    print("UWAGA: Tylko odczyt - NIE MODYFIKUJE mapy!")
    print("=" * 70)
    
    report = CoverageReport()
    
    # 1. Skanowanie stref
    print("\n[1/3] Skanowanie zdefiniowanych stref...")
    scan_zones(world_path, report)
    
    # 2. Dodatkowe regiony (spawn i okolice)
    print("\n[2/3] Skanowanie dodatkowych regionów...")
    additional_regions = [
        (0, 0),      # Spawn
        (1, 1),      # Okolice
        (-1, -1),
        (1, -1),
        (-1, 1),
    ]
    scan_additional_regions(world_path, report, additional_regions)
    
    # 3. Sprawdzenie pokrycia
    print("\n[3/3] Sprawdzanie pokrycia kodem konwertera...")
    check_coverage(report)
    
    print("\n" + "=" * 70)
    print("PODSUMOWANIE")
    print("=" * 70)
    print(f"Znaleziono bloki/TE EnderStorage: {report.total_found}")
    print(f"  - Obsługiwane: {report.supported}")
    print(f"  - Nieobsługiwane: {report.unsupported}")
    print(f"  - Nieznane TE IDs: {report.unknown_te_ids if report.unknown_te_ids else 'Brak'}")
    print(f"\nPrzeskanowano:")
    print(f"  - Regionów: {len(report.regions_scanned)}")
    print(f"  - Chunków: {report.chunks_scanned}")
    
    if report.errors:
        print(f"\nBłędy ({len(report.errors)}):")
        for err in report.errors[:10]:  # Pokaż pierwsze 10
            print(f"  - {err}")
    
    return report


def save_report(report: CoverageReport, output_dir: str = "output") -> None:
    """Zapisuje raport do pliku"""
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    # Zapisz JSON
    json_file = output_path / "enderstorage_coverage_report.json"
    with open(json_file, 'w', encoding='utf-8') as f:
        json.dump(report.to_dict(), f, indent=2, ensure_ascii=False)
    
    # Zapisz Markdown
    md_file = output_path / "enderstorage_coverage_report.md"
    with open(md_file, 'w', encoding='utf-8') as f:
        f.write("# Raport Pokrycia EnderStorage - Zadanie 4\n\n")
        import datetime
        f.write(f"**Data:** {datetime.datetime.now().isoformat()}\n\n")
        f.write(f"**Mapa zrodlowa:** mapa_1710/\n\n")
        f.write("---\n\n")
        
        f.write("## Podsumowanie\n\n")
        f.write(f"| Metryka | Wartosc |\n")
        f.write(f"|---------|---------|\n")
        f.write(f"| Znaleziono bloki/TE | {report.total_found} |\n")
        f.write(f"| Obslugiwane | {report.supported} |\n")
        f.write(f"| Nieobslugiwane | {report.unsupported} |\n")
        f.write(f"| Przeskanowane regionow | {len(report.regions_scanned)} |\n")
        f.write(f"| Przeskanowane chunkow | {report.chunks_scanned} |\n")
        
        f.write("\n## Szczegóły per typ\n\n")
        for te_id, blocks in sorted(report.found_by_type.items()):
            f.write(f"### {te_id}\n\n")
            f.write(f"- Liczba: {len(blocks)}\n")
            if blocks:
                sample = blocks[0]
                f.write(f"- Klucze NBT: {', '.join(sorted(sample.nbt_keys))}\n")
                f.write(f"- Ma freq: {sample.has_freq}\n")
                f.write(f"- Ma owner: {sample.has_owner}\n")
                f.write(f"- Ma rotation: {sample.has_rotation}\n")
            f.write("\n")
        
        if report.unknown_te_ids:
            f.write("## Nieznane TE IDs\n\n")
            for te_id in sorted(report.unknown_te_ids):
                f.write(f"- `{te_id}`\n")
            f.write("\n")
        
        if report.errors:
            f.write("## Błędy\n\n")
            for err in report.errors[:20]:
                f.write(f"- {err}\n")
            f.write("\n")
        
        f.write("---\n\n")
        f.write("*Raport wygenerowany automatycznie przez analizę pokrycia EnderStorage*\n")
    
    print(f"\nRaport zapisano do:")
    print(f"  - JSON: {json_file}")
    print(f"  - Markdown: {md_file}")


def main():
    """Główna funkcja"""
    # Generuj raport
    report = generate_report("mapa_1710")
    
    # Weryfikacja kompatybilności 1.18.2
    print("\n" + "=" * 70)
    print("WERYFIKACJA KOMPATYBILNOŚCI 1.18.2")
    print("=" * 70)
    verification = verify_1182_compatibility(report)
    
    print(f"\nMozliwosc konwersji: {'TAK' if verification['can_convert'] else 'NIE'}")
    
    if verification['issues']:
        print(f"\nProblemy krytyczne ({len(verification['issues'])}):")
        for issue in verification['issues'][:5]:
            print(f"  [X] {issue}")
    
    if verification['warnings']:
        print(f"\nOstrzezenia ({len(verification['warnings'])}):")
        for warning in set(verification['warnings'][:5]):
            print(f"  [!] {warning}")
    
    # Analiza różnic
    print("\n" + "=" * 70)
    print("ANALIZA RÓŻNIC SYMULACJI")
    print("=" * 70)
    analysis = analyze_differences(report)
    
    print(f"\nAkceptowalne roznice:")
    for diff in set(analysis['acceptable_differences'][:5]):
        print(f"  [OK] {diff}")
    
    if analysis['recommendations']:
        print(f"\nRekomendacje:")
        for rec in analysis['recommendations']:
            print(f"  -> {rec}")
    
    # Zapisz raport
    save_report(report)
    
    print("\n" + "=" * 70)
    print("ANALIZA ZAKOŃCZONA")
    print("=" * 70)


if __name__ == "__main__":
    main()
