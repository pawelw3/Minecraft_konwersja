#!/usr/bin/env python3
"""
Skrypt analizujący mapę 1.7.10 w poszukiwaniu bloków Jammy Furniture Reborn.
Zadanie 1: Identyfikacja wszystkich bloków Jammy Furniture na mapie.
"""

import os
import sys
import struct
import zlib
import argparse
from collections import defaultdict
from pathlib import Path

# Dodaj ścieżkę do parsera NBT
sys.path.insert(0, 'src')

try:
    from minecraft_map_parser.nbt_parser import NBTBuffer
except ImportError:
    print("Warning: NBT parser not found, using basic parsing")
    NBTBuffer = None

# Definicja ID bloków Jammy Furniture w 1.7.10
# Bloki są rejestrowane w Forge z prefiksem "jammyfurniture:"
JAMMY_BLOCK_NAMES = [
    # Bloki meblowe (główne)
    "jammyfurniture:Bath",
    "jammyfurniture:LightsOn",
    "jammyfurniture:LightsOff",
    "jammyfurniture:WoodBlocksOne",
    "jammyfurniture:WoodBlocksTwo", 
    "jammyfurniture:WoodBlocksThree",
    "jammyfurniture:WoodBlocksFour",
    "jammyfurniture:IronBlocksOne",
    "jammyfurniture:IronBlocksTwo",
    "jammyfurniture:CeramicBlocksOne",
    "jammyfurniture:RoofingBlocksOne",
    "jammyfurniture:MiscBlocksOne",
    "jammyfurniture:MobHeadsOne",
    "jammyfurniture:MobHeadsTwo",
    "jammyfurniture:MobHeadsThree",
    "jammyfurniture:MobHeadsFour",
    "jammyfurniture:ArmChair",
    "jammyfurniture:SofaLeft",
    "jammyfurniture:SofaRight",
    "jammyfurniture:SofaCenter",
    "jammyfurniture:SofaCorner",
]

# Mapowanie metadata na nazwy bloków (dla celów raportowania)
BLOCK_NAMES = {
    "jammyfurniture:Bath": "Wanna",
    "jammyfurniture:LightsOn": "Światło (włączone)",
    "jammyfurniture:LightsOff": "Światło (wyłączone)",
    "jammyfurniture:WoodBlocksOne": "Bloki drewniane 1 (zegar, rolety, stół)",
    "jammyfurniture:WoodBlocksTwo": "Bloki drewniane 2 (szafki kuchenne, TV, kosz)",
    "jammyfurniture:WoodBlocksThree": "Bloki drewniane 3 (krzesło, radio)",
    "jammyfurniture:WoodBlocksFour": "Bloki drewniane 4 (szafa, wieszak)",
    "jammyfurniture:IronBlocksOne": "Bloki metalowe 1 (lodówka, zamrażarka, kuchenka, kosz)",
    "jammyfurniture:IronBlocksTwo": "Bloki metalowe 2 (zmywarka, pralka)",
    "jammyfurniture:CeramicBlocksOne": "Bloki ceramiczne (szafka łazienkowa, zlew, toaleta)",
    "jammyfurniture:RoofingBlocksOne": "Dachówka",
    "jammyfurniture:MiscBlocksOne": "Różne (komin, piecek, choinka)",
    "jammyfurniture:MobHeadsOne": "Głowy mobów 1",
    "jammyfurniture:MobHeadsTwo": "Głowy mobów 2",
    "jammyfurniture:MobHeadsThree": "Głowy mobów 3",
    "jammyfurniture:MobHeadsFour": "Głowy mobów 4",
    "jammyfurniture:ArmChair": "Fotel",
    "jammyfurniture:SofaLeft": "Sofa (lewa)",
    "jammyfurniture:SofaRight": "Sofa (prawa)",
    "jammyfurniture:SofaCenter": "Sofa (środek)",
    "jammyfurniture:SofaCorner": "Sofa (narożnik)",
}


def read_region_file(filepath):
    """Czyta plik regionu .mca i zwraca chunki."""
    chunks = []
    with open(filepath, 'rb') as f:
        # Nagłówek: 1024 lokacji (offset + sektor count) + 1024 timestampów
        header = f.read(8192)
        
        for chunk_x in range(32):
            for chunk_z in range(32):
                idx = chunk_x + chunk_z * 32
                offset_data = header[idx*4:(idx+1)*4]
                offset = ((offset_data[0] << 16) | (offset_data[1] << 8) | offset_data[2]) * 4096
                sector_count = offset_data[3] * 4096
                
                if offset == 0:
                    continue
                
                f.seek(offset)
                # Chunk header: długość (4 bajty) + kompresja (1 bajt)
                length_bytes = f.read(4)
                if len(length_bytes) < 4:
                    continue
                length = struct.unpack('>I', length_bytes)[0]
                compression = struct.unpack('B', f.read(1))[0]
                
                if length > 0 and length < 1024*1024:  # Sanity check
                    compressed_data = f.read(length - 1)
                    try:
                        if compression == 2:  # zlib
                            chunk_data = zlib.decompress(compressed_data)
                            chunks.append((chunk_x, chunk_z, chunk_data))
                        elif compression == 1:  # gzip
                            import gzip
                            chunk_data = gzip.decompress(compressed_data)
                            chunks.append((chunk_x, chunk_z, chunk_data))
                    except Exception as e:
                        pass  # Pomiń uszkodzone chunki
    
    return chunks


def extract_block_ids_from_chunk(chunk_data):
    """Ekstrahuje ID bloków z danych chunka NBT."""
    try:
        if NBTBuffer:
            nbt = NBTBuffer(chunk_data)
            level = nbt.get('Level')
            if not level:
                return []
            
            sections = level.get('Sections')
            if not sections:
                return []
            
            block_ids = set()
            for section in sections:
                blocks = section.get('Blocks')
                if blocks:
                    block_ids.update(blocks)
            
            return list(block_ids)
    except Exception as e:
        pass
    
    return []


def scan_map_for_jammy(map_path, sample_size=None):
    """Skanuje mapę w poszukiwaniu bloków Jammy Furniture."""
    region_dir = Path(map_path) / "region"
    
    if not region_dir.exists():
        print(f"ERROR: Nie znaleziono folderu region: {region_dir}")
        return {}
    
    # Statystyki
    jammy_blocks_found = defaultdict(int)
    chunks_with_jammy = 0
    total_chunks = 0
    regions_scanned = 0
    
    mca_files = list(region_dir.glob("*.mca"))
    print(f"Znaleziono {len(mca_files)} plików regionów do skanowania...")
    
    if sample_size:
        import random
        mca_files = random.sample(mca_files, min(sample_size, len(mca_files)))
        print(f"Próbkowanie: skanowanie {len(mca_files)} plików")
    
    for mca_file in mca_files:
        regions_scanned += 1
        print(f"\rSkanowanie: {regions_scanned}/{len(mca_files)} regionów...", end="")
        
        chunks = read_region_file(mca_file)
        
        for chunk_x, chunk_z, chunk_data in chunks:
            total_chunks += 1
            # Tutaj musielibyśmy zdekodować NBT i sprawdzić bloki
            # Dla uproszczenia, sprawdzamy czy string "jammy" występuje w danych
            if b'jammy' in chunk_data.lower():
                chunks_with_jammy += 1
                # TODO: Pełna analiza NBT aby policzyć konkretne bloki
    
    print(f"\n\n=== WYNIKI SKANOWANIA ===")
    print(f"Przeskanowano regionów: {regions_scanned}")
    print(f"Przeskanowano chunków: {total_chunks}")
    print(f"Chunki z 'jammy' w danych: {chunks_with_jammy}")
    
    return {
        'regions_scanned': regions_scanned,
        'total_chunks': total_chunks,
        'chunks_with_jammy': chunks_with_jammy,
        'blocks_found': dict(jammy_blocks_found)
    }


def main():
    map_path = "mapa_1710"
    
    print("=" * 60)
    print("ANALIZA JAMMY FURNITURE REBORN - Zadanie 1")
    print("=" * 60)
    print()
    
    # Sprawdź czy istnieje folder mapy
    if not os.path.exists(map_path):
        print(f"ERROR: Nie znaleziono folderu mapy: {map_path}")
        sys.exit(1)
    
    # Pełna lista bloków do zidentyfikowania
    print("Bloki do zidentyfikowania:")
    for block in JAMMY_BLOCK_NAMES:
        name = BLOCK_NAMES.get(block, "Nieznany")
        print(f"  - {block}: {name}")
    print()
    
    # Parsuj argumenty
    parser = argparse.ArgumentParser(description='Analiza Jammy Furniture na mapie')
    parser.add_argument('--full', action='store_true', help='Pelne skanowanie wszystkich regionow')
    parser.add_argument('--sample', type=int, default=50, help='Liczba regionow do probkowania (domyslnie 50)')
    args = parser.parse_args()
    
    # Skanuj mapę
    if args.full:
        print("Tryb: PELNE SKANOWANIE wszystkich regionow...")
        results = scan_map_for_jammy(map_path, sample_size=None)
    else:
        print(f"Tryb: Probkowanie {args.sample} regionow...")
        results = scan_map_for_jammy(map_path, sample_size=args.sample)
    
    print()
    print("=" * 60)
    print("PODSUMOWANIE")
    print("=" * 60)
    
    if results['chunks_with_jammy'] > 0:
        print(f"\n✅ ZNALEZIONO bloki Jammy Furniture na mapie!")
        print(f"   Chunki zawierające 'jammy': {results['chunks_with_jammy']}")
    else:
        print(f"\n[!] Nie znaleziono blokow Jammy Furniture w probce")
        print(f"   (moze byc konieczne pelne skanowanie wszystkich regionow)")


if __name__ == "__main__":
    main()
