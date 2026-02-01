"""
Crafting System Converters

Konwertery dla systemu craftingu AE2:
- Crafting Unit
- Crafting Storage
- Crafting Monitor
- Molecular Assembler
"""

from typing import Dict, Any
from .base_converter import BaseNBTConverter, NBTConversionResult


class CraftingUnitConverter(BaseNBTConverter):
    """
    Konwerter dla Crafting Unit.
    
    Crafting Unit to proste bloki bez inwentarza.
    Zawierają tylko podstawowe dane o stanie.
    """
    
    @property
    def converter_name(self) -> str:
        return "crafting_unit"
    
    def convert(self, nbt_1710: Dict[str, Any], block_id: str = None) -> NBTConversionResult:
        """
        Konwertuje NBT Crafting Unit.
        
        Crafting Unit ma minimalne dane - głównie orientacja.
        """
        self.reset()
        
        converted = {}
        
        # Orientacja
        orientation = self._get_orientation(nbt_1710)
        if orientation:
            converted['visual'] = {'rotation': orientation.get('facing', 'north')}
        
        # Custom name (jeśli ustawione)
        custom_name = nbt_1710.get('customName')
        if custom_name:
            converted['customName'] = custom_name
        
        return self._create_result(converted)


class CraftingStorageConverter(BaseNBTConverter):
    """
    Konwerter dla Crafting Storage.
    
    Crafting Storage to Crafting Unit + pamięć dla CPU.
    Różne rozmiary: 1k, 4k, 16k, 64k (i 256k w 1.18.2)
    """
    
    @property
    def converter_name(self) -> str:
        return "crafting_storage"
    
    def convert(self, nbt_1710: Dict[str, Any], block_id: str = None) -> NBTConversionResult:
        """
        Konwertuje NBT Crafting Storage.
        
        W 1.7.10 metadata określa rozmiar:
        - 0: 1k
        - 1: 4k  
        - 2: 16k
        - 3: 64k
        
        W 1.18.2 są osobne bloki dla każdego rozmiaru.
        """
        self.reset()
        
        # Metadata musi być przekazana w block_id lub nbt
        metadata = nbt_1710.get('metadata', 0)
        
        converted = {
            'size_variant': metadata,  # Zachowaj info o rozmiarze
            'size_bytes': self._get_size_bytes(metadata)
        }
        
        # Orientacja
        orientation = self._get_orientation(nbt_1710)
        if orientation:
            converted['visual'] = {'rotation': orientation.get('facing', 'north')}
        
        # Custom name
        custom_name = nbt_1710.get('customName')
        if custom_name:
            converted['customName'] = custom_name
        
        return self._create_result(converted)
    
    def _get_size_bytes(self, metadata: int) -> int:
        """Zwraca rozmiar w bajtach na podstawie metadata"""
        sizes = {
            0: 1024,      # 1k
            1: 4096,      # 4k
            2: 16384,     # 16k
            3: 65536,     # 64k
        }
        return sizes.get(metadata, 1024)
    
    def resolve_block_id(self, base_id: str, metadata: int) -> str:
        """
        Zwraca pełne ID bloku 1.18.2 na podstawie metadata.
        
        Returns:
            ID bloku z odpowiednim rozmiarem
        """
        from ..mappings.block_mappings import resolve_crafting_storage_variant
        return resolve_crafting_storage_variant(base_id, metadata)


class CraftingAcceleratorConverter(BaseNBTConverter):
    """
    Konwerter dla Crafting Co-Processing Unit (1.7.10) 
    -> Crafting Accelerator (1.18.2).
    
    To jest "speed upgrade" dla CPU craftingu.
    """
    
    @property
    def converter_name(self) -> str:
        return "crafting_accelerator"
    
    def convert(self, nbt_1710: Dict[str, Any], block_id: str = None) -> NBTConversionResult:
        """Konwertuje Co-Processing Unit -> Accelerator"""
        self.reset()
        
        converted = {}
        
        # Orientacja
        orientation = self._get_orientation(nbt_1710)
        if orientation:
            converted['visual'] = {'rotation': orientation.get('facing', 'north')}
        
        return self._create_result(converted)


class MolecularAssemblerConverter(BaseNBTConverter):
    """
    Konwerter dla Molecular Assembler.
    
    Molecular Assembler wykonuje faktyczny crafting.
    W 1.18.2 wymaga Pattern Provider zamiast Interface.
    """
    
    @property
    def converter_name(self) -> str:
        return "molecular_assembler"
    
    def convert(self, nbt_1710: Dict[str, Any], block_id: str = None) -> NBTConversionResult:
        """
        Konwertuje NBT Molecular Assembler.
        
        Struktura 1.7.10:
        {
            "progress": 0,  # Postęp craftingu
            "isCrafting": false,
            "forward": 2,
            "up": 1
        }
        """
        self.reset()
        
        converted = {}
        
        # Stan craftingu (zostanie zresetowany po konwersji)
        is_crafting = nbt_1710.get('isCrafting', False)
        if is_crafting:
            self._add_warning(
                "Molecular Assembler był w trakcie craftingu - "
                "stan zostanie zresetowany"
            )
        
        # Orientacja
        orientation = self._get_orientation(nbt_1710)
        if orientation:
            converted['visual'] = {'rotation': orientation.get('facing', 'north')}
        
        # Custom name
        custom_name = nbt_1710.get('customName')
        if custom_name:
            converted['customName'] = custom_name
        
        return self._create_result(converted)


class CraftingMonitorConverter(BaseNBTConverter):
    """
    Konwerter dla Crafting Monitor.
    
    Wyświetla postęp craftingu. W 1.7.10 często ma custom name.
    """
    
    @property
    def converter_name(self) -> str:
        return "crafting_monitor"
    
    def convert(self, nbt_1710: Dict[str, Any], block_id: str = None) -> NBTConversionResult:
        """Konwertuje NBT Crafting Monitor"""
        self.reset()
        
        converted = {}
        
        # Orientacja
        orientation = self._get_orientation(nbt_1710)
        if orientation:
            converted['visual'] = {'rotation': orientation.get('facing', 'north')}
        
        # Custom name (często używane do oznaczania CPU)
        custom_name = nbt_1710.get('customName')
        if custom_name:
            converted['customName'] = custom_name
        
        return self._create_result(converted)
