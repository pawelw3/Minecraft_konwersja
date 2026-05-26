"""Logistics Pipes - Zadanie 4: coverage on main map zones.

Read-only scan of `mapa_1710/`. The script checks Logistics Pipes Tile
Entities in `strefy/*/coords.json`, runs the router conversion and writes a
small coverage report. It never writes to the source world.
"""

from __future__ import annotations

import json
import sys
from collections import Counter, defaultdict
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(PROJECT_ROOT))
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from minecraft_map_parser.anvil_parser import AnvilParser  # noqa: E402
from converters.router import convert_te_to_events  # noqa: E402
from converters.logistics_pipes.logistics_pipes_converter import find_pipe_class  # noqa: E402
from converters.logistics_pipes.mappings import (  # noqa: E402
    GENERIC_PIPE_TE_ID,
    is_logistics_pipes_te_id,
    resolve_pipe_class_from_id,
)


WORLD_PATH = PROJECT_ROOT / "mapa_1710"
ZONES_PATH = PROJECT_ROOT / "strefy"
OUTPUT_DIR = PROJECT_ROOT / "output" / "logistics_pipes_task4"
MAX_SAMPLES = 80


@dataclass
class FoundLogisticsTE:
    zone: str
    te_id: str
    x: int
    y: int
    z: int
    pipe_class: str | None
    target_blocks: list[str]
    warnings: list[str] = field(default_factory=list)
    nbt_keys: list[str] = field(default_factory=list)


@dataclass
class CoverageReport:
    total_regions: int = 0
    total_chunks: int = 0
    total_logistics_te: int = 0
    converted_events: int = 0
    placeholder_events: int = 0
    empty_events: int = 0
    zones: dict[str, dict[str, Any]] = field(default_factory=dict)
    te_counts: Counter[str] = field(default_factory=Counter)
    target_counts: Counter[str] = field(default_factory=Counter)
    pipe_class_counts: Counter[str] = field(default_factory=Counter)
    pipe_id_counts: Counter[str] = field(default_factory=Counter)
    warning_counts: Counter[str] = field(default_factory=Counter)
    samples: list[FoundLogisticsTE] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "total_regions": self.total_regions,
            "total_chunks": self.total_chunks,
            "total_logistics_te": self.total_logistics_te,
            "converted_events": self.converted_events,
            "placeholder_events": self.placeholder_events,
            "empty_events": self.empty_events,
            "zones": self.zones,
            "te_counts": dict(self.te_counts),
            "target_counts": dict(self.target_counts),
            "pipe_class_counts": dict(self.pipe_class_counts),
            "pipe_id_counts": dict(self.pipe_id_counts),
            "warning_counts": dict(self.warning_counts),
            "samples": [asdict(sample) for sample in self.samples],
            "errors": self.errors,
        }


def load_zones() -> dict[str, dict[str, Any]]:
    zones: dict[str, dict[str, Any]] = {}
    for coords_file in sorted(ZONES_PATH.glob("*/coords.json")):
        data = json.loads(coords_file.read_text(encoding="utf-8"))
        coords = data.get("minecraftCoordinates", [])
        if not coords:
            continue
        name = data.get("name", coords_file.parent.name)
        zones[name] = {
            "coords": coords,
            "x_min": min(point["x"] for point in coords),
            "x_max": max(point["x"] for point in coords),
            "z_min": min(point["z"] for point in coords),
            "z_max": max(point["z"] for point in coords),
        }
    return zones


def regions_for_zone(zone: dict[str, Any]) -> set[tuple[int, int]]:
    min_cx = zone["x_min"] >> 4
    max_cx = zone["x_max"] >> 4
    min_cz = zone["z_min"] >> 4
    max_cz = zone["z_max"] >> 4
    regions: set[tuple[int, int]] = set()
    for cx in range(min_cx, max_cx + 1):
        for cz in range(min_cz, max_cz + 1):
            regions.add((cx >> 5, cz >> 5))
    return regions


def chunk_intersects_zone(chunk_x: int, chunk_z: int, zone: dict[str, Any]) -> bool:
    block_x = chunk_x * 16
    block_z = chunk_z * 16
    return (
        block_x + 15 >= zone["x_min"]
        and block_x <= zone["x_max"]
        and block_z + 15 >= zone["z_min"]
        and block_z <= zone["z_max"]
    )


def block_in_zone(x: int, z: int, zone: dict[str, Any]) -> bool:
    return zone["x_min"] <= x <= zone["x_max"] and zone["z_min"] <= z <= zone["z_max"]


def warning_code(warning: str) -> str:
    return warning.split(":", 1)[0] if ":" in warning else warning


def analyze() -> CoverageReport:
    report = CoverageReport()
    zones = load_zones()

    for zone_name, zone in zones.items():
        zone_stats = {
            "regions": 0,
            "chunks": 0,
            "te_counts": Counter(),
            "target_counts": Counter(),
            "pipe_class_counts": Counter(),
            "pipe_id_counts": Counter(),
            "warning_counts": Counter(),
            "converted_events": 0,
            "placeholder_events": 0,
            "empty_events": 0,
            "errors": [],
        }
        print(f"Strefa {zone_name}: X {zone['x_min']}..{zone['x_max']}, Z {zone['z_min']}..{zone['z_max']}")
        for rx, rz in sorted(regions_for_zone(zone)):
            region_path = WORLD_PATH / "region" / f"r.{rx}.{rz}.mca"
            if not region_path.exists():
                continue
            zone_stats["regions"] += 1
            report.total_regions += 1
            try:
                parser = AnvilParser(str(region_path))
                for local_z in range(32):
                    for local_x in range(32):
                        chunk = parser.get_chunk(local_x, local_z)
                        if chunk is None or not chunk_intersects_zone(chunk.x, chunk.z, zone):
                            continue
                        zone_stats["chunks"] += 1
                        report.total_chunks += 1
                        for te in chunk.get_tile_entities():
                            te_id = str(te.get("id", ""))
                            if not is_logistics_pipes_te_id(te_id):
                                continue
                            x = int(te.get("x", 0) or 0)
                            y = int(te.get("y", 0) or 0)
                            z = int(te.get("z", 0) or 0)
                            if not block_in_zone(x, z, zone):
                                continue

                            events = convert_te_to_events(te, block_numeric_id=0, metadata=0, global_pos=(x, y, z))
                            pipe_class = None
                            if te_id == GENERIC_PIPE_TE_ID:
                                pipe_class = find_pipe_class(te) or resolve_pipe_class_from_id(te.get("pipeId"))
                            pipe_key = pipe_class or ("[unresolved]" if te_id == GENERIC_PIPE_TE_ID else "[non-pipe-te]")
                            targets = [str(event.get("block", "")) for event in events if event.get("block")]
                            warnings = [warning for event in events for warning in event.get("warnings", [])]

                            report.total_logistics_te += 1
                            report.te_counts[te_id] += 1
                            report.pipe_class_counts[pipe_key] += 1
                            zone_stats["te_counts"][te_id] += 1
                            zone_stats["pipe_class_counts"][pipe_key] += 1
                            if te_id == GENERIC_PIPE_TE_ID:
                                pipe_id = str(te.get("pipeId", "[missing]"))
                                report.pipe_id_counts[pipe_id] += 1
                                zone_stats["pipe_id_counts"][pipe_id] += 1
                            for target in targets:
                                report.target_counts[target] += 1
                                zone_stats["target_counts"][target] += 1
                                if target.startswith("conversion_placeholders:"):
                                    report.placeholder_events += 1
                                    zone_stats["placeholder_events"] += 1
                                else:
                                    report.converted_events += 1
                                    zone_stats["converted_events"] += 1
                            if not events:
                                report.empty_events += 1
                                zone_stats["empty_events"] += 1
                            for warning in warnings:
                                code = warning_code(warning)
                                report.warning_counts[code] += 1
                                zone_stats["warning_counts"][code] += 1
                            if len(report.samples) < MAX_SAMPLES:
                                report.samples.append(
                                    FoundLogisticsTE(
                                        zone=zone_name,
                                        te_id=te_id,
                                        x=x,
                                        y=y,
                                        z=z,
                                        pipe_class=pipe_class,
                                        target_blocks=targets,
                                        warnings=warnings,
                                        nbt_keys=sorted(te.keys()),
                                    )
                                )
            except Exception as exc:
                msg = f"{zone_name} region {rx},{rz}: {type(exc).__name__}: {exc}"
                report.errors.append(msg)
                zone_stats["errors"].append(msg)
        report.zones[zone_name] = jsonable_zone_stats(zone_stats)
    return report


def jsonable_zone_stats(zone_stats: dict[str, Any]) -> dict[str, Any]:
    return {
        "regions": zone_stats["regions"],
        "chunks": zone_stats["chunks"],
        "te_counts": dict(zone_stats["te_counts"]),
        "target_counts": dict(zone_stats["target_counts"]),
        "pipe_class_counts": dict(zone_stats["pipe_class_counts"]),
        "pipe_id_counts": dict(zone_stats["pipe_id_counts"]),
        "warning_counts": dict(zone_stats["warning_counts"]),
        "converted_events": zone_stats["converted_events"],
        "placeholder_events": zone_stats["placeholder_events"],
        "empty_events": zone_stats["empty_events"],
        "errors": zone_stats["errors"],
    }


def write_reports(report: CoverageReport) -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    assert "mapa_1710" not in str(OUTPUT_DIR.resolve()), "Output cannot be inside source world"

    json_path = OUTPUT_DIR / "logistics_pipes_task4_coverage.json"
    md_path = OUTPUT_DIR / "logistics_pipes_task4_coverage.md"
    json_path.write_text(json.dumps(report.to_dict(), indent=2, ensure_ascii=False), encoding="utf-8")

    lines = [
        "# Logistics Pipes - Zadanie 4: pokrycie stref mapy",
        "",
        "Zakres: `strefy/*/coords.json`, mapa `mapa_1710`, tryb tylko-do-odczytu.",
        "",
        "## Podsumowanie",
        "",
        f"- Regiony sprawdzone: {report.total_regions}",
        f"- Chunki sprawdzone: {report.total_chunks}",
        f"- Tile Entities Logistics Pipes: {report.total_logistics_te}",
        f"- Eventy konwersji: {report.converted_events}",
        f"- Eventy placeholder: {report.placeholder_events}",
        f"- Puste wyniki routera: {report.empty_events}",
        "",
        "## TE i cele",
        "",
        "| Typ | Liczba |",
        "| --- | ---: |",
    ]
    for te_id, count in report.te_counts.most_common():
        lines.append(f"| `{te_id}` | {count} |")

    lines.extend(["", "## Targety", "", "| Target | Liczba |", "| --- | ---: |"])
    for target, count in report.target_counts.most_common():
        lines.append(f"| `{target}` | {count} |")

    lines.extend(["", "## Rozpoznanie klas rur", "", "| Klasa pipe | Liczba |", "| --- | ---: |"])
    for pipe_class, count in report.pipe_class_counts.most_common():
        lines.append(f"| `{pipe_class}` | {count} |")

    lines.extend(["", "## Numeryczne pipeId", "", "| pipeId | Liczba |", "| --- | ---: |"])
    if report.pipe_id_counts:
        for pipe_id, count in report.pipe_id_counts.most_common():
            lines.append(f"| `{pipe_id}` | {count} |")
    else:
        lines.append("| brak | 0 |")

    lines.extend(["", "## Warningi", "", "| Kod | Liczba |", "| --- | ---: |"])
    if report.warning_counts:
        for code, count in report.warning_counts.most_common():
            lines.append(f"| `{code}` | {count} |")
    else:
        lines.append("| brak | 0 |")

    lines.extend(["", "## Per strefa", "", "| Strefa | TE | Converted | Placeholder | Warningi |", "| --- | ---: | ---: | ---: | ---: |"])
    for zone_name, stats in report.zones.items():
        te_total = sum(stats["te_counts"].values())
        warning_total = sum(stats["warning_counts"].values())
        lines.append(
            f"| {zone_name} | {te_total} | {stats['converted_events']} | "
            f"{stats['placeholder_events']} | {warning_total} |"
        )

    if report.errors:
        lines.extend(["", "## Bledy odczytu", ""])
        lines.extend(f"- {error}" for error in report.errors[:30])

    lines.extend(["", "## Wniosek dla kolejnego kroku", ""])
    unresolved = report.pipe_class_counts.get("[unresolved]", 0)
    if unresolved:
        lines.append(
            f"- {unresolved} rur nie mialo rozpoznawalnej klasy pipe w NBT i wymaga lookupu dynamicznego `pipeId` przed testami mapy."
        )
    else:
        lines.append("- Wszystkie rury w strefach zostaly rozpoznane po klasie pipe lub dynamicznym `pipeId`.")
    lines.append("- Eventy warningowe trzeba zachowac w testach mapy 5A/5B, bo opisuja utrate semantyki LP.")

    md_path.write_text("\n".join(lines), encoding="utf-8")
    print(f"Zapisano: {json_path}")
    print(f"Zapisano: {md_path}")


def main() -> None:
    report = analyze()
    write_reports(report)
    print(json.dumps({
        "total_logistics_te": report.total_logistics_te,
        "converted_events": report.converted_events,
        "placeholder_events": report.placeholder_events,
        "warnings": sum(report.warning_counts.values()),
        "errors": len(report.errors),
    }, indent=2))


if __name__ == "__main__":
    main()
