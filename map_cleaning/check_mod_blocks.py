#!/usr/bin/env python3
"""
Skrypt sprawdzający czy regiony zawierają bloki z modów (ID > 175)
"""
import sys
import os
import struct
import zlib
from pathlib import Path

def decompress_zlib(data):
    """Dekompresuje dane zlib"""
    try:
        return zlib.decompress(data)
    except:
        return None

def parse_nbt_simple(data, max_depth=10):
    """Uproszczony parser NBT - szuka tylko Blocks"""
    # Szukamy sekwencji bajtów 'Blocks' w NBT
    # W 1.7.10 struktura chunk to: Level -> Sections[] -> Blocks
    
    try:
        # Szukamy bloku "Blocks" (TAG_ByteArray = 7)
        # Format: type(1) + name_len(2) + name + len(4) + data
        
        pos = 0
        max_id = 0
        mod_blocks_count = 0
        
        while pos < len(data) - 10:
            # Szukamy typu 7 (ByteArray) przed "Blocks"
            if data[pos] == 7:
                # Sprawdź czy nazwa to "Blocks"
                name_len = struct.unpack('>H', data[pos+1:pos+3])[0]
                if name_len == 6 and pos + 9 < len(data):
                    name = data[pos+3:pos+9].decode('utf-8', errors='ignore')
                    if name == "Blocks":
                        # Znaleźliśmy Blocks array
                        arr_len = struct.unpack('>I', data[pos+9:pos+13])[0]
                        if arr_len == 4096 and pos + 13 + 4096 <= len(data):
                            block_data = data[pos+13:pos+13+4096]
                            for b in block_data:
                                block_id = b if b >= 0 else b + 256
                                if block_id > max_id:
                                    max_id = block_id
                                if block_id > 175 and block_id != 0:
                                    mod_blocks_count += 1
            pos += 1
        
        return max_id, mod_blocks_count
    except Exception as e:
        return 0, 0

def analyze_region(region_path):
    """Analizuje pojedynczy region"""
    try:
        with open(region_path, 'rb') as f:
            # Header: 1024 wpisów po 4 bajty (offset 3b + size 1b)
            header = f.read(4096)
            timestamps = f.read(4096)
            
            total_mod_blocks = 0
            max_block_id = 0
            chunks_with_data = 0
            
            for chunk_z in range(32):
                for chunk_x in range(32):
                    index = chunk_x + chunk_z * 32
                    offset = ((header[index * 4] << 16) | 
                             (header[index * 4 + 1] << 8) | 
                             header[index * 4 + 2])
                    sector_count = header[index * 4 + 3]
                    
                    if offset == 0 or sector_count == 0:
                        continue
                    
                    f.seek(offset * 4096)
                    length = struct.unpack('>I', f.read(4))[0]
                    compression = f.read(1)[0]
                    
                    if length < 1 or length > 10 * 1024 * 1024:
                        continue
                    
                    compressed = f.read(length - 1)
                    
                    if compression == 2:  # zlib
                        data = decompress_zlib(compressed)
                        if data:
                            max_id, mod_count = parse_nbt_simple(data)
                            if max_id > 0:
                                chunks_with_data += 1
                            if max_id > max_block_id:
                                max_block_id = max_id
                            total_mod_blocks += mod_count
            
            return {
                'chunks': chunks_with_data,
                'max_block_id': max_block_id,
                'mod_blocks': total_mod_blocks
            }
    except Exception as e:
        return {'error': str(e)}

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Użycie: python check_mod_blocks.py <ścieżka_do_regionu.mca>")
        sys.exit(1)
    
    region_path = sys.argv[1]
    result = analyze_region(region_path)
    
    if 'error' in result:
        print(f"Błąd: {result['error']}")
    else:
        print(f"Chunki z danymi: {result['chunks']}")
        print(f"Maksymalne ID bloku: {result['max_block_id']}")
        print(f"Liczba bloków z modów (ID > 175): {result['mod_blocks']}")
        if result['mod_blocks'] > 0:
            print("REGION ZAWIERA MODY - POWINIEN BYĆ PRZETWORZONY")
        else:
            print("Region nie zawiera bloków z modów")
