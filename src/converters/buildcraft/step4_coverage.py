"""
BuildCraft - Krok 4: Sprawdzenie pokrycia konwersji dla stref głównej mapy.

Wczytuje wyniki z kroku 1 (pozycje TE), odczytuje pełne NBT z mapy 1.7.10,
przepuszcza każdy TE przez router (konwerter BuildCraft) i generuje raport
pokrycia: ile skonwertowanych, ile usuniętych, ile błędów.

NIE MODYFIKUJE mapa_1710/ — tylko odczyt.
"""

from __future__ import annotations

import json
import math
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from minecraft_map_parser import AnvilParser
from converters.router import convert_te_to_events


PROJECT_ROOT = Path(__file__).resolve().parents[3]
MAP_ROOT = PROJECT_ROOT / "mapa_1710"
REGION_DIR = MAP_ROOT / "region"
STEP1_JSON = PROJECT_ROOT / "output" / "buildcraft_scan" / "buildcraft_step1_analysis.json"
OUTPUT_DIR = PROJECT_ROOT / "output" / "buildcraft_scan"


def load_step1_data() -> dict[str, Any]:
    with open(STEP1_JSON) as f:
        return json.load(f)


def world_to_region(wx: int, wz: int) -> tuple[int, int]:
    cx = math.floor(wx / 16)
    cz = math.floor(wz / 16)
    rx = math.floor(cx / 32)
    rz = math.floor(cz / 32)
    return rx, rz


def get_te_nbt_from_map(x: int, y: int, z: int) -> dict[str, Any] | None:
    """Odczytuje pełne NBT TileEntity z mapy na danej pozycji."""
    rx, rz = world_to_region(x, z)
    cx = (x // 16) % 32
    cz = (z // 16) % 32
    region_path = REGION_DIR / f"r.{rx}.{rz}.mca"
    if not region_path.exists():
        return None
    try:
        parser = AnvilParser(str(region_path))
        chunk = parser.get_chunk(cx, cz)
        if not chunk:
            return None
        for te in chunk.get_tile_entities():
            if te.get("x") == x and te.get("y") == y and te.get("z") == z:
                return te
    except Exception:
        return None
    return None


def analyze_zone(name: str, zone_data: dict[str, Any]) -> dict[str, Any]:
    """Analizuje pokrycie konwersji dla jednej strefy."""
    te_counts = zone_data.get("te_counts", {})
    te_positions = zone_data.get("te_positions", {})

    results = {
        "total_te": 0,
        "converted": 0,
        "removed": 0,
        "errors": 0,
        "per_te_type": {},
        "events": [],
        "error_details": [],
    }

    for te_id, positions in te_positions.items():
        type_stats = {
            "count": len(positions),
            "converted": 0,
            "removed": 0,
            "errors": 0,
        }
        results["total_te"] += len(positions)

        for pos in positions:
            x, y, z = pos
            nbt = get_te_nbt_from_map(x, y, z)
            if nbt is None:
                type_stats["errors"] += 1
                results["errors"] += 1
                results["error_details"].append({
                    "te_id": te_id,
                    "pos": pos,
                    "reason": "NBT not found on map",
                })
                continue

            events = convert_te_to_events(
                te_nbt=nbt,
                block_numeric_id=0,
                metadata=0,
                global_pos=(x, y, z),
            )

            if not events:
                type_stats["errors"] += 1
                results["errors"] += 1
                results["error_details"].append({
                    "te_id": te_id,
                    "pos": pos,
                    "reason": "Router returned empty events",
                })
                continue

            # Analiza eventów
            for event in events:
                block = event.get("block", "")
                op = event.get("op", "")
                if block == "minecraft:air" and op == "set_block":
                    type_stats["removed"] += 1
                    results["removed"] += 1
                elif block and block != "minecraft:air":
                    type_stats["converted"] += 1
                    results["converted"] += 1
                else:
                    type_stats["errors"] += 1
                    results["errors"] += 1

                results["events"].append({
                    "te_id": te_id,
                    "pos": pos,
                    "event": event,
                })

        results["per_te_type"][te_id] = type_stats

    return results


def main():
    if not STEP1_JSON.exists():
        print(f"Brak pliku kroku 1: {STEP1_JSON}")
        print("Najpierw uruchom: python src/converters/buildcraft/step1_analyze.py")
        return

    data = load_step1_data()
    zones = data.get("zones", {})

    print(f"Wczytano strefy: {list(zones.keys())}")

    all_results: dict[str, Any] = {}
    total_stats = Counter()

    for name, zone_data in zones.items():
        if name.startswith("_"):
            continue
        print(f"\nAnalizowanie strefy: {name} ...")
        result = analyze_zone(name, zone_data)
        all_results[name] = result
        total_stats["total"] += result["total_te"]
        total_stats["converted"] += result["converted"]
        total_stats["removed"] += result["removed"]
        total_stats["errors"] += result["errors"]
        print(f"  TE: {result['total_te']}, CONVERT: {result['converted']}, REMOVE: {result['removed']}, ERRORS: {result['errors']}")

    # Podsumowanie ogólne
    print(f"\n{'=' * 60}")
    print("PODSUMOWANIE POKRYCIA KONWERSJI BUILDRAFT")
    print(f"{'=' * 60}")
    print(f"Łącznie TileEntities: {total_stats['total']}")
    print(f"Skonwertowane (CONVERT): {total_stats['converted']} ({total_stats['converted']/total_stats['total']*100:.1f}%)")
    print(f"Usunięte (REMOVE): {total_stats['removed']} ({total_stats['removed']/total_stats['total']*100:.1f}%)")
    print(f"Błędy: {total_stats['errors']} ({total_stats['errors']/total_stats['total']*100:.1f}%)")

    # Zapisz wyniki JSON
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    output_json = OUTPUT_DIR / "buildcraft_step4_coverage.json"
    with open(output_json, "w") as f:
        json.dump({
            "zones": all_results,
            "total_stats": dict(total_stats),
        }, f, indent=2, default=str)
    print(f"\nZapisano wyniki JSON do: {output_json}")

    # Generuj raport Markdown
    output_md = OUTPUT_DIR / "buildcraft_step4_report.md"
    with open(output_md, "w") as f:
        f.write("# BuildCraft – Krok 4: Raport pokrycia konwersji\n\n")
        f.write(f"**Data generacji:** {__import__('datetime').datetime.now().isoformat()}\n\n")
        f.write("## Podsumowanie ogólne\n\n")
        f.write(f"- **Łącznie TileEntities:** {total_stats['total']}\n")
        f.write(f"- **Skonwertowane (CONVERT):** {total_stats['converted']} ({total_stats['converted']/total_stats['total']*100:.1f}%)\n")
        f.write(f"- **Usunięte (REMOVE):** {total_stats['removed']} ({total_stats['removed']/total_stats['total']*100:.1f}%)\n")
        f.write(f"- **Błędy:** {total_stats['errors']} ({total_stats['errors']/total_stats['total']*100:.1f}%)\n\n")

        f.write("## Wyniki per strefa\n\n")
        f.write("| Strefa | TE | CONVERT | REMOVE | Błędy |\n")
        f.write("|--------|-----|---------|--------|-------|\n")
        for name, result in all_results.items():
            f.write(f"| {name} | {result['total_te']} | {result['converted']} | {result['removed']} | {result['errors']} |\n")

        f.write("\n## Szczegóły per typ TE\n\n")
        for name, result in all_results.items():
            f.write(f"### {name}\n\n")
            for te_id, stats in result["per_te_type"].items():
                f.write(f"- `{te_id}`: {stats['count']} szt. (CONVERT: {stats['converted']}, REMOVE: {stats['removed']}, ERR: {stats['errors']})\n")
            f.write("\n")

        if total_stats['errors'] > 0:
            f.write("## Błędy\n\n")
            for name, result in all_results.items():
                for err in result.get("error_details", [])[:10]:
                    f.write(f"- `{err['te_id']}` @ {err['pos']}: {err['reason']}\n")

    print(f"Zapisano raport MD do: {output_md}")


if __name__ == "__main__":
    main()
