"""Symulacja reaktora Bigger Reactors 1.18.2.

Bazuje na kodzie źródłowym w projekcie:
- `mod_src/118/actual_src/1.18.2/BiggerReactors/repo/src/main/java/net/roguelogix/biggerreactors/multiblocks/reactor/simulation/base/BaseReactorSimulation.java`
- `mod_src/118/actual_src/1.18.2/BiggerReactors/repo/src/main/java/net/roguelogix/biggerreactors/multiblocks/reactor/simulation/IReactorSimulation.java`
- `mod_src/118/actual_src/1.18.2/BiggerReactors/repo/src/main/java/net/roguelogix/biggerreactors/multiblocks/reactor/ReactorMultiblockController.java`

Uproszczenia:
- Nie implementujemy pełnej symulacji OpenCL/CPU multi-threaded.
- radiate() jest uproszczone do modelu analitycznego.
- Heat transfer jest synchroniczny (tick-after-tick).
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class ReactorConfig1182:
    """Konfiguracja symulacji reaktora 1.18.2 (z SimulationConfiguration)."""
    fuel_rod_fuel_capacity: int = 4000          # mB na pręt
    rod_rfm3k: float = 1.0                     # RF per m^3 per K (fuel heat capacity)
    stack_rfm3k: float = 1.0                   # RF per m^3 per K (stack/casing heat capacity)
    fuel_to_stack_rfkt_multiplier: float = 1.0
    stack_to_coolant_rfmkt: float = 1.0
    stack_to_ambient_rfmkt: float = 0.001
    casing_heat_transfer_rfmkt: float = 1.0
    coolant_tank_capacity_per_fuel_rod: int = 4000
    passive_battery_per_external_block: int = 100_000
    passive_cooling_transfer_efficiency: float = 0.2
    fuel_fertility_decay_denominator: float = 20.0
    fuel_fertility_decay_denominator_inactive_multiplier: float = 200.0
    fuel_fertility_minimum_decay: float = 0.1
    ambient_temperature: float = 293.15         # K (~20°C)


class FuelTank:
    """Odpowiednik FuelTank z 1.18.2."""

    def __init__(self, capacity: int):
        self.capacity = capacity
        self.fuel = 0
        self.waste = 0

    def total_stored(self) -> int:
        return self.fuel + self.waste

    def insert_fuel(self, amount: int, simulated: bool = False) -> int:
        space = self.capacity - self.total_stored()
        added = min(amount, space)
        if not simulated:
            self.fuel += added
        return added

    def insert_waste(self, amount: int, simulated: bool = False) -> int:
        space = self.capacity - self.total_stored()
        added = min(amount, space)
        if not simulated:
            self.waste += added
        return added

    def extract_fuel(self, amount: int, simulated: bool = False) -> int:
        removed = min(amount, self.fuel)
        if not simulated:
            self.fuel -= removed
        return removed

    def extract_waste(self, amount: int, simulated: bool = False) -> int:
        removed = min(amount, self.waste)
        if not simulated:
            self.waste -= removed
        return removed

    def burn(self, amount: float):
        """Spalanie paliwa — amount to mB spalone w tym ticku."""
        self.fuel = max(0, int(self.fuel - amount))
        self.waste = min(self.capacity - self.fuel, self.waste + int(amount))

    def burned_last_tick(self) -> float:
        # Wartość historyczna — tutaj uproszczenie
        return 0.0


class Battery:
    """Bateria dla reaktora passively cooled (1.18.2).

    W oryginale battery jest HeatBody; ciepło zamiast podnosić temperaturę
    jest konwertowane na energię elektryczną (FE). Dla uproszczenia
    implementujemy transfer_with jako konwersję ciepła → energia.
    """

    def __init__(self, capacity: int):
        self.capacity = capacity
        self.stored = 0
        self.generated_last_tick = 0
        self.temperature = 293.15
        self.rf_per_kelvin = 1.0
        self.infinite = False

    def extract(self, amount: int) -> int:
        removed = min(amount, self.stored)
        self.stored -= removed
        return removed

    def generate(self, amount: int):
        self.generated_last_tick = amount
        self.stored = min(self.capacity, self.stored + amount)

    def set_temperature(self, temp: float):
        self.temperature = temp

    def transfer_with(self, other: "HeatBody", rfkt: float):
        """Ciepło przekazane do battery jest zamieniane na FE.

        Uproszczenie: zakładamy 100% sprawność konwersji.
        """
        temp_diff = other.temperature - self.temperature
        if temp_diff <= 0.0001:
            return
        rf_transferred = temp_diff * rfkt
        # In real BR battery is a HeatBody that dumps heat as FE
        # Here we just convert directly
        energy = int(rf_transferred)
        if energy > 0:
            self.generate(energy)
            other.temperature -= energy / other.rf_per_kelvin


class CoolantTank:
    """Zbiornik chłodziwa dla reaktora actively cooled (1.18.2)."""

    def __init__(self, per_side_capacity: int):
        self.per_side_capacity = per_side_capacity
        self.liquid = 0
        self.vapor = 0
        self.transitioned_last_tick = 0
        self.rf_transferred_last_tick = 0
        self.temperature = 293.15
        self.rf_per_kelvin = 1.0
        self.infinite = False

    def insert_liquid(self, amount: int) -> int:
        space = self.per_side_capacity - self.liquid
        added = min(amount, space)
        self.liquid += added
        return added

    def extract_vapor(self, amount: int) -> int:
        removed = min(amount, self.vapor)
        self.vapor -= removed
        return removed

    def transfer_with(self, other: "HeatBody", rfkt: float):
        """Ciepło przekazane do coolant tank zamienia wodę w parę."""
        temp_diff = other.temperature - self.temperature
        if temp_diff <= 0.0001:
            return
        rf_transferred = temp_diff * rfkt
        # Uproszczenie: 10 RF → 1 mB pary
        steam = int(rf_transferred / 10.0)
        steam = min(steam, self.liquid)
        if steam > 0:
            self.liquid -= steam
            self.vapor += steam
            self.transitioned_last_tick = steam
            other.temperature -= (steam * 10.0) / other.rf_per_kelvin


class HeatBody:
    """Uproszczony HeatBody z Phosphophyllite."""

    def __init__(self):
        self.rf_per_kelvin = 1.0
        self.temperature = 293.15
        self.infinite = False

    def set_temperature(self, temp: float):
        self.temperature = temp

    def transfer_with(self, other: "HeatBody", rfkt: float):
        """Przekazanie ciepła między dwoma ciałami.

        rfkt = współczynnik transferu (RF/K/tick).
        """
        if self.infinite and other.infinite:
            return
        temp_diff = self.temperature - other.temperature
        if abs(temp_diff) < 0.0001:
            return
        rf_transferred = temp_diff * rfkt
        if self.infinite:
            other.temperature += rf_transferred / other.rf_per_kelvin
        elif other.infinite:
            self.temperature -= rf_transferred / self.rf_per_kelvin
        else:
            self.temperature -= rf_transferred / self.rf_per_kelvin
            other.temperature += rf_transferred / other.rf_per_kelvin


class ReactorSimulation1182:
    """Uproszczona symulacja reaktora Bigger Reactors 1.18.2.

    Bazuje na BaseReactorSimulation.tick() oraz IReactorSimulation API.
    """

    def __init__(
        self,
        x: int = 3,
        y: int = 3,
        z: int = 3,
        control_rods: int = 1,
        manifold_count: int = 0,
        passively_cooled: bool = True,
        config: Optional[ReactorConfig1182] = None,
    ):
        self.config = config or ReactorConfig1182()
        self.x = x
        self.y = y
        self.z = z
        self.control_rods = control_rods
        self.manifold_count = manifold_count
        self.passively_cooled = passively_cooled

        # Heat bodies
        self.fuel_heat = HeatBody()
        self.stack_heat = HeatBody()
        self.ambient_heat = HeatBody()
        self.ambient_heat.infinite = True
        self.ambient_heat.set_temperature(self.config.ambient_temperature)

        # Output
        if passively_cooled:
            ext_blocks = ((x + 2) * (y + 2) * (z + 2)) - (x * y * z)
            self.battery = Battery(ext_blocks * self.config.passive_battery_per_external_block)
            self.coolant_tank = None
            self.output = self.battery
        else:
            per_side = control_rods * y * self.config.coolant_tank_capacity_per_fuel_rod
            per_side += manifold_count * self.config.coolant_tank_capacity_per_fuel_rod
            self.coolant_tank = CoolantTank(per_side)
            self.battery = None
            self.output = self.coolant_tank

        self.fuel_tank = FuelTank(
            self.config.fuel_rod_fuel_capacity * control_rods * y
        )

        self.fuel_fertility = 1.0
        self.was_active_last_tick = False

        # Control rod insertions (0.0 = out, 1.0 = fully inserted)
        self.control_rod_insertions = [0.0] * control_rods

        # Pre-computed heat transfer coefficients (simplified)
        self.fuel_to_stack_rfkt = (
            control_rods * y * 4 * self.config.casing_heat_transfer_rfmkt
            * self.config.fuel_to_stack_rfkt_multiplier
        )
        self.stack_to_coolant_rfkt = (
            2 * (x * y + x * z + y * z) * self.config.stack_to_coolant_rfmkt
        )
        if passively_cooled:
            self.stack_to_coolant_rfkt *= self.config.passive_cooling_transfer_efficiency

        self.casing_to_ambient_rfkt = (
            2 * ((x + 2) * (y + 2) + (x + 2) * (z + 2) + (z + 2) * (y + 2))
            * self.config.stack_to_ambient_rfmkt
        )

        # Heat capacities
        self.fuel_heat.rf_per_kelvin = control_rods * y * self.config.rod_rfm3k
        self.stack_heat.rf_per_kelvin = x * y * z * self.config.stack_rfm3k

    def set_all_control_rod_insertions(self, insertion: float):
        insertion = max(0.0, min(1.0, insertion))
        for i in range(len(self.control_rod_insertions)):
            self.control_rod_insertions[i] = insertion

    def _radiate(self) -> float:
        """Uproszczona radiacja — zwraca ilość spalonego paliwa (mB).

        W oryginale radiate() jest asynchroniczna i bardzo złożona.
        Tutaj przyjmujemy model:
        - burnRate ~ fuelAmount * (1 - meanInsertion) * fertility
        - ciepło proporcjonalne do burnRate
        """
        fuel = self.fuel_tank.fuel
        if fuel <= 0:
            return 0.0

        mean_insertion = sum(self.control_rod_insertions) / len(self.control_rod_insertions)
        control_modifier = 1.0 - mean_insertion

        # Uproszczony model z fertility
        base_burn = fuel * 0.0001 * control_modifier
        fertility_mod = max(1.0, math.log10(self.fuel_fertility) + 1.0) if self.fuel_fertility > 1.0 else 1.0
        to_burn = base_burn * fertility_mod

        # Ciepło generowane przez radiację
        heat_generated = to_burn * 100.0  # ~100 RF per mB (uproszczenie)
        self.fuel_heat.temperature += heat_generated / self.fuel_heat.rf_per_kelvin

        return to_burn

    def tick(self, active: bool):
        """Jeden tick reaktora."""
        to_burn = 0.0
        if self.was_active_last_tick or active:
            to_burn = self._radiate()
        else:
            self.fuel_tank.burn(0)

        # Fertility decay
        denominator = self.config.fuel_fertility_decay_denominator
        if not active:
            denominator *= self.config.fuel_fertility_decay_denominator_inactive_multiplier
        self.fuel_fertility = max(
            0.0,
            self.fuel_fertility - max(
                self.config.fuel_fertility_minimum_decay,
                self.fuel_fertility / denominator,
            ),
        )

        # Heat transfer
        self.fuel_heat.transfer_with(self.stack_heat, self.fuel_to_stack_rfkt)
        self.output.transfer_with(self.stack_heat, self.stack_to_coolant_rfkt)
        self.stack_heat.transfer_with(self.ambient_heat, self.casing_to_ambient_rfkt)

        if active:
            self.was_active_last_tick = True

        self.fuel_tank.burn(to_burn)

        # Passive battery generation (if passively cooled)
        if self.passively_cooled and self.battery:
            # W 1.18.2 bateria generuje energię proporcjonalnie do ciepła które
            # zostaje w niej zatrzymane. W naszym modelu ciepło przepływa
            # fuel→stack→battery, więc battery.temperature rośnie.
            # Oryginał: battery jest HeatBody i generuje FE zamiast ciepła.
            # Uproszczenie: zakładamy że całe ciepło trafiające do battery
            # jest konwertowane na energię elektryczną.
            pass

    def get_state(self) -> dict:
        """Zwraca aktualny stan reaktora (odpowiednik NBT / debug info)."""
        state = {
            "fuel_heat": self.fuel_heat.temperature,
            "stack_heat": self.stack_heat.temperature,
            "fuel": self.fuel_tank.fuel,
            "waste": self.fuel_tank.waste,
            "fertility": self.fuel_fertility,
        }
        if self.battery:
            state["battery_stored"] = self.battery.stored
            state["battery_capacity"] = self.battery.capacity
        if self.coolant_tank:
            state["coolant_liquid"] = self.coolant_tank.liquid
            state["coolant_vapor"] = self.coolant_tank.vapor
            state["coolant_capacity"] = self.coolant_tank.per_side_capacity
        return state
