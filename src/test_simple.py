import sys
sys.path.insert(0, '.')
from mc_editkit.world.editor import WorldEditor
from mc_editkit.world.types import Pos
import shutil
import os

CLEAN_WORLD = r'..\headless_server\tests\headless_server\1.7.10_clean'
TEST_WORLD = r'C:\Users\pawel\AppData\Local\Temp\mc_simple_test'

# Skopiuj świat
if os.path.exists(TEST_WORLD):
    shutil.rmtree(TEST_WORLD)
shutil.copytree(CLEAN_WORLD, TEST_WORLD)

world_path = os.path.join(TEST_WORLD, 'world')
editor = WorldEditor(world_path, backup=False)

# Ustaw stone na (0,64,0)
pos = Pos(0, 64, 0)
print(f'Ustawiam stone na {pos}')
editor.set_block(pos, 1, 0)

# Ustaw command block na (0,65,0)
pos2 = Pos(0, 65, 0)
print(f'Ustawiam command block na {pos2}')
editor.set_command_block(pos2, '/say TEST')

editor.commit()
editor.close()

# Sprawdź
import zlib
from io import BytesIO
import nbtlib

region_file = os.path.join(TEST_WORLD, 'world', 'region', 'r.0.0.mca')
with open(region_file, 'rb') as f:
    data = f.read()

print(f'Region size: {len(data)}')

# Chunk (0,0) -> idx 0
idx = 0
offset = idx * 4
loc_data = data[offset:offset+4]
sector_offset = ((loc_data[0] << 16) | (loc_data[1] << 8) | loc_data[2])
print(f'Chunk (0,0) sector_offset: {sector_offset}')

if sector_offset > 0:
    chunk_offset = sector_offset * 4096
    chunk_header = data[chunk_offset:chunk_offset+5]
    length = int.from_bytes(chunk_header[:4], 'big')
    chunk_data = data[chunk_offset+5:chunk_offset+5+length-1]
    nbt_bytes = zlib.decompress(chunk_data)
    
    bio = BytesIO(nbt_bytes)
    tag = nbtlib.tag.Compound.parse(bio)
    
    level = tag['Level'] if 'Level' in tag else tag
    
    sections = level.get('Sections', [])
    print(f'Sections: {len(sections)}')
    
    for sec in sections:
        y = sec.get('Y')
        blocks = sec.get('Blocks', [])
        non_zero = sum(1 for b in blocks if b != 0)
        if non_zero > 0:
            print(f'  Y={y}: non_zero={non_zero}')
    
    tes = level.get('TileEntities', [])
    print(f'TileEntities: {len(tes)}')
    for te in tes:
        print(f'  {te.get("id")} at ({te.get("x")},{te.get("y")},{te.get("z")})')
