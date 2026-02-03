"""
Mapowania bloków i itemów GrowthCraft 1.7.10 -> 1.18.2

Ten moduł zawiera mapowania dla:
- Bloków (BlockMappings)
- Itemów (ItemMappings)
- Płynów (FluidMappings)
"""

from typing import Dict, Optional, List
from dataclasses import dataclass


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


def get_block_mapping(id_1710: str) -> Optional[BlockMapping]:
    """Zwraca mapowanie bloku dla podanego ID 1.7.10"""
    return BLOCK_MAPPINGS.get(id_1710)


def get_item_mapping(id_1710: str) -> Optional[ItemMapping]:
    """Zwraca mapowanie itemu dla podanego ID 1.7.10"""
    return ITEM_MAPPINGS.get(id_1710)


def get_fluid_mapping(id_1710: str) -> Optional[FluidMapping]:
    """Zwraca mapowanie płynu dla podanego ID 1.7.10"""
    return FLUID_MAPPINGS.get(id_1710)


def convert_block_id(id_1710: str, metadata: int = 0) -> str:
    """
    Konwertuje ID bloku z 1.7.10 na 1.18.2
    
    Args:
        id_1710: ID bloku w formacie 1.7.10 (np. "grccellar:ferment_barrel")
        metadata: Metadata bloku (dla wariantów)
        
    Returns:
        ID bloku w formacie 1.18.2
    """
    mapping = get_block_mapping(id_1710)
    if mapping:
        return mapping.get_1182_id(metadata)
    # Domyślnie zwróć oryginalne ID (może być już w formacie 1.18.2)
    return id_1710


def convert_item_id(id_1710: str, damage: int = 0) -> str:
    """
    Konwertuje ID itemu z 1.7.10 na 1.18.2
    
    Args:
        id_1710: ID itemu w formacie 1.7.10
        damage: Damage/metadata itemu
        
    Returns:
        ID itemu w formacie 1.18.2
    """
    mapping = get_item_mapping(id_1710)
    if mapping:
        return mapping.get_1182_id(damage)
    # Domyślnie zwróć oryginalne ID
    return id_1710


def convert_fluid_id(id_1710: str) -> str:
    """
    Konwertuje ID płynu z 1.7.10 na 1.18.2
    
    Args:
        id_1710: ID płynu w formacie 1.7.10
        
    Returns:
        ID płynu w formacie 1.18.2
    """
    mapping = get_fluid_mapping(id_1710)
    if mapping:
        return mapping.id_1182
    # Domyślnie zwróć oryginalne ID
    return id_1710


def get_all_growthcraft_blocks() -> List[str]:
    """Zwraca listę wszystkich bloków GrowthCraft 1.7.10"""
    return list(BLOCK_MAPPINGS.keys())


def get_all_growthcraft_items() -> List[str]:
    """Zwraca listę wszystkich itemów GrowthCraft 1.7.10"""
    return list(ITEM_MAPPINGS.keys())


def get_all_growthcraft_fluids() -> List[str]:
    """Zwraca listę wszystkich płynów GrowthCraft 1.7.10"""
    return list(FLUID_MAPPINGS.keys())
