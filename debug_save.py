import sys
import zlib
sys.path.insert(0, 'src')
from schematic_to_world import SchematicLoader, BlockData, create_chunk_nbt, MCRegionWriter
from minecraft_map_parser.nbt_parser import NBTParser
from pathlib import Path

# Wczytaj schematic
schematic = SchematicLoader(Path('output/digital_counter_v2.schematic'))

# Zbuduj słownik bloków
chunk_blocks = {}
target_x, target_y, target_z = 0, 60, 0

for sy in range(schematic.height):
    for sz in range(schematic.length):
        for sx in range(schematic.width):
            block = schematic.get_block(sx, sy, sz)
            
            if block.block_id == 0:
                continue
            
            world_x = target_x + sx + schematic.offset_x
            world_y = target_y + sy + schematic.offset_y
            world_z = target_z + sz + schematic.offset_z
            
            chunk_blocks[(world_x, world_y, world_z)] = block

# Stwórz NBT chunka
chunk_nbt = create_chunk_nbt(chunk_blocks, 0, 0)

# Zapisz do pliku testowego
region_file = Path('output/test_region.mca')
region_writer = MCRegionWriter(region_file)
region_writer.set_chunk(0, 0, chunk_nbt)
region_writer.save()

print(f'Zapisano region do: {region_file}')

# Odczytaj z powrotem i sprawdź
with open(region_file, 'rb') as f:
    header = f.read(4096)
    offset = ((header[0] << 16) | (header[1] << 8) | header[2]) * 4096
    f.seek(offset)
    import struct
    length = struct.unpack('>I', f.read(4))[0]
    f.read(1)  # comp type
    data = zlib.decompress(f.read(length - 1))

parser = NBTParser(data)
chunk = parser.parse()

level = chunk.value['Level']
sections = level.value['Sections']

# Znajdź sekcję Y=3
for sec in sections.value:
    if isinstance(sec, tuple):
        _, sec = sec
    y_val = sec.get('Y')
    if isinstance(y_val, tuple):
        y_val = y_val[1]
    elif hasattr(y_val, 'value'):
        y_val = y_val.value
    
    if y_val == 3:
        blocks = sec.get('Blocks')
        if isinstance(blocks, tuple):
            blocks = blocks[1]
        elif hasattr(blocks, 'value'):
            blocks = blocks.value
        
        print(f'Sekcja Y=3 po zapisie/odczycie:')
        print(f'  [3204] = {blocks[3204]}')
        print(f'  [3205] = {blocks[3205]}')
        print(f'  [3206] = {blocks[3206]}')
        print(f'  [3207] = {blocks[3207]}')
        
        stone_count = sum(1 for b in blocks if b == 1)
        print(f'  Stone count: {stone_count}')
        break
