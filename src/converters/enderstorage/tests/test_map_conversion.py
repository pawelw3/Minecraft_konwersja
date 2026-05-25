"""
Testy konwersji EnderStorage na testowej mapie (Zadanie 5A lightweight).
"""

import sys
import json
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from minecraft_map_parser.anvil_parser import AnvilParser
from converters.router import convert_te_to_events


class TestEnderStorageMapConversion:
    def test_conversion_on_test_map(self):
        root = Path(__file__).parent.parent.parent.parent.parent
        parser = AnvilParser(str(root / "lightweigh_map_templates/1710/enderstorage_test/region/r.0.0.mca"))
        events = []
        for chunk in parser.get_all_chunks():
            for te in chunk.get_tile_entities():
                te_id = te.get("id", "")
                if te_id not in ("Ender Chest", "Ender Tank"):
                    continue
                blocks = chunk.get_blocks_and_metadata_at_positions()
                local_x = te["x"] % 16
                local_z = te["z"] % 16
                if local_x < 0:
                    local_x += 16
                if local_z < 0:
                    local_z += 16
                bid, meta = blocks.get((local_x, te["y"], local_z), (0, 0))
                ev = convert_te_to_events(
                    te_nbt=te,
                    block_numeric_id=bid,
                    metadata=meta,
                    global_pos=(te["x"], te["y"], te["z"]),
                )
                events.extend(ev)

        assert len(events) == 2
        chest = [e for e in events if e["block"] == "enderstorage:ender_chest"]
        tank = [e for e in events if e["block"] == "enderstorage:ender_tank"]
        assert len(chest) == 1
        assert len(tank) == 1
        assert chest[0]["nbt"]["Frequency"]["left"] == 1
        assert tank[0]["nbt"]["Frequency"]["owner"] == "player-uuid"
