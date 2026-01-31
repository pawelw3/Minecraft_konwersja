import gzip
import sys
sys.path.insert(0, 'src')
from minecraft_map_parser.nbt_parser import NBTParser

with open('output/digital_counter_v2.schematic', 'rb') as f:
    data = gzip.decompress(f.read())

parser = NBTParser(data)
schem = parser.parse()

tile_entities = schem.value.get('TileEntities', [])
if hasattr(tile_entities, 'value'):
    te_list = tile_entities.value
else:
    te_list = tile_entities

print("TileEntities w schematicu:")
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
    item_count = 0
    item_desc = ""
    
    if items:
        if hasattr(items, 'value'):
            items = items.value
        if isinstance(items, list):
            item_count = len(items)
            for item in items:
                if isinstance(item, tuple):
                    _, item = item
                item_val = item.value if hasattr(item, 'value') else item
                
                item_id = item_val.get('id')
                if isinstance(item_id, tuple): item_id = item_id[1]
                elif hasattr(item_id, 'value'): item_id = item_id.value
                
                count = item_val.get('Count', 1)
                if isinstance(count, tuple): count = count[1]
                elif hasattr(count, 'value'): count = count.value
                
                slot = item_val.get('Slot', 0)
                if isinstance(slot, tuple): slot = slot[1]
                elif hasattr(slot, 'value'): slot = slot.value
                
                item_desc += f"[ID:{item_id} x{count} slot{slot}]"
    
    print(f"  {te_id} at ({x},{y},{z}): {item_count} items {item_desc}")
