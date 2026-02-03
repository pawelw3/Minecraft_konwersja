"""
Enchanting Plus Main Converter

Główny konwerter dla moda Enchanting Plus (1.7.10) -> Enchanting Infuser (1.18.2).
Obsługuje konwersję bloków i Tile Entities.

Zawartość moda Enchanting Plus:
- enchanting_table: Podstawowy stół do wyboru enchantów
- advanced_table: Zaawansowany stół (modyfikacja, naprawa, zdejmowanie)
- arcane_inscriber: Konwersja książek na zwoje (BRAK odpowiednika w 1.18.2)

Zamiennik - Enchanting Infuser (1.18.2):
- enchanting_infuser: Odpowiednik podstawowego stołu
- advanced_enchanting_infuser: Odpowiednik zaawansowanego stołu
"""

from dataclasses import dataclass, field
from typing import Dict, Any, Optional, List, Tuple
import json

from .mappings.block_mappings import (
    get_block_mapping,
    BLOCK_MAPPINGS_1710_TO_1182,
    ALL_EP_BLOCK_IDS_1710,
    is_enchantingplus_block,
)
from .nbt_converters.base_converter import (
    BaseNBTConverter,
    NBTConversionResult,
    IdentityConverter,
    NullConverter,
)


@dataclass
class ConversionResult:
    """Wynik konwersji bloku/itemu"""
    success: bool
    block_id_1182: Optional[str] = None
    blockstate_props: Dict[str, str] = None
    nbt_1182: Optional[Dict[str, Any]] = None
    errors: List[str] = None
    warnings: List[str] = None
    
    def __post_init__(self):
        if self.blockstate_props is None:
            self.blockstate_props = {}
        if self.errors is None:
            self.errors = []
        if self.warnings is None:
            self.warnings = []


@dataclass
class EPBlockConversion:
    """Reprezentuje konwersję pojedynczego bloku Enchanting Plus"""
    original_id: str
    original_pos: Tuple[int, int, int]
    converted: ConversionResult
    
    def to_dict(self) -> Dict[str, Any]:
        """Eksportuje do słownika"""
        return {
            'original_id': self.original_id,
            'original_pos': self.original_pos,
            'new_id': self.converted.block_id_1182,
            'blockstate_props': self.converted.blockstate_props,
            'nbt': self.converted.nbt_1182,
            'errors': self.converted.errors,
            'warnings': self.converted.warnings
        }


class EnchantingPlusConverter:
    """
    Główny konwerter Enchanting Plus.
    
    Obsługuje:
    - Mapowanie ID bloków (1.7.10 -> 1.18.2)
    - Konwersję NBT Tile Entities (uproszczona - EP ma proste NBT)
    - Usuwanie bloków bez odpowiedników (Arcane Inscriber)
    
    Uwaga: Enchanting Plus ma prostsze NBT niż AE2 - głównie podstawowe
    dane TileEntity bez skomplikowanych struktur inventory.
    """
    
    SOURCE_VERSION = "1.7.10"
    TARGET_VERSION = "1.18.2"
    SOURCE_MOD = "Enchanting Plus"
    TARGET_MOD = "Enchanting Infuser"
    
    def __init__(self):
        self.errors: List[str] = []
        self.warnings: List[str] = []
        self._init_converters()
    
    def _init_converters(self):
        """Inicjalizuje mapę konwerterów NBT"""
        # Enchanting Plus ma proste NBT - używamy głównie IdentityConverter
        self.nbt_converters: Dict[str, BaseNBTConverter] = {
            'enchanting_table': IdentityConverter(),
            'advanced_table': IdentityConverter(),
            'arcane_inscriber': NullConverter(),  # Blok do usunięcia
            'default': IdentityConverter(),
        }
    
    def convert_block(self,
                      block_id_1710: str,
                      nbt_1710: Optional[Dict[str, Any]] = None,
                      metadata: int = 0,
                      position: Tuple[int, int, int] = (0, 0, 0),
                      strict: bool = False) -> EPBlockConversion:
        """
        Konwertuje blok Enchanting Plus z 1.7.10 do 1.18.2.
        
        Args:
            block_id_1710: ID bloku w wersji 1.7.10
            nbt_1710: NBT Tile Entity (opcjonalnie)
            metadata: Metadata bloku (dla wariantów)
            position: Pozycja (x, y, z)
            strict: Jeśli True, błędy powodują nieudaną konwersję
            
        Returns:
            EPBlockConversion z wynikiem konwersji
        """
        self.errors.clear()
        self.warnings.clear()
        
        # Krok 1: Sprawdź czy to blok Enchanting Plus
        if not is_enchantingplus_block(block_id_1710):
            error_msg = f"EPC-E-NOT-EP-BLOCK: {block_id_1710} nie jest blokiem Enchanting Plus"
            self.errors.append(error_msg)
            return EPBlockConversion(
                original_id=block_id_1710,
                original_pos=position,
                converted=ConversionResult(
                    success=False,
                    errors=[error_msg]
                )
            )
        
        # Krok 2: Znajdź mapowanie bloku
        mapping = get_block_mapping(block_id_1710)
        if not mapping:
            error_msg = f"EPC-E-BLOCK-NOT-MAPPED: Nie znaleziono mapowania dla {block_id_1710}"
            self.errors.append(error_msg)
            return EPBlockConversion(
                original_id=block_id_1710,
                original_pos=position,
                converted=ConversionResult(
                    success=False,
                    errors=[error_msg]
                )
            )
        
        # Krok 3: Sprawdź czy blok ma być usunięty
        if mapping.id_1182 == "minecraft:air":
            warning_msg = f"EPC-W-BLOCK-REMOVED: {block_id_1710} nie ma odpowiednika - zostanie usunięty"
            self.warnings.append(warning_msg)
            
            return EPBlockConversion(
                original_id=block_id_1710,
                original_pos=position,
                converted=ConversionResult(
                    success=True,  # Konwersja "udana" - blok usunięty celowo
                    block_id_1182="minecraft:air",
                    warnings=[warning_msg]
                )
            )
        
        # Krok 4: Konwertuj NBT (jeśli blok ma TileEntity)
        nbt_result = None
        if mapping.has_tile_entity and nbt_1710:
            converter_name = self._get_converter_name(block_id_1710)
            nbt_result = self._convert_nbt(converter_name, nbt_1710, block_id_1710)
        
        # Krok 5: Ekstrahuj blockstate_props (orientacja z NBT)
        # W Enchanting Plus stoły nie mają orientacji (zwykle zawsze skierowane w jedną stronę)
        blockstate_props = {}
        
        # Zbuduj wynik
        converted = ConversionResult(
            success=True,
            block_id_1182=mapping.id_1182,
            blockstate_props=blockstate_props,
            nbt_1182=nbt_result.converted_nbt if nbt_result else None,
            errors=nbt_result.errors if nbt_result else [],
            warnings=nbt_result.warnings if nbt_result else []
        )
        
        return EPBlockConversion(
            original_id=block_id_1710,
            original_pos=position,
            converted=converted
        )
    
    def _get_converter_name(self, block_id_1710: str) -> str:
        """Zwraca nazwę konwertera dla bloku"""
        if "enchanting_table" in block_id_1710:
            return 'enchanting_table'
        elif "advanced_table" in block_id_1710:
            return 'advanced_table'
        elif "arcane_inscriber" in block_id_1710:
            return 'arcane_inscriber'
        return 'default'
    
    def _convert_nbt(self, converter_name: str,
                     nbt_1710: Dict[str, Any],
                     block_id: str = None) -> NBTConversionResult:
        """Wykonuje konwersję NBT używając odpowiedniego konwertera"""
        converter = self.nbt_converters.get(converter_name)
        if not converter:
            converter = self.nbt_converters['default']
        
        return converter.convert(nbt_1710, block_id)
    
    def is_enchantingplus_block(self, block_id: str) -> bool:
        """Sprawdza czy blok należy do Enchanting Plus"""
        return is_enchantingplus_block(block_id)
    
    def get_supported_blocks(self) -> List[str]:
        """Zwraca listę obsługiwanych bloków Enchanting Plus"""
        return list(ALL_EP_BLOCK_IDS_1710)
    
    def get_conversion_report(self) -> Dict[str, Any]:
        """Generuje raport o możliwościach konwersji"""
        return {
            'source_mod': self.SOURCE_MOD,
            'target_mod': self.TARGET_MOD,
            'source_version': self.SOURCE_VERSION,
            'target_version': self.TARGET_VERSION,
            'supported_blocks': len(BLOCK_MAPPINGS_1710_TO_1182),
            'blocks_converted': sum(1 for m in BLOCK_MAPPINGS_1710_TO_1182.values() 
                                   if m.id_1182 != "minecraft:air"),
            'blocks_removed': sum(1 for m in BLOCK_MAPPINGS_1710_TO_1182.values() 
                                 if m.id_1182 == "minecraft:air"),
            'nbt_converters': list(self.nbt_converters.keys()),
            'special_cases': [
                'Arcane Inscriber -> usunięcie (brak odpowiednika)',
                'Enchanted Scrolls -> zastąpione vanilla Enchanted Books',
            ],
            'dependencies': [
                'Puzzles Lib (wymagana przez Enchanting Infuser)',
            ]
        }
    
    def batch_convert(self, blocks: List[Dict[str, Any]]) -> List[EPBlockConversion]:
        """
        Konwertuje listę bloków.
        
        Args:
            blocks: Lista słowników zawierających:
                - id: ID bloku 1.7.10
                - pos: (x, y, z)
                - nbt: NBT TileEntity (opcjonalnie)
                - metadata: metadata (opcjonalnie)
        
        Returns:
            Lista EPBlockConversion
        """
        results = []
        for block_data in blocks:
            result = self.convert_block(
                block_id_1710=block_data['id'],
                position=block_data['pos'],
                nbt_1710=block_data.get('nbt'),
                metadata=block_data.get('metadata', 0)
            )
            results.append(result)
        return results


def main():
    """Demo konwertera Enchanting Plus"""
    converter = EnchantingPlusConverter()
    
    print("=" * 60)
    print("ENCHANTING PLUS CONVERTER - Demo")
    print("=" * 60)
    
    # Raport
    report = converter.get_conversion_report()
    print(f"\nRaport konwersji:")
    print(f"  Mod źródłowy: {report['source_mod']}")
    print(f"  Mod docelowy: {report['target_mod']}")
    print(f"  Wersja źródłowa: {report['source_version']}")
    print(f"  Wersja docelowa: {report['target_version']}")
    print(f"  Obsługiwane bloki: {report['supported_blocks']}")
    print(f"  Bloki konwertowane: {report['blocks_converted']}")
    print(f"  Bloki usuwane: {report['blocks_removed']}")
    print(f"\nPrzypadki specjalne:")
    for case in report['special_cases']:
        print(f"  - {case}")
    
    # Przykład konwersji podstawowego stołu
    print("\n" + "=" * 60)
    print("Przykład 1: Konwersja podstawowego stołu")
    print("=" * 60)
    
    result = converter.convert_block(
        'EnchantingPlus:enchanting_table',
        position=(100, 64, 100)
    )
    
    print(f"\nOryginalny blok: {result.original_id}")
    print(f"Nowy blok: {result.converted.block_id_1182}")
    print(f"Sukces: {result.converted.success}")
    
    # Przykład konwersji zaawansowanego stołu
    print("\n" + "=" * 60)
    print("Przykład 2: Konwersja zaawansowanego stołu")
    print("=" * 60)
    
    result = converter.convert_block(
        'EnchantingPlus:advanced_table',
        position=(101, 64, 100)
    )
    
    print(f"\nOryginalny blok: {result.original_id}")
    print(f"Nowy blok: {result.converted.block_id_1182}")
    print(f"Sukces: {result.converted.success}")
    
    # Przykład konwersji Arcane Inscriber (do usunięcia)
    print("\n" + "=" * 60)
    print("Przykład 3: Arcane Inscriber (do usunięcia)")
    print("=" * 60)
    
    result = converter.convert_block(
        'EnchantingPlus:arcane_inscriber',
        position=(102, 64, 100)
    )
    
    print(f"\nOryginalny blok: {result.original_id}")
    print(f"Nowy blok: {result.converted.block_id_1182}")
    print(f"Sukces: {result.converted.success}")
    print(f"Ostrzeżenia: {result.converted.warnings}")
    
    # Batch conversion
    print("\n" + "=" * 60)
    print("Przykład 4: Batch conversion")
    print("=" * 60)
    
    blocks = [
        {'id': 'EnchantingPlus:enchanting_table', 'pos': (100, 64, 100)},
        {'id': 'EnchantingPlus:advanced_table', 'pos': (101, 64, 100)},
        {'id': 'EnchantingPlus:arcane_inscriber', 'pos': (102, 64, 100)},
    ]
    
    results = converter.batch_convert(blocks)
    print(f"\nPrzekonwertowano {len(results)} bloków:")
    for r in results:
        print(f"  {r.original_id} -> {r.converted.block_id_1182}")
    
    print("\n" + "=" * 60)
    print("Demo zakończone!")
    print("=" * 60)


if __name__ == "__main__":
    main()
