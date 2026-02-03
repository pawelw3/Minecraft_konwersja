"""
Batch converter dla Better Storage - integracja z głównym pipeline konwersji mapy.

Umożliwia konwersję wszystkich bloków Better Storage na mapie w jednym przebiegu.
"""

import json
from pathlib import Path
from typing import Dict, List, Optional, Any, Iterator, Tuple
from dataclasses import dataclass, asdict
import time

from .nbt_converter import BetterStorageConverter
from .crate_pile_simulation import CratePileLoader


@dataclass
class ConversionResult:
    """Wynik konwersji pojedynczego bloku"""
    x: int
    y: int
    z: int
    original_block: str
    target_block: str
    nbt: Dict[str, Any]
    warnings: List[str]
    overflow: List[Dict]
    success: bool
    error: Optional[str] = None


@dataclass
class BatchStats:
    """Statystyki batch conversion"""
    total_blocks: int = 0
    converted: int = 0
    failed: int = 0
    warnings: int = 0
    overflow_items: int = 0
    elapsed_time: float = 0.0
    
    def to_dict(self) -> Dict:
        return asdict(self)


class BetterStorageBatchConverter:
    """
    Batch converter dla wszystkich bloków Better Storage na mapie.
    
    Usage:
        batch = BetterStorageBatchConverter('mapa_1710', 'mapa_118')
        stats = batch.convert_all()
        batch.save_report('output/betterstorage_conversion_report.json')
    """
    
    # ID bloków Better Storage które należy konwertować
    BS_BLOCK_IDS = {
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
    }
    
    def __init__(
        self, 
        source_world_path: str,
        target_world_path: Optional[str] = None,
        config: Optional[Dict] = None
    ):
        """
        Inicjalizuje batch converter.
        
        Args:
            source_world_path: Ścieżka do świata źródłowego (1.7.10)
            target_world_path: Ścieżka do świata docelowego (1.18.2) - opcjonalna
            config: Dodatkowa konfiguracja
        """
        self.source_world = Path(source_world_path)
        self.target_world = Path(target_world_path) if target_world_path else None
        self.config = config or {}
        
        # Inicjalizujemy konwerter
        self.converter = BetterStorageConverter(str(self.source_world))
        
        # Cache dla wyników
        self.results: List[ConversionResult] = []
        self.stats = BatchStats()
        
    def is_better_storage_block(self, block_id: str) -> bool:
        """Sprawdza czy blok należy do Better Storage"""
        return block_id in self.BS_BLOCK_IDS
    
    def convert_single(
        self, 
        block_id: str, 
        nbt_data: Dict[str, Any],
        x: int, 
        y: int, 
        z: int
    ) -> ConversionResult:
        """
        Konwertuje pojedynczy blok.
        
        Args:
            block_id: ID bloku (np. 'betterstorage:reinforcedChest')
            nbt_data: Dane NBT TileEntity
            x, y, z: Współrzędne bloku
            
        Returns:
            ConversionResult z wynikiem konwersji
        """
        try:
            result = self.converter.convert_tile_entity(
                block_id, nbt_data, x, y, z
            )
            
            return ConversionResult(
                x=x, y=y, z=z,
                original_block=block_id,
                target_block=result.get('block_id', 'minecraft:air'),
                nbt=result.get('nbt', {}),
                warnings=result.get('warnings', []),
                overflow=result.get('overflow', []),
                success=True
            )
            
        except Exception as e:
            return ConversionResult(
                x=x, y=y, z=z,
                original_block=block_id,
                target_block='minecraft:air',
                nbt={},
                warnings=[],
                overflow=[],
                success=False,
                error=str(e)
            )
    
    def convert_chunk(
        self, 
        chunk_data: Dict[str, Any],
        chunk_x: int, 
        chunk_z: int
    ) -> List[ConversionResult]:
        """
        Konwertuje wszystkie bloki BS z jednego chunka.
        
        Args:
            chunk_data: Dane chunka (w tym TileEntities)
            chunk_x, chunk_z: Współrzędne chunka
            
        Returns:
            Lista wyników konwersji
        """
        results = []
        
        # Pobieramy TileEntities z chunka
        tile_entities = chunk_data.get('Level', {}).get('TileEntities', [])
        
        for te in tile_entities:
            block_id = te.get('id', '')
            
            if not self.is_better_storage_block(block_id):
                continue
            
            # Współrzędne w świecie
            x = te.get('x', 0)
            y = te.get('y', 0)
            z = te.get('z', 0)
            
            # Konwertujemy
            result = self.convert_single(block_id, te, x, y, z)
            results.append(result)
        
        return results
    
    def convert_all_from_iterator(
        self,
        block_iterator: Iterator[Tuple[str, Dict, int, int, int]]
    ) -> BatchStats:
        """
        Konwertuje wszystkie bloki z iteratora.
        
        Args:
            block_iterator: Iterator zwracający (block_id, nbt, x, y, z)
            
        Returns:
            Statystyki konwersji
        """
        start_time = time.time()
        
        self.results = []
        self.stats = BatchStats()
        
        for block_id, nbt, x, y, z in block_iterator:
            if not self.is_better_storage_block(block_id):
                continue
            
            self.stats.total_blocks += 1
            
            result = self.convert_single(block_id, nbt, x, y, z)
            self.results.append(result)
            
            if result.success:
                self.stats.converted += 1
                self.stats.warnings += len(result.warnings)
                self.stats.overflow_items += len(result.overflow)
            else:
                self.stats.failed += 1
        
        self.stats.elapsed_time = time.time() - start_time
        return self.stats
    
    def get_overflow_summary(self) -> Dict[str, List[ConversionResult]]:
        """
        Zwraca podsumowanie overflow (itemy które się nie zmieściły).
        
        Returns:
            Słownik: original_block -> lista wyników z overflow
        """
        overflow_blocks = {}
        
        for result in self.results:
            if result.overflow:
                block_type = result.original_block
                if block_type not in overflow_blocks:
                    overflow_blocks[block_type] = []
                overflow_blocks[block_type].append(result)
        
        return overflow_blocks
    
    def get_warnings_summary(self) -> Dict[str, List[str]]:
        """
        Zwraca podsumowanie ostrzeżeń.
        
        Returns:
            Słownik z liczbą ostrzeżeń per typ
        """
        warning_counts = {}
        
        for result in self.results:
            for warning in result.warnings:
                # Grupujemy po typie ostrzeżenia
                key = warning.split(':')[0] if ':' in warning else 'other'
                warning_counts[key] = warning_counts.get(key, 0) + 1
        
        return warning_counts
    
    def save_report(self, output_path: str):
        """
        Zapisuje raport z konwersji.
        
        Args:
            output_path: Ścieżka do pliku wyjściowego (.json)
        """
        report = {
            'stats': self.stats.to_dict(),
            'overflow_summary': {
                block_type: len(results) 
                for block_type, results in self.get_overflow_summary().items()
            },
            'warnings_summary': self.get_warnings_summary(),
            'failed_conversions': [
                {
                    'x': r.x, 'y': r.y, 'z': r.z,
                    'block': r.original_block,
                    'error': r.error
                }
                for r in self.results if not r.success
            ],
            'conversion_count_by_type': self._count_by_block_type(),
        }
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        print(f"Raport zapisany do: {output_path}")
    
    def _count_by_block_type(self) -> Dict[str, int]:
        """Liczy konwersje per typ bloku"""
        counts = {}
        for result in self.results:
            block = result.original_block
            counts[block] = counts.get(block, 0) + 1
        return counts
    
    def print_summary(self):
        """Wypisuje podsumowanie konwersji"""
        print("\n" + "=" * 60)
        print("BETTER STORAGE - PODSUMOWANIE KONWERSJI")
        print("=" * 60)
        print(f"Całkowity czas: {self.stats.elapsed_time:.2f}s")
        print(f"Przetworzone bloki: {self.stats.total_blocks}")
        print(f"  - Przekonwertowane: {self.stats.converted}")
        print(f"  - Błędy: {self.stats.failed}")
        print(f"Ostrzeżenia: {self.stats.warnings}")
        print(f"Itemy overflow: {self.stats.overflow_items}")
        
        if self.stats.failed > 0:
            print(f"\n⚠️  {self.stats.failed} bloków nie zostało przekonwertowanych!")
        
        print("\nKonwersje per typ bloku:")
        for block_type, count in sorted(self._count_by_block_type().items()):
            print(f"  {block_type}: {count}")
        
        print("=" * 60)


# Helper do użycia z zewnętrznym parserem mapy
def create_block_iterator_from_regions(region_dir: str):
    """
    Tworzy iterator bloków z folderu regionów MCA.
    
    To jest placeholder - w prawdziwej implementacji
    użylibyśmy pełnego parsera MCA.
    
    Args:
        region_dir: Ścieżka do folderu region/
        
    Yields:
        (block_id, nbt, x, y, z)
    """
    # TODO: Implementacja z użyciem MCA parsera
    # Na razie zwracamy pusty iterator
    return iter([])


def quick_convert_block(
    block_id: str,
    nbt_data: Dict[str, Any],
    world_path: str,
    x: int = 0, 
    y: int = 0, 
    z: int = 0
) -> Dict[str, Any]:
    """
    Szybka konwersja pojedynczego bloku bez tworzenia BatchConverter.
    
    Usage:
        result = quick_convert_block('betterstorage:crate', nbt, 'mapa_1710', 100, 64, 200)
        print(result['block_id'])  # 'minecraft:chest'
    """
    converter = BetterStorageBatchConverter(world_path)
    result = converter.convert_single(block_id, nbt_data, x, y, z)
    return {
        'block_id': result.target_block,
        'nbt': result.nbt,
        'warnings': result.warnings,
        'overflow': result.overflow,
        'success': result.success,
        'error': result.error
    }
