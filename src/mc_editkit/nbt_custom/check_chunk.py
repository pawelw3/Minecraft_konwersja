import sys
sys.path.insert(0, '.')
import zlib

region_file = r'C:\Users\pawel\AppData\Local\Temp\mc_server_spiral\world\region\r.-2.0.mca'

with open(region_file, 'rb') as f:
    data = f.read()

chunk_offset = 38 * 4096
chunk_header = data[chunk_offset:chunk_offset+5]
length = int.from_bytes(chunk_header[:4], 'big')

chunk_data = data[chunk_offset+5:chunk_offset+5+length]
nbt_bytes = zlib.decompress(chunk_data)

import nbtlib
from nbtlib import parse
from io import BytesIO

bio = BytesIO(nbt_bytes)
tag = parse(bio, byteorder='big')

print(f'Tag type: {type(tag)}')
print(f'Keys: {list(tag.keys())}')

if 'Level' in tag:
    level = tag['Level']
    print(f'Level keys: {list(level.keys())}')
    xpos = level.get('xPos')
    zpos = level.get('zPos')
    print(f'xPos: {xpos}, zPos: {zpos}')
    sections = level.get('Sections', [])
    print(f'Sections count: {len(sections)}')
    
    if sections:
        sec0 = sections[0]
        print(f'Section[0] Y: {sec0.get("Y")}')
        print(f'Section[0] keys: {list(sec0.keys())}')
        
        # Check blocks
        blocks = sec0.get('Blocks')
        if blocks:
            print(f'Blocks len: {len(blocks)}')
            # Count non-zero
            non_zero = sum(1 for b in blocks if b != 0)
            print(f'Non-zero blocks: {non_zero}')
            print(f'First 20 blocks: {list(blocks[:20])}')
        
        # Check TileEntities
        tes = level.get('TileEntities', [])
        print(f'TileEntities count: {len(tes)}')
        for te in tes[:3]:
            print(f'  TE: {te.get("id")} at ({te.get("x")},{te.get("y")},{te.get("z")})')
