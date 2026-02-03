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
BLOCK_MAPPINGS: Dict[str, BlockMapping] = {
    # === Moduł: Cellar (Browarnictwo) ===
    "grccellar:ferment_barrel": BlockMapping(
        id_1710="grccellar:ferment_barrel",
        id_1182="growthcraft:fermentation_barrel"
    ),
    "grccellar:brew_kettle": BlockMapping(
        id_1710="grccellar:brew_kettle",
        id_1182="growthcraft:brew_kettle"
    ),
    "grccellar:fruit_press": BlockMapping(
        id_1710="grccellar:fruit_press",
        id_1182="growthcraft:fruit_press"
    ),
    "grccellar:culture_jar": BlockMapping(
        id_1710="grccellar:culture_jar",
        id_1182="growthcraft:culture_jar"
    ),
    
    # === Moduł: Milk (Mleczarstwo) ===
    "grcmilk:cheese_vat": BlockMapping(
        id_1710="grcmilk:cheese_vat",
        id_1182="growthcraft:mixing_vat"
    ),
    "grcmilk:pancheon": BlockMapping(
        id_1710="grcmilk:pancheon",
        id_1182="growthcraft:pancheon"
    ),
    "grcmilk:butter_churn": BlockMapping(
        id_1710="grcmilk:butter_churn",
        id_1182="growthcraft:churn"
    ),
    "grcmilk:cheese_press": BlockMapping(
        id_1710="grcmilk:cheese_press",
        id_1182="growthcraft:cheese_press"
    ),
    "grcmilk:hanging_curds": BlockMapping(
        id_1710="grcmilk:hanging_curds",
        id_1182="growthcraft:hanging_curds"
    ),
    
    # === Moduł: Bees (Pszczelarstwo) ===
    "grcbees:bee_box": BlockMapping(
        id_1710="grcbees:bee_box",
        id_1182="growthcraft:bee_box"
    ),
    "grcbees:bee_hive": BlockMapping(
        id_1710="grcbees:bee_hive",
        id_1182="growthcraft:bee_hive"
    ),
    
    # === Moduł: Fishtrap (Pułapki na ryby) ===
    "grcfishtrap:fish_trap": BlockMapping(
        id_1710="grcfishtrap:fish_trap",
        id_1182="growthcraft:fish_trap"
    ),
    
    # === Moduł: Core ===
    "growthcraft:rope": BlockMapping(
        id_1710="growthcraft:rope",
        id_1182="growthcraft:rope"
    ),
    "growthcraft:fence_rope": BlockMapping(
        id_1710="growthcraft:fence_rope",
        id_1182="growthcraft:fence_rope"
    ),
    "growthcraft:salt_block": BlockMapping(
        id_1710="growthcraft:salt_block",
        id_1182="growthcraft:salt_block"
    ),
    
    # === Moduł: Bamboo ===
    "grcbamboo:bamboo": BlockMapping(
        id_1710="grcbamboo:bamboo",
        id_1182="growthcraft:bamboo"
    ),
    "grcbamboo:bamboo_stalk": BlockMapping(
        id_1710="grcbamboo:bamboo_stalk",
        id_1182="growthcraft:bamboo_stalk"
    ),
    "grcbamboo:bamboo_fence": BlockMapping(
        id_1710="grcbamboo:bamboo_fence",
        id_1182="growthcraft:bamboo_fence"
    ),
    "grcbamboo:bamboo_door": BlockMapping(
        id_1710="grcbamboo:bamboo_door",
        id_1182="growthcraft:bamboo_door"
    ),
    "grcbamboo:bamboo_slab": BlockMapping(
        id_1710="grcbamboo:bamboo_slab",
        id_1182="growthcraft:bamboo_slab"
    ),
    "grcbamboo:bamboo_stairs": BlockMapping(
        id_1710="grcbamboo:bamboo_stairs",
        id_1182="growthcraft:bamboo_stairs"
    ),
}


# Mapowania itemów GrowthCraft
ITEM_MAPPINGS: Dict[str, ItemMapping] = {
    # === Drożdże i kultury ===
    "grccellar:yeast": ItemMapping(
        id_1710="grccellar:yeast",
        id_1182="growthcraft:yeast"
    ),
    "grccellar:brewers_yeast": ItemMapping(
        id_1710="grccellar:brewers_yeast",
        id_1182="growthcraft:brewers_yeast"
    ),
    "grccellar:lager_yeast": ItemMapping(
        id_1710="grccellar:lager_yeast",
        id_1182="growthcraft:lager_yeast"
    ),
    "grccellar:bayanus_yeast": ItemMapping(
        id_1710="grccellar:bayanus_yeast",
        id_1182="growthcraft:bayanus_yeast"
    ),
    
    # === Butelki i alkohole ===
    "grccellar:bottle": ItemMapping(
        id_1710="grccellar:bottle",
        id_1182="growthcraft:bottle"
    ),
    "grccellar:bottle_apple_cider": ItemMapping(
        id_1710="grccellar:bottle_apple_cider",
        id_1182="growthcraft:bottle_apple_cider"
    ),
    "grccellar:bottle_wine": ItemMapping(
        id_1710="grccellar:bottle_wine",
        id_1182="growthcraft:bottle_wine"
    ),
    "grccellar:bottle_ale": ItemMapping(
        id_1710="grccellar:bottle_ale",
        id_1182="growthcraft:bottle_ale"
    ),
    "grccellar:bottle_lager": ItemMapping(
        id_1710="grccellar:bottle_lager",
        id_1182="growthcraft:bottle_lager"
    ),
    
    # === Pszczelarstwo ===
    "grcbees:bee": ItemMapping(
        id_1710="grcbees:bee",
        id_1182="growthcraft:bee"
    ),
    "grcbees:honey_comb": ItemMapping(
        id_1710="grcbees:honey_comb",
        id_1182="growthcraft:honey_comb"
    ),
    "grcbees:honey_comb_full": ItemMapping(
        id_1710="grcbees:honey_comb_full",
        id_1182="growthcraft:honey_comb_full"
    ),
    "grcbees:honey_jar": ItemMapping(
        id_1710="grcbees:honey_jar",
        id_1182="growthcraft:honey_jar"
    ),
    "grcbees:bees_wax": ItemMapping(
        id_1710="grcbees:bees_wax",
        id_1182="growthcraft:bees_wax"
    ),
    
    # === Mleczarstwo ===
    "grcmilk:rennet": ItemMapping(
        id_1710="grcmilk:rennet",
        id_1182="growthcraft:rennet"
    ),
    "grcmilk:starter_culture": ItemMapping(
        id_1710="grcmilk:starter_culture",
        id_1182="growthcraft:starter_culture"
    ),
    "grcmilk:butter": ItemMapping(
        id_1710="grcmilk:butter",
        id_1182="growthcraft:butter"
    ),
    "grcmilk:cheese_cloth": ItemMapping(
        id_1710="grcmilk:cheese_cloth",
        id_1182="growthcraft:cheese_cloth"
    ),
    "grcmilk:cheese": ItemMapping(
        id_1710="grcmilk:cheese",
        id_1182="growthcraft:cheese"
    ),
    "grcmilk:yogurt": ItemMapping(
        id_1710="grcmilk:yogurt",
        id_1182="growthcraft:yogurt"
    ),
    "grcmilk:ice_cream": ItemMapping(
        id_1710="grcmilk:ice_cream",
        id_1182="growthcraft:ice_cream"
    ),
    
    # === Sery (różne typy) ===
    "grcmilk:cheddar_cheese": ItemMapping(
        id_1710="grcmilk:cheddar_cheese",
        id_1182="growthcraft:cheddar_cheese"
    ),
    "grcmilk:cheddar_cheese_block": ItemMapping(
        id_1710="grcmilk:cheddar_cheese_block",
        id_1182="growthcraft:cheddar_cheese_block"
    ),
    "grcmilk:gorgonzola_cheese": ItemMapping(
        id_1710="grcmilk:gorgonzola_cheese",
        id_1182="growthcraft:gorgonzola_cheese"
    ),
    "grcmilk:emmentaler_cheese": ItemMapping(
        id_1710="grcmilk:emmentaler_cheese",
        id_1182="growthcraft:emmentaler_cheese"
    ),
    "grcmilk:appenzeller_cheese": ItemMapping(
        id_1710="grcmilk:appenzeller_cheese",
        id_1182="growthcraft:appenzeller_cheese"
    ),
    "grcmilk:asiago_cheese": ItemMapping(
        id_1710="grcmilk:asiago_cheese",
        id_1182="growthcraft:asiago_cheese"
    ),
    "grcmilk:parmesan_cheese": ItemMapping(
        id_1710="grcmilk:parmesan_cheese",
        id_1182="growthcraft:parmesan_cheese"
    ),
    "grcmilk:monterey_cheese": ItemMapping(
        id_1710="grcmilk:monterey_cheese",
        id_1182="growthcraft:monterey_cheese"
    ),
    
    # === Akcesoria mleczarstwa ===
    "grcmilk:stomach": ItemMapping(
        id_1710="grcmilk:stomach",
        id_1182="growthcraft:stomach"
    ),
    "grcmilk:thistle": ItemMapping(
        id_1710="grcmilk:thistle",
        id_1182="growthcraft:thistle"
    ),
    
    # === Owoce i zbiory ===
    "grcapples:apple": ItemMapping(
        id_1710="grcapples:apple",
        id_1182="growthcraft:apple"
    ),
    "grcgrapes:grapes": ItemMapping(
        id_1710="grcgrapes:grapes",
        id_1182="growthcraft:grapes"
    ),
    "grcgrapes:grape_seeds": ItemMapping(
        id_1710="grcgrapes:grape_seeds",
        id_1182="growthcraft:grape_seeds"
    ),
    "grchops:hops": ItemMapping(
        id_1710="grchops:hops",
        id_1182="growthcraft:hops"
    ),
    "grchops:hop_seeds": ItemMapping(
        id_1710="grchops:hop_seeds",
        id_1182="growthcraft:hop_seeds"
    ),
    
    # === Ryż i produkty ===
    "grcrice:rice": ItemMapping(
        id_1710="grcrice:rice",
        id_1182="growthcraft:rice"
    ),
    "grcrice:rice_cooked": ItemMapping(
        id_1710="grcrice:rice_cooked",
        id_1182="growthcraft:rice_cooked"
    ),
    "grcrice:sake": ItemMapping(
        id_1710="grcrice:sake",
        id_1182="growthcraft:sake"
    ),
    
    # === Bambus ===
    "grcbamboo:bamboo": ItemMapping(
        id_1710="grcbamboo:bamboo",
        id_1182="growthcraft:bamboo"
    ),
    "grcbamboo:bamboo_stalk": ItemMapping(
        id_1710="grcbamboo:bamboo_stalk",
        id_1182="growthcraft:bamboo_stalk"
    ),
    "grcbamboo:bamboo_shoot": ItemMapping(
        id_1710="grcbamboo:bamboo_shoot",
        id_1182="growthcraft:bamboo_shoot"
    ),
    "grcbamboo:bamboo_door": ItemMapping(
        id_1710="grcbamboo:bamboo_door",
        id_1182="growthcraft:bamboo_door"
    ),
    
    # === Sól ===
    "growthcraft:salt": ItemMapping(
        id_1710="growthcraft:salt",
        id_1182="growthcraft:salt"
    ),
    
    # === Akcesoria browarnicze ===
    "grccellar:brew_kettle_lid": ItemMapping(
        id_1710="grccellar:brew_kettle_lid",
        id_1182="growthcraft:brew_kettle_lid"
    ),
    "grccellar:fruit_presser": ItemMapping(
        id_1710="grccellar:fruit_presser",
        id_1182="growthcraft:fruit_presser"
    ),
    "grccellar:grain": ItemMapping(
        id_1710="grccellar:grain",
        id_1182="growthcraft:grain"
    ),
    "grccellar:hops": ItemMapping(
        id_1710="grccellar:hops",
        id_1182="growthcraft:hops"
    ),
}


# Mapowania płynów GrowthCraft
FLUID_MAPPINGS: Dict[str, FluidMapping] = {
    # === Soki ===
    "grccellar:apple_juice": FluidMapping(
        id_1710="grccellar:apple_juice",
        id_1182="growthcraft:apple_juice"
    ),
    "grccellar:grape_juice": FluidMapping(
        id_1710="grccellar:grape_juice",
        id_1182="growthcraft:grape_juice"
    ),
    "grccellar:hop_infused_water": FluidMapping(
        id_1710="grccellar:hop_infused_water",
        id_1182="growthcraft:hop_infused_water"
    ),
    
    # === Alkohole ===
    "grccellar:apple_cider": FluidMapping(
        id_1710="grccellar:apple_cider",
        id_1182="growthcraft:apple_cider"
    ),
    "grccellar:wine": FluidMapping(
        id_1710="grccellar:wine",
        id_1182="growthcraft:wine"
    ),
    "grccellar:ale": FluidMapping(
        id_1710="grccellar:ale",
        id_1182="growthcraft:ale"
    ),
    "grccellar:lager": FluidMapping(
        id_1710="grccellar:lager",
        id_1182="growthcraft:lager"
    ),
    "grccellar:fermented_apple_juice": FluidMapping(
        id_1710="grccellar:fermented_apple_juice",
        id_1182="growthcraft:apple_cider"
    ),
    
    # === Brzeczki ===
    "grccellar:wort": FluidMapping(
        id_1710="grccellar:wort",
        id_1182="growthcraft:wort"
    ),
    "grccellar:young_wort": FluidMapping(
        id_1710="grccellar:young_wort",
        id_1182="growthcraft:young_wort"
    ),
    
    # === Mleko i produkty mleczne ===
    "grcmilk:milk": FluidMapping(
        id_1710="grcmilk:milk",
        id_1182="growthcraft:milk"
    ),
    "grcmilk:cream": FluidMapping(
        id_1710="grcmilk:cream",
        id_1182="growthcraft:cream"
    ),
    "grcmilk:curds": FluidMapping(
        id_1710="grcmilk:curds",
        id_1182="growthcraft:curds"
    ),
    "grcmilk:whey": FluidMapping(
        id_1710="grcmilk:whey",
        id_1182="growthcraft:whey"
    ),
    "grcmilk:rennet": FluidMapping(
        id_1710="grcmilk:rennet",
        id_1182="growthcraft:rennet"
    ),
    "grcmilk:butter_milk": FluidMapping(
        id_1710="grcmilk:butter_milk",
        id_1182="growthcraft:butter_milk"
    ),
    "grcmilk:skim_milk": FluidMapping(
        id_1710="grcmilk:skim_milk",
        id_1182="growthcraft:skim_milk"
    ),
    "grcmilk:pasteurized_milk": FluidMapping(
        id_1710="grcmilk:pasteurized_milk",
        id_1182="growthcraft:pasteurized_milk"
    ),
    "grcmilk:ricotta": FluidMapping(
        id_1710="grcmilk:ricotta",
        id_1182="growthcraft:ricotta"
    ),
    "grcmilk:kumis": FluidMapping(
        id_1710="grcmilk:kumis",
        id_1182="growthcraft:kumis"
    ),
    
    # === Miód ===
    "grcbees:honey": FluidMapping(
        id_1710="grcbees:honey",
        id_1182="growthcraft:honey"
    ),
    "grcbees:honey_mead": FluidMapping(
        id_1710="grcbees:honey_mead",
        id_1182="growthcraft:honey_mead"
    ),
    
    # === Ryż i sake ===
    "grcrice:rice_water": FluidMapping(
        id_1710="grcrice:rice_water",
        id_1182="growthcraft:rice_water"
    ),
    "grcrice:rice_wine": FluidMapping(
        id_1710="grcrice:rice_wine",
        id_1182="growthcraft:sake"
    ),
    "grcrice:sake": FluidMapping(
        id_1710="grcrice:sake",
        id_1182="growthcraft:sake"
    ),
    
    # === Inne ===
    "grccellar:booze": FluidMapping(
        id_1710="grccellar:booze",
        id_1182="growthcraft:booze"
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
