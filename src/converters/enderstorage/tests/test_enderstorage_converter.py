"""
Testy konwertera EnderStorage 1.7.10 → 1.18.2.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from converters.enderstorage.enderstorage_converter import EnderStorageConverter, ConversionResult
from converters.router import convert_te_to_events


class TestEnderStorageConverter:
    def test_chest_conversion(self):
        conv = EnderStorageConverter()
        nbt = {"id": "Ender Chest", "freq": 0x123, "owner": "global", "x": 0, "y": 64, "z": 0}
        result = conv.convert_tile_entity("Ender Chest", nbt, metadata=0, position=(0, 64, 0))
        assert result.success
        assert result.block_id_1182 == "enderstorage:ender_chest"
        assert result.nbt_1182 is not None
        freq = result.nbt_1182["Frequency"]
        assert freq["left"] == 1
        assert freq["middle"] == 2
        assert freq["right"] == 3

    def test_tank_conversion(self):
        conv = EnderStorageConverter()
        nbt = {"id": "Ender Tank", "freq": 0xABC, "owner": "global", "x": 0, "y": 64, "z": 0}
        result = conv.convert_tile_entity("Ender Tank", nbt, metadata=1, position=(0, 64, 0))
        assert result.success
        assert result.block_id_1182 == "enderstorage:ender_tank"
        freq = result.nbt_1182["Frequency"]
        assert freq["left"] == 10
        assert freq["middle"] == 11
        assert freq["right"] == 12

    def test_owner_preserved(self):
        conv = EnderStorageConverter()
        nbt = {"id": "Ender Chest", "freq": 0, "owner": "player-uuid-123", "x": 0, "y": 64, "z": 0}
        result = conv.convert_tile_entity("Ender Chest", nbt, metadata=0)
        assert result.nbt_1182["Frequency"]["owner"] == "player-uuid-123"

    def test_router_integration(self):
        nbt = {"id": "Ender Chest", "freq": 0x111, "owner": "global", "x": 5, "y": 64, "z": 10}
        events = convert_te_to_events(
            te_nbt=nbt,
            block_numeric_id=0,
            metadata=0,
            global_pos=(5, 64, 10),
        )
        assert len(events) == 1
        assert events[0]["block"] == "enderstorage:ender_chest"
