"""
Cable Converters

Konwertery dla kabli AE2 (Glass Cable, Covered Cable, Smart Cable, Dense Cable).

UWAGA: Kable w AE2 używają systemu "Part" (multipart), nie standardowych TileEntities.
Są przechowywane w specjalnych multipart block entities (np. BlockCableBus).

Kluczowa różnica:
- 1.7.10: Zapisuje usedChannels w NBT (liczba kanałów na kablu)
- 1.18.2: Nie zapisuje usedChannels w NBT - jest to tylko informacja wizualna

Struktura NBT 1.7.10 BlockCableBus:
{
    "id": "BlockCableBus",
    "x": int, "y": int, "z": int,
    "hasRedstone": byte,           # Stan redstone (true/false)
    "def:X": compound,             # Definicja części X (kabel, terminal, itp.)
    "extra:X": compound,           # Dodatkowe dane części X
    # Może zawierać wiele części (multipart)
}
"""

from typing import Dict, Any, List, Tuple, Optional
from .base_converter import BaseNBTConverter, NBTConversionResult


# Mapowanie typów części AE2 z 1.7.10 na 1.18.2
# Źródło 1.7.10: appeng.parts.*
# Cel 1.18.2: appeng.parts.* (zmieniły się nazwy/ścieżki)
PART_TYPE_MAPPING = {
    # === KABLE (Networking) ===
    'appeng.parts.networking.PartCable': 'cable',
    'appeng.parts.networking.PartDenseCable': 'dense_cable',
    'appeng.parts.networking.PartQuartzFiber': 'quartz_fiber',
    
    # === TERMINALE (Reporting) ===
    'appeng.parts.reporting.PartTerminal': 'crafting_terminal',
    'appeng.parts.reporting.PartPatternTerminal': 'pattern_encoding_terminal',
    'appeng.parts.reporting.PartPatternTerminalEx': 'pattern_encoding_terminal',  # Ex -> zwykły
    'appeng.parts.reporting.PartInterfaceTerminal': 'interface_terminal',
    'appeng.parts.reporting.PartStorageMonitor': 'storage_monitor',
    'appeng.parts.reporting.PartConversionMonitor': 'conversion_monitor',
    'appeng.parts.reporting.PartPanel': 'panel',
    'appeng.parts.reporting.PartSemiDarkPanel': 'semi_dark_monitor',
    'appeng.parts.reporting.PartDarkPanel': 'dark_monitor',
    
    # === BUS (Automation) ===
    'appeng.parts.automation.PartImportBus': 'import_bus',
    'appeng.parts.automation.PartExportBus': 'export_bus',
    'appeng.parts.automation.PartStorageBus': 'storage_bus',
    
    # === P2P TUNNELS ===
    'appeng.parts.p2p.PartP2PTunnel': 'p2p_tunnel',
    'appeng.parts.p2p.PartP2PTunnelLight': 'p2p_tunnel_light',
    'appeng.parts.p2p.PartP2PTunnelRedstone': 'p2p_tunnel_redstone',
    'appeng.parts.p2p.PartP2PTunnelItem': 'p2p_tunnel_item',
    'appeng.parts.p2p.PartP2PTunnelFluid': 'p2p_tunnel_fluid',
    'appeng.parts.p2p.PartP2PTunnelFE': 'p2p_tunnel_fe',
    'appeng.parts.p2p.PartP2PTunnelME': 'p2p_tunnel_me',
    
    # === INNE ===
    'appeng.parts.misc.PartCableAnchor': 'cable_anchor',
    'appeng.parts.misc.PartToggleBus': 'toggle_bus',
    'appeng.parts.misc.PartInvertedToggleBus': 'inverted_toggle_bus',
}

# Mapowanie kolorów kabli (wspólne dla wszystkich typów kabli)
CABLE_COLOR_MAPPING = {
    0: 'fluix',      # Fluix (domyślny)
    1: 'white',
    2: 'orange',
    3: 'magenta',
    4: 'light_blue',
    5: 'yellow',
    6: 'lime',
    7: 'pink',
    8: 'gray',
    9: 'light_gray',
    10: 'cyan',
    11: 'purple',
    12: 'blue',
    13: 'brown',
    14: 'green',
    15: 'red',
    16: 'black',
}


class CableConverter(BaseNBTConverter):
    """
    Konwerter dla BlockCableBus - obsługuje multipart (kable, terminale, bus).
    
    W 1.7.10 BlockCableBus może zawierać wiele części (multipart):
    - Kable (Glass, Covered, Smart, Dense, Quartz Fiber)
    - Terminale (Crafting, Pattern, Interface)
    - Bus (Import, Export, Storage)
    - Panele (Panel, Illuminated Panel)
    - Akcesoria (Cable Anchor, Toggle Bus)
    
    Struktura NBT:
    - def:X - definicja części X
    - extra:X - dodatkowe dane części X
    """
    
    @property
    def converter_name(self) -> str:
        return "cable_bus"
    
    def convert(self, nbt_1710: Dict[str, Any], block_id: str = None,
                metadata: int = 0) -> NBTConversionResult:
        """
        Konwertuje NBT BlockCableBus z 1.7.10 na 1.18.2.
        
        Args:
            nbt_1710: NBT Tile Entity z 1.7.10
            block_id: ID bloku (opcjonalnie)
            metadata: Metadata bloku (opcjonalnie)
            
        Returns:
            NBTConversionResult z przekonwertowanym NBT
        """
        self.reset()
        
        converted = {}
        parts_converted = []
        
        # Parsuj części multipart
        parts = self._parse_parts(nbt_1710)
        
        if parts:
            # Info: znaleziono części (nie jest to ostrzeżenie, ale dla kompletności)
            pass
            
            for part in parts:
                converted_part = self._convert_part(part)
                if converted_part:
                    parts_converted.append(converted_part)
        else:
            self._add_warning("No parts found in CableBus - may be empty or new format")
        
        # Zachowaj hasRedstone jeśli istnieje
        if 'hasRedstone' in nbt_1710:
            converted['hasRedstone'] = nbt_1710['hasRedstone']
        
        # Zachowaj pozycję
        for coord in ['x', 'y', 'z']:
            if coord in nbt_1710:
                converted[coord] = nbt_1710[coord]
        
        # Zapisz przekonwertowane części
        if parts_converted:
            converted['parts'] = parts_converted
        
        return self._create_result(converted)
    
    def _parse_parts(self, nbt_1710: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Parsuje części multipart z def:X i extra:X.
        
        Args:
            nbt_1710: NBT Tile Entity
            
        Returns:
            Lista części z id, definicją i dodatkowymi danymi
        """
        parts = []
        
        # Znajdź wszystkie klucze def:X
        for key in nbt_1710.keys():
            if key.startswith('def:'):
                part_id = key.split(':')[1]  # np. "6" z "def:6"
                part_def = nbt_1710[key]
                part_extra = nbt_1710.get(f'extra:{part_id}', {})
                
                parts.append({
                    'id': part_id,
                    'def': part_def,
                    'extra': part_extra
                })
        
        return parts
    
    def _convert_part(self, part: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Konwertuje pojedynczą część z 1.7.10 na 1.18.2.
        
        Args:
            part: Słownik z id, def, extra
            
        Returns:
            Przekonwertowana część lub None jeśli nieznana
        """
        part_def = part.get('def', {})
        part_extra = part.get('extra', {})
        
        # Pobierz typ części
        part_type = self._identify_part_type(part_def)
        if not part_type:
            self._add_warning(f"Unknown part type: {part_def}")
            return None
        
        # Zbuduj przekonwertowaną część
        converted_part = {
            'part_id': part['id'],
            'type': part_type,
        }
        
        # Konwertuj właściwości specyficzne dla typu
        properties = self._convert_part_properties(part_type, part_def, part_extra)
        if properties:
            converted_part['properties'] = properties
        
        # Konwertuj konfigurację (filtry, karty, itp.)
        config = self._convert_part_config(part_type, part_extra)
        if config:
            converted_part['config'] = config
        
        return converted_part
    
    def _identify_part_type(self, part_def: Dict[str, Any]) -> Optional[str]:
        """
        Identyfikuje typ części na podstawie definicji.
        
        Args:
            part_def: Definicja części z NBT
            
        Returns:
            Typ części w formacie 1.18.2 lub None
        """
        # Sprawdź klasę części
        part_class = part_def.get('class') if isinstance(part_def, dict) else None
        
        if part_class and part_class in PART_TYPE_MAPPING:
            return PART_TYPE_MAPPING[part_class]
        
        # Sprawdź inne wskaźniki w part_def
        if isinstance(part_def, dict):
            # Sprawdź type jeśli istnieje
            part_type = part_def.get('type')
            if part_type:
                return part_type
            
            # Sprawdź id
            part_id = part_def.get('id')
            if part_id:
                return str(part_id)
        
        # Jeśli part_def to string, użyj go bezpośrednio
        if isinstance(part_def, str):
            return PART_TYPE_MAPPING.get(part_def, part_def)
        
        return None
    
    def _convert_part_properties(self, part_type: str, 
                                  part_def: Dict[str, Any],
                                  part_extra: Dict[str, Any]) -> Dict[str, Any]:
        """
        Konwertuje właściwości części (kolor, orientacja, itp.).
        
        Args:
            part_type: Typ części
            part_def: Definicja części
            part_extra: Dodatkowe dane części
            
        Returns:
            Słownik właściwości
        """
        properties = {}
        
        if not isinstance(part_def, dict):
            return properties
        
        # Kolor kabla
        if 'color' in part_def:
            color_id = part_def['color']
            properties['color'] = CABLE_COLOR_MAPPING.get(color_id, 'fluix')
        
        # Orientacja/facing (dla terminali i bus)
        if 'forward' in part_extra:
            forward = part_extra['forward']
            facing_map = {0: 'down', 1: 'up', 2: 'north', 3: 'south', 4: 'west', 5: 'east'}
            properties['facing'] = facing_map.get(forward, 'north')
        
        # Used channels (wizualne, tylko dla kabli)
        if 'usedChannels' in part_extra:
            properties['usedChannels'] = part_extra['usedChannels']
            # Info: usedChannels jest tylko wizualne
            pass
        
        # Custom name
        if 'customName' in part_extra:
            properties['customName'] = part_extra['customName']
        
        return properties
    
    def _convert_part_config(self, part_type: str, 
                             part_extra: Dict[str, Any]) -> Dict[str, Any]:
        """
        Konwertuje konfigurację części (filtry, karty, ustawienia).
        
        Args:
            part_type: Typ części
            part_extra: Dodatkowe dane części
            
        Returns:
            Słownik konfiguracji
        """
        config = {}
        
        if not isinstance(part_extra, dict):
            return config
        
        # Wspólne ustawienia dla bus
        if 'bus' in part_type or part_type in ['import_bus', 'export_bus', 'storage_bus']:
            # Fuzzy mode
            if 'fuzzyMode' in part_extra:
                config['fuzzyMode'] = bool(part_extra['fuzzyMode'])
            
            # Redstone control
            if 'redstoneControl' in part_extra:
                config['redstoneControl'] = part_extra['redstoneControl']
            
            # Crafting only (dla storage bus)
            if 'craftingOnly' in part_extra:
                config['craftingOnly'] = bool(part_extra['craftingOnly'])
            
            # Priority (dla storage bus)
            if 'priority' in part_extra:
                config['priority'] = part_extra['priority']
            
            # Access (read/write)
            if 'access' in part_extra:
                config['access'] = part_extra['access']
        
        # Filtry (wspólne dla wszystkich bus)
        if 'filter' in part_extra:
            config['filter'] = self._convert_filter(part_extra['filter'])
        
        # Karty upgrade
        if 'upgrades' in part_extra:
            config['upgrades'] = self._convert_upgrades(part_extra['upgrades'])
        
        # Ustawienia terminala
        if 'terminal' in part_type:
            # Sortowanie
            if 'sortBy' in part_extra:
                config['sortBy'] = part_extra['sortBy']
            
            # Kierunek sortowania
            if 'sortDir' in part_extra:
                config['sortDir'] = part_extra['sortDir']
            
            # Tryb wyświetlania
            if 'viewMode' in part_extra:
                config['viewMode'] = part_extra['viewMode']
        
        # Pattern terminal - ustawienia encoding
        if 'pattern_encoding' in part_type:
            if 'craftingMode' in part_extra:
                config['craftingMode'] = bool(part_extra['craftingMode'])
        
        return config
    
    def _convert_filter(self, filter_data: Any) -> List[Dict[str, Any]]:
        """
        Konwertuje filtr z 1.7.10 na 1.18.2.
        
        Args:
            filter_data: Dane filtra z NBT
            
        Returns:
            Lista przekonwertowanych itemów
        """
        if not filter_data:
            return []
        
        converted_filter = []
        
        # Obsługa różnych formatów
        if isinstance(filter_data, list):
            for item in filter_data:
                converted_item = self._convert_filter_item(item)
                if converted_item:
                    converted_filter.append(converted_item)
        elif isinstance(filter_data, dict):
            # Pojedynczy item
            converted_item = self._convert_filter_item(filter_data)
            if converted_item:
                converted_filter.append(converted_item)
        
        return converted_filter
    
    def _convert_filter_item(self, item: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Konwertuje pojedynczy item w filtrze.
        
        Args:
            item: Dane itemu
            
        Returns:
            Przekonwertowany item lub None
        """
        if not isinstance(item, dict):
            return None
        
        converted = {}
        
        # ID itemu
        if 'id' in item:
            converted['id'] = item['id']
        
        # Metadata/Damage
        if 'Damage' in item:
            converted['Damage'] = item['Damage']
        
        # Count
        if 'Count' in item:
            converted['Count'] = item['Count']
        
        # NBT tag
        if 'tag' in item:
            converted['tag'] = item['tag']
        
        return converted if converted else None
    
    def _convert_upgrades(self, upgrades_data: Any) -> List[str]:
        """
        Konwertuje karty upgrade z 1.7.10 na 1.18.2.
        
        Args:
            upgrades_data: Dane upgrade'ów z NBT
            
        Returns:
            Lista nazw upgrade'ów
        """
        if not upgrades_data:
            return []
        
        converted_upgrades = []
        
        # Mapowanie nazw upgrade'ów
        upgrade_mapping = {
            'fuzzy_card': 'fuzzy_card',
            'inverter_card': 'inverter_card',
            'acceleration_card': 'speed_card',
            'speed_card': 'speed_card',
            'capacity_card': 'capacity_card',
            'redstone_card': 'redstone_card',
            'crafting_card': 'crafting_card',
        }
        
        if isinstance(upgrades_data, list):
            for upgrade in upgrades_data:
                if isinstance(upgrade, str):
                    converted_upgrades.append(upgrade_mapping.get(upgrade, upgrade))
                elif isinstance(upgrade, dict) and 'id' in upgrade:
                    upgrade_id = upgrade['id']
                    # Wyekstrahuj nazwę z ID
                    if ':' in upgrade_id:
                        upgrade_name = upgrade_id.split(':')[-1].lower()
                        converted_upgrades.append(upgrade_mapping.get(upgrade_name, upgrade_name))
        elif isinstance(upgrades_data, dict):
            # Pojedynczy upgrade
            for key, value in upgrades_data.items():
                if value:
                    converted_upgrades.append(upgrade_mapping.get(key, key))
        
        return converted_upgrades


class GlassCableConverter(CableConverter):
    """Konwerter dla Glass Cable (przezroczysty kabel)"""
    
    @property
    def converter_name(self) -> str:
        return "glass_cable"


class CoveredCableConverter(CableConverter):
    """Konwerter dla Covered Cable (kabel w osłonie)"""
    
    @property
    def converter_name(self) -> str:
        return "covered_cable"


class SmartCableConverter(CableConverter):
    """Konwerter dla Smart Cable (kabel pokazujący zajętość kanałów)"""
    
    @property
    def converter_name(self) -> str:
        return "smart_cable"


class DenseCableConverter(CableConverter):
    """Konwerter dla Dense Cable (kabel o dużej przepustowości - 32 kanały)"""
    
    @property
    def converter_name(self) -> str:
        return "dense_cable"


class QuartzFiberConverter(CableConverter):
    """
    Konwerter dla Quartz Fiber.
    
    Quartz Fiber łączy sieci ME bez przekazywania kanałów.
    W 1.7.10 może mieć inną strukturę niż standardowe kable.
    """
    
    @property
    def converter_name(self) -> str:
        return "quartz_fiber"
