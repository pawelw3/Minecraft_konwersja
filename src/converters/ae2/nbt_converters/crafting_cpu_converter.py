"""
Crafting CPU Converter

Konwertuje NBT Crafting CPU (wieloblok) z 1.7.10 do 1.18.2.

WAŻNE: Struktura danych crafting job uległa fundamentalnej zmianie:
- 1.7.10: Bezpośrednie pola (finalOutput, inventory, tasks, waitingFor, itp.)
- 1.18.2: Obiekt "job" (ExecutingCraftingJob) + "inventory"

Konwersja zachowuje strukturę wielobloku, ale aktywne zadania crafting mogą być stracone.
"""

from typing import Dict, Any
from .base_converter import BaseNBTConverter, NBTConversionResult


class CraftingCPUConverter(BaseNBTConverter):
    """Konwerter dla Crafting CPU (wieloblok)
    
    Źródło 1.7.10: appeng.tile.crafting.TileCraftingTile
        - core: boolean (czy to blok centralny)
        - Jeśli core=true: dane CraftingCPUCluster zapisane bezpośrednio
          (finalOutput, inventory, tasks, waitingFor, elapsedTime, itp.)
    
    Źródło 1.18.2: appeng.blockentity.crafting.CraftingBlockEntity
        - core: boolean
        - Jeśli core=true: dane przechowywane w CraftingCpuLogic
          (inventory, job - opcjonalny)
    
    UWAGA: Konwersja aktywnych zadań crafting (tasks/job) jest niemożliwa
    bez głębokiej rekonstrukcji struktury. Wieloblok przebuduje się
    po załadowaniu świata, ale aktywne zadania mogą być stracone.
    """
    
    @property
    def converter_name(self) -> str:
        return "crafting_cpu"
    
    def convert(self, nbt_1710: Dict[str, Any], block_id: str = None,
                metadata: int = 0) -> NBTConversionResult:
        """
        Konwertuje NBT Crafting CPU.
        
        Struktura 1.7.10:
        {
            "core": true/false,
            "finalOutput": {...},  # jeśli core=true
            "inventory": [...],     # jeśli core=true
            "tasks": [...],         # jeśli core=true
            "waitingFor": [...],    # jeśli core=true
            "elapsedTime": 123,     # jeśli core=true
            "startItemCount": 100,  # jeśli core=true
            "remainingItemCount": 50,  # jeśli core=true
            "waiting": false,       # jeśli core=true
            "isComplete": false,    # jeśli core=true
            "link": {...}           # jeśli core=true, opcjonalne
        }
        
        Struktura 1.18.2:
        {
            "core": true/false,
            "inventory": [...],  # jeśli core=true
            "job": {...}         # jeśli core=true, opcjonalne
        }
        """
        self.reset()
        
        converted = {}
        
        # Pole core - identyczne w obu wersjach
        is_core = nbt_1710.get('core', False)
        converted['core'] = is_core
        
        if is_core:
            # To blok centralny - zawiera dane crafting job
            self._add_warning(
                "Crafting CPU core block: active crafting jobs may be lost during conversion. "
                "The multiblock will rebuild on world load, but pending crafts may need to be restarted."
            )
            
            # Próba konwersji inventory (to możemy zachować)
            inventory = nbt_1710.get('inventory', [])
            if inventory:
                converted['inventory'] = self._convert_inventory_list(inventory)
            
            # Pozostałe dane (tasks, waitingFor, finalOutput, itp.) są niekompatybilne
            # 1.7.10 ma płaską strukturę, 1.18.2 ma obiekt "job"
            # Nie ma sensownego sposobu na konwersję bez pełnej rekonstrukcji job
            
            # Dodajemy informację o stracie danych
            lost_fields = []
            for field in ['finalOutput', 'tasks', 'waitingFor', 'elapsedTime', 
                         'startItemCount', 'remainingItemCount', 'waiting', 
                         'isComplete', 'link']:
                if field in nbt_1710:
                    lost_fields.append(field)
            
            if lost_fields:
                self._add_warning(
                    f"Following crafting data fields cannot be converted and will be lost: {', '.join(lost_fields)}"
                )
        
        # Konwersja custom name (opcjonalne)
        custom_name = nbt_1710.get('customName')
        if custom_name:
            converted['customName'] = custom_name
        
        return self._create_result(converted)
    
    def _convert_inventory_list(self, inventory: list) -> list:
        """
        Konwertuje listę itemów z 1.7.10 do formatu 1.18.2.
        
        1.7.10: Lista IAEItemStack (zapisanych przez writeToNBT)
        1.18.2: ListTag z CompoundTag dla każdego itemu
        """
        result = []
        for item in inventory:
            if not item:
                continue
            converted = self._convert_item_stack(item)
            if converted:
                result.append(converted)
        return result


class CraftingMonitorConverter(BaseNBTConverter):
    """Konwerter dla Crafting Monitor
    
    Crafting Monitor jest częścią wielobloku Crafting CPU.
    W 1.7.10: TileCraftingMonitorTile
    W 1.18.2: CraftingMonitorBlockEntity
    
    Monitor nie przechowuje dodatkowych danych NBT poza orientacją
    (która jest w BlockState w 1.18.2).
    """
    
    @property
    def converter_name(self) -> str:
        return "crafting_monitor"
    
    def convert(self, nbt_1710: Dict[str, Any], block_id: str = None,
                metadata: int = 0) -> NBTConversionResult:
        """
        Crafting Monitor nie ma specyficznych danych NBT.
        Wszystkie istotne dane są w wielobloku (CraftingCPUCluster).
        """
        self.reset()
        
        # Crafting Monitor nie ma dodatkowych pól NBT
        # Orientacja jest w BlockState
        converted = {}
        
        # Ewentualnie custom name
        custom_name = nbt_1710.get('customName')
        if custom_name:
            converted['customName'] = custom_name
        
        return self._create_result(converted)
