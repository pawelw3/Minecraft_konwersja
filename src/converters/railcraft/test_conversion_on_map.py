"""
Testuje konwersję Railcraft na testowej mapie 1.7.10.
Odczytuje wszystkie TileEntities z mapy, wywołuje router konwersji,
zapisuje wyniki do JSONL.
"""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from minecraft_map_parser.anvil_parser import AnvilParser
from converters.router import convert_te_to_events


def convert_world(world_dir: Path, out_path: Path):
    region_dir = world_dir / "region"
    all_events = []
    te_count = 0

    for mca_file in sorted(region_dir.glob("*.mca")):
        parser = AnvilParser(str(mca_file))
        for chunk in parser.get_all_chunks():
            for te in chunk.get_tile_entities():
                te_id = te.get("id", "")
                if not te_id or not (te_id.startswith("RC") or te_id.startswith("Railcraft")):
                    continue
                te_count += 1
                # We need block metadata - get it from block at TE position
                blocks = chunk.get_blocks_and_metadata_at_positions()
                local_x = te["x"] % 16
                local_z = te["z"] % 16
                if local_x < 0:
                    local_x += 16
                if local_z < 0:
                    local_z += 16
                block_id, meta = blocks.get((local_x, te["y"], local_z), (0, 0))

                events = convert_te_to_events(
                    te_nbt=te,
                    block_numeric_id=block_id,
                    metadata=meta,
                    global_pos=(te["x"], te["y"], te["z"]),
                )
                all_events.extend(events)

    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        for event in all_events:
            f.write(json.dumps(event, ensure_ascii=False) + "\n")

    print(f"Converted {te_count} Railcraft TEs -> {len(all_events)} events")
    print(f"Saved to {out_path}")

    # Print summary
    block_counts = {}
    for event in all_events:
        bid = event.get("block", "UNKNOWN")
        block_counts[bid] = block_counts.get(bid, 0) + 1
    print("\nTarget block counts:")
    for bid, count in sorted(block_counts.items(), key=lambda x: -x[1]):
        print(f"  {bid}: {count}")


if __name__ == "__main__":
    world_dir = Path("lightweigh_map_templates/1710/railcraft_test")
    out_path = Path("output/railcraft_task4/test_conversion_events.jsonl")
    convert_world(world_dir, out_path)
