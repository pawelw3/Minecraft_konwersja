"""
Wstawianie schematica (.schematic) do mapy Minecraft (format MCA/Anvil).
Obsługuje format MC 1.7.10.
"""

import struct
import gzip
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
import zlib

from minecraft_map_parser.nbt_parser import NBTTag, NBTParser, decompress_nbt


@dataclass
class BlockData:
    """Dane bloku."""
    block_id: int
    meta: int
    tile_entity: Optional[Dict] = None


class SchematicLoader:
    """Ładuje dane z pliku .schematic."""
    
    def __init__(self, schematic_path: Path):
        self.path = schematic_path
        self.width = 0
        self.height = 0
        self.length = 0
        self.offset_x = 0
        self.offset_y = 0
        self.offset_z = 0
        self.blocks = []
        self.data = []
        self.tile_entities = []
        self._load()
    
    def _load(self):
        """Ładuje dane z pliku schematic."""
        with open(self.path, 'rb') as f:
            compressed_data = f.read()
        
        # Dekompresuj gzip
        data = gzip.decompress(compressed_data)
        
        # Parsuj NBT
        parser = NBTParser(data)
        root = parser.parse()
        
        if root.type != NBTTag.TAG_COMPOUND:
            raise ValueError("Invalid schematic format")
        
        # Odczytaj wymiary
        self.width = root["Width"]
        self.height = root["Height"]
        self.length = root["Length"]
        
        print(f"Schematic loaded: {self.width}x{self.height}x{self.length}")
        
        # Odczytaj bloki i dane
        self.blocks = root["Blocks"]
        self.data = root["Data"]
        
        # Odczytaj Tile Entities
        if "TileEntities" in root:
            te_list = root["TileEntities"]
            if isinstance(te_list, list):
                self.tile_entities = te_list
        
        # Odczytaj offsety (opcjonalne, dla kompatybilności ze schematami bez nich)
        if "WEOffsetX" in root:
            self.offset_x = root["WEOffsetX"]
        if "WEOffsetY" in root:
            self.offset_y = root["WEOffsetY"]
        if "WEOffsetZ" in root:
            self.offset_z = root["WEOffsetZ"]
        
        print(f"Tile entities: {len(self.tile_entities)}")
        print(f"Offsets: ({self.offset_x}, {self.offset_y}, {self.offset_z})")
    
    def _get_te_pos(self, tile_entity, x: int, y: int, z: int) -> bool:
        """Sprawdza czy Tile Entity jest na danej pozycji."""
        # Format NBTTag
        if isinstance(tile_entity, NBTTag) and tile_entity.type == NBTTag.TAG_COMPOUND:
            te_x = tile_entity.get("x")
            te_y = tile_entity.get("y")
            te_z = tile_entity.get("z")
            if te_x == x and te_y == y and te_z == z:
                return True
        # Format dict {str: NBTTag} - z NBTParser
        elif isinstance(tile_entity, dict):
            te_x = tile_entity.get('x')
            te_y = tile_entity.get('y')
            te_z = tile_entity.get('z')
            # Wartości to NBTTag, bierzemy .value
            if isinstance(te_x, NBTTag): te_x = te_x.value
            if isinstance(te_y, NBTTag): te_y = te_y.value
            if isinstance(te_z, NBTTag): te_z = te_z.value
            if te_x == x and te_y == y and te_z == z:
                return True
        # Format tuple (TAG, dict) - z naszego NBTWritera
        elif isinstance(tile_entity, tuple) and len(tile_entity) == 2:
            tag_type, te_data = tile_entity
            if tag_type == NBTTag.TAG_COMPOUND:
                te_x = te_data.get('x')
                te_y = te_data.get('y')
                te_z = te_data.get('z')
                # Wartości mogą być tuple (type, value)
                if isinstance(te_x, tuple): te_x = te_x[1]
                if isinstance(te_y, tuple): te_y = te_y[1]
                if isinstance(te_z, tuple): te_z = te_z[1]
                if te_x == x and te_y == y and te_z == z:
                    return True
        return False
    
    def get_block(self, x: int, y: int, z: int) -> BlockData:
        """Pobiera blok na danej pozycji (współrzędne schematica)."""
        if not (0 <= x < self.width and 0 <= y < self.height and 0 <= z < self.length):
            return BlockData(0, 0)  # Air
        
        index = y * self.width * self.length + z * self.width + x
        block_id = self.blocks[index] & 0xFF
        meta = self.data[index] & 0x0F
        
        # Znajdź Tile Entity dla tej pozycji
        te = None
        for tile_entity in self.tile_entities:
            if self._get_te_pos(tile_entity, x, y, z):
                te = tile_entity
                break
        
        return BlockData(block_id, meta, te)


class MCRegionWriter:
    """Writer dla plików regionu MCA (Minecraft Anvil)."""
    
    SECTOR_SIZE = 4096
    
    def __init__(self, region_path: Path):
        self.region_path = region_path
        # Przechowujemy chunki jako (raw_nbt_bytes, is_compressed)
        # Nowe chunki: is_compressed=False
        # Istniejące chunki (jeśli wczytamy): is_compressed=True
        self.chunks: Dict[Tuple[int, int], Tuple[bytes, bool]] = {}
    
    def set_chunk(self, chunk_x: int, chunk_z: int, chunk_nbt: bytes):
        """Ustawia dane chunka (surowe NBT, nieskompresowane)."""
        self.chunks[(chunk_x, chunk_z)] = (chunk_nbt, False)
    
    def save(self):
        """Zapisuje plik regionu."""
        self.region_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Sortuj chunki
        sorted_chunks = sorted(self.chunks.items(), key=lambda x: x[0])
        
        # Przygotuj location table
        location_table = bytearray(4096)
        timestamp_table = bytearray(4096)
        
        # Dane chunków
        chunk_data_sectors = bytearray()
        current_sector = 2  # Zacznij po headerach (2 sektory)
        
        for (cx, cz), (chunk_data, is_compressed) in sorted_chunks:
            # Jeśli dane nie są skompresowane, skompresuj je
            if not is_compressed:
                compressed = zlib.compress(chunk_data)
            else:
                compressed = chunk_data
            
            # Nagłówek: długość (4 bajty) + typ kompresji (1 bajt = 2 dla zlib)
            full_chunk = struct.pack('>I', len(compressed) + 1) + b'\x02' + compressed
            
            # Dopełnij do wielokrotności sektora
            padding_needed = (self.SECTOR_SIZE - (len(full_chunk) % self.SECTOR_SIZE)) % self.SECTOR_SIZE
            full_chunk += b'\x00' * padding_needed
            
            sectors_needed = len(full_chunk) // self.SECTOR_SIZE
            
            # Zapisz w location table
            idx = cz * 32 + cx
            location_table[idx * 4] = (current_sector >> 16) & 0xFF
            location_table[idx * 4 + 1] = (current_sector >> 8) & 0xFF
            location_table[idx * 4 + 2] = current_sector & 0xFF
            location_table[idx * 4 + 3] = sectors_needed
            
            # Timestamp (current time)
            import time
            ts = int(time.time())
            timestamp_table[idx * 4] = (ts >> 24) & 0xFF
            timestamp_table[idx * 4 + 1] = (ts >> 16) & 0xFF
            timestamp_table[idx * 4 + 2] = (ts >> 8) & 0xFF
            timestamp_table[idx * 4 + 3] = ts & 0xFF
            
            # Dodaj dane
            chunk_data_sectors.extend(full_chunk)
            current_sector += sectors_needed
        
        # Zapisz plik
        with open(self.region_path, 'wb') as f:
            f.write(location_table)
            f.write(timestamp_table)
            f.write(chunk_data_sectors)
        
        print(f"Saved region: {self.region_path}")


def create_chunk_nbt(blocks: Dict[Tuple[int, int, int], BlockData], 
                     chunk_x: int, chunk_z: int) -> bytes:
    """Tworzy dane NBT dla chunka."""
    
    # Inicjalizuj sekcje (16 sekcji po 16 bloków wysokości)
    sections = [None] * 16
    
    for (x, y, z), block in blocks.items():
        # Lokalne współrzędne w chunku
        local_x = x % 16
        local_z = z % 16
        section_idx = y // 16
        local_y = y % 16
        
        if not (0 <= section_idx < 16):
            continue
        
        if sections[section_idx] is None:
            # Inicjalizuj sekcję
            sections[section_idx] = {
                'blocks': bytearray(4096),
                'data': bytearray(2048),
                'sky_light': bytearray(2048),
                'block_light': bytearray(2048),
            }
        
        section = sections[section_idx]
        block_idx = local_y * 16 * 16 + local_z * 16 + local_x
        
        section['blocks'][block_idx] = block.block_id
        
        # Metadata (nibble - 4 bity na blok)
        data_idx = block_idx // 2
        is_high_nibble = block_idx % 2 == 1
        if is_high_nibble:
            section['data'][data_idx] = (section['data'][data_idx] & 0x0F) | ((block.meta & 0x0F) << 4)
        else:
            section['data'][data_idx] = (section['data'][data_idx] & 0xF0) | (block.meta & 0x0F)
        
        # Domyślne oświetlenie
        sky_light_idx = data_idx
        if is_high_nibble:
            section['sky_light'][sky_light_idx] = (section['sky_light'][sky_light_idx] & 0x0F) | 0xF0
        else:
            section['sky_light'][sky_light_idx] = (section['sky_light'][sky_light_idx] & 0xF0) | 0x0F
    
    # Buduj sekcje NBT
    section_list = []
    for i, section in enumerate(sections):
        if section is not None:
            # Zamień bytearray na bytes dla NBT
            section_compound = {
                'Y': (NBTWriter.TAG_BYTE, i),
                'Blocks': (NBTWriter.TAG_BYTE_ARRAY, bytes(section['blocks'])),
                'Data': (NBTWriter.TAG_BYTE_ARRAY, bytes(section['data'])),
                'SkyLight': (NBTWriter.TAG_BYTE_ARRAY, bytes(section['sky_light'])),
                'BlockLight': (NBTWriter.TAG_BYTE_ARRAY, bytes(section['block_light'])),
            }
            section_list.append((NBTWriter.TAG_COMPOUND, section_compound))
    
    # Biomes (256 bytes - 16x16)
    biomes = bytes([1] * 256)  # Plains
    
    # Height map (256 ints)
    height_map = [64] * 256
    
    # Buduj root compound
    level_compound = {
        'xPos': (NBTWriter.TAG_INT, chunk_x),
        'zPos': (NBTWriter.TAG_INT, chunk_z),
        'LastUpdate': (NBTWriter.TAG_LONG, 0),
        'LightPopulated': (NBTWriter.TAG_BYTE, 1),
        'TerrainPopulated': (NBTWriter.TAG_BYTE, 1),
        'V': (NBTWriter.TAG_BYTE, 1),
        'InhabitedTime': (NBTWriter.TAG_LONG, 0),
        'Biomes': (NBTWriter.TAG_BYTE_ARRAY, biomes),
        'HeightMap': (NBTWriter.TAG_INT_ARRAY, height_map),
        'Sections': (NBTWriter.TAG_LIST, section_list),
        'Entities': (NBTWriter.TAG_LIST, []),
        'TileEntities': (NBTWriter.TAG_LIST, []),
    }
    
    # Dodaj Tile Entities
    tile_entities = []
    for (x, y, z), block in blocks.items():
        if block.tile_entity:
            te_compound = convert_tile_entity_nbt(block.tile_entity, x, y, z)
            if te_compound:
                tile_entities.append((NBTWriter.TAG_COMPOUND, te_compound))
    
    if tile_entities:
        level_compound['TileEntities'] = (NBTWriter.TAG_LIST, tile_entities)
    
    root_compound = {
        'Level': (NBTWriter.TAG_COMPOUND, level_compound),
        'DataVersion': (NBTWriter.TAG_INT, 0),  # MC 1.7.10
    }
    
    # Zapisz do NBT
    writer = NBTWriter()
    return writer.write('', NBTWriter.TAG_COMPOUND, root_compound)


def convert_nbt_value_to_tuple(value):
    """Konwertuje wartość (NBTTag, tuple, lub inna) na tuple (type, value)."""
    if isinstance(value, NBTTag):
        return convert_nbt_tag_to_tuple(value)
    elif isinstance(value, tuple) and len(value) == 2:
        # Już tuple (type, value)
        return value
    elif isinstance(value, dict):
        # Dict z NTagami - konwertuj wszystkie wartości
        return (NBTWriter.TAG_COMPOUND, {k: convert_nbt_value_to_tuple(v) for k, v in value.items()})
    elif isinstance(value, list):
        # Lista - konwertuj elementy
        return (NBTWriter.TAG_LIST, [convert_nbt_value_to_tuple(item) for item in value])
    else:
        # Inna wartość - zgadnij typ
        if isinstance(value, int):
            if -128 <= value <= 127:
                return (NBTWriter.TAG_BYTE, value)
            elif -32768 <= value <= 32767:
                return (NBTWriter.TAG_SHORT, value)
            else:
                return (NBTWriter.TAG_INT, value)
        elif isinstance(value, str):
            return (NBTWriter.TAG_STRING, value)
        elif isinstance(value, bytes):
            return (NBTWriter.TAG_BYTE_ARRAY, value)
        return (NBTWriter.TAG_STRING, str(value))


def convert_tile_entity_nbt(te_tag, world_x: int, world_y: int, world_z: int) -> Dict:
    """Konwertuje Tile Entity z schematica na format świata."""
    result = {}
    
    # Obsługa dict {str: NBTTag} - z NBTParser
    if isinstance(te_tag, dict):
        for key, value in te_tag.items():
            if key == 'x':
                result['x'] = (NBTWriter.TAG_INT, world_x)
            elif key == 'y':
                result['y'] = (NBTWriter.TAG_INT, world_y)
            elif key == 'z':
                result['z'] = (NBTWriter.TAG_INT, world_z)
            else:
                result[key] = convert_nbt_value_to_tuple(value)
        return result
    
    # Obsługa tuple (TAG, dict) z naszego NBTWritera
    elif isinstance(te_tag, tuple) and len(te_tag) == 2:
        tag_type, te_data = te_tag
        if tag_type != NBTTag.TAG_COMPOUND:
            return None
        
        for key, value in te_data.items():
            if key == 'x':
                result['x'] = (NBTWriter.TAG_INT, world_x)
            elif key == 'y':
                result['y'] = (NBTWriter.TAG_INT, world_y)
            elif key == 'z':
                result['z'] = (NBTWriter.TAG_INT, world_z)
            else:
                # Value może być już tuple (type, value) z create_*
                if isinstance(value, tuple) and len(value) == 2:
                    result[key] = value
                else:
                    result[key] = convert_nbt_value_to_tuple(value)
        
        return result
    
    # Obsługa NBTTag (z innych źródeł)
    elif isinstance(te_tag, NBTTag) and te_tag.type == NBTTag.TAG_COMPOUND:
        for key, tag in te_tag.value.items() if isinstance(te_tag.value, dict) else []:
            if key == 'x':
                result['x'] = (NBTWriter.TAG_INT, world_x)
            elif key == 'y':
                result['y'] = (NBTWriter.TAG_INT, world_y)
            elif key == 'z':
                result['z'] = (NBTWriter.TAG_INT, world_z)
            else:
                result[key] = convert_nbt_tag_to_tuple(tag)
        
        return result
    
    return None


def convert_nbt_tag_to_tuple(tag) -> tuple:
    """Konwertuje NBTTag na tuple (type, value)."""
    # Obsługa dict (zagnieżdżone struktury z NBTParser)
    if isinstance(tag, dict):
        return (NBTWriter.TAG_COMPOUND, {k: convert_nbt_value_to_tuple(v) for k, v in tag.items()})
    
    # Obsługa NBTTag
    if not isinstance(tag, NBTTag):
        return convert_nbt_value_to_tuple(tag)
    
    if tag.type == NBTTag.TAG_BYTE:
        return (NBTWriter.TAG_BYTE, tag.value)
    elif tag.type == NBTTag.TAG_SHORT:
        return (NBTWriter.TAG_SHORT, tag.value)
    elif tag.type == NBTTag.TAG_INT:
        return (NBTWriter.TAG_INT, tag.value)
    elif tag.type == NBTTag.TAG_LONG:
        return (NBTWriter.TAG_LONG, tag.value)
    elif tag.type == NBTTag.TAG_STRING:
        return (NBTWriter.TAG_STRING, tag.value)
    elif tag.type == NBTTag.TAG_BYTE_ARRAY:
        return (NBTWriter.TAG_BYTE_ARRAY, tag.value)
    elif tag.type == NBTTag.TAG_LIST:
        items = [convert_nbt_tag_to_tuple(item) for item in tag.value]
        return (NBTWriter.TAG_LIST, items)
    elif tag.type == NBTTag.TAG_COMPOUND:
        items = {k: convert_nbt_tag_to_tuple(v) for k, v in tag.value.items()}
        return (NBTWriter.TAG_COMPOUND, items)
    else:
        return (tag.type, tag.value)


# Import NBTWriter at the end to avoid circular import
from minecraft_map_parser.nbt_writer import NBTWriter


def insert_schematic_into_world(
    schematic_path: Path,
    world_path: Path,
    target_x: int = 0,
    target_y: int = 64,
    target_z: int = 0
):
    """
    Wstawia schematic do świata Minecraft.
    
    Args:
        schematic_path: Ścieżka do pliku .schematic
        world_path: Ścieżka do folderu świata
        target_x: Docelowa współrzędna X (w świecie)
        target_y: Docelowa współrzędna Y (w świecie)
        target_z: Docelowa współrzędna Z (w świecie)
    """
    print(f"Wstawianie {schematic_path} do {world_path}")
    print(f"Docelowa pozycja: ({target_x}, {target_y}, {target_z})")
    
    # Załaduj schematic
    schematic = SchematicLoader(schematic_path)
    
    # Zbierz bloki pogrupowane według chunków
    chunk_blocks: Dict[Tuple[int, int], Dict[Tuple[int, int, int], BlockData]] = {}
    
    for sy in range(schematic.height):
        for sz in range(schematic.length):
            for sx in range(schematic.width):
                block = schematic.get_block(sx, sy, sz)
                
                if block.block_id == 0:  # Skip air
                    continue
                
                # Oblicz współrzędne świata (dodaj offsety z schematica)
                world_x = target_x + sx + schematic.offset_x
                world_y = target_y + sy + schematic.offset_y
                world_z = target_z + sz + schematic.offset_z
                
                # Znajdź chunk
                chunk_x = world_x // 16
                chunk_z = world_z // 16
                
                if (chunk_x, chunk_z) not in chunk_blocks:
                    chunk_blocks[(chunk_x, chunk_z)] = {}
                
                chunk_blocks[(chunk_x, chunk_z)][(world_x, world_y, world_z)] = block
    
    print(f"Bloki rozłożone na {len(chunk_blocks)} chunków")
    
    # Zapisz każdy chunk
    for (chunk_x, chunk_z), blocks in chunk_blocks.items():
        # Znajdź plik regionu
        region_x = chunk_x // 32
        region_z = chunk_z // 32
        
        region_file = world_path / "region" / f"r.{region_x}.{region_z}.mca"
        
        # Lokalne współrzędne chunka w regionie
        local_chunk_x = chunk_x % 32
        local_chunk_z = chunk_z % 32
        
        # Stwórz dane chunka
        chunk_nbt = create_chunk_nbt(blocks, chunk_x, chunk_z)
        
        # Załaduj/utwórz region i ustaw chunk
        region_writer = MCRegionWriter(region_file)
        region_writer.set_chunk(local_chunk_x, local_chunk_z, chunk_nbt)
        region_writer.save()
    
    print("Zakończono wstawianie schematica!")


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 3:
        print("Użycie: python schematic_to_world.py <schematic.schematic> <world_path> [x] [y] [z]")
        sys.exit(1)
    
    schematic_path = Path(sys.argv[1])
    world_path = Path(sys.argv[2])
    x = int(sys.argv[3]) if len(sys.argv) > 3 else 0
    y = int(sys.argv[4]) if len(sys.argv) > 4 else 64
    z = int(sys.argv[5]) if len(sys.argv) > 5 else 0
    
    insert_schematic_into_world(schematic_path, world_path, x, y, z)
