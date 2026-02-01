"""
IO Converters - IO Port, Spatial IO

Konwertery dla urządzeń wejścia/wyjścia AE2.
"""

from typing import Dict, Any
from .base_converter import BaseNBTConverter, NBTConversionResult


class IOPortConverter(BaseNBTConverter):
    """
    Konwerter dla ME IO Port.
    
    IO Port przesyła dane między storage cells a siecią ME.
    
    Źródło 1.7.10: appeng.tile.storage.TileIOPort
        - cells: AppEngInternalInventory (12 slotów - 6 input, 6 output)
        - upgrades: UpgradeInventory (3 sloty)
        - lastRedstoneState: int (ordinal YesNo)
        - ConfigManager: Settings (REDSTONE_CONTROLLED, FULLNESS_MODE, OPERATION_MODE)
    
    Źródło 1.18.2: appeng.blockentity.storage.IOPortBlockEntity
        - inputCells + outputCells: AppEngInternalInventory (6+6 slotów)
        - upgrades: IUpgradeInventory (3 sloty)
        - lastRedstoneState: int
        - IConfigManager: te same ustawienia
    
    WAŻNE: W 1.18.2 inventory cells jest podzielone na input/output,
    ale w NBT jest zapisywane jako combinedInventory.
    """
    
    @property
    def converter_name(self) -> str:
        return "io_port"
    
    def convert(self, nbt_1710: Dict[str, Any], block_id: str = None,
                metadata: int = 0) -> NBTConversionResult:
        """
        Konwertuje NBT IO Port.
        
        Struktura 1.7.10:
        {
            "cells": {  # 12 slotów - pierwsze 6 input, kolejne 6 output
                "item0": {...}, "item1": {...}, ... "item11": {...}
            },
            "upgrades": {"item0": {...}, "item1": {...}, "item2": {...}},
            "lastRedstoneState": 0,
            # ConfigManager settings (REDSTONE_CONTROLLED, FULLNESS_MODE, OPERATION_MODE)
        }
        
        Struktura 1.18.2:
        {
            # Inventory jest zarządzane przez AEBaseInvBlockEntity
            # upgrades są zapisywane osobno
            "upgrades": {...},
            "lastRedstoneState": 0,
            # ConfigManager settings
        }
        """
        self.reset()
        
        converted = {}
        
        # Konwersja lastRedstoneState
        last_rs = nbt_1710.get('lastRedstoneState', 0)
        converted['lastRedstoneState'] = last_rs
        
        # Konwersja upgrades
        upgrades = nbt_1710.get('upgrades', {})
        if upgrades:
            converted['upgrades'] = self._convert_upgrades(upgrades)
        
        # Konwersja cells (storage cells w slotach)
        cells = nbt_1710.get('cells', {})
        if cells:
            # W 1.18.2 inventory jest zarządzane przez klasę bazową
            # ale możemy zachować te same dane
            converted['inv'] = self._convert_cells_inventory(cells)
        
        # ConfigManager settings są zapisywane przez manager.writeToNBT()
        # Te ustawienia są kompatybilne między wersjami
        # (REDSTONE_CONTROLLED, FULLNESS_MODE, OPERATION_MODE)
        # Są zapisywane jako stringi w NBT
        
        # Przekopiuj wszystkie ustawienia configu
        config_settings = [
            'REDSTONE_CONTROLLED', 'FULLNESS_MODE', 'OPERATION_MODE'
        ]
        for setting in config_settings:
            if setting in nbt_1710:
                converted[setting] = nbt_1710[setting]
        
        return self._create_result(converted)
    
    def _convert_cells_inventory(self, cells: Dict[str, Any]) -> Dict[str, Any]:
        """
        Konwertuje inventory cells.
        
        1.7.10: 12 slotów w jednym compound (6 input + 6 output)
        1.18.2: Te same 12 slotów, ale logika podzielona na input/output
        """
        result = {}
        for key, item_data in cells.items():
            if not key.startswith('item'):
                continue
            if not item_data:
                result[key] = {}
                continue
            converted_item = self._convert_storage_cell_item(item_data)
            if converted_item:
                result[key] = converted_item
            else:
                result[key] = {}
        return result
    
    def _convert_storage_cell_item(self, item_nbt: Dict[str, Any]) -> Dict[str, Any]:
        """Konwertuje storage cell"""
        from ..mappings import get_item_mapping
        
        item_id = item_nbt.get('id', '')
        tag = item_nbt.get('tag', {})
        
        mapping = get_item_mapping(item_id)
        new_id = mapping.id_1182 if mapping else self._convert_item_id(item_id)
        
        result = {
            'id': new_id,
            'Count': item_nbt.get('Count', 1)
        }
        
        if tag:
            new_tag = self._convert_storage_cell_nbt(tag)
            if new_tag:
                result['tag'] = new_tag
        
        return result
    
    def _convert_storage_cell_nbt(self, cell_nbt: Dict[str, Any]) -> Dict[str, Any]:
        """Konwertuje NBT zawartości storage cell"""
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
    
    def _convert_upgrades(self, upgrades: Dict[str, Any]) -> Dict[str, Any]:
        """Konwertuje inventory upgrades"""
        result = {}
        for key, item_data in upgrades.items():
            if not key.startswith('item'):
                continue
            if not item_data:
                result[key] = {}
                continue
            converted = self._convert_item_stack(item_data)
            if converted:
                result[key] = converted
            else:
                result[key] = {}
        return result


class SpatialIOPortConverter(BaseNBTConverter):
    """
    Konwerter dla Spatial IO Port.
    
    Spatial IO Port umożliwia transport obszarów przestrzeni.
    
    Źródło 1.7.10: appeng.tile.spatial.TileSpatialIOPort
        - lastRedstoneState: int (ordinal YesNo)
        - Nie ma inventory w NBT (tylko redstone state)
    
    Źródło 1.18.2: appeng.blockentity.spatial.SpatialIOPortBlockEntity
        - lastRedstoneState: int
        - Także bez inventory w NBT
    
    UWAGA: Spatial IO wymaga pylonów i spatial storage cell,
    ale sam port nie przechowuje danych o obszarze - te są w cell.
    """
    
    @property
    def converter_name(self) -> str:
        return "spatial_io_port"
    
    def convert(self, nbt_1710: Dict[str, Any], block_id: str = None,
                metadata: int = 0) -> NBTConversionResult:
        """
        Konwertuje NBT Spatial IO Port.
        
        Struktura 1.7.10:
        {
            "lastRedstoneState": 0
        }
        
        Struktura 1.18.2:
        {
            "lastRedstoneState": 0
        }
        """
        self.reset()
        
        converted = {}
        
        # lastRedstoneState - identyczne w obu wersjach
        last_rs = nbt_1710.get('lastRedstoneState', 0)
        converted['lastRedstoneState'] = last_rs
        
        # Custom name (opcjonalne)
        custom_name = nbt_1710.get('customName')
        if custom_name:
            converted['customName'] = custom_name
        
        return self._create_result(converted)


class SpatialPylonConverter(BaseNBTConverter):
    """
    Konwerter dla Spatial Pylon.
    
    Spatial Pylon to część struktury do Spatial IO.
    Nie przechowuje danych NBT - tylko wizualny stan jest w BlockState.
    
    Źródło 1.7.10: appeng.tile.spatial.TileSpatialPylon
    Źródło 1.18.2: appeng.blockentity.spatial.SpatialPylonBlockEntity
    """
    
    @property
    def converter_name(self) -> str:
        return "spatial_pylon"
    
    def convert(self, nbt_1710: Dict[str, Any], block_id: str = None,
                metadata: int = 0) -> NBTConversionResult:
        """
        Spatial Pylon nie ma specyficznych danych NBT.
        Stan (połączenie, aktywność) jest w BlockState.
        """
        self.reset()
        
        converted = {}
        
        # Custom name (jeśli ustawione)
        custom_name = nbt_1710.get('customName')
        if custom_name:
            converted['customName'] = custom_name
        
        return self._create_result(converted)


class SpatialAnchorConverter(BaseNBTConverter):
    """
    Konwerter dla Spatial Anchor.
    
    UWAGA: Spatial Anchor nie istnieje w 1.7.10!
    Jest to nowy blok w 1.18.2 zastępujący funkcję chunk loading.
    
    Jeśli występuje na mapie, prawdopodobnie został dodany ręcznie
    lub jest to błąd mapowania.
    """
    
    @property
    def converter_name(self) -> str:
        return "spatial_anchor"
    
    def convert(self, nbt_1710: Dict[str, Any], block_id: str = None,
                metadata: int = 0) -> NBTConversionResult:
        """
        Spatial Anchor nie ma odpowiednika w 1.7.10.
        """
        self.reset()
        self._add_warning(
            "Spatial Anchor is a 1.18.2+ block with no 1.7.10 equivalent. "
            "It should not appear in conversion from 1.7.10."
        )
        return self._create_result({})
