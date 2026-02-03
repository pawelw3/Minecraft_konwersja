"""
Block Mappings for Enchanting Plus - 1.7.10 to 1.18.2

Mapowanie ID bloków Enchanting Plus na Enchanting Infuser.
"""

from typing import Dict, Optional
from dataclasses import dataclass


@dataclass
class BlockMapping:
    """Reprezentuje mapowanie bloku między wersjami"""
    id_1710: str
    id_1182: str
    has_tile_entity: bool = True
    notes: str = ""


# Mapowanie bloków Enchanting Plus: 1.7.10 -> 1.18.2 (Enchanting Infuser)
BLOCK_MAPPINGS_1710_TO_1182: Dict[str, BlockMapping] = {
    # Podstawowy stół enchantujący (wybór enchantów)
    "EnchantingPlus:enchanting_table": BlockMapping(
        id_1710="EnchantingPlus:enchanting_table",
        id_1182="enchantinginfuser:enchanting_infuser",
        has_tile_entity=True,
        notes="Podstawowy infuser - wybór enchantów bez RNG"
    ),
    
    # Zaawansowany stół enchantujący (modyfikacja, naprawa, zdejmowanie)
    "EnchantingPlus:advanced_table": BlockMapping(
        id_1710="EnchantingPlus:advanced_table",
        id_1182="enchantinginfuser:advanced_enchanting_infuser",
        has_tile_entity=True,
        notes="Zaawansowany infuser - modyfikacja enchantów, naprawa, zdejmowanie"
    ),
    
    # Arcane Inscriber - konwersja książek na zwoje (BRAK ODPOWIEDNIKA w 1.18.2)
    # W Enchanting Infuser nie ma tej funkcjonalności - zwoje nie są potrzebne
    "EnchantingPlus:arcane_inscriber": BlockMapping(
        id_1710="EnchantingPlus:arcane_inscriber",
        id_1182="minecraft:air",  # Usunięcie - brak odpowiednika
        has_tile_entity=True,
        notes="Arcane Inscriber - BRAK ODPOWIEDNIKA w Enchanting Infuser. "
              "Funkcjonalność nie jest potrzebna (zwoje zastąpione enchanted books)."
    ),
}


# Zestaw wszystkich ID bloków Enchanting Plus 1.7.10
ALL_EP_BLOCK_IDS_1710 = set(BLOCK_MAPPINGS_1710_TO_1182.keys())

# Zestaw wszystkich ID bloków Enchanting Infuser 1.18.2
ALL_EI_BLOCK_IDS_1182 = {m.id_1182 for m in BLOCK_MAPPINGS_1710_TO_1182.values()}


def get_block_mapping(block_id_1710: str) -> Optional[BlockMapping]:
    """
    Zwraca mapowanie dla bloku 1.7.10.
    
    Args:
        block_id_1710: ID bloku w wersji 1.7.10
        
    Returns:
        BlockMapping lub None jeśli nie znaleziono
    """
    return BLOCK_MAPPINGS_1710_TO_1182.get(block_id_1710)


def is_enchantingplus_block(block_id: str) -> bool:
    """Sprawdza czy blok należy do Enchanting Plus"""
    return block_id in ALL_EP_BLOCK_IDS_1710


def get_block_name(block_id: str) -> str:
    """
    Zwraca nazwę bloku (bez namespace) na podstawie ID.
    
    Args:
        block_id: Pełne ID bloku (np. 'EnchantingPlus:enchanting_table')
        
    Returns:
        Nazwa bloku (np. 'enchanting_table') lub 'unknown' jeśli nieznane
    """
    if ':' in block_id:
        return block_id.split(':', 1)[1]
    return block_id if block_id else 'unknown'


def get_conversion_info() -> Dict[str, any]:
    """Zwraca informacje o mapowaniu konwersji"""
    return {
        "source_mod": "Enchanting Plus",
        "target_mod": "Enchanting Infuser",
        "source_version": "1.7.10",
        "target_version": "1.18.2",
        "total_blocks_mapped": len(BLOCK_MAPPINGS_1710_TO_1182),
        "blocks_converted": sum(1 for m in BLOCK_MAPPINGS_1710_TO_1182.values() 
                               if m.id_1182 != "minecraft:air"),
        "blocks_removed": sum(1 for m in BLOCK_MAPPINGS_1710_TO_1182.values() 
                             if m.id_1182 == "minecraft:air"),
        "mappings": [
            {
                "from": m.id_1710,
                "to": m.id_1182,
                "notes": m.notes
            }
            for m in BLOCK_MAPPINGS_1710_TO_1182.values()
        ]
    }
