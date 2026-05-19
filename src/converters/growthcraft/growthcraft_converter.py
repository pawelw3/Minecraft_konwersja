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
    STRICT_1182_FUNCTIONAL,
    SUPPORTED_PROFILES,
    convert_block_id,
    get_all_growthcraft_blocks,
    get_all_growthcraft_items,
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
    
    # Mapowanie TileEntity ID (z mapy 1.7.10) -> Block ID (dla konwertera)
    # UWAGA: Te formaty zostały ODKRYTE z mapy, nie zgadnięte!
    TE_ID_TO_BLOCK_ID = {
        # Formaty odkryte z mapa_1710:
        "grc.tileentity.fermentBarrel": "grccellar:ferment_barrel",
        "grc.tileentity.beeBox": "grcbees:bee_box",
        "grc.tileentity.fishTrap": "grcfishtrap:fish_trap",
        # Standardowe formaty (dla kompatybilności)
        "TileEntityFermentationBarrel": "grccellar:ferment_barrel",
        "TileEntityBrewKettle": "grccellar:brew_kettle",
        "TileEntityBeeBox": "grcbees:bee_box",
        "TileEntityCheeseVat": "grcmilk:cheese_vat",
        "TileEntityFruitPress": "grccellar:fruit_press",
        "TileEntityCultureJar": "grccellar:culture_jar",
        "TileEntityPancheon": "grcmilk:pancheon",
        "TileEntityButterChurn": "grcmilk:butter_churn",
        "TileEntityCheesePress": "grcmilk:cheese_press",
        "TileEntityFishTrap": "grcfishtrap:fish_trap",
    }
    
    def __init__(self, profile: str = STRICT_1182_FUNCTIONAL):
        if profile not in SUPPORTED_PROFILES:
            raise ValueError(f"Nieznany profil GrowthCraft: {profile}")
        self.profile = profile
        self.errors: List[str] = []
        self.warnings: List[str] = []
        self.stats = {
            "processed": 0,
            "converted": 0,
            "failed": 0,
            "warnings": 0,
        }
    
    def _resolve_block_id(self, block_or_te_id: str) -> str:
        """
        Rozwiązuje ID bloku lub TE do standardowego ID bloku.
        
        Obsługuje formaty:
        - Block ID: "grccellar:ferment_barrel"
        - TE ID z mapy: "grc.tileentity.fermentBarrel"
        - Standardowy TE ID: "TileEntityFermentationBarrel"
        """
        # Jeśli to TE ID z mapy, zamień na Block ID
        if block_or_te_id in self.TE_ID_TO_BLOCK_ID:
            return self.TE_ID_TO_BLOCK_ID[block_or_te_id]
        # W przeciwnym razie zwróć oryginalne ID
        return block_or_te_id
    
    def convert_block(self, block_id: str, metadata: int = 0,
                     nbt: Optional[Dict[str, Any]] = None) -> ConversionResult:
        """
        Konwertuje blok GrowthCraft z 1.7.10 do 1.18.2.
        
        Args:
            block_id: ID bloku lub TE w formacie 1.7.10 (np. "grccellar:ferment_barrel" lub "grc.tileentity.fermentBarrel")
            metadata: Metadata bloku (dla wariantów)
            nbt: Opcjonalne NBT Tile Entity
            
        Returns:
            ConversionResult z wynikiem konwersji
        """
        self.stats["processed"] += 1
        
        # Rozwiąż ID (może być TE ID z mapy)
        resolved_id = self._resolve_block_id(block_id)
        
        # Sprawdź czy to blok GrowthCraft
        if not self.is_growthcraft_block(block_id):
            self.stats["failed"] += 1
            return ConversionResult(
                success=False,
                errors=[f"Blok {block_id} nie jest blokiem GrowthCraft"]
            )
        
        # Konwertuj ID bloku
        block_id_1182 = convert_block_id(resolved_id, metadata, profile=self.profile)
        
        # Jeśli nie ma NBT, zwróć tylko konwersję ID
        if not nbt:
            self.stats["converted"] += 1
            return ConversionResult(
                success=True,
                block_id_1182=block_id_1182,
                nbt_1182=None
            )
        
        # Konwertuj NBT jeśli dostępne (użyj rozwiązanego ID)
        nbt_result = self._convert_nbt(resolved_id, nbt, metadata, block_id_1182)
        
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
                    metadata: int = 0, target_block_id: Optional[str] = None) -> NBTConversionResult:
        """
        Konwertuje NBT używając odpowiedniego konwertera.
        """
        # Znajdź odpowiedni konwerter
        if self.profile == STRICT_1182_FUNCTIONAL:
            return self._convert_nbt_strict(block_id, nbt, metadata, target_block_id or block_id)

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

    def _convert_nbt_strict(self, block_id: str, nbt: Dict[str, Any],
                            metadata: int, target_block_id: str) -> NBTConversionResult:
        """
        Strict 1.18.2: mapuje funkcje Growthcraft na aktualne zamienniki i
        zachowuje stare dane procesu jako payload ratunkowy.
        """
        converted = {
            "id": target_block_id,
            "x": nbt.get("x", 0),
            "y": nbt.get("y", 0),
            "z": nbt.get("z", 0),
            "conversion_profile": self.profile,
            "legacy_growthcraft": self._extract_legacy_growthcraft_payload(block_id, nbt, metadata),
        }
        warnings = [
            "GC-W-FUNCTIONAL-REBUILD: Growthcraft CE nie jest domyslnym celem strict 1.18.2; "
            "NBT procesu zapisano w legacy_growthcraft do postprocessingu/review."
        ]
        preferred_mod = self._preferred_functional_mod(block_id)
        if preferred_mod:
            warnings.append(f"GC-W-PREFERRED-MOD: preferowany zamiennik funkcji: {preferred_mod}")
        return NBTConversionResult(success=True, converted_nbt=converted, warnings=warnings)

    def _extract_legacy_growthcraft_payload(self, block_id: str, nbt: Dict[str, Any],
                                            metadata: int) -> Dict[str, Any]:
        payload = {
            "source_block_id": block_id,
            "source_te_id": nbt.get("id"),
            "metadata": metadata,
            "process": self._extract_process_fields(nbt),
            "items": self._extract_legacy_items(nbt),
            "fluids": self._extract_legacy_fluids(nbt),
        }
        for key in ("bee_box", "brew_kettle", "vat_state", "heat_component", "lid_on"):
            if key in nbt:
                payload[key] = nbt[key]
        return payload

    def _extract_process_fields(self, nbt: Dict[str, Any]) -> Dict[str, Any]:
        process = {}
        for key in ("time", "progress", "progress_max", "CurrentProcessTicks", "MaxProcessTicks"):
            if key in nbt:
                process[key] = nbt[key]
        brew = nbt.get("brew_kettle")
        if isinstance(brew, dict):
            for key in ("time", "time_max", "heat_multiplier"):
                if key in brew:
                    process[f"brew_kettle.{key}"] = brew[key]
        return process

    def _extract_legacy_items(self, nbt: Dict[str, Any]) -> List[Dict[str, Any]]:
        items = nbt.get("items") or nbt.get("Items") or []
        return [dict(item) for item in items if isinstance(item, dict)]

    def _extract_legacy_fluids(self, nbt: Dict[str, Any]) -> List[Dict[str, Any]]:
        fluids = []
        for key, value in nbt.items():
            if isinstance(value, dict) and ("FluidName" in value or "Amount" in value):
                fluids.append({
                    "source_field": key,
                    "FluidName": value.get("FluidName"),
                    "Amount": value.get("Amount", 0),
                    "Tag": value.get("Tag"),
                })
        return fluids

    def _preferred_functional_mod(self, block_id: str) -> Optional[str]:
        if block_id.startswith("grcbees:"):
            return "Productive Bees (vanilla beehive jako bezpieczny blok strict)"
        if block_id.startswith("grcmilk:"):
            return "Farmer's Delight / addon kulinarny"
        if block_id in {"grccellar:ferment_barrel", "grccellar:brew_kettle"}:
            return "Brewin' and Chewin'"
        if block_id == "grccellar:fruit_press":
            return "Create"
        return None
    
    def is_growthcraft_block(self, block_id: str) -> bool:
        """Sprawdza czy blok jest blokiem GrowthCraft"""
        # Sprawdź bezpośrednie mapowanie TE ID
        if block_id in self.TE_ID_TO_BLOCK_ID:
            return True
        # Sprawdź prefiksy
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
            "grc.tileentity.",  # Format TE ID z mapy 1.7.10
            "TileEntity",  # Standardowy format TE ID
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
            "grc.item.",  # Format item ID z mapy
        ))
    
    def get_supported_blocks(self) -> List[str]:
        """Zwraca listę obsługiwanych bloków GrowthCraft"""
        return get_all_growthcraft_blocks(self.profile)
    
    def get_supported_items(self) -> List[str]:
        """Zwraca listę obsługiwanych itemów GrowthCraft"""
        return get_all_growthcraft_items(self.profile)
    
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
