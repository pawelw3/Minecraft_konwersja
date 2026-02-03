"""
Base NBT Converter for Enchanting Plus

Bazowa klasa dla konwerterów NBT Enchanting Plus.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Dict, Any, Optional, List


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
    Bazowa klasa dla konwerterów NBT Enchanting Plus.
    
    Enchanting Plus ma prostsze NBT niż AE2 - głównie podstawowe
    dane TileEntity bez skomplikowanych struktur.
    """
    
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
    
    def _clean_base_nbt(self, nbt_1710: Dict[str, Any]) -> Dict[str, Any]:
        """
        Czyści podstawowe pola NBT z wartości specyficznych dla 1.7.10.
        
        Pola usuwane:
        - id: ID TileEntity (niepotrzebne w 1.18.2 - jest w BlockState)
        - x, y, z: Współrzędne (niepotrzebne w 1.18.2 - są w BlockEntity)
        """
        return {k: v for k, v in nbt_1710.items() 
                if k not in ['id', 'x', 'y', 'z']}
    
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
        """Kopiuje NBT bez zmian (bez pól specyficznych dla 1.7.10)"""
        converted = self._clean_base_nbt(nbt_1710)
        return self._create_result(converted)


class NullConverter(BaseNBTConverter):
    """
    Konwerter pusty - dla bloków które są usuwane (np. Arcane Inscriber).
    Zwraca pusty NBT - blok zostanie usunięty.
    """
    
    @property
    def converter_name(self) -> str:
        return "null"
    
    def convert(self, nbt_1710: Dict[str, Any], block_id: str = None) -> NBTConversionResult:
        """Zwraca pusty wynik - blok zostanie usunięty"""
        self._add_warning(f"Blok {block_id} nie ma odpowiednika w 1.18.2 - zostanie usunięty")
        return self._create_result({}, success=True)
