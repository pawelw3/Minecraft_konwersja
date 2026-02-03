"""
Bazowy konwerter NBT dla EnderStorage

Definiuje wspólny interfejs i funkcjonalności dla wszystkich konwerterów NBT EnderStorage.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Dict, Any, Optional, List
import sys
import os

# Dodaj ścieżkę do src dla importów
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..'))


@dataclass
class NBTConversionResult:
    """Wynik konwersji NBT"""
    success: bool
    converted_nbt: Optional[Dict[str, Any]] = None
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    
    def __post_init__(self):
        if self.errors is None:
            self.errors = []
        if self.warnings is None:
            self.warnings = []


class BaseEnderStorageNBTConverter(ABC):
    """
    Bazowa klasa dla konwerterów NBT EnderStorage.
    
    Wszystkie konwertery EnderStorage dziedziczą po tej klasie
    i implementują metodę convert().
    """
    
    # Wersje obsługiwane przez konwerter
    SOURCE_VERSION = "1.7.10"
    TARGET_VERSION = "1.18.2"
    
    def __init__(self):
        self.errors: List[str] = []
        self.warnings: List[str] = []
    
    @abstractmethod
    def convert(self, nbt_1710: Dict[str, Any], block_id: str = None,
                metadata: int = 0) -> NBTConversionResult:
        """
        Konwertuje NBT z wersji 1.7.10 do 1.18.2.
        
        Args:
            nbt_1710: Słownik NBT z wersji 1.7.10
            block_id: ID bloku (opcjonalnie, dla kontekstu)
            metadata: Metadata bloku (dla wariantów)
            
        Returns:
            NBTConversionResult z wynikiem konwersji
        """
        pass
    
    @property
    @abstractmethod
    def converter_name(self) -> str:
        """Zwraca nazwę konwertera"""
        pass
    
    @property
    @abstractmethod
    def source_te_id(self) -> str:
        """Zwraca ID Tile Entity w wersji 1.7.10"""
        pass
    
    @property
    @abstractmethod
    def target_te_id(self) -> str:
        """Zwraca ID Tile Entity w wersji 1.18.2"""
        pass
    
    def _convert_item_stack(self, item_nbt: Dict[str, Any]) -> Dict[str, Any]:
        """
        Konwertuje ItemStack z 1.7.10 do 1.18.2.
        
        Kluczowe różnice:
        - 1.7.10: id, Damage, Count, tag
        - 1.18.2: id, Count, tag (brak Damage w głównym NBT)
        """
        if not item_nbt:
            return {}
        
        result = {
            'id': item_nbt.get('id', ''),
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
    
    def _convert_inventory(self, items_list: List[Dict], 
                          slot_mapping: Optional[Dict[int, int]] = None) -> List[Dict]:
        """
        Konwertuje inwentarz z formatu 1.7.10 do 1.18.2.
        
        1.7.10: lista slotów z 'Slot' jako klucz
        1.18.2: Lista 'Items' z 'Slot' jako klucz (podobnie)
        
        Args:
            items_list: Lista itemów w formacie 1.7.10
            slot_mapping: Opcjonalne mapowanie slotów (stary -> nowy)
            
        Returns:
            Lista itemów w formacie 1.18.2
        """
        if not items_list:
            return []
        
        items = []
        for slot_data in items_list:
            if not slot_data:
                continue
            
            converted = self._convert_item_stack(slot_data)
            if converted:
                old_slot = slot_data.get('Slot', 0)
                # Mapowanie slotu jeśli podano
                new_slot = slot_mapping.get(old_slot, old_slot) if slot_mapping else old_slot
                converted['Slot'] = new_slot
                items.append(converted)
        
        return items
    
    def _convert_frequency(self, freq_int: int, owner_str: str = "global") -> Dict[str, Any]:
        """
        Konwertuje frequency z formatu 1.7.10 (int + owner string) 
        do formatu 1.18.2 (Frequency object)
        
        Args:
            freq_int: Wartość częstotliwości (0-4095)
            owner_str: Właściciel jako string ("global" lub nazwa gracza)
            
        Returns:
            Słownik Frequency w formacie 1.18.2
        """
        from ..mappings import EnumColour
        
        left = EnumColour((freq_int >> 8) & 0xF)
        middle = EnumColour((freq_int >> 4) & 0xF)
        right = EnumColour(freq_int & 0xF)
        
        result = {
            "left": left.name.lower(),
            "middle": middle.name.lower(),
            "right": right.name.lower()
        }
        
        # W 1.18.2 owner to UUID lub brak (global)
        # W 1.7.10 to "global" lub nazwa gracza
        # Na razie nie robimy lookupu nazwa -> UUID, zostawiamy global
        if owner_str and owner_str != "global":
            # TODO: Lookup nazwy gracza -> UUID
            self.warnings.append(f"Personal owner '{owner_str}' converted to global (UUID lookup not implemented)")
        
        return result
    
    def _create_result(self, converted_nbt: Optional[Dict[str, Any]] = None,
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


class IdentityEnderStorageConverter(BaseEnderStorageNBTConverter):
    """
    Konwerter tożsamościowy dla EnderStorage - kopiowanie bez zmian.
    Używany dla prostych bloków bez specjalnych danych NBT.
    """
    
    def __init__(self, source_id: str, target_id: str, name: str = "identity"):
        super().__init__()
        self._source_id = source_id
        self._target_id = target_id
        self._name = name
    
    @property
    def converter_name(self) -> str:
        return self._name
    
    @property
    def source_te_id(self) -> str:
        return self._source_id
    
    @property
    def target_te_id(self) -> str:
        return self._target_id
    
    def convert(self, nbt_1710: Dict[str, Any], block_id: str = None,
                metadata: int = 0) -> NBTConversionResult:
        """
        Kopiuje NBT bez zmian (bez orientacji - to jest w blockstate).
        
        Usuwa pola specyficzne dla 1.7.10 które nie są potrzebne w 1.18.2.
        """
        # Usuń pola specyficzne dla 1.7.10
        converted = {k: v for k, v in nbt_1710.items()
                    if k not in ['id', 'x', 'y', 'z', 'forward', 'up']}
        
        return self._create_result(converted)
