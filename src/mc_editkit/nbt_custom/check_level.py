import zlib
from io import BytesIO
import nbtlib

region_file = r'C:\Users\pawel\AppData\Local\Temp\mc_test_988e5x6j\world\region\r.0.0.mca'
with open(region_file, 'rb') as f:
    data = f.read()

idx = 6 + 6 * 32
offset = idx * 4
loc_data = data[offset:offset+4]
sector_offset = ((loc_data[0] << 16) | (loc_data[1] << 8) | loc_data[2])

chunk_offset = sector_offset * 4096
chunk_header = data[chunk_offset:chunk_offset+5]
length = int.from_bytes(chunk_header[:4], 'big')
chunk_data = data[chunk_offset+5:chunk_offset+5+length-1]
nbt_bytes = zlib.decompress(chunk_data)

bio = BytesIO(nbt_bytes)
tag = nbtlib.tag.Compound.parse(bio)

level = tag['']['Level']
print(f'xPos={level.get("xPos")}, zPos={level.get("zPos")}')
print(f'LastUpdate={level.get("LastUpdate")}')

sections = level.get('Sections', [])
print(f'Sections: {len(sections)}')

for sec in sections:
    y = sec.get('Y')
    blocks = sec.get('Blocks', [])
    non_zero = sum(1 for b in blocks if b != 0)
    print(f'  Y={y}: non_zero={non_zero}')

# Check TileEntities
tes = level.get('TileEntities', [])
print(f'TileEntities: {len(tes)}')
for te in tes:
    print(f'  {te.get("id")} at ({te.get("x")},{te.get("y")},{te.get("z")})')
