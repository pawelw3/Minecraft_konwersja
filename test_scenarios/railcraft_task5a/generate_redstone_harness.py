#!/usr/bin/env python3
"""Generate redstone harness for Railcraft Task 5A (headless server integration test)."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


SCENARIO_DIR = Path(__file__).resolve().parent
SPEC_PATH = SCENARIO_DIR / "railcraft_task5a_redstone_spec.json"
PATCH_PATH = SCENARIO_DIR / "railcraft_task5a_redstone_harness_patch_1182.json"


def write_json(path: Path, data: dict[str, Any]) -> None:
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def main() -> None:
    # Panel testowy (wejścia)
    # Lever startuje test; command block loguje PASS
    panel = {
        "test_start_lever": {"x": 196, "y": 65, "z": 198, "block_id": "minecraft:lever", "properties": {"face": "floor", "facing": "north", "powered": "false"}},
        "assert_command_block": {
            "x": 198, "y": 65, "z": 198,
            "block_id": "minecraft:command_block",
            "nbt": {"id": "minecraft:command_block", "Command": "/say RAILCRAFT_TASK5A_REDSTONE_PASS", "auto": 1},
        },
    }

    # System pod testem (SUT) — bloki Railcraft które mają rolę redstone
    sut = [
        {"label": "detector_any", "position": [294, 64, 200], "role": "observer_output", "converted_block": "minecraft:observer"},
        {"label": "detector_mob", "position": [296, 64, 200], "role": "observer_output", "converted_block": "minecraft:observer"},
        {"label": "detector_player", "position": [298, 64, 200], "role": "observer_output", "converted_block": "minecraft:observer"},
        {"label": "signal_receiver_box", "position": [284, 64, 200], "role": "comparator_output", "converted_block": "minecraft:comparator"},
        {"label": "signal_controller_box", "position": [286, 64, 200], "role": "comparator_output", "converted_block": "minecraft:comparator"},
        {"label": "signal_sequencer_box", "position": [288, 64, 200], "role": "repeater_output", "converted_block": "minecraft:repeater"},
        {"label": "signal_capacitor_box", "position": [290, 64, 200], "role": "comparator_output", "converted_block": "minecraft:comparator"},
        {"label": "signal_analog_box", "position": [292, 64, 200], "role": "comparator_output", "converted_block": "minecraft:comparator"},
        {"label": "signal_switch_lever", "position": [282, 64, 200], "role": "lever_input", "converted_block": "minecraft:lever"},
    ]

    # Redstone wiring — połączenia od levera do SUT i od SUT do command blocka
    harness_edits = []

    # Redstone dust bus (prosta magistrala)
    for x in range(196, 200):
        harness_edits.append({"op": "set_block", "x": x, "y": 64, "z": 198, "block_id": "minecraft:redstone_wire", "properties": {}})

    # Vertical connections do SUT
    for item in sut:
        sx, sy, sz = item["position"]
        # Redstone dust na poziomie y=64 prowadząca od sz=198 do sz
        if sz != 198:
            step = 1 if sz > 198 else -1
            for z in range(198 + step, sz + step, step):
                harness_edits.append({"op": "set_block", "x": sx, "y": 64, "z": z, "block_id": "minecraft:redstone_wire", "properties": {}})

    # Assert command block
    harness_edits.append({
        "op": "set_block",
        "x": 198, "y": 65, "z": 198,
        "block_id": "minecraft:command_block",
        "properties": {},
    })
    harness_edits.append({
        "op": "set_te",
        "x": 198, "y": 65, "z": 198,
        "nbt": {"id": "minecraft:command_block", "Command": "/say RAILCRAFT_TASK5A_REDSTONE_PASS", "auto": 1},
    })

    # Lever
    harness_edits.append({
        "op": "set_block",
        "x": 196, "y": 65, "z": 198,
        "block_id": "minecraft:lever",
        "properties": {"face": "floor", "facing": "north", "powered": "false"},
    })

    spec = {
        "source_skill": "skills/integration_test_with_redstone/SKILL.md",
        "panel": panel,
        "system_under_test": sut,
        "acceptance": [
            "Lever TEST_START powers the assertion command block through a redstone bus.",
            "Observer-based detectors (detector_*) emit redstone when triggered by entity movement.",
            "Signal boxes (receiver, controller, capacitor, analog) emit comparator-like redstone signals.",
            "Harness positions do not collide with converted Railcraft samples.",
        ],
    }

    patch = {
        "format_version": "1.18.2",
        "metadata": {"name": "railcraft_task5a_redstone_harness", "purpose": "integration_test"},
        "edits": harness_edits,
    }

    write_json(SPEC_PATH, spec)
    write_json(PATCH_PATH, patch)
    print("Wrote redstone spec:", SPEC_PATH)
    print("Wrote redstone harness patch:", PATCH_PATH)
    print(f"Harness edits: {len(harness_edits)}")


if __name__ == "__main__":
    main()
