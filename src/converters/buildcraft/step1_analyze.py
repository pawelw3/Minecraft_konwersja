"""
BuildCraft - Krok 1: Wypisanie wszystkich bloków i Tile Entities moda.

Skanuje mapę 1.7.10 w poszukiwaniu bloków i TE BuildCraft,
generuje raport z rozkładem typów, pozycjami i statystykami per strefa.
NIE MODYFIKUJE mapa_1710/ — tylko odczyt.

Optymalizacja: używa AnvilParser bezpośrednio (szybkie) zamiast
ModBlockExtractor (wolne przy dużej liczbie regionów).
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
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from minecraft_map_parser import AnvilParser


PROJECT_ROOT = Path(__file__).resolve().parents[3]
MAP_ROOT = PROJECT_ROOT / "mapa_1710"
REGION_DIR = MAP_ROOT / "region"
STREFY_DIR = PROJECT_ROOT / "strefy"
OUTPUT_DIR = PROJECT_ROOT / "output" / "buildcraft_scan"

# BuildCraft 1.7.10 rezerwuje numeryczne ID zazwyczaj w zakresie 512-768
# (heurystyka z mod_block_extractor.py). W rzeczywistości może być inaczej,
# ale na podstawie TE możemy zweryfikować faktyczne ID.
BC_BLOCK_ID_RANGES = [(512, 768)]


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

    min_rx, min_rz = world_to_region(min_x, min_z)
    max_rx, max_rz = world_to_region(max_x, max_z)

    regions = set()
    for rx in range(min_rx, max_rx + 1):
        for rz in range(min_rz, max_rz + 1):
            regions.add((rx, rz))
    return regions


def region_file_exists(rx: int, rz: int) -> bool:
    return (REGION_DIR / f"r.{rx}.{rz}.mca").exists()


def is_buildcraft_te(te_id: str) -> bool:
    """Sprawdza czy TE id należy do BuildCraft."""
    return "buildcraft" in te_id.lower()


def is_likely_bc_block(block_id: int) -> bool:
    """Heurystyka: czy numeryczne ID bloku może należeć do BuildCraft."""
    for lo, hi in BC_BLOCK_ID_RANGES:
        if lo <= block_id < hi:
            return True
    return False


def scan_region(rx: int, rz: int) -> dict[str, Any]:
    """Skanuje pojedynczy region w poszukiwaniu TE i bloków BuildCraft."""
    region_path = REGION_DIR / f"r.{rx}.{rz}.mca"
    if not region_path.exists():
        return {"found": False, "te_counts": Counter(), "block_counts": Counter(), "te_positions": {}}

    try:
        parser = AnvilParser(str(region_path))
    except Exception as e:
        return {"found": False, "error": str(e), "te_counts": Counter(), "block_counts": Counter(), "te_positions": {}}

    te_counts = Counter()
    te_positions: dict[str, list[tuple[int, int, int]]] = defaultdict(list)
    block_counts = Counter()
    block_meta: dict[int, Counter] = defaultdict(Counter)

    for cz in range(32):
        for cx in range(32):
            try:
                chunk = parser.get_chunk(cx, cz)
            except Exception:
                continue
            if not chunk:
                continue

            chunk_has_bc = False
            chunk_tes = []

            # Faza 1: Tile Entities
            for te in chunk.get_tile_entities():
                te_id = te.get("id", "")
                if is_buildcraft_te(te_id):
                    chunk_has_bc = True
                    te_counts[te_id] += 1
                    x = te.get("x", 0)
                    y = te.get("y", 0)
                    z = te.get("z", 0)
                    te_positions[te_id].append((x, y, z))
                    chunk_tes.append((x, y, z))

            if not chunk_has_bc:
                # Nawet jeśli nie ma TE, sprawdźmy czy są bloki BC (rzadkie, ale możliwe)
                # Pomijamy dla wydajności; bloki dekoracyjne bez TE są mało istotne
                continue

            # Faza 2: Bloki w chunku (tylko jeśli są tam TE BuildCraft)
            try:
                blocks = chunk.get_blocks_and_metadata_at_positions()
            except Exception:
                continue

            # Zbierzmy bloki na pozycjach TE i sąsiednich (rury BC to TE,
            # ale np. Quarry, Pump, Tank to TE + blok; niektóre bloki mogą nie mieć TE)
            bc_positions = set(chunk_tes)

            for (lx, y, lz), (block_id, meta) in blocks.items():
                if is_likely_bc_block(block_id):
                    block_counts[block_id] += 1
                    block_meta[block_id][meta] += 1

    return {
        "found": True,
        "te_counts": te_counts,
        "te_positions": dict(te_positions),
        "block_counts": block_counts,
        "block_meta": {bid: dict(meta) for bid, meta in block_meta.items()},
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

    # Dodaj losowe regiony (spawn + okolice + przykładowe dalekie)
    extra_regions = {(0, 0), (1, 1), (-1, -1), (10, 10), (-10, -10)}
    all_regions.update(extra_regions)

    # Filtruj tylko istniejące regiony
    existing_regions = [(rx, rz) for rx, rz in all_regions if region_file_exists(rx, rz)]
    missing_regions = [(rx, rz) for rx, rz in all_regions if not region_file_exists(rx, rz)]

    print(f"\nŁącznie regionów do przeskanowania: {len(existing_regions)}")
    if missing_regions:
        print(f"Brakujących regionów: {len(missing_regions)} {missing_regions[:10]}...")

    total_te_counts = Counter()
    total_block_counts = Counter()
    total_block_meta: dict[int, Counter] = defaultdict(Counter)
    zone_results: dict[str, dict[str, Any]] = {}

    for idx, (rx, rz) in enumerate(existing_regions):
        if idx % 5 == 0 and idx > 0:
            print(f"  ...przetworzono {idx}/{len(existing_regions)} regionów")

        result = scan_region(rx, rz)
        if not result.get("found"):
            continue

        total_te_counts.update(result["te_counts"])
        total_block_counts.update(result["block_counts"])
        for bid, meta in result.get("block_meta", {}).items():
            for m, c in meta.items():
                total_block_meta[bid][m] += c

    # Per strefa
    for name, regs in zone_regions.items():
        zone_te = Counter()
        zone_te_positions: dict[str, list] = defaultdict(list)
        for rx, rz in regs:
            if not region_file_exists(rx, rz):
                continue
            result = scan_region(rx, rz)
            if result.get("found"):
                zone_te.update(result["te_counts"])
                for te_id, positions in result.get("te_positions", {}).items():
                    zone_te_positions[te_id].extend(positions)
        zone_results[name] = {
            "te_counts": dict(zone_te),
            "te_positions": dict(zone_te_positions),
        }

    # Extra regiony
    extra_te = Counter()
    for rx, rz in extra_regions:
        if not region_file_exists(rx, rz):
            continue
        result = scan_region(rx, rz)
        if result.get("found"):
            extra_te.update(result["te_counts"])
    zone_results["_extra_regions"] = {"te_counts": dict(extra_te)}
    total_te_counts.update(extra_te)

    print(f"\n{'=' * 60}")
    print("PODSUMOWANIE BUILDRAFT NA MAPIE")
    print(f"{'=' * 60}")
    print(f"Łącznie znalezionych TileEntities BuildCraft: {sum(total_te_counts.values())}")
    print(f"Unikalnych typów TE: {len(total_te_counts)}")
    print(f"\nTop typy TE:")
    for te_id, count in total_te_counts.most_common(20):
        print(f"  {te_id}: {count}")

    print(f"\nŁącznie znalezionych bloków BuildCraft (bez TE): {sum(total_block_counts.values())}")
    print(f"Unikalnych ID bloków: {len(total_block_counts)}")
    print(f"\nTop ID bloków:")
    for block_id, count in total_block_counts.most_common(20):
        print(f"  ID {block_id}: {count}")

    if total_block_meta:
        print(f"\nMetadane dla top bloków:")
        for block_id, count in total_block_counts.most_common(5):
            meta_counts = dict(total_block_meta[block_id])
            print(f"  ID {block_id}: {meta_counts}")

    # Zapisz wyniki
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    output_json = OUTPUT_DIR / "buildcraft_step1_analysis.json"
    with open(output_json, "w") as f:
        json.dump({
            "zones": zone_results,
            "total_te_counts": dict(total_te_counts),
            "total_block_counts": dict(total_block_counts),
            "block_meta": {bid: dict(meta) for bid, meta in total_block_meta.items()},
        }, f, indent=2, default=str)
    print(f"\nZapisano wyniki JSON do: {output_json}")

    # Generuj raport Markdown
    output_md = OUTPUT_DIR / "buildcraft_step1_report.md"
    with open(output_md, "w") as f:
        f.write("# BuildCraft – Krok 1: Analiza bloków i Tile Entities\n\n")
        f.write(f"**Data generacji:** {__import__('datetime').datetime.now().isoformat()}\n\n")
        f.write("## Podsumowanie ogólne\n\n")
        f.write(f"- **Łącznie TileEntities:** {sum(total_te_counts.values())}\n")
        f.write(f"- **Unikalne typy TE:** {len(total_te_counts)}\n")
        f.write(f"- **Łącznie bloki (bez TE):** {sum(total_block_counts.values())}\n")
        f.write(f"- **Unikalne ID bloków:** {len(total_block_counts)}\n\n")

        f.write("## Rozkład Tile Entities\n\n")
        f.write("| Tile Entity ID | Liczba |\n")
        f.write("|----------------|--------|\n")
        for te_id, count in total_te_counts.most_common():
            f.write(f"| `{te_id}` | {count} |\n")

        f.write("\n## Rozkład bloków (numeryczne ID)\n\n")
        f.write("| Block ID | Liczba |\n")
        f.write("|----------|--------|\n")
        for block_id, count in total_block_counts.most_common():
            f.write(f"| {block_id} | {count} |\n")

        f.write("\n## Wyniki per strefa\n\n")
        for name, data in zone_results.items():
            te_sum = sum(data.get("te_counts", {}).values())
            f.write(f"### {name}\n")
            f.write(f"- TE: {te_sum}\n")
            te_breakdown = data.get("te_counts", {})
            if te_breakdown:
                f.write("- Rozkład TE:\n")
                for te_id, cnt in Counter(te_breakdown).most_common():
                    f.write(f"  - `{te_id}`: {cnt}\n")
            f.write("\n")

    print(f"Zapisano raport MD do: {output_md}")


if __name__ == "__main__":
    main()
