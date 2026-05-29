"""Block-only converter for IC2 1.7.10 simple blocks."""

from __future__ import annotations

from converters.common.block_only import BlockOnlyResult, Position, explicit_fallback, normalize_metadata
from converters.ic2.mappings.block_mappings import CABLE, get_block_mapping, is_ic2_block


ALLOW_EMPTY_BE_TARGETS = {CABLE}


def convert_block_only(
    numeric_id: int,
    registry_name: str,
    metadata: int,
    position: Position = (0, 0, 0),
) -> BlockOnlyResult:
    del numeric_id, position
    meta = normalize_metadata(metadata)
    if not is_ic2_block(registry_name):
        return BlockOnlyResult.fail(f"IC2-BO-E-NOT-IC2: {registry_name}")

    mapping = get_block_mapping(registry_name, meta) or get_block_mapping(registry_name, 0)
    if mapping is None:
        return explicit_fallback(
            "minecraft:stone",
            f"IC2-BO-W-FALLBACK-UNKNOWN: {registry_name}:{meta}",
        )

    if mapping.has_block_entity and registry_name not in ALLOW_EMPTY_BE_TARGETS:
        return BlockOnlyResult.fail(
            f"IC2-BO-E-REQUIRES-BLOCK-ENTITY: {registry_name}:{meta}",
            warnings=["block must be handled by IC2 TE/NBT converter"],
        )

    warnings = []
    confidence = "high" if not mapping.notes else "medium"
    if mapping.notes:
        warnings.append(f"IC2-BO-W-LOSSY: {mapping.notes}")
    if registry_name in ALLOW_EMPTY_BE_TARGETS:
        warnings.append("IC2-BO-W-CABLE-BLOCKSTATE-ONLY: target may create empty cable BE")
        confidence = "medium"
    return BlockOnlyResult.ok(
        mapping.target_block_id,
        blockstate_props=dict(mapping.blockstate_props or {}),
        confidence=confidence,
        warnings=warnings,
    )
