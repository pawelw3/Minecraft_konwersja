"""
Enchanting Plus Batch Converter

Konwersja wsadowa bloków EP z postępem i statystykami.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional, Callable, Tuple
from pathlib import Path
import json
import time
from datetime import datetime

from .enchantingplus_converter import EnchantingPlusConverter, EPBlockConversion
from .ep_chunk_parser import EPChunkParser, ChunkAnalysisResult


@dataclass
class BatchConversionStats:
    """Statystyki konwersji wsadowej."""
    total_blocks: int = 0
    converted_blocks: int = 0
    removed_blocks: int = 0  # Bloki usunięte (np. Arcane Inscriber)
    failed_blocks: int = 0
    success_rate: float = 0.0
    duration_seconds: float = 0.0
    start_time: Optional[float] = None
    end_time: Optional[float] = None
    blocks_by_type: Dict[str, int] = field(default_factory=dict)
    errors: List[str] = field(default_factory=list)
    
    def start(self):
        """Rozpoczyna pomiar czasu."""
        self.start_time = time.time()
    
    def finish(self):
        """Kończy pomiar czasu i oblicza statystyki."""
        self.end_time = time.time()
        if self.start_time:
            self.duration_seconds = self.end_time - self.start_time
        
        if self.total_blocks > 0:
            self.success_rate = ((self.converted_blocks + self.removed_blocks) / self.total_blocks) * 100
    
    def add_block(self, block_type: str, success: bool, removed: bool = False, error: Optional[str] = None):
        """Dodaje blok do statystyk."""
        self.total_blocks += 1
        self.blocks_by_type[block_type] = self.blocks_by_type.get(block_type, 0) + 1
        
        if success:
            if removed:
                self.removed_blocks += 1
            else:
                self.converted_blocks += 1
        else:
            self.failed_blocks += 1
            if error:
                self.errors.append(error)
    
    def to_dict(self) -> Dict[str, Any]:
        """Eksportuje do słownika."""
        return {
            'total_blocks': self.total_blocks,
            'converted_blocks': self.converted_blocks,
            'removed_blocks': self.removed_blocks,
            'failed_blocks': self.failed_blocks,
            'success_rate_percent': round(self.success_rate, 2),
            'duration_seconds': round(self.duration_seconds, 2),
            'blocks_by_type': self.blocks_by_type,
            'error_count': len(self.errors)
        }


@dataclass
class BatchConversionResult:
    """Wynik konwersji wsadowej."""
    stats: BatchConversionStats
    converted_blocks: List[EPBlockConversion]
    output_path: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Eksportuje do słownika."""
        return {
            'stats': self.stats.to_dict(),
            'converted_blocks': [b.to_dict() for b in self.converted_blocks],
            'output_path': self.output_path
        }
    
    def save_json(self, filepath: str):
        """Zapisuje wyniki do pliku JSON."""
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(self.to_dict(), f, indent=2, ensure_ascii=False)


class EPBatchConverter:
    """
    Konwerter wsadowy dla Enchanting Plus.
    
    Obsługuje:
    - Skanowanie chunków w poszukiwaniu bloków EP
    - Konwersję wsadową z callbackami postępu
    - Generowanie statystyk i raportów
    - Eksport wyników do JSON
    """
    
    def __init__(self, 
                 world_path_1710: str,
                 output_path: str = "output/ep_conversion"):
        """
        Inicjalizuje konwerter wsadowy.
        
        Args:
            world_path_1710: Ścieżka do świata 1.7.10
            output_path: Ścieżka do zapisu wyników
        """
        self.world_path = Path(world_path_1710)
        self.output_path = Path(output_path)
        self.output_path.mkdir(parents=True, exist_ok=True)
        
        self.converter = EnchantingPlusConverter()
        self.chunk_parser = EPChunkParser(str(world_path_1710))
        self.progress_callback: Optional[Callable[[float, str], None]] = None
    
    def set_progress_callback(self, callback: Callable[[float, str], None]):
        """Ustawia callback postępu (percent, message)."""
        self.progress_callback = callback
    
    def _report_progress(self, percent: float, message: str):
        """Wywołuje callback postępu jeśli ustawiony."""
        if self.progress_callback:
            self.progress_callback(percent, message)
    
    def convert_single_chunk(self, 
                            chunk_x: int, 
                            chunk_z: int) -> List[EPBlockConversion]:
        """
        Konwertuje bloki EP w pojedynczym chunku.
        
        Args:
            chunk_x: Współrzędna X chunka
            chunk_z: Współrzędna Z chunka
            
        Returns:
            Lista wyników konwersji
        """
        analysis = self.chunk_parser.analyze_chunk(chunk_x, chunk_z)
        results = []
        
        if not analysis.has_ep_blocks:
            return results
        
        for ep_block in analysis.ep_blocks:
            result = self.converter.convert_block(
                block_id_1710=ep_block.block_id,
                position=ep_block.absolute_pos,
                nbt_1710=ep_block.tile_entity
            )
            results.append(result)
        
        return results
    
    def convert_region(self,
                      region_x: int,
                      region_z: int,
                      stats: Optional[BatchConversionStats] = None) -> List[EPBlockConversion]:
        """
        Konwertuje wszystkie bloki EP w regionie.
        
        Args:
            region_x: Współrzędna X regionu
            region_z: Współrzędna Z regionu
            stats: Opcjonalne statystyki do aktualizacji
            
        Returns:
            Lista wyników konwersji
        """
        analyses = self.chunk_parser.analyze_region(region_x, region_z)
        all_results = []
        
        for analysis in analyses:
            for ep_block in analysis.ep_blocks:
                result = self.converter.convert_block(
                    block_id_1710=ep_block.block_id,
                    position=ep_block.absolute_pos,
                    nbt_1710=ep_block.tile_entity
                )
                all_results.append(result)
                
                # Aktualizuj statystyki
                if stats:
                    is_removed = result.converted.block_id_1182 == "minecraft:air"
                    stats.add_block(
                        block_type=ep_block.block_id,
                        success=result.converted.success,
                        removed=is_removed,
                        error=result.converted.errors[0] if result.converted.errors else None
                    )
        
        return all_results
    
    def run_batch_conversion(self,
                            max_regions: Optional[int] = None,
                            specific_regions: Optional[List[Tuple[int, int]]] = None
                            ) -> BatchConversionResult:
        """
        Uruchamia pełną konwersję wsadową.
        
        Fazy:
        1. Analiza (30%) - skanowanie wszystkich chunków
        2. Konwersja (60%) - konwersja bloków EP
        3. Raportowanie (10%) - generowanie plików wyjściowych
        
        Args:
            max_regions: Maksymalna liczba regionów do przetworzenia
            specific_regions: Lista (rx, rz) konkretnych regionów do przetworzenia
            
        Returns:
            BatchConversionResult z wynikami
        """
        stats = BatchConversionStats()
        stats.start()
        
        self._report_progress(0, "Rozpoczynanie konwersji wsadowej...")
        
        # Faza 1: Analiza - znajdź wszystkie bloki EP
        self._report_progress(5, "Analiza mapy w poszukiwaniu bloków EP...")
        
        if specific_regions:
            region_list = specific_regions
        else:
            region_files = list(self.chunk_parser.region_path.glob('r.*.*.mca'))
            region_list = []
            for rf in region_files:
                parts = rf.stem.split('.')
                if len(parts) == 3:
                    try:
                        region_list.append((int(parts[1]), int(parts[2])))
                    except ValueError:
                        pass
        
        if max_regions and len(region_list) > max_regions:
            region_list = region_list[:max_regions]
        
        total_regions = len(region_list)
        self._report_progress(10, f"Znaleziono {total_regions} regionów do przetworzenia")
        
        # Faza 2: Konwersja
        all_converted = []
        
        for i, (rx, rz) in enumerate(region_list):
            progress_base = 10 + (i / total_regions) * 60
            self._report_progress(progress_base, f"Konwersja regionu r.{rx}.{rz}.mca...")
            
            results = self.convert_region(rx, rz, stats)
            all_converted.extend(results)
            
            progress_after = 10 + ((i + 1) / total_regions) * 60
            self._report_progress(progress_after, 
                f"Region r.{rx}.{rz}.mca: przekonwertowano {len(results)} bloków")
        
        # Faza 3: Raportowanie
        self._report_progress(75, "Generowanie raportów...")
        
        stats.finish()
        result = BatchConversionResult(
            stats=stats,
            converted_blocks=all_converted,
            output_path=str(self.output_path)
        )
        
        # Zapisz wyniki
        self._save_results(result)
        
        self._report_progress(100, "Konwersja zakończona!")
        
        return result
    
    def _save_results(self, result: BatchConversionResult):
        """Zapisuje wyniki konwersji do plików."""
        # Główny plik wynikowy
        result.save_json(self.output_path / 'converted_blocks.json')
        
        # Statystyki
        with open(self.output_path / 'conversion_stats.json', 'w', encoding='utf-8') as f:
            json.dump(result.stats.to_dict(), f, indent=2, ensure_ascii=False)
        
        # Lista błędów
        if result.stats.errors:
            with open(self.output_path / 'conversion_errors.json', 'w', encoding='utf-8') as f:
                json.dump(result.stats.errors, f, indent=2, ensure_ascii=False)
    
    def generate_summary_report(self) -> str:
        """Generuje podsumowanie tekstowe."""
        lines = [
            "=" * 60,
            "ENCHANTING PLUS - BATCH CONVERSION REPORT",
            "=" * 60,
            f"Timestamp: {datetime.now().isoformat()}",
            f"Source world: {self.world_path}",
            f"Output path: {self.output_path}",
            "",
            "SUPPORTED BLOCKS:",
            "  - EnchantingPlus:enchanting_table -> enchantinginfuser:enchanting_infuser",
            "  - EnchantingPlus:advanced_table -> enchantinginfuser:advanced_enchanting_infuser",
            "  - EnchantingPlus:arcane_inscriber -> REMOVED (no equivalent)",
            "",
            "To run conversion:",
            "  converter = EPBatchConverter('mapa_1710', 'output/ep_conversion')",
            "  result = converter.run_batch_conversion()",
            "",
            "=" * 60,
        ]
        return "\n".join(lines)


def main():
    """Demo batch convertera."""
    print("=" * 60)
    print("ENCHANTING PLUS BATCH CONVERTER - Demo")
    print("=" * 60)
    
    # Utwórz konwerter
    converter = EPBatchConverter(
        world_path_1710="mapa_1710",
        output_path="output/ep_conversion"
    )
    
    # Wyświetl podsumowanie
    print(converter.generate_summary_report())
    
    # Demo z callbackiem
    print("\n" + "=" * 60)
    print("Demo konwersji (max 5 regionów)...")
    print("=" * 60)
    
    def progress(percent, message):
        print(f"[{percent:5.1f}%] {message}")
    
    converter.set_progress_callback(progress)
    
    result = converter.run_batch_conversion(max_regions=5)
    
    print("\n" + "=" * 60)
    print("Wyniki konwersji:")
    print("=" * 60)
    print(f"Całkowita liczba bloków: {result.stats.total_blocks}")
    print(f"Przekonwertowane: {result.stats.converted_blocks}")
    print(f"Usunięte: {result.stats.removed_blocks}")
    print(f"Nieudane: {result.stats.failed_blocks}")
    print(f"Skuteczność: {result.stats.success_rate:.1f}%")
    print(f"Czas wykonania: {result.stats.duration_seconds:.2f}s")
    
    if result.stats.blocks_by_type:
        print("\nBloki według typu:")
        for block_type, count in result.stats.blocks_by_type.items():
            print(f"  {block_type}: {count}")
    
    print(f"\nWyniki zapisano w: {result.output_path}")
    print("=" * 60)


if __name__ == "__main__":
    main()
