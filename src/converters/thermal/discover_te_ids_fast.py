import sys
sys.path.insert(0, 'src')

from pathlib import Path
import re
import json
import struct
import zlib
from minecraft_map_parser.anvil_parser import AnvilParser
from minecraft_map_parser.nbt_parser import parse_nbt, NBTTag

THERMAL_PATTERNS = [
    r"thermalexpansion",
    r"thermaldynamics",
    r"thermalfoundation",
    r"ThermalExpansion",
    r"ThermalDynamics",
    r"ThermalFoundation",
]

REGIONS_TO_SCAN = [
    # Strefy
    "r.0.-1.mca",   # billund
    "r.1.-2.mca",   # choroszcz
    "r.0.5.mca", "r.0.6.mca", "r.1.5.mca", "r.1.6.mca",  # iii_rzesza
    "r.0.0.mca", "r.0.1.mca", "r.1.0.mca", "r.1.1.mca",  # rzym
    "r.-6.-6.mca", "r.-6.-5.mca", "r.-5.-6.mca", "r.-5.-5.mca",  # zsrr
    # Dodatkowe
    "r.-1.-1.mca",
    "r.10.10.mca",
    "r.-10.-10.mca",
]


def extract_te_ids_from_chunk_data(chunk_data: bytes):
    """Ekstrahuje TileEntity IDs z surowych danych chunka (szybsze niż pełny parser)."""
    try:
        nbt = parse_nbt(chunk_data)
    except Exception:
        return []

    level = nbt.get('Level', {})
    if isinstance(level, NBTTag):
        tes = level.get('TileEntities', [])
    else:
        tes = level.get('TileEntities', [])

    if tes is None:
        return []
    if isinstance(tes, NBTTag):
        tes = tes.value
    if not isinstance(tes, (list, tuple)):
        return []

    ids = []
    for te in tes:
        if isinstance(te, NBTTag):
            te = te.value
        if isinstance(te, dict):
            te_id = te.get('id', '')
            if isinstance(te_id, NBTTag):
                te_id = te_id.value
            ids.append(str(te_id))
    return ids


def scan_region_fast(region_path: Path):
    found_te_ids = {}
    chunk_count = 0

    if not region_path.exists():
        return found_te_ids, chunk_count, "missing"

    try:
        with open(region_path, 'rb') as f:
            data = f.read()
    except Exception as e:
        return found_te_ids, chunk_count, f"read_error: {e}"

    # Parse locations from header
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
            te_ids = extract_te_ids_from_chunk_data(chunk_data)
            for te_id in te_ids:
                for pattern in THERMAL_PATTERNS:
                    if re.search(pattern, te_id, re.IGNORECASE):
                        found_te_ids[te_id] = found_te_ids.get(te_id, 0) + 1
                        break

    return found_te_ids, chunk_count, "ok"


def main():
    world_path = Path("mapa_1710")
    region_path = world_path / "region"

    all_te_ids = {}
    stats = []

    for region_name in REGIONS_TO_SCAN:
        rp = region_path / region_name
        print(f"Scanning {region_name}...", flush=True)
        te_ids, chunk_count, status = scan_region_fast(rp)
        stats.append({
            "region": region_name,
            "chunks": chunk_count,
            "status": status,
            "te_types": len(te_ids),
            "te_total": sum(te_ids.values()),
        })
        for te_id, count in te_ids.items():
            all_te_ids[te_id] = all_te_ids.get(te_id, 0) + count
        print(f"  -> {chunk_count} chunks, {len(te_ids)} TE types, {sum(te_ids.values())} total TEs")

    print("\n=== Thermal TE IDs found on map ===")
    for te_id in sorted(all_te_ids.keys()):
        print(f"  {te_id}: {all_te_ids[te_id]}")

    # Save results
    output = {
        "te_ids": all_te_ids,
        "region_stats": stats,
    }
    out_path = Path("output/thermal_te_discovery.json")
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, 'w') as f:
        json.dump(output, f, indent=2)
    print(f"\nSaved to {out_path}")


if __name__ == "__main__":
    main()
