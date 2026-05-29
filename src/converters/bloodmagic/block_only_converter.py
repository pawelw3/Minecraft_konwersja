"""Blood Magic block-only converter.

Converts runes, ritual stones and decorative blocks without TileEntity
from Blood Magic 1.7.10 to 1.18.2.
"""

from __future__ import annotations

from converters.common.block_only import BlockOnlyResult, normalize_metadata
from converters.bloodmagic.block_only_mappings import (
    BLOOD_RUNE_META_MAP,
    SEPARATE_RUNE_MAP,
    RITUAL_STONE_META_MAP,
    DIRECT_BLOCK_MAP,
    RUNE_FALLBACK,
    RITUAL_STONE_FALLBACK,
)


def convert_block_only(
    numeric_id: int,
    registry_name: str,
    metadata: int,
    position: tuple[int, int, int],
) -> BlockOnlyResult:
    """Convert a Blood Magic block without TE to 1.18.2.

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

    # Direct block mappings
    direct = DIRECT_BLOCK_MAP.get(reg)
    if direct:
        target, confidence, warning = direct
        warnings = [warning] if warning else []
        return BlockOnlyResult.ok(
            target,
            confidence=confidence,
            warnings=warnings,
        )

    # BloodRune (metadata-based)
    if reg == "awwayoftime:bloodrune":
        target = BLOOD_RUNE_META_MAP.get(meta)
        if target:
            return BlockOnlyResult.ok(
                target,
                confidence="high",
                warnings=[],
            )
        return BlockOnlyResult.ok(
            RUNE_FALLBACK,
            confidence="low",
            warnings=[f"Unknown BloodRune metadata {meta}, fallback to blank_rune"],
        )

    # Separate rune blocks (no metadata)
    separate = SEPARATE_RUNE_MAP.get(reg)
    if separate:
        return BlockOnlyResult.ok(
            separate,
            confidence="high",
            warnings=[],
        )

    # Ritual Stone (metadata-based)
    if reg == "awwayoftime:ritualstone":
        target = RITUAL_STONE_META_MAP.get(meta)
        if target:
            return BlockOnlyResult.ok(
                target,
                confidence="medium",
                warnings=["RitualStone variant mapping requires verification in 1.18.2 blockstates"],
            )
        return BlockOnlyResult.ok(
            RITUAL_STONE_FALLBACK,
            confidence="low",
            warnings=[f"Unknown RitualStone metadata {meta}, fallback to ritual_stone"],
        )

    return BlockOnlyResult.fail(
        f"Unknown BloodMagic block-only registry: {registry_name}",
        confidence="low",
        warnings=["Block fell through to default fallback"],
    )
