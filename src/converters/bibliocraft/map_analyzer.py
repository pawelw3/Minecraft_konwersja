"""
Analiza użycia bloków BiblioCraft na mapie 1.7.10

Ten moduł analizuje rzeczywistą mapę Minecraft i generuje raport:
1. Które bloki BC są używane i w jakich ilościach
2. Gdzie znajdują się te bloki (koordynaty)
3. Jakie dane Tile Entity zawierają
4. Rekomendacje priorytetów konwersji
"""

import os
import json
from typing import Dict, List, Optional, Set, Tuple
from dataclasses import dataclass, field, asdict
from pathlib import Path
from collections import defaultdict
import struct


@dataclass
class BCBlockInstance:
    """Pojedyncza instancja bloku BC na mapie"""
    x: int
    y: int
    z: int
    block_id: str
    block_name: str
    metadata: int = 0
    has_tile_entity: bool = False
    te_data: Optional[Dict] = None
    chunk_x: int = 0
    chunk_z: int = 0
    region_x: int = 0
    region_z: int = 0
    
    @property
    def position_str(self) -> str:
        return f"({self.x}, {self.y}, {self.z})"
    
    @property
    def region_file(self) -> str:
        return f"r.{self.region_x}.{self.region_z}.mca"


@dataclass
class BCBlockStatistics:
    """Statystyki dla typu bloku BC"""
    block_id: str
    block_name: str
    count: int = 0
    with_inventory: int = 0
    with_custom_texture: int = 0
    positions: List[Tuple[int, int, int]] = field(default_factory=list)
    
    def add_instance(self, instance: BCBlockInstance):
        """Dodaje instancję do statystyk"""
        self.count += 1
        self.positions.append((instance.x, instance.y, instance.z))
        
        if instance.te_data:
            # Sprawdź czy ma inventory
            if any(key in instance.te_data for key in ["Items", "shelfItems", "armorItems"]):
                self.with_inventory += 1
            
            # Sprawdź czy ma customową teksturę
            if instance.te_data.get("frameTexture") or instance.te_data.get("resourceLocation"):
                self.with_custom_texture += 1


class BCMapAnalyzer:
    """
    Analizator mapy BC
    
    Skanuje pliki regionów (.mca) w poszukiwaniu bloków BiblioCraft.
    """
    
    # ID bloków BC (prefix BiblioCraft:)
    BC_BLOCK_PREFIXES = [
        "BiblioCraft",
    ]
    
    # Znane bloki BC do identyfikacji
    KNOWN_BC_BLOCKS = {
        "BiblioCraft:Bookcase": "Bookcase",
        "BiblioCraft:ArmorStand": "Armor Stand",
        "BiblioCraft:WeaponCase": "Display Case",
        "BiblioCraft:PotionShelf": "Potion Shelf",
        "BiblioCraft:WeaponRack": "Tool Rack",
        "BiblioCraft:GenericShelf": "Shelf",
        "BiblioCraft:Label": "Wood Label",
        "BiblioCraft:WritingDesk": "Desk",
        "BiblioCraft:TypeMachine": "Typesetting Table",
        "BiblioCraft:PrintPress": "Printing Press",
        "BiblioCraft:Table": "Table",
        "BiblioCraft:Seat": "Seat",
        "BiblioCraft:Lantern": "Fancy Lantern",
        "BiblioCraft:Lamp": "Fancy Lamp",
        "BiblioCraft:CookieJar": "Cookie Jar",
        "BiblioCraft:DinnerPlate": "Dinner Plate",
        "BiblioCraft:DiscRack": "Disc Rack",
        "BiblioCraft:MapFrame": "Map Frame",
        "BiblioCraft:FancySign": "Fancy Sign",
        "BiblioCraft:FancyWorkbench": "Fancy Workbench",
        "BiblioCraft:SwordPedestal": "Sword Pedestal",
        "BiblioCraft:FramedChest": "Framed Chest",
        "BiblioCraft:FurniturePaneler": "Furniture Paneler",
        "BiblioCraft:Clock": "Clock",
        "BiblioCraft:Painting": "Painting",
        "BiblioCraft:PaintPress": "Paint Press",
        "BiblioCraft:Bell": "Bell",
        "BiblioCraft:Clipboard": "Clipboard",
        # Framed variants
        "BiblioCraft:FramedBookcase": "Framed Bookcase",
        "BiblioCraft:FramedShelf": "Framed Shelf",
        "BiblioCraft:FramedLabel": "Framed Label",
        "BiblioCraft:FramedTable": "Framed Table",
        "BiblioCraft:FramedDesk": "Framed Desk",
        "BiblioCraft:FramedSeat": "Framed Seat",
        "BiblioCraft:FramedSign": "Framed Sign",
        "BiblioCraft:FramedDoor": "Framed Door",
        "BiblioCraft:FramedTrapDoor": "Framed TrapDoor",
        "BiblioCraft:FramedFence": "Framed Fence",
        "BiblioCraft:FramedGate": "Framed Gate",
    }
    
    def __init__(self, world_path: str):
        self.world_path = Path(world_path)
        self.region_path = self.world_path / "region"
        self.instances: List[BCBlockInstance] = []
        self.statistics: Dict[str, BCBlockStatistics] = {}
        self.errors: List[str] = []
        
    def analyze(self) -> Dict:
        """
        Przeprowadza pełną analizę mapy
        
        Returns:
            Słownik ze statystykami
        """
        print(f"Analiza mapy: {self.world_path}")
        
        if not self.region_path.exists():
            self.errors.append(f"Nie znaleziono folderu region: {self.region_path}")
            return {"error": "Region folder not found"}
        
        # Znajdź wszystkie pliki .mca
        region_files = list(self.region_path.glob("*.mca"))
        print(f"Znaleziono {len(region_files)} plików regionów")
        
        # Analizuj każdy region
        for i, region_file in enumerate(region_files):
            if i % 10 == 0:
                print(f"  Przetwarzanie {i+1}/{len(region_files)}: {region_file.name}")
            self._analyze_region(region_file)
        
        # Generuj statystyki
        self._generate_statistics()
        
        return self.get_summary()
    
    def _analyze_region(self, region_file: Path):
        """Analizuje pojedynczy plik regionu"""
        try:
            # Parsuj nazwę pliku (r.X.Z.mca)
            parts = region_file.stem.split(".")
            if len(parts) != 3 or parts[0] != "r":
                return
            
            region_x = int(parts[1])
            region_z = int(parts[2])
            
            # W prawdziwej implementacji - odczytaj NBT z chunków
            # Na razie - placeholder dla struktury
            # TODO: Integracja z minecraft_map_parser
            
        except Exception as e:
            self.errors.append(f"Błąd analizy {region_file}: {e}")
    
    def _generate_statistics(self):
        """Generuje statystyki z zebranych instancji"""
        self.statistics = {}
        
        for instance in self.instances:
            block_id = instance.block_id
            
            if block_id not in self.statistics:
                block_name = self.KNOWN_BC_BLOCKS.get(block_id, "Unknown")
                self.statistics[block_id] = BCBlockStatistics(
                    block_id=block_id,
                    block_name=block_name
                )
            
            self.statistics[block_id].add_instance(instance)
    
    def add_instance_from_parser(self, x: int, y: int, z: int,
                                  block_id: str, metadata: int,
                                  te_data: Optional[Dict] = None):
        """
        Dodaje instancję znalezioną przez parser mapy
        
        Używane przy integracji z minecraft_map_parser.
        """
        # Oblicz chunk i region
        chunk_x = x >> 4
        chunk_z = z >> 4
        region_x = chunk_x >> 5
        region_z = chunk_z >> 5
        
        # Sprawdź czy to blok BC
        if not any(block_id.startswith(prefix) for prefix in self.BC_BLOCK_PREFIXES):
            return
        
        instance = BCBlockInstance(
            x=x, y=y, z=z,
            block_id=block_id,
            block_name=self.KNOWN_BC_BLOCKS.get(block_id, "Unknown"),
            metadata=metadata,
            has_tile_entity=te_data is not None,
            te_data=te_data,
            chunk_x=chunk_x,
            chunk_z=chunk_z,
            region_x=region_x,
            region_z=region_z
        )
        
        self.instances.append(instance)
    
    def get_summary(self) -> Dict:
        """Zwraca podsumowanie analizy"""
        return {
            "total_bc_blocks": len(self.instances),
            "unique_block_types": len(self.statistics),
            "block_types": {
                block_id: {
                    "name": stats.block_name,
                    "count": stats.count,
                    "with_inventory": stats.with_inventory,
                    "with_custom_texture": stats.with_custom_texture
                }
                for block_id, stats in self.statistics.items()
            },
            "errors": len(self.errors)
        }
    
    def get_priority_blocks(self) -> List[Tuple[str, int]]:
        """
        Zwraca listę bloków według priorytetu konwersji
        
        Priorytet na podstawie:
        1. Ilość (więcej = ważniejsze)
        2. Czy ma inventory (tak = ważniejsze)
        3. Czy ma customową teksturę (tak = ważniejsze)
        """
        priorities = []
        
        for block_id, stats in self.statistics.items():
            # Score: count * (1 + inventory_bonus + texture_bonus)
            inventory_bonus = 2 if stats.with_inventory > 0 else 0
            texture_bonus = 1 if stats.with_custom_texture > 0 else 0
            
            score = stats.count * (1 + inventory_bonus + texture_bonus)
            priorities.append((block_id, score))
        
        # Sortuj malejąco
        priorities.sort(key=lambda x: x[1], reverse=True)
        return priorities
    
    def export_report(self, output_path: str):
        """Eksportuje raport do pliku JSON"""
        report = {
            "summary": self.get_summary(),
            "priorities": [
                {
                    "block_id": block_id,
                    "score": score,
                    "name": self.statistics[block_id].block_name
                }
                for block_id, score in self.get_priority_blocks()
            ],
            "detailed_stats": {
                block_id: asdict(stats)
                for block_id, stats in self.statistics.items()
            },
            "sample_positions": [
                {
                    "block_id": inst.block_id,
                    "position": inst.position_str,
                    "region": inst.region_file
                }
                for inst in self.instances[:100]  # Pierwsze 100
            ],
            "errors": self.errors[:50]  # Pierwsze 50 błędów
        }
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        print(f"Raport zapisano do: {output_path}")


class BCConversionPlanner:
    """
    Planer konwersji - pomaga określić kolejność i priorytety
    """
    
    # Poziomy priorytetu
    PRIORITY_CRITICAL = "CRITICAL"  # Inventory, duża ilość
    PRIORITY_HIGH = "HIGH"          # Custom textures, średnia ilość
    PRIORITY_MEDIUM = "MEDIUM"      # Standardowe bloki
    PRIORITY_LOW = "LOW"            # Dekoracyjne, rzadkie
    
    # Mapowanie bloków na poziom trudności konwersji
    CONVERSION_DIFFICULTY = {
        "BiblioCraft:FramedChest": "HIGH",      # FramedBlocks + inventory
        "BiblioCraft:Painting": "HIGH",         # Immersive Paintings
        "BiblioCraft:ArmorStand": "MEDIUM",     # Vanilla armor stand
        "BiblioCraft:Bookcase": "MEDIUM",       # Supplementaries, straty inventory
        "BiblioCraft:FurniturePaneler": "LOW",  # Nie przenosimy funkcji
        "BiblioCraft:TypeMachine": "LOW",       # Nie przenosimy funkcji
        "BiblioCraft:PrintPress": "LOW",        # Nie przenosimy funkcji
    }
    
    def __init__(self, analyzer: BCMapAnalyzer):
        self.analyzer = analyzer
        self.plan: List[Dict] = []
    
    def generate_plan(self) -> List[Dict]:
        """Generuje plan konwersji z priorytetami"""
        self.plan = []
        
        priorities = self.analyzer.get_priority_blocks()
        
        for block_id, score in priorities:
            stats = self.analyzer.statistics.get(block_id)
            if not stats:
                continue
            
            # Określ priorytet
            if score > 100:
                priority = self.PRIORITY_CRITICAL
            elif score > 50:
                priority = self.PRIORITY_HIGH
            elif score > 10:
                priority = self.PRIORITY_MEDIUM
            else:
                priority = self.PRIORITY_LOW
            
            # Określ trudność
            difficulty = self.CONVERSION_DIFFICULTY.get(block_id, "MEDIUM")
            
            # Określ target mod
            target = self._determine_target(block_id)
            
            self.plan.append({
                "block_id": block_id,
                "block_name": stats.block_name,
                "count": stats.count,
                "priority": priority,
                "difficulty": difficulty,
                "target_mod": target,
                "with_inventory": stats.with_inventory,
                "with_custom_texture": stats.with_custom_texture,
                "score": score
            })
        
        return self.plan
    
    def _determine_target(self, block_id: str) -> str:
        """Określa docelowy mod dla bloku"""
        if "Framed" in block_id:
            return "FramedBlocks"
        elif "Painting" in block_id:
            return "Immersive Paintings"
        elif block_id in ["BiblioCraft:ArmorStand"]:
            return "Vanilla"
        elif block_id in ["BiblioCraft:TypeMachine", "BiblioCraft:PrintPress", 
                          "BiblioCraft:FurniturePaneler", "BiblioCraft:PaintPress"]:
            return "REMOVE/REPLACE"
        else:
            return "Supplementaries"
    
    def export_plan(self, output_path: str):
        """Eksportuje plan do JSON"""
        if not self.plan:
            self.generate_plan()
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(self.plan, f, indent=2, ensure_ascii=False)
        
        print(f"Plan konwersji zapisano do: {output_path}")


# ============================================================================
# FUNKCJE POMOCNICZE
# ============================================================================

def analyze_world_for_bibliocraft(world_path: str, 
                                   output_report: Optional[str] = None,
                                   output_plan: Optional[str] = None) -> Dict:
    """
    Funkcja pomocnicza do analizy mapy
    
    Args:
        world_path: Ścieżka do folderu mapy
        output_report: Opcjonalna ścieżka do raportu JSON
        output_plan: Opcjonalna ścieżka do planu konwersji
        
    Returns:
        Podsumowanie analizy
    """
    print("=" * 60)
    print("ANALIZA: BiblioCraft na mapie")
    print("=" * 60)
    
    analyzer = BCMapAnalyzer(world_path)
    summary = analyzer.analyze()
    
    # Generuj plan
    planner = BCConversionPlanner(analyzer)
    plan = planner.generate_plan()
    
    # Eksportuj raporty
    if output_report:
        analyzer.export_report(output_report)
    
    if output_plan:
        planner.export_plan(output_plan)
    
    # Wyświetl podsumowanie
    print("\n--- Podsumowanie ---")
    print(f"  Całkowita liczba bloków BC: {summary.get('total_bc_blocks', 0)}")
    print(f"  Unikalne typy bloków: {summary.get('unique_block_types', 0)}")
    
    print("\n--- Priorytety konwersji ---")
    for item in plan[:10]:
        print(f"  [{item['priority']}] {item['block_name']}: {item['count']} "
              f"(-> {item['target_mod']})")
    
    print("=" * 60)
    
    return summary


# ============================================================================
# TESTOWANIE
# ============================================================================

if __name__ == "__main__":
    print("=" * 60)
    print("TEST: Map Analyzer")
    print("=" * 60)
    
    # Symulacja analizy
    analyzer = BCMapAnalyzer("/fake/world/path")
    
    # Dodaj przykładowe instancje
    test_instances = [
        (100, 64, 200, "BiblioCraft:Bookcase", 0, {"Items": [], "bookCount": 5}),
        (101, 64, 200, "BiblioCraft:FramedChest", 2, {"frameTexture": "minecraft:planks:0"}),
        (102, 65, 200, "BiblioCraft:Painting", 0, {"resourceLocation": "custom/sunset.png"}),
        (103, 64, 200, "BiblioCraft:Bookcase", 1, {"Items": [], "bookCount": 3}),
        (104, 64, 200, "BiblioCraft:Shelf", 0, {"shelfItems": []}),
    ]
    
    for x, y, z, block_id, meta, te in test_instances:
        analyzer.add_instance_from_parser(x, y, z, block_id, meta, te)
    
    # Generuj statystyki
    analyzer._generate_statistics()
    
    # Wyświetl wyniki
    print("\n--- Statystyki ---")
    summary = analyzer.get_summary()
    print(f"  Bloki BC: {summary['total_bc_blocks']}")
    print(f"  Typy: {summary['unique_block_types']}")
    
    print("\n--- Szczegóły ---")
    for block_id, stats in analyzer.statistics.items():
        print(f"  {stats.block_name}: {stats.count}")
        if stats.with_inventory:
            print(f"    - z inventory: {stats.with_inventory}")
        if stats.with_custom_texture:
            print(f"    - z custom teksturą: {stats.with_custom_texture}")
    
    # Test planera
    print("\n--- Plan konwersji ---")
    planner = BCConversionPlanner(analyzer)
    plan = planner.generate_plan()
    
    for item in plan:
        print(f"  [{item['priority']}] {item['block_name']} -> {item['target_mod']}")
    
    print("\n" + "=" * 60)
    print("Test zakończony!")
    print("=" * 60)
