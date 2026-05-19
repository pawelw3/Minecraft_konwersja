import sys
from pathlib import Path
sys.path.insert(0, 'src')
from converters.thermal.convert_thermal_test_map_v2 import read_region_chunk

region_file = Path('lightweigh_map_templates/1710_modded/thermal_test_v2/region/r.0.0.mca')
chunk = read_region_chunk(region_file, 0, 0)
level = chunk.get('Level')
sections = level.get('Sections')
sec = sections[0]
blocks = sec.get('Blocks')
print('blocks type:', type(blocks))
print('blocks len:', len(blocks))
print('blocks truthy:', bool(blocks))
print('first 3:', [int(b) & 0xFF for b in blocks[:3]])
