#!/usr/bin/env python3
"""Materialize Extra Utilities Task 5B as a 1.18.2 headless-server datapack.

Generates a datapack that applies the converted 1.18.2 patch via /setblock
commands. Blocks whose target mods are missing on the headless server are
replaced with conversion_placeholders:block_entity_placeholder.
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
DEFAULT_PATCH = SCENARIO_DIR / "extrautils_task5a_realworld_converted_patch_1182.json"
DEFAULT_SERVER_DIR = PROJECT_ROOT / "headless_server/1.18.2"
DEFAULT_BASE_WORLD = DEFAULT_SERVER_DIR / "world"
DEFAULT_TARGET_WORLD = DEFAULT_SERVER_DIR / "world_extrautils_task5b"
DEFAULT_REPORT = SCENARIO_DIR / "extrautils_task5b_headless_materialization_report.json"
DEFAULT_SERVER_PROPERTIES = SCENARIO_DIR / "server_extrautils_task5b.properties"

# Mods not present on the headless server
# NOTE: extremesoundmuffler mod is client-side only in 1.18.2 — it does not
# register a physical block. The sound_muffler block entity does not exist.
MISSING_MOD_PREFIXES = {
    "extremesoundmuffler:",
}

# Placeholder blocks available on the server
PLACEHOLDER_BLOCK = "conversion_placeholders:block_entity_placeholder"


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


def is_block_available(block_id: str) -> bool:
    return not any(block_id.startswith(prefix) for prefix in MISSING_MOD_PREFIXES)


def resolve_block_for_server(block_id: str) -> str:
    if block_id == "conversion_placeholders:inventory_placeholder":
        # The server JAR only has block_entity_placeholder
        return PLACEHOLDER_BLOCK
    if not is_block_available(block_id):
        return PLACEHOLDER_BLOCK
    return block_id


def setblock_command(edit: dict[str, Any]) -> str:
    block_id = resolve_block_for_server(str(edit["block_id"]))
    properties = edit.get("properties") if is_block_available(str(edit["block_id"])) else None
    nbt = edit.get("nbt")
    state = block_state(block_id, properties)
    snbt = to_snbt(nbt) if nbt else ""
    return f"setblock {edit['x']} {edit['y']} {edit['z']} {state}{snbt} replace"


def pair_patch_edits(patch: dict[str, Any]) -> tuple[list[str], dict[str, Any]]:
    block_edits: dict[tuple[int, int, int], dict[str, Any]] = {}
    te_edits: dict[tuple[int, int, int], dict[str, Any]] = {}
    for edit in patch.get("edits", []):
        pos = (int(edit["x"]), int(edit["y"]), int(edit["z"]))
        if edit.get("op") == "set_block":
            block_edits[pos] = edit
        elif edit.get("op") == "set_te":
            te_edits[pos] = edit

    commands: list[str] = []
    fallback_count = 0
    for pos in sorted(block_edits):
        te = te_edits.get(pos)
        if te:
            # Merge TE NBT into the block edit so /setblock can apply both
            merged = dict(block_edits[pos])
            merged["nbt"] = te.get("nbt")
            commands.append(setblock_command(merged))
        else:
            commands.append(setblock_command(block_edits[pos]))
        if resolve_block_for_server(str(block_edits[pos]["block_id"])) != block_edits[pos]["block_id"]:
            fallback_count += 1

    te_without_block = sorted(pos for pos in te_edits if pos not in block_edits)
    stats = {
        "block_edits": len(block_edits),
        "tile_entity_edits": len(te_edits),
        "commands": len(commands),
        "fallback_to_placeholder": fallback_count,
        "te_without_block": [list(pos) for pos in te_without_block],
        "x_range": [min(pos[0] for pos in block_edits), max(pos[0] for pos in block_edits)] if block_edits else None,
        "y_range": [min(pos[1] for pos in block_edits), max(pos[1] for pos in block_edits)] if block_edits else None,
        "z_range": [min(pos[2] for pos in block_edits), max(pos[2] for pos in block_edits)] if block_edits else None,
    }
    return commands, stats


def write_datapack(target_world: Path, commands: list[str]) -> dict[str, Any]:
    datapack_root = target_world / "datapacks" / "extrautils_task5b"
    function_dir = datapack_root / "data" / "extrautils_task5b" / "functions"
    load_tag_dir = datapack_root / "data" / "minecraft" / "tags" / "functions"
    function_dir.mkdir(parents=True, exist_ok=True)
    load_tag_dir.mkdir(parents=True, exist_ok=True)

    (datapack_root / "pack.mcmeta").write_text(
        json.dumps(
            {
                "pack": {
                    "pack_format": 9,
                    "description": "Extra Utilities Task 5B materialization datapack",
                }
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    (load_tag_dir / "load.json").write_text(
        json.dumps({"values": ["extrautils_task5b:apply"]}, indent=2) + "\n",
        encoding="utf-8",
    )

    function_lines = [
        "say [EXU_TASK5B] applying converted Extra Utilities 5A patch",
        *commands,
        "say [EXU_TASK5B] apply complete",
    ]
    apply_path = function_dir / "apply.mcfunction"
    apply_path.write_text("\n".join(function_lines) + "\n", encoding="utf-8")
    return {
        "datapack_root": str(datapack_root),
        "apply_function": str(apply_path),
        "load_function": "extrautils_task5b:apply",
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
    world_name = target_world.name
    lines = []
    replaced = False
    for line in text.splitlines():
        if line.startswith("level-name="):
            lines.append(f"level-name={world_name}")
            replaced = True
        else:
            lines.append(line)
    if not replaced:
        lines.append(f"level-name={world_name}")
    output_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def validate_targets(patch: dict[str, Any], server_dir: Path) -> dict[str, Any]:
    targets = sorted(
        {
            edit["block_id"]
            for edit in patch.get("edits", [])
            if edit.get("op") == "set_block"
        }
    )
    # Check which target blocks are known in installed JARs
    mods_dir = server_dir / "mods"
    known_blocks: set[str] = set()
    for jar in mods_dir.glob("*.jar"):
        if jar.name == "assets":
            continue
        try:
            with zipfile.ZipFile(jar) as archive:
                for name in archive.namelist():
                    if name.startswith("assets/") and "/blockstates/" in name and name.endswith(".json"):
                        block_name = name.split("/blockstates/", 1)[1].removesuffix(".json")
                        mod_id = name.split("/")[1]
                        known_blocks.add(f"{mod_id}:{block_name}")
        except zipfile.BadZipFile:
            continue

    missing = [t for t in targets if t not in known_blocks and not t.startswith("minecraft:")]
    return {
        "status": "ok" if not missing else "missing_targets",
        "target_count": len(targets),
        "known_block_asset_count": len(known_blocks),
        "missing": missing,
    }


def materialize(args: argparse.Namespace) -> dict[str, Any]:
    patch = load_json(args.patch)
    commands, stats = pair_patch_edits(patch)
    copy_world(args.base_world, args.target_world, args.overwrite)
    datapack = write_datapack(args.target_world, commands)
    write_server_properties_template(args.server_dir, args.target_world, args.server_properties_out)
    target_registry = validate_targets(patch, args.server_dir)

    report = {
        "name": "Extra Utilities Task 5B headless materialization",
        "status": "world_copy_prepared_with_datapack",
        "patch": str(args.patch),
        "server_dir": str(args.server_dir),
        "base_world": str(args.base_world),
        "target_world": str(args.target_world),
        "server_properties_template": str(args.server_properties_out),
        "datapack": datapack,
        "stats": stats,
        "target_registry_preflight": target_registry,
        "next_manual_or_task6_steps": [
            f"Copy {args.server_properties_out} to {args.server_dir / 'server.properties'} or set level-name={args.target_world.name}.",
            "Start the 1.18.2 Forge headless server.",
            "Confirm logs contain [EXU_TASK5B] apply complete.",
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
    print(f"Fallback to placeholder: {report['stats']['fallback_to_placeholder']}")
    print(f"Target registry preflight: {report['target_registry_preflight']['status']}")
    print(f"Report: {args.report}")
    return 0 if not report["stats"]["te_without_block"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
