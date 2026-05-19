#!/usr/bin/env python3
"""Repair FML registry data for the 1.7.10 placeholder ZSRR slice.

The slice stores placeholder blocks as numeric block id 4095. Forge still needs
the rest of the current client registry in FML.ItemData, otherwise it tries to
inject missing blocks during world load and can hit invalid block ids. This
script copies registry metadata from a known-good 1.7.10 world created with the
same modpack, then pins the local placeholder block/item to id 4095.
"""

from __future__ import annotations

import argparse
import copy
import json
from pathlib import Path
from typing import Any

import nbtlib
from nbtlib import Compound, Int, List, String


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_TARGET = PROJECT_ROOT / "lightweigh_map_templates" / "1710_modded" / "zsrr_ae2_mek_300_placeholders_1710"
DEFAULT_REPORT = Path(__file__).with_name("zsrr_ae2_mek_300_placeholders_1710_registry_repair_report.json")

PLACEHOLDER_BLOCK_ID = 4095
PLACEHOLDER_REGISTRY = "conversionplaceholders1710:block_entity_placeholder"
PLACEHOLDER_MOD_ID = "conversionplaceholders1710"
PLACEHOLDER_MOD_VERSION = "1.0.0"

FML_REGISTRY_KEYS = (
    "BlockedItemIds",
    "ItemSubstitutions",
    "BlockAliases",
    "BlockSubstitutions",
    "ItemAliases",
    "ModList",
    "ItemData",
)


def write_json(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def ensure_placeholder_entries(item_data: List[Compound]) -> None:
    desired = {
        "\x01" + PLACEHOLDER_REGISTRY: PLACEHOLDER_BLOCK_ID,
        "\x02" + PLACEHOLDER_REGISTRY: PLACEHOLDER_BLOCK_ID,
    }
    seen: set[str] = set()
    for entry in item_data:
        key = str(entry.get("K"))
        if key in desired:
            entry["V"] = Int(desired[key])
            seen.add(key)
    for key, value in desired.items():
        if key not in seen:
            item_data.append(Compound({"K": String(key), "V": Int(value)}))


def ensure_placeholder_mod(mod_list: List[Compound]) -> None:
    for entry in mod_list:
        if str(entry.get("ModId")) == PLACEHOLDER_MOD_ID:
            entry["ModVersion"] = String(PLACEHOLDER_MOD_VERSION)
            return
    mod_list.append(Compound({"ModId": String(PLACEHOLDER_MOD_ID), "ModVersion": String(PLACEHOLDER_MOD_VERSION)}))


def registry_stats(item_data: List[Compound]) -> dict[str, Any]:
    block_count = 0
    item_count = 0
    bad_block_ids: list[dict[str, Any]] = []
    placeholder_entries: list[dict[str, Any]] = []
    used_ids: dict[int, list[str]] = {}
    for entry in item_data:
        key = str(entry.get("K"))
        value = int(entry.get("V", -1))
        kind = key[:1]
        name = key[1:] if kind in ("\x01", "\x02") else key
        if kind == "\x01":
            block_count += 1
            if value > 4095:
                bad_block_ids.append({"id": value, "name": name})
        elif kind == "\x02":
            item_count += 1
        if name == PLACEHOLDER_REGISTRY:
            placeholder_entries.append({"key": repr(key), "id": value})
        used_ids.setdefault(value, []).append(key)
    placeholder_conflicts = [
        key for key in used_ids.get(PLACEHOLDER_BLOCK_ID, [])
        if key not in ("\x01" + PLACEHOLDER_REGISTRY, "\x02" + PLACEHOLDER_REGISTRY)
    ]
    return {
        "itemdata": len(item_data),
        "blocks": block_count,
        "items": item_count,
        "bad_block_ids": bad_block_ids[:50],
        "bad_block_id_count": len(bad_block_ids),
        "placeholder_entries": placeholder_entries,
        "placeholder_id_conflicts": placeholder_conflicts,
    }


def load_registry(source_level_dat: Path) -> Compound:
    source_nbt = nbtlib.load(source_level_dat)
    source_fml = source_nbt.get("FML")
    if not isinstance(source_fml, Compound):
        raise ValueError(f"{source_level_dat} does not contain root FML data")
    new_fml = Compound()
    for key in FML_REGISTRY_KEYS:
        if key in source_fml:
            new_fml[key] = copy.deepcopy(source_fml[key])
    new_fml.setdefault("ItemData", List[Compound]())
    new_fml.setdefault("ModList", List[Compound]())
    ensure_placeholder_entries(new_fml["ItemData"])
    ensure_placeholder_mod(new_fml["ModList"])
    stats = registry_stats(new_fml["ItemData"])
    if stats["bad_block_id_count"]:
        raise ValueError(f"Source registry still has block ids >4095: {stats['bad_block_ids'][:5]}")
    if stats["placeholder_id_conflicts"]:
        raise ValueError(f"Placeholder id {PLACEHOLDER_BLOCK_ID} conflicts with {stats['placeholder_id_conflicts'][:5]}")
    return new_fml


def repair_file(target_level_dat: Path, repaired_fml: Compound) -> dict[str, Any]:
    target_nbt = nbtlib.load(target_level_dat)
    old_fml = target_nbt.get("FML")
    old_stats = registry_stats(old_fml.get("ItemData", List[Compound]())) if isinstance(old_fml, Compound) else {}
    target_nbt["FML"] = copy.deepcopy(repaired_fml)
    target_nbt.save(target_level_dat, gzipped=True)
    new_stats = registry_stats(target_nbt["FML"]["ItemData"])
    return {
        "file": str(target_level_dat),
        "old": old_stats,
        "new": new_stats,
        "modlist": len(target_nbt["FML"].get("ModList", [])),
    }


def repair_world(target_world: Path, source_level_dat: Path) -> dict[str, Any]:
    repaired_fml = load_registry(source_level_dat)
    files = []
    for name in ("level.dat", "level.dat_old"):
        path = target_world / name
        if path.exists():
            files.append(repair_file(path, repaired_fml))
    return {
        "target_world": str(target_world),
        "source_level_dat": str(source_level_dat),
        "placeholder_id": PLACEHOLDER_BLOCK_ID,
        "files": files,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--target-world", type=Path, default=DEFAULT_TARGET)
    parser.add_argument("--source-level-dat", type=Path, required=True)
    parser.add_argument("--report", type=Path, default=DEFAULT_REPORT)
    args = parser.parse_args()

    report = repair_world(args.target_world, args.source_level_dat)
    write_json(args.report, report)
    for item in report["files"]:
        print(
            f"{Path(item['file']).name}: ItemData {item['old'].get('itemdata')} -> "
            f"{item['new']['itemdata']}; blocks {item['new']['blocks']}; "
            f"bad block ids {item['new']['bad_block_id_count']}; modlist {item['modlist']}"
        )
    print(f"Report: {args.report}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
