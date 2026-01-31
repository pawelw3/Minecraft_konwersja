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
TEST_WORLD = r'C:\Users\pawel\AppData\Local\Temp\mc_debug_test7'

if os.path.exists(TEST_WORLD):
    shutil.rmtree(TEST_WORLD)
shutil.copytree(CLEAN_WORLD, TEST_WORLD)

world_path = os.path.join(TEST_WORLD, 'world')
backend = AnvilBackend(world_path, backup=False)

pos = Pos(0, 64, 0)
backend.set_block(pos, 1, 0)

region_file = backend._get_region_file(pos.chunk_pos().region_pos())
local_x, local_z = pos.chunk_pos().local_region_pos()

# Sprawdź nbt przed zapisem
region_data = backend._region_cache[region_file]
nbt = backend._get_or_create_chunk(region_file, local_x, local_z)

print('Przed _write_chunk_nbt:')
print(f'  nbt keys: {list(nbt.keys())}')
print(f'  nbt["Level"] keys: {list(nbt["Level"].keys()) if "Level" in nbt else "N/A"}')

# Zapisz
backend._write_chunk_nbt(region_data, local_x, local_z, nbt)

# Sprawdź co zostało zapisane w region_data
idx = local_x + local_z * 32
offset = idx * 4
loc_data = region_data[offset:offset+4]
sector_offset = ((loc_data[0] << 16) | (loc_data[1] << 8) | loc_data[2])

chunk_offset = sector_offset * 4096
chunk_header = region_data[chunk_offset:chunk_offset+5]
length = int.from_bytes(chunk_header[:4], 'big')
chunk_data = region_data[chunk_offset+5:chunk_offset+5+length-1]
nbt_bytes = zlib.decompress(chunk_data)

bio = BytesIO(nbt_bytes)
tag = nbtlib.tag.Compound.parse(bio)

print('\nPo zapisie (z region_data):')
print(f'  Root keys: {list(tag.keys())}')
if 'Level' in tag:
    print(f'  Level keys: {list(tag["Level"].keys())}')
    sections = tag['Level'].get('Sections', [])
    print(f'  Sections: {len(sections)}')
    for sec in sections:
        y = sec.get('Y')
        blocks = sec.get('Blocks', [])
        non_zero = sum(1 for b in blocks if b != 0)
        if non_zero > 0:
            print(f'    Y={y}: non_zero={non_zero}')
