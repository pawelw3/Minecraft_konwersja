import json
import math

with open('chunk_test_report.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

SPAWN_X, SPAWN_Y, SPAWN_Z = 689, 4, -164
SPAWN_CHUNK_X = SPAWN_X // 16  # 43
SPAWN_CHUNK_Z = SPAWN_Z // 16  # -11 (floor division)

print('=' * 80)
print('ANALIZA GEOMETRII SPAWN CHUNKS')
print('=' * 80)
print(f'Spawn: ({SPAWN_X}, {SPAWN_Y}, {SPAWN_Z})')
print(f'Spawn chunk: ({SPAWN_CHUNK_X}, {SPAWN_CHUNK_Z})')
print()

# Znajdz wszystkie chunki ze sukcesem
placed_chunks = [(c['chunk_x'], c['chunk_z']) for c in data['chunks'] if c['status'] == 'BLOCK_PLACED']

if placed_chunks:
    min_x = min(c[0] for c in placed_chunks)
    max_x = max(c[0] for c in placed_chunks)
    min_z = min(c[1] for c in placed_chunks)
    max_z = max(c[1] for c in placed_chunks)
    
    print('ZAKRES SPAWN CHUNKS (chunki ze sukcesem):')
    print(f'  X: {min_x} do {max_x} (szerokość: {max_x - min_x + 1} chunków)')
    print(f'  Z: {min_z} do {max_z} (wysokość: {max_z - min_z + 1} chunków)')
    print(f'  Łącznie chunków ze sukcesem: {len(placed_chunks)}')
    print()
    
    # Sprawdź czy to kwadrat/prostokąt
    width_x = max_x - min_x + 1
    width_z = max_z - min_z + 1
    
    print(f'GEOMETRIA:')
    print(f'  Szerokość X: {width_x}')
    print(f'  Szerokość Z: {width_z}')
    print(f'  Powierzchnia: {width_x * width_z} chunków')
    
    if width_x == width_z == 16:
        print(f'  -> To KWADRAT 16x16! (klasyczne spawn chunks)')
    elif width_x == width_z:
        print(f'  -> To kwadrat {width_x}x{width_z}')
    else:
        print(f'  -> To prostokąt {width_x}x{width_z}')
    print()
    
    # Gdzie jest spawn w tym obszarze?
    spawn_rel_x = SPAWN_CHUNK_X - min_x
    spawn_rel_z = SPAWN_CHUNK_Z - min_z
    
    print(f'POZYCJA SPAWN W OBSZARZE:')
    print(f'  Spawn chunk: ({SPAWN_CHUNK_X}, {SPAWN_CHUNK_Z})')
    print(f'  Lewy górny róg obszaru: ({min_x}, {min_z})')
    print(f'  Spawn względem lewego górnego rogu: ({spawn_rel_x}, {spawn_rel_z})')
    print()
    
    # Sprawdź czy spawn jest w centrum czy na krawędzi
    center_x = (min_x + max_x) / 2
    center_z = (min_z + max_z) / 2
    
    print(f'Centrum obszaru: ({center_x}, {center_z})')
    print(f'Odległość spawn od centrum:')
    print(f'  X: {abs(SPAWN_CHUNK_X - center_x):.1f} chunków')
    print(f'  Z: {abs(SPAWN_CHUNK_Z - center_z):.1f} chunków')
    print()
    
    if spawn_rel_x == 0 or spawn_rel_x == width_x - 1 or spawn_rel_z == 0 or spawn_rel_z == width_z - 1:
        print('  -> Spawn jest NA KRAWĘDZI obszaru')
    elif spawn_rel_x == width_x // 2 and spawn_rel_z == width_z // 2:
        print('  -> Spawn jest W CENTRUM obszaru')
    else:
        print('  -> Spawn jest wewnątrz obszaru (niecentrycznie)')
    
    print()
    
    # Wizualizacja
    print('WIZUALIZACJA (X=spawn, #=spawn chunks ze sukcesem, .=poza obszarem):')
    print()
    
    # Przeskaluj dla czytelności
    for z in range(min_z - 2, max_z + 3):
        row = ''
        for x in range(min_x - 2, max_x + 3):
            if x == SPAWN_CHUNK_X and z == SPAWN_CHUNK_Z:
                row += 'X'  # Spawn
            elif (x, z) in placed_chunks:
                row += '#'  # Spawn chunk ze sukcesem
            elif min_x <= x <= max_x and min_z <= z <= max_z:
                row += '?'  # W granicach ale bez sukcesu (dziwne)
            else:
                row += '.'  # Poza obszarem
        print(f'  Chunk Z={z:3d}: {row}')
    
    print()
    print('Legenda: X=spawn, #=spawn chunk, .=poza obszarem')
