"""Block-only converter for Extra Utilities 1.7.10 blocks."""

from __future__ import annotations

from converters.common.block_only import BlockOnlyResult, Position, explicit_fallback, normalize_metadata
from converters.extrautils.mappings.block_mappings import get_mapping, is_extrautils_block


LEGACY_DYE_TO_CONCRETE = {
    0: "minecraft:black_concrete",
    1: "minecraft:red_concrete",
    2: "minecraft:green_concrete",
    3: "minecraft:brown_concrete",
    4: "minecraft:blue_concrete",
    5: "minecraft:purple_concrete",
    6: "minecraft:cyan_concrete",
    7: "minecraft:light_gray_concrete",
    8: "minecraft:gray_concrete",
    9: "minecraft:pink_concrete",
    10: "minecraft:lime_concrete",
    11: "minecraft:yellow_concrete",
    12: "minecraft:light_blue_concrete",
    13: "minecraft:magenta_concrete",
    14: "minecraft:orange_concrete",
    15: "minecraft:white_concrete",
}

COLORED_FAMILIES = {
    "colorStoneBrick",
    "colorWoodPlanks",
    "color_lightgem",
    "color_stone",
    "color_quartzBlock",
    "color_hellsand",
    "color_redstoneLight",
    "color_blockLapis",
    "color_obsidian",
    "color_blockRedstone",
    "color_blockCoal",
    "color_brick",
    "color_stonebrick",
}

DIRECT_FALLBACKS = {
    "decorativeBlock1": "minecraft:stone",
    "decorativeBlock2": "minecraft:stone",
    "block_bedrockium": "minecraft:netherite_block",
    "cobblestone_compressed": "minecraft:cobblestone",
    "conveyor": "minecraft:black_concrete",
    "greenscreen": "minecraft:lime_concrete",
    "spike_base": "minecraft:iron_bars",
    "spike_base_diamond": "minecraft:iron_bars",
    "spike_base_gold": "minecraft:iron_bars",
    "spike_base_wood": "minecraft:oak_fence",
    "etherealglass": "minecraft:glass",
}


def convert_block_only(
    numeric_id: int,
    registry_name: str,
    metadata: int,
    position: Position = (0, 0, 0),
) -> BlockOnlyResult:
    del numeric_id, position
    meta = normalize_metadata(metadata)
    if not is_extrautils_block(registry_name):
        return BlockOnlyResult.fail(f"EXU-BO-E-NOT-EXTRAUTILS: {registry_name}")

    mapping = get_mapping(registry_name, meta)
    if mapping is not None:
        if mapping.nbt_converter:
            return BlockOnlyResult.fail(
                f"EXU-BO-E-REQUIRES-BLOCK-ENTITY: {registry_name}:{meta}",
                warnings=["block has functional NBT converter and is outside block-only"],
            )
        return BlockOnlyResult.ok(
            mapping.target_block_id,
            confidence="high",
            warnings=[f"EXU-BO-W-MAPPED: {mapping.notes}"] if mapping.notes else [],
        )

    family = _family(registry_name)
    if family in COLORED_FAMILIES:
        return explicit_fallback(
            LEGACY_DYE_TO_CONCRETE[meta],
            f"EXU-BO-W-COLORED-FAMILY-FALLBACK: {family}:{meta}",
            confidence="medium",
        )
    if family in DIRECT_FALLBACKS:
        return explicit_fallback(
            DIRECT_FALLBACKS[family],
            f"EXU-BO-W-DIRECT-FALLBACK: {family}:{meta}",
        )
    return explicit_fallback(
        "minecraft:stone",
        f"EXU-BO-W-FALLBACK-UNKNOWN: {registry_name}:{meta}",
    )


def _family(registry_name: str) -> str:
    return registry_name.split(":", 1)[1] if ":" in registry_name else registry_name
