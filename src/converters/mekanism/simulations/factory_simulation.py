"""
Symulacja Factory Mekanism.

W 1.7.10 `TileEntityFactory`:
- ma `BASE_TICKS_REQUIRED = 200` i `ticksRequired = 200` bez speed upgrade,
- zapisuje `recipeType`, `recipeTicks` oraz `progress0`, `progress1`, ...,
- liczba torow zalezy od `FactoryTier`: BASIC=3, ADVANCED=5, ELITE=7.

W 1.18.2 `FactoryTier` ma te same 3/5/7 oraz dodatkowy ULTIMATE=9. Stary
`UltimateSmeltingFactory` z 1.7.10 jest nazwa TE dla elite factory, a nie
target `ultimate_*_factory`.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum

from .common import ItemStack, Tier


BASE_TICKS_REQUIRED = 200


class FactoryRecipeType(Enum):
    SMELTING = (0, "smelting", "energized_smelter")
    ENRICHING = (1, "enriching", "enrichment_chamber")
    CRUSHING = (2, "crushing", "crusher")
    COMPRESSING = (3, "compressing", "osmium_compressor")
    COMBINING = (4, "combining", "combiner")
    PURIFYING = (5, "purifying", "purification_chamber")
    INJECTING = (6, "injecting", "chemical_injection_chamber")
    INFUSING = (7, "infusing", "metallurgic_infuser")

    @property
    def ordinal(self) -> int:
        return self.value[0]

    @property
    def factory_name(self) -> str:
        return self.value[1]


FACTORY_PROCESSES_1710: dict[Tier, int] = {
    Tier.BASIC: 3,
    Tier.ADVANCED: 5,
    Tier.ELITE: 7,
}

FACTORY_PROCESSES_1182: dict[Tier, int] = {
    Tier.BASIC: 3,
    Tier.ADVANCED: 5,
    Tier.ELITE: 7,
    Tier.ULTIMATE: 9,
}


SIMPLE_RECIPES: dict[FactoryRecipeType, dict[str, ItemStack]] = {
    FactoryRecipeType.SMELTING: {
        "mekanism:dust_osmium": ItemStack("mekanism:ingot_osmium"),
        "Mekanism:OsmiumDust": ItemStack("Mekanism:Ingot:1"),
    },
    FactoryRecipeType.ENRICHING: {
        "mekanism:dirty_dust_osmium": ItemStack("mekanism:dust_osmium"),
        "Mekanism:DirtyOsmiumDust": ItemStack("Mekanism:OsmiumDust"),
    },
    FactoryRecipeType.CRUSHING: {
        "mekanism:clump_osmium": ItemStack("mekanism:dirty_dust_osmium"),
        "Mekanism:OsmiumClump": ItemStack("Mekanism:DirtyOsmiumDust"),
    },
}


@dataclass
class FactoryLane:
    input_stack: ItemStack | None = None
    output_stack: ItemStack | None = None
    progress: int = 0

    def can_insert_output(self, output: ItemStack) -> bool:
        return self.output_stack is None or self.output_stack.item_id == output.item_id


@dataclass
class Factory1710:
    tier: Tier
    recipe_type: FactoryRecipeType
    lanes: list[FactoryLane] = field(default_factory=list)
    energy: float = 0.0
    ticks_required: int = BASE_TICKS_REQUIRED

    def __post_init__(self) -> None:
        lane_count = FACTORY_PROCESSES_1710[self.tier]
        if not self.lanes:
            self.lanes = [FactoryLane() for _ in range(lane_count)]
        self.lanes = normalize_lanes(self.lanes, lane_count)

    def tick(self) -> int:
        operations = 0
        for lane in self.lanes:
            if self._can_operate(lane):
                lane.progress += 1
                self.energy = max(0.0, self.energy - 1.0)
                if lane.progress >= self.ticks_required:
                    self._operate(lane)
                    operations += 1
            else:
                lane.progress = 0
        return operations

    def run_ticks(self, ticks: int) -> int:
        return sum(self.tick() for _ in range(ticks))

    def _recipe_output(self, stack: ItemStack) -> ItemStack | None:
        recipe = SIMPLE_RECIPES.get(self.recipe_type, {})
        output = recipe.get(stack.item_id)
        return output.with_count(stack.count) if output else None

    def _can_operate(self, lane: FactoryLane) -> bool:
        if self.energy <= 0 or lane.input_stack is None or lane.input_stack.is_empty():
            return False
        output = self._recipe_output(lane.input_stack)
        return output is not None and lane.can_insert_output(output)

    def _operate(self, lane: FactoryLane) -> None:
        assert lane.input_stack is not None
        output = self._recipe_output(lane.input_stack)
        assert output is not None
        lane.input_stack = lane.input_stack.remove(1)
        produced = output.with_count(1)
        if lane.output_stack is None:
            lane.output_stack = produced
        else:
            lane.output_stack = lane.output_stack.add(1)
        lane.progress = 0

    def to_1182(self) -> "Factory1182":
        return Factory1182(
            tier=self.tier,
            recipe_type=self.recipe_type,
            lanes=[FactoryLane(l.input_stack, l.output_stack, l.progress) for l in self.lanes],
            energy=self.energy,
            ticks_required=self.ticks_required,
        )

    def legacy_nbt_summary(self) -> dict[str, int]:
        data = {"recipeType": self.recipe_type.ordinal, "recipeTicks": 0}
        data.update({f"progress{i}": lane.progress for i, lane in enumerate(self.lanes)})
        return data


@dataclass
class Factory1182(Factory1710):
    def __post_init__(self) -> None:
        lane_count = FACTORY_PROCESSES_1182[self.tier]
        if not self.lanes:
            self.lanes = [FactoryLane() for _ in range(lane_count)]
        self.lanes = normalize_lanes(self.lanes, lane_count)

    @property
    def target_block_id(self) -> str:
        return factory_target_id(self.tier, self.recipe_type)


def normalize_lanes(lanes: list[FactoryLane], lane_count: int) -> list[FactoryLane]:
    copied = list(lanes[:lane_count])
    while len(copied) < lane_count:
        copied.append(FactoryLane())
    return copied


def factory_target_id(tier: Tier, recipe_type: FactoryRecipeType) -> str:
    if tier is Tier.CREATIVE:
        raise ValueError("Factories do not have creative tier")
    return f"mekanism:{tier.value}_{recipe_type.factory_name}_factory"


def compare_factory_progress() -> tuple[Factory1710, Factory1182]:
    legacy = Factory1710(
        tier=Tier.ELITE,
        recipe_type=FactoryRecipeType.SMELTING,
        lanes=[FactoryLane(ItemStack("Mekanism:OsmiumDust", 2), progress=199)],
        energy=20,
    )
    modern = legacy.to_1182()
    legacy.tick()
    modern.tick()
    if legacy.lanes[0].output_stack != ItemStack("Mekanism:Ingot:1", 1):
        raise AssertionError("Legacy factory did not finish lane at tick 200")
    if modern.lanes[0].progress != legacy.lanes[0].progress:
        raise AssertionError("Converted factory progress diverged")
    return legacy, modern


if __name__ == "__main__":
    old, new = compare_factory_progress()
    print(old.legacy_nbt_summary())
    print(new.target_block_id)
