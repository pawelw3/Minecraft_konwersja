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
    Konwerter dla Crafting Unit (część wielobloku Crafting CPU).
    
    Crafting Unit to podstawowy blok wielobloku CPU.
    Może być "core" block (główny blok z danymi).
    
    Źródło 1.7.10: appeng.tile.crafting.TileCraftingTile
        - core: boolean (czy to blok centralny z danymi CPU)
        - Jeśli core=true: zapisane są dane CraftingCPUCluster
    
    Źródło 1.18.2: appeng.blockentity.crafting.CraftingBlockEntity
        - core: boolean
        - Jeśli core=true: dane w CraftingCpuLogic (inventory, job)
    
    UWAGA: Konwersja aktywnych zadań crafting jest ograniczona ze względu
    na różnice w strukturze danych między wersjami.
    """
    
    @property
    def converter_name(self) -> str:
        return "crafting_unit"
    
    def convert(self, nbt_1710: Dict[str, Any], block_id: str = None,
                metadata: int = 0) -> NBTConversionResult:
        """
        Konwertuje NBT Crafting Unit.
        
        Struktura 1.7.10:
        {
            "core": true/false,
            # Jeśli core=true, dodatkowe pola z CraftingCPUCluster:
            "finalOutput": {...},
            "inventory": [...],
            "tasks": [...],
            ...
        }
        
        Struktura 1.18.2:
        {
            "core": true/false,
            # Jeśli core=true:
            "inventory": [...],
            "job": {...}
        }
        """
        self.reset()
        
        converted = {}
        
        # Pole core - kluczowe dla wielobloku
        is_core = nbt_1710.get('core', False)
        converted['core'] = is_core
        
        if is_core:
            # To blok centralny - zawiera dane crafting job
            self._add_warning(
                "Crafting CPU core block detected. "
                "Active crafting jobs may be lost during conversion. "
                "The multiblock will rebuild on world load."
            )
            
            # Konwersja inventory (to możemy zachować)
            inventory = nbt_1710.get('inventory', [])
            if inventory:
                converted['inventory'] = self._convert_crafting_inventory(inventory)
            
            # Pozostałe dane są niekompatybilne (tasks, waitingFor, finalOutput, itp.)
            # 1.7.10 ma płaską strukturę, 1.18.2 ma obiekt "job"
            lost_fields = [f for f in ['finalOutput', 'tasks', 'waitingFor', 'elapsedTime', 
                         'startItemCount', 'remainingItemCount', 'waiting', 
                         'isComplete', 'link'] if f in nbt_1710]
            
            if lost_fields:
                self._add_warning(
                    f"Cannot convert crafting data fields: {', '.join(lost_fields)}"
                )
        
        # Custom name (jeśli ustawione)
        custom_name = nbt_1710.get('customName')
        if custom_name:
            converted['customName'] = custom_name
        
        return self._create_result(converted)
    
    def _convert_crafting_inventory(self, inventory: list) -> list:
        """Konwertuje inventory crafting CPU"""
        result = []
        for item in inventory:
            if not item:
                continue
            converted = self._convert_item_stack(item)
            if converted:
                result.append(converted)
        return result


class CraftingStorageConverter(BaseNBTConverter):
    """
    Konwerter dla Crafting Storage.
    
    Crafting Storage to Crafting Unit + pamięć dla CPU.
    Różne rozmiary: 1k, 4k, 16k, 64k (i 256k w 1.18.2)
    
    Źródło 1.7.10: appeng.tile.crafting.TileCraftingStorageTile
        - Rozmiar określony przez metadata (0-3)
    
    Źródło 1.18.2: appeng.blockentity.crafting.CraftingBlockEntity
        - Osobne bloki dla każdego rozmiaru (crafting_unit_1k, 4k, ...)
        - Rozmiar w BlockState/NBT?
    
    UWAGA: Metadata jest przekazywana przez parametr metadata!
    """
    
    @property
    def converter_name(self) -> str:
        return "crafting_storage"
    
    def convert(self, nbt_1710: Dict[str, Any], block_id: str = None,
                metadata: int = 0) -> NBTConversionResult:
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
        
        converted = {
            'size_variant': metadata & 3,  # bit 4 to formed, nie rozmiar
            'formed': bool(metadata & 4),
            'size_bytes': self._get_size_bytes(metadata)
        }
        
        # Custom name
        custom_name = nbt_1710.get('customName')
        if custom_name:
            converted['customName'] = custom_name
        
        # UWAGA: Orientacja jest w BlockState, nie w NBT!
        
        return self._create_result(converted)
    
    def _get_size_bytes(self, metadata: int) -> int:
        """Zwraca rozmiar w bajtach na podstawie metadata"""
        sizes = {
            0: 1024,      # 1k
            1: 4096,      # 4k
            2: 16384,     # 16k
            3: 65536,     # 64k
        }
        return sizes.get(metadata & 3, 1024)
    
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
    
    Źródło 1.7.10: appeng.tile.crafting.TileCraftingTile (metadata=1)
    Źródło 1.18.2: appeng.blockentity.crafting.CraftingBlockEntity (typ accelerator)
    """
    
    @property
    def converter_name(self) -> str:
        return "crafting_accelerator"
    
    def convert(self, nbt_1710: Dict[str, Any], block_id: str = None,
                metadata: int = 0) -> NBTConversionResult:
        """Konwertuje Co-Processing Unit -> Accelerator"""
        self.reset()
        
        converted = {}
        
        # UWAGA: Orientacja jest w BlockState, nie w NBT!
        
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
    
    def convert(self, nbt_1710: Dict[str, Any], block_id: str = None,
                metadata: int = 0) -> NBTConversionResult:
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
        
        # UWAGA: Orientacja jest w BlockState, nie w NBT!
        
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
    
    def convert(self, nbt_1710: Dict[str, Any], block_id: str = None,
                metadata: int = 0) -> NBTConversionResult:
        """Konwertuje NBT Crafting Monitor"""
        self.reset()
        
        converted = {}
        
        # UWAGA: Orientacja jest w BlockState, nie w NBT!
        
        # Custom name (często używane do oznaczania CPU)
        custom_name = nbt_1710.get('customName')
        if custom_name:
            converted['customName'] = custom_name
        
        return self._create_result(converted)
