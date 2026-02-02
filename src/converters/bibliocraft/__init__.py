"""
Konwerter BiblioCraft 1.7.10 -> 1.18.2 (Supplementaries + FramedBlocks + ImmersivePaintings)

Zawiera symulacje funkcjonalności wszystkich trzech docelowych modów
oraz właściwą implementację konwerterów NBT.
"""

# Symulacje (Zadanie 2)
from .simulation_framedblocks import (
    FramedBlockEntity, 
    FramedShape, 
    BlockState, 
    ItemStack,
    BiblioCraftFurnitureConverter,
    BC_TO_FRAMED_MAP,
    WOOD_TEXTURE_MAP
)

from .simulation_immersive_paintings import (
    ImmersivePaintingEntity,
    PaintingData,
    PaintingManager,
    BiblioCraftPaintingConverter,
    PaintingSize,
    PaintingFilter
)

from .simulation_supplementaries import (
    BookPileBlockEntity,
    ItemShelfBlockEntity,
    JarBlockEntity,
    BCBookcaseTE,
    BCShelfTE,
    SupplementariesConverter,
    ContainerHelper
)

# Konwertery NBT (Zadanie 3)
from .nbt_converter import (
    BC1170NBTReader,
    BC1182NBTWriter,
    BiblioCraftNBTConverter,
    ConvertedBlock,
    convert_bc_nbt_to_1182
)

from .texture_mappings import (
    WOOD_TEXTURE_MAP,
    STONE_TEXTURE_MAP,
    METAL_TEXTURE_MAP,
    NATURAL_TEXTURE_MAP,
    MOD_TEXTURE_MAP,
    COMPLETE_TEXTURE_MAP,
    convert_texture_id,
    convert_to_block_state,
    is_valid_texture,
    get_texture_category
)

from .image_converter import (
    BCImageInfo,
    IPImageRegistration,
    BCImageScanner,
    IPImageRegistry,
    BCtoIPImageConverter,
    convert_painting_bc_to_ip
)

from .map_analyzer import (
    BCBlockInstance,
    BCBlockStatistics,
    BCMapAnalyzer,
    BCConversionPlanner,
    analyze_world_for_bibliocraft
)

# Integracja z parserem (Zadanie 4)
from .bc_chunk_parser import (
    BCBlockInChunk,
    ChunkAnalysisResult,
    BiblioCraftChunkParser,
    find_bc_blocks_in_world
)

from .batch_converter import (
    ConversionResult,
    BatchConversionStats,
    BiblioCraftBatchConverter,
    convert_world_bibliocraft,
    convert_chunk_bibliocraft
)

from .report_generator import (
    LostDataInfo,
    VerificationItem,
    BiblioCraftReportGenerator,
    generate_conversion_report
)

from .edge_cases_handler import (
    EdgeCase,
    EdgeCaseLogger,
    BCNBTFixup,
    UnknownBlockHandler,
    TextureFallbackResolver,
    BCEdgeCaseManager
)

__all__ = [
    # FramedBlocks (symulacja)
    'FramedBlockEntity', 'FramedShape', 'BlockState', 'ItemStack',
    'BiblioCraftFurnitureConverter', 'BC_TO_FRAMED_MAP',
    # Immersive Paintings (symulacja)
    'ImmersivePaintingEntity', 'PaintingData', 'PaintingManager',
    'BiblioCraftPaintingConverter', 'PaintingSize', 'PaintingFilter',
    # Supplementaries (symulacja)
    'BookPileBlockEntity', 'ItemShelfBlockEntity', 'JarBlockEntity',
    'BCBookcaseTE', 'BCShelfTE', 'SupplementariesConverter', 'ContainerHelper',
    # NBT Converter (Zadanie 3)
    'BC1170NBTReader', 'BC1182NBTWriter', 'BiblioCraftNBTConverter',
    'ConvertedBlock', 'convert_bc_nbt_to_1182',
    # Texture Mappings (Zadanie 3)
    'WOOD_TEXTURE_MAP', 'STONE_TEXTURE_MAP', 'METAL_TEXTURE_MAP',
    'NATURAL_TEXTURE_MAP', 'MOD_TEXTURE_MAP', 'COMPLETE_TEXTURE_MAP',
    'convert_texture_id', 'convert_to_block_state', 'is_valid_texture',
    'get_texture_category',
    # Image Converter (Zadanie 3)
    'BCImageInfo', 'IPImageRegistration', 'BCImageScanner',
    'IPImageRegistry', 'BCtoIPImageConverter', 'convert_painting_bc_to_ip',
    # Map Analyzer (Zadanie 3)
    'BCBlockInstance', 'BCBlockStatistics', 'BCMapAnalyzer',
    'BCConversionPlanner', 'analyze_world_for_bibliocraft',
    # Chunk Parser (Zadanie 4)
    'BCBlockInChunk', 'ChunkAnalysisResult', 'BiblioCraftChunkParser',
    'find_bc_blocks_in_world',
    # Batch Converter (Zadanie 4)
    'ConversionResult', 'BatchConversionStats', 'BiblioCraftBatchConverter',
    'convert_world_bibliocraft', 'convert_chunk_bibliocraft',
    # Report Generator (Zadanie 4)
    'LostDataInfo', 'VerificationItem', 'BiblioCraftReportGenerator',
    'generate_conversion_report',
    # Edge Cases Handler (Zadanie 4)
    'EdgeCase', 'EdgeCaseLogger', 'BCNBTFixup', 'UnknownBlockHandler',
    'TextureFallbackResolver', 'BCEdgeCaseManager'
]
