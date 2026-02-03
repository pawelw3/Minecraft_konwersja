"""
Konwerter NBT dla TileEnderTank (EnderStorage)

Konwertuje TileEnderTank z wersji 1.7.10 do 1.18.2.
"""

from typing import Dict, Any, Optional
import sys
import os

# Dodaj ścieżkę do src dla importów
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..'))

from .base_converter import BaseEnderStorageNBTConverter, NBTConversionResult


class EnderTankNBTConverter(BaseEnderStorageNBTConverter):
    """
    Konwerter NBT dla TileEnderTank.
    
    Konwertuje dane zbiornika Ender z 1.7.10 do 1.18.2.
    
    Format 1.7.10:
    {
        "freq": int (0-4095),
        "owner": str ("global" lub nazwa gracza),
        "invert_redstone": bool,
        "rotation": int (0-3)
        # Ciecz jest współdzielona przez wszystkie zbiorniki o tej samej freq
        # i przechowywana w EnderStorageManager, nie w NBT bloku
    }
    
    Format 1.18.2:
    {
        "Frequency": {
            "left": str (kolor),
            "middle": str (kolor),
            "right": str (kolor),
            "owner": str (UUID, opcjonalnie)
        },
        "pressure_state": {
            "invert_redstone": bool
        }
    }
    """
    
    @property
    def converter_name(self) -> str:
        return "EnderTankNBTConverter"
    
    @property
    def source_te_id(self) -> str:
        return "EnderStorage:tileEnderTank"
    
    @property
    def target_te_id(self) -> str:
        return "enderstorage:ender_tank"
    
    def convert(self, nbt_1710: Dict[str, Any], block_id: str = None,
                metadata: int = 0) -> NBTConversionResult:
        """
        Konwertuje NBT TileEnderTank z 1.7.10 do 1.18.2.
        
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
            
            # Konwersja stanu ciśnieniowego
            pressure_state = {}
            if 'invert_redstone' in nbt_1710:
                pressure_state['invert_redstone'] = nbt_1710['invert_redstone']
            else:
                pressure_state['invert_redstone'] = False
            
            converted['pressure_state'] = pressure_state
            
            # Dodaj id Tile Entity dla 1.18.2
            converted['id'] = self.target_te_id
            
            # Zapisz oryginalne freq i owner jako metadane (dla debugowania)
            converted['__original_freq'] = freq_int
            converted['__original_owner'] = owner_str
            
            return self._create_result(converted, success=True)
            
        except Exception as e:
            self._add_error(f"Error converting EnderTank NBT: {str(e)}")
            return self._create_result(success=False)
