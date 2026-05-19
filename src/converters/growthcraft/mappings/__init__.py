"""
Mapowania bloków i itemów GrowthCraft 1.7.10 -> 1.18.2

Ten moduł zawiera mapowania dla:
- Bloków (BlockMappings)
- Itemów (ItemMappings)
- Płynów (FluidMappings)
"""

from typing import Dict, Optional, List
from dataclasses import dataclass


STRICT_1182_FUNCTIONAL = "strict_1182_functional"
GROWTHCRAFT_CE_EXPERIMENTAL = "growthcraft_ce_experimental"
DEFAULT_PROFILE = STRICT_1182_FUNCTIONAL
SUPPORTED_PROFILES = {STRICT_1182_FUNCTIONAL, GROWTHCRAFT_CE_EXPERIMENTAL}


@dataclass
class BlockMapping:
    """Pojedyncze mapowanie bloku"""
    id_1710: str
    id_1182: str
    metadata_map: Optional[Dict[int, str]] = None  # metadata -> blockstate variant
    
    def get_1182_id(self, metadata: int = 0) -> str:
        """Zwraca ID bloku w 1.18.2"""
        if self.metadata_map and metadata in self.metadata_map:
            return self.metadata_map[metadata]
        return self.id_1182


@dataclass
class ItemMapping:
    """Pojedyncze mapowanie itemu"""
    id_1710: str
    id_1182: str
    damage_map: Optional[Dict[int, str]] = None  # damage -> item variant
    
    def get_1182_id(self, damage: int = 0) -> str:
        """Zwraca ID itemu w 1.18.2"""
        if self.damage_map and damage in self.damage_map:
            return self.damage_map[damage]
        return self.id_1182


@dataclass
class FluidMapping:
    """Pojedyncze mapowanie płynu"""
    id_1710: str
    id_1182: str


# Mapowania bloków GrowthCraft
# UWAGA: W 1.18.2 Growthcraft jest podzielony na osobne mody:
# - growthcraft_cellar (browarnictwo)
# - growthcraft_milk (mleczarstwo)
# - growthcraft_apiary (pszczelarstwo - dawniej bees)
# - growthcraft_apples (jabłka)
# - growthcraft_bamboo (bambus)
# - growthcraft_rice (ryż)
# - growthcraft (core)

BLOCK_MAPPINGS: Dict[str, BlockMapping] = {
    # === Moduł: Cellar (Browarnictwo) ===
    "grccellar:ferment_barrel": BlockMapping(
        id_1710="grccellar:ferment_barrel",
        id_1182="growthcraft_cellar:fermentation_barrel"
    ),
    "grccellar:brew_kettle": BlockMapping(
        id_1710="grccellar:brew_kettle",
        id_1182="growthcraft_cellar:brew_kettle"
    ),
    "grccellar:fruit_press": BlockMapping(
        id_1710="grccellar:fruit_press",
        id_1182="growthcraft_cellar:fruit_press"
    ),
    "grccellar:culture_jar": BlockMapping(
        id_1710="grccellar:culture_jar",
        id_1182="growthcraft_cellar:culture_jar"
    ),
    "grccellar:roaster": BlockMapping(
        id_1710="grccellar:roaster",
        id_1182="growthcraft_cellar:roaster"
    ),

    # === Moduł: Milk (Mleczarstwo) ===
    "grcmilk:cheese_vat": BlockMapping(
        id_1710="grcmilk:cheese_vat",
        id_1182="growthcraft_milk:mixing_vat"
    ),
    "grcmilk:pancheon": BlockMapping(
        id_1710="grcmilk:pancheon",
        id_1182="growthcraft_milk:pancheon"
    ),
    "grcmilk:butter_churn": BlockMapping(
        id_1710="grcmilk:butter_churn",
        id_1182="growthcraft_milk:churn"
    ),
    "grcmilk:cheese_press": BlockMapping(
        id_1710="grcmilk:cheese_press",
        id_1182="growthcraft_milk:cheese_press"
    ),
    "grcmilk:hanging_curds": BlockMapping(
        id_1710="grcmilk:hanging_curds",
        id_1182="growthcraft_milk:cheese_curd"
    ),

    # === Moduł: Apiary (Pszczelarstwo) - dawniej Bees ===
    # W 1.18.2 bee_box ma warianty drewna (bee_box_oak, bee_box_birch, etc.)
    "grcbees:bee_box": BlockMapping(
        id_1710="grcbees:bee_box",
        id_1182="growthcraft_apiary:bee_box_oak",
        metadata_map={
            0: "growthcraft_apiary:bee_box_oak",
            1: "growthcraft_apiary:bee_box_spruce",
            2: "growthcraft_apiary:bee_box_birch",
            3: "growthcraft_apiary:bee_box_jungle",
            4: "growthcraft_apiary:bee_box_acacia",
            5: "growthcraft_apiary:bee_box_dark_oak",
        }
    ),
    # W 1.18.2 nie ma bee_hive jako bloku Growthcraft - używamy vanilla bee_nest
    "grcbees:bee_hive": BlockMapping(
        id_1710="grcbees:bee_hive",
        id_1182="minecraft:bee_nest"
    ),

    # === Moduł: Fishtrap - brak w 1.18.2, placeholder ===
    "grcfishtrap:fish_trap": BlockMapping(
        id_1710="grcfishtrap:fish_trap",
        id_1182="minecraft:barrel"  # Placeholder - brak odpowiednika
    ),

    # === Moduł: Core ===
    "growthcraft:rope": BlockMapping(
        id_1710="growthcraft:rope",
        id_1182="growthcraft:rope"
    ),
    "growthcraft:fence_rope": BlockMapping(
        id_1710="growthcraft:fence_rope",
        id_1182="growthcraft:rope_fence"
    ),
    "growthcraft:salt_block": BlockMapping(
        id_1710="growthcraft:salt_block",
        id_1182="growthcraft:salt_block"
    ),

    # === Moduł: Bamboo ===
    "grcbamboo:bamboo": BlockMapping(
        id_1710="grcbamboo:bamboo",
        id_1182="growthcraft_bamboo:bamboo"
    ),
    "grcbamboo:bamboo_stalk": BlockMapping(
        id_1710="grcbamboo:bamboo_stalk",
        id_1182="growthcraft_bamboo:bamboo_stalk"
    ),
    "grcbamboo:bamboo_fence": BlockMapping(
        id_1710="grcbamboo:bamboo_fence",
        id_1182="growthcraft_bamboo:bamboo_fence"
    ),
    "grcbamboo:bamboo_door": BlockMapping(
        id_1710="grcbamboo:bamboo_door",
        id_1182="growthcraft_bamboo:bamboo_door"
    ),
    "grcbamboo:bamboo_slab": BlockMapping(
        id_1710="grcbamboo:bamboo_slab",
        id_1182="growthcraft_bamboo:bamboo_slab"
    ),
    "grcbamboo:bamboo_stairs": BlockMapping(
        id_1710="grcbamboo:bamboo_stairs",
        id_1182="growthcraft_bamboo:bamboo_stairs"
    ),

    # === Moduł: Rice ===
    "grcrice:paddy": BlockMapping(
        id_1710="grcrice:paddy",
        id_1182="growthcraft_rice:rice_crop"
    ),

    # === Moduł: Grapes/Hops (w cellar w 1.18.2) ===
    "grcgrapes:grape_vine": BlockMapping(
        id_1710="grcgrapes:grape_vine",
        id_1182="growthcraft_cellar:grape_vine_crop"
    ),
    "grchops:hops_vine": BlockMapping(
        id_1710="grchops:hops_vine",
        id_1182="growthcraft_cellar:hops_crop"
    ),
}


# Mapowania itemów GrowthCraft
ITEM_MAPPINGS: Dict[str, ItemMapping] = {
    # === Drożdże i kultury (Cellar) ===
    "grccellar:yeast": ItemMapping(
        id_1710="grccellar:yeast",
        id_1182="growthcraft_cellar:yeast"
    ),
    "grccellar:brewers_yeast": ItemMapping(
        id_1710="grccellar:brewers_yeast",
        id_1182="growthcraft_cellar:brewers_yeast"
    ),
    "grccellar:lager_yeast": ItemMapping(
        id_1710="grccellar:lager_yeast",
        id_1182="growthcraft_cellar:lager_yeast"
    ),
    "grccellar:bayanus_yeast": ItemMapping(
        id_1710="grccellar:bayanus_yeast",
        id_1182="growthcraft_cellar:bayanus_yeast"
    ),

    # === Butelki i alkohole (Cellar) ===
    "grccellar:bottle": ItemMapping(
        id_1710="grccellar:bottle",
        id_1182="growthcraft_cellar:bottle"
    ),
    "grccellar:bottle_apple_cider": ItemMapping(
        id_1710="grccellar:bottle_apple_cider",
        id_1182="growthcraft_cellar:bottle_apple_cider"
    ),
    "grccellar:bottle_wine": ItemMapping(
        id_1710="grccellar:bottle_wine",
        id_1182="growthcraft_cellar:bottle_wine"
    ),
    "grccellar:bottle_ale": ItemMapping(
        id_1710="grccellar:bottle_ale",
        id_1182="growthcraft_cellar:bottle_ale"
    ),
    "grccellar:bottle_lager": ItemMapping(
        id_1710="grccellar:bottle_lager",
        id_1182="growthcraft_cellar:bottle_lager"
    ),

    # === Pszczelarstwo (Apiary) ===
    "grcbees:bee": ItemMapping(
        id_1710="grcbees:bee",
        id_1182="growthcraft_apiary:bee"
    ),
    "grcbees:honey_comb": ItemMapping(
        id_1710="grcbees:honey_comb",
        id_1182="growthcraft_apiary:honey_comb_empty"
    ),
    "grcbees:honey_comb_full": ItemMapping(
        id_1710="grcbees:honey_comb_full",
        id_1182="growthcraft_apiary:honey_comb_full"
    ),
    "grcbees:honey_jar": ItemMapping(
        id_1710="grcbees:honey_jar",
        id_1182="growthcraft_apiary:honey_jar"
    ),
    "grcbees:bees_wax": ItemMapping(
        id_1710="grcbees:bees_wax",
        id_1182="growthcraft_apiary:bees_wax"
    ),

    # === Mleczarstwo (Milk) ===
    "grcmilk:rennet": ItemMapping(
        id_1710="grcmilk:rennet",
        id_1182="growthcraft_milk:rennet"
    ),
    "grcmilk:starter_culture": ItemMapping(
        id_1710="grcmilk:starter_culture",
        id_1182="growthcraft_milk:starter_culture"
    ),
    "grcmilk:butter": ItemMapping(
        id_1710="grcmilk:butter",
        id_1182="growthcraft_milk:butter"
    ),
    "grcmilk:cheese_cloth": ItemMapping(
        id_1710="grcmilk:cheese_cloth",
        id_1182="growthcraft_milk:cheese_cloth"
    ),
    "grcmilk:cheese": ItemMapping(
        id_1710="grcmilk:cheese",
        id_1182="growthcraft_milk:cheese"
    ),
    "grcmilk:yogurt": ItemMapping(
        id_1710="grcmilk:yogurt",
        id_1182="growthcraft_milk:yogurt"
    ),
    "grcmilk:ice_cream": ItemMapping(
        id_1710="grcmilk:ice_cream",
        id_1182="growthcraft_milk:ice_cream"
    ),

    # === Sery (różne typy) - Milk ===
    "grcmilk:cheddar_cheese": ItemMapping(
        id_1710="grcmilk:cheddar_cheese",
        id_1182="growthcraft_milk:cheddar_cheese"
    ),
    "grcmilk:cheddar_cheese_block": ItemMapping(
        id_1710="grcmilk:cheddar_cheese_block",
        id_1182="growthcraft_milk:cheddar_cheese_block"
    ),
    "grcmilk:gorgonzola_cheese": ItemMapping(
        id_1710="grcmilk:gorgonzola_cheese",
        id_1182="growthcraft_milk:gorgonzola_cheese"
    ),
    "grcmilk:emmentaler_cheese": ItemMapping(
        id_1710="grcmilk:emmentaler_cheese",
        id_1182="growthcraft_milk:emmentaler_cheese"
    ),
    "grcmilk:appenzeller_cheese": ItemMapping(
        id_1710="grcmilk:appenzeller_cheese",
        id_1182="growthcraft_milk:appenzeller_cheese"
    ),
    "grcmilk:asiago_cheese": ItemMapping(
        id_1710="grcmilk:asiago_cheese",
        id_1182="growthcraft_milk:asiago_cheese"
    ),
    "grcmilk:parmesan_cheese": ItemMapping(
        id_1710="grcmilk:parmesan_cheese",
        id_1182="growthcraft_milk:parmesan_cheese"
    ),
    "grcmilk:monterey_cheese": ItemMapping(
        id_1710="grcmilk:monterey_cheese",
        id_1182="growthcraft_milk:monterey_cheese"
    ),

    # === Akcesoria mleczarstwa (Milk) ===
    "grcmilk:stomach": ItemMapping(
        id_1710="grcmilk:stomach",
        id_1182="growthcraft_milk:stomach"
    ),
    "grcmilk:thistle": ItemMapping(
        id_1710="grcmilk:thistle",
        id_1182="growthcraft_milk:thistle"
    ),

    # === Owoce i zbiory (Apples/Cellar) ===
    "grcapples:apple": ItemMapping(
        id_1710="grcapples:apple",
        id_1182="growthcraft_apples:apple"
    ),
    "grcgrapes:grapes": ItemMapping(
        id_1710="grcgrapes:grapes",
        id_1182="growthcraft_cellar:grapes"
    ),
    "grcgrapes:grape_seeds": ItemMapping(
        id_1710="grcgrapes:grape_seeds",
        id_1182="growthcraft_cellar:grape_seeds"
    ),
    "grchops:hops": ItemMapping(
        id_1710="grchops:hops",
        id_1182="growthcraft_cellar:hops"
    ),
    "grchops:hop_seeds": ItemMapping(
        id_1710="grchops:hop_seeds",
        id_1182="growthcraft_cellar:hop_seeds"
    ),

    # === Ryż i produkty (Rice) ===
    "grcrice:rice": ItemMapping(
        id_1710="grcrice:rice",
        id_1182="growthcraft_rice:rice"
    ),
    "grcrice:rice_cooked": ItemMapping(
        id_1710="grcrice:rice_cooked",
        id_1182="growthcraft_rice:rice_cooked"
    ),
    "grcrice:sake": ItemMapping(
        id_1710="grcrice:sake",
        id_1182="growthcraft_rice:sake"
    ),

    # === Bambus ===
    "grcbamboo:bamboo": ItemMapping(
        id_1710="grcbamboo:bamboo",
        id_1182="growthcraft_bamboo:bamboo"
    ),
    "grcbamboo:bamboo_stalk": ItemMapping(
        id_1710="grcbamboo:bamboo_stalk",
        id_1182="growthcraft_bamboo:bamboo_stalk"
    ),
    "grcbamboo:bamboo_shoot": ItemMapping(
        id_1710="grcbamboo:bamboo_shoot",
        id_1182="growthcraft_bamboo:bamboo_shoot"
    ),
    "grcbamboo:bamboo_door": ItemMapping(
        id_1710="grcbamboo:bamboo_door",
        id_1182="growthcraft_bamboo:bamboo_door"
    ),

    # === Sól (Core) ===
    "growthcraft:salt": ItemMapping(
        id_1710="growthcraft:salt",
        id_1182="growthcraft:salt"
    ),

    # === Akcesoria browarnicze (Cellar) ===
    "grccellar:brew_kettle_lid": ItemMapping(
        id_1710="grccellar:brew_kettle_lid",
        id_1182="growthcraft_cellar:brew_kettle_lid"
    ),
    "grccellar:fruit_presser": ItemMapping(
        id_1710="grccellar:fruit_presser",
        id_1182="growthcraft_cellar:fruit_presser"
    ),
    "grccellar:grain": ItemMapping(
        id_1710="grccellar:grain",
        id_1182="growthcraft_cellar:grain"
    ),
    "grccellar:hops": ItemMapping(
        id_1710="grccellar:hops",
        id_1182="growthcraft_cellar:hops"
    ),
}


# Mapowania płynów GrowthCraft
FLUID_MAPPINGS: Dict[str, FluidMapping] = {
    # === Soki (Cellar) ===
    "grccellar:apple_juice": FluidMapping(
        id_1710="grccellar:apple_juice",
        id_1182="growthcraft_cellar:apple_juice"
    ),
    "grccellar:grape_juice": FluidMapping(
        id_1710="grccellar:grape_juice",
        id_1182="growthcraft_cellar:grape_juice"
    ),
    "grccellar:hop_infused_water": FluidMapping(
        id_1710="grccellar:hop_infused_water",
        id_1182="growthcraft_cellar:hop_infused_water"
    ),

    # === Alkohole (Cellar) ===
    "grccellar:apple_cider": FluidMapping(
        id_1710="grccellar:apple_cider",
        id_1182="growthcraft_cellar:apple_cider"
    ),
    "grccellar:wine": FluidMapping(
        id_1710="grccellar:wine",
        id_1182="growthcraft_cellar:wine"
    ),
    "grccellar:ale": FluidMapping(
        id_1710="grccellar:ale",
        id_1182="growthcraft_cellar:ale"
    ),
    "grccellar:lager": FluidMapping(
        id_1710="grccellar:lager",
        id_1182="growthcraft_cellar:lager"
    ),
    "grccellar:fermented_apple_juice": FluidMapping(
        id_1710="grccellar:fermented_apple_juice",
        id_1182="growthcraft_cellar:apple_cider"
    ),

    # === Brzeczki (Cellar) ===
    "grccellar:wort": FluidMapping(
        id_1710="grccellar:wort",
        id_1182="growthcraft_cellar:wort"
    ),
    "grccellar:young_wort": FluidMapping(
        id_1710="grccellar:young_wort",
        id_1182="growthcraft_cellar:young_wort"
    ),

    # === Mleko i produkty mleczne (Milk) ===
    "grcmilk:milk": FluidMapping(
        id_1710="grcmilk:milk",
        id_1182="growthcraft_milk:milk"
    ),
    "grcmilk:cream": FluidMapping(
        id_1710="grcmilk:cream",
        id_1182="growthcraft_milk:cream"
    ),
    "grcmilk:curds": FluidMapping(
        id_1710="grcmilk:curds",
        id_1182="growthcraft_milk:curds"
    ),
    "grcmilk:whey": FluidMapping(
        id_1710="grcmilk:whey",
        id_1182="growthcraft_milk:whey"
    ),
    "grcmilk:rennet": FluidMapping(
        id_1710="grcmilk:rennet",
        id_1182="growthcraft_milk:rennet"
    ),
    "grcmilk:butter_milk": FluidMapping(
        id_1710="grcmilk:butter_milk",
        id_1182="growthcraft_milk:butter_milk"
    ),
    "grcmilk:skim_milk": FluidMapping(
        id_1710="grcmilk:skim_milk",
        id_1182="growthcraft_milk:skim_milk"
    ),
    "grcmilk:pasteurized_milk": FluidMapping(
        id_1710="grcmilk:pasteurized_milk",
        id_1182="growthcraft_milk:pasteurized_milk"
    ),
    "grcmilk:ricotta": FluidMapping(
        id_1710="grcmilk:ricotta",
        id_1182="growthcraft_milk:ricotta"
    ),
    "grcmilk:kumis": FluidMapping(
        id_1710="grcmilk:kumis",
        id_1182="growthcraft_milk:kumis"
    ),

    # === Miód (Apiary) ===
    "grcbees:honey": FluidMapping(
        id_1710="grcbees:honey",
        id_1182="growthcraft_apiary:honey"
    ),
    "grcbees:honey_mead": FluidMapping(
        id_1710="grcbees:honey_mead",
        id_1182="growthcraft_apiary:honey_mead"
    ),

    # === Ryż i sake (Rice) ===
    "grcrice:rice_water": FluidMapping(
        id_1710="grcrice:rice_water",
        id_1182="growthcraft_rice:rice_water"
    ),
    "grcrice:rice_wine": FluidMapping(
        id_1710="grcrice:rice_wine",
        id_1182="growthcraft_rice:sake"
    ),
    "grcrice:sake": FluidMapping(
        id_1710="grcrice:sake",
        id_1182="growthcraft_rice:sake"
    ),

    # === Inne (Cellar) ===
    "grccellar:booze": FluidMapping(
        id_1710="grccellar:booze",
        id_1182="growthcraft_cellar:booze"
    ),
}


STRICT_BLOCK_MAPPINGS: Dict[str, BlockMapping] = {
    "grccellar:ferment_barrel": BlockMapping("grccellar:ferment_barrel", "brewinandchewin:keg"),
    "grccellar:brew_kettle": BlockMapping("grccellar:brew_kettle", "brewinandchewin:keg"),
    "grccellar:fruit_press": BlockMapping("grccellar:fruit_press", "create:mechanical_press"),
    "grccellar:culture_jar": BlockMapping("grccellar:culture_jar", "farmersdelight:cooking_pot"),
    "grccellar:roaster": BlockMapping("grccellar:roaster", "farmersdelight:cooking_pot"),
    "grcmilk:cheese_vat": BlockMapping("grcmilk:cheese_vat", "farmersdelight:cooking_pot"),
    "grcmilk:pancheon": BlockMapping("grcmilk:pancheon", "farmersdelight:cooking_pot"),
    "grcmilk:butter_churn": BlockMapping("grcmilk:butter_churn", "farmersdelight:cooking_pot"),
    "grcmilk:cheese_press": BlockMapping("grcmilk:cheese_press", "farmersdelight:cooking_pot"),
    "grcmilk:hanging_curds": BlockMapping("grcmilk:hanging_curds", "minecraft:white_wool"),
    "grcbees:bee_box": BlockMapping(
        "grcbees:bee_box",
        "productivebees:advanced_oak_beehive",
        metadata_map={
            0: "productivebees:advanced_oak_beehive",
            1: "productivebees:advanced_spruce_beehive",
            2: "productivebees:advanced_birch_beehive",
            3: "productivebees:advanced_jungle_beehive",
            4: "productivebees:advanced_acacia_beehive",
            5: "productivebees:advanced_dark_oak_beehive",
        }
    ),
    "grcbees:bee_hive": BlockMapping("grcbees:bee_hive", "minecraft:bee_nest"),
    "grcfishtrap:fish_trap": BlockMapping("grcfishtrap:fish_trap", "minecraft:barrel"),
    "growthcraft:rope": BlockMapping("growthcraft:rope", "supplementaries:rope"),
    "growthcraft:fence_rope": BlockMapping("growthcraft:fence_rope", "supplementaries:rope"),
    "growthcraft:salt_block": BlockMapping("growthcraft:salt_block", "mekanism:block_salt"),
    "grcbamboo:bamboo": BlockMapping("grcbamboo:bamboo", "minecraft:bamboo"),
    "grcbamboo:bamboo_stalk": BlockMapping("grcbamboo:bamboo_stalk", "minecraft:bamboo"),
    "grcbamboo:bamboo_fence": BlockMapping("grcbamboo:bamboo_fence", "minecraft:jungle_fence"),
    "grcbamboo:bamboo_door": BlockMapping("grcbamboo:bamboo_door", "minecraft:jungle_door"),
    "grcbamboo:bamboo_slab": BlockMapping("grcbamboo:bamboo_slab", "minecraft:jungle_slab"),
    "grcbamboo:bamboo_stairs": BlockMapping("grcbamboo:bamboo_stairs", "minecraft:jungle_stairs"),
    "grcrice:paddy": BlockMapping("grcrice:paddy", "farmersdelight:rice_crop"),
    "grcgrapes:grape_vine": BlockMapping("grcgrapes:grape_vine", "minecraft:vine"),
    "grchops:hops_vine": BlockMapping("grchops:hops_vine", "minecraft:vine"),
}


STRICT_ITEM_MAPPINGS: Dict[str, ItemMapping] = {
    "grccellar:yeast": ItemMapping("grccellar:yeast", "brewinandchewin:yeast"),
    "grccellar:brewers_yeast": ItemMapping("grccellar:brewers_yeast", "brewinandchewin:yeast"),
    "grccellar:lager_yeast": ItemMapping("grccellar:lager_yeast", "brewinandchewin:yeast"),
    "grccellar:bayanus_yeast": ItemMapping("grccellar:bayanus_yeast", "brewinandchewin:yeast"),
    "grccellar:bottle": ItemMapping("grccellar:bottle", "minecraft:glass_bottle"),
    "grccellar:bottle_apple_cider": ItemMapping("grccellar:bottle_apple_cider", "minecraft:glass_bottle"),
    "grccellar:bottle_wine": ItemMapping("grccellar:bottle_wine", "minecraft:glass_bottle"),
    "grccellar:bottle_ale": ItemMapping("grccellar:bottle_ale", "minecraft:glass_bottle"),
    "grccellar:bottle_lager": ItemMapping("grccellar:bottle_lager", "minecraft:glass_bottle"),
    "grccellar:grain": ItemMapping("grccellar:grain", "minecraft:wheat"),
    "grccellar:hops": ItemMapping("grccellar:hops", "minecraft:wheat_seeds"),
    "grcbees:bee": ItemMapping("grcbees:bee", "minecraft:bee_spawn_egg"),
    "grcbees:honey_comb": ItemMapping("grcbees:honey_comb", "minecraft:honeycomb"),
    "grcbees:honey_comb_full": ItemMapping("grcbees:honey_comb_full", "minecraft:honeycomb"),
    "grcbees:honey_jar": ItemMapping("grcbees:honey_jar", "minecraft:honey_bottle"),
    "grcbees:bees_wax": ItemMapping("grcbees:bees_wax", "productivebees:wax"),
    "grcmilk:rennet": ItemMapping("grcmilk:rennet", "minecraft:milk_bucket"),
    "grcmilk:starter_culture": ItemMapping("grcmilk:starter_culture", "minecraft:milk_bucket"),
    "grcmilk:butter": ItemMapping("grcmilk:butter", "farmersdelight:butter"),
    "grcmilk:cheese_cloth": ItemMapping("grcmilk:cheese_cloth", "minecraft:string"),
    "grcmilk:cheese": ItemMapping("grcmilk:cheese", "farmersdelight:milk_bottle"),
    "grcapples:apple": ItemMapping("grcapples:apple", "minecraft:apple"),
    "grcgrapes:grapes": ItemMapping("grcgrapes:grapes", "minecraft:sweet_berries"),
    "grcgrapes:grape_seeds": ItemMapping("grcgrapes:grape_seeds", "minecraft:sweet_berries"),
    "grchops:hops": ItemMapping("grchops:hops", "minecraft:wheat_seeds"),
    "grchops:hop_seeds": ItemMapping("grchops:hop_seeds", "minecraft:wheat_seeds"),
    "grcrice:rice": ItemMapping("grcrice:rice", "farmersdelight:rice"),
    "grcrice:rice_cooked": ItemMapping("grcrice:rice_cooked", "minecraft:bowl"),
    "grcrice:sake": ItemMapping("grcrice:sake", "minecraft:glass_bottle"),
    "grcbamboo:bamboo": ItemMapping("grcbamboo:bamboo", "minecraft:bamboo"),
    "grcbamboo:bamboo_stalk": ItemMapping("grcbamboo:bamboo_stalk", "minecraft:bamboo"),
    "grcbamboo:bamboo_shoot": ItemMapping("grcbamboo:bamboo_shoot", "minecraft:bamboo"),
    "grcbamboo:bamboo_door": ItemMapping("grcbamboo:bamboo_door", "minecraft:jungle_door"),
    "growthcraft:salt": ItemMapping("growthcraft:salt", "mekanism:salt"),
}


STRICT_FLUID_MAPPINGS: Dict[str, FluidMapping] = {
    fluid_id: FluidMapping(fluid_id, "minecraft:water")
    for fluid_id in FLUID_MAPPINGS.keys()
}


def _mapping_set(profile: str, strict: Dict[str, object], ce: Dict[str, object]) -> Dict[str, object]:
    if profile == GROWTHCRAFT_CE_EXPERIMENTAL:
        return ce
    return strict


def get_block_mapping(id_1710: str, profile: str = DEFAULT_PROFILE) -> Optional[BlockMapping]:
    """Zwraca mapowanie bloku dla podanego ID 1.7.10"""
    return _mapping_set(profile, STRICT_BLOCK_MAPPINGS, BLOCK_MAPPINGS).get(id_1710)


def get_item_mapping(id_1710: str, profile: str = DEFAULT_PROFILE) -> Optional[ItemMapping]:
    """Zwraca mapowanie itemu dla podanego ID 1.7.10"""
    return _mapping_set(profile, STRICT_ITEM_MAPPINGS, ITEM_MAPPINGS).get(id_1710)


def get_fluid_mapping(id_1710: str, profile: str = DEFAULT_PROFILE) -> Optional[FluidMapping]:
    """Zwraca mapowanie płynu dla podanego ID 1.7.10"""
    return _mapping_set(profile, STRICT_FLUID_MAPPINGS, FLUID_MAPPINGS).get(id_1710)


def convert_block_id(id_1710: str, metadata: int = 0, profile: str = DEFAULT_PROFILE) -> str:
    """
    Konwertuje ID bloku z 1.7.10 na 1.18.2
    
    Args:
        id_1710: ID bloku w formacie 1.7.10 (np. "grccellar:ferment_barrel")
        metadata: Metadata bloku (dla wariantów)
        
    Returns:
        ID bloku w formacie 1.18.2
    """
    mapping = get_block_mapping(id_1710, profile)
    if mapping:
        return mapping.get_1182_id(metadata)
    # Domyślnie zwróć oryginalne ID (może być już w formacie 1.18.2)
    return id_1710


def convert_item_id(id_1710: str, damage: int = 0, profile: str = DEFAULT_PROFILE) -> str:
    """
    Konwertuje ID itemu z 1.7.10 na 1.18.2
    
    Args:
        id_1710: ID itemu w formacie 1.7.10
        damage: Damage/metadata itemu
        
    Returns:
        ID itemu w formacie 1.18.2
    """
    mapping = get_item_mapping(id_1710, profile)
    if mapping:
        return mapping.get_1182_id(damage)
    # Domyślnie zwróć oryginalne ID
    return id_1710


def convert_fluid_id(id_1710: str, profile: str = DEFAULT_PROFILE) -> str:
    """
    Konwertuje ID płynu z 1.7.10 na 1.18.2
    
    Args:
        id_1710: ID płynu w formacie 1.7.10
        
    Returns:
        ID płynu w formacie 1.18.2
    """
    mapping = get_fluid_mapping(id_1710, profile)
    if mapping:
        return mapping.id_1182
    # Domyślnie zwróć oryginalne ID
    return id_1710


def get_all_growthcraft_blocks(profile: str = DEFAULT_PROFILE) -> List[str]:
    """Zwraca listę wszystkich bloków GrowthCraft 1.7.10"""
    return list(_mapping_set(profile, STRICT_BLOCK_MAPPINGS, BLOCK_MAPPINGS).keys())


def get_all_growthcraft_items(profile: str = DEFAULT_PROFILE) -> List[str]:
    """Zwraca listę wszystkich itemów GrowthCraft 1.7.10"""
    return list(_mapping_set(profile, STRICT_ITEM_MAPPINGS, ITEM_MAPPINGS).keys())


def get_all_growthcraft_fluids(profile: str = DEFAULT_PROFILE) -> List[str]:
    """Zwraca listę wszystkich płynów GrowthCraft 1.7.10"""
    return list(_mapping_set(profile, STRICT_FLUID_MAPPINGS, FLUID_MAPPINGS).keys())
