"""AE2 block-only mappings for 1.7.10 -> 1.18.2.

Maps decorative blocks without TileEntity.
"""

from __future__ import annotations

# Registry name -> (target_block, confidence, warning_or_none)
# These are direct 1:1 mappings for decorative AE2 blocks.
AE2_BLOCK_ONLY_MAP: dict[str, tuple[str, str, str | None]] = {
    # Solids / decorative
    "appliedenergistics2:tile.blockquartz": ("ae2:quartz_block", "high", None),
    "appliedenergistics2:tile.blockquartzchiseled": ("ae2:quartz_block", "high", "Chiseled quartz mapped to ae2:quartz_block; chiseled variant may need blockstate"),
    "appliedenergistics2:tile.blockquartzglass": ("ae2:quartz_glass", "high", None),
    "appliedenergistics2:tile.blockfluix": ("ae2:fluix_block", "high", None),
    "appliedenergistics2:tile.blockskystone": ("ae2:sky_stone_block", "high", None),
    "appliedenergistics2:tile.orequartz": ("ae2:quartz_ore", "high", None),
    "appliedenergistics2:tile.blocktinytnt": ("ae2:tiny_tnt", "high", None),
    "appliedenergistics2:tile.blockquartztorch": ("ae2:quartz_fixture", "medium", None),
    "appliedenergistics2:tile.blocklightdetector": ("ae2:light_detector", "medium", None),
    "appliedenergistics2:tile.blockmatrixframe": ("ae2:matrix_frame", "high", None),
    "appliedenergistics2:tile.blockpaint": ("ae2:paint", "low", "Paint splotches rarely occur on production maps"),
}

# Stairs: registry -> target block in 1.18.2
AE2_STAIRS_MAP: dict[str, str] = {
    "appliedenergistics2:tile.chiseledquartzstairs": "ae2:chiseled_quartz_stairs",
    "appliedenergistics2:tile.skystonestairs": "ae2:sky_stone_stairs",
    "appliedenergistics2:tile.skystonebrickstairs": "ae2:sky_stone_brick_stairs",
    "appliedenergistics2:tile.skystonesmallbrickstairs": "ae2:sky_stone_small_brick_stairs",
    "appliedenergistics2:tile.quartzstairs": "ae2:quartz_stairs",
    "appliedenergistics2:tile.skystoneblockstairs": "ae2:sky_stone_block_stairs",
    "appliedenergistics2:tile.quartzpillarstairs": "ae2:quartz_pillar_stairs",
    "appliedenergistics2:tile.fluixstairs": "ae2:fluix_stairs",
}

# BlockQuartzPillar metadata -> axis blockstate
QUARTZ_PILLAR_AXIS_MAP: dict[int, str] = {
    0: "y",
    1: "x",
    2: "z",
}

# Sky Stone metadata -> target block (1.7.10 had variants in metadata)
SKY_STONE_VARIANT_MAP: dict[int, str] = {
    0: "ae2:sky_stone_block",
    1: "ae2:smooth_sky_stone_block",
    2: "ae2:sky_stone_brick",
    3: "ae2:sky_stone_small_brick",
}

# Ore metadata -> stone vs deepslate (in 1.7.10 AE2 certus ore only had one variant)
ORE_FALLBACK = "ae2:quartz_ore"
ORE_DEEPSLATE = "ae2:deepslate_quartz_ore"
