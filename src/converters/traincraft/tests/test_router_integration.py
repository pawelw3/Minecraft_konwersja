"""Testy integracyjne routera dla Traincraft."""

import pytest
from converters.router import convert_te_to_events, detect_mod


class TestRouterDetection:
    def test_detects_tc_rail(self):
        assert detect_mod("tileTCRail") == "traincraft"

    def test_detects_tc_rail_gag(self):
        assert detect_mod("tileTCRailGag") == "traincraft"

    def test_detects_tc_lantern(self):
        assert detect_mod("tileLantern") == "traincraft"

    def test_detects_tc_distil(self):
        assert detect_mod("Tile Distil") == "traincraft"


class TestRouterConversion:
    def test_straight_track(self):
        te = {"id": "tileTCRail", "type": "SMALL_STRAIGHT", "facingMeta": 0, "x": 10, "y": 64, "z": -5}
        events = convert_te_to_events(te, block_numeric_id=100, metadata=0, global_pos=(10, 64, -5))
        assert len(events) == 1
        ev = events[0]
        assert ev["block"] == "create:track"
        assert ev["op"] == "set_block"
        assert ev["blockstate"]["shape"] == "zo"
        assert ev["blockstate"]["turn"] == "false"

    def test_slope_track(self):
        te = {"id": "tileTCRail", "type": "SLOPE_WOOD", "facingMeta": 2, "x": 0, "y": 70, "z": 0}
        events = convert_te_to_events(te, block_numeric_id=100, metadata=0, global_pos=(0, 70, 0))
        assert len(events) == 1
        ev = events[0]
        assert ev["block"] == "create:track"
        assert ev["blockstate"]["shape"] == "an"

    def test_turn_removed(self):
        te = {"id": "tileTCRail", "type": "MEDIUM_TURN", "facingMeta": 0, "x": 0, "y": 64, "z": 0}
        events = convert_te_to_events(te, block_numeric_id=100, metadata=0, global_pos=(0, 64, 0))
        assert len(events) == 1
        assert events[0]["block"] == "minecraft:air"

    def test_switch_approximated(self):
        te = {"id": "tileTCRail", "type": "MEDIUM_SWITCH", "facingMeta": 0, "x": 5, "y": 64, "z": 5}
        events = convert_te_to_events(te, block_numeric_id=100, metadata=0, global_pos=(5, 64, 5))
        assert len(events) == 1
        assert events[0]["block"] == "create:track"

    def test_rail_gag_becomes_air(self):
        te = {"id": "tileTCRailGag", "x": 1, "y": 65, "z": 2}
        events = convert_te_to_events(te, block_numeric_id=101, metadata=0, global_pos=(1, 65, 2))
        assert len(events) == 1
        assert events[0]["block"] == "minecraft:air"
        assert events[0]["op"] == "set_block"

    def test_unknown_tc_machine_placeholder(self):
        te = {"id": "Tile Distil", "x": 0, "y": 64, "z": 0}
        events = convert_te_to_events(te, block_numeric_id=102, metadata=0, global_pos=(0, 64, 0))
        assert len(events) == 1
        assert events[0]["block"] == "conversion_placeholders:block_entity_placeholder"
