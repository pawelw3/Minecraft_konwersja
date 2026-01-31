#!/usr/bin/env python3
"""
Weryfikacja Command Blocka i jego Tile Entity
"""

import sys
import struct
import zlib
import gzip
from pathlib import Path
from io import BytesIO

# Dodaj ścieżkę do src jeśli potrzeba
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

def read_chunk_nbt(region_file, local_chunk_x, local_chunk_z):
    """Odczytuje NBT chunka z pliku regionu."""
    with open(region_file, "rb") as f:
        # Offset w tablicy lokalizacji
        index = local_chunk_x + local_chunk_z * 32
        f.seek(index * 4)
        
        offset_bytes = f.read(4)
        if len(offset_bytes) != 4:
            return None
        
        sector_offset = ((offset_bytes[0] & 0xFF) << 16) | \
                       ((offset_bytes[1] & 0xFF) << 8) | \
                       (offset_bytes[2] & 0xFF)
        sector_count = offset_bytes[3] & 0xFF
        
        if sector_offset == 0 or sector_count == 0:
            return None
        
        # Odczytaj dane chunka
        f.seek(sector_offset * 4096)
        
        length_bytes = f.read(4)
        length = struct.unpack(">I", length_bytes)[0]
        
        compression_type = f.read(1)[0]
        
        if length < 1 or length > 1024 * 1024:
            return None
        
        compressed_data = f.read(length - 1)
        
        if compression_type == 1:
            data = gzip.decompress(compressed_data)
        elif compression_type == 2:
            data = zlib.decompress(compressed_data)
        else:
            data = compressed_data
        
        # Parsuj NBT - uproszczona wersja
        return parse_nbt_simple(data)


def parse_nbt_simple(data):
    """Uproszczony parser NBT - zwraca surowe dane."""
    try:
        # Użyj hephaistos przez JPype jeśli dostępne
        import jpype
        if not jpype.isJVMStarted():
            # Spróbuj znaleźć JVM
            jpype.startJVM()
        
        from org.jglrxavpok.hephaistos.nbt import NBTReader, CompressedProcesser
        reader = NBTReader(data, CompressedProcesser.NONE)
        return reader.read()
    except:
        return None


def find_command_block_te(world_path, target_x, target_y, target_z):
    """Znajduje Tile Entity Command Blocka na danej pozycji."""
    
    # Oblicz współrzędne chunka i regionu
    chunk_x = target_x // 16
    chunk_z = target_z // 16
    region_x = chunk_x // 32
    region_z = chunk_z // 32
    local_chunk_x = chunk_x % 32
    local_chunk_z = chunk_z % 32
    
    print(f"Szukam Command Blocka na ({target_x}, {target_y}, {target_z})")
    print(f"Chunk: ({chunk_x}, {chunk_z}), Region: ({region_x}, {region_z})")
    print(f"Lokalny chunk: ({local_chunk_x}, {local_chunk_z})")
    
    region_file = Path(world_path) / "region" / f"r.{region_x}.{region_z}.mca"
    
    if not region_file.exists():
        print(f"[ERR] Brak pliku regionu: {region_file}")
        return False
    
    print(f"Plik regionu: {region_file}")
    
    # Użyj JPype do odczytu
    try:
        import jpype
        from jpype.types import *
        
        if not jpype.isJVMStarted():
            # Znajdź JVM w workerze
            worker_dir = Path(__file__).parent.parent.parent / "jvm" / "worker"
            jars = list((worker_dir / "build" / "libs").glob("*.jar"))
            if jars:
                classpath = str(jars[0])
                jpype.startJVM(classpath=[classpath])
        
        from org.jglrxavpok.hephaistos.mca import RegionFile
        from java.io import RandomAccessFile
        
        raf = RandomAccessFile(str(region_file), "r")
        region = RegionFile(raf, region_x, region_z, 0, 255)
        
        if not region.hasChunk(chunk_x, chunk_z):
            print("[ERR] Chunk nie istnieje w regionie")
            raf.close()
            return False
        
        chunk_data = region.getChunkData(chunk_x, chunk_z)
        if chunk_data is None:
            print("[ERR] Nie udało się odczytać danych chunka")
            raf.close()
            return False
        
        level = chunk_data.getCompound("Level")
        if level is None:
            print("[ERR] Brak Level w chunku")
            raf.close()
            return False
        
        # Sprawdź Tile Entities
        te_list = level.getList("TileEntities")
        if te_list is None or te_list.size() == 0:
            print("[ERR] Brak Tile Entities w chunku")
            raf.close()
            return False
        
        print(f"\nZnaleziono {te_list.size()} Tile Entities:")
        
        found = False
        for i in range(te_list.size()):
            te = te_list.get(i)
            x = te.getInt("x") or 0
            y = te.getInt("y") or 0
            z = te.getInt("z") or 0
            id_val = te.getString("id") or "unknown"
            
            if x == target_x and y == target_y and z == target_z:
                found = True
                print(f"\n[FOUND] TE[{i}]: ({x}, {y}, {z}) id='{id_val}'")
                
                if id_val == "Control":
                    command = te.getString("Command")
                    custom_name = te.getString("CustomName")
                    track_output = te.getByte("TrackOutput")
                    
                    print(f"  -> Command: '{command}'")
                    print(f"  -> CustomName: '{custom_name}'")
                    print(f"  -> TrackOutput: {track_output}")
                    
                    if command and "[TEST_REDSTONE]" in command:
                        print("\n[PASS] Command Block ustawiony poprawnie z testową komendą!")
                    else:
                        print("\n[WARN] Command Block znaleziony ale komenda nie zawiera [TEST_REDSTONE]")
                else:
                    print(f"[WARN] Znaleziono TE ale id='{id_val}' != 'Control'")
            
            elif id_val == "Control":
                # Inny command block
                command = te.getString("Command")
                print(f"  TE[{i}]: ({x}, {y}, {z}) id='{id_val}' - Command: '{command[:50]}...'")
        
        raf.close()
        return found
        
    except Exception as e:
        print(f"[ERR] Błąd podczas odczytu: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--world", default="../../map_read_write_tests/kimi1")
    parser.add_argument("--x", type=int, default=60)
    parser.add_argument("--y", type=int, default=64)
    parser.add_argument("--z", type=int, default=50)
    
    args = parser.parse_args()
    
    success = find_command_block_te(args.world, args.x, args.y, args.z)
    
    return 0 if success else 1


if __name__ == "__main__":
    exit(main())
