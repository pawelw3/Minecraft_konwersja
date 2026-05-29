"""BiblioCraft block-only converter.

Converts decorative blocks without TileEntity from BiblioCraft 1.7.10 to 1.18.2.
"""

from __future__ import annotations

from converters.common.block_only import BlockOnlyResult, normalize_metadata
from converters.bibliocraft.block_only_mappings import (
    SEAT_WOOD_MAP,
    SEAT_FALLBACK,
    REGISTRY_HANDLERS,
)


def convert_block_only(
    numeric_id: int,
    registry_name: str,
    metadata: int,
    position: tuple[int, int, int],
) -> BlockOnlyResult:
    """Convert a BiblioCraft block without TE to 1.18.2.

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

    handler = REGISTRY_HANDLERS.get(reg)

    if handler == "bell":
        return BlockOnlyResult.ok(
            "minecraft:bell",
            confidence="medium",
            warnings=["BiblioCraft Bell mapped to vanilla bell; redstone sound behaviour differs"],
        )

    if handler == "seat":
        target = SEAT_WOOD_MAP.get(meta, SEAT_FALLBACK)
        if meta not in SEAT_WOOD_MAP:
            return BlockOnlyResult.ok(
                target,
                confidence="low",
                warnings=[f"Unknown BiblioCraft Seat wood type metadata {meta}, fallback to oak_stairs"],
            )
        return BlockOnlyResult.ok(
            target,
            confidence="medium",
            warnings=["BiblioCraft Seat mapped to vanilla stairs; sitting functionality lost"],
        )

    if handler == "mapframe":
        return BlockOnlyResult.ok(
            "supplementaries:frame",
            confidence="medium",
            warnings=["BiblioCraft MapFrame mapped to Supplementaries frame; verify map display"],
        )

    return BlockOnlyResult.fail(
        f"Unknown BiblioCraft block-only registry: {registry_name}",
        confidence="low",
        warnings=["Block fell through to default fallback"],
    )
