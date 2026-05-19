"""
Integracja BiblioCraft z minecraft_map_parser - wykrywanie bloków BC w chunkach

Ten moduł odpowiada za:
1. Parsowanie chunków z mapy 1.7.10 w poszukiwaniu bloków BC
2. Ekstrakcję danych TileEntity z bloków BC
3. Przygotowanie danych do konwersji
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, field
from pathlib import Path
import json

from minecraft_map_parser.anvil_parser import AnvilParser, ChunkData
from minecraft_map_parser.nbt_parser import NBTTag


@dataclass
class BCBlockInChunk:
    """Blok BC znaleziony w chunku"""
    x: int
    y: int
    z: int
    block_id: str
    block_name: str
    metadata: int
    chunk_x: int
    chunk_z: int
    tile_entity: Optional[Dict] = None
    section_y: int = 0
    
    @property
    def absolute_pos(self) -> Tuple[int, int, int]:
        """Zwraca absolutną pozycję w świecie"""
        return (self.x, self.y, self.z)
    
    @property
    def region_pos(self) -> Tuple[int, int]:
        """Zwraca pozycję regionu"""
        return (self.chunk_x >> 5, self.chunk_z >> 5)


@dataclass
class ChunkAnalysisResult:
    """Wynik analizy chunka"""
    chunk_x: int
    chunk_z: int
    bc_blocks: List[BCBlockInChunk] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)
    
    @property
    def block_count(self) -> int:
        return len(self.bc_blocks)
    
    @property
    def has_bc_blocks(self) -> bool:
        return len(self.bc_blocks) > 0


class BiblioCraftChunkParser:
    """
    Parser wyspecjalizowany dla bloków BiblioCraft
    
    Integruje się z AnvilParser aby wykrywać i ekstrahować bloki BC.
    """
    
    # Rzeczywiste ID TileEntity BiblioCraft z plików MCA 1.7.10
    KNOWN_BC_TE_IDS = {
        "BookcaseTile", "GenericShelfTile", "PotionShelfTile", "ToolRackTile",
        "WeaponCaseTile", "SwordPedestalTile", "TableTile", "seatTile",
        "CookieJarTile", "dinnerPlateTile", "DiscRackTile", "MapFrameTile",
        "fancySignTile", "WritingDeskTile", "biblioBellTile", "biblioClipboardTile",
        "biblioTypewriterTile", "PrintPressTile", "biblioPaintingTile", "biblioPaintPressTile",
        "ArmorStandTile", "biblioClockTile", "LanternTile", "LampTile",
        "WoodLabelTile", "FramedChestTile",
    }

    # Mapowanie TE ID → czytelna nazwa bloku
    BC_BLOCK_NAMES = {
        "BookcaseTile":        "Bookcase",
        "ArmorStandTile":      "Armor Stand",
        "WeaponCaseTile":      "Display Case",
        "PotionShelfTile":     "Potion Shelf",
        "ToolRackTile":        "Tool Rack",
        "GenericShelfTile":    "Shelf",
        "WoodLabelTile":       "Wood Label",
        "WritingDeskTile":     "Writing Desk",
        "biblioTypewriterTile":"Typewriter",
        "PrintPressTile":      "Printing Press",
        "TableTile":           "Table",
        "seatTile":            "Seat",
        "LanternTile":         "Fancy Lantern",
        "LampTile":            "Fancy Lamp",
        "CookieJarTile":       "Cookie Jar",
        "dinnerPlateTile":     "Dinner Plate",
        "DiscRackTile":        "Disc Rack",
        "MapFrameTile":        "Map Frame",
        "fancySignTile":       "Fancy Sign",
        "SwordPedestalTile":   "Sword Pedestal",
        "FramedChestTile":     "Framed Chest",
        "biblioClockTile":     "Clock",
        "biblioPaintingTile":  "Painting",
        "biblioPaintPressTile":"Paint Press",
        "biblioBellTile":      "Bell",
        "biblioClipboardTile": "Clipboard",
    }
    
    def __init__(self, world_path: str):
        self.world_path = Path(world_path)
        self.region_path = self.world_path / "region"
        self.stats = {
            "chunks_analyzed": 0,
            "chunks_with_bc": 0,
            "bc_blocks_found": 0,
            "errors": 0
        }
        self._parser_cache = {}
    
    def _get_parser_for_chunk(self, chunk_x: int, chunk_z: int) -> Optional[AnvilParser]:
        """Pobiera lub tworzy parser dla danego chunka"""
        region_x = chunk_x >> 5
        region_z = chunk_z >> 5
        cache_key = (region_x, region_z)
        
        if cache_key not in self._parser_cache:
            region_file = self.region_path / f"r.{region_x}.{region_z}.mca"
            if not region_file.exists():
                return None
            try:
                self._parser_cache[cache_key] = AnvilParser(str(region_file))
            except Exception:
                return None
        
        return self._parser_cache[cache_key]
    
    def analyze_chunk(self, chunk_x: int, chunk_z: int) -> ChunkAnalysisResult:
        """
        Analizuje pojedynczy chunk w poszukiwaniu bloków BC
        
        Args:
            chunk_x: Współrzędna X chunka
            chunk_z: Współrzędna Z chunka
            
        Returns:
            ChunkAnalysisResult z wynikami analizy
        """
        result = ChunkAnalysisResult(chunk_x=chunk_x, chunk_z=chunk_z)
        
        try:
            # Pobierz parser dla tego chunka
            parser = self._get_parser_for_chunk(chunk_x, chunk_z)
            if not parser:
                return result
            
            # Pobierz dane chunka — AnvilParser używa lokalnych współrzędnych (0-31)
            local_x = chunk_x % 32
            local_z = chunk_z % 32
            chunk_data = parser.get_chunk(local_x, local_z)
            if not chunk_data:
                return result
            
            self.stats["chunks_analyzed"] += 1
            
            # Pobierz Tile Entities
            tile_entities = chunk_data.get_tile_entities()
            
            # Znajdź TE z BC
            for te in tile_entities:
                if self._is_bc_tile_entity(te):
                    bc_block = self._extract_bc_block(te, chunk_x, chunk_z)
                    if bc_block:
                        result.bc_blocks.append(bc_block)
                        self.stats["bc_blocks_found"] += 1
            
            if result.has_bc_blocks:
                self.stats["chunks_with_bc"] += 1
                
        except Exception as e:
            result.errors.append(f"Błąd parsowania chunka: {e}")
            self.stats["errors"] += 1
        
        return result
    
    def analyze_region(self, region_x: int, region_z: int) -> List[ChunkAnalysisResult]:
        """
        Analizuje wszystkie chunki w regionie
        
        Args:
            region_x: Współrzędna X regionu
            region_z: Współrzędna Z regionu
            
        Returns:
            Lista wyników dla chunków zawierających bloki BC
        """
        results = []
        
        # Region zawiera 32x32 chunków
        for cz in range(32):
            for cx in range(32):
                # Oblicz globalne współrzędne chunka
                chunk_x = region_x * 32 + cx
                chunk_z = region_z * 32 + cz
                
                result = self.analyze_chunk(chunk_x, chunk_z)
                if result.has_bc_blocks:
                    results.append(result)
        
        return results
    
    def scan_all_regions(self, progress_callback=None) -> List[ChunkAnalysisResult]:
        """
        Skanuje wszystkie regiony w folderze world/region
        
        Args:
            progress_callback: Funkcja callback(progress_percent, message)
            
        Returns:
            Lista wszystkich wyników z blokami BC
        """
        results = []
        
        if not self.region_path.exists():
            return results
        
        # Znajdź wszystkie pliki regionów
        region_files = list(self.region_path.glob("r.*.*.mca"))
        total_regions = len(region_files)
        
        for i, region_file in enumerate(region_files):
            # Parsuj nazwę pliku (r.X.Z.mca)
            parts = region_file.stem.split(".")
            if len(parts) != 3:
                continue
            
            try:
                region_x = int(parts[1])
                region_z = int(parts[2])
            except ValueError:
                continue
            
            # Callback postępu
            if progress_callback:
                progress = (i / total_regions) * 100
                progress_callback(progress, f"Analiza regionu {region_x},{region_z}")
            
            # Analizuj region
            region_results = self.analyze_region(region_x, region_z)
            results.extend(region_results)
        
        if progress_callback:
            progress_callback(100, "Analiza zakończona")
        
        return results
    
    def _is_bc_tile_entity(self, te_data: Dict) -> bool:
        """Sprawdza czy TileEntity należy do BiblioCraft"""
        te_id = self._get_te_id(te_data)
        return te_id in self.KNOWN_BC_TE_IDS
    
    def _get_te_id(self, te_data: Dict) -> str:
        """Wyciąga ID z danych TileEntity"""
        if isinstance(te_data, dict):
            return te_data.get("id", "")
        elif isinstance(te_data, NBTTag):
            id_tag = te_data.get("id")
            return id_tag.value if id_tag else ""
        return ""
    
    def _extract_bc_block(self, te_data: Dict, chunk_x: int, chunk_z: int) -> Optional[BCBlockInChunk]:
        """Ekstrahuje dane bloku BC z TileEntity"""
        try:
            # Konwertuj NBTTag na dict jeśli potrzeba
            if isinstance(te_data, NBTTag):
                te_data = self._nbt_to_dict(te_data)
            
            te_id = te_data.get("id", "")
            
            # Pobierz pozycję
            x = te_data.get("x", 0)
            y = te_data.get("y", 0)
            z = te_data.get("z", 0)
            
            # Oblicz section Y (sekcja 16 bloków w pionie)
            section_y = y // 16
            
            # Określ nazwę bloku
            block_name = self.BC_BLOCK_NAMES.get(te_id, "Unknown BC Block")
            
            # Metadata (może być w różnych miejscach)
            metadata = te_data.get("metadata", 0)
            
            return BCBlockInChunk(
                x=x,
                y=y,
                z=z,
                block_id=te_id,
                block_name=block_name,
                metadata=metadata,
                chunk_x=chunk_x,
                chunk_z=chunk_z,
                tile_entity=te_data,
                section_y=section_y
            )
            
        except Exception as e:
            return None
    
    def _nbt_to_dict(self, nbt_tag: NBTTag) -> Dict:
        """Konwertuje NBTTag na słownik Pythona"""
        if isinstance(nbt_tag.value, dict):
            result = {}
            for key, value in nbt_tag.value.items():
                if isinstance(value, NBTTag):
                    result[key] = self._nbt_to_dict(value)
                elif isinstance(value, list):
                    result[key] = [
                        self._nbt_to_dict(item) if isinstance(item, NBTTag) else item
                        for item in value
                    ]
                else:
                    result[key] = value
            return result
        return {"value": nbt_tag.value}
    
    def get_statistics(self) -> Dict:
        """Zwraca statystyki analizy"""
        return self.stats.copy()
    
    def get_blocks_by_type(self, results: List[ChunkAnalysisResult]) -> Dict[str, List[BCBlockInChunk]]:
        """Grupuje bloki według typu"""
        blocks_by_type = {}
        
        for result in results:
            for block in result.bc_blocks:
                block_type = block.block_id
                if block_type not in blocks_by_type:
                    blocks_by_type[block_type] = []
                blocks_by_type[block_type].append(block)
        
        return blocks_by_type


def find_bc_blocks_in_world(world_path: str, 
                            progress_callback=None) -> Tuple[List[ChunkAnalysisResult], Dict]:
    """
    Funkcja pomocnicza - znajduje wszystkie bloki BC na mapie
    
    Args:
        world_path: Ścieżka do folderu świata
        progress_callback: Opcjonalny callback postępu
        
    Returns:
        Tuple (lista wyników, statystyki)
    """
    parser = BiblioCraftChunkParser(world_path)
    results = parser.scan_all_regions(progress_callback)
    stats = parser.get_statistics()
    return results, stats


# Testowanie
if __name__ == "__main__":
    print("=" * 60)
    print("TEST: BiblioCraft Chunk Parser")
    print("=" * 60)
    
    # Test z mockowanymi danymi
    class MockNBTTag:
        def __init__(self, value):
            self.value = value
        
        def get(self, key, default=None):
            return self.value.get(key, default)
    
    # Test wykrywania BC TE
    parser = BiblioCraftChunkParser("/fake/path")
    
    test_te_cases = [
        {"id": "TileEntityBookcase", "x": 100, "y": 64, "z": 200},
        {"id": "TileEntityArmorStand", "x": 101, "y": 64, "z": 200},
        {"id": "minecraft:chest", "x": 102, "y": 64, "z": 200},  # Nie BC
        {"id": "BiblioCraft:Painting", "x": 103, "y": 65, "z": 200},
    ]
    
    print("\n--- Test wykrywania BC TE ---")
    for te in test_te_cases:
        is_bc = parser._is_bc_tile_entity(te)
        status = "BC" if is_bc else "Inny"
        print(f"  {te['id']}: {status}")
    
    # Test ekstrakcji
    print("\n--- Test ekstrakcji bloku ---")
    te_data = {
        "id": "TileEntityBookcase",
        "x": 100,
        "y": 64,
        "z": 200,
        "Items": [{"id": "minecraft:book", "Count": 5}],
        "bookCount": 5
    }
    
    block = parser._extract_bc_block(te_data, 6, 12)
    if block:
        print(f"  Znaleziono: {block.block_name}")
        print(f"  Pozycja: {block.absolute_pos}")
        print(f"  Region: {block.region_pos}")
        print(f"  Section Y: {block.section_y}")
    
    print("\n" + "=" * 60)
    print("Test zakończony!")
    print("=" * 60)
