"""
Rozszerzone mapowania tekstur i ID dla konwersji BiblioCraft 1.7.10 -> 1.18.2

Ten moduł zawiera pełne mapowania:
- Tekstur drewna (BC 1.7.10 metadata -> 1.18.2 block IDs)
- Tekstur z innych modów (BOP, Forestry, itp.)
- ID bloków i itemów
- Metadata -> BlockState properties
"""

from typing import Dict, Optional, Tuple


# ============================================================================
# MAPOWANIE TEKSTUR DREWNA (BC 1.7.10 -> 1.18.2)
# ============================================================================

WOOD_TEXTURE_MAP = {
    # Minecraft Vanilla - planks (metadata)
    "minecraft:planks": "minecraft:oak_planks",
    "minecraft:planks:0": "minecraft:oak_planks",
    "minecraft:planks:1": "minecraft:spruce_planks",
    "minecraft:planks:2": "minecraft:birch_planks",
    "minecraft:planks:3": "minecraft:jungle_planks",
    "minecraft:planks:4": "minecraft:acacia_planks",
    "minecraft:planks:5": "minecraft:dark_oak_planks",
    
    # Minecraft Vanilla - logs (metadata)
    "minecraft:log": "minecraft:oak_log",
    "minecraft:log:0": "minecraft:oak_log",
    "minecraft:log:1": "minecraft:spruce_log",
    "minecraft:log:2": "minecraft:birch_log",
    "minecraft:log:3": "minecraft:jungle_log",
    "minecraft:log2": "minecraft:acacia_log",
    "minecraft:log2:0": "minecraft:acacia_log",
    "minecraft:log2:1": "minecraft:dark_oak_log",
    
    # Minecraft Vanilla - stripped logs (nowe w 1.18.2, fallback na zwykłe)
    "minecraft:stripped_oak_log": "minecraft:stripped_oak_log",
    "minecraft:stripped_spruce_log": "minecraft:stripped_spruce_log",
    "minecraft:stripped_birch_log": "minecraft:stripped_birch_log",
    "minecraft:stripped_jungle_log": "minecraft:stripped_jungle_log",
    "minecraft:stripped_acacia_log": "minecraft:stripped_acacia_log",
    "minecraft:stripped_dark_oak_log": "minecraft:stripped_dark_oak_log",
    
    # Minecraft Vanilla - wood (stem)
    "minecraft:wood": "minecraft:oak_wood",
    "minecraft:wood:0": "minecraft:oak_wood",
    "minecraft:wood:1": "minecraft:spruce_wood",
    "minecraft:wood:2": "minecraft:birch_wood",
    "minecraft:wood:3": "minecraft:jungle_wood",
    "minecraft:wood2": "minecraft:acacia_wood",
    "minecraft:wood2:0": "minecraft:acacia_wood",
    "minecraft:wood2:1": "minecraft:dark_oak_wood",
}


# ============================================================================
# MAPOWANIE KAMIENIA I MATERIAŁÓW BUDOWLANYCH
# ============================================================================

STONE_TEXTURE_MAP = {
    # Podstawowe bloki kamienne
    "minecraft:stone": "minecraft:stone",
    "minecraft:stone:0": "minecraft:stone",
    "minecraft:stone:1": "minecraft:granite",
    "minecraft:stone:2": "minecraft:polished_granite",
    "minecraft:stone:3": "minecraft:diorite",
    "minecraft:stone:4": "minecraft:polished_diorite",
    "minecraft:stone:5": "minecraft:andesite",
    "minecraft:stone:6": "minecraft:polished_andesite",
    
    # Cobblestone
    "minecraft:cobblestone": "minecraft:cobblestone",
    "minecraft:mossy_cobblestone": "minecraft:mossy_cobblestone",
    
    # Stone bricks
    "minecraft:stonebrick": "minecraft:stone_bricks",
    "minecraft:stonebrick:0": "minecraft:stone_bricks",
    "minecraft:stonebrick:1": "minecraft:mossy_stone_bricks",
    "minecraft:stonebrick:2": "minecraft:cracked_stone_bricks",
    "minecraft:stonebrick:3": "minecraft:chiseled_stone_bricks",
    
    # Cegły
    "minecraft:brick_block": "minecraft:bricks",
    "minecraft:stone_slab:4": "minecraft:bricks",  # Brick slab jako bricks
    
    # Piaskowiec
    "minecraft:sandstone": "minecraft:sandstone",
    "minecraft:sandstone:0": "minecraft:sandstone",
    "minecraft:sandstone:1": "minecraft:chiseled_sandstone",
    "minecraft:sandstone:2": "minecraft:cut_sandstone",
    
    # Czerwony piaskowiec
    "minecraft:red_sandstone": "minecraft:red_sandstone",
    "minecraft:red_sandstone:0": "minecraft:red_sandstone",
    "minecraft:red_sandstone:1": "minecraft:chiseled_red_sandstone",
    "minecraft:red_sandstone:2": "minecraft:cut_red_sandstone",
    
    # Nether
    "minecraft:netherrack": "minecraft:netherrack",
    "minecraft:soul_sand": "minecraft:soul_sand",
    "minecraft:glowstone": "minecraft:glowstone",
    "minecraft:nether_brick": "minecraft:nether_bricks",
    "minecraft:quartz_block": "minecraft:quartz_block",
    "minecraft:quartz_block:0": "minecraft:quartz_block",
    "minecraft:quartz_block:1": "minecraft:chiseled_quartz_block",
    "minecraft:quartz_block:2": "minecraft:quartz_pillar",
    
    # End
    "minecraft:end_stone": "minecraft:end_stone",
    "minecraft:end_bricks": "minecraft:end_stone_bricks",
}


# ============================================================================
# MAPOWANIE BLOKÓW ZWIĄZANYCH Z METALAMI
# ============================================================================

METAL_TEXTURE_MAP = {
    # Żelazo
    "minecraft:iron_block": "minecraft:iron_block",
    "minecraft:iron_bars": "minecraft:iron_bars",
    
    # Złoto
    "minecraft:gold_block": "minecraft:gold_block",
    
    # Diament
    "minecraft:diamond_block": "minecraft:diamond_block",
    
    # Szmaragd
    "minecraft:emerald_block": "minecraft:emerald_block",
    
    # Lapis
    "minecraft:lapis_block": "minecraft:lapis_block",
    
    # Redstone
    "minecraft:redstone_block": "minecraft:redstone_block",
    
    # Węgiel/obsydian
    "minecraft:coal_block": "minecraft:coal_block",
    "minecraft:obsidian": "minecraft:obsidian",
}


# ============================================================================
# MAPOWANIE BLOKÓW NATURALNYCH
# ============================================================================

NATURAL_TEXTURE_MAP = {
    # Trawa
    "minecraft:grass": "minecraft:grass_block",
    "minecraft:dirt": "minecraft:dirt",
    "minecraft:dirt:0": "minecraft:dirt",
    "minecraft:dirt:1": "minecraft:coarse_dirt",
    "minecraft:dirt:2": "minecraft:podzol",
    "minecraft:farmland": "minecraft:farmland",
    
    # Dżungla
    "minecraft:leaves": "minecraft:oak_leaves",
    "minecraft:leaves:0": "minecraft:oak_leaves",
    "minecraft:leaves:1": "minecraft:spruce_leaves",
    "minecraft:leaves:2": "minecraft:birch_leaves",
    "minecraft:leaves:3": "minecraft:jungle_leaves",
    "minecraft:leaves2": "minecraft:acacia_leaves",
    "minecraft:leaves2:0": "minecraft:acacia_leaves",
    "minecraft:leaves2:1": "minecraft:dark_oak_leaves",
    
    # Wełna
    "minecraft:wool": "minecraft:white_wool",
    "minecraft:wool:0": "minecraft:white_wool",
    "minecraft:wool:1": "minecraft:orange_wool",
    "minecraft:wool:2": "minecraft:magenta_wool",
    "minecraft:wool:3": "minecraft:light_blue_wool",
    "minecraft:wool:4": "minecraft:yellow_wool",
    "minecraft:wool:5": "minecraft:lime_wool",
    "minecraft:wool:6": "minecraft:pink_wool",
    "minecraft:wool:7": "minecraft:gray_wool",
    "minecraft:wool:8": "minecraft:light_gray_wool",
    "minecraft:wool:9": "minecraft:cyan_wool",
    "minecraft:wool:10": "minecraft:purple_wool",
    "minecraft:wool:11": "minecraft:blue_wool",
    "minecraft:wool:12": "minecraft:brown_wool",
    "minecraft:wool:13": "minecraft:green_wool",
    "minecraft:wool:14": "minecraft:red_wool",
    "minecraft:wool:15": "minecraft:black_wool",
    
    # Terracotta/glina
    "minecraft:hardened_clay": "minecraft:terracotta",
    "minecraft:stained_hardened_clay": "minecraft:white_terracotta",
    "minecraft:stained_hardened_clay:0": "minecraft:white_terracotta",
    "minecraft:stained_hardened_clay:1": "minecraft:orange_terracotta",
    "minecraft:stained_hardened_clay:2": "minecraft:magenta_terracotta",
    "minecraft:stained_hardened_clay:3": "minecraft:light_blue_terracotta",
    "minecraft:stained_hardened_clay:4": "minecraft:yellow_terracotta",
    "minecraft:stained_hardened_clay:5": "minecraft:lime_terracotta",
    "minecraft:stained_hardened_clay:6": "minecraft:pink_terracotta",
    "minecraft:stained_hardened_clay:7": "minecraft:gray_terracotta",
    "minecraft:stained_hardened_clay:8": "minecraft:light_gray_terracotta",
    "minecraft:stained_hardened_clay:9": "minecraft:cyan_terracotta",
    "minecraft:stained_hardened_clay:10": "minecraft:purple_terracotta",
    "minecraft:stained_hardened_clay:11": "minecraft:blue_terracotta",
    "minecraft:stained_hardened_clay:12": "minecraft:brown_terracotta",
    "minecraft:stained_hardened_clay:13": "minecraft:green_terracotta",
    "minecraft:stained_hardened_clay:14": "minecraft:red_terracotta",
    "minecraft:stained_hardened_clay:15": "minecraft:black_terracotta",
}


# ============================================================================
# MAPOWANIE BLOKÓW Z INNYCH MODÓW (Biomes O' Plenty, Forestry, etc.)
# ============================================================================

MOD_TEXTURE_MAP = {
    # Biomes O' Plenty - drewno (jeśli dostępne w 1.18.2)
    "BiomesOPlenty:planks": "biomesoplenty:fir_planks",  # Fallback
    "BiomesOPlenty:planks:0": "biomesoplenty:_sacred_oak_planks",
    "BiomesOPlenty:planks:1": "biomesoplenty:cherry_planks",
    "BiomesOPlenty:planks:2": "biomesoplenty:umbran_planks",
    "BiomesOPlenty:planks:3": "biomesoplenty:fir_planks",
    "BiomesOPlenty:planks:4": "biomesoplenty:ethereal_planks",
    "BiomesOPlenty:planks:5": "biomesoplenty:magic_planks",
    "BiomesOPlenty:planks:6": "biomesoplenty:mangrove_planks",
    "BiomesOPlenty:planks:7": "biomesoplenty:palm_planks",
    "BiomesOPlenty:planks:8": "biomesoplenty:redwood_planks",
    "BiomesOPlenty:planks:9": "biomesoplenty:willow_planks",
    "BiomesOPlenty:planks:10": "biomesoplenty:pine_planks",
    "BiomesOPlenty:planks:11": "biomesoplenty:hellbark_planks",
    "BiomesOPlenty:planks:12": "biomesoplenty:jacaranda_planks",
    "BiomesOPlenty:planks:13": "biomesoplenty:mahogany_planks",
    "BiomesOPlenty:planks:14": "biomesoplenty:ebony_planks",
    "BiomesOPlenty:planks:15": "biomesoplenty:eucalyptus_planks",
    
    # Forestry - drewno (jeśli dostępne)
    "Forestry:planks": "forestry:larch_planks",  # Fallback
    "Forestry:planks:0": "forestry:larch_planks",
    "Forestry:planks:1": "forestry:teak_planks",
    "Forestry:planks:2": "forestry:acacia_forestry_planks",
    "Forestry:planks:3": "forestry:lime_planks",
    "Forestry:planks:4": "forestry:chestnut_planks",
    "Forestry:planks:5": "forestry:wenge_planks",
    "Forestry:planks:6": "forestry:baobab_planks",
    "Forestry:planks:7": "forestry:sequoia_planks",
    "Forestry:planks:8": "forestry:kapok_planks",
    "Forestry:planks:9": "forestry:ebony_forestry_planks",
    "Forestry:planks:10": "forestry:mahogany_forestry_planks",
    "Forestry:planks:11": "forestry:balsa_planks",
    "Forestry:planks:12": "forestry:willow_forestry_planks",
    "Forestry:planks:13": "forestry:walnut_planks",
    "Forestry:planks:14": "forestry:greenheart_planks",
    "Forestry:planks:15": "forestry:cherry_forestry_planks",
    
    # Natura - drewno (jeśli dostępne)
    "Natura:planks": "natura:maple_planks",  # Fallback
    
    # Carpenter's Blocks - covered blocks
    "CarpentersBlocks:blockCarpentersBlock": "framedblocks:framed_block",
}


# ============================================================================
# POŁĄCZONE MAPOWANIE
# ============================================================================

COMPLETE_TEXTURE_MAP = {
    **WOOD_TEXTURE_MAP,
    **STONE_TEXTURE_MAP,
    **METAL_TEXTURE_MAP,
    **NATURAL_TEXTURE_MAP,
    **MOD_TEXTURE_MAP,
}


# ============================================================================
# FUNKCJE POMOCNICZE
# ============================================================================

def convert_texture_id(bc_texture: str, default: str = "minecraft:oak_planks") -> str:
    """
    Konwertuje ID tekstury z BC 1.7.10 na 1.18.2
    
    Args:
        bc_texture: ID tekstury w formacie BC (np. "minecraft:planks:0")
        default: Domyślna wartość jeśli nie znaleziono
        
    Returns:
        ID tekstury w formacie 1.18.2
    """
    # Sprawdź w pełnym mapowaniu
    if bc_texture in COMPLETE_TEXTURE_MAP:
        return COMPLETE_TEXTURE_MAP[bc_texture]
    
    # Sprawdź w poszczególnych mapowaniach
    for mapping in [WOOD_TEXTURE_MAP, STONE_TEXTURE_MAP, METAL_TEXTURE_MAP, 
                    NATURAL_TEXTURE_MAP, MOD_TEXTURE_MAP]:
        if bc_texture in mapping:
            return mapping[bc_texture]
    
    # Parsowanie formatu z metadata
    if ":" in bc_texture:
        parts = bc_texture.split(":")
        if len(parts) == 3:  # mod:block:meta
            mod_id, block_name, meta = parts
            # Spróbuj bez metadata
            base_key = f"{mod_id}:{block_name}"
            if base_key in COMPLETE_TEXTURE_MAP:
                return COMPLETE_TEXTURE_MAP[base_key]
    
    # Zwróć domyślną lub oryginał
    return default if default else bc_texture


def convert_to_block_state(bc_texture: str) -> Tuple[str, Dict]:
    """
    Konwertuje teksturę BC na BlockState 1.18.2
    
    Returns:
        Tuple (block_id, properties_dict)
    """
    block_id = convert_texture_id(bc_texture)
    properties = {}
    
    # Dodaj domyślne properties w zależności od typu bloku
    if "log" in block_id and "stripped" not in block_id:
        properties["axis"] = "y"
    elif "stairs" in block_id:
        properties["facing"] = "north"
        properties["half"] = "bottom"
    elif "slab" in block_id:
        properties["type"] = "bottom"
    
    return block_id, properties


def is_valid_texture(bc_texture: str) -> bool:
    """Sprawdza czy tekstura istnieje w mapowaniu"""
    return bc_texture in COMPLETE_TEXTURE_MAP


def get_texture_category(bc_texture: str) -> str:
    """Zwraca kategorię tekstury (wood, stone, metal, natural, mod, unknown)"""
    if bc_texture in WOOD_TEXTURE_MAP:
        return "wood"
    elif bc_texture in STONE_TEXTURE_MAP:
        return "stone"
    elif bc_texture in METAL_TEXTURE_MAP:
        return "metal"
    elif bc_texture in NATURAL_TEXTURE_MAP:
        return "natural"
    elif bc_texture in MOD_TEXTURE_MAP:
        return "mod"
    return "unknown"


def get_all_wood_textures() -> Dict[str, str]:
    """Zwraca wszystkie mapowania tekstur drewna"""
    return WOOD_TEXTURE_MAP.copy()


def get_all_stone_textures() -> Dict[str, str]:
    """Zwraca wszystkie mapowania tekstur kamienia"""
    return STONE_TEXTURE_MAP.copy()


# ============================================================================
# TESTOWANIE
# ============================================================================

if __name__ == "__main__":
    print("=" * 60)
    print("TEST: Texture Mappings")
    print("=" * 60)
    
    # Test mapowań drewna
    print("\n--- Drewno ---")
    wood_tests = [
        "minecraft:planks:0",
        "minecraft:planks:5",
        "minecraft:log:2",
        "minecraft:log2:1",
    ]
    for test in wood_tests:
        result = convert_texture_id(test)
        print(f"  {test} -> {result}")
    
    # Test mapowań kamienia
    print("\n--- Kamień ---")
    stone_tests = [
        "minecraft:stone",
        "minecraft:stone:1",
        "minecraft:stonebrick:2",
        "minecraft:sandstone:1",
    ]
    for test in stone_tests:
        result = convert_texture_id(test)
        print(f"  {test} -> {result}")
    
    # Test kategorii
    print("\n--- Kategorie ---")
    test_textures = [
        "minecraft:planks:0",
        "minecraft:stone",
        "minecraft:iron_block",
        "minecraft:wool:5",
        "BiomesOPlenty:planks:3",
    ]
    for test in test_textures:
        category = get_texture_category(test)
        print(f"  {test} -> {category}")
    
    # Statystyki
    print("\n--- Statystyki ---")
    print(f"  Drewno: {len(WOOD_TEXTURE_MAP)} tekstur")
    print(f"  Kamień: {len(STONE_TEXTURE_MAP)} tekstur")
    print(f"  Metal: {len(METAL_TEXTURE_MAP)} tekstur")
    print(f"  Naturalne: {len(NATURAL_TEXTURE_MAP)} tekstur")
    print(f"  Z modów: {len(MOD_TEXTURE_MAP)} tekstur")
    print(f"  Razem: {len(COMPLETE_TEXTURE_MAP)} tekstur")
    
    print("\n" + "=" * 60)
    print("Test zakończony!")
    print("=" * 60)
