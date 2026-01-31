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

# Sprawdź Tile Entities w chunku
tile_entities = level.value.get('TileEntities', [])
if hasattr(tile_entities, 'value'):
    te_list = tile_entities.value
else:
    te_list = tile_entities

print("Droppery w ring counterze:")
for te in te_list:
    if isinstance(te, tuple):
        _, te = te
    
    te_val = te.value if hasattr(te, 'value') else te
    
    te_id = te_val.get('id')
    if isinstance(te_id, tuple): te_id = te_id[1]
    elif hasattr(te_id, 'value'): te_id = te_id.value
    
    if te_id not in ['Trap', 'Dropper']:  # Trap to ID droppera w 1.7.10
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
    
    # Sprawdź czy to dropper z ring countera (y=61 i x,z w odpowiednim zakresie)
    if y != 61:
        continue
    
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
    
    print(f"  Dropper at ({x},{y},{z}): {item_count} items {item_desc}")
