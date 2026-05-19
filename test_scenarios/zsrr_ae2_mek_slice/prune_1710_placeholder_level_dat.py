#!/usr/bin/env python3
"""Prune FML registry data for the 1.7.10 placeholder ZSRR slice.

The placeholder world intentionally keeps only vanilla, AE2, Mekanism and the
local placeholder block. Leaving thousands of old ItemData mappings for removed
mods makes Forge 1.7.10 stop at the missing-mapping confirmation screen and may
cause it to load a backup level.dat. This script removes those stale mappings
from level.dat and level.dat_old.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import nbtlib
from nbtlib import Compound, Int, List, String


PROJECT_ROOT = Path(__file__).resolve().parents[2]
SCENARIO_DIR = Path(__file__).resolve().parent
DEFAULT_WORLD = PROJECT_ROOT / "lightweigh_map_templates" / "1710_modded" / "zsrr_ae2_mek_300_placeholders_1710"
DEFAULT_REPORT = SCENARIO_DIR / "zsrr_ae2_mek_300_placeholders_1710_level_prune_report.json"

PLACEHOLDER_BLOCK_ID = 4095
PLACEHOLDER_BLOCK_REGISTRY = "conversionplaceholders1710:block_entity_placeholder"
PLACEHOLDER_MOD_ID = "conversionplaceholders1710"
PLACEHOLDER_MOD_VERSION = "1.0.0"

KEEP_ITEM_NAMESPACES = {
    "minecraft",
    "appliedenergistics2",
    "Mekanism",
    "MekanismGenerators",
    "MekanismTools",
    PLACEHOLDER_MOD_ID,
}

KEEP_MOD_IDS = {
    "mcp",
    "FML",
    "Forge",
    "CodeChickenCore",
    "appliedenergistics2-core",
    "appliedenergistics2",
    "Mekanism",
    "MekanismGenerators",
    "MekanismTools",
    PLACEHOLDER_MOD_ID,
}


def write_json(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def item_namespace(key: str) -> str:
    name = key[1:] if key and key[0] in ("\x01", "\x02") else key
    return name.split(":", 1)[0]


def ensure_placeholder_entries(item_data: List[Compound]) -> None:
    existing_by_key = {str(entry.get("K")): entry for entry in item_data}
    desired = {
        "\x01" + PLACEHOLDER_BLOCK_REGISTRY: PLACEHOLDER_BLOCK_ID,
        "\x02" + PLACEHOLDER_BLOCK_REGISTRY: PLACEHOLDER_BLOCK_ID,
    }
    for key, value in desired.items():
        if key in existing_by_key:
            existing_by_key[key]["V"] = Int(value)
        else:
            item_data.append(Compound({"K": String(key), "V": Int(value)}))


def ensure_placeholder_mod(mod_list: List[Compound]) -> None:
    for entry in mod_list:
        if str(entry.get("ModId")) == PLACEHOLDER_MOD_ID:
            entry["ModVersion"] = String(PLACEHOLDER_MOD_VERSION)
            return
    mod_list.append(Compound({
        "ModId": String(PLACEHOLDER_MOD_ID),
        "ModVersion": String(PLACEHOLDER_MOD_VERSION),
    }))


def prune_file(path: Path) -> dict[str, Any]:
    nbt_file = nbtlib.load(path)
    fml = nbt_file.setdefault("FML", Compound())
    item_data = fml.setdefault("ItemData", List[Compound]())
    mod_list = fml.setdefault("ModList", List[Compound]())

    before_itemdata = len(item_data)
    before_modlist = len(mod_list)

    kept_item_entries = []
    removed_namespaces: dict[str, int] = {}
    for entry in item_data:
        key = str(entry.get("K"))
        namespace = item_namespace(key)
        if namespace in KEEP_ITEM_NAMESPACES:
            kept_item_entries.append(entry)
        else:
            removed_namespaces[namespace] = removed_namespaces.get(namespace, 0) + 1

    new_item_data = List[Compound](kept_item_entries)
    ensure_placeholder_entries(new_item_data)

    kept_mod_entries = []
    removed_mods: list[str] = []
    for entry in mod_list:
        mod_id = str(entry.get("ModId"))
        if mod_id in KEEP_MOD_IDS:
            kept_mod_entries.append(entry)
        else:
            removed_mods.append(mod_id)
    new_mod_list = List[Compound](kept_mod_entries)
    ensure_placeholder_mod(new_mod_list)

    fml["ItemData"] = new_item_data
    fml["ModList"] = new_mod_list
    nbt_file.save(path, gzipped=True)

    return {
        "file": str(path),
        "itemdata_before": before_itemdata,
        "itemdata_after": len(new_item_data),
        "modlist_before": before_modlist,
        "modlist_after": len(new_mod_list),
        "removed_item_namespaces": dict(sorted(removed_namespaces.items(), key=lambda item: (-item[1], item[0]))[:100]),
        "removed_mods": sorted(set(removed_mods)),
    }


def prune_world(world: Path) -> dict[str, Any]:
    files = []
    for name in ("level.dat", "level.dat_old"):
        path = world / name
        if path.exists():
            files.append(prune_file(path))
    return {
        "world": str(world),
        "keep_item_namespaces": sorted(KEEP_ITEM_NAMESPACES),
        "keep_mod_ids": sorted(KEEP_MOD_IDS),
        "files": files,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--world", type=Path, default=DEFAULT_WORLD)
    parser.add_argument("--report", type=Path, default=DEFAULT_REPORT)
    args = parser.parse_args()

    report = prune_world(args.world)
    write_json(args.report, report)
    for item in report["files"]:
        print(
            f"{Path(item['file']).name}: ItemData {item['itemdata_before']} -> {item['itemdata_after']}; "
            f"ModList {item['modlist_before']} -> {item['modlist_after']}"
        )
    print(f"Report: {args.report}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
