import sys
sys.path.insert(0, 'src')
from schematic_to_world import SchematicLoader
from pathlib import Path

schematic = SchematicLoader(Path('output/digital_counter_v2.schematic'))

print(f'Tile entities: {len(schematic.tile_entities)}')
print(f'Offsets: ({schematic.offset_x}, {schematic.offset_y}, {schematic.offset_z})')

# Sprawdź co jest w tile_entities
for i, te in enumerate(schematic.tile_entities):
    print(f'\nTE {i}: type={type(te)}')
    if isinstance(te, tuple):
        tag_type, te_data = te
        print(f'  tag_type: {tag_type}')
        print(f'  te_data keys: {te_data.keys() if hasattr(te_data, "keys") else "N/A"}')
        
        # Sprawdź pozycję
        x = te_data.get('x')
        y = te_data.get('y')
        z = te_data.get('z')
        
        if isinstance(x, tuple): x = x[1]
        if isinstance(y, tuple): y = y[1]
        if isinstance(z, tuple): z = z[1]
        
        print(f'  Position: ({x},{y},{z})')
        
        # Sprawdź czy to dropper
        te_id = te_data.get('id')
        if isinstance(te_id, tuple): te_id = te_id[1]
        print(f'  ID: {te_id}')

# Sprawdź _get_te_pos dla pozycji (6,1,4) - dropper D0 w schematicu
print('\n\nTest _get_te_pos dla (6,1,4):')
for te in schematic.tile_entities:
    result = schematic._get_te_pos(te, 6, 1, 4)
    print(f'  Result: {result}')
