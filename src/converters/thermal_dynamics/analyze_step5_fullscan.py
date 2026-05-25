"""
Krok 5: Pełny skan mapy z multiprocessingiem.
Szuka WSZYSTKICH regionów z Thermal Dynamics TE.
"""

import json
import sys
import time
import zlib
import struct
from pathlib import Path
from collections import Counter
from concurrent.futures import ProcessPoolExecutor, as_completed
import multiprocessing

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "src"))


def scan_region_file(args):
    """Funkcja worker'a — skanuje pojedynczy plik regionu."""
    region_path_str = args
    region_path = Path(region_path_str)

    result = {
        "has_td": False,
        "region_coords": None,
        "chunks_checked": 0,
        "te_count": 0,
        "te_by_id": Counter(),
        "attachments": Counter(),
        "facades": Counter(),
        "error": None,
    }

    try:
        # Lekki parser tylko dla TileEntities
        data = region_path.read_bytes()

        # Wyciągnij współrzędne regionu z nazwy
        import re
        m = re.search(r'r\.(-?\d+)\.(-?\d+)\.mca', region_path.name)
        if m:
            result["region_coords"] = (int(m.group(1)), int(m.group(2)))

        # Parsuj nagłówek z lokalizacjami chunków
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
                        chunk_bytes = zlib.decompress(compressed)
                    else:
                        chunk_bytes = compressed
                except Exception:
                    continue

                result["chunks_checked"] += 1

                # Szybkie szukanie "thermaldynamics" w surowych bajtach chunka
                if b"thermaldynamics" not in chunk_bytes:
                    continue

                # Mamy potencjalne TD TE — parsuj NBT
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

                    if not te_id.startswith('thermaldynamics'):
                        continue

                    result["has_td"] = True
                    result["te_count"] += 1
                    result["te_by_id"][te_id] += 1

                    # Załączniki i fasady
                    for side in range(6):
                        att_key = f"attachment{side}"
                        if att_key in te:
                            att = te[att_key]
                            if isinstance(att, dict) and att:
                                result["attachments"][te_id] += 1

                        facade_key = f"facade{side}"
                        if facade_key in te:
                            facade = te[facade_key]
                            if isinstance(facade, dict) and facade:
                                result["facades"][te_id] += 1

    except Exception as e:
        result["error"] = f"{region_path.name}: {type(e).__name__}: {e}"

    return result


def analyze_td_fullscan(max_workers=None):
    if max_workers is None:
        max_workers = max(1, multiprocessing.cpu_count() - 1)

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
    all_mapped = Counter()
    all_unmapped = Counter()
    all_attachments = Counter()
    all_facades = Counter()
    regions_with_td = []
    total_chunks = 0
    errors = []

    # Import mapowań w głównym procesie
    sys.path.insert(0, str(ROOT / "src"))
    from converters.thermal_dynamics.mappings import get_mapping_for_te_id

    with ProcessPoolExecutor(max_workers=max_workers) as executor:
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

            if res["has_td"]:
                regions_with_td.append(res["region_coords"])
                for te_id, count in res["te_by_id"].items():
                    all_te_by_id[te_id] += count
                    mapping = get_mapping_for_te_id(te_id)
                    if mapping:
                        all_mapped[te_id] += count
                    else:
                        all_unmapped[te_id] += count
                for te_id, count in res["attachments"].items():
                    all_attachments[te_id] += count
                for te_id, count in res["facades"].items():
                    all_facades[te_id] += count

    elapsed = time.time() - start
    total_te = sum(all_te_by_id.values())
    total_mapped = sum(all_mapped.values())
    total_unmapped = sum(all_unmapped.values())

    report = {
        "total_regions": total_regions,
        "regions_with_td": len(regions_with_td),
        "regions_with_td_list": [str(r) for r in sorted(regions_with_td)],
        "total_chunks_checked": total_chunks,
        "total_td_te_found": total_te,
        "td_te_by_id": dict(all_te_by_id),
        "td_te_mapped": dict(all_mapped),
        "td_te_unmapped": dict(all_unmapped),
        "attachments_found": dict(all_attachments),
        "facades_found": dict(all_facades),
        "errors_count": len(errors),
        "errors": errors[:20],
        "scan_time_seconds": round(elapsed, 2),
    }

    output_dir = ROOT / "src" / "converters" / "thermal_dynamics"
    output_dir.mkdir(parents=True, exist_ok=True)

    json_file = output_dir / "THERMAL_DYNAMICS_STEP5_FULLSCAN.json"
    with open(json_file, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, ensure_ascii=False)

    md_file = output_dir / "THERMAL_DYNAMICS_STEP5_FULLSCAN.md"
    with open(md_file, 'w', encoding='utf-8') as f:
        f.write("# Thermal Dynamics — Krok 5 (Pełny skan)\n\n")
        f.write("> Pełny skan wszystkich regionów z multiprocessingiem\n\n")
        f.write("## Wyniki\n\n")
        f.write(f"- **Czas skanu:** {elapsed:.1f}s\n")
        f.write(f"- **Regiony:** {total_regions}\n")
        f.write(f"- **Regiony z TD:** {len(regions_with_td)}\n")
        f.write(f"- **Sprawdzone chunki:** {total_chunks:,}\n")
        f.write(f"- **Znalezione TE TD:** {total_te}\n\n")

        f.write("## Pokrycie konwersji\n\n")
        f.write("| Tile Entity ID | Liczba | Mapowanie | Uwagi |\n")
        f.write("|----------------|--------|-----------|-------|\n")
        for te_id, count in all_te_by_id.most_common():
            unmapped = all_unmapped.get(te_id, 0)
            status = "[OK]" if unmapped == 0 else "[MISSING]"
            notes = []
            if all_attachments.get(te_id, 0) > 0:
                notes.append("załączniki")
            if all_facades.get(te_id, 0) > 0:
                notes.append("fasady")
            note_str = ", ".join(notes) if notes else "-"
            f.write(f"| {te_id} | {count} | {status} | {note_str} |\n")

        f.write("\n## Podsumowanie\n\n")
        f.write(f"- **Zmapowane TE:** {total_mapped}/{total_te} ({100*total_mapped//max(total_te,1)}%)\n")
        f.write(f"- **Niezmapowane TE:** {total_unmapped}\n")
        f.write(f"- **TE z załącznikami:** {sum(all_attachments.values())}\n")
        f.write(f"- **TE z facadami:** {sum(all_facades.values())}\n")
        if errors:
            f.write(f"\n## Błędy ({len(errors)})\n\n")
            for err in errors[:10]:
                f.write(f"- {err}\n")

    print(f"\n{'='*60}")
    print("RAPORT PEŁNY SKAN (KROK 5):")
    print(f"{'='*60}")
    print(f"Czas: {elapsed:.1f}s")
    print(f"Regiony: {total_regions}")
    print(f"Regiony z TD: {len(regions_with_td)}")
    print(f"Chunki: {total_chunks:,}")
    print(f"TE TD: {total_te}")
    print(f"Zmapowane: {total_mapped} | Niezmapowane: {total_unmapped}")
    for te_id, count in all_te_by_id.most_common():
        print(f"  {te_id}: {count}")
    print(f"\nRaport zapisano do:\n  {json_file}\n  {md_file}")

    return report


if __name__ == "__main__":
    print("="*60)
    print("THERMAL DYNAMICS — KROK 5: PEŁNY SKAN")
    print("="*60)
    analyze_td_fullscan()
