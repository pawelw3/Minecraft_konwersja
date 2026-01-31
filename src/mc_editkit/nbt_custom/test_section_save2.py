import sys
sys.path.insert(0, '.')
from mc_editkit.world.backends.anvil_backend import AnvilBackend
from mc_editkit.world.types import Pos
import tempfile
import shutil
import os

world_src = r'..\headless_server\1.7.10\world'
world_copy = tempfile.mkdtemp(prefix='mc_test_')
shutil.copytree(world_src, os.path.join(world_copy, 'world'))

world_path = os.path.join(world_copy, 'world')
print(f'Test swiat: {world_path}')

backend = AnvilBackend(world_path, backup=False)

# Ustaw blok
pos = Pos(100, 200, 100)
backend.set_block(pos, 137, 0)

backend.commit()

# Sprawdź co zostało zapisane
region_file = os.path.join(world_path, 'region', 'r.0.0.mca')
with open(region_file, 'rb') as f:
    data = f.read()

# Chunk (6,6) -> Local (6,6) -> Index 6 + 6*32 = 198
idx = 6 + 6 * 32
offset = idx * 4
loc_data = data[offset:offset+4]
sector_offset = ((loc_data[0] << 16) | (loc_data[1] << 8) | loc_data[2])
print(f'Chunk sector_offset={sector_offset}')

if sector_offset > 0:
    import zlib
    from io import BytesIO
    import nbtlib
    
    chunk_offset = sector_offset * 4096
    chunk_header = data[chunk_offset:chunk_offset+5]
    length = int.from_bytes(chunk_header[:4], 'big')
    chunk_data = data[chunk_offset+5:chunk_offset+5+length-1]
    nbt_bytes = zlib.decompress(chunk_data)
    
    bio = BytesIO(nbt_bytes)
    tag = nbtlib.tag.Compound.parse(bio)
    
    # Root has empty key
    root_val = list(tag.values())[0] if tag else None
    if root_val and hasattr(root_val, 'keys'):
        level = root_val
        print(f'xPos={level.get("xPos")}, zPos={level.get("zPos")}')
        sections = level.get('Sections', [])
        print(f'Sections count={len(sections)}')
        for sec in sections:
            y = sec.get('Y')
            blocks = sec.get('Blocks', [])
            non_zero = sum(1 for b in blocks if b != 0)
            print(f'  Sec Y={y}: blocks={non_zero}')
    else:
        print('No root value')
else:
    print('ERROR: sector_offset is 0!')

print(f'Zachowano: {world_copy}')  # DEBUG: nie usuwaj
