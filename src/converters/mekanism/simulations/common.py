"""
Wspolne modele do symulacji Mekanism.

Symulacje sa celowo male i deterministyczne. Nie probuja byc pelnym silnikiem
Mekanism; ich zadaniem jest uchwycic semantyke, ktora musi przetrwac migracje
NBT 1.7.10 -> 1.18.2.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class Version(Enum):
    V1710 = "1.7.10"
    V1182 = "1.18.2"


class Tier(Enum):
    BASIC = "basic"
    ADVANCED = "advanced"
    ELITE = "elite"
    ULTIMATE = "ultimate"
    CREATIVE = "creative"


@dataclass(frozen=True)
class ItemStack:
    item_id: str
    count: int = 1
    nbt: dict[str, Any] = field(default_factory=dict)

    def is_empty(self) -> bool:
        return self.count <= 0 or self.item_id == ""

    def with_count(self, count: int) -> "ItemStack":
        return ItemStack(self.item_id, count, dict(self.nbt))

    def add(self, amount: int) -> "ItemStack":
        return self.with_count(self.count + amount)

    def remove(self, amount: int) -> "ItemStack":
        return self.with_count(max(0, self.count - amount))


@dataclass
class StackTank:
    """Minimalny model energy/fluid/gas/chemical tanku."""

    content_id: str | None
    amount: int | float
    capacity: int | float

    @property
    def fill_ratio(self) -> float:
        if self.capacity <= 0:
            return 0.0
        return max(0.0, min(1.0, float(self.amount) / float(self.capacity)))

    def receive(self, content_id: str, amount: int | float) -> int | float:
        if self.content_id not in (None, content_id):
            return 0
        accepted = min(amount, self.capacity - self.amount)
        if accepted > 0:
            self.content_id = content_id
            self.amount += accepted
        return accepted

    def draw(self, amount: int | float) -> int | float:
        drawn = min(amount, self.amount)
        self.amount -= drawn
        if self.amount <= 0:
            self.amount = 0
            self.content_id = None
        return drawn


@dataclass
class SimulationEvent:
    step: str
    inputs: list[ItemStack] = field(default_factory=list)
    outputs: list[ItemStack] = field(default_factory=list)
    consumed: dict[str, int | float] = field(default_factory=dict)
    notes: list[str] = field(default_factory=list)


def assert_same_item_count(left: ItemStack, right: ItemStack) -> None:
    if left.item_id != right.item_id or left.count != right.count:
        raise AssertionError(f"Different stacks: {left!r} != {right!r}")
