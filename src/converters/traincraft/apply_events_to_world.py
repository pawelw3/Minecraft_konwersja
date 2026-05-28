"""
Applies Traincraft conversion events (JSONL) to a 1.18.2 world using Amulet.
"""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

import amulet
from amulet.api.block import Block


def apply_events(world_path: Path, events_path: Path):
    print(f"Loading world: {world_path}")
    level = amulet.load_level(str(world_path))
    dimension = "minecraft:overworld"
    version = ("java", (1, 18, 2))

    stats = {"set_block": 0, "set_block_entity": 0, "errors": 0}

    with open(events_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                ev = json.loads(line)
            except json.JSONDecodeError:
                continue

            op = ev.get("op", "set_block")
            pos = ev.get("pos", [0, 0, 0])
            block_id = ev.get("block", "minecraft:air")
            x, y, z = pos

            try:
                if ":" not in block_id:
                    block_id = "minecraft:" + block_id

                namespace, name = block_id.split(":", 1)
                blockstate = ev.get("blockstate", {})

                # For mod blocks (like create:track), Amulet may not support arbitrary
                # blockstate properties. We skip properties for mod blocks and let the
                # game use defaults. Vanilla blocks still get properties.
                properties = {}
                if blockstate and namespace == "minecraft":
                    for k, v in blockstate.items():
                        properties[k] = str(v)

                block = Block(namespace, name, properties if properties else None)
                level.set_version_block(x, y, z, dimension, version, block)

                if op == "set_block_entity":
                    # Amulet handles block entity through the block for simple cases
                    # For Create tracks with TE NBT, we'd need deeper integration
                    stats["set_block_entity"] += 1
                else:
                    stats["set_block"] += 1

            except Exception as e:
                stats["errors"] += 1
                if stats["errors"] <= 5:
                    print(f"Error at {pos}: {e}")

    print("Saving world...")
    level.save()
    level.close()
    print(f"Done. set_block={stats['set_block']}, set_block_entity={stats['set_block_entity']}, errors={stats['errors']}")
    return stats


if __name__ == "__main__":
    world = Path("test_worlds/traincraft_task5b_1182")
    events = Path("output/traincraft_task5a/conversion_events.jsonl")
    apply_events(world, events)
