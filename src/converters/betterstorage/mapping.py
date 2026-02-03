"""
Mapowania dla konwertera Better Storage 1.7.10 → 1.18.2

UWAGI po weryfikacji kodu:
- ContainerMaterial jest TYLKO kosmetyczny (tekstury)
- Pojemność skrzyń zależy od configu (27/33/39 slotów), NIE od materiału
- Crate Pile ma dane w osobnych plikach (data/crates/)
- Iron Chests ma tylko 7 typów (brak emerald/silver/tin/zinc/steel)
"""

from typing import Dict, Tuple, Optional, Any


# Mapowanie bloków Better Storage na 1.18.2
# Format: 'betterstorage:block_name' -> ('target_modid:target_block', extra_params)
BLOCK_MAPPING: Dict[str, Tuple[str, Dict[str, Any]]] = {
    # Reinforced Chest → Iron Chests (NIE per materiał!)
    # Pojemność zależy od configu: 27(9x3) → copper, 33(11x3) → iron, 39(13x3) → iron
    'betterstorage:reinforcedChest': ('ironchest:iron_chest', {
        'note': 'Pojemność BS zależy od configu reinforcedColumns',
        'capacity_mapping': {
            27: 'ironchest:copper_chest',  # 45 slotów
            33: 'ironchest:iron_chest',    # 54 slotów
            39: 'ironchest:iron_chest',    # 54 slotów
        },
        'material_is_cosmetic': True,  # Materiał TYLKO do wyglądu
    }),
    
    # Reinforced Locker → Iron Chests / Barrel
    'betterstorage:reinforcedLocker': ('ironchest:iron_chest', {
        'note': '36 slotów → Iron Chest (54 slotów)',
        'material_is_cosmetic': True,
    }),
    
    # Locker → Barrel (pionowy) lub Chest
    'betterstorage:locker': ('minecraft:barrel', {
        'note': '36 slotów → Barrel (27) lub Iron Chest (54)',
        'alternative': 'ironchest:iron_chest',
        'vertical': True,
    }),
    
    # Crate → Vanilla Chest (NIE Storage Drawers!)
    # Zawartość w osobnych plikach data/crates/<id>.dat
    'betterstorage:crate': ('minecraft:chest', {
        'note': 'Crate Pile z osobnych plików!',
        'slots_per_crate': 18,
        'use_crate_pile_loader': True,
    }),
    
    # Cardboard Box → Packing Tape
    'betterstorage:cardboardBox': ('packingtape:packed', {
        'note': 'Inny system zużywania - taśma vs blok',
        'fallback': 'minecraft:chest',  # Jeśli Packing Tape niedostępny
    }),
    
    # Crafting Station → Crafting Station (ten sam mod)
    'betterstorage:craftingStation': ('craftingstation:crafting_station', {
        'note': 'Ten sam mod - sprawdzić kompatybilność NBT',
        'nbt_compatible': 'unknown',  # Do weryfikacji w Zadaniu 2
    }),
    
    # Armor Stand → Vanilla Armor Stand
    'betterstorage:armorStand': ('minecraft:armor_stand', {
        'note': 'Wypakować zawartość - vanilla nie ma GUI!',
        'extract_inventory': True,
    }),
    
    # Backpack → Sophisticated Backpacks (osobne zadanie)
    'betterstorage:backpack': ('sophisticatedbackpacks:backpack', {
        'note': 'Szczegóły w osobnym dokumencie',
        'separate_task': True,
    }),
    
    # Ender Backpack → Vanilla Ender Chest
    # Używa player.getInventoryEnderChest() - to vanilla!
    'betterstorage:enderBackpack': ('minecraft:ender_chest', {
        'note': 'Używa vanilla ender chest! Nie Ender Storage.',
        'is_access_block': True,  # To tylko "dostęp", nie storage
    }),
    
    # Present → Vanilla Chest + tabliczka
    'betterstorage:present': ('minecraft:chest', {
        'note': 'Funkcja ozdobna tracona - dodać tabliczkę',
        'add_sign': True,
    }),
    
    # Lockable Door → Supplementaries Lock lub Vanilla Door
    'betterstorage:lockableDoor': ('minecraft:oak_door', {
        'note': 'Funkcja zamka tracona - alternatywa: supplementaries:lock_block',
        'alternative': 'supplementaries:locked_door',
    }),
    
    # Flint Block → Stone (placeholder)
    'betterstorage:flintBlock': ('minecraft:stone', {
        'note': 'Blok dekoracyjny - placeholder',
    }),
}


# Mapowanie itemów
ITEM_MAPPING: Dict[str, Tuple[str, Dict[str, Any]]] = {
    # Lock & Key System
    'betterstorage:lock': ('lockandkey:lock', {
        'note': 'Funkcjonalność podobna - weryfikacja w 1.18.2',
    }),
    'betterstorage:key': ('lockandkey:key', {
        'note': 'Funkcjonalność podobna',
    }),
    'betterstorage:keyring': (None, {
        'note': 'Brak odpowiednika - pominąć',
        'skip': True,
    }),
    'betterstorage:masterKey': (None, {
        'note': 'Brak odpowiednika - pominąć',
        'skip': True,
    }),
    
    # Cardboard items
    'betterstorage:cardboardSheet': ('minecraft:paper', {
        'note': 'Fallback na papier',
    }),
    'betterstorage:cardboardHelmet': ('minecraft:leather_helmet', {
        'note': 'Fallback na skórzaną zbroję',
    }),
    'betterstorage:cardboardChestplate': ('minecraft:leather_chestplate', {
        'note': 'Fallback na skórzaną zbroję',
    }),
    'betterstorage:cardboardLeggings': ('minecraft:leather_leggings', {
        'note': 'Fallback na skórzaną zbroję',
    }),
    'betterstorage:cardboardBoots': ('minecraft:leather_boots', {
        'note': 'Fallback na skórzaną zbroję',
    }),
    'betterstorage:cardboardSword': ('minecraft:wooden_sword', {
        'note': 'Fallback na drewnianą broń',
    }),
    'betterstorage:cardboardPickaxe': ('minecraft:wooden_pickaxe', {
        'note': 'Fallback na drewniane narzędzie',
    }),
    'betterstorage:cardboardShovel': ('minecraft:wooden_shovel', {
        'note': 'Fallback na drewniane narzędzie',
    }),
    'betterstorage:cardboardAxe': ('minecraft:wooden_axe', {
        'note': 'Fallback na drewniane narzędzie',
    }),
    'betterstorage:cardboardHoe': ('minecraft:wooden_hoe', {
        'note': 'Fallback na drewniane narzędzie',
    }),
    
    # Gadżety
    'betterstorage:drinkingHelmet': (None, {
        'note': 'Brak odpowiednika',
        'skip': True,
    }),
    'betterstorage:bucketSlime': ('minecraft:slime_ball', {
        'note': 'Konwertować na slime ball + bucket',
        'give_bucket': True,
    }),
    'betterstorage:presentBook': (None, {
        'note': 'Brak odpowiednika - funkcja opakowywania',
        'skip': True,
    }),
}


# Mapowanie kolorów (int RGB → DyeColor string)
# BS używa int, 1.18.2 używa enum DyeColor
COLOR_MAPPING: Dict[int, Optional[str]] = {
    -1: None,           # Brak koloru
    0: 'white',
    1: 'orange',
    2: 'magenta',
    3: 'light_blue',
    4: 'yellow',
    5: 'lime',
    6: 'pink',
    7: 'gray',
    8: 'light_gray',
    9: 'cyan',
    10: 'purple',
    11: 'blue',
    12: 'brown',
    13: 'green',
    14: 'red',
    15: 'black',
}

# Reverse mapping (nazwa → int)
COLOR_NAME_TO_INT: Dict[str, int] = {
    'white': 0,
    'orange': 1,
    'magenta': 2,
    'light_blue': 3,
    'yellow': 4,
    'lime': 5,
    'pink': 6,
    'gray': 7,
    'light_gray': 8,
    'cyan': 9,
    'purple': 10,
    'blue': 11,
    'brown': 12,
    'green': 13,
    'red': 14,
    'black': 15,
}


def convert_color_to_dye_color(color_int: int) -> Optional[str]:
    """Konwertuje int koloru BS na string DyeColor 1.18.2"""
    return COLOR_MAPPING.get(color_int)


def convert_color_to_int(color_name: str) -> int:
    """Konwertuje nazwę koloru na int BS"""
    return COLOR_NAME_TO_INT.get(color_name, -1)


# Mapowanie orientacji
# BS 1.7.10: byte 0-5 (ForgeDirection)
# 1.18.2: String "north", "south", "east", "west"
ORIENTATION_MAPPING: Dict[int, str] = {
    0: 'down',      # Y-
    1: 'up',        # Y+
    2: 'north',     # Z-
    3: 'south',     # Z+
    4: 'west',      # X-
    5: 'east',      # X+
}

# Reverse mapping (dla niektórych zastosowań)
DIRECTION_TO_BYTE: Dict[str, int] = {
    'down': 0,
    'up': 1,
    'north': 2,
    'south': 3,
    'west': 4,
    'east': 5,
}


def convert_orientation(byte_orientation: int) -> str:
    """Konwertuje byte orientation BS na string 1.18.2"""
    return ORIENTATION_MAPPING.get(byte_orientation, 'north')


def convert_orientation_to_byte(direction: str) -> int:
    """Konwertuje string direction na byte BS"""
    return DIRECTION_TO_BYTE.get(direction, 2)


# Materiały dla Reinforced Chest/Locker (Tylko kosmetyka!)
# Używane w polu Material NBT - TYLKO dla informacji, NIE wpływa na pojemność
CONTAINER_MATERIALS: Dict[str, Dict[str, Any]] = {
    'iron': {
        'ore_dict': 'ingotIron',
        'block': 'minecraft:iron_block',
        'info': 'Standardowy materiał',
    },
    'gold': {
        'ore_dict': 'ingotGold',
        'block': 'minecraft:gold_block',
        'info': 'Dekoracyjny',
    },
    'diamond': {
        'ore_dict': 'gemDiamond',
        'block': 'minecraft:diamond_block',
        'info': 'Dekoracyjny',
    },
    'emerald': {
        'ore_dict': 'gemEmerald',
        'block': 'minecraft:emerald_block',
        'info': 'Dekoracyjny - Iron Chests NIE ma emerald!',
        'warning': 'No emerald chest in IronChests',
    },
    'copper': {
        'ore_dict': 'ingotCopper',
        'block': 'minecraft:copper_block',
        'info': 'Dekoracyjny',
    },
    'tin': {
        'ore_dict': 'ingotTin',
        'block': 'blockTin',
        'info': 'Dekoracyjny - Iron Chests NIE ma tin!',
        'warning': 'No tin chest in IronChests',
    },
    'silver': {
        'ore_dict': 'ingotSilver',
        'block': 'blockSilver',
        'info': 'Dekoracyjny - Iron Chests NIE ma silver!',
        'warning': 'No silver chest in IronChests',
    },
    'zinc': {
        'ore_dict': 'ingotZinc',
        'block': 'blockZinc',
        'info': 'Dekoracyjny - Iron Chests NIE ma zinc!',
        'warning': 'No zinc chest in IronChests',
    },
    'steel': {
        'ore_dict': 'ingotSteel',
        'block': 'blockSteel',
        'info': 'Dekoracyjny - Iron Chests NIE ma steel!',
        'warning': 'No steel chest in IronChests',
    },
}


def get_material_info(material: str) -> Dict[str, Any]:
    """Pobiera informacje o materiale (kosmetycznym!)"""
    return CONTAINER_MATERIALS.get(material, {
        'ore_dict': None,
        'block': None,
        'info': 'Unknown material',
    })


# Enchanty Better Storage (wszystkie tracone)
BS_ENCHANTMENTS: Dict[int, Dict[str, Any]] = {
    170: {
        'name': 'Unlocking',
        'max_level': 3,
        'effect': 'Otwieranie bez zużycia klucza',
        'conversion': None,
    },
    171: {
        'name': 'Lockpicking',
        'max_level': 5,
        'effect': 'Zwiększa szansę na otwarcie bez klucza',
        'conversion': None,
    },
    172: {
        'name': 'Morphing',
        'max_level': 1,
        'effect': 'Zmienia wygląd zamka',
        'conversion': None,
    },
    173: {
        'name': 'Persistence',
        'max_level': 3,
        'effect': 'Zwiększa odporność na wybuchy',
        'conversion': None,
    },
    174: {
        'name': 'Security',
        'max_level': 1,
        'effect': 'Blokuje otwieranie bez klucza',
        'conversion': None,
    },
    175: {
        'name': 'Shock',
        'max_level': 3,
        'effect': 'Poraża przy próbie włamania',
        'conversion': None,
    },
    176: {
        'name': 'Trigger',
        'max_level': 1,
        'effect': 'Wyzwala redstone przy włamaniu',
        'conversion': None,
    },
}


# Konfiguracja pojemności (z GlobalConfig.java BS)
# reinforcedColumns: 9, 11, 13 (domyślnie 13)
REINFORCED_CHEST_CAPACITIES: Dict[int, int] = {
    9: 27,   # 9×3
    11: 33,  # 11×3
    13: 39,  # 13×3
}


def get_reinforced_chest_capacity(columns: int) -> int:
    """
    Zwraca pojemność Reinforced Chest na podstawie configu.
    
    Args:
        columns: Liczba kolumn (9, 11, lub 13)
        
    Returns:
        Pojemność w slotach
    """
    return REINFORCED_CHEST_CAPACITIES.get(columns, 39)


def get_iron_chest_type_for_capacity(bs_capacity: int) -> str:
    """
    Zwraca typ Iron Chests odpowiedni dla pojemności BS.
    
    Args:
        bs_capacity: Pojemność BS (27, 33, lub 39)
        
    Returns:
        ID bloku Iron Chests
    """
    mapping = {
        27: 'ironchest:copper_chest',  # 45 slotów
        33: 'ironchest:iron_chest',    # 54 slotów
        39: 'ironchest:iron_chest',    # 54 slotów
    }
    return mapping.get(bs_capacity, 'ironchest:iron_chest')


# Sloty dla poszczególnych typów kontenerów
CONTAINER_SLOTS: Dict[str, int] = {
    'minecraft:chest': 27,
    'minecraft:barrel': 27,
    'ironchest:copper_chest': 45,
    'ironchest:iron_chest': 54,
    'ironchest:gold_chest': 81,
    'ironchest:diamond_chest': 108,
    'ironchest:crystal_chest': 108,
    'ironchest:obsidian_chest': 108,
    'ironchest:dirt_chest': 1,
}


def get_container_slots(block_id: str) -> int:
    """Zwraca liczbę slotów dla danego kontenera"""
    return CONTAINER_SLOTS.get(block_id, 27)
