"""
Skrypt wyciągający przykładowe NBT dla Thermal Series TE z mapy 1.7.10.
"""
import sys
sys.path.insert(0, 'src')

from minecraft_map_parser.anvil_parser import AnvilParser
import os
import json
from collections import defaultdict

THERMAL_TE_IDS = [
    'thermalexpansion.', 'thermaldynamics.'
]

search_paths = [
    'mapa_1710/region',
    'lightweigh_map_templates/1710/region',
    'lightweigh_map_templates/1710_modded/region',
]

found_samples = defaultdict(list)
MAX_PER_TYPE = 3

for base_path in search_paths:
    if not os.path.exists(base_path):
        continue
    print(f"Skanowanie: {base_path}")
    for fname in sorted(os.listdir(base_path)):
        if not fname.endswith('.mca'):
            continue
        path = os.path.join(base_path, fname)
        try:
            region = AnvilParser(path)
        except Exception as e:
            continue
        for cx in range(32):
            for cz in range(32):
                try:
                    chunk = region.get_chunk(cx, cz)
                except:
                    continue
                if chunk is None:
                    continue
                te_list = chunk.tile_entities if hasattr(chunk, 'tile_entities') else []
                if not te_list:
                    continue
                for te in te_list:
                    if not isinstance(te, dict):
                        continue
                    te_id = te.get('id', '')
                    if not any(te_id.startswith(p) for p in THERMAL_TE_IDS):
                        continue
                    if len(found_samples[te_id]) < MAX_PER_TYPE:
                        sample = dict(te)
                        sample.pop('x', None)
                        sample.pop('y', None)
                        sample.pop('z', None)
                        found_samples[te_id].append(sample)

print(f"\nZnaleziono {len(found_samples)} typow TE:")
for te_id, samples in sorted(found_samples.items()):
    print(f"  {te_id}: {len(samples)} probek")

output = {
    'metadata': {
        'source': 'mapa_1710 + lightweight templates',
        'date': '2026-05-19',
        'purpose': 'Thermal Series Zadanie 2 - NBT analysis'
    },
    'samples': dict(found_samples)
}

out_path = 'src/converters/thermal/thermal_1710_nbt_samples.json'
with open(out_path, 'w') as f:
    json.dump(output, f, indent=2, default=str)

print(f"\nZapisano do: {out_path}")
