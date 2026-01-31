import sys
sys.path.insert(0, 'src')
from schematic_to_world import SchematicLoader, BlockData, create_chunk_nbt
from pathlib import Path

schematic = SchematicLoader(Path('output/digital_counter_v2.schematic'))

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

# Policz bloki z TE
te_count = sum(1 for b in chunk_blocks.values() if b.tile_entity)
print(f'Bloki z TE: {te_count}')

# Sprawdź konkretnie dropper na (6,61,8)
block = chunk_blocks.get((6, 61, 8))
if block:
    print(f'Block at (6,61,8): ID={block.block_id}, TE={block.tile_entity}')
    if block.tile_entity:
        print(f'  TE type: {type(block.tile_entity)}')
else:
    print('No block at (6,61,8)')

# Stwórz chunk NBT
chunk_nbt = create_chunk_nbt(chunk_blocks, 0, 0)
print(f'Chunk NBT created: {len(chunk_nbt)} bytes')
