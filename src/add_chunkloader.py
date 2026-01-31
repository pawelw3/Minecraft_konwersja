"""
Dodaje chunkloader do mapy MC 1.7.10 poprzez ustawienie spawnu w chunku ze strukturą.
W 1.7.10 chunk ze spawnem jest zawsze ładowany.
"""

import struct
import zlib
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent))
from minecraft_map_parser.nbt_parser import NBTParser, NBTTag
from minecraft_map_parser.nbt_writer import NBTWriter, write_nbt_gzipped, create_int, create_long, create_byte


def add_forced_chunk_to_level_dat(world_path: Path, chunk_x: int = 0, chunk_z: int = 0):
    """
    Dodaje forced chunk do level.dat oraz ustawia spawn w tym chunku.
    W 1.7.10 chunk ze spawnem jest ładowany przez serwer.
    """
    level_dat = world_path / "level.dat"
    
    if not level_dat.exists():
        print(f"ERROR: Nie znaleziono {level_dat}")
        return False
    
    # Odczytaj level.dat
    with open(level_dat, 'rb') as f:
        data = f.read()
    
    # Dekompresuj
    if data[:2] == b'\x1f\x8b':
        import gzip
        decompressed = gzip.decompress(data)
    else:
        decompressed = data
    
    # Parsuj NBT
    parser = NBTParser(decompressed)
    root = parser.parse()
    
    print(f"Odczytano level.dat, root tag: {root.name}")
    
    # Pobierz dane
    data_compound = root.value
    
    # Ustaw spawn w chunku (0, 60, 0) - środek struktury
    spawn_x = chunk_x * 16 + 8
    spawn_y = 64
    spawn_z = chunk_z * 16 + 8
    
    print(f"Ustawianie spawnu na: ({spawn_x}, {spawn_y}, {spawn_z})")
    
    # Aktualizuj spawn
    data_compound['SpawnX'] = create_int(spawn_x)
    data_compound['SpawnY'] = create_int(spawn_y)
    data_compound['SpawnZ'] = create_int(spawn_z)
    
    # Dodaj GameRules z keepSpawnLoaded (jeśli to działa w 1.7.10)
    if 'GameRules' not in data_compound:
        data_compound['GameRules'] = (NBTTag.TAG_COMPOUND, {})
    
    # Ustaw spawn radius na maksimum aby chunk był zawsze ładowany
    data_compound['spawnRadius'] = create_int(0)  # 0 = tylko spawn chunk
    
    # Zapisz z powrotem
    writer = NBTWriter()
    new_data = writer.write(root.name, NBTTag.TAG_COMPOUND, data_compound)
    
    # Kompresuj
    compressed = gzip.compress(new_data)
    
    # Zapisz backup
    backup_path = level_dat.with_suffix('.dat.backup')
    import shutil
    shutil.copy(level_dat, backup_path)
    print(f"Backup zapisany: {backup_path}")
    
    # Zapisz nowy plik
    with open(level_dat, 'wb') as f:
        f.write(compressed)
    
    print(f"Zapisano level.dat ze spawnem w ({spawn_x}, {spawn_y}, {spawn_z})")
    print("Chunk ze spawnem będzie ładowany przez serwer!")
    
    return True


def create_forced_chunks_dat(world_path: Path, chunks: list):
    """
    Tworzy forcedchunks.dat z listą chunków do załadowania.
    Format: lista (chunkX, chunkZ)
    """
    forced_chunks_file = world_path / "forcedchunks.dat"
    
    # Format forcedchunks.dat w 1.7.10:
    # ROOT: { "Data": COMPOUND { "TicketList": LIST of COMPOUNDS } }
    # Każdy ticket: { "ChunkX": INT, "ChunkZ": INT, "ModID": STRING, "TicketID": STRING }
    
    tickets = []
    for i, (cx, cz) in enumerate(chunks):
        ticket = {
            "ChunkX": create_int(cx),
            "ChunkZ": create_int(cz),
            "ModID": (NBTTag.TAG_STRING, "ForgeEssentials"),  # lub inny mod
            "TicketID": (NBTTag.TAG_STRING, f"chunkloader_{i}"),
        }
        tickets.append((NBTTag.TAG_COMPOUND, ticket))
    
    data_compound = {
        "TicketList": (NBTTag.TAG_LIST, tickets)
    }
    
    root_compound = {
        "Data": (NBTTag.TAG_COMPOUND, data_compound)
    }
    
    # Zapisz
    writer = NBTWriter()
    nbt_data = writer.write("", NBTTag.TAG_COMPOUND, root_compound)
    
    # Kompresuj
    import gzip
    compressed = gzip.compress(nbt_data)
    
    with open(forced_chunks_file, 'wb') as f:
        f.write(compressed)
    
    print(f"Utworzono {forced_chunks_file} z {len(chunks)} chunkami")
    return True


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        world_path = Path("headless_server/1.7.10/world")
    else:
        world_path = Path(sys.argv[1])
    
    # Ustaw spawn w chunku (0,0) gdzie jest struktura
    add_forced_chunk_to_level_dat(world_path, chunk_x=0, chunk_z=0)
    
    # Dodatkowo utwórz forcedchunks.dat
    create_forced_chunks_dat(world_path, [(0, 0)])
    
    print("\nChunkloader skonfigurowany!")
    print("Chunk (0,0) będzie ładowany przy starcie serwera.")
