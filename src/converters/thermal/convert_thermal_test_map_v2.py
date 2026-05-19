"""
Konwersja testowej mapy 1.7.10 z blokami Thermal -> raport 1.18.2 (v2).
Uzywa indeksowania zamiast iteracji po sekcjach.
"""
import sys
from pathlib import Path
import json
import struct
import zlib
import io

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import nbtlib
from converters.thermal.thermal_converter import ThermalConverter


def read_region_chunk(region_path: Path, local_x: int, local_z: int):
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


def _resolve_block_string_id(block_id: int) -> str | None:
    mapping = {
        3438: "ThermalExpansion:Machine",
        3439: "ThermalExpansion:Device",
        3440: "ThermalExpansion:Dynamo",
        3441: "ThermalExpansion:Cell",
        3442: "ThermalExpansion:Tank",
        3443: "ThermalExpansion:Strongbox",
        3444: "ThermalExpansion:Cache",
        3445: "ThermalExpansion:Workbench",
        3446: "ThermalExpansion:Tesseract",
        3447: "ThermalExpansion:Plate",
        3448: "ThermalExpansion:Light",
        3449: "ThermalExpansion:Frame",
        3450: "ThermalExpansion:Glass",
        3451: "ThermalExpansion:Rockwool",
        3452: "ThermalExpansion:Sponge",
        3304: "ThermalDynamics:FluxDuct",
        3305: "ThermalDynamics:FluidDuct",
        3306: "ThermalDynamics:ItemDuct",
        3307: "ThermalDynamics:StructuralDuct",
        3308: "ThermalDynamics:TransportDuct",
        964: "ThermalFoundation:FluidRedstone",
        965: "ThermalFoundation:FluidGlowstone",
        968: "ThermalFoundation:FluidCryotheum",
        1293: "ThermalFoundation:FluidEnder",
        972: "ThermalFoundation:FluidSteam",
    }
    return mapping.get(block_id)


def scan_and_convert_v2(world_path: str):
    world_path = Path(world_path)
    region_file = world_path / "region" / "r.0.0.mca"
    if not region_file.exists():
        return None

    converter = ThermalConverter()
    results = []
    stats = {"total_blocks_found": 0, "converted": 0, "failed": 0, "warnings": 0}

    for local_x in range(32):
        for local_z in range(32):
            chunk = read_region_chunk(region_file, local_x, local_z)
            if chunk is None:
                continue

            level = chunk.get('Level')
            if level is None:
                print(f"DEBUG: ({local_x},{local_z}) no level")
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

            n_sections = len(sections)
            for i in range(n_sections):
                section = sections[i]
                block_arr = section.get('Blocks')
                data_arr = section.get('Data', [])
                add_arr = section.get('Add', [])
                y_base = int(section.get('Y', 0)) * 16

                if block_arr is None:
                    continue
                arr_len = len(block_arr)
                if arr_len == 0:
                    continue

                found_nonzero = 0
                found_nonzero = 0
                resolved_count = 0
                for idx in range(arr_len):
                    low = int(block_arr[idx]) & 0xFF
                    high = 0
                    if add_arr is not None:
                        di = idx // 2
                        if di < len(add_arr):
                            add_val = int(add_arr[di]) & 0xFF
                            if idx % 2 == 0:
                                high = add_val & 0x0F
                            else:
                                high = (add_val >> 4) & 0x0F
                    block_id = low | (high << 8)

                    if block_id == 0:
                        continue
                    found_nonzero += 1

                    block_str_id = _resolve_block_string_id(block_id)
                    if block_str_id is None:
                        continue
                    resolved_count += 1

                    di = idx // 2
                    meta = 0
                    if di < len(data_arr):
                        data_val = int(data_arr[di])
                        if idx % 2 == 0:
                            meta = data_val & 0x0F
                        else:
                            meta = (data_val >> 4) & 0x0F

                    sy = idx // 256
                    sz = (idx % 256) // 16
                    sx = idx % 16
                    x = local_x * 16 + sx
                    y = y_base + sy
                    z = local_z * 16 + sz

                    te = te_map.get((x, y, z))
                    stats["total_blocks_found"] += 1

                    try:
                        te_dict = None
                        if te:
                            te_dict = {}
                            for k, v in te.items():
                                if hasattr(v, 'value'):
                                    v = v.value
                                te_dict[k] = v

                        result = converter.convert_block(block_str_id, meta, te_dict, (x, y, z))

                        entry = {
                            "pos": [x, y, z],
                            "source": f"{block_str_id}:{meta}",
                            "source_block_id": block_id,
                            "target": result.get("target_block_id"),
                            "target_blockstate": result.get("target_blockstate"),
                            "target_nbt_id": result.get("target_nbt", {}).get("id") if result.get("target_nbt") else None,
                            "warnings": result.get("warnings", []),
                            "info": result.get("info", ""),
                        }
                        results.append(entry)
                        stats["converted"] += 1
                        stats["warnings"] += len(entry["warnings"])
                    except Exception as e:
                        stats["failed"] += 1
                        results.append({
                            "pos": [x, y, z],
                            "source": f"{block_str_id}:{meta}",
                            "error": str(e),
                        })

    return {
        "metadata": {"source_world": str(world_path), "converter": "ThermalConverter", "date": "2026-05-19"},
        "stats": stats,
        "results": results,
    }


if __name__ == "__main__":
    world_dir = "lightweigh_map_templates/1710_modded/thermal_test_v2"
    report = scan_and_convert_v2(world_dir)
    out_path = "src/converters/thermal/thermal_test_conversion_report.json"
    with open(out_path, 'w') as f:
        json.dump(report, f, indent=2, default=str)
    print(f"Konwersja zakonczona!")
    print(f"  Znaleziono blokow: {report['stats']['total_blocks_found']}")
    print(f"  Przekonwertowano: {report['stats']['converted']}")
    print(f"  Bledy: {report['stats']['failed']}")
    print(f"  Ostrzezenia: {report['stats']['warnings']}")
    print(f"\n=== Podsumowanie konwersji ===")
    targets = {}
    for r in report['results']:
        t = r.get('target', 'UNKNOWN')
        targets[t] = targets.get(t, 0) + 1
    for t, c in sorted(targets.items(), key=lambda x: -x[1]):
        print(f"  {t}: {c}")
