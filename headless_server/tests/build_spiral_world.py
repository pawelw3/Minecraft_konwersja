#!/usr/bin/env python3
"""
Buduje spiralny test redstone w świecie Minecraft 1.7.10.
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

from minecraft_map_parser.nbt_parser import parse_nbt, NBTTag


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


def get_chunk_offset_and_size(data, chunk_x, chunk_z):
    """Zwraca offset i rozmiar chunka w sektorach."""
    index = chunk_x + chunk_z * 32
    offset = index * 4
    chunk_data = data[offset:offset + 4]
    sector_offset = ((chunk_data[0] << 16) | (chunk_data[1] << 8) | chunk_data[2])
    sector_count = chunk_data[3]
    return sector_offset, sector_count


def decompress_chunk_data(data, sector_offset):
    """Dekompresuje dane chunka."""
    byte_offset = sector_offset * 4096
    length_data = data[byte_offset:byte_offset + 4]
    length = struct.unpack('>I', length_data)[0]
    compression_type = data[byte_offset + 4]
    compressed_data = data[byte_offset + 5:byte_offset + 5 + length - 1]
    
    if compression_type == 1:
        return gzip.decompress(compressed_data)
    elif compression_type == 2:
        return zlib.decompress(compressed_data)
    else:
        return compressed_data


def compress_chunk_data(data):
    """Kompresuje dane chunka (zlib)."""
    return zlib.compress(data)


def create_new_chunk(chunk_x, chunk_z, y_level=64):
    """Tworzy nowy pusty chunk z podstawowymi danymi."""
    # Struktura NBT chunka 1.7.10
    sections = []
    
    # Tworzymy sekcje dla Y=0-127 (8 sekcji)
    for sec_y in range(8):
        # Pusta sekcja - same bloki powietrza (0)
        blocks = bytearray(4096)  # 16x16x16
        data = bytearray(2048)    # metadata (nibble per block)
        skylight = bytearray(2048)  # pełne światło nieba
        blocklight = bytearray(2048)  # brak światła bloków
        
        sections.append({
            'Y': sec_y,
            'Blocks': bytes(blocks),
            'Data': bytes(data),
            'SkyLight': bytes([0xff] * 2048),  # pełne światło
            'BlockLight': bytes(blocklight)
        })
    
    # Biomy (256 bajtów)
    biomes = bytes([1] * 256)  # plains
    
    chunk_nbt = {
        'Level': {
            'xPos': chunk_x,
            'zPos': chunk_z,
            'LastUpdate': 0,
            'TerrainPopulated': 1,
            'Sections': sections,
            'Biomes': biomes,
            'Entities': [],
            'TileEntities': [],
            'TileTicks': []
        },
        'DataVersion': 0
    }
    
    return chunk_nbt


def set_block(chunk_nbt, x, y, z, block_id, metadata=0):
    """Ustawia blok w chunku."""
    level = chunk_nbt.get('Level', {})
    sections = level.get('Sections', [])
    
    # Znajdź sekcję dla danego Y
    sec_y = y // 16
    local_y = y % 16
    local_x = x % 16
    local_z = z % 16
    
    # Znajdź lub utwórz sekcję
    section = None
    for s in sections:
        if isinstance(s, dict):
            if s.get('Y') == sec_y:
                section = s
                break
        elif isinstance(s, NBTTag):
            if s.get('Y') == sec_y:
                section = s.value if hasattr(s, 'value') else s
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
        sections.append(section)
    
    # Konwertuj do bytearray jeśli potrzeba
    if isinstance(section.get('Blocks'), bytes):
        section['Blocks'] = bytearray(section['Blocks'])
    if isinstance(section.get('Data'), bytes):
        section['Data'] = bytearray(section['Data'])
    
    # Ustaw blok
    index = local_y * 256 + local_z * 16 + local_x
    section['Blocks'][index] = block_id
    
    # Ustaw metadata (nibble per block)
    data_index = index // 2
    is_high_nibble = index % 2 == 1
    if is_high_nibble:
        section['Data'][data_index] = (section['Data'][data_index] & 0x0F) | (metadata << 4)
    else:
        section['Data'][data_index] = (section['Data'][data_index] & 0xF0) | (metadata & 0x0F)
    
    level['Sections'] = sections


def add_tile_entity(chunk_nbt, x, y, z, entity_type, command=""):
    """Dodaje tile entity (np. command block) do chunku."""
    level = chunk_nbt.get('Level', {})
    tile_entities = level.get('TileEntities', [])
    
    if isinstance(tile_entities, NBTTag):
        tile_entities = tile_entities.value if hasattr(tile_entities, 'value') else []
    
    entity = {
        'id': entity_type,
        'x': x,
        'y': y,
        'z': z
    }
    
    if command:
        entity['Command'] = command
        entity['CustomName'] = '@'
        entity['TrackOutput'] = 1
    
    tile_entities.append(entity)
    level['TileEntities'] = tile_entities


def write_nbt(nbt_data):
    """Prosty writer NBT - zwraca bajty."""
    def write_tag(stream, name, value, tag_type):
        stream.write(struct.pack('>B', tag_type))
        stream.write(struct.pack('>H', len(name)))
        stream.write(name.encode('utf-8'))
        write_payload(stream, value, tag_type)
    
    def write_payload(stream, value, tag_type):
        if tag_type == 1:  # BYTE
            stream.write(struct.pack('>b', value))
        elif tag_type == 2:  # SHORT
            stream.write(struct.pack('>h', value))
        elif tag_type == 3:  # INT
            stream.write(struct.pack('>i', value))
        elif tag_type == 4:  # LONG
            stream.write(struct.pack('>q', value))
        elif tag_type == 8:  # STRING
            encoded = value.encode('utf-8')
            stream.write(struct.pack('>H', len(encoded)))
            stream.write(encoded)
        elif tag_type == 7:  # BYTE_ARRAY
            stream.write(struct.pack('>i', len(value)))
            stream.write(value)
        elif tag_type == 10:  # COMPOUND
            for k, v in value.items():
                if isinstance(v, bool):
                    write_tag(stream, k, 1 if v else 0, 1)
                elif isinstance(v, int):
                    write_tag(stream, k, v, 3)
                elif isinstance(v, str):
                    write_tag(stream, k, v, 8)
                elif isinstance(v, bytes):
                    write_tag(stream, k, v, 7)
                elif isinstance(v, list):
                    # List tag
                    stream.write(struct.pack('>B', 9))
                    stream.write(struct.pack('>H', len(k)))
                    stream.write(k.encode('utf-8'))
                    if v:
                        # Określ typ pierwszego elementu
                        first = v[0]
                        if isinstance(first, dict):
                            stream.write(struct.pack('>B', 10))  # COMPOUND
                            stream.write(struct.pack('>i', len(v)))
                            for item in v:
                                write_payload(stream, item, 10)
                        elif isinstance(first, int):
                            stream.write(struct.pack('>B', 3))  # INT
                            stream.write(struct.pack('>i', len(v)))
                            for item in v:
                                stream.write(struct.pack('>i', item))
                    else:
                        stream.write(struct.pack('>B', 0))  # END
                        stream.write(struct.pack('>i', 0))
                elif isinstance(v, dict):
                    write_tag(stream, k, v, 10)
            stream.write(struct.pack('>B', 0))  # END tag
    
    stream = BytesIO()
    write_tag(stream, '', {'Level': nbt_data.get('Level', {})}, 10)
    return stream.getvalue()


def build_spiral_world(world_path, radius=5):
    """Buduje spiralny test w świecie."""
    print(f"Budowanie spirali R={radius} w {world_path}")
    
    chunks = generate_spiral_chunks(radius)
    print(f"Wygenerowano {len(chunks)} punktów spirali")
    
    # Grupuj chunki według regionów
    region_chunks = defaultdict(list)
    for cx, cz, step in chunks:
        region_x = cx // 32 if cx >= 0 else (cx - 31) // 32
        region_z = cz // 32 if cz >= 0 else (cz - 31) // 32
        region_chunks[(region_x, region_z)].append((cx, cz, step))
    
    print(f"Chunki podzielone na {len(region_chunks)} regionów")
    
    # Przygotuj bloki do wstawienia dla każdego chunka
    Y_LEVEL = 64
    
    # ID bloków
    STONE = 1
    REDSTONE_WIRE = 55
    REPEATER = 93
    COMMAND_BLOCK = 137
    REDSTONE_BLOCK = 152
    
    # Dla każdego regionu
    for (region_x, region_z), region_chunk_list in region_chunks.items():
        region_file = os.path.join(world_path, 'region', f'r.{region_x}.{region_z}.mca')
        
        # Przygotuj dane dla chunków w tym regionie
        chunk_data = {}
        
        for cx, cz, step in region_chunk_list:
            local_cx = cx % 32 if cx >= 0 else (cx % 32 + 32) % 32
            local_cz = cz % 32 if cz >= 0 else (cz % 32 + 32) % 32
            
            # Utwórz nowy chunk
            chunk_nbt = create_new_chunk(cx, cz, Y_LEVEL)
            
            # Platforma stone
            center_x = cx * 16 + 8
            center_z = cz * 16 + 8
            for dx in range(-2, 3):
                for dz in range(-2, 3):
                    set_block(chunk_nbt, center_x + dx, Y_LEVEL - 1, center_z + dz, STONE)
            
            chunk_data[(local_cx, local_cz)] = (chunk_nbt, cx, cz, step)
        
        # Dodaj połączenia między chunkami
        for i, (cx, cz, step) in enumerate(chunks):
            if step == 0:
                # Start - redstone block
                center_x = cx * 16 + 8
                center_z = cz * 16 + 8
                local_cx = cx % 32 if cx >= 0 else (cx % 32 + 32) % 32
                local_cz = cz % 32 if cz >= 0 else (cz % 32 + 32) % 32
                if (local_cx, local_cz) in chunk_data:
                    chunk_nbt, _, _, _ = chunk_data[(local_cx, local_cz)]
                    set_block(chunk_nbt, center_x, Y_LEVEL, center_z, REDSTONE_BLOCK)
                    chunk_data[(local_cx, local_cz)] = (chunk_nbt, cx, cz, step)
                continue
            
            # Znajdź poprzedni chunk
            prev_cx, prev_cz, prev_step = chunks[i-1]
            
            center_x = prev_cx * 16 + 8
            center_z = prev_cz * 16 + 8
            
            # Kierunek do bieżącego chunka
            if cx > prev_cx:
                direction = 1  # east
            elif cx < prev_cx:
                direction = 3  # west
            elif cz > prev_cz:
                direction = 2  # south
            else:
                direction = 0  # north
            
            # Ustaw repeater w poprzednim chunku
            local_cx = prev_cx % 32 if prev_cx >= 0 else (prev_cx % 32 + 32) % 32
            local_cz = prev_cz % 32 if prev_cz >= 0 else (prev_cz % 32 + 32) % 32
            if (local_cx, local_cz) in chunk_data:
                chunk_nbt, _, _, _ = chunk_data[(local_cx, local_cz)]
                set_block(chunk_nbt, center_x, Y_LEVEL, center_z, REPEATER, direction)
                chunk_data[(local_cx, local_cz)] = (chunk_nbt, prev_cx, prev_cz, prev_step)
            
            # Command block w bieżącym chunku
            curr_center_x = cx * 16 + 8
            curr_center_z = cz * 16 + 8
            cb_x = curr_center_x + 1
            cb_z = curr_center_z
            
            local_cx = cx % 32 if cx >= 0 else (cx % 32 + 32) % 32
            local_cz = cz % 32 if cz >= 0 else (cz % 32 + 32) % 32
            if (local_cx, local_cz) in chunk_data:
                chunk_nbt, _, _, _ = chunk_data[(local_cx, local_cz)]
                set_block(chunk_nbt, cb_x, Y_LEVEL, cb_z, COMMAND_BLOCK)
                command = f"/say [PROBE] REACHED cx={cx} cz={cz} step={step}"
                add_tile_entity(chunk_nbt, cb_x, Y_LEVEL, cb_z, 'Control', command)
                chunk_data[(local_cx, local_cz)] = (chunk_nbt, cx, cz, step)
        
        # Zapisz region
        os.makedirs(os.path.dirname(region_file), exist_ok=True)
        save_region(region_file, chunk_data)
        print(f"  Zapisano region r.{region_x}.{region_z}.mca ({len(region_chunk_list)} chunków)")
    
    print("\nGotowe! Spirala została zbudowana.")
    return len(chunks)


def save_region(filepath, chunk_data):
    """Zapisuje plik regionu MCA."""
    # Inicjalizuj nagłówki
    locations = bytearray(4096)  # 1024 * 4 bajty
    timestamps = bytearray(4096)  # 1024 * 4 bajty
    chunks_bytes = bytearray()
    
    sector_offset = 2  # Zaczynamy po nagłówkach (2 sektory)
    
    for (local_cx, local_cz), (chunk_nbt, global_cx, global_cz, step) in sorted(chunk_data.items()):
        index = local_cx + local_cz * 32
        
        # Zapisz chunk NBT
        nbt_bytes = write_nbt(chunk_nbt)
        compressed = zlib.compress(nbt_bytes)
        
        # Długość + kompresja + dane
        chunk_bytes = struct.pack('>I', len(compressed) + 1) + b'\x02' + compressed
        
        # Dopełnij do wielokrotności 4096
        padding_needed = (4096 - (len(chunk_bytes) % 4096)) % 4096
        chunk_bytes_padded = chunk_bytes + b'\x00' * padding_needed
        
        sector_count = len(chunk_bytes_padded) // 4096
        
        # Zapisz w nagłówku
        loc_index = index * 4
        locations[loc_index] = (sector_offset >> 16) & 0xFF
        locations[loc_index + 1] = (sector_offset >> 8) & 0xFF
        locations[loc_index + 2] = sector_offset & 0xFF
        locations[loc_index + 3] = sector_count
        
        # Timestamp
        ts_index = index * 4
        timestamps[ts_index:ts_index + 4] = struct.pack('>I', 0)
        
        # Dodaj dane chunka
        chunks_bytes.extend(chunk_bytes_padded)
        
        sector_offset += sector_count
    
    # Zapisz plik
    with open(filepath, 'wb') as f:
        f.write(locations)
        f.write(timestamps)
        f.write(chunks_bytes)


if __name__ == "__main__":
    world_path = os.path.join(os.path.dirname(__file__), '..', '1.7.10', 'world_spiral_test')
    world_path = os.path.normpath(world_path)
    
    print("=" * 60)
    print("BUDOWANIE ŚWIATA TESTOWEGO - SPIRALA REDSTONE")
    print("=" * 60)
    
    count = build_spiral_world(world_path, radius=5)
    
    print(f"\nŚwiat testowy utworzony w:")
    print(f"  {world_path}")
    print(f"\nAby uruchomić test:")
    print(f"  1. Zmień level-name w server.properties na 'world_spiral_test'")
    print(f"  2. Uruchom serwer: cd headless_server\\1.7.10 && .\\run.bat")
    print(f"  3. Obserwuj logi - powinny pojawić się wpisy [PROBE] REACHED...")
