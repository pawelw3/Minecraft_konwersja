"""
Debug - odczyt chunka z regionu.
"""

import struct
import zlib
from pathlib import Path
from minecraft_map_parser.nbt_parser import NBTTag, NBTParser


def read_chunk_from_region(region_path: Path, chunk_x: int, chunk_z: int) -> NBTTag:
    """Odczytuje chunk z pliku regionu."""
    
    local_x = chunk_x % 32
    local_z = chunk_z % 32
    
    with open(region_path, 'rb') as f:
        location_offset = (local_z * 32 + local_x) * 4
        f.seek(location_offset)
        
        offset_data = f.read(4)
        if len(offset_data) < 4:
            return None
        
        offset = ((offset_data[0] << 16) | (offset_data[1] << 8) | offset_data[2]) * 4096
        sector_count = offset_data[3]
        
        print(f"Chunk ({chunk_x}, {chunk_z}):")
        print(f"  Local: ({local_x}, {local_z})")
        print(f"  Offset: {offset} bytes, Sectors: {sector_count}")
        
        if offset == 0:
            print("  Chunk is empty (offset=0)")
            return None
        
        f.seek(offset)
        length = struct.unpack('>I', f.read(4))[0]
        compression = struct.unpack('B', f.read(1))[0]
        chunk_data = f.read(length - 1)
        
        print(f"  Length: {length}, Compression: {compression}")
        
        if compression == 2:
            decompressed = zlib.decompress(chunk_data)
        else:
            decompressed = chunk_data
        
        parser = NBTParser(decompressed)
        return parser.parse()


def print_chunk_info(chunk_nbt: NBTTag):
    """Wyświetla informacje o chunku."""
    if not chunk_nbt:
        print("Chunk is None")
        return
    
    print(f"Root type: {chunk_nbt.type}")
    print(f"Root name: {chunk_nbt.name}")
    
    level = chunk_nbt.value.get('Level')
    if not level:
        print("No Level tag found")
        return
    
    print(f"\nLevel contents:")
    for key in level.value.keys():
        tag = level.value[key]
        print(f"  {key}: type={tag.type}")
    
    # Sections
    sections = level.value.get('Sections')
    if sections:
        print(f"\nSections count: {len(sections.value)}")
        for i, section in enumerate(sections.value):
            if isinstance(section, tuple):
                _, section = section
            if isinstance(section, NBTTag) and section.type == NBTTag.TAG_COMPOUND:
                y_val = section.value.get('Y')
                y = y_val.value if y_val else '?'
                blocks = section.value.get('Blocks')
                print(f"  Section {i}: Y={y}, has Blocks={blocks is not None}")
                if blocks:
                    non_air = sum(1 for b in blocks.value if b != 0)
                    print(f"    Non-air blocks: {non_air}")
    
    # Tile Entities
    tes = level.value.get('TileEntities')
    if tes:
        print(f"\nTile Entities count: {len(tes.value)}")
    
    # Position
    x_pos = level.value.get('xPos')
    z_pos = level.value.get('zPos')
    if x_pos and z_pos:
        print(f"\nChunk position: ({x_pos.value}, {z_pos.value})")


if __name__ == "__main__":
    import sys
    
    region_path = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("lightweigh_map_templates/1710_modded/konwersja1_with_schematic/region/r.0.0.mca")
    chunk_x = int(sys.argv[2]) if len(sys.argv) > 2 else 0
    chunk_z = int(sys.argv[3]) if len(sys.argv) > 3 else 0
    
    chunk = read_chunk_from_region(region_path, chunk_x, chunk_z)
    print_chunk_info(chunk)
