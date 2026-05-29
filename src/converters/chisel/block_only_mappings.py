"""Chisel block-only mappings for 1.7.10 -> 1.18.2.

Chisel has 223+ families and ~2600+ variants. Full per-variant mapping
requires texture-level matching. This module provides family-level
fallbacks and explicit mappings for the most common families.
"""

from __future__ import annotations

# Families where Rechiseled has a close counterpart.
# Format: registry_name -> (target_prefix, has_variant_suffix, confidence)
# If has_variant_suffix is True, metadata is appended as suffix index.
RECHISELED_FAMILY_MAP: dict[str, tuple[str, bool, str]] = {
    # Stones with high confidence direct families
    "chisel:andesite": ("rechiseled:andesite", True, "high"),
    "chisel:basalt": ("rechiseled:basalt", True, "high"),
    "chisel:diorite": ("rechiseled:diorite", True, "high"),
    "chisel:granite": ("rechiseled:granite", True, "high"),
    "chisel:cobblestone": ("rechiseled:cobblestone", True, "medium"),
    "chisel:stonebrick": ("rechiseled:stone_bricks", True, "medium"),
    "chisel:sandstone": ("rechiseled:sandstone", True, "medium"),
    "chisel:endstone": ("rechiseled:end_stone", True, "medium"),
    "chisel:obsidian": ("rechiseled:obsidian", True, "medium"),
    "chisel:dirt": ("rechiseled:dirt", True, "medium"),
    "chisel:ice": ("rechiseled:ice", True, "medium"),
    "chisel:quartz": ("rechiseled:quartz_block", True, "medium"),
    "chisel:purpur": ("rechiseled:purpur_block", True, "medium"),
    "chisel:prismarine": ("rechiseled:prismarine", True, "medium"),
    "chisel:prismarine_bricks": ("rechiseled:prismarine_bricks", True, "medium"),
    "chisel:dark_prismarine": ("rechiseled:dark_prismarine", True, "medium"),
    "chisel:nether_bricks": ("rechiseled:nether_bricks", True, "medium"),
    "chisel:red_nether_bricks": ("rechiseled:red_nether_bricks", True, "medium"),
    "chisel:coal": ("rechiseled:coal_block", True, "medium"),
    "chisel:lapis": ("rechiseled:lapis_block", True, "medium"),
    "chisel:redstone": ("rechiseled:redstone_block", True, "medium"),
    "chisel:iron": ("rechiseled:iron_block", True, "medium"),
    "chisel:gold": ("rechiseled:gold_block", True, "medium"),
    "chisel:diamond": ("rechiseled:diamond_block", True, "medium"),
    "chisel:emerald": ("rechiseled:emerald_block", True, "medium"),
    "chisel:netherite": ("rechiseled:netherite_block", True, "medium"),
    "chisel:amethyst": ("rechiseled:amethyst_block", True, "medium"),
    # Woods
    "chisel:oak": ("rechiseled:oak", True, "medium"),
    "chisel:spruce": ("rechiseled:spruce", True, "medium"),
    "chisel:birch": ("rechiseled:birch", True, "medium"),
    "chisel:jungle": ("rechiseled:jungle", True, "medium"),
    "chisel:acacia": ("rechiseled:acacia", True, "medium"),
    "chisel:dark_oak": ("rechiseled:dark_oak", True, "medium"),
}

# Fallback per material category when family is unknown but material can be guessed.
CATEGORY_FALLBACKS: dict[str, str] = {
    "stone": "minecraft:stone",
    "cobble": "minecraft:cobblestone",
    "brick": "minecraft:stone_bricks",
    "wood": "minecraft:oak_planks",
    "log": "minecraft:oak_log",
    "metal": "minecraft:iron_block",
    "glass": "minecraft:glass",
    "glass_pane": "minecraft:glass_pane",
    "wool": "minecraft:white_wool",
    "concrete": "minecraft:white_concrete",
    "terracotta": "minecraft:terracotta",
}

# Global fallback when nothing matches
GLOBAL_FALLBACK = "minecraft:stone"
