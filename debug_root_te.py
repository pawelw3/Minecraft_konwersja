import gzip
import sys
sys.path.insert(0, 'src')
from minecraft_map_parser.nbt_parser import NBTParser, NBTTag

with open('output/digital_counter_v2.schematic', 'rb') as f:
    data = gzip.decompress(f.read())

parser = NBTParser(data)
root = parser.parse()

print(f'Root type: {root.type}')
print(f'Root value type: {type(root.value)}')

# Pobierz TileEntities
te_tag = root.value.get('TileEntities')
print(f'\nTE tag type: {type(te_tag)}')
if isinstance(te_tag, NBTTag):
    print(f'TE NBTTag type: {te_tag.type}')
    print(f'TE value type: {type(te_tag.value)}')
    
    if isinstance(te_tag.value, list):
        print(f'List length: {len(te_tag.value)}')
        for i, item in enumerate(te_tag.value[:3]):  # Pierwsze 3
            print(f'  Item {i}: type={type(item)}')
            if isinstance(item, NBTTag):
                print(f'    NBTTag type: {item.type}')
            elif isinstance(item, tuple):
                print(f'    Tuple: {item[0]}, value type={type(item[1])}')
            elif isinstance(item, dict):
                print(f'    Dict keys: {list(item.keys())[:5]}')

# Sprawdź co zwraca root["TileEntities"]
print('\n\nroot["TileEntities"]:')
te_list = root["TileEntities"]
print(f'Type: {type(te_list)}')
if isinstance(te_list, list) and len(te_list) > 0:
    print(f'First item type: {type(te_list[0])}')
