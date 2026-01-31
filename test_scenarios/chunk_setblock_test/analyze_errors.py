import json
with open('chunk_test_report.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# Sprawdź unikalne odpowiedzi
responses = {}
for chunk in data['chunks']:
    resp = chunk.get('response', '')
    if resp not in responses:
        responses[resp] = 0
    responses[resp] += 1

print('UNIKALNE ODPOWIEDZI SERWERA:')
for resp, count in sorted(responses.items(), key=lambda x: -x[1]):
    print(f'  "{resp}": {count} razy')

# Sprawdź błędy poza światem
outside_world = [c for c in data['chunks'] if 'outside of the world' in c.get('response', '')]
print()
print(f'Liczba prób poza światem: {len(outside_world)}')
if outside_world:
    print('Przykładowe pozycje poza światem:')
    for ex in outside_world[:5]:
        print(f'  {ex["position"]} w chunk ({ex["chunk_x"]}, {ex["chunk_z"]})')

# Sprawdź gdzie był sukces
placed = [c for c in data['chunks'] if c['status'] == 'BLOCK_PLACED']
print()
print(f'Sukcesy (block placed): {len(placed)}')
if placed:
    print('Zakresy chunków ze sukcesem:')
    x_coords = [c['chunk_x'] for c in placed]
    z_coords = [c['chunk_z'] for c in placed]
    print(f'  X: {min(x_coords)} do {max(x_coords)}')
    print(f'  Z: {min(z_coords)} do {max(z_coords)}')
