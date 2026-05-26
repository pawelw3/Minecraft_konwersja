#!/usr/bin/env python3
"""Generate ComputerCraft Task 5A test patch for 1.7.10 world editing.

Produces a Hephaistos-compatible patch JSON that places representative
ComputerCraft blocks and tile-entities with varied states.
"""
from __future__ import annotations

import json
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[2]
SCENARIO_DIR = Path(__file__).resolve().parent
OUTPUT_PATCH = SCENARIO_DIR / "computercraft_task5a_patch.json"

# Block IDs from mapa_1710 block registry
BLOCK_IDS = {
    "CC-TurtleExpanded": 574,
    "command_computer": 575,
    "CC-Computer": 576,
    "CC-Peripheral": 577,
    "CC-Cable": 578,
    "CC-Turtle": 579,
    "CC-TurtleAdvanced": 580,
}


@dataclass(frozen=True)
class Sample:
    name: str
    block_id: int
    metadata: int
    x: int
    y: int
    z: int
    te_nbt: dict[str, Any] | None
    category: str
    purpose: str


def build_samples() -> list[Sample]:
    samples: list[Sample] = []
    base_x, base_y, base_z = 0, 64, 0

    def add(
        name: str,
        block_name: str,
        meta: int,
        dx: int,
        dz: int,
        te_nbt: dict[str, Any] | None = None,
        category: str = "block",
        purpose: str = "",
    ) -> None:
        x = base_x + dx
        y = base_y
        z = base_z + dz
        samples.append(
            Sample(name, BLOCK_IDS[block_name], meta, x, y, z, te_nbt, category, purpose)
        )

    # Row 0: Computers
    add(
        "computer_normal_on",
        "CC-Computer",
        0,
        0,
        0,
        {"id": "computer", "computerID": 1, "on": True},
        "computer",
        "Normal computer facing south, turned on",
    )
    add(
        "computer_normal_off",
        "CC-Computer",
        1,
        1,
        0,
        {"id": "computer", "computerID": 2, "on": False, "label": "TestPC"},
        "computer",
        "Normal computer facing west, turned off with label",
    )
    add(
        "computer_advanced_on",
        "CC-Computer",
        8,
        2,
        0,
        {"id": "computer", "computerID": 3, "on": True},
        "computer",
        "Advanced computer facing south, turned on",
    )
    add(
        "command_computer",
        "command_computer",
        0,
        3,
        0,
        {"id": "command_computer", "computerID": 4, "on": True},
        "computer",
        "Command computer",
    )

    # Row 1: Monitors
    add(
        "monitor_normal_wall_tl",
        "CC-Peripheral",
        10,
        0,
        1,
        {"id": "monitor", "xIndex": 0, "yIndex": 0, "width": 2, "height": 2, "dir": 2},
        "monitor",
        "Normal monitor, wall-mounted, top-left of 2x2",
    )
    add(
        "monitor_normal_wall_tr",
        "CC-Peripheral",
        10,
        1,
        1,
        {"id": "monitor", "xIndex": 1, "yIndex": 0, "width": 2, "height": 2, "dir": 2},
        "monitor",
        "Normal monitor, wall-mounted, top-right of 2x2",
    )
    add(
        "monitor_advanced_ceiling",
        "CC-Peripheral",
        12,
        2,
        1,
        {"id": "monitor", "xIndex": 0, "yIndex": 0, "width": 1, "height": 1, "dir": 9},
        "monitor",
        "Advanced monitor, ceiling-mounted",
    )
    add(
        "monitor_advanced_floor",
        "CC-Peripheral",
        12,
        3,
        1,
        {"id": "monitor", "xIndex": 0, "yIndex": 0, "width": 1, "height": 1, "dir": 15},
        "monitor",
        "Advanced monitor, floor-mounted",
    )

    # Row 2: Peripherals
    add(
        "disk_drive",
        "CC-Peripheral",
        2,
        0,
        2,
        {"id": "diskdrive", "Item": {"id": "minecraft:record_13", "Count": 1, "Damage": 0}},
        "peripheral",
        "Disk drive with a disk inside",
    )
    add(
        "printer",
        "CC-Peripheral",
        11,
        1,
        2,
        {"id": "ccprinter", "page": 1, "title": "TestDoc", "paperCount": 64, "inkCount": 128},
        "peripheral",
        "Printer with paper and ink",
    )
    add(
        "speaker",
        "CC-Peripheral",
        13,
        2,
        2,
        {"id": "speaker"},
        "peripheral",
        "Speaker",
    )
    add(
        "wireless_modem",
        "CC-Peripheral",
        6,
        3,
        2,
        {"id": "wirelessmodem", "peripheralAccess": True},
        "peripheral",
        "Wireless modem (normal)",
    )

    # Row 3: Cables
    add(
        "wired_modem_only",
        "CC-Cable",
        0,
        0,
        3,
        {"id": "wiredmodem", "peripheralAccess": True},
        "cable",
        "Wired modem without cable",
    )
    add(
        "wired_modem_with_cable",
        "CC-Cable",
        6,
        1,
        3,
        {"id": "wiredmodem", "peripheralAccess": True},
        "cable",
        "Wired modem with cable",
    )
    add(
        "cable_only",
        "CC-Cable",
        13,
        2,
        3,
        {"id": "wiredmodem", "peripheralAccess": False},
        "cable",
        "Cable only (no modem)",
    )

    # Row 4: Turtles
    add(
        "turtle_normal",
        "CC-Turtle",
        0,
        0,
        4,
        {
            "id": "turtle",
            "dir": 2,
            "leftUpgrade": 1,
            "rightUpgrade": 2,
            "fuelLevel": 1000,
        },
        "turtle",
        "Normal turtle with wireless modem + crafting table",
    )
    add(
        "turtle_expanded",
        "CC-TurtleExpanded",
        0,
        1,
        4,
        {
            "id": "turtleex",
            "dir": 3,
            "leftUpgrade": -1,
            "rightUpgrade": 8,
        },
        "turtle",
        "Expanded turtle with advanced modem + speaker",
    )
    add(
        "turtle_advanced",
        "CC-TurtleAdvanced",
        0,
        2,
        4,
        {
            "id": "turtleadv",
            "dir": 4,
            "leftUpgrade": "computercraft:wireless_modem",
            "colour": 0xFF0000,
            "overlay": "turtle_rainbow",
        },
        "turtle",
        "Advanced turtle with string upgrade, colour, overlay",
    )

    return samples


def generate_patch(samples: list[Sample]) -> dict[str, Any]:
    edits: list[dict[str, Any]] = []
    metadata_samples: list[dict[str, Any]] = []

    for s in samples:
        edits.append(
            {
                "op": "set_block",
                "x": s.x,
                "y": s.y,
                "z": s.z,
                "id": s.block_id,
                "meta": s.metadata,
            }
        )

        if s.te_nbt:
            # Merge coordinates into TE NBT
            te = dict(s.te_nbt)
            te["x"] = s.x
            te["y"] = s.y
            te["z"] = s.z
            edits.append(
                {
                    "op": "set_te",
                    "x": s.x,
                    "y": s.y,
                    "z": s.z,
                    "nbt": te,
                }
            )

        metadata_samples.append(
            {
                "name": s.name,
                "block": s.block_id,
                "meta": s.metadata,
                "x": s.x,
                "y": s.y,
                "z": s.z,
                "has_te": s.te_nbt is not None,
                "category": s.category,
                "purpose": s.purpose,
            }
        )

    return {
        "edits": edits,
        "metadata": {
            "mod": "computercraft",
            "task": "5A",
            "sample_count": len(samples),
            "samples": metadata_samples,
        },
    }


def main() -> None:
    samples = build_samples()
    patch = generate_patch(samples)
    OUTPUT_PATCH.write_text(json.dumps(patch, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Generated patch with {len(patch['edits'])} edits -> {OUTPUT_PATCH}")
    print(f"Samples: {patch['metadata']['sample_count']}")
    for s in samples:
        te_flag = "+TE" if s.te_nbt else ""
        print(f"  {s.name}: block={s.block_id}:{s.metadata} at ({s.x},{s.y},{s.z}) {te_flag}")


if __name__ == "__main__":
    main()
