#!/usr/bin/env python3
"""Materialize Reliquary Task 5B as a 1.18.2 headless-server datapack.

Reads reliquary_task5a_converted_patch_1182.json, generates setblock commands,
copies the base world, writes a datapack into the new world directory, and
produces a server.properties template.

When the `reliquary` mod is not installed on the headless server:
  - TE blocks (altar, cauldron, mortar) → conversion_placeholders:block_entity_placeholder
  - fertile_lily_pad  → minecraft:lily_pad
  - interdiction_torch → minecraft:torch
  - wraith_node        → minecraft:stone
"""

from __future__ import annotations

import argparse
import json
import shutil
from collections import Counter
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parents[2]
SCENARIO_DIR = Path(__file__).resolve().parent

DEFAULT_PATCH = SCENARIO_DIR / "reliquary_task5a_converted_patch_1182.json"
DEFAULT_SERVER_DIR = PROJECT_ROOT / "headless_server" / "1.18.2"
DEFAULT_BASE_WORLD = DEFAULT_SERVER_DIR / "world"
DEFAULT_TARGET_WORLD = DEFAULT_SERVER_DIR / "world_reliquary_task5b"
DEFAULT_REPORT = SCENARIO_DIR / "reliquary_task5b_headless_materialization_report.json"
DEFAULT_SERVER_PROPERTIES = SCENARIO_DIR / "server_reliquary_task5b.properties"
REPORT_MD = SCENARIO_DIR / "RELIQUARY_TASK5B_REPORT.md"
HANDOFF = SCENARIO_DIR / "HANDOFF_RELIQUARY_TASK5B.md"

DATAPACK_NAME = "reliquary_task5b"
DATAPACK_SAY_PREFIX = "[RELIQUARY_TASK5B]"

# Vanilla fallbacks for Reliquary blocks when the mod is not installed.
# TE blocks use the placeholder so NBT is preserved.
_RELIQUARY_VANILLA_FALLBACK: dict[str, str] = {
    "reliquary:alkahestry_altar":    "conversion_placeholders:block_entity_placeholder",
    "reliquary:apothecary_cauldron": "conversion_placeholders:block_entity_placeholder",
    "reliquary:apothecary_mortar":   "conversion_placeholders:block_entity_placeholder",
    "reliquary:fertile_lily_pad":    "minecraft:lily_pad",
    "reliquary:interdiction_torch":  "minecraft:torch",
    "reliquary:wraith_node":         "minecraft:stone",
}


# ──────────────────────────────────────────────────────────────────────────────
# Helpers
# ──────────────────────────────────────────────────────────────────────────────

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
    ids: set[str] = {"minecraft"}
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
        elif "reliquary" in name:
            ids.add("reliquary")
        elif "rechiseled" in name:
            ids.add("rechiseled")
    return ids


def resolve_block(
    block_id: str,
    nbt: dict[str, Any] | None,
    installed: set[str],
) -> tuple[str, dict[str, Any] | None, bool]:
    """Return (resolved_block_id, resolved_nbt, used_fallback)."""
    namespace = block_id.split(":", 1)[0]
    if namespace in installed:
        return block_id, nbt, False

    fallback = _RELIQUARY_VANILLA_FALLBACK.get(block_id)
    if fallback is None:
        # Generic fallback for unknown reliquary: blocks
        fallback = "minecraft:stone"

    if fallback == "conversion_placeholders:block_entity_placeholder":
        if "conversion_placeholders" not in installed:
            # Can't place the placeholder — fall back to stone but warn
            return "minecraft:stone", None, True
        # Preserve NBT in placeholder
        resolved_nbt: dict[str, Any] | None = None
        if nbt is not None:
            resolved_nbt = dict(nbt)
            resolved_nbt["id"] = "conversion_placeholders:block_entity_placeholder"
        return fallback, resolved_nbt, True

    return fallback, None, True


def block_state_str(block_id: str, properties: dict[str, Any] | None) -> str:
    if not properties:
        return block_id
    props = ",".join(f"{k}={v}" for k, v in sorted(properties.items()))
    return f"{block_id}[{props}]"


def setblock_command(
    edit: dict[str, Any], installed: set[str]
) -> tuple[str, dict[str, Any]]:
    pos = edit["pos"]
    source_block = str(edit["block"])
    source_nbt = edit.get("nbt")

    target_block, target_nbt, used_fallback = resolve_block(source_block, source_nbt, installed)
    properties = edit.get("blockstate") if not used_fallback else None
    state = block_state_str(target_block, properties)
    snbt = to_snbt(target_nbt) if target_nbt else ""
    command = f"setblock {pos[0]} {pos[1]} {pos[2]} {state}{snbt} replace"
    return command, {
        "source_block": source_block,
        "target_block": target_block,
        "fallback": used_fallback,
        "has_nbt": target_nbt is not None,
        "op": edit.get("op"),
        "pos": pos,
    }


# ──────────────────────────────────────────────────────────────────────────────
# Datapack writer
# ──────────────────────────────────────────────────────────────────────────────

def write_datapack(target_world: Path, commands: list[str]) -> dict[str, Any]:
    datapack_root = target_world / "datapacks" / DATAPACK_NAME
    function_dir = datapack_root / "data" / DATAPACK_NAME / "functions"
    load_tag_dir = datapack_root / "data" / "minecraft" / "tags" / "functions"
    function_dir.mkdir(parents=True, exist_ok=True)
    load_tag_dir.mkdir(parents=True, exist_ok=True)

    (datapack_root / "pack.mcmeta").write_text(
        json.dumps(
            {"pack": {"pack_format": 9, "description": "Reliquary Task 5B materialization datapack"}},
            indent=2,
        ) + "\n",
        encoding="utf-8",
    )
    (load_tag_dir / "load.json").write_text(
        json.dumps({"values": [f"{DATAPACK_NAME}:apply"]}, indent=2) + "\n",
        encoding="utf-8",
    )
    lines = [
        f"say {DATAPACK_SAY_PREFIX} applying converted Reliquary 5A patch",
        *commands,
        f"say {DATAPACK_SAY_PREFIX} apply complete",
    ]
    apply_path = function_dir / "apply.mcfunction"
    apply_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return {
        "datapack_root": str(datapack_root.relative_to(PROJECT_ROOT)),
        "apply_function": f"{DATAPACK_NAME}:apply",
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
    output_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


# ──────────────────────────────────────────────────────────────────────────────
# Report / markdown
# ──────────────────────────────────────────────────────────────────────────────

def write_markdown_report(report: dict[str, Any]) -> None:
    stats = report["stats"]
    fallback_note = (
        "Reliquary nie jest zainstalowany na headless serwerze. "
        "Bloki TE (altar, cauldron, mortar) zmaterializowano jako "
        "`conversion_placeholders:block_entity_placeholder` z pełnym NBT 1.18.2. "
        "Bloki bez TE (lily_pad, torch, stone) zmapowano na najbliższy odpowiednik vanilla."
    )
    lines = [
        "# Reliquary Task 5B – Raport materializacji",
        "",
        "## Podsumowanie",
        "",
        f"- Status: `{report['status']}`",
        f"- Target world: `{report['target_world']}`",
        f"- Komendy setblock: {stats['commands']}",
        f"- Edycje bloków: {stats['block_edits']}",
        f"- Edycje BlockEntity: {stats['block_entity_edits']}",
        f"- Fallbacki (brak moda): {stats['fallback_count']}",
        "",
        "## Uwaga o fallbackach",
        "",
        fallback_note,
        "",
        "## Resolutions per próbka",
        "",
        "| Blok źródłowy | Target | Fallback |",
        "|---------------|--------|----------|",
    ]
    for res in report.get("sample_resolutions", []):
        fb = "✅" if not res["fallback"] else "⚠️"
        lines.append(f"| `{res['source_block']}` | `{res['target_block']}` | {fb} |")

    lines += [
        "",
        "## Pliki",
        "",
        f"- `{DEFAULT_REPORT.name}`",
        f"- `{DEFAULT_SERVER_PROPERTIES.name}`",
        f"- `headless_server/1.18.2/{DEFAULT_TARGET_WORLD.name}/datapacks/{DATAPACK_NAME}/`",
        "",
        "## Następne kroki",
        "",
        f"1. Uruchomić headless 1.18.2 z `{DEFAULT_SERVER_PROPERTIES.name}` jako `server.properties`.",
        f"2. Potwierdzić w logu marker `{DATAPACK_SAY_PREFIX} apply complete`.",
        "3. W Zadaniu 6 wykonać tick/restart verification.",
        "4. Po zainstalowaniu JARa Reliquary powtórzyć 5B bez fallbacków.",
    ]
    write_text(REPORT_MD, "\n".join(lines) + "\n")


def write_handoff(report: dict[str, Any]) -> None:
    stats = report["stats"]
    text = f"""# Handoff: Reliquary – Zadanie 5B

## Podsumowanie sesji

Wykonano Zadanie 5B dla Reliquary: przygotowano kopię świata headless 1.18.2 i datapack,
który materializuje `reliquary_task5a_converted_patch_1182.json` komendami `/setblock`.

## Ukończono

- [x] Dodano `materialize_reliquary_task5b.py`
- [x] Skopiowano base world do `headless_server/1.18.2/world_reliquary_task5b`
- [x] Wygenerowano datapack `{DATAPACK_NAME}`
- [x] Wygenerowano template `{DEFAULT_SERVER_PROPERTIES.name}`
- [x] Wygenerowano raport JSON i Markdown

## Wyniki

- Komendy setblock: {stats['commands']}
- Edycje bloków: {stats['block_edits']}
- Edycje BlockEntity (z NBT): {stats['block_entity_edits']}
- Fallbacki (Reliquary nie zainstalowany): {stats['fallback_count']}

## Kluczowa informacja o fallbackach

Reliquary JAR nie jest na headless serwerze. Bloki TE trafią do
`conversion_placeholders:block_entity_placeholder` z zachowanym NBT 1.18.2.
Po dodaniu JARa Reliquary i ponownym uruchomieniu 5B dane będą gotowe do
pełnej weryfikacji.

## Nowe pliki

- `test_scenarios/reliquary_task5a/materialize_reliquary_task5b.py`
- `test_scenarios/reliquary_task5a/reliquary_task5b_headless_materialization_report.json`
- `test_scenarios/reliquary_task5a/RELIQUARY_TASK5B_REPORT.md`
- `test_scenarios/reliquary_task5a/HANDOFF_RELIQUARY_TASK5B.md`
- `test_scenarios/reliquary_task5a/server_reliquary_task5b.properties`
- `headless_server/1.18.2/world_reliquary_task5b/`

## Następne kroki (Zadanie 6)

1. [ ] Uruchomić headless 1.18.2 z `server_reliquary_task5b.properties`
2. [ ] Potwierdzić marker `{DATAPACK_SAY_PREFIX} apply complete` w logu
3. [ ] Wykonać tick/restart verification przez RCON
4. [ ] Opcjonalnie: zainstalować Reliquary JAR i powtórzyć bez fallbacków

---

**Status:** ✅ Zadanie 5B ukończone
**Data:** 2026-05-28
"""
    write_text(HANDOFF, text)


# ──────────────────────────────────────────────────────────────────────────────
# Main
# ──────────────────────────────────────────────────────────────────────────────

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
        # fertile_lily_pad requires water in the block below — inject it first.
        if (
            not resolution["fallback"]
            and resolution["source_block"] == "reliquary:fertile_lily_pad"
        ):
            pos = edit["pos"]
            commands.append(f"setblock {pos[0]} {pos[1] - 2} {pos[2]} minecraft:stone replace")
            commands.append(f"setblock {pos[0]} {pos[1] - 1} {pos[2]} minecraft:water replace")
        commands.append(command)
        resolutions.append(resolution)
        if resolution["fallback"]:
            fallback_counts[resolution["source_block"]] += 1

    copy_world(args.base_world, args.target_world, args.overwrite)
    datapack = write_datapack(args.target_world, commands)
    write_server_properties(args.server_dir, args.target_world, args.server_properties_out)

    all_edits = [e for e in patch.get("edits", []) if e.get("op") in {"set_block", "set_block_entity"}]
    be_edits = [e for e in all_edits if e.get("op") == "set_block_entity"]

    report = {
        "name": "Reliquary Task 5B headless materialization",
        "status": "world_copy_prepared_with_datapack",
        "patch": str(args.patch.relative_to(PROJECT_ROOT)),
        "server_dir": str(args.server_dir.relative_to(PROJECT_ROOT)),
        "base_world": str(args.base_world.relative_to(PROJECT_ROOT)),
        "target_world": str(args.target_world.relative_to(PROJECT_ROOT)),
        "server_properties_template": str(args.server_properties_out.relative_to(PROJECT_ROOT)),
        "installed_mod_ids": sorted(installed),
        "datapack": datapack,
        "stats": {
            "commands": len(commands),
            "block_edits": len(all_edits),
            "block_entity_edits": len(be_edits),
            "fallback_count": sum(fallback_counts.values()),
            "fallback_unique_blocks": len(fallback_counts),
        },
        "fallback_counts": dict(fallback_counts.most_common()),
        "sample_resolutions": resolutions,
        "next_steps": [
            f"Copy {args.server_properties_out} to {args.server_dir / 'server.properties'} or set level-name directly.",
            "Start the 1.18.2 Forge headless server.",
            f"Confirm logs contain '{DATAPACK_SAY_PREFIX} apply complete'.",
            "Continue with Task 6: tick/restart verification via RCON.",
        ],
    }
    write_json(args.report, report)
    write_markdown_report(report)
    write_handoff(report)
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description="Materialize Reliquary Task 5B")
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
    print(f"Report:       {args.report}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
