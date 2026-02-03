"""
Enchanting Plus Converter

Konwerter dla moda Enchanting Plus (1.7.10) -> Enchanting Infuser (1.18.2).

Moduł zawiera:
- Mapowania bloków i itemów
- Konwertery NBT dla Tile Entities
- Główny konwerter EnchantingPlusConverter
- Parser chunków (EPChunkParser)
- Konwerter wsadowy (EPBatchConverter)
- Generator raportów (EPReportGenerator)

Przykład użycia:
    >>> from src.converters.enchantingplus import EnchantingPlusConverter
    >>> converter = EnchantingPlusConverter()
    >>> result = converter.convert_block('EnchantingPlus:enchanting_table', position=(100, 64, 100))
    
Przykład batch conversion:
    >>> from src.converters.enchantingplus import EPBatchConverter
    >>> batch = EPBatchConverter('mapa_1710', 'output/ep_conversion')
    >>> result = batch.run_batch_conversion()
"""

# Główny konwerter
from .enchantingplus_converter import (
    EnchantingPlusConverter,
    ConversionResult,
    EPBlockConversion,
)

# Mapowania
from .mappings.block_mappings import (
    get_block_mapping,
    BLOCK_MAPPINGS_1710_TO_1182,
    is_enchantingplus_block,
    get_block_name,
    ALL_EP_BLOCK_IDS_1710,
)

# Konwertery NBT
from .nbt_converters.base_converter import (
    BaseNBTConverter,
    NBTConversionResult,
    IdentityConverter,
    NullConverter,
)

# Parser chunków
from .ep_chunk_parser import (
    EPChunkParser,
    EPBlockInChunk,
    ChunkAnalysisResult,
)

# Batch converter
from .batch_converter import (
    EPBatchConverter,
    BatchConversionStats,
    BatchConversionResult,
)

# Report generator
try:
    from .report_generator import (
        EPReportGenerator,
        VerificationItem,
    )
except ImportError:
    # Jeśli typing.Tuple nie jest dostępne w report_generator
    pass

__version__ = '1.0.0'
__author__ = 'AI Assistant'

__all__ = [
    # Główny konwerter
    'EnchantingPlusConverter',
    'ConversionResult',
    'EPBlockConversion',
    
    # Mapowania
    'get_block_mapping',
    'BLOCK_MAPPINGS_1710_TO_1182',
    'is_enchantingplus_block',
    'get_block_name',
    'ALL_EP_BLOCK_IDS_1710',
    
    # Konwertery NBT
    'BaseNBTConverter',
    'NBTConversionResult',
    'IdentityConverter',
    'NullConverter',
    
    # Parser chunków
    'EPChunkParser',
    'EPBlockInChunk',
    'ChunkAnalysisResult',
    
    # Batch converter
    'EPBatchConverter',
    'BatchConversionStats',
    'BatchConversionResult',
    
    # Report generator
    'EPReportGenerator',
    'VerificationItem',
]


def convert_world_enchantingplus(
    world_path_1710: str,
    output_path: str = "output/ep_conversion",
    progress_callback=None,
    max_regions: int = None
) -> dict:
    """
    Funkcja pomocnicza do konwersji całego świata.
    
    Args:
        world_path_1710: Ścieżka do świata 1.7.10
        output_path: Ścieżka do zapisu wyników
        progress_callback: Funkcja (percent, message) -> None
        max_regions: Maksymalna liczba regionów do przetworzenia
        
    Returns:
        Słownik ze statystykami konwersji
        
    Example:
        >>> stats = convert_world_enchantingplus('mapa_1710', 'output/ep')
        >>> print(f"Przekonwertowano: {stats['converted_blocks']}")
    """
    converter = EPBatchConverter(world_path_1710, output_path)
    
    if progress_callback:
        converter.set_progress_callback(progress_callback)
    
    result = converter.run_batch_conversion(max_regions=max_regions)
    
    # Wygeneruj raporty
    generator = EPReportGenerator(f"{output_path}/reports")
    generator.generate_full_report(result)
    
    return result.stats.to_dict()


def convert_chunk_enchantingplus(
    world_path_1710: str,
    chunk_x: int,
    chunk_z: int
) -> list:
    """
    Funkcja pomocnicza do konwersji pojedynczego chunka.
    
    Args:
        world_path_1710: Ścieżka do świata 1.7.10
        chunk_x: Współrzędna X chunka
        chunk_z: Współrzędna Z chunka
        
    Returns:
        Lista przekonwertowanych bloków
        
    Example:
        >>> blocks = convert_chunk_enchantingplus('mapa_1710', 10, 20)
        >>> for block in blocks:
        ...     print(f"{block.original_id} -> {block.converted.block_id_1182}")
    """
    converter = EPBatchConverter(world_path_1710)
    return converter.convert_single_chunk(chunk_x, chunk_z)


def generate_conversion_report(
    output_path: str,
    result=None,
    format: str = 'html'
) -> str:
    """
    Funkcja pomocnicza do generowania raportu.
    
    Args:
        output_path: Ścieżka do zapisu raportu
        result: Opcjonalny wynik konwersji (BatchConversionResult)
        format: Format raportu ('html', 'markdown', 'json')
        
    Returns:
        Ścieżka do wygenerowanego raportu
    """
    from .batch_converter import BatchConversionResult, BatchConversionStats
    
    generator = EPReportGenerator(output_path)
    
    if result is None:
        # Stwórz pusty raport
        stats = BatchConversionStats()
        result = BatchConversionResult(stats=stats, converted_blocks=[])
    
    if format == 'html':
        return generator.generate_html_report(result)
    elif format == 'markdown':
        return generator.generate_markdown_report(result)
    else:
        reports = generator.generate_full_report(result)
        return reports.get(format, reports['html'])
