"""Block-only converter for Traincraft simple non-rail blocks."""

from __future__ import annotations

from converters.common.block_only import BlockOnlyResult, Position, explicit_fallback, normalize_metadata
from converters.common.placeholders import PLACEHOLDER_BLOCK_ID


DIRECT = {
    "tc:stopper": ("minecraft:oak_fence", "medium"),
    "tc:oreTC": ("minecraft:iron_ore", "low"),
    "tc:waterWheel": (PLACEHOLDER_BLOCK_ID, "low"),
    "tc:windMill": (PLACEHOLDER_BLOCK_ID, "low"),
    "tc:fluid.diesel": (PLACEHOLDER_BLOCK_ID, "low"),
    "tc:fluid.refinedfuel": (PLACEHOLDER_BLOCK_ID, "low"),
}
ORPHAN_ONLY = {
    "tc:lantern": ("minecraft:lantern", "low"),
    "tc:bridgePillar": ("minecraft:oak_log", "low"),
}


def convert_block_only(
    numeric_id: int,
    registry_name: str,
    metadata: int,
    position: Position = (0, 0, 0),
) -> BlockOnlyResult:
    del numeric_id, position
    meta = normalize_metadata(metadata)
    if not registry_name.startswith("tc:"):
        return BlockOnlyResult.fail(f"TC-BO-E-NOT-TRAINCRAFT: {registry_name}")
    if registry_name in DIRECT:
        target, confidence = DIRECT[registry_name]
        return explicit_fallback(target, f"TC-BO-W-DIRECT-FALLBACK: {registry_name}:{meta}", confidence=confidence)
    if registry_name in ORPHAN_ONLY:
        target, confidence = ORPHAN_ONLY[registry_name]
        return explicit_fallback(
            target,
            f"TC-BO-W-ORPHAN-ONLY-FALLBACK-NO-TE-PRESENT: {registry_name}:{meta}",
            confidence=confidence,
        )
    return BlockOnlyResult.fail(
        f"TC-BO-E-REQUIRES-BLOCK-ENTITY: {registry_name}:{meta}",
        warnings=["Traincraft rails/machines are handled by TE/track converter"],
    )
