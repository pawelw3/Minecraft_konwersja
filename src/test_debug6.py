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
TEST_WORLD = r'C:\Users\pawel\AppData\Local\Temp\mc_debug_test5'

if os.path.exists(TEST_WORLD):
    shutil.rmtree(TEST_WORLD)
shutil.copytree(CLEAN_WORLD, TEST_WORLD)

world_path = os.path.join(TEST_WORLD, 'world')
backend = AnvilBackend(world_path, backup=False)

pos = Pos(0, 64, 0)
backend.set_block(pos, 1, 0)

region_file = backend._get_region_file(pos.chunk_pos().region_pos())

# Sprawdź chunk w pamięci PRZED commitem
local_x, local_z = 0, 0
nbt_before = backend._get_or_create_chunk(region_file, local_x, local_z)
level_before = nbt_before['Level'] if 'Level' in nbt_before else nbt_before
sections_before = level_before.get('Sections', [])
print(f'PRZED commit: Sections={len(sections_before)}')
for sec in sections_before:
    y = sec.get('Y')
    blocks = sec.get('Blocks', [])
    non_zero = sum(1 for b in blocks if b != 0)
    print(f'  Y={y}: non_zero={non_zero}')

# Commit
backend.commit()

# Sprawdź chunk w pliku PO commitcie (bezpośrednio, bez _read_chunk_nbt)
with open(region_file, 'rb') as f:
    data = f.read()

idx = local_x + local_z * 32
offset = idx * 4
loc_data = data[offset:offset+4]
sector_offset = ((loc_data[0] << 16) | (loc_data[1] << 8) | loc_data[2])
print(f'\nPO commit: sector_offset={sector_offset}')

chunk_offset = sector_offset * 4096
chunk_header = data[chunk_offset:chunk_offset+5]
length = int.from_bytes(chunk_header[:4], 'big')
compression = chunk_header[4]
print(f'length={length}, compression={compression}')

if length > 1:
    chunk_data = data[chunk_offset+5:chunk_offset+5+length-1]
    nbt_bytes = zlib.decompress(chunk_data)
    print(f'nbt_bytes={len(nbt_bytes)}')
    
    # Parsuj
    bio = BytesIO(nbt_bytes)
    tag = nbtlib.tag.Compound.parse(bio)
    
    print(f'Root keys: {list(tag.keys())}')
    
    level = tag['Level'] if 'Level' in tag else tag
    print(f'Level keys: {list(level.keys())}')
    
    sections = level.get('Sections', [])
    print(f'Sections={len(sections)}')
    for sec in sections:
        y = sec.get('Y')
        blocks = sec.get('Blocks', [])
        non_zero = sum(1 for b in blocks if b != 0)
        print(f'  Y={y}: non_zero={non_zero}')
