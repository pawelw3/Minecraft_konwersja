"""
Tworzenie testowej mapy 1.7.10 z blokami Blood Magic.

Ten skrypt generuje plik patch JSON który może być zastosowany przez narzędzie JVM
do stworzenia mapy testowej z różnymi blokami i Tile Entities Blood Magic.
"""

import json
import os
from pathlib import Path
from typing import Dict, Any, List


def create_blood_altar_te(x: int, y: int, z: int, tier: int, lp: int, active: bool = False) -> Dict[str, Any]:
    """
    Stwórz Tile Entity dla Blood Altar.
    
    WAŻNE: W 1.7.10 rzeczywiste TE ID na mapie to "containerAltar" (nie "Altar")
    """
    return {
        "op": "set_te",
        "x": x,
        "y": y,
        "z": z,
        "nbt": {
            "id": "containerAltar",  # Rzeczywiste TE ID z mapy
            "x": x,
            "y": y,
            "z": z,
            "currentEssence": lp,
            "upgradeLevel": tier,
            "isActive": active,
            "progress": 0 if not active else 50,
            "liquidRequired": 1000 if active else 0,
            "canBeFilled": True
        }
    }


def create_master_ritual_stone_te(
    x: int, y: int, z: int, 
    ritual_type: str, 
    owner: str = "TestPlayer",
    active: bool = False
) -> Dict[str, Any]:
    """
    Stwórz Tile Entity dla Master Ritual Stone.
    
    WAŻNE: W 1.7.10 rzeczywiste TE ID na mapie to "containerMasterStone"
    """
    return {
        "op": "set_te",
        "x": x,
        "y": y,
        "z": z,
        "nbt": {
            "id": "containerMasterStone",  # Rzeczywiste TE ID z mapy
            "x": x,
            "y": y,
            "z": z,
            "ritualType": ritual_type,
            "owner": owner,
            "isActive": active,
            "cooldown": 0,
            "runningTime": 0 if not active else 1200
        }
    }


def create_block_edit(x: int, y: int, z: int, block_id: int, meta: int = 0) -> Dict[str, Any]:
    """Stwórz edycję bloku."""
    return {
        "op": "set_block",
        "x": x,
        "y": y,
        "z": z,
        "id": block_id,
        "meta": meta
    }


def generate_bloodmagic_test_patch() -> Dict[str, Any]:
    """
    Generuje pełny patch JSON z testowymi blokami Blood Magic.
    
    Używamy placeholder ID dla bloków modów (1000+) ponieważ:
    - W 1.7.10 ID bloków modów są dynamiczne (przydzielane przez Forge)
    - Konwerter Python rozpoznaje bloki po Tile Entity ID
    - Podczas konwersji na 1.18.2, ID string są używane do mapowania
    """
    edits = []
    
    # Podłoga z kamienia (vanilla) dla referencji
    for x in range(-5, 15):
        for z in range(-5, 20):
            edits.append(create_block_edit(x, 63, z, 1, 0))  # Stone
    
    # === SEKCJA 1: Blood Altars z różnymi tierami ===
    section1_x = 0
    section1_z = 0
    
    # Tier 1 - pusty
    edits.append(create_block_edit(section1_x, 64, section1_z, 1000, 0))  # Altar placeholder
    edits.append(create_blood_altar_te(section1_x, 64, section1_z, tier=1, lp=0))
    
    # Tier 2 - z LP
    edits.append(create_block_edit(section1_x + 2, 64, section1_z, 1000, 0))
    edits.append(create_blood_altar_te(section1_x + 2, 64, section1_z, tier=2, lp=5000))
    
    # Tier 3 - aktywny crafting
    edits.append(create_block_edit(section1_x + 4, 64, section1_z, 1000, 0))
    edits.append(create_blood_altar_te(section1_x + 4, 64, section1_z, tier=3, lp=10000, active=True))
    
    # Tier 4 - pełny
    edits.append(create_block_edit(section1_x + 6, 64, section1_z, 1000, 0))
    edits.append(create_blood_altar_te(section1_x + 6, 64, section1_z, tier=4, lp=25000))
    
    # Tier 5 - max
    edits.append(create_block_edit(section1_x + 8, 64, section1_z, 1000, 0))
    edits.append(create_blood_altar_te(section1_x + 8, 64, section1_z, tier=5, lp=50000))
    
    # === SEKCJA 2: Master Ritual Stones z różnymi rytuałami ===
    section2_x = 0
    section2_z = 5
    
    # Well of Suffering - aktywny
    edits.append(create_block_edit(section2_x, 64, section2_z, 1001, 0))
    edits.append(create_master_ritual_stone_te(
        section2_x, 64, section2_z, 
        ritual_type="suffering",
        active=True
    ))
    
    # Water - nieaktywny
    edits.append(create_block_edit(section2_x + 3, 64, section2_z, 1001, 0))
    edits.append(create_master_ritual_stone_te(
        section2_x + 3, 64, section2_z, 
        ritual_type="water",
        active=False
    ))
    
    # Speed
    edits.append(create_block_edit(section2_x + 6, 64, section2_z, 1001, 0))
    edits.append(create_master_ritual_stone_te(
        section2_x + 6, 64, section2_z, 
        ritual_type="speed",
        active=False
    ))
    
    # Regeneration - aktywny
    edits.append(create_block_edit(section2_x + 9, 64, section2_z, 1001, 0))
    edits.append(create_master_ritual_stone_te(
        section2_x + 9, 64, section2_z, 
        ritual_type="regeneration",
        active=True
    ))
    
    # === SEKCJA 3: Blood Runes (różne typy) ===
    section3_x = 0
    section3_z = 10
    
    # Speed Rune (osobny blok w 1.7.10)
    edits.append(create_block_edit(section3_x, 64, section3_z, 1010, 0))
    
    # Efficiency Rune
    edits.append(create_block_edit(section3_x + 1, 64, section3_z, 1011, 0))
    
    # Sacrifice Rune
    edits.append(create_block_edit(section3_x + 2, 64, section3_z, 1012, 0))
    
    # Self-Sacrifice Rune
    edits.append(create_block_edit(section3_x + 3, 64, section3_z, 1013, 0))
    
    # Blood Rune z metadanymi (0-5)
    for meta in range(6):
        edits.append(create_block_edit(section3_x + 4 + meta, 64, section3_z, 1014, meta))
    
    # === SEKCJA 4: Struktura ołtarza Tier 3 ===
    # Symulacja struktury ołtarza z runami
    altar_x = 10
    altar_z = 0
    
    # Centralny ołtarz
    edits.append(create_block_edit(altar_x, 64, altar_z, 1000, 0))
    edits.append(create_blood_altar_te(altar_x, 64, altar_z, tier=3, lp=15000))
    
    # Runy wokół (pierścień 3x3)
    rune_positions = [
        (-1, -1), (0, -1), (1, -1),
        (-1, 0),           (1, 0),
        (-1, 1),  (0, 1),  (1, 1)
    ]
    
    for dx, dz in rune_positions:
        edits.append(create_block_edit(altar_x + dx, 64, altar_z + dz, 1010, 0))  # Speed rune
    
    # === SEKCJA 5: Bloki dekoracyjne ===
    section5_x = 10
    section5_z = 5
    
    # Large Bloodstone Brick
    edits.append(create_block_edit(section5_x, 64, section5_z, 1020, 0))
    
    # Bloodstone Brick
    edits.append(create_block_edit(section5_x + 1, 64, section5_z, 1021, 0))
    
    # Ritual Stone (placeholder)
    edits.append(create_block_edit(section5_x + 2, 64, section5_z, 1022, 0))
    
    # Imperfect Ritual Stone (placeholder)
    edits.append(create_block_edit(section5_x + 3, 64, section5_z, 1023, 0))
    
    # === SEKCJA 6: Soul Forge (usunięty w 1.18.2 - test fallbacku) ===
    section6_x = 10
    section6_z = 10
    
    edits.append(create_block_edit(section6_x, 64, section6_z, 1030, 0))
    edits.append({
        "op": "set_te",
        "x": section6_x,
        "y": 64,
        "z": section6_z,
        "nbt": {
            "id": "SoulForge",
            "x": section6_x,
            "y": 64,
            "z": section6_z,
            "progress": 50
        }
    })
    
    return {"edits": edits}


def save_patch(output_path: Path, patch: Dict[str, Any]) -> None:
    """Zapisz patch do pliku JSON."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, 'w') as f:
        json.dump(patch, f, indent=2)
    print(f"Zapisano patch: {output_path}")
    print(f"Liczba edycji: {len(patch['edits'])}")


def main():
    """Główna funkcja generująca testową mapę."""
    # Ścieżki
    base_dir = Path("lightweigh_map_templates/1710_modded/bloodmagic_test")
    patch_file = base_dir / "bloodmagic_patch.json"
    
    # Upewnij się że katalog istnieje
    base_dir.mkdir(parents=True, exist_ok=True)
    
    # Generuj patch
    patch = generate_bloodmagic_test_patch()
    save_patch(patch_file, patch)
    
    print("\n=== Instrukcja stworzenia mapy testowej ===")
    print(f"1. Upewnij się że świat '{base_dir}' ma folder 'region'")
    print(f"2. Uruchom narzędzie JVM:")
    print(f"   cd jvm/worker")
    print(f"   java -jar build/libs/mc-editkit-worker-1.0-SNAPSHOT.jar \\")
    print(f"       --world ../../{base_dir} \\")
    print(f"       --patch bloodmagic_patch.json")
    print(f"\n3. Sprawdź czy mapa została stworzona poprawnie:")
    print(f"   java -jar build/libs/mc-editkit-worker-1.0-SNAPSHOT.jar \\")
    print(f"       --world ../../{base_dir} \\")
    print(f"       --list-regions")
    
    return patch_file


if __name__ == "__main__":
    main()
