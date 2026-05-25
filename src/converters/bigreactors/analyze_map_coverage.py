"""Analiza pokrycia Big Reactors na mapie 1.7.10.

Tylko odczyt. Nie modyfikuje mapy.
"""

from __future__ import annotations

import json
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "src"))

from minecraft_map_parser.anvil_parser import AnvilParser  # noqa: E402
from minecraft_map_parser.nbt_parser import NBTTag  # noqa: E402

from converters.bigreactors.mappings import (  # noqa: E402
    ALL_BIGREACTORS_TE_IDS,
    get_mapping_for_te_id,
    is_bigreactors_te_id,
)

MAP_DIR = Path("mapa_1710/region")
ZONES_DIR = Path("strefy")
OUTPUT_DIR = Path("output/bigreactors_task4")


def get_nbt_value(value):
    if isinstance(value, NBTTag):
        return value.value
    return value


def load_zones() -> dict[str, Any]:
    zones = {}
    for path in sorted(ZONES_DIR.glob("*/coords.json")):
        data = json.loads(path.read_text(encoding="utf-8"))
        points = [(int(p["x"]), int(p["z"])) for p in data["minecraftCoordinates"]]
        zones[data["name"]] = {
            "name": data["name"],
            "points": points,
        }
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


def classify_zone(x: int, z: int, zones: dict[str, Any]) -> str:
    for name, zone in zones.items():
        if point_in_polygon((x, z), zone["points"]):
            return name
    return "outside_defined_zones"


def scan_all_regions() -> dict[str, Any]:
    zones = load_zones()
    stats = {
        "regions_total": 0,
        "regions_scanned": 0,
        "regions_with_bigreactors": 0,
        "chunks_scanned": 0,
        "chunks_with_bigreactors": 0,
        "total_te": 0,
        "total_bigreactors_te": 0,
        "te_by_id": Counter(),
        "te_by_zone": Counter(),
        "te_positions": defaultdict(list),
        "errors": [],
    }

    region_files = sorted(MAP_DIR.glob("*.mca"))
    stats["regions_total"] = len(region_files)

    for i, region_file in enumerate(region_files):
        if i % 100 == 0:
            print(f"Scanning {i}/{len(region_files)}: {region_file.name}")

        try:
            parser = AnvilParser(str(region_file))
            chunks = parser.get_all_chunks()
            region_has_br = False

            for chunk in chunks:
                chunk_has_br = False
                for te in chunk.get_tile_entities():
                    stats["total_te"] += 1
                    te_id = str(get_nbt_value(te.get("id", "")))

                    if is_bigreactors_te_id(te_id):
                        stats["total_bigreactors_te"] += 1
                        stats["te_by_id"][te_id] += 1
                        x = int(get_nbt_value(te.get("x", 0)))
                        y = int(get_nbt_value(te.get("y", 0)))
                        z = int(get_nbt_value(te.get("z", 0)))
                        zone = classify_zone(x, z, zones)
                        stats["te_by_zone"][zone] += 1
                        stats["te_positions"][te_id].append({
                            "x": x, "y": y, "z": z,
                            "region": region_file.name,
                            "zone": zone,
                        })
                        region_has_br = True
                        chunk_has_br = True

                if chunk_has_br:
                    stats["chunks_with_bigreactors"] += 1
                stats["chunks_scanned"] += 1

            if region_has_br:
                stats["regions_with_bigreactors"] += 1
            stats["regions_scanned"] += 1

        except Exception as e:
            stats["errors"].append({"region": region_file.name, "error": str(e)})

    return stats


def build_report(stats: dict[str, Any]) -> dict[str, Any]:
    # Sprawdzenie pokrycia konwertera
    coverage = {}
    for te_id, count in stats["te_by_id"].items():
        mapping = get_mapping_for_te_id(te_id)
        coverage[te_id] = {
            "count": count,
            "mapped": mapping is not None,
            "target_block_id": mapping.target_block_id if mapping else None,
            "notes": mapping.notes if mapping else None,
        }

    all_known = ALL_BIGREACTORS_TE_IDS
    found_ids = set(stats["te_by_id"].keys())
    missing = all_known - found_ids

    return {
        "scan_stats": {
            "regions_total": stats["regions_total"],
            "regions_scanned": stats["regions_scanned"],
            "regions_with_bigreactors": stats["regions_with_bigreactors"],
            "chunks_scanned": stats["chunks_scanned"],
            "chunks_with_bigreactors": stats["chunks_with_bigreactors"],
            "total_te_scanned": stats["total_te"],
            "total_bigreactors_te": stats["total_bigreactors_te"],
        },
        "te_by_id": dict(stats["te_by_id"]),
        "te_by_zone": dict(stats["te_by_zone"]),
        "coverage": coverage,
        "missing_on_map": sorted(missing),
        "errors": stats["errors"],
    }


def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    print("=== Big Reactors Map Coverage Analysis ===")
    print(f"Map: {MAP_DIR}")
    print(f"Zones: {ZONES_DIR}")

    stats = scan_all_regions()
    report = build_report(stats)

    json_path = OUTPUT_DIR / "bigreactors_coverage_report.json"
    json_path.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"\nJSON report saved: {json_path}")

    # Markdown summary
    md_lines = [
        "# Big Reactors — Analiza pokrycia na mapie 1.7.10",
        "",
        f"**Data:** {__import__('datetime').datetime.now().isoformat()}",
        f"**Regionów:** {report['scan_stats']['regions_scanned']} / {report['scan_stats']['regions_total']}",
        f"**Chunków ze skanem:** {report['scan_stats']['chunks_scanned']}",
        f"**Regionów z BigReactors:** {report['scan_stats']['regions_with_bigreactors']}",
        f"**Chunków z BigReactors:** {report['scan_stats']['chunks_with_bigreactors']}",
        f"**Tile Entities BigReactors:** {report['scan_stats']['total_bigreactors_te']}",
        "",
        "## Rozkład TE per ID",
        "",
        "| TE ID | Liczba | Zmapowane | Target 1.18.2 |",
        "|-------|--------|-----------|---------------|",
    ]
    for te_id in sorted(report["te_by_id"].keys(), key=lambda x: report["te_by_id"][x], reverse=True):
        c = report["coverage"][te_id]
        md_lines.append(
            f"| {te_id} | {c['count']} | {'✅' if c['mapped'] else '❌'} | {c['target_block_id'] or '-'} |"
        )

    md_lines.extend([
        "",
        "## Rozkład per strefa",
        "",
        "| Strefa | Liczba TE |",
        "|--------|-----------|",
    ])
    for zone in sorted(report["te_by_zone"].keys(), key=lambda x: report["te_by_zone"][x], reverse=True):
        md_lines.append(f"| {zone} | {report['te_by_zone'][zone]} |")

    if report["missing_on_map"]:
        md_lines.extend([
            "",
            "## Znane TE nieobecne na mapie",
            "",
        ])
        for te_id in report["missing_on_map"]:
            md_lines.append(f"- `{te_id}`")

    if report["errors"]:
        md_lines.extend([
            "",
            f"## Błędy skanu ({len(report['errors'])})",
            "",
        ])
        for err in report["errors"][:10]:
            md_lines.append(f"- `{err['region']}`: {err['error']}")

    md_path = OUTPUT_DIR / "bigreactors_coverage_report.md"
    md_path.write_text("\n".join(md_lines), encoding="utf-8")
    print(f"Markdown report saved: {md_path}")

    print("\n=== Done ===")


if __name__ == "__main__":
    main()
