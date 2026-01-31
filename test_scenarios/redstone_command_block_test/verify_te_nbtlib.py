#!/usr/bin/env python3
"""
Weryfikacja Command Block Tile Entity używając nbtlib
"""

import struct
import zlib
import gzip
from pathlib import Path
import nbtlib

def read_chunk_data(region_file, local_chunk_x, local_chunk_z):
    """Odczytuje surowe dane chunka z pliku regionu."""
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
            return gzip.decompress(compressed_data)
        elif compression_type == 2:
            return zlib.decompress(compressed_data)
        else:
            return compressed_data


def find_command_block_te(world_path, target_x, target_y, target_z):
    """Znajduje Tile Entity Command Blocka na danej pozycji."""
    
    # Oblicz współrzędne
    chunk_x = target_x // 16
    chunk_z = target_z // 16
    region_x = chunk_x // 32
    region_z = chunk_z // 32
    local_chunk_x = chunk_x % 32
    local_chunk_z = chunk_z % 32
    
    print(f"=" * 60)
    print(f"WERYFIKACJA COMMAND BLOCK TILE ENTITY")
    print(f"=" * 60)
    print(f"Pozycja docelowa: ({target_x}, {target_y}, {target_z})")
    print(f"Chunk: ({chunk_x}, {chunk_z})")
    print(f"Region: ({region_x}, {region_z})")
    print(f"Lokalny chunk: ({local_chunk_x}, {local_chunk_z})")
    
    region_file = Path(world_path) / "region" / f"r.{region_x}.{region_z}.mca"
    
    if not region_file.exists():
        print(f"[ERR] Brak pliku regionu: {region_file}")
        return False
    
    print(f"\nPlik regionu: {region_file}")
    
    # Odczytaj dane chunka
    chunk_data = read_chunk_data(region_file, local_chunk_x, local_chunk_z)
    if chunk_data is None:
        print("[ERR] Nie udało się odczytać danych chunka")
        return False
    
    print(f"[OK] Odczytano {len(chunk_data)} bajtów danych chunka")
    
    # Parsuj NBT
    try:
        from io import BytesIO
        nbt_file = nbtlib.File.parse(BytesIO(chunk_data))
        root = nbt_file.root
    except Exception as e:
        print(f"[ERR] Błąd parsowania NBT: {e}")
        return False
    
    # Pobierz Level
    if "Level" not in root:
        print("[ERR] Brak 'Level' w root NBT")
        return False
    
    level = root["Level"]
    
    # Pobierz TileEntities
    if "TileEntities" not in level:
        print("[ERR] Brak 'TileEntities' w Level")
        return False
    
    tile_entities = level["TileEntities"]
    print(f"\nZnaleziono {len(tile_entities)} Tile Entities:")
    
    found = False
    for i, te in enumerate(tile_entities):
        x = int(te.get("x", 0))
        y = int(te.get("y", 0))
        z = int(te.get("z", 0))
        id_val = str(te.get("id", "unknown"))
        
        if x == target_x and y == target_y and z == target_z:
            found = True
            print(f"\n{'='*60}")
            print(f"[FOUND] TE[{i}] na pozycji ({x}, {y}, {z})")
            print(f"{'='*60}")
            print(f"  id: '{id_val}'")
            
            if id_val == "Control":
                command = str(te.get("Command", ""))
                custom_name = str(te.get("CustomName", ""))
                track_output = int(te.get("TrackOutput", 0))
                success_count = int(te.get("SuccessCount", 0))
                
                print(f"  Command: '{command}'")
                print(f"  CustomName: '{custom_name}'")
                print(f"  TrackOutput: {track_output}")
                print(f"  SuccessCount: {success_count}")
                
                print(f"\n{'='*60}")
                if "[TEST_REDSTONE]" in command:
                    print("[PASS] Command Block Tile Entity ustawiony poprawnie!")
                    print("       Testowa komenda znaleziona w polu Command.")
                else:
                    print("[WARN] Command Block znaleziony ale komenda nie zawiera [TEST_REDSTONE]")
            else:
                print(f"[WARN] Znaleziono TE ale id='{id_val}' != 'Control'")
            print(f"{'='*60}")
        elif id_val == "Control":
            # Inny command block
            command = str(te.get("Command", ""))[:50]
            print(f"  TE[{i}]: ({x}, {y}, {z}) id='{id_val}' - Command: '{command}...'")
    
    return found


def verify_all_blocks(world_path):
    """Weryfikuje wszystkie bloki w układzie testowym."""
    
    print("\n" + "="*60)
    print("WERYFIKACJA WSZYSTKICH BLOKÓW W UKŁADZIE")
    print("="*60)
    
    # Lista bloków do sprawdzenia
    blocks_to_check = [
        (50, 63, 50, 1, 0, "Stone (pod dźwignią)"),
        (51, 63, 50, 1, 0, "Stone (pod redstone)"),
        (60, 63, 50, 1, 0, "Stone (pod command blockiem)"),
        (50, 64, 50, 69, 5, "Lever"),
        (51, 64, 50, 55, 15, "Redstone Dust"),
        (52, 64, 50, 55, 15, "Redstone Dust"),
        (53, 64, 50, 55, 15, "Redstone Dust"),
        (54, 64, 50, 93, 1, "Repeater"),
        (55, 64, 50, 55, 15, "Redstone Dust"),
        (56, 64, 50, 55, 15, "Redstone Dust"),
        (57, 64, 50, 55, 15, "Redstone Dust"),
        (58, 64, 50, 93, 1, "Repeater"),
        (59, 64, 50, 55, 15, "Redstone Dust"),
        (60, 64, 50, 137, 0, "Command Block"),
    ]
    
    passed = 0
    failed = 0
    
    for x, y, z, expected_id, expected_meta, desc in blocks_to_check:
        # Oblicz pozycję w chunku
        chunk_x = x // 16
        chunk_z = z // 16
        region_x = chunk_x // 32
        region_z = chunk_z // 32
        local_chunk_x = chunk_x % 32
        local_chunk_z = chunk_z % 32
        
        region_file = Path(world_path) / "region" / f"r.{region_x}.{region_z}.mca"
        
        if not region_file.exists():
            print(f"[ERR] {desc} at ({x},{y},{z}): Brak pliku regionu")
            failed += 1
            continue
        
        try:
            chunk_data = read_chunk_data(region_file, local_chunk_x, local_chunk_z)
            if chunk_data is None:
                print(f"[ERR] {desc} at ({x},{y},{z}): Brak danych chunka")
                failed += 1
                continue
            
            from io import BytesIO
            nbt_file = nbtlib.File.parse(BytesIO(chunk_data))
            level = nbt_file.root["Level"]
            sections = level["Sections"]
            
            # Znajdź sekcję Y
            section_y = y // 16
            local_y = y % 16
            local_x = x % 16
            local_z = z % 16
            
            section = None
            for s in sections:
                if int(s["Y"]) == section_y:
                    section = s
                    break
            
            if section is None:
                print(f"[ERR] {desc} at ({x},{y},{z}): Brak sekcji Y={section_y}")
                failed += 1
                continue
            
            # Odczytaj blok
            blocks = section["Blocks"]
            index = (local_y * 16 + local_z) * 16 + local_x
            actual_id = blocks[index] & 0xFF
            
            if actual_id == expected_id:
                print(f"[OK] {desc} at ({x},{y},{z}): ID={actual_id}")
                passed += 1
            else:
                print(f"[FAIL] {desc} at ({x},{y},{z}): Oczekiwano ID={expected_id}, odczytano ID={actual_id}")
                failed += 1
                
        except Exception as e:
            print(f"[ERR] {desc} at ({x},{y},{z}): {e}")
            failed += 1
    
    print(f"\n{'='*60}")
    print(f"Podsumowanie: {passed} OK, {failed} FAIL")
    print(f"{'='*60}")
    
    return failed == 0


def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--world", default="../../map_read_write_tests/kimi1")
    parser.add_argument("--x", type=int, default=60)
    parser.add_argument("--y", type=int, default=64)
    parser.add_argument("--z", type=int, default=50)
    
    args = parser.parse_args()
    
    world_path = Path(args.world)
    
    # Weryfikacja wszystkich bloków
    blocks_ok = verify_all_blocks(world_path)
    
    # Weryfikacja Tile Entity
    te_ok = find_command_block_te(world_path, args.x, args.y, args.z)
    
    print("\n" + "="*60)
    if blocks_ok and te_ok:
        print("[PASS] Wszystkie testy zakończone sukcesem!")
        print("="*60)
        return 0
    else:
        print("[FAIL] Niektóre testy nie powiodły się")
        print("="*60)
        return 1


if __name__ == "__main__":
    exit(main())
