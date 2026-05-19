#!/usr/bin/env python3
"""Generate the full Mekanism core Task 5A scenario.

This is the "whole 5A" variant: it places every mapped Mekanism core block
variant available in the dynamic 1.7.10 registry, plus NBT-bearing variants
for tiers, factory recipe types, tanks, bins, frequency machines, and caches.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT))
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from src.converters.mekanism import MekanismConverter  # noqa: E402
from src.converters.mekanism.analyze_map_coverage import load_block_registry  # noqa: E402
from src.converters.mekanism.mappings import (  # noqa: E402
    BASIC_BLOCK,
    BASIC_BLOCK2,
    BOUNDING_BLOCK,
    CARDBOARD_BOX,
    ENERGY_CUBE,
    FACTORY_RECIPE_BY_ORDINAL,
    FACTORY_TIER_BY_META,
    GAS_TANK,
    GLOW_PLASTIC_BLOCK,
    MACHINE_BLOCK,
    MACHINE_BLOCK2,
    MACHINE_BLOCK3,
    ORE_BLOCK,
    PLASTIC_BLOCK,
    PLASTIC_FENCE,
    REINFORCED_PLASTIC_BLOCK,
    ROAD_PLASTIC_BLOCK,
    SALT_BLOCK,
    SLICK_PLASTIC_BLOCK,
    STATIC_MAPPINGS,
    TE_ID_TO_MAPPING_KEY,
    get_block_mapping,
)
from test_scenarios.mekanism_task5a.generate_mekanism_task5a import Sample, make_redstone_spec  # noqa: E402


WORLD_PATH = PROJECT_ROOT / "mapa_1710"
DEFAULT_OUT = Path(__file__).resolve().parent
FULL_PREFIX = "mekanism_task5a_full"


TE_BY_BLOCK_META: dict[tuple[str, int], str] = {value: key for key, value in TE_ID_TO_MAPPING_KEY.items()}
EXTRA_TE_BY_BLOCK_META = {
    (BASIC_BLOCK, 10): "StructuralGlass",
    (BASIC_BLOCK, 15): "ThermalEvaporationValve",
    (BASIC_BLOCK2, 0): "ThermalEvaporationBlock",
    (BASIC_BLOCK2, 1): "InductionCasing",
    (BASIC_BLOCK2, 3): "InductionCell",
    (BASIC_BLOCK2, 4): "InductionProvider",
    (BASIC_BLOCK2, 5): "SuperheatingElement",
    (BASIC_BLOCK2, 6): "PressureDisperser",
    (BASIC_BLOCK2, 7): "BoilerCasing",
    (BASIC_BLOCK2, 8): "BoilerValve",
    (CARDBOARD_BOX, 0): "CardboardBox",
}


def mekanism_numeric_registry() -> dict[str, int]:
    registry = load_block_registry(WORLD_PATH)
    return {name: numeric_id for numeric_id, name in registry.items() if name.startswith("Mekanism:")}


def positioned(samples: list[Sample], columns: int, offset_x: int, offset_y: int, offset_z: int) -> list[Sample]:
    placed: list[Sample] = []
    for index, sample in enumerate(samples):
        x = offset_x + (index % columns) * 2
        z = offset_z + (index // columns) * 2
        nbt = dict(sample.nbt or {}) if sample.nbt is not None else None
        if nbt is not None:
            nbt.update({"x": x, "y": offset_y, "z": z})
        placed.append(Sample(sample.name, sample.block_id, sample.metadata, x, offset_y, z, nbt, sample.category, sample.purpose, sample.redstone_role))
    return placed


def base_machine_nbt(te_id: str, index: int) -> dict[str, Any]:
    return {
        "id": te_id,
        "electricityStored": 10000.0 + index * 250,
        "facing": 3 + (index % 3),
        "Items": [{"Slot": 0, "id": "Mekanism:Ingot", "Damage": 1, "Count": 1 + (index % 16)}],
        "operatingTicks": index % 20,
        "clientActive": True,
    }


def nbt_for(block_id: str, metadata: int, te_id: str, index: int, tier: str | int | None = None, recipe_type: int | None = None) -> dict[str, Any]:
    nbt = base_machine_nbt(te_id, index)
    if tier is not None:
        nbt["tier"] = tier
    if recipe_type is not None:
        nbt.update(
            {
                "recipeType": recipe_type,
                "recipeTicks": 10 + recipe_type,
                "progress0": recipe_type * 3,
                "progress1": recipe_type * 5,
            }
        )
    if te_id == "DigitalMiner":
        nbt.update(
            {
                "radius": 12,
                "minY": 5,
                "maxY": 64,
                "running": True,
                "silkTouch": True,
                "inverse": False,
                "filters": [{"type": "tag", "value": "forge:ores/osmium"}],
                "oresToMine": {"legacy": "cache"},
            }
        )
    elif te_id in {"MekanismTeleporter", "QuantumEntangloporter", "SecurityDesk", "ElectricChest"}:
        nbt.update({"frequency": f"task5a_full_{te_id}", "owner": "pawel", "public": False})
    elif te_id == "EnergyCube":
        nbt.update({"electricityStored": 400000.0 + index * 1000})
    elif te_id == "GasTank":
        nbt.update({"dumping": 0, "gasTank": {"stored": {"gasName": "gas:hydrogen_chloride", "amount": 16000 + index}}})
    elif te_id == "PortableTank":
        nbt.update({"fluidTank": {"FluidName": "water", "Amount": 8000 + index}})
    elif te_id == "Bin":
        nbt.update({"itemType": {"id": "Mekanism:Ingot", "Damage": 1, "Count": 1}, "itemCount": 64 + index})
    elif te_id == "CardboardBox":
        nbt.update({"storedBlock": {"id": "Mekanism:BasicBlock", "meta": 0}, "storedTileEntity": {"id": "Bin", "itemCount": 3}})
    elif block_id == BASIC_BLOCK2 or te_id in {"DynamicTank", "DynamicValve", "InductionPort"}:
        nbt.update({"structure": {"legacy": True}, "structureFound": True})
    return nbt


def add_sample(
    samples: list[Sample],
    name: str,
    block_id: str,
    metadata: int,
    category: str,
    purpose: str,
    nbt: dict[str, Any] | None = None,
    redstone_role: str | None = None,
) -> None:
    samples.append(Sample(name=name, block_id=block_id, metadata=metadata, x=0, y=0, z=0, nbt=nbt, category=category, purpose=purpose, redstone_role=redstone_role))


def build_full_samples() -> list[Sample]:
    samples: list[Sample] = []
    seen_static: set[tuple[str, int]] = set()
    index = 0

    # Static and metadata-bound variants.
    for block_id, metadata in sorted(STATIC_MAPPINGS):
        mapping = get_block_mapping(block_id, metadata)
        if mapping is None:
            continue
        seen_static.add((block_id, metadata))
        te_id = TE_BY_BLOCK_META.get((block_id, metadata)) or EXTRA_TE_BY_BLOCK_META.get((block_id, metadata))
        nbt = nbt_for(block_id, metadata, te_id, index) if mapping.has_block_entity and te_id else None
        add_sample(samples, f"{block_id.split(':')[1].lower()}_{metadata}", block_id, metadata, "all_mapped_static", f"{mapping.target_block_id}", nbt)
        index += 1

    # All recipe/tier variants that are selected by NBT, not only metadata.
    for metadata, tier in FACTORY_TIER_BY_META.items():
        te_id = TE_BY_BLOCK_META[(MACHINE_BLOCK, metadata)]
        for recipe_type, recipe_name in FACTORY_RECIPE_BY_ORDINAL.items():
            nbt = nbt_for(MACHINE_BLOCK, metadata, te_id, index, recipe_type=recipe_type)
            add_sample(samples, f"{tier}_{recipe_name}_factory", MACHINE_BLOCK, metadata, "factory_recipe_matrix", f"{tier} factory recipeType={recipe_type}", nbt, "redstone_controlled_machine" if metadata == 7 and recipe_type == 0 else None)
            index += 1

    tier_names = ["basic", "advanced", "elite", "ultimate"]
    for tier_meta, tier in enumerate(tier_names):
        add_sample(samples, f"{tier}_bin_payload", BASIC_BLOCK, 6, "tier_matrix", "Bin tier + item payload", nbt_for(BASIC_BLOCK, 6, "Bin", index, tier=tier))
        index += 1
        add_sample(samples, f"{tier}_energy_cube_charged", ENERGY_CUBE, tier_meta, "tier_matrix", "EnergyCube tier + stored energy", nbt_for(ENERGY_CUBE, tier_meta, "EnergyCube", index, tier=tier_meta), "redstone_power_source_candidate" if tier == "advanced" else None)
        index += 1
        add_sample(samples, f"{tier}_gas_tank_hcl", GAS_TANK, tier_meta, "tier_matrix", "GasTank tier + chemical payload", nbt_for(GAS_TANK, tier_meta, "GasTank", index, tier=tier_meta))
        index += 1
        add_sample(samples, f"{tier}_fluid_tank_water", MACHINE_BLOCK2, 11, "tier_matrix", "Portable tank tier + water payload", nbt_for(MACHINE_BLOCK2, 11, "PortableTank", index, tier=tier))
        index += 1
        add_sample(samples, f"{tier}_induction_cell", BASIC_BLOCK2, 3, "tier_matrix", "Induction cell tier NBT", nbt_for(BASIC_BLOCK2, 3, "InductionCell", index, tier=tier))
        index += 1
        add_sample(samples, f"{tier}_induction_provider", BASIC_BLOCK2, 4, "tier_matrix", "Induction provider tier NBT", nbt_for(BASIC_BLOCK2, 4, "InductionProvider", index, tier=tier))
        index += 1

    # Creative Energy Cube exists in legacy metadata and is useful as a boundary case.
    add_sample(samples, "creative_energy_cube_boundary", ENERGY_CUBE, 4, "tier_matrix", "Creative tier boundary", nbt_for(ENERGY_CUBE, 4, "EnergyCube", index, tier=4))
    index += 1

    # Plastic families and other registry names not seen in Task 4 zones.
    for block_id in (PLASTIC_BLOCK, SLICK_PLASTIC_BLOCK, ROAD_PLASTIC_BLOCK, GLOW_PLASTIC_BLOCK, REINFORCED_PLASTIC_BLOCK, PLASTIC_FENCE):
        for metadata in range(16):
            mapping = get_block_mapping(block_id, metadata)
            if mapping:
                add_sample(samples, f"{block_id.split(':')[1].lower()}_{metadata}", block_id, metadata, "decor_full_color_matrix", mapping.notes)
                index += 1

    if get_block_mapping(CARDBOARD_BOX, 0):
        add_sample(samples, "cardboard_box_packed_block", CARDBOARD_BOX, 0, "packed_block", "Cardboard box with stored block NBT", nbt_for(CARDBOARD_BOX, 0, "CardboardBox", index))
        index += 1

    # Registry/meta sweep for every source block name in the dynamic map. This
    # catches future mapping additions without needing to hand-edit the scenario.
    registry = mekanism_numeric_registry()
    for block_id in sorted(registry):
        for metadata in range(16):
            if (block_id, metadata) in seen_static:
                continue
            if any(sample.block_id == block_id and sample.metadata == metadata and sample.category != "tier_matrix" for sample in samples):
                continue
            mapping = get_block_mapping(block_id, metadata)
            if mapping is None:
                continue
            te_id = TE_BY_BLOCK_META.get((block_id, metadata)) or EXTRA_TE_BY_BLOCK_META.get((block_id, metadata))
            nbt = nbt_for(block_id, metadata, te_id, index) if mapping.has_block_entity and te_id else None
            add_sample(samples, f"registry_sweep_{block_id.split(':')[1].lower()}_{metadata}", block_id, metadata, "registry_sweep", f"{mapping.target_block_id}", nbt)
            index += 1

    return positioned(samples, columns=18, offset_x=100, offset_y=64, offset_z=100)


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
            "name": f"{FULL_PREFIX}_source",
            "generated_by": "generate_mekanism_task5a_full.py",
            "source_world_for_dynamic_ids": str(WORLD_PATH.relative_to(PROJECT_ROOT)),
            "samples": len(samples),
            "block_samples": sum(1 for sample in samples if sample.nbt is None),
            "block_entity_samples": sum(1 for sample in samples if sample.nbt is not None),
            "missing_registry_names": sorted(set(missing_registry)),
        },
        "edits": edits,
    }


def make_target_patch_and_report(samples: list[Sample]) -> tuple[dict[str, Any], dict[str, Any]]:
    converter = MekanismConverter()
    target_edits: list[dict[str, Any]] = []
    sample_results: list[dict[str, Any]] = []
    warnings: list[str] = []
    errors: list[str] = []
    source_variant_keys: set[str] = set()
    target_block_ids: set[str] = set()

    for sample in samples:
        source_variant_keys.add(f"{sample.block_id}:{sample.metadata}")
        result = converter.convert_block(sample.block_id, sample.metadata, sample.nbt, (sample.x, sample.y, sample.z))
        converted = result.converted
        if converted.block_id_1182:
            target_block_ids.add(converted.block_id_1182)
        sample_results.append(
            {
                "name": sample.name,
                "category": sample.category,
                "purpose": sample.purpose,
                "source": {"block_id": sample.block_id, "metadata": sample.metadata, "position": [sample.x, sample.y, sample.z], "has_nbt": sample.nbt is not None},
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
        target_edits.append({"op": "set_block", "x": sample.x, "y": sample.y, "z": sample.z, "block_id": converted.block_id_1182, "properties": converted.blockstate_props, "label": sample.name})
        if converted.nbt_1182 is not None:
            target_edits.append({"op": "set_te", "x": sample.x, "y": sample.y, "z": sample.z, "nbt": converted.nbt_1182, "label": sample.name})

    report = {
        "name": "Mekanism Task 5A full conversion report",
        "sample_count": len(samples),
        "source_variant_count": len(source_variant_keys),
        "target_block_count": len(target_block_ids),
        "block_entity_sample_count": sum(1 for sample in samples if sample.nbt is not None),
        "success_count": sum(1 for sample in sample_results if sample["success"]),
        "failure_count": sum(1 for sample in sample_results if not sample["success"]),
        "warnings": sorted(set(warnings)),
        "errors": errors,
        "stats": converter.stats,
        "samples": sample_results,
        "events": [event.to_dict() for event in converter.get_events()],
    }
    target_patch = {
        "format_version": "1.18.2",
        "metadata": {"name": f"{FULL_PREFIX}_converted", "generated_by": "generate_mekanism_task5a_full.py", "source": f"{FULL_PREFIX}_source_patch_1710.json"},
        "edits": target_edits,
    }
    return target_patch, report


def write_json(path: Path, data: dict[str, Any]) -> None:
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate full Mekanism Task 5A patches")
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    args = parser.parse_args()

    samples = build_full_samples()
    source_patch = make_source_patch(samples, mekanism_numeric_registry())
    target_patch, report = make_target_patch_and_report(samples)
    redstone_spec = make_redstone_spec([sample for sample in samples if sample.redstone_role], 100, 64, 100)

    args.out.mkdir(parents=True, exist_ok=True)
    write_json(args.out / f"{FULL_PREFIX}_source_patch_1710.json", source_patch)
    write_json(args.out / f"{FULL_PREFIX}_converted_patch_1182.json", target_patch)
    write_json(args.out / f"{FULL_PREFIX}_conversion_report.json", report)
    write_json(args.out / f"{FULL_PREFIX}_redstone_spec.json", redstone_spec)

    print(f"Wrote full Mekanism Task 5A files to {args.out}")
    print(f"Samples: {report['sample_count']}")
    print(f"Source variants: {report['source_variant_count']}")
    print(f"Block entity samples: {report['block_entity_sample_count']}")
    print(f"Source edits: {len(source_patch['edits'])}")
    print(f"Target edits: {len(target_patch['edits'])}")
    print(f"Failures: {report['failure_count']}")
    return 0 if report["failure_count"] == 0 and not source_patch["metadata"]["missing_registry_names"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
