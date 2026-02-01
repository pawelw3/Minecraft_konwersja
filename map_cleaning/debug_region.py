#!/usr/bin/env python3
"""
Debug - sprawdźmy dlaczego niektóre regiony nie są przetwarzane
"""
import struct
import zlib
import sys

def decompress_zlib(data):
    try:
        return zlib.decompress(data)
    except Exception as e:
        return None, str(e)

def analyze_chunk_header(region_path, chunk_x, chunk_z):
    """Analizuje nagłówek konkretnego chunka w regionie"""
    with open(region_path, 'rb') as f:
        # Header
        header = f.read(4096)
        timestamps = f.read(4096)
        
        index = chunk_x + chunk_z * 32
        offset = ((header[index * 4] << 16) | 
                 (header[index * 4 + 1] << 8) | 
                 header[index * 4 + 2])
        sector_count = header[index * 4 + 3]
        
        print(f"Chunk {chunk_x},{chunk_z}:")
        print(f"  Offset: {offset} sectors ({offset * 4096} bytes)")
        print(f"  Sector count: {sector_count}")
        
        if offset == 0 or sector_count == 0:
            print("  -> Pusty chunk")
            return
        
        f.seek(offset * 4096)
        length_bytes = f.read(4)
        length = struct.unpack('>I', length_bytes)[0]
        compression = f.read(1)[0]
        
        print(f"  Compressed length: {length} bytes")
        print(f"  Compression type: {compression} (1=gzip, 2=zlib)")
        
        compressed = f.read(length - 1)
        print(f"  Actually read: {len(compressed)} bytes")
        
        if compression == 2:
            result = decompress_zlib(compressed)
            if isinstance(result, tuple):
                print(f"  Decompression ERROR: {result[1]}")
            else:
                print(f"  Decompressed: {len(result)} bytes")
                # Sprawdź czy to poprawne NBT
                if result[0] == 10:  # TAG_Compound
                    print(f"  NBT: TAG_Compound (OK)")
                else:
                    print(f"  NBT: Unknown type {result[0]}")

if __name__ == "__main__":
    if len(sys.argv) < 4:
        print("Użycie: python debug_region.py <region.mca> <chunk_x> <chunk_z>")
        sys.exit(1)
    
    analyze_chunk_header(sys.argv[1], int(sys.argv[2]), int(sys.argv[3]))
