"""
ID Resolver for AE2 Converter

Obsługa dynamicznych ID bloków z różnych źródeł:
- Główna mapa (mapa_1710)
- Mapy testowe (lightweigh_map_templates/1710)
- Dynamiczne przypisanie ID
"""

from typing import Dict, Optional, Set, Tuple
from dataclasses import dataclass
import json
import os


@dataclass
class BlockIDInfo:
    """Informacje o ID bloku"""
    block_id: str
    metadata: int = 0
    tile_entity_type: Optional[str] = None
    source: str = "unknown"  # Skąd pochodzi ID


class IDResolver:
    """
    Resolver dla dynamicznych ID bloków AE2.
    
    W Minecraft 1.7.10 bloki mają numeryczne ID przypisywane dynamicznie.
    Ten resolver mapuje nazwy bloków na ich faktyczne ID w danej mapie.
    """
    
    def __init__(self):
        # Mapa: nazwa -> numeryczne ID (z level.dat lub innych źródeł)
        self.block_id_map: Dict[str, int] = {}
        # Mapa: numeryczne ID -> nazwa
        self.reverse_id_map: Dict[int, str] = {}
        # Cache dla map testowych
        self.test_world_cache: Dict[str, Dict[str, int]] = {}
        
    def load_from_map(self, map_path: str) -> bool:
        """
        Ładuje mapowanie ID z mapy Minecraft.
        
        UWAGA: W 1.7.10 z Forge bloki z modów mają STRINGOWE ID w NBT chunków.
        Nie ma potrzeby parsowania level.dat dla mapowania numerycznego ID.
        
        Args:
            map_path: Ścieżka do folderu mapy (zawierającego level.dat)
            
        Returns:
            True jeśli udało się załadować
            
        Raises:
            NotImplementedError: Jeśli wykryjemy stare numeryczne ID (przed Forge)
        """
        level_dat = os.path.join(map_path, "level.dat")
        if not os.path.exists(level_dat):
            self._last_error = f"Nie znaleziono level.dat w {map_path}"
            return False
        
        # W 1.7.10 z Forge, ID bloków w NBT chunków są STRINGAMI
        # (np. "appliedenergistics2:tile.BlockController")
        # Nie ma potrzeby parsowania level.dat dla mapowania ID.
        
        # JEŚLI ktoś używa BARDZO starej wersji (pre-Forge), wtedy
        # ID są numeryczne i wymagają mapowania. To nie jest wspierane.
        
        self._mode = "string_id_only"
        return True
    
    def resolve_block_id(self, numeric_id: int, metadata: int = 0) -> BlockIDInfo:
        """
        Rozwiązuje numeryczne ID na nazwę bloku.
        
        W 1.7.10 z Forge, bloki z modów mają stringowe ID w NBT:
        "appliedenergistics2:tile.BlockController"
        
        Ta metoda jest używana gdy mamy stare numeryczne ID.
        """
        # Sprawdź cache
        if numeric_id in self.reverse_id_map:
            name = self.reverse_id_map[numeric_id]
            return BlockIDInfo(
                block_id=name,
                metadata=metadata,
                source="cache"
            )
        
        # Domyślne: zakładamy że to już string ID
        # (W 1.7.10 z Forge, ID w NBT to stringi)
        return BlockIDInfo(
            block_id=str(numeric_id),
            metadata=metadata,
            source="direct"
        )
    
    def get_ae2_block_id(self, block_name: str, world_type: str = "main") -> str:
        """
        Zwraca pełne ID bloku AE2 dla danej nazwy.
        
        Args:
            block_name: Nazwa bloku (np. "BlockController", "controller")
            world_type: "main" lub nazwa mapy testowej
            
        Returns:
            Pełne ID bloku (np. "appliedenergistics2:tile.BlockController")
        """
        # Normalizuj nazwę
        name = block_name.lower().replace("block", "")
        
        # Mapa znanych nazw
        name_map = {
            'controller': 'appliedenergistics2:tile.BlockController',
            'drive': 'appliedenergistics2:tile.BlockDrive',
            'chest': 'appliedenergistics2:tile.BlockChest',
            'interface': 'appliedenergistics2:tile.BlockInterface',
            'ioport': 'appliedenergistics2:tile.BlockIOPort',
            'craftingunit': 'appliedenergistics2:tile.BlockCraftingUnit',
            'craftingstorage': 'appliedenergistics2:tile.BlockCraftingStorage',
            'craftingmonitor': 'appliedenergistics2:tile.BlockCraftingMonitor',
            'molecularassembler': 'appliedenergistics2:tile.BlockMolecularAssembler',
            'energyacceptor': 'appliedenergistics2:tile.BlockEnergyAcceptor',
            'energycell': 'appliedenergistics2:tile.BlockEnergyCell',
            'denseenergycell': 'appliedenergistics2:tile.BlockDenseEnergyCell',
            'quantumring': 'appliedenergistics2:tile.BlockQuantumRing',
            'quantumlinkchamber': 'appliedenergistics2:tile.BlockQuantumLinkChamber',
            'spatialioport': 'appliedenergistics2:tile.BlockSpatialIOPort',
            'spatialpylon': 'appliedenergistics2:tile.BlockSpatialPylon',
            'charger': 'appliedenergistics2:tile.BlockCharger',
            'inscriber': 'appliedenergistics2:tile.BlockInscriber',
            'vibrationchamber': 'appliedenergistics2:tile.BlockVibrationChamber',
            'quartzgrowthaccelerator': 'appliedenergistics2:tile.BlockQuartzGrowthAccelerator',
            'condenser': 'appliedenergistics2:tile.BlockCondenser',
            'grinder': 'appliedenergistics2:tile.BlockGrinder',
            'crank': 'appliedenergistics2:tile.BlockCrank',
            'skychest': 'appliedenergistics2:tile.BlockSkyChest',
            'wireless': 'appliedenergistics2:tile.BlockWireless',
            'security': 'appliedenergistics2:tile.BlockSecurity',
            'cablebus': 'appliedenergistics2:tile.BlockCableBus',
        }
        
        return name_map.get(name, f"appliedenergistics2:tile.{block_name}")
    
    def is_ae2_block(self, block_id: str) -> bool:
        """Sprawdza czy ID należy do AE2"""
        ae2_prefixes = [
            'appliedenergistics2:',
            'ae2:',
        ]
        return any(block_id.startswith(prefix) for prefix in ae2_prefixes)
    
    def get_block_metadata(self, block_id: str) -> Tuple[str, int]:
        """
        Ekstrahuje ID i metadata z stringa.
        
        Formaty:
        - "block_id" -> ("block_id", 0)
        - "block_id:1" -> ("block_id", 1)
        """
        if ':' in block_id:
            parts = block_id.rsplit(':', 1)
            try:
                metadata = int(parts[1])
                return (parts[0], metadata)
            except ValueError:
                pass
        
        return (block_id, 0)
    
    def register_test_world(self, world_name: str, id_map: Dict[str, int]):
        """
        Rejestruje mapowanie ID dla mapy testowej.
        
        Args:
            world_name: Nazwa świata testowego
            id_map: Mapa nazwa -> ID
        """
        self.test_world_cache[world_name] = id_map.copy()
    
    def load_test_world_ids(self, templates_path: str) -> Dict[str, int]:
        """
        Ładuje ID z folderu szablonów map testowych.
        
        Returns:
            Mapa nazwa bloku -> numeryczne ID
        """
        result = {}
        
        # Szukaj plików z konfiguracją ID
        id_config = os.path.join(templates_path, "ae2_block_ids.json")
        if os.path.exists(id_config):
            with open(id_config, 'r') as f:
                result = json.load(f)
        
        return result


class DynamicIDRegistry:
    """
    Rejestr mapowań ID dla konwersji.
    
    W 1.7.10 z Forge ID są stringami - nie ma "dynamicznych" ID numerycznych.
    Ta klasa służy do śledzenia mapowań nazw bloków między wersjami.
    """
    
    def __init__(self):
        # Mapa: oryginalne ID (1.7.10) -> nowe ID (1.18.2)
        self.id_mapping: Dict[str, str] = {}
        # Ostrzeżenia o nieznanych ID
        self.warnings: List[str] = []
        
    def register_mapping(self, old_id: str, new_id: str):
        """Rejestruje mapowanie ID"""
        self.id_mapping[old_id] = new_id
        
    def get_new_id(self, old_id: str) -> Optional[str]:
        """Zwraca nowe ID dla starego ID"""
        return self.id_mapping.get(old_id)
    
    def generate_id(self, prefix: str = "ae2") -> str:
        """Generuje nowe unikalne ID"""
        new_id = f"{prefix}:generated_{self._next_id}"
        self._next_id += 1
        return new_id
    
    def save_to_file(self, filepath: str):
        """Zapisuje rejestr do pliku JSON"""
        with open(filepath, 'w') as f:
            json.dump(self.id_mapping, f, indent=2)
    
    def load_from_file(self, filepath: str):
        """Ładuje rejestr z pliku JSON"""
        if os.path.exists(filepath):
            with open(filepath, 'r') as f:
                self.id_mapping = json.load(f)
