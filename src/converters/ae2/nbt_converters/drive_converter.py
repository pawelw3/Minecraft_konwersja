"""
ME Drive Converter

Konwertuje NBT ME Drive z 1.7.10 do 1.18.2.

KLUCZOWE RÓŻNICE:
- 1.7.10: inv (lista), priority (int), fuzzyMode (byte)
- 1.18.2: items (lista), priority (int), fuzzyMode (string)
"""

from typing import Dict, Any, List
from .base_converter import BaseNBTConverter, NBTConversionResult


class DriveConverter(BaseNBTConverter):
    """Konwerter dla ME Drive i ME Chest"""
    
    @property
    def converter_name(self) -> str:
        return "drive"
    
    def convert(self, nbt_1710: Dict[str, Any], block_id: str = None) -> NBTConversionResult:
        """
        Konwertuje NBT ME Drive/Chest.
        
        Struktura 1.7.10:
        {
            "id": "AEBaseTile",
            "inv": [{Slot: 0, id: "...", Count: 1, tag: {...}}, ...],
            "priority": 0,
            "fuzzyMode": 0,
            "forward": 2,
            "up": 1,
            "customName": ""
        }
        
        Struktura 1.18.2:
        {
            "id": "ae2:drive",
            "items": [...],
            "priority": 0,
            "fuzzyMode": "IGNORE_ALL",
            "visual": {...}
        }
        """
        self.reset()
        
        converted = {
            'priority': nbt_1710.get('priority', 0),
        }
        
        # Konwersja inwentarza (storage cells)
        inv_1710 = nbt_1710.get('inv', [])
        if inv_1710:
            converted['items'] = self._convert_drive_inventory(inv_1710)
        else:
            converted['items'] = []
        
        # Konwersja fuzzy mode
        fuzzy_mode = nbt_1710.get('fuzzyMode', 0)
        converted['fuzzyMode'] = self._convert_fuzzy_mode(fuzzy_mode)
        
        # Konwersja custom name
        custom_name = nbt_1710.get('customName')
        if custom_name:
            converted['customName'] = custom_name
        
        # Orientacja
        orientation = self._get_orientation(nbt_1710)
        if orientation:
            converted['visual'] = {'rotation': orientation.get('facing', 'north')}
        
        return self._create_result(converted)
    
    def _convert_drive_inventory(self, inv_1710: List[Dict]) -> List[Dict]:
        """
        Konwertuje inwentarz Drive z 1.7.10 do 1.18.2.
        
        ME Drive ma 10 slotów na storage cells.
        ME Chest ma 1 slot na storage cell + 54 slotów na itemy.
        """
        items = []
        
        for slot_data in inv_1710:
            if not slot_data:
                continue
            
            slot = slot_data.get('Slot', 0)
            item_id = slot_data.get('id', '')
            
            # Konwertuj storage cell
            converted_item = self._convert_storage_cell_item(slot_data)
            
            if converted_item:
                converted_item['Slot'] = slot
                items.append(converted_item)
        
        return items
    
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
    
    def _convert_fuzzy_mode(self, fuzzy_mode: int) -> str:
        """
        Konwertuje fuzzy mode z int do string.
        
        1.7.10: 0, 1, 2 (int)
        1.18.2: "IGNORE_ALL", "PERCENT_25", "PERCENT_50", ...
        """
        modes = {
            0: "IGNORE_ALL",
            1: "PERCENT_25",
            2: "PERCENT_50",
            3: "PERCENT_75",
            4: "PERCENT_99"
        }
        return modes.get(fuzzy_mode, "IGNORE_ALL")


class ChestConverter(DriveConverter):
    """
    Konwerter dla ME Chest - dziedziczy z DriveConverter
    z drobnymi modyfikacjami.
    """
    
    @property
    def converter_name(self) -> str:
        return "chest"
    
    def convert(self, nbt_1710: Dict[str, Any], block_id: str = None) -> NBTConversionResult:
        """
        ME Chest jest podobny do ME Drive, ale ma tylko 1 slot na cell
        i dodatkowy inwentarz na itemy.
        """
        # Użyj konwersji z Drive, ale oznacz jako chest
        result = super().convert(nbt_1710, block_id)
        
        if result.success and result.converted_nbt:
            # Dodaj marker że to chest (może być użyteczne)
            result.converted_nbt['chestType'] = True
        
        return result
