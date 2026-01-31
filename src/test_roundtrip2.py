import sys
sys.path.insert(0, '.')
from mc_editkit.world.editor import WorldEditor
from mc_editkit.world.types import Pos

world_path = r'..\headless_server\tests\headless_server\1.7.10_clean\world'
print(f'Test round-trip #2 na: {world_path}')

editor = WorldEditor(world_path, backup=False)

# Test: command block at (0, 65, 0)
pos = Pos(0, 65, 0)
print(f'Ustawiam command block na {pos}')
editor.set_command_block(pos, '/say [ROUNDTRIP] ok')

editor.commit()
editor.close()
print('Zapisano. Odczyt...')

# Odczytaj
editor2 = WorldEditor(world_path, backup=False)
block_id, meta = editor2.get_block(pos)
print(f'Odczytany blok: {block_id}:{meta} (oczekiwano 137:0)')

te = editor2.get_tile_entity(pos)
if te:
    te_id = te.get('id')
    te_cmd = te.get('Command')
    print(f'TE id: {te_id}')
    print(f'TE Command: {te_cmd}')
    if te_id == 'Control' and '[ROUNDTRIP]' in (te_cmd or ''):
        print('ROUND-TRIP #2 PASS!')
    else:
        print('ROUND-TRIP #2 TE FAIL!')
else:
    print('ROUND-TRIP #2 TE MISSING!')
editor2.close()
