import nbtlib

world_path = '../headless_server/1.7.10/world_cuttable_test/level.dat'
level = nbtlib.load(world_path)

# Zmień spawn na (0, 64, 0) - przy blokach testowych
level['Data']['SpawnX'] = nbtlib.tag.Int(0)
level['Data']['SpawnY'] = nbtlib.tag.Int(64)  
level['Data']['SpawnZ'] = nbtlib.tag.Int(0)

level.save(world_path)
print('Spawn zmieniony na (0, 64, 0)')
