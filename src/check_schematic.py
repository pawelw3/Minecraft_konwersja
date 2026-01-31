import gzip
from pathlib import Path
import sys
sys.path.insert(0, 'src')
from minecraft_map_parser.nbt_parser import NBTParser

with open('output/digital_counter.schematic', 'rb') as f:
    data = gzip.decompress(f.read())

parser = NBTParser(data)
schem = parser.parse()

print(f"Width: {schem.value['Width'].value}")
print(f"Height: {schem.value['Height'].value}")
print(f"Length: {schem.value['Length'].value}")

blocks = schem.value['Blocks'].value
data_arr = schem.value['Data'].value

print(f"Blocks array size: {len(blocks)}")
print(f"Data array size: {len(data_arr)}")

# Check non-air blocks in the schematic
print("Non-air blocks in schematic:")
width = schem.value['Width'].value
height = schem.value['Height'].value
length = schem.value['Length'].value

count = 0
for y in range(height):
    for z in range(length):
        for x in range(width):
            idx = y * width * length + z * width + x
            if blocks[idx] != 0:
                print(f"  ({x},{y},{z}): {blocks[idx]}")
                count += 1
                if count > 30:
                    print("  ... (truncated)")
                    break
        if count > 30:
            break
    if count > 30:
        break

print(f"\nTotal non-air blocks: {sum(1 for b in blocks if b != 0)}")
