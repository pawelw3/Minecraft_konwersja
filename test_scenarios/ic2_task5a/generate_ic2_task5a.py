#!/usr/bin/env python3
"""Generate IC2 Task 5A test patches for 1.7.10 world editing.

Produces a Hephaistos-compatible patch JSON that places representative IC2
blocks and tile-entities with varied states (inventory, energy, progress).
"""
from __future__ import annotations

import json
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[2]
SCENARIO_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(PROJECT_ROOT))
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from src.converters.mekanism.analyze_map_coverage import load_block_registry  # noqa: E402

WORLD_PATH = PROJECT_ROOT / "mapa_1710"
SOURCE_PATCH = SCENARIO_DIR / "ic2_task5a_source_patch_1710.json"


@dataclass(frozen=True)
class Sample:
    name: str
    block_id_str: str
    metadata: int
    x: int
    y: int
    z: int
    nbt: dict[str, Any] | None
    category: str
    purpose: str


def ic2_numeric_registry() -> dict[str, int]:
    registry = load_block_registry(WORLD_PATH)
    return {name: numeric_id for numeric_id, name in registry.items() if name.startswith("IC2:")}


def item_stack(item_id: str, count: int = 1, damage: int = 0, slot: int | None = None) -> dict[str, Any]:
    stack: dict[str, Any] = {"id": item_id, "Count": count}
    if damage:
        stack["Damage"] = damage
    if slot is not None:
        stack["Slot"] = slot
    return stack


def inv_slots_1input_1output(input_item: dict, output_item: dict, battery: dict | None = None) -> dict[str, Any]:
    slots: dict[str, Any] = {
        "input": {"0": input_item},
        "output": {"0": output_item},
    }
    if battery:
        slots["battery"] = {"0": battery}
    slots["upgrade"] = {}
    slots["discharge"] = {}
    return {"InvSlots": slots}


def standard_machine_nbt(
    te_id: str,
    x: int, y: int, z: int,
    facing: int = 3,
    active: bool = True,
    progress: int = 100,
    energy: float = 500.0,
    inv_slots: dict | None = None,
) -> dict[str, Any]:
    nbt: dict[str, Any] = {
        "id": te_id,
        "x": x,
        "y": y,
        "z": z,
        "facing": facing,
        "active": active,
        "progress": progress,
        "energy": energy,
    }
    if inv_slots:
        nbt.update(inv_slots)
    return nbt


def build_samples(offset_x: int, offset_y: int, offset_z: int) -> list[Sample]:
    samples: list[Sample] = []
    reg = ic2_numeric_registry()

    def add(
        name: str,
        block_name: str,
        meta: int,
        dx: int,
        dz: int,
        nbt: dict[str, Any] | None = None,
        category: str = "block",
        purpose: str = "",
    ) -> None:
        x = offset_x + dx
        y = offset_y
        z = offset_z + dz
        samples.append(Sample(name, block_name, meta, x, y, z, nbt, category, purpose))

    # Row 0: Machines (blockMachine)
    row = 0
    add("machine_block", "IC2:blockMachine", 0, 0, row, None, "decoration", "Crafting block, no TE")

    iron_ore = item_stack("minecraft:iron_ore", 8)
    iron_dust = item_stack("IC2:itemDust", 4, damage=5)  # iron dust meta varies
    battery = item_stack("IC2:itemBatChargeRE", 1)
    add(
        "macerator_with_ore",
        "IC2:blockMachine",
        3,
        1,
        row,
        standard_machine_nbt(
            "ic2.core.block.machine.tileentity.TileEntityMacerator",
            offset_x + 1, offset_y, offset_z + row,
            facing=3, active=True, progress=120, energy=800.0,
            inv_slots=inv_slots_1input_1output(iron_ore, iron_dust, battery),
        ),
        "machine",
        "Macerator processing iron ore",
    )

    cobble = item_stack("minecraft:cobblestone", 16)
    stone = item_stack("minecraft:stone", 16)
    add(
        "electric_furnace_smelting",
        "IC2:blockMachine",
        2,
        2,
        row,
        standard_machine_nbt(
            "ic2.core.block.machine.tileentity.TileEntityElectricFurnace",
            offset_x + 2, offset_y, offset_z + row,
            facing=3, active=True, progress=80, energy=600.0,
            inv_slots=inv_slots_1input_1output(cobble, stone, battery),
        ),
        "machine",
        "Electric furnace smelting cobble",
    )

    add(
        "compressor_empty",
        "IC2:blockMachine",
        5,
        3,
        row,
        standard_machine_nbt(
            "ic2.core.block.machine.tileentity.TileEntityCompressor",
            offset_x + 3, offset_y, offset_z + row,
            facing=3, active=False, progress=0, energy=0.0,
        ),
        "machine",
        "Compressor idle",
    )

    add(
        "induction_furnace_hot",
        "IC2:blockMachine",
        13,
        4,
        row,
        {
            "id": "ic2.core.block.machine.tileentity.TileEntityInduction",
            "x": offset_x + 4, "y": offset_y, "z": offset_z + row,
            "facing": 3, "active": True, "progress": 50, "energy": 10000.0,
            "heat": 5000,
            "InvSlots": {
                "input": {"0": item_stack("minecraft:iron_ingot", 4), "1": item_stack("minecraft:gold_ingot", 4)},
                "output": {"0": item_stack("IC2:itemIngot", 4, damage=3)},  # refined iron
                "battery": {"0": item_stack("IC2:itemBatCrystal", 1)},
                "upgrade": {},
            },
        },
        "machine",
        "Induction furnace with heat and dual input",
    )

    add(
        "mass_fabricator_uum",
        "IC2:blockMachine",
        14,
        5,
        row,
        {
            "id": "ic2.core.block.machine.tileentity.TileEntityMatter",
            "x": offset_x + 5, "y": offset_y, "z": offset_z + row,
            "facing": 3, "active": True, "progress": 500, "energy": 1000000.0,
            "InvSlots": {
                "amplifier": {"0": item_stack("IC2:itemScrap", 64)},
                "battery": {},
                "upgrade": {},
            },
        },
        "machine",
        "Mass fabricator with scrap amplifier",
    )

    # Row 1: Machines2 + Machines3
    row = 2
    add(
        "teleporter_linked",
        "IC2:blockMachine2",
        0,
        0,
        row,
        {
            "id": "ic2.core.block.machine.tileentity.TileEntityTeleporter",
            "x": offset_x, "y": offset_y, "z": offset_z + row,
            "facing": 3, "active": False, "energy": 500000.0,
            "targetSet": True,
            "targetX": offset_x + 10,
            "targetY": offset_y,
            "targetZ": offset_z + row,
        },
        "machine",
        "Teleporter with target set",
    )

    add(
        "thermal_centrifuge_running",
        "IC2:blockMachine2",
        12,
        1,
        row,
        standard_machine_nbt(
            "ic2.core.block.machine.tileentity.TileEntityCentrifuge",
            offset_x + 1, offset_y, offset_z + row,
            facing=3, active=True, progress=200, energy=2000.0,
            inv_slots=inv_slots_1input_1output(
                item_stack("IC2:itemOreCrushed", 4, damage=1),
                item_stack("IC2:itemDustSmall", 2, damage=2),
                item_stack("IC2:itemBatLamaCrystal", 1),
            ),
        ),
        "machine",
        "Thermal centrifuge processing crushed ore",
    )

    add(
        "metal_former_rolling",
        "IC2:blockMachine2",
        13,
        2,
        row,
        standard_machine_nbt(
            "ic2.core.block.machine.tileentity.TileEntityMetalFormer",
            offset_x + 2, offset_y, offset_z + row,
            facing=3, active=True, progress=150, energy=1500.0,
            inv_slots=inv_slots_1input_1output(
                item_stack("minecraft:iron_ingot", 1),
                item_stack("IC2:itemPlates", 1, damage=4),  # iron plate
            ),
        ),
        "machine",
        "Metal former in rolling mode",
    )

    add(
        "blast_furnace_steel",
        "IC2:blockMachine3",
        1,
        3,
        row,
        {
            "id": "ic2.core.block.machine.tileentity.TileEntityBlastFurnace",
            "x": offset_x + 3, "y": offset_y, "z": offset_z + row,
            "facing": 3, "active": True, "progress": 300, "energy": 0.0,
            "heat": 8000,
            "InvSlots": {
                "input": {"0": item_stack("IC2:itemDust", 2, damage=5)},  # iron dust
                "output": {"0": item_stack("IC2:itemIngot", 1, damage=3)},  # steel
                "air": {},
            },
        },
        "machine",
        "Blast furnace making steel",
    )

    # Row 2: Generators
    row = 4
    add(
        "generator_burning",
        "IC2:blockGenerator",
        0,
        0,
        row,
        {
            "id": "ic2.core.block.generator.tileentity.TileEntityGenerator",
            "x": offset_x, "y": offset_y, "z": offset_z + row,
            "facing": 3, "active": True, "energy": 2000.0,
            "fuel": 800,
            "Items": [{"Slot": 0, "id": "minecraft:coal", "Count": 32, "Damage": 0}],
        },
        "generator",
        "Generator burning coal",
    )

    add(
        "solar_panel_idle",
        "IC2:blockGenerator",
        3,
        1,
        row,
        {
            "id": "ic2.core.block.generator.tileentity.TileEntitySolarPanel",
            "x": offset_x + 1, "y": offset_y, "z": offset_z + row,
            "facing": 3, "active": False, "energy": 50.0,
        },
        "generator",
        "Solar panel with stored energy",
    )

    add(
        "nuclear_reactor_cold",
        "IC2:blockGenerator",
        7,
        2,
        row,
        {
            "id": "ic2.core.block.reactor.tileentity.TileEntityNuclearReactorElectric",
            "x": offset_x + 2, "y": offset_y, "z": offset_z + row,
            "facing": 3, "active": False, "energy": 0.0,
            "heat": 0,
            "output": 0,
        },
        "generator",
        "Nuclear reactor cold, empty",
    )

    # Row 3: Energy Storage + Transformers
    row = 6
    add(
        "batbox_half_full",
        "IC2:blockElectric",
        0,
        0,
        row,
        {
            "id": "ic2.core.block.wiring.tileentity.TileEntityBatBox",
            "x": offset_x, "y": offset_y, "z": offset_z + row,
            "facing": 3, "active": False, "energy": 20000.0,
            "Items": [{"Slot": 0, "id": "IC2:itemBatREDischarged", "Count": 1, "Damage": 0}],
        },
        "storage",
        "BatBox half charged with battery",
    )

    add(
        "mfe_full",
        "IC2:blockElectric",
        1,
        1,
        row,
        {
            "id": "ic2.core.block.wiring.tileentity.TileEntityMFE",
            "x": offset_x + 1, "y": offset_y, "z": offset_z + row,
            "facing": 3, "active": False, "energy": 600000.0,
        },
        "storage",
        "MFE fully charged",
    )

    add(
        "mfsu_max",
        "IC2:blockElectric",
        2,
        2,
        row,
        {
            "id": "ic2.core.block.wiring.tileentity.TileEntityMFSU",
            "x": offset_x + 2, "y": offset_y, "z": offset_z + row,
            "facing": 3, "active": False, "energy": 10000000.0,
            "Items": [{"Slot": 0, "id": "IC2:itemBatLamaCrystal", "Count": 1, "Damage": 0}],
        },
        "storage",
        "MFSU max charge with lapotron",
    )

    add(
        "cesu_quarter",
        "IC2:blockElectric",
        3,
        3,
        row,
        {
            "id": "ic2.core.block.wiring.tileentity.TileEntityCESU",
            "x": offset_x + 3, "y": offset_y, "z": offset_z + row,
            "facing": 3, "active": False, "energy": 75000.0,
        },
        "storage",
        "CESU quarter charged",
    )

    add(
        "lv_transformer",
        "IC2:blockElectric",
        5,
        4,
        row,
        {
            "id": "ic2.core.block.wiring.tileentity.TileEntityTransformer",
            "x": offset_x + 4, "y": offset_y, "z": offset_z + row,
            "facing": 3, "active": False, "energy": 0.0,
        },
        "transformer",
        "LV Transformer",
    )

    add(
        "mv_transformer",
        "IC2:blockElectric",
        6,
        5,
        row,
        {
            "id": "ic2.core.block.wiring.tileentity.TileEntityTransformer",
            "x": offset_x + 5, "y": offset_y, "z": offset_z + row,
            "facing": 3, "active": False, "energy": 0.0,
        },
        "transformer",
        "MV Transformer",
    )

    # Row 4: Cables + Decorations + Misc
    row = 8
    add("copper_cable", "IC2:blockCable", 0, 0, row, None, "cable", "Copper cable")
    add("glass_fibre_cable", "IC2:blockCable", 1, 1, row, None, "cable", "Glass fibre cable")
    add("gold_cable", "IC2:blockCable", 2, 2, row, None, "cable", "Gold cable")
    add("tin_cable", "IC2:blockCable", 4, 3, row, None, "cable", "Tin cable")

    add("ore_copper", "IC2:blockOreCopper", 0, 5, row, None, "resource", "Copper ore")
    add("ore_uranium", "IC2:blockOreUran", 0, 6, row, None, "resource", "Uranium ore")
    add("rubber_wood", "IC2:blockRubWood", 0, 7, row, None, "resource", "Rubber wood")

    add(
        "chargepad_active",
        "IC2:blockChargepad",
        0,
        9,
        row,
        {
            "id": "ic2.core.block.personal.tileentity.TileEntityChargepad",
            "x": offset_x + 9, "y": offset_y, "z": offset_z + row,
            "facing": 3, "active": True, "energy": 50000.0,
        },
        "personal",
        "Chargepad with stored energy",
    )

    # Row 5: Reactor components
    row = 10
    add("reactor_chamber", "IC2:blockReactorChamber", 0, 0, row, None, "reactor", "Reactor chamber")
    add("reactor_fluid_port", "IC2:blockReactorFluidPort", 0, 1, row, None, "reactor", "Reactor fluid port")
    add("reactor_access_hatch", "IC2:blockReactorAccessHatch", 0, 2, row, None, "reactor", "Reactor access hatch")
    add("reactor_redstone_port", "IC2:blockReactorRedstonePort", 0, 3, row, None, "reactor", "Reactor redstone port")
    add("reactor_vessel", "IC2:blockreactorvessel", 0, 4, row, None, "reactor", "Reactor vessel")

    return samples


def generate_patch(samples: list[Sample]) -> dict[str, Any]:
    reg = ic2_numeric_registry()
    edits: list[dict[str, Any]] = []
    report_samples: list[dict[str, Any]] = []

    for s in samples:
        numeric_id = reg.get(s.block_id_str)
        if numeric_id is None:
            print(f"WARNING: {s.block_id_str} not found in registry, skipping")
            continue

        edits.append({
            "op": "set_block",
            "x": s.x,
            "y": s.y,
            "z": s.z,
            "id": numeric_id,
            "meta": s.metadata,
        })

        if s.nbt is not None:
            edits.append({
                "op": "set_te",
                "x": s.x,
                "y": s.y,
                "z": s.z,
                "nbt": s.nbt,
            })

        report_samples.append({
            "name": s.name,
            "block": s.block_id_str,
            "meta": s.metadata,
            "numeric_id": numeric_id,
            "x": s.x,
            "y": s.y,
            "z": s.z,
            "has_te": s.nbt is not None,
            "category": s.category,
            "purpose": s.purpose,
        })

    return {
        "edits": edits,
        "metadata": {
            "mod": "IC2",
            "task": "5A",
            "sample_count": len(report_samples),
            "samples": report_samples,
        },
    }


def main() -> None:
    samples = build_samples(offset_x=100, offset_y=64, offset_z=100)
    patch = generate_patch(samples)
    SOURCE_PATCH.write_text(json.dumps(patch, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Generated patch with {len(patch['edits'])} edits -> {SOURCE_PATCH}")
    print(f"Samples: {patch['metadata']['sample_count']}")


if __name__ == "__main__":
    main()
