"""Block-only converter for Reliquary simple blocks."""

from __future__ import annotations

from converters.common.block_only import BlockOnlyResult, Position, explicit_fallback, normalize_metadata
from converters.common.placeholders import PLACEHOLDER_BLOCK_ID


DIRECT = {
    "lilypad": "reliquary:fertile_lily_pad",
    "interdiction_torch": "reliquary:interdiction_torch",
    "wraith_node": "reliquary:wraith_node",
}


def convert_block_only(
    numeric_id: int,
    registry_name: str,
    metadata: int,
    position: Position = (0, 0, 0),
) -> BlockOnlyResult:
    del numeric_id, position
    meta = normalize_metadata(metadata)
    if not registry_name.startswith("xreliquary:"):
        return BlockOnlyResult.fail(f"REL-BO-E-NOT-RELIQUARY: {registry_name}")
    name = registry_name.split(":", 1)[1]
    if name in DIRECT:
        warnings = [f"REL-BO-W-UNEXPECTED-META: {meta}"] if meta else []
        return BlockOnlyResult.ok(DIRECT[name], confidence="high" if not warnings else "medium", warnings=warnings)
    return BlockOnlyResult.fail(
        f"REL-BO-E-REQUIRES-BLOCK-ENTITY: {registry_name}:{meta}",
        target_block=PLACEHOLDER_BLOCK_ID,
        warnings=["Reliquary altar/cauldron/mortar are TE-owned"],
    )
