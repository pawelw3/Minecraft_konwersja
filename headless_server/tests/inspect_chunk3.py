#!/usr/bin/env python3
"""
Inspekcja chunka - wersja z debugowaniem sekcji.
"""

import sys
import os

script_dir = os.path.dirname(os.path.abspath(__file__))
src_path = os.path.join(script_dir, '..', '..', 'src')
sys.path.insert(0, os.path.normpath(src_path))

from minecraft_map_parser.anvil_parser import AnvilParser

def inspect_chunk_detailed(region_file, chunk_x, chunk_z):
    """Szczegółowa inspekcja chunka."""
    print(f"Chunk ({chunk_x}, {chunk_z}) w {os.path.basename(region_file)}")
    
    try:
        parser = AnvilParser(region_file)
        chunk = parser.get_chunk(chunk_x, chunk_z)
        
        if not chunk:
            print("  Chunk nie istnieje!")
            return
        
        # Pobierz surowe dane NBT
        nbt = chunk.nbt
        level = nbt.get('Level', {})
        if hasattr(level, 'value'):
            level = level.value
        
        sections = level.get('Sections', [])
        if hasattr(sections, 'value'):
            sections = sections.value
        
        print(f"  Liczba sekcji: {len(sections)}")
        
        for section in sections:
            if hasattr(section, 'value'):
                section = section.value
            
            y = section.get('Y')
            if hasattr(y, 'value'):
                y = y.value
            
            blocks = section.get('Blocks')
            if hasattr(blocks, 'value'):
                blocks = blocks.value
            
            print(f"    Sekcja Y={y}: type={type(blocks).__name__}, len={len(blocks) if blocks else 0}")
            
            if isinstance(blocks, (bytes, bytearray)) and len(blocks) > 0:
                # Policz niezerowe
                non_zero = sum(1 for b in blocks if b != 0)
                print(f"      Niezerowe bloki: {non_zero}")
                
                if non_zero > 0:
                    # Pokaż pierwsze 5
                    for i, b in enumerate(blocks):
                        if b != 0:
                            local_y = i // 256
                            local_z = (i % 256) // 16
                            local_x = i % 16
                            print(f"        Block at ({local_x}, {local_y + y*16}, {local_z}): ID={b}")
                            if i > 50:  # Limit
                                break

if __name__ == "__main__":
    world_dir = os.path.join(script_dir, '..', '1.7.10', 'world_spiral_test')
    
    print("=" * 60)
    inspect_chunk_detailed(os.path.join(world_dir, 'region', 'r.0.0.mca'), 0, 0)
    
    print()
    print("=" * 60)
    inspect_chunk_detailed(os.path.join(world_dir, 'region', 'r.0.0.mca'), 1, 0)
