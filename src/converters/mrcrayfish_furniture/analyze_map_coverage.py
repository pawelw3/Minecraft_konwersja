# -*- coding: utf-8 -*-
"""
Analiza pokrycia MrCrayfish Furniture Mod na mapie 1.7.10

Zgodnie ze skillem main_map_coverage:
- Przeskanowanie wszystkich stref (billund, choroszcz, iii_rzesza, rzym, zsrr)
- Przeskanowanie dodatkowych losowych regionow
- Generowanie raportow JSON i Markdown

ABSOLUTNY ZAKAZ MODYFIKACJI mapa_1710/ — tylko odczyt.
"""

from __future__ import annotations

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

import json
from pathlib import Path
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Any, Optional
from collections import Counter

from converters.mrcrayfish_furniture.mrcrayfish_chunk_parser import MrCrayfishChunkParser
from converters.mrcrayfish_furniture.mrcrayfish_converter import MrCrayfishConverter


# Definicje stref
ZONES = {
    "billund": {"x": (280, 602), "z": (-364, -81)},
    "choroszcz": {"x": (763, 916), "z": (-787, -636)},
    "iii_rzesza": {"x": (455, 966), "z": (2955, 3477)},
    "rzym": {"x": (301, 1005), "z": (163, 929)},
    "zsrr": {"x": (-2948, -2086), "z": (-2857, -1759)},
}


def load_zone_coords() -> Dict[str, Tuple[Tuple[int, int], Tuple[int, int]]]:
    """Wczytuje wspolrzedne stref z plikow JSON."""
    zones = {}
    zones_dir = Path("strefy")
    for zone_name in ZONES:
        coords_file = zones_dir / zone_name / "coords.json"
        if coords_file.exists():
            with open(coords_file, "r", encoding="utf-8") as f:
                data = json.load(f)
            coords = data.get("minecraftCoordinates", [])
            if coords:
                xs = [c["x"] for c in coords]
                zs = [c["z"] for c in coords]
                zones[zone_name] = ((min(xs), max(xs)), (min(zs), max(zs)))
        else:
            # Fallback do hardcoded
            zones[zone_name] = (
                ZONES[zone_name]["x"],
                ZONES[zone_name]["z"],
            )
    return zones


def world_to_chunk(x: int, z: int) -> Tuple[int, int]:
    """Konwertuje wspolrzedne swiata na wspolrzedne chunka."""
    return x >> 4, z >> 4


def get_chunks_for_zone(
    zone: Tuple[Tuple[int, int], Tuple[int, int]]
) -> List[Tuple[int, int]]:
    """Zwraca liste chunkow w obrebie strefy."""
    (x_min, x_max), (z_min, z_max) = zone
    cx_min, cz_min = world_to_chunk(x_min, z_min)
    cx_max, cz_max = world_to_chunk(x_max, z_max)
    chunks = []
    for cx in range(cx_min, cx_max + 1):
        for cz in range(cz_min, cz_max + 1):
            chunks.append((cx, cz))
    return chunks


def get_regions_for_chunks(chunks: List[Tuple[int, int]]) -> set:
    """Zwraca unikalne regiony dla listy chunkow."""
    regions = set()
    for cx, cz in chunks:
        regions.add((cx >> 5, cz >> 5))
    return regions


@dataclass
class CoverageStats:
    zone_name: str
    total_chunks: int = 0
    scanned_chunks: int = 0
    chunks_with_cfm: int = 0
    total_blocks: int = 0
    block_counts: Counter = field(default_factory=Counter)
    te_counts: Counter = field(default_factory=Counter)
    conversion_coverage: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    errors: List[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "zone_name": self.zone_name,
            "total_chunks": self.total_chunks,
            "scanned_chunks": self.scanned_chunks,
            "chunks_with_cfm": self.chunks_with_cfm,
            "total_blocks": self.total_blocks,
            "block_counts": dict(self.block_counts.most_common()),
            "te_counts": dict(self.te_counts.most_common()),
            "conversion_coverage": self.conversion_coverage,
            "errors": self.errors,
        }


def analyze_zone(
    zone_name: str,
    zone_coords: Tuple[Tuple[int, int], Tuple[int, int]],
    world_path: str,
    progress_interval: int = 100,
) -> CoverageStats:
    """Przeskanowuje strefe i zwraca statystyki pokrycia."""
    parser = MrCrayfishChunkParser(world_path)
    converter = MrCrayfishConverter()
    chunks = get_chunks_for_zone(zone_coords)
    stats = CoverageStats(zone_name=zone_name, total_chunks=len(chunks))

    for i, (cx, cz) in enumerate(chunks):
        try:
            result = parser.analyze_chunk(cx, cz)
            stats.scanned_chunks += 1

            if result.has_cfm:
                stats.chunks_with_cfm += 1
                stats.total_blocks += result.block_count

                for block in result.blocks:
                    stats.block_counts[block.block_id] += 1
                    if block.tile_entity:
                        te_id = block.tile_entity.get("id", "UNKNOWN")
                        stats.te_counts[te_id] += 1

                    # Sprawdzamy pokrycie konwersji
                    if block.tile_entity:
                        event = converter.convert_tile_entity(
                            block.tile_entity,
                            block.block_id,
                            block.metadata,
                            block.absolute_pos,
                        )
                    else:
                        event = converter.convert_block(
                            block.block_id,
                            block.metadata,
                            block.absolute_pos,
                        )

                    key = block.block_id
                    if key not in stats.conversion_coverage:
                        stats.conversion_coverage[key] = {
                            "count": 0,
                            "event_type": event.event_type,
                            "target_block": event.target_block_id,
                            "sample_te": block.tile_entity.get("id") if block.tile_entity else None,
                        }
                    stats.conversion_coverage[key]["count"] += 1

        except Exception as e:
            stats.errors.append(f"Chunk {cx},{cz}: {e}")

        if progress_interval > 0 and (i + 1) % progress_interval == 0:
            print(f"  [{zone_name}] Przeskanowano {i+1}/{len(chunks)} chunkow, "
                  f"znaleziono {stats.total_blocks} blokow CFM")

    return stats


def analyze_random_regions(
    world_path: str,
    region_list: List[Tuple[int, int]],
) -> CoverageStats:
    """Przeskanowuje liste regionow (dodatkowe regiony do sprawdzenia)."""
    parser = MrCrayfishChunkParser(world_path)
    converter = MrCrayfishConverter()
    stats = CoverageStats(zone_name="random_regions")

    for region_x, region_z in region_list:
        print(f"  [Random] Region {region_x},{region_z}")
        try:
            results = parser.analyze_region(region_x, region_z)
            for result in results:
                stats.scanned_chunks += 1
                if result.has_cfm:
                    stats.chunks_with_cfm += 1
                    stats.total_blocks += result.block_count
                    for block in result.blocks:
                        stats.block_counts[block.block_id] += 1
                        if block.tile_entity:
                            stats.te_counts[block.tile_entity.get("id", "UNKNOWN")] += 1
        except Exception as e:
            stats.errors.append(f"Region {region_x},{region_z}: {e}")

    return stats


def generate_report(
    zone_stats: List[CoverageStats],
    random_stats: CoverageStats,
    output_dir: Path,
) -> None:
    """Generuje raporty JSON i Markdown."""
    output_dir.mkdir(parents=True, exist_ok=True)

    # Zabezpieczenie: nigdy nie zapisuj do mapa_1710/
    assert "mapa_1710" not in str(output_dir), "BŁĄD: Próba zapisu do mapy źródłowej!"

    # JSON
    json_data = {
        "zones": [s.to_dict() for s in zone_stats],
        "random_regions": random_stats.to_dict(),
        "summary": {
            "total_zones": len(zone_stats),
            "total_scanned_chunks": sum(s.scanned_chunks for s in zone_stats) + random_stats.scanned_chunks,
            "total_cfm_chunks": sum(s.chunks_with_cfm for s in zone_stats) + random_stats.chunks_with_cfm,
            "total_cfm_blocks": sum(s.total_blocks for s in zone_stats) + random_stats.total_blocks,
        },
    }
    with open(output_dir / "mrcrayfish_coverage.json", "w", encoding="utf-8") as f:
        json.dump(json_data, f, indent=2, ensure_ascii=False)

    # Markdown
    lines = [
        "# Raport pokrycia: MrCrayfish Furniture Mod",
        "",
        f"**Data:** 2026-05-19",
        f"**Mod:** MrCrayfish Furniture Mod 1.7.10 -> 1.18.2",
        "",
        "## Podsumowanie",
        "",
        f"- Przeskanowane strefy: {len(zone_stats)}",
        f"- Przeskanowane chunki: {json_data['summary']['total_scanned_chunks']}",
        f"- Chunki z blokami CFM: {json_data['summary']['total_cfm_chunks']}",
        f"- Znalezione bloki/TE CFM: {json_data['summary']['total_cfm_blocks']}",
        "",
        "## Wyniki per strefa",
        "",
    ]

    for stats in zone_stats:
        lines.extend([
            f"### {stats.zone_name}",
            "",
            f"- Chunki do przeskanowania: {stats.total_chunks}",
            f"- Przeskanowane: {stats.scanned_chunks}",
            f"- Z CFM: {stats.chunks_with_cfm}",
            f"- Bloki CFM: {stats.total_blocks}",
            "",
        ])
        if stats.block_counts:
            lines.append("| Blok | Liczba |")
            lines.append("|------|--------|")
            for block_id, count in stats.block_counts.most_common(20):
                lines.append(f"| {block_id} | {count} |")
            lines.append("")
        if stats.errors:
            lines.append(f"**Bledy:** {len(stats.errors)}")
            lines.append("")

    # Random regions
    lines.extend([
        "## Dodatkowe regiony",
        "",
        f"- Przeskanowane chunki: {random_stats.scanned_chunks}",
        f"- Z CFM: {random_stats.chunks_with_cfm}",
        f"- Bloki CFM: {random_stats.total_blocks}",
        "",
    ])
    if random_stats.block_counts:
        lines.append("| Blok | Liczba |")
        lines.append("|------|--------|")
        for block_id, count in random_stats.block_counts.most_common(20):
            lines.append(f"| {block_id} | {count} |")
        lines.append("")

    # Pokrycie konwersji
    all_coverage: Dict[str, Dict[str, Any]] = {}
    for stats in zone_stats + [random_stats]:
        for block_id, info in stats.conversion_coverage.items():
            if block_id not in all_coverage:
                all_coverage[block_id] = dict(info)
            else:
                all_coverage[block_id]["count"] += info["count"]

    lines.extend([
        "## Pokrycie konwersji",
        "",
        f"- Unikalne typy blokow: {len(all_coverage)}",
        "",
        "| Blok 1.7.10 | Liczba | Typ eventu | Blok 1.18.2 |",
        "|-------------|--------|------------|-------------|",
    ])
    for block_id in sorted(all_coverage, key=lambda k: all_coverage[k]["count"], reverse=True):
        info = all_coverage[block_id]
        event_type = info["event_type"]
        target = info["target_block"] or "—"
        lines.append(f"| {block_id} | {info['count']} | {event_type} | {target} |")
    lines.append("")

    # Nieznane TE
    all_te = Counter()
    for stats in zone_stats + [random_stats]:
        all_te.update(stats.te_counts)

    known_te = {
        "cfmOven", "cfmFridge", "cfmCabinet", "cfmFreezer", "cfmBedsideCabinet",
        "cfmMailBox", "cfmComputer", "cfmPrinter", "cfmTV", "cfmStereo",
        "cfmPresent", "cfmBin", "cfmWallCabinet", "cfmBath", "cfmBasin",
        "cfmShowerHead", "cfmCookieJar", "cfmPlate", "cfmCouch", "cfmToaster",
        "cfmChoppingBoard", "cfmBlender", "cfmMicrowave", "cfmWashingMachine",
        "cfmDishwasher", "cfmCabinetKitchen", "cfmCounterSink", "cfmCup",
    }
    unknown_te = [te for te in all_te if te not in known_te]

    if unknown_te:
        lines.extend([
            "## Nieznane TileEntity ID",
            "",
            "Nastepujace TE ID zostaly znalezione na mapie ale nie sa obslugiwane w konwerterze:",
            "",
        ])
        for te in unknown_te:
            lines.append(f"- `{te}` (liczba: {all_te[te]})")
        lines.append("")
    else:
        lines.extend([
            "## Nieznane TileEntity ID",
            "",
            "Brak — wszystkie znalezione TE ID sa obslugiwane. ✅",
            "",
        ])

    with open(output_dir / "mrcrayfish_coverage.md", "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    print(f"\nRaporty zapisane do: {output_dir}")
    print(f"  - {output_dir / 'mrcrayfish_coverage.json'}")
    print(f"  - {output_dir / 'mrcrayfish_coverage.md'}")


def main():
    world_path = "mapa_1710"
    output_dir = Path("output/mrcrayfish_task4")

    # Zabezpieczenie
    assert "mapa_1710" not in str(output_dir.resolve()), "BŁĄD: output_dir wskazuje na mape zrodlowa!"

    zones = load_zone_coords()
    zone_stats: List[CoverageStats] = []

    print("=" * 60)
    print("Analiza pokrycia: MrCrayfish Furniture Mod")
    print("=" * 60)

    for zone_name, zone_coords in zones.items():
        print(f"\n--- Strefa: {zone_name} ---")
        chunks = get_chunks_for_zone(zone_coords)
        regions = get_regions_for_chunks(chunks)
        print(f"  Zakres chunkow: {len(chunks)} chunkow w {len(regions)} regionach")
        stats = analyze_zone(zone_name, zone_coords, world_path)
        zone_stats.append(stats)
        print(f"  Zakonczono: {stats.chunks_with_cfm} chunkow z CFM, {stats.total_blocks} blokow")

    # Dodatkowe regiony
    print("\n--- Dodatkowe regiony ---")
    random_regions = [
        (0, 0),    # spawn
        (1, 1),    # okolice spawnu
        (-1, -1),  # okolice spawnu
        (10, 10),  # dalsze obszary
        (-10, -10),
    ]
    random_stats = analyze_random_regions(world_path, random_regions)
    print(f"  Zakonczono: {random_stats.chunks_with_cfm} chunkow z CFM, {random_stats.total_blocks} blokow")

    # Generowanie raportow
    print("\n--- Generowanie raportow ---")
    generate_report(zone_stats, random_stats, output_dir)

    print("\n" + "=" * 60)
    print("Analiza zakonczona.")
    print("=" * 60)


if __name__ == "__main__":
    main()
