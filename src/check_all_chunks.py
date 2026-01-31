import sys
sys.path.insert(0, '.')
import zlib
from io import BytesIO
import nbtlib
import os

region_file = r'C:\Users\pawel\AppData\Local\Temp\mc_spiral_r1_test\world\region\r.0.0.mca'
with open(region_file, 'rb') as f:
    data = f.read()

print(f'Region size: {len(data)} bytes')

for idx in range(32*32):
    offset = idx * 4
    loc_data = data[offset:offset+4]
    sector_offset = ((loc_data[0] << 16) | (loc_data[1] << 8) | loc_data[2])
    sector_count = loc_data[3]
    
    if sector_offset > 0:
        lz = idx // 32
        lx = idx % 32
        
        chunk_offset = sector_offset * 4096
        if chunk_offset + 5 > len(data):
            continue
            
        chunk_header = data[chunk_offset:chunk_offset+5]
        length = int.from_bytes(chunk_header[:4], 'big')
        
        if length < 1 or chunk_offset + 5 + length - 1 > len(data):
            continue
        
        try:
            chunk_data = data[chunk_offset+5:chunk_offset+5+length-1]
            nbt_bytes = zlib.decompress(chunk_data)
            
            bio = BytesIO(nbt_bytes)
            tag = nbtlib.tag.Compound.parse(bio)
            
            level = tag['Level'] if 'Level' in tag else tag
            
            # Count non-zero blocks
            total_blocks = 0
            sections = level.get('Sections', [])
            for sec in sections:
                blocks = sec.get('Blocks', [])
                total_blocks += sum(1 for b in blocks if b != 0)
            
            tes = level.get('TileEntities', [])
            
            if total_blocks > 0 or len(tes) > 0:
                print(f'Chunk [{lx},{lz}]: blocks={total_blocks}, TE={len(tes)}')
        except:
            pass
