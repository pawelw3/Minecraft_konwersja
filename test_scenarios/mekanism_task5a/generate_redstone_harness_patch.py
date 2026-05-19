#!/usr/bin/env python3
"""Generate an executable redstone harness patch for Mekanism Task 5A.

The harness follows `skills/integration_test_with_redstone/SKILL.md`:

- panel input: TEST_START lever,
- adapter layer: redstone bus,
- SUT references: Mekanism converted sample machines,
- assertion/log: command block that prints PASS.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


SCENARIO_DIR = Path(__file__).resolve().parent
DEFAULT_SPEC = SCENARIO_DIR / "mekanism_task5a_redstone_spec.json"
DEFAULT_BASE_PATCH = SCENARIO_DIR / "mekanism_task5a_realworld_converted_patch_1182.json"
DEFAULT_OUT = SCENARIO_DIR / "mekanism_task5a_redstone_harness_patch_1182.json"
DEFAULT_MERGED_OUT = SCENARIO_DIR / "mekanism_task5a_converted_with_redstone_patch_1182.json"
DEFAULT_REPORT = SCENARIO_DIR / "mekanism_task5a_redstone_harness_report.json"


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, data: dict[str, Any]) -> None:
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def block_edit(x: int, y: int, z: int, block_id: str, properties: dict[str, str] | None = None, label: str | None = None) -> dict[str, Any]:
    edit = {"op": "set_block", "x": x, "y": y, "z": z, "block_id": block_id, "properties": properties or {}}
    if label:
        edit["label"] = label
    return edit


def te_edit(x: int, y: int, z: int, nbt: dict[str, Any], label: str | None = None) -> dict[str, Any]:
    edit = {"op": "set_te", "x": x, "y": y, "z": z, "nbt": nbt}
    if label:
        edit["label"] = label
    return edit


def build_harness(spec: dict[str, Any]) -> dict[str, Any]:
    panel = spec["panel"]
    lever = panel["test_start"]
    command_block = panel["command_block"]

    lever_x = int(lever["x"])
    lever_y = int(lever["y"])
    lever_z = int(lever["z"])
    command_x = int(command_block["x"])
    command_y = lever_y
    command_z = int(command_block["z"])
    bus_y = lever_y
    support_y = lever_y - 1

    if lever_z != command_z:
        raise ValueError("This first harness generator expects lever and command block on the same Z line.")
    if command_x <= lever_x + 1:
        raise ValueError("Command block must be east of the lever with room for a redstone bus.")

    edits: list[dict[str, Any]] = []

    for x in range(lever_x, command_x):
        edits.append(block_edit(x, support_y, lever_z, "minecraft:polished_andesite", label="redstone_support"))

    edits.append(
        block_edit(
            lever_x,
            bus_y,
            lever_z,
            "minecraft:lever",
            {"face": "floor", "facing": "east", "powered": "false"},
            "TEST_START",
        )
    )

    repeater_positions = set(range(lever_x + 12, command_x, 12)) if command_x - lever_x > 15 else set()
    for x in range(lever_x + 1, command_x):
        if x in repeater_positions:
            edits.append(
                block_edit(
                    x,
                    bus_y,
                    lever_z,
                    "minecraft:repeater",
                    {"delay": "1", "facing": "east", "locked": "false", "powered": "false"},
                    "TEST_START_bus_repeater",
                )
            )
            continue
        edits.append(
            block_edit(
                x,
                bus_y,
                lever_z,
                "minecraft:redstone_wire",
                {"east": "side", "north": "none", "power": "0", "south": "none", "west": "side"},
                "TEST_START_bus",
            )
        )

    edits.append(block_edit(command_x, command_y, command_z, "minecraft:command_block", {"facing": "west", "conditional": "false"}, "assertion_command_block"))
    edits.append(
        te_edit(
            command_x,
            command_y,
            command_z,
            {
                "id": "minecraft:command_block",
                "x": command_x,
                "y": command_y,
                "z": command_z,
                "Command": str(command_block["command"]).lstrip("/"),
                "CustomName": "{\"text\":\"MEK_5A_ASSERT\"}",
                "TrackOutput": True,
                "auto": False,
                "conditionMet": False,
                "powered": False,
                "SuccessCount": 0,
            },
            "assertion_command_block",
        )
    )

    return {
        "format_version": "1.18.2",
        "metadata": {
            "name": "mekanism_task5a_redstone_harness",
            "generated_by": "generate_redstone_harness_patch.py",
            "source_spec": DEFAULT_SPEC.name,
            "skill": spec.get("source_skill"),
            "notes": [
                "Panel input is a floor lever named TEST_START.",
                "The redstone bus powers a command block assertion sink.",
                "The command block is moved to the bus level so the harness is directly powerable.",
            ],
        },
        "edits": edits,
    }


def block_positions(patch: dict[str, Any]) -> dict[tuple[int, int, int], dict[str, Any]]:
    positions: dict[tuple[int, int, int], dict[str, Any]] = {}
    for edit in patch.get("edits", []):
        if edit.get("op") == "set_block":
            positions[(int(edit["x"]), int(edit["y"]), int(edit["z"]))] = edit
    return positions


def find_block_collisions(base_patch: dict[str, Any], harness_patch: dict[str, Any]) -> list[dict[str, Any]]:
    base_positions = block_positions(base_patch)
    collisions = []
    for pos, harness_edit in block_positions(harness_patch).items():
        base_edit = base_positions.get(pos)
        if base_edit is None:
            continue
        collisions.append(
            {
                "position": list(pos),
                "base_block_id": base_edit.get("block_id"),
                "harness_block_id": harness_edit.get("block_id"),
                "base_label": base_edit.get("label"),
                "harness_label": harness_edit.get("label"),
            }
        )
    return collisions


def merge_patches(base_patch: dict[str, Any], harness_patch: dict[str, Any]) -> dict[str, Any]:
    return {
        "format_version": "1.18.2",
        "metadata": {
            "name": "mekanism_task5a_converted_with_redstone",
            "generated_by": "generate_redstone_harness_patch.py",
            "base_patch": DEFAULT_BASE_PATCH.name,
            "harness_patch": DEFAULT_OUT.name,
        },
        "edits": list(base_patch.get("edits", [])) + list(harness_patch.get("edits", [])),
    }


def build_report(
    spec: dict[str, Any],
    base_patch: dict[str, Any],
    harness_patch: dict[str, Any],
    merged_patch: dict[str, Any],
) -> dict[str, Any]:
    block_counts: dict[str, int] = {}
    for edit in harness_patch["edits"]:
        if edit["op"] == "set_block":
            block_counts[edit["block_id"]] = block_counts.get(edit["block_id"], 0) + 1
    collisions = find_block_collisions(base_patch, harness_patch)
    return {
        "name": "Mekanism Task 5A redstone harness report",
        "status": "generated_patch_ready_for_1.18_writer_or_setblock_materializer",
        "harness_edits": len(harness_patch["edits"]),
        "merged_edits": len(merged_patch["edits"]),
        "block_collision_count": len(collisions),
        "block_collisions": collisions,
        "block_counts": block_counts,
        "sut": spec.get("system_under_test", []),
        "acceptance": spec.get("acceptance", []),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--spec", type=Path, default=DEFAULT_SPEC)
    parser.add_argument("--base-patch", type=Path, default=DEFAULT_BASE_PATCH)
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    parser.add_argument("--merged-out", type=Path, default=DEFAULT_MERGED_OUT)
    parser.add_argument("--report", type=Path, default=DEFAULT_REPORT)
    args = parser.parse_args()

    spec = load_json(args.spec)
    base_patch = load_json(args.base_patch)
    harness_patch = build_harness(spec)
    merged_patch = merge_patches(base_patch, harness_patch)
    report = build_report(spec, base_patch, harness_patch, merged_patch)

    write_json(args.out, harness_patch)
    write_json(args.merged_out, merged_patch)
    write_json(args.report, report)

    print(f"Harness edits: {report['harness_edits']}")
    print(f"Merged edits: {report['merged_edits']}")
    print(f"Block collisions: {report['block_collision_count']}")
    print(f"Harness patch: {args.out}")
    print(f"Merged patch: {args.merged_out}")
    print(f"Report: {args.report}")
    return 0 if report["block_collision_count"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
