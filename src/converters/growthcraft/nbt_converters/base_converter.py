"""
Bazowy konwerter NBT dla GrowthCraft

Definiuje wspólny interfejs i funkcjonalności dla wszystkich konwerterów NBT GrowthCraft.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Dict, Any, Optional, List, Tuple
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


class BaseGrowthcraftNBTConverter(ABC):
    """
    Bazowa klasa dla konwerterów NBT GrowthCraft.
    
    Wszystkie konwertery GrowthCraft dziedziczą po tej klasie
    i implementują metodę convert().
    """
    
    # Wersje obsługiwane przez konwerter
    SOURCE_VERSION = "1.7.10"
    TARGET_VERSION = "1.18.2"
    
    def __init__(self, profile: str = None):
        from ..mappings import GROWTHCRAFT_CE_EXPERIMENTAL

        self.profile = profile or GROWTHCRAFT_CE_EXPERIMENTAL
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
        
        from ..mappings import convert_item_id
        
        result = {
            'id': convert_item_id(item_nbt.get('id', ''), profile=self.profile),
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
                          slot_mapping: Optional[Dict[int, int]] = None) -> Dict[str, Any]:
        """
        Konwertuje inwentarz z formatu 1.7.10 do 1.18.2.
        
        1.7.10: lista slotów z 'Slot' jako klucz
        1.18.2: CompoundTag 'inventory' z 'Items' jako listą
        
        Args:
            items_list: Lista itemów w formacie 1.7.10
            slot_mapping: Opcjonalne mapowanie slotów (stary -> nowy)
            
        Returns:
            Słownik 'inventory' w formacie 1.18.2
        """
        if not items_list:
            return {'Size': 1, 'Items': []}
        
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
        
        # Znajdź maksymalny rozmiar inventory
        max_slot = max((item.get('Slot', 0) for item in items), default=0)
        size = max(max_slot + 1, 1)
        
        return {'Size': size, 'Items': items}
    
    def _convert_fluid_stack(self, fluid_nbt: Dict[str, Any]) -> Dict[str, Any]:
        """
        Konwertuje FluidStack z 1.7.10 do 1.18.2.
        
        Struktura w obu wersjach jest podobna:
        - FluidName: nazwa płynu
        - Amount: ilość w mB
        - Tag: opcjonalne NBT płynu
        """
        if not fluid_nbt:
            return {}
        
        from ..mappings import convert_fluid_id
        
        result = {
            'FluidName': convert_fluid_id(fluid_nbt.get('FluidName', ''), profile=self.profile),
            'Amount': fluid_nbt.get('Amount', 0)
        }
        
        # Zachowaj tag jeśli istnieje
        if 'Tag' in fluid_nbt:
            result['Tag'] = fluid_nbt['Tag']
        
        return result
    
    def _get_orientation(self, nbt: Dict[str, Any]) -> Optional[str]:
        """
        Ekstrahuje orientację z NBT 1.7.10.
        
        W 1.7.10: forward (byte), up (byte) - ForgeDirection
        W 1.18.2: BlockState properties (facing, itp.) - NIE w NBT BE!
        
        Returns:
            String z orientacją (north, south, east, west, up, down) lub None
        """
        forward = nbt.get('forward')
        if forward is not None:
            return self._forge_direction_to_facing(forward)
        return None
    
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
    
    def _facing_to_forge_direction(self, facing: str) -> int:
        """
        Konwertuje facing string do ForgeDirection (int).
        """
        directions = {
            "down": 0,
            "up": 1,
            "north": 2,
            "south": 3,
            "west": 4,
            "east": 5
        }
        return directions.get(facing, 2)
    
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


class IdentityGrowthcraftConverter(BaseGrowthcraftNBTConverter):
    """
    Konwerter tożsamościowy dla GrowthCraft - kopiowanie bez zmian.
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
