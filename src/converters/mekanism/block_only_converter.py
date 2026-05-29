"""Block-only converter for Mekanism 1.7.10 blocks without TileEntity."""

from __future__ import annotations

from converters.common.block_only import BlockOnlyResult, Position, explicit_fallback, normalize_metadata
from converters.mekanism.mappings import get_block_mapping, is_mekanism_block


def convert_block_only(
    numeric_id: int,
    registry_name: str,
    metadata: int,
    position: Position = (0, 0, 0),
) -> BlockOnlyResult:
    del numeric_id, position
    meta = normalize_metadata(metadata)
    if not is_mekanism_block(registry_name):
        return BlockOnlyResult.fail(f"MEK-BO-E-NOT-MEKANISM: {registry_name}")

    mapping = get_block_mapping(registry_name, meta)
    if mapping is None:
        return explicit_fallback(
            "minecraft:stone",
            f"MEK-BO-W-FALLBACK-UNKNOWN: {registry_name}:{meta}",
        )

    if mapping.has_block_entity:
        return BlockOnlyResult.fail(
            f"MEK-BO-E-REQUIRES-BLOCK-ENTITY: {registry_name}:{meta}",
            warnings=["block must be handled by Mekanism TE/NBT converter"],
        )

    warnings = []
    confidence = "high"
    if mapping.notes:
        warnings.append(f"MEK-BO-W-LOSSY: {mapping.notes}")
        confidence = "medium"
    return BlockOnlyResult.ok(
        mapping.target_block_id,
        blockstate_props={},
        confidence=confidence,
        warnings=warnings,
    )
