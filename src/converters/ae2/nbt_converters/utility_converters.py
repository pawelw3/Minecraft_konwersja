"""
Utility Converters for AE2

Konwertery dla utility blocks AE2:
- Charger
- Inscriber
- Vibration Chamber
- Growth Accelerator
- Condenser
- IO Port
- Security Station
- Wireless Access Point
"""

from typing import Dict, Any
from .base_converter import BaseNBTConverter, NBTConversionResult


class ChargerConverter(BaseNBTConverter):
    """Konwerter dla Charger (ładowanie Certus Quartz)"""
    
    @property
    def converter_name(self) -> str:
        return "charger"
    
    def convert(self, nbt_1710: Dict[str, Any], block_id: str = None) -> NBTConversionResult:
        """
        Konwertuje NBT Charger.
        
        Charger ma 2 sloty (input + output) i przechowuje energię.
        """
        self.reset()
        
        converted = {}
        
        # Konwersja inwentarza (2 sloty)
        inv = nbt_1710.get('inv', [])
        if inv:
            converted['items'] = [
                self._convert_item_stack(item)
                for item in inv if item
            ]
        
        # Energia (AE)
        energy = nbt_1710.get('internalCurrentPower', 0)
        converted['internalCurrentPower'] = energy
        
        # Orientacja
        orientation = self._get_orientation(nbt_1710)
        if orientation:
            converted['visual'] = {'rotation': orientation.get('facing', 'north')}
        
        return self._create_result(converted)


class InscriberConverter(BaseNBTConverter):
    """Konwerter dla Inscriber (tworzenie procesorów)"""
    
    @property
    def converter_name(self) -> str:
        return "inscriber"
    
    def convert(self, nbt_1710: Dict[str, Any], block_id: str = None) -> NBTConversionResult:
        """
        Konwertuje NBT Inscriber.
        
        Inscriber ma 3 sloty: top, bottom, output + side slot.
        """
        self.reset()
        
        converted = {}
        
        # Konwersja inwentarza
        inv = nbt_1710.get('inv', [])  # top, bottom, output
        side_inv = nbt_1710.get('sideInv', [])  # side slot
        
        if inv:
            converted['items'] = [
                self._convert_item_stack(item)
                for item in inv if item
            ]
        
        if side_inv:
            converted['sideItems'] = [
                self._convert_item_stack(item)
                for item in side_inv if item
            ]
        
        # Progress
        progress = nbt_1710.get('progress', 0)
        if progress > 0:
            converted['progress'] = progress
        
        # Orientacja
        orientation = self._get_orientation(nbt_1710)
        if orientation:
            converted['visual'] = {'rotation': orientation.get('facing', 'north')}
        
        return self._create_result(converted)


class VibrationChamberConverter(BaseNBTConverter):
    """
    Konwerter dla Vibration Chamber (generator AE).
    
    W 1.7.10: własny system energii AE
    W 1.18.2: kompatybilność z Forge Energy
    """
    
    @property
    def converter_name(self) -> str:
        return "vibration_chamber"
    
    def convert(self, nbt_1710: Dict[str, Any], block_id: str = None) -> NBTConversionResult:
        """
        Konwertuje NBT Vibration Chamber.
        
        Ma slot na paliwo i produkuje AE.
        """
        self.reset()
        
        converted = {}
        
        # Inwentarz (1 slot na paliwo)
        inv = nbt_1710.get('inv', [])
        if inv:
            converted['items'] = [
                self._convert_item_stack(item)
                for item in inv if item
            ]
        
        # Burn time (czas palenia)
        burn_time = nbt_1710.get('burnTime', 0)
        if burn_time > 0:
            converted['burnTime'] = burn_time
        
        # Max burn time
        max_burn_time = nbt_1710.get('maxBurnTime', 0)
        if max_burn_time > 0:
            converted['maxBurnTime'] = max_burn_time
        
        # Energia
        energy = nbt_1710.get('internalCurrentPower', 0)
        converted['internalCurrentPower'] = energy
        
        return self._create_result(converted)


class IOPortConverter(BaseNBTConverter):
    """
    Konwerter dla IO Port.
    
    Transfer zawartości między storage cells.
    """
    
    @property
    def converter_name(self) -> str:
        return "io_port"
    
    def convert(self, nbt_1710: Dict[str, Any], block_id: str = None) -> NBTConversionResult:
        """
        Konwertuje NBT IO Port.
        
        Ma 6 slotów na cells (input) + 6 slotów (output).
        """
        self.reset()
        
        converted = {}
        
        # Konwersja inwentarza cells
        inv = nbt_1710.get('inv', [])
        if inv:
            converted['items'] = [
                self._convert_storage_cell_item(item)
                for item in inv if item
            ]
        
        # Priorytet
        priority = nbt_1710.get('priority', 0)
        converted['priority'] = priority
        
        # Orientacja
        orientation = self._get_orientation(nbt_1710)
        if orientation:
            converted['visual'] = {'rotation': orientation.get('facing', 'north')}
        
        return self._create_result(converted)
    
    def _convert_storage_cell_item(self, item_nbt: Dict[str, Any]) -> Dict[str, Any]:
        """Konwertuje storage cell z zachowaniem NBT"""
        from ..mappings import get_item_mapping
        
        item_id = item_nbt.get('id', '')
        tag = item_nbt.get('tag', {})
        
        mapping = get_item_mapping(item_id)
        new_id = mapping.id_1182 if mapping else self._convert_item_id(item_id)
        
        result = {
            'id': new_id,
            'Count': item_nbt.get('Count', 1)
        }
        
        # Konwertuj NBT cell jeśli istnieje
        if tag and 'StorageCell' in tag:
            # Użyj StorageCellConverter
            from .storage_cell_converter import StorageCellConverter
            converter = StorageCellConverter()
            cell_result = converter.convert(tag)
            if cell_result.success and cell_result.converted_nbt:
                result['tag'] = cell_result.converted_nbt
        
        return result


class SecurityStationConverter(BaseNBTConverter):
    """
    Konwerter dla Security Station.
    
    Kontrola dostępu do sieci - ważne dla praw graczy!
    """
    
    @property
    def converter_name(self) -> str:
        return "security_station"
    
    def convert(self, nbt_1710: Dict[str, Any], block_id: str = None) -> NBTConversionResult:
        """
        Konwertuje NBT Security Station.
        
        UWAGA: Prawa dostępu wymagają konwersji UUID!
        """
        self.reset()
        
        converted = {}
        
        # Lista graczy i ich prawa
        players = nbt_1710.get('players', [])
        if players:
            # UWAGA: Wymaga konwersji UUID!
            converted['players'] = self._convert_player_list(players)
        
        # Inwentarz (karty dostępu)
        inv = nbt_1710.get('inv', [])
        if inv:
            converted['items'] = [
                self._convert_item_stack(item)
                for item in inv if item
            ]
        
        # Właściciel
        owner = nbt_1710.get('owner')
        if owner:
            # UWAGA: Wymaga konwersji UUID!
            converted['owner'] = owner
            self._add_warning("Wymagana konwersja UUID właściciela")
        
        return self._create_result(converted)
    
    def _convert_player_list(self, players: list) -> list:
        """Konwertuje listę graczy z ich prawami"""
        result = []
        for player in players:
            converted = {
                'name': player.get('name', ''),
                'uuid': player.get('uuid', ''),  # Do konwersji!
                'permissions': player.get('permissions', 0)
            }
            result.append(converted)
            
            if converted['uuid']:
                self._add_warning(
                    f"Gracz {converted['name']} wymaga konwersji UUID"
                )
        
        return result


class WirelessAccessPointConverter(BaseNBTConverter):
    """
    Konwerter dla Wireless Access Point.
    
    Punkt dostępowy do sieci ME przez wireless.
    """
    
    @property
    def converter_name(self) -> str:
        return "wireless_ap"
    
    def convert(self, nbt_1710: Dict[str, Any], block_id: str = None) -> NBTConversionResult:
        """
        Konwertuje NBT Wireless Access Point.
        
        Ma slot na wireless booster.
        """
        self.reset()
        
        converted = {}
        
        # Slot na booster
        inv = nbt_1710.get('inv', [])
        if inv:
            converted['items'] = [
                self._convert_item_stack(item)
                for item in inv if item
            ]
        
        # Nazwa (do identyfikacji w terminalu)
        custom_name = nbt_1710.get('customName')
        if custom_name:
            converted['customName'] = custom_name
        
        # Orientacja
        orientation = self._get_orientation(nbt_1710)
        if orientation:
            converted['visual'] = {'rotation': orientation.get('facing', 'north')}
        
        return self._create_result(converted)


class QuantumBridgeConverter(BaseNBTConverter):
    """
    Konwerter dla Quantum Bridge.
    
    Ważne: Zachowanie połączenia quantum!
    """
    
    @property
    def converter_name(self) -> str:
        return "quantum_link"
    
    def convert(self, nbt_1710: Dict[str, Any], block_id: str = None) -> NBTConversionResult:
        """
        Konwertuje NBT Quantum Link Chamber.
        
        Zawiera singularity (pair_id) - kluczowe dla połączenia!
        """
        self.reset()
        
        converted = {}
        
        # Singularity (para połączenia)
        singularity = nbt_1710.get('singularity')
        if singularity:
            converted['singularity'] = singularity
            # pair_id jest w singularity
        
        # Slot na singularity
        inv = nbt_1710.get('inv', [])
        if inv:
            converted['items'] = [
                self._convert_item_stack(item)
                for item in inv if item
            ]
        
        # Stan połączenia
        status = nbt_1710.get('status', 'offline')
        converted['status'] = status
        
        return self._create_result(converted)


class SpatialIOPortConverter(BaseNBTConverter):
    """
    Konwerter dla Spatial IO Port.
    
    Obsługa Spatial Storage Cells.
    """
    
    @property
    def converter_name(self) -> str:
        return "spatial_io_port"
    
    def convert(self, nbt_1710: Dict[str, Any], block_id: str = None) -> NBTConversionResult:
        """Konwertuje NBT Spatial IO Port"""
        self.reset()
        
        converted = {}
        
        # Slot na spatial cell
        inv = nbt_1710.get('inv', [])
        if inv:
            converted['items'] = [
                self._convert_item_stack(item)
                for item in inv if item
            ]
        
        # Orientacja
        orientation = self._get_orientation(nbt_1710)
        if orientation:
            converted['visual'] = {'rotation': orientation.get('facing', 'north')}
        
        return self._create_result(converted)
