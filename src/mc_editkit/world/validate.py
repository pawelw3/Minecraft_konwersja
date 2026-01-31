"""
Walidatory spójności świata po edycji
"""
import logging
from pathlib import Path
from typing import List, Tuple, Optional

try:
    from pyanvileditor import AnvilEditor
except ImportError:
    AnvilEditor = None

logger = logging.getLogger(__name__)


class WorldValidator:
    """
    Walidator świata po edycji.
    Sprawdza czy regiony i chunki są poprawne.
    """
    
    def __init__(self, world_path: str):
        self.world_path = Path(world_path)
        self.region_path = self.world_path / "region"
        self.errors: List[str] = []
        self.warnings: List[str] = []
    
    def validate_all(self) -> bool:
        """
        Uruchamia wszystkie walidacje.
        
        Returns:
            True jeśli wszystko OK, False jeśli są błędy
        """
        self.errors = []
        self.warnings = []
        
        self._validate_regions_exist()
        self._validate_region_files()
        self._validate_chunks()
        
        if self.errors:
            logger.error(f"Walidacja nieudana: {len(self.errors)} błędów")
            for err in self.errors:
                logger.error(f"  - {err}")
        
        if self.warnings:
            logger.warning(f"Ostrzeżenia: {len(self.warnings)}")
            for warn in self.warnings:
                logger.warning(f"  - {warn}")
        
        return len(self.errors) == 0
    
    def _validate_regions_exist(self):
        """Sprawdza czy istnieje katalog region"""
        if not self.region_path.exists():
            self.errors.append(f"Nie istnieje katalog region: {self.region_path}")
    
    def _validate_region_files(self):
        """Sprawdza czy pliki regionów są poprawne"""
        if not self.region_path.exists():
            return
        
        for region_file in self.region_path.glob("r.*.mca"):
            try:
                if AnvilEditor:
                    # Spróbuj otworzyć
                    editor = AnvilEditor(str(region_file))
                    editor.close()
            except Exception as e:
                self.errors.append(f"Nie można otworzyć {region_file}: {e}")
    
    def _validate_chunks(self):
        """Sprawdza czy chunki mają poprawne NBT"""
        if not self.region_path.exists() or not AnvilEditor:
            return
        
        for region_file in self.region_path.glob("r.*.mca"):
            try:
                editor = AnvilEditor(str(region_file))
                
                # Sprawdź każdy chunk w regionie
                for chunk_x in range(32):
                    for chunk_z in range(32):
                        try:
                            chunk = editor.get_chunk(chunk_x, chunk_z)
                            if chunk is None:
                                continue
                            
                            # Sprawdź czy chunk ma poprawne dane
                            sections = chunk.get_section(0)
                            # Jeśli nie ma błędów przy odczycie, chunk jest OK
                            
                        except Exception as e:
                            self.warnings.append(
                                f"Błąd chunka ({chunk_x}, {chunk_z}) w {region_file.name}: {e}"
                            )
                
                editor.close()
                
            except Exception as e:
                self.errors.append(f"Błąd walidacji {region_file}: {e}")
    
    def validate_tile_entities(self, region_pos: Tuple[int, int]) -> List[str]:
        """
        Sprawdza TileEntities w danym regionie.
        
        Returns:
            Lista błędów
        """
        errors = []
        
        if not AnvilEditor:
            return errors
        
        region_file = self.region_path / f"r.{region_pos[0]}.{region_pos[1]}.mca"
        if not region_file.exists():
            return errors
        
        try:
            editor = AnvilEditor(str(region_file))
            
            for chunk_x in range(32):
                for chunk_z in range(32):
                    chunk = editor.get_chunk(chunk_x, chunk_z)
                    if chunk is None:
                        continue
                    
                    try:
                        tes = chunk.get_tile_entities()
                        for te in tes:
                            # Sprawdź czy TE ma wymagane pola
                            if 'id' not in te:
                                errors.append(
                                    f"TE w chunku ({chunk_x}, {chunk_z}) nie ma pola 'id'"
                                )
                            
                            # Sprawdź współrzędne
                            for coord in ['x', 'y', 'z']:
                                if coord not in te:
                                    errors.append(
                                        f"TE {te.get('id', '?')} nie ma współrzędnej '{coord}'"
                                    )
                    except Exception as e:
                        errors.append(f"Błąd odczytu TE w chunku ({chunk_x}, {chunk_z}): {e}")
            
            editor.close()
            
        except Exception as e:
            errors.append(f"Błąd walidacji regionu {region_pos}: {e}")
        
        return errors


def validate_world(world_path: str) -> bool:
    """
    Funkcja pomocnicza do walidacji świata.
    
    Returns:
        True jeśli świat jest poprawny
    """
    validator = WorldValidator(world_path)
    return validator.validate_all()
