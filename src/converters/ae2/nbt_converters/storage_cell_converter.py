"""
Storage Cell Converter

Konwertuje NBT Storage Cell (jako item w Drive/Chest) z 1.7.10 do 1.18.2.

UWAGA: To jest konwerter dla NBT samej komórki (jako item),
nie dla zawartości komórki (która jest konwertowana w DriveConverter).
"""

from typing import Dict, Any
from .base_converter import BaseNBTConverter, NBTConversionResult


class StorageCellConverter(BaseNBTConverter):
    """
    Konwerter dla Storage Cells.
    
    Obsługuje:
    - Item Storage Cells (1k, 4k, 16k, 64k)
    - Fluid Storage Cells (1k, 4k, 16k, 64k)
    - Portable Cells
    - View Cell
    
    Źródło 1.7.10: appeng.items.storage.ItemBasicStorageCell
        - NBT: StorageCell.items, StorageCell.itemCount
        
    Źródło 1.18.2: appeng.items.storage.BasicStorageCell
        - NBT: storage.items, storage.count
    
    UWAGA: W 1.18.2 struktura NBT może się różnić - wymaga weryfikacji!
    """
    
    @property
    def converter_name(self) -> str:
        return "storage_cell"
    
    def convert(self, nbt_1710: Dict[str, Any], block_id: str = None,
                metadata: int = 0) -> NBTConversionResult:
        """
        Konwertuje NBT Storage Cell item.
        
        Struktura 1.7.10:
        {
            "StorageCell": {
                "items": [...],
                "itemCount": 123
            },
            "priority": 0,
            "fuzzyMode": 0,
            "partition": [...]  # Filtrowanie
        }
        
        Struktura 1.18.2:
        {
            "storage": {
                "items": [...],
                "count": 123
            },
            "priority": 0,
            "fuzzyMode": "IGNORE_ALL",
            "partition": [...]
        }
        """
        self.reset()
        
        converted = {}
        
        # Konwersja zawartości storage
        storage_cell = nbt_1710.get('StorageCell', {})
        if storage_cell:
            converted['storage'] = self._convert_storage_content(storage_cell)
        
        # Priority
        priority = nbt_1710.get('priority', 0)
        converted['priority'] = priority
        
        # Fuzzy mode
        fuzzy_mode = nbt_1710.get('fuzzyMode', 0)
        converted['fuzzyMode'] = self._convert_fuzzy_mode(fuzzy_mode)
        
        # Partition (filtr)
        partition = nbt_1710.get('partition', [])
        if partition:
            converted['partition'] = self._convert_partition(partition)
        
        # Include/Exclude mode
        include_mode = nbt_1710.get('include', True)
        converted['include'] = include_mode
        
        return self._create_result(converted)
    
    def _convert_storage_content(self, storage_cell: Dict[str, Any]) -> Dict[str, Any]:
        """
        Konwertuje zawartość storage cell.
        
        Kluczowa konwersja: items z 1.7.10 do formatu 1.18.2
        """
        items_1710 = storage_cell.get('items', [])
        converted_items = []
        
        for item in items_1710:
            converted = self._convert_item_stack(item)
            if converted:
                converted_items.append(converted)
        
        return {
            'items': converted_items,
            'count': storage_cell.get('itemCount', 0)
        }
    
    def _convert_partition(self, partition: list) -> list:
        """
        Konwertuje partition list (filtr typów).
        
        Partition to lista dozwolonych typów itemów.
        """
        result = []
        
        for entry in partition:
            if isinstance(entry, dict):
                # Konwertuj ID itemu
                converted = {
                    'id': self._convert_item_id(entry.get('id', '')),
                }
                
                # Dodaj metadata jeśli istnieje
                damage = entry.get('Damage', 0)
                if damage > 0:
                    converted['tag'] = {'Damage': damage}
                
                result.append(converted)
            else:
                # Jeśli to już string, po prostu przekonwertuj ID
                result.append(self._convert_item_id(str(entry)))
        
        return result
    
    def _convert_fuzzy_mode(self, fuzzy_mode: int) -> str:
        """Konwertuje fuzzy mode z int na string"""
        modes = {
            0: "IGNORE_ALL",
            1: "PERCENT_25",
            2: "PERCENT_50", 
            3: "PERCENT_75",
            4: "PERCENT_99"
        }
        return modes.get(fuzzy_mode, "IGNORE_ALL")
    
    def convert_cell_type(self, cell_type_1710: str, size: int) -> str:
        """
        Konwertuje typ komórki.
        
        Returns:
            ID komórki w 1.18.2
        """
        from ..mappings import get_item_mapping
        
        mapping = get_item_mapping(cell_type_1710)
        if mapping:
            return mapping.id_1182
        
        # Domyślne mapowanie
        return f"ae2:item_storage_cell_{size}k"


class PortableCellConverter(StorageCellConverter):
    """
    Konwerter dla Portable Cell.
    
    Portable Cell w 1.7.10 to osobny item, w 1.18.2 też.
    Dodatkowo ma energy NBT.
    """
    
    @property
    def converter_name(self) -> str:
        return "portable_cell"
    
    def convert(self, nbt_1710: Dict[str, Any], block_id: str = None) -> NBTConversionResult:
        """
        Konwertuje Portable Cell.
        
        Dodatkowo obsługuje energy (AE/FE).
        """
        # Najpierw użyj standardowej konwersji storage
        result = super().convert(nbt_1710, block_id)
        
        if not result.success:
            return result
        
        # Dodaj energy
        energy = nbt_1710.get('internalCurrentPower', 0)
        if energy > 0:
            # Konwertuj AE na FE (jeśli potrzeba)
            # W 1.18.2 Portable Cell używa AE (wewnętrznie)
            result.converted_nbt['internalCurrentPower'] = energy
        
        return result
