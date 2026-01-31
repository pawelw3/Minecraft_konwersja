import sys
sys.path.insert(0, '.')
from mc_editkit.world.backends.anvil_backend import AnvilBackend
import nbtlib
from io import BytesIO

backend = AnvilBackend.__new__(AnvilBackend)  # Bypass init

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
print(f'  nbt["Level"]["Sections"]: {len(nbt["Level"]["Sections"])}')

# Użyj _create_section
section = backend._create_section(4)
print(f'  section type: {type(section)}')
print(f'  section["Y"]: {section["Y"]}')

# Dodaj do level
level = nbt['Level']
level['Sections'].append(section)

print('\nPo dodaniu:')
print(f'  nbt["Level"]["Sections"]: {len(nbt["Level"]["Sections"])}')

# Serializuj
buffer = BytesIO()
nbt.write(buffer, byteorder='big')
nbt_bytes = buffer.getvalue()
print(f'  Serialized: {len(nbt_bytes)} bytes')

# Deserializuj
bio = BytesIO(nbt_bytes)
tag = nbtlib.tag.Compound.parse(bio)

print('\nPo deserializacji:')
print(f'  Root keys: {list(tag.keys())}')
if 'Level' in tag:
    print(f'  Level keys: {list(tag["Level"].keys())}')
    print(f'  Sections: {len(tag["Level"].get("Sections", []))}')
