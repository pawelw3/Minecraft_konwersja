"""Testy symulacji Big Reactors / Bigger Reactors (Zadanie 2).

Weryfikują czy symulacje zachowują się zgodnie z logiką wyjętą z kodu źródłowego.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import unittest

from simulations.reactor_simulation_1710 import (
    ReactorSimulation1710,
    ModeratorProperties,
)
from simulations.reactor_simulation_1182 import ReactorSimulation1182
from simulations.turbine_simulation_1710 import TurbineSimulation1710
from simulations.turbine_simulation_1182 import TurbineSimulation1182
from simulations.cyanite_reprocessor_simulation import CyaniteReprocessorSimulation


class TestReactorSimulation1710(unittest.TestCase):
    def test_no_fuel_no_heat(self):
        r = ReactorSimulation1710()
        r.active = True
        r.tick()
        self.assertEqual(r.fuel_heat, 20.0)
        self.assertEqual(r.reactor_heat, 20.0)

    def test_fuel_generates_heat(self):
        r = ReactorSimulation1710(num_fuel_rods=4, reactor_volume=27)
        r.add_fuel(4000)
        r.active = True
        for _ in range(10):
            r.tick()
        self.assertGreater(r.fuel_heat, 20.0)
        self.assertGreaterEqual(r.reactor_heat, 20.0)

    def test_control_rod_reduces_burn(self):
        r = ReactorSimulation1710(num_fuel_rods=8, reactor_volume=64)
        r.add_fuel(16000)
        r.active = True
        r.set_control_rod_insertion(0.0)
        for _ in range(50):
            r.tick()
        heat_0 = r.fuel_heat

        r2 = ReactorSimulation1710(num_fuel_rods=8, reactor_volume=64)
        r2.add_fuel(16000)
        r2.active = True
        r2.set_control_rod_insertion(1.0)
        for _ in range(50):
            r2.tick()
        heat_1 = r2.fuel_heat

        # Przy insertion=0.0 ciepło paliwa powinno wzrosnąć (reakcja zachodzi)
        self.assertGreater(heat_0, 20.0)
        # Przy insertion=1.0 ciepło powinno pozostać niskie (brak reakcji)
        self.assertEqual(heat_1, 20.0)

    def test_passive_cooling_generates_energy(self):
        r = ReactorSimulation1710(
            num_fuel_rods=4,
            reactor_volume=27,
            passively_cooled=True,
        )
        r.add_fuel(4000)
        r.active = True
        for _ in range(50):
            r.tick()
        self.assertGreater(r.energy_stored, 0.0)


class TestReactorSimulation1182(unittest.TestCase):
    def test_no_fuel_no_heat(self):
        r = ReactorSimulation1182(x=3, y=3, z=3, control_rods=1)
        r.tick(active=True)
        self.assertEqual(r.fuel_tank.fuel, 0)
        self.assertEqual(r.fuel_heat.temperature, 293.15)

    def test_fuel_generates_heat(self):
        r = ReactorSimulation1182(x=5, y=5, z=5, control_rods=2)
        r.fuel_tank.insert_fuel(8000)
        for _ in range(20):
            r.tick(active=True)
        # Sumaryczne ciepło w systemie powinno wzrosnąć
        total_heat = r.fuel_heat.temperature + r.stack_heat.temperature
        self.assertGreater(total_heat, 2 * 293.15)

    def test_control_rod_reduces_burn(self):
        r1 = ReactorSimulation1182(x=3, y=3, z=3, control_rods=1)
        r1.fuel_tank.insert_fuel(4000)
        r1.set_all_control_rod_insertions(0.0)
        for _ in range(10):
            r1.tick(active=True)

        r2 = ReactorSimulation1182(x=3, y=3, z=3, control_rods=1)
        r2.fuel_tank.insert_fuel(4000)
        r2.set_all_control_rod_insertions(1.0)
        for _ in range(10):
            r2.tick(active=True)

        # Przy insertion=1.0 zużycie powinno być mniejsze
        self.assertLess(r1.fuel_tank.fuel, 4000)
        self.assertEqual(r2.fuel_tank.fuel, 4000)

    def test_passive_battery(self):
        r = ReactorSimulation1182(
            x=3, y=3, z=3,
            control_rods=1,
            passively_cooled=True,
        )
        r.fuel_tank.insert_fuel(4000)
        for _ in range(20):
            r.tick(active=True)
        self.assertIsNotNone(r.battery)


class TestTurbineSimulation1710(unittest.TestCase):
    def test_no_steam_no_spin(self):
        t = TurbineSimulation1710()
        t.active = True
        t.tick()
        self.assertEqual(t.get_rotor_speed(), 0.0)

    def test_steam_spins_rotor(self):
        t = TurbineSimulation1710(blade_surface_area=8, rotor_mass=20, coil_size=8)
        t.steam = 5000
        t.active = True
        for _ in range(20):
            t.tick()
        self.assertGreater(t.get_rotor_speed(), 0.0)

    def test_inductor_generates_energy(self):
        t = TurbineSimulation1710(blade_surface_area=8, rotor_mass=20, coil_size=8)
        t.steam = 5000
        t.active = True
        t.inductor_engaged = True
        for _ in range(30):
            t.tick()
        self.assertGreater(t.energy_stored, 0.0)

    def test_disengaged_inductor_no_energy(self):
        t = TurbineSimulation1710(blade_surface_area=8, rotor_mass=20, coil_size=8)
        t.steam = 5000
        t.active = True
        t.inductor_engaged = False
        for _ in range(30):
            t.tick()
        self.assertEqual(t.energy_stored, 0.0)
        self.assertGreater(t.get_rotor_speed(), 0.0)  # wirnik się kręci, ale nie generuje


class TestTurbineSimulation1182(unittest.TestCase):
    def test_no_steam_no_spin(self):
        t = TurbineSimulation1182()
        t.active = True
        t.tick()
        self.assertEqual(t.rpm(), 0.0)

    def test_steam_spins_rotor(self):
        t = TurbineSimulation1182(
            x=5, y=5, z=5,
            rotor_shafts=3, rotor_mass=30, coil_size=4,
        )
        t.fluid_tank.vapor = 5000
        t.active = True
        for _ in range(20):
            t.tick()
        self.assertGreater(t.rpm(), 0.0)

    def test_coil_generates_energy(self):
        t = TurbineSimulation1182(
            x=5, y=5, z=5,
            rotor_shafts=3, rotor_mass=30, coil_size=4,
            inductor_drag_coefficient=2.0,  # wyższy drag = więcej energii
            induction_efficiency=0.8,
        )
        # Ustaw maksymalny flow by turbina mogła pracować pełną mocą
        t.set_nominal_flow_rate(t.max_max_flow_rate)
        t.fluid_tank.vapor = 50000
        t.active = True
        t.coil_engaged = True
        for _ in range(200):
            t.tick()
        self.assertGreater(t.battery.stored, 0)

    def test_disengaged_coil_no_energy(self):
        t = TurbineSimulation1182(
            x=5, y=5, z=5,
            rotor_shafts=3, rotor_mass=30, coil_size=4,
        )
        t.fluid_tank.vapor = 5000
        t.active = True
        t.coil_engaged = False
        for _ in range(30):
            t.tick()
        self.assertEqual(t.battery.stored, 0)
        self.assertGreater(t.rpm(), 0.0)


class TestCyaniteReprocessorSimulation(unittest.TestCase):
    def test_no_inputs_no_progress(self):
        c = CyaniteReprocessorSimulation()
        c.tick()
        self.assertEqual(c.progress, 0)
        self.assertFalse(c.active)

    def test_full_cycle(self):
        c = CyaniteReprocessorSimulation()
        c.insert_cyanite(4)
        c.insert_water(5000)
        c.charge_energy(10000)

        for _ in range(210):
            c.tick()

        self.assertEqual(c.cycles_completed, 1)
        self.assertEqual(c.outlet_stack_size, 1)
        self.assertEqual(c.inlet_stack_size, 2)
        self.assertEqual(c.water, 4000)

    def test_multiple_cycles(self):
        c = CyaniteReprocessorSimulation()
        c.insert_cyanite(20)
        c.insert_water(10000)
        c.charge_energy(20000)

        for _ in range(450):
            c.tick()

        self.assertGreaterEqual(c.cycles_completed, 2)
        self.assertGreaterEqual(c.outlet_stack_size, 2)


if __name__ == "__main__":
    unittest.main()
