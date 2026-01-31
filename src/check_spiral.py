import sys
sys.path.insert(0, '.')
import zlib
from io import BytesIO
import nbtlib

region_file = r'C:\Users\pawel\AppData\Local\Temp\mc_spiral_r1_test\world\region\r.0.0.mca'
with open(region_file, 'rb') as f:
    data = f.read()

idx = 0 + 0 * 32
offset = idx * 4
loc_data = data[offset:offset+4]
sector_offset = ((loc_data[0] << 16) | (loc_data[1] << 8) | loc_data[2])

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
    print('Sections:', len(sections))
    for sec in sections:
        y = sec.get('Y')
        blocks = sec.get('Blocks', [])
        non_zero = sum(1 for b in blocks if b != 0)
        if non_zero > 0:
            print(f'  Y={y}: non_zero={non_zero}')
    
    tes = level.get('TileEntities', [])
    print('TileEntities:', len(tes))
    for te in tes:
        te_id = te.get('id')
        x, y, z = te.get('x'), te.get('y'), te.get('z')
        cmd = te.get('Command', '')
        print(f'  {te_id} at ({x},{y},{z}): {cmd[:40]}')
