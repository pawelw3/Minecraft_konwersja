"""
Główny konwerter Blood Magic - orchestrator dla wszystkich konwerterów

Source mapping:
- 1.7.10: WayofTime/alchemicalWizardry (różne klasy)
- 1.18.2: wayoftime/bloodmagic (różne klasy)

Ten moduł implementuje główny interfejs konwersji dla Blood Magic,
korzystając z poszczególnych konwerterów specyficznych dla typów bloków/TE.

WAŻNE: W 1.18.2 każda Blood Rune to osobny blok (nie blockstate).
"""

from dataclasses import dataclass, field
from typing import Dict, Any, Optional, Tuple, List
from uuid import UUID

from .block_mappings import (
    map_block_id, 
    map_blood_rune, 
    map_te_id,
    RUNE_BLOCK_MAPPING,
)
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
    
    Source mapping:
    - 1.7.10: WayofTime/alchemicalWizardry/ModBlocks.java
    - 1.18.2: wayoftime/bloodmagic/common/block/BloodMagicBlocks.java
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
        # UWAGA: Rzeczywiste TE ID z mapy to "containerAltar" i "containerMasterStone"
        self._te_converters = {
            # Rzeczywiste TE ID z mapy 1.7.10
            "containerAltar": self.altar_converter,
            "containerMasterStone": self.ritual_converter,
            # Fallback dla oczekiwanych ID
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
            pos: Pozycja (x, y, z) - opcjonalnie, ale zalecana dla BE
            owner_uuid: UUID właściciela (jeśli znany)
            
        Returns:
            ConversionResult z wynikiem konwersji
        """
        result = ConversionResult()
        
        # 1. Obsługa run (osobne bloki w 1.7.10 i 1.18.2)
        if block_id_1710 in RUNE_BLOCK_MAPPING:
            result.block_id_1182 = RUNE_BLOCK_MAPPING[block_id_1710]
            result.converted = True
            return result
        
        # 2. Obsługa BloodRune (z metadanymi)
        if block_id_1710 == "AWWayofTime:bloodRune":
            new_block_id, warning = map_blood_rune(metadata)
            if warning:
                result.warnings.append(warning)
            
            if new_block_id is None:
                result.errors.append(
                    f"BM-E-RUNE-MAP-FAILED: Nie udało się zmapować BloodRune meta={metadata}"
                )
                return result
            
            result.block_id_1182 = new_block_id
            result.converted = True
            return result
        
        # 3. Mapowanie ID bloku (pozostałe bloki)
        new_block_id, warning = map_block_id(block_id_1710)
        
        if warning:
            if "REMOVED" in warning:
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
        
        # 4. Konwersja Tile Entity (jeśli istnieje)
        if te_nbt_1710:
            te_id = te_nbt_1710.get("id", "")
            be_nbt, warnings = self._convert_tile_entity(
                te_id, te_nbt_1710, owner_uuid, pos
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
        owner_uuid: Optional[UUID] = None,
        pos: Optional[Tuple[int, int, int]] = None
    ) -> Tuple[Optional[Dict[str, Any]], List[str]]:
        """
        Konwertuj Tile Entity używając odpowiedniego konwertera
        
        Args:
            te_id: ID TileEntity w 1.7.10
            te_nbt: NBT TileEntity
            owner_uuid: UUID właściciela
            pos: Pozycja (x, y, z) - dodawana do NBT dla BE
            
        Returns:
            Tuple (be_nbt, warnings)
        """
        all_warnings = []
        
        # Konwersja przez specyficzny konwerter
        if te_id in self._te_converters:
            converter = self._te_converters[te_id]
            be_nbt, warnings = converter.convert(te_nbt, owner_uuid)
            all_warnings.extend(warnings)
        else:
            # Brak specyficznego konwertera
            be_nbt = {}
            all_warnings.append(f"BM-W-NO-TE-CONVERTER: Brak konwertera dla TE {te_id}")
        
        # Dodaj pozycję do NBT (wymagane dla BlockEntity w 1.18.2)
        if be_nbt and pos:
            be_nbt["x"] = pos[0]
            be_nbt["y"] = pos[1]
            be_nbt["z"] = pos[2]
        
        return be_nbt, all_warnings
    
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
            
        Note:
            Format wyjściowy to format pośredni. Właściwy zapis w 1.18.2
            wymaga umieszczenia danych w BMWorldSavedData.
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
        blocks = list(BLOCK_ID_MAPPING.keys())
        blocks.extend(RUNE_BLOCK_MAPPING.keys())
        blocks.append("AWWayofTime:bloodRune")
        return blocks
    
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
