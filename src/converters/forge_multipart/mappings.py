"""
Mapowania ForgeMultipart 1.7.10 -> CB Multipart / CB Microblock 1.18.2.

Source mapping:
- 1.7.10: dekompilacja JAR ForgeMultipart-1.7.10-1.2.0.345-universal.jar
- 1.18.2: mod_src/118/actual_src/1.18.2/CBMultipart/repo, branch 1.18.x
"""

from __future__ import annotations

import re

# ---------------------------------------------------------------------------
# Mapowanie ID blokow
# ---------------------------------------------------------------------------
BLOCK_ID_1710_TO_1182: dict[str, str] = {
    "ForgeMultipart:block": "cb_multipart:multipart",
}

# ---------------------------------------------------------------------------
# Mapowanie ID TileEntity / BlockEntity
# ---------------------------------------------------------------------------
TE_ID_1710_TO_1182: dict[str, str] = {
    # Exact string potwierdzony na mapie 1.7.10.
    "savedMultipart": "cb_multipart:saved_multipart",
    # Alternatywy zachowane defensywnie.
    "TileMultipart": "cb_multipart:saved_multipart",
    "ForgeMultipart:TileMultipart": "cb_multipart:saved_multipart",
}

# ---------------------------------------------------------------------------
# Mapowanie ID partow (multipart registry) 1.7.10 -> 1.18.2
# ---------------------------------------------------------------------------
PART_ID_1710_TO_1182: dict[str, str] = {
    # ForgeMicroblock -> CB Microblock.
    "mcr_face": "cb_microblock:face",
    "mcr_hollow": "cb_microblock:hollow",
    "mcr_corner": "cb_microblock:corner",
    "mcr_cnr": "cb_microblock:corner",
    "mcr_edge": "cb_microblock:edge",
    "mcr_post": "cb_microblock:post",

    # McMultipart vanilla parts. CBMultipart registers these through
    # cb_multipart_minecraft, but the active registry namespace is minecraft.
    "mc_torch": "minecraft:torch",
    "mc_redtorch": "minecraft:redstone_torch",
    "mc_button": "minecraft:stone_button",
    "mc_lever": "minecraft:lever",

    # ProjectRed parts are handled by the ProjectRed converter; these aliases
    # remain as a best-effort pass-through for multipart containers.
    "pr_redwire": "projectred-transmission:redwire",
    "pr_insulated": "projectred-transmission:insulated_wire",
    "pr_bundled": "projectred-transmission:bundled_cable",
    "pr_framed": "projectred-transmission:framed_wire",
    "pr_gate": "projectred-integration:gate",
}

# ---------------------------------------------------------------------------
# Mapowanie itemow (inventory TE innych modow)
# ---------------------------------------------------------------------------
ITEM_ID_1710_TO_1182: dict[str, str] = {
    "ForgeMicroblock:microblock": "cb_microblock:microblock",
    "microblock:microblock": "cb_microblock:microblock",
    "ForgeMicroblock:sawStone": "cb_microblock:stone_saw",
    "ForgeMicroblock:sawIron": "cb_microblock:iron_saw",
    "ForgeMicroblock:sawDiamond": "cb_microblock:diamond_saw",
    "ForgeMicroblock:stoneRod": "cb_microblock:stone_rod",
}

_RESOURCE_LOCATION_RE = re.compile(r"^[a-z0-9_.-]+:[a-z0-9/._-]+$")

MICROBLOCK_FALLBACK_MATERIAL = "minecraft:stone"

# CBMicroblock nie traktuje stringa `material` jako zwyklego tekstu: przy
# wczytywaniu musi on wskazywac material zarejestrowany po stronie klienta.
# Dlatego przepuszczamy tylko konserwatywny zestaw vanilla blokow 1.18.2, a
# stare ID modow 1.7.10 mapujemy jawnie do bezpiecznych odpowiednikow.
SAFE_MICROBLOCK_MATERIALS_1182: set[str] = {
    "minecraft:acacia_log",
    "minecraft:acacia_planks",
    "minecraft:andesite",
    "minecraft:basalt",
    "minecraft:birch_log",
    "minecraft:birch_planks",
    "minecraft:black_terracotta",
    "minecraft:black_wool",
    "minecraft:blue_terracotta",
    "minecraft:blue_wool",
    "minecraft:bricks",
    "minecraft:brown_terracotta",
    "minecraft:brown_wool",
    "minecraft:calcite",
    "minecraft:chiseled_quartz_block",
    "minecraft:chiseled_stone_bricks",
    "minecraft:clay",
    "minecraft:coal_block",
    "minecraft:cobblestone",
    "minecraft:cyan_terracotta",
    "minecraft:cyan_wool",
    "minecraft:dark_oak_log",
    "minecraft:dark_oak_planks",
    "minecraft:deepslate",
    "minecraft:diamond_block",
    "minecraft:diorite",
    "minecraft:dirt",
    "minecraft:emerald_block",
    "minecraft:end_stone",
    "minecraft:glass",
    "minecraft:glowstone",
    "minecraft:gold_block",
    "minecraft:granite",
    "minecraft:gray_terracotta",
    "minecraft:gray_wool",
    "minecraft:green_terracotta",
    "minecraft:green_wool",
    "minecraft:iron_block",
    "minecraft:jungle_log",
    "minecraft:jungle_planks",
    "minecraft:lapis_block",
    "minecraft:light_blue_terracotta",
    "minecraft:light_blue_wool",
    "minecraft:light_gray_terracotta",
    "minecraft:light_gray_wool",
    "minecraft:lime_terracotta",
    "minecraft:lime_wool",
    "minecraft:magenta_terracotta",
    "minecraft:magenta_wool",
    "minecraft:mossy_cobblestone",
    "minecraft:mossy_stone_bricks",
    "minecraft:netherrack",
    "minecraft:oak_log",
    "minecraft:oak_planks",
    "minecraft:obsidian",
    "minecraft:orange_terracotta",
    "minecraft:orange_wool",
    "minecraft:pink_terracotta",
    "minecraft:pink_wool",
    "minecraft:polished_andesite",
    "minecraft:polished_basalt",
    "minecraft:polished_deepslate",
    "minecraft:polished_diorite",
    "minecraft:polished_granite",
    "minecraft:purple_terracotta",
    "minecraft:purple_wool",
    "minecraft:purpur_block",
    "minecraft:quartz_block",
    "minecraft:quartz_bricks",
    "minecraft:red_nether_bricks",
    "minecraft:red_sandstone",
    "minecraft:red_terracotta",
    "minecraft:red_wool",
    "minecraft:redstone_block",
    "minecraft:sandstone",
    "minecraft:smooth_quartz",
    "minecraft:smooth_red_sandstone",
    "minecraft:smooth_sandstone",
    "minecraft:smooth_stone",
    "minecraft:spruce_log",
    "minecraft:spruce_planks",
    "minecraft:stone",
    "minecraft:stone_bricks",
    "minecraft:terracotta",
    "minecraft:warped_planks",
    "minecraft:white_terracotta",
    "minecraft:white_wool",
    "minecraft:yellow_terracotta",
    "minecraft:yellow_wool",
}

_TERRACOTTA_BY_1710_META = {
    "0": "minecraft:white_terracotta",
    "1": "minecraft:orange_terracotta",
    "2": "minecraft:magenta_terracotta",
    "3": "minecraft:light_blue_terracotta",
    "4": "minecraft:yellow_terracotta",
    "5": "minecraft:lime_terracotta",
    "6": "minecraft:pink_terracotta",
    "7": "minecraft:gray_terracotta",
    "8": "minecraft:light_gray_terracotta",
    "9": "minecraft:cyan_terracotta",
    "10": "minecraft:purple_terracotta",
    "11": "minecraft:blue_terracotta",
    "12": "minecraft:brown_terracotta",
    "13": "minecraft:green_terracotta",
    "14": "minecraft:red_terracotta",
    "15": "minecraft:black_terracotta",
}

_WOOL_BY_1710_META = {
    "0": "minecraft:white_wool",
    "1": "minecraft:orange_wool",
    "2": "minecraft:magenta_wool",
    "3": "minecraft:light_blue_wool",
    "4": "minecraft:yellow_wool",
    "5": "minecraft:lime_wool",
    "6": "minecraft:pink_wool",
    "7": "minecraft:gray_wool",
    "8": "minecraft:light_gray_wool",
    "9": "minecraft:cyan_wool",
    "10": "minecraft:purple_wool",
    "11": "minecraft:blue_wool",
    "12": "minecraft:brown_wool",
    "13": "minecraft:green_wool",
    "14": "minecraft:red_wool",
    "15": "minecraft:black_wool",
}

# Stare material names ForgeMicroblock potrafia przechowywac registry/unlocalized
# names blokow 1.7.10. CBMicroblock 1.18.2 robi z tego ResourceLocation bez
# defensywnego try/catch, wiec kazdy camelCase w material wysypuje ladowanie
# chunka. Mapujemy znane dekoracyjne materialy Extra Utilities na stabilne
# vanilla odpowiedniki, tracac kolor tylko tam, gdzie nie ma pewnego targetu.
MICROBLOCK_MATERIAL_1710_TO_1182: dict[str, str] = {
    "tile.extrautils:color_quartzblock": "minecraft:quartz_block",
    "extrautils:color_quartzblock": "minecraft:quartz_block",
    "extrautilities:color_quartzblock": "minecraft:quartz_block",
    "tile.extrautils:color_blocklapis": "minecraft:lapis_block",
    "extrautils:color_blocklapis": "minecraft:lapis_block",
    "extrautilities:color_blocklapis": "minecraft:lapis_block",
    "tile.extrautils:color_blockredstone": "minecraft:redstone_block",
    "extrautils:color_blockredstone": "minecraft:redstone_block",
    "extrautilities:color_blockredstone": "minecraft:redstone_block",
    "tile.extrautils:color_blockcoal": "minecraft:coal_block",
    "extrautils:color_blockcoal": "minecraft:coal_block",
    "extrautilities:color_blockcoal": "minecraft:coal_block",
    "tile.extrautils:color_blockdiamond": "minecraft:diamond_block",
    "extrautils:color_blockdiamond": "minecraft:diamond_block",
    "extrautilities:color_blockdiamond": "minecraft:diamond_block",
    "tile.extrautils:color_blockemerald": "minecraft:emerald_block",
    "extrautils:color_blockemerald": "minecraft:emerald_block",
    "extrautilities:color_blockemerald": "minecraft:emerald_block",
    "tile.extrautils:color_blockgold": "minecraft:gold_block",
    "extrautils:color_blockgold": "minecraft:gold_block",
    "extrautilities:color_blockgold": "minecraft:gold_block",
    "tile.extrautils:color_blockiron": "minecraft:iron_block",
    "extrautils:color_blockiron": "minecraft:iron_block",
    "extrautilities:color_blockiron": "minecraft:iron_block",
    "tile.extrautils:color_stonebrick": "minecraft:stone_bricks",
    "extrautils:color_stonebrick": "minecraft:stone_bricks",
    "extrautilities:color_stonebrick": "minecraft:stone_bricks",
    "tile.extrautils:color_cobblestone": "minecraft:cobblestone",
    "extrautils:color_cobblestone": "minecraft:cobblestone",
    "extrautilities:color_cobblestone": "minecraft:cobblestone",
    "tile.extrautils:color_woodplanks": "minecraft:oak_planks",
    "extrautils:color_woodplanks": "minecraft:oak_planks",
    "extrautilities:color_woodplanks": "minecraft:oak_planks",
    "tile.extrautils:color_brick": "minecraft:bricks",
    "extrautils:color_brick": "minecraft:bricks",
    "extrautilities:color_brick": "minecraft:bricks",
    "tile.extrautils:color_obsidian": "minecraft:obsidian",
    "extrautils:color_obsidian": "minecraft:obsidian",
    "extrautilities:color_obsidian": "minecraft:obsidian",
    "tile.extrautils:colorstonebrick": "minecraft:stone_bricks",
    "extrautils:colorstonebrick": "minecraft:stone_bricks",
    "extrautilities:colorstonebrick": "minecraft:stone_bricks",
    "tile.extrautils:color_lightgem": "minecraft:glowstone",
    "extrautils:color_lightgem": "minecraft:glowstone",
    "extrautilities:color_lightgem": "minecraft:glowstone",
    "tile.extrautils:decorativeblock1": "minecraft:stone_bricks",
    "extrautils:decorativeblock1": "minecraft:stone_bricks",
    "extrautilities:decorativeblock1": "minecraft:stone_bricks",
    "tile.extrautils:cobblestone_compressed": "minecraft:cobblestone",
    "extrautils:cobblestone_compressed": "minecraft:cobblestone",
    "extrautilities:cobblestone_compressed": "minecraft:cobblestone",
    "thermalfoundation:storage": "minecraft:iron_block",
    "mekanism:basicblock": "minecraft:iron_block",
    "projred|exploration:projectred.exploration.stone": "minecraft:stone",
    "projectred|exploration:projectred.exploration.stone": "minecraft:stone",
    "projred_exploration:projectred.exploration.stone": "minecraft:stone",
    "minecraft:brick_block": "minecraft:bricks",
    "minecraft:stonebrick": "minecraft:stone_bricks",
    "minecraft:wood": "minecraft:oak_log",
    "minecraft:log": "minecraft:oak_log",
    "minecraft:log2": "minecraft:acacia_log",
    "minecraft:planks": "minecraft:oak_planks",
    "minecraft:hardened_clay": "minecraft:terracotta",
    "minecraft:stained_hardened_clay": "minecraft:terracotta",
    "minecraft:wool": "minecraft:white_wool",
}

KNOWN_PART_IDS_1182 = set(PART_ID_1710_TO_1182.values()) | {
    "minecraft:soul_torch",
    "minecraft:polished_blackstone_button",
    "minecraft:oak_button",
    "minecraft:spruce_button",
    "minecraft:birch_button",
    "minecraft:jungle_button",
    "minecraft:acacia_button",
    "minecraft:dark_oak_button",
    "minecraft:crimson_button",
    "minecraft:warped_button",
}


def map_block_id(block_id_1710: str) -> str | None:
    """Zwraca block ID 1.18.2 lub None jesli nieznane."""
    return BLOCK_ID_1710_TO_1182.get(block_id_1710)


def map_te_id(te_id_1710: str) -> str | None:
    """Zwraca TE/BE ID 1.18.2 lub None jesli nieznane."""
    return TE_ID_1710_TO_1182.get(te_id_1710)


def map_part_id(part_id_1710: str) -> str:
    """Zwraca part ID 1.18.2; jesli brak mapowania, zwraca oryginal."""
    return PART_ID_1710_TO_1182.get(part_id_1710, part_id_1710)


def is_known_part_id_1182(part_id: str) -> bool:
    """Czy part ID odpowiada typowi znanemu z CBMultipart/CBMicroblock 1.18.x."""
    return part_id in KNOWN_PART_IDS_1182


def map_item_id(item_id_1710: str) -> str:
    """Zwraca item ID 1.18.2; jesli brak mapowania, zwraca oryginal."""
    return ITEM_ID_1710_TO_1182.get(item_id_1710, item_id_1710)


def _strip_trailing_metadata(material: str) -> str:
    """Usuwa koncowe `_meta` ze starych nazw materialow microblockow."""
    return re.sub(r"_[0-9]+$", "", material)


def _trailing_metadata(material: str) -> str | None:
    match = re.search(r"_([0-9]+)$", material)
    return match.group(1) if match else None


def _is_safe_microblock_material(material: str) -> bool:
    return material in SAFE_MICROBLOCK_MATERIALS_1182


def _map_chisel_material(key: str) -> str:
    name = key.split(":", 1)[1]
    if "glowstone" in name or "light" in name:
        return "minecraft:glowstone"
    if "gold" in name:
        return "minecraft:gold_block"
    if "iron" in name:
        return "minecraft:iron_block"
    if "diamond" in name:
        return "minecraft:diamond_block"
    if "emerald" in name:
        return "minecraft:emerald_block"
    if "lapis" in name:
        return "minecraft:lapis_block"
    if "redstone" in name:
        return "minecraft:redstone_block"
    if "coal" in name:
        return "minecraft:coal_block"
    if "quartz" in name:
        return "minecraft:quartz_block"
    if "marble" in name or "limestone" in name or "concrete" in name:
        return "minecraft:calcite"
    if "glass" in name:
        return "minecraft:glass"
    if "brick" in name:
        return "minecraft:stone_bricks"
    if "cobblestone" in name:
        return "minecraft:cobblestone"
    if "sandstone" in name:
        return "minecraft:sandstone"
    if "netherrack" in name or "nether" in name:
        return "minecraft:netherrack"
    if "wood" in name or "plank" in name:
        return "minecraft:oak_planks"
    return MICROBLOCK_FALLBACK_MATERIAL


def _map_minecraft_legacy_material(key: str) -> str | None:
    meta = _trailing_metadata(key)
    base = _strip_trailing_metadata(key)
    if base in MICROBLOCK_MATERIAL_1710_TO_1182:
        mapped_base = MICROBLOCK_MATERIAL_1710_TO_1182[base]
        if base == "minecraft:stained_hardened_clay" and meta:
            return _TERRACOTTA_BY_1710_META.get(meta, mapped_base)
        if base == "minecraft:wool" and meta:
            return _WOOL_BY_1710_META.get(meta, mapped_base)
        return mapped_base
    if key in SAFE_MICROBLOCK_MATERIALS_1182:
        return key
    return None


def map_microblock_material(material_1710: str) -> str:
    """Zwraca bezpieczny material microblocka dla CBMicroblock 1.18.2.

    Najpierw wykonuje znane mapowania starych nazw 1.7.10, a potem przepuszcza
    tylko materialy z konserwatywnej whitelisty 1.18.2. Skladniowo poprawne,
    ale niezarejestrowane materialy typu `chisel:glowstone_4` sa mapowane do
    bezpiecznych odpowiednikow, bo pusty material zatrzymuje ladowanie calego
    chunka w CBMultipart 1.18.x.
    """
    if not material_1710:
        return MICROBLOCK_FALLBACK_MATERIAL

    material = str(material_1710).strip()
    lower_material = material.lower()

    minecraft_mapped = _map_minecraft_legacy_material(lower_material)
    if minecraft_mapped:
        return minecraft_mapped

    key = _strip_trailing_metadata(material).lower()
    mapped = MICROBLOCK_MATERIAL_1710_TO_1182.get(key)
    if mapped:
        return mapped

    lower_key = _strip_trailing_metadata(lower_material)
    mapped = MICROBLOCK_MATERIAL_1710_TO_1182.get(lower_key)
    if mapped:
        return mapped

    if lower_material.startswith("chisel:"):
        return _map_chisel_material(lower_material)

    if lower_material.startswith(("tile.extrautils:", "extrautils:", "extrautilities:")):
        if "lightgem" in lower_material:
            return "minecraft:glowstone"
        if "colorstonebrick" in lower_material or "decorativeblock" in lower_material:
            return "minecraft:stone_bricks"
        if "cobblestone" in lower_material:
            return "minecraft:cobblestone"
        return MICROBLOCK_FALLBACK_MATERIAL

    if lower_material.startswith(("thermalfoundation:", "mekanism:")):
        return "minecraft:iron_block"

    if _RESOURCE_LOCATION_RE.match(lower_material) and _is_safe_microblock_material(lower_material):
        return lower_material

    return MICROBLOCK_FALLBACK_MATERIAL
