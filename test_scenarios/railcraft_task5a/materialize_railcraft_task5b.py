#!/usr/bin/env python3
"""Materialize Railcraft Task 5B as a 1.18.2 headless-server datapack.

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
DEFAULT_PATCH = SCENARIO_DIR / "railcraft_task5a_converted_patch_1182.json"
DEFAULT_SERVER_DIR = PROJECT_ROOT / "headless_server/1.18.2"
DEFAULT_BASE_WORLD = DEFAULT_SERVER_DIR / "world"
DEFAULT_TARGET_WORLD = DEFAULT_SERVER_DIR / "world_railcraft_task5b"
DEFAULT_REPORT = SCENARIO_DIR / "railcraft_task5b_headless_materialization_report.json"
DEFAULT_SERVER_PROPERTIES = SCENARIO_DIR / "server_railcraft_task5b.properties"


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


# Mods that are NOT installed on the headless server (require fallback)
UNAVAILABLE_MODS = {"immersiveengineering", "railways"}


def is_block_available(block_id: str) -> bool:
    mod = block_id.split(":")[0]
    return mod not in UNAVAILABLE_MODS


def fallback_block_id(block_id: str) -> str:
    return "conversion_placeholders:block_entity_placeholder"


def setblock_command(edit: dict[str, Any]) -> str:
    block_id = str(edit["block_id"])
    properties = edit.get("properties")
    nbt = edit.get("nbt")

    if not is_block_available(block_id):
        block_id = fallback_block_id(block_id)
        properties = None  # placeholders have no blockstate properties
        nbt = None  # drop NBT for placeholders to avoid invalid TE data
    elif block_id == fallback_block_id(block_id):
        # Also strip properties from any fallback/placeholder block
        properties = None
        nbt = None
    elif block_id.startswith("framedblocks:"):
        # FramedBlocks 5.11.5 does not use blockstate properties for slab/stair
        properties = None

    state = block_state(block_id, properties)
    snbt = to_snbt(nbt) if nbt else ""
    return f"setblock {edit['x']} {edit['y']} {edit['z']} {state}{snbt} replace"


def generate_datapack(patch: dict[str, Any], datapack_dir: Path) -> tuple[list[str], dict[str, Any]]:
    datapack_dir.mkdir(parents=True, exist_ok=True)

    pack_mcmeta = {
        "pack": {
            "pack_format": 9,
            "description": "Railcraft Task 5B - materialize converted blocks",
        }
    }
    (datapack_dir / "pack.mcmeta").write_text(json.dumps(pack_mcmeta, indent=2) + "\n", encoding="utf-8")

    functions_dir = datapack_dir / "data" / "railcraft_task5b" / "functions"
    functions_dir.mkdir(parents=True, exist_ok=True)

    load_tag_dir = datapack_dir / "data" / "minecraft" / "tags" / "functions"
    load_tag_dir.mkdir(parents=True, exist_ok=True)
    (load_tag_dir / "load.json").write_text(
        json.dumps({"values": ["railcraft_task5b:apply"]}, indent=2) + "\n", encoding="utf-8"
    )

    commands: list[str] = []
    block_count = 0
    nbt_count = 0
    fallback_count = 0
    for edit in patch.get("edits", []):
        if edit.get("op") != "set_block":
            continue
        commands.append(setblock_command(edit))
        block_count += 1
        if edit.get("nbt"):
            nbt_count += 1
        if not is_block_available(str(edit.get("block_id", ""))):
            fallback_count += 1

    commands.append('say [RAILCRAFT_TASK5B] apply complete')

    (functions_dir / "apply.mcfunction").write_text("\n".join(commands) + "\n", encoding="utf-8")

    return commands, {
        "commands": len(commands),
        "block_edits": block_count,
        "nbt_edits": nbt_count,
        "fallback_blocks": fallback_count,
    }


def materialize(
    patch_path: Path,
    server_dir: Path,
    base_world: Path,
    target_world: Path,
    report_path: Path,
    server_properties_path: Path,
) -> None:
    patch = load_json(patch_path)

    if target_world.exists():
        shutil.rmtree(target_world)
    shutil.copytree(base_world, target_world)

    datapack_dir = target_world / "datapacks" / "railcraft_task5b"
    commands, stats = generate_datapack(patch, datapack_dir)

    server_properties = """# Railcraft Task 5B server properties
level-name=world_railcraft_task5b
server-port=25571
rcon.port=25581
rcon.password=test123
enable-rcon=true
enable-command-block=true
online-mode=false
spawn-protection=0
motd=Railcraft Task 5B Materialization
"""
    server_properties_path.write_text(server_properties, encoding="utf-8")

    existing_props = server_dir / "server.properties"
    if existing_props.exists():
        backup = server_dir / "server.properties.before_railcraft_task5b"
        shutil.copy2(existing_props, backup)
    shutil.copy2(server_properties_path, existing_props)

    report = {
        "mod": "Railcraft",
        "task": "5B",
        "source_patch": str(patch_path),
        "target_world": str(target_world),
        "datapack": str(datapack_dir),
        "commands": stats["commands"],
        "block_edits": stats["block_edits"],
        "nbt_edits": stats["nbt_edits"],
        "fallback_blocks": stats["fallback_blocks"],
        "unavailable_mods": sorted(UNAVAILABLE_MODS),
    }
    write_json(report_path, report)

    print(f"Datapack generated: {datapack_dir}")
    print(f"Commands: {stats['commands']} (blocks={stats['block_edits']}, nbt={stats['nbt_edits']}, fallback={stats['fallback_blocks']})")
    print(f"Server properties: {existing_props}")
    print(f"Report: {report_path}")


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
