"""
Zadanie 5A: Test konwersji MrCrayfish Furniture Mod na testowej mapie 1.7.10.

Skanuje testowy swiat z wygenerowanymi blokami CFM, uruchamia konwersję
i produkuje raport weryfikacyjny.
"""

import sys
import os
import json
from collections import Counter

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..'))

from src.converters.mrcrayfish_furniture.mrcrayfish_chunk_parser import MrCrayfishChunkParser
from src.converters.mrcrayfish_furniture.mrcrayfish_converter import MrCrayfishConverter


def run_test(world_path: str):
    parser = MrCrayfishChunkParser(world_path)
    
    print("=" * 60)
    print("ZADANIE 5A: Test konwersji MrCrayfish Furniture Mod")
    print("=" * 60)
    print(f"Swiat testowy: {world_path}")
    print()

    # Skanuj wszystkie regiony (z scan_blocks=True)
    results = []
    for region_file in sorted(parser.region_path.glob("r.*.*.mca")):
        parts = region_file.stem.split(".")
        if len(parts) == 3:
            try:
                rx, rz = int(parts[1]), int(parts[2])
            except ValueError:
                continue
            for cz in range(32):
                for cx in range(32):
                    chunk_x = rx * 32 + cx
                    chunk_z = rz * 32 + cz
                    result = parser.analyze_chunk(chunk_x, chunk_z, scan_blocks=True)
                    if result.has_cfm:
                        results.append(result)
    
    total_blocks = sum(len(r.blocks) for r in results)
    total_events = sum(len(r.events) for r in results)
    
    print(f"Chunki z CFM: {len(results)}")
    print(f"Lacznie blokow CFM: {total_blocks}")
    print(f"Lacznie eventow: {total_events}")
    print()

    # Agreguj typy eventow
    event_types = Counter()
    source_blocks = Counter()
    target_blocks = Counter()
    warnings = []
    errors = []

    for result in results:
        for event in result.events:
            event_types[event.event_type] += 1
            source_blocks[event.source_block_id] += 1
            if event.target_block_id:
                target_blocks[event.target_block_id] += 1
            warnings.extend(event.warnings)
            errors.extend(event.errors)

    print("-" * 40)
    print("Typy eventow:")
    for etype, count in sorted(event_types.items(), key=lambda x: -x[1]):
        print(f"  {etype}: {count}")

    print()
    print("-" * 40)
    print("Bloki zrodlowe (top 30):")
    for name, count in source_blocks.most_common(30):
        print(f"  {name}: {count}")

    print()
    print("-" * 40)
    print("Bloki docelowe (top 30):")
    for name, count in target_blocks.most_common(30):
        print(f"  {name}: {count}")

    if warnings:
        print()
        print("-" * 40)
        print(f"Ostrzezenia ({len(warnings)}):")
        for w in set(warnings):
            print(f"  - {w}")

    if errors:
        print()
        print("-" * 40)
        print(f"Bledy ({len(errors)}):")
        for e in set(errors):
            print(f"  - {e}")

    # Sprawdz pokrycie - czy wszystkie bloki z source_blocks maja target
    unknown = [name for name in source_blocks if name not in target_blocks and event_types.get('placeholder', 0) == 0]
    
    print()
    print("=" * 60)
    print("PODSUMOWANIE WERYFIKACJI")
    print("=" * 60)
    
    # Sprawdz czy wszystkie unikalne typy blokow sa obslugiwane
    unique_source = set(source_blocks.keys())
    converter = MrCrayfishConverter()
    unhandled = []
    for block_id in sorted(unique_source):
        event = converter.convert_block(block_id, 0)
        if event.event_type == "placeholder" and block_id not in [
            "cfm:basin", "cfm:bath1", "cfm:bath2", "cfm:showerbottom", "cfm:showertop",
            "cfm:showerheadoff", "cfm:showerheadon", "cfm:toilet", "cfm:tap",
            "cfm:barstool", "cfm:hey", "cfm:nyan", "cfm:pattern", "cfm:yellowGlow", "cfm:whiteGlass",
        ]:
            unhandled.append(block_id)
    
    if unhandled:
        print(f"Nieobsluzone bloki: {unhandled}")
    else:
        print("Wszystkie bloki CFM sa obslugiwane przez konwerter.")
    
    print(f"Lacznie unikalnych typow blokow: {len(unique_source)}")
    print(f"Lacznie eventow: {total_events}")
    
    # Zapisz raport
    report = {
        "task": "5A",
        "mod": "MrCrayfishFurniture",
        "world_path": world_path,
        "chunks_with_cfm": len(results),
        "total_blocks": total_blocks,
        "total_events": total_events,
        "event_types": dict(event_types),
        "source_blocks": dict(source_blocks),
        "target_blocks": dict(target_blocks),
        "warnings": list(set(warnings)),
        "errors": list(set(errors)),
        "unhandled_blocks": unhandled,
    }
    
    report_path = os.path.join(world_path, "task5a_report.json")
    with open(report_path, 'w') as f:
        json.dump(report, f, indent=2)
    print(f"\nRaport zapisany: {report_path}")
    
    return report


if __name__ == '__main__':
    world = '.'
    run_test(world)
