import sys
sys.path.insert(0, '.')
import nbtlib

# Stwórz chunk jak w _get_or_create_chunk
nbt = nbtlib.Compound({
    'Level': nbtlib.Compound({
        'xPos': nbtlib.Int(0),
        'zPos': nbtlib.Int(0),
        'Sections': nbtlib.List[nbtlib.Compound]([]),
    }),
    'DataVersion': nbtlib.Int(0)
})

print('Przed:')
print(f'  nbt type: {type(nbt)}')
print(f'  nbt["Level"] type: {type(nbt["Level"])}')

# Pobierz level
level = nbt['Level'] if 'Level' in nbt else nbt
print(f'  level type: {type(level)}')

# Dodaj sekcję
section = nbtlib.Compound({
    'Y': nbtlib.Byte(4),
    'Blocks': nbtlib.ByteArray([1] + [0] * 4095),
})
level['Sections'].append(section)

print('\nPo dodaniu sekcji:')
print(f'  nbt["Level"]["Sections"]: {len(nbt["Level"]["Sections"])}')

# Serializuj
from io import BytesIO
buffer = BytesIO()
nbt.write(buffer, byteorder='big')
nbt_bytes = buffer.getvalue()

# Deserializuj
bio = BytesIO(nbt_bytes)
tag = nbtlib.tag.Compound.parse(bio)

print('\nPo deserializacji:')
print(f'  Root keys: {list(tag.keys())}')
print(f'  Level keys: {list(tag["Level"].keys()) if "Level" in tag else "N/A"}')
