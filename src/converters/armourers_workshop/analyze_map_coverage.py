"""Read-only Armourer's Workshop coverage analysis for the real 1.7.10 map."""

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

from converters.armourers_workshop.converter import ArmourersWorkshopConverter  # noqa: E402
from converters.armourers_workshop.mappings import BLOCK_MAPPINGS, resolve_source_name  # noqa: E402
from converters.common.item_id_resolver import load_item_id_mapping  # noqa: E402
from minecraft_map_parser.anvil_parser import AnvilParser  # noqa: E402
from minecraft_map_parser.nbt_parser import NBTTag  # noqa: E402


WORLD_PATH = PROJECT_ROOT / "mapa_1710"
ZONES_PATH = PROJECT_ROOT / "strefy"
OUTPUT_DIR = PROJECT_ROOT / "output" / "armourers_workshop_task4"
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
    source_name: str | None
    target: str | None
    status: str
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
    source_name: str | None
    target: str | None
    status: str
    nbt_keys: list[str] = field(default_factory=list)
    skin_pointer: str | None = None
    warnings: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)


@dataclass
class ScopeStats:
    regions: int = 0
    chunks: int = 0
    aw_blocks: int = 0
    aw_te: int = 0
    direct_blocks: int = 0
    placeholder_blocks: int = 0
    failed_blocks: int = 0
    direct_te: int = 0
    placeholder_te: int = 0
    failed_te: int = 0
    block_counts: Counter = field(default_factory=Counter)
    te_counts: Counter = field(default_factory=Counter)
    target_counts: Counter = field(default_factory=Counter)
    warnings: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "regions": self.regions,
            "chunks": self.chunks,
            "aw_blocks": self.aw_blocks,
            "aw_te": self.aw_te,
            "direct_blocks": self.direct_blocks,
            "placeholder_blocks": self.placeholder_blocks,
            "failed_blocks": self.failed_blocks,
            "direct_te": self.direct_te,
            "placeholder_te": self.placeholder_te,
            "failed_te": self.failed_te,
            "block_counts": dict(self.block_counts),
            "te_counts": dict(self.te_counts),
            "target_counts": dict(self.target_counts),
            "warnings": self.warnings,
            "errors": self.errors,
        }


@dataclass
class CoverageReport:
    numeric_block_registry: dict[int, str]
    known_source_names: list[str]
    scopes: dict[str, ScopeStats] = field(default_factory=dict)
    total_regions: int = 0
    total_chunks: int = 0
    total_aw_blocks: int = 0
    total_aw_te: int = 0
    converted_block_variants: int = 0
    placeholder_block_variants: int = 0
    unsupported_block_variants: int = 0
    converted_te: int = 0
    placeholder_te: int = 0
    unsupported_te: int = 0
    block_counts: Counter = field(default_factory=Counter)
    te_counts: Counter = field(default_factory=Counter)
    target_counts: Counter = field(default_factory=Counter)
    skin_pointer_counts: Counter = field(default_factory=Counter)
    warnings: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)
    block_samples: list[FoundBlockSample] = field(default_factory=list)
    te_samples: list[FoundTESample] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "numeric_block_registry": {str(k): v for k, v in sorted(self.numeric_block_registry.items())},
            "known_source_names": self.known_source_names,
            "scopes": {name: stats.to_dict() for name, stats in self.scopes.items()},
            "total_regions": self.total_regions,
            "total_chunks": self.total_chunks,
            "total_aw_blocks": self.total_aw_blocks,
            "total_aw_te": self.total_aw_te,
            "converted_block_variants": self.converted_block_variants,
            "placeholder_block_variants": self.placeholder_block_variants,
            "unsupported_block_variants": self.unsupported_block_variants,
            "converted_te": self.converted_te,
            "placeholder_te": self.placeholder_te,
            "unsupported_te": self.unsupported_te,
            "block_counts": dict(self.block_counts),
            "te_counts": dict(self.te_counts),
            "target_counts": dict(self.target_counts),
            "skin_pointer_counts": dict(self.skin_pointer_counts),
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


def load_aw_registry(world_path: Path) -> dict[int, str]:
    raw_mapping = load_item_id_mapping(world_path / "level.dat")
    registry: dict[int, str] = {}
    for numeric_id, registry_name in raw_mapping.items():
        name = str(registry_name)
        if name.startswith("armourersWorkshop:block."):
            registry[int(numeric_id)] = name
    return registry


def is_aw_te_id(te_id: str) -> bool:
    return te_id in {mapping.source_te_id for mapping in BLOCK_MAPPINGS.values() if mapping.source_te_id}


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


def conversion_status(conversion: Any) -> str:
    result = conversion.converted
    if not result.success:
        return "failed"
    if result.event_json is not None or any("PLACEHOLDER-RESCUE" in warning for warning in result.warnings):
        return "placeholder"
    return "converted"


def add_status(stats: ScopeStats, report: CoverageReport, status: str, *, is_te: bool) -> None:
    if is_te:
        if status == "converted":
            stats.direct_te += 1
            report.converted_te += 1
        elif status == "placeholder":
            stats.placeholder_te += 1
            report.placeholder_te += 1
        else:
            stats.failed_te += 1
            report.unsupported_te += 1
    else:
        if status == "converted":
            stats.direct_blocks += 1
        elif status == "placeholder":
            stats.placeholder_blocks += 1
        else:
            stats.failed_blocks += 1


def scan_blocks_in_chunk(
    chunk: Any,
    scope_name: str,
    scope: dict[str, Any],
    registry: dict[int, str],
    converter: ArmourersWorkshopConverter,
    report: CoverageReport,
    stats: ScopeStats,
    sample_counts: Counter,
) -> None:
    for section in chunk.get_sections():
        section_y, blocks, add, data = section_arrays(section)
        if blocks is None:
            continue
        for index, raw_block in enumerate(blocks):
            block_id = (get_nibble(add, index) << 8) | (raw_block & 0xFF)
            registry_name = registry.get(block_id)
            if registry_name is None:
                continue
            y = section_y * 16 + (index // 256)
            z = chunk.z * 16 + ((index % 256) // 16)
            x = chunk.x * 16 + (index % 16)
            if not block_in_scope(x, z, scope):
                continue
            metadata = get_nibble(data, index)
            source_name = resolve_source_name(registry_name)
            key = f"{registry_name}:{metadata}"
            stats.aw_blocks += 1
            report.total_aw_blocks += 1
            stats.block_counts[key] += 1
            report.block_counts[key] += 1
            if sample_counts[key] < MAX_SAMPLES_PER_KEY:
                conversion = converter.convert_block(registry_name, metadata, None, (x, y, z))
                status = conversion_status(conversion)
                report.block_samples.append(
                    FoundBlockSample(
                        scope=scope_name,
                        block_id=block_id,
                        registry_name=registry_name,
                        metadata=metadata,
                        x=x,
                        y=y,
                        z=z,
                        source_name=source_name,
                        target=conversion.converted.block_id_1182,
                        status=status,
                        warnings=conversion.converted.warnings,
                        errors=conversion.converted.errors,
                    )
                )
                sample_counts[key] += 1


def scan_tile_entities_in_chunk(
    chunk: Any,
    scope_name: str,
    scope: dict[str, Any],
    registry: dict[int, str],
    converter: ArmourersWorkshopConverter,
    report: CoverageReport,
    stats: ScopeStats,
    sample_counts: Counter,
) -> None:
    for raw_te in chunk.get_tile_entities():
        te = nbt_to_python(raw_te)
        te_id = str(te.get("id", ""))
        if not is_aw_te_id(te_id):
            continue
        x = int(te.get("x", 0) or 0)
        y = int(te.get("y", 0) or 0)
        z = int(te.get("z", 0) or 0)
        if not block_in_scope(x, z, scope):
            continue
        block_id, metadata = get_block_at(chunk, x, y, z)
        registry_name = registry.get(block_id) if block_id is not None else None
        source_name = resolve_source_name(registry_name or "", te_id)
        conversion = converter.convert_block(registry_name or source_name or te_id, metadata, te, (x, y, z))
        status = conversion_status(conversion)
        skin_pointer = extract_skin_pointer(te)

        stats.aw_te += 1
        report.total_aw_te += 1
        stats.te_counts[te_id] += 1
        report.te_counts[te_id] += 1
        add_status(stats, report, status, is_te=True)
        if conversion.converted.block_id_1182:
            stats.target_counts[conversion.converted.block_id_1182] += 1
            report.target_counts[conversion.converted.block_id_1182] += 1
        if skin_pointer:
            report.skin_pointer_counts[skin_pointer] += 1
        stats.warnings.extend(conversion.converted.warnings)
        stats.errors.extend(conversion.converted.errors)
        report.warnings.extend(conversion.converted.warnings)
        report.errors.extend(conversion.converted.errors)

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
                    source_name=source_name,
                    target=conversion.converted.block_id_1182,
                    status=status,
                    nbt_keys=sorted(str(key) for key in te.keys()),
                    skin_pointer=skin_pointer,
                    warnings=conversion.converted.warnings,
                    errors=conversion.converted.errors,
                )
            )
            sample_counts[te_id] += 1


def extract_skin_pointer(te: dict[str, Any]) -> str | None:
    skin_data = te.get("armourersWorkshop")
    if not isinstance(skin_data, dict):
        return None
    identifier = skin_data.get("identifier")
    if not isinstance(identifier, dict):
        return None
    local_id = identifier.get("localId")
    library_file = identifier.get("libraryFile")
    if library_file:
        return f"library:{library_file}"
    if local_id not in (None, "", 0, -1):
        return f"local:{local_id}"
    return None


def build_scopes() -> dict[str, dict[str, Any]]:
    scopes = load_zones()
    for rx, rz in sorted(EXTRA_REGIONS):
        scopes[f"extra_region_{rx}_{rz}"] = {"type": "region", "rx": rx, "rz": rz}
    return scopes


def analyze() -> CoverageReport:
    registry = load_aw_registry(WORLD_PATH)
    converter = ArmourersWorkshopConverter()
    report = CoverageReport(numeric_block_registry=registry, known_source_names=sorted(BLOCK_MAPPINGS))
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


def annotate_block_variants(report: CoverageReport, converter: ArmourersWorkshopConverter) -> None:
    variant_results: dict[str, tuple[str, str | None, list[str], list[str]]] = {}
    for key in report.block_counts:
        registry_name, metadata_text = key.rsplit(":", 1)
        conversion = converter.convert_block(registry_name, int(metadata_text), None, (0, 0, 0))
        variant_results[key] = (
            conversion_status(conversion),
            conversion.converted.block_id_1182,
            conversion.converted.warnings,
            conversion.converted.errors,
        )

    report.converted_block_variants = sum(1 for status, _, _, _ in variant_results.values() if status == "converted")
    report.placeholder_block_variants = sum(1 for status, _, _, _ in variant_results.values() if status == "placeholder")
    report.unsupported_block_variants = sum(1 for status, _, _, _ in variant_results.values() if status == "failed")

    for key, count in report.block_counts.items():
        status, target, warnings, errors = variant_results[key]
        if target:
            report.target_counts[target] += count
        report.warnings.extend(warnings)
        report.errors.extend(errors)
        for scope_stats in report.scopes.values():
            if key not in scope_stats.block_counts:
                continue
            if status == "converted":
                scope_stats.direct_blocks += scope_stats.block_counts[key]
            elif status == "placeholder":
                scope_stats.placeholder_blocks += scope_stats.block_counts[key]
            else:
                scope_stats.failed_blocks += scope_stats.block_counts[key]
            if target:
                scope_stats.target_counts[target] += scope_stats.block_counts[key]
            scope_stats.warnings.extend(warnings)
            scope_stats.errors.extend(errors)

    for sample in report.block_samples:
        key = f"{sample.registry_name}:{sample.metadata}"
        status, target, warnings, errors = variant_results.get(key, ("failed", None, [], []))
        sample.status = status
        sample.target = target
        sample.warnings = warnings
        sample.errors = errors


def write_reports(report: CoverageReport) -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    json_path = OUTPUT_DIR / "armourers_workshop_task4_coverage.json"
    md_path = OUTPUT_DIR / "ARMOURERS_WORKSHOP_ZADANIE4_COVERAGE.md"
    json_path.write_text(json.dumps(report.to_dict(), indent=2, ensure_ascii=False), encoding="utf-8")

    lines = [
        "# Armourer's Workshop - raport pokrycia Zadania 4",
        "",
        "Zakres: strefy z `strefy/*/coords.json` oraz stale probki regionow "
        "`(0,0)`, `(1,1)`, `(-1,-1)`, `(10,10)`, `(-10,-10)`. Mapa `mapa_1710` byla tylko czytana.",
        "",
        "## Podsumowanie",
        "",
        f"- Dynamiczne ID blokow AW z `level.dat`: {len(report.numeric_block_registry)}",
        f"- Regiony sprawdzone: {report.total_regions}",
        f"- Chunki sprawdzone: {report.total_chunks}",
        f"- Bloki AW znalezione: {report.total_aw_blocks}",
        f"- Warianty blok/meta AW znalezione: {len(report.block_counts)}",
        f"- Warianty blok/meta z pelnym remapem: {report.converted_block_variants}",
        f"- Warianty blok/meta placeholder-rescue: {report.placeholder_block_variants}",
        f"- Warianty blok/meta nieobslugiwane: {report.unsupported_block_variants}",
        f"- Tile Entities AW znalezione: {report.total_aw_te}",
        f"- TE z pelnym remapem: {report.converted_te}",
        f"- TE placeholder-rescue: {report.placeholder_te}",
        f"- TE nieobslugiwane: {report.unsupported_te}",
        "",
        "## Najczestsze bloki",
        "",
    ]
    if report.block_counts:
        for key, count in report.block_counts.most_common(40):
            lines.append(f"- `{key}`: {count}")
    else:
        lines.append("- Brak blokow Armourer's Workshop w skanowanym zakresie.")

    lines.extend(["", "## Tile Entities", ""])
    if report.te_counts:
        for te_id, count in report.te_counts.most_common():
            lines.append(f"- `{te_id}`: {count}")
    else:
        lines.append("- Brak TE Armourer's Workshop w skanowanym zakresie.")

    lines.extend(["", "## Najczestsze cele 1.18.2 / rescue", ""])
    if report.target_counts:
        for key, count in report.target_counts.most_common(40):
            lines.append(f"- `{key}`: {count}")
    else:
        lines.append("- Brak celow, bo nie znaleziono blokow/TE.")

    lines.extend(["", "## Wskazniki skinow z TE", ""])
    if report.skin_pointer_counts:
        for key, count in report.skin_pointer_counts.most_common(30):
            lines.append(f"- `{key}`: {count}")
    else:
        lines.append("- Brak wskaznikow skinow w probkach TE lub TE ich nie zawieraly.")

    lines.extend(["", "## Strefy i probki", ""])
    for scope_name, stats in report.scopes.items():
        lines.append(f"### {scope_name}")
        lines.append(f"- Regiony: {stats.regions}")
        lines.append(f"- Chunki: {stats.chunks}")
        lines.append(f"- Bloki AW: {stats.aw_blocks}")
        lines.append(f"- TE AW: {stats.aw_te}")
        lines.append(f"- Pelny remap blokow/TE: {stats.direct_blocks}/{stats.direct_te}")
        lines.append(f"- Placeholder-rescue blokow/TE: {stats.placeholder_blocks}/{stats.placeholder_te}")
        lines.append(f"- Nieobslugiwane blokow/TE: {stats.failed_blocks}/{stats.failed_te}")
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
