"""Symulacja turbiny Big Reactors 1.7.10.

Bazuje na kodzie źródłowym w projekcie:
- `mod_src/1710/actual_src/1.7.10/BigReactors/repo/src/main/java/erogenousbeef/bigreactors/common/multiblock/MultiblockTurbine.java`

Uproszczenia:
- Nie symulujemy rozkładu 3D wirnika; użytkownik podaje gotowe
  bladeSurfaceArea, rotorMass, coilSize.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Optional


@dataclass
class TurbineConfig1710:
    """Konfiguracja turbiny 1.7.10 (z MultiblockTurbine + BigReactors config)."""
    power_production_multiplier: float = 1.0
    turbine_power_production_multiplier: float = 1.0
    max_energy_stored: float = 1_000_000.0  # 1 MRF
    input_fluid_per_blade: int = 25         # mB/t na łopatkę (domyślnie)
    fluid_energy_density: float = 10.0      # RF per mB pary
    inductor_base_drag_coefficient: float = 0.01


class TurbineSimulation1710:
    """Uproszczona symulacja turbiny Big Reactors 1.7.10.

    Implementuje logikę z MultiblockTurbine.updateServer().
    """

    def __init__(
        self,
        blade_surface_area: int = 4,
        rotor_mass: int = 10,
        coil_size: int = 4,
        induction_efficiency: float = 0.5,
        induction_energy_exponent_bonus: float = 1.0,
        config: Optional[TurbineConfig1710] = None,
    ):
        self.config = config or TurbineConfig1710()
        self.blade_surface_area = blade_surface_area
        self.rotor_mass = rotor_mass
        self.coil_size = coil_size
        self.induction_efficiency = induction_efficiency
        self.induction_energy_exponent_bonus = induction_energy_exponent_bonus

        # Dynamiczne
        self.energy_stored = 0.0
        self.active = False
        self.rotor_energy = 0.0
        self.inductor_engaged = True

        # Ustawienia gracza
        self.vent_status = "overflow"  # "overflow", "all", "closed"
        self.max_intake_rate = 2000    # mB/t

        # Tanki (para → woda)
        self.steam = 0
        self.water = 0
        self.tank_capacity = 4000

        # Statystyki ostatniego ticku
        self.energy_generated_last_tick = 0.0
        self.fluid_consumed_last_tick = 0
        self.rotor_efficiency_last_tick = 1.0

        # Współczynniki drag (przeliczone na podstawie kodu)
        self.inductor_drag_coefficient = (
            self.config.inductor_base_drag_coefficient * coil_size
        )
        self.rotor_drag_coefficient = 0.01 * rotor_mass
        self.blade_drag = 0.00025

    def get_rotor_speed(self) -> float:
        """RPM wirnika. W oryginale: rotorEnergy / rotorMass."""
        if self.rotor_mass <= 0:
            return 0.0
        return self.rotor_energy / self.rotor_mass

    def tick(self):
        self.energy_generated_last_tick = 0.0
        self.fluid_consumed_last_tick = 0
        self.rotor_efficiency_last_tick = 1.0

        steam_in = 0
        if self.active:
            steam_in = min(self.max_intake_rate, self.steam)
            if self.vent_status == "closed":
                available_space = self.tank_capacity - self.water
                steam_in = min(steam_in, available_space)

        if steam_in > 0 or self.rotor_energy > 0:
            rotor_speed = self.get_rotor_speed()

            # Aerodynamic drag
            aerodynamic_drag_torque = rotor_speed * self.blade_drag

            lift_torque = 0.0
            if steam_in > 0:
                fluid_energy_density = self.config.fluid_energy_density

                # Maksymalna ilość pary którą można przetworzyć
                steam_to_process = self.blade_surface_area * self.config.input_fluid_per_blade
                steam_to_process = min(steam_to_process, steam_in)
                lift_torque = steam_to_process * fluid_energy_density

                if steam_to_process < steam_in:
                    excess = steam_in - steam_to_process
                    needed_blades = math.ceil(steam_in / self.config.input_fluid_per_blade)
                    missing_blades = max(0, needed_blades - self.blade_surface_area)
                    blade_efficiency = 1.0 - (missing_blades / needed_blades)
                    lift_torque += excess * fluid_energy_density * blade_efficiency
                    self.rotor_efficiency_last_tick = lift_torque / (steam_in * fluid_energy_density)

            # Indukcja (generowanie energii)
            induction_torque = (
                rotor_speed * self.inductor_drag_coefficient * self.coil_size
                if self.inductor_engaged else 0.0
            )
            energy_to_generate = (induction_torque ** self.induction_energy_exponent_bonus) * self.induction_efficiency
            if energy_to_generate > 0.0:
                # Krzywa wydajności RPM
                efficiency = 0.25 * math.cos(rotor_speed / (45.5 * math.pi)) + 0.75
                if rotor_speed < 500:
                    efficiency = min(0.5, efficiency)
                energy = energy_to_generate * efficiency
                energy *= (
                    self.config.power_production_multiplier
                    * self.config.turbine_power_production_multiplier
                )
                self.energy_generated_last_tick = energy
                self.energy_stored = min(
                    self.config.max_energy_stored,
                    self.energy_stored + energy,
                )

            # Update rotor energy
            self.rotor_energy += (
                lift_torque
                - induction_torque
                - aerodynamic_drag_torque
                - self.rotor_drag_coefficient
            )
            if self.rotor_energy < 0:
                self.rotor_energy = 0.0

            # Zużycie pary i produkcja wody
            if steam_in > 0:
                self.fluid_consumed_last_tick = steam_in
                self.steam -= steam_in
                if self.vent_status != "all":
                    self.water = min(self.tank_capacity, self.water + steam_in)

    def set_active(self, active: bool):
        self.active = active

    def set_inductor_engaged(self, engaged: bool):
        self.inductor_engaged = engaged

    def set_vent_status(self, status: str):
        assert status in ("overflow", "all", "closed")
        self.vent_status = status

    def get_state(self) -> dict:
        return {
            "rpm": self.get_rotor_speed(),
            "rotor_energy": self.rotor_energy,
            "energy_stored": self.energy_stored,
            "steam": self.steam,
            "water": self.water,
            "active": self.active,
            "inductor_engaged": self.inductor_engaged,
            "energy_generated_last_tick": self.energy_generated_last_tick,
            "fluid_consumed_last_tick": self.fluid_consumed_last_tick,
            "rotor_efficiency_last_tick": self.rotor_efficiency_last_tick,
        }
