import gzip
import sys
sys.path.insert(0, 'src')
from minecraft_map_parser.nbt_parser import NBTParser, NBTTag
from schematic_to_world import convert_tile_entity_nbt

with open('output/digital_counter_v2.schematic', 'rb') as f:
    data = gzip.decompress(f.read())

parser = NBTParser(data)
schem = parser.parse()

tile_entities = schem.value.get('TileEntities', [])
if hasattr(tile_entities, 'value'):
    te_list = tile_entities.value
else:
    te_list = tile_entities

print("Konwersja TE z schematica:")
for te in te_list:
    if isinstance(te, tuple):
        _, te = te
    
    te_val = te.value if hasattr(te, 'value') else te
    
    te_id = te_val.get('id')
    if isinstance(te_id, tuple): te_id = te_id[1]
    elif hasattr(te_id, 'value'): te_id = te_id.value
    
    if te_id != 'Trap':
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
    
    print(f"  TE z schematica: {te_id} at ({x},{y},{z})")
    print(f"  Type: {type(te)}")
    
    if isinstance(te, NBTTag):
        print(f"  NBTTag type: {te.type}")
        print(f"  NBTTag value type: {type(te.value)}")
        
        # Sprawdź Items
        items_tag = te.value.get('Items')
        if items_tag:
            print(f"  Items tag type: {type(items_tag)}")
            if isinstance(items_tag, NBTTag):
                print(f"  Items NBTTag type: {items_tag.type}")
                print(f"  Items value: {items_tag.value}")
        
        # Konwertuj
        world_x = x  # już relatywne
        world_y = y + 60  # dodaj target_y
        world_z = z + 2  # dodaj offset_z
        
        result = convert_tile_entity_nbt(te, world_x, world_y, world_z)
        print(f"  Po konwersji: {result}")
