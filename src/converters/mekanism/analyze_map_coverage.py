"""Analiza pokrycia konwertera Mekanism na strefach mapy 1.7.10.

Tylko odczyt. Skrypt nie modyfikuje `mapa_1710/`.
"""

from __future__ import annotations

import gzip
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
from minecraft_map_parser.nbt_parser import NBTTag, parse_nbt  # noqa: E402
from src.converters.mekanism import MekanismConverter, get_block_mapping, get_mapping_for_te_id  # noqa: E402
from src.converters.mekanism.mappings import TE_ID_TO_MAPPING_KEY  # noqa: E402


WORLD_PATH = Path("mapa_1710")
ZONES_PATH = Path("strefy")
OUTPUT_DIR = Path("output/mekanism")


@dataclass
class FoundTE:
    zone: str
    te_id: str
    x: int
    y: int
    z: int
    block_id: str | None
    metadata: int
    target: str | None
    success: bool
    warnings: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)
    nbt_keys: list[str] = field(default_factory=list)


@dataclass
class CoverageReport:
    zones: dict[str, dict[str, Any]] = field(default_factory=dict)
    numeric_block_registry: dict[int, str] = field(default_factory=dict)
    total_regions: int = 0
    total_chunks: int = 0
    total_mekanism_blocks: int = 0
    total_mekanism_te: int = 0
    converted_te: int = 0
    unsupported_te: int = 0
    converted_block_variants: int = 0
    unsupported_block_variants: int = 0
    block_counts: Counter = field(default_factory=Counter)
    te_counts: Counter = field(default_factory=Counter)
    target_counts: Counter = field(default_factory=Counter)
    warnings: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)
    found_te: list[FoundTE] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "zones": self.zones,
            "numeric_block_registry": {str(k): v for k, v in sorted(self.numeric_block_registry.items())},
            "total_regions": self.total_regions,
            "total_chunks": self.total_chunks,
            "total_mekanism_blocks": self.total_mekanism_blocks,
            "total_mekanism_te": self.total_mekanism_te,
            "converted_te": self.converted_te,
            "unsupported_te": self.unsupported_te,
            "converted_block_variants": self.converted_block_variants,
            "unsupported_block_variants": self.unsupported_block_variants,
            "block_counts": dict(self.block_counts),
            "te_counts": dict(self.te_counts),
            "target_counts": dict(self.target_counts),
            "warnings": self.warnings,
            "errors": self.errors,
            "found_te": [asdict(item) for item in self.found_te],
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


def load_block_registry(world_path: Path) -> dict[int, str]:
    raw = gzip.open(world_path / "level.dat", "rb").read()
    root = nbt_to_python(parse_nbt(raw))
    registry: dict[int, str] = {}
    for entry in root.get("FML", {}).get("ItemData", []):
        key = entry.get("K")
        value = entry.get("V")
        if not isinstance(key, str) or not isinstance(value, int):
            continue
        if not key.startswith("\x01"):
            continue
        registry[value] = key[1:]
    return registry


def load_zones() -> dict[str, dict[str, Any]]:
    zones = {}
    for zone_file in sorted(ZONES_PATH.glob("*/coords.json")):
        data = json.loads(zone_file.read_text(encoding="utf-8"))
        coords = data.get("minecraftCoordinates", [])
        if not coords:
            continue
        name = data.get("name", zone_file.parent.name)
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
    regions = set()
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


def section_arrays(section: dict[str, Any]) -> tuple[int, Any, Any, Any]:
    section = nbt_to_python(section)
    section_y = int(section.get("Y", 0) or 0)
    return section_y, section.get("Blocks"), section.get("Add") or section.get("AddBlocks"), section.get("Data")


def get_nibble(data: Any, index: int) -> int:
    if not data or index // 2 >= len(data):
        return 0
    value = data[index // 2]
    return (value & 0x0F) if index % 2 == 0 else ((value >> 4) & 0x0F)


def get_block_at(chunk, x: int, y: int, z: int) -> tuple[int | None, int]:
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
        block_id = ((get_nibble(add, index) << 8) | (blocks[index] & 0xFF))
        metadata = get_nibble(data, index)
        return block_id, metadata
    return None, 0


def scan_blocks_in_chunk(
    chunk,
    zone: dict[str, Any],
    registry: dict[int, str],
    mekanism_ids: set[int],
    report: CoverageReport,
    zone_stats: dict[str, Any],
) -> None:
    chunk_x0 = chunk.x * 16
    chunk_z0 = chunk.z * 16
    full_chunk_inside = (
        zone["x_min"] <= chunk_x0
        and chunk_x0 + 15 <= zone["x_max"]
        and zone["z_min"] <= chunk_z0
        and chunk_z0 + 15 <= zone["z_max"]
    )
    for section in chunk.get_sections():
        section_y, blocks, add, data = section_arrays(section)
        if blocks is None or add is None:
            continue
        max_index = min(4096, len(blocks))
        for index in range(max_index):
            numeric_id = (get_nibble(add, index) << 8) | (blocks[index] & 0xFF)
            if numeric_id not in mekanism_ids:
                continue
            if not full_chunk_inside:
                local_z = (index >> 4) & 0x0F
                local_x = index & 0x0F
                world_x = chunk_x0 + local_x
                world_z = chunk_z0 + local_z
                if not block_in_zone(world_x, world_z, zone):
                    continue
            metadata = get_nibble(data, index)
            registry_name = registry[numeric_id]
            key = f"{registry_name}:{metadata}"
            report.block_counts[key] += 1
            zone_stats["block_counts"][key] += 1
            report.total_mekanism_blocks += 1


def is_mekanism_te(te_id: str) -> bool:
    return te_id in TE_ID_TO_MAPPING_KEY


def analyze() -> CoverageReport:
    registry = load_block_registry(WORLD_PATH)
    zones = load_zones()
    converter = MekanismConverter()
    mekanism_numeric_ids = {block_id for block_id, name in registry.items() if name.startswith("Mekanism:")}
    report = CoverageReport(
        numeric_block_registry={block_id: name for block_id, name in registry.items() if name.startswith("Mekanism:")}
    )

    for zone_name, zone in zones.items():
        zone_stats = {
            "regions": 0,
            "chunks": 0,
            "block_counts": Counter(),
            "te_counts": Counter(),
            "converted_te": 0,
            "unsupported_te": 0,
            "warnings": [],
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
                        scan_blocks_in_chunk(chunk, zone, registry, mekanism_numeric_ids, report, zone_stats)
                        for te in chunk.get_tile_entities():
                            te_id = str(te.get("id", ""))
                            x = int(te.get("x", 0) or 0)
                            y = int(te.get("y", 0) or 0)
                            z = int(te.get("z", 0) or 0)
                            if not block_in_zone(x, z, zone) or not is_mekanism_te(te_id):
                                continue
                            block_numeric_id, metadata = get_block_at(chunk, x, y, z)
                            block_name = registry.get(block_numeric_id) if block_numeric_id is not None else None
                            result = converter.convert_block(block_name or te_id, metadata, te, (x, y, z))
                            report.total_mekanism_te += 1
                            report.te_counts[te_id] += 1
                            zone_stats["te_counts"][te_id] += 1
                            if result.converted.success:
                                report.converted_te += 1
                                zone_stats["converted_te"] += 1
                            else:
                                report.unsupported_te += 1
                                zone_stats["unsupported_te"] += 1
                            report.target_counts[str(result.converted.block_id_1182)] += 1
                            report.warnings.extend(result.converted.warnings)
                            report.errors.extend(result.converted.errors)
                            zone_stats["warnings"].extend(result.converted.warnings)
                            zone_stats["errors"].extend(result.converted.errors)
                            report.found_te.append(
                                FoundTE(
                                    zone=zone_name,
                                    te_id=te_id,
                                    x=x,
                                    y=y,
                                    z=z,
                                    block_id=block_name,
                                    metadata=metadata,
                                    target=result.converted.block_id_1182,
                                    success=result.converted.success,
                                    warnings=result.converted.warnings,
                                    errors=result.converted.errors,
                                    nbt_keys=sorted(te.keys()),
                                )
                            )
            except Exception as exc:
                msg = f"{zone_name} region {rx},{rz}: {exc}"
                report.errors.append(msg)
                zone_stats["errors"].append(msg)
        report.zones[zone_name] = _jsonable_zone_stats(zone_stats)

    converted_variants = 0
    unsupported_variants = 0
    for key in report.block_counts:
        registry_name, metadata = key.rsplit(":", 1)
        mapping = get_block_mapping(registry_name, int(metadata))
        if mapping:
            converted_variants += 1
        else:
            unsupported_variants += 1
            report.warnings.append(f"MEK-W-BLOCK-VARIANT-UNMAPPED: {key}")
    report.converted_block_variants = converted_variants
    report.unsupported_block_variants = unsupported_variants
    return report


def _jsonable_zone_stats(zone_stats: dict[str, Any]) -> dict[str, Any]:
    return {
        "regions": zone_stats["regions"],
        "chunks": zone_stats["chunks"],
        "block_counts": dict(zone_stats["block_counts"]),
        "te_counts": dict(zone_stats["te_counts"]),
        "converted_te": zone_stats["converted_te"],
        "unsupported_te": zone_stats["unsupported_te"],
        "warnings": zone_stats["warnings"],
        "errors": zone_stats["errors"],
    }


def write_reports(report: CoverageReport) -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    json_path = OUTPUT_DIR / "mekanism_coverage_report.json"
    md_path = OUTPUT_DIR / "mekanism_coverage_report.md"
    json_path.write_text(json.dumps(report.to_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    lines = [
        "# Mekanism - raport pokrycia Zadania 4",
        "",
        "Zakres: strefy z `strefy/*/coords.json`, mapa `mapa_1710`, tylko odczyt.",
        "",
        "## Podsumowanie",
        "",
        f"- Regiony sprawdzone: {report.total_regions}",
        f"- Chunks sprawdzone: {report.total_chunks}",
        f"- Bloki Mekanism w strefach: {report.total_mekanism_blocks}",
        f"- Tile Entities Mekanism w strefach: {report.total_mekanism_te}",
        f"- TE skonwertowane przez kod: {report.converted_te}",
        f"- TE nieobslugiwane: {report.unsupported_te}",
        f"- Warianty blokow z mapowaniem: {report.converted_block_variants}",
        f"- Warianty blokow bez mapowania: {report.unsupported_block_variants}",
        "",
        "## Tile Entities",
        "",
    ]
    if report.te_counts:
        for te_id, count in report.te_counts.most_common():
            lines.append(f"- `{te_id}`: {count}")
    else:
        lines.append("- Brak TE Mekanism w skanowanych strefach.")
    lines.extend(["", "## Bloki", ""])
    if report.block_counts:
        for key, count in report.block_counts.most_common():
            lines.append(f"- `{key}`: {count}")
    else:
        lines.append("- Brak blokow Mekanism w skanowanych strefach.")
    lines.extend(["", "## Strefy", ""])
    for zone_name, stats in report.zones.items():
        lines.append(f"### {zone_name}")
        lines.append(f"- Chunks: {stats['chunks']}")
        lines.append(f"- TE: {sum(stats['te_counts'].values())}")
        lines.append(f"- Bloki: {sum(stats['block_counts'].values())}")
        lines.append("")
    if report.warnings:
        lines.extend(["## Warningi", ""])
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
    coverage = analyze()
    write_reports(coverage)
