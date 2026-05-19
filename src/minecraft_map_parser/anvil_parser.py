"""
Parser formatu Anvil (MCA) dla Minecraft.
Obsługuje pliki regionów z chunkami.
"""

import struct
from dataclasses import dataclass
from typing import List, Optional, Dict, Any, Tuple
from io import BytesIO
import zlib

from .nbt_parser import parse_nbt, NBTTag


@dataclass
class ChunkData:
    """Dane pojedynczego chunka."""
    x: int  # współrzędna chunka X
    z: int  # współrzędna chunka Z
    nbt: NBTTag  # surowe dane NBT
    
    def get_sections(self) -> List[Dict[str, Any]]:
        """Zwraca sekcje chunka (16x16x16 bloków)."""
        level = self.nbt.get('Level', {})
        if isinstance(level, NBTTag):
            sections = level.get('Sections', [])
        else:
            sections = level.get('Sections', [])
        
        if sections is None:
            return []
        
        # Jeśli sections to NBTTag (lista), wyciągnij value
        if isinstance(sections, NBTTag):
            sections = sections.value
        if sections is None:
            return []
        
        result = []
        for section in sections:
            if isinstance(section, NBTTag):
                section = section.value
            if isinstance(section, dict):
                result.append(section)
        return result
    
    def _nbt_to_python(self, value: Any) -> Any:
        """Rekurencyjnie konwertuje NBT na zwykłe typy Python."""
        if isinstance(value, NBTTag):
            if value.type == NBTTag.TAG_COMPOUND:
                return {k: self._nbt_to_python(v) for k, v in value.value.items()}
            elif value.type == NBTTag.TAG_LIST:
                return [self._nbt_to_python(v) for v in value.value]
            else:
                return value.value
        elif isinstance(value, dict):
            return {k: self._nbt_to_python(v) for k, v in value.items()}
        elif isinstance(value, list):
            return [self._nbt_to_python(v) for v in value]
        else:
            return value
    
    def get_tile_entities(self) -> List[Dict[str, Any]]:
        """Zwraca listę tile entities w chunku."""
        level = self.nbt.get('Level', {})
        if isinstance(level, NBTTag):
            entities = level.get('TileEntities', [])
        else:
            entities = level.get('TileEntities', [])
        
        if entities is None:
            return []
        
        # Jeśli entities to NBTTag (lista), wyciągnij value
        if isinstance(entities, NBTTag):
            entities = entities.value
        if entities is None:
            return []
        
        result = []
        for entity in entities:
            if isinstance(entity, NBTTag):
                entity = entity.value
            if isinstance(entity, dict):
                # Rekurencyjnie przetwórz wszystkie wartości NBT
                result.append(self._nbt_to_python(entity))
        return result
    
    def get_entities(self) -> List[Dict[str, Any]]:
        """Zwraca listę entities (mobów, przedmiotów) w chunku."""
        level = self.nbt.get('Level', {})
        if isinstance(level, NBTTag):
            entities = level.get('Entities', [])
        else:
            entities = level.get('Entities', [])
        
        if entities is None:
            return []
        
        # Jeśli entities to NBTTag (lista), wyciągnij value
        if isinstance(entities, NBTTag):
            entities = entities.value
        if entities is None:
            return []
        
        result = []
        for entity in entities:
            if isinstance(entity, NBTTag):
                entity = entity.value
            if isinstance(entity, dict):
                result.append(entity)
        return result
    
    def get_biomes(self) -> Optional[bytes]:
        """Zwraca dane biomów (256 bajtów)."""
        level = self.nbt.get('Level', {})
        if isinstance(level, NBTTag):
            biomes = level.get('Biomes', None)
        else:
            biomes = level.get('Biomes', None)
        
        if biomes is None:
            return None
        
        if isinstance(biomes, NBTTag):
            return biomes.value
        return biomes
    
    def get_block_ids_from_sections(self) -> List[int]:
        """
        Zwraca listę wszystkich ID bloków z sekcji chunka.
        
        WAŻNE: W Minecraft 1.7.10 bloki o ID > 255 wymagają odczytu 
        z tablicy Add/AddBlocks (dodatkowe 4 bity na blok).
        
        Format:
        - Blocks: 4096 bajtów (8 bitów na blok, ID 0-255)
        - Add/AddBlocks: 2048 bajtów (4 bity na blok, górne 4 bity ID 256-4095)
        - Data: 2048 bajtów (metadata)
        
        Pełne ID = (Add[nibble] << 8) | Blocks[byte]
        
        Returns:
            Lista pełnych ID bloków (0-4095) znalezionych w sekcjach
        """
        block_ids = set()
        sections = self.get_sections()
        
        for section in sections:
            if not isinstance(section, dict):
                continue
            
            # Pobierz tablice
            blocks = section.get('Blocks')
            add = section.get('Add') or section.get('AddBlocks')  # Obie nazwy używane w różnych wersjach
            
            if blocks is None:
                continue
            
            # Konwertuj z NBTTag jeśli potrzeba
            if isinstance(blocks, NBTTag):
                blocks = blocks.value
            if isinstance(add, NBTTag):
                add = add.value
            
            if not isinstance(blocks, (bytes, bytearray, list)):
                continue
            
            # Przetwarzaj każdy blok w sekcji (4096 = 16x16x16)
            for i in range(4096):
                if i >= len(blocks):
                    break
                
                # Dolne 8 bitów ID z tablicy Blocks
                low = blocks[i] & 0xFF
                
                # Górne 4 bity ID z tablicy Add (jeśli istnieje)
                high = 0
                if add and i // 2 < len(add):
                    # Każdy bajt w Add zawiera 2 nibbles (dwa bloki)
                    # Parzyste i: dolny nibble, nieparzyste i: górny nibble
                    if i % 2 == 0:
                        high = add[i // 2] & 0x0F
                    else:
                        high = (add[i // 2] >> 4) & 0x0F
                
                # Pełne ID bloku (12 bitów)
                full_id = (high << 8) | low
                block_ids.add(full_id)
        
        return sorted(list(block_ids))

    def get_blocks_and_metadata_at_positions(self) -> Dict[Tuple[int, int, int], Tuple[int, int]]:
        """Return {(local_x, global_y, local_z): (block_id, metadata)}.

        local_x and local_z are 0-15 (position within the chunk).
        metadata is the 4-bit value from the Data nibble array.
        """
        result: Dict[Tuple[int, int, int], Tuple[int, int]] = {}
        for section in self.get_sections():
            if not isinstance(section, dict):
                continue

            section_y = section.get('Y', 0)
            if isinstance(section_y, NBTTag):
                section_y = section_y.value
            section_y = int(section_y) if section_y else 0

            blocks = section.get('Blocks')
            add = section.get('Add') or section.get('AddBlocks')
            data_arr = section.get('Data')

            if blocks is None:
                continue
            if isinstance(blocks, NBTTag):
                blocks = blocks.value
            if isinstance(add, NBTTag):
                add = add.value
            if isinstance(data_arr, NBTTag):
                data_arr = data_arr.value
            if not isinstance(blocks, (bytes, bytearray, list)):
                continue

            for y_in_section in range(16):
                for z in range(16):
                    for x in range(16):
                        i = y_in_section * 256 + z * 16 + x
                        if i >= len(blocks):
                            break

                        low = blocks[i] & 0xFF
                        high = 0
                        if add and i // 2 < len(add):
                            if i % 2 == 0:
                                high = add[i // 2] & 0x0F
                            else:
                                high = (add[i // 2] >> 4) & 0x0F
                        full_id = (high << 8) | low

                        meta = 0
                        if data_arr and i // 2 < len(data_arr):
                            if i % 2 == 0:
                                meta = data_arr[i // 2] & 0x0F
                            else:
                                meta = (data_arr[i // 2] >> 4) & 0x0F

                        global_y = section_y * 16 + y_in_section
                        result[(x, global_y, z)] = (full_id, meta)

        return result

    def get_blocks_at_positions(self) -> Dict[Tuple[int, int, int], int]:
        """
        Zwraca mapę pozycji bloków do ich ID.
        
        Uwzględnia Add/AddBlocks dla bloków o ID > 255.
        
        Returns:
            Słownik {(x, y, z): block_id, ...}
        """
        blocks_map = {}
        sections = self.get_sections()
        
        for section in sections:
            if not isinstance(section, dict):
                continue
            
            # Pobierz Y sekcji (0-15 dla chunka, odpowiada 0-255 w świecie)
            section_y = section.get('Y', 0)
            if isinstance(section_y, NBTTag):
                section_y = section_y.value
            section_y = int(section_y) if section_y else 0
            
            blocks = section.get('Blocks')
            add = section.get('Add') or section.get('AddBlocks')
            
            if blocks is None:
                continue
            
            # Konwertuj z NBTTag jeśli potrzeba
            if isinstance(blocks, NBTTag):
                blocks = blocks.value
            if isinstance(add, NBTTag):
                add = add.value
            
            if not isinstance(blocks, (bytes, bytearray, list)):
                continue
            
            # Przetwarzaj każdy blok w sekcji
            # Layout: dla każdego Y w sekcji, potem Z, potem X
            for y_in_section in range(16):
                for z in range(16):
                    for x in range(16):
                        i = y_in_section * 256 + z * 16 + x
                        
                        if i >= len(blocks):
                            break
                        
                        # Dolne 8 bitów ID
                        low = blocks[i] & 0xFF
                        
                        # Górne 4 bity z Add
                        high = 0
                        if add and i // 2 < len(add):
                            if i % 2 == 0:
                                high = add[i // 2] & 0x0F
                            else:
                                high = (add[i // 2] >> 4) & 0x0F
                        
                        full_id = (high << 8) | low
                        
                        # Globalna wysokość Y w chunku
                        global_y = section_y * 16 + y_in_section
                        
                        blocks_map[(x, global_y, z)] = full_id
        
        return blocks_map


class AnvilParser:
    """Parser plików regionów Anvil (.mca)."""
    
    SECTOR_SIZE = 4096
    CHUNK_HEADER_SIZE = 5
    
    def __init__(self, filepath: str):
        self.filepath = filepath
        self.data = self._load_file()
        self.chunk_locations = self._parse_locations()
    
    def _load_file(self) -> bytes:
        """Wczytuje plik regionu."""
        with open(self.filepath, 'rb') as f:
            return f.read()
    
    def _parse_locations(self) -> List[Optional[Tuple[int, int]]]:
        """
        Parsuje nagłówek z lokalizacjami chunków.
        Zwraca listę 1024 pozycji (offset w sektorach, liczba sektorów).
        """
        locations = []
        for i in range(1024):
            offset = i * 4
            # 3 bajty offset + 1 bajt liczby sektorów
            data = self.data[offset:offset + 4]
            sector_offset = ((data[0] << 16) | (data[1] << 8) | data[2])
            sector_count = data[3]
            
            if sector_offset == 0 and sector_count == 0:
                locations.append(None)  # chunk nie istnieje
            else:
                locations.append((sector_offset, sector_count))
        
        return locations
    
    def _get_chunk_timestamp(self, chunk_x: int, chunk_z: int) -> int:
        """Pobiera timestamp dla chunka."""
        index = chunk_x + chunk_z * 32
        offset = 4096 + index * 4
        data = self.data[offset:offset + 4]
        return struct.unpack('>I', data)[0]
    
    def _read_chunk_data(self, chunk_index: int) -> Optional[bytes]:
        """Czyta surowe dane chunka."""
        location = self.chunk_locations[chunk_index]
        if location is None:
            return None
        
        sector_offset, sector_count = location
        byte_offset = sector_offset * self.SECTOR_SIZE
        
        # Nagłówek chunka: długość (4 bajty) + kompresja (1 bajt)
        length_data = self.data[byte_offset:byte_offset + 4]
        length = struct.unpack('>I', length_data)[0]
        compression_type = self.data[byte_offset + 4]
        
        # Dane chunka (długość - 1, bo pierwszy bajt to typ kompresji)
        compressed_data = self.data[byte_offset + 5:byte_offset + 5 + length - 1]
        
        # Dekompresja
        if compression_type == 1:  # gzip
            import gzip
            return gzip.decompress(compressed_data)
        elif compression_type == 2:  # zlib
            return zlib.decompress(compressed_data)
        else:
            # Brak kompresji
            return compressed_data
    
    def get_chunk(self, chunk_x: int, chunk_z: int) -> Optional[ChunkData]:
        """
        Pobiera dane chunka na podstawie lokalnych współrzędnych (0-31).
        """
        if not (0 <= chunk_x < 32 and 0 <= chunk_z < 32):
            raise ValueError(f"Invalid chunk coordinates: ({chunk_x}, {chunk_z})")
        
        index = chunk_x + chunk_z * 32
        chunk_data = self._read_chunk_data(index)
        
        if chunk_data is None:
            return None
        
        # Parsuj NBT
        nbt = parse_nbt(chunk_data)
        
        # Pobierz globalne współrzędne chunka
        level = nbt.get('Level', {})
        if isinstance(level, NBTTag):
            global_x = level.get('xPos', 0)
            global_z = level.get('zPos', 0)
        else:
            global_x = level.get('xPos', 0)
            global_z = level.get('zPos', 0)
        
        # Konwertuj do int (może być NBTTag)
        if isinstance(global_x, NBTTag):
            global_x = global_x.value
        if isinstance(global_z, NBTTag):
            global_z = global_z.value
        global_x = int(global_x) if global_x else 0
        global_z = int(global_z) if global_z else 0
        
        return ChunkData(global_x, global_z, nbt)
    
    def get_all_chunks(self) -> List[ChunkData]:
        """Pobiera wszystkie istniejące chunki z regionu."""
        chunks = []
        for chunk_z in range(32):
            for chunk_x in range(32):
                chunk = self.get_chunk(chunk_x, chunk_z)
                if chunk is not None:
                    chunks.append(chunk)
        return chunks
    
    def get_region_coordinates(self) -> Tuple[int, int]:
        """Wyciąga współrzędne regionu z nazwy pliku (r.X.Z.mca)."""
        import re
        match = re.search(r'r\.(-?\d+)\.(-?\d+)\.mca', str(self.filepath))
        if match:
            return int(match.group(1)), int(match.group(2))
        return (0, 0)


def get_region_for_block(block_x: int, block_z: int) -> Tuple[int, int]:
    """Oblicza współrzędne regionu dla danych współrzędnych bloku."""
    # Python // to floor division, które działa poprawnie dla ujemnych
    region_x = block_x // 512
    region_z = block_z // 512
    return (region_x, region_z)


def get_chunk_in_region(block_x: int, block_z: int) -> Tuple[int, int]:
    """Oblicza lokalne współrzędne chunka w regionie."""
    chunk_x = (block_x // 16) % 32
    chunk_z = (block_z // 16) % 32
    if chunk_x < 0:
        chunk_x += 32
    if chunk_z < 0:
        chunk_z += 32
    return (chunk_x, chunk_z)


def get_block_in_chunk(block_x: int, block_z: int) -> Tuple[int, int]:
    """Oblicza lokalne współrzędne bloku w chunku (0-15)."""
    local_x = block_x % 16
    local_z = block_z % 16
    if local_x < 0:
        local_x += 16
    if local_z < 0:
        local_z += 16
    return (local_x, local_z)
