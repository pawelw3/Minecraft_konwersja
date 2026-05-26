"""Analiza pokrycia ComputerCraft na mapie 1.7.10.

Zadanie 4: Sprawdzenie czy kod pokrywa wszystkie bloki/TE ComputerCraft na mapie.
Tylko odczyt — NIE modyfikuje mapy.

Używa szybkiego skanowania bajtowego.

Uruchomienie:
    python src/converters/computercraft/analyze_map_coverage.py
"""

from __future__ import annotations

import json
import struct
import sys
import time
import zlib
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "src"))

from minecraft_map_parser.nbt_parser import NBTTag, parse_nbt  # noqa: E402

# Znane stringi które identyfikują ComputerCraft w surowych bajtach chunka
# UWAGA: Bare IDs (bez prefiksu) są częste na mapie — musimy je też łapać.
CC_BYTE_PATTERNS = [
    b"computercraft",
    b"computer",          # bare "computer"
    b"turtle",            # bare "turtle"
    b"monitor",           # bare "monitor"
    b"ccprinter",         # bare "ccprinter"
    b"wirelessmodem",     # bare "wirelessmodem"
    b"wiredmodem",        # bare "wiredmodem"
    b"command_computer",  # bare "command_computer"
    b"advanced_modem",    # bare "advanced_modem"
    b"turtleex",          # bare "turtleex"
    b"turtleadv",         # bare "turtleadv"
]

# TE IDs które rozpoznajemy (w tym bare IDs)
CC_KNOWN_TE_IDS = {
    "computercraft : computer",
    "computercraft : diskdrive",
    "computercraft : wirelessmodem",
    "computercraft : monitor",
    "computercraft : ccprinter",
    "computercraft : wiredmodem",
    "computercraft : command_computer",
    "computercraft : advanced_modem",
    "computercraft : speaker",
    "computercraft : turtle",
    "computercraft : turtleex",
    "computercraft : turtleadv",
    "computer",
    "monitor",
    "turtle",
    "drive",
    "speaker",
    "ccprinter",
    "wirelessmodem",
    "wiredmodem",
    "command_computer",
    "advanced_modem",
    "turtleex",
    "turtleadv",
}

MAP_DIR = ROOT / "mapa_1710/region"
ZONES_DIR = ROOT / "strefy"
OUTPUT_DIR = ROOT / "output/computercraft_task4"


# ---------------------------------------------------------------------------
# Zone helpers
# ---------------------------------------------------------------------------

def load_zones() -> dict[str, Any]:
    zones = {}
    for path in sorted(ZONES_DIR.glob("*/coords.json")):
        data = json.loads(path.read_text(encoding="utf-8"))
        points = [(int(p["x"]), int(p["z"])) for p in data["minecraftCoordinates"]]
        zones[data["name"]] = points
    return zones


def point_in_polygon(point: tuple[int, int], polygon: list[tuple[int, int]]) -> bool:
    px, pz = point
    inside = False
    j = len(polygon) - 1
    for i, (xi, zi) in enumerate(polygon):
        xj, zj = polygon[j]
        if (zi > pz) != (zj > pz):
            intersection_x = (xj - xi) * (pz - zi) / (zj - zi) + xi
            if px < intersection_x:
                inside = not inside
        j = i
    return inside


def classify_zone(x: int, z: int, zones: dict[str, list[tuple[int, int]]]) -> str:
    for name, polygon in zones.items():
        if point_in_polygon((x, z), polygon):
            return name
    return "outside_defined_zones"


# ---------------------------------------------------------------------------
# Fast region scanner
# ---------------------------------------------------------------------------

def scan_region_file(region_path: Path) -> dict[str, Any]:
    result = {
        "has_cc": False,
        "chunks_checked": 0,
        "te_count": 0,
        "te_by_id": Counter(),
        "te_positions": [],
        "error": None,
    }

    try:
        data = region_path.read_bytes()

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
                length = struct.unpack(">I", length_data)[0]
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

                # Szybki filtr bajtowy
                if not any(pat in chunk_bytes for pat in CC_BYTE_PATTERNS):
                    continue

                try:
                    nbt = parse_nbt(chunk_bytes)
                except Exception:
                    continue

                level = nbt.get("Level", {})
                if isinstance(level, NBTTag):
                    level = level.value if hasattr(level, "value") else {}
                if not isinstance(level, dict):
                    continue

                te_list = level.get("TileEntities", [])
                if isinstance(te_list, NBTTag):
                    te_list = te_list.value if hasattr(te_list, "value") else []

                for te in te_list:
                    if isinstance(te, NBTTag):
                        te = te.value if hasattr(te, "value") else {}
                    if not isinstance(te, dict):
                        continue

                    te_id_obj = te.get("id")
                    if isinstance(te_id_obj, NBTTag):
                        te_id = str(te_id_obj.value if hasattr(te_id_obj, "value") else te_id_obj)
                    else:
                        te_id = str(te_id_obj) if te_id_obj else ""

                    if te_id not in CC_KNOWN_TE_IDS:
                        continue

                    result["has_cc"] = True
                    result["te_count"] += 1
                    result["te_by_id"][te_id] += 1

                    x = int(te.get("x", 0) if not isinstance(te.get("x"), NBTTag) else te.get("x").value)
                    y = int(te.get("y", 0) if not isinstance(te.get("y"), NBTTag) else te.get("y").value)
                    z = int(te.get("z", 0) if not isinstance(te.get("z"), NBTTag) else te.get("z").value)
                    result["te_positions"].append({"te_id": te_id, "x": x, "y": y, "z": z})

    except Exception as e:
        result["error"] = f"{region_path.name}: {type(e).__name__}: {e}"

    return result


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    print("=" * 60, flush=True)
    print("ComputerCraft — analiza pokrycia na mapie 1.7.10", flush=True)
    print("=" * 60, flush=True)

    if not MAP_DIR.exists():
        print(f"BŁĄD: Nie znaleziono folderu regionów w {MAP_DIR}", flush=True)
        return

    region_files = sorted(MAP_DIR.glob("r.*.*.mca"))
    total_regions = len(region_files)
    print(f"Znaleziono {total_regions} plików regionów.", flush=True)

    zones = load_zones()
    print(f"Wczytano {len(zones)} stref.", flush=True)
    print("Skanowanie sekwencyjne (szybki filtr bajtowy)...", flush=True)

    start = time.time()

    all_te_by_id = Counter()
    total_chunks = 0
    te_positions = []
    errors = []
    regions_with_cc = 0

    for i, rf in enumerate(region_files):
        if i % 100 == 0 and i > 0:
            elapsed = time.time() - start
            print(f"  {i}/{total_regions} regionów ({elapsed:.1f}s)", flush=True)

        res = scan_region_file(rf)

        if res["error"]:
            errors.append(res["error"])

        total_chunks += res["chunks_checked"]
        for k, v in res["te_by_id"].items():
            all_te_by_id[k] += v
        te_positions.extend(res["te_positions"])
        if res["has_cc"]:
            regions_with_cc += 1

    elapsed = time.time() - start
    print(f"\nSkanowanie zakończone w {elapsed:.1f}s", flush=True)

    # Klasyfikacja stref
    te_by_zone = Counter()
    for pos in te_positions:
        zone = classify_zone(pos["x"], pos["z"], zones)
        te_by_zone[f"{pos['te_id']}@{zone}"] += 1
        te_by_zone[f"__zone_total__@{zone}"] += 1

    # Raport
    total_cc = sum(all_te_by_id.values())
    unsupported = {k: v for k, v in all_te_by_id.items() if k not in CC_KNOWN_TE_IDS}

    zone_totals = Counter()
    te_by_zone_breakdown = defaultdict(Counter)
    for key, count in te_by_zone.items():
        if key.startswith("__zone_total__@"):
            zone_totals[key.split("@", 1)[1]] = count
        else:
            te_id, zone_name = key.split("@", 1)
            te_by_zone_breakdown[zone_name][te_id] = count

    report = {
        "summary": {
            "regions_total": total_regions,
            "regions_scanned": total_regions,
            "regions_with_cc": regions_with_cc,
            "chunks_scanned": total_chunks,
            "total_cc_te": total_cc,
            "supported_te": total_cc - sum(unsupported.values()),
            "unsupported_te": sum(unsupported.values()),
            "coverage_percent": round(100 * (total_cc - sum(unsupported.values())) / total_cc, 2) if total_cc else 100.0,
            "elapsed_seconds": round(elapsed, 2),
        },
        "te_by_id": dict(all_te_by_id),
        "unsupported_te_ids": unsupported,
        "zone_breakdown": {
            zone: {
                "total": zone_totals[zone],
                "te_types": dict(te_by_zone_breakdown[zone]),
            }
            for zone in sorted(zone_totals.keys())
        },
        "sample_positions": {
            te_id: [p for p in te_positions if p["te_id"] == te_id][:10]
            for te_id in sorted(all_te_by_id.keys())
        },
        "errors": errors[:20],
    }

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    report_path = OUTPUT_DIR / "computercraft_coverage_report.json"
    report_path.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")

    print("\n" + "=" * 60, flush=True)
    print("PODSUMOWANIE", flush=True)
    print("=" * 60, flush=True)
    summary = report["summary"]
    print(f"Regionów przeskanowanych: {summary['regions_total']}", flush=True)
    print(f"Regionów z ComputerCraft: {summary['regions_with_cc']}", flush=True)
    print(f"Chunków przeskanowanych:  {summary['chunks_scanned']}", flush=True)
    print(f"TE ComputerCraft:         {summary['total_cc_te']}", flush=True)
    print(f"Obsługiwane TE:           {summary['supported_te']}", flush=True)
    print(f"Nieobsługiwane TE:        {summary['unsupported_te']}", flush=True)
    print(f"Pokrycie:                 {summary['coverage_percent']}%", flush=True)
    print(f"Czas skanowania:          {summary['elapsed_seconds']}s", flush=True)

    print("\n--- TE by ID ---", flush=True)
    for te_id, count in sorted(report["te_by_id"].items(), key=lambda x: -x[1]):
        status = "[OK]" if te_id in CC_KNOWN_TE_IDS else "[MISSING]"
        print(f"  {status} {te_id:40s} : {count:5d}", flush=True)

    print("\n--- Podzial per strefa ---", flush=True)
    for zone, data in sorted(report["zone_breakdown"].items(), key=lambda x: -x[1]["total"]):
        print(f"  {zone:25s} : {data['total']:5d} TE", flush=True)

    print(f"\nRaport zapisano do: {report_path}", flush=True)

    if errors:
        print(f"\n[!] Bledy podczas skanowania ({len(errors)}):", flush=True)
        for err in errors[:5]:
            print(f"  - {err}", flush=True)


if __name__ == "__main__":
    main()
