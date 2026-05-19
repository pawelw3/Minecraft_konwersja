import sys
sys.path.insert(0, 'src')

from pathlib import Path
import json
import struct
import zlib
from minecraft_map_parser.nbt_parser import parse_nbt, NBTTag

# Block IDs from level.dat for Thermal blocks
THERMAL_BLOCK_IDS = {
    962, 963, 964, 965, 968, 971, 972, 973,
    1293, 1414, 1942, 2015,
    3304, 3305, 3306, 3307, 3308,
    3438, 3439, 3440, 3441, 3442, 3443, 3444,
    3445, 3446, 3447, 3448, 3449, 3450, 3451, 3452,
    3453, 3454, 3455, 3456,
}

REGIONS_TO_SCAN = [
    "r.0.-1.mca", "r.1.-2.mca",
    "r.0.5.mca", "r.0.6.mca", "r.1.5.mca", "r.1.6.mca",
    "r.0.0.mca", "r.0.1.mca", "r.1.0.mca", "r.1.1.mca",
    "r.-6.-6.mca", "r.-6.-5.mca", "r.-5.-6.mca", "r.-5.-5.mca",
    "r.-1.-1.mca", "r.10.10.mca", "r.-10.-10.mca",
]


def scan_region_blocks(region_path: Path):
    found_ids = {}
    chunk_count = 0

    if not region_path.exists():
        return found_ids, chunk_count, "missing"

    try:
        with open(region_path, 'rb') as f:
            data = f.read()
    except Exception as e:
        return found_ids, chunk_count, f"read_error: {e}"

    for cz in range(32):
        for cx in range(32):
            index = cx + cz * 32
            offset = index * 4
            sector_offset = ((data[offset] << 16) | (data[offset+1] << 8) | data[offset+2])
            sector_count = data[offset + 3]

            if sector_offset == 0 and sector_count == 0:
                continue

            byte_offset = sector_offset * 4096
            if byte_offset + 5 > len(data):
                continue

            length_data = data[byte_offset:byte_offset + 4]
            length = struct.unpack('>I', length_data)[0]
            compression_type = data[byte_offset + 4]

            if byte_offset + 5 + length - 1 > len(data):
                continue

            compressed = data[byte_offset + 5:byte_offset + 5 + length - 1]

            try:
                if compression_type == 2:
                    chunk_data = zlib.decompress(compressed)
                elif compression_type == 1:
                    import gzip
                    chunk_data = gzip.decompress(compressed)
                else:
                    chunk_data = compressed
            except Exception:
                continue

            chunk_count += 1
            try:
                nbt = parse_nbt(chunk_data)
            except Exception:
                continue

            level = nbt.get('Level', {})
            if isinstance(level, NBTTag):
                sections = level.get('Sections', [])
            else:
                sections = level.get('Sections', [])

            if sections is None:
                continue
            if isinstance(sections, NBTTag):
                sections = sections.value
            if not isinstance(sections, (list, tuple)):
                continue

            for sec in sections:
                if isinstance(sec, NBTTag):
                    sec = sec.value
                if not isinstance(sec, dict):
                    continue
                blocks = sec.get('Blocks', None)
                add_arr = sec.get('Add') or sec.get('AddBlocks')
                if blocks is None:
                    continue
                if isinstance(blocks, NBTTag):
                    blocks = blocks.value
                if isinstance(add_arr, NBTTag):
                    add_arr = add_arr.value
                if not isinstance(blocks, (bytes, bytearray, list)):
                    continue

                for i in range(len(blocks)):
                    low = blocks[i] & 0xFF
                    high = 0
                    if add_arr and i // 2 < len(add_arr):
                        if i % 2 == 0:
                            high = add_arr[i // 2] & 0x0F
                        else:
                            high = (add_arr[i // 2] >> 4) & 0x0F
                    full_id = (high << 8) | low
                    if full_id in THERMAL_BLOCK_IDS:
                        found_ids[full_id] = found_ids.get(full_id, 0) + 1

    return found_ids, chunk_count, "ok"


def main():
    region_path = Path("mapa_1710/region")
    all_ids = {}
    stats = []

    for region_name in REGIONS_TO_SCAN:
        rp = region_path / region_name
        print(f"Scanning blocks {region_name}...", flush=True)
        ids, chunk_count, status = scan_region_blocks(rp)
        stats.append({
            "region": region_name,
            "chunks": chunk_count,
            "status": status,
            "block_types": len(ids),
            "block_total": sum(ids.values()),
        })
        for bid, count in ids.items():
            all_ids[bid] = all_ids.get(bid, 0) + count
        print(f"  -> {chunk_count} chunks, {len(ids)} block types, {sum(ids.values())} total blocks")

    print("\n=== Thermal Block IDs found on map ===")
    for bid in sorted(all_ids.keys()):
        print(f"  ID {bid}: {all_ids[bid]} blocks")

    # Save
    output = {
        "block_ids": all_ids,
        "region_stats": stats,
    }
    out_path = Path("output/thermal_block_discovery.json")
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, 'w') as f:
        json.dump(output, f, indent=2)
    print(f"\nSaved to {out_path}")


if __name__ == "__main__":
    main()
