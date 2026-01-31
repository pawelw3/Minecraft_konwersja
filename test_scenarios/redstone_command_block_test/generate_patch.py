#!/usr/bin/env python3
"""
Generator patch JSON dla testu Redstone + Command Block
Generuje plik patch.json dla MC EditKit Worker (Kotlin/Hephaistos)

Użycie:
    python generate_patch.py [--output patch.json]
"""

import json
import argparse
from pathlib import Path

def generate_redstone_test_patch(offset_x=50, offset_y=64, offset_z=50, 
                                   wire_length=3, repeater_count=2, 
                                   command_msg=None, power_source=None,
                                   name="Redstone Test"):
    """
    Generuje patch dla układu testowego redstone z command blockiem.
    
    Układ:
    - Dźwignia (Lever) na początku (włączona lub wyłączona)
    - Redstone dust (wire_length bloki)
    - Repeater (delay=1 tick, powtarzany co 4 bloki)
    - ... (powtarzane repeater_count razy)
    - Command Block (z Tile Entity)
    
    Args:
        offset_x, offset_y, offset_z: Pozycja startowa
        wire_length: Długość kabla między repeaterami (domyślnie 3)
        repeater_count: Liczba repeaterów (domyślnie 2)
        command_msg: Komenda do wykonania (domyślnie testowa)
        lever_active: Czy dźwignia ma być włączona (True/False)
        name: Nazwa testu
    """
    
    edits = []
    
    # Oblicz całkowitą długość układu
    # (wire_length + 1 za repeater) * repeater_count + wire_length przed ostatnim repeaterem + command block
    # Dodajemy 1 blok na początku na power source (redstone torch lub block)
    total_length = (wire_length + 1) * repeater_count + wire_length + 1 + 1  # +1 na power source
    
    # Podłoga (stone) pod całym układem (łącznie z miejscem na power source)
    for i in range(total_length + 2):
        edits.append({
            "op": "set_block",
            "x": offset_x + i,
            "y": offset_y - 1,
            "z": offset_z,
            "id": 1,  # Stone
            "meta": 0
        })
    
    # Miejsce na power source (zostanie wstawione przez RCON /setblock)
    # Na razie tylko stone pod nim (już dodany wyżej)
    power_source_x = offset_x
    
    # Pierwszy blok redstone - wyłączony (meta=0, będzie aktywowany przez power source)
    edits.append({
        "op": "set_block",
        "x": offset_x + 1,
        "y": offset_y,
        "z": offset_z,
        "id": 55,  # Redstone wire
        "meta": 0   # Wyłączony - zostanie aktywowany przez RCON
    })
    
    # Aktualna pozycja X (zaczynamy od offset_x + 2, bo +0 to power source, +1 to pierwszy redstone)
    current_x = offset_x + 2
    
    # Generuj segmenty: redstone + repeater
    for rep in range(repeater_count):
        # Redstone dust (wire_length bloków)
        for i in range(wire_length):
            edits.append({
                "op": "set_block",
                "x": current_x + i,
                "y": offset_y,
                "z": offset_z,
                "id": 55,  # Redstone wire
                "meta": 15  # Max power
            })
        current_x += wire_length
        
        # Repeater - ID 93
        # Meta: bits 0-1 = delay (0-3), bits 2-3 = facing
        # facing east = 1, delay = 1 tick → meta = 1
        # delay = 4 ticki → meta = 5 (czyli delay=4, bo 0=1tick, 1=2ticks, 2=3ticks, 3=4ticks w nowszych, ale w 1.7.10: 0=1, 1=2, 2=3, 3=4)
        # W 1.7.10: 0=1 tick, 1=2 ticks, 2=3 ticks, 3=4 ticks
        # facing: 0=north, 1=east, 2=south, 3=west
        # facing east = 1, więc meta = 1 | (delay << 2)
        # Dla delay=4 ticki: delay_bits=3, meta = 1 | (3 << 2) = 1 | 12 = 13
        delay_bits = 3  # 4 ticki (max delay)
        repeater_meta = 1 | (delay_bits << 2)  # facing east + delay
        edits.append({
            "op": "set_block",
            "x": current_x,
            "y": offset_y,
            "z": offset_z,
            "id": 93,  # Repeater
            "meta": repeater_meta
        })
        current_x += 1
    
    # Ostatni odcinek redstone przed command blockiem
    for i in range(wire_length):
        edits.append({
            "op": "set_block",
            "x": current_x + i,
            "y": offset_y,
            "z": offset_z,
            "id": 55,
            "meta": 15
        })
    current_x += wire_length
    
    # Command Block - ID 137
    edits.append({
        "op": "set_block",
        "x": current_x,
        "y": offset_y,
        "z": offset_z,
        "id": 137,  # Command Block
        "meta": 0
    })
    
    # Komenda - jeśli nie podano, użyj domyślnej
    if command_msg is None:
        command_msg = f"/say [TEST_REDSTONE] {name} - Układ działa! Test PASS."
    
    # Tile Entity dla Command Blocka
    edits.append({
        "op": "set_te",
        "x": current_x,
        "y": offset_y,
        "z": offset_z,
        "nbt": {
            "id": "Control",
            "Command": command_msg,
            "CustomName": "@",
            "TrackOutput": 1,
            "SuccessCount": 0
        }
    })
    
    # Dodaj informacje o power source do metadanych
    power_source_info = {
        "x": power_source_x,
        "y": offset_y,
        "z": offset_z,
        "type": "redstone_torch" if power_source is None else power_source,
        "command": f"/setblock {power_source_x} {offset_y} {offset_z} minecraft:redstone_torch 5"
    }
    
    patch = {
        "metadata": {
            "name": name,
            "version": "1.7.10",
            "generated_by": "generate_patch.py",
            "offset": {"x": offset_x, "y": offset_y, "z": offset_z},
            "total_edits": len(edits),
            "wire_length": wire_length,
            "repeater_count": repeater_count,
            "command_block_x": current_x,
            "power_source": power_source_info
        },
        "edits": edits
    }
    
    return patch


def validate_patch(patch):
    """Walidacja patcha przed zapisaniem."""
    edits = patch.get("edits", [])
    
    # Sprawdź czy nie ma duplikatów pozycji (block + TE mogą być na tej samej pozycji)
    block_positions = set()
    for edit in edits:
        if edit["op"] == "set_block":
            pos = (edit["x"], edit["y"], edit["z"])
            if pos in block_positions:
                raise ValueError(f"Duplikat pozycji bloku: {pos}")
            block_positions.add(pos)
    
    # Sprawdź czy wszystkie bloki mają wymagane pola
    required_fields = {"set_block": ["x", "y", "z", "id"], "set_te": ["x", "y", "z", "nbt"]}
    for i, edit in enumerate(edits):
        op = edit.get("op")
        if op not in required_fields:
            raise ValueError(f"Nieznana operacja w edit #{i}: {op}")
        for field in required_fields[op]:
            if field not in edit:
                raise ValueError(f"Brak pola '{field}' w edit #{i}")
    
    return True


def main():
    parser = argparse.ArgumentParser(description="Generator patcha dla testu redstone")
    parser.add_argument("--output", "-o", default="redstone_test_patch.json", 
                       help="Nazwa pliku wyjściowego (domyślnie: redstone_test_patch.json)")
    parser.add_argument("--x", type=int, default=50, help="Offset X (domyślnie: 50)")
    parser.add_argument("--y", type=int, default=64, help="Offset Y (domyślnie: 64)")
    parser.add_argument("--z", type=int, default=50, help="Offset Z (domyślnie: 50)")
    
    args = parser.parse_args()
    
    print(f"Generowanie patcha dla układu testowego...")
    print(f"Offset: ({args.x}, {args.y}, {args.z})")
    
    patch = generate_redstone_test_patch(args.x, args.y, args.z)
    
    try:
        validate_patch(patch)
        print("[OK] Walidacja patcha: OK")
    except ValueError as e:
        print(f"[ERR] Błąd walidacji: {e}")
        return 1
    
    output_path = Path(args.output)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(patch, f, indent=2, ensure_ascii=False)
    
    print(f"[OK] Zapisano patch: {output_path}")
    print(f"   Liczba edycji: {patch['metadata']['total_edits']}")
    print(f"   Bloki: {len([e for e in patch['edits'] if e['op'] == 'set_block'])}")
    print(f"   Tile Entities: {len([e for e in patch['edits'] if e['op'] == 'set_te'])}")
    
    return 0


if __name__ == "__main__":
    exit(main())
