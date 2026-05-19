"""
Tworzenie testowej mapy 1.7.10 z blokami Thermal Series (v2).

Bezposrednia konstrukcja chunk NBT z obsluga Add array (dla block ID > 255).
Uzywa MCRegionWriter do zapisu.
"""
import sys
from pathlib import Path
import io

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from schematic_to_world import MCRegionWriter
import nbtlib
from nbtlib import Compound, Byte, Short, Int, Long, ByteArray, IntArray, List, String

# ID blokow Thermal z modpacka 1710
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

THERMAL_FLUIDS = {
    "FluidRedstone": 964,
    "FluidGlowstone": 965,
    "FluidCryotheum": 968,
    "FluidEnder": 1293,
    "FluidSteam": 972,
}

TE_TEMPLATES = {
    "furnace": {"id": "thermalexpansion.Furnace", "Facing": 3, "Type": 0, "Energy": 15000, "Process": 0, "ProcessMax": 200, "Items": [], "RedstoneControl": 0},
    "pulverizer": {"id": "thermalexpansion.Pulverizer", "Facing": 3, "Type": 1, "Energy": 20000, "Process": 0, "ProcessMax": 200, "Items": [{"Slot": 0, "id": "minecraft:iron_ore", "Count": 16, "Damage": 0}], "RedstoneControl": 0},
    "cell": {"id": "thermalexpansion.Cell", "Facing": 3, "Type": 2, "Energy": {"Storage": 9000000, "Capacity": 18000000}, "Send": 8000},
    "tank": {"id": "thermalexpansion.Tank", "Facing": 3, "Type": 1, "Mode": 0, "Tank": {"FluidName": "water", "Amount": 2000}},
    "dynamo": {"id": "thermalexpansion.DynamoMagmatic", "Facing": 3, "Type": 0, "Energy": 20000, "Fuel": 500, "FuelMax": 1000, "FuelFluid": {"FluidName": "lava", "Amount": 500}},
    "tesseract": {"id": "thermalexpansion.Tesseract", "Facing": 3, "Frequency": 42, "ModeItem": 1, "ModeFluid": 1, "ModeEnergy": 1, "Access": 0},
    "duct_energy": {"id": "thermaldynamics.FluxDuct", "Con": 0b00111100},
    "duct_item": {"id": "thermaldynamics.ItemDuct", "Con": 0b00111100},
}


def create_section(y_index: int, blocks_data: list) -> Compound:
    """Tworzy sekcje chunka z obsluga Add array."""
    blocks = bytearray(4096)
    data = bytearray(2048)
    add = bytearray(2048)
    block_light = bytearray(2048)
    sky_light = bytearray([0xFF] * 2048)

    for lx, ly, lz, bid, meta in blocks_data:
        idx = ly * 256 + lz * 16 + lx
        blocks[idx] = bid & 0xFF
        di = idx // 2
        if idx % 2 == 0:
            data[di] = (data[di] & 0xF0) | (meta & 0x0F)
        else:
            data[di] = (data[di] & 0x0F) | ((meta & 0x0F) << 4)
        high = (bid >> 8) & 0x0F
        if high:
            if idx % 2 == 0:
                add[di] = (add[di] & 0xF0) | high
            else:
                add[di] = (add[di] & 0x0F) | (high << 4)

    return Compound({
        "Y": Byte(y_index),
        "Blocks": ByteArray(blocks),
        "Data": ByteArray(data),
        "Add": ByteArray(add),
        "BlockLight": ByteArray(block_light),
        "SkyLight": ByteArray(sky_light),
    })


def dict_to_compound(d: dict) -> Compound:
    """Rekurencyjnie konwertuje dict Pythona na nbtlib Compound."""
    result = {}
    for k, v in d.items():
        if isinstance(v, dict):
            result[k] = dict_to_compound(v)
        elif isinstance(v, list):
            if v and isinstance(v[0], dict):
                result[k] = List[Compound]([dict_to_compound(item) for item in v])
            else:
                result[k] = List[Int]([Int(x) for x in v])
        elif isinstance(v, str):
            result[k] = String(v)
        elif isinstance(v, bool):
            result[k] = Byte(1 if v else 0)
        elif isinstance(v, int):
            if -128 <= v <= 127:
                result[k] = Byte(v)
            elif -32768 <= v <= 32767:
                result[k] = Short(v)
            else:
                result[k] = Int(v)
        else:
            result[k] = String(str(v))
    return Compound(result)


def build_chunk_nbt(chunk_x: int, chunk_z: int, sections: list, tile_entities: list) -> bytes:
    """Buduje NBT chunka i zwraca skompresowane bajty."""
    level = Compound({
        "xPos": Int(chunk_x),
        "zPos": Int(chunk_z),
        "LastUpdate": Long(0),
        "TerrainPopulated": Byte(1),
        "Biomes": ByteArray([1] * 256),
        "HeightMap": IntArray([64] * 256),
        "Sections": List[Compound](sections),
        "TileEntities": List[Compound]([dict_to_compound(te) for te in tile_entities]),
        "Entities": List[Compound]([]),
    })
    root = Compound({
        "Level": level,
    })
    f = nbtlib.File(root)
    buf = io.BytesIO()
    f.write(buf, byteorder='big')
    return buf.getvalue()


def create_thermal_test_world(world_path: str):
    world_path = Path(world_path)
    region_path = world_path / "region" / "r.0.0.mca"
    region_path.parent.mkdir(parents=True, exist_ok=True)

    writer = MCRegionWriter(region_path)
    tile_entities = []
    section_blocks = []

    base_x, base_y, base_z = 0, 64, 0
    sec_y = base_y // 16

    def add_block(world_x, world_y, world_z, block_id, meta, te_key=None):
        lx = world_x & 15
        ly = world_y & 15
        lz = world_z & 15
        section_blocks.append((lx, ly, lz, block_id, meta))
        if te_key:
            te = dict(TE_TEMPLATES[te_key])
            te["x"] = world_x
            te["y"] = world_y
            te["z"] = world_z
            tile_entities.append(te)

    # Rzed 1: Maszyny
    add_block(base_x + 0, base_y, base_z, THERMAL_BLOCKS["Machine"], 0, "furnace")
    add_block(base_x + 1, base_y, base_z, THERMAL_BLOCKS["Machine"], 1, "pulverizer")
    add_block(base_x + 2, base_y, base_z, THERMAL_BLOCKS["Machine"], 3, None)
    add_block(base_x + 3, base_y, base_z, THERMAL_BLOCKS["Machine"], 4, None)
    add_block(base_x + 4, base_y, base_z, THERMAL_BLOCKS["Machine"], 11, None)

    # Rzed 2: Storage
    add_block(base_x + 0, base_y, base_z + 2, THERMAL_BLOCKS["Cell"], 0, "cell")
    add_block(base_x + 1, base_y, base_z + 2, THERMAL_BLOCKS["Tank"], 0, "tank")
    add_block(base_x + 2, base_y, base_z + 2, THERMAL_BLOCKS["Strongbox"], 0, None)
    add_block(base_x + 3, base_y, base_z + 2, THERMAL_BLOCKS["Cache"], 0, None)
    add_block(base_x + 4, base_y, base_z + 2, THERMAL_BLOCKS["Workbench"], 0, None)

    # Rzed 3: Dynama
    add_block(base_x + 0, base_y, base_z + 4, THERMAL_BLOCKS["Dynamo"], 0, "dynamo")
    add_block(base_x + 1, base_y, base_z + 4, THERMAL_BLOCKS["Dynamo"], 1, None)
    add_block(base_x + 2, base_y, base_z + 4, THERMAL_BLOCKS["Dynamo"], 2, None)

    # Rzed 4: Special
    add_block(base_x + 0, base_y, base_z + 6, THERMAL_BLOCKS["Tesseract"], 0, "tesseract")
    add_block(base_x + 1, base_y, base_z + 6, THERMAL_BLOCKS["Plate"], 1, None)
    add_block(base_x + 2, base_y, base_z + 6, THERMAL_BLOCKS["Light"], 0, None)
    add_block(base_x + 3, base_y, base_z + 6, THERMAL_BLOCKS["Frame"], 0, None)
    add_block(base_x + 4, base_y, base_z + 6, THERMAL_BLOCKS["Glass"], 0, None)

    # Rzed 5: Ducty
    add_block(base_x + 0, base_y, base_z + 8, 3304, 0, "duct_energy")
    add_block(base_x + 1, base_y, base_z + 8, 3304, 1, None)
    add_block(base_x + 2, base_y, base_z + 8, 3305, 0, None)
    add_block(base_x + 3, base_y, base_z + 8, 3306, 0, "duct_item")
    add_block(base_x + 4, base_y, base_z + 8, 3307, 0, None)

    # Rzed 6: Fluids
    for i, (name, fid) in enumerate(list(THERMAL_FLUIDS.items())[:5]):
        add_block(base_x + i, base_y, base_z + 10, fid, 0, None)

    section = create_section(sec_y, section_blocks)
    chunk_data = build_chunk_nbt(0, 0, [section], tile_entities)
    writer.set_chunk(0, 0, chunk_data)
    writer.save()

    print(f"Testowy swiat utworzony: {world_path}")
    print(f"Bloki: {len(section_blocks)}, TE: {len(tile_entities)}")


if __name__ == "__main__":
    import os
    world_dir = "lightweigh_map_templates/1710_modded/thermal_test_v2"
    os.makedirs(world_dir, exist_ok=True)
    create_thermal_test_world(world_dir)
