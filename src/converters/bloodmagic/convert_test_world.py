"""
Konwersja testowej mapy Blood Magic z 1.7.10 na 1.18.2.

Ten skrypt:
1. Odczytuje mapę 1.7.10 z folderu lightweigh_map_templates/1710_modded/bloodmagic_test
2. Znajduje bloki Blood Magic (po Tile Entity ID)
3. Konwertuje je używając BloodMagicConverter
4. Zapisuje wynikową mapę w formacie 1.18.2
"""

import json
import sys
from pathlib import Path
from typing import Dict, Any, List, Tuple, Optional

# Dodaj src do path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from minecraft_map_parser.nbt_parser import NBTParser
from minecraft_map_parser.anvil_parser import AnvilParser
from converters.bloodmagic.converter import BloodMagicConverter
from converters.bloodmagic.block_mappings import TE_ID_MAPPING


class BloodMagicWorldConverter:
    """
    Konwerter mapy Minecraft z Blood Magic z 1.7.10 na 1.18.2.
    """
    
    def __init__(self, name_to_uuid_mapping: Optional[Dict[str, str]] = None):
        """
        Inicjalizacja konwertera.
        
        Args:
            name_to_uuid_mapping: Opcjonalne mapowanie nazw graczy na UUID
        """
        self.converter = BloodMagicConverter(name_to_uuid_mapping)
        self.stats = {
            "chunks_processed": 0,
            "blocks_converted": 0,
            "tile_entities_converted": 0,
            "warnings": [],
            "errors": []
        }
    
    def convert_region_file(
        self, 
        input_path: Path, 
        output_path: Path,
        block_id_mapping: Dict[int, str]  # num ID -> string ID (np. 1000 -> "AWWayofTime:Altar")
    ) -> bool:
        """
        Konwertuj pojedynczy plik regionu (.mca).
        
        Args:
            input_path: Ścieżka do pliku .mca 1.7.10
            output_path: Ścieżka do pliku .mca 1.18.2
            block_id_mapping: Mapowanie numerycznych ID na string ID modów
            
        Returns:
            True jeśli konwersja się powiodła
        """
        try:
            # Odczytaj chunki z pliku 1.7.10 używając AnvilParser
            parser = AnvilParser(str(input_path))
            chunks_data = []
            
            # Pobierz wszystkie chunki
            chunk_objects = parser.get_all_chunks()
            
            for chunk in chunk_objects:
                try:
                    if chunk and chunk.nbt:
                        # Konwertuj NBT na słownik używając _nbt_to_python
                        chunk_nbt = chunk._nbt_to_python(chunk.nbt)
                        chunks_data.append((chunk.x, chunk.z, chunk_nbt))
                except Exception as e:
                    pass  # Ignoruj uszkodzone chunki
            
            print(f"  Odczytano {len(chunks_data)} chunków z {input_path.name}")
            
            # Przetwórz każdy chunk
            converted_chunks = []
            for cx, cz, chunk_nbt in chunks_data:
                converted = self._convert_chunk(chunk_nbt, block_id_mapping)
                if converted:
                    converted_chunks.append((cx, cz, converted))
            
            print(f"  Skonwertowano {len(converted_chunks)} chunków")
            
            # Zapisz skonwertowane chunki
            # TODO: Implementacja zapisu w formacie 1.18.2
            # Na razie zapisz jako JSON do analizy
            output_json = output_path.with_suffix('.json')
            self._save_converted_chunks(converted_chunks, output_json)
            
            return True
            
        except Exception as e:
            print(f"  Błąd konwersji {input_path.name}: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def _convert_chunk(
        self, 
        chunk_nbt: Dict[str, Any],
        block_id_mapping: Dict[int, str]
    ) -> Optional[Dict[str, Any]]:
        """
        Konwertuj pojedynczy chunk.
        
        Args:
            chunk_nbt: NBT chunka z 1.7.10
            block_id_mapping: Mapowanie ID bloków
            
        Returns:
            Skonwertowany chunk lub None
        """
        try:
            level = chunk_nbt.get("Level", {})
            
            # Pobierz Tile Entities
            tile_entities = level.get("TileEntities", [])
            converted_tes = []
            
            for te in tile_entities:
                te_id = te.get("id", "")
                
                # Sprawdź czy to Blood Magic TE
                if te_id in ["containerAltar", "containerMasterStone", "TileSoulJar", "Altar", "MasterStone", "SoulForge"]:
                    converted_te = self._convert_tile_entity(te)
                    if converted_te:
                        converted_tes.append(converted_te)
                        self.stats["tile_entities_converted"] += 1
            
            # Pobierz sekcje (bloki)
            sections = level.get("Sections", [])
            converted_sections = []
            
            for section in sections:
                converted_section = self._convert_section(section, block_id_mapping)
                if converted_section:
                    converted_sections.append(converted_section)
            
            self.stats["chunks_processed"] += 1
            
            return {
                "original": chunk_nbt,
                "converted_tile_entities": converted_tes,
                "converted_sections": converted_sections
            }
            
        except Exception as e:
            print(f"    Błąd konwersji chunka: {e}")
            return None
    
    def _convert_tile_entity(self, te: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Konwertuj Tile Entity Blood Magic."""
        te_id = te.get("id", "")
        
        # Użyj konwertera BloodMagic
        try:
            # Mapowanie pozycji
            x, y, z = te.get("x", 0), te.get("y", 0), te.get("z", 0)
            
            # Konwertuj używając głównego konwertera
            # Symuluj blok (używamy placeholder ID)
            block_id = "AWWayofTime:Altar" if "Altar" in te_id else \
                      "AWWayofTime:masterStone" if "MasterStone" in te_id else \
                      "AWWayofTime:soulForge" if "SoulForge" in te_id else \
                      "AWWayofTime:unknown"
            
            result = self.converter.convert_block(
                block_id_1710=block_id,
                metadata=0,
                te_nbt_1710=te,
                pos=(x, y, z)
            )
            
            if result.is_success():
                return {
                    "original_id": te_id,
                    "new_id": result.block_id_1182,
                    "new_be_nbt": result.be_nbt_1182,
                    "warnings": result.warnings
                }
            else:
                self.stats["errors"].extend(result.errors)
                return None
                
        except Exception as e:
            print(f"      Błąd konwersji TE {te_id}: {e}")
            return None
    
    def _convert_section(
        self, 
        section: Dict[str, Any],
        block_id_mapping: Dict[int, str]
    ) -> Optional[Dict[str, Any]]:
        """Konwertuj sekcję (Y-level) chunka."""
        # W 1.7.10 sekcje mają Blocks (byte array) i Data (nibble array)
        # W 1.18.2 używamy palette i block states
        
        y = section.get("Y", 0)
        blocks = section.get("Blocks", [])
        data = section.get("Data", [])
        
        # Dla uproszczenia - zwróć oryginalną sekcję z informacją o konwersji
        return {
            "y": y,
            "original_blocks_count": len(blocks),
            "note": "Konwersja sekcji wymaga mapowania ID bloków"
        }
    
    def _save_converted_chunks(self, chunks: List[Tuple], output_path: Path):
        """Zapisz skonwertowane chunki do JSON."""
        data = {
            "metadata": {
                "source_version": "1.7.10",
                "target_version": "1.18.2",
                "converter": "BloodMagicWorldConverter",
                "chunks_count": len(chunks)
            },
            "chunks": []
        }
        
        for cx, cz, chunk_data in chunks:
            chunk_summary = {
                "chunk_x": cx,
                "chunk_z": cz,
                "tile_entities": chunk_data.get("converted_tile_entities", []),
                "sections": chunk_data.get("converted_sections", [])
            }
            data["chunks"].append(chunk_summary)
        
        with open(output_path, 'w') as f:
            json.dump(data, f, indent=2, default=str)
        
        print(f"  Zapisano wynik: {output_path}")
    
    def print_stats(self):
        """Wypisz statystyki konwersji."""
        print("\n=== Statystyki konwersji ===")
        print(f"Przetworzone chunki: {self.stats['chunks_processed']}")
        print(f"Skonwertowane Tile Entities: {self.stats['tile_entities_converted']}")
        print(f"Ostrzeżenia: {len(self.stats['warnings'])}")
        print(f"Błędy: {len(self.stats['errors'])}")
        
        if self.stats['warnings']:
            print("\nOstrzeżenia:")
            for w in set(self.stats['warnings'][:10]):  # Pokaż max 10
                print(f"  - {w}")
        
        if self.stats['errors']:
            print("\nBłędy:")
            for e in set(self.stats['errors'][:10]):
                print(f"  - {e}")


def main():
    """Główna funkcja konwersji mapy testowej."""
    # Ścieżki
    input_world = Path("lightweigh_map_templates/1710_modded/bloodmagic_test")
    output_world = Path("lightweigh_map_templates/1710_modded/bloodmagic_test_converted")
    
    output_world.mkdir(parents=True, exist_ok=True)
    (output_world / "region").mkdir(exist_ok=True)
    
    # Mapowanie numerycznych ID na string ID
    # Te ID były użyte w patchu
    block_id_mapping = {
        1000: "AWWayofTime:Altar",
        1001: "AWWayofTime:masterStone",
        1010: "AWWayofTime:speedRune",
        1011: "AWWayofTime:efficiencyRune",
        1012: "AWWayofTime:runeOfSacrifice",
        1013: "AWWayofTime:runeOfSelfSacrifice",
        1014: "AWWayofTime:bloodRune",
        1020: "AWWayofTime:largeBloodStoneBrick",
        1021: "AWWayofTime:bloodStoneBrick",
        1022: "AWWayofTime:ritualStone",
        1023: "AWWayofTime:imperfectRitualStone",
        1030: "AWWayofTime:soulForge",
    }
    
    print("=== Konwersja mapy Blood Magic 1.7.10 -> 1.18.2 ===")
    print(f"Źródło: {input_world}")
    print(f"Cel: {output_world}")
    print()
    
    # Znajdź wszystkie pliki regionów
    region_files = list((input_world / "region").glob("*.mca"))
    print(f"Znaleziono {len(region_files)} plików regionów")
    print()
    
    # Konwertuj każdy region
    world_converter = BloodMagicWorldConverter()
    
    for region_file in region_files:
        print(f"Konwersja: {region_file.name}")
        output_file = output_world / "region" / region_file.name
        
        success = world_converter.convert_region_file(
            region_file, 
            output_file,
            block_id_mapping
        )
        
        if success:
            print(f"  [OK] Sukces")
        else:
            print(f"  [FAIL] Blad")
        print()
    
    # Wypisz statystyki
    world_converter.print_stats()
    
    print(f"\nKonwersja zakończona. Wyniki w: {output_world}")


if __name__ == "__main__":
    main()
