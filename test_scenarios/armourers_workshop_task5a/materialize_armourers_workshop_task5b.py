#!/usr/bin/env python3
"""Materialize Armourer's Workshop Task 5B as a 1.18.2 headless datapack.

The converted AW fixture contains normal block/block-entity events plus a
sidecar for the global skin library. This script prepares a dedicated Forge
1.18.2 headless world, writes a load datapack with `/setblock` commands, and
copies the fixture `.armour` files into the target world `skin-library`.
"""

from __future__ import annotations

import argparse
import json
import shutil
import zipfile
from collections import Counter
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parents[2]
SCENARIO_DIR = Path(__file__).resolve().parent

DEFAULT_PATCH = SCENARIO_DIR / "armourers_workshop_task5a_converted_patch_1182.json"
DEFAULT_SERVER_DIR = PROJECT_ROOT / "headless_server" / "1.18.2"
DEFAULT_BASE_WORLD = DEFAULT_SERVER_DIR / "world"
DEFAULT_TARGET_WORLD = DEFAULT_SERVER_DIR / "world_armourers_workshop_task5b"
DEFAULT_REPORT = SCENARIO_DIR / "armourers_workshop_task5b_headless_materialization_report.json"
DEFAULT_SERVER_PROPERTIES = SCENARIO_DIR / "server_armourers_workshop_task5b.properties"
REPORT_MD = SCENARIO_DIR / "ARMOURERS_WORKSHOP_TASK5B_REPORT.md"
HANDOFF = SCENARIO_DIR / "HANDOFF_ARMOURERS_WORKSHOP_TASK5B.md"

DATAPACK_NAME = "armourers_workshop_task5b"
DATAPACK_SAY_PREFIX = "[AW_TASK5B]"
PLACEHOLDER_BE = "conversion_placeholders:block_entity_placeholder"
PLACEHOLDER_INV = "conversion_placeholders:inventory_placeholder"

VANILLA_FALLBACKS = {
    "armourers_workshop:skin-cube-glass": "minecraft:glass",
    "armourers_workshop:skin-cube-glowing": "minecraft:glowstone",
    "armourers_workshop:skin-cube-glass-glowing": "minecraft:glowstone",
    "armourers_workshop:outfit-maker": "minecraft:stone",
}


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def rel(path: Path) -> str:
    try:
        return str(path.resolve().relative_to(PROJECT_ROOT.resolve())).replace("\\", "/")
    except ValueError:
        return str(path)


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
    ids = {"minecraft"}
    mods_dir = server_dir / "mods"
    if not mods_dir.exists():
        return ids
    for path in mods_dir.iterdir():
        name = path.name.lower()
        if path.is_dir():
            ids.add(name)
            continue
        if not name.endswith(".jar"):
            continue
        if "conversion-placeholders" in name or "conversion_placeholders" in name:
            ids.add("conversion_placeholders")
        if "armourers" in name and "workshop" in name:
            ids.add("armourers_workshop")
    return ids


def find_armourers_workshop_jar(server_dir: Path) -> Path | None:
    mods_dir = server_dir / "mods"
    if not mods_dir.exists():
        return None
    candidates = [
        path
        for path in mods_dir.glob("*.jar")
        if "armourers" in path.name.lower() and "workshop" in path.name.lower()
    ]
    return sorted(candidates)[0] if candidates else None


def load_aw_blockstate_properties(server_dir: Path) -> dict[str, dict[str, set[str]]]:
    jar = find_armourers_workshop_jar(server_dir)
    if jar is None:
        return {}

    by_block: dict[str, dict[str, set[str]]] = {}
    with zipfile.ZipFile(jar) as archive:
        for path in archive.namelist():
            if not path.startswith("assets/armourers_workshop/blockstates/") or not path.endswith(".json"):
                continue
            block_name = path.removeprefix("assets/armourers_workshop/blockstates/").removesuffix(".json")
            block_id = f"armourers_workshop:{block_name}"
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
) -> tuple[dict[str, str], list[str]]:
    if not properties:
        return {}, []
    allowed = blockstate_properties.get(block_id)
    if block_id.startswith("armourers_workshop:") and allowed is None:
        return {}, [f"{block_id}: dropped all properties, no AW blockstate preflight data"]

    safe: dict[str, str] = {}
    dropped: list[str] = []
    for key, value in properties.items():
        value_text = str(value)
        if allowed is not None and (key not in allowed or value_text not in allowed[key]):
            dropped.append(f"{block_id}: dropped {key}={value_text}")
            continue
        safe[key] = value_text
    return safe, dropped


def placeholder_nbt(
    source_block: str,
    source_nbt: dict[str, Any] | None,
    pos: list[int],
    reason: str,
) -> dict[str, Any]:
    return {
        "id": PLACEHOLDER_BE,
        "source_mod": "armourers_workshop",
        "source_block_id": source_block,
        "source_te_id": str((source_nbt or {}).get("id", "")),
        "source_metadata": 0,
        "source_pos": pos,
        "conversion_reason": reason,
        "conversion_stage": "armourers_workshop_task5b",
        "original_nbt": source_nbt or {},
        "extra": {
            "original_target_block_1182": source_block,
            "note": "Armourer's Workshop JAR missing on headless server during Task 5B.",
        },
    }


def resolve_event(
    event: dict[str, Any],
    installed: set[str],
) -> tuple[str, dict[str, Any] | None, bool, str]:
    block_id = str(event["block"])
    nbt = event.get("nbt")
    pos = [int(v) for v in event["pos"]]
    namespace = block_id.split(":", 1)[0]
    if namespace in installed:
        return block_id, nbt, False, "native"

    if block_id in {PLACEHOLDER_BE, PLACEHOLDER_INV}:
        if "conversion_placeholders" in installed:
            return block_id, nbt, False, "native_placeholder"
        return "minecraft:stone", None, True, "missing_placeholder_mod"

    if namespace == "armourers_workshop":
        if nbt and "conversion_placeholders" in installed:
            return PLACEHOLDER_BE, placeholder_nbt(block_id, nbt, pos, "missing_armourers_workshop_jar"), True, "aw_be_placeholder"
        return VANILLA_FALLBACKS.get(block_id, "minecraft:stone"), None, True, "aw_vanilla_fallback"

    return "minecraft:stone", None, True, "unknown_namespace_fallback"


def block_state(block_id: str, properties: dict[str, Any] | None) -> str:
    if not properties:
        return block_id
    props = ",".join(f"{key}={value}" for key, value in sorted(properties.items()))
    return f"{block_id}[{props}]"


def setblock_command(event: dict[str, Any], blockstate_properties: dict[str, dict[str, set[str]]], installed: set[str]) -> tuple[str, dict[str, Any]]:
    pos = [int(v) for v in event["pos"]]
    source_block = str(event["block"])
    target_block, target_nbt, fallback, reason = resolve_event(event, installed)
    properties = event.get("blockstate") if not fallback else None
    safe_properties, dropped = command_safe_properties(target_block, properties, blockstate_properties)
    state = block_state(target_block, safe_properties)
    snbt = to_snbt(target_nbt) if target_nbt else ""
    command = f"setblock {pos[0]} {pos[1]} {pos[2]} {state}{snbt} replace"
    return command, {
        "pos": pos,
        "op": event.get("op"),
        "source_block": source_block,
        "target_block": target_block,
        "fallback": fallback,
        "reason": reason,
        "has_nbt": target_nbt is not None,
        "dropped_properties": dropped,
    }


def build_commands(patch: dict[str, Any], server_dir: Path) -> tuple[list[str], list[dict[str, Any]], dict[str, Any]]:
    installed = installed_mod_ids(server_dir)
    blockstate_properties = load_aw_blockstate_properties(server_dir)
    commands: list[str] = []
    resolutions: list[dict[str, Any]] = []
    dropped: list[str] = []

    for event in patch.get("events", []):
        if event.get("op") not in {"set_block", "set_block_entity"}:
            continue
        command, resolution = setblock_command(event, blockstate_properties, installed)
        commands.append(command)
        resolutions.append(resolution)
        dropped.extend(resolution["dropped_properties"])

    block_events = [event for event in patch.get("events", []) if event.get("op") in {"set_block", "set_block_entity"}]
    stats = {
        "commands": len(commands),
        "block_events": len(block_events),
        "block_entity_events": sum(1 for event in block_events if event.get("op") == "set_block_entity"),
        "fallback_count": sum(1 for resolution in resolutions if resolution["fallback"]),
        "fallback_reasons": dict(Counter(resolution["reason"] for resolution in resolutions if resolution["fallback"])),
        "dropped_property_count": len(dropped),
        "dropped_properties": dropped[:100],
    }
    return commands, resolutions, stats


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
    datapack_root = target_world / "datapacks" / DATAPACK_NAME
    function_dir = datapack_root / "data" / DATAPACK_NAME / "functions"
    load_tag_dir = datapack_root / "data" / "minecraft" / "tags" / "functions"
    function_dir.mkdir(parents=True, exist_ok=True)
    load_tag_dir.mkdir(parents=True, exist_ok=True)

    write_text(
        datapack_root / "pack.mcmeta",
        json.dumps(
            {"pack": {"pack_format": 9, "description": "Armourer's Workshop Task 5B materialization datapack"}},
            indent=2,
        )
        + "\n",
    )
    write_text(load_tag_dir / "load.json", json.dumps({"values": [f"{DATAPACK_NAME}:apply"]}, indent=2) + "\n")

    lines = [
        f"say {DATAPACK_SAY_PREFIX} applying converted Armourer's Workshop 5A patch",
        *commands,
        f"say {DATAPACK_SAY_PREFIX} apply complete",
    ]
    apply_path = function_dir / "apply.mcfunction"
    write_text(apply_path, "\n".join(lines) + "\n")
    return {
        "datapack_root": rel(datapack_root),
        "apply_function": f"{DATAPACK_NAME}:apply",
        "apply_path": rel(apply_path),
        "function_lines": len(lines),
    }


def write_server_properties(server_dir: Path, target_world: Path, output_path: Path) -> None:
    source = server_dir / "server.properties"
    text = source.read_text(encoding="utf-8") if source.exists() else (
        "enable-command-block=true\nonline-mode=false\nspawn-protection=0\n"
    )
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
    write_text(output_path, "\n".join(lines) + "\n")


def copy_skin_library_sidecars(patch: dict[str, Any], target_world: Path) -> dict[str, Any]:
    copied: list[str] = []
    missing_sources: list[str] = []
    for sidecar in patch.get("sidecars", []):
        if sidecar.get("op") != "armourers_workshop_convert_skin_library":
            continue
        source_root = PROJECT_ROOT / str(sidecar["source_root"])
        target_root = target_world / str(sidecar.get("target_root", "skin-library"))
        if not source_root.exists():
            missing_sources.append(rel(source_root))
            continue
        for source_file in sorted(source_root.rglob("*.armour")):
            relative = source_file.relative_to(source_root)
            target_file = target_root / relative
            target_file.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source_file, target_file)
            copied.append(rel(target_file))
    return {"copied_files": copied, "copied_count": len(copied), "missing_sources": missing_sources}


def validate_aw_targets(patch: dict[str, Any], server_dir: Path) -> dict[str, Any]:
    targets = sorted(
        {
            str(event["block"])
            for event in patch.get("events", [])
            if str(event.get("block", "")).startswith("armourers_workshop:")
        }
    )
    jar = find_armourers_workshop_jar(server_dir)
    if jar is None:
        return {"status": "missing_aw_jar", "target_count": len(targets), "missing": targets}

    with zipfile.ZipFile(jar) as archive:
        known = {
            path.removeprefix("assets/armourers_workshop/blockstates/").removesuffix(".json")
            for path in archive.namelist()
            if path.startswith("assets/armourers_workshop/blockstates/") and path.endswith(".json")
        }
    missing = [target for target in targets if target.split(":", 1)[1] not in known]
    return {
        "status": "ok" if not missing else "missing_targets",
        "jar": rel(jar),
        "target_count": len(targets),
        "known_blockstate_count": len(known),
        "missing": missing,
    }


def write_markdown_report(report: dict[str, Any]) -> None:
    stats = report["stats"]
    lines = [
        "# Armourer's Workshop Task 5B - raport",
        "",
        "## Podsumowanie",
        "",
        f"- Status: `{report['status']}`",
        f"- Target world: `{report['target_world']}`",
        f"- Komendy setblock: `{stats['commands']}`",
        f"- Eventy blokow: `{stats['block_events']}`",
        f"- Eventy BlockEntity: `{stats['block_entity_events']}`",
        f"- Fallbacki: `{stats['fallback_count']}`",
        f"- Skopiowane pliki `.armour`: `{report['skin_library']['copied_count']}`",
        f"- AW registry preflight: `{report['aw_registry_preflight']['status']}`",
        "",
        "## Fallbacki",
        "",
    ]
    if stats["fallback_reasons"]:
        for reason, count in sorted(stats["fallback_reasons"].items()):
            lines.append(f"- `{reason}`: `{count}`")
    else:
        lines.append("- Brak fallbackow.")

    lines += [
        "",
        "## Resolutions",
        "",
        "| Source | Target | Fallback | Reason |",
        "|--------|--------|----------|--------|",
    ]
    for resolution in report["sample_resolutions"]:
        fallback = "TAK" if resolution["fallback"] else "NIE"
        lines.append(
            f"| `{resolution['source_block']}` | `{resolution['target_block']}` | {fallback} | `{resolution['reason']}` |"
        )

    lines += [
        "",
        "## Skin library",
        "",
        f"- Source sidecar files copied: `{report['skin_library']['copied_count']}`",
    ]
    for copied in report["skin_library"]["copied_files"]:
        lines.append(f"- `{copied}`")
    if report["skin_library"]["missing_sources"]:
        lines.append("- Missing sidecar sources:")
        for missing in report["skin_library"]["missing_sources"]:
            lines.append(f"- `{missing}`")

    lines += [
        "",
        "## Pliki",
        "",
        f"- `{rel(DEFAULT_REPORT)}`",
        f"- `{rel(DEFAULT_SERVER_PROPERTIES)}`",
        f"- `{rel(DEFAULT_TARGET_WORLD / 'datapacks' / DATAPACK_NAME)}`",
        "",
        "## Nastepne kroki",
        "",
        f"1. W Zadaniu 6 uruchomic headless 1.18.2 z `{DEFAULT_SERVER_PROPERTIES.name}` jako `server.properties`.",
        f"2. Potwierdzic w logu marker `{DATAPACK_SAY_PREFIX} apply complete`.",
        "3. Po dodaniu prawidlowego JAR-a AW 1.18.2 powtorzyc 5B bez fallbackow.",
    ]
    write_text(REPORT_MD, "\n".join(lines) + "\n")


def write_handoff(report: dict[str, Any]) -> None:
    stats = report["stats"]
    text = f"""# Handoff: Armourer's Workshop - Zadanie 5B

## Podsumowanie sesji

Wykonano Zadanie 5B dla Armourer's Workshop: przygotowano swiat headless 1.18.2,
datapack materializujacy `armourers_workshop_task5a_converted_patch_1182.json`
oraz przeniesiono fixture globalnej biblioteki `.armour` do `skin-library`.

## Ukonczono

- [x] Dodano `materialize_armourers_workshop_task5b.py`.
- [x] Skopiowano base world do `headless_server/1.18.2/world_armourers_workshop_task5b`.
- [x] Wygenerowano datapack `{DATAPACK_NAME}`.
- [x] Skopiowano sidecar `.armour` do target world.
- [x] Wygenerowano template `{DEFAULT_SERVER_PROPERTIES.name}`.
- [x] Wygenerowano raport JSON i Markdown.

## Wyniki

- Komendy setblock: `{stats['commands']}`.
- Eventy blokow: `{stats['block_events']}`.
- Eventy BlockEntity: `{stats['block_entity_events']}`.
- Fallbacki: `{stats['fallback_count']}`.
- Skopiowane pliki `.armour`: `{report['skin_library']['copied_count']}`.
- AW registry preflight: `{report['aw_registry_preflight']['status']}`.

## Uwaga

Na headless serwerze nie ma obecnie JAR-a Armourer's Workshop 1.18.2, wiec
eventy AW z NBT trafiaja do `conversion_placeholders:block_entity_placeholder`
z zachowanym oryginalnym NBT 1.18.2. Po dolozeniu wlasciwego JAR-a AW trzeba
powtorzyc 5B bez fallbackow.

## Nowe pliki

- `test_scenarios/armourers_workshop_task5a/materialize_armourers_workshop_task5b.py`
- `test_scenarios/armourers_workshop_task5a/armourers_workshop_task5b_headless_materialization_report.json`
- `test_scenarios/armourers_workshop_task5a/ARMOURERS_WORKSHOP_TASK5B_REPORT.md`
- `test_scenarios/armourers_workshop_task5a/HANDOFF_ARMOURERS_WORKSHOP_TASK5B.md`
- `test_scenarios/armourers_workshop_task5a/server_armourers_workshop_task5b.properties`
- `headless_server/1.18.2/world_armourers_workshop_task5b/`

## Nastepne kroki

1. [ ] Zadanie 6: uruchomic headless 1.18.2 i potwierdzic `{DATAPACK_SAY_PREFIX} apply complete`.
2. [ ] Dolozyc prawidlowy JAR AW 1.18.2 do `headless_server/1.18.2/mods` i powtorzyc 5B bez fallbackow.

---

**Status:** Zadanie 5B ukonczone
**Data:** 2026-05-28
"""
    write_text(HANDOFF, text)


def materialize(args: argparse.Namespace) -> dict[str, Any]:
    patch = load_json(args.patch)
    commands, resolutions, stats = build_commands(patch, args.server_dir)
    copy_world(args.base_world, args.target_world, args.overwrite)
    datapack = write_datapack(args.target_world, commands)
    skin_library = copy_skin_library_sidecars(patch, args.target_world)
    write_server_properties(args.server_dir, args.target_world, args.server_properties_out)
    aw_registry = validate_aw_targets(patch, args.server_dir)

    report = {
        "name": "Armourer's Workshop Task 5B headless materialization",
        "status": "world_copy_prepared_with_datapack",
        "patch": rel(args.patch),
        "server_dir": rel(args.server_dir),
        "base_world": rel(args.base_world),
        "target_world": rel(args.target_world),
        "server_properties_template": rel(args.server_properties_out),
        "installed_mod_ids": sorted(installed_mod_ids(args.server_dir)),
        "datapack": datapack,
        "skin_library": skin_library,
        "stats": stats,
        "aw_registry_preflight": aw_registry,
        "sample_resolutions": resolutions,
        "next_steps": [
            f"Copy {args.server_properties_out} to {args.server_dir / 'server.properties'} or set level-name directly.",
            "Start the 1.18.2 Forge headless server.",
            f"Confirm logs contain '{DATAPACK_SAY_PREFIX} apply complete'.",
            "Continue with Task 6: tick/restart verification.",
        ],
    }
    write_json(args.report, report)
    write_markdown_report(report)
    write_handoff(report)
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description="Materialize Armourer's Workshop Task 5B")
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
    print(f"Datapack:     {report['datapack']['datapack_root']}")
    print(f"Commands:     {report['stats']['commands']}")
    print(f"Fallbacks:    {report['stats']['fallback_count']}")
    print(f"AW preflight: {report['aw_registry_preflight']['status']}")
    print(f"Skin files:   {report['skin_library']['copied_count']}")
    print(f"Report:       {args.report}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
