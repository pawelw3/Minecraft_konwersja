#!/usr/bin/env python3
"""Build a safer 1.7.10 ZSRR slice with non-AE2/Mekanism blocks as placeholders."""

from __future__ import annotations

import argparse
import json
import shutil
import sys
from collections import Counter
from pathlib import Path
from typing import Any

import nbtlib
from nbtlib import Compound, Int, List, String


PROJECT_ROOT = Path(__file__).resolve().parents[2]
SCENARIO_DIR = Path(__file__).resolve().parent
DEFAULT_SOURCE = PROJECT_ROOT / "lightweigh_map_templates" / "1710_modded" / "zsrr_ae2_mek_300"
DEFAULT_TARGET = PROJECT_ROOT / "lightweigh_map_templates" / "1710_modded" / "zsrr_ae2_mek_300_placeholders_1710"
DEFAULT_PATCH = SCENARIO_DIR / "zsrr_ae2_mek_300_placeholders_1710_patch.json"
DEFAULT_REPORT = SCENARIO_DIR / "zsrr_ae2_mek_300_placeholders_1710_report.json"

PLACEHOLDER_BLOCK_ID = 4095
PLACEHOLDER_BLOCK_REGISTRY = "conversionplaceholders1710:block_entity_placeholder"
PLACEHOLDER_TE_ID = "conversionplaceholders1710.block_entity_placeholder"
PLACEHOLDER_MOD_ID = "conversionplaceholders1710"
PLACEHOLDER_MOD_VERSION = "1.0.0"
VANILLA_MAX_ID_1710 = 175

KEEP_MOD_PREFIXES = (
    "appliedenergistics2:",
    "mekanism:",
    "mekanismgenerators:",
    "mekanismtools:",
)

sys.path.insert(0, str(PROJECT_ROOT))
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from minecraft_map_parser.anvil_parser import AnvilParser  # noqa: E402
from src.converters.mekanism.analyze_map_coverage import (  # noqa: E402
    get_block_at,
    get_nibble,
    load_block_registry,
    nbt_to_python,
    section_arrays,
)
from test_scenarios.zsrr_ae2_mek_slice.prune_1710_placeholder_level_dat import prune_world  # noqa: E402


def write_json(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def sanitize_json(value: Any) -> Any:
    if isinstance(value, dict):
        return {str(key): sanitize_json(inner) for key, inner in value.items()}
    if isinstance(value, (list, tuple)):
        return [sanitize_json(item) for item in value]
    if isinstance(value, bytes):
        return [int(item) for item in value]
    if isinstance(value, bytearray):
        return [int(item) for item in value]
    if isinstance(value, (str, int, float, bool)) or value is None:
        return value
    return str(value)


def copy_world(source: Path, target: Path) -> None:
    root = (PROJECT_ROOT / "lightweigh_map_templates" / "1710_modded").resolve()
    target_resolved = target.resolve() if target.exists() else target.parent.resolve() / target.name
    if target.exists():
        if root not in target_resolved.parents:
            raise RuntimeError(f"Refusing to delete outside templates: {target_resolved}")
        shutil.rmtree(target)
    shutil.copytree(source, target)


def patch_level_dat(world: Path) -> None:
    for name in ("level.dat", "level.dat_old"):
        path = world / name
        if not path.exists():
            continue
        nbt_file = nbtlib.load(path)
        root = nbt_file
        fml = root.setdefault("FML", Compound())
        item_data = fml.setdefault("ItemData", List[Compound]())
        mod_list = fml.setdefault("ModList", List[Compound]())

        existing_by_key = {str(entry.get("K")): entry for entry in item_data}
        desired = {
            "\x01" + PLACEHOLDER_BLOCK_REGISTRY: PLACEHOLDER_BLOCK_ID,
            "\x02" + PLACEHOLDER_BLOCK_REGISTRY: PLACEHOLDER_BLOCK_ID,
        }
        for key, value in desired.items():
            if key in existing_by_key:
                existing_by_key[key]["V"] = Int(value)
            else:
                item_data.append(Compound({"K": String(key), "V": Int(value)}))

        if not any(str(entry.get("ModId")) == PLACEHOLDER_MOD_ID for entry in mod_list):
            mod_list.append(Compound({
                "ModId": String(PLACEHOLDER_MOD_ID),
                "ModVersion": String(PLACEHOLDER_MOD_VERSION),
            }))
        nbt_file.save(path, gzipped=True)


def is_kept_block(numeric_id: int, registry_name: str | None) -> bool:
    if numeric_id == 0:
        return True
    if numeric_id <= VANILLA_MAX_ID_1710:
        return True
    if registry_name is None:
        return False
    lower = registry_name.lower()
    return lower.startswith(KEEP_MOD_PREFIXES)


def source_mod(registry_name: str | None) -> str:
    if not registry_name or ":" not in registry_name:
        return "unknown"
    return registry_name.split(":", 1)[0]


def collect_tile_entities(world: Path) -> dict[tuple[int, int, int], dict[str, Any]]:
    result: dict[tuple[int, int, int], dict[str, Any]] = {}
    for region_file in sorted((world / "region").glob("r.*.*.mca")):
        parser = AnvilParser(str(region_file))
        for chunk in parser.get_all_chunks():
            for raw_te in chunk.get_tile_entities():
                te = sanitize_json(nbt_to_python(raw_te))
                try:
                    pos = (int(te["x"]), int(te["y"]), int(te["z"]))
                except (KeyError, TypeError, ValueError):
                    continue
                result[pos] = te
    return result


def placeholder_te(
    *,
    x: int,
    y: int,
    z: int,
    numeric_id: int,
    metadata: int,
    registry_name: str | None,
    original_te: dict[str, Any] | None,
) -> dict[str, Any]:
    original = dict(original_te or {})
    te_id = str(original.get("id") or "")
    return {
        "id": PLACEHOLDER_TE_ID,
        "x": x,
        "y": y,
        "z": z,
        "source_mod": source_mod(registry_name),
        "source_block_id": registry_name or "",
        "source_numeric_id": numeric_id,
        "source_te_id": te_id,
        "source_metadata": metadata,
        "source_pos": [x, y, z],
        "conversion_reason": "non_target_mod_replaced_for_1710_stability",
        "original_nbt": original,
        "extra": {
            "target_slice": "zsrr_ae2_mek_300",
            "kept_mods": ["appliedenergistics2", "Mekanism", "MekanismGenerators", "MekanismTools"],
            "had_original_te": original_te is not None,
        },
    }


def build_patch(world: Path) -> tuple[dict[str, Any], dict[str, Any]]:
    registry = load_block_registry(world)
    original_tes = collect_tile_entities(world)
    edits: list[dict[str, Any]] = []
    stats = Counter()
    by_source_block = Counter()
    by_source_mod = Counter()
    by_region = Counter()

    for region_file in sorted((world / "region").glob("r.*.*.mca")):
        parser = AnvilParser(str(region_file))
        for chunk in parser.get_all_chunks():
            chunk_x0 = chunk.x * 16
            chunk_z0 = chunk.z * 16
            for section in chunk.get_sections():
                section_y, blocks, add, data = section_arrays(section)
                if blocks is None:
                    continue
                base_y = int(section_y) * 16
                max_index = min(4096, len(blocks))
                for index in range(max_index):
                    numeric_id = (get_nibble(add, index) << 8) | (blocks[index] & 0xFF)
                    registry_name = registry.get(numeric_id)
                    if is_kept_block(numeric_id, registry_name):
                        continue
                    metadata = get_nibble(data, index)
                    local_x = index & 0x0F
                    local_z = (index >> 4) & 0x0F
                    local_y = (index >> 8) & 0x0F
                    x = chunk_x0 + local_x
                    y = base_y + local_y
                    z = chunk_z0 + local_z
                    original_te = original_tes.get((x, y, z))
                    edits.append({"op": "set_block", "x": x, "y": y, "z": z, "id": PLACEHOLDER_BLOCK_ID, "meta": 0})
                    edits.append({
                        "op": "set_te",
                        "x": x,
                        "y": y,
                        "z": z,
                        "nbt": placeholder_te(
                            x=x,
                            y=y,
                            z=z,
                            numeric_id=numeric_id,
                            metadata=metadata,
                            registry_name=registry_name,
                            original_te=original_te,
                        ),
                    })
                    key = f"{registry_name or '[unknown]'}:{metadata}"
                    by_source_block[key] += 1
                    by_source_mod[source_mod(registry_name)] += 1
                    by_region[region_file.name] += 1
                    stats["placeholder_blocks"] += 1
                    if original_te is not None:
                        stats["placeholder_blocks_with_original_te"] += 1

    # Remove non-kept orphan TileEntities left on vanilla/air positions.
    for (x, y, z), te in sorted(original_tes.items()):
        te_id = str(te.get("id") or "")
        chunk_x = x // 16
        chunk_z = z // 16
        region_file = world / "region" / f"r.{chunk_x // 32}.{chunk_z // 32}.mca"
        if not region_file.exists():
            continue
        parser = AnvilParser(str(region_file))
        matching_chunk = None
        for chunk in parser.get_all_chunks():
            if chunk.x == chunk_x and chunk.z == chunk_z:
                matching_chunk = chunk
                break
        if matching_chunk is None:
            continue
        numeric_id, _metadata = get_block_at(matching_chunk, x, y, z)
        registry_name = registry.get(numeric_id) if numeric_id is not None else None
        if numeric_id is not None and not is_kept_block(numeric_id, registry_name):
            continue
        lower_block = (registry_name or "").lower()
        if lower_block.startswith(KEEP_MOD_PREFIXES):
            continue
        if te_id:
            edits.append({"op": "remove_te", "x": x, "y": y, "z": z})
            stats["orphan_non_target_te_removed"] += 1

    patch = {
        "format_version": "1.7.10",
        "metadata": {
            "name": "zsrr_ae2_mek_300_placeholders_1710",
            "source_world": str(world),
            "placeholder_block_id": PLACEHOLDER_BLOCK_ID,
            "placeholder_registry": PLACEHOLDER_BLOCK_REGISTRY,
            "kept_mod_prefixes": KEEP_MOD_PREFIXES,
        },
        "edits": edits,
    }
    report = {
        "world": str(world),
        "placeholder_block_id": PLACEHOLDER_BLOCK_ID,
        "placeholder_registry": PLACEHOLDER_BLOCK_REGISTRY,
        "stats": dict(stats),
        "edit_count": len(edits),
        "top_source_mods": dict(by_source_mod.most_common(50)),
        "top_source_blocks": dict(by_source_block.most_common(100)),
        "by_region": dict(by_region),
    }
    return patch, report


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", type=Path, default=DEFAULT_SOURCE)
    parser.add_argument("--target", type=Path, default=DEFAULT_TARGET)
    parser.add_argument("--patch", type=Path, default=DEFAULT_PATCH)
    parser.add_argument("--report", type=Path, default=DEFAULT_REPORT)
    parser.add_argument(
        "--minimal-registry",
        action="store_true",
        help=(
            "Prune FML level.dat registry to vanilla/AE2/Mekanism/placeholders. "
            "Do not use this for a full 1.7.10 modpack client, because FML will "
            "try to inject the missing loaded mod IDs back into the world."
        ),
    )
    args = parser.parse_args()

    copy_world(args.source, args.target)
    patch_level_dat(args.target)
    if args.minimal_registry:
        prune_world(args.target)
    patch, report = build_patch(args.target)
    write_json(args.patch, patch)
    write_json(args.report, report)
    print(f"Created world copy: {args.target}")
    print(f"Placeholder blocks: {report['stats'].get('placeholder_blocks', 0)}")
    print(f"Patch edits: {report['edit_count']}")
    print(f"Patch: {args.patch}")
    print(f"Report: {args.report}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
