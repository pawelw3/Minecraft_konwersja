#!/usr/bin/env python3
"""Materialize Chisel Task 5B as a 1.18.2 headless-server datapack."""

from __future__ import annotations

import argparse
import json
import shutil
from collections import Counter
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parents[2]
SCENARIO_DIR = Path(__file__).resolve().parent
DEFAULT_PATCH = SCENARIO_DIR / "chisel_task5a_converted_patch_1182.json"
DEFAULT_SERVER_DIR = PROJECT_ROOT / "headless_server" / "1.18.2"
DEFAULT_BASE_WORLD = DEFAULT_SERVER_DIR / "world"
DEFAULT_TARGET_WORLD = DEFAULT_SERVER_DIR / "world_chisel_task5b"
DEFAULT_REPORT = SCENARIO_DIR / "chisel_task5b_headless_materialization_report.json"
DEFAULT_SERVER_PROPERTIES = SCENARIO_DIR / "server_chisel_task5b.properties"
REPORT_MD = SCENARIO_DIR / "CHISEL_TASK5B_REPORT.md"
HANDOFF = SCENARIO_DIR / "HANDOFF_CHISEL_TASK5B.md"


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


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


def installed_mod_ids(server_dir: Path) -> set[str]:
    mods_dir = server_dir / "mods"
    ids = {"minecraft"}
    if not mods_dir.exists():
        return ids
    for path in mods_dir.iterdir():
        name = path.name.lower()
        if path.is_dir():
            ids.add(name)
            continue
        if not name.endswith(".jar"):
            continue
        if "conversion-placeholders" in name:
            ids.add("conversion_placeholders")
        elif "rechiseled" in name:
            ids.add("rechiseled")
        elif "chipped" in name:
            ids.add("chipped")
        elif name.startswith("framedblocks"):
            ids.add("framedblocks")
    return ids


def vanilla_fallback_for(block_id: str) -> str:
    namespace, _, path = block_id.partition(":")
    if namespace == "minecraft":
        return block_id
    tokens = path.lower()
    if "glass_pane" in tokens:
        return "minecraft:glass_pane"
    if "glass" in tokens:
        return "minecraft:glass"
    if "wool" in tokens or "carpet" in tokens:
        return "minecraft:white_wool"
    if "cobblestone" in tokens:
        return "minecraft:cobblestone"
    if "sandstone" in tokens and "red" in tokens:
        return "minecraft:cut_red_sandstone"
    if "sandstone" in tokens:
        return "minecraft:cut_sandstone"
    if "granite" in tokens:
        return "minecraft:polished_granite"
    if "diorite" in tokens:
        return "minecraft:polished_diorite"
    if "andesite" in tokens:
        return "minecraft:polished_andesite"
    if "quartz" in tokens or "marble" in tokens or "limestone" in tokens:
        return "minecraft:quartz_block"
    if "glowstone" in tokens:
        return "minecraft:glowstone"
    if "netherrack" in tokens:
        return "minecraft:netherrack"
    if "obsidian" in tokens:
        return "minecraft:obsidian"
    if "gold" in tokens:
        return "minecraft:gold_block"
    if "iron" in tokens or "factory" in tokens or "technical" in tokens:
        return "minecraft:iron_block"
    if "diamond" in tokens:
        return "minecraft:diamond_block"
    if "emerald" in tokens:
        return "minecraft:emerald_block"
    if "lapis" in tokens:
        return "minecraft:lapis_block"
    if "redstone" in tokens:
        return "minecraft:redstone_block"
    if "dirt" in tokens:
        return "minecraft:dirt"
    if "spruce_planks" in tokens:
        return "minecraft:spruce_planks"
    if "birch_planks" in tokens:
        return "minecraft:birch_planks"
    if "jungle_planks" in tokens:
        return "minecraft:jungle_planks"
    if "dark_oak_planks" in tokens:
        return "minecraft:dark_oak_planks"
    if "planks" in tokens:
        return "minecraft:oak_planks"
    if "brick" in tokens:
        return "minecraft:stone_bricks"
    return "minecraft:stone"


def resolve_block(block_id: str, installed: set[str]) -> tuple[str, bool]:
    namespace = block_id.split(":", 1)[0]
    if namespace in installed:
        return block_id, False
    return vanilla_fallback_for(block_id), True


def block_state(block_id: str, properties: dict[str, Any] | None) -> str:
    if not properties:
        return block_id
    props = ",".join(f"{key}={value}" for key, value in sorted(properties.items()))
    return f"{block_id}[{props}]"


def setblock_command(edit: dict[str, Any], installed: set[str]) -> tuple[str, dict[str, Any]]:
    pos = edit["pos"]
    source_block = str(edit["block"])
    target_block, used_fallback = resolve_block(source_block, installed)
    properties = edit.get("blockstate") if not used_fallback else None
    state = block_state(target_block, properties)
    nbt = edit.get("nbt") if not used_fallback or target_block.startswith("conversion_placeholders:") else None
    if target_block == "conversion_placeholders:inventory_placeholder":
        # The currently installed placeholder JAR on the headless server only
        # contains block_entity_placeholder. Keep the rescued inventory inside
        # NBT, but materialize it under the available BE type.
        target_block = "conversion_placeholders:block_entity_placeholder"
        state = block_state(target_block, None)
        used_fallback = True
        if isinstance(nbt, dict):
            nbt = dict(nbt)
            nbt["id"] = "conversion_placeholders:block_entity_placeholder"
    snbt = to_snbt(nbt) if nbt else ""
    command = f"setblock {pos[0]} {pos[1]} {pos[2]} {state}{snbt} replace"
    return command, {
        "source_block": source_block,
        "target_block": target_block,
        "fallback": used_fallback,
        "op": edit.get("op"),
    }


def write_datapack(target_world: Path, commands: list[str]) -> dict[str, Any]:
    datapack_root = target_world / "datapacks" / "chisel_task5b"
    function_dir = datapack_root / "data" / "chisel_task5b" / "functions"
    load_tag_dir = datapack_root / "data" / "minecraft" / "tags" / "functions"
    function_dir.mkdir(parents=True, exist_ok=True)
    load_tag_dir.mkdir(parents=True, exist_ok=True)

    (datapack_root / "pack.mcmeta").write_text(
        json.dumps(
            {
                "pack": {
                    "pack_format": 9,
                    "description": "Chisel Task 5B materialization datapack",
                }
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    (load_tag_dir / "load.json").write_text(
        json.dumps({"values": ["chisel_task5b:apply"]}, indent=2) + "\n",
        encoding="utf-8",
    )

    lines = [
        "say [CHISEL_TASK5B] applying converted Chisel 5A patch",
        *commands,
        "say [CHISEL_TASK5B] apply complete",
    ]
    apply_path = function_dir / "apply.mcfunction"
    apply_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return {
        "datapack_root": str(datapack_root),
        "apply_function": str(apply_path),
        "load_function": "chisel_task5b:apply",
        "function_lines": len(lines),
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
    if source.exists():
        text = source.read_text(encoding="utf-8")
    else:
        text = "enable-command-block=true\nonline-mode=false\nspawn-protection=0\n"
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


def write_markdown_report(report: dict[str, Any]) -> None:
    stats = report["stats"]
    lines = [
        "# Chisel Task 5B - raport",
        "",
        "## Podsumowanie",
        "",
        "Przygotowano swiat headless 1.18.2 z datapackiem materializujacym wynik Zadania 5A.",
        "",
        f"- Status: `{report['status']}`",
        f"- Target world: `{report['target_world']}`",
        f"- Komendy setblock: {stats['commands']}",
        f"- Edycje blokow: {stats['block_edits']}",
        f"- Edycje BlockEntity: {stats['block_entity_edits']}",
        f"- Fallbacki z powodu brakujacych modow: {stats['fallback_count']}",
        "",
        "## Uwagi",
        "",
        "Headless 1.18.2 nie ma obecnie JARow Rechiseled/Chipped, wiec ich targety zostaly w datapacku zastapione bezpiecznymi blokami vanilla. Placeholdery TE zostaja zachowane przez `conversion_placeholders`.",
        "",
        "## Pliki",
        "",
        "- `materialize_chisel_task5b.py`",
        "- `chisel_task5b_headless_materialization_report.json`",
        "- `server_chisel_task5b.properties`",
        "- `headless_server/1.18.2/world_chisel_task5b/datapacks/chisel_task5b/`",
        "",
        "## Nastepne kroki",
        "",
        "1. Uruchomic headless 1.18.2 z `server_chisel_task5b.properties` jako `server.properties`.",
        "2. Potwierdzic w logu marker `[CHISEL_TASK5B] apply complete`.",
        "3. W Zadaniu 6 wykonac tick/restart verification i sprawdzic placeholdery TE.",
        "",
    ]
    write_text(REPORT_MD, "\n".join(lines))


def write_handoff(report: dict[str, Any]) -> None:
    stats = report["stats"]
    text = f"""# Handoff: Chisel - Zadanie 5B

## Podsumowanie sesji

Wykonano Zadanie 5B dla Chisel: przygotowano kopie swiata headless 1.18.2 i datapack, ktory materializuje `chisel_task5a_converted_patch_1182.json` komendami `/setblock`.

## Ukonczono

- [x] Dodano `materialize_chisel_task5b.py`.
- [x] Skopiowano base world do `headless_server/1.18.2/world_chisel_task5b`.
- [x] Wygenerowano datapack `chisel_task5b`.
- [x] Wygenerowano template `server_chisel_task5b.properties`.
- [x] Wygenerowano raport JSON i Markdown.

## Wyniki

- Komendy setblock: {stats['commands']}.
- Edycje blokow: {stats['block_edits']}.
- Edycje BlockEntity: {stats['block_entity_edits']}.
- Fallbacki Rechiseled/Chipped -> vanilla: {stats['fallback_count']}.

## Nowe pliki

- `test_scenarios/chisel_task5a/materialize_chisel_task5b.py`
- `test_scenarios/chisel_task5a/chisel_task5b_headless_materialization_report.json`
- `test_scenarios/chisel_task5a/CHISEL_TASK5B_REPORT.md`
- `test_scenarios/chisel_task5a/HANDOFF_CHISEL_TASK5B.md`
- `test_scenarios/chisel_task5a/server_chisel_task5b.properties`
- `headless_server/1.18.2/world_chisel_task5b/`

## Nastepne kroki

1. [ ] Zadanie 6: odpalic headless 1.18.2, poczekac na `[CHISEL_TASK5B] apply complete`, wykonac tick/restart verification.
2. [ ] Po dolozeniu JARow Rechiseled/Chipped mozna powtorzyc 5B bez fallbackow wizualnych.
"""
    write_text(HANDOFF, text)


def materialize(args: argparse.Namespace) -> dict[str, Any]:
    patch = load_json(args.patch)
    installed = installed_mod_ids(args.server_dir)
    commands: list[str] = []
    resolutions: list[dict[str, Any]] = []
    fallback_counts: Counter[str] = Counter()

    for edit in patch.get("edits", []):
        if edit.get("op") not in {"set_block", "set_block_entity"}:
            continue
        command, resolution = setblock_command(edit, installed)
        commands.append(command)
        resolutions.append(resolution)
        if resolution["fallback"]:
            fallback_counts[resolution["source_block"]] += 1

    copy_world(args.base_world, args.target_world, args.overwrite)
    datapack = write_datapack(args.target_world, commands)
    write_server_properties_template(args.server_dir, args.target_world, args.server_properties_out)

    block_edits = [edit for edit in patch.get("edits", []) if edit.get("op") in {"set_block", "set_block_entity"}]
    be_edits = [edit for edit in patch.get("edits", []) if edit.get("op") == "set_block_entity"]
    report = {
        "name": "Chisel Task 5B headless materialization",
        "status": "world_copy_prepared_with_datapack",
        "patch": str(args.patch),
        "server_dir": str(args.server_dir),
        "base_world": str(args.base_world),
        "target_world": str(args.target_world),
        "server_properties_template": str(args.server_properties_out),
        "installed_mod_ids": sorted(installed),
        "datapack": datapack,
        "stats": {
            "commands": len(commands),
            "block_edits": len(block_edits),
            "block_entity_edits": len(be_edits),
            "fallback_count": sum(fallback_counts.values()),
            "fallback_unique_blocks": len(fallback_counts),
        },
        "fallback_counts": dict(fallback_counts.most_common()),
        "sample_resolutions": resolutions[:80],
        "next_steps": [
            f"Copy {args.server_properties_out} to {args.server_dir / 'server.properties'} or start with equivalent level-name.",
            "Start the 1.18.2 Forge headless server.",
            "Confirm logs contain [CHISEL_TASK5B] apply complete.",
            "Continue with Task 6: tick/restart verification.",
        ],
    }
    write_json(args.report, report)
    write_markdown_report(report)
    write_handoff(report)
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
    print(f"Fallbacks: {report['stats']['fallback_count']}")
    print(f"Report: {args.report}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
