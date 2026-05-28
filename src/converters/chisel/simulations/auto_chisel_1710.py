"""
Simulation of Chisel Auto Chisel machine behavior.

Based on:
- mod_src/1710/actual_src/1.7.10/Chisel/repo/base/src/main/java/
  team/chisel/common/block/TileAutoChisel.java

The source available in the repo is a newer Chisel codebase, but it preserves
the Auto Chisel contract we need for conversion: chisel slot, target slot,
input/output inventories, progress, and optional FE power.
"""

from __future__ import annotations

from dataclasses import dataclass, field


MAX_PROGRESS = 1024
BASE_PROGRESS = 16
SPEEDUP_PROGRESS = 64
POWER_PER_TICK = 20
ENERGY_CAPACITY = 10_000


@dataclass
class ItemStack:
    item: str
    count: int = 1

    @property
    def empty(self) -> bool:
        return not self.item or self.count <= 0

    def copy(self) -> "ItemStack":
        return ItemStack(self.item, self.count)


@dataclass(frozen=True)
class ChiselVariation:
    item: str
    group: str


@dataclass
class CarvingRegistry:
    variations: dict[str, ChiselVariation]

    def variation(self, item: str) -> ChiselVariation | None:
        return self.variations.get(item)

    def group(self, item: str) -> str | None:
        variation = self.variation(item)
        return variation.group if variation else None


@dataclass
class AutoChiselConfig:
    needs_power: bool = False
    powered_speed: bool = True


@dataclass
class AutoChisel1710:
    registry: CarvingRegistry
    config: AutoChiselConfig = field(default_factory=AutoChiselConfig)
    chisel: ItemStack = field(default_factory=lambda: ItemStack("chisel:iron_chisel"))
    target: ItemStack = field(default_factory=lambda: ItemStack(""))
    inputs: list[ItemStack] = field(default_factory=lambda: [ItemStack("") for _ in range(12)])
    outputs: list[ItemStack] = field(default_factory=lambda: [ItemStack("") for _ in range(12)])
    energy: int = ENERGY_CAPACITY
    progress: float = 0
    source_slot: int = -1
    events: list[str] = field(default_factory=list)

    def get_speed_factor(self) -> float:
        if not self.config.powered_speed:
            return 1.0
        return max(0.0, min(1.0, self.energy / ENERGY_CAPACITY))

    def get_power_progress_per_tick(self) -> int:
        max_per_tick = BASE_PROGRESS + SPEEDUP_PROGRESS if self.config.needs_power else SPEEDUP_PROGRESS
        # Java Math.ceil() equivalent for positive values.
        value = self.get_speed_factor() * max_per_tick
        return int(value) if value == int(value) else int(value) + 1

    def get_usage_per_tick(self) -> int:
        value = self.get_speed_factor() * POWER_PER_TICK
        return int(value) if value == int(value) else int(value) + 1

    def can_output(self, stack: ItemStack) -> bool:
        if stack.empty:
            return True
        remaining = stack.count
        for slot in self.outputs:
            if slot.empty:
                return True
            if slot.item == stack.item and slot.count < 64:
                remaining -= 64 - slot.count
                if remaining <= 0:
                    return True
        return False

    def merge_output(self, stack: ItemStack) -> None:
        if stack.empty:
            return
        remaining = stack.count
        for slot in self.outputs:
            if slot.item == stack.item and slot.count < 64:
                moved = min(64 - slot.count, remaining)
                slot.count += moved
                remaining -= moved
                if remaining == 0:
                    return
        for index, slot in enumerate(self.outputs):
            if slot.empty:
                moved = min(64, remaining)
                self.outputs[index] = ItemStack(stack.item, moved)
                remaining -= moved
                if remaining == 0:
                    return
        if remaining:
            raise RuntimeError("output overflow despite can_output check")

    def _find_source_slot(self, target_variation: ChiselVariation) -> None:
        result = ItemStack(target_variation.item, 1)
        current = self.inputs[self.source_slot] if self.source_slot >= 0 else ItemStack("")
        if not current.empty:
            result.count = current.count
        if not current.empty and self.registry.group(current.item) != target_variation.group:
            current = ItemStack("")
        if not current.empty and not self.can_output(result):
            self.source_slot = -1
            return
        if not current.empty:
            return
        self.source_slot = -1
        for index, stack in enumerate(self.inputs):
            if stack.empty:
                continue
            if self.registry.group(stack.item) != target_variation.group:
                continue
            result.count = stack.count
            if self.can_output(result):
                self.source_slot = index
                self.events.append(f"source:{index}")
                return

    def tick(self) -> None:
        if self.config.needs_power and self.energy <= 0:
            self.events.append("stall:no_power")
            return

        target_variation = self.registry.variation(self.target.item)
        if self.chisel.empty or target_variation is None:
            self.source_slot = -1
            self.progress = 0
            self.events.append("reset:no_chisel_or_target")
            return

        self._find_source_slot(target_variation)
        if self.source_slot < 0:
            self.progress = 0
            self.events.append("idle:no_source")
            return

        source = self.inputs[self.source_slot]
        source_variation = self.registry.variation(source.item)
        if source_variation == target_variation:
            self.inputs[self.source_slot] = ItemStack("")
            self.merge_output(source)
            self.events.append(f"move_same:{source.item}:{source.count}")
            return

        if self.progress < MAX_PROGRESS:
            if not self.config.needs_power:
                self.progress = min(MAX_PROGRESS, self.progress + BASE_PROGRESS)
            to_use = min(MAX_PROGRESS - self.progress, self.get_power_progress_per_tick())
            power_to_use = self.get_usage_per_tick()
            if to_use > 0 and power_to_use > 0:
                if self.config.powered_speed:
                    used = min(self.energy, power_to_use)
                    self.energy -= used
                    self.progress += to_use * (used / power_to_use)
                else:
                    self.progress += to_use
            self.events.append(f"progress:{self.progress:.2f}")
            return

        result = ItemStack(target_variation.item, source.count)
        if not self.can_output(result):
            self.source_slot = -1
            self.progress = 0
            self.events.append("stall:output_full")
            return
        self.inputs[self.source_slot] = ItemStack("")
        self.merge_output(result)
        self.events.append(f"craft:{source.item}->{result.item}:{result.count}")
        self.source_slot = (self.source_slot + 1) % len(self.inputs)
        self.progress = 0

    def run_until_idle_or(self, ticks: int) -> list[str]:
        for _ in range(ticks):
            self.tick()
        return self.events

