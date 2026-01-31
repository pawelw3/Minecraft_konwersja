#!/usr/bin/env python3
"""
Inspekcja chunka ze spiralnego testu.
"""

import sys
import os
import struct
import zlib

script_dir = os.path.dirname(os.path.abspath(__file__))
src_path = os.path.join(script_dir, '..', '..', 'src')
sys.path.insert(0, os.path.normpath(src_path))

from minecraft_map_parser.anvil_parser import AnvilParser

def inspect_chunk(region_file, chunk_x, chunk_z):
    """Sprawdza zawartość chunka."""
    print(f"Inspekcja chunka ({chunk_x}, {chunk_z}) w {region_file}")
    
    try:
        parser = AnvilParser(region_file)
        chunk = parser.get_chunk(chunk_x, chunk_z)
        
        if not chunk:
            print("  Chunk nie istnieje!")
            return
        
        print(f"  Globalne współrzędne: ({chunk.x}, {chunk.z})")
        
        # Sprawdź sekcje
        sections = chunk.get_sections()
        print(f"  Liczba sekcji: {len(sections)}")
        
        # Sprawdź Level data
        level = chunk.nbt.get('Level', {})
        if hasattr(level, 'value'):
            level = level.value
        print(f"  Level keys: {list(level.keys()) if isinstance(level, dict) else 'N/A'}")
        if isinstance(level, dict):
            print(f"  TerrainPopulated: {level.get('TerrainPopulated', 'N/A')}")
            print(f"  LastUpdate: {level.get('LastUpdate', 'N/A')}")
        
        # Sprawdź tile entities
        tile_entities = chunk.get_tile_entities()
        print(f"  Tile entities: {len(tile_entities)}")
        for te in tile_entities:
            print(f"    - {te.get('id', 'unknown')} at ({te.get('x')}, {te.get('y')}, {te.get('z')})")
            if 'Command' in te:
                print(f"      Command: {te['Command']}")
        
        # Sprawdź bloki w sekcji Y=4 (64//16=4)
        for section in sections:
            if isinstance(section, dict):
                y_val = section.get('Y')
                if y_val == 4:
                    print(f"  Sekcja Y={y_val}:")
                    blocks = section.get('Blocks', [])
                    data = section.get('Data', [])
                    print(f"    Bloki: {len(blocks)} bytes")
                    print(f"    Data: {len(data)} bytes")
                    
                    # Znajdź niezerowe bloki
                    non_zero = []
                    blocks_bytes = blocks
                    if hasattr(blocks, 'value'):
                        blocks_bytes = blocks.value
                    if isinstance(blocks_bytes, bytes):
                        for idx, byte in enumerate(blocks_bytes):
                            if byte != 0:
                                local_y = idx // 256
                                local_z = (idx % 256) // 16
                                local_x = idx % 16
                                non_zero.append((local_x, local_y + y_val*16, local_z, byte))
                    
                    print(f"    Niezerowe bloki: {len(non_zero)}")
                    for bx, by, bz, bid in non_zero[:20]:
                        print(f"      ({bx}, {by}, {bz}): ID={bid}")
                    if len(non_zero) > 20:
                        print(f"      ... i {len(non_zero) - 20} więcej")
                    break
        
    except Exception as e:
        print(f"  BŁĄD: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    world_dir = os.path.join(script_dir, '..', '1.7.10', 'world_spiral_test')
    
    # Sprawdź chunk (0,0) - powinien mieć redstone block
    print("=" * 60)
    inspect_chunk(os.path.join(world_dir, 'region', 'r.0.0.mca'), 0, 0)
    
    print()
    print("=" * 60)
    # Sprawdź chunk (1,0) - powinien mieć command block
    inspect_chunk(os.path.join(world_dir, 'region', 'r.0.0.mca'), 1, 0)
