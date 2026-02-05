#!/usr/bin/env python3
"""
verify_nbt.py - Weryfikacja NBT w region files dla testów CuttableBlocks

Użycie:
    python verify_nbt.py <path_to_region_mca> [--te-id cuttableblocks:cuttable_te]

Weryfikuje:
    - Czy region file można odczytać
    - Czy zawiera poprawne chunki
    - Czy zawiera TileEntity CuttableBlocks z oczekiwanymi polami
"""

import sys
import struct
import argparse
from pathlib import Path


def read_region_header(file_path):
    """Odczytuje nagłówek region file (1024 lokacje chunków)."""
    with open(file_path, 'rb') as f:
        header = f.read(4096)  # 1024 * 4 bajty
    
    locations = []
    for i in range(1024):
        offset = struct.unpack('>I', header[i*4:(i+1)*4])[0]
        sector_offset = (offset >> 8) & 0xFFFFFF
        sector_count = offset & 0xFF
        locations.append((sector_offset, sector_count))
    
    return locations


def read_chunk_data(file_path, sector_offset, sector_count):
    """Odczytuje surowe dane chunka z pliku region."""
    with open(file_path, 'rb') as f:
        f.seek(sector_offset * 4096)
        
        # Pierwsze 4 bajty: długość (włącznie z kompresją)
        length_bytes = f.read(4)
        if len(length_bytes) < 4:
            return None
        
        length = struct.unpack('>I', length_bytes)[0]
        
        # 1 bajt: typ kompresji
        compression = struct.unpack('B', f.read(1))[0]
        
        # Dane chunka (skompresowane)
        data = f.read(length - 1)
        
        return compression, data


def decompress_chunk_data(compression, data):
    """Dekompresuje dane chunka."""
    if compression == 1:  # GZip
        import gzip
        return gzip.decompress(data)
    elif compression == 2:  # Zlib
        import zlib
        return zlib.decompress(data)
    else:
        raise ValueError(f"Nieznany typ kompresji: {compression}")


def parse_nbt_simple(data):
    """Prosty parser NBT - zwraca tekstową reprezentację."""
    # Dla uproszczenia użyjmy przybliżonego parsowania
    # W prawdziwej implementacji użylibyśmy biblioteki NBT
    
    try:
        # Szukaj tagów Compound z TileEntity
        text = data.decode('utf-8', errors='ignore')
        return text
    except:
        return ""


def verify_cuttable_te(chunk_text, expected_te_id="cuttableblocks:cuttable_te"):
    """Sprawdza czy chunk zawiera TileEntity CuttableBlocks."""
    issues = []
    
    if expected_te_id not in chunk_text:
        issues.append(f"Nie znaleziono TE: {expected_te_id}")
        return issues
    
    # Sprawdź czy zawiera wymagane pola
    required_fields = [
        "originalBlock",
        "originalMeta",
        "normalX",
        "normalY",
        "normalZ",
        "keepPositive"
    ]
    
    for field in required_fields:
        if field not in chunk_text:
            issues.append(f"Brakujące pole: {field}")
    
    return issues


def main():
    parser = argparse.ArgumentParser(
        description="Weryfikacja NBT w region files dla CuttableBlocks"
    )
    parser.add_argument("region_file", help="Ścieżka do pliku .mca")
    parser.add_argument(
        "--te-id", 
        default="cuttableblocks:cuttable_te",
        help="ID TileEntity do wyszukania"
    )
    
    args = parser.parse_args()
    
    region_path = Path(args.region_file)
    if not region_path.exists():
        print(f"BŁĄD: Plik nie istnieje: {region_path}")
        sys.exit(1)
    
    print(f"Weryfikacja: {region_path}")
    print(f"Szukam TE: {args.te_id}")
    print("-" * 50)
    
    try:
        locations = read_region_header(region_path)
        
        chunks_with_te = 0
        total_chunks = 0
        all_issues = []
        
        for chunk_idx, (sector_offset, sector_count) in enumerate(locations):
            if sector_offset == 0:
                continue  # Pusty chunk
            
            total_chunks += 1
            
            try:
                compression, data = read_chunk_data(
                    region_path, sector_offset, sector_count
                )
                decompressed = decompress_chunk_data(compression, data)
                chunk_text = parse_nbt_simple(decompressed)
                
                issues = verify_cuttable_te(chunk_text, args.te_id)
                if issues:
                    all_issues.extend(issues)
                else:
                    if args.te_id in chunk_text:
                        chunks_with_te += 1
                        
            except Exception as e:
                all_issues.append(f"Chunk {chunk_idx}: {e}")
        
        print(f"Znaleziono chunków: {total_chunks}")
        print(f"Chunków z Cuttable TE: {chunks_with_te}")
        
        if all_issues:
            print("\nProblemy:")
            for issue in all_issues[:10]:  # Pokaż max 10
                print(f"  - {issue}")
            if len(all_issues) > 10:
                print(f"  ... i {len(all_issues) - 10} więcej")
            sys.exit(1)
        else:
            print("\nWeryfikacja NBT: PASSED")
            sys.exit(0)
            
    except Exception as e:
        print(f"BŁĄD podczas weryfikacji: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
