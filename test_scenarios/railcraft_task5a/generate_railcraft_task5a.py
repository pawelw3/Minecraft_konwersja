#!/usr/bin/env python3
"""Generate Railcraft Task 5A source/converted patches and redstone harness."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parents[2]
SCENARIO_DIR = Path(__file__).resolve().parent
WORLD_PATH = PROJECT_ROOT / "mapa_1710"

sys.path.insert(0, str(PROJECT_ROOT))
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from src.converters.mekanism.analyze_map_coverage import load_block_registry  # noqa: E402


SOURCE_PATCH = SCENARIO_DIR / "railcraft_task5a_source_patch_1710.json"
CONVERTED_PATCH = SCENARIO_DIR / "railcraft_task5a_converted_patch_1182.json"
CONVERSION_REPORT = SCENARIO_DIR / "railcraft_task5a_conversion_report.json"
REPORT_MD = SCENARIO_DIR / "RAILCRAFT_TASK5A_REPORT.md"


def write_json(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def railcraft_numeric_registry() -> dict[str, int]:
    registry = load_block_registry(WORLD_PATH)
    return {name: int(numeric_id) for numeric_id, name in registry.items() if isinstance(name, str) and name.startswith("Railcraft:")}


def raw_id(block_id: str) -> str:
    return block_id.split(":")[-1]


def item_stack(item_id: str, count: int = 1, damage: int = 0, slot: int | None = None) -> dict[str, Any]:
    stack: dict[str, Any] = {"id": item_id, "Count": count}
    if damage:
        stack["Damage"] = damage
    if slot is not None:
        stack["Slot"] = slot
    return stack


def base_nbt(te_id: str, x: int, y: int, z: int) -> dict[str, Any]:
    return {"id": te_id, "x": x, "y": y, "z": z}


Sample = dict[str, Any]


def make_samples(reg: dict[str, int]) -> list[Sample]:
    samples: list[Sample] = []
    x0, y0, z0 = 200, 64, 200  # start area for test map

    def add(name: str, block_name: str, meta: int, te_id: str | None, nbt_extra: dict[str, Any] | None = None, label: str = ""):
        x = x0 + len(samples) * 2
        z = z0
        block_id = reg.get(block_name, 0)
        sample: Sample = {
            "name": name,
            "label": label or name,
            "block_name": block_name,
            "block_id": block_id,
            "metadata": meta,
            "x": x,
            "y": y0,
            "z": z,
            "te_id": te_id,
            "nbt": None,
        }
        if te_id:
            nbt = base_nbt(te_id, x, y0, z)
            if nbt_extra:
                nbt.update(nbt_extra)
            sample["nbt"] = nbt
        samples.append(sample)

    # ── TRACKS ──
    add("track_reinforced", "Railcraft:track", 4, "RailcraftTrackTile", {"trackTag": "railcraft:track.reinforced"})
    add("track_switch", "Railcraft:track", 1, "RailcraftTrackTESRTile", {"trackTag": "railcraft:track.switch"})
    add("track_control", "Railcraft:track", 0, "RailcraftTrackTile", {"trackTag": "railcraft:track.control"})

    # ── MACHINES ALPHA ──
    add("coke_oven_empty", "Railcraft:machine.alpha", 7, "RCCokeOvenTile")
    add("coke_oven_with_coal", "Railcraft:machine.alpha", 7, "RCCokeOvenTile",
        {"Items": [item_stack("minecraft:coal", 16, slot=0)]},
        label="coke_oven_with_inventory")
    add("blast_furnace", "Railcraft:machine.alpha", 12, "RCBlastFurnaceTile",
        {"Items": [item_stack("minecraft:iron_ingot", 8, slot=0)]})
    add("rolling_machine", "Railcraft:machine.alpha", 8, "RCRollingMachineTile")
    add("rock_crusher", "Railcraft:machine.alpha", 15, "RCRockCrusherTile")
    add("smoker", "Railcraft:machine.alpha", 5, "RCSmokerTile")
    add("steam_oven", "Railcraft:machine.alpha", 3, "RCSteamOvenTile")
    add("world_anchor", "Railcraft:machine.alpha", 0, "RCWorldAnchorTile")
    add("personal_anchor", "Railcraft:machine.alpha", 2, "RCPersonalAnchorTile")
    add("feed_station", "Railcraft:machine.alpha", 11, "RCFeedStationTile")
    add("water_tank", "Railcraft:machine.alpha", 14, "RCWaterTankTile")

    # ── MACHINES BETA ──
    add("boiler_tank_high", "Railcraft:machine.beta", 4, "RCBoilerTankHighTile")
    add("boiler_firebox_liquid", "Railcraft:machine.beta", 6, "RCBoilerFireboxLiquidTile")
    add("engine_steam_hobby", "Railcraft:machine.beta", 7, "RCEngineSteamHobby")
    add("engine_steam_low", "Railcraft:machine.beta", 8, "RCEngineSteamLow")
    add("engine_steam_high", "Railcraft:machine.beta", 9, "RCEngineSteamHigh")
    add("iron_tank_wall", "Railcraft:machine.beta", 0, "RCIronTankWallTile")
    add("iron_tank_gauge", "Railcraft:machine.beta", 1, "RCIronTankGaugeTile")
    add("iron_tank_valve", "Railcraft:machine.beta", 2, "RCIronTankValveTile")
    add("steel_tank_wall", "Railcraft:machine.beta", 13, "RCSteelTankWallTile")
    add("steel_tank_gauge", "Railcraft:machine.beta", 14, "RCSteelTankGaugeTile")
    add("steel_tank_valve", "Railcraft:machine.beta", 15, "RCSteelTankValveTile")
    add("void_chest_empty", "Railcraft:machine.beta", 11, "RCVoidChestTile")
    add("void_chest_with_items", "Railcraft:machine.beta", 11, "RCVoidChestTile",
        {"Items": [
            item_stack("minecraft:diamond", 3, slot=0),
            item_stack("minecraft:stone", 64, slot=1),
        ]},
        label="void_chest_with_inventory")
    add("metals_chest", "Railcraft:machine.beta", 12, "RCMetalsChestTile")
    add("anchor_sentinel", "Railcraft:machine.beta", 10, "RCAnchorSentinelTile")

    # ── MACHINES GAMMA ──
    add("item_loader", "Railcraft:machine.gamma", 0, "RCLoaderTile")
    add("item_unloader", "Railcraft:machine.gamma", 1, "RCUnloaderTile")
    add("adv_item_loader", "Railcraft:machine.gamma", 2, "RCLoaderAdvancedTile")
    add("fluid_loader", "Railcraft:machine.gamma", 4, "RCLoaderTileLiquid")
    add("energy_loader", "Railcraft:machine.gamma", 6, "RCLoaderTileEnergy")
    add("cart_dispenser", "Railcraft:machine.gamma", 8, "RCMinecartDispenserTile")

    # ── MACHINES DELTA ──
    add("shunting_wire", "Railcraft:machine.delta", 0, "RCWireTile")

    # ── MACHINES EPSILON ──
    add("electric_feeder", "Railcraft:machine.epsilon", 0, "RCElectricFeederTile")
    add("flux_transformer", "Railcraft:machine.epsilon", 4, "RCFluxTransformerTile")
    add("engraving_bench", "Railcraft:machine.epsilon", 5, "RCEngravingBenchTile")

    # ── SIGNALS ──
    add("signal_block", "Railcraft:signal", 3, "RCTileStructureSignal")
    add("signal_distant", "Railcraft:signal", 11, "RCTileStructureSignal")
    add("signal_switch_lever", "Railcraft:signal", 4, "RCTileStructureSwitch")
    add("signal_receiver_box", "Railcraft:signal", 8, "RCTileStructureReceiverBox")
    add("signal_controller_box", "Railcraft:signal", 9, "RCTileStructureControllerBox")
    add("signal_sequencer_box", "Railcraft:signal", 6, "RCTileStructureSequencer")
    add("signal_capacitor_box", "Railcraft:signal", 7, "RCTileStructureCapacitor")
    add("signal_analog_box", "Railcraft:signal", 10, "RCTileStructureAnalog")

    # ── DETECTORS ──
    add("detector_any", "Railcraft:detector", 0, "RCDetectorTile")
    add("detector_mob", "Railcraft:detector", 4, "RCDetectorTile")
    add("detector_player", "Railcraft:detector", 5, "RCDetectorTile")
    add("detector_animal", "Railcraft:detector", 6, "RCDetectorTile")
    add("detector_villager", "Railcraft:detector", 7, "RCDetectorTile")
    add("detector_item", "Railcraft:detector", 8, "RCDetectorTile")
    add("detector_train", "Railcraft:detector", 9, "RCDetectorTile")
    add("detector_routing", "Railcraft:detector", 10, "RCDetectorTile")
    add("detector_locomotive", "Railcraft:detector", 11, "RCDetectorTile")

    # ── AESTHETICS ──
    add("slab_iron", "Railcraft:slab", 0, "RCSlabTile", {"slab": "IRON"})
    add("slab_steel_top", "Railcraft:slab", 8, "RCSlabTile", {"slab": "STEEL"})  # top half via meta 8
    add("stair_iron", "Railcraft:stair", 3, "RCStairTile", {"stair": "IRON"})
    add("stair_steel_upside", "Railcraft:stair", 7, "RCStairTile", {"stair": "STEEL"})  # upside-down via meta 4+?

    # ── OTHER ──
    add("residual_heat", "Railcraft:residual.heat", 0, "RCHiddenTile")
    add("firestone_recharge", "Railcraft:firestone.recharge", 0, "RCFirestoneRechargeTile")
    add("lantern_stone", "Railcraft:lantern.stone", 0, None)
    add("lantern_metal", "Railcraft:lantern.metal", 0, None)
    add("cube_steel", "Railcraft:cube", 2, None)
    add("anvil_steel", "Railcraft:anvil", 0, None)

    return samples


def build_source_patch(samples: list[Sample]) -> dict[str, Any]:
    edits: list[dict[str, Any]] = []
    for s in samples:
        block_edit = {
            "op": "set_block",
            "x": s["x"],
            "y": s["y"],
            "z": s["z"],
            "id": s["block_id"],
            "meta": s["metadata"],
            "registry_name": s["block_name"],
            "label": s["label"],
        }
        edits.append(block_edit)
        if s["te_id"] and s["nbt"]:
            te_edit = {
                "op": "set_te",
                "x": s["x"],
                "y": s["y"],
                "z": s["z"],
                "nbt": s["nbt"],
                "label": s["label"],
            }
            edits.append(te_edit)
    return {
        "format_version": "1.7.10",
        "metadata": {
            "name": "railcraft_task5a_source",
            "generated_by": "generate_railcraft_task5a.py",
            "source_world_for_dynamic_ids": str(WORLD_PATH),
            "samples": len(samples),
        },
        "edits": edits,
    }


def main() -> None:
    print("Loading block registry from", WORLD_PATH)
    reg = railcraft_numeric_registry()
    if not reg:
        print("WARNING: No Railcraft blocks found in registry; using hardcoded fallback IDs")

    samples = make_samples(reg)
    print(f"Generated {len(samples)} samples")

    source_patch = build_source_patch(samples)
    write_json(SOURCE_PATCH, source_patch)
    print("Wrote source patch:", SOURCE_PATCH)

    # Print summary
    missing = [s["block_name"] for s in samples if s["block_id"] == 0]
    if missing:
        print("WARNING: Missing registry IDs for:", missing)
    else:
        print("All sample blocks resolved from registry.")


if __name__ == "__main__":
    main()
