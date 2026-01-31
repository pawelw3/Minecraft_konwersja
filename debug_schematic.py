import gzip
import sys
sys.path.insert(0, 'src')
from minecraft_map_parser.nbt_parser import NBTParser

with open('output/digital_counter_v2.schematic', 'rb') as f:
    data = gzip.decompress(f.read())

parser = NBTParser(data)
schem = parser.parse()

blocks = schem.value['Blocks'].value
width = schem.value['Width'].value
height = schem.value['Height'].value
length = schem.value['Length'].value

offset_x = schem.value.get('WEOffsetX', 0)
offset_y = schem.value.get('WEOffsetY', 0)
offset_z = schem.value.get('WEOffsetZ', 0)
if hasattr(offset_x, 'value'): offset_x = offset_x.value
if hasattr(offset_y, 'value'): offset_y = offset_y.value
if hasattr(offset_z, 'value'): offset_z = offset_z.value

target_x, target_y, target_z = 0, 60, 0

chunk_blocks = {}

for sy in range(height):
    for sz in range(length):
        for sx in range(width):
            idx = sy * width * length + sz * width + sx
            block_id = blocks[idx] & 0xFF
            
            if block_id == 0:
                continue
            
            world_x = target_x + sx + offset_x
            world_y = target_y + sy + offset_y
            world_z = target_z + sz + offset_z
            
            chunk_x = world_x // 16
            chunk_z = world_z // 16
            
            if (chunk_x, chunk_z) not in chunk_blocks:
                chunk_blocks[(chunk_x, chunk_z)] = {}
            
            chunk_blocks[(chunk_x, chunk_z)][(world_x, world_y, world_z)] = block_id

print(f'Bloki w chunkach: {len(chunk_blocks)}')
for (cx, cz), blocks_dict in chunk_blocks.items():
    print(f'  Chunk ({cx},{cz}): {len(blocks_dict)} blokow')

c0 = chunk_blocks[(0, 0)]
pos1 = (5, 60, 8)
pos2 = (6, 60, 8)
print(f'(5,60,8) w slowniku: {pos1 in c0} -> {c0.get(pos1, "BRAK")}')
print(f'(6,60,8) w slowniku: {pos2 in c0} -> {c0.get(pos2, "BRAK")}')

stones = [pos for pos, bid in c0.items() if bid == 1]
print(f'Stone w chunk (0,0): {len(stones)}')
