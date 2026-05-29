"""Block-only converter for MrCrayfish Furniture 1.7.10 blocks."""

from __future__ import annotations

from converters.common.block_only import BlockOnlyResult, Position, explicit_fallback, normalize_metadata
from converters.common.placeholders import PLACEHOLDER_BLOCK_ID


LEGACY_DYE_TO_WOOL = {
    0: "minecraft:white_wool",
    1: "minecraft:orange_wool",
    2: "minecraft:magenta_wool",
    3: "minecraft:light_blue_wool",
    4: "minecraft:yellow_wool",
    5: "minecraft:lime_wool",
    6: "minecraft:pink_wool",
    7: "minecraft:gray_wool",
    8: "minecraft:light_gray_wool",
    9: "minecraft:cyan_wool",
    10: "minecraft:purple_wool",
    11: "minecraft:blue_wool",
    12: "minecraft:brown_wool",
    13: "minecraft:green_wool",
    14: "minecraft:red_wool",
    15: "minecraft:black_wool",
}

DIRECT_TARGETS = {
    "coffetablewood": ("minecraft:oak_slab", "medium"),
    "coffetablestone": ("minecraft:smooth_stone_slab", "medium"),
    "tablewood": ("minecraft:oak_planks", "low"),
    "tablestone": ("minecraft:smooth_stone", "low"),
    "chairwood": (PLACEHOLDER_BLOCK_ID, "low"),
    "chairstone": (PLACEHOLDER_BLOCK_ID, "low"),
    "cabinet": (PLACEHOLDER_BLOCK_ID, "low"),
    "bedsidecabinet": (PLACEHOLDER_BLOCK_ID, "low"),
    "blindon": (PLACEHOLDER_BLOCK_ID, "low"),
    "blindoff": (PLACEHOLDER_BLOCK_ID, "low"),
    "curtainon": ("minecraft:white_wool", "low"),
    "curtainoff": ("minecraft:white_wool", "low"),
    "birdbath": ("minecraft:cauldron", "low"),
    "whitefence": ("minecraft:white_wool", "low"),
    "tap": (PLACEHOLDER_BLOCK_ID, "low"),
    "mailbox": (PLACEHOLDER_BLOCK_ID, "low"),
    "electricfence": ("minecraft:iron_bars", "medium"),
    "doorbell": ("minecraft:stone_button", "medium"),
    "firealarmoff": ("minecraft:redstone_lamp", "low"),
    "firealarmon": ("minecraft:redstone_lamp", "low"),
    "ceilinglightoff": ("minecraft:lantern", "medium"),
    "ceilinglighton": ("minecraft:glowstone", "medium"),
    "toilet": (PLACEHOLDER_BLOCK_ID, "low"),
    "basin": (PLACEHOLDER_BLOCK_ID, "low"),
    "wallcabinet": (PLACEHOLDER_BLOCK_ID, "low"),
    "bath1": (PLACEHOLDER_BLOCK_ID, "low"),
    "bath2": (PLACEHOLDER_BLOCK_ID, "low"),
    "showerbottom": (PLACEHOLDER_BLOCK_ID, "low"),
    "showertop": (PLACEHOLDER_BLOCK_ID, "low"),
    "showerheadoff": (PLACEHOLDER_BLOCK_ID, "low"),
    "showerheadon": (PLACEHOLDER_BLOCK_ID, "low"),
    "bin": (PLACEHOLDER_BLOCK_ID, "low"),
    "tree": ("minecraft:oak_sapling", "low"),
    "cookiejar": (PLACEHOLDER_BLOCK_ID, "low"),
    "plate": (PLACEHOLDER_BLOCK_ID, "low"),
    "cup": (PLACEHOLDER_BLOCK_ID, "low"),
    "counterdoored": (PLACEHOLDER_BLOCK_ID, "low"),
    "countersink": (PLACEHOLDER_BLOCK_ID, "low"),
    "kitchencabinet": (PLACEHOLDER_BLOCK_ID, "low"),
    "choppingboard": (PLACEHOLDER_BLOCK_ID, "low"),
    "barstool": (PLACEHOLDER_BLOCK_ID, "low"),
    "hey": (PLACEHOLDER_BLOCK_ID, "low"),
    "nyan": (PLACEHOLDER_BLOCK_ID, "low"),
    "pattern": (PLACEHOLDER_BLOCK_ID, "low"),
    "yellowglow": ("minecraft:glowstone", "medium"),
    "whiteglass": ("minecraft:white_stained_glass", "high"),
    "stonepath": ("minecraft:stone_pressure_plate", "medium"),
}

EXPLICIT_REMOVALS = {
    "oven",
    "ovenoverhead",
    "microwave",
    "computer",
    "printer",
    "tv",
    "stereo",
    "washingmachine",
    "dishwasher",
    "toaster",
    "blender",
    "lampoff",
    "lampon",
}


def convert_block_only(
    numeric_id: int,
    registry_name: str,
    metadata: int,
    position: Position = (0, 0, 0),
) -> BlockOnlyResult:
    del numeric_id, position
    meta = normalize_metadata(metadata)
    name = _family(registry_name)
    if not registry_name.lower().startswith("cfm:"):
        return BlockOnlyResult.fail(f"CFM-BO-E-NOT-CFM: {registry_name}")

    if name == "couch" or name == "present":
        return explicit_fallback(
            LEGACY_DYE_TO_WOOL[meta],
            f"CFM-BO-W-COLORED-WOOL-FALLBACK: {name}:{meta}",
            confidence="medium",
        )
    if name == "hedge":
        target = {
            0: "minecraft:oak_leaves",
            1: "minecraft:spruce_leaves",
            2: "minecraft:birch_leaves",
            3: "minecraft:jungle_leaves",
        }.get(meta, "minecraft:oak_leaves")
        return explicit_fallback(target, f"CFM-BO-W-HEDGE-FALLBACK: meta={meta}", confidence="medium")
    if name in EXPLICIT_REMOVALS:
        return explicit_fallback(
            "minecraft:air",
            f"CFM-BO-W-EXPLICIT-REMOVAL: {name}",
            confidence="medium",
        )
    if name in DIRECT_TARGETS:
        target, confidence = DIRECT_TARGETS[name]
        warning = f"CFM-BO-W-TARGET-PACK-FALLBACK: {name} -> {target}"
        return explicit_fallback(target, warning, confidence=confidence)
    return explicit_fallback(
        PLACEHOLDER_BLOCK_ID,
        f"CFM-BO-W-FALLBACK-UNKNOWN: {registry_name}:{meta}",
    )


def _family(registry_name: str) -> str:
    return registry_name.split(":", 1)[1].lower() if ":" in registry_name else registry_name.lower()
