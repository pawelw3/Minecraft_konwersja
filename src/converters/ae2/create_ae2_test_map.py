"""
Tworzenie testowej mapy 1.7.10 z wszystkimi blokami AE2.

Generuje JSON dla narzędzia JVM JVM, który ustawia:
- Wszystkie typy bloków AE2 z odpowiednimi ID
- Tile Entities z różnymi konfiguracjami (inventory, patterny, itp.)
"""

import json
import os
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
    # Bloki bez TE lub rzadkie - używamy tymczasowych ID
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
    "BlockGrinder": 248,
    "BlockCrank": 249,
    "BlockTinyTNT": 250,
    "BlockLightDetector": 251,
    "BlockQuartzFixture": 252,
}

def create_test_map_json():
    """Tworzy JSON z opisem testowej mapy AE2."""
    
    edits = []
    base_x, base_y, base_z = 0, 64, 0
    
    # Bloki w rzędzie - podstawowe bloki AE2
    basic_blocks = [
        ("BlockController", 0),
        ("BlockDrive", 0),
        ("BlockChest", 0),
        ("BlockInterface", 0),
        ("BlockMolecularAssembler", 0),
        ("BlockCraftingUnit", 0),  # metadata 0 = unit
        ("BlockCraftingUnit", 1),  # metadata 1 = co-processor
        ("BlockCraftingStorage", 0),  # 1k
        ("BlockCraftingStorage", 1),  # 4k
        ("BlockCraftingStorage", 2),  # 16k
        ("BlockCraftingStorage", 3),  # 64k
        ("BlockCraftingMonitor", 0),
        ("BlockCableBus", 0),
        ("BlockEnergyAcceptor", 0),
        ("BlockIOPort", 0),
        ("BlockInscriber", 0),
        ("BlockCharger", 0),
        ("BlockSecurity", 0),
        ("BlockQuartzGrowthAccelerator", 0),
        ("BlockCellWorkbench", 0),
        ("BlockEnergyCell", 0),
        ("BlockDenseEnergyCell", 0),
        ("BlockWireless", 0),
        ("BlockQuantumRing", 0),
        ("BlockQuantumLinkChamber", 0),
        ("BlockSpatialIOPort", 0),
        ("BlockSpatialPylon", 0),
        ("BlockCondenser", 0),
        ("BlockVibrationChamber", 0),
        ("BlockSkyChest", 0),
    ]
    
    # Ustaw bloki w rzędzie
    for i, (block_name, meta) in enumerate(basic_blocks):
        x = base_x + i
        y = base_y
        z = base_z
        block_id = AE2_BLOCKS[block_name]
        
        edits.append({
            "op": "set_block",
            "x": x,
            "y": y,
            "z": z,
            "id": block_id,
            "meta": meta
        })
        
        # Dodaj Tile Entity dla bloków, które je wymagajają
        te_data = create_tile_entity(block_name, x, y, z)
        if te_data:
            edits.append({
                "op": "set_te",
                "x": x,
                "y": y,
                "z": z,
                "nbt": te_data
            })
    
    # Druga warstwa - bloki z inventory
    inventory_blocks = [
        ("BlockDrive", create_drive_nbt()),
        ("BlockChest", create_chest_nbt()),
        ("BlockInterface", create_interface_nbt()),
        ("BlockInterface", create_interface_with_patterns_nbt()),
        ("BlockIOPort", create_io_port_nbt()),
        ("BlockInscriber", create_inscriber_nbt()),
        ("BlockCharger", create_charger_nbt()),
        ("BlockSecurity", create_security_nbt()),
    ]
    
    for i, (block_name, nbt_data) in enumerate(inventory_blocks):
        x = base_x + i
        y = base_y + 2
        z = base_z
        block_id = AE2_BLOCKS[block_name]
        
        edits.append({
            "op": "set_block",
            "x": x,
            "y": y,
            "z": z,
            "id": block_id,
            "meta": 0
        })
        
        if nbt_data:
            edits.append({
                "op": "set_te",
                "x": x,
                "y": y,
                "z": z,
                "nbt": nbt_data
            })
    
    # Trzecia warstwa - Crafting CPU różnych rozmiarów
    crafting_configs = [
        # (x, z, width, height, depth, storage_type)
        (0, 5, 2, 2, 2, "mixed"),  # Mały CPU
        (5, 5, 3, 2, 3, "64k"),    # Średni CPU
        (10, 5, 4, 3, 4, "mixed"), # Duży CPU
    ]
    
    for cx, cz, cw, ch, cd, storage_type in crafting_configs:
        for dx in range(cw):
            for dy in range(ch):
                for dz in range(cd):
                    x = base_x + cx + dx
                    y = base_y + 4 + dy
                    z = base_z + cz + dz
                    
                    # Ustaw crafting unit/storage
                    if storage_type == "mixed":
                        # Mieszane - różne rozmiary storage
                        meta = (dx + dy + dz) % 4
                        block_name = "BlockCraftingStorage"
                    else:
                        meta = 3 if storage_type == "64k" else 0
                        block_name = "BlockCraftingStorage"
                    
                    block_id = AE2_BLOCKS[block_name]
                    edits.append({
                        "op": "set_block",
                        "x": x,
                        "y": y,
                        "z": z,
                        "id": block_id,
                        "meta": meta
                    })
                    
                    # Dodaj TE dla storage
                    edits.append({
                        "op": "set_te",
                        "x": x,
                        "y": y,
                        "z": z,
                        "nbt": create_crafting_storage_nbt(x, y, z, meta)
                    })
    
    # Czwarta warstwa - Quantum Bridge
    quantum_positions = [
        (20, 5), (21, 5), (22, 5),  # Ring
        (21, 6),                      # Link Chamber
        (20, 6), (22, 6),             # Ring
        (20, 7), (21, 7), (22, 7),    # Ring
    ]
    
    for qx, qz in quantum_positions:
        x = base_x + qx
        y = base_y + 4
        z = base_z + qz
        
        if (qx, qz) == (21, 6):
            block_name = "BlockQuantumLinkChamber"
        else:
            block_name = "BlockQuantumRing"
        
        block_id = AE2_BLOCKS[block_name]
        edits.append({
            "op": "set_block",
            "x": x,
            "y": y,
            "z": z,
            "id": block_id,
            "meta": 0
        })
    
    # Piąta warstwa - Spatial IO
    spatial_positions = [
        (25, 5, "BlockSpatialIOPort"),
        (25, 6, "BlockSpatialPylon"),
        (26, 5, "BlockSpatialPylon"),
        (26, 6, "BlockSpatialPylon"),
        (27, 5, "BlockSpatialPylon"),
        (27, 6, "BlockSpatialPylon"),
    ]
    
    for sx, sz, block_name in spatial_positions:
        x = base_x + sx
        y = base_y + 4
        z = base_z + sz
        block_id = AE2_BLOCKS[block_name]
        edits.append({
            "op": "set_block",
            "x": x,
            "y": y,
            "z": z,
            "id": block_id,
            "meta": 0
        })
    
    # Szósta warstwa - Kable i części (CableBus)
    cable_positions = [
        (0, 10), (1, 10), (2, 10), (3, 10),
        (0, 11), (1, 11), (2, 11), (3, 11),
    ]
    
    for cx, cz in cable_positions:
        x = base_x + cx
        y = base_y + 2
        z = base_z + cz
        block_id = AE2_BLOCKS["BlockCableBus"]
        edits.append({
            "op": "set_block",
            "x": x,
            "y": y,
            "z": z,
            "id": block_id,
            "meta": 0
        })
        
        # Dodaj CableBus TE z różnymi konfiguracjami
        edits.append({
            "op": "set_te",
            "x": x,
            "y": y,
            "z": z,
            "nbt": create_cable_bus_nbt(cx, cz)
        })
    
    return {"edits": edits}


def create_tile_entity(block_name, x, y, z):
    """Tworzy podstawowe Tile Entity dla bloku AE2."""
    base_nbt = {
        "id": block_name,
        "x": x,
        "y": y,
        "z": z,
        "forward": 2,  # North
        "up": 1,       # Up
    }
    
    # Dodaj specyficzne pola dla różnych typów bloków
    if block_name == "BlockController":
        base_nbt["energy"] = 8000.0  # Pełna energia
        
    elif block_name == "BlockDrive":
        base_nbt["priority"] = 0
        base_nbt["fuzzyMode"] = 0
        # Puste inventory - zostanie wypełnione w create_drive_nbt
        
    elif block_name == "BlockInterface":
        base_nbt["priority"] = 0
        base_nbt["blockingMode"] = 0
        
    elif block_name == "BlockMolecularAssembler":
        base_nbt["progress"] = 0
        base_nbt["isCrafting"] = 0
        
    return base_nbt


def create_drive_nbt():
    """Tworzy NBT dla ME Drive z storage cells."""
    return {
        "id": "BlockDrive",
        "priority": 5,
        "fuzzyMode": 0,
        "forward": 2,
        "up": 1,
        "inv": {
            "item0": {
                "id": "appliedenergistics2:item.ItemBasicStorageCell.1k",
                "Count": 1,
                "Damage": 0,
                "tag": {
                    "StorageCell": {
                        "items": [],
                        "itemCount": 0
                    }
                }
            },
            "item1": {
                "id": "appliedenergistics2:item.ItemBasicStorageCell.4k",
                "Count": 1,
                "Damage": 0,
                "tag": {
                    "StorageCell": {
                        "items": [
                            {"id": "minecraft:cobblestone", "Count": 64, "Damage": 0, "Slot": 0}
                        ],
                        "itemCount": 64
                    }
                }
            },
            "item2": {
                "id": "appliedenergistics2:item.ItemBasicStorageCell.16k",
                "Count": 1,
                "Damage": 0
            },
            "item3": {
                "id": "appliedenergistics2:item.ItemBasicStorageCell.64k",
                "Count": 1,
                "Damage": 0
            },
            "item4": {
                "id": "appliedenergistics2:item.ItemViewCell",
                "Count": 1,
                "Damage": 0
            }
        }
    }


def create_chest_nbt():
    """Tworzy NBT dla ME Chest."""
    return {
        "id": "BlockChest",
        "priority": 0,
        "fuzzyMode": 0,
        "forward": 2,
        "up": 1,
        "item": {
            "id": "appliedenergistics2:item.ItemBasicStorageCell.4k",
            "Count": 1,
            "Damage": 0,
            "tag": {
                "StorageCell": {
                    "items": [
                        {"id": "minecraft:diamond", "Count": 16, "Damage": 0, "Slot": 0}
                    ],
                    "itemCount": 16
                }
            }
        }
    }


def create_interface_nbt():
    """Tworzy NBT dla ME Interface (bez patternów)."""
    return {
        "id": "BlockInterface",
        "priority": 0,
        "blockingMode": 0,
        "forward": 2,
        "up": 1,
        "config": {
            "item0": {"id": "minecraft:cobblestone", "Count": 64, "Damage": 0},
            "item1": {"id": "minecraft:stone", "Count": 32, "Damage": 0}
        },
        "storage": {}
    }


def create_interface_with_patterns_nbt():
    """Tworzy NBT dla ME Interface z patternami."""
    return {
        "id": "BlockInterface",
        "priority": 10,
        "blockingMode": 1,
        "forward": 3,  # South
        "up": 1,
        "config": {},
        "storage": {},
        "patterns": {
            "item0": {
                "id": "appliedenergistics2:item.ItemEncodedPattern",
                "Count": 1,
                "Damage": 0,
                "tag": {
                    "crafting": 1,
                    "in": {
                        "item0": {"id": "minecraft:cobblestone", "Count": 3, "Damage": 0}
                    },
                    "out": {
                        "item0": {"id": "minecraft:stone_slab", "Count": 6, "Damage": 0}
                    }
                }
            },
            "item1": {
                "id": "appliedenergistics2:item.ItemEncodedPattern",
                "Count": 1,
                "Damage": 0,
                "tag": {
                    "crafting": 1,
                    "in": {
                        "item0": {"id": "minecraft:planks", "Count": 4, "Damage": 0}
                    },
                    "out": {
                        "item0": {"id": "minecraft:crafting_table", "Count": 1, "Damage": 0}
                    }
                }
            }
        }
    }


def create_io_port_nbt():
    """Tworzy NBT dla IO Port."""
    return {
        "id": "BlockIOPort",
        "forward": 2,
        "up": 1,
        "mode": 0,  # Transfer mode
    }


def create_inscriber_nbt():
    """Tworzy NBT dla Inscribera."""
    return {
        "id": "BlockInscriber",
        "forward": 2,
        "up": 1,
        "inv": {
            "item0": {"id": "appliedenergistics2:item.ItemMultiMaterial", "Count": 1, "Damage": 16},  # Printed Logic
            "item1": {"id": "appliedenergistics2:item.ItemMultiMaterial", "Count": 1, "Damage": 20},  # Silicon
        },
        "processing": 0
    }


def create_charger_nbt():
    """Tworzy NBT dla Chargera."""
    return {
        "id": "BlockCharger",
        "forward": 2,
        "up": 1,
        "inv": {
            "item0": {"id": "appliedenergistics2:item.ItemMultiMaterial", "Count": 1, "Damage": 1}  # Certus Quartz
        }
    }


def create_security_nbt():
    """Tworzy NBT dla Security Station."""
    return {
        "id": "BlockSecurity",
        "forward": 2,
        "up": 1,
        "user": "test_player_uuid"
    }


def create_crafting_storage_nbt(x, y, z, meta):
    """Tworzy NBT dla Crafting Storage."""
    sizes = {0: "1k", 1: "4k", 2: "16k", 3: "64k"}
    return {
        "id": "BlockCraftingStorage",
        "x": x,
        "y": y,
        "z": z,
        "size": sizes.get(meta, "1k"),
        "forward": 2,
        "up": 1
    }


def create_cable_bus_nbt(cx, cz):
    """Tworzy NBT dla Cable Bus (multipart)."""
    # Różne konfiguracje kabli
    cable_types = [
        {"type": "glass", "color": "fluix"},
        {"type": "covered", "color": "white"},
        {"type": "smart", "color": "fluix"},
        {"type": "dense", "color": "fluix"},
    ]
    
    cable_idx = (cx + cz) % len(cable_types)
    cable = cable_types[cable_idx]
    
    return {
        "id": "BlockCableBus",
        "cableType": cable["type"],
        "color": cable["color"],
        "connections": [0, 1, 2, 3, 4, 5],  # Wszystkie strony
        "parts": [
            {"type": "cable", "id": f"part.cable.{cable['type']}.{cable['color']}"}
        ]
    }


def main():
    """Główna funkcja - generuje JSON dla narzędzia JVM."""
    test_map = create_test_map_json()
    
    output_dir = Path("lightweigh_map_templates/1710_modded/ae2_test")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    output_file = output_dir / "ae2_test_patch.json"
    with open(output_file, 'w') as f:
        json.dump(test_map, f, indent=2)
    
    print(f"Utworzono plik: {output_file}")
    print(f"Liczba operacji: {len(test_map['edits'])}")
    
    # Podsumowanie bloków
    block_counts = {}
    for edit in test_map['edits']:
        if edit['op'] == 'set_block':
            block_id = edit['id']
            block_counts[block_id] = block_counts.get(block_id, 0) + 1
    
    print("\nBloki do ustawienia:")
    for block_id, count in sorted(block_counts.items()):
        print(f"  ID {block_id}: {count}x")


if __name__ == "__main__":
    main()
