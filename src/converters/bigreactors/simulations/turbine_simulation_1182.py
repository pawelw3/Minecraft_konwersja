"""Symulacja turbiny Bigger Reactors 1.18.2.

Bazuje na kodzie źródłowym w projekcie:
- `mod_src/118/actual_src/1.18.2/BiggerReactors/repo/src/main/java/net/roguelogix/biggerreactors/multiblocks/turbine/simulation/modern/ModernTurbineSimulation.java`
- `mod_src/118/actual_src/1.18.2/BiggerReactors/repo/src/main/java/net/roguelogix/biggerreactors/multiblocks/turbine/TurbineMultiblockController.java`

Uproszczenia:
- Nie symulujemy pełnego układu 3D wirnika (rotorConfiguration); użytkownik
  podaje gotowe parametry geometryczne (rotorShafts, rotorMass, bladeArea).
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Optional


@dataclass
class TurbineConfig1182:
    """Konfiguracja turbiny 1.18.2 (z Config.CONFIG.Turbine)."""
    flow_rate_per_block: int = 25
    fluid_per_blade_liner_kilometre: float = 1.0
    rotor_axial_mass_per_shaft: float = 10.0
    rotor_axial_mass_per_blade: float = 5.0
    coil_drag_multiplier: float = 1.0
    battery_size_per_coil_block: int = 1_000_000
    tank_volume_per_block: int = 4000
    friction_drag_multiplier: float = 1.0
    aerodynamic_drag_multiplier: float = 1.0
    effective_grid_frequency: float = 30.0  # Hz
    efficiency_peaks: float = 2.0            # liczba pików wydajności


class FluidTank:
    """Uproszczony FluidTank z ModernTurbineSimulation."""

    def __init__(self):
        self.per_side_capacity = 4000
        self.vapor = 0
        self.liquid = 0
        self.transitioned_last_tick = 0

    def flow(self, max_flow: int, can_vent: bool) -> int:
        """Zwraca ilość pary która przepłynęła przez turbinę.

        Uproszczenie: pobieramy min(vapor, max_flow).
        """
        flow = min(self.vapor, max_flow)
        self.vapor -= flow
        self.transitioned_last_tick = flow
        if can_vent:
            # Overflow venting — nie robimy nic, para jest "zużyta"
            pass
        return flow

    def dump_liquid(self):
        self.liquid = 0


class Battery:
    """Bateria turbiny (ITurbineBattery)."""

    def __init__(self):
        self.capacity = 0
        self.stored = 0

    def set_capacity(self, capacity: int):
        self.capacity = capacity
        self.stored = min(self.stored, capacity)

    def generate(self, amount: int):
        self.stored = min(self.capacity, self.stored + amount)

    def extract(self, amount: int) -> int:
        removed = min(amount, self.stored)
        self.stored -= removed
        return removed


class TurbineSimulation1182:
    """Uproszczona symulacja turbiny Bigger Reactors 1.18.2.

    Implementuje logikę z ModernTurbineSimulation.tick().
    """

    def __init__(
        self,
        x: int = 3,
        y: int = 3,
        z: int = 3,
        rotor_shafts: int = 3,
        rotor_mass: float = 30.0,
        linear_blade_meters: float = 4.0,
        coil_size: int = 4,
        induction_efficiency: float = 0.5,
        induction_energy_exponent_bonus: float = 1.0,
        inductor_drag_coefficient: float = 0.01,
        config: Optional[TurbineConfig1182] = None,
    ):
        self.config = config or TurbineConfig1182()
        self.x = x
        self.y = y
        self.z = z
        self.rotor_shafts = rotor_shafts
        self.rotor_mass = rotor_mass
        self.linear_blade_meters = linear_blade_meters
        self.coil_size = coil_size
        self.induction_efficiency = induction_efficiency
        self.induction_energy_exponent_bonus = induction_energy_exponent_bonus
        self.inductor_drag_coefficient = inductor_drag_coefficient

        self.active = False
        self.rotor_energy = 0.0
        self.coil_engaged = True
        self.vent_state = "overflow"  # "overflow", "all", "closed"
        self.max_flow_rate = -1

        self.fluid_tank = FluidTank()
        self.battery = Battery()

        # Wewnętrzne pre-computed
        self.rotor_capacity_per_rpm = (
            self.linear_blade_meters
            * self.config.fluid_per_blade_liner_kilometre
            / 1000.0
            * 2.0 * math.pi
        )
        self.rotor_axial_mass = (
            rotor_shafts * self.config.rotor_axial_mass_per_shaft
            + linear_blade_meters * self.config.rotor_axial_mass_per_blade
        )
        self.max_max_flow_rate = (
            ((x * z) - 1) * self.config.flow_rate_per_block
        )

        if self.max_flow_rate == -1:
            self.max_flow_rate = int(self.rotor_capacity_per_rpm * 1800)

        self.battery.set_capacity((coil_size + 1) * self.config.battery_size_per_coil_block)
        self.fluid_tank.per_side_capacity = (
            ((x * y * z) - (rotor_shafts + coil_size))
            * self.config.tank_volume_per_block
        )

        # Statystyki
        self.energy_generated_last_tick = 0.0
        self.rotor_efficiency_last_tick = 0.0

    def rpm(self) -> float:
        if self.rotor_axial_mass <= 0:
            return 0.0
        return self.rotor_energy / self.rotor_axial_mass

    def tick(self):
        rpm = self.rpm()

        if self.active:
            can_vent = self.vent_state != "closed"
            flow_rate = self.fluid_tank.flow(self.max_flow_rate, can_vent)
            effective_flow_rate = flow_rate

            rotor_capacity = self.rotor_capacity_per_rpm * max(100.0, rpm)

            if flow_rate > rotor_capacity:
                excess_flow = flow_rate - rotor_capacity
                excess_efficiency = rotor_capacity / flow_rate
                effective_flow_rate = rotor_capacity + excess_flow * excess_efficiency

            if flow_rate != 0:
                self.rotor_efficiency_last_tick = effective_flow_rate / flow_rate
            else:
                self.rotor_efficiency_last_tick = 0.0

            if effective_flow_rate > 0:
                # latentHeat * effectiveFlowRate * turbineMultiplier
                # Uproszczenie: zakładamy latentHeat=10, turbineMultiplier=1
                self.rotor_energy += 10.0 * effective_flow_rate
        else:
            self.fluid_tank.flow(0, self.vent_state != "closed")
            self.rotor_efficiency_last_tick = 0.0

        if self.vent_state == "all":
            self.fluid_tank.dump_liquid()

        if self.coil_engaged:
            induction_torque = rpm * self.inductor_drag_coefficient * self.coil_size
            energy_to_generate = (
                induction_torque ** self.induction_energy_exponent_bonus
            ) * self.induction_efficiency

            # Krzywa wydajności RPM
            frequency = self.config.effective_grid_frequency
            peak_rpm = frequency * 60.0
            min_rpm = peak_rpm / (2 ** (self.config.efficiency_peaks - 0.5))

            if rpm < min_rpm:
                efficiency = 0.5
            elif rpm > peak_rpm:
                numerator = rpm - peak_rpm
                denominator = 8.0 * frequency * peak_rpm
                possible_efficiency = -(numerator ** 2) / denominator
                efficiency = max(0.0, possible_efficiency + 1.0)
            else:
                log_value = -2.0 * (math.log(rpm / peak_rpm) / math.log(2)) + 1.0
                efficiency = -0.25 * math.cos(log_value * math.pi) + 0.75

            energy_to_generate *= efficiency
            self.energy_generated_last_tick = energy_to_generate

            if energy_to_generate > 1.0:
                self.battery.generate(int(energy_to_generate))

            self.rotor_energy -= induction_torque
        else:
            self.energy_generated_last_tick = 0.0

        # Drag
        self.rotor_energy -= self.rotor_mass * (
            rpm * self.config.friction_drag_multiplier
        ) ** 2
        self.rotor_energy -= self.linear_blade_meters * (
            rpm * self.config.aerodynamic_drag_multiplier
        ) ** 2

        if self.rotor_energy < 0:
            self.rotor_energy = 0.0

    def set_active(self, active: bool):
        self.active = active

    def set_coil_engaged(self, engaged: bool):
        self.coil_engaged = engaged

    def set_vent_state(self, state: str):
        assert state in ("overflow", "all", "closed")
        self.vent_state = state

    def set_nominal_flow_rate(self, flow_rate: int):
        self.max_flow_rate = min(self.max_max_flow_rate, max(0, flow_rate))

    def get_state(self) -> dict:
        return {
            "rpm": self.rpm(),
            "rotor_energy": self.rotor_energy,
            "battery_stored": self.battery.stored,
            "battery_capacity": self.battery.capacity,
            "vapor": self.fluid_tank.vapor,
            "liquid": self.fluid_tank.liquid,
            "active": self.active,
            "coil_engaged": self.coil_engaged,
            "energy_generated_last_tick": self.energy_generated_last_tick,
            "rotor_efficiency_last_tick": self.rotor_efficiency_last_tick,
        }
