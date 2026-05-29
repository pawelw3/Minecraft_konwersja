"""Block-only converter for Open Modular Turrets defensive blocks."""

from __future__ import annotations

from converters.common.block_only import BlockOnlyResult, Position, explicit_fallback, normalize_metadata
from converters.common.placeholders import PLACEHOLDER_BLOCK_ID


HARD_WALLS = {
    "hardwalltierone": "minecraft:obsidian",
    "hardwalltiertwo": "minecraft:obsidian",
    "hardwalltierthree": "minecraft:netherite_block",
    "hardwalltierfour": "minecraft:netherite_block",
    "hardwalltierfive": PLACEHOLDER_BLOCK_ID,
}
FENCES = {
    "fencetierone",
    "fencetiertwo",
    "fencetierthree",
    "fencetierfour",
    "fencetierfive",
}


def convert_block_only(
    numeric_id: int,
    registry_name: str,
    metadata: int,
    position: Position = (0, 0, 0),
) -> BlockOnlyResult:
    del numeric_id, position
    meta = normalize_metadata(metadata)
    if not registry_name.startswith("openmodularturrets:"):
        return BlockOnlyResult.fail(f"OMT-BO-E-NOT-OMT: {registry_name}")
    if meta != 0:
        return explicit_fallback(
            PLACEHOLDER_BLOCK_ID,
            f"OMT-BO-W-UNEXPECTED-META: {registry_name}:{meta}",
        )

    name = registry_name.split(":", 1)[1].lower()
    if name in HARD_WALLS:
        confidence = "medium" if HARD_WALLS[name] != PLACEHOLDER_BLOCK_ID else "low"
        return explicit_fallback(HARD_WALLS[name], f"OMT-BO-W-HARDWALL-FALLBACK: {name}", confidence=confidence)
    if name in FENCES:
        return explicit_fallback("minecraft:iron_bars", f"OMT-BO-W-FENCE-FALLBACK: {name}", confidence="medium")
    return BlockOnlyResult.fail(
        f"OMT-BO-E-REQUIRES-BLOCK-ENTITY: {registry_name}:{meta}",
        warnings=["block is owned by OMT TE/entity converter"],
    )
