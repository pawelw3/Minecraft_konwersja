"""
Base NBT Converter for AE2

Bazowa klasa dla wszystkich konwerterów NBT AE2.
Definiuje interfejs i wspólne funkcjonalności.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Dict, Any, Optional, List, Tuple


@dataclass
class NBTConversionResult:
    """Wynik konwersji NBT"""
    success: bool
    converted_nbt: Optional[Dict[str, Any]] = None
    errors: List[str] = None
    warnings: List[str] = None
    
    def __post_init__(self):
        if self.errors is None:
            self.errors = []
        if self.warnings is None:
            self.warnings = []


class BaseNBTConverter(ABC):
    """
    Bazowa klasa dla konwerterów NBT AE2.
    
    Wszystkie konwertery powinny dziedziczyć po tej klasie
    i implementować metodę convert().
    """
    
    # Wersje obsługiwane przez konwerter
    SOURCE_VERSION = "1.7.10"
    TARGET_VERSION = "1.18.2"
    
    def __init__(self):
        self.errors: List[str] = []
        self.warnings: List[str] = []
    
    @abstractmethod
    def convert(self, nbt_1710: Dict[str, Any], block_id: str = None) -> NBTConversionResult:
        """
        Konwertuje NBT z wersji 1.7.10 do 1.18.2.
        
        Args:
            nbt_1710: Słownik NBT z wersji 1.7.10
            block_id: ID bloku (opcjonalnie, dla kontekstu)
            
        Returns:
            NBTConversionResult z wynikiem konwersji
        """
        pass
    
    @property
    @abstractmethod
    def converter_name(self) -> str:
        """Zwraca nazwę konwertera"""
        pass
    
    def _convert_item_stack(self, item_nbt: Dict[str, Any]) -> Dict[str, Any]:
        """
        Konwertuje ItemStack z 1.7.10 do 1.18.2.
        
        Kluczowe różnice:
        - 1.7.10: id, Damage, Count, tag
        - 1.18.2: id, Count, tag (brak Damage - w NBT)
        """
        if not item_nbt:
            return {}
        
        result = {
            'id': self._convert_item_id(item_nbt.get('id', '')),
            'Count': item_nbt.get('Count', 1)
        }
        
        # Konwersja metadata (Damage) do NBT
        damage = item_nbt.get('Damage', 0)
        tag = item_nbt.get('tag', {})
        
        if damage > 0 or tag:
            new_tag = dict(tag) if isinstance(tag, dict) else {}
            if damage > 0:
                new_tag['Damage'] = damage
            result['tag'] = new_tag
        
        return result
    
    def _convert_item_id(self, item_id_1710: str) -> str:
        """
        Konwertuje ID itemu z 1.7.10 do 1.18.2.
        
        Podstawowe mapowania:
        - appliedenergistics2:item.* -> ae2:*
        """
        from ..mappings import get_item_mapping
        
        mapping = get_item_mapping(item_id_1710)
        if mapping:
            return mapping.id_1182
        
        # Domyślna konwersja - zamiana prefixu
        if item_id_1710.startswith("appliedenergistics2:"):
            # Próba ekstrakcji nazwy
            parts = item_id_1710.split(":")
            if len(parts) > 1:
                name = parts[1].replace("item.Item", "").lower()
                return f"ae2:{name}"
        
        # Vanilla i inne mody - bez zmian
        return item_id_1710
    
    def _convert_inventory(self, inv_nbt: List[Dict], slots: int = None) -> Dict[str, Any]:
        """
        Konwertuje inwentarz z formatu 1.7.10 do 1.18.2.
        
        1.7.10: lista slotów z 'Slot' jako klucz
        1.18.2: słownik 'items' z pozycjami
        """
        if not inv_nbt:
            return {'items': []}
        
        items = []
        for slot_data in inv_nbt:
            if not slot_data:
                continue
            
            converted = self._convert_item_stack(slot_data)
            if converted:
                converted['Slot'] = slot_data.get('Slot', 0)
                items.append(converted)
        
        return {'items': items}
    
    def _get_orientation(self, nbt: Dict[str, Any]) -> Dict[str, Any]:
        """
        Ekstrahuje orientację z NBT 1.7.10.
        
        W 1.7.10: forward (byte), up (byte) - ForgeDirection
        W 1.18.2: Odpowiednio przekształcone
        """
        forward = nbt.get('forward', 0)
        up = nbt.get('up', 0)
        
        return {
            'forward': forward,
            'up': up,
            # W 1.18.2 może być inaczej zapisane
            'facing': self._forge_direction_to_facing(forward)
        }
    
    def _forge_direction_to_facing(self, direction: int) -> str:
        """
        Konwertuje ForgeDirection (int) do facing string.
        
        ForgeDirection:
        0: DOWN, 1: UP, 2: NORTH, 3: SOUTH, 4: WEST, 5: EAST
        """
        directions = {
            0: "down",
            1: "up",
            2: "north",
            3: "south",
            4: "west",
            5: "east"
        }
        return directions.get(direction, "north")
    
    def _create_result(self, converted_nbt: Dict[str, Any] = None, 
                       success: bool = True) -> NBTConversionResult:
        """Tworzy wynik konwersji"""
        return NBTConversionResult(
            success=success,
            converted_nbt=converted_nbt,
            errors=self.errors.copy(),
            warnings=self.warnings.copy()
        )
    
    def _add_error(self, message: str):
        """Dodaje błąd do listy"""
        self.errors.append(message)
    
    def _add_warning(self, message: str):
        """Dodaje ostrzeżenie do listy"""
        self.warnings.append(message)
    
    def reset(self):
        """Resetuje stan konwertera"""
        self.errors.clear()
        self.warnings.clear()


class IdentityConverter(BaseNBTConverter):
    """
    Konwerter tożsamościowy - kopiowanie bez zmian.
    Używany dla prostych bloków bez specjalnych danych NBT.
    """
    
    @property
    def converter_name(self) -> str:
        return "identity"
    
    def convert(self, nbt_1710: Dict[str, Any], block_id: str = None) -> NBTConversionResult:
        """Kopiuje NBT bez zmian"""
        # Usuń pola specyficzne dla 1.7.10 które nie są potrzebne w 1.18.2
        converted = {k: v for k, v in nbt_1710.items() 
                    if k not in ['id', 'x', 'y', 'z']}
        
        return self._create_result(converted)
