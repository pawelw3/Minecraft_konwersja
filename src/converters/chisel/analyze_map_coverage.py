"""Read-only Chisel coverage analysis for the real 1.7.10 map.

The scanner reads dynamic block IDs from `mapa_1710/level.dat`, scans project
zones plus fixed sample regions, and writes reports only under `output/`.
"""

from __future__ import annotations

import json
import sys
from collections import Counter
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(PROJECT_ROOT))
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from converters.chisel.chisel_converter import ChiselConverter  # noqa: E402
from converters.chisel.mappings import (  # noqa: E402
    DynamicChiselIdEntry,
    is_chisel_te_id,
    normalize_family,
)
from converters.common.item_id_resolver import load_item_id_mapping  # noqa: E402
from minecraft_map_parser.anvil_parser import AnvilParser  # noqa: E402
from minecraft_map_parser.nbt_parser import NBTTag  # noqa: E402


WORLD_PATH = PROJECT_ROOT / "mapa_1710"
ZONES_PATH = PROJECT_ROOT / "strefy"
OUTPUT_DIR = PROJECT_ROOT / "output" / "chisel_coverage"
EXTRA_REGIONS = {(0, 0), (1, 1), (-1, -1), (10, 10), (-10, -10)}
MAX_SAMPLES_PER_KEY = 8


@dataclass
class FoundBlockSample:
    scope: str
    block_id: int
    registry_name: str
    metadata: int
    x: int
    y: int
    z: int
    target: str | None
    success: bool
    warnings: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)


@dataclass
class FoundTESample:
    scope: str
    te_id: str
    x: int
    y: int
    z: int
    block_id: int | None
    registry_name: str | None
    metadata: int
    target: str | None
    success: bool
    nbt_keys: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)


@dataclass
class ScopeStats:
    regions: int = 0
    chunks: int = 0
    chisel_blocks: int = 0
    chisel_te: int = 0
    block_counts: Counter = field(default_factory=Counter)
    target_counts: Counter = field(default_factory=Counter)
    te_counts: Counter = field(default_factory=Counter)
    warnings: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "regions": self.regions,
            "chunks": self.chunks,
            "chisel_blocks": self.chisel_blocks,
            "chisel_te": self.chisel_te,
            "block_counts": dict(self.block_counts),
            "target_counts": dict(self.target_counts),
            "te_counts": dict(self.te_counts),
            "warnings": self.warnings,
            "errors": self.errors,
        }


@dataclass
class CoverageReport:
    numeric_block_registry: dict[int, str]
    scopes: dict[str, ScopeStats] = field(default_factory=dict)
    total_regions: int = 0
    total_chunks: int = 0
    total_chisel_blocks: int = 0
    total_chisel_te: int = 0
    converted_block_variants: int = 0
    unsupported_block_variants: int = 0
    converted_te: int = 0
    unsupported_te: int = 0
    block_counts: Counter = field(default_factory=Counter)
    target_counts: Counter = field(default_factory=Counter)
    te_counts: Counter = field(default_factory=Counter)
    warnings: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)
    block_samples: list[FoundBlockSample] = field(default_factory=list)
    te_samples: list[FoundTESample] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "numeric_block_registry": {str(k): v for k, v in sorted(self.numeric_block_registry.items())},
            "scopes": {name: stats.to_dict() for name, stats in self.scopes.items()},
            "total_regions": self.total_regions,
            "total_chunks": self.total_chunks,
            "total_chisel_blocks": self.total_chisel_blocks,
            "total_chisel_te": self.total_chisel_te,
            "converted_block_variants": self.converted_block_variants,
            "unsupported_block_variants": self.unsupported_block_variants,
            "converted_te": self.converted_te,
            "unsupported_te": self.unsupported_te,
            "block_counts": dict(self.block_counts),
            "target_counts": dict(self.target_counts),
            "te_counts": dict(self.te_counts),
            "warnings": self.warnings,
            "errors": self.errors,
            "block_samples": [asdict(item) for item in self.block_samples],
            "te_samples": [asdict(item) for item in self.te_samples],
        }


def nbt_to_python(value: Any) -> Any:
    if isinstance(value, NBTTag):
        if value.type == NBTTag.TAG_COMPOUND:
            return {key: nbt_to_python(inner) for key, inner in value.value.items()}
        if value.type == NBTTag.TAG_LIST:
            return [nbt_to_python(inner) for inner in value.value]
        return value.value
    if isinstance(value, dict):
        return {key: nbt_to_python(inner) for key, inner in value.items()}
    if isinstance(value, list):
        return [nbt_to_python(inner) for inner in value]
    return value


def load_chisel_registry(world_path: Path) -> dict[int, str]:
    raw_mapping = load_item_id_mapping(world_path / "level.dat")
    registry: dict[int, str] = {}
    for numeric_id, registry_name in raw_mapping.items():
        if not str(registry_name).lower().startswith("chisel:"):
            continue
        registry[int(numeric_id)] = str(registry_name)
    return registry


def dynamic_map_from_registry(registry: dict[int, str]) -> dict[int, DynamicChiselIdEntry]:
    result: dict[int, DynamicChiselIdEntry] = {}
    for numeric_id, registry_name in registry.items():
        path = registry_name.split(":", 1)[1]
        family = path.rsplit(".", 1)[0] if "." in path else path
        result[numeric_id] = DynamicChiselIdEntry(numeric_id=numeric_id, family=normalize_family(family))
    return result


def load_zones() -> dict[str, dict[str, Any]]:
    zones: dict[str, dict[str, Any]] = {}
    for zone_file in sorted(ZONES_PATH.glob("*/coords.json")):
        data = json.loads(zone_file.read_text(encoding="utf-8"))
        coords = data.get("minecraftCoordinates", [])
        if not coords:
            continue
        name = data.get("name", zone_file.parent.name)
        zones[name] = {
            "type": "zone",
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


def chunk_intersects_scope(chunk_x: int, chunk_z: int, scope: dict[str, Any]) -> bool:
    if scope["type"] == "region":
        return (chunk_x >> 5, chunk_z >> 5) == (scope["rx"], scope["rz"])
    block_x = chunk_x * 16
    block_z = chunk_z * 16
    return (
        block_x + 15 >= scope["x_min"]
        and block_x <= scope["x_max"]
        and block_z + 15 >= scope["z_min"]
        and block_z <= scope["z_max"]
    )


def block_in_scope(x: int, z: int, scope: dict[str, Any]) -> bool:
    if scope["type"] == "region":
        return (x >> 9, z >> 9) == (scope["rx"], scope["rz"])
    return scope["x_min"] <= x <= scope["x_max"] and scope["z_min"] <= z <= scope["z_max"]


def section_arrays(section: dict[str, Any]) -> tuple[int, Any, Any, Any]:
    section = nbt_to_python(section)
    section_y = int(section.get("Y", 0) or 0)
    return section_y, section.get("Blocks"), section.get("Add") or section.get("AddBlocks"), section.get("Data")


def get_nibble(data: Any, index: int) -> int:
    if not data or index // 2 >= len(data):
        return 0
    value = data[index // 2]
    return (value & 0x0F) if index % 2 == 0 else ((value >> 4) & 0x0F)


def get_block_at(chunk: Any, x: int, y: int, z: int) -> tuple[int | None, int]:
    local_x = x - chunk.x * 16
    local_z = z - chunk.z * 16
    if not (0 <= local_x < 16 and 0 <= local_z < 16 and 0 <= y <= 255):
        return None, 0
    target_section_y = y // 16
    y_in_section = y % 16
    for section in chunk.get_sections():
        section_y, blocks, add, data = section_arrays(section)
        if section_y != target_section_y or blocks is None:
            continue
        index = y_in_section * 256 + local_z * 16 + local_x
        if index >= len(blocks):
            return None, 0
        return ((get_nibble(add, index) << 8) | (blocks[index] & 0xFF)), get_nibble(data, index)
    return None, 0


def scan_blocks_in_chunk(
    chunk: Any,
    scope_name: str,
    scope: dict[str, Any],
    registry: dict[int, str],
    converter: ChiselConverter,
    report: CoverageReport,
    stats: ScopeStats,
    sample_counts: Counter,
) -> None:
    chunk_x0 = chunk.x * 16
    chunk_z0 = chunk.z * 16
    full_chunk_inside = scope["type"] == "region" or (
        scope["x_min"] <= chunk_x0
        and chunk_x0 + 15 <= scope["x_max"]
        and scope["z_min"] <= chunk_z0
        and chunk_z0 + 15 <= scope["z_max"]
    )
    chisel_ids = set(registry)
    for section in chunk.get_sections():
        section_y, blocks, add, data = section_arrays(section)
        # Every Chisel block ID in this world is >255, so sections without Add
        # cannot contain Chisel blocks. This matches the faster per-mod scanners.
        if blocks is None or add is None:
            continue
        max_index = min(4096, len(blocks))
        for index in range(max_index):
            numeric_id = (get_nibble(add, index) << 8) | (blocks[index] & 0xFF)
            if numeric_id not in chisel_ids:
                continue
            local_x = index & 0x0F
            local_z = (index >> 4) & 0x0F
            local_y = (index >> 8) & 0x0F
            world_x = chunk_x0 + local_x
            world_z = chunk_z0 + local_z
            if not full_chunk_inside and not block_in_scope(world_x, world_z, scope):
                continue
            metadata = get_nibble(data, index)
            world_y = section_y * 16 + local_y
            registry_name = registry[numeric_id]
            key = f"{registry_name}:{metadata}"
            stats.chisel_blocks += 1
            report.total_chisel_blocks += 1
            stats.block_counts[key] += 1
            report.block_counts[key] += 1
            if sample_counts[key] < MAX_SAMPLES_PER_KEY:
                report.block_samples.append(
                    FoundBlockSample(
                        scope=scope_name,
                        block_id=numeric_id,
                        registry_name=registry_name,
                        metadata=metadata,
                        x=world_x,
                        y=world_y,
                        z=world_z,
                        target=None,
                        success=True,
                    )
                )
                sample_counts[key] += 1


def scan_tile_entities_in_chunk(
    chunk: Any,
    scope_name: str,
    scope: dict[str, Any],
    registry: dict[int, str],
    converter: ChiselConverter,
    report: CoverageReport,
    stats: ScopeStats,
    sample_counts: Counter,
) -> None:
    for raw_te in chunk.get_tile_entities():
        te = nbt_to_python(raw_te)
        te_id = str(te.get("id", ""))
        if not is_chisel_te_id(te_id):
            continue
        x = int(te.get("x", 0) or 0)
        y = int(te.get("y", 0) or 0)
        z = int(te.get("z", 0) or 0)
        if not block_in_scope(x, z, scope):
            continue
        block_id, metadata = get_block_at(chunk, x, y, z)
        registry_name = registry.get(block_id) if block_id is not None else None
        result = converter.convert_tile_entity(te_id, te, metadata, (x, y, z))
        stats.chisel_te += 1
        report.total_chisel_te += 1
        stats.te_counts[te_id] += 1
        report.te_counts[te_id] += 1
        if result.converted.success:
            report.converted_te += 1
        else:
            report.unsupported_te += 1
        if result.converted.block_id_1182:
            stats.target_counts[result.converted.block_id_1182] += 1
            report.target_counts[result.converted.block_id_1182] += 1
        stats.warnings.extend(result.converted.warnings)
        stats.errors.extend(result.converted.errors)
        report.warnings.extend(result.converted.warnings)
        report.errors.extend(result.converted.errors)
        if sample_counts[te_id] < MAX_SAMPLES_PER_KEY:
            report.te_samples.append(
                FoundTESample(
                    scope=scope_name,
                    te_id=te_id,
                    x=x,
                    y=y,
                    z=z,
                    block_id=block_id,
                    registry_name=registry_name,
                    metadata=metadata,
                    target=result.converted.block_id_1182,
                    success=result.converted.success,
                    nbt_keys=sorted(str(key) for key in te.keys()),
                    warnings=result.converted.warnings,
                    errors=result.converted.errors,
                )
            )
            sample_counts[te_id] += 1


def build_scopes() -> dict[str, dict[str, Any]]:
    scopes = load_zones()
    for rx, rz in sorted(EXTRA_REGIONS):
        scopes[f"extra_region_{rx}_{rz}"] = {"type": "region", "rx": rx, "rz": rz}
    return scopes


def analyze() -> CoverageReport:
    registry = load_chisel_registry(WORLD_PATH)
    dynamic_map = dynamic_map_from_registry(registry)
    converter = ChiselConverter(dynamic_id_map=dynamic_map)
    report = CoverageReport(numeric_block_registry=registry)
    scopes = build_scopes()
    block_sample_counts: Counter = Counter()
    te_sample_counts: Counter = Counter()

    for scope_name, scope in scopes.items():
        stats = ScopeStats()
        regions = {(scope["rx"], scope["rz"])} if scope["type"] == "region" else regions_for_zone(scope)
        print(f"Skanuje {scope_name}: {sorted(regions)}")
        for rx, rz in sorted(regions):
            region_path = WORLD_PATH / "region" / f"r.{rx}.{rz}.mca"
            if not region_path.exists():
                continue
            stats.regions += 1
            report.total_regions += 1
            try:
                parser = AnvilParser(str(region_path))
                for local_z in range(32):
                    for local_x in range(32):
                        chunk = parser.get_chunk(local_x, local_z)
                        if chunk is None or not chunk_intersects_scope(chunk.x, chunk.z, scope):
                            continue
                        stats.chunks += 1
                        report.total_chunks += 1
                        scan_blocks_in_chunk(
                            chunk,
                            scope_name,
                            scope,
                            registry,
                            converter,
                            report,
                            stats,
                            block_sample_counts,
                        )
                        scan_tile_entities_in_chunk(
                            chunk,
                            scope_name,
                            scope,
                            registry,
                            converter,
                            report,
                            stats,
                            te_sample_counts,
                        )
            except Exception as exc:  # noqa: BLE001
                message = f"{scope_name} region {rx},{rz}: {exc}"
                stats.errors.append(message)
                report.errors.append(message)
        report.scopes[scope_name] = stats

    annotate_block_variants(report, converter)
    return report


def annotate_block_variants(report: CoverageReport, converter: ChiselConverter) -> None:
    variant_results: dict[str, tuple[bool, str | None, list[str], list[str]]] = {}
    for key in report.block_counts:
        registry_name, metadata_text = key.rsplit(":", 1)
        numeric_id = next((block_id for block_id, name in report.numeric_block_registry.items() if name == registry_name), None)
        if numeric_id is None:
            variant_results[key] = (False, None, [], [f"CHISEL-E-ID-LOOKUP-MISSING: {registry_name}"])
            continue
        result = converter.convert_block(numeric_id, int(metadata_text), None, (0, 0, 0))
        variant_results[key] = (
            result.converted.success,
            result.converted.block_id_1182,
            result.converted.warnings,
            result.converted.errors,
        )

    report.converted_block_variants = sum(1 for success, _, _, _ in variant_results.values() if success)
    report.unsupported_block_variants = sum(1 for success, _, _, _ in variant_results.values() if not success)

    for key, count in report.block_counts.items():
        success, target, warnings, errors = variant_results[key]
        if target:
            report.target_counts[target] += count
        report.warnings.extend(warnings)
        report.errors.extend(errors)

    for scope_stats in report.scopes.values():
        for key, count in scope_stats.block_counts.items():
            success, target, warnings, errors = variant_results[key]
            if target:
                scope_stats.target_counts[target] += count
            scope_stats.warnings.extend(warnings)
            scope_stats.errors.extend(errors)

    for sample in report.block_samples:
        key = f"{sample.registry_name}:{sample.metadata}"
        success, target, warnings, errors = variant_results.get(key, (False, None, [], []))
        sample.success = success
        sample.target = target
        sample.warnings = warnings
        sample.errors = errors


def write_reports(report: CoverageReport) -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    json_path = OUTPUT_DIR / "chisel_coverage_report.json"
    md_path = OUTPUT_DIR / "CHISEL_ZADANIE4_COVERAGE.md"
    json_path.write_text(json.dumps(report.to_dict(), indent=2, ensure_ascii=False), encoding="utf-8")

    lines = [
        "# Chisel - raport pokrycia Zadania 4",
        "",
        "Zakres: strefy z `strefy/*/coords.json` oraz stale probki regionow "
        "`(0,0)`, `(1,1)`, `(-1,-1)`, `(10,10)`, `(-10,-10)`. Mapa `mapa_1710` byla tylko czytana.",
        "",
        "## Podsumowanie",
        "",
        f"- Dynamiczne ID Chisel z `level.dat`: {len(report.numeric_block_registry)}",
        f"- Regiony sprawdzone: {report.total_regions}",
        f"- Chunki sprawdzone: {report.total_chunks}",
        f"- Bloki Chisel znalezione: {report.total_chisel_blocks}",
        f"- Warianty blok/meta Chisel znalezione: {len(report.block_counts)}",
        f"- Tile Entities Chisel znalezione: {report.total_chisel_te}",
        f"- TE przekazane przez konwerter: {report.converted_te}",
        f"- TE nieobslugiwane: {report.unsupported_te}",
        "",
        "## Najczestsze bloki",
        "",
    ]
    if report.block_counts:
        for key, count in report.block_counts.most_common(40):
            lines.append(f"- `{key}`: {count}")
    else:
        lines.append("- Brak blokow Chisel w skanowanym zakresie.")

    lines.extend(["", "## Najczestsze cele 1.18.2", ""])
    if report.target_counts:
        for key, count in report.target_counts.most_common(40):
            lines.append(f"- `{key}`: {count}")
    else:
        lines.append("- Brak celow, bo nie znaleziono blokow/TE.")

    lines.extend(["", "## Tile Entities", ""])
    if report.te_counts:
        for te_id, count in report.te_counts.most_common():
            lines.append(f"- `{te_id}`: {count}")
    else:
        lines.append("- Brak TE Chisel w skanowanym zakresie.")

    lines.extend(["", "## Strefy i probki", ""])
    for scope_name, stats in report.scopes.items():
        lines.append(f"### {scope_name}")
        lines.append(f"- Regiony: {stats.regions}")
        lines.append(f"- Chunki: {stats.chunks}")
        lines.append(f"- Bloki Chisel: {stats.chisel_blocks}")
        lines.append(f"- TE Chisel: {stats.chisel_te}")
        lines.append("")

    if report.warnings:
        lines.extend(["## Warningi unikalne", ""])
        for warning in sorted(set(report.warnings)):
            lines.append(f"- {warning}")
    if report.errors:
        lines.extend(["", "## Bledy", ""])
        for error in report.errors:
            lines.append(f"- {error}")

    md_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Zapisano: {json_path}")
    print(f"Zapisano: {md_path}")


if __name__ == "__main__":
    write_reports(analyze())
