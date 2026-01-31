#!/usr/bin/env python3
"""
Wstawia spiralny test do istniejącego świata Minecraft 1.7.10.
Używa biblioteki nbtlib do modyfikacji NBT.
"""

import sys
import os
import struct
import zlib
from collections import defaultdict
from pathlib import Path

# Dodaj src do path
script_dir = Path(__file__).parent
src_path = script_dir.parent.parent / 'src'
sys.path.insert(0, str(src_path))

try:
    import nbtlib
    from nbtlib import File, Compound, Int, Byte, String, ByteArray, List
except ImportError:
    print("Błąd: nbtlib nie jest zainstalowany. Uruchom: pip install nbtlib")
    sys.exit(1)


def generate_spiral_chunks(radius):
    """Generuje listę chunków w spiralę od (0,0)"""
    chunks = []
    x, z = 0, 0
    dx, dz = 1, 0
    steps = 1
    step_count = 0
    direction_changes = 0
    
    for step in range((2 * radius + 1) ** 2):
        if abs(x) > radius or abs(z) > radius:
            break
        chunks.append((x, z, step))
        
        x += dx
        z += dz
        step_count += 1
        
        if step_count == steps:
            step_count = 0
            direction_changes += 1
            if dx == 1 and dz == 0:
                dx, dz = 0, 1
            elif dx == 0 and dz == 1:
                dx, dz = -1, 0
            elif dx == -1 and dz == 0:
                dx, dz = 0, -1
            elif dx == 0 and dz == -1:
                dx, dz = 1, 0
            
            if direction_changes % 2 == 0:
                steps += 1
    
    return chunks


def read_chunk_data(region_path, chunk_x, chunk_z):
    """Czyta surowe dane chunka z pliku regionu."""
    with open(region_path, 'rb') as f:
        data = f.read()
    
    index = chunk_x + chunk_z * 32
    offset = index * 4
    chunk_info = data[offset:offset + 4]
    sector_offset = ((chunk_info[0] << 16) | (chunk_info[1] << 8) | chunk_info[2])
    sector_count = chunk_info[3]
    
    if sector_offset == 0:
        return None
    
    byte_offset = sector_offset * 4096
    length_data = data[byte_offset:byte_offset + 4]
    length = struct.unpack('>I', length_data)[0]
    compression_type = data[byte_offset + 4]
    compressed_data = data[byte_offset + 5:byte_offset + 5 + length - 1]
    
    if compression_type == 2:
        return zlib.decompress(compressed_data)
    elif compression_type == 1:
        import gzip
        return gzip.decompress(compressed_data)
    return compressed_data


def write_chunk_data(chunk_nbt):
    """Zapisuje chunk NBT do bajtów."""
    # Użyj nbtlib do zapisu
    from io import BytesIO
    nbt_file = File({'Level': chunk_nbt['Level']})
    buffer = BytesIO()
    nbt_file.write(buffer, byteorder='big')
    return buffer.getvalue()


def modify_chunk(chunk_nbt, cx, cz, y_level=200):
    """Modyfikuje chunk aby dodać platformę stone."""
    level = chunk_nbt.get('Level', {})
    
    # Pobierz lub utwórz sekcje
    sections = level.get('Sections', [])
    
    # Znajdź lub utwórz sekcję dla y_level
    sec_y = y_level // 16
    target_section = None
    
    for section in sections:
        if section.get('Y') == sec_y:
            target_section = section
            break
    
    if target_section is None:
        # Utwórz nową sekcję
        target_section = Compound({
            'Y': Byte(sec_y),
            'Blocks': ByteArray([0] * 4096),
            'Data': ByteArray([0] * 2048),
            'SkyLight': ByteArray([0xff] * 2048),
            'BlockLight': ByteArray([0] * 2048)
        })
        sections.append(target_section)
    
    # Upewnij się że Blocks jest modyfikowalny
    if isinstance(target_section['Blocks'], bytes):
        target_section['Blocks'] = ByteArray(list(target_section['Blocks']))
    
    blocks = target_section['Blocks']
    
    # Dodaj platformę stone (5x5 w środku chunka)
    center_x = 8
    center_z = 8
    local_y = y_level % 16
    
    for dx in range(-2, 3):
        for dz in range(-2, 3):
            x = center_x + dx
            z = center_z + dz
            idx = local_y * 256 + z * 16 + x
            blocks[idx] = 1  # stone
    
    return chunk_nbt


def add_redstone_block(chunk_nbt, y_level=200):
    """Dodaje redstone block w środku chunka."""
    level = chunk_nbt.get('Level', {})
    sections = level.get('Sections', [])
    sec_y = y_level // 16
    
    for section in sections:
        if section.get('Y') == sec_y:
            if isinstance(section['Blocks'], bytes):
                section['Blocks'] = ByteArray(list(section['Blocks']))
            
            local_y = y_level % 16
            idx = local_y * 256 + 8 * 16 + 8  # (8, y, 8) - środek
            section['Blocks'][idx] = 152  # redstone block
            break
    
    return chunk_nbt


def add_command_block(chunk_nbt, command, y_level=200):
    """Dodaje command block z komendą."""
    level = chunk_nbt.get('Level', {})
    
    # Dodaj tile entity
    tile_entities = level.get('TileEntities', [])
    
    cb = Compound({
        'id': String('Control'),
        'x': Int(9),  # obok środka
        'y': Int(y_level),
        'z': Int(8),
        'Command': String(command),
        'CustomName': String('@'),
        'TrackOutput': Byte(1)
    })
    tile_entities.append(cb)
    
    # Dodaj blok command block
    sections = level.get('Sections', [])
    sec_y = y_level // 16
    
    for section in sections:
        if section.get('Y') == sec_y:
            if isinstance(section['Blocks'], bytes):
                section['Blocks'] = ByteArray(list(section['Blocks']))
            
            local_y = y_level % 16
            idx = local_y * 256 + 8 * 16 + 9  # (9, y, 8)
            section['Blocks'][idx] = 137  # command block
            break
    
    return chunk_nbt


def save_region_chunk(region_path, chunk_x, chunk_z, chunk_bytes):
    """Zapisuje zmodyfikowany chunk z powrotem do regionu."""
    with open(region_path, 'r+b') as f:
        # Odczytaj nagłówek
        f.seek((chunk_x + chunk_z * 32) * 4)
        header = f.read(4)
        sector_offset = ((header[0] << 16) | (header[1] << 8) | header[2])
        sector_count = header[3]
        
        if sector_offset == 0:
            print(f"    Warning: chunk ({chunk_x}, {chunk_z}) nie istniał")
            return False
        
        # Kompresja
        compressed = zlib.compress(chunk_bytes)
        new_data = struct.pack('>I', len(compressed) + 1) + b'\x02' + compressed
        
        # Sprawdź czy się zmieści
        new_sectors = (len(new_data) + 4095) // 4096
        if new_sectors > sector_count:
            print(f"    Warning: nowe dane zajmują {new_sectors} sektorów, mamy {sector_count}")
            # Przytnij lub znajdź nowe miejsce - dla uproszczenia pomijamy
            return False
        
        # Zapisz
        f.seek(sector_offset * 4096)
        f.write(new_data)
        f.write(b'\x00' * (sector_count * 4096 - len(new_data)))  # Dopełnienie
        
        return True


def insert_spiral(world_path, radius=3, y_level=200):
    """Wstawia spiralę do istniejącego świata (uproszczona wersja)."""
    print(f"Wstawianie spirali R={radius} do {world_path}")
    print(f"Wysokość Y={y_level}")
    
    chunks = generate_spiral_chunks(radius)
    print(f"Wygenerowano {len(chunks)} punktów spirali")
    
    # Przetwórz tylko chunki w regionie r.0.0.mca (0-31, 0-31)
    region_chunks = [(cx, cz, step) for cx, cz, step in chunks 
                     if 0 <= cx < 32 and 0 <= cz < 32]
    
    print(f"Chunki w regionie r.0.0.mca: {len(region_chunks)}")
    
    region_file = Path(world_path) / 'region' / 'r.0.0.mca'
    if not region_file.exists():
        print(f"Błąd: {region_file} nie istnieje")
        return
    
    modified_count = 0
    
    for cx, cz, step in region_chunks:
        # Wczytaj chunk
        data = read_chunk_data(str(region_file), cx, cz)
        if data is None:
            print(f"  Chunk ({cx}, {cz}) nie istnieje, pomijam")
            continue
        
        # Parsuj NBT
        try:
            from io import BytesIO
            chunk_nbt = nbtlib.File.parse(BytesIO(data), byteorder='big')
        except Exception as e:
            print(f"  Błąd parsowania chunka ({cx}, {cz}): {e}")
            continue
        
        # Modyfikuj chunk
        chunk_nbt = modify_chunk(chunk_nbt, cx, cz, y_level)
        
        if step == 0:
            # Start - redstone block
            chunk_nbt = add_redstone_block(chunk_nbt, y_level)
        else:
            # Command block
            command = f"/say [PROBE] REACHED cx={cx} cz={cz} step={step}"
            chunk_nbt = add_command_block(chunk_nbt, command, y_level)
        
        # Zapisz chunk
        chunk_bytes = write_chunk_data(chunk_nbt)
        if save_region_chunk(str(region_file), cx, cz, chunk_bytes):
            modified_count += 1
    
    print(f"\nZmodyfikowano {modified_count} chunków")
    print("Gotowe!")


if __name__ == "__main__":
    world_path = script_dir.parent / '1.7.10' / 'world'
    
    print("=" * 60)
    print("WSTAWIANIE SPIRALI DO ISTNIEJĄCEGO ŚWIATA (v2)")
    print("=" * 60)
    
    # Użyj R=3 aby zmieścić się w jednym regionie
    insert_spiral(world_path, radius=3, y_level=200)
