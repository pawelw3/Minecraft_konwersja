from nbtlib import ByteArray
arr = ByteArray([1,2,3])
print('before import: len=', len(arr), 'bool=', bool(arr))

import sys
sys.path.insert(0, 'src')
from converters.thermal.convert_thermal_test_map_v2 import read_region_chunk

arr2 = ByteArray([1,2,3])
print('after import: len=', len(arr2), 'bool=', bool(arr2))

from converters.thermal.thermal_converter import ThermalConverter
arr3 = ByteArray([1,2,3])
print('after ThermalConverter import: len=', len(arr3), 'bool=', bool(arr3))
