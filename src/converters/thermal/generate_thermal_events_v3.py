"""Generuje Event JSON dla mapy 1.18.2 z konwersji Thermal."""
import sys
from pathlib import Path
import json
import struct
import zlib
import io

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import nbtlib
from converters.thermal.thermal_converter import ThermalConverter


def read_region_chunk(region_path, local_x, local_z):
    with open(region_path, 'rb') as f:
        data = f.read()
    offset_idx = (local_x + local_z * 32) * 4
    offset = ((data[offset_idx] << 16) | (data[offset_idx + 1] << 8) | data[offset_idx + 2])
    if offset == 0:
        return None
    byte_offset = offset * 4096
    length = struct.unpack('>I', data[byte_offset:byte_offset + 4])[0]
    compression = data[byte_offset + 4]
    compressed = data[byte_offset + 5:byte_offset + 5 + length - 1]
    if compression == 2:
        chunk_data = zlib.decompress(compressed)
    elif compression == 1:
        chunk_data = __import__('gzip').decompress(compressed)
    else:
        chunk_data = compressed
    return nbtlib.File.from_fileobj(io.BytesIO(chunk_data), byteorder='big')


def _resolve_block_string_id(block_id):
    mapping = {
        3438: "ThermalExpansion:Machine", 3439: "ThermalExpansion:Device",
        3440: "ThermalExpansion:Dynamo", 3441: "ThermalExpansion:Cell",
        3442: "ThermalExpansion:Tank", 3443: "ThermalExpansion:Strongbox",
        3444: "ThermalExpansion:Cache", 3445: "ThermalExpansion:Workbench",
        3446: "ThermalExpansion:Tesseract", 3447: "ThermalExpansion:Plate",
        3448: "ThermalExpansion:Light", 3449: "ThermalExpansion:Frame",
        3450: "ThermalExpansion:Glass", 3451: "ThermalExpansion:Rockwool",
        3452: "ThermalExpansion:Sponge",
        3304: "ThermalDynamics:ThermalDynamics_0",
        3305: "ThermalDynamics:ThermalDynamics_16",
        3306: "ThermalDynamics:ThermalDynamics_32",
        3307: "ThermalDynamics:ThermalDynamics_48",
        3308: "ThermalDynamics:ThermalDynamics_64",
        962: "ThermalFoundation:Ore", 963: "ThermalFoundation:Storage",
        964: "ThermalFoundation:FluidRedstone",
        965: "ThermalFoundation:FluidGlowstone",
        968: "ThermalFoundation:FluidCryotheum",
        971: "ThermalFoundation:FluidMana", 972: "ThermalFoundation:FluidSteam",
        973: "ThermalFoundation:FluidCoal", 1293: "ThermalFoundation:FluidEnder",
        1414: "ThermalFoundation:FluidPetrotheum",
        1942: "ThermalFoundation:FluidPyrotheum",
        2015: "ThermalFoundation:FluidAerotheum",
        55: "minecraft:redstone_wire", 69: "minecraft:lever",
        137: "minecraft:command_block",
    }
    return mapping.get(block_id)


def generate_events(world_path):
    world_path = Path(world_path)
    converter = ThermalConverter()
    events = []
    stats = {"total": 0, "converted": 0, "failed": 0}

    region_files = list(world_path.glob("region/*.mca"))
    for region_file in region_files:
        for local_x in range(32):
            for local_z in range(32):
                chunk = read_region_chunk(region_file, local_x, local_z)
                if chunk is None:
                    continue
                level = chunk.get('Level')
                if level is None:
                    continue
                sections = level.get('Sections')
                if not sections:
                    continue

                te_list = level.get('TileEntities', [])
                te_map = {}
                for te in te_list:
                    te_x = int(te.get('x', 0))
                    te_y = int(te.get('y', 0))
                    te_z = int(te.get('z', 0))
                    te_map[(te_x, te_y, te_z)] = te

                chunk_x = int(level.get('xPos', 0))
                chunk_z = int(level.get('zPos', 0))

                for sec in sections:
                    y_base = int(sec.get('Y', 0)) * 16
                    block_arr = sec.get('Blocks')
                    add_arr = sec.get('Add')
                    data_arr = sec.get('Data')
                    if block_arr is None:
                        continue

                    for idx in range(len(block_arr)):
                        bid = block_arr[idx] & 0xFF
                        if add_arr is not None and idx // 2 < len(add_arr):
                            if idx % 2 == 0:
                                bid |= (add_arr[idx // 2] & 0x0F) << 8
                            else:
                                bid |= ((add_arr[idx // 2] >> 4) & 0x0F) << 8
                        if bid == 0:
                            continue

                        meta = 0
                        if data_arr is not None and idx // 2 < len(data_arr):
                            if idx % 2 == 0:
                                meta = data_arr[idx // 2] & 0x0F
                            else:
                                meta = (data_arr[idx // 2] >> 4) & 0x0F

                        lx = idx & 15
                        lz = (idx >> 4) & 15
                        ly = (idx >> 8) & 15
                        wx = chunk_x * 16 + lx
                        wy = y_base + ly
                        wz = chunk_z * 16 + lz

                        block_str = _resolve_block_string_id(bid)
                        if block_str is None:
                            continue

                        stats["total"] += 1
                        te = te_map.get((wx, wy, wz))
                        te_dict = dict(te) if te else None

                        try:
                            result = converter.convert_block(block_str, meta, te_dict, position=(wx, wy, wz))
                            target_id = result.get("target_block_id")
                            if not target_id:
                                stats["failed"] += 1
                                continue

                            blockstate = result.get("target_blockstate", {})
                            target_nbt = result.get("target_nbt")

                            event = {
                                "op": "set_block" if not target_nbt else "set_block_entity",
                                "pos": [wx, wy, wz],
                                "block": target_id,
                            }
                            if blockstate:
                                event["blockstate"] = blockstate
                            if target_nbt:
                                # Convert nbtlib types to plain Python types
                                plain_nbt = {}
                                for k, v in target_nbt.items():
                                    if hasattr(v, 'value'):
                                        v = v.value
                                    if isinstance(v, dict):
                                        plain_nbt[k] = {kk: vv.value if hasattr(vv, 'value') else vv for kk, vv in v.items()}
                                    else:
                                        plain_nbt[k] = v
                                event["nbt"] = plain_nbt

                            events.append(event)
                            stats["converted"] += 1
                        except Exception as e:
                            stats["failed"] += 1
                            print(f"ERROR {block_str}:{meta} at ({wx},{wy},{wz}): {e}")

    report = {
        "metadata": {"source": str(world_path), "converter": "ThermalConverter", "date": "2026-05-20"},
        "stats": stats,
        "events": events,
    }
    out_path = Path("output/thermal_v3_events.json")
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, 'w') as f:
        json.dump(report, f, indent=2, default=str)
    print(f"Events: {stats['converted']}/{stats['total']} (failed: {stats['failed']})")
    print(f"Saved: {out_path}")
    return report


if __name__ == "__main__":
    generate_events("lightweigh_map_templates/1710_modded/thermal_test_v3")
