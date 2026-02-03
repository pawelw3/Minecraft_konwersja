"""
Konwerter NBT dla TileEnderChest (EnderStorage)

Konwertuje TileEnderChest z wersji 1.7.10 do 1.18.2.
"""

from typing import Dict, Any, Optional
import sys
import os

# Dodaj ścieżkę do src dla importów
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..'))

from .base_converter import BaseEnderStorageNBTConverter, NBTConversionResult


class EnderChestNBTConverter(BaseEnderStorageNBTConverter):
    """
    Konwerter NBT dla TileEnderChest.
    
    Konwertuje dane skrzyni Ender z 1.7.10 do 1.18.2.
    
    Format 1.7.10:
    {
        "freq": int (0-4095),
        "owner": str ("global" lub nazwa gracza),
        "rotation": int (0-3),
        "Items": [...]  # opcjonalnie, współdzielone przez wszystkie skrzynie o tej samej freq
    }
    
    Format 1.18.2:
    {
        "Frequency": {
            "left": str (kolor),
            "middle": str (kolor),
            "right": str (kolor),
            "owner": str (UUID, opcjonalnie)
        },
        "rotation": int (0-3),
        "Items": [...]  # opcjonalnie
    }
    """
    
    @property
    def converter_name(self) -> str:
        return "EnderChestNBTConverter"
    
    @property
    def source_te_id(self) -> str:
        # Na mapie TE ID to "Ender Chest" (ze spacja), nie "TileEnderChest"
        return "Ender Chest"
    
    @property
    def target_te_id(self) -> str:
        return "enderstorage:ender_chest"
    
    def convert(self, nbt_1710: Dict[str, Any], block_id: str = None,
                metadata: int = 0) -> NBTConversionResult:
        """
        Konwertuje NBT 'Ender Chest' z 1.7.10 do 1.18.2.
        
        UWAGA: Na mapie 1.7.10 TE ID to 'Ender Chest' (ze spacja), nie 'TileEnderChest'.
        
        Args:
            nbt_1710: Słownik NBT z wersji 1.7.10
            block_id: ID bloku (opcjonalnie)
            metadata: Metadata bloku (0=chest, 1=tank)
            
        Returns:
            NBTConversionResult z przekonwertowanym NBT
        """
        self.reset()
        
        try:
            converted = {}
            
            # Konwersja frequency (int -> Frequency object)
            freq_int = nbt_1710.get('freq', 0)
            owner_str = nbt_1710.get('owner', 'global')
            converted['Frequency'] = self._convert_frequency(freq_int, owner_str)
            
            # Konwersja rotacji (0-3) - w NBT to 'rot', nie 'rotation'
            if 'rot' in nbt_1710:
                converted['rotation'] = nbt_1710['rot']
            elif 'rotation' in nbt_1710:
                converted['rotation'] = nbt_1710['rotation']
            
            # Konwersja inventory (Items) - wspoldzielone przez wszystkie skrzynie o tej samej freq
            # W 1.7.10 Items sa w storage managerze, nie w NTE bloku
            # Ale jesli sa w NBT, przekonwertuj
            if 'Items' in nbt_1710 and nbt_1710['Items']:
                items = nbt_1710['Items']
                if isinstance(items, list):
                    converted['Items'] = self._convert_inventory(items)
                else:
                    converted['Items'] = items
            
            # Dodaj id Tile Entity dla 1.18.2
            converted['id'] = self.target_te_id
            
            # Zapisz oryginalne freq i owner jako metadane (dla debugowania)
            converted['__original_freq'] = freq_int
            converted['__original_owner'] = owner_str
            
            return self._create_result(converted, success=True)
            
        except Exception as e:
            self._add_error(f"Error converting Ender Chest NBT: {str(e)}")
            return self._create_result(success=False)
