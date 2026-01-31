import sys
sys.path.insert(0, 'src')
from schematic_to_world import SchematicLoader, BlockData, create_chunk_nbt
from pathlib import Path

# Wczytaj schematic
schematic = SchematicLoader(Path('output/digital_counter_v2.schematic'))

# Zbuduj słownik bloków tak jak w insert_schematic_into_world
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

print(f'Bloki w chunk_blocks: {len(chunk_blocks)}')

# Sprawdź czy (5,60,8) i (6,60,8) są
print(f'(5,60,8): {chunk_blocks.get((5,60,8), None)}')
print(f'(6,60,8): {chunk_blocks.get((6,60,8), None)}')

# Stwórz NBT chunka
chunk_nbt = create_chunk_nbt(chunk_blocks, 0, 0)
print(f'Chunk NBT size: {len(chunk_nbt)} bytes')

# Parsuj z powrotem i sprawdź
from minecraft_map_parser.nbt_parser import NBTParser
parser = NBTParser(chunk_nbt)
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
        
        # Sprawdź indeksy 3205 i 3206
        print(f'Sekcja Y=3:')
        print(f'  [3204] = {blocks[3204]}')
        print(f'  [3205] = {blocks[3205]}')
        print(f'  [3206] = {blocks[3206]}')
        print(f'  [3207] = {blocks[3207]}')
        
        # Policz stone
        stone_count = sum(1 for b in blocks if b == 1)
        print(f'  Stone count: {stone_count}')
        break
