"""
Wstawia bloki ukośne (CuttableBlocks) do mapy Minecraft 1.7.10
Bezpośrednia edycja plików MCA używając nbtlib
"""

import sys
import json
from pathlib import Path
from nbtlib import File, Compound, List, Byte, Int, Float, String, ByteArray
import struct

# Block ID dla CuttableBlock (tymczasowe)
CUTTABLE_BLOCK_ID = 200

def get_region_filename(chunk_x, chunk_z):
    """Oblicza nazwę pliku regionu dla danego chunka"""
    region_x = chunk_x >> 5
    region_z = chunk_z >> 5
    return f"r.{region_x}.{region_z}.mca"

def get_local_chunk_coords(chunk_x, chunk_z):
    """Oblicza lokalne współrzędne chunka w regionie"""
    local_x = chunk_x & 31
    local_z = chunk_z & 31
    return local_x, local_z

def read_chunk_from_region(region_path, local_x, local_z):
    """Odczytuje chunk z pliku regionu"""
    if not region_path.exists():
        return None
    
    with open(region_path, 'rb') as f:
        # Header chunk locations (1024 entries * 4 bytes)
        f.seek(0)
        header = f.read(4096)
        
        # Calculate chunk location offset in header
        chunk_index = local_x + local_z * 32
        location_offset = chunk_index * 4
        
        # Read chunk location
        offset_sectors = struct.unpack('>I', b'\x00' + header[location_offset:location_offset+3])[0]
        sector_count = header[location_offset + 3]
        
        if offset_sectors == 0:
            return None  # Chunk nie istnieje
        
        # Read chunk data
        f.seek(offset_sectors * 4096)
        length = struct.unpack('>I', f.read(4))[0]
        compression_type = f.read(1)[0]
        
        chunk_data = f.read(length - 1)
        
        # Dekompresja
        if compression_type == 1:  # gzip
            import gzip
            chunk_data = gzip.decompress(chunk_data)
        elif compression_type == 2:  # zlib
            import zlib
            chunk_data = zlib.decompress(chunk_data)
        
        # Parsowanie NBT
        from io import BytesIO
        return File.parse(BytesIO(chunk_data), byteorder='big')

def write_chunk_to_region(region_path, local_x, local_z, nbt_data):
    """Zapisuje chunk do pliku regionu"""
    import gzip
    import zlib
    
    # Serializacja NBT
    from io import BytesIO
    buffer_io = BytesIO()
    nbt_data.write(buffer_io, byteorder='big')
    buffer = buffer_io.getvalue()
    
    # Kompresja zlib
    compressed = zlib.compress(buffer)
    
    # Przygotowanie danych chunka
    length = len(compressed) + 1
    chunk_bytes = struct.pack('>I', length) + b'\x02' + compressed
    
    # Padding do pełnych sektorów (4096 bytes)
    sectors_needed = (len(chunk_bytes) + 4095) // 4096
    chunk_bytes += b'\x00' * (sectors_needed * 4096 - len(chunk_bytes))
    
    # Odczyt/creating region file
    if not region_path.exists():
        # Create new region file
        with open(region_path, 'wb') as f:
            # Empty header
            f.write(b'\x00' * 8192)
    
    with open(region_path, 'r+b') as f:
        # Read header
        f.seek(0)
        header = bytearray(f.read(4096))
        
        # Calculate chunk location
        chunk_index = local_x + local_z * 32
        location_offset = chunk_index * 4
        
        # Find free location or overwrite existing
        f.seek(0, 2)  # End of file
        file_size = f.tell()
        
        # Check if chunk already exists
        current_offset = struct.unpack('>I', b'\x00' + header[location_offset:location_offset+3])[0]
        
        if current_offset == 0:
            # New chunk - append at end
            new_offset = (file_size + 4095) // 4096
            header[location_offset:location_offset+3] = struct.pack('>I', new_offset)[1:4]
            header[location_offset + 3] = sectors_needed
            
            f.seek(0)
            f.write(header)
            f.seek(new_offset * 4096)
            f.write(chunk_bytes)
        else:
            # Overwrite existing (assuming enough space)
            header[location_offset + 3] = sectors_needed
            f.seek(0)
            f.write(header)
            f.seek(current_offset * 4096)
            f.write(chunk_bytes)

def get_block_id(block_name):
    """Mapuje nazwę bloku na ID (vanilla 1.7.10)"""
    block_map = {
        "minecraft:stone": 1,
        "minecraft:grass": 2,
        "minecraft:dirt": 3,
        "minecraft:cobblestone": 4,
        "minecraft:planks": 5,
        "minecraft:bedrock": 7,
        "minecraft:sand": 12,
        "minecraft:gravel": 13,
        "minecraft:gold_ore": 14,
        "minecraft:iron_ore": 15,
        "minecraft:coal_ore": 16,
        "minecraft:log": 17,
        "minecraft:leaves": 18,
        "minecraft:glass": 20,
        "minecraft:lapis_ore": 21,
        "minecraft:lapis_block": 22,
        "minecraft:sandstone": 24,
        "minecraft:wool": 35,
        "minecraft:gold_block": 41,
        "minecraft:iron_block": 42,
        "minecraft:brick_block": 45,
        "minecraft:bookshelf": 47,
        "minecraft:mossy_cobblestone": 48,
        "minecraft:obsidian": 49,
        "minecraft:diamond_ore": 56,
        "minecraft:diamond_block": 57,
        "minecraft:crafting_table": 58,
        "minecraft:redstone_ore": 73,
        "minecraft:emerald_ore": 129,
        "minecraft:emerald_block": 133,
        "minecraft:stonebrick": 98,
    }
    return block_map.get(block_name, 1)  # Default to stone

def insert_cuttable_block(chunk_nbt, x, y, z, original_block_id, original_meta, 
                          normal_x, normal_y, normal_z, keep_positive):
    """Wstawia blok ukośny do chunka"""
    
    # Pobierz Level compound
    level = chunk_nbt['Level']
    
    # Pobierz lub utwórz sekcje
    if 'Sections' not in level:
        level['Sections'] = List[Compound]()
    
    sections = level['Sections']
    
    # Znajdź lub utwórz sekcję
    section_y = y // 16
    section = None
    for sec in sections:
        if sec['Y'] == Byte(section_y):
            section = sec
            break
    
    if section is None:
        # Utwórz nową sekcję
        section = Compound({
            'Y': Byte(section_y),
            'Blocks': ByteArray([0] * 4096),
            'Data': ByteArray([0] * 2048),
            'SkyLight': ByteArray([0xFF] * 2048),
            'BlockLight': ByteArray([0] * 2048),
        })
        sections.append(section)
    
    # Oblicz pozycję w sekcji
    local_x = x & 15
    local_y = y & 15
    local_z = z & 15
    block_index = local_y * 256 + local_z * 16 + local_x
    data_index = block_index // 2
    data_shift = (block_index % 2) * 4
    
    # Wstaw blok
    blocks = list(section['Blocks'])
    data = list(section['Data'])
    
    blocks[block_index] = CUTTABLE_BLOCK_ID
    
    # Metadata (4 bity na blok)
    data_byte = data[data_index]
    data[data_index] = (data_byte & ~(0xF << data_shift)) | ((original_meta & 0xF) << data_shift)
    
    section['Blocks'] = ByteArray(blocks)
    section['Data'] = ByteArray(data)
    
    # Dodaj TileEntity
    if 'TileEntities' not in level:
        level['TileEntities'] = List[Compound]()
    
    tile_entities = level['TileEntities']
    
    # Usuń istniejące TE na tej pozycji
    level['TileEntities'] = List[Compound]([
        te for te in tile_entities 
        if not (te.get('x') == Int(x) and te.get('y') == Int(y) and te.get('z') == Int(z))
    ])
    
    # Dodaj nowe TE
    tile_entity = Compound({
        'id': String('CuttableTE'),
        'x': Int(x),
        'y': Int(y),
        'z': Int(z),
        'OriginalBlockID': Int(original_block_id),
        'OriginalMeta': Int(original_meta),
        'NormalX': Float(normal_x),
        'NormalY': Float(normal_y),
        'NormalZ': Float(normal_z),
        'KeepPositive': Byte(1 if keep_positive else 0),
    })
    
    level['TileEntities'].append(tile_entity)
    
    print(f"    Wstawiono blok ukośny at ({x}, {y}, {z})")

def process_chunk(world_path, chunk_x, chunk_z, blocks):
    """Przetwarza pojedynczy chunk"""
    print(f"Processing chunk ({chunk_x}, {chunk_z})")
    
    region_file = Path(world_path) / "region" / get_region_filename(chunk_x, chunk_z)
    local_x, local_z = get_local_chunk_coords(chunk_x, chunk_z)
    
    # Odczytaj chunk
    chunk_nbt = read_chunk_from_region(region_file, local_x, local_z)
    
    if chunk_nbt is None:
        print(f"  Chunk nie istnieje, tworzenie nowego...")
        # Utwórz nowy chunk
        chunk_nbt = File({
            'Level': Compound({
                'xPos': Int(chunk_x),
                'zPos': Int(chunk_z),
                'Sections': List[Compound](),
                'TileEntities': List[Compound](),
            })
        })
    
    # Wstaw bloki
    for block in blocks:
        x = int(block['x'])
        y = int(block['y'])
        z = int(block['z'])
        
        original_block_id = get_block_id(block['original_block'])
        original_meta = int(block['original_meta'])
        
        normal = block['normal']
        normal_x = float(normal[0])
        normal_y = float(normal[1])
        normal_z = float(normal[2])
        
        keep_positive = bool(block['keep_positive'])
        
        insert_cuttable_block(
            chunk_nbt, x, y, z,
            original_block_id, original_meta,
            normal_x, normal_y, normal_z,
            keep_positive
        )
    
    # Zapisz chunk
    write_chunk_to_region(region_file, local_x, local_z, chunk_nbt)
    print(f"  Zapisano chunk ({chunk_x}, {chunk_z})")

def main():
    if len(sys.argv) < 3:
        print("Użycie: python apply_patch_to_world.py <world_path> <patch_json_path>")
        print("Przykład: python apply_patch_to_world.py \"../headless_server/1.7.10/world_cuttable_test\" \"cuttable_test_patch_jvm.json\"")
        return
    
    world_path = sys.argv[1]
    patch_path = sys.argv[2]
    
    print("=== APLIKOWANIE PATCHA CUTTABLE BLOCKS ===")
    print(f"Świat: {world_path}")
    print(f"Patch: {patch_path}")
    
    # Wczytaj patch
    with open(patch_path, 'r') as f:
        patch = json.load(f)
    
    print("\nMetadane:")
    for key, value in patch['metadata'].items():
        print(f"  {key}: {value}")
    
    # Przetwórz chunki
    chunks = patch['chunks']
    print(f"\nPrzetwarzanie {len(chunks)} chunków...")
    
    for chunk_key, chunk_data in chunks.items():
        cx = int(chunk_data['x'])
        cz = int(chunk_data['z'])
        blocks = chunk_data['blocks']
        
        process_chunk(world_path, cx, cz, blocks)
    
    print("\n=== ZAKOŃCZONO ===")
    print("Bloki ukośne zostały wstawione do mapy.")
    print(f"Łącznie wstawiono {sum(len(c['blocks']) for c in chunks.values())} bloków.")
    print("\nNastępne kroki:")
    print("1. Zbuduj mod CuttableBlocks: .\\gradlew.bat build")
    print("2. Skopiuj JAR do headless_server/1.7.10/mods/")
    print("3. Uruchom serwer i przetestuj")

if __name__ == '__main__':
    main()
