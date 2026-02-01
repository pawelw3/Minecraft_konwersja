"""
ME Drive Converter

Konwertuje NBT ME Drive z 1.7.10 do 1.18.2.

KLUCZOWE RÓŻNICE:
- 1.7.10: inv (compound z item0, item1, ...), priority (int)
- 1.18.2: inv (compound z item0, item1, ...), priority (int)

WAŻNE: Format inventory jest taki sam w obu wersjach (nested compound),
ale struktura ItemStack się zmienia.
"""

from typing import Dict, Any, List
from .base_converter import BaseNBTConverter, NBTConversionResult


class DriveConverter(BaseNBTConverter):
    """Konwerter dla ME Drive
    
    Źródło 1.7.10: appeng.tile.storage.TileDrive
        - inv: AppEngInternalInventory (10 slotów) - zapisany jako compound
          z kluczami item0, item1, ..., item9
        - priority: int
        - forward/up: ForgeDirection (orientacja - teraz w BlockState)
    
    Źródło 1.18.2: appeng.blockentity.storage.DriveBlockEntity
        - inv: AppEngCellInventory (10 slotów) - zapisany jako compound
          z kluczami item0, item1, ..., item9
        - priority: int
        - Orientacja: w BlockState (facing)
    """
    
    @property
    def converter_name(self) -> str:
        return "drive"
    
    def convert(self, nbt_1710: Dict[str, Any], block_id: str = None,
                metadata: int = 0) -> NBTConversionResult:
        """
        Konwertuje NBT ME Drive.
        
        Struktura 1.7.10:
        {
            "id": "AEBaseTile",
            "inv": {
                "item0": {id: "...", Count: 1, tag: {...}},
                "item1": {},  # pusty jeśli brak itemu
                ...
            },
            "priority": 0,
            "forward": 2,  # ForgeDirection - teraz w BlockState
            "up": 1
        }
        
        Struktura 1.18.2:
        {
            "id": "ae2:drive",
            "inv": {
                "item0": {...},
                "item1": {},
                ...
            },
            "priority": 0
        }
        """
        self.reset()
        
        converted = {
            'priority': nbt_1710.get('priority', 0),
        }
        
        # Konwersja inwentarza (storage cells)
        # 1.7.10: inv jako compound z item0, item1, ...
        inv_1710 = nbt_1710.get('inv', {})
        if isinstance(inv_1710, dict):
            converted['inv'] = self._convert_drive_inventory_compound(inv_1710)
        elif isinstance(inv_1710, list):
            # Fallback dla starego formatu listowego (jeśli wystąpi)
            converted['inv'] = self._convert_drive_inventory_list(inv_1710)
        else:
            converted['inv'] = {}
        
        # Konwersja custom name (opcjonalne)
        custom_name = nbt_1710.get('customName')
        if custom_name:
            converted['customName'] = custom_name
        
        return self._create_result(converted)
    
    def _convert_drive_inventory_compound(self, inv_1710: Dict[str, Any]) -> Dict[str, Any]:
        """
        Konwertuje inwentarz Drive z formatu compound 1.7.10 do 1.18.2.
        
        Format: {"item0": {...}, "item1": {...}, ...}
        """
        result = {}
        
        for key, item_data in inv_1710.items():
            if not key.startswith('item'):
                continue
            
            if not item_data:
                # Pusty slot - zapisz pusty compound
                result[key] = {}
                continue
            
            # Konwertuj storage cell
            converted_item = self._convert_storage_cell_item(item_data)
            if converted_item:
                result[key] = converted_item
            else:
                result[key] = {}
        
        return result
    
    def _convert_drive_inventory_list(self, inv_1710: List[Dict]) -> Dict[str, Any]:
        """
        Konwertuje inwentarz z formatu listowego (fallback).
        
        Format: [{Slot: 0, id: "...", ...}, ...]
        """
        result = {}
        
        for slot_data in inv_1710:
            if not slot_data:
                continue
            
            slot = slot_data.get('Slot', 0)
            slot_key = f'item{slot}'
            
            # Konwertuj storage cell
            converted_item = self._convert_storage_cell_item(slot_data)
            if converted_item:
                result[slot_key] = converted_item
        
        return result
    
    def _convert_storage_cell_item(self, item_nbt: Dict[str, Any]) -> Dict[str, Any]:
        """
        Konwertuje storage cell z zawartością.
        
        Kluczowe: konwersja NBT zawartości komórki!
        """
        from ..mappings import get_item_mapping
        
        item_id = item_nbt.get('id', '')
        tag = item_nbt.get('tag', {})
        
        # Znajdź mapowanie itemu
        mapping = get_item_mapping(item_id)
        if mapping:
            new_id = mapping.id_1182
        else:
            new_id = self._convert_item_id(item_id)
        
        result = {
            'id': new_id,
            'Count': item_nbt.get('Count', 1)
        }
        
        # Konwersja NBT storage cell (jeśli ma zawartość)
        if tag:
            new_tag = self._convert_storage_cell_nbt(tag)
            if new_tag:
                result['tag'] = new_tag
        
        return result
    
    def _convert_storage_cell_nbt(self, cell_nbt: Dict[str, Any]) -> Dict[str, Any]:
        """
        Konwertuje NBT zawartości storage cell.
        
        Struktura 1.7.10:
        {
            "StorageCell": {
                "items": [...],
                "itemCount": 123
            }
        }
        
        Struktura 1.18.2:
        {
            "storage": {
                "items": [...],
                "count": 123
            }
        }
        """
        storage_cell = cell_nbt.get('StorageCell', {})
        if not storage_cell:
            return {}
        
        items_1710 = storage_cell.get('items', [])
        converted_items = []
        
        for item in items_1710:
            converted_item = self._convert_item_stack(item)
            if converted_item:
                converted_items.append(converted_item)
        
        return {
            'storage': {
                'items': converted_items,
                'count': storage_cell.get('itemCount', 0)
            }
        }


class ChestConverter(DriveConverter):
    """Konwerter dla ME Chest - dziedziczy z DriveConverter
    
    Źródło 1.7.10: appeng.tile.storage.TileChest
        - Podobny do TileDrive, ale tylko 1 slot na cell (inv ma 2 sloty:
          slot 0 na cell, slot 1 na jukebox)
        - priority: int
        - paintedColor: byte (kolor)
        - config: ConfigManager (różne ustawienia)
    
    Źródło 1.18.2: appeng.blockentity.storage.MEChestBlockEntity
        - inv: 2 sloty (cell + jukebox)
        - priority: int
        - paintedColor: byte
        - config: ConfigManager
        - keyTypeSelection: KeyTypeSelection
    """
    
    @property
    def converter_name(self) -> str:
        return "chest"
    
    def convert(self, nbt_1710: Dict[str, Any], block_id: str = None,
                metadata: int = 0) -> NBTConversionResult:
        """
        ME Chest jest podobny do ME Drive, ale ma dodatkowe pola.
        """
        # Użyj konwersji z Drive dla priority i inv
        result = super().convert(nbt_1710, block_id, metadata)
        
        if not result.success or not result.converted_nbt:
            return result
        
        # Dodaj paintedColor (opcjonalne, domyślnie Transparent=0)
        painted_color = nbt_1710.get('paintedColor', 0)
        if painted_color != 0:  # Zapisz tylko jeśli nie jest domyślny
            result.converted_nbt['paintedColor'] = painted_color
        
        # TODO: Konwersja config (ConfigManager) - zawiera ustawienia dostępu,
        # sortowania, itp. Wymaga analizy struktury ConfigManager w obu wersjach.
        
        return result
