import gzip
import sys
sys.path.insert(0, 'src')
from minecraft_map_parser.nbt_parser import NBTParser, NBTTag

with open('output/digital_counter_v2.schematic', 'rb') as f:
    data = gzip.decompress(f.read())

parser = NBTParser(data)
root = parser.parse()

te_list = root["TileEntities"]

print(f'TE list length: {len(te_list)}')
print(f'First TE type: {type(te_list[0])}')

# Sprawdź pierwszy TE (dropper z itemem)
te0 = te_list[0]
print(f'\nFirst TE keys: {list(te0.keys())}')

for key, value in te0.items():
    print(f'  {key}: type={type(value)}, value={value}')
    if isinstance(value, NBTTag):
        print(f'    NBTTag type: {value.type}, value={value.value}')
