#!/usr/bin/env python3
import json

with open('chunk_test_report.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

print('=' * 80)
print('RAPORT Z TESTU SETBLOCK NA WSZYSTKICH CHUNKACH')
print('=' * 80)
print()
print('PARAMETRY TESTU:')
print(f'  Swiat: {data["world_path"]}')
print(f'  RCON: {data["rcon_host"]}:{data["rcon_port"]}')
print(f'  Czas startu: {data["start_time"]}')
print(f'  Czas zakonczenia: {data["end_time"]}')
print(f'  Czas trwania: {data["duration_seconds"]:.2f} sekund')
print()
print('WYNIKI OGOLNE:')
print(f'  Liczba chunkow: {data["total_chunks"]}')
print(f'  Sukcesow RCON: {data["summary"]["success"]}')
print(f'  Niepowodzen RCON: {data["summary"]["failed"]}')
print()
print('SZCZEGOLY WYNIKOW SETBLOCK:')
print(f'  Block placed (blok postawiony):     {data["summary"]["block_placed"]:5d} ({data["summary"]["block_placed"]*100//data["total_chunks"]}%)')
print(f'  Cannot place (nie mozna postawic):  {data["summary"]["cannot_place"]:5d} ({data["summary"]["cannot_place"]*100//data["total_chunks"]}%)')
print(f'  Inne odpowiedzi:                    {data["summary"]["other"]:5d} ({data["summary"]["other"]*100//data["total_chunks"]}%)')
print()

# Znajdz przyklady
examples_placed = [c for c in data['chunks'] if c['status'] == 'BLOCK_PLACED'][:5]
examples_cannot = [c for c in data['chunks'] if c['status'] == 'CANNOT_PLACE'][:5]

print('PRZYKLADY - BLOCK PLACED (puste miejsce):')
for ex in examples_placed:
    print(f'  Chunk ({ex["chunk_x"]}, {ex["chunk_z"]}) -> {ex["position"]}: {ex["response"]}')
print()

print('PRZYKLADY - CANNOT PLACE (zajete miejsce):')
for ex in examples_cannot:
    print(f'  Chunk ({ex["chunk_x"]}, {ex["chunk_z"]}) -> {ex["position"]}: {ex["response"]}')
print()

# Statystyki regionalne
regions = {}
for chunk in data['chunks']:
    region_key = f'r.{chunk["chunk_x"] // 32}.{chunk["chunk_z"] // 32}'
    if region_key not in regions:
        regions[region_key] = {'total': 0, 'placed': 0, 'cannot': 0}
    regions[region_key]['total'] += 1
    if chunk['status'] == 'BLOCK_PLACED':
        regions[region_key]['placed'] += 1
    elif chunk['status'] == 'CANNOT_PLACE':
        regions[region_key]['cannot'] += 1

print('STATYSTYKI PER REGION:')
print(f'  {"Region":<15} {"Chunki":>8} {"Placed":>8} {"Cannot":>8} {"% Placed":>10}')
print('  ' + '-' * 60)
for region, stats in sorted(regions.items()):
    pct = stats['placed'] * 100 // stats['total'] if stats['total'] > 0 else 0
    print(f'  {region:<15} {stats["total"]:>8} {stats["placed"]:>8} {stats["cannot"]:>8} {pct:>9}%')

print()
print('=' * 80)
print('WNIOSKI:')
print('=' * 80)
print(f'1. Test wykonano na {data["total_chunks"]} chunkach w {data["duration_seconds"]:.1f} sekund')
print(f'2. Srednio {(data["duration_seconds"]/data["total_chunks"]*1000):.1f} ms na komende')
print(f'3. Tylko {data["summary"]["block_placed"]} miejsc ({data["summary"]["block_placed"]*100//data["total_chunks"]}%) bylo pustych')
print(f'4. {data["summary"]["cannot_place"]} miejsc bylo juz zajetych (prawdopodobnie bedrock lub inne bloki)')
print(f'5. Poziom Y=40 jest zajety w wiekszosci chunkow (stare mapy, jaskinie, struktury)')
print()
