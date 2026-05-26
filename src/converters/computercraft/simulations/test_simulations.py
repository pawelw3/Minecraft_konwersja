"""Testy porównawcze symulacji ComputerCraft 1.7.10 → CC:Tweaked 1.18.2.

Uruchomienie:
    python -m unittest src.converters.computercraft.simulations.test_simulations
"""

from __future__ import annotations

import unittest

from .computer_simulation import (
    Computer1182,
    Computer1710,
    convert_computer_family,
    convert_computer_nbt,
)
from .monitor_multiblock_simulation import (
    DIR_TO_BLOCKSTATE,
    Monitor1182,
    Monitor1710,
    convert_monitor_dir,
    convert_monitor_nbt,
    derive_monitor_blockstate,
)
from .network_simulation import Cable1182, Cable1710, convert_cable_nbt
from .turtle_simulation import (
    Turtle1182,
    Turtle1710,
    TurtleUpgradeData,
    convert_turtle_nbt,
    resolve_upgrade_id,
)


class TestComputerSimulation(unittest.TestCase):
    def test_nbt_roundtrip(self):
        comp = Computer1710(computer_id=42, label="Test", on=True)
        nbt = comp.write_to_nbt()
        converted = convert_computer_nbt(nbt)
        loaded = Computer1182.read_from_nbt(converted)
        self.assertEqual(loaded.computer_id, comp.computer_id)
        self.assertEqual(loaded.label, comp.label)
        self.assertEqual(loaded.on, comp.on)

    def test_family_mapping(self):
        self.assertEqual(convert_computer_family("computercraft:computer", 2), "normal")
        self.assertEqual(convert_computer_family("computercraft:computer", 10), "advanced")
        self.assertEqual(convert_computer_family("computercraft:command_computer", 0), "command")

    def test_missing_label(self):
        comp = Computer1710(computer_id=1, on=False)
        nbt = comp.write_to_nbt()
        converted = convert_computer_nbt(nbt)
        self.assertNotIn("Label", converted)
        loaded = Computer1182.read_from_nbt(converted)
        self.assertIsNone(loaded.label)


class TestMonitorSimulation(unittest.TestCase):
    def test_dir_to_blockstate_horizontal(self):
        # dir=2 (north facing)
        ori, fac = convert_monitor_dir(2)
        self.assertEqual(ori, "north")
        self.assertEqual(fac, "north")

    def test_dir_to_blockstate_ceiling(self):
        # dir=8 (ceiling, base north)
        ori, fac = convert_monitor_dir(8)
        self.assertEqual(ori, "down")
        self.assertEqual(fac, "north")

    def test_dir_to_blockstate_floor(self):
        # dir=14 (floor, base north)
        ori, fac = convert_monitor_dir(14)
        self.assertEqual(ori, "up")
        self.assertEqual(fac, "north")

    def test_all_dir_values_mapped(self):
        for d in DIR_TO_BLOCKSTATE:
            ori, fac = convert_monitor_dir(d)
            self.assertIn(ori, ("north", "up", "down"))
            self.assertIn(fac, ("north", "south", "west", "east"))

    def test_nbt_conversion(self):
        mon = Monitor1710(x_index=1, y_index=0, width=3, height=2, dir=5)
        nbt = mon.write_to_nbt()
        converted = convert_monitor_nbt(nbt)
        self.assertEqual(converted["XIndex"], 1)
        self.assertEqual(converted["YIndex"], 0)
        self.assertEqual(converted["Width"], 3)
        self.assertEqual(converted["Height"], 2)

    def test_blockstate_derivation(self):
        # Origin monitor (0,0) w 2x2
        mon = Monitor1710(x_index=0, y_index=0, width=2, height=2, dir=2)
        bs = derive_monitor_blockstate(mon.write_to_nbt())
        self.assertEqual(bs["orientation"], "north")
        self.assertEqual(bs["facing"], "north")
        self.assertEqual(bs["state"], "rd")  # right + down

        # Prawy-górny (1,0)
        mon2 = Monitor1710(x_index=1, y_index=0, width=2, height=2, dir=2)
        bs2 = derive_monitor_blockstate(mon2.write_to_nbt())
        self.assertEqual(bs2["state"], "ld")  # left + down

        # Środkowy monitor 3x3
        mon3 = Monitor1710(x_index=1, y_index=1, width=3, height=3, dir=2)
        bs3 = derive_monitor_blockstate(mon3.write_to_nbt())
        self.assertEqual(bs3["state"], "lrud")

    def test_get_right_equivalence(self):
        """Weryfikacja że getRight() jest równoważny po konwersji."""
        for d in DIR_TO_BLOCKSTATE:
            with self.subTest(dir=d):
                m1710 = Monitor1710(dir=d)
                ori, fac = convert_monitor_dir(d)
                m1182 = Monitor1182(orientation=ori, facing=fac)
                self.assertEqual(
                    m1710.get_right(),
                    m1182.get_right(),
                    f"getRight mismatch for dir={d}",
                )


class TestTurtleSimulation(unittest.TestCase):
    def test_nbt_conversion(self):
        t = Turtle1710(
            computer_id=7,
            label="Digger",
            on=True,
            fuel_level=1000,
            selected_slot=2,
            colour_hex=0x00FF00,
            overlay="computercraft:turtle",
            left_upgrade=TurtleUpgradeData(upgrade_id="minecraft:diamond_pickaxe"),
            right_upgrade=TurtleUpgradeData(upgrade_id="computercraft:wireless_modem"),
        )
        nbt = t.write_to_nbt()
        converted = convert_turtle_nbt(nbt)
        loaded = Turtle1182.read_from_nbt(converted)
        self.assertEqual(loaded.computer_id, 7)
        self.assertEqual(loaded.label, "Digger")
        self.assertEqual(loaded.on, True)
        self.assertEqual(loaded.fuel_level, 1000)
        self.assertEqual(loaded.selected_slot, 2)
        self.assertEqual(loaded.colour_hex, 0x00FF00)
        self.assertEqual(loaded.overlay, "computercraft:turtle")
        self.assertEqual(loaded.left_upgrade.upgrade_id, "minecraft:diamond_pickaxe")
        self.assertEqual(loaded.right_upgrade.upgrade_id, "computercraft:wireless_modem_normal")

    def test_legacy_numeric_upgrades(self):
        self.assertEqual(resolve_upgrade_id(1), "computercraft:wireless_modem_normal")
        self.assertEqual(resolve_upgrade_id(2), "minecraft:crafting_table")
        self.assertEqual(resolve_upgrade_id(5), "minecraft:diamond_pickaxe")
        self.assertEqual(resolve_upgrade_id(-1), "computercraft:wireless_modem_advanced")
        self.assertEqual(resolve_upgrade_id(8), "computercraft:speaker")
        self.assertIsNone(resolve_upgrade_id(99))

    def test_string_upgrade_rename(self):
        self.assertEqual(resolve_upgrade_id("computercraft:wireless_modem"), "computercraft:wireless_modem_normal")
        self.assertEqual(resolve_upgrade_id("computercraft:advanced_modem"), "computercraft:wireless_modem_advanced")
        self.assertEqual(resolve_upgrade_id("minecraft:diamond_pickaxe"), "minecraft:diamond_pickaxe")

    def test_no_owner_in_1710(self):
        t = Turtle1710()
        nbt = t.write_to_nbt()
        converted = convert_turtle_nbt(nbt)
        self.assertNotIn("Owner", converted)

    def test_inventory_preserved(self):
        inv = [{"Slot": 0, "id": "minecraft:dirt", "Count": 64}]
        t = Turtle1710(inventory=inv)
        nbt = t.write_to_nbt()
        converted = convert_turtle_nbt(nbt)
        self.assertEqual(converted["Items"], inv)


class TestNetworkSimulation(unittest.TestCase):
    def test_cable_nbt_conversion(self):
        cab = Cable1710(peripheral_access_allowed=True, attached_peripheral_id=5)
        nbt = cab.write_to_nbt()
        converted = convert_cable_nbt(nbt)
        self.assertEqual(converted["PeripheralId"], 5)
        loaded = Cable1182.read_from_nbt(converted)
        self.assertEqual(loaded.peripheral_id, 5)

    def test_cable_no_peripheral(self):
        cab = Cable1710(peripheral_access_allowed=False, attached_peripheral_id=-1)
        nbt = cab.write_to_nbt()
        converted = convert_cable_nbt(nbt)
        self.assertNotIn("PeripheralId", converted)


if __name__ == "__main__":
    unittest.main(verbosity=2)
