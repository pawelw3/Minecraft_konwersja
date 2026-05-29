"""Blood Magic block-only mappings for 1.7.10 -> 1.18.2.

Maps runes, ritual stones, decorative blocks without TileEntity.
"""

from __future__ import annotations

# BloodRune metadata -> target rune block in 1.18.2
BLOOD_RUNE_META_MAP: dict[int, str] = {
    0: "bloodmagic:blank_rune",
    1: "bloodmagic:dislocation_rune",
    2: "bloodmagic:capacity_rune",
    3: "bloodmagic:better_capacity_rune",
    4: "bloodmagic:orb_rune",
    5: "bloodmagic:acceleration_rune",
}

# Separate rune blocks (no metadata)
SEPARATE_RUNE_MAP: dict[str, str] = {
    "awwayoftime:speedrune": "bloodmagic:speed_rune",
    "awwayoftime:efficiencyrune": "bloodmagic:efficiency_rune",
    "awwayoftime:runeofsacrifice": "bloodmagic:sacrifice_rune",
    "awwayoftime:runeofselfsacrifice": "bloodmagic:self_sacrifice_rune",
}

# Ritual Stone metadata -> target (if variants exist in 1.18.2 as separate blocks or blockstates)
# In 1.7.10 RitualStone had metadata for type (raw, fire, water, earth, air, dusk).
# In 1.18.2 these may be blockstates of ritual_stone or separate blocks.
RITUAL_STONE_META_MAP: dict[int, str] = {
    0: "bloodmagic:ritual_stone",
    1: "bloodmagic:fire_ritual_stone",
    2: "bloodmagic:water_ritual_stone",
    3: "bloodmagic:earth_ritual_stone",
    4: "bloodmagic:air_ritual_stone",
    5: "bloodmagic:dusk_ritual_stone",
}

# Direct 1:1 block mappings (registry -> target)
DIRECT_BLOCK_MAP: dict[str, tuple[str, str, str | None]] = {
    "awwayoftime:imperfectritualstone": ("bloodmagic:imperfect_ritual_stone", "high", None),
    "awwayoftime:bloodstonebrick": ("bloodmagic:bloodstone_brick", "high", None),
    "awwayoftime:largebloodstonebrick": ("bloodmagic:large_bloodstone_brick", "high", None),
    "awwayoftime:crystal": ("minecraft:amethyst_block", "low", "BloodMagic Crystal has no 1:1 equivalent; fallback to amethyst_block"),
    "awwayoftime:enchantmentglyph": ("bloodmagic:blank_rune", "low", "EnchantmentGlyph has no equivalent; fallback to blank_rune"),
    "awwayoftime:stabilityglyph": ("bloodmagic:blank_rune", "low", "StabilityGlyph has no equivalent; fallback to blank_rune"),
    "awwayoftime:bloodlight": ("minecraft:torch", "low", "BloodLightSource has no equivalent; fallback to torch"),
}

# Fallbacks
RUNE_FALLBACK = "bloodmagic:blank_rune"
RITUAL_STONE_FALLBACK = "bloodmagic:ritual_stone"
