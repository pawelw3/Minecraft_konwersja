import sys
sys.path.insert(0, '.')
from mc_editkit.world.backends.anvil_backend import AnvilBackend
from mc_editkit.world.types import Pos
import shutil
import os

CLEAN_WORLD = r'..\headless_server\tests\headless_server\1.7.10_clean'
TEST_WORLD = r'C:\Users\pawel\AppData\Local\Temp\mc_debug_test'

if os.path.exists(TEST_WORLD):
    shutil.rmtree(TEST_WORLD)
shutil.copytree(CLEAN_WORLD, TEST_WORLD)

world_path = os.path.join(TEST_WORLD, 'world')
backend = AnvilBackend(world_path, backup=False)

pos = Pos(0, 64, 0)
print(f'Ustawiam stone na {pos}')
print(f'  chunk_pos: {pos.chunk_pos()}')
print(f'  region_pos: {pos.chunk_pos().region_pos()}')
print(f'  local_region: {pos.chunk_pos().local_region_pos()}')

backend.set_block(pos, 1, 0)

print(f'Modified regions: {backend._modified_regions}')
print(f'Region cache keys: {list(backend._region_cache.keys())}')

backend.commit()
print('Commit zakończony')
