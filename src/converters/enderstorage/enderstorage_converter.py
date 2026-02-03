"""
Główny konwerter EnderStorage dla Minecraft 1.7.10 -> 1.18.2

Ten moduł zawiera główną klasę konwertera dla wszystkich bloków i Tile Entities
z moda EnderStorage.
"""

import sys
import os
from typing import Dict, Any, Optional, List, Tuple
from dataclasses import dataclass, field

# Dodaj ścieżkę do src dla importów
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from .mappings import (
    get_block_mapping,
    convert_block_id,
    convert_item_id,
    is_enderstorage_block,
    is_enderstorage_item,
    Frequency,
    EnumColour,
)
from .nbt_converters import (
    EnderChestNBTConverter,
    EnderTankNBTConverter,
)
from .nbt_converters.base_converter import NBTConversionResult


@dataclass
class ConversionResult:
    """Wynik konwersji bloku/TE EnderStorage"""
    success: bool
    block_id_1182: Optional[str] = None
    nbt_1182: Optional[Dict[str, Any]] = None
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    
    def __post_init__(self):
        if self.errors is None:
            self.errors = []
        if self.warnings is None:
            self.warnings = []


class EnderStorageConverter:
    """
    Główny konwerter dla moda EnderStorage.
    
    Obsługuje konwersję wszystkich bloków i Tile Entities z EnderStorage 1.7.10
    do formatu 1.18.2.
    
    Użycie:
        converter = EnderStorageConverter()
        result = converter.convert_block(
            block_id="EnderStorage:blockEnderStorage",
            metadata=0,
            nbt=nbt_data_1710
        )
        
        if result.success:
            print(f"Nowe ID: {result.block_id_1182}")
            print(f"Nowe NBT: {result.nbt_1182}")
    """
    
    # Mapowanie ID Tile Entity -> Konwerter NBT
    # UWAGA: Na mapie 1.7.10 TE ID to "Ender Chest" i "Ender Tank" (ze spacja!)
    # Nie "TileEnderChest"/"TileEnderTank" jak w kodzie źródłowym Java
    TE_CONVERTERS = {
        # Ender Chest (na mapie: id="Ender Chest")
        "Ender Chest": EnderChestNBTConverter,
        # Ender Tank (na mapie: id="Ender Tank")
        "Ender Tank": EnderTankNBTConverter,
        # Dla kompatybilności z nazewnictwem w kodzie źródłowym
        "TileEnderChest": EnderChestNBTConverter,
        "TileEnderTank": EnderTankNBTConverter,
    }
    
    def __init__(self):
        self.errors: List[str] = []
        self.warnings: List[str] = []
        self.stats = {
            "processed": 0,
            "converted": 0,
            "failed": 0,
            "warnings": 0,
        }
    
    def convert_block(self, block_id: str, metadata: int = 0,
                     nbt: Optional[Dict[str, Any]] = None) -> ConversionResult:
        """
        Konwertuje blok EnderStorage z 1.7.10 do 1.18.2.
        
        Args:
            block_id: ID bloku w formacie 1.7.10 (np. "EnderStorage:blockEnderStorage")
            metadata: Metadata bloku (0=chest, 1=tank)
            nbt: Opcjonalne NBT Tile Entity
            
        Returns:
            ConversionResult z wynikiem konwersji
        """
        self.stats["processed"] += 1
        
        # Sprawdź czy to blok EnderStorage
        if not self.is_enderstorage_block(block_id):
            self.stats["failed"] += 1
            return ConversionResult(
                success=False,
                errors=[f"Blok {block_id} nie jest blokiem EnderStorage"]
            )
        
        # Konwertuj ID bloku
        block_id_1182 = convert_block_id(block_id, metadata)
        
        # Jeśli nie ma NBT, zwróć tylko konwersję ID
        if not nbt:
            self.stats["converted"] += 1
            return ConversionResult(
                success=True,
                block_id_1182=block_id_1182,
                nbt_1182=None
            )
        
        # Konwertuj NBT jeśli dostępne
        nbt_result = self._convert_nbt(block_id, nbt, metadata)
        
        if nbt_result.success:
            self.stats["converted"] += 1
            self.stats["warnings"] += len(nbt_result.warnings)
            
            return ConversionResult(
                success=True,
                block_id_1182=block_id_1182,
                nbt_1182=nbt_result.converted_nbt,
                warnings=nbt_result.warnings
            )
        else:
            self.stats["failed"] += 1
            return ConversionResult(
                success=False,
                block_id_1182=block_id_1182,
                errors=nbt_result.errors,
                warnings=nbt_result.warnings
            )
    
    def convert_tile_entity(self, te_id: str, nbt: Dict[str, Any],
                           metadata: int = 0) -> ConversionResult:
        """
        Konwertuje Tile Entity EnderStorage.
        
        Alias dla convert_block dla jasności.
        """
        return self.convert_block(te_id, metadata, nbt)
    
    def _convert_nbt(self, block_id: str, nbt: Dict[str, Any],
                    metadata: int = 0) -> NBTConversionResult:
        """
        Konwertuje NBT używając odpowiedniego konwertera.
        
        Wybiera konwerter na podstawie ID Tile Entity (nie block_id).
        """
        # Pobierz ID Tile Entity z NBT
        te_id = nbt.get('id', '')
        
        # Znajdź odpowiedni konwerter na podstawie TE ID
        converter_class = self.TE_CONVERTERS.get(te_id)
        
        if not converter_class:
            # Brak specyficznego konwertera - użyj tożsamości
            self.warnings.append(f"Brak specyficznego konwertera dla TE '{te_id}', używam tożsamości")
            from .nbt_converters.base_converter import IdentityEnderStorageConverter
            converter = IdentityEnderStorageConverter(
                source_id=te_id,
                target_id=convert_block_id(block_id, metadata),
                name="identity_fallback"
            )
            return converter.convert(nbt, block_id, metadata)
        
        # Utwórz instancję konwertera i wykonaj konwersję
        converter = converter_class()
        return converter.convert(nbt, block_id, metadata)
    
    def is_enderstorage_block(self, block_id: str) -> bool:
        """Sprawdza czy blok jest blokiem EnderStorage"""
        return is_enderstorage_block(block_id)
    
    def is_enderstorage_item(self, item_id: str) -> bool:
        """Sprawdza czy item jest itemem EnderStorage"""
        return is_enderstorage_item(item_id)
    
    def convert_item(self, item_id: str, damage: int = 0, 
                    nbt: Optional[Dict[str, Any]] = None) -> ConversionResult:
        """
        Konwertuje item EnderStorage.
        
        Specjalna obsługa dla EnderPouch - konwersja damage (freq) do NBT.
        
        Args:
            item_id: ID itemu w formacie 1.7.10
            damage: Damage/metadata (dla EnderPouch = frequency int)
            nbt: Opcjonalne NBT itemu
            
        Returns:
            ConversionResult z wynikiem konwersji
        """
        self.stats["processed"] += 1
        
        # Konwertuj ID itemu
        item_id_1182 = convert_item_id(item_id, damage)
        
        # Specjalna obsługa dla EnderPouch
        if item_id == "EnderStorage:enderPouch" or item_id.endswith("enderPouch"):
            # W 1.7.10: damage = freq (int)
            # W 1.18.2: NBT Frequency
            converted_nbt = nbt.copy() if nbt else {}
            
            # Konwertuj damage (freq) do Frequency
            frequency = Frequency.from_int(damage & 0xFFF)
            converted_nbt['Frequency'] = frequency.to_nbt_1182()
            
            self.stats["converted"] += 1
            return ConversionResult(
                success=True,
                block_id_1182=item_id_1182,
                nbt_1182=converted_nbt
            )
        
        # Dla innych itemów - zwykła konwersja
        self.stats["converted"] += 1
        return ConversionResult(
            success=True,
            block_id_1182=item_id_1182,
            nbt_1182=nbt
        )
    
    def get_supported_blocks(self) -> List[str]:
        """Zwraca listę obsługiwanych bloków EnderStorage"""
        from .mappings import get_all_enderstorage_blocks
        return get_all_enderstorage_blocks()
    
    def get_supported_items(self) -> List[str]:
        """Zwraca listę obsługiwanych itemów EnderStorage"""
        from .mappings import get_all_enderstorage_items
        return get_all_enderstorage_items()
    
    def get_stats(self) -> Dict[str, int]:
        """Zwraca statystyki konwersji"""
        return self.stats.copy()
    
    def reset_stats(self):
        """Resetuje statystyki konwersji"""
        self.stats = {
            "processed": 0,
            "converted": 0,
            "failed": 0,
            "warnings": 0,
        }
    
    def convert_frequency(self, freq_int: int, owner: str = "global") -> Dict[str, Any]:
        """
        Pomocnicza metoda do konwersji frequency.
        
        Args:
            freq_int: Wartość częstotliwości (0-4095)
            owner: Właściciel ("global" lub nazwa gracza)
            
        Returns:
            Słownik Frequency w formacie 1.18.2
        """
        frequency = Frequency.from_int(freq_int)
        nbt = frequency.to_nbt_1182()
        
        # Dodaj informację o właścicielu jeśli potrzeba
        if owner and owner != "global":
            # TODO: Lookup UUID
            pass
        
        return nbt


def convert_enderstorage_te(te_id: str, nbt: Dict[str, Any],
                           metadata: int = 0) -> Tuple[str, Optional[Dict[str, Any]], List[str]]:
    """
    Funkcja pomocnicza do szybkiej konwersji Tile Entity EnderStorage.
    
    Args:
        te_id: ID Tile Entity w 1.7.10
        nbt: NBT Tile Entity
        metadata: Metadata bloku (0=chest, 1=tank)
        
    Returns:
        Krotka (new_id, new_nbt, warnings)
    """
    converter = EnderStorageConverter()
    result = converter.convert_tile_entity(te_id, nbt, metadata)
    
    if result.success:
        return result.block_id_1182, result.nbt_1182, result.warnings
    else:
        # W przypadku błędu zwróć oryginalne dane z błędami jako ostrzeżenia
        return te_id, nbt, result.errors


def convert_enderstorage_item(item_id: str, damage: int = 0,
                             nbt: Optional[Dict[str, Any]] = None) -> Tuple[str, Optional[Dict[str, Any]], List[str]]:
    """
    Funkcja pomocnicza do szybkiej konwersji itemu EnderStorage.
    
    Args:
        item_id: ID itemu w 1.7.10
        damage: Damage/metadata (dla EnderPouch = frequency)
        nbt: Opcjonalne NBT itemu
        
    Returns:
        Krotka (new_id, new_nbt, warnings)
    """
    converter = EnderStorageConverter()
    result = converter.convert_item(item_id, damage, nbt)
    
    if result.success:
        return result.block_id_1182, result.nbt_1182, result.warnings
    else:
        # W przypadku błędu zwróć oryginalne dane
        return item_id, nbt, result.errors


# Słownik konwerterów dla szybkiego dostępu
TE_CONVERTERS_MAP = {
    ("EnderStorage:blockEnderStorage", 0): EnderChestNBTConverter,
    ("EnderStorage:blockEnderStorage", 1): EnderTankNBTConverter,
}


def get_converter_for_te(te_id: str, metadata: int = 0) -> Optional[type]:
    """
    Zwraca klasę konwertera dla danego ID Tile Entity.
    
    Args:
        te_id: ID Tile Entity w 1.7.10
        metadata: Metadata bloku (0=chest, 1=tank)
        
    Returns:
        Klasa konwertera lub None jeśli nie znaleziono
    """
    return TE_CONVERTERS_MAP.get((te_id, metadata))
