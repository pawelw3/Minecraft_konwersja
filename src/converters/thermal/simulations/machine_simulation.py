"""Symulacja funkcjonalnosci maszyn Thermal Expansion.

Maszyny Thermal 1.7.10 przetwarzaja itemy/plyny zuzyciem energii (RF).
W 1.18.2 mechanika jest identyczna (FE zamiast RF), ale NBT sie zmienilo.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional


@dataclass
class MachineState:
    """Stan maszyny Thermal Expansion (symulacja)."""
    machine_type: str  # np. "furnace", "pulverizer", "smelter"
    energy_stored: int = 0
    energy_capacity: int = 40000  # podstawowy capacity w 1.7.10
    progress: int = 0
    progress_max: int = 200  # ticki do przetworzenia
    input_item: Optional[str] = None
    output_item: Optional[str] = None
    output_secondary: Optional[str] = None  # secondary output (np. sawmill)
    secondary_chance: float = 0.0
    tank_fluid: Optional[str] = None  # dla maszyn z plynami
    tank_amount: int = 0
    tank_capacity: int = 4000
    redstone_control: int = 0  # 0=ignored, 1=low, 2=high
    side_config: list = field(default_factory=lambda: [0]*6)  # face config
    augment_slots: list = field(default_factory=list)

    # Tier: 0=basic, 1=hardened, 2=reinforced, 3=resonant, 4=creative
    tier: int = 0

    def tick(self, rf_per_tick: int = 20) -> bool:
        """Symuluje 1 tick maszyny. Zwraca True jesli przetworzono item."""
        if self.input_item is None:
            return False
        if self.redstone_control == 1 and self._redstone_signal:
            return False
        if self.redstone_control == 2 and not self._redstone_signal:
            return False
        if self.energy_stored < rf_per_tick:
            return False

        self.energy_stored -= rf_per_tick
        self.progress += 1

        if self.progress >= self.progress_max:
            self._finish_process()
            return True
        return False

    def _finish_process(self):
        """Kanczy proces przetwarzania."""
        self.progress = self.progress_max
        self.input_item = None
        # W prawdziwej grze: output idzie do slotu output
        # Symulacja: zostawiamy output_item ustawiony

    def can_process(self, input_item: str) -> bool:
        """Sprawdza czy maszyna moze przetworzyc dany item."""
        recipes = {
            "furnace": ["minecraft:iron_ore", "minecraft:gold_ore", "minecraft:sand", "thermal:iron_dust", "thermal:gold_dust"],
            "pulverizer": ["minecraft:iron_ore", "minecraft:gold_ore", "minecraft:cobblestone"],
            "smelter": ["minecraft:iron_ore", "minecraft:gold_ore", "minecraft:sand"],
            "sawmill": ["minecraft:oak_log", "minecraft:birch_log"],
            "crucible": ["minecraft:cobblestone", "minecraft:redstone_block"],
            "transposer": ["minecraft:bucket", "minecraft:glass_bottle"],
            "insolator": ["minecraft:wheat_seeds", "minecraft:potato"],
        }
        valid = recipes.get(self.machine_type, [])
        return input_item in valid

    def insert_item(self, item: str) -> bool:
        """Wklada item do maszyny."""
        if self.input_item is not None:
            return False
        if not self.can_process(item):
            return False
        self.input_item = item
        # Ustaw output na podstawie receptury
        self._set_output(item)
        return True

    def _set_output(self, input_item: str):
        """Ustawia output na podstawie receptury."""
        outputs = {
            "furnace": {
                "minecraft:iron_ore": "minecraft:iron_ingot",
                "minecraft:gold_ore": "minecraft:gold_ingot",
                "minecraft:sand": "minecraft:glass",
                "thermal:iron_dust": "minecraft:iron_ingot",
                "thermal:gold_dust": "minecraft:gold_ingot",
            },
            "pulverizer": {
                "minecraft:iron_ore": "thermal:iron_dust",
                "minecraft:gold_ore": "thermal:gold_dust",
                "minecraft:cobblestone": "minecraft:sand",
            },
            "smelter": {
                "minecraft:iron_ore": "minecraft:iron_ingot",
                "minecraft:gold_ore": "minecraft:gold_ingot",
            },
            "sawmill": {
                "minecraft:oak_log": "minecraft:oak_planks",
                "minecraft:birch_log": "minecraft:birch_planks",
            },
        }
        recipe = outputs.get(self.machine_type, {})
        self.output_item = recipe.get(input_item)

    @property
    def _redstone_signal(self) -> bool:
        return False  # stub


def simulate_ore_processing_line(
    input_ore: str = "minecraft:iron_ore",
    energy_available: int = 100000,
) -> dict:
    """Symuluje linie przetwarzania: Pulverizer -> Furnace (2x output).

    W Thermal 1.7.10 standardowy pipeline to:
    1. Pulverizer: ruda -> pył (2x przy wzmocnieniu)
    2. Furnace: pył -> sztabka

    Zwraca dict z wynikami.
    """
    pulverizer = MachineState("pulverizer", energy_stored=energy_available)
    furnace = MachineState("furnace", energy_stored=energy_available)

    # Krok 1: Pulverizer
    pulverizer.insert_item(input_ore)
    ticks_pulv = 0
    while pulverizer.progress < pulverizer.progress_max and ticks_pulv < 1000:
        pulverizer.tick(rf_per_tick=40)
        ticks_pulv += 1

    # Krok 2: Furnace
    dust = pulverizer.output_item
    if dust:
        furnace.insert_item(dust)
        ticks_furn = 0
        while furnace.progress < furnace.progress_max and ticks_furn < 1000:
            furnace.tick(rf_per_tick=20)
            ticks_furn += 1

    return {
        "input": input_ore,
        "pulverizer_output": pulverizer.output_item,
        "furnace_output": furnace.output_item,
        "ticks_pulverizer": ticks_pulv,
        "ticks_furnace": ticks_furn,
        "energy_consumed": (ticks_pulv * 40) + (ticks_furn * 20),
        "yield_multiplier": 2.0 if "dust" in str(pulverizer.output_item) else 1.0,
    }


def simulate_induction_smelter(
    primary: str = "minecraft:iron_ingot",
    secondary: str = "thermal:nickel_ingot",
    energy_available: int = 50000,
) -> dict:
    """Symuluje Induction Smelter: 2 itemy -> stop (alloy).

    Przyklad: Iron + Nickel -> Invar Ingot
    """
    smelter = MachineState("smelter", energy_stored=energy_available)
    # Symulacja wstawienia obu skladnikow
    smelter.insert_item(primary)
    smelter.output_item = "thermal:invar_ingot"  # forced alloy output

    ticks = 0
    while smelter.progress < smelter.progress_max and ticks < 1000:
        smelter.tick(rf_per_tick=40)
        ticks += 1

    return {
        "primary": primary,
        "secondary": secondary,
        "output": smelter.output_item,
        "ticks": ticks,
        "energy_consumed": ticks * 40,
    }


if __name__ == "__main__":
    # Demo symulacji
    print("=== Symulacja ore processing (Iron Ore) ===")
    result = simulate_ore_processing_line("minecraft:iron_ore")
    for k, v in result.items():
        print(f"  {k}: {v}")

    print("\n=== Symulacja Induction Smelter (Invar) ===")
    result = simulate_induction_smelter()
    for k, v in result.items():
        print(f"  {k}: {v}")
