#!/usr/bin/env python3
"""Generate Mekanism Task 5A test patches.

The script does not edit any Minecraft world. It produces:

- a 1.7.10 patch with representative Mekanism blocks and block entities,
- a 1.18.2 patch produced by the Mekanism converter,
- a conversion report with events/warnings,
- a small redstone integration spec for later headless-server testing.
"""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT))
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from src.converters.mekanism import MekanismConverter  # noqa: E402
from src.converters.mekanism.analyze_map_coverage import load_block_registry  # noqa: E402
from src.converters.mekanism.mappings import get_block_mapping  # noqa: E402


WORLD_PATH = PROJECT_ROOT / "mapa_1710"
DEFAULT_OUT = Path(__file__).resolve().parent


@dataclass
class Sample:
    name: str
    block_id: str
    metadata: int
    x: int
    y: int
    z: int
    nbt: dict[str, Any] | None = None
    category: str = "block"
    purpose: str = ""
    redstone_role: str | None = None


@dataclass
class GeneratedScenario:
    source_patch: dict[str, Any]
    target_patch: dict[str, Any]
    report: dict[str, Any]
    redstone_spec: dict[str, Any]
    samples: list[Sample] = field(default_factory=list)


def mekanism_numeric_registry() -> dict[str, int]:
    registry = load_block_registry(WORLD_PATH)
    return {name: numeric_id for numeric_id, name in registry.items() if name.startswith("Mekanism:")}


def build_samples(offset_x: int, offset_y: int, offset_z: int) -> list[Sample]:
    samples: list[Sample] = []

    def add(
        name: str,
        block_id: str,
        metadata: int,
        dx: int,
        dz: int,
        nbt: dict[str, Any] | None = None,
        category: str = "block",
        purpose: str = "",
        redstone_role: str | None = None,
    ) -> None:
        nbt_with_pos = None
        x = offset_x + dx
        y = offset_y
        z = offset_z + dz
        if nbt is not None:
            nbt_with_pos = dict(nbt)
            nbt_with_pos.update({"x": x, "y": y, "z": z})
        samples.append(Sample(name, block_id, metadata, x, y, z, nbt_with_pos, category, purpose, redstone_role))

    # Real block entities from the Task 4 coverage report.
    add(
        "quantum_entangloporter_powered",
        "Mekanism:MachineBlock3",
        0,
        0,
        0,
        {
            "id": "QuantumEntangloporter",
            "frequency": "task5a_shared",
            "owner": "pawel",
            "electricityStored": 500000.0,
            "facing": 3,
            "Items": [{"Slot": 0, "id": "Mekanism:Ingot", "Damage": 1, "Count": 16}],
        },
        "frequency",
        "Frequency/owner/energy preservation candidate.",
    )
    add(
        "basic_bin_with_osmium",
        "Mekanism:BasicBlock",
        6,
        2,
        0,
        {
            "id": "Bin",
            "tier": "basic",
            "itemType": {"id": "Mekanism:Ingot", "Damage": 1, "Count": 1},
            "itemCount": 128,
        },
        "storage",
        "Container-like BE with item payload.",
    )
    add(
        "digital_miner_running_cache",
        "Mekanism:MachineBlock",
        4,
        4,
        0,
        {
            "id": "DigitalMiner",
            "radius": 12,
            "minY": 5,
            "maxY": 64,
            "running": True,
            "silkTouch": True,
            "inverse": False,
            "filters": [{"type": "tag", "value": "forge:ores/osmium"}],
            "oresToMine": {"legacy": "cache"},
            "electricityStored": 750000.0,
            "facing": 2,
        },
        "machine",
        "Running miner must reset runtime cache.",
    )
    add(
        "elite_smelting_factory_progress",
        "Mekanism:MachineBlock",
        7,
        6,
        0,
        {
            "id": "UltimateSmeltingFactory",
            "recipeType": 0,
            "recipeTicks": 12,
            "progress0": 199,
            "progress1": 5,
            "electricityStored": 120000.0,
            "Items": [
                {"Slot": 0, "id": "Mekanism:OsmiumDust", "Count": 2},
                {"Slot": 5, "id": "Mekanism:Ingot", "Damage": 1, "Count": 1},
            ],
            "facing": 5,
        },
        "factory",
        "Factory recipe/progress/inventory conversion.",
        "redstone_controlled_machine",
    )
    add(
        "elite_crushing_factory_progress",
        "Mekanism:MachineBlock",
        7,
        8,
        0,
        {
            "id": "UltimateSmeltingFactory",
            "recipeType": 2,
            "progress0": 77,
            "electricityStored": 120000.0,
            "Items": [{"Slot": 0, "id": "Mekanism:Ingot", "Damage": 1, "Count": 1}],
            "facing": 5,
        },
        "factory",
        "Same block/meta, different recipeType target.",
    )
    add(
        "teleporter_frequency",
        "Mekanism:MachineBlock",
        11,
        10,
        0,
        {
            "id": "MekanismTeleporter",
            "frequency": "task5a_base",
            "owner": "pawel",
            "electricityStored": 250000.0,
            "facing": 3,
        },
        "frequency",
        "Legacy owner without UUID warning.",
    )
    add(
        "advanced_energy_cube",
        "Mekanism:EnergyCube",
        1,
        12,
        0,
        {"id": "EnergyCube", "tier": "advanced", "electricityStored": 4000000.0, "facing": 3},
        "energy",
        "Tier and energy container conversion.",
        "redstone_power_source_candidate",
    )
    add(
        "portable_fluid_tank",
        "Mekanism:MachineBlock2",
        11,
        14,
        0,
        {
            "id": "PortableTank",
            "tier": "elite",
            "fluidTank": {"FluidName": "water", "Amount": 16000},
            "facing": 3,
        },
        "fluid",
        "Fluid tank tier selection.",
    )
    add(
        "gas_tank_hydrogen_chloride",
        "Mekanism:GasTank",
        0,
        16,
        0,
        {"id": "GasTank", "tier": 0, "gasTank": {"stored": {"gasName": "gas:hydrogen_chloride", "amount": 32000}}},
        "chemical",
        "Gas to chemical tank conversion.",
    )

    # Non-BE and placeholder-like blocks found by Task 4.
    add("salt_block", "Mekanism:SaltBlock", 0, 0, 3, None, "decor", "Direct target in Mekanism 10.")
    add("bounding_block", "Mekanism:BoundingBlock", 0, 2, 3, None, "placeholder", "Invisible bounding target.")
    add("advanced_bounding_block", "Mekanism:BoundingBlock", 1, 4, 3, None, "placeholder", "Advanced invisible bounding target.")
    add("obsidian_tnt_fallback", "Mekanism:ObsidianTNT", 0, 6, 3, {"id": "ObsidianTNT"}, "fallback", "Falls back to vanilla TNT.")
    add("slick_plastic_gray", "Mekanism:SlickPlasticBlock", 8, 8, 3, None, "decor", "Slickness lost; color preserved.")
    add("plastic_white", "Mekanism:PlasticBlock", 15, 10, 3, None, "decor", "Plastic lost; color preserved.")
    add("road_plastic_brown", "Mekanism:RoadPlasticBlock", 3, 12, 3, None, "decor", "Speed boost lost; color preserved.")

    # Static block coverage from common Mekanism groups.
    add("osmium_ore", "Mekanism:OreBlock", 0, 0, 6, None, "ore", "Ore remap.")
    add("copper_ore_vanilla", "Mekanism:OreBlock", 1, 2, 6, None, "ore", "Vanilla copper fallback.")
    add("tin_ore", "Mekanism:OreBlock", 2, 4, 6, None, "ore", "Ore remap.")
    add("steel_block", "Mekanism:BasicBlock", 5, 6, 6, None, "storage_block", "Material block remap.")
    add("thermal_evaporation_block", "Mekanism:BasicBlock2", 0, 8, 6, None, "multiblock", "Multiblock wall.")
    add("induction_port", "Mekanism:BasicBlock2", 2, 10, 6, {"id": "InductionPort", "tier": "basic"}, "multiblock", "Multiblock BE.")

    return samples


def make_source_patch(samples: list[Sample], numeric_registry: dict[str, int]) -> dict[str, Any]:
    edits: list[dict[str, Any]] = []
    missing_registry: list[str] = []
    for sample in samples:
        numeric_id = numeric_registry.get(sample.block_id)
        if numeric_id is None:
            missing_registry.append(sample.block_id)
            continue
        edits.append(
            {
                "op": "set_block",
                "x": sample.x,
                "y": sample.y,
                "z": sample.z,
                "id": numeric_id,
                "meta": sample.metadata,
                "registry_name": sample.block_id,
                "label": sample.name,
            }
        )
        if sample.nbt:
            edits.append({"op": "set_te", "x": sample.x, "y": sample.y, "z": sample.z, "nbt": sample.nbt, "label": sample.name})
    return {
        "format_version": "1.7.10",
        "metadata": {
            "name": "mekanism_task5a_source",
            "generated_by": "generate_mekanism_task5a.py",
            "source_world_for_dynamic_ids": str(WORLD_PATH.relative_to(PROJECT_ROOT)),
            "samples": len(samples),
            "missing_registry_names": sorted(set(missing_registry)),
        },
        "edits": edits,
    }


def make_target_patch_and_report(samples: list[Sample]) -> tuple[dict[str, Any], dict[str, Any]]:
    converter = MekanismConverter()
    target_edits: list[dict[str, Any]] = []
    sample_results: list[dict[str, Any]] = []
    errors: list[str] = []
    warnings: list[str] = []

    for sample in samples:
        result = converter.convert_block(sample.block_id, sample.metadata, sample.nbt, (sample.x, sample.y, sample.z))
        converted = result.converted
        sample_results.append(
            {
                "name": sample.name,
                "category": sample.category,
                "purpose": sample.purpose,
                "source": {"block_id": sample.block_id, "metadata": sample.metadata, "position": [sample.x, sample.y, sample.z]},
                "target": {"block_id": converted.block_id_1182, "has_nbt": converted.nbt_1182 is not None},
                "success": converted.success,
                "warnings": converted.warnings,
                "errors": converted.errors,
            }
        )
        warnings.extend(converted.warnings)
        errors.extend(converted.errors)
        if not converted.success or not converted.block_id_1182:
            continue
        target_edits.append(
            {
                "op": "set_block",
                "x": sample.x,
                "y": sample.y,
                "z": sample.z,
                "block_id": converted.block_id_1182,
                "properties": converted.blockstate_props,
                "label": sample.name,
            }
        )
        if converted.nbt_1182 is not None:
            target_edits.append(
                {
                    "op": "set_te",
                    "x": sample.x,
                    "y": sample.y,
                    "z": sample.z,
                    "nbt": converted.nbt_1182,
                    "label": sample.name,
                }
            )

    target_patch = {
        "format_version": "1.18.2",
        "metadata": {
            "name": "mekanism_task5a_converted",
            "generated_by": "generate_mekanism_task5a.py",
            "source": "mekanism_task5a_source_patch_1710.json",
        },
        "edits": target_edits,
    }
    report = {
        "name": "Mekanism Task 5A conversion sample report",
        "samples": sample_results,
        "stats": converter.stats,
        "success_count": sum(1 for sample in sample_results if sample["success"]),
        "failure_count": sum(1 for sample in sample_results if not sample["success"]),
        "warnings": sorted(set(warnings)),
        "errors": errors,
        "events": [event.to_dict() for event in converter.get_events()],
    }
    return target_patch, report


def make_redstone_spec(samples: list[Sample], offset_x: int, offset_y: int, offset_z: int) -> dict[str, Any]:
    controlled = [sample for sample in samples if sample.redstone_role]
    return {
        "name": "mekanism_task5a_redstone_integration_spec",
        "version": "1.7.10_source_to_1.18.2_target",
        "source_skill": "skills/integration_test_with_redstone/SKILL.md",
        "status": "spec_for_later_headless_server_run",
        "panel": {
            "test_start": {"x": offset_x, "y": offset_y + 1, "z": offset_z - 4, "block": "minecraft:lever"},
            "command_block": {
                "x": offset_x + 14,
                "y": offset_y,
                "z": offset_z - 4,
                "command": "/say [TEST_MEKANISM_5A] redstone harness reached assertion bus PASS",
            },
        },
        "adapter_strategy": [
            "Use redstone line as TEST_START bus.",
            "Use energy/item availability as the machine input adapter where direct GUI redstone mode is unavailable.",
            "Use command block console output as the first assertion sink.",
            "Later server test should add RCON checks for output inventory/state after ticks and restart.",
        ],
        "system_under_test": [
            {
                "name": sample.name,
                "position": [sample.x, sample.y, sample.z],
                "source_block_id": sample.block_id,
                "metadata": sample.metadata,
                "role": sample.redstone_role,
            }
            for sample in controlled
        ],
        "acceptance": [
            "Converted world loads with Mekanism 10 without missing block crashes.",
            "Command block logs PASS after TEST_START bus is powered.",
            "Factory and energy cube retain converted NBT after 3 minutes and one restart.",
        ],
    }


def generate(offset_x: int, offset_y: int, offset_z: int) -> GeneratedScenario:
    samples = build_samples(offset_x, offset_y, offset_z)
    source_patch = make_source_patch(samples, mekanism_numeric_registry())
    target_patch, report = make_target_patch_and_report(samples)
    redstone_spec = make_redstone_spec(samples, offset_x, offset_y, offset_z)
    return GeneratedScenario(source_patch, target_patch, report, redstone_spec, samples)


def write_json(path: Path, data: dict[str, Any]) -> None:
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate Mekanism Task 5A patches")
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    parser.add_argument("--x", type=int, default=100)
    parser.add_argument("--y", type=int, default=64)
    parser.add_argument("--z", type=int, default=100)
    args = parser.parse_args()

    scenario = generate(args.x, args.y, args.z)
    args.out.mkdir(parents=True, exist_ok=True)
    write_json(args.out / "mekanism_task5a_source_patch_1710.json", scenario.source_patch)
    write_json(args.out / "mekanism_task5a_converted_patch_1182.json", scenario.target_patch)
    write_json(args.out / "mekanism_task5a_conversion_report.json", scenario.report)
    write_json(args.out / "mekanism_task5a_redstone_spec.json", scenario.redstone_spec)

    print(f"Wrote Mekanism Task 5A files to {args.out}")
    print(f"Samples: {len(scenario.samples)}")
    print(f"Source edits: {len(scenario.source_patch['edits'])}")
    print(f"Target edits: {len(scenario.target_patch['edits'])}")
    print(f"Failures: {scenario.report['failure_count']}")
    return 0 if scenario.report["failure_count"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
