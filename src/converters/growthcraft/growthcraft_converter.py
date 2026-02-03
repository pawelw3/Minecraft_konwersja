"""
Główny konwerter GrowthCraft dla Minecraft 1.7.10 -> 1.18.2

Ten moduł zawiera główną klasę konwertera dla wszystkich bloków i Tile Entities
z moda GrowthCraft.
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
    get_all_growthcraft_blocks,
    get_all_growthcraft_items,
    get_all_growthcraft_fluids,
)
from .nbt_converters import (
    FermentationBarrelNBTConverter,
    BrewKettleNBTConverter,
    BeeBoxNBTConverter,
    MixingVatNBTConverter,
)
from .nbt_converters.base_converter import NBTConversionResult


@dataclass
class ConversionResult:
    """Wynik konwersji bloku/TE GrowthCraft"""
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


class GrowthcraftConverter:
    """
    Główny konwerter dla moda GrowthCraft.
    
    Obsługuje konwersję wszystkich bloków i Tile Entities z GrowthCraft 1.7.10
    do formatu 1.18.2.
    
    Użycie:
        converter = GrowthcraftConverter()
        result = converter.convert_block(
            block_id="grccellar:ferment_barrel",
            metadata=0,
            nbt=nbt_data_1710
        )
        
        if result.success:
            print(f"Nowe ID: {result.block_id_1182}")
            print(f"Nowe NBT: {result.nbt_1182}")
    """
    
    # Mapowanie ID TE -> Konwerter NBT
    TE_CONVERTERS = {
        "grccellar:ferment_barrel": FermentationBarrelNBTConverter,
        "grccellar:brew_kettle": BrewKettleNBTConverter,
        "grcbees:bee_box": BeeBoxNBTConverter,
        "grcmilk:cheese_vat": MixingVatNBTConverter,
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
        Konwertuje blok GrowthCraft z 1.7.10 do 1.18.2.
        
        Args:
            block_id: ID bloku w formacie 1.7.10 (np. "grccellar:ferment_barrel")
            metadata: Metadata bloku (dla wariantów)
            nbt: Opcjonalne NBT Tile Entity
            
        Returns:
            ConversionResult z wynikiem konwersji
        """
        self.stats["processed"] += 1
        
        # Sprawdź czy to blok GrowthCraft
        if not self.is_growthcraft_block(block_id):
            self.stats["failed"] += 1
            return ConversionResult(
                success=False,
                errors=[f"Blok {block_id} nie jest blokiem GrowthCraft"]
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
        Konwertuje Tile Entity GrowthCraft.
        
        Alias dla convert_block dla jasności.
        """
        return self.convert_block(te_id, metadata, nbt)
    
    def _convert_nbt(self, block_id: str, nbt: Dict[str, Any],
                    metadata: int = 0) -> NBTConversionResult:
        """
        Konwertuje NBT używając odpowiedniego konwertera.
        """
        # Znajdź odpowiedni konwerter
        converter_class = self.TE_CONVERTERS.get(block_id)
        
        if not converter_class:
            # Brak specyficznego konwertera - użyj tożsamości
            self.warnings.append(f"Brak specyficznego konwertera dla {block_id}, używam tożsamości")
            return NBTConversionResult(
                success=True,
                converted_nbt=nbt,
                warnings=[f"Brak specyficznego konwertera dla {block_id}"]
            )
        
        # Utwórz instancję konwertera i wykonaj konwersję
        converter = converter_class()
        return converter.convert(nbt, block_id, metadata)
    
    def is_growthcraft_block(self, block_id: str) -> bool:
        """Sprawdza czy blok jest blokiem GrowthCraft"""
        return block_id.startswith((
            "grccellar:",
            "grcmilk:",
            "grcbees:",
            "grcfishtrap:",
            "grcbamboo:",
            "grcapples:",
            "grcgrapes:",
            "grchops:",
            "grcrice:",
            "growthcraft:",  # Może być już w formacie 1.18.2
        ))
    
    def is_growthcraft_item(self, item_id: str) -> bool:
        """Sprawdza czy item jest itemem GrowthCraft"""
        return item_id.startswith((
            "grccellar:",
            "grcmilk:",
            "grcbees:",
            "grcfishtrap:",
            "grcbamboo:",
            "grcapples:",
            "grcgrapes:",
            "grchops:",
            "grcrice:",
            "growthcraft:",
        ))
    
    def get_supported_blocks(self) -> List[str]:
        """Zwraca listę obsługiwanych bloków GrowthCraft"""
        return get_all_growthcraft_blocks()
    
    def get_supported_items(self) -> List[str]:
        """Zwraca listę obsługiwanych itemów GrowthCraft"""
        return get_all_growthcraft_items()
    
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


def convert_growthcraft_te(te_id: str, nbt: Dict[str, Any],
                           metadata: int = 0) -> Tuple[str, Optional[Dict[str, Any]], List[str]]:
    """
    Funkcja pomocnicza do szybkiej konwersji Tile Entity GrowthCraft.
    
    Args:
        te_id: ID Tile Entity w 1.7.10
        nbt: NBT Tile Entity
        metadata: Metadata bloku
        
    Returns:
        Krotka (new_id, new_nbt, warnings)
    """
    converter = GrowthcraftConverter()
    result = converter.convert_tile_entity(te_id, nbt, metadata)
    
    if result.success:
        return result.block_id_1182, result.nbt_1182, result.warnings
    else:
        # W przypadku błędu zwróć oryginalne dane z błędami jako ostrzeżenia
        return te_id, nbt, result.errors


# Słownik konwerterów dla szybkiego dostępu
TE_CONVERTERS_MAP = {
    "grccellar:ferment_barrel": FermentationBarrelNBTConverter,
    "grccellar:brew_kettle": BrewKettleNBTConverter,
    "grcbees:bee_box": BeeBoxNBTConverter,
    "grcmilk:cheese_vat": MixingVatNBTConverter,
}


def get_converter_for_te(te_id: str) -> Optional[type]:
    """
    Zwraca klasę konwertera dla danego ID Tile Entity.
    
    Args:
        te_id: ID Tile Entity w 1.7.10
        
    Returns:
        Klasa konwertera lub None jeśli nie znaleziono
    """
    return TE_CONVERTERS_MAP.get(te_id)
