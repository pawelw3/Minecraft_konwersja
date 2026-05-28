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


def map_microblock_material(material_1710: str) -> str:
    """Zwraca bezpieczny material microblocka dla CBMicroblock 1.18.2.

    Najpierw wykonuje znane mapowania starych nazw 1.7.10, potem przepuszcza
    juz poprawne ResourceLocation. Nieznane lub skladniowo niepoprawne materialy
    sprowadza do `minecraft:stone`, bo pusty/niepoprawny material zatrzymuje
    ladowanie calego chunka w CBMultipart 1.18.x.
    """
    if not material_1710:
        return "minecraft:stone"

    material = str(material_1710).strip()
    key = _strip_trailing_metadata(material).lower()
    mapped = MICROBLOCK_MATERIAL_1710_TO_1182.get(key)
    if mapped:
        return mapped

    lower_material = material.lower()
    if lower_material != material:
        lower_key = _strip_trailing_metadata(lower_material)
        mapped = MICROBLOCK_MATERIAL_1710_TO_1182.get(lower_key)
        if mapped:
            return mapped
        if _RESOURCE_LOCATION_RE.match(lower_material):
            return lower_material

    if _RESOURCE_LOCATION_RE.match(material):
        return material

    return "minecraft:stone"
