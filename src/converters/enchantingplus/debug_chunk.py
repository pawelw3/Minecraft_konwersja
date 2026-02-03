"""
Debug: Sprawdzenie chunka z blokami EP
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))

from src.converters.enchantingplus import EPChunkParser


def debug_chunk():
    """Debug chunka z blokami EP."""
    project_root = Path(__file__).resolve().parents[3]
    test_world_path = str(project_root / "lightweigh_map_templates" / "1710_modded" / "ep_test_world")
    
    parser = EPChunkParser(test_world_path)
    
    print("=" * 60)
    print("DEBUG: Analiza chunka (0, 0)")
    print("=" * 60)
    print(f"Ścieżka: {parser.world_path}")
    print(f"Region path: {parser.region_path}")
    print(f"Region files: {list(parser.region_path.glob('*.mca'))}")
    
    # Analizuj chunk (0, 0)
    result = parser.analyze_chunk(0, 0)
    
    print(f"\nWynik analizy chunka (0, 0):")
    print(f"  Has EP blocks: {result.has_ep_blocks}")
    print(f"  EP blocks count: {len(result.ep_blocks)}")
    print(f"  Total TE: {result.total_tile_entities}")
    
    if result.ep_blocks:
        print("\n  Znalezione bloki EP:")
        for block in result.ep_blocks:
            print(f"    - {block.block_id} at {block.absolute_pos}")
    
    # Sprawdź czy plik region istnieje
    region_file = parser.region_path / "r.0.0.mca"
    print(f"\nRegion file exists: {region_file.exists()}")
    print(f"Region file size: {region_file.stat().st_size if region_file.exists() else 0} bytes")
    
    # Spróbuj debug block IDs
    print("\n" + "=" * 60)
    print("DEBUG: Block IDs w chunku (0, 0)")
    print("=" * 60)
    
    debug_result = parser.debug_chunk_block_ids(0, 0)
    print(f"Result: {debug_result}")


if __name__ == "__main__":
    debug_chunk()
