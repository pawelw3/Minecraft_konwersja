"""
Generuje patch JSON dla worker.jar z wszystkimi blokami CFM + TE.
Używa ID bloków z mapy 1.7.10 (level.dat -> FML/ItemData).
"""

import json
import gzip
import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..'))
from src.minecraft_map_parser.nbt_parser import parse_nbt

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..'))

def load_cfm_block_ids():
    """Wczytuje ID bloków CFM z level.dat mapy 1.7.10."""
    level_path = os.path.join(PROJECT_ROOT, 'mapa_1710', 'level.dat')
    with open(level_path, 'rb') as f:
        data = f.read()
    uncompressed = gzip.decompress(data)
    nbt = parse_nbt(uncompressed)

    fml = nbt['FML']
    if hasattr(fml, 'value'):
        fml = fml.value

    item_data = fml['ItemData']
    if hasattr(item_data, 'value'):
        item_data = item_data.value

    blocks = {}
    for item in item_data:
        if hasattr(item, 'value'):
            item = item.value
        if isinstance(item, dict):
            name = None
            id_val = None
            item_type = None
            for k, v in item.items():
                key = k.value if hasattr(k, 'value') else k
                val = v.value if hasattr(v, 'value') else v
                if key == 'K':
                    name = str(val)
                    item_type = name[0] if name else ''
                    name = name[1:]
                elif key == 'V':
                    id_val = val
            if name and name.startswith('cfm:') and item_type == '\x01':
                blocks[name] = id_val

    return blocks


def generate_patch():
    block_ids = load_cfm_block_ids()
    edits = []

    # TE IDs dla CFM (z analizy kodu źródłowego)
    TE_MAP = {
        'cfm:oven': 'cfmOven',
        'cfm:fridge': 'cfmFridge',
        'cfm:freezer': 'cfmFreezer',
        'cfm:cabinet': 'cfmCabinet',
        'cfm:bedsidecabinet': 'cfmCabinet',
        'cfm:wallcabinet': 'cfmCabinet',
        'cfm:kitchencabinet': 'cfmCabinet',
        'cfm:counterdoored': 'cfmCabinet',
        'cfm:microwave': 'cfmMicrowave',
        'cfm:printer': 'cfmPrinter',
        'cfm:washingmachine': 'cfmWashingMachine',
        'cfm:dishwasher': 'cfmDishwasher',
        'cfm:computer': 'cfmComputer',
        'cfm:stereo': 'cfmStereo',
        'cfm:blender': 'cfmBlender',
        'cfm:toaster': 'cfmToaster',
        'cfm:plate': 'cfmPlate',
        'cfm:bin': 'cfmBin',
        'cfm:cookiejar': 'cfmCookieJar',
    }

    # Bloki z metadanymi (kolory/orientacja)
    COLOR_BLOCKS = {'cfm:couch', 'cfm:chairwood', 'cfm:chairstone', 'cfm:barstool'}

    # Pozycja startowa (chunk 0,0 -> bloki 0-15)
    base_x, base_y, base_z = 0, 64, 0
    spacing = 2

    # 1. Wszystkie bloki CFM w siatce (bez kolorów)
    row = 0
    col = 0
    max_cols = 8

    for name in sorted(block_ids.keys()):
        bid = block_ids[name]
        x = base_x + col * spacing
        z = base_z + row * spacing
        y = base_y

        # Ustaw blok
        edits.append({
            "op": "set_block",
            "x": x, "y": y, "z": z,
            "id": bid,
            "meta": 0
        })

        # Dodaj TE jeśli blok go wymaga
        te_id = TE_MAP.get(name)
        if te_id:
            te_nbt = {"id": te_id}
            # Dodaj przykładowe inventory dla niektórych TE
            if name in {'cfm:oven', 'cfm:microwave', 'cfm:printer', 'cfm:washingmachine',
                        'cfm:dishwasher', 'cfm:computer', 'cfm:stereo', 'cfm:toaster',
                        'cfm:blender', 'cfm:plate', 'cfm:bin', 'cfm:cookiejar'}:
                # Proste TE bez inventory lub z pustym inventory
                pass
            elif name in {'cfm:fridge', 'cfm:freezer'}:
                # Fridge/Freezer - mają inventory slots
                te_nbt["Items"] = []
                for slot_idx in range(4):
                    te_nbt["Items"].append({
                        "id": 264,  # diamond
                        "Count": 1,
                        "Damage": 0,
                        "Slot": slot_idx
                    })
            elif name in {'cfm:cabinet', 'cfm:bedsidecabinet', 'cfm:wallcabinet',
                          'cfm:kitchencabinet', 'cfm:counterdoored'}:
                # Cabinet - różne slot names w zależności od typu
                slot_prefix = name.replace('cfm:', '').replace('cabinet', '').replace('counter', '')
                te_nbt["Items"] = []
                for slot_idx in range(4):
                    te_nbt["Items"].append({
                        "id": 264,
                        "Count": 1,
                        "Damage": 0,
                        "Slot": slot_idx
                    })

            edits.append({
                "op": "set_te",
                "x": x, "y": y, "z": z,
                "nbt": te_nbt
            })

        col += 1
        if col >= max_cols:
            col = 0
            row += 1

    # 2. Kolorowe warianty (couch, chair, barstool) - meta 0-15 w osobnej sekcji
    color_row = row + 2
    for name in sorted(COLOR_BLOCKS):
        if name not in block_ids:
            continue
        bid = block_ids[name]
        for meta in range(16):
            x = base_x + meta * spacing
            z = base_z + color_row * spacing
            y = base_y
            edits.append({
                "op": "set_block",
                "x": x, "y": y, "z": z,
                "id": bid,
                "meta": meta
            })
        color_row += 1

    # 3. Fridge+Freezer multiblock (obok siebie, różne orientacje)
    fridge_row = color_row + 1
    # Para Fridge+Freezer (meta = orientacja)
    for orient in range(4):
        x = base_x + orient * 4
        z = base_z + fridge_row * spacing
        y = base_y
        # Fridge
        edits.append({
            "op": "set_block",
            "x": x, "y": y, "z": z,
            "id": block_ids.get('cfm:fridge', 2737),
            "meta": orient
        })
        edits.append({
            "op": "set_te",
            "x": x, "y": y, "z": z,
            "nbt": {
                "id": "cfmFridge",
                "Items": [
                    {"id": 264, "Count": 2, "Damage": 0, "Slot": 0},
                    {"id": 265, "Count": 4, "Damage": 0, "Slot": 1}
                ]
            }
        })
        # Freezer
        edits.append({
            "op": "set_block",
            "x": x + 1, "y": y, "z": z,
            "id": block_ids.get('cfm:freezer', 2736),
            "meta": orient
        })
        edits.append({
            "op": "set_te",
            "x": x + 1, "y": y, "z": z,
            "nbt": {
                "id": "cfmFreezer",
                "Items": [
                    {"id": 266, "Count": 3, "Damage": 0, "Slot": 0}
                ]
            }
        })

    return {"edits": edits}


if __name__ == '__main__':
    patch = generate_patch()
    with open('cfm_full_patch.json', 'w') as f:
        json.dump(patch, f, indent=2)
    print(f"Generated patch with {len(patch['edits'])} edits")
    print("Saved to cfm_full_patch.json")
