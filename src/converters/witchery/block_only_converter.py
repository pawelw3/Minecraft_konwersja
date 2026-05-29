"""Block-only converter for Witchery simple blocks."""

from __future__ import annotations

from converters.common.block_only import BlockOnlyResult, Position, explicit_fallback, normalize_metadata
from converters.common.placeholders import PLACEHOLDER_BLOCK_ID


CROP_FALLBACKS = {
    "belladonna": "minecraft:poppy",
    "mandrake": "minecraft:dandelion",
    "artichoke": "minecraft:wheat",
    "snowbell": "minecraft:snow",
    "wormwood": "minecraft:fern",
    "mindrake": "minecraft:dandelion",
    "wolfsbane": "minecraft:blue_orchid",
    "garlicplant": "minecraft:wheat",
}
DIRECT = {
    "spanishmoss": ("minecraft:vine", "medium"),
    "leapinglily": ("minecraft:lily_pad", "medium"),
    "alderwooddoor": ("minecraft:oak_door", "medium"),
    "shadedglass": ("minecraft:tinted_glass", "medium"),
    "witchwoodslab": ("minecraft:oak_slab", "medium"),
    "rowanwooddoor": ("minecraft:oak_door", "medium"),
    "daylightcollector": ("minecraft:daylight_detector", "medium"),
    "stairswoodrowan": ("minecraft:oak_stairs", "medium"),
    "stockade": ("minecraft:oak_fence", "medium"),
    "bramble": ("minecraft:sweet_berry_bush", "medium"),
    "pitdirt": ("minecraft:dirt", "medium"),
    "witchsapling": ("minecraft:oak_sapling", "medium"),
    "witchleaves": ("minecraft:oak_leaves", "medium"),
    "wickerbundle": ("minecraft:hay_block", "medium"),
    "tormentstone": ("minecraft:blackstone", "medium"),
    "stairswoodalder": ("minecraft:oak_stairs", "medium"),
    "stairswoodhawthorn": ("minecraft:oak_stairs", "medium"),
    "bloodedwool": ("minecraft:red_wool", "medium"),
    "shadedglass_active": ("minecraft:tinted_glass", "medium"),
    "perpetualice": ("minecraft:blue_ice", "medium"),
    "pitgrass": ("minecraft:grass_block", "medium"),
    "lilypad": ("minecraft:lily_pad", "high"),
    "witchlog": ("minecraft:oak_log", "medium"),
    "witchwood": ("minecraft:oak_planks", "low"),
}
PLACEHOLDER = {
    "force",
    "embermoss",
    "disease",
    "circleglyphinfernal",
    "infinityegg",
    "circleglyphotherwhere",
    "spiritflowing",
    "glintweed",
    "icestockade",
    "circleglyphritual",
    "crittersnare",
    "wallgen",
    "mirrorwall",
    "demonheart",
    "plantmine",
    "brew",
    "hollowtears",
}


def convert_block_only(
    numeric_id: int,
    registry_name: str,
    metadata: int,
    position: Position = (0, 0, 0),
) -> BlockOnlyResult:
    del numeric_id, position
    meta = normalize_metadata(metadata)
    if not registry_name.startswith("witchery:"):
        return BlockOnlyResult.fail(f"WIT-BO-E-NOT-WITCHERY: {registry_name}")
    name = registry_name.split(":", 1)[1].lower()
    if name in CROP_FALLBACKS:
        return explicit_fallback(
            CROP_FALLBACKS[name],
            f"WIT-BO-W-CROP-FALLBACK: {name}:age_meta={meta}",
            confidence="low",
        )
    if name in DIRECT:
        target, confidence = DIRECT[name]
        return explicit_fallback(target, f"WIT-BO-W-VANILLA-FALLBACK: {name}:{meta}", confidence=confidence)
    if name in PLACEHOLDER:
        return explicit_fallback(PLACEHOLDER_BLOCK_ID, f"WIT-BO-W-PLACEHOLDER-FALLBACK: {name}:{meta}")
    return BlockOnlyResult.fail(
        f"WIT-BO-E-REQUIRES-BLOCK-ENTITY: {registry_name}:{meta}",
        warnings=["Witchery functional/decorative TE remains placeholder/NBT converter scope"],
    )
