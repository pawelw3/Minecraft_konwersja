"""
Krok 4: Analiza pokrycia konwersji Thermal Series (ThermalExpansion + ThermalFoundation)
na mapie 1.7.10.
"""
import json
import os
import sys
import time
from pathlib import Path
from collections import Counter
from concurrent.futures import ThreadPoolExecutor, as_completed

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "src"))


def is_thermal_te(te_id: str) -> bool:
    return te_id.startswith("thermalexpansion.") or te_id.startswith("thermalfoundation.")


def scan_region_file(args):
    region_path_str = args
    region_path = Path(region_path_str)

    result = {
        "has_thermal": False,
        "region_coords": None,
        "chunks_checked": 0,
        "te_count": 0,
        "te_by_id": Counter(),
        "error": None,
    }

    try:
        data = region_path.read_bytes()
        import re
        m = re.search(r'r\.(-?\d+)\.(-?\d+)\.mca', region_path.name)
        if m:
            result["region_coords"] = (int(m.group(1)), int(m.group(2)))

        for cz in range(32):
            for cx in range(32):
                index = cx + cz * 32
                offset = index * 4
                loc_data = data[offset:offset + 4]
                sector_offset = ((loc_data[0] << 16) | (loc_data[1] << 8) | loc_data[2])
                sector_count = loc_data[3]

                if sector_offset == 0 and sector_count == 0:
                    continue

                byte_offset = sector_offset * 4096
                if byte_offset + 5 > len(data):
                    continue

                length_data = data[byte_offset:byte_offset + 4]
                length = struct.unpack('>I', length_data)[0]
                if length < 1 or byte_offset + 5 + length - 1 > len(data):
                    continue

                compression_type = data[byte_offset + 4]
                compressed = data[byte_offset + 5:byte_offset + 5 + length - 1]

                try:
                    if compression_type == 1:
                        import gzip
                        chunk_bytes = gzip.decompress(compressed)
                    elif compression_type == 2:
                        import zlib
                        chunk_bytes = zlib.decompress(compressed)
                    else:
                        chunk_bytes = compressed
                except Exception:
                    continue

                result["chunks_checked"] += 1

                if b"thermalexpansion" not in chunk_bytes and b"thermalfoundation" not in chunk_bytes:
                    continue

                try:
                    from minecraft_map_parser.nbt_parser import parse_nbt, NBTTag
                    nbt = parse_nbt(chunk_bytes)
                except Exception:
                    continue

                level = nbt.get('Level', {})
                if isinstance(level, NBTTag):
                    level = level.value if hasattr(level, 'value') else {}
                if not isinstance(level, dict):
                    continue

                te_list = level.get('TileEntities', [])
                if isinstance(te_list, NBTTag):
                    te_list = te_list.value if hasattr(te_list, 'value') else []

                for te in te_list:
                    if isinstance(te, NBTTag):
                        te = te.value if hasattr(te, 'value') else {}
                    if not isinstance(te, dict):
                        continue

                    te_id_obj = te.get('id')
                    if isinstance(te_id_obj, NBTTag):
                        te_id = str(te_id_obj.value if hasattr(te_id_obj, 'value') else te_id_obj)
                    else:
                        te_id = str(te_id_obj) if te_id_obj else ''

                    if not is_thermal_te(te_id):
                        continue

                    result["has_thermal"] = True
                    result["te_count"] += 1
                    result["te_by_id"][te_id] += 1

    except Exception as e:
        result["error"] = f"{region_path.name}: {type(e).__name__}: {e}"

    return result


def analyze_thermal_coverage(max_workers=None):
    if max_workers is None:
        max_workers = min(32, (os.cpu_count() or 4) * 2)

    project_root = ROOT
    region_path = project_root / "mapa_1710" / "region"

    if not region_path.exists():
        print(f"BŁĄD: Nie znaleziono folderu regionów w {region_path}")
        return

    region_files = sorted(region_path.glob("r.*.*.mca"))
    total_regions = len(region_files)
    print(f"Znaleziono {total_regions} plików regionów.")
    print(f"Używam {max_workers} workerów...")

    start = time.time()

    all_te_by_id = Counter()
    regions_with_thermal = []
    total_chunks = 0
    errors = []

    sys.path.insert(0, str(ROOT / "src"))
    from converters.thermal.mappings import get_mapping_by_te_id

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {executor.submit(scan_region_file, str(rf)): rf for rf in region_files}
        completed = 0
        for future in as_completed(futures):
            completed += 1
            if completed % 100 == 0:
                elapsed = time.time() - start
                print(f"  {completed}/{total_regions} regionów ({elapsed:.1f}s)")
            try:
                res = future.result()
            except Exception as e:
                errors.append(str(e))
                continue

            if res["error"]:
                errors.append(res["error"])

            total_chunks += res["chunks_checked"]

            if res["has_thermal"]:
                regions_with_thermal.append(res["region_coords"])
                for te_id, count in res["te_by_id"].items():
                    all_te_by_id[te_id] += count

    elapsed = time.time() - start
    total_te = sum(all_te_by_id.values())

    # Sprawdź mapowania
    mapped = Counter()
    unmapped = Counter()
    for te_id, count in all_te_by_id.items():
        mapping = get_mapping_by_te_id(te_id)
        if mapping:
            mapped[te_id] = count
        else:
            unmapped[te_id] = count

    report = {
        "total_regions": total_regions,
        "regions_with_thermal": len(regions_with_thermal),
        "regions_with_thermal_list": [str(r) for r in sorted(regions_with_thermal)],
        "total_chunks_checked": total_chunks,
        "total_thermal_te_found": total_te,
        "te_by_id": dict(all_te_by_id),
        "te_mapped": dict(mapped),
        "te_unmapped": dict(unmapped),
        "errors_count": len(errors),
        "errors": errors[:20],
        "scan_time_seconds": round(elapsed, 2),
    }

    output_dir = ROOT / "src" / "converters" / "thermal"
    output_dir.mkdir(parents=True, exist_ok=True)

    json_file = output_dir / "THERMAL_STEP4_COVERAGE.json"
    with open(json_file, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, ensure_ascii=False)

    md_file = output_dir / "THERMAL_STEP4_COVERAGE.md"
    with open(md_file, 'w', encoding='utf-8') as f:
        f.write("# Thermal Series — Krok 4 (Pokrycie na mapie)\n\n")
        f.write("> Pełny skan wszystkich regionów z multiprocessingiem\n\n")
        f.write("## Wyniki\n\n")
        f.write(f"- **Czas skanu:** {elapsed:.1f}s\n")
        f.write(f"- **Regiony:** {total_regions}\n")
        f.write(f"- **Regiony z Thermal:** {len(regions_with_thermal)}\n")
        f.write(f"- **Sprawdzone chunki:** {total_chunks:,}\n")
        f.write(f"- **Znalezione TE Thermal:** {total_te}\n\n")

        f.write("## Pokrycie konwersji\n\n")
        f.write("| Tile Entity ID | Liczba | Mapowanie |\n")
        f.write("|----------------|--------|-----------|\n")
        for te_id, count in all_te_by_id.most_common():
            is_mapped = te_id in mapped
            status = "[OK]" if is_mapped else "[MISSING]"
            f.write(f"| {te_id} | {count} | {status} |\n")

        f.write("\n## Podsumowanie\n\n")
        total_mapped = sum(mapped.values())
        total_unmapped = sum(unmapped.values())
        f.write(f"- **Zmapowane TE:** {total_mapped}/{total_te} ({100*total_mapped//max(total_te,1)}%)\n")
        f.write(f"- **Niezmapowane TE:** {total_unmapped}\n")
        if unmapped:
            f.write("- **Lista niezmapowanych:**\n")
            for te_id, count in unmapped.most_common():
                f.write(f"  - `{te_id}`: {count}\n")

        if errors:
            f.write(f"\n## Błędy ({len(errors)})\n\n")
            for err in errors[:10]:
                f.write(f"- {err}\n")

    print(f"\n{'='*60}")
    print("RAPORT POKRYCIA THERMAL (KROK 4):")
    print(f"{'='*60}")
    print(f"Czas: {elapsed:.1f}s")
    print(f"Regiony: {total_regions}")
    print(f"Regiony z Thermal: {len(regions_with_thermal)}")
    print(f"Chunki: {total_chunks:,}")
    print(f"TE Thermal: {total_te}")
    print(f"Zmapowane: {sum(mapped.values())} | Niezmapowane: {sum(unmapped.values())}")
    for te_id, count in all_te_by_id.most_common():
        status = "[OK]" if te_id in mapped else "[MISSING]"
        print(f"  {status} {te_id}: {count}")
    print(f"\nRaport zapisano do:\n  {json_file}\n  {md_file}")

    return report


if __name__ == "__main__":
    import struct
    print("="*60)
    print("THERMAL SERIES — KROK 4: POKRYCIE NA MAPIE")
    print("="*60)
    analyze_thermal_coverage()
