"""Testy konwertera ComputerCraft 1.7.10 → CC:Tweaked 1.18.2."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from converters.computercraft.computercraft_converter import ComputerCraftConverter
from converters.router import convert_te_to_events


class TestComputerCraftConverter:
    def setup_method(self):
        self.conv = ComputerCraftConverter()

    # ------------------------------------------------------------------
    # Computer
    # ------------------------------------------------------------------
    def test_computer_normal(self):
        result = self.conv.convert_block(
            "computercraft:computer", metadata=2,
            nbt_1710={"computerID": 5, "label": "Miner", "on": True}
        )
        assert result.converted.success
        assert result.converted.block_id_1182 == "computercraft:computer_normal"
        assert result.converted.blockstate_props["facing"] == "north"
        assert result.converted.blockstate_props["state"] == "on"
        assert result.converted.nbt_1182 == {"ComputerId": 5, "Label": "Miner", "On": True}

    def test_computer_advanced(self):
        result = self.conv.convert_block(
            "computercraft:computer", metadata=10,
            nbt_1710={"computerID": 7, "on": False}
        )
        assert result.converted.success
        assert result.converted.block_id_1182 == "computercraft:computer_advanced"
        assert result.converted.blockstate_props["state"] == "off"
        assert result.converted.nbt_1182 == {"ComputerId": 7, "On": False}

    def test_command_computer(self):
        result = self.conv.convert_block(
            "computercraft:command_computer", metadata=0,
            nbt_1710={"computerID": 1, "label": "Admin", "on": True}
        )
        assert result.converted.success
        assert result.converted.block_id_1182 == "computercraft:computer_command"
        assert result.converted.blockstate_props["facing"] == "north"

    # ------------------------------------------------------------------
    # Monitor
    # ------------------------------------------------------------------
    def test_monitor_normal_horizontal(self):
        result = self.conv.convert_block(
            "computercraft:peripheral", metadata=10,
            nbt_1710={"xIndex": 0, "yIndex": 0, "width": 2, "height": 2, "dir": 2}
        )
        assert result.converted.success
        assert result.converted.block_id_1182 == "computercraft:monitor_normal"
        bs = result.converted.blockstate_props
        assert bs["orientation"] == "north"
        assert bs["facing"] == "north"
        assert bs["state"] == "rd"
        assert result.converted.nbt_1182 == {"XIndex": 0, "YIndex": 0, "Width": 2, "Height": 2}

    def test_monitor_advanced_ceiling(self):
        result = self.conv.convert_block(
            "computercraft:peripheral", metadata=12,
            nbt_1710={"xIndex": 1, "yIndex": 0, "width": 3, "height": 2, "dir": 9}
        )
        assert result.converted.success
        assert result.converted.block_id_1182 == "computercraft:monitor_advanced"
        bs = result.converted.blockstate_props
        assert bs["orientation"] == "down"
        assert bs["facing"] == "south"
        assert bs["state"] == "lrd"

    def test_monitor_floor(self):
        result = self.conv.convert_block(
            "computercraft:peripheral", metadata=10,
            nbt_1710={"xIndex": 0, "yIndex": 1, "width": 2, "height": 3, "dir": 16}
        )
        bs = result.converted.blockstate_props
        assert bs["orientation"] == "up"
        assert bs["facing"] == "west"
        assert bs["state"] == "rud"

    # ------------------------------------------------------------------
    # Turtle
    # ------------------------------------------------------------------
    def test_turtle_normal(self):
        result = self.conv.convert_block(
            "computercraft:turtle", metadata=0,
            nbt_1710={
                "computerID": 3, "label": "Digger", "on": True,
                "dir": 4, "fuelLevel": 1000, "selectedSlot": 1,
                "leftUpgrade": "minecraft:diamond_pickaxe",
                "rightUpgrade": "computercraft:wireless_modem",
            }
        )
        assert result.converted.success
        assert result.converted.block_id_1182 == "computercraft:turtle_normal"
        assert result.converted.blockstate_props["facing"] == "west"
        nbt = result.converted.nbt_1182
        assert nbt["ComputerId"] == 3
        assert nbt["Fuel"] == 1000
        assert nbt["Slot"] == 1
        assert nbt["LeftUpgrade"] == "minecraft:diamond_pickaxe"
        assert nbt["RightUpgrade"] == "computercraft:wireless_modem_normal"

    def test_turtle_expanded_maps_to_normal(self):
        result = self.conv.convert_block(
            "computercraft:turtle_expanded", metadata=0,
            nbt_1710={"computerID": 8, "on": False}
        )
        assert result.converted.success
        assert result.converted.block_id_1182 == "computercraft:turtle_normal"

    def test_turtle_advanced(self):
        result = self.conv.convert_block(
            "computercraft:turtle_advanced", metadata=0,
            nbt_1710={"computerID": 9, "on": True}
        )
        assert result.converted.success
        assert result.converted.block_id_1182 == "computercraft:turtle_advanced"

    def test_turtle_legacy_numeric_upgrades(self):
        result = self.conv.convert_block(
            "computercraft:turtle", metadata=0,
            nbt_1710={
                "leftUpgrade": 1,   # legacy wireless modem
                "rightUpgrade": -1, # legacy advanced modem
            }
        )
        nbt = result.converted.nbt_1182
        assert nbt["LeftUpgrade"] == "computercraft:wireless_modem_normal"
        assert nbt["RightUpgrade"] == "computercraft:wireless_modem_advanced"

    def test_turtle_colour_and_overlay(self):
        result = self.conv.convert_block(
            "computercraft:turtle", metadata=0,
            nbt_1710={
                "colour": 0xFF0000,
                "overlay_mod": "minecraft",
                "overlay_path": "diamond_pickaxe",
            }
        )
        nbt = result.converted.nbt_1182
        assert nbt["Colour"] == 0xFF0000
        assert nbt["Overlay"] == "minecraft:diamond_pickaxe"

    # ------------------------------------------------------------------
    # Disk Drive
    # ------------------------------------------------------------------
    def test_disk_drive(self):
        result = self.conv.convert_block(
            "computercraft:peripheral", metadata=3,
            nbt_1710={"item": {"id": "computercraft:disk", "Count": 1, "tag": {"diskID": 2}}}
        )
        assert result.converted.success
        assert result.converted.block_id_1182 == "computercraft:disk_drive"
        assert result.converted.blockstate_props["facing"] == "south"
        assert result.converted.nbt_1182["Item"]["id"] == "computercraft:disk"

    # ------------------------------------------------------------------
    # Printer
    # ------------------------------------------------------------------
    def test_printer(self):
        result = self.conv.convert_block(
            "computercraft:peripheral", metadata=11,
            nbt_1710={"printing": True, "pageTitle": "Test Page", "Items": []}
        )
        assert result.converted.success
        assert result.converted.block_id_1182 == "computercraft:printer"
        nbt = result.converted.nbt_1182
        assert nbt["Printing"] is True
        assert nbt["PageTitle"] == "Test Page"

    # ------------------------------------------------------------------
    # Wireless Modem
    # ------------------------------------------------------------------
    def test_wireless_modem(self):
        result = self.conv.convert_block(
            "computercraft:peripheral", metadata=6,
            nbt_1710={}
        )
        assert result.converted.success
        assert result.converted.block_id_1182 == "computercraft:wireless_modem_normal"
        assert result.converted.blockstate_props["facing"] == "north"
        assert result.converted.blockstate_props["on"] == "false"
        assert result.converted.nbt_1182 is None

    def test_advanced_modem(self):
        result = self.conv.convert_block(
            "computercraft:advanced_modem", metadata=0,
            nbt_1710={}
        )
        assert result.converted.success
        assert result.converted.block_id_1182 == "computercraft:wireless_modem_advanced"
        assert result.converted.blockstate_props["on"] == "false"

    # ------------------------------------------------------------------
    # Speaker
    # ------------------------------------------------------------------
    def test_speaker(self):
        result = self.conv.convert_block(
            "computercraft:peripheral", metadata=13,
            nbt_1710={}
        )
        assert result.converted.success
        assert result.converted.block_id_1182 == "computercraft:speaker"
        assert result.converted.blockstate_props["facing"] == "north"

    # ------------------------------------------------------------------
    # Cable / Wired Modem
    # ------------------------------------------------------------------
    def test_cable_modem_only(self):
        result = self.conv.convert_block(
            "computercraft:cable", metadata=2,
            nbt_1710={"peripheralAccess": False, "peripheralID": -1}
        )
        assert result.converted.success
        assert result.converted.block_id_1182 == "computercraft:cable"
        assert result.converted.blockstate_props["cable"] == "false"
        assert result.converted.blockstate_props["modem"] == "north_off"
        assert result.converted.nbt_1182 is None

    def test_cable_with_modem_and_peripheral(self):
        result = self.conv.convert_block(
            "computercraft:cable", metadata=8,
            nbt_1710={"peripheralAccess": True, "peripheralID": 3}
        )
        assert result.converted.success
        assert result.converted.blockstate_props["cable"] == "true"
        # meta 8 → modem + cable, facing = (8-6)=2 → north
        assert result.converted.blockstate_props["modem"] == "north_off"
        assert result.converted.nbt_1182 == {"PeripheralId": 3}

    def test_cable_only(self):
        result = self.conv.convert_block(
            "computercraft:cable", metadata=13,
            nbt_1710={}
        )
        assert result.converted.success
        assert result.converted.blockstate_props["cable"] == "true"
        assert result.converted.blockstate_props["modem"] == "none"

    # ------------------------------------------------------------------
    # Tile Entity ID conversion
    # ------------------------------------------------------------------
    def test_te_computer(self):
        result = self.conv.convert_tile_entity(
            "computercraft : computer",
            nbt_1710={"computerID": 10, "on": True},
            metadata=0,
        )
        assert result.converted.success
        assert result.converted.block_id_1182 == "computercraft:computer_normal"

    def test_te_monitor(self):
        result = self.conv.convert_tile_entity(
            "computercraft : monitor",
            nbt_1710={"xIndex": 0, "yIndex": 0, "width": 1, "height": 1, "dir": 2},
            metadata=10,
        )
        assert result.converted.success
        assert result.converted.block_id_1182 == "computercraft:monitor_normal"

    def test_te_turtleadv(self):
        result = self.conv.convert_tile_entity(
            "computercraft : turtleadv",
            nbt_1710={"computerID": 99},
            metadata=0,
        )
        assert result.converted.success
        assert result.converted.block_id_1182 == "computercraft:turtle_advanced"

    # ------------------------------------------------------------------
    # Router integration
    # ------------------------------------------------------------------
    def test_router_computer(self):
        events = convert_te_to_events(
            te_nbt={"id": "computercraft : computer", "computerID": 5, "on": True, "x": 1, "y": 64, "z": 2},
            block_numeric_id=0,
            metadata=2,
            global_pos=(1, 64, 2),
        )
        assert len(events) == 1
        ev = events[0]
        assert ev["op"] == "set_block_entity"
        assert ev["block"] == "computercraft:computer_normal"
        assert ev["nbt"]["ComputerId"] == 5
        assert ev["blockstate"]["facing"] == "north"

    def test_router_monitor(self):
        events = convert_te_to_events(
            te_nbt={"id": "monitor", "xIndex": 0, "yIndex": 0, "width": 2, "height": 2, "dir": 2, "x": 0, "y": 0, "z": 0},
            block_numeric_id=0,
            metadata=10,
            global_pos=(0, 0, 0),
        )
        assert len(events) == 1
        assert events[0]["block"] == "computercraft:monitor_normal"

    def test_router_unknown_te(self):
        events = convert_te_to_events(
            te_nbt={"id": "computercraft : unknown_thing", "x": 0, "y": 0, "z": 0},
            block_numeric_id=0,
            metadata=0,
            global_pos=(0, 0, 0),
        )
        # Powinien zwrócić placeholder bo unknown_thing nie jest w mapowaniach
        assert len(events) == 1
        assert "placeholder" in events[0]["block"]

    # ------------------------------------------------------------------
    # Errors
    # ------------------------------------------------------------------
    def test_unmapped_block(self):
        result = self.conv.convert_block("computercraft:unknown", metadata=0)
        assert not result.converted.success
        assert "CC-E-BLOCK-NOT-MAPPED" in result.converted.errors[0]

    def test_unmapped_te(self):
        result = self.conv.convert_tile_entity("computercraft : unknown", nbt_1710={}, metadata=0)
        assert not result.converted.success
        assert "CC-E-TE-NOT-MAPPED" in result.converted.errors[0]
