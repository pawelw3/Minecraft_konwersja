#!/usr/bin/env python3
"""
Inspekcja chunka - wersja z pełnym odczytem bloków.
"""

import sys
import os
import struct
import zlib

script_dir = os.path.dirname(os.path.abspath(__file__))
src_path = os.path.join(script_dir, '..', '..', 'src')
sys.path.insert(0, os.path.normpath(src_path))

def read_raw_chunk(region_file, chunk_x, chunk_z):
    """Czyta surowe dane chunka z pliku regionu."""
    with open(region_file, 'rb') as f:
        data = f.read()
    
    # Lokalizacja chunka
    index = chunk_x + chunk_z * 32
    offset = index * 4
    chunk_data = data[offset:offset + 4]
    sector_offset = ((chunk_data[0] << 16) | (chunk_data[1] << 8) | chunk_data[2])
    sector_count = chunk_data[3]
    
    if sector_offset == 0:
        return None
    
    # Czytaj dane
    byte_offset = sector_offset * 4096
    length_data = data[byte_offset:byte_offset + 4]
    length = struct.unpack('>I', length_data)[0]
    compression_type = data[byte_offset + 4]
    compressed_data = data[byte_offset + 5:byte_offset + 5 + length - 1]
    
    if compression_type == 2:
        return zlib.decompress(compressed_data)
    return compressed_data

from minecraft_map_parser.nbt_parser import parse_nbt

def inspect_blocks(region_file, chunk_x, chunk_z):
    """Inspekcja bloków w chunku."""
    print(f"Inspekcja chunka ({chunk_x}, {chunk_z}) w {os.path.basename(region_file)}")
    
    raw = read_raw_chunk(region_file, chunk_x, chunk_z)
    if not raw:
        print("  Chunk nie istnieje!")
        return
    
    nbt = parse_nbt(raw)
    level = nbt.get('Level', {})
    if hasattr(level, 'value'):
        level = level.value
    
    global_x = level.get('xPos', 0)
    global_z = level.get('zPos', 0)
    if hasattr(global_x, 'value'):
        global_x = global_x.value
    if hasattr(global_z, 'value'):
        global_z = global_z.value
    
    print(f"  Globalne współrzędne: ({global_x}, {global_z})")
    
    sections = level.get('Sections', [])
    if hasattr(sections, 'value'):
        sections = sections.value
    
    print(f"  Sekcje: {len(sections)}")
    
    # Sprawdź każdą sekcję
    for section in sections:
        if hasattr(section, 'value'):
            section = section.value
        
        y = section.get('Y', 0)
        if hasattr(y, 'value'):
            y = y.value
        
        blocks = section.get('Blocks', b'')
        if hasattr(blocks, 'value'):
            blocks = blocks.value
        
        if isinstance(blocks, bytes) and len(blocks) == 4096:
            # Znajdź niezerowe bloki
            found = []
            for idx, bid in enumerate(blocks):
                if bid != 0:
                    local_y = idx // 256
                    local_z = (idx % 256) // 16
                    local_x = idx % 16
                    world_x = global_x * 16 + local_x
                    world_y = y * 16 + local_y
                    world_z = global_z * 16 + local_z
                    found.append((world_x, world_y, world_z, bid))
            
            if found:
                print(f"    Sekcja Y={y}: {len(found)} niezerowych bloków")
                for wx, wy, wz, bid in found[:10]:
                    block_name = {
                        1: "stone",
                        55: "redstone_wire",
                        93: "repeater",
                        137: "command_block",
                        152: "redstone_block"
                    }.get(bid, f"block_{bid}")
                    print(f"      ({wx}, {wy}, {wz}): {block_name} ({bid})")
                if len(found) > 10:
                    print(f"      ... i {len(found) - 10} więcej")

if __name__ == "__main__":
    world_dir = os.path.join(script_dir, '..', '1.7.10', 'world_spiral_test')
    
    print("=" * 60)
    print("CHUNK (0,0) - powinien mieć redstone block")
    inspect_blocks(os.path.join(world_dir, 'region', 'r.0.0.mca'), 0, 0)
    
    print()
    print("=" * 60)
    print("CHUNK (1,0) - powinien mieć command block")
    inspect_blocks(os.path.join(world_dir, 'region', 'r.0.0.mca'), 1, 0)
    
    print()
    print("=" * 60)
    print("CHUNK (0,1) - kolejny command block")
    inspect_blocks(os.path.join(world_dir, 'region', 'r.0.0.mca'), 0, 1)
