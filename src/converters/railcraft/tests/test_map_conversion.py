"""
Testy konwersji Railcraft na testowej mapie (Zadanie 5A lightweight).
"""

import sys
import json
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from converters.railcraft.test_conversion_on_map import convert_world


class TestRailcraftMapConversion:
    def test_conversion_runs_without_errors(self):
        root = Path(__file__).parent.parent.parent.parent.parent
        world_dir = root / "lightweigh_map_templates/1710/railcraft_test"
        out_path = root / "output/railcraft_task4/test_map_conversion_events.jsonl"
        convert_world(world_dir, out_path)
        assert out_path.exists()

        events = []
        with open(out_path, encoding="utf-8") as f:
            for line in f:
                events.append(json.loads(line))

        # Should have at least 19 events for 19 Railcraft TEs
        assert len(events) >= 19

        # Check specific conversions
        blocks_by_pos = {}
        for event in events:
            pos = tuple(event["pos"])
            blocks_by_pos[pos] = event

        # Coke Oven -> IE Coke Oven
        assert blocks_by_pos[(4, 64, 0)]["block"] == "immersiveengineering:coke_oven"
        # Blast Furnace -> IE Blast Furnace
        assert blocks_by_pos[(6, 64, 0)]["block"] == "immersiveengineering:blast_furnace"
        # Hidden Tile -> air
        assert blocks_by_pos[(20, 64, 0)]["block"] == "minecraft:air"
        # Slab -> FramedBlocks slab
        assert blocks_by_pos[(22, 64, 0)]["block"] == "framedblocks:framed_slab"
        assert blocks_by_pos[(22, 64, 0)]["blockstate"]["type"] == "bottom"
        # Stair -> FramedBlocks stairs
        assert blocks_by_pos[(24, 64, 0)]["block"] == "framedblocks:framed_stairs"
        # Steel tanks -> Create fluid tank
        assert blocks_by_pos[(26, 64, 0)]["block"] == "create:fluid_tank"
        # Void chest -> Thermal nullifier
        assert blocks_by_pos[(32, 64, 0)]["block"] == "thermal:device_nullifier"
        # Signal boxes -> comparator
        assert blocks_by_pos[(0, 64, 2)]["block"] == "minecraft:comparator"
        assert blocks_by_pos[(2, 64, 2)]["block"] == "minecraft:comparator"
