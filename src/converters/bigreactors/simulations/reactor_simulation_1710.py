"""Symulacja reaktora Big Reactors 1.7.10.

Bazuje na kodzie źródłowym w projekcie:
- `mod_src/1710/actual_src/1.7.10/BigReactors/repo/src/main/java/erogenousbeef/bigreactors/common/multiblock/MultiblockReactor.java`
- `mod_src/1710/actual_src/1.7.10/BigReactors/repo/src/main/java/erogenousbeef/bigreactors/common/multiblock/helpers/RadiationHelper.java`
- `mod_src/1710/actual_src/1.7.10/BigReactors/repo/src/main/java/erogenousbeef/bigreactors/common/multiblock/helpers/FuelContainer.java`
- `mod_src/1710/actual_src/1.7.10/BigReactors/repo/src/main/java/erogenousbeef/bigreactors/common/multiblock/helpers/CoolantContainer.java`

Uproszczenia względem oryginału:
- Nie symulujemy propagacji promieniowania blok-po-bloku w 3D. Zamiast tego
  użytkownik podaje efektywną głębokość moderacji i średnie właściwości moderatora.
- Nie symulujemy wymiany ciepła z poszczególnymi blockami (fuel rod → casing → coolant);
  stosujemy globalne współczynniki transferu ciepła.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class ModeratorProperties:
    """Średnie właściwości moderatora wewnątrz reaktora (z ReactorInteriorData)."""
    absorption: float = 0.1       # jak dużo promieniowania jest pochłaniane
    heat_efficiency: float = 0.25 # ile z pochłoniętego promieniowania idzie jako ciepło
    moderation: float = 1.1       # jak bardzo zmiękcza promieniowanie (zmniejsza hardness)
    conductivity: float = 0.001   # przewodność cieplna (RF/m·K)


@dataclass
class ReactorConfig:
    """Stałe konfiguracyjne reaktora (z BigReactors.java i statycznych pól)."""
    power_production_multiplier: float = 1.0
    reactor_power_production_multiplier: float = 1.0
    fuel_usage_multiplier: float = 1.0
    passive_cooling_power_efficiency: float = 0.5   # 50% penalty
    passive_cooling_transfer_efficiency: float = 0.2 # 20% heat transfer
    reactor_heat_loss_conductivity: float = 0.001
    fuel_capacity_per_rod: int = 4 * 1000            # 4 ingots * 1000 mB
    max_energy_stored: float = 10_000_000.0           # 10 MRF
    ambient_temperature: float = 20.0                 # °C, ok. 293K


class FuelContainer:
    """Uproszczony FuelContainer z 1.7.10.

    Rejestruje ilość paliwa (yellorium/blutonium) i odpadów (cyanite).
    """

    def __init__(self, capacity: int):
        self.capacity = capacity
        self.fuel = 0
        self.waste = 0

    def get_fuel_amount(self) -> int:
        return self.fuel

    def get_waste_amount(self) -> int:
        return self.waste

    def get_total_amount(self) -> int:
        return self.fuel + self.waste

    def get_fuel_reactivity(self) -> float:
        """Reaktywność paliwa — w 1.7.10 zależy od stosunku fuel/waste.

        Dokładna wartość zależy od FuelContainer.getFuelReactivity(),
        które zwykle zwraca ~1.0 dla czystego paliwa, maleje z waste.
        """
        total = self.get_total_amount()
        if total == 0:
            return 1.0
        # Uproszczenie: czyste paliwo = 1.05, same odpady = 0.95
        return 0.95 + 0.10 * (self.fuel / total)

    def on_radiation_uses_fuel(self, amount: float):
        """Zużycie paliwa podczas promieniowania."""
        self.fuel = max(0, int(self.fuel - amount))
        self.waste = min(self.capacity - self.fuel, self.waste + int(amount))

    def refuel(self, amount: int) -> int:
        """Dodaje paliwo, zwraca ile faktycznie weszło."""
        space = self.capacity - self.get_total_amount()
        added = min(amount, space)
        self.fuel += added
        return added

    def eject_waste(self, amount: int) -> int:
        """Wyrzuca odpady, zwraca ile wyrzucono."""
        removed = min(amount, self.waste)
        self.waste -= removed
        return removed


class RadiationHelper:
    """Uproszczony RadiationHelper z 1.7.10.

    Oryginalny kod propaguje promieniowanie w 4 kierunkach kardynalnych,
    po 4 bloki z moderacją. Tutaj uśredniamy efekt do jednego "pocisku"
    o efektywnej głębokości moderacji.
    """

    FUEL_PER_RADIATION_UNIT = 0.0007
    RF_PER_RADIATION_UNIT = 10.0
    FISSION_EVENTS_PER_FUEL_UNIT = 0.01

    def __init__(self):
        self.fertility = 1.0

    def get_fertility_modifier(self) -> float:
        """Fertility wpływa na zużycie paliwa — wyższa = mniejsze zużycie."""
        if self.fertility <= 1.0:
            return 1.0
        return math.log10(self.fertility) + 1.0

    def radiate(
        self,
        fuel_container: FuelContainer,
        fuel_heat: float,
        control_rod_insertion: float,  # 0.0 .. 1.0
        num_control_rods: int,
        moderator: ModeratorProperties,
        moderation_depth: int = 4,  # ile bloków "przechodzi" promieniowanie
    ) -> dict:
        """Symuluje jeden tick promieniowania.

        Zwraca dict z polami:
        - fuel_rf_change: ciepło dodane do paliwa (RF)
        - environment_rf_change: ciepło dodane do otoczenia (RF)
        - fuel_usage: zużyte paliwo (mB)
        """
        if fuel_container.get_fuel_amount() <= 0:
            return {"fuel_rf_change": 0.0, "environment_rf_change": 0.0, "fuel_usage": 0.0}

        # radiationPenaltyBase — kara za wysoką temperaturę
        radiation_penalty_base = math.exp(-15 * math.exp(-0.0025 * fuel_heat))

        base_fuel_amount = fuel_container.get_fuel_amount() + (fuel_container.get_waste_amount() / 100)
        fuel_reactivity = fuel_container.get_fuel_reactivity()

        raw_rad_intensity = base_fuel_amount * self.FISSION_EVENTS_PER_FUEL_UNIT
        scaled_rad_intensity = (raw_rad_intensity ** fuel_reactivity)
        scaled_rad_intensity = ((scaled_rad_intensity / num_control_rods) ** fuel_reactivity) * num_control_rods

        # Control rod moderation
        control_rod_modifier = 1.0 - control_rod_insertion
        scaled_rad_intensity *= control_rod_modifier
        raw_rad_intensity *= control_rod_modifier

        effective_rad_intensity = scaled_rad_intensity * (
            1.0 + (-0.95 * math.exp(-10.0 * math.exp(-0.0012 * fuel_heat)))
        )

        rad_hardness = 0.2 + 0.8 * radiation_penalty_base

        # Fuel usage
        raw_fuel_usage = (
            self.FUEL_PER_RADIATION_UNIT * raw_rad_intensity / self.get_fertility_modifier()
        )

        fuel_rf_change = self.RF_PER_RADIATION_UNIT * effective_rad_intensity
        environment_rf_change = 0.0

        # Moderacja — uproszczenie 4 kierunków × moderation_depth
        # W oryginale każdy kierunek to osobne ttl=4 kroki.
        total_intensity = effective_rad_intensity * 4.0
        for _ in range(4 * moderation_depth):
            if total_intensity <= 0.0001:
                break
            absorbed = total_intensity * moderator.absorption * (1.0 - rad_hardness)
            total_intensity -= absorbed
            environment_rf_change += absorbed * moderator.heat_efficiency
            rad_hardness *= moderator.moderation

        self.fertility += fuel_rf_change  # fertility rośnie z generowanym ciepłem

        return {
            "fuel_rf_change": fuel_rf_change,
            "environment_rf_change": environment_rf_change,
            "fuel_usage": raw_fuel_usage,
        }

    def tick(self, active: bool):
        """Rozpad fertility między tickami."""
        denominator = 20.0
        if not active:
            denominator *= 200.0
        self.fertility = max(0.0, self.fertility - max(0.1, self.fertility / denominator))


class ReactorSimulation1710:
    """Uproszczona symulacja reaktora Big Reactors 1.7.10.

    Implementuje logikę z MultiblockReactor.updateServer() w wersji
    zredukowanej do jednowymiarowego modelu cieplnego.
    """

    def __init__(
        self,
        num_fuel_rods: int = 4,
        reactor_volume: int = 27,  # np. 3x3x3
        moderator: Optional[ModeratorProperties] = None,
        config: Optional[ReactorConfig] = None,
        passively_cooled: bool = True,
    ):
        self.config = config or ReactorConfig()
        self.moderator = moderator or ModeratorProperties()
        self.num_fuel_rods = num_fuel_rods
        self.reactor_volume = reactor_volume
        self.passively_cooled = passively_cooled

        self.active = False
        self.fuel_heat = 20.0
        self.reactor_heat = 20.0
        self.energy_stored = 0.0

        self.fuel_container = FuelContainer(
            capacity=num_fuel_rods * self.config.fuel_capacity_per_rod
        )
        self.radiation_helper = RadiationHelper()

        # Współczynniki transferu ciepła (uproszczone)
        self.fuel_to_reactor_htc = num_fuel_rods * self.moderator.conductivity
        self.reactor_to_coolant_htc = reactor_volume * self.moderator.conductivity * 2.0
        if passively_cooled:
            self.reactor_to_coolant_htc *= self.config.passive_cooling_transfer_efficiency

        # Coolant / steam (dla active cooling)
        self.coolant_tank = 0  # mB wody
        self.steam_tank = 0    # mB pary
        self.steam_generated_last_tick = 0
        self.energy_generated_last_tick = 0.0
        self.fuel_consumed_last_tick = 0.0

        # Control rods (0.0 = wysunięte, 1.0 = wciśnięte)
        self.control_rod_insertion = 0.0

    def set_control_rod_insertion(self, insertion: float):
        """0.0 = brak moderacji (max moc), 1.0 = pełne wciśnięcie (min moc)."""
        self.control_rod_insertion = max(0.0, min(1.0, insertion))

    def add_fuel(self, amount: int) -> int:
        return self.fuel_container.refuel(amount)

    def tick(self):
        """Jeden tick reaktora (~1/20 s)."""
        self.energy_generated_last_tick = 0.0
        self.fuel_consumed_last_tick = 0.0
        self.steam_generated_last_tick = 0

        if self.active:
            rad_result = self.radiation_helper.radiate(
                fuel_container=self.fuel_container,
                fuel_heat=self.fuel_heat,
                control_rod_insertion=self.control_rod_insertion,
                num_control_rods=self.num_fuel_rods,
                moderator=self.moderator,
            )
            self.fuel_heat += self._rf_to_temp(
                rad_result["fuel_rf_change"], self.num_fuel_rods
            )
            self.reactor_heat += self._rf_to_temp(
                rad_result["environment_rf_change"], self.reactor_volume
            )
            self.fuel_consumed_last_tick = rad_result["fuel_usage"]

        self.radiation_helper.tick(self.active)

        # Heat transfer: fuel pool ↔ reactor environment
        temp_diff = self.fuel_heat - self.reactor_heat
        if temp_diff > 0.01:
            rf_transferred = temp_diff * self.fuel_to_reactor_htc
            self.fuel_heat = self._rf_to_temp(
                self._temp_to_rf(self.fuel_heat, self.num_fuel_rods) - rf_transferred,
                self.num_fuel_rods,
            )
            self.reactor_heat = self._rf_to_temp(
                self._temp_to_rf(self.reactor_heat, self.reactor_volume) + rf_transferred,
                self.reactor_volume,
            )

        # Heat transfer: reactor ↔ coolant / ambient
        temp_diff = self.reactor_heat - self.config.ambient_temperature
        if temp_diff > 0.01:
            rf_transferred = temp_diff * self.reactor_to_coolant_htc
            if self.passively_cooled:
                rf_transferred *= self.config.passive_cooling_transfer_efficiency
                energy = rf_transferred * self.config.passive_cooling_power_efficiency
                energy *= (
                    self.config.power_production_multiplier
                    * self.config.reactor_power_production_multiplier
                )
                self.energy_generated_last_tick += energy
                self.energy_stored = min(
                    self.config.max_energy_stored,
                    self.energy_stored + energy,
                )
                self.reactor_heat = self._rf_to_temp(
                    self._temp_to_rf(self.reactor_heat, self.reactor_volume) - rf_transferred,
                    self.reactor_volume,
                )
            else:
                # Active cooling: zamiana wody w parę
                # Uproszczenie: 1 mB wody ≈ 10 RF ciepła → para
                steam = int(rf_transferred / 10.0)
                steam = min(steam, self.coolant_tank)
                if steam > 0:
                    self.coolant_tank -= steam
                    self.steam_tank += steam
                    self.steam_generated_last_tick = steam
                    self.reactor_heat = self._rf_to_temp(
                        self._temp_to_rf(self.reactor_heat, self.reactor_volume)
                        - steam * 10.0,
                        self.reactor_volume,
                    )

        # Passive heat loss (do otoczenia)
        temp_diff = self.reactor_heat - self.config.ambient_temperature
        if temp_diff > 0.000001:
            rf_lost = max(1.0, temp_diff * self.config.reactor_heat_loss_conductivity)
            self.reactor_heat = self._rf_to_temp(
                max(0.0, self._temp_to_rf(self.reactor_heat, self.reactor_volume) - rf_lost),
                self.reactor_volume,
            )

        # Clamp
        if self.reactor_heat < 0:
            self.reactor_heat = 0.0
        if self.fuel_heat < 0:
            self.fuel_heat = 0.0

    # --- helpers ---

    @staticmethod
    def _temp_to_rf(temp: float, volume: int) -> float:
        """Zamiana temperatury na energię wewnętrzną (RF)."""
        # W oryginale StaticUtils.Energy.getRFFromVolumeAndTemp
        # Przybliżenie: RF = volume * temp * 10 (dobór arbitralny by zachować skalę)
        return volume * temp * 10.0

    @staticmethod
    def _rf_to_temp(rf: float, volume: int) -> float:
        if volume <= 0:
            return 0.0
        return rf / (volume * 10.0)
