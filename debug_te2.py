import gzip
import sys
sys.path.insert(0, 'src')
from minecraft_map_parser.nbt_parser import NBTParser

with open('output/digital_counter_v2.schematic', 'rb') as f:
    data = gzip.decompress(f.read())

parser = NBTParser(data)
schem = parser.parse()

# Sprawdź wymiary i offsety
width = schem.value['Width'].value
height = schem.value['Height'].value
length = schem.value['Length'].value
offset_x = schem.value.get('WEOffsetX', 0)
offset_y = schem.value.get('WEOffsetY', 0)
offset_z = schem.value.get('WEOffsetZ', 0)

if hasattr(offset_x, 'value'): offset_x = offset_x.value
if hasattr(offset_y, 'value'): offset_y = offset_y.value
if hasattr(offset_z, 'value'): offset_z = offset_z.value

print(f'Schematic: {width}x{height}x{length}')
print(f'Offset: ({offset_x}, {offset_y}, {offset_z})')

# Sprawdź bloki na pozycjach Tile Entities
blocks = schem.value['Blocks'].value

def get_block(schem_x, schem_y, schem_z):
    idx = schem_y * width * length + schem_z * width + schem_x
    if 0 <= idx < len(blocks):
        return blocks[idx]
    return -1

# Sprawdź Tile Entities
tile_entities = schem.value.get('TileEntities', [])
if hasattr(tile_entities, 'value'):
    te_list = tile_entities.value
else:
    te_list = tile_entities

print(f'\nTileEntities ({len(te_list)}):')
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
    
    block_id = get_block(x, y, z)
    
    # Sprawdź Items
    items = te_val.get('Items')
    has_items = 'YES' if items else 'NO'
    
    print(f'  TE: {te_id} at ({x},{y},{z}), BlockID: {block_id}, Items: {has_items}')

# Sprawdź gdzie są droppery w schematicu (ID 158)
print(f'\nDroppers (ID 158) w schematicu:')
for y in range(height):
    for z in range(length):
        for x in range(width):
            idx = y * width * length + z * width + x
            if blocks[idx] == 158:
                print(f'  Dropper at ({x},{y},{z})')
