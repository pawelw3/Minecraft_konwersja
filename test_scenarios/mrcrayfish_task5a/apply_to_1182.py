"""
Aplikuje eventy konwersji CFM na testowa mape 1.18.2.
"""

import sys
import os
import json
import subprocess

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..'))

from src.converters.mrcrayfish_furniture.mrcrayfish_chunk_parser import MrCrayfishChunkParser


def main():
    world_1710 = '.'
    world_1182 = './target_1182'
    worker_jar = '../../jvm/worker/build/libs/mc-editkit-worker-1.0-SNAPSHOT.jar'
    level_dat_path = os.path.abspath(os.path.join(os.getcwd(), '..', '..', 'mapa_1710', 'level.dat'))

    # 1. Skanuj swiat 1.7.10
    parser = MrCrayfishChunkParser(world_1710, level_dat_path=level_dat_path)
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

    # 2. Generuj eventy
    events = []
    for result in results:
        for event in result.events:
            e = event.to_set_block_event()
            if e:
                events.append(e)

    # Dodaj remove_block dla usunietych blokow (ktore maja event_type == 'remove')
    for result in results:
        for event in result.events:
            if event.event_type == 'remove' and event.position:
                events.append({
                    "op": "remove_block",
                    "pos": list(event.position),
                })

    events_path = os.path.join(world_1710, 'events_1182.json')
    with open(events_path, 'w') as f:
        json.dump({"events": events}, f, indent=2)

    print(f"Generated {len(events)} events -> {events_path}")

    # 3. Utworz pusty swiat 1.18.2
    os.makedirs(os.path.join(world_1182, 'region'), exist_ok=True)

    # 4. Aplikuj eventy przez worker.jar
    cmd = [
        'java', '-jar', worker_jar,
        '--apply-events', events_path,
        '--target-world', world_1182,
    ]
    print(f"Running: {' '.join(cmd)}")
    result = subprocess.run(cmd, capture_output=True, text=True)
    print(result.stdout)
    if result.stderr:
        print("STDERR:", result.stderr)
    print(f"Return code: {result.returncode}")


if __name__ == '__main__':
    main()
