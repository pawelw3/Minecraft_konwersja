"""Chisel block-only converter.

Converts decorative blocks without TileEntity from Chisel 1.7.10
to Rechiseled / Chipped / Vanilla 1.18.2.
"""

from __future__ import annotations

from converters.common.block_only import BlockOnlyResult, normalize_metadata
from converters.chisel.block_only_mappings import (
    RECHISELED_FAMILY_MAP,
    CATEGORY_FALLBACKS,
    GLOBAL_FALLBACK,
)


def _guess_category(registry_name: str) -> str | None:
    """Guess material category from registry name for fallback selection."""
    reg = registry_name.lower()
    if "glass_pane" in reg or "glasspane" in reg:
        return "glass_pane"
    if "glass" in reg:
        return "glass"
    if "wool" in reg:
        return "wool"
    if "concrete" in reg:
        return "concrete"
    if "terracotta" in reg:
        return "terracotta"
    if "cobble" in reg:
        return "cobble"
    if "brick" in reg:
        return "brick"
    if "log" in reg or "wood" in reg:
        return "wood"
    if "metal" in reg or "iron" in reg or "gold" in reg or "copper" in reg or "tin" in reg or "silver" in reg or "lead" in reg or "nickel" in reg or "platinum" in reg or "steel" in reg or "bronze" in reg or "electrum" in reg or "invar" in reg or "aluminum" in reg:
        return "metal"
    if "stone" in reg or "marble" in reg or "limestone" in reg or "basalt" in reg or "granite" in reg or "diorite" in reg or "andesite" in reg or "slate" in reg:
        return "stone"
    return None


def convert_block_only(
    numeric_id: int,
    registry_name: str,
    metadata: int,
    position: tuple[int, int, int],
) -> BlockOnlyResult:
    """Convert a Chisel block without TE to 1.18.2.

    Args:
        numeric_id: Legacy numeric block ID.
        registry_name: Lower-case registry name (e.g. "chisel:andesite").
        metadata: Block metadata 0-15 (variant index).
        position: (x, y, z) block position.

    Returns:
        BlockOnlyResult with target block and blockstate properties.
    """
    meta = normalize_metadata(metadata)
    reg = registry_name.lower()

    # Skip TE blocks explicitly
    if reg in ("chisel:autochisel", "chisel:present", "chisel:beacon"):
        return BlockOnlyResult.fail(
            f"Chisel block {registry_name} has TileEntity and must use TE workflow",
            confidence="high",
        )

    # Known Rechiseled family mapping
    family = RECHISELED_FAMILY_MAP.get(reg)
    if family:
        prefix, has_variant, confidence = family
        if has_variant:
            # Rechiseled often uses suffixes like _1, _2, etc.
            # We cap metadata to a reasonable variant index.
            variant_index = meta + 1
            target = f"{prefix}_{variant_index}"
        else:
            target = prefix
        return BlockOnlyResult.ok(
            target,
            confidence=confidence,
            warnings=[
                f"Chisel family '{reg}' mapped to Rechiseled pattern '{target}'. "
                f"Variant accuracy requires visual verification."
            ],
        )

    # Unknown family: try category fallback
    category = _guess_category(reg)
    if category:
        fallback = CATEGORY_FALLBACKS.get(category, GLOBAL_FALLBACK)
        return BlockOnlyResult.ok(
            fallback,
            confidence="low",
            warnings=[
                f"Unknown Chisel family '{reg}' (metadata {meta}). "
                f"Category fallback '{fallback}' used."
            ],
        )

    # Ultimate fallback
    return BlockOnlyResult.ok(
        GLOBAL_FALLBACK,
        confidence="low",
        warnings=[
            f"Unknown Chisel family '{reg}' (metadata {meta}). "
            f"Global fallback '{GLOBAL_FALLBACK}' used."
        ],
    )
