import sys
sys.path.insert(0, '.')
from mc_editkit.world.backends.anvil_backend import AnvilBackend
from mc_editkit.world.types import Pos
import shutil
import os

CLEAN_WORLD = r'..\headless_server\tests\headless_server\1.7.10_clean'
TEST_WORLD = r'C:\Users\pawel\AppData\Local\Temp\mc_debug_test4'

if os.path.exists(TEST_WORLD):
    shutil.rmtree(TEST_WORLD)
shutil.copytree(CLEAN_WORLD, TEST_WORLD)

world_path = os.path.join(TEST_WORLD, 'world')
backend = AnvilBackend(world_path, backup=False)

pos = Pos(0, 64, 0)
backend.set_block(pos, 1, 0)

region_file = backend._get_region_file(pos.chunk_pos().region_pos())

# Sprawdź czy to ten sam obiekt
region_data_from_cache = backend._region_cache[region_file]
print(f'Cache id: {id(region_data_from_cache)}')

# Sprawdź nagłówek przed zapisem
idx = 0
offset = idx * 4
loc_data = region_data_from_cache[offset:offset+4]
sector_offset = ((loc_data[0] << 16) | (loc_data[1] << 8) | loc_data[2])
print(f'Przed zapisem: sector_offset={sector_offset}')

# Zapisz ręcznie
with open(region_file, 'wb') as f:
    f.write(region_data_from_cache)

# Sprawdź co zostało zapisane
with open(region_file, 'rb') as f:
    data_after = f.read()

print(f'File id: {id(data_after)}')
print(f'Same data? {data_after == bytes(region_data_from_cache)}')

# Sprawdź nagłówek po zapisie
loc_data2 = data_after[offset:offset+4]
sector_offset2 = ((loc_data2[0] << 16) | (loc_data2[1] << 8) | loc_data2[2])
print(f'Po zapisie: sector_offset={sector_offset2}')
