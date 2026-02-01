"""
Skrypt pomocniczy do czyszczenia entities z mapy.
Bezpośrednio modyfikuje pliki .mca.
"""
import struct
import zlib
import sys
from pathlib import Path
from typing import Dict, Set, Tuple, Optional

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

try:
    import nbtlib
except ImportError:
    print("Błąd: nbtlib nie jest zainstalowany. Uruchom: pip install nbtlib")
    sys.exit(1)

from minecraft_map_parser.anvil_parser import AnvilParser


SECTOR_SIZE = 4096


def read_chunk_nbt(region_data: bytearray, local_x: int, local_z: int) -> Optional[nbtlib.Compound]:
    """Odczytuje NBT chunka z danych regionu."""
    index = local_x + local_z * 32
    offset = index * 4
    
    if offset + 4 > len(region_data):
        return None
    
    data = region_data[offset:offset + 4]
    sector_offset = ((data[0] << 16) | (data[1] << 8) | data[2])
    sector_count = data[3]
    
    if sector_offset == 0:
        return None
    
    byte_offset = sector_offset * SECTOR_SIZE
    
    if byte_offset + 5 > len(region_data):
        return None
    
    length = struct.unpack('>I', region_data[byte_offset:byte_offset + 4])[0]
    compression_type = region_data[byte_offset + 4]
    
    if byte_offset + 5 + length - 1 > len(region_data):
        return None
    
    compressed_data = region_data[byte_offset + 5:byte_offset + 5 + length - 1]
    
    try:
        if compression_type == 2:  # zlib
            data = zlib.decompress(compressed_data)
        elif compression_type == 1:  # gzip
            import gzip
            data = gzip.decompress(compressed_data)
        else:
            data = compressed_data
        
        # Użyj tymczasowego pliku dla nbtlib
        import tempfile
        import os
        with tempfile.NamedTemporaryFile(delete=False) as tmp:
            tmp.write(data)
            tmp_path = tmp.name
        
        try:
            nbt = nbtlib.load(tmp_path, byteorder='big')
            return nbt
        finally:
            os.unlink(tmp_path)
    
    except Exception as e:
        return None


def write_chunk_nbt(region_data: bytearray, local_x: int, local_z: int, nbt: nbtlib.Compound) -> bool:
    """Zapisuje NBT chunka do danych regionu."""
    from io import BytesIO
    
    # Serializuj NBT
    buffer = BytesIO()
    nbt.write(buffer, byteorder='big')
    nbt_bytes = buffer.getvalue()
    
    # Kompresja
    compressed = zlib.compress(nbt_bytes)
    chunk_data = struct.pack('>I', len(compressed) + 1) + b'\x02' + compressed
    
    # Padding
    padding = (SECTOR_SIZE - (len(chunk_data) % SECTOR_SIZE)) % SECTOR_SIZE
    chunk_data_padded = chunk_data + b'\x00' * padding
    new_sector_count = len(chunk_data_padded) // SECTOR_SIZE
    
    # Znajdź lokalizację
    index = local_x + local_z * 32
    offset = index * 4
    
    data = region_data[offset:offset + 4]
    sector_offset = ((data[0] << 16) | (data[1] << 8) | data[2])
    old_sector_count = data[3]
    
    if sector_offset == 0 or new_sector_count > old_sector_count:
        # Nowe miejsce na końcu
        sector_offset = len(region_data) // SECTOR_SIZE
        if len(region_data) % SECTOR_SIZE != 0:
            sector_offset += 1
    
    # Zapisz dane
    byte_offset = sector_offset * SECTOR_SIZE
    end_offset = byte_offset + len(chunk_data_padded)
    
    if end_offset > len(region_data):
        region_data.extend(b'\x00' * (end_offset - len(region_data)))
    
    region_data[byte_offset:end_offset] = chunk_data_padded
    
    # Aktualizuj nagłówek
    region_data[offset] = (sector_offset >> 16) & 0xFF
    region_data[offset + 1] = (sector_offset >> 8) & 0xFF
    region_data[offset + 2] = sector_offset & 0xFF
    region_data[offset + 3] = new_sector_count
    
    return True


def clean_entities_from_region(region_file: Path) -> Tuple[int, int]:
    """
    Czyści entities z pliku regionu.
    
    Returns:
        (liczba chunków zmodyfikowanych, liczba entities usuniętych)
    """
    with open(region_file, 'rb') as f:
        region_data = bytearray(f.read())
    
    modified_chunks = 0
    total_entities_removed = 0
    
    for chunk_z in range(32):
        for chunk_x in range(32):
            try:
                nbt = read_chunk_nbt(region_data, chunk_x, chunk_z)
                if nbt is None:
                    continue
                
                # Pobierz Level
                level = nbt.get('Level')
                if level is None:
                    continue
                
                # Sprawdź entities
                entities = level.get('Entities')
                if entities is None or len(entities) == 0:
                    continue
                
                entity_count = len(entities)
                
                # Wyczyść entities
                level['Entities'] = nbtlib.List[nbtlib.Compound]([])
                
                # Zapisz chunk
                write_chunk_nbt(region_data, chunk_x, chunk_z, nbt)
                
                modified_chunks += 1
                total_entities_removed += entity_count
                
            except Exception as e:
                print(f"    Błąd w chunk ({chunk_x},{chunk_z}): {e}")
    
    # Zapisz zmiany
    if modified_chunks > 0:
        with open(region_file, 'wb') as f:
            f.write(region_data)
    
    return modified_chunks, total_entities_removed


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="Czyści entities z mapy")
    parser.add_argument("world", type=Path, help="Ścieżka do świata")
    parser.add_argument("--region", type=str, help="Tylko konkretny region (x,z)")
    
    args = parser.parse_args()
    
    region_path = args.world / "region"
    if not region_path.exists():
        print(f"Błąd: Nie znaleziono {region_path}")
        sys.exit(1)
    
    region_files = list(region_path.glob("r.*.mca"))
    
    if args.region:
        parts = args.region.split(',')
        if len(parts) == 2:
            rfile = region_path / f"r.{parts[0]}.{parts[1]}.mca"
            if rfile.exists():
                region_files = [rfile]
            else:
                print(f"Nie znaleziono regionu: {rfile}")
                sys.exit(1)
    
    print(f"Czyszczenie entities z {len(region_files)} regionów...")
    
    total_modified = 0
    total_entities = 0
    
    for i, region_file in enumerate(sorted(region_files), 1):
        print(f"[{i}/{len(region_files)}] {region_file.name}...", end=" ")
        
        modified, entities = clean_entities_from_region(region_file)
        total_modified += modified
        total_entities += entities
        
        if modified > 0:
            print(f"zmodyfikowano {modified} chunków, usunięto {entities} entities")
        else:
            print("brak zmian")
    
    print(f"\nPodsumowanie:")
    print(f"  Zmodyfikowane chunki: {total_modified}")
    print(f"  Usunięte entities: {total_entities}")


if __name__ == "__main__":
    main()
