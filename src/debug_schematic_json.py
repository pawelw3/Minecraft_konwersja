import json

with open('test_scenarios/digital_counter_vanilla/schematics/voxel_grid.json') as f:
    data = json.load(f)

print('Kluczowe bloki i ich współrzędne w schematicu:')
print('='*60)

for section_name, section_data in data['sections'].items():
    print(f'\nSekcja: {section_name}')
    for v in section_data.get('voxels', []):
        purpose = v.get('purpose', '')
        if any(x in purpose for x in ['support', 'D0', 'D1', 'C0', 'CMD0', 'clock_out', 'master_switch', 'clock_delay']):
            block_name = v['block'].split(':')[-1]
            print(f'  ({v["x"]}, {v["y"]}, {v["z"]}): {block_name} - {purpose}')

print('\n\nPrzesunięcie do świata (target_y=60):')
print('y_schematic + 60 = y_world')
