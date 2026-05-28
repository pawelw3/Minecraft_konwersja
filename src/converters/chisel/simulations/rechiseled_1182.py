"""
Simulation of Rechiseled chisel item block selection.

Based on:
- mod_src/118/actual_src/1.18.2/Rechiseled/repo/src/main/java/
  com/supermartijn642/rechiseled/ChiselItem.java
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum


class Shape(str, Enum):
    BLOCK = "block"
    STAIRS = "stairs"
    SLAB = "slab"


class Axis(str, Enum):
    X = "x"
    Y = "y"
    Z = "z"


@dataclass(frozen=True)
class Direction:
    axis: Axis
    step: tuple[int, int, int]


EAST = Direction(Axis.X, (1, 0, 0))
UP = Direction(Axis.Y, (0, 1, 0))
SOUTH = Direction(Axis.Z, (0, 0, 1))


@dataclass(frozen=True)
class ItemWithWorth:
    item: str
    worth: float = 1.0


@dataclass
class ChiselingEntry:
    regular: dict[Shape, ItemWithWorth] = field(default_factory=dict)
    connecting: dict[Shape, ItemWithWorth] = field(default_factory=dict)

    def all_items(self) -> dict[str, tuple[Shape, bool, float]]:
        items: dict[str, tuple[Shape, bool, float]] = {}
        for shape, item in self.regular.items():
            items[item.item] = (shape, False, item.worth)
        for shape, item in self.connecting.items():
            items[item.item] = (shape, True, item.worth)
        return items

    def contains(self, item: str) -> bool:
        return item in self.all_items()


@dataclass
class ChiselingRecipe:
    entries: list[ChiselingEntry]

    def get_worth(self, block: str) -> float | None:
        for entry in self.entries:
            item = entry.all_items().get(block)
            if item is not None:
                return item[2]
        return None

    def find_shape(self, block: str) -> Shape | None:
        for entry in self.entries:
            item = entry.all_items().get(block)
            if item is not None:
                return item[0]
        return None

    def contains(self, block: str) -> bool:
        return self.find_shape(block) is not None

    def filter_block_for_shape(self, filter_item: str, target_shape: Shape) -> str | None:
        for entry in self.entries:
            if not entry.contains(filter_item):
                continue
            for source_map in (entry.regular, entry.connecting):
                if any(item.item == filter_item for item in source_map.values()):
                    target = source_map.get(target_shape)
                    return target.item if target else None
        return None

    def alternatives(self, current: str, shape: Shape, worth: float) -> list[str]:
        result: list[str] = []
        for entry in self.entries:
            if entry.contains(current):
                continue
            for source_map in (entry.regular, entry.connecting):
                item = source_map.get(shape)
                if item and item.worth == worth:
                    result.append(item.item)
        return result


@dataclass
class RecipeManager:
    by_item: dict[str, ChiselingRecipe]

    def recipe_for_item(self, item: str) -> ChiselingRecipe | None:
        return self.by_item.get(item)

    @classmethod
    def from_recipes(cls, recipes: list[ChiselingRecipe]) -> "RecipeManager":
        by_item: dict[str, ChiselingRecipe] = {}
        for recipe in recipes:
            for entry in recipe.entries:
                for item in entry.all_items():
                    by_item[item] = recipe
        return cls(by_item)


@dataclass
class SimpleWorld:
    blocks: dict[tuple[int, int, int], str]
    occluded_faces: set[tuple[int, int, int]] = field(default_factory=set)

    def get_block(self, pos: tuple[int, int, int]) -> str:
        return self.blocks.get(pos, "minecraft:air")

    def is_occluded(self, pos: tuple[int, int, int]) -> bool:
        return pos in self.occluded_faces


def add_pos(left: tuple[int, int, int], right: tuple[int, int, int]) -> tuple[int, int, int]:
    return (left[0] + right[0], left[1] + right[1], left[2] + right[2])


def find_chiselable_blocks(
    world: SimpleWorld,
    recipes: RecipeManager,
    targeted_pos: tuple[int, int, int],
    side: Direction,
    filter_item: str | None = None,
    is_shift_down: bool = False,
) -> list[tuple[tuple[int, int, int], str]]:
    if filter_item and not filter_item.startswith(("minecraft:", "rechiseled:")):
        return []

    recipe = recipes.recipe_for_item(filter_item) if filter_item else None
    if filter_item and recipe is None:
        return []

    targeted_block = world.get_block(targeted_pos)
    targeted_recipe = recipes.recipe_for_item(targeted_block)
    if recipe is None:
        recipe = targeted_recipe
        if recipe is None:
            return []
    elif recipe is not targeted_recipe:
        return []

    target_shape = recipe.find_shape(targeted_block)
    filter_block = recipe.filter_block_for_shape(filter_item, target_shape) if filter_item and target_shape else None
    if filter_item and filter_block is None:
        return []

    x_range = 0 if is_shift_down or side.axis == Axis.X else 1
    y_range = 0 if is_shift_down or side.axis == Axis.Y else 1
    z_range = 0 if is_shift_down or side.axis == Axis.Z else 1
    result: list[tuple[tuple[int, int, int], str]] = []

    for x in range(-x_range, x_range + 1):
        for y in range(-y_range, y_range + 1):
            for z in range(-z_range, z_range + 1):
                pos = add_pos(targeted_pos, (x, y, z))
                state = world.get_block(pos)
                if state == filter_block:
                    continue
                worth = recipe.get_worth(state)
                if worth is None:
                    continue
                front_pos = add_pos(pos, side.step)
                if world.is_occluded(front_pos):
                    continue
                shape = recipe.find_shape(state)
                if target_shape is not None and shape != target_shape:
                    continue
                if filter_block:
                    result.append((pos, filter_block))
                    continue
                alternatives = recipe.alternatives(state, shape, worth)
                if alternatives:
                    result.append((pos, alternatives[0]))
    return result

