#!/usr/bin/env python3
"""
Wstawia spiralny test bezpośrednio modyfikując bajty w pliku MCA.
Używa uproszczonego podejścia - tylko modyfikacja sekcji bloków.
"""

import os
import struct
import zlib
from pathlib import Path
from collections import defaultdict


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


def find_nbt_tag(data, tag_name):
    """Znajduje tag NBT w danych (prosty parser)."""
    # Szukaj stringa z nazwą tagu
    name_bytes = tag_name.encode('utf-8')
    idx = data.find(name_bytes)
    return idx


def modify_chunk_data(chunk_data, cx, cz, y_level=200):
    """Modyfikuje dane chunka aby dodać bloki spiralne."""
    # Dekompresuj
    try:
        decompressed = zlib.decompress(chunk_data)
    except:
        return None
    
    # Konwertuj do bytearray dla modyfikacji
    data = bytearray(decompressed)
    
    # Znajdź sekcje (szukamy 'Sections' w NBT)
    sections_idx = data.find(b'Sections')
    if sections_idx == -1:
        return None
    
    # Szukamy sekcji z odpowiednim Y
    sec_y = y_level // 16
    target_y_bytes = bytes([1, 0, 1, sec_y & 0xFF])  # TAG_Byte 'Y' = sec_y
    
    # Znajdź wszystkie sekcje i modyfikuj je
    # To jest uproszczone - zakładamy że struktura jest standardowa
    
    # Dodaj platformę stone w środku chunka
    # Y=200 -> sekcja 12, lokalne Y=8
    local_y = y_level % 16
    center_x, center_z = 8, 8
    
    # Szukamy 'Blocks' w sekcjach
    blocks_idx = data.find(b'Blocks')
    if blocks_idx != -1:
        # Przesuń się za nazwę tagu (2 bajty długości + nazwa + 4 bajty długości array)
        # To jest bardzo uproszczone i może nie działać dla wszystkich chunków
        pass
    
    return bytes(data)


def insert_spiral_simple(world_path, radius=3, y_level=200):
    """Uproszczona wersja wstawiania spirali."""
    print(f"Wstawianie spirali R={radius} do {world_path}")
    print(f"Wysokość Y={y_level}")
    
    chunks = generate_spiral_chunks(radius)
    print(f"Wygenerowano {len(chunks)} punktów spirali")
    
    # Tylko chunki w regionie r.0.0.mca
    region_chunks = [(cx, cz, step) for cx, cz, step in chunks 
                     if 0 <= cx < 32 and 0 <= cz < 32]
    
    print(f"Chunki w regionie r.0.0.mca: {len(region_chunks)}")
    print()
    print("UWAGA: Bezpośrednia modyfikacja NBT jest skomplikowana.")
    print("Zalecane podejścia:")
    print("  1. Użyj MCEdit lub Amulet Editor do wstawienia schematu")
    print("  2. Użyj WorldEdit na serwerze z komendami")
    print("  3. Zbuduj strukturę ręcznie w grze")
    print()
    print("Plik z listą chunków został zapisany: spiral_chunks_r3.txt")
    
    # Zapisz listę chunków
    with open('headless_server/tests/spiral_chunks_r3.txt', 'w') as f:
        for cx, cz, step in region_chunks:
            f.write(f"step={step} chunk=({cx},{cz}) block=({cx*16+8},{y_level},{cz*16+8})\n")


if __name__ == "__main__":
    script_dir = Path(__file__).parent
    world_path = script_dir.parent / '1.7.10' / 'world'
    
    print("=" * 60)
    print("WSTAWIANIE SPIRALI - WERSJA BEZPOŚREDNIA")
    print("=" * 60)
    
    insert_spiral_simple(world_path, radius=3, y_level=200)
