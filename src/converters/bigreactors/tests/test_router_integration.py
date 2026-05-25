"""Testy integracyjne routera dla Big Reactors."""

from __future__ import annotations

import pytest

from converters.router import convert_te_to_events, detect_mod


class TestRouterDetection:
    def test_detect_reactor_part(self):
        assert detect_mod("BRReactorPart") == "bigreactors"

    def test_detect_fuel_rod(self):
        assert detect_mod("BRFuelRod") == "bigreactors"

    def test_detect_turbine_part(self):
        assert detect_mod("BRTurbinePart") == "bigreactors"

    def test_detect_power_tap(self):
        assert detect_mod("BRReactorPowerTap") == "bigreactors"

    def test_detect_cyanite_reprocessor(self):
        assert detect_mod("BRCyaniteReprocessor") == "bigreactors"

    def test_detect_unknown(self):
        assert detect_mod("SomeRandomTE") == "unknown"


class TestRouterConversionEvents:
    def test_reactor_casing_event(self):
        te_nbt = {"id": "BRReactorPart", "x": 10, "y": 64, "z": -5}
        events = convert_te_to_events(te_nbt, block_numeric_id=0, metadata=0, global_pos=(10, 64, -5))
        assert len(events) == 1
        ev = events[0]
        assert ev["op"] == "set_block_entity"
        assert ev["block"] == "biggerreactors:reactor_casing"
        assert ev["pos"] == [10, 64, -5]
        assert ev["nbt"]["id"] == "biggerreactors:reactor_casing"

    def test_reactor_terminal_event(self):
        te_nbt = {"id": "BRReactorPart", "x": 0, "y": 0, "z": 0}
        events = convert_te_to_events(te_nbt, block_numeric_id=0, metadata=1, global_pos=(0, 0, 0))
        assert events[0]["block"] == "biggerreactors:reactor_terminal"

    def test_fuel_rod_event(self):
        te_nbt = {"id": "BRFuelRod", "x": 1, "y": 2, "z": 3}
        events = convert_te_to_events(te_nbt, block_numeric_id=0, metadata=0, global_pos=(1, 2, 3))
        assert events[0]["block"] == "biggerreactors:reactor_fuel_rod"

    def test_turbine_power_tap_event(self):
        te_nbt = {"id": "BRTurbinePowerTap", "x": 5, "y": 70, "z": 10}
        events = convert_te_to_events(te_nbt, block_numeric_id=0, metadata=0, global_pos=(5, 70, 10))
        assert events[0]["block"] == "biggerreactors:turbine_power_tap"

    def test_rednet_fallback_warning(self):
        te_nbt = {"id": "BRReactorRedNetPort", "x": 0, "y": 0, "z": 0}
        events = convert_te_to_events(te_nbt, block_numeric_id=0, metadata=0, global_pos=(0, 0, 0))
        assert events[0]["block"] == "biggerreactors:reactor_redstone_port"
        assert any("RedNet" in str(w) for w in events[0].get("warnings", []))

    def test_creative_part_removed(self):
        te_nbt = {"id": "BRReactorCreativeCoolantPort", "x": 0, "y": 0, "z": 0}
        events = convert_te_to_events(te_nbt, block_numeric_id=0, metadata=0, global_pos=(0, 0, 0))
        assert events[0]["block"] == "minecraft:air"

    def test_uranium_ore_no_te(self):
        # Uranium ore nie ma TE, wiec router nie powinien tego wywolywac,
        # ale jesli ktos przekaze pusty te_nbt, to powinien zwrocic pusta liste.
        events = convert_te_to_events({}, block_numeric_id=0, metadata=0, global_pos=(0, 0, 0))
        assert events == []

    def test_access_port_inventory_preserved(self):
        te_nbt = {
            "id": "BRReactorAccessPort",
            "x": 0, "y": 0, "z": 0,
            "Items": [
                {"Slot": 0, "id": "BigReactors:ingotYellorium", "Count": 8},
            ],
        }
        events = convert_te_to_events(te_nbt, block_numeric_id=0, metadata=0, global_pos=(0, 0, 0))
        nbt_out = events[0]["nbt"]
        assert nbt_out["Items"][0]["id"] == "biggerreactors:uranium_ingot"

    def test_unknown_bigreactors_te_placeholder(self):
        # TE ktore wyglada jak BigReactors ale nie jest znany
        te_nbt = {"id": "BRUnknownTile", "x": 0, "y": 0, "z": 0}
        events = convert_te_to_events(te_nbt, block_numeric_id=0, metadata=0, global_pos=(0, 0, 0))
        # BRUnknownTile zaczyna sie od "BR" ale nie jest w ALL_BIGREACTORS_TE_IDS
        # detect_mod zwroci "unknown" -> placeholder
        assert len(events) == 1
        assert events[0]["block"] == "conversion_placeholders:block_entity_placeholder"
