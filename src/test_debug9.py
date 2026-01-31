import sys
sys.path.insert(0, '.')
import nbtlib
from io import BytesIO

# Stwórz prosty chunk NBT
nbt = nbtlib.Compound({
    'Level': nbtlib.Compound({
        'xPos': nbtlib.Int(0),
        'zPos': nbtlib.Int(0),
        'Sections': nbtlib.List[nbtlib.Compound]([
            nbtlib.Compound({
                'Y': nbtlib.Byte(4),
                'Blocks': nbtlib.ByteArray([1] + [0] * 4095),
            })
        ]),
    }),
    'DataVersion': nbtlib.Int(0)
})

print('Przed serializacją:')
print(f'  Keys: {list(nbt.keys())}')
print(f'  Level keys: {list(nbt["Level"].keys())}')

# Serializuj
buffer = BytesIO()
nbt.write(buffer, byteorder='big')
nbt_bytes = buffer.getvalue()
print(f'\nSerialized: {len(nbt_bytes)} bytes')

# Deserializuj
bio = BytesIO(nbt_bytes)
tag = nbtlib.tag.Compound.parse(bio)

print('\nPo deserializacji:')
print(f'  Root keys: {list(tag.keys())}')
if 'Level' in tag:
    print(f'  Level keys: {list(tag["Level"].keys())}')
    sections = tag['Level'].get('Sections', [])
    print(f'  Sections: {len(sections)}')
