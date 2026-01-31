"""
Obsługa struktur (schematów budynków/circuitów)
"""
import json
import logging
from typing import Dict, List, Tuple, Optional, Any
from pathlib import Path

from .palette import BlockPalette, BlockEntry
from ..world.types import Pos

logger = logging.getLogger(__name__)


class Structure:
    """
    Reprezentacja struktury (schematu) do wstawienia do świata.
    
    Podobna do formatu schematic, ale uproszczona i zoptymalizowana
    dla naszych potrzeb.
    """
    
    def __init__(self, size: Tuple[int, int, int] = (0, 0, 0)):
        """
        Tworzy nową strukturę.
        
        Args:
            size: Rozmiar (width, height, depth)
        """
        self.size = size
        self.palette = BlockPalette()
        
        # Mapa pozycji -> indeks w palecie
        # Klucz: (x, y, z) względem origin
        self.blocks: Dict[Tuple[int, int, int], int] = {}
        
        # Origin (punkt odniesienia)
        self.origin = (0, 0, 0)
    
    def set_block(self, x: int, y: int, z: int, 
                  block_id: int, meta: int = 0,
                  tile_entity: Optional[Dict[str, Any]] = None):
        """
        Ustawia blok w strukturze.
        """
        idx = self.palette.add(block_id, meta, tile_entity)
        self.blocks[(x, y, z)] = idx
        
        # Aktualizuj rozmiar jeśli potrzeba
        self.size = (
            max(self.size[0], x + 1),
            max(self.size[1], y + 1),
            max(self.size[2], z + 1)
        )
    
    def get_block(self, x: int, y: int, z: int) -> BlockEntry:
        """Zwraca blok na danej pozycji (lub air)"""
        idx = self.blocks.get((x, y, z), 0)
        return self.palette.get(idx)
    
    def get_blocks(self) -> List[Tuple[int, int, int, BlockEntry]]:
        """
        Zwraca listę wszystkich bloków jako (x, y, z, BlockEntry).
        """
        result = []
        for (x, y, z), idx in self.blocks.items():
            entry = self.palette.get(idx)
            if entry.block_id != 0:  # Pomiń air
                result.append((x, y, z, entry))
        return result
    
    def paste(self, editor, origin: Pos, 
              overwrite: bool = True,
              include_tile_entities: bool = True):
        """
        Wstawia strukturę do świata.
        
        Args:
            editor: WorldEditor
            origin: Pozycja w świecie (lewy-dolny-tylny róg)
            overwrite: Czy nadpisywać istniejące bloki
            include_tile_entities: Czy wstawiać TE
        """
        logger.info(f"Wstawianie struktury {self.size} na pozycję {origin}")
        
        count = 0
        for (x, y, z), idx in self.blocks.items():
            entry = self.palette.get(idx)
            
            if entry.block_id == 0:  # Pomiń air
                continue
            
            world_pos = Pos(origin.x + x, origin.y + y, origin.z + z)
            
            # Sprawdź czy nadpisywać
            if not overwrite:
                existing = editor.get_block(world_pos)
                if existing[0] != 0:  # Nie air
                    continue
            
            # Ustaw blok
            editor.set_block(world_pos, entry.block_id, entry.meta)
            
            # Ustaw TE jeśli jest
            if include_tile_entities and entry.tile_entity:
                editor.set_tile_entity(world_pos, entry.tile_entity)
            
            count += 1
        
        logger.info(f"Wstawiono {count} bloków")
    
    @classmethod
    def from_voxel_grid(cls, path: str) -> 'Structure':
        """
        Wczytuje strukturę z pliku voxel_grid.json (format z test_scenarios).
        """
        path = Path(path)
        with open(path, 'r') as f:
            data = json.load(f)
        
        structure = cls()
        
        # Wczytaj voxele
        for section_name, section_data in data.get("sections", {}).items():
            for voxel in section_data.get("voxels", []):
                x = voxel.get("x", 0)
                y = voxel.get("y", 0)
                z = voxel.get("z", 0)
                block_name = voxel.get("block", "minecraft:air")
                
                # Parsuj nazwę bloku
                if block_name.startswith("minecraft:"):
                    block_id = cls._block_name_to_id(block_name)
                    meta = 0
                    
                    # Obsługa properties (dla uproszczenia - tylko niektóre)
                    props = voxel.get("properties", {})
                    if "facing" in props:
                        meta = cls._facing_to_meta(props["facing"])
                else:
                    # Dla innych bloków - spróbuj zmapować lub użyj stone
                    logger.warning(f"Nieznany blok: {block_name}, używam stone")
                    block_id = 1
                    meta = 0
                
                structure.set_block(x, y, z, block_id, meta)
        
        logger.info(f"Wczytano strukturę z {path}: {len(structure.blocks)} bloków")
        return structure
    
    @staticmethod
    def _block_name_to_id(name: str) -> int:
        """Mapuje nazwę bloku na ID (uproszczone)"""
        mapping = {
            "minecraft:air": 0,
            "minecraft:stone": 1,
            "minecraft:grass": 2,
            "minecraft:dirt": 3,
            "minecraft:cobblestone": 4,
            "minecraft:planks": 5,
            "minecraft:redstone_wire": 55,
            "minecraft:repeater": 93,
            "minecraft:unpowered_repeater": 93,
            "minecraft:redstone_torch": 76,
            "minecraft:dropper": 158,
            "minecraft:comparator": 149,
            "minecraft:command_block": 137,
            "minecraft:chest": 54,
            "minecraft:hopper": 154,
        }
        return mapping.get(name, 1)  # Domyślnie stone
    
    @staticmethod
    def _facing_to_meta(facing: str) -> int:
        """Mapuje facing na metadata"""
        facing_map = {
            "north": 0,
            "east": 1,
            "south": 2,
            "west": 3,
            "up": 0,
            "down": 0,
        }
        return facing_map.get(facing, 0)
    
    def save(self, path: str):
        """Zapisuje strukturę do pliku JSON"""
        data = {
            "size": self.size,
            "palette": {
                str(idx): {
                    "id": entry.block_id,
                    "meta": entry.meta,
                    "te": entry.tile_entity
                }
                for idx, entry in self.palette._entries.items()
            },
            "blocks": {
                f"{x},{y},{z}": idx
                for (x, y, z), idx in self.blocks.items()
            }
        }
        
        with open(path, 'w') as f:
            json.dump(data, f, indent=2)
        
        logger.info(f"Zapisano strukturę do {path}")
    
    @classmethod
    def load(cls, path: str) -> 'Structure':
        """Wczytuje strukturę z pliku JSON"""
        with open(path, 'r') as f:
            data = json.load(f)
        
        structure = cls()
        structure.size = tuple(data.get("size", (0, 0, 0)))
        
        # Wczytaj paletę
        for idx_str, entry_data in data.get("palette", {}).items():
            idx = int(idx_str)
            structure.palette._entries[idx] = BlockEntry(
                block_id=entry_data["id"],
                meta=entry_data.get("meta", 0),
                tile_entity=entry_data.get("te")
            )
            structure.palette._next_index = max(structure.palette._next_index, idx + 1)
        
        # Wczytaj bloki
        for pos_str, idx in data.get("blocks", {}).items():
            x, y, z = map(int, pos_str.split(","))
            structure.blocks[(x, y, z)] = idx
        
        return structure
