"""Symulacja funkcjonalnosci dynam (generatorow energii) Thermal Expansion.

Dynama w 1.7.10 generuja RF z roznych zrodel.
W 1.18.2 generuja FE, ale mechanika paliw jest podobna.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


@dataclass
class DynamoState:
    """Stan dynamo (symulacja)."""
    dynamo_type: str  # steam, magmatic, compression, reactant, enervation
    energy_stored: int = 0
    energy_capacity: int = 40000
    fuel_item: Optional[str] = None
    fuel_fluid: Optional[str] = None
    fuel_amount: int = 0
    output_rate: int = 80  # RF/t base
    efficiency: float = 1.0
    augment_slots: list = None

    def __post_init__(self):
        if self.augment_slots is None:
            self.augment_slots = []
        # Ustawienia specyficzne per typ
        defaults = {
            "steam": {"output_rate": 80, "fuel_fluid": "water"},
            "magmatic": {"output_rate": 80, "fuel_fluid": "lava"},
            "compression": {"output_rate": 80, "fuel_fluid": "fuel"},
            "reactant": {"output_rate": 80, "fuel_item": "redstone"},
            "enervation": {"output_rate": 80, "fuel_item": "energetic_alloy"},
        }
        cfg = defaults.get(self.dynamo_type, {})
        for k, v in cfg.items():
            if getattr(self, k) is None:
                setattr(self, k, v)

    def tick(self) -> int:
        """Symuluje 1 tick. Zwraca wyprodukowana energia (RF)."""
        if not self._has_fuel():
            return 0
        if self.energy_stored >= self.energy_capacity:
            return 0

        produced = int(self.output_rate * self.efficiency)
        self.energy_stored = min(self.energy_capacity, self.energy_stored + produced)
        self._consume_fuel()
        return produced

    def _has_fuel(self) -> bool:
        if self.fuel_item:
            return self.fuel_amount > 0
        if self.fuel_fluid:
            return self.fuel_amount > 0
        return False

    def _consume_fuel(self):
        # Uproszczona konsumpcja: co 100 tickow zuzywa 1 jednostke
        if not hasattr(self, '_tick_counter'):
            self._tick_counter = 0
        self._tick_counter += 1
        if self._tick_counter >= 100:
            self._tick_counter = 0
            self.fuel_amount = max(0, self.fuel_amount - 1)

    def insert_fuel(self, item: Optional[str] = None, fluid: Optional[str] = None, amount: int = 1000):
        """Wklada paliwo."""
        if item:
            self.fuel_item = item
            self.fuel_amount += amount
        if fluid:
            self.fuel_fluid = fluid
            self.fuel_amount += amount


def simulate_dynamo_array(
    dynamo_specs: list[dict],
    ticks: int = 1000,
) -> dict:
    """Symuluje farme dynam generujacych energie.

    Args:
        dynamo_specs: lista dictow z ``type``, ``fuel``, ``amount``
        ticks: liczba tickow do symulacji

    Returns:
        dict z sumaryczna produkcja energii
    """
    dynamos = []
    for spec in dynamo_specs:
        d = DynamoState(dynamo_type=spec["type"])
        d.insert_fuel(item=spec.get("fuel_item"), fluid=spec.get("fuel_fluid"), amount=spec.get("amount", 1000))
        dynamos.append(d)

    total_produced = 0
    for _ in range(ticks):
        for d in dynamos:
            total_produced += d.tick()

    return {
        "ticks": ticks,
        "total_rf": total_produced,
        "avg_rf_per_tick": total_produced / ticks,
        "dynamo_count": len(dynamos),
    }


if __name__ == "__main__":
    print("=== Symulacja farmy dynam ===")
    specs = [
        {"type": "steam", "fuel_fluid": "water", "amount": 5000},
        {"type": "magmatic", "fuel_fluid": "lava", "amount": 5000},
        {"type": "compression", "fuel_fluid": "fuel", "amount": 5000},
    ]
    result = simulate_dynamo_array(specs, ticks=1000)
    for k, v in result.items():
        print(f"  {k}: {v}")
