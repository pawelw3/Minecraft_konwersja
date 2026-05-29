"""BuildCraft block-only mappings for 1.7.10 -> 1.18.2.

Only a handful of BuildCraft blocks lack TileEntity.
"""

from __future__ import annotations

# Registry name (lower-case) -> (target_block, confidence, warning_or_none)
BC_BLOCK_ONLY_MAP: dict[str, tuple[str, str, str | None]] = {
    "buildcraft|builders:blockframe": ("minecraft:iron_bars", "low", "BuildCraft Frame has no 1:1 equivalent"),
    "buildcraft|builders:frameblock": ("minecraft:iron_bars", "low", "BuildCraft Frame has no 1:1 equivalent"),
    "buildcraft|core:spring": ("minecraft:water", "low", "BuildCraft Spring lost infinite-source behaviour"),
    "buildcraft|core:blockbuildtool": ("minecraft:air", "high", None),
    "buildcraft|factory:blockplainpipe": ("minecraft:iron_bars", "low", "BuildCraft PlainPipe has no equivalent"),
}
