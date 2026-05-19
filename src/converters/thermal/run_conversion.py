import sys
from pathlib import Path
sys.path.insert(0, 'src')
from converters.thermal.convert_thermal_test_map import scan_and_convert

report = scan_and_convert('lightweigh_map_templates/1710_modded/thermal_test_v2')
print('stats:', report['stats'])
for r in report['results'][:5]:
    print(r)
