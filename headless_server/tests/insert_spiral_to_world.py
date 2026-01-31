#!/usr/bin/env python3
"""
Wstawia spiralny test do istniejącego świata Minecraft 1.7.10.
Modyfikuje bezpośrednio pliki regionów MCA.
"""

import sys
import os
import struct
import zlib
import gzip
from io import BytesIO
from collections import defaultdict

# Dodaj src do path
script_dir = os.path.dirname(os.path.abspath(__file__))
src_path = os.path.join(script_dir, '..', '..', 'src')
sys.path.insert(0, os.path.normpath(src_path))

from minecraft_map_parser.anvil_parser import AnvilParser
from minecraft_map_parser.nbt_parser import parse_nbt


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


def write_nbt_to_bytes(nbt_tag):
    """Konwertuje NBT tag do bajtów (używając istniejącej struktury)."""
    # Prosta implementacja - zapisz do formatu NBT
    def write_tag(name, tag, tag_type):
        stream = BytesIO()
        stream.write(struct.pack('>B', tag_type))
        stream.write(struct.pack('>H', len(name)))
        stream.write(name.encode('utf-8'))
        write_payload(stream, tag, tag_type)
        return stream.getvalue()
    
    def write_payload(stream, tag, tag_type):
        if tag_type == 1:  # BYTE
            stream.write(struct.pack('>b', tag.value if hasattr(tag, 'value') else tag))
        elif tag_type == 2:  # SHORT
            stream.write(struct.pack('>h', tag.value if hasattr(tag, 'value') else tag))
        elif tag_type == 3:  # INT
            stream.write(struct.pack('>i', tag.value if hasattr(tag, 'value') else tag))
        elif tag_type == 4:  # LONG
            stream.write(struct.pack('>q', tag.value if hasattr(tag, 'value') else tag))
        elif tag_type == 8:  # STRING
            s = tag.value if hasattr(tag, 'value') else tag
            encoded = s.encode('utf-8')
            stream.write(struct.pack('>H', len(encoded)))
            stream.write(encoded)
        elif tag_type == 7:  # BYTE_ARRAY
            arr = tag.value if hasattr(tag, 'value') else tag
            stream.write(struct.pack('>i', len(arr)))
            stream.write(arr)
        elif tag_type == 10:  # COMPOUND
            d = tag.value if hasattr(tag, 'value') else tag
            for k, v in d.items():
                if hasattr(v, 'type_id'):
                    stream.write(write_tag(k, v, v.type_id))
                elif isinstance(v, bool):
                    stream.write(write_tag(k, 1 if v else 0, 1))
                elif isinstance(v, int):
                    stream.write(write_tag(k, v, 3))
                elif isinstance(v, str):
                    stream.write(write_tag(k, v, 8))
                elif isinstance(v, (bytes, bytearray)):
                    stream.write(write_tag(k, bytes(v), 7))
                elif isinstance(v, list):
                    # List
                    stream.write(struct.pack('>B', 9))
                    stream.write(struct.pack('>H', len(k)))
                    stream.write(k.encode('utf-8'))
                    if v and hasattr(v[0], 'type_id'):
                        stream.write(struct.pack('>B', v[0].type_id))
                        stream.write(struct.pack('>i', len(v)))
                        for item in v:
                            write_payload(stream, item, item.type_id)
                    else:
                        stream.write(struct.pack('>B', 0))
                        stream.write(struct.pack('>i', 0))
            stream.write(struct.pack('>B', 0))  # END
    
    return write_tag('', nbt_tag, 10)


def modify_chunk_blocks(chunk_nbt, y_level=200):
    """Modyfikuje chunk NBT aby dodać bloki spiralne."""
    level = chunk_nbt.get('Level', {})
    if hasattr(level, 'value'):
        level = level.value
    
    cx = level.get('xPos', 0)
    cz = level.get('zPos', 0)
    if hasattr(cx, 'value'):
        cx = cx.value
    if hasattr(cz, 'value'):
        cz = cz.value
    
    sections = level.get('Sections', [])
    if hasattr(sections, 'value'):
        sections = sections.value
    
    # Konwertuj sekcje do modyfikowalnej formy
    new_sections = []
    for sec in sections:
        if hasattr(sec, 'value'):
            sec = sec.value
        new_sec = {}
        for k, v in sec.items():
            if hasattr(v, 'value'):
                new_sec[k] = v.value
            else:
                new_sec[k] = v
        new_sections.append(new_sec)
    
    # Upewnij się że mamy sekcję dla y_level
    sec_y = y_level // 16
    section = None
    for s in new_sections:
        if s.get('Y') == sec_y:
            section = s
            break
    
    if section is None:
        # Utwórz nową sekcję
        section = {
            'Y': sec_y,
            'Blocks': bytearray(4096),
            'Data': bytearray(2048),
            'SkyLight': bytearray([0xff] * 2048),
            'BlockLight': bytearray(2048)
        }
        new_sections.append(section)
    
    # Konwertuj do bytearray
    if isinstance(section.get('Blocks'), bytes):
        section['Blocks'] = bytearray(section['Blocks'])
    if isinstance(section.get('Data'), bytes):
        section['Data'] = bytearray(section['Data'])
    if isinstance(section.get('SkyLight'), bytes):
        section['SkyLight'] = bytearray(section['SkyLight'])
    if isinstance(section.get('BlockLight'), bytes):
        section['BlockLight'] = bytearray(section['BlockLight'])
    
    # Dodaj platformę stone w środku chunku
    center_x = cx * 16 + 8
    center_z = cz * 16 + 8
    
    for dx in range(-2, 3):
        for dz in range(-2, 3):
            bx = (center_x + dx) % 16
            bz = (center_z + dz) % 16
            by = y_level % 16
            idx = by * 256 + bz * 16 + bx
            section['Blocks'][idx] = 1  # stone
    
    level['Sections'] = new_sections
    return chunk_nbt, (cx, cz)


def add_command_block(chunk_nbt, x, y, z, command, y_level=200):
    """Dodaje command block do chunku."""
    level = chunk_nbt.get('Level', {})
    if hasattr(level, 'value'):
        level = level.value
    
    tile_entities = level.get('TileEntities', [])
    if hasattr(tile_entities, 'value'):
        tile_entities = list(tile_entities.value)
    else:
        tile_entities = list(tile_entities)
    
    # Dodaj command block
    cb = {
        'id': 'Control',
        'x': x,
        'y': y,
        'z': z,
        'Command': command,
        'CustomName': '@',
        'TrackOutput': 1
    }
    tile_entities.append(cb)
    level['TileEntities'] = tile_entities
    
    # Ustaw blok command block
    sections = level.get('Sections', [])
    if hasattr(sections, 'value'):
        sections = sections.value
    
    cx = level.get('xPos', 0)
    if hasattr(cx, 'value'):
        cx = cx.value
    cz = level.get('zPos', 0)
    if hasattr(cz, 'value'):
        cz = cz.value
    
    sec_y = y // 16
    for section in sections:
        if hasattr(section, 'value'):
            section = section.value
        if section.get('Y') == sec_y:
            if isinstance(section.get('Blocks'), bytes):
                section['Blocks'] = bytearray(section['Blocks'])
            
            local_x = x % 16
            local_y = y % 16
            local_z = z % 16
            idx = local_y * 256 + local_z * 16 + local_x
            section['Blocks'][idx] = 137  # command block
            break
    
    return chunk_nbt


def save_modified_region(region_file, modified_chunks):
    """Zapisuje zmodyfikowane chunki z powrotem do pliku regionu."""
    # Wczytaj istniejący plik
    with open(region_file, 'rb') as f:
        original_data = bytearray(f.read())
    
    # Modyfikuj chunki
    for (chunk_x, chunk_z), chunk_bytes in modified_chunks.items():
        index = chunk_x + chunk_z * 32
        
        # Pobierz lokalizację
        offset = index * 4
        sector_offset = ((original_data[offset] << 16) | 
                        (original_data[offset + 1] << 8) | 
                        original_data[offset + 2])
        sector_count = original_data[offset + 3]
        
        if sector_offset == 0:
            # Chunk nie istniał - musimy go dodać na końcu pliku
            # Dla uproszczenia pomijamy ten przypadek
            print(f"  Warning: chunk ({chunk_x}, {chunk_z}) nie istniał, pomijam")
            continue
        
        byte_offset = sector_offset * 4096
        
        # Kompresja nowych danych
        compressed = zlib.compress(chunk_bytes)
        new_chunk_data = struct.pack('>I', len(compressed) + 1) + b'\x02' + compressed
        
        # Dopełnij do wielokrotności sektora
        padding_needed = (4096 - (len(new_chunk_data) % 4096)) % 4096
        new_chunk_data_padded = new_chunk_data + b'\x00' * padding_needed
        
        new_sector_count = len(new_chunk_data_padded) // 4096
        
        # Sprawdź czy zmieścimy się w tych samych sektorach
        if new_sector_count > sector_count:
            print(f"  Warning: nowe dane chunku ({chunk_x}, {chunk_z}) większe niż oryginalne")
            # Dla uproszczenia - użyj tylko tyle ile się zmieści
            new_chunk_data_padded = new_chunk_data_padded[:sector_count * 4096]
        
        # Zapisz nowe dane
        original_data[byte_offset:byte_offset + len(new_chunk_data_padded)] = new_chunk_data_padded
    
    # Zapisz plik
    with open(region_file, 'wb') as f:
        f.write(original_data)


def insert_spiral(world_path, radius=5, y_level=200):
    """Wstawia spiralę do istniejącego świata."""
    print(f"Wstawianie spirali R={radius} do {world_path}")
    print(f"Wysokość Y={y_level}")
    
    chunks = generate_spiral_chunks(radius)
    print(f"Wygenerowano {len(chunks)} punktów spirali")
    
    # Grupuj chunki według regionów
    region_chunks = defaultdict(list)
    for cx, cz, step in chunks:
        region_x = cx // 32 if cx >= 0 else (cx - 31) // 32
        region_z = cz // 32 if cz >= 0 else (cz - 31) // 32
        region_chunks[(region_x, region_z)].append((cx, cz, step))
    
    print(f"Chunki podzielone na {len(region_chunks)} regionów")
    
    # Dla każdego regionu
    for (region_x, region_z), region_chunk_list in region_chunks.items():
        region_file = os.path.join(world_path, 'region', f'r.{region_x}.{region_z}.mca')
        
        if not os.path.exists(region_file):
            print(f"  Pominięto region r.{region_x}.{region_z}.mca (nie istnieje)")
            continue
        
        print(f"  Przetwarzanie regionu r.{region_x}.{region_z}.mca ({len(region_chunk_list)} chunków)...")
        
        # Wczytaj region
        parser = AnvilParser(region_file)
        modified = {}
        
        for cx, cz, step in region_chunk_list:
            local_cx = cx % 32 if cx >= 0 else (cx % 32 + 32) % 32
            local_cz = cz % 32 if cz >= 0 else (cz % 32 + 32) % 32
            
            chunk = parser.get_chunk(local_cx, local_cz)
            if not chunk:
                print(f"    Warning: chunk ({cx}, {cz}) nie istnieje w regionie")
                continue
            
            # Modyfikuj chunk
            chunk_nbt = chunk.nbt
            chunk_nbt, (chunk_cx, chunk_cz) = modify_chunk_blocks(chunk_nbt, y_level)
            
            # Zapisz zmiany
            chunk_bytes = write_nbt_to_bytes(chunk_nbt)
            modified[(local_cx, local_cz)] = chunk_bytes
        
        # Zapisz zmodyfikowany region
        if modified:
            save_modified_region(region_file, modified)
            print(f"    Zapisano {len(modified)} zmodyfikowanych chunków")
    
    print("\nGotowe!")


if __name__ == "__main__":
    world_path = os.path.join(os.path.dirname(__file__), '..', '1.7.10', 'world')
    world_path = os.path.normpath(world_path)
    
    print("=" * 60)
    print("WSTAWIANIE SPIRALI DO ISTNIEJĄCEGO ŚWIATA")
    print("=" * 60)
    
    insert_spiral(world_path, radius=5, y_level=200)
