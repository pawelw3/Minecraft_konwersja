import json
import math

with open('chunk_test_report.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# Spawn location (from level.dat)
SPAWN_X, SPAWN_Y, SPAWN_Z = 689, 4, -164
SPAWN_CHUNK_X = SPAWN_X // 16  # 43
SPAWN_CHUNK_Z = SPAWN_Z // 16  # -11 (rounds toward -inf)

print('=' * 80)
print('ANALIZA ODGŁEGŁOŚCI OD SPAWNu')
print('=' * 80)
print(f'Pozycja spawnu: ({SPAWN_X}, {SPAWN_Y}, {SPAWN_Z})')
print(f'Chunk spawnu: ({SPAWN_CHUNK_X}, {SPAWN_CHUNK_Z})')
print()

# Analizuj wszystkie chunki
results_by_distance = {
    '0-5': {'total': 0, 'placed': 0, 'cannot': 0},
    '5-10': {'total': 0, 'placed': 0, 'cannot': 0},
    '10-20': {'total': 0, 'placed': 0, 'cannot': 0},
    '20-50': {'total': 0, 'placed': 0, 'cannot': 0},
    '50+': {'total': 0, 'placed': 0, 'cannot': 0},
}

for chunk in data['chunks']:
    chunk_x = chunk['chunk_x']
    chunk_z = chunk['chunk_z']
    
    # Oblicz odległość euklidesową w chunkach
    dist = math.sqrt((chunk_x - SPAWN_CHUNK_X)**2 + (chunk_z - SPAWN_CHUNK_Z)**2)
    
    # Klasyfikuj
    if dist <= 5:
        key = '0-5'
    elif dist <= 10:
        key = '5-10'
    elif dist <= 20:
        key = '10-20'
    elif dist <= 50:
        key = '20-50'
    else:
        key = '50+'
    
    results_by_distance[key]['total'] += 1
    if chunk['status'] == 'BLOCK_PLACED':
        results_by_distance[key]['placed'] += 1
    else:
        results_by_distance[key]['cannot'] += 1

print('WYNIKI WEDŁUG ODLEGŁOŚCI OD SPAWN CHUNKA:')
print(f'  {"Odległość":<15} {"Chunki":>8} {"Placed":>8} {"Outside":>8} {"% Sukcesu":>12}')
print('  ' + '-' * 65)

for dist_range, stats in sorted(results_by_distance.items()):
    if stats['total'] > 0:
        pct = stats['placed'] * 100 / stats['total']
        print(f'  {dist_range + " chunków":<15} {stats["total"]:>8} {stats["placed"]:>8} {stats["cannot"]:>8} {pct:>11.1f}%')

print()

# Znajdź najdalszy sukces
placed_chunks = [c for c in data['chunks'] if c['status'] == 'BLOCK_PLACED']
if placed_chunks:
    max_dist = 0
    max_dist_chunk = None
    for chunk in placed_chunks:
        chunk_x = chunk['chunk_x']
        chunk_z = chunk['chunk_z']
        dist = math.sqrt((chunk_x - SPAWN_CHUNK_X)**2 + (chunk_z - SPAWN_CHUNK_Z)**2)
        if dist > max_dist:
            max_dist = dist
            max_dist_chunk = chunk
    
    print(f'NAJDALSZY SUKCES:')
    print(f'  Chunk: ({max_dist_chunk["chunk_x"]}, {max_dist_chunk["chunk_z"]})')
    print(f'  Pozycja: {max_dist_chunk["position"]}')
    print(f'  Odległość: {max_dist:.1f} chunków od spawnu')
    print()

# Sprawdź czy są sukcesy dalej niż 20 chunków od spawnu
far_placed = [c for c in placed_chunks 
              if math.sqrt((c['chunk_x'] - SPAWN_CHUNK_X)**2 + (c['chunk_z'] - SPAWN_CHUNK_Z)**2) > 20]

print('HIPOTEZA: Setblock działa tylko w załadowanych chunkach (spawn + okolice)')
print()
print('WERYFIKACJA:')
if len(far_placed) == 0:
    print('  [OK] BRAK sukcesow dalej niz 20 chunkow od spawnu')
    print('  [OK] To potwierdza hipoteze - tylko spawn chunki sa zaladowane')
else:
    print(f'  [X] Znaleziono {len(far_placed)} sukcesow dalej niz 20 chunkow')
    print('  [X] Hipoteza czesciowo niepotwierdzona')

print()
print('WNIOSKI:')
print('  - Serwer bez graczy ładuje tylko spawn chunki (okolice 0,0 lub spawn point)')
print('  - Chunki poza spawnem są w pamięci (istnieją w MCA) ale nie są "załadowane" do gry')
print('  - Setblock na niezaładowanych chunkach zwraca "outside of the world"')
print('  - Aby przetestować dalekie chunki, trzeba najpierw je załadować (np. przez /forceload)')
