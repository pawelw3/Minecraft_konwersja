#!/usr/bin/env python3
"""Generate AE2 Task 5A source/converted patches and redstone harness."""

from __future__ import annotations

import json
import sys
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parents[2]
SCENARIO_DIR = Path(__file__).resolve().parent
WORLD_PATH = PROJECT_ROOT / "mapa_1710"

sys.path.insert(0, str(PROJECT_ROOT))
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from src.converters.ae2.ae2_converter import AE2Converter  # noqa: E402
from src.converters.ae2.mappings.block_mappings import BLOCK_MAPPINGS_1710_TO_1182  # noqa: E402
from src.converters.mekanism.analyze_map_coverage import load_block_registry  # noqa: E402


SOURCE_PATCH = SCENARIO_DIR / "ae2_task5a_source_patch_1710.json"
CONVERTED_PATCH = SCENARIO_DIR / "ae2_task5a_converted_patch_1182.json"
CONVERSION_REPORT = SCENARIO_DIR / "ae2_task5a_conversion_report.json"
REDSTONE_SPEC = SCENARIO_DIR / "ae2_task5a_redstone_spec.json"
REDSTONE_PATCH = SCENARIO_DIR / "ae2_task5a_redstone_harness_patch_1182.json"
MERGED_PATCH = SCENARIO_DIR / "ae2_task5a_converted_with_redstone_patch_1182.json"
REPORT_MD = SCENARIO_DIR / "AE2_TASK5A_REPORT.md"


@dataclass(frozen=True)
class Sample:
    name: str
    block_id: str
    metadata: int
    x: int
    y: int
    z: int
    nbt: dict[str, Any] | None
    category: str
    purpose: str
    redstone_role: str | None = None


def write_json(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def ae2_numeric_registry() -> dict[str, int]:
    registry = load_block_registry(WORLD_PATH)
    return {name: numeric_id for numeric_id, name in registry.items() if name.startswith("appliedenergistics2:")}


def raw_id(block_id: str) -> str:
    return block_id.rsplit(".", 1)[-1]


def item_stack(item_id: str, count: int = 1, damage: int = 0, tag: dict[str, Any] | None = None, slot: int | None = None) -> dict[str, Any]:
    stack: dict[str, Any] = {"id": item_id, "Count": count}
    if damage:
        stack["Damage"] = damage
    if tag:
        stack["tag"] = tag
    if slot is not None:
        stack["Slot"] = slot
    return stack


def storage_cell(size: str, slot: int, payload_id: str, payload_count: int) -> dict[str, Any]:
    return item_stack(
        f"appliedenergistics2:item.ItemBasicStorageCell.{size}",
        slot=slot,
        tag={
            "StorageCell": {
                "items": [item_stack(payload_id, payload_count)],
                "itemCount": payload_count,
            }
        },
    )


def base_nbt(block_id: str, x: int, y: int, z: int) -> dict[str, Any]:
    return {"id": raw_id(block_id), "x": x, "y": y, "z": z, "forward": 2, "up": 1}


def sample_nbt(block_id: str, metadata: int, x: int, y: int, z: int, variant: str) -> dict[str, Any] | None:
    if block_id.endswith("BlockDrive"):
        nbt = base_nbt(block_id, x, y, z)
        nbt.update(
            {
                "priority": 7,
                "inv": {
                    "item0": storage_cell("1k", 0, "minecraft:cobblestone", 512),
                    "item1": storage_cell("4k", 1, "minecraft:iron_ingot", 128),
                    "item2": storage_cell("16k", 2, "minecraft:gold_ingot", 64),
                    "item3": storage_cell("64k", 3, "minecraft:diamond", 16),
                    "item4": {},
                },
            }
        )
        return nbt
    if block_id.endswith("BlockChest"):
        nbt = base_nbt(block_id, x, y, z)
        nbt.update({"priority": 3, "inv": {"item0": storage_cell("4k", 0, "minecraft:diamond", 32)}})
        return nbt
    if block_id.endswith("BlockSkyChest"):
        nbt = base_nbt(block_id, x, y, z)
        nbt.update({"inv": {"item0": item_stack("minecraft:certus_quartz_crystal", 12)}})
        return nbt
    if block_id.endswith("BlockInterface"):
        nbt = base_nbt(block_id, x, y, z)
        nbt.update(
            {
                "priority": 25,
                "config": [item_stack("minecraft:iron_ingot", 1, slot=0)],
                "storage": [item_stack("minecraft:chest", 16, slot=3)],
                "patterns": [
                    item_stack(
                        "appliedenergistics2:item.ItemEncodedPattern",
                        tag={
                            "crafting": True,
                            "in": [item_stack("minecraft:oak_planks", 4)],
                            "out": [item_stack("minecraft:crafting_table", 1)],
                            "substitute": False,
                        },
                        slot=0,
                    ),
                    item_stack(
                        "appliedenergistics2:item.ItemEncodedPattern",
                        tag={
                            "crafting": False,
                            "in": [item_stack("minecraft:iron_ingot", 1), item_stack("minecraft:coal", 1)],
                            "out": [item_stack("minecraft:steel_ingot", 1)],
                            "substitute": True,
                        },
                        slot=1,
                    ),
                ],
            }
        )
        return nbt
    if block_id.endswith("BlockCableBus"):
        nbt = base_nbt(block_id, x, y, z)
        if variant == "empty":
            nbt.update({"hasRedstone": False})
            return nbt
        nbt.update(
            {
                "hasRedstone": True,
                "def:0": {"class": "appeng.parts.networking.PartCable", "color": 0},
                "extra:0": {"usedChannels": 4},
                "def:1": {"class": "appeng.parts.reporting.PartTerminal", "color": 0},
                "extra:1": {"customName": "Task5A terminal"},
                "def:2": {"class": "appeng.parts.automation.PartExportBus", "color": 0},
                "extra:2": {"config": [item_stack("minecraft:cobblestone", 1, slot=0)]},
            }
        )
        return nbt
    if block_id.endswith("BlockCraftingStorage"):
        nbt = base_nbt(block_id, x, y, z)
        nbt.update({"customName": f"CPU storage meta {metadata}"})
        return nbt
    if block_id.endswith("BlockCraftingUnit"):
        nbt = base_nbt(block_id, x, y, z)
        nbt.update(
            {
                "core": metadata % 2 == 0,
                "inventory": [item_stack("minecraft:iron_ingot", 8)],
                "finalOutput": item_stack("minecraft:piston", 1),
            }
        )
        return nbt
    if block_id.endswith("BlockMolecularAssembler"):
        nbt = base_nbt(block_id, x, y, z)
        nbt.update({"isCrafting": True, "progress": 40, "customName": "Assembler active"})
        return nbt
    if block_id.endswith("BlockIOPort"):
        nbt = base_nbt(block_id, x, y, z)
        nbt.update({"cells": {"item0": storage_cell("1k", 0, "minecraft:stone", 100)}, "lastRedstoneState": 1})
        return nbt
    if block_id.endswith("BlockInscriber"):
        nbt = base_nbt(block_id, x, y, z)
        nbt.update(
            {
                "inv": [
                    item_stack("appliedenergistics2:item.ItemMultiMaterial", 1, damage=13, slot=0),
                    item_stack("appliedenergistics2:item.ItemMultiMaterial", 1, damage=19, slot=1),
                ],
                "progress": 20,
            }
        )
        return nbt
    if block_id.endswith("BlockCharger"):
        nbt = base_nbt(block_id, x, y, z)
        nbt.update({"inv": [item_stack("appliedenergistics2:item.ItemMultiMaterial", 1, damage=0, slot=0)], "internalCurrentPower": 2000})
        return nbt
    if block_id.endswith("BlockSecurity"):
        nbt = base_nbt(block_id, x, y, z)
        nbt.update({"owner": "pawel", "players": [{"name": "pawel", "uuid": "legacy-offline", "permissions": 255}]})
        return nbt
    if block_id.endswith("BlockWireless"):
        nbt = base_nbt(block_id, x, y, z)
        nbt.update({"inv": [item_stack("appliedenergistics2:item.ItemMultiMaterial", 16, damage=42, slot=0)]})
        return nbt
    if block_id.endswith("BlockQuantumLinkChamber"):
        nbt = base_nbt(block_id, x, y, z)
        nbt.update({"singularity": {"pair_id": "task5a-quantum"}, "inv": [item_stack("appliedenergistics2:item.ItemSingularity", 1, slot=0)]})
        return nbt
    if block_id.endswith("BlockSpatialIOPort"):
        nbt = base_nbt(block_id, x, y, z)
        nbt.update({"inv": [item_stack("appliedenergistics2:item.ItemSpatialStorageCell.2Cubed", 1, slot=0)]})
        return nbt
    if any(block_id.endswith(suffix) for suffix in [
        "BlockController",
        "BlockEnergyAcceptor",
        "BlockEnergyCell",
        "BlockDenseEnergyCell",
        "BlockCraftingMonitor",
        "BlockQuantumRing",
        "BlockSpatialPylon",
        "BlockQuartzGrowthAccelerator",
        "BlockCondenser",
        "BlockVibrationChamber",
        "BlockLightDetector",
    ]):
        return base_nbt(block_id, x, y, z)
    return None


def add_sample(samples: list[Sample], block_id: str, metadata: int, category: str, purpose: str, variant: str = "default", redstone_role: str | None = None) -> None:
    index = len(samples)
    x = 100 + (index % 12) * 3
    y = 64 + (index // 144) * 8
    z = 100 + ((index // 12) % 12) * 3
    nbt = sample_nbt(block_id, metadata, x, y, z, variant)
    samples.append(Sample(f"{raw_id(block_id).lower()}_{metadata}_{variant}", block_id, metadata, x, y, z, nbt, category, purpose, redstone_role))


def build_samples() -> list[Sample]:
    samples: list[Sample] = []
    for block_id, mapping in sorted(BLOCK_MAPPINGS_1710_TO_1182.items()):
        if block_id.endswith("BlockCraftingStorage"):
            for metadata in range(8):
                add_sample(samples, block_id, metadata, "metadata_matrix", "Crafting storage size 0..3 plus formed bit")
            continue
        if block_id.endswith("BlockCraftingUnit"):
            for metadata in range(4):
                add_sample(samples, block_id, metadata, "metadata_matrix", "Crafting unit and accelerator metadata", redstone_role="crafting_cpu_member" if metadata == 1 else None)
            continue
        if block_id.endswith("BlockCableBus"):
            add_sample(samples, block_id, 0, "multipart", "Cable + terminal + export bus", redstone_role="redstone_controlled_network")
            add_sample(samples, block_id, 0, "multipart", "Second cable sample for empty/new-format warning", variant="empty")
            continue
        add_sample(samples, block_id, 0, "all_mapped_blocks", mapping.notes)

    # Explicit legacy alias sample to keep old report names covered.
    alias_index = len(samples)
    samples.append(
        Sample(
            "blockquartzfixture_alias",
            "appliedenergistics2:tile.BlockQuartzFixture",
            0,
            100 + (alias_index % 12) * 3,
            64,
            100 + ((alias_index // 12) % 12) * 3,
            None,
            "alias_compat",
            "Legacy project alias for BlockQuartzTorch -> ae2:quartz_fixture",
        )
    )
    return samples


def make_source_patch(samples: list[Sample], registry: dict[str, int]) -> dict[str, Any]:
    edits: list[dict[str, Any]] = []
    missing_registry = []
    for sample in samples:
        numeric_id = registry.get(sample.block_id)
        if numeric_id is None and sample.block_id.endswith("BlockQuartzFixture"):
            numeric_id = registry.get("appliedenergistics2:tile.BlockQuartzTorch")
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
        if sample.nbt is not None:
            edits.append({"op": "set_te", "x": sample.x, "y": sample.y, "z": sample.z, "nbt": sample.nbt, "label": sample.name})
    return {
        "format_version": "1.7.10",
        "metadata": {
            "name": "ae2_task5a_source",
            "generated_by": "generate_ae2_task5a.py",
            "source_world_for_dynamic_ids": "mapa_1710",
            "samples": len(samples),
            "missing_registry": sorted(set(missing_registry)),
        },
        "edits": edits,
    }


def convert_samples(samples: list[Sample]) -> tuple[dict[str, Any], dict[str, Any]]:
    converter = AE2Converter()
    edits: list[dict[str, Any]] = []
    sample_results: list[dict[str, Any]] = []
    target_counts = Counter()
    warning_counts = Counter()

    for sample in samples:
        result = converter.convert_block(sample.block_id, sample.nbt, sample.metadata, (sample.x, sample.y, sample.z))
        converted = result.converted
        if converted.block_id_1182:
            target_counts[converted.block_id_1182] += 1
        for warning in converted.warnings:
            warning_counts[warning.split(":", 1)[0]] += 1
        sample_results.append(
            {
                "label": sample.name,
                "source_block_id": sample.block_id,
                "metadata": sample.metadata,
                "position": [sample.x, sample.y, sample.z],
                "target_block_id": converted.block_id_1182,
                "success": converted.success,
                "additional_blocks": len(converted.additional_blocks),
                "warnings": converted.warnings,
                "errors": converted.errors,
            }
        )
        if not converted.success or not converted.block_id_1182:
            continue
        edits.append(
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
            edits.append({"op": "set_te", "x": sample.x, "y": sample.y, "z": sample.z, "nbt": converted.nbt_1182, "label": sample.name})
        for index, extra in enumerate(converted.additional_blocks):
            ex, ey, ez = extra.original_pos
            edits.append(
                {
                    "op": "set_block",
                    "x": ex,
                    "y": ey,
                    "z": ez,
                    "block_id": extra.converted.block_id_1182,
                    "properties": extra.converted.blockstate_props,
                    "label": f"{sample.name}_additional_{index}",
                }
            )
            if extra.converted.nbt_1182 is not None:
                edits.append({"op": "set_te", "x": ex, "y": ey, "z": ez, "nbt": extra.converted.nbt_1182, "label": f"{sample.name}_additional_{index}"})

    patch = {
        "format_version": "1.18.2",
        "metadata": {"name": "ae2_task5a_converted", "generated_by": "generate_ae2_task5a.py"},
        "edits": edits,
    }
    report = {
        "name": "AE2 Task 5A conversion report",
        "samples": len(samples),
        "source_block_edits": len(samples),
        "target_edits": len(edits),
        "success": sum(1 for item in sample_results if item["success"]),
        "failed": sum(1 for item in sample_results if not item["success"]),
        "additional_blocks": sum(item["additional_blocks"] for item in sample_results),
        "target_counts": dict(target_counts),
        "warning_counts": dict(warning_counts),
        "samples_detail": sample_results,
    }
    return patch, report


def block_edit(x: int, y: int, z: int, block_id: str, properties: dict[str, str] | None = None, label: str | None = None) -> dict[str, Any]:
    edit = {"op": "set_block", "x": x, "y": y, "z": z, "block_id": block_id, "properties": properties or {}}
    if label:
        edit["label"] = label
    return edit


def make_redstone_spec(samples: list[Sample]) -> dict[str, Any]:
    sut = [
        {"label": sample.name, "position": [sample.x, sample.y, sample.z], "role": sample.redstone_role}
        for sample in samples
        if sample.redstone_role
    ]
    return {
        "source_skill": "skills/integration_test_with_redstone/SKILL.md",
        "panel": {
            "test_start": {"x": 96, "y": 65, "z": 96},
            "command_block": {
                "x": 100,
                "y": 65,
                "z": 96,
                "command": "/say AE2_TASK5A_REDSTONE_PASS",
            },
        },
        "system_under_test": sut,
        "acceptance": [
            "Lever TEST_START powers the assertion command block through a repeater bus.",
            "Harness positions do not collide with converted AE2 samples.",
            "AE2 redstone-sensitive samples are present for later headless checks.",
        ],
    }


def make_redstone_harness(spec: dict[str, Any], base_patch: dict[str, Any]) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    lever = spec["panel"]["test_start"]
    command = spec["panel"]["command_block"]
    lx, ly, lz = int(lever["x"]), int(lever["y"]), int(lever["z"])
    cx, cy, cz = int(command["x"]), int(command["y"]), int(command["z"])
    edits: list[dict[str, Any]] = []
    for x in range(lx, cx + 1):
        edits.append(block_edit(x, ly - 1, lz, "minecraft:polished_andesite", label="redstone_support"))
    edits.append(block_edit(lx, ly, lz, "minecraft:lever", {"face": "floor", "facing": "east", "powered": "false"}, "TEST_START"))
    repeater_positions = set(range(lx + 12, cx, 12))
    for x in range(lx + 1, cx):
        if x in repeater_positions:
            edits.append(block_edit(x, ly, lz, "minecraft:repeater", {"facing": "east", "delay": "1", "locked": "false", "powered": "false"}, "TEST_START_bus_repeater"))
        else:
            edits.append(block_edit(x, ly, lz, "minecraft:redstone_wire", {"east": "side", "west": "side", "north": "none", "south": "none", "power": "0"}, "TEST_START_bus"))
    edits.append(block_edit(cx, cy, cz, "minecraft:command_block", {"facing": "west", "conditional": "false"}, "assertion_command_block"))
    edits.append(
        {
            "op": "set_te",
            "x": cx,
            "y": cy,
            "z": cz,
            "nbt": {
                "id": "minecraft:command_block",
                "x": cx,
                "y": cy,
                "z": cz,
                "Command": str(command["command"]).lstrip("/"),
                "CustomName": "{\"text\":\"AE2_5A_ASSERT\"}",
                "TrackOutput": True,
                "auto": False,
                "powered": False,
                "SuccessCount": 0,
            },
            "label": "assertion_command_block",
        }
    )
    harness = {"format_version": "1.18.2", "metadata": {"name": "ae2_task5a_redstone_harness"}, "edits": edits}
    merged = {"format_version": "1.18.2", "metadata": {"name": "ae2_task5a_converted_with_redstone"}, "edits": base_patch["edits"] + edits}
    base_positions = {(e["x"], e["y"], e["z"]) for e in base_patch["edits"] if e["op"] == "set_block"}
    harness_positions = {(e["x"], e["y"], e["z"]) for e in edits if e["op"] == "set_block"}
    report = {
        "name": "AE2 Task 5A redstone harness report",
        "harness_edits": len(edits),
        "merged_edits": len(merged["edits"]),
        "block_collision_count": len(base_positions & harness_positions),
        "block_collisions": [list(pos) for pos in sorted(base_positions & harness_positions)],
        "system_under_test": spec["system_under_test"],
    }
    return harness, merged, report


def write_report_md(conversion_report: dict[str, Any], harness_report: dict[str, Any]) -> None:
    lines = [
        "# AE2 Task 5A - raport",
        "",
        "Status: wykonane ponownie na aktualnym konwerterze AE2.",
        "",
        "## Liczby",
        "",
        f"- Sample: {conversion_report['samples']}",
        f"- Udane konwersje: {conversion_report['success']}",
        f"- Nieudane konwersje: {conversion_report['failed']}",
        f"- Target edits 1.18.2: {conversion_report['target_edits']}",
        f"- Dodatkowe bloki utworzone przez konwerter: {conversion_report['additional_blocks']}",
        f"- Redstone harness edits: {harness_report['harness_edits']}",
        f"- Kolizje harnessa z AE2: {harness_report['block_collision_count']}",
        "",
        "## Zakres",
        "",
        "- Wszystkie aktualnie mapowane bloki core AE2.",
        "- Metadata matrix dla `BlockCraftingStorage` 0..7.",
        "- Metadata matrix dla `BlockCraftingUnit` 0..3.",
        "- Inventory dla Drive, Chest, SkyChest, IO Port, Inscriber i Charger.",
        "- Interface z patternami, ktory tworzy `ae2:pattern_provider`.",
        "- CableBus jako stabilny lossy fallback materialowy.",
        "- Lossy fallbacki `BlockCrank` i `BlockGrinder`.",
        "- Alias `BlockQuartzFixture` oraz realny rejestr `BlockQuartzTorch`.",
        "- Prosty redstone harness zgodny z `skills/integration_test_with_redstone` do pozniejszego headless.",
        "",
        "## Granica kroku",
        "",
        "Ten krok konczy sie na patchach testowej mapy 1.7.10, patchu wynikowym 1.18.2 i harnessie redstone. Fizyczne materializowanie/uruchomienie na headless serwerze nalezy do 5B/6.",
    ]
    REPORT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    samples = build_samples()
    registry = ae2_numeric_registry()
    source_patch = make_source_patch(samples, registry)
    converted_patch, conversion_report = convert_samples(samples)
    spec = make_redstone_spec(samples)
    harness_patch, merged_patch, harness_report = make_redstone_harness(spec, converted_patch)

    write_json(SOURCE_PATCH, source_patch)
    write_json(CONVERTED_PATCH, converted_patch)
    write_json(CONVERSION_REPORT, conversion_report)
    write_json(REDSTONE_SPEC, spec)
    write_json(REDSTONE_PATCH, harness_patch)
    write_json(MERGED_PATCH, merged_patch)
    write_json(SCENARIO_DIR / "ae2_task5a_redstone_harness_report.json", harness_report)
    write_report_md(conversion_report, harness_report)

    failures = conversion_report["failed"] + len(source_patch["metadata"]["missing_registry"]) + harness_report["block_collision_count"]
    print(f"Samples: {conversion_report['samples']}")
    print(f"Success: {conversion_report['success']}")
    print(f"Failed: {conversion_report['failed']}")
    print(f"Missing registry: {len(source_patch['metadata']['missing_registry'])}")
    print(f"Target edits: {conversion_report['target_edits']}")
    print(f"Additional blocks: {conversion_report['additional_blocks']}")
    print(f"Redstone collisions: {harness_report['block_collision_count']}")
    print(f"Report: {REPORT_MD}")
    return 0 if failures == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
