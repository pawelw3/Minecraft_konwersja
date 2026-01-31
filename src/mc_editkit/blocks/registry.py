"""
Rejestr bloków: vanilla + mody (Minecraft 1.7.10)
Mapowanie nazw logicznych na (id, meta)
"""
from typing import Dict, Tuple, Optional
import json
import os


class BlockRegistry:
    """
    Rejestr bloków dla Minecraft 1.7.10.
    Mapuje nazwy logiczne "namespace:name" na (block_id, metadata)
    """
    
    # Bloki vanilla (najważniejsze dla testów)
    VANILLA_BLOCKS: Dict[str, Tuple[int, int]] = {
        # Podstawowe
        "minecraft:air": (0, 0),
        "minecraft:stone": (1, 0),
        "minecraft:grass": (2, 0),
        "minecraft:dirt": (3, 0),
        "minecraft:cobblestone": (4, 0),
        "minecraft:planks": (5, 0),
        
        # Redstone
        "minecraft:redstone_wire": (55, 0),
        "minecraft:unpowered_repeater": (93, 0),
        "minecraft:powered_repeater": (94, 0),
        "minecraft:redstone_block": (152, 0),
        "minecraft:redstone_torch": (76, 0),
        "minecraft:unlit_redstone_torch": (75, 0),
        
        # Mechanizmy
        "minecraft:command_block": (137, 0),
        "minecraft:dropper": (158, 0),
        "minecraft:dispenser": (23, 0),
        "minecraft:hopper": (154, 0),
        "minecraft:comparator": (149, 0),
        "minecraft:unpowered_comparator": (149, 0),
        "minecraft:powered_comparator": (150, 0),
        "minecraft:piston": (33, 0),
        "minecraft:sticky_piston": (29, 0),
        
        # Storage
        "minecraft:chest": (54, 0),
        "minecraft:trapped_chest": (146, 0),
        "minecraft:furnace": (61, 0),
        "minecraft:lit_furnace": (62, 0),
        
        # Inne
        "minecraft:glass": (20, 0),
        "minecraft:bedrock": (7, 0),
        "minecraft:sand": (12, 0),
        "minecraft:gravel": (13, 0),
        "minecraft:gold_block": (41, 0),
        "minecraft:iron_block": (42, 0),
        "minecraft:obsidian": (49, 0),
        "minecraft:mob_spawner": (52, 0),
        "minecraft:torch": (50, 0),
        "minecraft:lever": (69, 0),
        "minecraft:stone_button": (77, 0),
        "minecraft:wooden_button": (143, 0),
        "minecraft:stone_pressure_plate": (70, 0),
        "minecraft:wooden_pressure_plate": (72, 0),
    }
    
    def __init__(self, mod_registry_path: Optional[str] = None):
        """
        Inicjalizuje rejestr bloków.
        
        Args:
            mod_registry_path: Ścieżka do JSON z mapowaniem bloków modowych
        """
        self._blocks = dict(self.VANILLA_BLOCKS)
        self._mod_blocks: Dict[str, Tuple[int, int]] = {}
        
        if mod_registry_path and os.path.exists(mod_registry_path):
            self._load_mod_registry(mod_registry_path)
    
    def _load_mod_registry(self, path: str):
        """Ładuje rejestr bloków modowych z pliku JSON"""
        with open(path, 'r') as f:
            data = json.load(f)
        
        for name, info in data.get("blocks", {}).items():
            if isinstance(info, list) and len(info) >= 2:
                self._mod_blocks[name] = (info[0], info[1])
                self._blocks[name] = (info[0], info[1])
    
    def get(self, name: str) -> Tuple[int, int]:
        """
        Zwraca (block_id, meta) dla danej nazwy bloku.
        
        Raises:
            KeyError: Jeśli blok nie istnieje w rejestrze
        """
        if name not in self._blocks:
            raise KeyError(f"Blok '{name}' nie istnieje w rejestrze. "
                          f"Użyj register() aby dodać lub sprawdź nazwę.")
        return self._blocks[name]
    
    def get_id(self, name: str) -> int:
        """Zwraca ID bloku"""
        return self.get(name)[0]
    
    def get_meta(self, name: str) -> int:
        """Zwraca metadata bloku"""
        return self.get(name)[1]
    
    def register(self, name: str, block_id: int, meta: int = 0):
        """
        Rejestruje nowy blok (np. modowy).
        
        Args:
            name: Nazwa logiczna bloku (np. "modid:blockname")
            block_id: ID numeryczne bloku
            meta: Metadata (0-15)
        """
        self._blocks[name] = (block_id, meta)
        if ":" in name and not name.startswith("minecraft:"):
            self._mod_blocks[name] = (block_id, meta)
    
    def lookup_by_id(self, block_id: int, meta: int = 0) -> Optional[str]:
        """Szuka nazwy bloku po ID i meta (reverse lookup)"""
        for name, (bid, bmeta) in self._blocks.items():
            if bid == block_id and bmeta == meta:
                return name
        return None
    
    def is_vanilla(self, name: str) -> bool:
        """Sprawdza czy blok jest vanilla"""
        return name.startswith("minecraft:") and name in self.VANILLA_BLOCKS
    
    def is_modded(self, name: str) -> bool:
        """Sprawdza czy blok jest modowy"""
        return name in self._mod_blocks
    
    def list_all(self) -> Dict[str, Tuple[int, int]]:
        """Zwraca wszystkie zarejestrowane bloki"""
        return dict(self._blocks)
    
    def list_modded(self) -> Dict[str, Tuple[int, int]]:
        """Zwraca tylko bloki modowe"""
        return dict(self._mod_blocks)
    
    def save_mod_registry(self, path: str):
        """Zapisuje rejestr bloków modowych do pliku JSON"""
        data = {
            "blocks": {name: [bid, meta] for name, (bid, meta) in self._mod_blocks.items()},
            "version": "1.7.10",
            "format": 1
        }
        with open(path, 'w') as f:
            json.dump(data, f, indent=2)


# Globalna instancja rejestru
DEFAULT_REGISTRY = BlockRegistry()


def get_registry() -> BlockRegistry:
    """Zwraca domyślny rejestr bloków"""
    return DEFAULT_REGISTRY
