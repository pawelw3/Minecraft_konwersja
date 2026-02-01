"""
Tworzenie ROZSZERZONEJ testowej mapy 1.7.10 z dużą ilością bloków AE2.
20x więcej bloków niż wersja podstawowa (~2400 bloków)
Bloki rozproszone w różnych miejscach i na różnych wysokościach.
"""

import json
import os
import random
from pathlib import Path

# ID bloków AE2 z mapy głównej (1.7.10)
AE2_BLOCKS = {
    "BlockController": 208,
    "BlockDrive": 156,
    "BlockChest": 115,
    "BlockInterface": 192,
    "BlockMolecularAssembler": 117,
    "BlockCraftingUnit": 232,
    "BlockCraftingStorage": 127,
    "BlockCraftingMonitor": 54,
    "BlockCableBus": 236,
    "BlockEnergyAcceptor": 149,
    "BlockIOPort": 160,
    "BlockInscriber": 233,
    "BlockCharger": 213,
    "BlockSecurity": 236,
    "BlockQuartzGrowthAccelerator": 56,
    "BlockCellWorkbench": 193,
    "BlockEnergyCell": 238,
    "BlockDenseEnergyCell": 239,
    "BlockWireless": 240,
    "BlockQuantumRing": 241,
    "BlockQuantumLinkChamber": 242,
    "BlockSpatialIOPort": 243,
    "BlockSpatialPylon": 244,
    "BlockCondenser": 245,
    "BlockVibrationChamber": 246,
    "BlockSkyChest": 247,
}

def create_nbt_for_block(block_name, x, y, z, variant=0):
    """Tworzy NBT dla danego bloku AE2."""
    base_nbt = {
        "id": block_name,
        "x": x,
        "y": y,
        "z": z,
    }
    
    if block_name == "BlockController":
        base_nbt.update({"forward": 2, "up": 1, "energy": 8000.0})
    elif block_name == "BlockDrive":
        # Dodaj storage cells w niektórych slotach
        inv = {}
        for slot in range(10):
            if random.random() > 0.5:  # 50% szans na cell
                cell_types = ["ItemBasicStorageCell.1k", "ItemBasicStorageCell.4k", 
                             "ItemBasicStorageCell.16k", "ItemBasicStorageCell.64k",
                             "ItemViewCell"]
                inv[f"item{slot}"] = {"id": random.choice(cell_types), "Count": 1, "Damage": 0}
        base_nbt.update({"forward": 2, "up": 1, "priority": 0, "fuzzyMode": 0, "inv": inv})
    elif block_name == "BlockChest":
        if random.random() > 0.7:
            base_nbt["item"] = {"id": "ItemBasicStorageCell.4k", "Count": 1, "Damage": 0}
    elif block_name == "BlockInterface":
        base_nbt.update({"forward": 2, "up": 1, "priority": 0, "blockingMode": 0})
    elif block_name == "BlockCraftingUnit":
        base_nbt.update({"forward": 2, "up": 1, "core": variant == 0})
    elif block_name == "BlockCraftingStorage":
        size_map = {0: "1k", 1: "4k", 2: "16k", 3: "64k"}
        base_nbt.update({"forward": 2, "up": 1, "storage": size_map.get(variant, "1k")})
    elif block_name == "BlockEnergyCell":
        base_nbt.update({"forward": 2, "up": 1, "energy": random.randint(1000, 50000)})
    elif block_name == "BlockDenseEnergyCell":
        base_nbt.update({"forward": 2, "up": 1, "energy": random.randint(5000, 200000)})
    elif block_name == "BlockInscriber":
        # Czasem dodaj przedmioty do inscribera
        if random.random() > 0.6:
            items = ["ItemMaterial.LogicProcessor", "ItemMaterial.CalcProcessor", "ItemMaterial.EngProcessor"]
            top = {"id": random.choice(items), "Count": 1, "Damage": 0}
            bottom = {"id": "ItemMaterial.Silicon", "Count": random.randint(1,5), "Damage": 0}
            base_nbt.update({"forward": 2, "up": 1, "top": top, "bottom": bottom})
        else:
            base_nbt.update({"forward": 2, "up": 1})
    elif block_name in ["BlockCharger", "BlockIOPort", "BlockSecurity", 
                       "BlockQuartzGrowthAccelerator", "BlockCellWorkbench"]:
        base_nbt.update({"forward": 2, "up": 1})
    else:
        base_nbt.update({"forward": 2, "up": 1})
    
    return base_nbt

def generate_scattered_positions(count, area_size=200, y_range=(60, 90)):
    """Generuje rozproszone pozycje w obszarze."""
    positions = []
    used = set()
    
    for _ in range(count):
        attempts = 0
        while attempts < 100:
            x = random.randint(-area_size//2, area_size//2)
            z = random.randint(-area_size//2, area_size//2)
            y = random.randint(y_range[0], y_range[1])
            
            # Unikaj duplikatów
            key = (x, y, z)
            if key not in used:
                used.add(key)
                positions.append((x, y, z))
                break
            attempts += 1
    
    return positions

def create_extended_test_map():
    """Tworzy rozszerzoną testową mapę AE2."""
    
    edits = []
    random.seed(42)  # Dla powtarzalności
    
    # Lista typów bloków do wygenerowania (z wagami - częstotliwość)
    block_types = [
        # (nazwa, ilość, metadata_variant)
        ("BlockController", 20, [0]),  # 20 kontrolerów
        ("BlockDrive", 100, [0]),  # 100 drive'ów
        ("BlockChest", 60, [0]),  # 60 chestów
        ("BlockInterface", 150, [0]),  # 150 interfejsów
        ("BlockMolecularAssembler", 80, [0]),  # 80 assemblerów
        ("BlockCraftingUnit", 100, [0, 1]),  # 100 crafting units (różne typy)
        ("BlockCraftingStorage", 300, [0, 1, 2, 3]),  # 300 storage (różne rozmiary)
        ("BlockCraftingMonitor", 50, [0]),  # 50 monitorów
        ("BlockCableBus", 400, [0]),  # 400 kabli/części
        ("BlockEnergyAcceptor", 40, [0]),  # 40 acceptorów
        ("BlockEnergyCell", 60, [0]),  # 60 celli energii
        ("BlockDenseEnergyCell", 30, [0]),  # 30 dense celli
        ("BlockIOPort", 50, [0]),  # 50 IO portów
        ("BlockInscriber", 80, [0]),  # 80 inscriberów
        ("BlockCharger", 40, [0]),  # 40 chargerów
        ("BlockSecurity", 25, [0]),  # 25 security stations
        ("BlockQuartzGrowthAccelerator", 60, [0]),  # 60 acceleratorów
        ("BlockCellWorkbench", 40, [0]),  # 40 workbenchy
        ("BlockWireless", 30, [0]),  # 30 wireless AP
        ("BlockQuantumRing", 60, [0]),  # 60 quantum rings
        ("BlockQuantumLinkChamber", 20, [0]),  # 20 link chamberów
        ("BlockSpatialIOPort", 20, [0]),  # 20 spatial IO
        ("BlockSpatialPylon", 100, [0]),  # 100 pylonów
        ("BlockCondenser", 30, [0]),  # 30 condenserów
        ("BlockVibrationChamber", 25, [0]),  # 25 vibration chamberów
        ("BlockSkyChest", 80, [0]),  # 80 sky chestów
    ]
    
    total_blocks = sum(count for _, count, _ in block_types)
    print(f"Generowanie {total_blocks} bloków AE2...")
    
    # Generuj pozycje dla wszystkich bloków
    positions = generate_scattered_positions(total_blocks, area_size=300, y_range=(55, 95))
    
    pos_idx = 0
    for block_name, count, variants in block_types:
        for i in range(count):
            if pos_idx >= len(positions):
                break
                
            x, y, z = positions[pos_idx]
            block_id = AE2_BLOCKS[block_name]
            variant = random.choice(variants)
            
            # Dodaj blok
            edits.append({
                "op": "set_block",
                "x": x,
                "y": y,
                "z": z,
                "id": block_id,
                "meta": variant
            })
            
            # Dodaj Tile Entity
            nbt = create_nbt_for_block(block_name, x, y, z, variant)
            edits.append({
                "op": "set_te",
                "x": x,
                "y": y,
                "z": z,
                "nbt": nbt
            })
            
            pos_idx += 1
    
    # Zapisz plik JSON
    output = {"edits": edits}
    
    output_dir = Path("lightweigh_map_templates/1710_modded/ae2_test_extended")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    output_file = output_dir / "ae2_extended_patch.json"
    with open(output_file, 'w') as f:
        json.dump(output, f, indent=2)
    
    print(f"\nZapisano {len(edits)} operacji do: {output_file}")
    print(f"Liczba bloków: {len(edits)//2}")
    print(f"Obszar: X: -150 do 150, Z: -150 do 150, Y: 55-95")
    
    # Pokaż statystyki
    print("\n=== STATYSTYKI ===")
    for block_name, count, _ in block_types:
        print(f"{block_name}: {count}")
    
    return output_file

if __name__ == "__main__":
    create_extended_test_map()
