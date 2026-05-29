"""BuildCraft block-only converter.

Converts blocks without TileEntity from BuildCraft 1.7.10 to 1.18.2.
"""

from __future__ import annotations

from converters.common.block_only import BlockOnlyResult, normalize_metadata
from converters.buildcraft.block_only_mappings import BC_BLOCK_ONLY_MAP


def convert_block_only(
    numeric_id: int,
    registry_name: str,
    metadata: int,
    position: tuple[int, int, int],
) -> BlockOnlyResult:
    """Convert a BuildCraft block without TE to 1.18.2.

    Args:
        numeric_id: Legacy numeric block ID.
        registry_name: Lower-case registry name (BuildCraft uses pipes in names).
        metadata: Block metadata 0-15.
        position: (x, y, z) block position.

    Returns:
        BlockOnlyResult with target block and blockstate properties.
    """
    meta = normalize_metadata(metadata)
    reg = registry_name.lower()

    mapping = BC_BLOCK_ONLY_MAP.get(reg)
    if mapping:
        target, confidence, warning = mapping
        warnings = [warning] if warning else []
        return BlockOnlyResult.ok(
            target,
            confidence=confidence,
            warnings=warnings,
        )

    return BlockOnlyResult.fail(
        f"Unknown BuildCraft block-only registry: {registry_name}",
        confidence="low",
        warnings=["Block fell through to default fallback"],
    )
