#!/usr/bin/env python3
"""Materialize ForgeMultipart Task 5B as a 1.18.2 headless-server datapack."""

from __future__ import annotations

import json
import shutil
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parents[2]
SCENARIO_DIR = Path(__file__).resolve().parent
DEFAULT_EVENTS = PROJECT_ROOT / "output/forge_multipart/task5a_events_1182.json"
DEFAULT_SERVER_DIR = PROJECT_ROOT / "headless_server/1.18.2"
DEFAULT_BASE_WORLD = DEFAULT_SERVER_DIR / "world"
DEFAULT_TARGET_WORLD = DEFAULT_SERVER_DIR / "world_forge_multipart_task5b"
DEFAULT_REPORT = SCENARIO_DIR / "forge_multipart_task5b_headless_materialization_report.json"


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, data: dict[str, Any]) -> None:
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


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
        return json.dumps(value, ensure_ascii=False)
    if isinstance(value, list):
        return "[" + ",".join(to_snbt(item) for item in value) + "]"
    if isinstance(value, dict):
        items = []
        for key, item in value.items():
            safe = key.replace("_", "").replace("-", "").replace(".", "").isalnum()
            key_text = key if safe else json.dumps(key, ensure_ascii=False)
            items.append(f"{key_text}:{to_snbt(item)}")
        return "{" + ",".join(items) + "}"
    return json.dumps(str(value), ensure_ascii=False)


def setblock_command(event: dict[str, Any]) -> str:
    x, y, z = event["pos"]
    nbt = dict(event.get("nbt") or {})
    nbt.pop("x", None)
    nbt.pop("y", None)
    nbt.pop("z", None)
    snbt = to_snbt(nbt) if nbt else ""
    return f"setblock {x} {y} {z} {event['block']}{snbt} replace"


def generate_datapack(events: dict[str, Any], datapack_dir: Path) -> dict[str, Any]:
    datapack_dir.mkdir(parents=True, exist_ok=True)
    (datapack_dir / "pack.mcmeta").write_text(
        json.dumps(
            {"pack": {"pack_format": 9, "description": "ForgeMultipart Task 5B materialization"}},
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )

    function_dir = datapack_dir / "data" / "forge_multipart_task5b" / "functions"
    function_dir.mkdir(parents=True, exist_ok=True)
    tag_dir = datapack_dir / "data" / "minecraft" / "tags" / "functions"
    tag_dir.mkdir(parents=True, exist_ok=True)
    (tag_dir / "load.json").write_text(
        json.dumps({"values": ["forge_multipart_task5b:apply"]}, indent=2) + "\n",
        encoding="utf-8",
    )

    commands = []
    for event in events.get("events", []):
        if event.get("op") != "set_block_entity":
            continue
        commands.append(setblock_command(event))
    commands.append('say [FORGE_MULTIPART_TASK5B] apply complete')
    (function_dir / "apply.mcfunction").write_text("\n".join(commands) + "\n", encoding="utf-8")

    return {"commands": len(commands), "block_entity_edits": len(commands) - 1}


def materialize() -> None:
    events = load_json(DEFAULT_EVENTS)
    if DEFAULT_TARGET_WORLD.exists():
        shutil.rmtree(DEFAULT_TARGET_WORLD)
    shutil.copytree(DEFAULT_BASE_WORLD, DEFAULT_TARGET_WORLD)

    datapack_dir = DEFAULT_TARGET_WORLD / "datapacks" / "forge_multipart_task5b"
    stats = generate_datapack(events, datapack_dir)

    server_properties = """# ForgeMultipart Task 5B server properties
level-name=world_forge_multipart_task5b
server-port=25681
rcon.port=25691
rcon.password=test123
enable-rcon=true
enable-command-block=true
online-mode=false
spawn-protection=0
motd=ForgeMultipart Task 5B Materialization
"""
    (SCENARIO_DIR / "server_forge_multipart_task5b.properties").write_text(server_properties, encoding="utf-8")
    server_props = DEFAULT_SERVER_DIR / "server.properties"
    if server_props.exists():
        shutil.copy2(server_props, DEFAULT_SERVER_DIR / "server.properties.before_forge_multipart_task5b")
    server_props.write_text(server_properties, encoding="utf-8")

    report = {
        "mod": "ForgeMultipart",
        "target": "CBMultipart",
        "task": "5B",
        "source_events": str(DEFAULT_EVENTS),
        "target_world": str(DEFAULT_TARGET_WORLD),
        "datapack": str(datapack_dir),
        **stats,
    }
    write_json(DEFAULT_REPORT, report)
    print(f"Datapack: {datapack_dir}")
    print(f"Commands: {stats['commands']}")
    print(f"Report: {DEFAULT_REPORT}")


if __name__ == "__main__":
    materialize()
