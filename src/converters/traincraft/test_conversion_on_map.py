"""
Testuje konwersję Traincraft na testowej mapie 1.7.10.
Odczytuje wszystkie TileEntities z mapy, wywołuje konwerter,
zapisuje wyniki do JSONL.
"""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from minecraft_map_parser.anvil_parser import AnvilParser
from converters.traincraft.traincraft_converter import TraincraftConverter
from converters.traincraft.mappings.block_mappings import is_traincraft_te_id


def convert_world(world_dir: Path, out_path: Path, removals_path: Path | None = None):
    region_dir = world_dir / "region"
    converter = TraincraftConverter(removals_path=removals_path)

    all_events = []
    te_count = 0
    tc_counts: dict[str, int] = {}

    for mca_file in sorted(region_dir.glob("*.mca")):
        parser = AnvilParser(str(mca_file))
        for chunk in parser.get_all_chunks():
            for te in chunk.get_tile_entities():
                    te_id = te.get("id", "")
                    if not is_traincraft_te_id(te_id):
                        continue
                    te_count += 1
                    tc_counts[te_id] = tc_counts.get(te_id, 0) + 1

                    x = int(te.get("x", 0))
                    y = int(te.get("y", 0))
                    z = int(te.get("z", 0))
                    pos = (x, y, z)

                    # Get block ID and metadata at TE position
                    blocks = chunk.get_blocks_and_metadata_at_positions()
                    local_x = x % 16
                    local_z = z % 16
                    if local_x < 0:
                        local_x += 16
                    if local_z < 0:
                        local_z += 16
                    block_id, meta = blocks.get((local_x, y, local_z), (0, 0))

                    result = converter.convert_tile_entity(
                        te_id=te_id,
                        te_nbt=te,
                        block_id=f"tc:tcRail",  # simplified; real block ID would need numeric mapping
                        metadata=meta,
                        pos=pos,
                    )
                    if result is None:
                        # Gag blocks -> air event
                        event = {"op": "set_block", "pos": list(pos), "block": "minecraft:air"}
                    else:
                        block_id_1182, _, props, nbt = result
                        event: dict = {"pos": list(pos), "block": block_id_1182}
                        if nbt:
                            event["op"] = "set_block_entity"
                            event["nbt"] = nbt
                        else:
                            event["op"] = "set_block"
                        if props:
                            event["blockstate"] = props
                    all_events.append(event)

    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        for event in all_events:
            f.write(json.dumps(event, ensure_ascii=False) + "\n")

    summary = {
        "world": str(world_dir),
        "total_te_processed": te_count,
        "total_events": len(all_events),
        "te_counts": tc_counts,
        "output": str(out_path),
    }
    summary_path = out_path.with_suffix(".summary.json")
    with open(summary_path, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)

    print(f"Processed {te_count} Traincraft TEs -> {len(all_events)} events")
    print(f"Saved to {out_path}")
    print(f"Summary: {summary_path}")
    return summary


if __name__ == "__main__":
    world = Path("test_worlds/traincraft_task5a_world")
    out = Path("output/traincraft_task5a/conversion_events.jsonl")
    removals = Path("output/traincraft_task4/track_removals.json")
    convert_world(world, out, removals_path=removals if removals.exists() else None)
