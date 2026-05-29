"""Block-only converter for Railcraft 1.7.10 simple blocks."""

from __future__ import annotations

from converters.common.block_only import BlockOnlyResult, Position, explicit_fallback, normalize_metadata
from converters.common.placeholders import PLACEHOLDER_BLOCK_ID
from converters.railcraft.mappings.block_mappings import get_mapping


BRICK_FALLBACKS = {
    "brick.abyssal": "minecraft:deepslate_bricks",
    "brick.bleachedbone": "minecraft:bone_block",
    "brick.bloodstained": "minecraft:red_nether_bricks",
    "brick.frostbound": "minecraft:packed_ice",
    "brick.quarried": "minecraft:smooth_stone",
    "brick.sandy": "minecraft:sandstone",
    "brick.nether": "minecraft:nether_bricks",
    "brick.infernal": "minecraft:blackstone",
}
DIRECT_FALLBACKS = {
    "fluid.creosote": ("thermal:creosote", "low"),
    "fluid.steam": ("minecraft:air", "medium"),
    "post.metal": ("minecraft:iron_bars", "medium"),
    "post.metal.platform": ("minecraft:iron_bars", "low"),
    "post": ("minecraft:oak_fence", "medium"),
    "wall.alpha": ("minecraft:stone_brick_wall", "medium"),
    "wall.beta": ("minecraft:blackstone_wall", "medium"),
    "glass": ("thermal:obsidian_glass", "medium"),
    "worldlogic": ("minecraft:air", "high"),
}


def convert_block_only(
    numeric_id: int,
    registry_name: str,
    metadata: int,
    position: Position = (0, 0, 0),
) -> BlockOnlyResult:
    del numeric_id, position
    meta = normalize_metadata(metadata)
    if not registry_name.startswith("Railcraft:"):
        return BlockOnlyResult.fail(f"RC-BO-E-NOT-RAILCRAFT: {registry_name}")
    block_id = "railcraft." + registry_name.split(":", 1)[1]

    mapping = get_mapping(block_id, meta)
    if mapping is not None:
        if mapping.has_block_entity:
            return BlockOnlyResult.fail(
                f"RC-BO-E-REQUIRES-BLOCK-ENTITY: {registry_name}:{meta}",
                warnings=["block is handled by Railcraft TE/event converter"],
            )
        warnings = [f"RC-BO-W-MAPPED: {mapping.notes}"] if mapping.notes else []
        confidence = "medium" if warnings else "high"
        return BlockOnlyResult.ok(
            mapping.target_block_id,
            blockstate_props=mapping.blockstate_props or {},
            confidence=confidence,
            warnings=warnings,
        )

    family = registry_name.split(":", 1)[1]
    if family in BRICK_FALLBACKS:
        return explicit_fallback(
            BRICK_FALLBACKS[family],
            f"RC-BO-W-BRICK-FALLBACK: {family}:{meta}",
            confidence="medium",
        )
    if family in DIRECT_FALLBACKS:
        target, confidence = DIRECT_FALLBACKS[family]
        return explicit_fallback(target, f"RC-BO-W-DIRECT-FALLBACK: {family}:{meta}", confidence=confidence)
    if family.startswith("machine.") or family in {"track", "signal"}:
        return BlockOnlyResult.fail(
            f"RC-BO-E-REQUIRES-BLOCK-ENTITY: {registry_name}:{meta}",
            warnings=["Railcraft machine/track/signal remains outside generic block-only"],
        )
    return explicit_fallback(PLACEHOLDER_BLOCK_ID, f"RC-BO-W-FALLBACK-UNKNOWN: {registry_name}:{meta}")
