import nbtlib

world_path = '../headless_server/1.7.10/world_cuttable_test/level.dat'

# Odczytaj plik
data = nbtlib.load(world_path)

print(f"Przed: Spawn = ({data['Data']['SpawnX']}, {data['Data']['SpawnY']}, {data['Data']['SpawnZ']})")

# Zmień spawn
data['Data']['SpawnX'] = nbtlib.tag.Int(0)
data['Data']['SpawnY'] = nbtlib.tag.Int(64)
data['Data']['SpawnZ'] = nbtlib.tag.Int(0)

print(f"Po: Spawn = ({data['Data']['SpawnX']}, {data['Data']['SpawnY']}, {data['Data']['SpawnZ']})")

# Zapisz plik - nbtlib zadba o gzip
data.save()

print("Spawn zmieniony i zapisany!")
