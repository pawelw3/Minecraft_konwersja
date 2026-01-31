import sys
sys.path.insert(0, '.')
from mc_editkit.world.backends.anvil_backend import AnvilBackend
from mc_editkit.world.types import Pos
import shutil
import os

CLEAN_WORLD = r'..\headless_server\tests\headless_server\1.7.10_clean'
TEST_WORLD = r'C:\Users\pawel\AppData\Local\Temp\mc_debug_test6'

if os.path.exists(TEST_WORLD):
    shutil.rmtree(TEST_WORLD)
shutil.copytree(CLEAN_WORLD, TEST_WORLD)

world_path = os.path.join(TEST_WORLD, 'world')
backend = AnvilBackend(world_path, backup=False)

pos = Pos(0, 64, 0)
region_file = backend._get_region_file(pos.chunk_pos().region_pos())
local_x, local_z = pos.chunk_pos().local_region_pos()

region_data = backend._load_region(region_file)
nbt_before = backend._read_chunk_nbt(region_data, local_x, local_z)

print('PRZED _get_or_create_chunk:')
print(f'  Keys: {list(nbt_before.keys())}')
if 'Level' in nbt_before:
    print(f'  Level type: {type(nbt_before["Level"])}')
    print(f'  Level keys: {list(nbt_before["Level"].keys()) if hasattr(nbt_before["Level"], "keys") else "N/A"}')

# Teraz wywołaj _get_or_create_chunk
nbt_after = backend._get_or_create_chunk(region_file, local_x, local_z)

print('\nPO _get_or_create_chunk:')
print(f'  Keys: {list(nbt_after.keys())}')
if 'Level' in nbt_after:
    print(f'  Level type: {type(nbt_after["Level"])}')
    print(f'  Level keys: {list(nbt_after["Level"].keys()) if hasattr(nbt_after["Level"], "keys") else "N/A"}')
