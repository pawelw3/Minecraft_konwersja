#!/usr/bin/env python3
"""Materialize Logistics Pipes Task 5B as a 1.18.2 headless-server datapack.

The Task 5A fixture already emits 1.18.2 Event JSON. This script prepares a
dedicated headless world copy and a datapack whose load function applies those
events with /setblock. It also installs the local Pretty Pipes 1.18.2 jar when
it is present in mod_src/118/mod_jars.
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
DEFAULT_PATCH = SCENARIO_DIR / "logistics_pipes_task5a_converted_patch_1182.json"
DEFAULT_SERVER_DIR = PROJECT_ROOT / "headless_server" / "1.18.2"
DEFAULT_BASE_WORLD = DEFAULT_SERVER_DIR / "world"
DEFAULT_TARGET_WORLD = DEFAULT_SERVER_DIR / "world_logistics_pipes_task5b"
DEFAULT_REPORT = SCENARIO_DIR / "logistics_pipes_task5b_headless_materialization_report.json"
DEFAULT_SERVER_PROPERTIES = SCENARIO_DIR / "server_logistics_pipes_task5b.properties"
LOCAL_PRETTY_PIPES_JAR = PROJECT_ROOT / "mod_src" / "118" / "mod_jars" / "PrettyPipes-1.12.8.jar"


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
    nbt = edit.get("nbt")
    snbt = to_snbt(nbt) if nbt else ""
    return f"setblock {x} {y} {z} {state}{snbt} replace"


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


def write_datapack(target_world: Path, commands: list[str]) -> dict[str, Any]:
    datapack_root = target_world / "datapacks" / "logistics_pipes_task5b"
    function_dir = datapack_root / "data" / "logistics_pipes_task5b" / "functions"
    load_tag_dir = datapack_root / "data" / "minecraft" / "tags" / "functions"
    function_dir.mkdir(parents=True, exist_ok=True)
    load_tag_dir.mkdir(parents=True, exist_ok=True)

    (datapack_root / "pack.mcmeta").write_text(
        json.dumps(
            {
                "pack": {
                    "pack_format": 9,
                    "description": "Logistics Pipes Task 5B materialization datapack",
                }
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    (load_tag_dir / "load.json").write_text(
        json.dumps({"values": ["logistics_pipes_task5b:apply"]}, indent=2) + "\n",
        encoding="utf-8",
    )

    function_lines = [
        "say [LOGISTICS_PIPES_TASK5B] applying converted Logistics Pipes 5A fixture",
        *commands,
        "say [LOGISTICS_PIPES_TASK5B] apply complete",
    ]
    apply_path = function_dir / "apply.mcfunction"
    apply_path.write_text("\n".join(function_lines) + "\n", encoding="utf-8")
    return {
        "datapack_root": str(datapack_root),
        "apply_function": str(apply_path),
        "load_function": "logistics_pipes_task5b:apply",
        "function_lines": len(function_lines),
    }


def install_local_pretty_pipes(server_dir: Path, install: bool) -> dict[str, Any]:
    mods_dir = server_dir / "mods"
    existing = sorted(mods_dir.glob("*PrettyPipes*.jar")) + sorted(mods_dir.glob("*prettypipes*.jar"))
    if existing:
        return {"status": "already_present", "jars": [str(path) for path in existing]}
    if not LOCAL_PRETTY_PIPES_JAR.exists():
        return {"status": "missing_local_jar", "source": str(LOCAL_PRETTY_PIPES_JAR), "jars": []}
    if not install:
        return {"status": "available_not_installed", "source": str(LOCAL_PRETTY_PIPES_JAR), "jars": []}

    mods_dir.mkdir(parents=True, exist_ok=True)
    target = mods_dir / LOCAL_PRETTY_PIPES_JAR.name
    shutil.copy2(LOCAL_PRETTY_PIPES_JAR, target)
    return {"status": "installed", "source": str(LOCAL_PRETTY_PIPES_JAR), "jars": [str(target)]}


def jar_contains_blockstate(jar: Path, namespace: str, block_name: str) -> bool:
    path = f"assets/{namespace}/blockstates/{block_name}.json"
    try:
        with zipfile.ZipFile(jar) as archive:
            return path in archive.namelist()
    except zipfile.BadZipFile:
        return False


def validate_mod_targets(server_dir: Path, target_blocks: set[str]) -> dict[str, Any]:
    mods_dir = server_dir / "mods"
    jars = sorted(mods_dir.glob("*.jar"))
    missing: list[str] = []
    present: dict[str, str] = {}
    for block_id in sorted(target_blocks):
        if ":" not in block_id:
            missing.append(block_id)
            continue
        namespace, block_name = block_id.split(":", 1)
        found = next((jar for jar in jars if jar_contains_blockstate(jar, namespace, block_name)), None)
        if found is None:
            missing.append(block_id)
        else:
            present[block_id] = str(found)
    return {
        "status": "ok" if not missing else "missing_blockstates",
        "present": present,
        "missing": missing,
    }


def write_server_properties_template(server_dir: Path, target_world: Path, output_path: Path) -> None:
    source = server_dir / "server.properties"
    if source.exists():
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
        return

    output_path.write_text(
        f"level-name={target_world.name}\n"
        "allow-nether=false\n"
        "gamemode=creative\n"
        "difficulty=peaceful\n"
        "spawn-protection=0\n"
        "max-tick-time=-1\n"
        "enable-command-block=true\n",
        encoding="utf-8",
    )


def materialize(args: argparse.Namespace) -> dict[str, Any]:
    patch = load_json(args.patch)
    edits = [edit for edit in patch.get("edits", []) if edit.get("op") in ("set_block", "set_block_entity")]
    commands = [setblock_command(edit) for edit in edits]

    pretty_pipes = install_local_pretty_pipes(args.server_dir, install=not args.no_install_pretty_pipes)
    copy_world(args.base_world, args.target_world, args.overwrite)
    datapack = write_datapack(args.target_world, commands)
    write_server_properties_template(args.server_dir, args.target_world, args.server_properties_out)

    target_blocks = {str(edit.get("block", "")) for edit in edits if edit.get("block")}
    mod_validation = validate_mod_targets(args.server_dir, target_blocks)
    te_edits = [edit for edit in edits if edit.get("op") == "set_block_entity"]

    report = {
        "mod": "Logistics Pipes",
        "task": "5B",
        "status": "world_copy_prepared_with_datapack",
        "patch": str(args.patch),
        "server_dir": str(args.server_dir),
        "base_world": str(args.base_world),
        "target_world": str(args.target_world),
        "server_properties_template": str(args.server_properties_out),
        "pretty_pipes_dependency": pretty_pipes,
        "target_validation": mod_validation,
        "datapack": datapack,
        "stats": {
            "commands": len(commands),
            "block_edits": len(edits),
            "tile_entity_edits": len(te_edits),
            "target_blocks": sorted(target_blocks),
        },
        "next_steps": [
            f"Copy {args.server_properties_out} to {args.server_dir / 'server.properties'} or start the server with matching level-name.",
            "Start the 1.18.2 Forge headless server.",
            "Confirm logs contain [LOGISTICS_PIPES_TASK5B] apply complete.",
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
    parser.add_argument("--no-install-pretty-pipes", action="store_true")
    args = parser.parse_args()

    report = materialize(args)
    print(f"Target world: {report['target_world']}")
    print(f"Datapack: {report['datapack']['datapack_root']}")
    print(f"Commands: {report['stats']['commands']}")
    print(f"Tile entity edits: {report['stats']['tile_entity_edits']}")
    print(f"Pretty Pipes: {report['pretty_pipes_dependency']['status']}")
    print(f"Target validation: {report['target_validation']['status']}")
    print(f"Report: {args.report}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
