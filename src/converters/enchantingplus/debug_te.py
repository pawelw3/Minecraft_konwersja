"""
Debug: Sprawdzenie Tile Entities w chunku
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))

from src.minecraft_map_parser.anvil_parser import AnvilParser


def debug_te():
    """Debug Tile Entities."""
    project_root = Path(__file__).resolve().parents[3]
    region_file = project_root / "lightweigh_map_templates" / "1710_modded" / "ep_test_world" / "region" / "r.0.0.mca"
    
    print("=" * 60)
    print("DEBUG: Tile Entities w regionie r.0.0.mca")
    print("=" * 60)
    print(f"Region file: {region_file}")
    print(f"Exists: {region_file.exists()}")
    
    parser = AnvilParser(str(region_file))
    chunk_data = parser.get_chunk(0, 0)
    
    if chunk_data is None:
        print("Chunk (0, 0) nie istnieje!")
        return
    
    print("\nChunk (0, 0) załadowany pomyślnie")
    
    # Pobierz Tile Entities
    tile_entities = chunk_data.get_tile_entities()
    print(f"\nLiczba Tile Entities: {len(tile_entities)}")
    
    print("\nSzczegóły Tile Entities:")
    for i, te in enumerate(tile_entities):
        print(f"\n  TE #{i+1}:")
        if isinstance(te, dict):
            for key, value in te.items():
                print(f"    {key}: {value}")
        else:
            print(f"    {te}")


if __name__ == "__main__":
    debug_te()
