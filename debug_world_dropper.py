import struct
import zlib
import sys
sys.path.insert(0, 'src')
from minecraft_map_parser.nbt_parser import NBTParser

with open('headless_server/1.7.10/world/region/r.0.0.mca', 'rb') as f:
    header = f.read(4096)
    offset = ((header[0] << 16) | (header[1] << 8) | header[2]) * 4096
    f.seek(offset)
    length = struct.unpack('>I', f.read(4))[0]
    f.read(1)
    data = zlib.decompress(f.read(length - 1))

parser = NBTParser(data)
chunk = parser.parse()
level = chunk.value['Level']
sections = level.value['Sections']

# Sprawdź dropper D0 na pozycji (6, 61, 8)
world_x, world_y, world_z = 6, 61, 8

local_x = world_x % 16
local_z = world_z % 16
section_idx = world_y // 16
local_y = world_y % 16

print(f'World ({world_x},{world_y},{world_z})')
print(f'  Local: ({local_x},{local_y},{local_z})')
print(f'  Section: {section_idx}')

for sec in sections.value:
    if isinstance(sec, tuple):
        _, sec = sec
    y_val = sec.get('Y')
    if isinstance(y_val, tuple): y_val = y_val[1]
    elif hasattr(y_val, 'value'): y_val = y_val.value
    
    if y_val == section_idx:
        blocks = sec.get('Blocks')
        if isinstance(blocks, tuple): blocks = blocks[1]
        elif hasattr(blocks, 'value'): blocks = blocks.value
        
        block_idx = local_y * 256 + local_z * 16 + local_x
        print(f'  Block ID at idx {block_idx}: {blocks[block_idx]}')
        break

# Sprawdź Tile Entities w chunku
tile_entities = level.value.get('TileEntities', [])
if hasattr(tile_entities, 'value'):
    te_list = tile_entities.value
else:
    te_list = tile_entities

print(f'\nTileEntities in chunk ({len(te_list)}):')
for te in te_list:
    if isinstance(te, tuple):
        _, te = te
    
    te_val = te.value if hasattr(te, 'value') else te
    
    te_id = te_val.get('id')
    if isinstance(te_id, tuple): te_id = te_id[1]
    elif hasattr(te_id, 'value'): te_id = te_id.value
    
    x = te_val.get('x')
    y = te_val.get('y')
    z = te_val.get('z')
    
    if isinstance(x, tuple): x = x[1]
    elif hasattr(x, 'value'): x = x.value
    if isinstance(y, tuple): y = y[1]
    elif hasattr(y, 'value'): y = y.value
    if isinstance(z, tuple): z = z[1]
    elif hasattr(z, 'value'): z = z.value
    
    items = te_val.get('Items')
    has_items = 'YES' if items else 'NO'
    
    print(f'  TE: {te_id} at ({x},{y},{z}), Items: {has_items}')
