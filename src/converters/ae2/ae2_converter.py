"""
AE2 Main Converter

Główny konwerter dla Applied Energistics 2.
Integruje wszystkie komponenty i obsługuje konwersję bloków, 
Tile Entities oraz itemów AE2.
"""

from dataclasses import dataclass, field
from typing import Dict, Any, Optional, List, Tuple
import json

from .mappings import get_block_mapping, get_item_mapping
from .mappings.block_mappings import (
    normalize_block_id,
    resolve_crafting_storage_variant,
    resolve_crafting_unit_variant,
    ALL_AE2_BLOCK_IDS_1710
)
from .utils import IDResolver

# Import konwerterów NBT
from .nbt_converters import (
    BaseNBTConverter,
    NBTConversionResult,
    DriveConverter,
    ChestConverter,
    InterfaceConverter,
    StorageCellConverter,
    CraftingUnitConverter,
    IOPortConverter,
    SpatialIOPortConverter,
    SpatialPylonConverter,
)
from .nbt_converters.crafting_converter import (
    CraftingStorageConverter,
    CraftingAcceleratorConverter,
    MolecularAssemblerConverter,
    CraftingMonitorConverter,
)
from .nbt_converters.utility_converters import (
    ChargerConverter,
    InscriberConverter,
    VibrationChamberConverter,
    SecurityStationConverter,
    WirelessAccessPointConverter,
    QuantumBridgeConverter,
)
from .nbt_converters.cable_converter import CableConverter
from .nbt_converters.base_converter import IdentityConverter


@dataclass
class ConversionResult:
    """Wynik konwersji bloku/itemu"""
    success: bool
    block_id_1182: Optional[str] = None
    blockstate_props: Dict[str, str] = None  # Właściwości BlockState (np. facing)
    nbt_1182: Optional[Dict[str, Any]] = None
    additional_blocks: List['AE2BlockConversion'] = None
    errors: List[str] = None
    warnings: List[str] = None
    
    def __post_init__(self):
        if self.blockstate_props is None:
            self.blockstate_props = {}
        if self.additional_blocks is None:
            self.additional_blocks = []
        if self.errors is None:
            self.errors = []
        if self.warnings is None:
            self.warnings = []


@dataclass
class AE2BlockConversion:
    """
    Reprezentuje konwersję pojedynczego bloku AE2.
    
    Może zawierać dodatkowe bloki (np. Pattern Provider przy Interface).
    """
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
            'additional_blocks': [
                {
                    'id': b.converted.block_id_1182,
                    'pos': b.original_pos,
                    'blockstate_props': b.converted.blockstate_props,
                    'nbt': b.converted.nbt_1182
                }
                for b in self.converted.additional_blocks
            ],
            'errors': self.converted.errors,
            'warnings': self.converted.warnings
        }


class AE2Converter:
    """
    Główny konwerter AE2.
    
    Obsługuje:
    - Mapowanie ID bloków (1.7.10 -> 1.18.2)
    - Konwersję NBT Tile Entities
    - Konwersję itemów (storage cells, itp.)
    - Specjalne przypadki (Interface -> Interface + Pattern Provider)
    """
    
    # Wersje obsługiwane
    SOURCE_VERSION = "1.7.10"
    TARGET_VERSION = "1.18.2"
    
    def __init__(self):
        self.id_resolver = IDResolver()
        self._init_converters()
        self.errors: List[str] = []
        self.warnings: List[str] = []
        
    def _init_converters(self):
        """Inicjalizuje mapę konwerterów NBT"""
        self.nbt_converters: Dict[str, BaseNBTConverter] = {
            # Core network
            'controller': IdentityConverter(),
            'drive': DriveConverter(),
            'chest': DriveConverter(),  # Chest dziedziczy z Drive
            'sky_chest': ChestConverter(),
            'energy_acceptor': IdentityConverter(),
            'energy_cell': IdentityConverter(),
            
            # Crafting
            'crafting_unit': CraftingUnitConverter(),
            'crafting_storage': CraftingStorageConverter(),
            'crafting_accelerator': CraftingAcceleratorConverter(),
            'crafting_monitor': CraftingMonitorConverter(),
            'molecular_assembler': MolecularAssemblerConverter(),
            
            # Interface & IO
            'interface': InterfaceConverter(),
            'io_port': IOPortConverter(),
            
            # Quantum
            'quantum_ring': IdentityConverter(),
            'quantum_link': QuantumBridgeConverter(),
            
            # Spatial
            'spatial_io_port': SpatialIOPortConverter(),
            'spatial_pylon': IdentityConverter(),
            
            # Utility
            'charger': ChargerConverter(),
            'inscriber': InscriberConverter(),
            'vibration_chamber': VibrationChamberConverter(),
            'growth_accelerator': IdentityConverter(),
            'condenser': IdentityConverter(),
            'security_station': SecurityStationConverter(),
            'wireless_ap': WirelessAccessPointConverter(),
            
            # Cable Bus (multipart - kable, terminale, bus)
            'cable_bus': CableConverter(),
            
            # Default
            'default': IdentityConverter(),
        }
    
    def convert_block(self, 
                      block_id_1710: str, 
                      nbt_1710: Optional[Dict[str, Any]] = None,
                      metadata: int = 0,
                      position: Tuple[int, int, int] = (0, 0, 0),
                      strict: bool = False) -> AE2BlockConversion:
        """
        Konwertuje blok AE2 z 1.7.10 do 1.18.2.
        
        Args:
            block_id_1710: ID bloku w wersji 1.7.10
            nbt_1710: NBT Tile Entity (opcjonalnie)
            metadata: Metadata bloku (dla wariantów)
            position: Pozycja (x, y, z)
            strict: Jeśli True, błędy powodują nieudaną konwersję
            
        Returns:
            AE2BlockConversion z wynikiem konwersji
        """
        """
        Konwertuje blok AE2 z 1.7.10 do 1.18.2.
        
        Args:
            block_id_1710: ID bloku w wersji 1.7.10
            nbt_1710: NBT Tile Entity (opcjonalnie)
            metadata: Metadata bloku (dla wariantów)
            position: Pozycja (x, y, z)
            
        Returns:
            AE2BlockConversion z wynikiem konwersji
        """
        self.errors.clear()
        self.warnings.clear()
        
        normalized_block_id = normalize_block_id(block_id_1710)

        # Krok 1: Znajdź mapowanie bloku
        mapping = get_block_mapping(normalized_block_id)
        if not mapping:
            error_msg = f"AE2C-E-BLOCK-NOT-MAPPED: Nie znaleziono mapowania dla {block_id_1710}"
            self.errors.append(error_msg)
            return AE2BlockConversion(
                original_id=block_id_1710,
                original_pos=position,
                converted=ConversionResult(
                    success=False,
                    errors=[error_msg]
                )
            )
        
        # Krok 2: Rozwiąż warianty (np. Crafting Storage)
        block_id_1182 = self._resolve_variant(normalized_block_id, metadata)
        
        # Krok 3: Konwertuj NBT (z metadata!)
        nbt_result = None
        if mapping.has_tile_entity and nbt_1710:
            nbt_result = self._convert_nbt(
                mapping.nbt_converter or 'default',
                nbt_1710,
                normalized_block_id,
                metadata
            )
        
        # Krok 4: Obsłuż specjalne przypadki
        additional_blocks = []
        
        # Interface z patternami -> dodaj Pattern Provider
        if mapping.nbt_converter == 'interface' and nbt_result:
            patterns = nbt_result.converted_nbt.get('__patterns_for_provider') if nbt_result.converted_nbt else None
            if patterns:
                # Stwórz Pattern Provider obok Interface
                provider_pos = self._find_adjacent_position(position, nbt_1710)
                provider_nbt = self._create_pattern_provider_nbt(patterns, nbt_1710)
                
                additional_blocks.append(AE2BlockConversion(
                    original_id=f"{block_id_1710}:pattern_provider",
                    original_pos=provider_pos,
                    converted=ConversionResult(
                        success=True,
                        block_id_1182="ae2:pattern_provider",
                        nbt_1182=provider_nbt
                    )
                ))
                
                # Usuń patterny z Interface (bo są w Provider)
                del nbt_result.converted_nbt['__patterns_for_provider']

        if block_id_1182 in {'minecraft:lever', 'minecraft:grindstone'}:
            self.warnings.append(
                f"AE2C-W-LOSSY-FALLBACK: {normalized_block_id} -> {block_id_1182}; "
                "AE2 11.7.6 nie ma odpowiednika 1:1"
            )
        
        # Krok 5: Ekstrahuj blockstate_props (orientacja z NBT)
        blockstate_props = {}
        if nbt_1710:
            # Konwersja orientacji z 1.7.10 (forward/up) do BlockState
            forward = nbt_1710.get('forward')
            if forward is not None:
                facing_map = {0: 'down', 1: 'up', 2: 'north', 3: 'south', 4: 'west', 5: 'east'}
                blockstate_props['facing'] = facing_map.get(forward, 'north')
        
        # Zbuduj wynik
        converted = ConversionResult(
            success=True,
            block_id_1182=block_id_1182,
            blockstate_props=blockstate_props,
            nbt_1182=nbt_result.converted_nbt if nbt_result else None,
            additional_blocks=additional_blocks,
            errors=nbt_result.errors if nbt_result else [],
            warnings=(nbt_result.warnings if nbt_result else []) + self.warnings
        )
        
        return AE2BlockConversion(
            original_id=block_id_1710,
            original_pos=position,
            converted=converted
        )
    
    def convert_item(self, item_id_1710: str, 
                     item_nbt: Optional[Dict[str, Any]] = None,
                     metadata: int = 0) -> ConversionResult:
        """
        Konwertuje item AE2.
        
        Args:
            item_id_1710: ID itemu w 1.7.10
            item_nbt: NBT itemu
            metadata: Metadata (dla ItemMultiMaterial)
            
        Returns:
            ConversionResult
        """
        # Znajdź mapowanie
        mapping = get_item_mapping(item_id_1710, metadata)
        if not mapping:
            return ConversionResult(
                success=False,
                errors=[f"Nie znaleziono mapowania dla {item_id_1710}"]
            )
        
        # Konwertuj NBT jeśli to storage cell
        converted_nbt = None
        if item_nbt and 'StorageCell' in item_nbt:
            converter = StorageCellConverter()
            result = converter.convert(item_nbt)
            if result.success:
                converted_nbt = result.converted_nbt
        
        return ConversionResult(
            success=True,
            block_id_1182=mapping.id_1182,  # Właściwie item_id
            nbt_1182=converted_nbt
        )
    
    def _convert_nbt(self, converter_name: str, 
                     nbt_1710: Dict[str, Any],
                     block_id: str = None,
                     metadata: int = 0) -> NBTConversionResult:
        """Wykonuje konwersję NBT używając odpowiedniego konwertera"""
        converter = self.nbt_converters.get(converter_name)
        if not converter:
            converter = self.nbt_converters['default']
        
        return converter.convert(nbt_1710, block_id, metadata)
    
    def _resolve_variant(self, block_id_1710: str, metadata: int) -> str:
        """Rozwiązuje wariant bloku na podstawie metadata"""
        # Crafting Storage
        if 'BlockCraftingStorage' in block_id_1710:
            return resolve_crafting_storage_variant(block_id_1710, metadata)
        
        # Crafting Unit (zawiera Crafting Co-Processing Unit)
        if 'BlockCraftingUnit' in block_id_1710:
            new_id, _ = resolve_crafting_unit_variant(metadata)
            return new_id
        
        # Domyślnie zwróć bazowe mapowanie
        mapping = get_block_mapping(normalize_block_id(block_id_1710))
        return mapping.id_1182 if mapping else block_id_1710
    
    def _find_adjacent_position(self, pos: Tuple[int, int, int], 
                                 nbt_1710: Dict[str, Any]) -> Tuple[int, int, int]:
        """Znajduje sąsiednią pozycję dla Pattern Provider"""
        x, y, z = pos
        
        # Sprawdź orientację Interface
        forward = nbt_1710.get('forward', 2)  # Domyślnie NORTH
        
        # Umieść Provider w stronę "wskazywania" Interface
        # ForgeDirection: 0=DOWN, 1=UP, 2=NORTH, 3=SOUTH, 4=WEST, 5=EAST
        offsets = {
            0: (0, -1, 0),   # DOWN
            1: (0, 1, 0),    # UP
            2: (0, 0, -1),   # NORTH
            3: (0, 0, 1),    # SOUTH
            4: (-1, 0, 0),   # WEST
            5: (1, 0, 0),    # EAST
        }
        
        offset = offsets.get(forward, (0, 0, 1))
        return (x + offset[0], y + offset[1], z + offset[2])
    
    def _create_pattern_provider_nbt(self, patterns: list, 
                                     interface_nbt: Dict[str, Any]) -> Dict[str, Any]:
        """Tworzy NBT dla Pattern Provider"""
        return {
            'items': patterns,
            'priority': interface_nbt.get('priority', 0),
            'blockingMode': interface_nbt.get('blockingMode', False),
        }
    
    def is_ae2_block(self, block_id: str) -> bool:
        """Sprawdza czy blok należy do AE2"""
        return normalize_block_id(block_id) in ALL_AE2_BLOCK_IDS_1710
    
    def get_supported_blocks(self) -> List[str]:
        """Zwraca listę obsługiwanych bloków AE2"""
        return list(ALL_AE2_BLOCK_IDS_1710)
    
    def get_conversion_report(self) -> Dict[str, Any]:
        """Generuje raport o możliwościach konwersji"""
        from .mappings.block_mappings import BLOCK_MAPPINGS_1710_TO_1182
        from .mappings.item_mappings import ITEM_MAPPINGS_1710_TO_1182
        
        return {
            'source_version': self.SOURCE_VERSION,
            'target_version': self.TARGET_VERSION,
            'supported_blocks': len(BLOCK_MAPPINGS_1710_TO_1182),
            'supported_items': len(ITEM_MAPPINGS_1710_TO_1182),
            'nbt_converters': list(self.nbt_converters.keys()),
            'special_cases': [
                'Interface -> Interface + Pattern Provider (jeśli ma patterny)',
                'Crafting Storage metadata -> osobne bloki',
                'Item Damage -> NBT tag',
                'Storage Cell NBT transformacja',
            ]
        }


def main():
    """Demo konwertera AE2"""
    converter = AE2Converter()
    
    print("=" * 60)
    print("AE2 CONVERTER - Demo")
    print("=" * 60)
    
    # Raport
    report = converter.get_conversion_report()
    print("\nRaport konwersji:")
    print(f"  Wersja źródłowa: {report['source_version']}")
    print(f"  Wersja docelowa: {report['target_version']}")
    print(f"  Obsługiwane bloki: {report['supported_blocks']}")
    print(f"  Obsługiwane itemy: {report['supported_items']}")
    print(f"  Konwertery NBT: {len(report['nbt_converters'])}")
    
    # Przykład konwersji ME Drive
    print("\n" + "=" * 60)
    print("Przykład: Konwersja ME Drive")
    print("=" * 60)
    
    drive_nbt = {
        'priority': 5,
        'inv': [
            {'Slot': 0, 'id': 'appliedenergistics2:item.ItemBasicStorageCell.64k', 'Count': 1, 'tag': {
                'StorageCell': {'items': [], 'itemCount': 0}
            }},
            {'Slot': 1, 'id': 'appliedenergistics2:item.ItemBasicStorageCell.16k', 'Count': 1},
        ],
        'fuzzyMode': 0,
        'forward': 2,
        'up': 1
    }
    
    result = converter.convert_block(
        'appliedenergistics2:tile.BlockDrive',
        drive_nbt,
        position=(100, 64, 100)
    )
    
    print(f"\nOryginalny blok: {result.original_id}")
    print(f"Nowy blok: {result.converted.block_id_1182}")
    print(f"NBT: {json.dumps(result.converted.nbt_1182, indent=2)}")
    
    if result.converted.warnings:
        print(f"\nOstrzeżenia: {result.converted.warnings}")
    
    # Przykład konwersji Interface z patternami
    print("\n" + "=" * 60)
    print("Przykład: Konwersja Interface z patternami")
    print("=" * 60)
    
    interface_nbt = {
        'priority': 0,
        'config': [],
        'storage': [],
        'patterns': [
            {'id': 'appliedenergistics2:item.ItemEncodedPattern', 'Count': 1, 'tag': {
                'crafting': True,
                'in': [{'id': 'minecraft:cobblestone', 'Count': 3}],
                'out': [{'id': 'minecraft:stone_slab', 'Count': 6}]
            }}
        ],
        'forward': 3,
        'up': 1
    }
    
    result = converter.convert_block(
        'appliedenergistics2:tile.BlockInterface',
        interface_nbt,
        position=(100, 64, 101)
    )
    
    print(f"\nOryginalny blok: {result.original_id}")
    print(f"Nowy blok: {result.converted.block_id_1182}")
    print(f"Dodatkowe bloki: {len(result.converted.additional_blocks)}")
    
    if result.converted.additional_blocks:
        for block in result.converted.additional_blocks:
            print(f"  - {block.converted.block_id_1182} at {block.original_pos}")
    
    print("\n" + "=" * 60)
    print("Demo zakończone!")
    print("=" * 60)


if __name__ == "__main__":
    main()
