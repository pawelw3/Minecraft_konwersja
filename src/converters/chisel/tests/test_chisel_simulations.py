from src.converters.chisel.simulations.auto_chisel_1710 import (
    AutoChisel1710,
    AutoChiselConfig,
    CarvingRegistry,
    ChiselVariation,
    ItemStack,
    MAX_PROGRESS,
)
from src.converters.chisel.simulations.rechiseled_1182 import (
    ChiselingEntry,
    ChiselingRecipe,
    EAST,
    ItemWithWorth,
    RecipeManager,
    Shape,
    SimpleWorld,
    find_chiselable_blocks,
)


def registry() -> CarvingRegistry:
    return CarvingRegistry(
        {
            "chisel:stone_raw": ChiselVariation("chisel:stone_raw", "stone"),
            "chisel:stone_tiles": ChiselVariation("chisel:stone_tiles", "stone"),
            "chisel:marble_raw": ChiselVariation("chisel:marble_raw", "marble"),
        }
    )


def test_auto_chisel_converts_input_after_progress_reaches_max():
    machine = AutoChisel1710(
        registry=registry(),
        config=AutoChiselConfig(needs_power=False, powered_speed=False),
        target=ItemStack("chisel:stone_tiles"),
    )
    machine.inputs[0] = ItemStack("chisel:stone_raw", 5)

    machine.run_until_idle_or(80)

    assert machine.outputs[0] == ItemStack("chisel:stone_tiles", 5)
    assert machine.inputs[0].empty
    assert any(event == "craft:chisel:stone_raw->chisel:stone_tiles:5" for event in machine.events)


def test_auto_chisel_moves_same_variation_without_progress():
    machine = AutoChisel1710(registry=registry(), target=ItemStack("chisel:stone_tiles"))
    machine.inputs[0] = ItemStack("chisel:stone_tiles", 3)

    machine.tick()

    assert machine.progress == 0
    assert machine.outputs[0] == ItemStack("chisel:stone_tiles", 3)
    assert "move_same:chisel:stone_tiles:3" in machine.events


def test_auto_chisel_stalls_without_required_power():
    machine = AutoChisel1710(
        registry=registry(),
        config=AutoChiselConfig(needs_power=True, powered_speed=True),
        target=ItemStack("chisel:stone_tiles"),
        energy=0,
    )
    machine.inputs[0] = ItemStack("chisel:stone_raw", 1)

    machine.tick()

    assert machine.progress == 0
    assert machine.outputs[0].empty
    assert machine.events == ["stall:no_power"]


def test_auto_chisel_powered_progress_consumes_energy():
    machine = AutoChisel1710(
        registry=registry(),
        config=AutoChiselConfig(needs_power=True, powered_speed=True),
        target=ItemStack("chisel:stone_tiles"),
        energy=10_000,
    )
    machine.inputs[0] = ItemStack("chisel:stone_raw", 1)

    machine.tick()

    assert 0 < machine.progress <= MAX_PROGRESS
    assert machine.energy < 10_000


def rechiseled_manager() -> RecipeManager:
    recipe = ChiselingRecipe(
        [
            ChiselingEntry(
                regular={
                    Shape.BLOCK: ItemWithWorth("minecraft:stone"),
                    Shape.STAIRS: ItemWithWorth("minecraft:stone_stairs"),
                },
            ),
            ChiselingEntry(
                regular={
                    Shape.BLOCK: ItemWithWorth("rechiseled:stone_tiles"),
                    Shape.STAIRS: ItemWithWorth("rechiseled:stone_tiles_stairs"),
                },
            ),
            ChiselingEntry(
                connecting={
                    Shape.BLOCK: ItemWithWorth("rechiseled:stone_bricks_connecting"),
                    Shape.STAIRS: ItemWithWorth("rechiseled:stone_bricks_stairs_connecting"),
                },
            ),
        ]
    )
    return RecipeManager.from_recipes([recipe])


def test_rechiseled_left_click_selects_visible_3x3_plane():
    world = SimpleWorld(
        {
            (0, y, z): "minecraft:stone"
            for y in (-1, 0, 1)
            for z in (-1, 0, 1)
        },
        occluded_faces={(1, 1, 1)},
    )

    changes = find_chiselable_blocks(world, rechiseled_manager(), (0, 0, 0), EAST)

    assert len(changes) == 8
    assert ((0, 1, 1), "rechiseled:stone_tiles") not in changes
    assert all(new_block == "rechiseled:stone_tiles" for _, new_block in changes)


def test_rechiseled_shift_limits_conversion_to_single_target():
    world = SimpleWorld(
        {
            (0, y, z): "minecraft:stone"
            for y in (-1, 0, 1)
            for z in (-1, 0, 1)
        }
    )

    changes = find_chiselable_blocks(world, rechiseled_manager(), (0, 0, 0), EAST, is_shift_down=True)

    assert changes == [((0, 0, 0), "rechiseled:stone_tiles")]


def test_rechiseled_filter_preserves_target_shape():
    world = SimpleWorld({(0, 0, 0): "minecraft:stone_stairs"})

    changes = find_chiselable_blocks(
        world,
        rechiseled_manager(),
        (0, 0, 0),
        EAST,
        filter_item="rechiseled:stone_tiles",
        is_shift_down=True,
    )

    assert changes == [((0, 0, 0), "rechiseled:stone_tiles_stairs")]

