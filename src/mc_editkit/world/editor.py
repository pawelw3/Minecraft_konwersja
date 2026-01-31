"""
WorldEditor - główne API do edycji światów Minecraft
"""
import logging
import shutil
import tempfile
from pathlib import Path
from typing import Optional, Dict, Any, List, Tuple
from contextlib import contextmanager

from .types import Pos, EditOperation
from .backends.anvil_backend import AnvilBackend
from ..blocks.registry import BlockRegistry, get_registry

logger = logging.getLogger(__name__)


class WorldEditor:
    """
    Główne API do edycji światów Minecraft OFFLINE.
    
    Umożliwia:
    - atomowe operacje set_block, set_tile_entity
    - hurtowe operacje paste, apply
    - transakcje commit/rollback
    """
    
    def __init__(self, world_path: str, 
                 backup: bool = True,
                 registry: Optional[BlockRegistry] = None):
        """
        Inicjalizuje edytor świata.
        
        Args:
            world_path: Ścieżka do katalogu świata
            backup: Czy tworzyć backup przed edycją
            registry: Rejestr bloków (domyślnie globalny)
        """
        self.world_path = Path(world_path)
        self.backup = backup
        self.registry = registry or get_registry()
        
        # Backend (nbtlib)
        self._backend = AnvilBackend(str(world_path), backup=backup)
        
        # Historia operacji (dla undo)
        self._operations: List[EditOperation] = []
    
    def set_block(self, pos: Pos, block_id: int, meta: int = 0):
        """
        Ustawia blok na danej pozycji.
        
        Args:
            pos: Pozycja w świecie
            block_id: ID bloku (numeryczne)
            meta: Metadata (0-15)
        """
        self._backend.set_block(pos, block_id, meta)
        self._operations.append(EditOperation(pos, block_id, meta))
        logger.info(f"set_block({pos}): {block_id}:{meta}")
    
    def set_block_by_name(self, pos: Pos, name: str):
        """
        Ustawia blok po nazwie (z rejestru).
        
        Args:
            pos: Pozycja w świecie
            name: Nazwa bloku (np. "minecraft:stone")
        """
        block_id, meta = self.registry.get(name)
        self.set_block(pos, block_id, meta)
    
    def get_block(self, pos: Pos) -> Tuple[int, int]:
        """
        Zwraca (block_id, meta) dla danej pozycji.
        """
        return self._backend.get_block(pos)
    
    def set_tile_entity(self, pos: Pos, te_data: Dict[str, Any]):
        """
        Ustawia TileEntity na danej pozycji.
        
        Args:
            pos: Pozycja w świecie
            te_data: Słownik z danymi TE (musi zawierać 'id')
        """
        # Walidacja
        if 'id' not in te_data:
            raise ValueError("TileEntity musi zawierać pole 'id'")
        
        self._backend.set_tile_entity(pos, te_data)
        logger.info(f"set_tile_entity({pos}): {te_data['id']}")
    
    def get_tile_entity(self, pos: Pos) -> Optional[Dict[str, Any]]:
        """
        Zwraca TileEntity dla danej pozycji lub None.
        """
        return self._backend.get_tile_entity(pos)
    
    def clear_tile_entity(self, pos: Pos):
        """Usuwa TileEntity z danej pozycji"""
        self._backend.clear_tile_entity(pos)
        logger.info(f"clear_tile_entity({pos})")
    
    def set_command_block(self, pos: Pos, command: str, 
                          custom_name: str = "@",
                          track_output: bool = True):
        """
        Ustawia command block z daną komendą.
        
        Args:
            pos: Pozycja w świecie
            command: Komenda do wykonania
            custom_name: Nazwa wyświetlana (domyślnie "@")
            track_output: Czy śledzić output (domyślnie True)
        """
        # Ustaw blok command blocka
        self.set_block_by_name(pos, "minecraft:command_block")
        
        # Ustaw TE z poprawnym ID dla 1.7.10
        # Uwaga: W 1.7.x command block ma TE id="Control" (nie "command_block")
        te = {
            'id': 'Control',
            'Command': command,
            'CustomName': custom_name,
            'TrackOutput': 1 if track_output else 0
        }
        self.set_tile_entity(pos, te)
        
        logger.info(f"set_command_block({pos}): {command[:50]}...")
    
    def commit(self):
        """
        Zapisuje wszystkie zmiany do plików.
        """
        self._backend.commit()
        logger.info("Commit zakończony")
    
    def rollback(self):
        """
        Cofa zmiany (przywraca backup).
        """
        self._backend.rollback()
        logger.info("Rollback zakończony")
    
    def close(self):
        """Zamyka edytor bez zapisywania"""
        self._backend.close()
        logger.info("Edytor zamknięty")
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is None:
            self.commit()
        else:
            logger.error(f"Błąd podczas edycji: {exc_val}")
            self.rollback()
        self.close()


@contextmanager
def edit_world(world_path: str, backup: bool = True):
    """
    Context manager do edycji świata.
    
    Przykład:
        with edit_world("path/to/world") as editor:
            editor.set_block_by_name(Pos(0, 64, 0), "minecraft:stone")
            editor.set_command_block(Pos(1, 64, 0), "/say Hello!")
    """
    editor = WorldEditor(world_path, backup=backup)
    try:
        yield editor
        editor.commit()
    except Exception as e:
        logger.error(f"Błąd podczas edycji: {e}")
        editor.rollback()
        raise
    finally:
        editor.close()


class WorldCopier:
    """
    Pomocnicza klasa do tworzenia kopii świata dla testów.
    """
    
    @staticmethod
    def create_copy(source_path: str, dest_path: Optional[str] = None) -> str:
        """
        Tworzy kopię świata.
        
        Args:
            source_path: Ścieżka do oryginalnego świata
            dest_path: Ścieżka docelowa (domyślnie temp)
            
        Returns:
            Ścieżka do kopii świata
        """
        source = Path(source_path)
        
        if dest_path is None:
            dest = Path(tempfile.mkdtemp(prefix="mc_world_copy_"))
        else:
            dest = Path(dest_path)
        
        # Kopiuj tylko regiony (dla testów redstone nie potrzebujemy playerdata itp.)
        dest.mkdir(parents=True, exist_ok=True)
        
        # Kopiuj regiony
        region_src = source / "region"
        region_dst = dest / "region"
        if region_src.exists():
            shutil.copytree(region_src, region_dst, dirs_exist_ok=True)
        
        # Kopiuj level.dat (wymagany przez serwer)
        level_src = source / "level.dat"
        if level_src.exists():
            shutil.copy2(level_src, dest / "level.dat")
        
        logger.info(f"Utworzono kopię świata: {source} -> {dest}")
        return str(dest)
