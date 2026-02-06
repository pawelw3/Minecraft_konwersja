import json

with open('cuttable_test_patch_jvm.json', 'r') as f:
    patch = json.load(f)

print('=== WSPÓŁRZĘDNE BLOKÓW CUTTABLE ===')
print()

all_x = []
all_y = []
all_z = []

for chunk_key, chunk_data in patch['chunks'].items():
    print(f"Chunk {chunk_key}:")
    for block in chunk_data['blocks']:
        x, y, z = block['x'], block['y'], block['z']
        all_x.append(x)
        all_y.append(y)
        all_z.append(z)
        orig = block['original_block']
        cut_type = block['cut_type']
        print(f"  ({x:3}, {y:2}, {z:3}) - {orig} - {cut_type}")
    print()

print('=== ZAKRES ===')
print(f"X: {min(all_x)} do {max(all_x)}")
print(f"Y: {min(all_y)} do {max(all_y)}")
print(f"Z: {min(all_z)} do {max(all_z)}")
print()
print('Spawn: (0, 64, 0) - srodek obszaru testowego')
