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
print(f'Ustawiam blok na pozycji: {pos}')
print(f'  -> chunk: {pos.chunk_pos()}')
print(f'  -> section_y: {pos.section_y()}')
print(f'  -> local_chunk: {pos.local_chunk_pos()}')

backend.set_block(pos, 137, 0)

print(f'Modified regions: {backend._modified_regions}')

backend.commit()

print('Zapisano. Sprawdzam...')

# Sprawdź ponownie
backend2 = AnvilBackend(world_path, backup=False)
block_id, meta = backend2.get_block(pos)
print(f'Odczytany blok: {block_id}:{meta} (oczekiwano 137:0)')

if block_id == 137:
    print('SUCCESS!')
else:
    print('FAIL!')
    print('  Chunk pos:', pos.chunk_pos())
    region_pos = pos.chunk_pos().region_pos()
    print('  Region pos:', region_pos)
    region_file = os.path.join(world_path, 'region', f'r.{region_pos.x}.{region_pos.z}.mca')
    print(f'  Region file exists: {os.path.exists(region_file)}')

print(f'Zachowano: {world_copy}')
