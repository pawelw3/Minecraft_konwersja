"""
Tworzenie testowej mapy 1.7.10 z blokami Thermal Series.

Uzywa mc_editkit do bezposredniej edycji plikow .mca.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from mc_editkit.world.backends.anvil_backend import AnvilBackend
from mc_editkit.world.types import Pos

# ID blokow Thermal z modpacka 1710 (z level.dat)
THERMAL_BLOCKS = {
    "Machine": 3438,
    "Device": 3439,
    "Dynamo": 3440,
    "Cell": 3441,
    "Tank": 3442,
    "Strongbox": 3443,
    "Cache": 3444,
    "Workbench": 3445,
    "Tesseract": 3446,
    "Plate": 3447,
    "Light": 3448,
    "Frame": 3449,
    "Glass": 3450,
    "Rockwool": 3451,
    "Sponge": 3452,
}

# Thermal Dynamics duct blocks (blockDuct array with metadata offsets)
THERMAL_DUCTS = {
    0: 3304,   # meta 0-15
    16: 3305,  # meta 16-31
    32: 3306,  # meta 32-47
    48: 3307,  # meta 48-63
    64: 3308,  # meta 64-79
}

# Thermal Foundation fluid blocks
THERMAL_FLUIDS = {
    "FluidRedstone": 964,
    "FluidGlowstone": 965,
    "FluidEnder": 1293,
    "FluidCryotheum": 968,
    "FluidPyrotheum": 967,
    "FluidAerotheum": 969,
    "FluidPetrotheum": 970,
    "FluidMana": 971,
    "FluidSteam": 972,
    "FluidCoal": 973,
}

# Test TE NBT templates
TE_TEMPLATES = {
    "furnace": {
        "id": "thermalexpansion.Furnace",
        "Facing": 3,
        "Type": 0,
        "Energy": 15000,
        "Process": 0,
        "ProcessMax": 200,
        "Items": [],
        "RedstoneControl": 0,
    },
    "pulverizer": {
        "id": "thermalexpansion.Pulverizer",
        "Facing": 3,
        "Type": 1,
        "Energy": 20000,
        "Process": 0,
        "ProcessMax": 200,
        "Items": [{"Slot": 0, "id": "minecraft:iron_ore", "Count": 16, "Damage": 0}],
        "RedstoneControl": 0,
    },
    "smelter": {
        "id": "thermalexpansion.Smelter",
        "Facing": 3,
        "Type": 0,
        "Energy": 20000,
        "Process": 0,
        "ProcessMax": 200,
        "Items": [{"Slot": 0, "id": "minecraft:iron_ore", "Count": 8, "Damage": 0}, {"Slot": 1, "id": "minecraft:sand", "Count": 8, "Damage": 0}],
        "RedstoneControl": 0,
    },
    "crucible": {
        "id": "thermalexpansion.Crucible",
        "Facing": 3,
        "Type": 0,
        "Energy": 20000,
        "Process": 0,
        "ProcessMax": 200,
        "Tank": {"FluidName": "lava", "Amount": 0},
        "RedstoneControl": 0,
    },
    "insolator": {
        "id": "thermalexpansion.Insolator",
        "Facing": 3,
        "Type": 0,
        "Energy": 15000,
        "Process": 0,
        "ProcessMax": 200,
        "Items": [{"Slot": 0, "id": "minecraft:wheat_seeds", "Count": 4, "Damage": 0}],
        "RedstoneControl": 0,
    },
    "cell": {
        "id": "thermalexpansion.Cell",
        "Facing": 3,
        "Type": 2,  # reinforced
        "Energy": {"Storage": 9000000, "Capacity": 18000000},
        "Send": 8000,
    },
    "tank": {
        "id": "thermalexpansion.Tank",
        "Facing": 3,
        "Type": 1,  # hardened
        "Mode": 0,
        "Tank": {"FluidName": "water", "Amount": 2000},
    },
    "dynamo": {
        "id": "thermalexpansion.DynamoMagmatic",
        "Facing": 3,
        "Type": 0,
        "Energy": 20000,
        "Fuel": 500,
        "FuelMax": 1000,
        "FuelFluid": {"FluidName": "lava", "Amount": 500},
    },
    "tesseract": {
        "id": "thermalexpansion.Tesseract",
        "Facing": 3,
        "Frequency": 42,
        "ModeItem": 1,
        "ModeFluid": 1,
        "ModeEnergy": 1,
        "Access": 0,
    },
    "duct_energy": {
        "id": "thermaldynamics.FluxDuct",
        "Con": 0b00111100,
    },
    "duct_item": {
        "id": "thermaldynamics.ItemDuct",
        "Con": 0b00111100,
    },
    "duct_fluid": {
        "id": "thermaldynamics.FluidDuct",
        "Con": 0b00111100,
    },
}


def create_thermal_test_world(world_path: str):
    """Tworzy testowy swiat z blokami Thermal."""
    backend = AnvilBackend(world_path, backup=False)

    base_x, base_y, base_z = 0, 64, 0

    # Rzed 1: Maszyny (Machine block z metadata)
    machines = [
        ("furnace", 0),
        ("pulverizer", 1),
        ("smelter", 3),
        ("crucible", 4),
        ("insolator", 11),
    ]
    for i, (te_key, meta) in enumerate(machines):
        pos = Pos(base_x + i, base_y, base_z)
        backend.set_block(pos, THERMAL_BLOCKS["Machine"], meta)
        te = dict(TE_TEMPLATES[te_key])
        te["x"] = pos.x
        te["y"] = pos.y
        te["z"] = pos.z
        backend.set_tile_entity(pos, te)

    # Rzed 2: Storage
    storage_blocks = [
        ("Cell", 0, "cell"),
        ("Tank", 0, "tank"),
        ("Strongbox", 0, None),
        ("Cache", 0, None),
        ("Workbench", 0, None),
    ]
    for i, (block, meta, te_key) in enumerate(storage_blocks):
        pos = Pos(base_x + i, base_y, base_z + 2)
        backend.set_block(pos, THERMAL_BLOCKS[block], meta)
        if te_key:
            te = dict(TE_TEMPLATES[te_key])
            te["x"] = pos.x
            te["y"] = pos.y
            te["z"] = pos.z
            backend.set_tile_entity(pos, te)

    # Rzed 3: Dynama
    dynamo_types = [
        ("Dynamo", 0, "dynamo"),
        ("Dynamo", 1, "dynamo"),
        ("Dynamo", 2, "dynamo"),
    ]
    for i, (block, meta, te_key) in enumerate(dynamo_types):
        pos = Pos(base_x + i, base_y, base_z + 4)
        backend.set_block(pos, THERMAL_BLOCKS[block], meta)
        te = dict(TE_TEMPLATES[te_key])
        te["id"] = ["thermalexpansion.DynamoSteam", "thermalexpansion.DynamoMagmatic", "thermalexpansion.DynamoCompression"][i]
        te["x"] = pos.x
        te["y"] = pos.y
        te["z"] = pos.z
        backend.set_tile_entity(pos, te)

    # Rzed 4: Special
    specials = [
        ("Tesseract", 0, "tesseract"),
        ("Plate", 1, None),
        ("Light", 0, None),
        ("Frame", 0, None),
        ("Glass", 0, None),
    ]
    for i, (block, meta, te_key) in enumerate(specials):
        pos = Pos(base_x + i, base_y, base_z + 6)
        backend.set_block(pos, THERMAL_BLOCKS[block], meta)
        if te_key:
            te = dict(TE_TEMPLATES[te_key])
            te["x"] = pos.x
            te["y"] = pos.y
            te["z"] = pos.z
            backend.set_tile_entity(pos, te)

    # Rzed 5: Ducty (Thermal Dynamics)
    duct_configs = [
        (3304, 0, "duct_energy"),   # FluxDuct
        (3304, 1, "duct_energy"),   # FluxDuctSuperConductor
        (3305, 0, "duct_fluid"),    # FluidDuct
        (3306, 0, "duct_item"),     # ItemDuct
        (3307, 0, None),            # StructuralDuct
    ]
    for i, (block_id, meta, te_key) in enumerate(duct_configs):
        pos = Pos(base_x + i, base_y, base_z + 8)
        backend.set_block(pos, block_id, meta)
        if te_key:
            te = dict(TE_TEMPLATES[te_key])
            te["x"] = pos.x
            te["y"] = pos.y
            te["z"] = pos.z
            backend.set_tile_entity(pos, te)

    # Rzed 6: Thermal Foundation fluids
    for i, (name, fluid_id) in enumerate(list(THERMAL_FLUIDS.items())[:5]):
        pos = Pos(base_x + i, base_y, base_z + 10)
        backend.set_block(pos, fluid_id, 0)

    backend.commit()
    backend.close()
    print(f"Testowy swiat utworzony: {world_path}")
    print(f"Bloki: {len(machines) + len(storage_blocks) + len(dynamo_types) + len(specials) + len(duct_configs) + 5}")


if __name__ == "__main__":
    import os
    world_dir = "lightweigh_map_templates/1710_modded/thermal_test"
    os.makedirs(world_dir, exist_ok=True)
    os.makedirs(os.path.join(world_dir, "region"), exist_ok=True)
    create_thermal_test_world(world_dir)
