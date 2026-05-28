#!/usr/bin/env python3
"""Generate Extra Utilities Task 5A test patches.

Produces:
- a 1.7.10 source patch with representative ExU blocks and tile entities,
- a 1.18.2 target patch produced by the ExtraUtils converter,
- a conversion report with events/warnings,
- a redstone integration spec for later headless-server testing.
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

from converters.extrautils.extrautils_converter import ExtraUtilsConverter  # noqa: E402
from src.converters.mekanism.analyze_map_coverage import load_block_registry  # noqa: E402


WORLD_PATH = PROJECT_ROOT / "mapa_1710"
DEFAULT_OUT = Path(__file__).resolve().parent


# Numeric block IDs from mapa_1710 registry
BLOCK_IDS: dict[str, int] = {
    "ExtraUtilities:generator": 2000,
    "ExtraUtilities:generator.8": 2001,
    "ExtraUtilities:generator.64": 3205,
    "ExtraUtilities:magnumTorch": 1998,
    "ExtraUtilities:cursedearthside": 1987,
    "ExtraUtilities:angelBlock": 1955,
    "ExtraUtilities:trashcan": 1988,
    "ExtraUtilities:sound_muffler": 2189,
    "ExtraUtilities:filing": 2216,
    "ExtraUtilities:drum": 1999,
    "ExtraUtilities:enderQuarry": 1994,
    "ExtraUtilities:enderThermicPump": 1993,
}


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


def extrautils_numeric_registry() -> dict[str, int]:
    registry = load_block_registry(WORLD_PATH)
    return {name: numeric_id for numeric_id, name in registry.items() if name.startswith("ExtraUtilities:")}


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

    # ── Row 0: Generators x1 (meta 0-11) with varied NBT states ──
    # Survivalist generator — basic, no extra NBT
    add(
        "generator_stone_empty",
        "ExtraUtilities:generator",
        0,
        0,
        0,
        {"id": "extrautils:generatorstone", "rotation": 0},
        "generator",
        "Survivalist generator, empty, facing south.",
    )
    # Lava generator — with energy and fluid tank
    add(
        "generator_lava_powered",
        "ExtraUtilities:generator",
        2,
        1,
        0,
        {
            "id": "extrautils:generatorlava",
            "rotation": 1,
            "Energy": 50000,
            "Tank_0": {"FluidName": "minecraft:lava", "Amount": 4000},
            "coolDown": 0,
        },
        "generator",
        "Lava generator with RF energy and lava tank, facing west.",
        "redstone_power_source_candidate",
    )
    # Solar generator — no fuel tank, just energy
    add(
        "generator_solar_day",
        "ExtraUtilities:generator",
        7,
        2,
        0,
        {
            "id": "extrautils:generatorsolar",
            "rotation": 2,
            "Energy": 12000,
        },
        "generator",
        "Solar generator with stored energy, facing north.",
    )
    # Overclocked generator — high cooldown state (warning expected)
    add(
        "generator_overclocked_cooldown",
        "ExtraUtilities:generator",
        10,
        3,
        0,
        {
            "id": "extrautils:generatoroverclocked",
            "rotation": 3,
            "Energy": 80000,
            "coolDown": 120,
            "backup": True,
        },
        "generator",
        "Overclocked generator with cooldown/backup flags (state loss warning).",
    )
    # Pink generator — edge case, maps to gourmand fallback
    add(
        "generator_pink_fallback",
        "ExtraUtilities:generator",
        9,
        4,
        0,
        {"id": "extrautils:generatorpink", "rotation": 0},
        "generator",
        "Pink generator fallback to Gourmand Dynamo.",
    )

    # ── Row 1: Generators x8 and x64 ──
    add(
        "generator_lava_x8",
        "ExtraUtilities:generator.8",
        2,
        0,
        2,
        {
            "id": "extrautils:generatorlava",
            "rotation": 0,
            "Energy": 250000,
            "Tank_0": {"FluidName": "minecraft:lava", "Amount": 32000},
        },
        "generator",
        "Lava generator x8 tier.",
    )
    add(
        "generator_solar_x64",
        "ExtraUtilities:generator.64",
        7,
        1,
        2,
        {
            "id": "extrautils:generatorsolar",
            "rotation": 1,
            "Energy": 500000,
        },
        "generator",
        "Solar generator x64 tier (maps to Mekanism solar).",
    )
    add(
        "generator_nether_x64",
        "ExtraUtilities:generator.64",
        11,
        2,
        2,
        {
            "id": "extrautils:generatornether",
            "rotation": 2,
            "Energy": 999000,
            "coolDown": 0,
        },
        "generator",
        "Nether Star generator x64 tier.",
    )

    # ── Row 2: Utility blocks ──
    add("magnum_torch", "ExtraUtilities:magnumTorch", 0, 0, 4, None, "utility", "Anti-mob torch → Torchmaster Mega Torch.")
    add("cursed_earth", "ExtraUtilities:cursedearthside", 0, 1, 4, None, "utility", "Cursed Earth → Cursed Earth mod.")
    add("angel_block", "ExtraUtilities:angelBlock", 0, 2, 4, None, "utility", "Angel Block → Angel Block Renewed.")
    add("sound_muffler", "ExtraUtilities:sound_muffler", 0, 3, 4, None, "utility", "Sound Muffler → Extreme Sound Muffler.")

    # ── Row 3: Trash Cans (meta 0=item, 1=liquid, 2=energy) ──
    add("trash_can_item", "ExtraUtilities:trashcan", 0, 0, 6, None, "utility", "Item Trash Can.")
    add("trash_can_liquid", "ExtraUtilities:trashcan", 1, 1, 6, None, "utility", "Liquid Trash Can.")
    add("trash_can_energy", "ExtraUtilities:trashcan", 2, 2, 6, None, "utility", "Energy Trash Can.")

    # ── Row 4: Filing Cabinets ──
    # Empty filing cabinet
    add(
        "filing_cabinet_empty",
        "ExtraUtilities:filing",
        0,
        0,
        8,
        {"id": "TileEntityFilingCabinet"},
        "storage",
        "Empty filing cabinet.",
    )
    # Filing cabinet with items (custom ExU inventory format)
    add(
        "filing_cabinet_with_items",
        "ExtraUtilities:filing",
        1,
        1,
        8,
        {
            "id": "TileEntityFilingCabinet",
            "item_no": 3,
            "item_0": {"id": "minecraft:cobblestone", "Count": 64, "Damage": 0, "Size": 3456},
            "item_1": {"id": "minecraft:iron_ingot", "Count": 32, "Damage": 0, "Size": 1728},
            "item_2": {"id": "minecraft:gold_ingot", "Count": 16, "Damage": 0, "Size": 864},
        },
        "storage",
        "Filing cabinet with 3 item stacks.",
    )
    # Diamond filing cabinet (meta 6+ means diamond variant)
    add(
        "filing_cabinet_diamond_empty",
        "ExtraUtilities:filing",
        6,
        2,
        8,
        {"id": "TileEntityFilingCabinet"},
        "storage",
        "Diamond filing cabinet, empty.",
    )
    # Filing cabinet overflow test (>54 items should warn)
    add(
        "filing_cabinet_overflow",
        "ExtraUtilities:filing",
        3,
        3,
        8,
        {
            "id": "TileEntityFilingCabinet",
            "item_no": 60,
            **{f"item_{i}": {"id": "minecraft:stone", "Count": 1, "Damage": 0, "Size": 64} for i in range(60)},
        },
        "storage",
        "Filing cabinet with 60 items (overflow warning).",
    )

    # ── Row 5: Drum and Quarry ──
    add("drum_empty", "ExtraUtilities:drum", 0, 0, 10, {"id": "extrautils:drum"}, "storage", "Empty drum (fluid storage placeholder).")
    add("ender_quarry", "ExtraUtilities:enderQuarry", 0, 1, 10, {"id": "extrautils:enderquarry"}, "machine", "Ender Quarry → placeholder.")
    add(
        "ender_thermic_pump",
        "ExtraUtilities:enderThermicPump",
        0,
        2,
        10,
        {"id": "extrautils:enderpump"},
        "machine",
        "Ender-Thermic Pump → Mekanism Electric Pump.",
    )

    # ── Row 6: Additional generator coverage ──
    add("generator_ender", "ExtraUtilities:generator", 3, 0, 12, {"id": "extrautils:generatorender", "rotation": 0}, "generator", "Ender generator.")
    add("generator_food", "ExtraUtilities:generator", 5, 1, 12, {"id": "extrautils:generatorfood", "rotation": 1}, "generator", "Culinary generator.")
    add("generator_potion", "ExtraUtilities:generator", 6, 2, 12, {"id": "extrautils:generatorpotion", "rotation": 2}, "generator", "Potion generator.")
    add("generator_tnt", "ExtraUtilities:generator", 8, 3, 12, {"id": "extrautils:generatortnt", "rotation": 3}, "generator", "TNT generator.")
    add("generator_redflux", "ExtraUtilities:generator", 4, 4, 12, {"id": "extrautils:generatorredflux", "rotation": 0}, "generator", "Heated Redstone generator.")

    return samples


def make_source_patch(samples: list[Sample]) -> dict[str, Any]:
    edits: list[dict[str, Any]] = []
    missing_registry: list[str] = []
    for sample in samples:
        numeric_id = BLOCK_IDS.get(sample.block_id)
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
            "name": "extrautils_task5a_source",
            "generated_by": "generate_extrautils_task5a.py",
            "source_world_for_dynamic_ids": str(WORLD_PATH.relative_to(PROJECT_ROOT)),
            "samples": len(samples),
            "missing_registry_names": sorted(set(missing_registry)),
        },
        "edits": edits,
    }


def make_target_patch_and_report(samples: list[Sample]) -> tuple[dict[str, Any], dict[str, Any]]:
    converter = ExtraUtilsConverter()
    target_edits: list[dict[str, Any]] = []
    sample_results: list[dict[str, Any]] = []
    errors: list[str] = []
    warnings: list[str] = []

    for sample in samples:
        result = converter.convert_block(sample.block_id, sample.metadata, sample.nbt, (sample.x, sample.y, sample.z))
        sample_results.append(
            {
                "name": sample.name,
                "category": sample.category,
                "purpose": sample.purpose,
                "source": {"block_id": sample.block_id, "metadata": sample.metadata, "position": [sample.x, sample.y, sample.z]},
                "target": {"block_id": result.block_id_1182, "has_nbt": result.nbt_1182 is not None},
                "success": result.success,
                "warnings": result.warnings,
                "errors": result.errors,
            }
        )
        warnings.extend(result.warnings)
        errors.extend(result.errors)
        if not result.success or not result.block_id_1182:
            continue
        target_edits.append(
            {
                "op": "set_block",
                "x": sample.x,
                "y": sample.y,
                "z": sample.z,
                "block_id": result.block_id_1182,
                "properties": result.blockstate_props,
                "label": sample.name,
            }
        )
        if result.nbt_1182 is not None:
            target_edits.append(
                {
                    "op": "set_te",
                    "x": sample.x,
                    "y": sample.y,
                    "z": sample.z,
                    "nbt": result.nbt_1182,
                    "label": sample.name,
                }
            )

    target_patch = {
        "format_version": "1.18.2",
        "metadata": {
            "name": "extrautils_task5a_converted",
            "generated_by": "generate_extrautils_task5a.py",
            "source": "extrautils_task5a_source_patch_1710.json",
        },
        "edits": target_edits,
    }
    report = {
        "name": "Extra Utilities Task 5A conversion sample report",
        "samples": sample_results,
        "success_count": sum(1 for sample in sample_results if sample["success"]),
        "failure_count": sum(1 for sample in sample_results if not sample["success"]),
        "warnings": sorted(set(warnings)),
        "errors": errors,
    }
    return target_patch, report


def make_redstone_spec(samples: list[Sample], offset_x: int, offset_y: int, offset_z: int) -> dict[str, Any]:
    controlled = [sample for sample in samples if sample.redstone_role]
    return {
        "name": "extrautils_task5a_redstone_integration_spec",
        "version": "1.7.10_source_to_1.18.2_target",
        "source_skill": "skills/integration_test_with_redstone/SKILL.md",
        "status": "spec_for_later_headless_server_run",
        "panel": {
            "test_start": {"x": offset_x, "y": offset_y + 1, "z": offset_z - 4, "block": "minecraft:lever"},
            "command_block": {
                "x": offset_x + 14,
                "y": offset_y,
                "z": offset_z - 4,
                "command": "/say [TEST_EXU_5A] redstone harness reached assertion bus PASS",
            },
        },
        "adapter_strategy": [
            "Use redstone line as TEST_START bus.",
            "Use energy output from converted generators as the power source adapter.",
            "Use command block console output as the first assertion sink.",
            "Later server test should add RCON checks for generator energy state after ticks and restart.",
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
            "Converted world loads with target mods (Thermal, Mekanism, Torchmaster, etc.) without missing block crashes.",
            "Command block logs PASS after TEST_START bus is powered.",
            "Generators retain converted NBT (energy, facing) after 3 minutes and one restart.",
        ],
    }


def generate(offset_x: int, offset_y: int, offset_z: int) -> GeneratedScenario:
    samples = build_samples(offset_x, offset_y, offset_z)
    source_patch = make_source_patch(samples)
    target_patch, report = make_target_patch_and_report(samples)
    redstone_spec = make_redstone_spec(samples, offset_x, offset_y, offset_z)
    return GeneratedScenario(source_patch, target_patch, report, redstone_spec, samples)


def write_json(path: Path, data: dict[str, Any]) -> None:
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate Extra Utilities Task 5A patches")
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    parser.add_argument("--x", type=int, default=200)
    parser.add_argument("--y", type=int, default=64)
    parser.add_argument("--z", type=int, default=200)
    args = parser.parse_args()

    scenario = generate(args.x, args.y, args.z)
    args.out.mkdir(parents=True, exist_ok=True)
    write_json(args.out / "extrautils_task5a_source_patch_1710.json", scenario.source_patch)
    write_json(args.out / "extrautils_task5a_converted_patch_1182.json", scenario.target_patch)
    write_json(args.out / "extrautils_task5a_conversion_report.json", scenario.report)
    write_json(args.out / "extrautils_task5a_redstone_spec.json", scenario.redstone_spec)

    print(f"Wrote Extra Utilities Task 5A files to {args.out}")
    print(f"Samples: {len(scenario.samples)}")
    print(f"Source edits: {len(scenario.source_patch['edits'])}")
    print(f"Target edits: {len(scenario.target_patch['edits'])}")
    print(f"Failures: {scenario.report['failure_count']}")
    return 0 if scenario.report["failure_count"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
