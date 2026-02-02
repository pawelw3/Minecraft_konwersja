"""
Batch Converter dla BiblioCraft - konwersja wsadowa chunków

Ten moduł odpowiada za:
1. Konwersję wielu chunków w jednym przebiegu
2. Śledzenie postępu i statystyk
3. Zarządzanie błędami i edge cases
4. Generowanie raportów po konwersji
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from typing import Dict, List, Optional, Tuple, Callable, Any
from dataclasses import dataclass, field
from pathlib import Path
from datetime import datetime
import json
import traceback

from .bc_chunk_parser import BiblioCraftChunkParser, ChunkAnalysisResult, BCBlockInChunk
from .nbt_converter import BiblioCraftNBTConverter, ConvertedBlock
from .texture_mappings import convert_texture_id


@dataclass
class ConversionResult:
    """Wynik konwersji pojedynczego bloku"""
    original_block: BCBlockInChunk
    converted_block: Optional[ConvertedBlock]
    success: bool
    error_message: Optional[str] = None
    warnings: List[str] = field(default_factory=list)
    
    @property
    def position(self) -> Tuple[int, int, int]:
        return self.original_block.absolute_pos


@dataclass
class BatchConversionStats:
    """Statystyki konwersji wsadowej"""
    start_time: datetime
    end_time: Optional[datetime] = None
    total_chunks: int = 0
    chunks_with_bc: int = 0
    total_bc_blocks: int = 0
    converted_blocks: int = 0
    failed_blocks: int = 0
    skipped_blocks: int = 0
    warnings_count: int = 0
    
    @property
    def duration_seconds(self) -> float:
        if self.end_time:
            return (self.end_time - self.start_time).total_seconds()
        return 0.0
    
    @property
    def success_rate(self) -> float:
        if self.total_bc_blocks == 0:
            return 100.0
        return (self.converted_blocks / self.total_bc_blocks) * 100
    
    def to_dict(self) -> Dict:
        return {
            "start_time": self.start_time.isoformat(),
            "end_time": self.end_time.isoformat() if self.end_time else None,
            "duration_seconds": self.duration_seconds,
            "total_chunks": self.total_chunks,
            "chunks_with_bc": self.chunks_with_bc,
            "total_bc_blocks": self.total_bc_blocks,
            "converted_blocks": self.converted_blocks,
            "failed_blocks": self.failed_blocks,
            "skipped_blocks": self.skipped_blocks,
            "warnings_count": self.warnings_count,
            "success_rate_percent": round(self.success_rate, 2)
        }


class BiblioCraftBatchConverter:
    """
    Główna klasa do wsadowej konwersji bloków BiblioCraft
    
    Koordynuje proces:
    1. Analiza chunków (BiblioCraftChunkParser)
    2. Konwersja NBT (BiblioCraftNBTConverter)
    3. Raportowanie wyników
    """
    
    def __init__(self, world_path_1710: str, output_path: str):
        self.world_path = Path(world_path_1710)
        self.output_path = Path(output_path)
        self.output_path.mkdir(parents=True, exist_ok=True)
        
        self.parser = BiblioCraftChunkParser(str(self.world_path))
        self.nbt_converter = BiblioCraftNBTConverter()
        
        self.stats = BatchConversionStats(start_time=datetime.now())
        self.results: List[ConversionResult] = []
        self.errors: List[Dict] = []
        
        # Callbacki
        self.progress_callback: Optional[Callable[[float, str], None]] = None
        self.block_converted_callback: Optional[Callable[[ConversionResult], None]] = None
    
    def set_progress_callback(self, callback: Callable[[float, str], None]):
        """Ustawia callback do raportowania postępu"""
        self.progress_callback = callback
    
    def set_block_converted_callback(self, callback: Callable[[ConversionResult], None]):
        """Ustawia callback wywoływany po konwersji każdego bloku"""
        self.block_converted_callback = callback
    
    def convert_single_block(self, bc_block: BCBlockInChunk) -> ConversionResult:
        """
        Konwertuje pojedynczy blok BC
        
        Args:
            bc_block: Blok BC do konwersji
            
        Returns:
            ConversionResult z wynikiem
        """
        warnings = []
        
        try:
            # Sprawdź czy mamy dane TileEntity
            if not bc_block.tile_entity:
                return ConversionResult(
                    original_block=bc_block,
                    converted_block=None,
                    success=False,
                    error_message="Brak danych TileEntity",
                    warnings=warnings
                )
            
            # Konwersja NBT
            te_data = bc_block.tile_entity
            block_id = bc_block.block_id
            pos = bc_block.absolute_pos
            
            # Sprawdź czy tekstura jest znana (dla Framed blocks)
            if "Framed" in block_id:
                frame_texture = te_data.get("frameTexture", "")
                if frame_texture:
                    converted_texture = convert_texture_id(frame_texture, None)
                    if converted_texture is None:
                        warnings.append(f"Nieznana tekstura: {frame_texture}, użyto oak_planks")
            
            # Wykonaj konwersję
            converted = self.nbt_converter.convert_tile_entity(
                nbt_1710=te_data,
                block_id=block_id,
                pos=pos
            )
            
            if converted:
                # Dodaj notatki z konwersji do warnings
                if converted.conversion_notes:
                    warnings.extend(converted.conversion_notes)
                
                result = ConversionResult(
                    original_block=bc_block,
                    converted_block=converted,
                    success=True,
                    warnings=warnings
                )
                
                self.stats.converted_blocks += 1
            else:
                # Nieznany typ bloku - pominięty
                result = ConversionResult(
                    original_block=bc_block,
                    converted_block=None,
                    success=False,
                    error_message="Nieznany typ bloku lub brak konwertera",
                    warnings=warnings
                )
                self.stats.skipped_blocks += 1
            
            return result
            
        except Exception as e:
            error_msg = f"{type(e).__name__}: {str(e)}"
            self.stats.failed_blocks += 1
            
            return ConversionResult(
                original_block=bc_block,
                converted_block=None,
                success=False,
                error_message=error_msg,
                warnings=warnings
            )
    
    def convert_chunk(self, chunk_result: ChunkAnalysisResult) -> List[ConversionResult]:
        """
        Konwertuje wszystkie bloki BC w chunku
        
        Args:
            chunk_result: Wynik analizy chunka
            
        Returns:
            Lista wyników konwersji
        """
        chunk_results = []
        
        for bc_block in chunk_result.bc_blocks:
            conversion_result = self.convert_single_block(bc_block)
            chunk_results.append(conversion_result)
            self.results.append(conversion_result)
            
            # Callback
            if self.block_converted_callback:
                self.block_converted_callback(conversion_result)
            
            # Aktualizuj statystyki
            if conversion_result.warnings:
                self.stats.warnings_count += len(conversion_result.warnings)
        
        return chunk_results
    
    def run_batch_conversion(self, 
                            chunk_filter: Optional[Callable[[int, int], bool]] = None) -> BatchConversionStats:
        """
        Uruchamia pełną konwersję wsadową
        
        Args:
            chunk_filter: Opcjonalna funkcja filtrująca chunki (cx, cz) -> bool
            
        Returns:
            Statystyki konwersji
        """
        print("=" * 60)
        print("BATCH CONVERSION: BiblioCraft 1.7.10 -> 1.18.2")
        print("=" * 60)
        print(f"Świat: {self.world_path}")
        print(f"Output: {self.output_path}")
        print()
        
        # Faza 1: Analiza - znajdź wszystkie bloki BC
        print("Faza 1/3: Analiza mapy...")
        
        def analysis_progress(progress, message):
            if self.progress_callback:
                self.progress_callback(progress * 0.3, message)  # 30% na analizę
        
        all_results = self.parser.scan_all_regions(analysis_progress)
        
        # Filtruj chunki jeśli podano filter
        if chunk_filter:
            all_results = [
                r for r in all_results 
                if chunk_filter(r.chunk_x, r.chunk_z)
            ]
        
        self.stats.total_chunks = self.parser.get_statistics()["chunks_analyzed"]
        self.stats.chunks_with_bc = len(all_results)
        self.stats.total_bc_blocks = sum(r.block_count for r in all_results)
        
        print(f"  Znaleziono {self.stats.total_bc_blocks} bloków BC w {self.stats.chunks_with_bc} chunkach")
        print()
        
        # Faza 2: Konwersja
        print("Faza 2/3: Konwersja bloków...")
        
        total_blocks = self.stats.total_bc_blocks
        processed_blocks = 0
        
        for i, chunk_result in enumerate(all_results):
            # Konwertuj chunk
            self.convert_chunk(chunk_result)
            
            # Aktualizuj postęp
            processed_blocks += chunk_result.block_count
            progress = 30 + (processed_blocks / total_blocks) * 60  # 30-90%
            
            if self.progress_callback:
                self.progress_callback(
                    progress, 
                    f"Konwersja {processed_blocks}/{total_blocks} bloków"
                )
            
            # Log co 10 chunków
            if (i + 1) % 10 == 0:
                print(f"  Przetworzono {i+1}/{len(all_results)} chunków...")
        
        print(f"  Przekonwertowano {self.stats.converted_blocks} bloków")
        print()
        
        # Faza 3: Generowanie raportu
        print("Faza 3/3: Generowanie raportu...")
        self._generate_outputs()
        
        if self.progress_callback:
            self.progress_callback(100, "Konwersja zakończona")
        
        # Zakończ statystyki
        self.stats.end_time = datetime.now()
        
        # Podsumowanie
        print()
        print("=" * 60)
        print("PODSUMOWANIE")
        print("=" * 60)
        print(f"Czas wykonania: {self.stats.duration_seconds:.2f}s")
        print(f"Przetworzone chunki: {self.stats.chunks_with_bc}")
        print(f"Znalezione bloki BC: {self.stats.total_bc_blocks}")
        print(f"Przekonwertowane: {self.stats.converted_blocks}")
        print(f"Nieudane: {self.stats.failed_blocks}")
        print(f"Pominięte: {self.stats.skipped_blocks}")
        print(f"Ostrzeżenia: {self.stats.warnings_count}")
        print(f"Skuteczność: {self.stats.success_rate:.1f}%")
        print("=" * 60)
        
        return self.stats
    
    def convert_single_chunk(self, chunk_x: int, chunk_z: int) -> List[ConversionResult]:
        """
        Konwertuje pojedynczy chunk (przydatne do testów)
        
        Args:
            chunk_x: Współrzędna X chunka
            chunk_z: Współrzędna Z chunka
            
        Returns:
            Lista wyników konwersji
        """
        # Analizuj chunk
        chunk_result = self.parser.analyze_chunk(chunk_x, chunk_z)
        
        if not chunk_result.has_bc_blocks:
            print(f"Chunk {chunk_x},{chunk_z} nie zawiera bloków BC")
            return []
        
        print(f"Znaleziono {chunk_result.block_count} bloków BC w chunku {chunk_x},{chunk_z}")
        
        # Konwertuj
        return self.convert_chunk(chunk_result)
    
    def _generate_outputs(self):
        """Generuje pliki wyjściowe (NBT, raporty)"""
        # Zapisz wyniki konwersji
        self._save_conversion_results()
        
        # Zapisz statystyki
        self._save_statistics()
        
        # Zapisz błędy
        if self.stats.failed_blocks > 0:
            self._save_errors()
    
    def _save_conversion_results(self):
        """Zapisuje przekonwertowane bloki do JSON"""
        output_file = self.output_path / "converted_blocks.json"
        
        data = []
        for result in self.results:
            if result.success and result.converted_block:
                data.append({
                    "position": result.position,
                    "original_id": result.original_block.block_id,
                    "converted_id": result.converted_block.block_id,
                    "nbt": result.converted_block.tile_entity,
                    "warnings": result.warnings
                })
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        print(f"  Zapisano wyniki: {output_file}")
    
    def _save_statistics(self):
        """Zapisuje statystyki do JSON"""
        output_file = self.output_path / "conversion_stats.json"
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(self.stats.to_dict(), f, indent=2, ensure_ascii=False)
        
        print(f"  Zapisano statystyki: {output_file}")
    
    def _save_errors(self):
        """Zapisuje błędy do JSON"""
        output_file = self.output_path / "conversion_errors.json"
        
        errors = [
            {
                "position": result.position,
                "block_id": result.original_block.block_id,
                "error": result.error_message
            }
            for result in self.results
            if not result.success and result.error_message
        ]
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(errors, f, indent=2, ensure_ascii=False)
        
        print(f"  Zapisano błędy: {output_file}")
    
    def get_results_by_block_type(self) -> Dict[str, List[ConversionResult]]:
        """Grupuje wyniki według typu bloku"""
        results_by_type = {}
        
        for result in self.results:
            block_type = result.original_block.block_id
            if block_type not in results_by_type:
                results_by_type[block_type] = []
            results_by_type[block_type].append(result)
        
        return results_by_type


# Funkcje pomocnicze

def convert_world_bibliocraft(world_path_1710: str, 
                               output_path: str,
                               progress_callback=None) -> Dict:
    """
    Funkcja pomocnicza - konwertuje cały świat
    
    Args:
        world_path_1710: Ścieżka do świata 1.7.10
        output_path: Ścieżka do folderu wyjściowego
        progress_callback: Opcjonalny callback postępu
        
    Returns:
        Słownik ze statystykami
    """
    converter = BiblioCraftBatchConverter(world_path_1710, output_path)
    
    if progress_callback:
        converter.set_progress_callback(progress_callback)
    
    stats = converter.run_batch_conversion()
    return stats.to_dict()


def convert_chunk_bibliocraft(world_path_1710: str,
                               chunk_x: int,
                               chunk_z: int,
                               output_path: Optional[str] = None) -> List[ConversionResult]:
    """
    Funkcja pomocnicza - konwertuje pojedynczy chunk
    
    Args:
        world_path_1710: Ścieżka do świata
        chunk_x: Współrzędna X chunka
        chunk_z: Współrzędna Z chunka
        output_path: Opcjonalna ścieżka do zapisu wyników
        
    Returns:
        Lista wyników konwersji
    """
    if output_path is None:
        output_path = os.path.join(world_path_1710, "..", "bc_conversion_output")
    
    converter = BiblioCraftBatchConverter(world_path_1710, output_path)
    results = converter.convert_single_chunk(chunk_x, chunk_z)
    
    return results


# Testowanie
if __name__ == "__main__":
    print("=" * 60)
    print("TEST: BiblioCraft Batch Converter")
    print("=" * 60)
    
    # Test statystyk
    print("\n--- Test statystyk ---")
    from datetime import datetime
    stats = BatchConversionStats(start_time=datetime.now())
    stats.total_bc_blocks = 100
    stats.converted_blocks = 95
    stats.failed_blocks = 3
    stats.skipped_blocks = 2
    stats.end_time = datetime.now()
    
    print(f"  Skuteczność: {stats.success_rate:.1f}%")
    print(f"  Czas: {stats.duration_seconds:.2f}s")
    print(f"  Dict: {stats.to_dict()}")
    
    # Test wyniku konwersji
    print("\n--- Test ConversionResult ---")
    from bc_chunk_parser import BCBlockInChunk
    
    bc_block = BCBlockInChunk(
        x=100, y=64, z=200,
        block_id="BiblioCraft:Bookcase",
        block_name="Bookcase",
        metadata=0,
        chunk_x=6,
        chunk_z=12,
        tile_entity={"id": "TileEntityBookcase", "bookCount": 5}
    )
    
    result = ConversionResult(
        original_block=bc_block,
        converted_block=None,
        success=False,
        error_message="Test error"
    )
    
    print(f"  Pozycja: {result.position}")
    print(f"  Sukces: {result.success}")
    print(f"  Błąd: {result.error_message}")
    
    print("\n" + "=" * 60)
    print("Test zakończony!")
    print("=" * 60)
