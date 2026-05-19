#!/usr/bin/env python3
"""Materialize AE2 Task 5B as a 1.18.2 headless-server datapack.

The project does not yet rely on a direct 1.18.2 MCA writer for these modded
block palettes. This prepares a dedicated headless world copy and a datapack
whose load function applies the converted 1.18.2 patch with `/setblock`.
Task 6 can then boot this world, tick it, save it, and restart it.
"""

from __future__ import annotations

import argparse
import json
import shutil
import zipfile
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parents[2]
SCENARIO_DIR = Path(__file__).resolve().parent
DEFAULT_PATCH = SCENARIO_DIR / "ae2_task5a_converted_with_redstone_patch_1182.json"
DEFAULT_SERVER_DIR = PROJECT_ROOT / "headless_server/1.18.2"
DEFAULT_BASE_WORLD = DEFAULT_SERVER_DIR / "world"
DEFAULT_TARGET_WORLD = DEFAULT_SERVER_DIR / "world_ae2_task5b"
DEFAULT_REPORT = SCENARIO_DIR / "ae2_task5b_headless_materialization_report.json"
DEFAULT_SERVER_PROPERTIES = SCENARIO_DIR / "server_ae2_task5b.properties"


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
            safe_key = key.replace("_", "").replace("-", "").replace(".", "").isalnum()
            key_text = key if safe_key else quote_snbt_string(key)
            items.append(f"{key_text}:{to_snbt(item)}")
        return "{" + ",".join(items) + "}"
    return quote_snbt_string(str(value))


def find_ae2_jar(server_dir: Path) -> Path | None:
    jars = sorted((server_dir / "mods").glob("appliedenergistics2-*.jar"))
    return jars[0] if jars else None


def load_ae2_blockstate_properties(server_dir: Path) -> dict[str, dict[str, set[str]]]:
    jar = find_ae2_jar(server_dir)
    if jar is None:
        return {}

    by_block: dict[str, dict[str, set[str]]] = {}
    with zipfile.ZipFile(jar) as archive:
        for path in archive.namelist():
            if not path.startswith("assets/ae2/blockstates/") or not path.endswith(".json"):
                continue
            block_name = path.removeprefix("assets/ae2/blockstates/").removesuffix(".json")
            block_id = f"ae2:{block_name}"
            try:
                blockstate = json.loads(archive.read(path).decode("utf-8"))
            except (UnicodeDecodeError, json.JSONDecodeError):
                continue
            allowed: dict[str, set[str]] = {}
            for variant_key in (blockstate.get("variants") or {}).keys():
                if not variant_key:
                    continue
                for assignment in variant_key.split(","):
                    if "=" not in assignment:
                        continue
                    key, value = assignment.split("=", 1)
                    allowed.setdefault(key, set()).add(value)
            by_block[block_id] = allowed
    return by_block


def command_safe_properties(
    block_id: str,
    properties: dict[str, Any] | None,
    blockstate_properties: dict[str, dict[str, set[str]]],
) -> tuple[dict[str, Any], list[str]]:
    if not properties:
        return {}, []
    allowed = blockstate_properties.get(block_id)
    if block_id.startswith("ae2:") and not allowed:
        return {}, [f"{block_id}: dropped all properties, blockstate has no variants"]

    safe: dict[str, Any] = {}
    dropped: list[str] = []
    for key, value in properties.items():
        value_text = str(value)
        if allowed is not None and (key not in allowed or value_text not in allowed[key]):
            dropped.append(f"{block_id}: dropped {key}={value_text}")
            continue
        safe[key] = value_text
    return safe, dropped


def block_state(block_id: str, properties: dict[str, Any] | None) -> str:
    if not properties:
        return block_id
    props = ",".join(f"{key}={value}" for key, value in sorted(properties.items()))
    return f"{block_id}[{props}]"


def setblock_command(block_edit: dict[str, Any], properties: dict[str, Any], te_nbt: dict[str, Any] | None = None) -> str:
    state = block_state(str(block_edit["block_id"]), properties)
    nbt = to_snbt(te_nbt) if te_nbt else ""
    return f"setblock {block_edit['x']} {block_edit['y']} {block_edit['z']} {state}{nbt} replace"


def pair_patch_edits(
    patch: dict[str, Any],
    blockstate_properties: dict[str, dict[str, set[str]]],
) -> tuple[list[str], dict[str, Any]]:
    block_edits: dict[tuple[int, int, int], dict[str, Any]] = {}
    te_edits: dict[tuple[int, int, int], dict[str, Any]] = {}
    for edit in patch.get("edits", []):
        pos = (int(edit["x"]), int(edit["y"]), int(edit["z"]))
        if edit.get("op") == "set_block":
            block_edits[pos] = edit
        elif edit.get("op") == "set_te":
            te_edits[pos] = edit

    commands: list[str] = []
    dropped_properties: list[str] = []
    for pos in sorted(block_edits):
        block_edit = block_edits[pos]
        te = te_edits.get(pos)
        safe_properties, dropped = command_safe_properties(
            str(block_edit["block_id"]),
            block_edit.get("properties") or {},
            blockstate_properties,
        )
        dropped_properties.extend(dropped)
        commands.append(setblock_command(block_edit, safe_properties, te.get("nbt") if te else None))

    te_without_block = sorted(pos for pos in te_edits if pos not in block_edits)
    stats = {
        "block_edits": len(block_edits),
        "tile_entity_edits": len(te_edits),
        "commands": len(commands),
        "te_without_block": [list(pos) for pos in te_without_block],
        "dropped_property_count": len(dropped_properties),
        "dropped_properties": dropped_properties[:100],
        "x_range": [min(pos[0] for pos in block_edits), max(pos[0] for pos in block_edits)] if block_edits else None,
        "y_range": [min(pos[1] for pos in block_edits), max(pos[1] for pos in block_edits)] if block_edits else None,
        "z_range": [min(pos[2] for pos in block_edits), max(pos[2] for pos in block_edits)] if block_edits else None,
    }
    return commands, stats


def write_datapack(target_world: Path, commands: list[str]) -> dict[str, Any]:
    datapack_root = target_world / "datapacks" / "ae2_task5b"
    function_dir = datapack_root / "data" / "ae2_task5b" / "functions"
    load_tag_dir = datapack_root / "data" / "minecraft" / "tags" / "functions"
    function_dir.mkdir(parents=True, exist_ok=True)
    load_tag_dir.mkdir(parents=True, exist_ok=True)

    (datapack_root / "pack.mcmeta").write_text(
        json.dumps(
            {
                "pack": {
                    "pack_format": 9,
                    "description": "AE2 Task 5B materialization datapack",
                }
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    (load_tag_dir / "load.json").write_text(
        json.dumps({"values": ["ae2_task5b:apply"]}, indent=2) + "\n",
        encoding="utf-8",
    )

    function_lines = [
        "say [AE2_TASK5B] applying converted AE2 5A patch",
        *commands,
        "say [AE2_TASK5B] apply complete",
    ]
    apply_path = function_dir / "apply.mcfunction"
    apply_path.write_text("\n".join(function_lines) + "\n", encoding="utf-8")
    return {
        "datapack_root": str(datapack_root),
        "apply_function": str(apply_path),
        "load_function": "ae2_task5b:apply",
        "function_lines": len(function_lines),
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


def validate_ae2_targets(patch: dict[str, Any], server_dir: Path) -> dict[str, Any]:
    targets = sorted(
        {
            edit["block_id"]
            for edit in patch.get("edits", [])
            if edit.get("op") == "set_block" and str(edit.get("block_id", "")).startswith("ae2:")
        }
    )
    jar = find_ae2_jar(server_dir)
    if jar is None:
        return {"status": "missing_ae2_jar", "target_count": len(targets), "missing": targets}

    with zipfile.ZipFile(jar) as archive:
        known = {
            path.removeprefix("assets/ae2/blockstates/").removesuffix(".json")
            for path in archive.namelist()
            if path.startswith("assets/ae2/blockstates/") and path.endswith(".json")
        }
    missing = [target for target in targets if target.split(":", 1)[1] not in known]
    return {
        "status": "ok" if not missing else "missing_targets",
        "jar": str(jar),
        "target_count": len(targets),
        "known_blockstate_count": len(known),
        "missing": missing,
    }


def materialize(args: argparse.Namespace) -> dict[str, Any]:
    patch = load_json(args.patch)
    blockstate_properties = load_ae2_blockstate_properties(args.server_dir)
    commands, stats = pair_patch_edits(patch, blockstate_properties)
    copy_world(args.base_world, args.target_world, args.overwrite)
    datapack = write_datapack(args.target_world, commands)
    write_server_properties_template(args.server_dir, args.target_world, args.server_properties_out)
    ae2_registry = validate_ae2_targets(patch, args.server_dir)

    report = {
        "name": "AE2 Task 5B headless materialization",
        "status": "world_copy_prepared_with_datapack",
        "patch": str(args.patch),
        "server_dir": str(args.server_dir),
        "base_world": str(args.base_world),
        "target_world": str(args.target_world),
        "server_properties_template": str(args.server_properties_out),
        "datapack": datapack,
        "stats": stats,
        "ae2_registry_preflight": ae2_registry,
        "next_manual_or_task6_steps": [
            f"Copy {args.server_properties_out} to {args.server_dir / 'server.properties'} or set level-name={args.target_world.name}.",
            "Start the 1.18.2 Forge headless server.",
            "Confirm logs contain [AE2_TASK5B] apply complete.",
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
    print(f"Dropped blockstate properties: {report['stats']['dropped_property_count']}")
    print(f"AE2 registry preflight: {report['ae2_registry_preflight']['status']}")
    print(f"Report: {args.report}")
    return 0 if not report["stats"]["te_without_block"] and report["ae2_registry_preflight"]["status"] == "ok" else 1


if __name__ == "__main__":
    raise SystemExit(main())
