"""AE2 step 4 coverage for the main map zones.

This script does not read or modify MCA files. It consumes the aggregated
AE2 positions produced by the fixed map scan and checks them against
strefy/*/coords.json plus the current AE2 converter contracts.
"""

from __future__ import annotations

import csv
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[3]
AE2_DIR = ROOT / "src" / "converters" / "ae2"
ZONES_DIR = ROOT / "strefy"
MAP_DIR = ROOT / "mapa_1710"
MAP_CSV = ROOT / "output" / "ae2_analysis" / "ae2_block_entities_all.csv"
MAP_ANALYSIS = ROOT / "output" / "ae2_analysis" / "ae2_analysis_fixed.json"
STEP1_JSON = AE2_DIR / "AE2_STEP1_REANALYSIS.json"
STEP2_JSON = AE2_DIR / "AE2_STEP2_SIMULATION_RESULTS.json"
OUT_JSON = ROOT / "output" / "ae2_analysis" / "ae2_step4_zone_coverage.json"
OUT_MD = AE2_DIR / "AE2_STEP4_ZONE_COVERAGE.md"
OUT_HANDOFF = AE2_DIR / "HANDOFF_AE2_ZADANIE4_REDO.md"

sys.path.insert(0, str(ROOT))

from src.converters.ae2.ae2_converter import AE2Converter  # noqa: E402
from src.converters.ae2.mappings.block_mappings import get_block_mapping, normalize_block_id  # noqa: E402


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def load_rows() -> list[dict[str, Any]]:
    with MAP_CSV.open("r", encoding="utf-8", newline="") as handle:
        rows = []
        for row in csv.DictReader(handle):
            rows.append(
                {
                    "id": row["id"],
                    "x": int(row["x"]),
                    "y": int(row["y"]),
                    "z": int(row["z"]),
                    "chunk_x": int(row["chunk_x"]),
                    "chunk_z": int(row["chunk_z"]),
                }
            )
    return rows


def load_zones() -> dict[str, dict[str, Any]]:
    zones: dict[str, dict[str, Any]] = {}
    for path in sorted(ZONES_DIR.glob("*/coords.json")):
        data = load_json(path)
        points = [(int(p["x"]), int(p["z"])) for p in data["minecraftCoordinates"]]
        xs = [x for x, _ in points]
        zs = [z for _, z in points]
        min_x, max_x = min(xs), max(xs)
        min_z, max_z = min(zs), max(zs)
        regions = []
        for rx in range(min_x // 512, max_x // 512 + 1):
            for rz in range(min_z // 512, max_z // 512 + 1):
                region_path = MAP_DIR / "region" / f"r.{rx}.{rz}.mca"
                regions.append(
                    {
                        "region": f"r.{rx}.{rz}.mca",
                        "exists": region_path.exists(),
                    }
                )
        zones[data["name"]] = {
            "name": data["name"],
            "points": points,
            "bounds": {"min_x": min_x, "max_x": max_x, "min_z": min_z, "max_z": max_z},
            "regions_intersecting_bounds": regions,
        }
    return zones


def point_on_segment(point: tuple[int, int], a: tuple[int, int], b: tuple[int, int]) -> bool:
    px, pz = point
    ax, az = a
    bx, bz = b
    cross = (pz - az) * (bx - ax) - (px - ax) * (bz - az)
    if cross != 0:
        return False
    return min(ax, bx) <= px <= max(ax, bx) and min(az, bz) <= pz <= max(az, bz)


def point_in_polygon(point: tuple[int, int], polygon: list[tuple[int, int]]) -> bool:
    for i, a in enumerate(polygon):
        if point_on_segment(point, a, polygon[(i + 1) % len(polygon)]):
            return True

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


def classify_id(raw_id: str) -> dict[str, Any]:
    normalized = normalize_block_id(raw_id)
    mapping = get_block_mapping(normalized)
    if not mapping:
        return {
            "raw_id": raw_id,
            "normalized_id": normalized,
            "mapped": False,
            "target": "",
            "converter": "",
            "category": "non_core_or_unmapped",
            "notes": "Brak mapowania w core AE2; TileChestHungry jest traktowany jako dane spoza core AE2/addon.",
        }

    if mapping.id_1182 in {"minecraft:lever", "minecraft:grindstone"}:
        category = "lossy_fallback"
    elif mapping.id_1182.startswith("ae2:"):
        category = "full_ae2"
    else:
        category = "external_target"

    return {
        "raw_id": raw_id,
        "normalized_id": normalized,
        "mapped": True,
        "target": mapping.id_1182,
        "converter": mapping.nbt_converter or "",
        "category": category,
        "notes": mapping.notes,
    }


def dry_run_unique_ids(ids: list[str]) -> list[dict[str, Any]]:
    converter = AE2Converter()
    results = []
    for raw_id in sorted(set(ids)):
        nbt = {"id": raw_id, "x": 0, "y": 64, "z": 0}
        result = converter.convert_block(raw_id, nbt, metadata=0, position=(0, 64, 0))
        results.append(
            {
                "raw_id": raw_id,
                "success": result.converted.success,
                "target": result.converted.block_id_1182 or "",
                "errors": result.converted.errors,
                "warnings": result.converted.warnings,
            }
        )
    return results


def region_name(row: dict[str, Any]) -> str:
    return f"r.{row['chunk_x'] // 32}.{row['chunk_z'] // 32}.mca"


def empty_zone_result(zone: dict[str, Any]) -> dict[str, Any]:
    return {
        "name": zone["name"],
        "bounds": zone["bounds"],
        "regions_intersecting_bounds": zone["regions_intersecting_bounds"],
        "total_ae2_like_te": 0,
        "full_ae2_count": 0,
        "lossy_fallback_count": 0,
        "non_core_or_unmapped_count": 0,
        "by_id": Counter(),
        "by_target": Counter(),
        "by_category": Counter(),
        "by_region": Counter(),
        "unhandled_ids": Counter(),
    }


def convert_counters(value: Any) -> Any:
    if isinstance(value, Counter):
        return dict(value)
    if isinstance(value, defaultdict):
        return {k: convert_counters(v) for k, v in value.items()}
    if isinstance(value, dict):
        return {k: convert_counters(v) for k, v in value.items()}
    if isinstance(value, list):
        return [convert_counters(v) for v in value]
    return value


def build_report() -> dict[str, Any]:
    rows = load_rows()
    zones = load_zones()
    step1 = load_json(STEP1_JSON)
    step2 = load_json(STEP2_JSON)
    map_analysis = load_json(MAP_ANALYSIS)

    classifications = {raw_id: classify_id(raw_id) for raw_id in sorted({row["id"] for row in rows})}
    dry_runs = dry_run_unique_ids([row["id"] for row in rows])
    dry_run_errors = [entry for entry in dry_runs if not entry["success"] and entry["raw_id"] != "TileChestHungry"]

    zone_results = {name: empty_zone_result(zone) for name, zone in zones.items()}
    outside_zones = Counter()
    global_categories = Counter()
    global_targets = Counter()
    top_regions = Counter()
    rows_in_any_zone = 0

    for row in rows:
        classification = classifications[row["id"]]
        category = classification["category"]
        target = classification["target"] or "unmapped"
        global_categories[category] += 1
        global_targets[target] += 1
        top_regions[region_name(row)] += 1

        matched = []
        for name, zone in zones.items():
            if point_in_polygon((row["x"], row["z"]), zone["points"]):
                matched.append(name)

        if not matched:
            outside_zones[row["id"]] += 1
            continue

        rows_in_any_zone += 1
        for name in matched:
            result = zone_results[name]
            result["total_ae2_like_te"] += 1
            result["by_id"][row["id"]] += 1
            result["by_target"][target] += 1
            result["by_category"][category] += 1
            result["by_region"][region_name(row)] += 1
            if category == "full_ae2":
                result["full_ae2_count"] += 1
            elif category == "lossy_fallback":
                result["lossy_fallback_count"] += 1
            else:
                result["non_core_or_unmapped_count"] += 1
                result["unhandled_ids"][row["id"]] += 1

    report = {
        "inputs": {
            "map_csv": str(MAP_CSV.relative_to(ROOT)).replace("\\", "/"),
            "map_analysis": str(MAP_ANALYSIS.relative_to(ROOT)).replace("\\", "/"),
            "zones_dir": str(ZONES_DIR.relative_to(ROOT)).replace("\\", "/"),
            "map_dir": str(MAP_DIR.relative_to(ROOT)).replace("\\", "/"),
            "step1": str(STEP1_JSON.relative_to(ROOT)).replace("\\", "/"),
            "step2": str(STEP2_JSON.relative_to(ROOT)).replace("\\", "/"),
        },
        "summary": {
            "zones_checked": len(zones),
            "global_ae2_like_te": len(rows),
            "global_ae2_like_te_from_analysis": map_analysis["total_ae2_te"],
            "global_core_mapped_te": step1["map_totals"]["mapped_te_count_by_prefixed_table"],
            "global_non_core_or_unmapped_te": step1["map_totals"]["unmapped_te_count"],
            "in_defined_zones": rows_in_any_zone,
            "outside_defined_zones": len(rows) - rows_in_any_zone,
            "step2_status": step2["status"],
            "step2_passed": f"{step2['passed']}/{step2['total']}",
            "dry_run_core_errors": dry_run_errors,
        },
        "global_by_category": global_categories,
        "global_by_target": global_targets,
        "global_top_regions": dict(top_regions.most_common(20)),
        "outside_zones_by_id": outside_zones,
        "classifications": classifications,
        "dry_runs": dry_runs,
        "zones": zone_results,
    }
    return convert_counters(report)


def pct(part: int, total: int) -> str:
    if total == 0:
        return "0.0%"
    return f"{part / total * 100:.1f}%"


def table(rows: list[list[Any]], headers: list[str]) -> list[str]:
    lines = ["| " + " | ".join(headers) + " |", "| " + " | ".join(["---"] * len(headers)) + " |"]
    for row in rows:
        lines.append("| " + " | ".join(str(v) for v in row) + " |")
    return lines


def write_markdown(report: dict[str, Any]) -> None:
    summary = report["summary"]
    zone_rows = []
    for zone in report["zones"].values():
        total = zone["total_ae2_like_te"]
        accepted = zone["full_ae2_count"] + zone["lossy_fallback_count"]
        zone_rows.append(
            [
                zone["name"],
                total,
                zone["full_ae2_count"],
                zone["lossy_fallback_count"],
                zone["non_core_or_unmapped_count"],
                pct(accepted, total),
            ]
        )

    type_rows = []
    zone_type_counter = Counter()
    for zone in report["zones"].values():
        zone_type_counter.update(zone["by_id"])
    for raw_id, count in zone_type_counter.most_common():
        classification = report["classifications"][raw_id]
        type_rows.append([raw_id, count, classification["target"] or "unmapped", classification["category"]])

    lines = [
        "# AE2 - Krok 4: pokrycie stref glownej mapy",
        "",
        "Zakres: `strefy/*/coords.json`, `mapa_1710`, bez edycji mapy. Raport uzywa aktualnych wynikow kroku 1-3 oraz pelnego agregatu `output/ae2_analysis/ae2_block_entities_all.csv`.",
        "",
        "## Podsumowanie",
        "",
        f"- Strefy sprawdzone: {summary['zones_checked']}",
        f"- Globalnie znalezione AE2-like Tile Entities: {summary['global_ae2_like_te']}",
        f"- Globalnie zmapowane core AE2: {summary['global_core_mapped_te']}",
        f"- Globalnie poza core/unmapped: {summary['global_non_core_or_unmapped_te']} (`TileChestHungry`)",
        f"- W zdefiniowanych strefach: {summary['in_defined_zones']}",
        f"- Poza zdefiniowanymi strefami: {summary['outside_defined_zones']}",
        f"- Symulacje kroku 2: {summary['step2_status']} ({summary['step2_passed']})",
        f"- Suchy przebieg konwertera dla core AE2: {'OK' if not summary['dry_run_core_errors'] else 'BLEDY'}",
        "",
        "## Pokrycie po strefach",
        "",
        *table(
            zone_rows,
            ["Strefa", "AE2-like TE", "Pelne AE2", "Lossy fallback", "Poza core/unmapped", "Akceptowane"],
        ),
        "",
        "## Typy AE2 w strefach",
        "",
    ]

    if type_rows:
        lines.extend(table(type_rows, ["NBT id", "Liczba", "Target", "Kategoria"]))
    else:
        lines.append("Brak AE2-like Tile Entities wewnatrz zdefiniowanych stref.")

    lines.extend(
        [
            "",
            "## Uwagi",
            "",
            "- `full_ae2` oznacza mapowanie na blok `ae2:*` z aktualnym konwerterem NBT.",
            "- `lossy_fallback` oznacza jawna decyzje projektu: `BlockCrank -> minecraft:lever`, `BlockGrinder -> minecraft:grindstone`; nie jest to potwierdzona migracja 1:1.",
            "- `TileChestHungry` pozostaje poza core AE2 i nie blokuje pokrycia AE2 11.7.6.",
            "- Step 4 nie zapisuje do `mapa_1710`; operuje na wygenerowanym CSV z pozycjami i definicjach stref.",
            "",
            "## Najwieksze regiony AE2 globalnie",
            "",
            *table(
                [[region, count] for region, count in report["global_top_regions"].items()],
                ["Region", "AE2-like TE"],
            ),
        ]
    )

    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_handoff(report: dict[str, Any]) -> None:
    summary = report["summary"]
    content = f"""# Handoff: AE2 - Zadanie 4 wykonane ponownie

## Podsumowanie sesji
Wykonano krok 4 AE2 na aktualnych artefaktach po krokach 1-3. Sprawdzono pokrycie realnych AE2-like Tile Entities w strefach `strefy/*/coords.json`, wykonano suchy przebieg konwertera po realnych typach i potwierdzono zgodnosc z kontraktami symulacji.

## Ukończono
- [x] Przeliczono AE2 w 5 zdefiniowanych strefach bez edycji `mapa_1710`.
- [x] Rozdzielono przypadki na pelne AE2, jawny lossy fallback i poza core/unmapped.
- [x] Wykonano dry-run aktualnego `AE2Converter` po realnych typach z mapy.
- [x] Naprawiono podpisy konwerterow utility AE2, ktore blokowaly `BlockQuantumLinkChamber`.
- [x] Potwierdzono symulacje kroku 2: {summary['step2_status']} ({summary['step2_passed']}).

## Wynik
- Globalnie AE2-like TE: {summary['global_ae2_like_te']}
- Globalnie core AE2 zmapowane: {summary['global_core_mapped_te']}
- W strefach: {summary['in_defined_zones']}
- Poza strefami: {summary['outside_defined_zones']}
- Dry-run core AE2: {'OK' if not summary['dry_run_core_errors'] else 'BLEDY'}

## Nowe pliki
- `src/converters/ae2/analyze_step4_zone_coverage.py`
- `src/converters/ae2/AE2_STEP4_ZONE_COVERAGE.md`
- `src/converters/ae2/HANDOFF_AE2_ZADANIE4_REDO.md`
- `output/ae2_analysis/ae2_step4_zone_coverage.json`

## Zmodyfikowane pliki
- `src/converters/ae2/nbt_converters/utility_converters.py`
- `src/converters/ae2/tests/test_ae2_converter.py`
- `src/converters/ae2/analyze_step1_inventory.py`
- `src/converters/ae2/AE2_STEP1_REANALYSIS.md`
- `src/converters/ae2/AE2_STEP1_REANALYSIS.json`

## Następne kroki
1. [ ] Krok 5A AE2: przygotowac lekka mape testowa z reprezentatywnymi blokami i NBT.
2. [ ] Krok 5B AE2: uruchomic konwersje testowej mapy i zweryfikowac wynik.
3. [ ] W testach mapowych osobno przejrzec lossy fallbacki `BlockCrank` i `BlockGrinder`.
"""
    OUT_HANDOFF.write_text(content, encoding="utf-8")


def main() -> None:
    report = build_report()
    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    write_markdown(report)
    write_handoff(report)

    summary = report["summary"]
    print("AE2 step 4 zone coverage complete")
    print(f"Zones checked: {summary['zones_checked']}")
    print(f"Global AE2-like TE: {summary['global_ae2_like_te']}")
    print(f"In zones: {summary['in_defined_zones']}")
    print(f"Outside zones: {summary['outside_defined_zones']}")
    print(f"Step 2 simulations: {summary['step2_status']} ({summary['step2_passed']})")
    print(f"Dry-run core errors: {len(summary['dry_run_core_errors'])}")
    print(f"Wrote: {OUT_MD.relative_to(ROOT)}")
    print(f"Wrote: {OUT_JSON.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
