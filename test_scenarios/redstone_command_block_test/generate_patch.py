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

def generate_redstone_test_patch(offset_x=50, offset_y=64, offset_z=50):
    """
    Generuje patch dla układu testowego redstone z command blockiem.
    
    Układ:
    - Dźwignia (Lever) na początku
    - Redstone dust (3 bloki)
    - Repeater (delay=4 ticki)
    - Redstone dust (3 bloki)
    - Repeater (delay=4 ticki)
    - Redstone dust (1 blok)
    - Command Block (z Tile Entity)
    """
    
    edits = []
    
    # Podłoga (stone) pod całym układem
    for i in range(11):
        edits.append({
            "op": "set_block",
            "x": offset_x + i,
            "y": offset_y - 1,
            "z": offset_z,
            "id": 1,  # Stone
            "meta": 0
        })
    
    # Dźwignia (Lever) - ID 69, meta 5 = facing east, active
    edits.append({
        "op": "set_block",
        "x": offset_x,
        "y": offset_y,
        "z": offset_z,
        "id": 69,
        "meta": 5
    })
    
    # Redstone dust (3 bloki) - ID 55, meta 15 = fully powered
    for i in range(1, 4):
        edits.append({
            "op": "set_block",
            "x": offset_x + i,
            "y": offset_y,
            "z": offset_z,
            "id": 55,  # Redstone wire
            "meta": 15  # Max power
        })
    
    # Repeater 1 - ID 93 (inactive), meta 5 = facing east, delay=1
    # W MC 1.7.10: bits 0-1 = delay (0-3), bits 2-3 = facing
    # facing east = 1, delay = 0 (1 tick) → meta = 1 | (0 << 2) = 1
    # ALE: w praktyce repeater sam się aktualizuje gdy dostanie sygnał
    edits.append({
        "op": "set_block",
        "x": offset_x + 4,
        "y": offset_y,
        "z": offset_z,
        "id": 93,  # Repeater (inactive)
        "meta": 1   # Facing east, delay=1
    })
    
    # Redstone dust (3 bloki)
    for i in range(5, 8):
        edits.append({
            "op": "set_block",
            "x": offset_x + i,
            "y": offset_y,
            "z": offset_z,
            "id": 55,
            "meta": 15
        })
    
    # Repeater 2 - ID 93
    edits.append({
        "op": "set_block",
        "x": offset_x + 8,
        "y": offset_y,
        "z": offset_z,
        "id": 93,
        "meta": 1  # Facing east, delay=1
    })
    
    # Redstone dust (1 blok) przed command blockiem
    edits.append({
        "op": "set_block",
        "x": offset_x + 9,
        "y": offset_y,
        "z": offset_z,
        "id": 55,
        "meta": 15
    })
    
    # Command Block - ID 137
    edits.append({
        "op": "set_block",
        "x": offset_x + 10,
        "y": offset_y,
        "z": offset_z,
        "id": 137,  # Command Block
        "meta": 0
    })
    
    # Tile Entity dla Command Blocka
    edits.append({
        "op": "set_te",
        "x": offset_x + 10,
        "y": offset_y,
        "z": offset_z,
        "nbt": {
            "id": "Control",
            "Command": "/say [TEST_REDSTONE] Układ redstone działa poprawnie! Test PASS.",
            "CustomName": "@",
            "TrackOutput": 1,
            "SuccessCount": 0
        }
    })
    
    patch = {
        "metadata": {
            "name": "Redstone Command Block Test",
            "version": "1.7.10",
            "generated_by": "generate_patch.py",
            "offset": {"x": offset_x, "y": offset_y, "z": offset_z},
            "total_edits": len(edits)
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
