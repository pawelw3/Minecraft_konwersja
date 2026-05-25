"""Symulacja Cyanite Reprocessor dla Big Reactors 1.7.10 / Bigger Reactors 1.18.2.

Bazuje na kodzie źródłowym w projekcie:
- 1.7.10: `mod_src/1710/actual_src/1.7.10/BigReactors/repo/src/main/java/erogenousbeef/bigreactors/common/tileentity/TileEntityCyaniteReprocessor.java`
- 1.18.2: `mod_src/118/actual_src/1.18.2/BiggerReactors/repo/src/main/java/net/roguelogix/biggerreactors/machine/tiles/CyaniteReprocessorTile.java`
          `mod_src/118/actual_src/1.18.2/BiggerReactors/repo/src/main/java/net/roguelogix/biggerreactors/machine/state/CyaniteReprocessorState.java`

Logika w obu wersjach jest zasadniczo taka sama:
- Slot INLET: waste (cyanite)
- Slot OUTLET: fuel (blutonium w 1.7.10; w 1.18.2 nazewnictwo może być inne)
- 1 bucket wody na cykl
- Cykl: 200 ticks (10 s)
- Koszt energii: 2000 RF na cykl
- 2 ingoty cyanite → 1 ingot blutonium
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


@dataclass
class ReprocessorConfig:
    cycle_length: int = 200          # ticks
    cycle_energy_cost: int = 2000    # RF
    max_energy_stored: int = 10000   # RF
    fluid_consumed: int = 1000       # mB (1 bucket)
    ingots_consumed: int = 2
    tank_capacity: int = 5000        # mB
    inventory_stack_limit: int = 64


class CyaniteReprocessorSimulation:
    """Symulacja Cyanite Reprocessor — wspólna dla 1.7.10 i 1.18.2.

    Różnice w NBT / nazwach są obsługiwane przez parametry konfiguracyjne.
    """

    def __init__(self, config: Optional[ReprocessorConfig] = None):
        self.config = config or ReprocessorConfig()

        # Inventory
        self.inlet_stack_size = 0   # cyanite (waste)
        self.outlet_stack_size = 0  # blutonium (fuel)

        # Fluid
        self.water = 0

        # Energy
        self.energy_stored = 0

        # Progress
        self.progress = 0           # 0 .. cycle_length
        self.active = False

        # Stats
        self.cycles_completed = 0

    def insert_cyanite(self, amount: int) -> int:
        """Dodaje cyanite do slotu INLET. Zwraca ile nie zmieściło się."""
        space = self.config.inventory_stack_limit - self.inlet_stack_size
        added = min(amount, space)
        self.inlet_stack_size += added
        return amount - added

    def insert_water(self, amount: int) -> int:
        """Dodaje wodę do zbiornika. Zwraca ile nie zmieściło się."""
        space = self.config.tank_capacity - self.water
        added = min(amount, space)
        self.water += added
        return amount - added

    def charge_energy(self, amount: int) -> int:
        """Ładuje energię. Zwraca ile nie zmieściło się."""
        space = self.config.max_energy_stored - self.energy_stored
        added = min(amount, space)
        self.energy_stored += added
        return amount - added

    def _can_begin_cycle(self) -> bool:
        """Czy są składniki by rozpocząć cykl?"""
        if self.water < self.config.fluid_consumed:
            return False
        if self.inlet_stack_size < self.config.ingots_consumed:
            return False
        if self.outlet_stack_size >= self.config.inventory_stack_limit:
            return False
        return True

    def tick(self):
        """Jeden tick maszyny."""
        energy_per_tick = self.config.cycle_energy_cost / self.config.cycle_length

        if self.progress > 0:
            # Cykl trwa
            if self.energy_stored >= energy_per_tick:
                self.energy_stored -= int(energy_per_tick)
                self.progress += 1
            else:
                # Brak energii — zatrzymanie (w oryginale maszyna się zatrzymuje)
                self.active = False
                return

            if self.progress >= self.config.cycle_length:
                self._finish_cycle()
        else:
            # Spróbuj rozpocząć nowy cykl
            if self._can_begin_cycle() and self.energy_stored >= energy_per_tick:
                self.progress = 1
                self.active = True
                self.energy_stored -= int(energy_per_tick)
            else:
                self.active = False

    def _finish_cycle(self):
        """Kończy cykl i produkuje wyjście."""
        self.progress = 0
        self.inlet_stack_size -= self.config.ingots_consumed
        self.water -= self.config.fluid_consumed
        self.outlet_stack_size = min(
            self.config.inventory_stack_limit,
            self.outlet_stack_size + 1,
        )
        self.cycles_completed += 1
        self.active = False

    def get_state(self) -> dict:
        return {
            "inlet": self.inlet_stack_size,
            "outlet": self.outlet_stack_size,
            "water": self.water,
            "energy": self.energy_stored,
            "progress": self.progress,
            "progress_total": self.config.cycle_length,
            "active": self.active,
            "cycles_completed": self.cycles_completed,
        }

    @staticmethod
    def convert_inventory_1710_to_1182(
        inlet_count: int,
        outlet_count: int,
        water_mb: int,
        progress: int,
    ) -> dict:
        """Konwersja stanu inventory Cyanite Reprocessor z 1.7.10 na 1.18.2.

        W 1.18.2 nazewnictwo jest takie same (cyanite/blutonium), ale
        system inventory jest oparty na ItemStack/ItemHandler (Forge 1.18.2).
        Wartości progresu i ilości pozostają bez zmian.
        """
        return {
            "inlet_count": inlet_count,
            "outlet_count": outlet_count,
            "water_mb": water_mb,
            "progress": progress,
        }
