#!/usr/bin/env python3
"""
Generator spiralnego testu dla Minecraft 1.7.10
Tworzy spiralę chunków z redstone kablami i command blockami.
"""

import sys
import os
import struct

# Dodaj src do path
script_dir = os.path.dirname(os.path.abspath(__file__))
src_path = os.path.join(script_dir, '..', '..', 'src')
sys.path.insert(0, os.path.normpath(src_path))

try:
    from minecraft_map_parser.nbt_parser import NBTWriter, NBTTagCompound, NBTTagInt, NBTTagString, NBTTagList
    print("Zaimportowano moduły NBT parsera")
except ImportError as e:
    print(f"Błąd importu: {e}")
    print("Kontynuowanie bez importu parsera (tylko generowanie listy chunków)...")


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
            # Zmiana kierunku: prawo -> góra -> lewo -> dół -> prawo
            if dx == 1 and dz == 0:  # prawo -> góra
                dx, dz = 0, 1
            elif dx == 0 and dz == 1:  # góra -> lewo
                dx, dz = -1, 0
            elif dx == -1 and dz == 0:  # lewo -> dół
                dx, dz = 0, -1
            elif dx == 0 and dz == -1:  # dół -> prawo
                dx, dz = 1, 0
            
            if direction_changes % 2 == 0:
                steps += 1
    
    return chunks


def create_spiral_schematic(radius=5, y_level=64):
    """
    Tworzy schematic spiralnego kabla redstone z command blockami.
    Zwraca: (blocks_dict, chunks_list)
    """
    chunks = generate_spiral_chunks(radius)
    blocks = {}  # (x, y, z) -> (block_id, metadata)
    
    # ID bloków dla 1.7.10
    STONE = (1, 0)
    REDSTONE_WIRE = (55, 0)
    REPEATER = (93, 0)  # unpowered repeater
    COMMAND_BLOCK = (137, 0)
    REDSTONE_BLOCK = (152, 0)
    
    # Platforma stone pod całą spiralą
    for cx, cz, step in chunks:
        center_x = cx * 16 + 8
        center_z = cz * 16 + 8
        for dx in range(-2, 3):
            for dz in range(-2, 3):
                blocks[(center_x + dx, y_level - 1, center_z + dz)] = STONE
    
    # Redstone block na starcie (0,0) - stałe zasilanie
    start_x = 0 * 16 + 8
    start_z = 0 * 16 + 8
    blocks[(start_x, y_level, start_z)] = REDSTONE_BLOCK
    
    # Kable i repeatery między chunkami
    for i in range(len(chunks) - 1):
        cx1, cz1, step1 = chunks[i]
        cx2, cz2, step2 = chunks[i + 1]
        
        x1 = cx1 * 16 + 8
        z1 = cz1 * 16 + 8
        x2 = cx2 * 16 + 8
        z2 = cz2 * 16 + 8
        
        # Kierunek od 1 do 2
        if x2 > x1:  # w prawo
            direction = 1  # east
        elif x2 < x1:  # w lewo
            direction = 3  # west
        elif z2 > z1:  # w dół (Z rośnie na południe w MC)
            direction = 2  # south
        else:  # z2 < z1 - w górę
            direction = 0  # north
        
        # Repeater w punkcie 1 skierowany do punktu 2
        repeater_meta = direction
        blocks[(x1, y_level, z1)] = (93, repeater_meta)
        
        # Dust między punktami (około 16 bloków)
        if direction == 1:  # east
            for dx in range(1, 8):
                blocks[(x1 + dx, y_level, z1)] = REDSTONE_WIRE
            blocks[(x1 + 8, y_level, z1)] = (93, direction)  # drugi repeater w środku
            for dx in range(9, 16):
                blocks[(x1 + dx, y_level, z1)] = REDSTONE_WIRE
        elif direction == 3:  # west
            for dx in range(1, 8):
                blocks[(x1 - dx, y_level, z1)] = REDSTONE_WIRE
            blocks[(x1 - 8, y_level, z1)] = (93, direction)
            for dx in range(9, 16):
                blocks[(x1 - dx, y_level, z1)] = REDSTONE_WIRE
        elif direction == 2:  # south
            for dz in range(1, 8):
                blocks[(x1, y_level, z1 + dz)] = REDSTONE_WIRE
            blocks[(x1, y_level, z1 + 8)] = (93, direction)
            for dz in range(9, 16):
                blocks[(x1, y_level, z1 + dz)] = REDSTONE_WIRE
        elif direction == 0:  # north
            for dz in range(1, 8):
                blocks[(x1, y_level, z1 - dz)] = REDSTONE_WIRE
            blocks[(x1, y_level, z1 - 8)] = (93, direction)
            for dz in range(9, 16):
                blocks[(x1, y_level, z1 - dz)] = REDSTONE_WIRE
    
    # Command blocki w każdym chunku (oprócz startu który ma redstone_block)
    for cx, cz, step in chunks:
        if step == 0:
            continue  # Skip start - tam jest redstone block
        
        center_x = cx * 16 + 8
        center_z = cz * 16 + 8
        
        # Command block obok checkpointu
        cb_x = center_x + 1
        cb_z = center_z
        
        # Podłączenie do kabla - repeater zasilający CB
        blocks[(center_x, y_level, center_z)] = (93, 1)  # repeater east -> CB
        blocks[(cb_x, y_level, cb_z)] = COMMAND_BLOCK
        
        # Command do wykonania
        command = f"/say [PROBE] REACHED cx={cx} cz={cz} step={step}"
        # Zapiszemy komendę osobno - NBT dla tile entity
    
    return blocks, chunks


def save_schematic_info(chunks, output_file):
    """Zapisuje informacje o spiralę do pliku"""
    with open(output_file, 'w') as f:
        f.write("# Spiral Test Schematic - Chunk List\n")
        f.write("# Format: step cx cz x z\n")
        for cx, cz, step in chunks:
            x = cx * 16 + 8
            z = cz * 16 + 8
            f.write(f"{step} {cx} {cz} {x} {z}\n")
    print(f"Zapisano listę {len(chunks)} chunków do {output_file}")


if __name__ == "__main__":
    print("Generator spiralnego testu dla Minecraft 1.7.10")
    print("=" * 50)
    
    # Parametry
    RADIUS = 5  # Zaczynamy od małej spirali
    Y_LEVEL = 64
    
    # Generowanie
    print(f"Generowanie spirali o promieniu R={RADIUS}...")
    chunks = generate_spiral_chunks(RADIUS)
    print(f"Wygenerowano {len(chunks)} punktów spirali")
    
    # Wyświetl pierwsze 10 punktów
    print("\nPierwsze 10 punktów spirali:")
    for cx, cz, step in chunks[:10]:
        print(f"  step={step}: chunk ({cx}, {cz}) -> block ({cx*16+8}, {cz*16+8})")
    
    # Zapisz info
    os.makedirs("headless_server/tests", exist_ok=True)
    save_schematic_info(chunks, "headless_server/tests/spiral_chunks_r5.txt")
    
    print("\nGotowe! Teraz użyj WorldEdit lub skryptu NBT aby wstawić bloki.")
    print("Wymagane bloki:")
    print("  - Stone (1) - platforma")
    print("  - Redstone Wire (55) - kable")
    print("  - Repeater (93) - wzmacniacze")
    print("  - Command Block (137) - z komendami /say [PROBE] REACHED...")
    print("  - Redstone Block (152) - start zasilania")
