"""
Mapowanie materiałów pokrycia CarpentersBlocks 1.7.10 -> 1.18.2.

Źródło prawdy: Minecraft 1.7.10 Forge block/item registry names + metadata
Cel: Minecraft 1.18.2 resource location strings

Format klucza: (cbUniqueId_1710, damage)
  cbUniqueId to string z GameRegistry.findUniqueIdentifierFor().toString()
  Przykłady: "minecraft:log", "CarpentersBlocks:blockCarpentersSlope"

Format wartości: string ResourceLocation 1.18.2
  Przykłady: "minecraft:oak_log", "minecraft:spruce_planks"

FALLBACK:
  Jeśli brak wpisu, próbujemy heurystycznie (brak damage → bezpośrednie mapowanie
  nazwy z :).  Ostatecznie zwracamy None.
"""

from __future__ import annotations

# -------------------------------------------------------------------
# Mapowanie (cbUniqueId, damage) -> 1.18.2 block ID
# -------------------------------------------------------------------

COVER_MATERIAL_MAP: dict[tuple[str, int], str] = {
    # --- Drewno: belki (log) ---
    ("minecraft:log", 0): "minecraft:oak_log",
    ("minecraft:log", 1): "minecraft:spruce_log",
    ("minecraft:log", 2): "minecraft:birch_log",
    ("minecraft:log", 3): "minecraft:jungle_log",
    # damage 4-7 = kora (bark all sides) - te same bloki
    ("minecraft:log", 4): "minecraft:oak_log",
    ("minecraft:log", 5): "minecraft:spruce_log",
    ("minecraft:log", 6): "minecraft:birch_log",
    ("minecraft:log", 7): "minecraft:jungle_log",
    ("minecraft:log2", 0): "minecraft:acacia_log",
    ("minecraft:log2", 1): "minecraft:dark_oak_log",
    ("minecraft:log2", 4): "minecraft:acacia_log",
    ("minecraft:log2", 5): "minecraft:dark_oak_log",

    # --- Deski (planks) ---
    ("minecraft:planks", 0): "minecraft:oak_planks",
    ("minecraft:planks", 1): "minecraft:spruce_planks",
    ("minecraft:planks", 2): "minecraft:birch_planks",
    ("minecraft:planks", 3): "minecraft:jungle_planks",
    ("minecraft:planks", 4): "minecraft:acacia_planks",
    ("minecraft:planks", 5): "minecraft:dark_oak_planks",

    # --- Kamień i warianty ---
    ("minecraft:stone", 0): "minecraft:stone",
    ("minecraft:stone", 1): "minecraft:granite",
    ("minecraft:stone", 2): "minecraft:polished_granite",
    ("minecraft:stone", 3): "minecraft:diorite",
    ("minecraft:stone", 4): "minecraft:polished_diorite",
    ("minecraft:stone", 5): "minecraft:andesite",
    ("minecraft:stone", 6): "minecraft:polished_andesite",
    ("minecraft:cobblestone", 0): "minecraft:cobblestone",
    ("minecraft:mossy_cobblestone", 0): "minecraft:mossy_cobblestone",

    # --- Ceglane ---
    ("minecraft:brick_block", 0): "minecraft:bricks",
    ("minecraft:brick", 0): "minecraft:bricks",           # alias
    ("minecraft:stonebrick", 0): "minecraft:stone_bricks",
    ("minecraft:stonebrick", 1): "minecraft:mossy_stone_bricks",
    ("minecraft:stonebrick", 2): "minecraft:cracked_stone_bricks",
    ("minecraft:stonebrick", 3): "minecraft:chiseled_stone_bricks",
    ("minecraft:netherbrick", 0): "minecraft:nether_bricks",
    ("minecraft:nether_brick", 0): "minecraft:nether_bricks",     # alias
    ("minecraft:red_nether_brick", 0): "minecraft:red_nether_bricks",

    # --- Ziemia i piasek ---
    ("minecraft:dirt", 0): "minecraft:dirt",
    ("minecraft:dirt", 1): "minecraft:coarse_dirt",
    ("minecraft:dirt", 2): "minecraft:podzol",
    ("minecraft:grass", 0): "minecraft:grass_block",
    ("minecraft:sand", 0): "minecraft:sand",
    ("minecraft:sand", 1): "minecraft:red_sand",
    ("minecraft:gravel", 0): "minecraft:gravel",
    ("minecraft:clay", 0): "minecraft:clay",

    # --- Piaskowiec ---
    ("minecraft:sandstone", 0): "minecraft:sandstone",
    ("minecraft:sandstone", 1): "minecraft:chiseled_sandstone",
    ("minecraft:sandstone", 2): "minecraft:cut_sandstone",
    ("minecraft:red_sandstone", 0): "minecraft:red_sandstone",
    ("minecraft:red_sandstone", 1): "minecraft:chiseled_red_sandstone",
    ("minecraft:red_sandstone", 2): "minecraft:cut_red_sandstone",

    # --- Liście ---
    ("minecraft:leaves", 0): "minecraft:oak_leaves",
    ("minecraft:leaves", 1): "minecraft:spruce_leaves",
    ("minecraft:leaves", 2): "minecraft:birch_leaves",
    ("minecraft:leaves", 3): "minecraft:jungle_leaves",
    ("minecraft:leaves", 4): "minecraft:oak_leaves",    # no-decay variant
    ("minecraft:leaves", 5): "minecraft:spruce_leaves",
    ("minecraft:leaves", 6): "minecraft:birch_leaves",
    ("minecraft:leaves", 7): "minecraft:jungle_leaves",
    ("minecraft:leaves2", 0): "minecraft:acacia_leaves",
    ("minecraft:leaves2", 1): "minecraft:dark_oak_leaves",
    ("minecraft:leaves2", 4): "minecraft:acacia_leaves",
    ("minecraft:leaves2", 5): "minecraft:dark_oak_leaves",

    # --- Wełna (wool) - 16 kolorów ---
    ("minecraft:wool", 0): "minecraft:white_wool",
    ("minecraft:wool", 1): "minecraft:orange_wool",
    ("minecraft:wool", 2): "minecraft:magenta_wool",
    ("minecraft:wool", 3): "minecraft:light_blue_wool",
    ("minecraft:wool", 4): "minecraft:yellow_wool",
    ("minecraft:wool", 5): "minecraft:lime_wool",
    ("minecraft:wool", 6): "minecraft:pink_wool",
    ("minecraft:wool", 7): "minecraft:gray_wool",
    ("minecraft:wool", 8): "minecraft:light_gray_wool",
    ("minecraft:wool", 9): "minecraft:cyan_wool",
    ("minecraft:wool", 10): "minecraft:purple_wool",
    ("minecraft:wool", 11): "minecraft:blue_wool",
    ("minecraft:wool", 12): "minecraft:brown_wool",
    ("minecraft:wool", 13): "minecraft:green_wool",
    ("minecraft:wool", 14): "minecraft:red_wool",
    ("minecraft:wool", 15): "minecraft:black_wool",

    # --- Szkło ---
    ("minecraft:glass", 0): "minecraft:glass",
    ("minecraft:glass_pane", 0): "minecraft:glass_pane",
    ("minecraft:stained_glass", 0): "minecraft:white_stained_glass",
    ("minecraft:stained_glass", 1): "minecraft:orange_stained_glass",
    ("minecraft:stained_glass", 2): "minecraft:magenta_stained_glass",
    ("minecraft:stained_glass", 3): "minecraft:light_blue_stained_glass",
    ("minecraft:stained_glass", 4): "minecraft:yellow_stained_glass",
    ("minecraft:stained_glass", 5): "minecraft:lime_stained_glass",
    ("minecraft:stained_glass", 6): "minecraft:pink_stained_glass",
    ("minecraft:stained_glass", 7): "minecraft:gray_stained_glass",
    ("minecraft:stained_glass", 8): "minecraft:light_gray_stained_glass",
    ("minecraft:stained_glass", 9): "minecraft:cyan_stained_glass",
    ("minecraft:stained_glass", 10): "minecraft:purple_stained_glass",
    ("minecraft:stained_glass", 11): "minecraft:blue_stained_glass",
    ("minecraft:stained_glass", 12): "minecraft:brown_stained_glass",
    ("minecraft:stained_glass", 13): "minecraft:green_stained_glass",
    ("minecraft:stained_glass", 14): "minecraft:red_stained_glass",
    ("minecraft:stained_glass", 15): "minecraft:black_stained_glass",
    ("minecraft:stained_glass_pane", 0): "minecraft:white_stained_glass_pane",
    ("minecraft:stained_glass_pane", 1): "minecraft:orange_stained_glass_pane",
    ("minecraft:stained_glass_pane", 2): "minecraft:magenta_stained_glass_pane",
    ("minecraft:stained_glass_pane", 3): "minecraft:light_blue_stained_glass_pane",
    ("minecraft:stained_glass_pane", 4): "minecraft:yellow_stained_glass_pane",
    ("minecraft:stained_glass_pane", 5): "minecraft:lime_stained_glass_pane",
    ("minecraft:stained_glass_pane", 6): "minecraft:pink_stained_glass_pane",
    ("minecraft:stained_glass_pane", 7): "minecraft:gray_stained_glass_pane",
    ("minecraft:stained_glass_pane", 8): "minecraft:light_gray_stained_glass_pane",
    ("minecraft:stained_glass_pane", 9): "minecraft:cyan_stained_glass_pane",
    ("minecraft:stained_glass_pane", 10): "minecraft:purple_stained_glass_pane",
    ("minecraft:stained_glass_pane", 11): "minecraft:blue_stained_glass_pane",
    ("minecraft:stained_glass_pane", 12): "minecraft:brown_stained_glass_pane",
    ("minecraft:stained_glass_pane", 13): "minecraft:green_stained_glass_pane",
    ("minecraft:stained_glass_pane", 14): "minecraft:red_stained_glass_pane",
    ("minecraft:stained_glass_pane", 15): "minecraft:black_stained_glass_pane",

    # --- Terakota (hardened clay) ---
    ("minecraft:hardened_clay", 0): "minecraft:terracotta",
    ("minecraft:stained_hardened_clay", 0): "minecraft:white_terracotta",
    ("minecraft:stained_hardened_clay", 1): "minecraft:orange_terracotta",
    ("minecraft:stained_hardened_clay", 2): "minecraft:magenta_terracotta",
    ("minecraft:stained_hardened_clay", 3): "minecraft:light_blue_terracotta",
    ("minecraft:stained_hardened_clay", 4): "minecraft:yellow_terracotta",
    ("minecraft:stained_hardened_clay", 5): "minecraft:lime_terracotta",
    ("minecraft:stained_hardened_clay", 6): "minecraft:pink_terracotta",
    ("minecraft:stained_hardened_clay", 7): "minecraft:gray_terracotta",
    ("minecraft:stained_hardened_clay", 8): "minecraft:light_gray_terracotta",
    ("minecraft:stained_hardened_clay", 9): "minecraft:cyan_terracotta",
    ("minecraft:stained_hardened_clay", 10): "minecraft:purple_terracotta",
    ("minecraft:stained_hardened_clay", 11): "minecraft:blue_terracotta",
    ("minecraft:stained_hardened_clay", 12): "minecraft:brown_terracotta",
    ("minecraft:stained_hardened_clay", 13): "minecraft:green_terracotta",
    ("minecraft:stained_hardened_clay", 14): "minecraft:red_terracotta",
    ("minecraft:stained_hardened_clay", 15): "minecraft:black_terracotta",

    # --- Kwarc ---
    ("minecraft:quartz_block", 0): "minecraft:quartz_block",
    ("minecraft:quartz_block", 1): "minecraft:chiseled_quartz_block",
    ("minecraft:quartz_block", 2): "minecraft:quartz_pillar",

    # --- Mur (wall) ---
    ("minecraft:cobblestone_wall", 0): "minecraft:cobblestone_wall",
    ("minecraft:cobblestone_wall", 1): "minecraft:mossy_cobblestone_wall",

    # --- Płyty (slab) - pełne warianty ---
    ("minecraft:stone_slab", 0): "minecraft:smooth_stone_slab",
    ("minecraft:stone_slab", 1): "minecraft:sandstone_slab",
    ("minecraft:stone_slab", 2): "minecraft:petrified_oak_slab",
    ("minecraft:stone_slab", 3): "minecraft:cobblestone_slab",
    ("minecraft:stone_slab", 4): "minecraft:brick_slab",
    ("minecraft:stone_slab", 5): "minecraft:stone_brick_slab",
    ("minecraft:stone_slab", 6): "minecraft:nether_brick_slab",
    ("minecraft:stone_slab", 7): "minecraft:quartz_slab",
    ("minecraft:double_stone_slab", 0): "minecraft:smooth_stone",
    ("minecraft:double_stone_slab", 1): "minecraft:sandstone",
    ("minecraft:double_stone_slab", 3): "minecraft:cobblestone",
    ("minecraft:double_stone_slab", 4): "minecraft:bricks",
    ("minecraft:double_stone_slab", 5): "minecraft:stone_bricks",
    ("minecraft:double_stone_slab", 6): "minecraft:nether_bricks",
    ("minecraft:double_stone_slab", 7): "minecraft:quartz_block",
    ("minecraft:wooden_slab", 0): "minecraft:oak_slab",
    ("minecraft:wooden_slab", 1): "minecraft:spruce_slab",
    ("minecraft:wooden_slab", 2): "minecraft:birch_slab",
    ("minecraft:wooden_slab", 3): "minecraft:jungle_slab",
    ("minecraft:wooden_slab", 4): "minecraft:acacia_slab",
    ("minecraft:wooden_slab", 5): "minecraft:dark_oak_slab",

    # --- Różne bloki bez wariantów ---
    ("minecraft:iron_block", 0): "minecraft:iron_block",
    ("minecraft:gold_block", 0): "minecraft:gold_block",
    ("minecraft:diamond_block", 0): "minecraft:diamond_block",
    ("minecraft:emerald_block", 0): "minecraft:emerald_block",
    ("minecraft:lapis_block", 0): "minecraft:lapis_block",
    ("minecraft:coal_block", 0): "minecraft:coal_block",
    ("minecraft:redstone_block", 0): "minecraft:redstone_block",
    ("minecraft:ice", 0): "minecraft:ice",
    ("minecraft:packed_ice", 0): "minecraft:packed_ice",
    ("minecraft:snow", 0): "minecraft:snow_block",
    ("minecraft:soul_sand", 0): "minecraft:soul_sand",
    ("minecraft:obsidian", 0): "minecraft:obsidian",
    ("minecraft:netherrack", 0): "minecraft:netherrack",
    ("minecraft:nether_brick", 0): "minecraft:nether_bricks",
    ("minecraft:end_stone", 0): "minecraft:end_stone",
    ("minecraft:mycelium", 0): "minecraft:mycelium",
    ("minecraft:waterlily", 0): "minecraft:lily_pad",

    # --- Beton (concrete) - 1.12+ ---
    ("minecraft:concrete", 0): "minecraft:white_concrete",
    ("minecraft:concrete", 1): "minecraft:orange_concrete",
    ("minecraft:concrete", 2): "minecraft:magenta_concrete",
    ("minecraft:concrete", 3): "minecraft:light_blue_concrete",
    ("minecraft:concrete", 4): "minecraft:yellow_concrete",
    ("minecraft:concrete", 5): "minecraft:lime_concrete",
    ("minecraft:concrete", 6): "minecraft:pink_concrete",
    ("minecraft:concrete", 7): "minecraft:gray_concrete",
    ("minecraft:concrete", 8): "minecraft:light_gray_concrete",
    ("minecraft:concrete", 9): "minecraft:cyan_concrete",
    ("minecraft:concrete", 10): "minecraft:purple_concrete",
    ("minecraft:concrete", 11): "minecraft:blue_concrete",
    ("minecraft:concrete", 12): "minecraft:brown_concrete",
    ("minecraft:concrete", 13): "minecraft:green_concrete",
    ("minecraft:concrete", 14): "minecraft:red_concrete",
    ("minecraft:concrete", 15): "minecraft:black_concrete",

    # --- Schody - jako cover bloki (bez geometrii) ---
    ("minecraft:oak_stairs", 0): "minecraft:oak_planks",
    ("minecraft:spruce_stairs", 0): "minecraft:spruce_planks",
    ("minecraft:birch_stairs", 0): "minecraft:birch_planks",
    ("minecraft:jungle_stairs", 0): "minecraft:jungle_planks",
    ("minecraft:acacia_stairs", 0): "minecraft:acacia_planks",
    ("minecraft:dark_oak_stairs", 0): "minecraft:dark_oak_planks",
    ("minecraft:stone_stairs", 0): "minecraft:cobblestone",
    ("minecraft:sandstone_stairs", 0): "minecraft:sandstone",
    ("minecraft:brick_stairs", 0): "minecraft:bricks",
    ("minecraft:stone_brick_stairs", 0): "minecraft:stone_bricks",
    ("minecraft:nether_brick_stairs", 0): "minecraft:nether_bricks",
    ("minecraft:quartz_stairs", 0): "minecraft:quartz_block",
}

# -------------------------------------------------------------------
# Mapowania jednoargumentowe (cbUniqueId → 1.18.2, gdy damage=0 lub ignorowany)
# Uzupełniają COVER_MATERIAL_MAP gdy brak wpisu z damage.
# -------------------------------------------------------------------

_NO_DAMAGE_MAP: dict[str, str] = {
    "minecraft:cobblestone": "minecraft:cobblestone",
    "minecraft:mossy_cobblestone": "minecraft:mossy_cobblestone",
    "minecraft:grass": "minecraft:grass_block",
    "minecraft:gravel": "minecraft:gravel",
    "minecraft:clay": "minecraft:clay",
    "minecraft:glass": "minecraft:glass",
    "minecraft:glass_pane": "minecraft:glass_pane",
    "minecraft:iron_block": "minecraft:iron_block",
    "minecraft:gold_block": "minecraft:gold_block",
    "minecraft:diamond_block": "minecraft:diamond_block",
    "minecraft:emerald_block": "minecraft:emerald_block",
    "minecraft:lapis_block": "minecraft:lapis_block",
    "minecraft:coal_block": "minecraft:coal_block",
    "minecraft:redstone_block": "minecraft:redstone_block",
    "minecraft:ice": "minecraft:ice",
    "minecraft:packed_ice": "minecraft:packed_ice",
    "minecraft:snow": "minecraft:snow_block",
    "minecraft:soul_sand": "minecraft:soul_sand",
    "minecraft:obsidian": "minecraft:obsidian",
    "minecraft:netherrack": "minecraft:netherrack",
    "minecraft:nether_brick": "minecraft:nether_bricks",
    "minecraft:end_stone": "minecraft:end_stone",
    "minecraft:mycelium": "minecraft:mycelium",
    "minecraft:brick_block": "minecraft:bricks",
    "minecraft:hardened_clay": "minecraft:terracotta",
    "minecraft:quartz_block": "minecraft:quartz_block",
}


def resolve_cover_material(cb_unique_id: str, damage: int) -> str | None:
    """
    Zwraca 1.18.2 block ID dla materiału pokrycia z CB 1.7.10.

    Args:
        cb_unique_id: Forge registry name z cbUniqueId (np. "minecraft:log")
        damage: metadata ItemStack (np. 1 dla spruce)

    Returns:
        Resource location 1.18.2 lub None jeśli nieznany materiał.
    """
    # 1. Dokładne trafienie (unique_id, damage)
    key = (cb_unique_id, damage)
    if key in COVER_MATERIAL_MAP:
        return COVER_MATERIAL_MAP[key]

    # 2. Fallback: damage=0 jeśli damage != 0 (może mieć wpis bezuszkodzony)
    if damage != 0:
        key0 = (cb_unique_id, 0)
        if key0 in COVER_MATERIAL_MAP:
            return COVER_MATERIAL_MAP[key0]

    # 3. Fallback: single-arg map (ignoruje damage)
    if cb_unique_id in _NO_DAMAGE_MAP:
        return _NO_DAMAGE_MAP[cb_unique_id]

    # 4. Heurystyka: jeśli "minecraft:" i brak mapowania → zwróć ID bez damage
    if cb_unique_id.startswith("minecraft:"):
        return cb_unique_id

    # 5. Nieznany materiał (inny mod)
    return None
