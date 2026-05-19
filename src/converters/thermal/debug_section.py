import sys
from pathlib import Path
sys.path.insert(0, 'src')
from converters.thermal.convert_thermal_test_map import read_region_chunk

region_file = Path('lightweigh_map_templates/1710_modded/thermal_test_v2/region/r.0.0.mca')
chunk = read_region_chunk(region_file, 0, 0)
level = chunk.get('Level')
sections = level.get('Sections')

sec = sections[0]
print('sec.get method:', sec.get)
print('sec.get Blocks:', type(sec.get('Blocks')), len(sec.get('Blocks')))

for s in sections:
    print('loop s.get Blocks:', type(s.get('Blocks')), len(s.get('Blocks')))
    break
