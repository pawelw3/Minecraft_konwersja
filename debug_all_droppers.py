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

# Sprawdź bloki na poziomie Y=61 (sekcja 3, lokalne Y=13)
sections = level.value['Sections']
for sec in sections.value:
    if isinstance(sec, tuple):
        _, sec = sec
    y_val = sec.get('Y')
    if isinstance(y_val, tuple): y_val = y_val[1]
    elif hasattr(y_val, 'value'): y_val = y_val.value
    
    if y_val == 3:
        blocks = sec.get('Blocks')
        if isinstance(blocks, tuple): blocks = blocks[1]
        elif hasattr(blocks, 'value'): blocks = blocks.value
        
        print('Droppers (ID 158) na Y=61 w chunku:')
        for lx in range(16):
            for lz in range(16):
                idx = 13 * 256 + lz * 16 + lx  # lokalne Y=13
                if blocks[idx] == 158:
                    world_x = lx
                    world_z = lz
                    print(f'  Dropper at ({world_x},61,{world_z})')
        break

# Sprawdź Tile Entities
tile_entities = level.value.get('TileEntities', [])
if hasattr(tile_entities, 'value'):
    te_list = tile_entities.value
else:
    te_list = tile_entities

print(f'\nTileEntities ({len(te_list)}):')
droppers = []
for te in te_list:
    if isinstance(te, tuple):
        _, te = te
    
    te_val = te.value if hasattr(te, 'value') else te
    
    te_id = te_val.get('id')
    if isinstance(te_id, tuple): te_id = te_id[1]
    elif hasattr(te_id, 'value'): te_id = te_id.value
    
    if te_id not in ['Trap', 'Dropper']:
        continue
    
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
    item_count = 0
    if items:
        if hasattr(items, 'value'):
            items = items.value
        if isinstance(items, list):
            item_count = len(items)
    
    droppers.append((x, y, z, item_count))

print(f'Droppers: {len(droppers)}')
for d in sorted(droppers):
    print(f'  ({d[0]},{d[1]},{d[2]}): {d[3]} items')
