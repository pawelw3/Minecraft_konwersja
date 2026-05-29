"""AE2 block-only converter.

Converts decorative blocks without TileEntity from AE2 1.7.10 to 1.18.2.
"""

from __future__ import annotations

from converters.common.block_only import BlockOnlyResult, normalize_metadata
from converters.ae2.block_only_mappings import (
    AE2_BLOCK_ONLY_MAP,
    AE2_STAIRS_MAP,
    QUARTZ_PILLAR_AXIS_MAP,
    SKY_STONE_VARIANT_MAP,
    ORE_FALLBACK,
    ORE_DEEPSLATE,
)


def convert_block_only(
    numeric_id: int,
    registry_name: str,
    metadata: int,
    position: tuple[int, int, int],
) -> BlockOnlyResult:
    """Convert an AE2 block without TE to 1.18.2.

    Args:
        numeric_id: Legacy numeric block ID.
        registry_name: Lower-case registry name.
        metadata: Block metadata 0-15.
        position: (x, y, z) block position.

    Returns:
        BlockOnlyResult with target block and blockstate properties.
    """
    meta = normalize_metadata(metadata)
    reg = registry_name.lower()

    # Special handling FIRST (before direct map) for metadata-dependent blocks
    # Sky Stone variants via metadata
    if reg == "appliedenergistics2:tile.blockskystone":
        target = SKY_STONE_VARIANT_MAP.get(meta)
        if target:
            return BlockOnlyResult.ok(
                target,
                confidence="high",
                warnings=[],
            )
        return BlockOnlyResult.ok(
            "ae2:sky_stone_block",
            confidence="low",
            warnings=[f"Unknown Sky Stone metadata {meta}, fallback to sky_stone_block"],
        )

    # Certus Quartz Ore (deepslate check)
    if reg == "appliedenergistics2:tile.orequartz":
        _, y, _ = position
        target = ORE_DEEPSLATE if y < 0 else ORE_FALLBACK
        return BlockOnlyResult.ok(
            target,
            confidence="high",
            warnings=[],
        )

    # Quartz Pillar (special axis handling)
    if reg == "appliedenergistics2:tile.blockquartzpillar":
        axis = QUARTZ_PILLAR_AXIS_MAP.get(meta, "y")
        return BlockOnlyResult.ok(
            "ae2:quartz_pillar",
            blockstate_props={"axis": axis},
            confidence="high",
            warnings=[],
        )

    # Stairs mapping
    stair_target = AE2_STAIRS_MAP.get(reg)
    if stair_target:
        # In 1.7.10 stair metadata 0-7 stores facing/half/shape in a packed format.
        # For block-only we pass it through as blockstate props and let the writer
        # decode it using vanilla stair rules.
        return BlockOnlyResult.ok(
            stair_target,
            blockstate_props={"legacy_meta": str(meta)},
            confidence="high",
            warnings=["Stair orientation encoded in legacy_meta; decode via vanilla stair rules"],
        )

    # Direct solid block mapping (for blocks that do NOT vary by metadata)
    mapping = AE2_BLOCK_ONLY_MAP.get(reg)
    if mapping:
        target, confidence, warning = mapping
        warnings = [warning] if warning else []
        return BlockOnlyResult.ok(
            target,
            confidence=confidence,
            warnings=warnings,
        )

    return BlockOnlyResult.fail(
        f"Unknown AE2 block-only registry: {registry_name}",
        confidence="low",
        warnings=["Block fell through to default fallback"],
    )
