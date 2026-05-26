#!/usr/bin/env python3
"""Materialize ComputerCraft Task 5B as a 1.18.2 headless-server datapack.

Generates a datapack that applies the converted 1.18.2 patch via /setblock
commands, then boots the headless Forge 1.18.2 server to materialize blocks.
"""
from __future__ import annotations

import json
import shutil
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[2]
SCENARIO_DIR = Path(__file__).resolve().parent
DEFAULT_PATCH = SCENARIO_DIR / "computercraft_task5a_converted_1182.json"
DEFAULT_SERVER_DIR = PROJECT_ROOT / "headless_server/1.18.2"
DEFAULT_BASE_WORLD = DEFAULT_SERVER_DIR / "world"
DEFAULT_TARGET_WORLD = DEFAULT_SERVER_DIR / "world_computercraft_task5b"
DEFAULT_REPORT = SCENARIO_DIR / "computercraft_task5b_headless_materialization_report.json"


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
            safe = key.replace("_", "").replace("-", "").replace(".", "").isalnum()
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
    block_id = str(edit["block_id"])
    properties = edit.get("properties")
    nbt = edit.get("nbt")
    state = block_state(block_id, properties)
    snbt = to_snbt(nbt) if nbt else ""
    return f"setblock {edit['x']} {edit['y']} {edit['z']} {state}{snbt} replace"


def generate_datapack(patch: dict[str, Any], datapack_dir: Path) -> tuple[list[str], dict[str, Any]]:
    datapack_dir.mkdir(parents=True, exist_ok=True)

    # pack.mcmeta
    pack_mcmeta = {
        "pack": {
            "pack_format": 9,
            "description": "ComputerCraft Task 5B - materialize converted blocks",
        }
    }
    (datapack_dir / "pack.mcmeta").write_text(json.dumps(pack_mcmeta, indent=2) + "\n", encoding="utf-8")

    functions_dir = datapack_dir / "data" / "computercraft_task5b" / "functions"
    functions_dir.mkdir(parents=True, exist_ok=True)

    load_tag_dir = datapack_dir / "data" / "minecraft" / "tags" / "functions"
    load_tag_dir.mkdir(parents=True, exist_ok=True)
    (load_tag_dir / "load.json").write_text(
        json.dumps({"values": ["computercraft_task5b:apply"]}, indent=2) + "\n", encoding="utf-8"
    )

    commands: list[str] = []
    block_count = 0
    nbt_count = 0
    for edit in patch.get("edits", []):
        if edit.get("op") != "set_block":
            continue
        commands.append(setblock_command(edit))
        block_count += 1
        if edit.get("nbt"):
            nbt_count += 1

    commands.append('say [CC_TASK5B] apply complete')

    (functions_dir / "apply.mcfunction").write_text("\n".join(commands) + "\n", encoding="utf-8")

    return commands, {
        "commands": len(commands),
        "setblock_commands": block_count,
        "nbt_commands": nbt_count,
        "datapack_dir": str(datapack_dir),
    }


def setup_world(base_world: Path, target_world: Path, datapack_dir: Path) -> None:
    if target_world.exists():
        shutil.rmtree(target_world)
    shutil.copytree(base_world, target_world)

    # Copy datapack
    target_datapacks = target_world / "datapacks"
    target_datapacks.mkdir(parents=True, exist_ok=True)
    datapack_target = target_datapacks / "computercraft_task5b"
    if datapack_target.exists():
        shutil.rmtree(datapack_target)
    shutil.copytree(datapack_dir, datapack_target)


def generate_server_properties(target_world: Path) -> Path:
    props = target_world.parent / "server_computercraft_task5b.properties"
    props.write_text(
        f"level-name={target_world.name}\n"
        "gamemode=creative\n"
        "difficulty=peaceful\n"
        "allow-flight=true\n"
        "max-players=1\n"
        "online-mode=false\n"
        "spawn-protection=0\n"
        "enable-command-block=true\n"
        "server-port=25571\n",
        encoding="utf-8",
    )
    return props


def materialize(patch_path: Path, server_dir: Path, base_world: Path, target_world: Path, report_path: Path) -> None:
    patch = load_json(patch_path)

    datapack_dir = target_world.parent / "datapacks_computercraft_task5b"
    commands, stats = generate_datapack(patch, datapack_dir)

    setup_world(base_world, target_world, datapack_dir)
    props_path = generate_server_properties(target_world)

    report = {
        "mod": "computercraft",
        "task": "5B",
        "server_dir": str(server_dir),
        "world": str(target_world),
        "datapack": str(datapack_dir),
        "server_properties": str(props_path),
        "commands": commands,
        "stats": stats,
    }
    write_json(report_path, report)

    print(f"Datapack generated: {datapack_dir}")
    print(f"World: {target_world}")
    print(f"Server properties: {props_path}")
    print(f"Stats: {stats}")
    print(f"\nTo start server:")
    print(f"  cd {server_dir}")
    print(f"  copy server_computercraft_task5b.properties server.properties")
    print(f"  run.bat")


def main() -> None:
    materialize(DEFAULT_PATCH, DEFAULT_SERVER_DIR, DEFAULT_BASE_WORLD, DEFAULT_TARGET_WORLD, DEFAULT_REPORT)


if __name__ == "__main__":
    main()
