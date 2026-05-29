"""Big Reactors block-only converter.

Converts blocks without TileEntity from Big Reactors 1.7.10 to Bigger Reactors 1.18.2.
"""

from __future__ import annotations

from converters.common.block_only import BlockOnlyResult, normalize_metadata
from converters.bigreactors.block_only_mappings import (
    BR_METAL_MAP,
    REGISTRY_HANDLERS,
    FALLBACK_METAL,
    ORE_TARGET,
    ORE_TARGET_DEEPSLATE,
)


def convert_block_only(
    numeric_id: int,
    registry_name: str,
    metadata: int,
    position: tuple[int, int, int],
) -> BlockOnlyResult:
    """Convert a Big Reactors block without TE to 1.18.2.

    Args:
        numeric_id: Legacy numeric block ID.
        registry_name: Lower-case registry name (e.g. "bigreactors:yelloriteore").
        metadata: Block metadata 0-15.
        position: (x, y, z) block position.

    Returns:
        BlockOnlyResult with target block and blockstate properties.
    """
    meta = normalize_metadata(metadata)
    reg = registry_name.lower()

    handler = REGISTRY_HANDLERS.get(reg)

    if handler == "ore":
        # Yellorite Ore -> Uranium Ore (deepslate if deep enough)
        _, y, _ = position
        target = ORE_TARGET_DEEPSLATE if y < 0 else ORE_TARGET
        return BlockOnlyResult.ok(
            target,
            confidence="high",
            warnings=[],
        )

    if handler == "metal":
        target = BR_METAL_MAP.get(meta)
        if target:
            return BlockOnlyResult.ok(
                target,
                confidence="high",
                warnings=[],
            )
        return BlockOnlyResult.ok(
            FALLBACK_METAL,
            confidence="low",
            warnings=[f"Unknown BRMetalBlock metadata {meta}, fallback to graphite_block"],
        )

    return BlockOnlyResult.fail(
        f"Unknown BigReactors block-only registry: {registry_name}",
        confidence="low",
        warnings=["Block fell through to default fallback"],
    )
