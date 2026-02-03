"""
Mapowania bloków i itemów EnderStorage 1.7.10 -> 1.18.2

Ten moduł zawiera mapowania dla:
- Bloków (BlockMappings)
- Itemów (ItemMappings)
- Kolorów (EnumColour)
- Frequency (konwersja int <-> EnumColour)
"""

from typing import Dict, Optional, List, Tuple
from dataclasses import dataclass
from enum import Enum
import uuid


class EnumColour(Enum):
    """Kolory dostępne w EnderStorage (0-15)"""
    WHITE = 0
    ORANGE = 1
    MAGENTA = 2
    LIGHT_BLUE = 3
    YELLOW = 4
    LIME = 5
    PINK = 6
    GRAY = 7
    LIGHT_GRAY = 8
    CYAN = 9
    PURPLE = 10
    BLUE = 11
    BROWN = 12
    GREEN = 13
    RED = 14
    BLACK = 15


@dataclass
class Frequency:
    """
    Reprezentacja częstotliwości w 1.18.2
    Zawiera 3 kolory (lewy, środkowy, prawy) i opcjonalnego właściciela
    """
    left: EnumColour = EnumColour.WHITE
    middle: EnumColour = EnumColour.WHITE
    right: EnumColour = EnumColour.WHITE
    owner: Optional[uuid.UUID] = None
    
    def to_int(self) -> int:
        """Konwersja do int (0-4095) jak w 1.7.10"""
        return (self.left.value << 8) | (self.middle.value << 4) | self.right.value
    
    @classmethod
    def from_int(cls, freq_int: int, owner: Optional[uuid.UUID] = None) -> 'Frequency':
        """Tworzy Frequency z int (format 1.7.10)"""
        left = EnumColour((freq_int >> 8) & 0xF)
        middle = EnumColour((freq_int >> 4) & 0xF)
        right = EnumColour(freq_int & 0xF)
        return cls(left=left, middle=middle, right=right, owner=owner)
    
    def to_nbt_1182(self) -> Dict[str, any]:
        """Konwertuje do formatu NBT 1.18.2"""
        result = {
            "left": self.left.name.lower(),
            "middle": self.middle.name.lower(),
            "right": self.right.name.lower()
        }
        if self.owner:
            result["owner"] = str(self.owner)
        return result
    
    @classmethod
    def from_nbt_1182(cls, nbt: Dict[str, any]) -> 'Frequency':
        """Tworzy Frequency z NBT 1.18.2"""
        left = EnumColour[nbt.get("left", "white").upper()]
        middle = EnumColour[nbt.get("middle", "white").upper()]
        right = EnumColour[nbt.get("right", "white").upper()]
        
        owner = None
        if "owner" in nbt:
            try:
                owner = uuid.UUID(nbt["owner"])
            except ValueError:
                pass
        
        return cls(left=left, middle=middle, right=right, owner=owner)
    
    def is_global(self) -> bool:
        """Czy to skrzynia/zbiornik globalny (bez właściciela)?"""
        return self.owner is None
    
    def get_storage_key(self) -> str:
        """
        Generuje klucz do storage backend.
        Format 1.18.2: "left,middle,right|owner_uuid" lub "left,middle,right|global"
        """
        colors = f"{self.left.name},{self.middle.name},{self.right.name}"
        if self.owner:
            return f"{colors}|{self.owner}"
        return f"{colors}|global"
    
    def __hash__(self):
        return hash(self.get_storage_key())
    
    def __eq__(self, other):
        if not isinstance(other, Frequency):
            return False
        return (self.left == other.left and 
                self.middle == other.middle and 
                self.right == other.right and
                self.owner == other.owner)


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


# Mapowania bloków EnderStorage
# W 1.7.10: jeden blok z metadata (0=chest, 1=tank)
# W 1.18.2: osobne bloki
BLOCK_MAPPINGS: Dict[str, BlockMapping] = {
    "EnderStorage:blockEnderStorage": BlockMapping(
        id_1710="EnderStorage:blockEnderStorage",
        id_1182="enderstorage:ender_chest",  # domyślnie chest
        metadata_map={
            0: "enderstorage:ender_chest",
            1: "enderstorage:ender_tank"
        }
    ),
}


# Mapowania itemów EnderStorage
ITEM_MAPPINGS: Dict[str, ItemMapping] = {
    "EnderStorage:enderPouch": ItemMapping(
        id_1710="EnderStorage:enderPouch",
        id_1182="enderstorage:ender_pouch"
    ),
}


# Mapowanie nazw kolorów (string -> EnumColour)
COLOUR_NAME_MAP: Dict[str, EnumColour] = {
    "white": EnumColour.WHITE,
    "orange": EnumColour.ORANGE,
    "magenta": EnumColour.MAGENTA,
    "light_blue": EnumColour.LIGHT_BLUE,
    "yellow": EnumColour.YELLOW,
    "lime": EnumColour.LIME,
    "pink": EnumColour.PINK,
    "gray": EnumColour.GRAY,
    "light_gray": EnumColour.LIGHT_GRAY,
    "cyan": EnumColour.CYAN,
    "purple": EnumColour.PURPLE,
    "blue": EnumColour.BLUE,
    "brown": EnumColour.BROWN,
    "green": EnumColour.GREEN,
    "red": EnumColour.RED,
    "black": EnumColour.BLACK,
}


def get_block_mapping(id_1710: str) -> Optional[BlockMapping]:
    """Zwraca mapowanie bloku dla podanego ID 1.7.10"""
    return BLOCK_MAPPINGS.get(id_1710)


def get_item_mapping(id_1710: str) -> Optional[ItemMapping]:
    """Zwraca mapowanie itemu dla podanego ID 1.7.10"""
    return ITEM_MAPPINGS.get(id_1710)


def convert_block_id(id_1710: str, metadata: int = 0) -> str:
    """
    Konwertuje ID bloku z 1.7.10 na 1.18.2
    
    Args:
        id_1710: ID bloku w formacie 1.7.10 (np. "EnderStorage:blockEnderStorage")
        metadata: Metadata bloku (0=chest, 1=tank)
        
    Returns:
        ID bloku w formacie 1.18.2
    """
    mapping = get_block_mapping(id_1710)
    if mapping:
        return mapping.get_1182_id(metadata)
    # Domyślnie zwróć oryginalne ID
    return id_1710


def convert_item_id(id_1710: str, damage: int = 0) -> str:
    """
    Konwertuje ID itemu z 1.7.10 na 1.18.2
    
    Args:
        id_1710: ID itemu w formacie 1.7.10
        damage: Damage/metadata itemu (dla EnderPouch = frequency)
        
    Returns:
        ID itemu w formacie 1.18.2
    """
    mapping = get_item_mapping(id_1710)
    if mapping:
        return mapping.get_1182_id(damage)
    # Domyślnie zwróć oryginalne ID
    return id_1710


def int_to_colours(freq_int: int) -> Tuple[EnumColour, EnumColour, EnumColour]:
    """
    Konwertuje int freq (1.7.10) na trzy kolory
    
    Args:
        freq_int: Wartość częstotliwości (0-4095)
        
    Returns:
        Tuple (left, middle, right) jako EnumColour
    """
    left = EnumColour((freq_int >> 8) & 0xF)
    middle = EnumColour((freq_int >> 4) & 0xF)
    right = EnumColour(freq_int & 0xF)
    return (left, middle, right)


def colours_to_int(left: EnumColour, middle: EnumColour, right: EnumColour) -> int:
    """
    Konwertuje trzy kolory na int freq (1.7.10)
    
    Args:
        left: Lewy kolor
        middle: Środkowy kolor
        right: Prawy kolor
        
    Returns:
        Wartość częstotliwości (0-4095)
    """
    return (left.value << 8) | (middle.value << 4) | right.value


def convert_frequency_nbt(freq_int: int, owner_str: str = "global") -> Dict[str, any]:
    """
    Konwertuje frequency z formatu 1.7.10 (int + owner string) 
    do formatu 1.18.2 (Frequency object)
    
    Args:
        freq_int: Wartość częstotliwości (0-4095)
        owner_str: Właściciel jako string ("global" lub nazwa gracza)
        
    Returns:
        Słownik Frequency w formacie 1.18.2
    """
    frequency = Frequency.from_int(freq_int)
    
    # Konwersja owner: w 1.7.10 to "global" lub nazwa gracza
    # W 1.18.2 to UUID lub null (global)
    if owner_str and owner_str != "global":
        # TODO: Lookup nazwy gracza -> UUID
        # Na razie zostawiamy jako global (None)
        pass
    
    return frequency.to_nbt_1182()


def get_all_enderstorage_blocks() -> List[str]:
    """Zwraca listę wszystkich bloków EnderStorage 1.7.10"""
    return list(BLOCK_MAPPINGS.keys())


def get_all_enderstorage_items() -> List[str]:
    """Zwraca listę wszystkich itemów EnderStorage 1.7.10"""
    return list(ITEM_MAPPINGS.keys())


def is_enderstorage_block(block_id: str) -> bool:
    """Sprawdza czy blok jest blokiem EnderStorage"""
    return block_id in BLOCK_MAPPINGS or block_id.startswith("EnderStorage:")


def is_enderstorage_item(item_id: str) -> bool:
    """Sprawdza czy item jest itemem EnderStorage"""
    return item_id in ITEM_MAPPINGS or item_id.startswith("EnderStorage:")
