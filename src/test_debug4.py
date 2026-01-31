import sys
sys.path.insert(0, '.')
from mc_editkit.world.backends.anvil_backend import AnvilBackend
from mc_editkit.world.types import Pos
import shutil
import os
import zlib
import struct
from io import BytesIO
import nbtlib

CLEAN_WORLD = r'..\headless_server\tests\headless_server\1.7.10_clean'
TEST_WORLD = r'C:\Users\pawel\AppData\Local\Temp\mc_debug_test3'

if os.path.exists(TEST_WORLD):
    shutil.rmtree(TEST_WORLD)
shutil.copytree(CLEAN_WORLD, TEST_WORLD)

world_path = os.path.join(TEST_WORLD, 'world')
backend = AnvilBackend(world_path, backup=False)

pos = Pos(0, 64, 0)
backend.set_block(pos, 1, 0)

# Sprawdź co jest w region_data przed commitem
region_file = backend._get_region_file(pos.chunk_pos().region_pos())
region_data = backend._region_cache[region_file]

print(f'Region data size: {len(region_data)}')

# Sprawdź nagłówek chunka (0,0)
idx = 0 + 0 * 32
offset = idx * 4
loc_data = region_data[offset:offset+4]
sector_offset = ((loc_data[0] << 16) | (loc_data[1] << 8) | loc_data[2])
sector_count = loc_data[3]
print(f'Header: sector_offset={sector_offset}, sector_count={sector_count}')

if sector_offset > 0:
    chunk_offset = sector_offset * 4096
    chunk_header = region_data[chunk_offset:chunk_offset+5]
    length = int.from_bytes(chunk_header[:4], 'big')
    compression = chunk_header[4]
    print(f'Chunk: length={length}, compression={compression}')

# Sprawdźmy czy commit działa
print('Calling commit...')
backend.commit()

# Sprawdź po commitcie
print('\nPo commitcie:')
with open(region_file, 'rb') as f:
    data = f.read()
print(f'File size: {len(data)}')

# Sprawdź nagłówek
loc_data = data[offset:offset+4]
sector_offset = ((loc_data[0] << 16) | (loc_data[1] << 8) | loc_data[2])
sector_count = loc_data[3]
print(f'Header: sector_offset={sector_offset}, sector_count={sector_count}')

if sector_offset > 0:
    chunk_offset = sector_offset * 4096
    chunk_header = data[chunk_offset:chunk_offset+5]
    length = int.from_bytes(chunk_header[:4], 'big')
    compression = chunk_header[4]
    print(f'Chunk: length={length}, compression={compression}')
    
    if length > 1:
        chunk_data = data[chunk_offset+5:chunk_offset+5+length-1]
        try:
            nbt_bytes = zlib.decompress(chunk_data)
            print(f'Decompressed: {len(nbt_bytes)} bytes')
            
            bio = BytesIO(nbt_bytes)
            tag = nbtlib.tag.Compound.parse(bio)
            
            level = tag['Level'] if 'Level' in tag else tag
            sections = level.get('Sections', [])
            print(f'Sections: {len(sections)}')
        except Exception as e:
            print(f'Error: {e}')
