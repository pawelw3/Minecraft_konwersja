import sys
sys.path.insert(0, 'src')
import struct
import zlib
from pathlib import Path

region_path = Path('lightweigh_map_templates/1710_modded/konwersja1_with_schematic/region/r.0.0.mca')

# Read and decompress chunk
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

def get_block(chunk, x, y, z):
    level = chunk.value['Level']
    sections = level.value['Sections']
    
    section_idx = y // 16
    local_y = y % 16
    local_x = x % 16
    local_z = z % 16
    
    for sec in sections.value:
        if isinstance(sec, tuple):
            _, sec = sec
        y_val = sec.get('Y')
        if isinstance(y_val, tuple):
            y_val = y_val[1]
        elif hasattr(y_val, 'value'):
            y_val = y_val.value
            
        if y_val != section_idx:
            continue
        
        blocks_tag = sec.get('Blocks')
        if isinstance(blocks_tag, tuple):
            blocks = blocks_tag[1]
        elif hasattr(blocks_tag, 'value'):
            blocks = blocks_tag.value
        else:
            continue
            
        idx = local_y * 256 + local_z * 16 + local_x
        if idx < len(blocks):
            return blocks[idx]
    return 0

# Check specific blocks
coords = [
    (1, 62, 2, 'clock_inverter_support'),
    (6, 60, 6, 'D0_support'),
    (6, 61, 6, 'D0'),
    (6, 61, 5, 'C0'),
    (6, 61, 4, 'CMD0'),
    (0, 63, 2, 'master_switch'),
    (3, 63, 2, 'clock_delay_r1'),
    (2, 63, 2, 'torch'),
    (6, 63, 2, 'clock_out'),
]

print('Sprawdzenie blokow w regionie:')
print('-'*50)
block_names = {0: 'air', 1: 'stone', 55: 'redstone_wire', 69: 'lever', 75: 'torch_off', 93: 'repeater', 137: 'cmd_block', 149: 'comparator', 158: 'dropper'}
for x, y, z, name in coords:
    bid = get_block(chunk, x, y, z)
    bname = block_names.get(bid, "?")
    print(f'({x},{y},{z}): {bid} ({bname}) - {name}')
