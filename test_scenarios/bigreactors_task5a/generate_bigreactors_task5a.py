#!/usr/bin/env python3
"""Generate Big Reactors Task 5A test patch for 1.7.10 world editing.

Produces a Hephaistos-compatible patch JSON that places representative
Big Reactors blocks and tile-entities with varied states.
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

from src.minecraft_map_parser.nbt_parser import parse_nbt  # noqa: E402

WORLD_PATH = PROJECT_ROOT / "mapa_1710"
SOURCE_PATCH = SCENARIO_DIR / "bigreactors_task5a_source_patch_1710.json"


# ---------------------------------------------------------------------------
# Block numeric IDs from level.dat registry
# ---------------------------------------------------------------------------
BLOCK_IDS = {
    "BigReactors:YelloriteOre": 974,
    "BigReactors:BRReactorPart": 977,
    "BigReactors:BRMultiblockGlass": 978,
    "BigReactors:BRTurbinePart": 980,
    "BigReactors:BRDevice": 982,
    "BigReactors:BRMultiblockCreativePart": 1139,
    "BigReactors:BRMetalBlock": 1195,
    "BigReactors:YelloriumFuelRod": 1317,
    "BigReactors:BRTurbineRotorPart": 1410,
    "BigReactors:BRReactorRedstonePort": 1579,
}


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def block_edit(block_id_str: str, meta: int, x: int, y: int, z: int) -> dict[str, Any]:
    return {
        "op": "set_block",
        "x": x,
        "y": y,
        "z": z,
        "id": BLOCK_IDS[block_id_str],
        "meta": meta,
    }


def te_edit(x: int, y: int, z: int, nbt: dict[str, Any]) -> dict[str, Any]:
    return {
        "op": "set_te",
        "x": x,
        "y": y,
        "z": z,
        "nbt": nbt,
    }


def item_stack(item_id: str, count: int = 1, damage: int = 0, slot: int | None = None) -> dict[str, Any]:
    stack: dict[str, Any] = {"id": item_id, "Count": count}
    if damage:
        stack["Damage"] = damage
    if slot is not None:
        stack["Slot"] = slot
    return stack


# ---------------------------------------------------------------------------
# Build source patch
# ---------------------------------------------------------------------------

def build_patch() -> list[dict[str, Any]]:
    edits: list[dict[str, Any]] = []
    base_x, base_y, base_z = 200, 64, 200

    def bx(dx: int = 0, dy: int = 0, dz: int = 0) -> tuple[int, int, int]:
        return (base_x + dx, base_y + dy, base_z + dz)

    # =====================================================================
    # Row 0: Bloki proste (ore, metal blocks, fluids)
    # =====================================================================
    row_z = 0

    # Yellorite Ore
    x, y, z = bx(0, 0, row_z)
    edits.append(block_edit("BigReactors:YelloriteOre", 0, x, y, z))
    edits.append({"op": "set_block", "x": x, "y": y + 1, "z": z, "id": 1, "meta": 0, "note": "stone marker"})

    # Metal blocks (meta 0-4)
    for meta, name in enumerate(["Yellorium", "Cyanite", "Graphite", "Blutonium", "Ludicrite"]):
        x, y, z = bx(1 + meta, 0, row_z)
        edits.append(block_edit("BigReactors:BRMetalBlock", meta, x, y, z))
        edits.append({"op": "set_block", "x": x, "y": y + 1, "z": z, "id": 1, "meta": 0, "note": "stone marker"})

    # =====================================================================
    # Row 1: Reactor parts (BRReactorPart meta 0-7)
    # =====================================================================
    row_z = 2

    reactor_parts = {
        0: ("BRReactorPart", "Reactor Casing"),
        1: ("BRReactorPart", "Reactor Controller"),
        2: ("BRReactorControlRod", "Reactor Control Rod"),
        3: ("BRReactorPowerTap", "Reactor Power Tap"),
        4: ("BRReactorAccessPort", "Reactor Access Port"),
        5: ("BRReactorCoolantPort", "Reactor Coolant Port"),
        6: ("BRReactorRedNetPort", "Reactor RedNet Port"),
        7: ("BRReactorComputerPort", "Reactor Computer Port"),
    }

    for meta, (te_id, label) in reactor_parts.items():
        x, y, z = bx(meta, 0, row_z)
        edits.append(block_edit("BigReactors:BRReactorPart", meta, x, y, z))
        # TE NBT
        nbt: dict[str, Any] = {
            "id": te_id,
            "x": x,
            "y": y,
            "z": z,
            "facing": 3,
        }
        if meta == 2:  # Control Rod
            nbt["controlRodInsertion"] = 50
        if meta == 3:  # Power Tap
            nbt["energyStored"] = 25000
        if meta == 4:  # Access Port
            nbt["Items"] = [
                item_stack("BigReactors:ingotYellorium", 16, slot=0),
                item_stack("BigReactors:ingotBlutonium", 4, slot=1),
            ]
        if meta == 5:  # Coolant Port
            nbt["tanks"] = [{"fluid": "water", "amount": 4000}]
        edits.append(te_edit(x, y, z, nbt))
        edits.append({"op": "set_block", "x": x, "y": y + 1, "z": z, "id": 1, "meta": 0, "note": "stone marker"})

    # Reactor Redstone Port (osobny blok)
    x, y, z = bx(8, 0, row_z)
    edits.append(block_edit("BigReactors:BRReactorRedstonePort", 0, x, y, z))
    edits.append(te_edit(x, y, z, {
        "id": "BRReactorRedstonePort",
        "x": x, "y": y, "z": z,
        "facing": 3,
        "io": 0,
    }))
    edits.append({"op": "set_block", "x": x, "y": y + 1, "z": z, "id": 1, "meta": 0, "note": "stone marker"})

    # Reactor Glass (meta 0)
    x, y, z = bx(9, 0, row_z)
    edits.append(block_edit("BigReactors:BRMultiblockGlass", 0, x, y, z))
    edits.append(te_edit(x, y, z, {
        "id": "BRReactorGlass",
        "x": x, "y": y, "z": z,
    }))
    edits.append({"op": "set_block", "x": x, "y": y + 1, "z": z, "id": 1, "meta": 0, "note": "stone marker"})

    # Fuel Rod
    x, y, z = bx(10, 0, row_z)
    edits.append(block_edit("BigReactors:YelloriumFuelRod", 0, x, y, z))
    edits.append(te_edit(x, y, z, {
        "id": "BRFuelRod",
        "x": x, "y": y, "z": z,
    }))
    edits.append({"op": "set_block", "x": x, "y": y + 1, "z": z, "id": 1, "meta": 0, "note": "stone marker"})

    # =====================================================================
    # Row 2: Turbine parts (BRTurbinePart meta 0-5)
    # =====================================================================
    row_z = 4

    turbine_parts = {
        0: ("BRTurbinePart", "Turbine Housing"),
        1: ("BRTurbinePart", "Turbine Controller"),
        2: ("BRTurbinePowerTap", "Turbine Power Tap"),
        3: ("BRTurbineFluidPort", "Turbine Fluid Port"),
        4: ("BRTurbineRotorBearing", "Turbine Rotor Bearing"),
        5: ("BRTurbineComputerPort", "Turbine Computer Port"),
    }

    for meta, (te_id, label) in turbine_parts.items():
        x, y, z = bx(meta, 0, row_z)
        edits.append(block_edit("BigReactors:BRTurbinePart", meta, x, y, z))
        nbt = {
            "id": te_id,
            "x": x,
            "y": y,
            "z": z,
            "facing": 3,
        }
        if meta == 2:  # Power Tap
            nbt["energyStored"] = 12000
        if meta == 3:  # Fluid Port
            nbt["tanks"] = [{"fluid": "steam", "amount": 8000}]
        edits.append(te_edit(x, y, z, nbt))
        edits.append({"op": "set_block", "x": x, "y": y + 1, "z": z, "id": 1, "meta": 0, "note": "stone marker"})

    # Turbine Glass (meta 1)
    x, y, z = bx(6, 0, row_z)
    edits.append(block_edit("BigReactors:BRMultiblockGlass", 1, x, y, z))
    edits.append(te_edit(x, y, z, {
        "id": "BRTurbineGlass",
        "x": x, "y": y, "z": z,
    }))
    edits.append({"op": "set_block", "x": x, "y": y + 1, "z": z, "id": 1, "meta": 0, "note": "stone marker"})

    # Turbine Rotor Part (shaft=0, blade=1)
    for meta, label in [(0, "Rotor Shaft"), (1, "Rotor Blade")]:
        x, y, z = bx(7 + meta, 0, row_z)
        edits.append(block_edit("BigReactors:BRTurbineRotorPart", meta, x, y, z))
        edits.append(te_edit(x, y, z, {
            "id": "BRTurbineRotorPart",
            "x": x, "y": y, "z": z,
        }))
        edits.append({"op": "set_block", "x": x, "y": y + 1, "z": z, "id": 1, "meta": 0, "note": "stone marker"})

    # =====================================================================
    # Row 3: Cyanite Reprocessor + Creative parts
    # =====================================================================
    row_z = 6

    # Cyanite Reprocessor
    x, y, z = bx(0, 0, row_z)
    edits.append(block_edit("BigReactors:BRDevice", 0, x, y, z))
    edits.append(te_edit(x, y, z, {
        "id": "BRCyaniteReprocessor",
        "x": x, "y": y, "z": z,
        "facing": 3,
        "energyStored": 1500,
        "cookTime": 42,
        "Items": [
            item_stack("BigReactors:ingotCyanite", 2, slot=0),
            item_stack("minecraft:water_bucket", 1, slot=1),
        ],
    }))
    edits.append({"op": "set_block", "x": x, "y": y + 1, "z": z, "id": 1, "meta": 0, "note": "stone marker"})

    # Creative parts (0 = reactor creative coolant, 1 = turbine creative steam)
    for meta, label in [(0, "Creative Coolant"), (1, "Creative Steam")]:
        x, y, z = bx(1 + meta, 0, row_z)
        edits.append(block_edit("BigReactors:BRMultiblockCreativePart", meta, x, y, z))
        te_id = "BRReactorCreativeCoolantPort" if meta == 0 else "BRTurbineCreativeSteamGenerator"
        edits.append(te_edit(x, y, z, {
            "id": te_id,
            "x": x, "y": y, "z": z,
        }))
        edits.append({"op": "set_block", "x": x, "y": y + 1, "z": z, "id": 1, "meta": 0, "note": "stone marker"})

    # =====================================================================
    # Row 4-8: Mini reactor multiblock (3x3x4 interior)
    # =====================================================================
    reactor_base_x = base_x
    reactor_base_z = base_z + 8
    reactor_base_y = base_y

    # Floor / ceiling casing (3x3)
    for ry in [0, 3]:
        for rx in range(3):
            for rz in range(3):
                x = reactor_base_x + rx
                y = reactor_base_y + ry
                z = reactor_base_z + rz
                edits.append(block_edit("BigReactors:BRReactorPart", 0, x, y, z))
                edits.append(te_edit(x, y, z, {
                    "id": "BRReactorPart",
                    "x": x, "y": y, "z": z,
                }))

    # Walls (with glass window)
    for ry in [1, 2]:
        for rx in range(3):
            for rz in range(3):
                if rx == 1 and rz == 1:
                    continue  # interior
                x = reactor_base_x + rx
                y = reactor_base_y + ry
                z = reactor_base_z + rz
                # Front wall glass
                if rx == 1 and rz == 2:
                    edits.append(block_edit("BigReactors:BRMultiblockGlass", 0, x, y, z))
                    edits.append(te_edit(x, y, z, {"id": "BRReactorGlass", "x": x, "y": y, "z": z}))
                else:
                    edits.append(block_edit("BigReactors:BRReactorPart", 0, x, y, z))
                    edits.append(te_edit(x, y, z, {"id": "BRReactorPart", "x": x, "y": y, "z": z}))

    # Fuel rod in center
    x = reactor_base_x + 1
    z = reactor_base_z + 1
    for ry in [1, 2]:
        y = reactor_base_y + ry
        edits.append(block_edit("BigReactors:YelloriumFuelRod", 0, x, y, z))
        edits.append(te_edit(x, y, z, {"id": "BRFuelRod", "x": x, "y": y, "z": z}))

    # Controller on side
    x = reactor_base_x + 1
    y = reactor_base_y + 1
    z = reactor_base_z - 1
    edits.append(block_edit("BigReactors:BRReactorPart", 1, x, y, z))
    edits.append(te_edit(x, y, z, {"id": "BRReactorPart", "x": x, "y": y, "z": z, "facing": 2}))

    # Power tap on other side
    x = reactor_base_x + 3
    y = reactor_base_y + 1
    z = reactor_base_z + 1
    edits.append(block_edit("BigReactors:BRReactorPart", 3, x, y, z))
    edits.append(te_edit(x, y, z, {"id": "BRReactorPowerTap", "x": x, "y": y, "z": z, "facing": 5, "energyStored": 10000}))

    # Access port
    x = reactor_base_x + 1
    y = reactor_base_y + 2
    z = reactor_base_z - 1
    edits.append(block_edit("BigReactors:BRReactorPart", 4, x, y, z))
    edits.append(te_edit(x, y, z, {
        "id": "BRReactorAccessPort",
        "x": x, "y": y, "z": z,
        "facing": 2,
        "Items": [
            item_stack("BigReactors:ingotYellorium", 64, slot=0),
        ],
    }))

    # Control rod on top
    x = reactor_base_x + 1
    y = reactor_base_y + 3
    z = reactor_base_z + 1
    edits.append(block_edit("BigReactors:BRReactorPart", 2, x, y, z))
    edits.append(te_edit(x, y, z, {"id": "BRReactorControlRod", "x": x, "y": y, "z": z, "controlRodInsertion": 75}))

    # =====================================================================
    # Row 9-13: Mini turbine multiblock (3x3x4)
    # =====================================================================
    turbine_base_x = base_x + 5
    turbine_base_z = base_z + 8
    turbine_base_y = base_y

    # Floor / ceiling housing
    for ry in [0, 3]:
        for rx in range(3):
            for rz in range(3):
                x = turbine_base_x + rx
                y = turbine_base_y + ry
                z = turbine_base_z + rz
                edits.append(block_edit("BigReactors:BRTurbinePart", 0, x, y, z))
                edits.append(te_edit(x, y, z, {"id": "BRTurbinePart", "x": x, "y": y, "z": z}))

    # Walls (with glass)
    for ry in [1, 2]:
        for rx in range(3):
            for rz in range(3):
                if rx == 1 and rz == 1:
                    continue
                x = turbine_base_x + rx
                y = turbine_base_y + ry
                z = turbine_base_z + rz
                if rx == 1 and rz == 2:
                    edits.append(block_edit("BigReactors:BRMultiblockGlass", 1, x, y, z))
                    edits.append(te_edit(x, y, z, {"id": "BRTurbineGlass", "x": x, "y": y, "z": z}))
                else:
                    edits.append(block_edit("BigReactors:BRTurbinePart", 0, x, y, z))
                    edits.append(te_edit(x, y, z, {"id": "BRTurbinePart", "x": x, "y": y, "z": z}))

    # Rotor shaft in center
    x = turbine_base_x + 1
    z = turbine_base_z + 1
    for ry in [1, 2]:
        y = turbine_base_y + ry
        edits.append(block_edit("BigReactors:BRTurbineRotorPart", 0, x, y, z))
        edits.append(te_edit(x, y, z, {"id": "BRTurbineRotorPart", "x": x, "y": y, "z": z}))

    # Rotor blades around shaft
    for dx, dz in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
        x = turbine_base_x + 1 + dx
        z = turbine_base_z + 1 + dz
        for ry in [1, 2]:
            y = turbine_base_y + ry
            edits.append(block_edit("BigReactors:BRTurbineRotorPart", 1, x, y, z))
            edits.append(te_edit(x, y, z, {"id": "BRTurbineRotorPart", "x": x, "y": y, "z": z}))

    # Bearing on front
    x = turbine_base_x + 1
    y = turbine_base_y + 1
    z = turbine_base_z - 1
    edits.append(block_edit("BigReactors:BRTurbinePart", 4, x, y, z))
    edits.append(te_edit(x, y, z, {"id": "BRTurbineRotorBearing", "x": x, "y": y, "z": z, "facing": 2}))

    # Power tap
    x = turbine_base_x + 3
    y = turbine_base_y + 1
    z = turbine_base_z + 1
    edits.append(block_edit("BigReactors:BRTurbinePart", 2, x, y, z))
    edits.append(te_edit(x, y, z, {"id": "BRTurbinePowerTap", "x": x, "y": y, "z": z, "facing": 5, "energyStored": 5000}))

    # Fluid port
    x = turbine_base_x + 1
    y = turbine_base_y + 2
    z = turbine_base_z - 1
    edits.append(block_edit("BigReactors:BRTurbinePart", 3, x, y, z))
    edits.append(te_edit(x, y, z, {"id": "BRTurbineFluidPort", "x": x, "y": y, "z": z, "facing": 2}))

    # Controller on top
    x = turbine_base_x + 1
    y = turbine_base_y + 3
    z = turbine_base_z + 1
    edits.append(block_edit("BigReactors:BRTurbinePart", 1, x, y, z))
    edits.append(te_edit(x, y, z, {"id": "BRTurbinePart", "x": x, "y": y, "z": z}))

    return edits


def main() -> None:
    edits = build_patch()
    patch = {"edits": edits}
    SOURCE_PATCH.write_text(json.dumps(patch, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"Generated {len(edits)} edits -> {SOURCE_PATCH}")

    # Summary
    blocks = sum(1 for e in edits if e["op"] == "set_block")
    tes = sum(1 for e in edits if e["op"] == "set_te")
    print(f"  Blocks: {blocks}")
    print(f"  TEs: {tes}")


if __name__ == "__main__":
    main()
