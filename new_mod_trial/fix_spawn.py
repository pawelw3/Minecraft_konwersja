import nbtlib
from nbtlib import tag

world_path = '../headless_server/1.7.10/world_cuttable_test/level.dat'

# Odczytaj plik
with open(world_path, 'rb') as f:
    data = nbtlib.File.from_fileobj(f)

print(f"Przed: Spawn = ({data['Data']['SpawnX']}, {data['Data']['SpawnY']}, {data['Data']['SpawnZ']})")

# Zmień spawn
data['Data']['SpawnX'] = tag.Int(0)
data['Data']['SpawnY'] = tag.Int(64)
data['Data']['SpawnZ'] = tag.Int(0)

print(f"Po: Spawn = ({data['Data']['SpawnX']}, {data['Data']['SpawnY']}, {data['Data']['SpawnZ']})")

# Zapisz plik
import gzip
with open(world_path, 'wb') as f:
    data.write(gzip.GzipFile(fileobj=f, mode='wb'))

print("Spawn zmieniony i zapisany!")
