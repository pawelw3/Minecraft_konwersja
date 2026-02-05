"""
Generuje patch JSON z blokami ukośnymi (CuttableBlocks) do wstawienia na mapę testową.

Format bloku w 1.7.10:
- Block ID: będzie przypisany przez mod (np. "cuttableblocks:cuttable_block")
- Metadata: zależna od oryginalnego bloku
- TileEntity ("CuttableTE"): przechowuje oryginalny blok i płaszczyznę cięcia
"""

import json
import random
import math

def generate_diagonal_blocks_patch():
    """Generuje patch z blokami ukośnymi w różnych konfiguracjach"""
    
    blocks = []
    
    # Spawn point (przyjmujemy 0, 64, 0 jako spawn)
    spawn_x, spawn_y, spawn_z = 0, 64, 0
    
    # Definicje różnych cięć (normalne płaszczyzn)
    cut_types = [
        {"name": "45_XY", "normal": [1, 1, 0], "desc": "Przekątna pozioma XY"},
        {"name": "45_XZ", "normal": [1, 0, 1], "desc": "Przekątna XZ"},
        {"name": "45_YZ", "normal": [0, 1, 1], "desc": "Przekątna YZ"},
        {"name": "60_XYZ", "normal": [1, 1, 1], "desc": "Równomierna przestrzenna"},
        {"name": "30_X", "normal": [2, 1, 0], "desc": "Płaska X"},
        {"name": "22_5_X", "normal": [2.414, 1, 0], "desc": "Łagodna X"},
        {"name": "vertical_X", "normal": [1, 0, 0], "desc": "Pionowa X"},
        {"name": "vertical_Z", "normal": [0, 0, 1], "desc": "Pionowa Z"},
    ]
    
    # Oryginalne bloki (BlockID:Meta) - bloki z 1.7.10
    original_blocks = [
        {"id": "minecraft:stone", "meta": 0, "name": "Stone"},
        {"id": "minecraft:dirt", "meta": 0, "name": "Dirt"},
        {"id": "minecraft:planks", "meta": 0, "name": "Oak Planks"},
        {"id": "minecraft:planks", "meta": 1, "name": "Spruce Planks"},
        {"id": "minecraft:cobblestone", "meta": 0, "name": "Cobblestone"},
        {"id": "minecraft:brick_block", "meta": 0, "name": "Bricks"},
        {"id": "minecraft:stonebrick", "meta": 0, "name": "Stone Bricks"},
        {"id": "minecraft:stonebrick", "meta": 2, "name": "Cracked Stone Bricks"},
        {"id": "minecraft:wool", "meta": 14, "name": "Red Wool"},
        {"id": "minecraft:wool", "meta": 11, "name": "Blue Wool"},
    ]
    
    # Modowe bloki (jeśli są na mapie)
    mod_blocks = [
        {"id": "minecraft:gold_block", "meta": 0, "name": "Gold Block"},
        {"id": "minecraft:iron_block", "meta": 0, "name": "Iron Block"},
        {"id": "minecraft:diamond_block", "meta": 0, "name": "Diamond Block"},
        {"id": "minecraft:emerald_block", "meta": 0, "name": "Emerald Block"},
    ]
    
    all_blocks = original_blocks + mod_blocks
    
    # Generuj bloki w spiralnej formacji wokół spawnu
    # Pierwsza warstwa: różne typy cięć obok siebie
    print("Generowanie bloków ukośnych...")
    
    block_id = 1000  # Tymczasowy ID, mod przypisze właściwy
    
    # Warstwa 1: Płaszczyzny 45° w rzędzie (X += 3)
    for i, cut in enumerate(cut_types[:4]):
        x = spawn_x + (i - 1.5) * 4
        y = spawn_y
        z = spawn_z
        
        block = {
            "id": block_id,
            "x": int(x),
            "y": int(y),
            "z": int(z),
            "original_block": all_blocks[i % len(all_blocks)]["id"],
            "original_meta": all_blocks[i % len(all_blocks)]["meta"],
            "normal": cut["normal"],
            "keep_positive": True,
            "cut_type": cut["name"],
            "description": cut["desc"]
        }
        blocks.append(block)
        print(f"  Block {block_id}: {cut['name']} at ({x}, {y}, {z})")
        block_id += 1
    
    # Warstwa 2: Różne oryginalne bloki, to samo cięcie (Z += 3)
    for i, orig_block in enumerate(all_blocks[:6]):
        x = spawn_x + (i - 2.5) * 3
        y = spawn_y
        z = spawn_z + 5
        
        block = {
            "id": block_id,
            "x": int(x),
            "y": int(y),
            "z": int(z),
            "original_block": orig_block["id"],
            "original_meta": orig_block["meta"],
            "normal": [1, 1, 0],  # 45° XY
            "keep_positive": True,
            "cut_type": "45_XY",
            "description": f"{orig_block['name']} - 45°"
        }
        blocks.append(block)
        print(f"  Block {block_id}: {orig_block['name']} at ({x}, {y}, {z})")
        block_id += 1
    
    # Warstza 3: Różne kierunki keep_positive (Z += 3)
    for i in range(4):
        x = spawn_x + (i - 1.5) * 3
        y = spawn_y
        z = spawn_z + 10
        
        block = {
            "id": block_id,
            "x": int(x),
            "y": int(y),
            "z": int(z),
            "original_block": "minecraft:stone",
            "original_meta": 0,
            "normal": [1, 1, 0],
            "keep_positive": i % 2 == 0,
            "cut_type": "45_XY",
            "description": f"Stone - keep_positive={i % 2 == 0}"
        }
        blocks.append(block)
        print(f"  Block {block_id}: Stone keep_positive={i % 2 == 0} at ({x}, {y}, {z})")
        block_id += 1
    
    # Warstwa 4: Pionowe cięcia (Y += 1, różne X)
    vertical_cuts = [
        {"normal": [1, 0, 0], "name": "Vertical X"},
        {"normal": [0, 0, 1], "name": "Vertical Z"},
        {"normal": [1, 0, 1], "name": "Diagonal XZ"},
    ]
    for i, vcut in enumerate(vertical_cuts):
        x = spawn_x + (i - 1) * 4
        y = spawn_y + 1
        z = spawn_z + 2
        
        block = {
            "id": block_id,
            "x": int(x),
            "y": int(y),
            "z": int(z),
            "original_block": "minecraft:planks",
            "original_meta": 0,
            "normal": vcut["normal"],
            "keep_positive": True,
            "cut_type": vcut["name"].replace(" ", "_").lower(),
            "description": vcut["name"]
        }
        blocks.append(block)
        print(f"  Block {block_id}: {vcut['name']} at ({x}, {y}, {z})")
        block_id += 1
    
    # Warstwa 5: Więcej różnych kątów w głąb Z
    advanced_cuts = [
        {"normal": [2, 1, 0], "name": "30_X"},
        {"normal": [1, 2, 0], "name": "30_Y"},
        {"normal": [1, 1, 2], "name": "mixed_XYZ"},
        {"normal": [3, 1, 0], "name": "shallow_X"},
    ]
    for i, acut in enumerate(advanced_cuts):
        x = spawn_x + (i - 1.5) * 4
        y = spawn_y
        z = spawn_z - 5
        
        block = {
            "id": block_id,
            "x": int(x),
            "y": int(y),
            "z": int(z),
            "original_block": "minecraft:cobblestone",
            "original_meta": 0,
            "normal": acut["normal"],
            "keep_positive": True,
            "cut_type": acut["name"],
            "description": acut["name"]
        }
        blocks.append(block)
        print(f"  Block {block_id}: {acut['name']} at ({x}, {y}, {z})")
        block_id += 1
    
    # Dodaj kilka bloków wyżej/niżej (różne Y)
    for dy in [-2, 2]:
        for i in range(3):
            x = spawn_x + (i - 1) * 3
            y = spawn_y + dy
            z = spawn_z + 7
            
            block = {
                "id": block_id,
                "x": int(x),
                "y": int(y),
                "z": int(z),
                "original_block": "minecraft:wool",
                "original_meta": 14 if dy > 0 else 11,
                "normal": [1, 1, 0],
                "keep_positive": True,
                "cut_type": "45_XY",
                "description": f"Wool Y={y}"
            }
            blocks.append(block)
            print(f"  Block {block_id}: Wool Y={y} at ({x}, {y}, {z})")
            block_id += 1
    
    # Podsumowanie
    print(f"\nWygenerowano {len(blocks)} bloków ukośnych")
    
    # Sformatuj patch w formacie używanym przez jvm/worker
    patch = {
        "metadata": {
            "name": "CuttableBlocks Test Patch",
            "description": "Testowe bloki ukośne z różnymi kątami i teksturami",
            "version": "1.0",
            "generated_for": "cuttableblocks mod test"
        },
        "blocks": blocks
    }
    
    return patch

def save_patch(patch, filename="cuttable_test_patch.json"):
    """Zapisuje patch do pliku JSON"""
    with open(filename, 'w') as f:
        json.dump(patch, f, indent=2)
    print(f"\nZapisano patch do: {filename}")
    print(f"  Liczba bloków: {len(patch['blocks'])}")

if __name__ == '__main__':
    patch = generate_diagonal_blocks_patch()
    save_patch(patch)
    
    # Zapisz też w formacie dla JVM workera
    # JVM worker oczekuje formatu z chunks
    jvm_patch = {
        "metadata": patch["metadata"],
        "chunks": {}
    }
    
    # Grupuj bloki według chunków
    for block in patch["blocks"]:
        cx = block["x"] // 16
        cz = block["z"] // 16
        chunk_key = f"{cx},{cz}"
        
        if chunk_key not in jvm_patch["chunks"]:
            jvm_patch["chunks"][chunk_key] = {
                "x": cx,
                "z": cz,
                "blocks": []
            }
        
        jvm_patch["chunks"][chunk_key]["blocks"].append(block)
    
    with open("cuttable_test_patch_jvm.json", 'w') as f:
        json.dump(jvm_patch, f, indent=2)
    print(f"Zapisano patch JVM do: cuttable_test_patch_jvm.json")
    print(f"  Liczba chunków: {len(jvm_patch['chunks'])}")
