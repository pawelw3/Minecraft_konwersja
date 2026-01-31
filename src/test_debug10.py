import sys
sys.path.insert(0, '.')
from mc_editkit.world.backends.anvil_backend import AnvilBackend
from mc_editkit.world.types import Pos
import shutil
import os
import zlib
from io import BytesIO
import nbtlib

CLEAN_WORLD = r'..\headless_server\tests\headless_server\1.7.10_clean'
TEST_WORLD = r'C:\Users\pawel\AppData\Local\Temp\mc_debug_test8'

if os.path.exists(TEST_WORLD):
    shutil.rmtree(TEST_WORLD)
shutil.copytree(CLEAN_WORLD, TEST_WORLD)

world_path = os.path.join(TEST_WORLD, 'world')
backend = AnvilBackend(world_path, backup=False)

pos = Pos(0, 64, 0)
region_file = backend._get_region_file(pos.chunk_pos().region_pos())
local_x, local_z = pos.chunk_pos().local_region_pos()
region_data = backend._load_region(region_file)

# Pobierz chunk
nbt = backend._get_or_create_chunk(region_file, local_x, local_z)
print('Po _get_or_create_chunk:')
print(f'  nbt type: {type(nbt)}')
print(f'  nbt keys: {list(nbt.keys())}')

# Modyfikuj jak w set_block
section_y = pos.section_y()
section = backend._get_section(nbt, section_y)

if section is None:
    section = backend._create_section(section_y)
    level = backend._get_level(nbt)
    level['Sections'].append(section)
    print(f'\nDodano sekcję Y={section_y}')

print('Po dodaniu sekcji:')
print(f'  nbt keys: {list(nbt.keys())}')
print(f'  Level["Sections"]: {len(backend._get_level(nbt).get("Sections", []))}')

# Zapisz
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
