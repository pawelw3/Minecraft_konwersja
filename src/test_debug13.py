import sys
sys.path.insert(0, '.')
from mc_editkit.world.backends.anvil_backend import AnvilBackend
from mc_editkit.world.types import Pos
import shutil
import os

CLEAN_WORLD = r'..\headless_server\tests\headless_server\1.7.10_clean'
TEST_WORLD = r'C:\Users\pawel\AppData\Local\Temp\mc_debug_test9'

if os.path.exists(TEST_WORLD):
    shutil.rmtree(TEST_WORLD)
shutil.copytree(CLEAN_WORLD, TEST_WORLD)

world_path = os.path.join(TEST_WORLD, 'world')
backend = AnvilBackend(world_path, backup=False)

pos = Pos(0, 64, 0)
region_file = backend._get_region_file(pos.chunk_pos().region_pos())
local_x, local_z = pos.chunk_pos().local_region_pos()
region_data = backend._load_region(region_file)

# Odczytaj chunk
nbt = backend._read_chunk_nbt(region_data, local_x, local_z)
print(f'Typ nbt z _read_chunk_nbt: {type(nbt)}')
print(f'Keys: {list(nbt.keys())}')

# Opakuj w Level
nbt_wrapped = nbtlib.Compound({
    'Level': nbt,
    'DataVersion': nbtlib.Int(0)
})
print(f'\nPo opakowaniu:')
print(f'  nbt_wrapped type: {type(nbt_wrapped)}')
print(f'  nbt_wrapped["Level"] type: {type(nbt_wrapped["Level"])}')

# Dodaj sekcję
section = backend._create_section(4)
level = nbt_wrapped['Level']
print(f'  level type: {type(level)}')

# To jest problem! Jeśli nbt jest nbtlib.File, to może mieć inne zachowanie
if hasattr(level, 'keys'):
    print(f'  level keys: {list(level.keys())}')
    level['Sections'].append(section)
    print(f'  Po append: {len(level["Sections"])}')

# Serializuj
from io import BytesIO
buffer = BytesIO()
nbt_wrapped.write(buffer, byteorder='big')
nbt_bytes = buffer.getvalue()
print(f'\nSerialized: {len(nbt_bytes)} bytes')

# Deserializuj
import nbtlib
bio = BytesIO(nbt_bytes)
tag = nbtlib.tag.Compound.parse(bio)
print(f'Root keys: {list(tag.keys())}')
