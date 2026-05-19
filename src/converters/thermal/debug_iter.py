import sys
from pathlib import Path
sys.path.insert(0, 'src')
from converters.thermal.convert_thermal_test_map import read_region_chunk

region_file = Path('lightweigh_map_templates/1710_modded/thermal_test_v2/region/r.0.0.mca')
chunk = read_region_chunk(region_file, 0, 0)
level = chunk.get('Level')
sections = level.get('Sections')

# Bezposredni dostep
sec0 = sections[0]
b0 = sec0.get('Blocks')
print('Direct access:')
print('  type:', type(b0))
print('  len:', len(b0))
print('  first 3:', [int(x) & 0xFF for x in b0[:3]])

# Iteracja
print('Iteration:')
for i, sec in enumerate(sections):
    b = sec.get('Blocks')
    print(f'  [{i}] type={type(b)} len={len(b)} first3={[int(x) & 0xFF for x in b[:3]]}')
    print(f'  [{i}] same_as_sec0={sec is sec0}')
    break

# Sprawdz czy to samo ID
print('ID check:')
print('  id(sec0):', id(sec0))
print('  id(sec):', id(sec))
print('  id(b0):', id(b0))
print('  id(b):', id(b))
