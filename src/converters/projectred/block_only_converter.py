"""Block-only converter for ProjectRed Exploration blocks."""

from __future__ import annotations

from converters.common.block_only import BlockOnlyResult, Position, explicit_fallback, normalize_metadata
from converters.projectred.mappings.block_mappings import get_block_mapping


STONE_WALLS = {
    0: "minecraft:stone_brick_wall",
    1: "minecraft:stone_brick_wall",
    2: "minecraft:blackstone_wall",
    3: "minecraft:blackstone_wall",
    4: "minecraft:polished_blackstone_brick_wall",
}


def convert_block_only(
    numeric_id: int,
    registry_name: str,
    metadata: int,
    position: Position = (0, 0, 0),
) -> BlockOnlyResult:
    del numeric_id, position
    meta = normalize_metadata(metadata)
    if not registry_name.startswith("ProjRed|"):
        return BlockOnlyResult.fail(f"PR-BO-E-NOT-PROJECTRED: {registry_name}")

    if "projectred.exploration.stonewalls" in registry_name:
        return explicit_fallback(
            STONE_WALLS.get(meta, "minecraft:stone_brick_wall"),
            f"PR-BO-W-WALL-FALLBACK: meta={meta}",
            confidence="medium" if meta in STONE_WALLS else "low",
        )
    if "projectred.exploration.lily" in registry_name:
        return explicit_fallback(
            "minecraft:lily_pad",
            f"PR-BO-W-LILY-REMOVED-FALLBACK: meta={meta}",
            confidence="low",
        )

    mapping = get_block_mapping(registry_name, meta)
    if mapping is None:
        return explicit_fallback("minecraft:stone", f"PR-BO-W-FALLBACK-UNKNOWN: {registry_name}:{meta}")
    if mapping.has_block_entity:
        return BlockOnlyResult.fail(
            f"PR-BO-E-REQUIRES-BLOCK-ENTITY: {registry_name}:{meta}",
            warnings=["block is TE/multipart or functional ProjectRed block"],
        )
    confidence = "high" if "exploration" in registry_name else "medium"
    warnings = [f"PR-BO-W-MAPPED: {mapping.notes}"] if mapping.notes else []
    return BlockOnlyResult.ok(mapping.id_1182, confidence=confidence, warnings=warnings)
