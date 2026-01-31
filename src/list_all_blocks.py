import sys
sys.path.insert(0, 'src')
import struct
import zlib
from pathlib import Path

region_path = Path('lightweigh_map_templates/1710_modded/konwersja1_with_schematic/region/r.0.0.mca')

with open(region_path, 'rb') as f:
    location = f.read(4096)
    offset = ((location[0] << 16) | (location[1] << 8) | location[2]) * 4096
    f.seek(offset)
    length = struct.unpack('>I', f.read(4))[0]
    compression = struct.unpack('B', f.read(1))[0]
    data = f.read(length - 1)
    decompressed = zlib.decompress(data)

from minecraft_map_parser.nbt_parser import NBTParser
parser = NBTParser(decompressed)
chunk = parser.parse()

level = chunk.value['Level']
print(f"xPos: {level.value['xPos'].value}")
print(f"zPos: {level.value['zPos'].value}")

sections = level.value['Sections']
print(f"Sections: {len(sections.value)}")

block_names = {0: 'air', 1: 'stone', 55: 'redstone_wire', 69: 'lever', 75: 'torch_off', 93: 'repeater', 137: 'cmd_block', 149: 'comparator', 158: 'dropper'}

# Show all blocks in section Y=3
for sec in sections.value:
    if isinstance(sec, tuple):
        _, sec = sec
    y_val = sec.get('Y')
    if isinstance(y_val, tuple):
        y_val = y_val[1]
    elif hasattr(y_val, 'value'):
        y_val = y_val.value
    
    if y_val != 3:
        continue
    
    blocks = sec.get('Blocks')
    if isinstance(blocks, tuple):
        blocks = blocks[1]
    elif hasattr(blocks, 'value'):
        blocks = blocks.value
    
    print(f"Non-air blocks in section Y=3 (world Y=48-63):")
    for y in range(16):
        for z in range(16):
            for x in range(16):
                idx = y * 256 + z * 16 + x
                if idx < len(blocks) and blocks[idx] != 0:
                    abs_x = x
                    abs_y = 3 * 16 + y
                    abs_z = z
                    bid = blocks[idx]
                    name = block_names.get(bid, f"ID:{bid}")
                    print(f"  ({abs_x},{abs_y},{abs_z}): {bid} ({name})")
