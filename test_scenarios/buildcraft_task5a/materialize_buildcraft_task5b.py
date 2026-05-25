#!/usr/bin/env python3
"""Materialize BuildCraft Task 5B as a 1.18.2 headless-server datapack."""

from __future__ import annotations

import argparse
import json
import shutil
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parents[2]
SCENARIO_DIR = Path(__file__).resolve().parent
DEFAULT_PATCH = SCENARIO_DIR / "buildcraft_task5a_converted_patch_1182.json"
DEFAULT_SERVER_DIR = PROJECT_ROOT / "headless_server/1.18.2"
DEFAULT_BASE_WORLD = DEFAULT_SERVER_DIR / "world"
DEFAULT_TARGET_WORLD = DEFAULT_SERVER_DIR / "world_buildcraft_task5b"
DEFAULT_REPORT = SCENARIO_DIR / "buildcraft_task5b_headless_materialization_report.json"
DEFAULT_SERVER_PROPERTIES = SCENARIO_DIR / "server_buildcraft_task5b.properties"
RECIPE_SOURCE = PROJECT_ROOT / "src/converters/buildcraft/data_pack_recipes"

# 1.7.10 numeric item ID -> 1.18.2 item ID string (minimal mapping)
ITEM_ID_MAP: dict[int, str] = {
    263: "minecraft:coal",
}


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, data: dict[str, Any]) -> None:
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def quote_snbt_string(value: str) -> str:
    return json.dumps(value, ensure_ascii=False)


def to_snbt(value: Any) -> str:
    if value is None:
        return '""'
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, int):
        return str(value)
    if isinstance(value, float):
        return repr(value)
    if isinstance(value, str):
        return quote_snbt_string(value)
    if isinstance(value, list):
        return "[" + ",".join(to_snbt(item) for item in value) + "]"
    if isinstance(value, dict):
        items = []
        for key, item in value.items():
            if item is None:
                continue
            safe = key.replace("_", "").replace("-", "").replace(".", "").replace(":", "").isalnum()
            key_text = key if safe else quote_snbt_string(key)
            items.append(f"{key_text}:{to_snbt(item)}")
        return "{" + ",".join(items) + "}"
    return quote_snbt_string(str(value))


def fix_numeric_item_ids(nbt: Any) -> Any:
    """Recursively replace numeric item IDs in NBT with 1.18.2 string IDs."""
    if isinstance(nbt, dict):
        fixed: dict[str, Any] = {}
        for k, v in nbt.items():
            if k == "id" and isinstance(v, int) and v in ITEM_ID_MAP:
                fixed[k] = ITEM_ID_MAP[v]
            else:
                fixed[k] = fix_numeric_item_ids(v)
        return fixed
    if isinstance(nbt, list):
        return [fix_numeric_item_ids(item) for item in nbt]
    return nbt


def block_state(block_id: str, properties: dict[str, Any] | None) -> str:
    if not properties:
        return block_id
    props = ",".join(f"{key}={value}" for key, value in sorted(properties.items()))
    return f"{block_id}[{props}]"


def setblock_command(edit: dict[str, Any]) -> str:
    pos = edit["pos"]
    x, y, z = pos[0], pos[1], pos[2]
    block_id = str(edit["block"])
    properties = edit.get("blockstate") or edit.get("properties")
    state = block_state(block_id, properties)
    raw_nbt = edit.get("nbt")
    if raw_nbt is not None:
        nbt = fix_numeric_item_ids(raw_nbt)
        nbt_snbt = to_snbt(nbt)
        return f"setblock {x} {y} {z} {state}{nbt_snbt} replace"
    return f"setblock {x} {y} {z} {state} replace"


def write_datapack(target_world: Path, commands: list[str]) -> dict[str, Any]:
    datapack_root = target_world / "datapacks" / "buildcraft_task5b"
    function_dir = datapack_root / "data" / "buildcraft_task5b" / "functions"
    load_tag_dir = datapack_root / "data" / "minecraft" / "tags" / "functions"
    recipe_dir = datapack_root / "data" / "buildcraft_conversion" / "recipes" / "machines" / "refinery"

    function_dir.mkdir(parents=True, exist_ok=True)
    load_tag_dir.mkdir(parents=True, exist_ok=True)
    recipe_dir.mkdir(parents=True, exist_ok=True)

    (datapack_root / "pack.mcmeta").write_text(
        json.dumps(
            {
                "pack": {
                    "pack_format": 9,
                    "description": "BuildCraft Task 5B materialization datapack",
                }
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    (load_tag_dir / "load.json").write_text(
        json.dumps({"values": ["buildcraft_task5b:apply"]}, indent=2) + "\n",
        encoding="utf-8",
    )

    function_lines = [
        "say [BUILDCRAFT_TASK5B] applying converted BuildCraft 5A patch",
        *commands,
        "say [BUILDCRAFT_TASK5B] apply complete",
    ]
    apply_path = function_dir / "apply.mcfunction"
    apply_path.write_text("\n".join(function_lines) + "\n", encoding="utf-8")

    # Copy custom recipe
    recipe_src = RECIPE_SOURCE / "data" / "buildcraft_conversion" / "recipes" / "machines" / "refinery" / "bc_oil_to_fuel.json"
    if recipe_src.exists():
        shutil.copy2(recipe_src, recipe_dir / "bc_oil_to_fuel.json")
        recipe_copied = str(recipe_dir / "bc_oil_to_fuel.json")
    else:
        recipe_copied = None

    return {
        "datapack_root": str(datapack_root),
        "apply_function": str(apply_path),
        "load_function": "buildcraft_task5b:apply",
        "function_lines": len(function_lines),
        "recipe_copied": recipe_copied,
    }


def copy_world(base_world: Path, target_world: Path, overwrite: bool) -> None:
    if target_world.exists():
        if not overwrite:
            return
        resolved = target_world.resolve()
        root = PROJECT_ROOT.resolve()
        if not str(resolved).startswith(str(root)):
            raise RuntimeError(f"Refusing to remove target outside project: {resolved}")
        shutil.rmtree(target_world)
    shutil.copytree(base_world, target_world)


def write_server_properties_template(server_dir: Path, target_world: Path, output_path: Path) -> None:
    source = server_dir / "server.properties"
    text = source.read_text(encoding="utf-8")
    lines = []
    replaced = False
    for line in text.splitlines():
        if line.startswith("level-name="):
            lines.append(f"level-name={target_world.name}")
            replaced = True
        else:
            lines.append(line)
    if not replaced:
        lines.append(f"level-name={target_world.name}")
    output_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def materialize(args: argparse.Namespace) -> dict[str, Any]:
    patch = load_json(args.patch)
    commands: list[str] = []
    for edit in patch.get("edits", []):
        commands.append(setblock_command(edit))

    copy_world(args.base_world, args.target_world, args.overwrite)
    datapack = write_datapack(args.target_world, commands)
    write_server_properties_template(args.server_dir, args.target_world, args.server_properties_out)

    block_edits = [e for e in patch.get("edits", []) if e.get("op") in ("set_block", "set_block_entity")]
    te_edits = [e for e in patch.get("edits", []) if e.get("op") == "set_block_entity"]

    report = {
        "name": "BuildCraft Task 5B headless materialization",
        "status": "world_copy_prepared_with_datapack",
        "patch": str(args.patch),
        "server_dir": str(args.server_dir),
        "base_world": str(args.base_world),
        "target_world": str(args.target_world),
        "server_properties_template": str(args.server_properties_out),
        "datapack": datapack,
        "stats": {
            "commands": len(commands),
            "block_edits": len(block_edits),
            "tile_entity_edits": len(te_edits),
        },
        "next_steps": [
            f"Copy {args.server_properties_out} to {args.server_dir / 'server.properties'}.",
            "Start the 1.18.2 Forge headless server.",
            "Confirm logs contain [BUILDCRAFT_TASK5B] apply complete.",
            "Continue with Task 6: tick/restart verification.",
        ],
    }
    write_json(args.report, report)
    return report


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--patch", type=Path, default=DEFAULT_PATCH)
    parser.add_argument("--server-dir", type=Path, default=DEFAULT_SERVER_DIR)
    parser.add_argument("--base-world", type=Path, default=DEFAULT_BASE_WORLD)
    parser.add_argument("--target-world", type=Path, default=DEFAULT_TARGET_WORLD)
    parser.add_argument("--report", type=Path, default=DEFAULT_REPORT)
    parser.add_argument("--server-properties-out", type=Path, default=DEFAULT_SERVER_PROPERTIES)
    parser.add_argument("--overwrite", action="store_true")
    args = parser.parse_args()

    report = materialize(args)
    print(f"Target world: {report['target_world']}")
    print(f"Datapack: {report['datapack']['datapack_root']}")
    print(f"Commands: {report['stats']['commands']}")
    print(f"Block edits: {report['stats']['block_edits']}")
    print(f"Tile entity edits: {report['stats']['tile_entity_edits']}")
    print(f"Report: {args.report}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
