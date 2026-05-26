#!/usr/bin/env python3
"""Materialize Big Reactors Task 5B as a 1.18.2 headless-server datapack."""

from __future__ import annotations

import json
import shutil
import subprocess
import sys
import time
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[2]
SCENARIO_DIR = Path(__file__).resolve().parent
DEFAULT_PATCH = SCENARIO_DIR / "bigreactors_task5a_converted_patch_1182.json"
DEFAULT_SERVER_DIR = PROJECT_ROOT / "headless_server/1.18.2"
DEFAULT_BASE_WORLD = DEFAULT_SERVER_DIR / "world"
DEFAULT_TARGET_WORLD = DEFAULT_SERVER_DIR / "world_bigreactors_task5b"
DEFAULT_REPORT = SCENARIO_DIR / "bigreactors_task5b_headless_materialization_report.json"
DEFAULT_SERVER_PROPERTIES = SCENARIO_DIR / "server_bigreactors_task5b.properties"


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

    pack_mcmeta = {
        "pack": {
            "pack_format": 9,
            "description": "BigReactors Task 5B - materialize converted blocks",
        }
    }
    (datapack_dir / "pack.mcmeta").write_text(json.dumps(pack_mcmeta, indent=2) + "\n", encoding="utf-8")

    functions_dir = datapack_dir / "data" / "bigreactors_task5b" / "functions"
    functions_dir.mkdir(parents=True, exist_ok=True)

    load_tag_dir = datapack_dir / "data" / "minecraft" / "tags" / "functions"
    load_tag_dir.mkdir(parents=True, exist_ok=True)
    (load_tag_dir / "load.json").write_text(
        json.dumps({"values": ["bigreactors_task5b:apply"]}, indent=2) + "\n", encoding="utf-8"
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

    commands.append('say [BIGREACTORS_TASK5B] apply complete')

    (functions_dir / "apply.mcfunction").write_text("\n".join(commands) + "\n", encoding="utf-8")

    return commands, {
        "commands": len(commands),
        "block_edits": block_count,
        "nbt_edits": nbt_count,
    }


def materialize(
    patch_path: Path,
    server_dir: Path,
    base_world: Path,
    target_world: Path,
    report_path: Path,
    server_properties_path: Path,
) -> dict[str, Any]:
    patch = load_json(patch_path)

    # Clean target world
    if target_world.exists():
        shutil.rmtree(target_world)
    shutil.copytree(base_world, target_world)

    # Generate datapack
    datapack_dir = target_world / "datapacks" / "bigreactors_task5b"
    commands, stats = generate_datapack(patch, datapack_dir)

    # Write server.properties
    server_properties_path.write_text(
        f"level-name=world_bigreactors_task5b\n"
        f"allow-nether=false\n"
        f"gamemode=creative\n"
        f"difficulty=peaceful\n"
        f"spawn-protection=0\n"
        f"max-tick-time=-1\n"
        f"enable-command-block=true\n",
        encoding="utf-8",
    )

    # Copy server.properties
    shutil.copy(server_properties_path, server_dir / "server.properties")

    # Run server (Windows: use java directly with win_args.txt, not bash run.sh)
    print("Starting headless server for materialization...")
    log_out = server_dir / "server_bigreactors_task5b_out.log"
    log_err = server_dir / "server_bigreactors_task5b_err.log"

    out_handle = log_out.open("w", encoding="utf-8", errors="replace")
    err_handle = log_err.open("w", encoding="utf-8", errors="replace")
    proc = subprocess.Popen(
        [
            "java",
            "@user_jvm_args.txt",
            "@libraries/net/minecraftforge/forge/1.18.2-40.2.4/win_args.txt",
            "nogui",
        ],
        cwd=str(server_dir),
        stdout=out_handle,
        stderr=err_handle,
        creationflags=getattr(subprocess, "CREATE_NEW_PROCESS_GROUP", 0),
    )
    out_handle.close()
    err_handle.close()

    # Wait for "apply complete" in logs
    start = time.time()
    timeout = 180
    found = False
    while time.time() - start < timeout:
        time.sleep(2)
        if log_out.exists():
            text = log_out.read_text(encoding="utf-8", errors="ignore")
            if "[BIGREACTORS_TASK5B] apply complete" in text:
                found = True
                break
            if "Done" in text and "For help, type \"help\"" in text:
                # Server is up, check again after a moment
                time.sleep(3)
                text = log_out.read_text(encoding="utf-8", errors="ignore")
                if "[BIGREACTORS_TASK5B] apply complete" in text:
                    found = True
                    break

    proc.terminate()
    try:
        proc.wait(timeout=10)
    except subprocess.TimeoutExpired:
        proc.kill()
        proc.wait()

    report = {
        "mod": "BigReactors",
        "task": "5B",
        "server_dir": str(server_dir),
        "target_world": str(target_world),
        "datapack_commands": stats,
        "materialized": found,
        "timeout_seconds": timeout,
        "elapsed_seconds": time.time() - start,
        "log_out": str(log_out),
        "log_err": str(log_err),
    }
    write_json(report_path, report)

    print(f"Materialization: {'OK' if found else 'TIMEOUT/FAILED'}")
    print(f"Report -> {report_path}")
    return report


def main() -> None:
    materialize(
        DEFAULT_PATCH,
        DEFAULT_SERVER_DIR,
        DEFAULT_BASE_WORLD,
        DEFAULT_TARGET_WORLD,
        DEFAULT_REPORT,
        DEFAULT_SERVER_PROPERTIES,
    )


if __name__ == "__main__":
    main()
