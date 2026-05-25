"""Skaner mapy IC2 - Zadanie 4.

Znajduje wszystkie bloki/TE IC2 na mapie 1.7.10 i sprawdza pokrycie mapowań.
NIE MODYFIKUJE mapa_1710/ — tylko odczyt.
"""

from __future__ import annotations

import json
import math
import os
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

# Upewnij się że src/ jest na path
sys.path.insert(0, str(Path(__file__).resolve().parents[3]))

from minecraft_map_parser.anvil_parser import AnvilParser
from converters.ic2.mappings.block_mappings import is_ic2_te_id


PROJECT_ROOT = Path(__file__).resolve().parents[3]
MAP_ROOT = PROJECT_ROOT / "mapa_1710"
REGION_DIR = MAP_ROOT / "region"
STREFY_DIR = PROJECT_ROOT / "strefy"
OUTPUT_DIR = PROJECT_ROOT / "output" / "ic2_scan"

# Wzorce IC2 TileEntity ID (odkryte z mapy, nie zgadywane)
# Na razie używamy szerokiego wzorca, potem zwężymy do rzeczywistych ID.
IC2_TE_PATTERNS = ["TileEntity", "IC2TE"]

# Block ID IC2 w formacie string (dla mapowań bloków bez TE)
IC2_BLOCK_PATTERNS = ["IC2:"]


def load_zones() -> dict[str, dict[str, Any]]:
    """Wczytuje definicje stref z coords.json."""
    zones = {}
    for zone_dir in sorted(STREFY_DIR.iterdir()):
        if zone_dir.is_dir():
            coords_file = zone_dir / "coords.json"
            if coords_file.exists():
                with open(coords_file) as f:
                    zones[zone_dir.name] = json.load(f)
    return zones


def world_to_region(wx: int, wz: int) -> tuple[int, int]:
    """Konwertuje współrzędne świata na współrzędne regionu."""
    cx = math.floor(wx / 16)
    cz = math.floor(wz / 16)
    rx = math.floor(cx / 32)
    rz = math.floor(cz / 32)
    return rx, rz


def get_regions_for_zone(zone: dict[str, Any]) -> set[tuple[int, int]]:
    """Zwraca zbiór regionów (rx, rz) pokrywających strefę."""
    coords = zone.get("minecraftCoordinates", [])
    if not coords:
        return set()

    xs = [c["x"] for c in coords]
    zs = [c["z"] for c in coords]
    min_x, max_x = min(xs), max(xs)
    min_z, max_z = min(zs), max(zs)

    # Rozszerzamy o margines chunków (1 region = 32 chunków = 512 bloków)
    min_rx, min_rz = world_to_region(min_x, min_z)
    max_rx, max_rz = world_to_region(max_x, max_z)

    regions = set()
    for rx in range(min_rx, max_rx + 1):
        for rz in range(min_rz, max_rz + 1):
            regions.add((rx, rz))
    return regions


def region_file_exists(rx: int, rz: int) -> bool:
    return (REGION_DIR / f"r.{rx}.{rz}.mca").exists()


def is_ic2_te(te_id: str) -> bool:
    """Sprawdza czy TE id należy do IC2.

    IC2 experimental 2.2.827 zapisuje realne TE zwykle jako krótkie nazwy
    rejestracyjne Forge, np. "Macerator", "Cable", "TECrop".
    """
    return is_ic2_te_id(te_id)


def scan_region(rx: int, rz: int) -> dict[str, Any]:
    """Skanuje pojedynczy region w poszukiwaniu bloków IC2."""
    region_path = REGION_DIR / f"r.{rx}.{rz}.mca"
    if not region_path.exists():
        return {"found": False, "te_counts": Counter(), "block_counts": Counter()}

    try:
        parser = AnvilParser(str(region_path))
    except Exception as e:
        return {"found": False, "error": str(e), "te_counts": Counter(), "block_counts": Counter()}

    te_counts = Counter()
    block_counts = Counter()
    te_positions: dict[str, list[tuple[int, int, int]]] = defaultdict(list)

    for cz in range(32):
        for cx in range(32):
            try:
                chunk = parser.get_chunk(cx, cz)
            except Exception:
                continue
            if not chunk:
                continue

            # TileEntities
            for te in chunk.get_tile_entities():
                te_id = te.get("id", "")
                if is_ic2_te(te_id):
                    te_counts[te_id] += 1
                    x = te.get("x", 0)
                    y = te.get("y", 0)
                    z = te.get("z", 0)
                    te_positions[te_id].append((x, y, z))

            # Bloki (bez TE) - w 1.7.10 bloki są w Sections jako byte array
            # To jest uproszczone - sprawdzamy tylko czy są bloki IC2
            # Pełna analiza bloków wymagałaby dekodowania palety, co jest skomplikowane
            # W 1.7.10 bloki bez TE nie mają string ID w NBT chunka (numeryczne ID)
            # Pomijamy to na razie, skupiamy się na TE.

    return {
        "found": True,
        "te_counts": te_counts,
        "te_positions": dict(te_positions),
    }


def main():
    zones = load_zones()
    print(f"Wczytano strefy: {list(zones.keys())}")

    all_regions: set[tuple[int, int]] = set()
    zone_regions: dict[str, set[tuple[int, int]]] = {}

    for name, zone in zones.items():
        regs = get_regions_for_zone(zone)
        zone_regions[name] = regs
        all_regions.update(regs)
        print(f"  {name}: {len(regs)} regionów")

    # Dodaj losowe regiony (spawn + okolice)
    extra_regions = {(0, 0), (1, 1), (-1, -1), (10, 10), (-10, -10)}
    all_regions.update(extra_regions)

    # Filtruj tylko istniejące regiony
    existing_regions = [(rx, rz) for rx, rz in all_regions if region_file_exists(rx, rz)]
    missing_regions = [(rx, rz) for rx, rz in all_regions if not region_file_exists(rx, rz)]

    print(f"\nŁącznie regionów do przeskanowania: {len(existing_regions)}")
    if missing_regions:
        print(f"Brakujących regionów: {len(missing_regions)} {missing_regions[:10]}...")

    total_te_counts = Counter()
    zone_results: dict[str, dict[str, Any]] = {}

    for name, regs in zone_regions.items():
        zone_te = Counter()
        zone_positions: dict[str, list] = defaultdict(list)
        for rx, rz in regs:
            if not region_file_exists(rx, rz):
                continue
            result = scan_region(rx, rz)
            if result.get("found"):
                zone_te.update(result["te_counts"])
                for te_id, positions in result.get("te_positions", {}).items():
                    zone_positions[te_id].extend(positions)
        zone_results[name] = {"te_counts": dict(zone_te), "te_positions": dict(zone_positions)}
        total_te_counts.update(zone_te)
        print(f"  {name}: {sum(zone_te.values())} TE")

    # Extra regiony (bez strefy)
    extra_te = Counter()
    for rx, rz in extra_regions:
        if not region_file_exists(rx, rz):
            continue
        result = scan_region(rx, rz)
        if result.get("found"):
            extra_te.update(result["te_counts"])
    zone_results["_extra_regions"] = {"te_counts": dict(extra_te)}
    total_te_counts.update(extra_te)

    print(f"\n=== PODSUMOWANIE IC2 NA MAPIE ===")
    print(f"Łącznie znalezionych TileEntities IC2: {sum(total_te_counts.values())}")
    print(f"Unikalnych typów TE: {len(total_te_counts)}")
    print("\nTop 20 typów TE:")
    for te_id, count in total_te_counts.most_common(20):
        print(f"  {te_id}: {count}")

    # Sprawdź pokrycie mapowań
    from converters.ic2.mappings.block_mappings import get_mapping_for_te_id

    covered = 0
    uncovered = 0
    uncovered_ids = []
    for te_id, count in total_te_counts.items():
        if get_mapping_for_te_id(te_id):
            covered += count
        else:
            uncovered += count
            uncovered_ids.append((te_id, count))

    print(f"\n=== POKRYCIE MAPOWAŃ ===")
    print(f"Pokryte (znane w block_inventory): {covered} ({covered/(covered+uncovered)*100:.1f}%)")
    print(f"Niepokryte (nieznane TE ID): {uncovered} ({uncovered/(covered+uncovered)*100:.1f}%)")
    if uncovered_ids:
        print("Nieznane TE ID:")
        for te_id, count in sorted(uncovered_ids, key=lambda x: -x[1])[:20]:
            print(f"  {te_id}: {count}")

    # Zapisz wyniki
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    output_file = OUTPUT_DIR / "ic2_map_analysis.json"
    with open(output_file, "w") as f:
        json.dump({
            "zones": zone_results,
            "total_te_counts": dict(total_te_counts),
            "coverage": {
                "covered": covered,
                "uncovered": uncovered,
                "uncovered_ids": uncovered_ids,
            },
        }, f, indent=2, default=str)
    print(f"\nZapisano wyniki do: {output_file}")


if __name__ == "__main__":
    main()
