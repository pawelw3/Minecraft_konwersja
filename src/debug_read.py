import sys
sys.path.insert(0, '.')
from mc_editkit.world.backends.anvil_backend import AnvilBackend
from mc_editkit.world.types import Pos

world_path = r'..\headless_server\tests\headless_server\1.7.10_clean\world'
backend = AnvilBackend(world_path, backup=False)

pos = Pos(0, 64, 0)
chunk_pos = pos.chunk_pos()
region_pos = chunk_pos.region_pos()
region_file = backend._get_region_file(region_pos)
local_x, local_z = chunk_pos.local_region_pos()

region_data = backend._load_region(region_file)
nbt = backend._read_chunk_nbt(region_data, local_x, local_z)

print(f'NBT type: {type(nbt)}')
print(f'NBT keys: {list(nbt.keys())}')

level = nbt.get('Level')
print(f'Level from nbt.get: {type(level)}')

empty_key = ''
if empty_key in nbt:
    print(f'Empty key present: {type(nbt[empty_key])}')
    print(f'Empty key keys: {list(nbt[empty_key].keys())}')
else:
    print('Empty key NOT present')
