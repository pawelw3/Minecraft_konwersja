import gzip
import sys
sys.path.insert(0, 'src')
from minecraft_map_parser.nbt_parser import NBTParser

with open('output/digital_counter_v2.schematic', 'rb') as f:
    data = gzip.decompress(f.read())

parser = NBTParser(data)
schem = parser.parse()

# Sprawdź Tile Entities
tile_entities = schem.value.get('TileEntities', [])
if hasattr(tile_entities, 'value'):
    te_list = tile_entities.value
else:
    te_list = tile_entities

print(f'TileEntities count: {len(te_list)}')

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
    
    # Sprawdź Items
    items = te_val.get('Items')
    has_items = 'YES' if items else 'NO'
    
    print(f'  TE: {te_id} at ({x},{y},{z}), Items: {has_items}')
