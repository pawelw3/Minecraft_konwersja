"""Mapping helpers for Chisel 1.7.10 decorative block conversion.

The real 1.7.10 world stores Chisel blocks as numeric IDs plus metadata.
This module therefore supports a dynamic ID table discovered from a map or
test world, while also offering visual family fallbacks for hand-written tests.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parents[3]
RECHISELED_BLOCKSTATES = (
    PROJECT_ROOT
    / "mod_src"
    / "118"
    / "actual_src"
    / "1.18.2"
    / "Rechiseled"
    / "repo"
    / "src"
    / "generated"
    / "resources"
    / "assets"
    / "rechiseled"
    / "blockstates"
)
CHIPPED_BLOCKSTATES = (
    PROJECT_ROOT
    / "mod_src"
    / "118"
    / "actual_src"
    / "1.18.2"
    / "Chipped"
    / "repo"
    / "common"
    / "src"
    / "main"
    / "generated"
    / "resources"
    / "assets"
    / "chipped"
    / "blockstates"
)


@dataclass(frozen=True)
class ChiselBlockKey:
    block_id: str
    metadata: int


@dataclass(frozen=True)
class ChiselTarget:
    block_id: str
    confidence: str
    reason: str
    visual_family: str
    blockstate_props: dict[str, str] = field(default_factory=dict)


@dataclass(frozen=True)
class DynamicChiselIdEntry:
    numeric_id: int
    family: str
    meta_variants: dict[int, str] = field(default_factory=dict)


def normalize_family(value: str) -> str:
    value = value.replace("Chisel:", "").replace("chisel:", "")
    value = value.replace("-", "_").replace("/", "_")
    value = re.sub(r"[^a-zA-Z0-9_]+", "_", value).lower()
    value = re.sub(r"_+", "_", value).strip("_")
    aliases = {
        "stonebricksmooth": "stone_bricks",
        "stonebrick": "stone_bricks",
        "endstone": "end_stone",
        "sandstoneyellow": "sandstone",
        "sandstonered": "red_sandstone",
        "cobblestonemossy": "mossy_cobblestone",
        "netherbrick": "nether_bricks",
        "netherrack": "netherrack",
        "gold": "gold_block",
        "gold_block": "gold_block",
        "blockgold": "gold_block",
        "iron": "iron_block",
        "iron_block": "iron_block",
        "blockiron": "iron_block",
        "diamond": "diamond_block",
        "diamond_block": "diamond_block",
        "emerald": "emerald_block",
        "emerald_block": "emerald_block",
        "lapis": "lapis_block",
        "lapis_block": "lapis_block",
        "redstone": "redstone_block",
        "redstone_block": "redstone_block",
        "glowstone": "glowstone",
        "quartz": "quartz_block",
        "factoryblock": "factory",
        "technicalnew": "technical",
        "technical2": "technical",
        "glasspane": "glass_pane",
        "glasspanedyed": "stained_glass_pane",
        "glassdyed": "stained_glass",
        "planks": "oak_planks",
        "wood": "oak_planks",
    }
    return aliases.get(value, value)


def variant_tokens(value: str) -> list[str]:
    value = normalize_family(value)
    tokens = [token for token in value.split("_") if token]
    return tokens


def load_dynamic_id_map(path: str | Path | None) -> dict[int, DynamicChiselIdEntry]:
    if path is None:
        return {}
    raw_path = Path(path)
    if not raw_path.exists():
        return {}
    data = json.loads(raw_path.read_text(encoding="utf-8"))
    entries: dict[int, DynamicChiselIdEntry] = {}
    for item in data.get("chisel_ids", data if isinstance(data, list) else []):
        numeric_id = int(item["numeric_id"])
        entries[numeric_id] = DynamicChiselIdEntry(
            numeric_id=numeric_id,
            family=normalize_family(str(item["family"])),
            meta_variants={int(k): str(v) for k, v in (item.get("meta_variants") or {}).items()},
        )
    return entries


def available_targets() -> set[str]:
    targets: set[str] = set()
    for namespace, blockstate_dir in (("rechiseled", RECHISELED_BLOCKSTATES), ("chipped", CHIPPED_BLOCKSTATES)):
        if not blockstate_dir.exists():
            continue
        for path in blockstate_dir.glob("*.json"):
            targets.add(f"{namespace}:{path.stem}")
    return targets


def base_target_candidates(family: str, variant_hint: str | None = None) -> list[tuple[str, str]]:
    family = normalize_family(family)
    variant = normalize_family(variant_hint or "")
    candidates: list[tuple[str, str]] = []

    # Rechiseled naming is material_pattern; use visually conservative patterns.
    pattern_preference = _pattern_preference(variant)
    for pattern in pattern_preference:
        candidates.append((f"rechiseled:{family}_{pattern}", f"rechiseled pattern {pattern}"))

    # Some Rechiseled families use vanilla-style base names.
    if family == "stone_bricks":
        for pattern in pattern_preference:
            candidates.append((f"rechiseled:stone_{pattern}", f"stone fallback pattern {pattern}"))
    if family == "factory":
        candidates.extend([
            ("rechiseled:iron_block_plating", "industrial plating fallback"),
            ("rechiseled:iron_block_bricks", "industrial bricks fallback"),
        ])
    if family == "technical":
        candidates.extend([
            ("rechiseled:iron_block_bordered_plating", "technical metal panel fallback"),
            ("rechiseled:iron_block_plating", "technical metal fallback"),
        ])
    if family in {"marble", "limestone", "temple", "templemossy", "holystone"}:
        candidates.extend([
            ("rechiseled:quartz_block_small_tiles", "light stone small tiles fallback"),
            ("rechiseled:quartz_block_brick_paving", "light stone brick fallback"),
            ("rechiseled:stone_small_tiles", "stone small tiles fallback"),
        ])
    if family in {"glass", "stained_glass", "glass_pane", "stained_glass_pane"}:
        candidates.extend([
            ("minecraft:glass", "transparent vanilla fallback"),
            ("minecraft:glass_pane", "transparent pane fallback"),
        ])
    if family in {"carpet", "wool", "woolen_clay"}:
        candidates.append(("minecraft:white_wool", "wool color fallback until dye metadata is decoded"))

    # Chipped fallback catches decorative variants that Rechiseled lacks.
    for pattern in pattern_preference:
        candidates.append((f"chipped:{family}_{pattern}", f"chipped pattern {pattern}"))

    candidates.append((_vanilla_fallback(family), "vanilla material fallback"))
    return candidates


def resolve_visual_target(family: str, metadata: int = 0, variant_hint: str | None = None) -> ChiselTarget:
    targets = available_targets()
    family = normalize_family(family)
    candidates = base_target_candidates(family, variant_hint)
    for block_id, reason in candidates:
        if block_id in targets or block_id.startswith("minecraft:"):
            confidence = "high" if block_id in targets and normalize_family(block_id.split(":", 1)[1]).startswith(family) else "medium"
            return ChiselTarget(
                block_id=block_id,
                confidence=confidence,
                reason=f"{reason}; meta={metadata}",
                visual_family=family,
            )
    return ChiselTarget(
        block_id="minecraft:stone",
        confidence="low",
        reason=f"no visual target found for family={family} meta={metadata}",
        visual_family=family,
    )


def resolve_from_block_id(
    block_id: str | int,
    metadata: int,
    dynamic_id_map: dict[int, DynamicChiselIdEntry] | None = None,
) -> ChiselTarget:
    dynamic_id_map = dynamic_id_map or {}
    if isinstance(block_id, int) or str(block_id).isdigit():
        numeric_id = int(block_id)
        entry = dynamic_id_map.get(numeric_id)
        if entry is None:
            return ChiselTarget(
                block_id="minecraft:stone",
                confidence="low",
                reason=f"unknown numeric Chisel id {numeric_id}; dynamic id map required",
                visual_family="unknown",
            )
        return resolve_visual_target(entry.family, metadata, entry.meta_variants.get(metadata))

    raw = str(block_id)
    if ":" in raw:
        namespace, path = raw.split(":", 1)
        if namespace.lower() == "chisel":
            return resolve_visual_target(path, metadata)
    return resolve_visual_target(raw, metadata)


def is_chisel_te_id(te_id: str) -> bool:
    lowered = te_id.lower()
    return te_id in {
        "TileEntityAutoChisel",
        "TileEntityCarvableBeacon",
        "TileEntityPresent",
        "chisel:TileEntityAutoChisel",
        "chisel:autoChisel",
        "chisel:auto_chisel",
    } or lowered in {
        "autochisel",
        "tile.chisel.autochisel",
        "tile.chisel.present",
        "chisel:present",
        "tile.chisel.beacon",
        "chisel:beacon",
    } or "autochisel" in lowered


def is_chisel_block_id(block_id: str | int, dynamic_id_map: dict[int, DynamicChiselIdEntry] | None = None) -> bool:
    if isinstance(block_id, int) or str(block_id).isdigit():
        return int(block_id) in (dynamic_id_map or {})
    return str(block_id).lower().startswith("chisel:")


def _pattern_preference(variant_hint: str) -> list[str]:
    tokens = set(variant_tokens(variant_hint))
    if {"pillar", "column"} & tokens:
        return ["pillar", "chiseled", "polished"]
    if {"small", "smalltile", "smalltiles"} & tokens:
        return ["small_tiles", "tiles", "brick_pattern"]
    if {"large", "largetile", "largetiles"} & tokens:
        return ["large_tiles", "tiles", "brick_paving"]
    if {"cracked", "broken"} & tokens:
        return ["cracked", "bricks", "tiles"]
    if {"panel", "border", "bordered"} & tokens:
        return ["bordered", "panel", "polished"]
    if {"ornate", "chiseled", "carved"} & tokens:
        return ["chiseled", "ornate", "polished"]
    if {"brick", "bricks", "lbrick"} & tokens:
        return ["bricks", "brick_pattern", "brick_paving"]
    if {"tile", "tiles"} & tokens:
        return ["tiles", "small_tiles", "large_tiles"]
    return ["tiles", "bricks", "polished", "chiseled"]


def _vanilla_fallback(family: str) -> str:
    return {
        "andesite": "minecraft:polished_andesite",
        "diorite": "minecraft:polished_diorite",
        "granite": "minecraft:polished_granite",
        "cobblestone": "minecraft:cobblestone",
        "mossy_cobblestone": "minecraft:mossy_cobblestone",
        "stone_bricks": "minecraft:stone_bricks",
        "sandstone": "minecraft:cut_sandstone",
        "red_sandstone": "minecraft:cut_red_sandstone",
        "obsidian": "minecraft:obsidian",
        "glowstone": "minecraft:glowstone",
        "quartz_block": "minecraft:chiseled_quartz_block",
        "gold_block": "minecraft:gold_block",
        "iron_block": "minecraft:iron_block",
        "diamond_block": "minecraft:diamond_block",
        "emerald_block": "minecraft:emerald_block",
        "lapis_block": "minecraft:lapis_block",
        "redstone_block": "minecraft:redstone_block",
        "end_stone": "minecraft:end_stone_bricks",
        "purpur": "minecraft:purpur_block",
        "oak_planks": "minecraft:oak_planks",
    }.get(family, "minecraft:stone")
