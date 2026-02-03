"""
Główny konwerter Blood Magic - orchestrator dla wszystkich konwerterów

Source mapping:
- 1.7.10: WayofTime/alchemicalWizardry (różne klasy)
- 1.18.2: wayoftime/bloodmagic (różne klasy)

Ten moduł implementuje główny interfejs konwersji dla Blood Magic,
korzystając z poszczególnych konwerterów specyficznych dla typów bloków/TE.
"""

from dataclasses import dataclass, field
from typing import Dict, Any, Optional, Tuple, List
from uuid import UUID

from .block_mappings import map_block_id, get_blockstate_props, map_te_id
from .altar_converter import BloodAltarConverter
from .ritual_converter import MasterRitualStoneConverter
from .soul_network_converter import SoulNetworkConverter, BloodOrbConverter


@dataclass
class ConversionResult:
    """Wynik konwersji bloku/TE"""
    # Identyfikacja
    block_id_1182: Optional[str] = None
    blockstate_props: Dict[str, Any] = field(default_factory=dict)
    be_nbt_1182: Optional[Dict[str, Any]] = None
    
    # Dodatkowe bloki do postawienia (jeśli potrzebne)
    extra_blocks: List[Dict[str, Any]] = field(default_factory=list)
    
    # Diagnostyka
    warnings: List[str] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)
    
    # Metadane
    converted: bool = False
    skipped: bool = False
    
    def is_success(self) -> bool:
        """Czy konwersja się powiodła (bez błędów krytycznych)"""
        return len(self.errors) == 0 and (self.block_id_1182 is not None or self.skipped)


class BloodMagicConverter:
    """
    Główny konwerter dla moda Blood Magic
    
    Konwertuje bloki i Tile Entities z 1.7.10 na 1.18.2.
    """
    
    def __init__(self, name_to_uuid_mapping: Optional[Dict[str, UUID]] = None):
        """
        Args:
            name_to_uuid_mapping: Opcjonalne mapowanie nazw graczy na UUID
        """
        # Inicjalizacja pod-konwerterów
        self.altar_converter = BloodAltarConverter()
        self.ritual_converter = MasterRitualStoneConverter()
        self.soul_network_converter = SoulNetworkConverter(name_to_uuid_mapping)
        self.orb_converter = BloodOrbConverter(name_to_uuid_mapping)
        
        # Mapowanie konwerterów dla poszczególnych TE
        self._te_converters = {
            "Altar": self.altar_converter,
            "MasterStone": self.ritual_converter,
        }
    
    def set_name_to_uuid_mapping(self, mapping: Dict[str, UUID]) -> None:
        """Ustaw mapowanie nazw graczy na UUID dla wszystkich konwerterów"""
        self.soul_network_converter.set_name_to_uuid_mapping(mapping)
        self.orb_converter.set_name_to_uuid_mapping(mapping)
    
    def convert_block(
        self,
        block_id_1710: str,
        metadata: int = 0,
        te_nbt_1710: Optional[Dict[str, Any]] = None,
        pos: Optional[Tuple[int, int, int]] = None,
        owner_uuid: Optional[UUID] = None,
    ) -> ConversionResult:
        """
        Konwertuj blok Blood Magic z 1.7.10 na 1.18.2
        
        Args:
            block_id_1710: ID bloku w 1.7.10 (np. "AWWayofTime:Altar")
            metadata: Wartość metadata 0-15
            te_nbt_1710: NBT TileEntity (jeśli blok ma TE)
            pos: Pozycja (x, y, z) - opcjonalnie
            owner_uuid: UUID właściciela (jeśli znany)
            
        Returns:
            ConversionResult z wynikiem konwersji
        """
        result = ConversionResult()
        
        # 1. Mapowanie ID bloku
        new_block_id, warning = map_block_id(block_id_1710)
        
        if warning:
            if "REMOVED" in warning:
                # Blok usunięty - pomijamy
                result.warnings.append(warning)
                result.skipped = True
                return result
            else:
                result.warnings.append(warning)
        
        if new_block_id is None:
            result.errors.append(
                f"BM-E-BLOCK-MAP-FAILED: Nie udało się zmapować bloku {block_id_1710}"
            )
            return result
        
        result.block_id_1182 = new_block_id
        
        # 2. Mapowanie blockstate (dla bloków z metadata)
        blockstate_props, warning = get_blockstate_props(block_id_1710, metadata)
        if warning:
            result.warnings.append(warning)
        result.blockstate_props = blockstate_props
        
        # 3. Konwersja Tile Entity (jeśli istnieje)
        if te_nbt_1710:
            te_id = te_nbt_1710.get("id", "")
            be_nbt, warnings = self._convert_tile_entity(
                te_id, te_nbt_1710, owner_uuid
            )
            result.warnings.extend(warnings)
            
            if be_nbt:
                result.be_nbt_1182 = be_nbt
                # Dodaj ID BlockEntity
                new_te_id, warning = map_te_id(te_id)
                if new_te_id:
                    result.be_nbt_1182["id"] = new_te_id
            else:
                result.warnings.append(
                    f"BM-W-TE-CONVERSION-FAILED: Nie udało się skonwertować TE {te_id}"
                )
        
        result.converted = True
        return result
    
    def _convert_tile_entity(
        self,
        te_id: str,
        te_nbt: Dict[str, Any],
        owner_uuid: Optional[UUID] = None
    ) -> Tuple[Optional[Dict[str, Any]], List[str]]:
        """
        Konwertuj Tile Entity używając odpowiedniego konwertera
        
        Args:
            te_id: ID TileEntity w 1.7.10
            te_nbt: NBT TileEntity
            owner_uuid: UUID właściciela
            
        Returns:
            Tuple (be_nbt, warnings)
        """
        if te_id in self._te_converters:
            converter = self._te_converters[te_id]
            return converter.convert(te_nbt, owner_uuid)
        
        # Brak specyficznego konwertera - zwracamy pusty dict
        return None, [f"BM-W-NO-TE-CONVERTER: Brak konwertera dla TE {te_id}"]
    
    def convert_soul_networks(
        self,
        networks_1710: Dict[str, Dict[str, Any]]
    ) -> Tuple[Dict[str, Dict[str, Any]], List[str]]:
        """
        Konwertuj wszystkie Soul Networks
        
        Args:
            networks_1710: Słownik {nazwa_gracza: dane_network}
            
        Returns:
            Tuple (networks_1182, warnings)
        """
        return self.soul_network_converter.convert_all_networks(networks_1710)
    
    def convert_blood_orb(
        self,
        item_nbt_1710: Dict[str, Any]
    ) -> Tuple[Dict[str, Any], List[str]]:
        """
        Konwertuj Blood Orb (item)
        
        Args:
            item_nbt_1710: NBT przedmiotu z 1.7.10
            
        Returns:
            Tuple (item_nbt_1182, warnings)
        """
        return self.orb_converter.convert_orb_item(item_nbt_1710)
    
    def get_supported_blocks(self) -> List[str]:
        """Zwróć listę obsługiwanych ID bloków 1.7.10"""
        from .block_mappings import BLOCK_ID_MAPPING
        return list(BLOCK_ID_MAPPING.keys())
    
    def get_conversion_stats(
        self,
        results: List[ConversionResult]
    ) -> Dict[str, Any]:
        """
        Generuj statystyki konwersji
        
        Args:
            results: Lista wyników konwersji
            
        Returns:
            Słownik ze statystykami
        """
        total = len(results)
        successful = sum(1 for r in results if r.converted and not r.skipped)
        skipped = sum(1 for r in results if r.skipped)
        failed = sum(1 for r in results if not r.is_success())
        
        all_warnings = []
        all_errors = []
        for r in results:
            all_warnings.extend(r.warnings)
            all_errors.extend(r.errors)
        
        return {
            "total_blocks": total,
            "converted": successful,
            "skipped": skipped,
            "failed": failed,
            "warnings_count": len(all_warnings),
            "errors_count": len(all_errors),
            "unique_warnings": list(set(all_warnings)),
            "unique_errors": list(set(all_errors)),
        }
