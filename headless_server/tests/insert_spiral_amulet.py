#!/usr/bin/env python3
"""
Wstawia spiralny test do istniejącego świata używając amulet-core.
"""

import sys
import os
from pathlib import Path
from collections import defaultdict

# Dodaj src do path
script_dir = Path(__file__).parent
src_path = script_dir.parent.parent / 'src'
sys.path.insert(0, str(src_path))

try:
    import amulet
    from amulet.api.block import Block
except ImportError:
    print("Błąd: amulet-core nie jest zainstalowany. Uruchom: pip install amulet-core")
    sys.exit(1)


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


def insert_spiral(world_path, radius=3, y_level=200):
    """Wstawia spiralę do świata używając amulet."""
    print(f"Wstawianie spirali R={radius} do {world_path}")
    print(f"Wysokość Y={y_level}")
    
    chunks = generate_spiral_chunks(radius)
    print(f"Wygenerowano {len(chunks)} punktów spirali")
    
    # Otwórz świat
    try:
        world = amulet.load_level(str(world_path))
        print(f"Otwarto świat: {world.level_wrapper.platform} {world.level_wrapper.version}")
        print(f"Wymiary: {world.dimensions}")
    except Exception as e:
        print(f"Błąd otwierania świata: {e}")
        import traceback
        traceback.print_exc()
        return
    
    dimension = "minecraft:overworld"
    version = ("java", (1, 7, 10))
    
    # Bloki
    stone = Block("minecraft", "stone")
    redstone_block = Block("minecraft", "redstone_block")
    command_block = Block("minecraft", "command_block")
    repeater = Block("minecraft", "unpowered_repeater")
    redstone_wire = Block("minecraft", "redstone_wire")
    
    modified_count = 0
    
    try:
        for cx, cz, step in chunks:
            print(f"  Przetwarzanie chunk ({cx}, {cz}) step={step}...")
            
            # Współrzędne środka chunka
            center_x = cx * 16 + 8
            center_z = cz * 16 + 8
            
            # Dodaj platformę stone (5x5)
            for dx in range(-2, 3):
                for dz in range(-2, 3):
                    world.set_version_block(
                        center_x + dx, y_level - 1, center_z + dz,
                        dimension, version, stone
                    )
            
            if step == 0:
                # Start - redstone block
                world.set_version_block(
                    center_x, y_level, center_z,
                    dimension, version, redstone_block
                )
            else:
                # Repeater w poprzednim chunku - znajdź kierunek
                prev_cx, prev_cz, _ = chunks[step - 1]
                
                # Kierunek od poprzedniego do obecnego
                if cx > prev_cx:
                    direction = "east"
                elif cx < prev_cx:
                    direction = "west"
                elif cz > prev_cz:
                    direction = "south"
                else:
                    direction = "north"
                
                # Ustaw repeater w poprzednim chunku
                prev_center_x = prev_cx * 16 + 8
                prev_center_z = prev_cz * 16 + 8
                
                # Dodaj redstone wire między chunkami
                # (uproszczone - tylko w środku chunka)
                
                # Command block w bieżącym chunku
                cb_x = center_x + 1
                cb_z = center_z
                world.set_version_block(
                    cb_x, y_level, cb_z,
                    dimension, version, command_block
                )
            
            modified_count += 1
        
        # Zapisz zmiany
        print("\nZapisywanie zmian...")
        world.save()
        world.close()
        
        print(f"\nZmodyfikowano {modified_count} chunków")
        print("Gotowe!")
        
    except Exception as e:
        print(f"Błąd podczas modyfikacji: {e}")
        import traceback
        traceback.print_exc()
        try:
            world.close()
        except:
            pass


if __name__ == "__main__":
    world_path = script_dir.parent / '1.7.10' / 'world'
    
    print("=" * 60)
    print("WSTAWIANIE SPIRALI - AMULET-CORE")
    print("=" * 60)
    
    insert_spiral(world_path, radius=3, y_level=200)
