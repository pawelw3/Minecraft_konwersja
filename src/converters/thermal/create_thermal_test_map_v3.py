"""
Tworzenie rozszerzonej testowej mapy 1.7.10 z blokami Thermal Series (v3).

Zawiera:
- Wszystkie maszyny, dynamy, urzadzenia
- Storage z roznymi tierami i zawartoscia
- Wszystkie typy ductow
- Bloki specjalne (Tesseract, Sponge, itp.)
- Rudy i bloki z Thermal Foundation
- TE z roznymi stanami (facing, redstone, inventory)
- Prosty setup redstone do testow
"""
import sys
from pathlib import Path
import io

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from schematic_to_world import MCRegionWriter
import nbtlib
from nbtlib import Compound, Byte, Short, Int, Long, ByteArray, IntArray, List, String

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

THERMAL_FLUIDS = {
    "FluidRedstone": 964,
    "FluidGlowstone": 965,
    "FluidCryotheum": 968,
    "FluidEnder": 1293,
    "FluidSteam": 972,
    "FluidMana": 971,
    "FluidCoal": 973,
    "FluidPyrotheum": 1942,
    "FluidAerotheum": 2015,
    "FluidPetrotheum": 1414,
}

THERMAL_DYNAMICS = {
    "ThermalDynamics_0": 3304,
    "ThermalDynamics_16": 3305,
    "ThermalDynamics_32": 3306,
    "ThermalDynamics_48": 3307,
    "ThermalDynamics_64": 3308,
}

THERMAL_FOUNDATION = {
    "Ore": 962,
    "Storage": 963,
}


def create_section(y_index: int, blocks_data: list) -> Compound:
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
    root = Compound({"Level": level})
    f = nbtlib.File(root)
    buf = io.BytesIO()
    f.write(buf, byteorder='big')
    return buf.getvalue()


def create_thermal_test_world(world_path: str):
    world_path = Path(world_path)
    region_path = world_path / "region" / "r.0.0.mca"
    region_path.parent.mkdir(parents=True, exist_ok=True)

    writer = MCRegionWriter(region_path)

    # === CHUNK (0,0): Machines, Devices, Dynamos ===
    te_list_00 = []
    blocks_00 = []
    base_y = 64
    sec_y = base_y // 16

    def add_block(bx, by, bz, bid, meta, te_data=None):
        lx = bx & 15
        ly = by & 15
        lz = bz & 15
        blocks_00.append((lx, ly, lz, bid, meta))
        if te_data:
            te = dict(te_data)
            te["x"] = bx
            te["y"] = by
            te["z"] = bz
            te_list_00.append(te)

    # Row 0: Machines (meta 0-11)
    machines = [
        (0, "thermalexpansion.Furnace", {"Facing": 3, "Type": 0, "Energy": 15000}),
        (1, "thermalexpansion.Pulverizer", {"Facing": 3, "Type": 1, "Energy": 20000, "Items": [{"Slot": 0, "id": "minecraft:iron_ore", "Count": 16, "Damage": 0}]}),
        (2, "thermalexpansion.Sawmill", {"Facing": 3, "Type": 2, "Energy": 10000}),
        (3, "thermalexpansion.Smelter", {"Facing": 3, "Type": 3, "Energy": 25000}),
        (4, "thermalexpansion.Crucible", {"Facing": 3, "Type": 4, "Energy": 18000}),
        (5, "thermalexpansion.Transposer", {"Facing": 3, "Type": 5, "Energy": 12000}),
        (6, "thermalexpansion.Precipitator", {"Facing": 3, "Type": 6, "Energy": 15000}),
        (7, "thermalexpansion.Extruder", {"Facing": 3, "Type": 7, "Energy": 22000}),
        (8, "thermalexpansion.Accumulator", {"Facing": 3, "Type": 8, "Energy": 5000}),
        (9, "thermalexpansion.Assembler", {"Facing": 3, "Type": 9, "Energy": 20000}),
        (10, "thermalexpansion.Charger", {"Facing": 3, "Type": 10, "Energy": 16000}),
        (11, "thermalexpansion.Insolator", {"Facing": 3, "Type": 11, "Energy": 18000}),
    ]
    for meta, te_id, extra in machines:
        te = {"id": te_id, **extra, "Process": 0, "ProcessMax": 200, "RedstoneControl": 0}
        add_block(meta, base_y, 0, THERMAL_BLOCKS["Machine"], meta, te)

    # Row 1: Devices (meta 0-7)
    devices = [
        (0, "thermalexpansion.Workbench", {"Facing": 3, "Type": 0}),
        (1, "thermalexpansion.Pump", {"Facing": 3, "Type": 1}),
        (2, "thermalexpansion.Activator", {"Facing": 3, "Type": 2}),
        (3, "thermalexpansion.Breaker", {"Facing": 3, "Type": 3}),
        (4, "thermalexpansion.Collector", {"Facing": 3, "Type": 4}),
        (5, "thermalexpansion.Nullifier", {"Facing": 3, "Type": 5}),
        (6, "thermalexpansion.Buffer", {"Facing": 3, "Type": 6}),
        (7, "thermalexpansion.Extender", {"Facing": 3, "Type": 7}),
    ]
    for meta, te_id, extra in devices:
        te = {"id": te_id, **extra}
        add_block(meta, base_y, 2, THERMAL_BLOCKS["Device"], meta, te)

    # Row 2: Dynamos (meta 0-4)
    dynamos = [
        (0, "thermalexpansion.DynamoSteam", {"Facing": 3, "Type": 0, "Energy": 0, "Fuel": 0, "FuelMax": 1000}),
        (1, "thermalexpansion.DynamoMagmatic", {"Facing": 3, "Type": 1, "Energy": 10000, "Fuel": 500, "FuelMax": 1000, "FuelFluid": {"FluidName": "lava", "Amount": 500}}),
        (2, "thermalexpansion.DynamoCompression", {"Facing": 3, "Type": 2, "Energy": 5000, "Fuel": 300, "FuelMax": 1000}),
        (3, "thermalexpansion.DynamoReactant", {"Facing": 3, "Type": 3, "Energy": 8000, "Fuel": 400, "FuelMax": 1000}),
        (4, "thermalexpansion.DynamoEnervation", {"Facing": 3, "Type": 4, "Energy": 12000, "Fuel": 600, "FuelMax": 1000}),
    ]
    for meta, te_id, extra in dynamos:
        te = {"id": te_id, **extra}
        add_block(meta, base_y, 4, THERMAL_BLOCKS["Dynamo"], meta, te)

    # Row 3: Storage with different tiers and inventory
    storage_items = [
        [{"Slot": 0, "id": "minecraft:stone", "Count": 64, "Damage": 0}],
        [{"Slot": 0, "id": "minecraft:iron_ingot", "Count": 32, "Damage": 0}, {"Slot": 1, "id": "minecraft:gold_ingot", "Count": 16, "Damage": 0}],
        [{"Slot": 0, "id": "minecraft:diamond", "Count": 8, "Damage": 0}],
        [{"Slot": 0, "id": "minecraft:redstone", "Count": 64, "Damage": 0}],
        [{"Slot": 0, "id": "minecraft:emerald", "Count": 16, "Damage": 0}],
    ]
    for tier in range(5):
        te = {"id": "thermalexpansion.Cell", "Facing": 3, "Type": tier, "Energy": {"Storage": 1000000 * (tier + 1), "Capacity": 2000000 * (tier + 1)}, "Send": 1000 * (tier + 1), "Items": storage_items[tier]}
        add_block(tier, base_y, 6, THERMAL_BLOCKS["Cell"], tier, te)

    for tier in range(5):
        te = {"id": "thermalexpansion.Tank", "Facing": 3, "Type": tier, "Mode": 0, "Tank": {"FluidName": "water" if tier % 2 == 0 else "lava", "Amount": 1000 * (tier + 1)}}
        add_block(tier + 5, base_y, 6, THERMAL_BLOCKS["Tank"], tier, te)

    # Row 4: Strongbox, Cache, Workbench with items
    te_strongbox = {"id": "thermalexpansion.Strongbox", "Facing": 3, "Type": 2, "Items": [{"Slot": 0, "id": "minecraft:iron_pickaxe", "Count": 1, "Damage": 0, "tag": {"ench": [{"id": 32, "lvl": 3}]}}]}
    add_block(0, base_y, 8, THERMAL_BLOCKS["Strongbox"], 2, te_strongbox)
    te_cache = {"id": "thermalexpansion.Cache", "Facing": 3, "Type": 1, "Items": [{"Slot": 0, "id": "minecraft:cobblestone", "Count": 64, "Damage": 0}]}
    add_block(1, base_y, 8, THERMAL_BLOCKS["Cache"], 1, te_cache)
    te_workbench = {"id": "thermalexpansion.NewWorkbench", "Facing": 3, "Type": 0, "Items": [{"Slot": 0, "id": "minecraft:stick", "Count": 16, "Damage": 0}]}
    add_block(2, base_y, 8, THERMAL_BLOCKS["Workbench"], 0, te_workbench)

    section_00 = create_section(sec_y, blocks_00)
    chunk_00 = build_chunk_nbt(0, 0, [section_00], te_list_00)
    writer.set_chunk(0, 0, chunk_00)

    # === CHUNK (1,0): Ducts, Special, Foundation ===
    te_list_10 = []
    blocks_10 = []

    def add_block_10(bx, by, bz, bid, meta, te_data=None):
        lx = bx & 15
        ly = by & 15
        lz = bz & 15
        blocks_10.append((lx, ly, lz, bid, meta))
        if te_data:
            te = dict(te_data)
            te["x"] = bx
            te["y"] = by
            te["z"] = bz
            te_list_10.append(te)

    # Row 0: Energy ducts (offset 0, meta 0-7)
    energy_ducts = [
        (0, "thermaldynamics.FluxDuct"),
        (1, "thermaldynamics.FluxDuct"),
        (2, "thermaldynamics.FluxDuct"),
        (3, "thermaldynamics.FluxDuct"),
        (4, "thermaldynamics.FluxDuct"),
        (5, "thermaldynamics.FluxDuct"),
        (6, "thermaldynamics.FluxDuctSuperConductor"),
        (7, "thermaldynamics.FluxDuctSuperConductor"),
    ]
    for meta, te_id in energy_ducts:
        te = {"id": te_id, "Con": 0b00111100}
        add_block_10(16 + meta, base_y, 0, THERMAL_DYNAMICS["ThermalDynamics_0"], meta, te)

    # Row 1: Fluid ducts (offset 16, meta 0-7)
    fluid_ducts = [
        (0, "thermaldynamics.FluidDuct"),
        (1, "thermaldynamics.FluidDuct"),
        (2, "thermaldynamics.FluidDuct"),
        (3, "thermaldynamics.FluidDuct"),
        (4, "thermaldynamics.FluidDuct"),
        (5, "thermaldynamics.FluidDuct"),
        (6, "thermaldynamics.FluidDuctSuper"),
        (7, "thermaldynamics.FluidDuctSuper"),
    ]
    for meta, te_id in fluid_ducts:
        te = {"id": te_id, "Con": 0b00111100}
        add_block_10(16 + meta, base_y, 2, THERMAL_DYNAMICS["ThermalDynamics_16"], meta, te)

    # Row 2: Item ducts (offset 32, meta 0-7)
    item_ducts = [
        (0, "thermaldynamics.ItemDuct"),
        (1, "thermaldynamics.ItemDuct"),
        (2, "thermaldynamics.ItemDuct"),
        (3, "thermaldynamics.ItemDuct"),
        (4, "thermaldynamics.ItemDuct"),
        (5, "thermaldynamics.ItemDuct"),
        (6, "thermaldynamics.ItemDuct"),
        (7, "thermaldynamics.ItemDuct"),
    ]
    for meta, te_id in item_ducts:
        te = {"id": te_id, "Con": 0b00111100}
        add_block_10(16 + meta, base_y, 4, THERMAL_DYNAMICS["ThermalDynamics_32"], meta, te)

    # Row 3: Structural & Transport
    add_block_10(16 + 0, base_y, 6, THERMAL_DYNAMICS["ThermalDynamics_48"], 0, {"id": "thermaldynamics.StructuralDuct", "Con": 0})
    add_block_10(16 + 1, base_y, 6, THERMAL_DYNAMICS["ThermalDynamics_48"], 1, None)
    add_block_10(16 + 2, base_y, 6, THERMAL_DYNAMICS["ThermalDynamics_64"], 0, {"id": "thermaldynamics.TransportDuct", "Con": 0})
    add_block_10(16 + 3, base_y, 6, THERMAL_DYNAMICS["ThermalDynamics_64"], 1, {"id": "thermaldynamics.TransportDuct", "Con": 0})
    add_block_10(16 + 4, base_y, 6, THERMAL_DYNAMICS["ThermalDynamics_64"], 2, {"id": "thermaldynamics.TransportDuct", "Con": 0})

    # Row 4: Special blocks
    add_block_10(16 + 0, base_y, 8, THERMAL_BLOCKS["Tesseract"], 0, {"id": "thermalexpansion.Tesseract", "Facing": 3, "Frequency": 42, "ModeItem": 1, "ModeFluid": 1, "ModeEnergy": 1})
    add_block_10(16 + 1, base_y, 8, THERMAL_BLOCKS["Sponge"], 0, {"id": "thermalexpansion.Sponge", "Facing": 3})
    add_block_10(16 + 2, base_y, 8, THERMAL_BLOCKS["Sponge"], 1, {"id": "thermalexpansion.SpongeMagmatic", "Facing": 3})
    add_block_10(16 + 3, base_y, 8, THERMAL_BLOCKS["Light"], 0, None)
    add_block_10(16 + 4, base_y, 8, THERMAL_BLOCKS["Light"], 1, None)
    add_block_10(16 + 5, base_y, 8, THERMAL_BLOCKS["Plate"], 1, None)
    add_block_10(16 + 6, base_y, 8, THERMAL_BLOCKS["Frame"], 0, None)
    add_block_10(16 + 7, base_y, 8, THERMAL_BLOCKS["Glass"], 0, None)

    # Row 5: Rockwool colors
    for color in range(16):
        add_block_10(16 + color, base_y, 10, THERMAL_BLOCKS["Rockwool"], color, None)

    # Row 6: Foundation ores
    for ore_meta in range(7):
        add_block_10(16 + ore_meta, base_y, 12, THERMAL_FOUNDATION["Ore"], ore_meta, None)

    # Row 7: Foundation storage
    for storage_meta in range(13):
        add_block_10(16 + storage_meta, base_y, 14, THERMAL_FOUNDATION["Storage"], storage_meta, None)

    section_10 = create_section(sec_y, blocks_10)
    chunk_10 = build_chunk_nbt(1, 0, [section_10], te_list_10)
    writer.set_chunk(1, 0, chunk_10)

    # === CHUNK (0,1): State variations (facing, redstone, inventory) ===
    te_list_01 = []
    blocks_01 = []

    def add_block_01(bx, by, bz, bid, meta, te_data=None):
        lx = bx & 15
        ly = by & 15
        lz = bz & 15
        blocks_01.append((lx, ly, lz, bid, meta))
        if te_data:
            te = dict(te_data)
            te["x"] = bx
            te["y"] = by
            te["z"] = bz
            te_list_01.append(te)

    # Row 0: Same machine with different facing
    for facing in range(6):
        te = {"id": "thermalexpansion.Furnace", "Facing": facing, "Type": 0, "Energy": 10000, "Process": 0, "ProcessMax": 200, "RedstoneControl": 0}
        add_block_01(facing, base_y, 16 + 0, THERMAL_BLOCKS["Machine"], 0, te)

    # Row 1: Same machine with different redstone control
    for rc in range(3):
        te = {"id": "thermalexpansion.Pulverizer", "Facing": 3, "Type": 1, "Energy": 20000, "Process": 0, "ProcessMax": 200, "RedstoneControl": rc}
        add_block_01(rc, base_y, 16 + 2, THERMAL_BLOCKS["Machine"], 1, te)

    # Row 2: Machine with/without items
    add_block_01(0, base_y, 16 + 4, THERMAL_BLOCKS["Machine"], 0, {"id": "thermalexpansion.Furnace", "Facing": 3, "Type": 0, "Energy": 15000, "Items": [], "RedstoneControl": 0})
    add_block_01(1, base_y, 16 + 4, THERMAL_BLOCKS["Machine"], 0, {"id": "thermalexpansion.Furnace", "Facing": 3, "Type": 0, "Energy": 15000, "Items": [{"Slot": 0, "id": "minecraft:iron_ore", "Count": 8, "Damage": 0}], "RedstoneControl": 0})
    add_block_01(2, base_y, 16 + 4, THERMAL_BLOCKS["Machine"], 0, {"id": "thermalexpansion.Furnace", "Facing": 3, "Type": 0, "Energy": 15000, "Items": [{"Slot": 0, "id": "minecraft:sand", "Count": 32, "Damage": 0}, {"Slot": 1, "id": "minecraft:coal", "Count": 16, "Damage": 0}], "RedstoneControl": 0})

    # Row 3: Cell with different energy levels
    for tier in range(3):
        te = {"id": "thermalexpansion.Cell", "Facing": 3, "Type": tier, "Energy": {"Storage": 500000 * tier, "Capacity": 2000000 * (tier + 1)}, "Send": 1000}
        add_block_01(tier, base_y, 16 + 6, THERMAL_BLOCKS["Cell"], tier, te)

    section_01 = create_section(sec_y, blocks_01)
    chunk_01 = build_chunk_nbt(0, 1, [section_01], te_list_01)
    writer.set_chunk(0, 1, chunk_01)

    # === CHUNK (1,1): Redstone test setup ===
    te_list_11 = []
    blocks_11 = []

    def add_block_11(bx, by, bz, bid, meta, te_data=None):
        lx = bx & 15
        ly = by & 15
        lz = bz & 15
        blocks_11.append((lx, ly, lz, bid, meta))
        if te_data:
            te = dict(te_data)
            te["x"] = bx
            te["y"] = by
            te["z"] = bz
            te_list_11.append(te)

    # Simple redstone test: Lever -> Redstone dust -> Machine (Furnace)
    # When lever ON, machine should receive redstone signal
    # Command block to log test result

    # Lever at (16, 64, 16)
    add_block_11(16, base_y, 16, 69, 5, None)  # lever, facing east
    # Redstone wire
    add_block_11(17, base_y, 16, 55, 0, None)  # redstone wire
    add_block_11(18, base_y, 16, 55, 0, None)
    # Furnace with redstone control = 2 (HIGH = requires signal)
    add_block_11(19, base_y, 16, THERMAL_BLOCKS["Machine"], 0, {"id": "thermalexpansion.Furnace", "Facing": 3, "Type": 0, "Energy": 15000, "RedstoneControl": 2, "Items": [{"Slot": 0, "id": "minecraft:iron_ore", "Count": 8, "Damage": 0}]})
    # Command block to log
    add_block_11(20, base_y, 16, 137, 0, {"id": "Control", "Command": "/say THERMAL_REDSTONE_TEST_1 PASS", "auto": 1})

    # Energy test: Dynamo -> Energy Duct -> Machine
    add_block_11(16, base_y, 18, THERMAL_BLOCKS["Dynamo"], 0, {"id": "thermalexpansion.DynamoSteam", "Facing": 3, "Type": 0, "Energy": 0, "Fuel": 1000, "FuelMax": 1000})
    add_block_11(17, base_y, 18, THERMAL_DYNAMICS["ThermalDynamics_0"], 0, {"id": "thermaldynamics.FluxDuct", "Con": 0b00111100})
    add_block_11(18, base_y, 18, THERMAL_DYNAMICS["ThermalDynamics_0"], 0, {"id": "thermaldynamics.FluxDuct", "Con": 0b00111100})
    add_block_11(19, base_y, 18, THERMAL_BLOCKS["Machine"], 0, {"id": "thermalexpansion.Furnace", "Facing": 3, "Type": 0, "Energy": 0, "RedstoneControl": 0})

    section_11 = create_section(sec_y, blocks_11)
    chunk_11 = build_chunk_nbt(1, 1, [section_11], te_list_11)
    writer.set_chunk(1, 1, chunk_11)

    writer.save()

    total_blocks = len(blocks_00) + len(blocks_10) + len(blocks_01) + len(blocks_11)
    total_te = len(te_list_00) + len(te_list_10) + len(te_list_01) + len(te_list_11)
    print(f"Testowy swiat v3 utworzony: {world_path}")
    print(f"Chunki: (0,0), (1,0), (0,1), (1,1)")
    print(f"Bloki: {total_blocks}, TE: {total_te}")


if __name__ == "__main__":
    import os
    world_dir = "lightweigh_map_templates/1710_modded/thermal_test_v3"
    os.makedirs(world_dir, exist_ok=True)
    create_thermal_test_world(world_dir)
