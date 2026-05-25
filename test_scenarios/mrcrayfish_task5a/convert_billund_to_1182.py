"""
Konwersja strefy Billund z prawdziwej mapy 1.7.10 -> 1.18.2.

Uzywa MrCrayfishChunkParser ze skanowaniem sekcji blokow (scan_blocks=True)
oraz item_id_resolver do konwersji numerycznych ID przedmiotow.
"""

import sys
import os
import json
import subprocess

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..'))

from src.converters.mrcrayfish_furniture.mrcrayfish_chunk_parser import MrCrayfishChunkParser


def main():
    world_1710 = os.path.abspath(os.path.join(os.getcwd(), '..', '..', 'mapa_1710'))
    world_1182 = './target_billund_1182'
    worker_jar = '../../jvm/worker/build/libs/mc-editkit-worker-1.0-SNAPSHOT.jar'
    level_dat_path = os.path.abspath(os.path.join(os.getcwd(), '..', '..', 'mapa_1710', 'level.dat'))

    # Wspolrzedne billund: x=280..602, z=-364..-81
    cx_min, cx_max = 280 // 16, 602 // 16
    cz_min, cz_max = -364 // 16, -81 // 16

    print("=" * 60)
    print("KONWERSJA BILLUND: 1.7.10 -> 1.18.2")
    print("=" * 60)
    print(f"Zrodlo: {world_1710}")
    print(f"Docel: {world_1182}")
    print(f"Zakres chunkow: cx={cx_min}..{cx_max}, cz={cz_min}..{cz_max}")
    print()

    # 1. Skanuj
    parser = MrCrayfishChunkParser(world_1710, level_dat_path=level_dat_path)
    results = []
    for cz in range(cz_min, cz_max + 1):
        for cx in range(cx_min, cx_max + 1):
            result = parser.analyze_chunk(cx, cz, scan_blocks=True)
            if result.has_cfm:
                results.append(result)

    total_blocks = sum(len(r.blocks) for r in results)
    print(f"Znaleziono chunkow z CFM: {len(results)}")
    print(f"Lacznie blokow CFM: {total_blocks}")
    print()

    # 2. Generuj eventy
    events = []
    for result in results:
        for event in result.events:
            e = event.to_set_block_event()
            if e:
                events.append(e)
        for event in result.events:
            if event.event_type == 'remove' and event.position:
                events.append({
                    "op": "remove_block",
                    "pos": list(event.position),
                })

    events_path = os.path.join(world_1182, 'events.json')
    os.makedirs(world_1182, exist_ok=True)
    with open(events_path, 'w') as f:
        json.dump({"events": events}, f, indent=2)

    print(f"Wygenerowano {len(events)} eventow -> {events_path}")

    # 3. Utworz pusty swiat 1.18.2
    os.makedirs(os.path.join(world_1182, 'region'), exist_ok=True)

    # 4. Aplikuj eventy
    cmd = [
        'java', '-jar', worker_jar,
        '--apply-events', events_path,
        '--target-world', world_1182,
    ]
    print(f"Uruchamianie: {' '.join(cmd)}")
    result = subprocess.run(cmd, capture_output=True, text=True)
    print(result.stdout)
    if result.stderr:
        print("STDERR:", result.stderr)

    # 5. Raport
    report = {
        "zone": "billund",
        "chunks_with_cfm": len(results),
        "total_blocks": total_blocks,
        "total_events": len(events),
        "source_world": world_1710,
        "target_world": world_1182,
        "parser_stats": parser.get_stats(),
    }
    report_path = os.path.join(world_1182, 'report.json')
    with open(report_path, 'w') as f:
        json.dump(report, f, indent=2)
    print(f"\nRaport zapisany: {report_path}")

    return result.returncode


if __name__ == '__main__':
    sys.exit(main())
