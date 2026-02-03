"""
Generator testowej mapy Enchanting Plus dla wersji 1.7.10

Tworzy testową mapę ze wszystkimi blokami Enchanting Plus:
- enchanting_table (podstawowy stół)
- advanced_table (zaawansowany stół)
- arcane_inscriber (konwerter książek -> zwoje)

Z różnymi stanami Tile Entities (z inventory i bez).

Używa Kotlin/Hephaistos worker do modyfikacji region files.
"""

import subprocess
import json
import os
from pathlib import Path
from typing import Dict, Any, List


def get_project_root() -> Path:
    """Zwraca ścieżkę do root projektu."""
    current = Path(__file__).resolve()
    # Idź w górę aż znajdziesz folder z 'mapa_1710' lub 'src'
    for parent in current.parents:
        if (parent / 'mapa_1710').exists() or (parent / 'src').exists():
            return parent
    return current.parents[3]


class EnchantingPlusTestWorldGenerator:
    """Generator testowej mapy z blokami Enchanting Plus."""
    
    # Definicje bloków do wygenerowania
    BLOCKS_CONFIG = [
        # Rząd 1: Podstawowe stoły enchantujące
        {"type": "enchanting_table", "x": 2, "y": 64, "z": 2, "variant": "basic", "data": {}},
        {"type": "enchanting_table", "x": 4, "y": 64, "z": 2, "variant": "with_player", "data": {"lastPlayer": "TestPlayer"}},
        {"type": "enchanting_table", "x": 6, "y": 64, "z": 2, "variant": "with_inventory", "data": {
            "Items": [
                {"id": 403, "Count": 1, "Damage": 0, "Slot": 0},
                {"id": 267, "Count": 1, "Damage": 0, "Slot": 1}
            ]
        }},
        
        # Rząd 2: Zaawansowane stoły
        {"type": "advanced_table", "x": 2, "y": 64, "z": 5, "variant": "basic", "data": {}},
        {"type": "advanced_table", "x": 4, "y": 64, "z": 5, "variant": "with_repair_data", "data": {
            "repairCost": 15,
            "playerKnowledge": ["sharpness", "efficiency", "unbreaking"]
        }},
        {"type": "advanced_table", "x": 6, "y": 64, "z": 5, "variant": "full_inventory", "data": {
            "Items": [
                {"id": 276, "Count": 1, "Damage": 10, "Slot": 0,
                 "tag": {"ench": [{"id": 16, "lvl": 3}]}},
                {"id": 278, "Count": 1, "Damage": 0, "Slot": 1,
                 "tag": {"ench": [{"id": 32, "lvl": 4}, {"id": 34, "lvl": 3}]}}
            ]
        }},
        
        # Rząd 3: Arcane Inscriber (do usunięcia w konwersji)
        {"type": "arcane_inscriber", "x": 2, "y": 64, "z": 8, "variant": "empty", "data": {}},
        {"type": "arcane_inscriber", "x": 4, "y": 64, "z": 8, "variant": "with_scrolls", "data": {
            "storedScrolls": [
                {"enchantId": 16, "enchantLevel": 5, "scrollType": "weapon"},
                {"enchantId": 32, "enchantLevel": 4, "scrollType": "tool"}
            ],
            "Items": [{"id": 403, "Count": 5, "Damage": 0, "Slot": 0}]
        }},
        {"type": "arcane_inscriber", "x": 6, "y": 64, "z": 8, "variant": "complex_state", "data": {
            "currentRecipe": {"input": "book", "output": "scroll", "cost": 10},
            "progress": 50,
            "playerOwner": "TestPlayer123"
        }},
        
        # Rząd 4: Kombinacje bloków
        {"type": "enchanting_table", "x": 10, "y": 64, "z": 2, "variant": "combo_1", "data": {}},
        {"type": "advanced_table", "x": 11, "y": 64, "z": 2, "variant": "combo_2", "data": {}},
        {"type": "arcane_inscriber", "x": 12, "y": 64, "z": 2, "variant": "combo_3", "data": {}},
    ]
    
    def __init__(self, output_path: str = None):
        """Inicjalizuje generator."""
        self.project_root = get_project_root()
        if output_path is None:
            output_path = str(self.project_root / "lightweigh_map_templates" / "1710_modded" / "ep_test_world")
        self.output_path = Path(output_path)
        self.jvm_worker = self.project_root / "jvm" / "worker"
        
    def generate(self) -> Path:
        """Generuje testową mapę."""
        print("=" * 60)
        print("GENERATOR TESTOWEJ MAPY ENCHANTING PLUS")
        print("=" * 60)
        print(f"Ścieżka wyjściowa: {self.output_path}")
        
        # Utwórz strukturę folderów
        self._create_directory_structure()
        
        # Wygeneruj plik patch JSON
        patch_path = self._generate_patch_json()
        
        # Wywołaj Kotlin worker do wygenerowania mapy
        self._generate_with_kotlin(patch_path)
        
        # Wygeneruj metadane
        self._generate_metadata()
        
        print("\n" + "=" * 60)
        print("GENEROWANIE ZAKOŃCZONE")
        print("=" * 60)
        print(f"Mapa testowa: {self.output_path}")
        
        return self.output_path
    
    def _create_directory_structure(self):
        """Tworzy strukturę folderów dla mapy."""
        print("\n--- Tworzenie struktury folderów ---")
        
        # Usuń starą mapę jeśli istnieje
        if self.output_path.exists():
            import shutil
            shutil.rmtree(self.output_path)
            print(f"Usunięto starą mapę: {self.output_path}")
        
        # Utwórz foldery
        (self.output_path / "region").mkdir(parents=True)
        print(f"Utworzono: {self.output_path}/region")
    
    def _generate_patch_json(self) -> Path:
        """Generuje plik patch JSON dla Kotlin worker."""
        print("\n--- Generowanie patch JSON ---")
        
        edits = []
        
        # Dodaj platformę (kamień)
        for x in range(20):
            for z in range(20):
                edits.append({
                    "op": "set_block",
                    "x": x,
                    "y": 63,
                    "z": z,
                    "id": 1,  # Stone
                    "meta": 0
                })
        
        # Dodaj bloki Enchanting Plus
        for block in self.BLOCKS_CONFIG:
            # Ustaw blok (stone jako placeholder - mod zamieni na właściwy)
            edits.append({
                "op": "set_block",
                "x": block["x"],
                "y": block["y"],
                "z": block["z"],
                "id": 1,  # Stone - placeholder
                "meta": 0
            })
            
            # Ustaw Tile Entity
            te_nbt = {
                "id": f"EnchantingPlus:{block['type']}",
                "x": block["x"],
                "y": block["y"],
                "z": block["z"]
            }
            
            # Dodaj dodatkowe dane
            for key, value in block["data"].items():
                te_nbt[key] = value
            
            edits.append({
                "op": "set_te",
                "x": block["x"],
                "y": block["y"],
                "z": block["z"],
                "nbt": te_nbt
            })
        
        patch = {"edits": edits}
        
        patch_path = self.output_path / "ep_test_patch.json"
        with open(patch_path, 'w', encoding='utf-8') as f:
            json.dump(patch, f, indent=2, ensure_ascii=False)
        
        print(f"Zapisano patch: {patch_path}")
        print(f"Liczba edycji: {len(edits)}")
        return patch_path
    
    def _generate_with_kotlin(self, patch_path: Path):
        """Wywołuje Kotlin worker do załadowania patcha."""
        print("\n--- Wywoływanie Kotlin worker ---")
        
        # Sprawdź czy istnieje jar worker
        build_dir = self.jvm_worker / "build" / "libs"
        jar_files = list(build_dir.glob("*.jar")) if build_dir.exists() else []
        
        if not jar_files:
            print("OSTRZEŻENIE: Nie znaleziono zbudowanego JAR worker")
            print("Próba budowy...")
            self._build_kotlin_worker()
            jar_files = list(build_dir.glob("*.jar"))
        
        if jar_files:
            jar_path = jar_files[0]
            print(f"Używam JAR: {jar_path}")
            
            # Przygotuj argumenty dla worker
            cmd = [
                "java", "-jar", str(jar_path),
                "--world", str(self.output_path),
                "--patch", str(patch_path)
            ]
            
            print(f"Komenda: {' '.join(cmd)}")
            
            try:
                result = subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    cwd=str(self.jvm_worker),
                    timeout=60
                )
                
                print(result.stdout)
                if result.returncode != 0:
                    print(f"Błąd: {result.stderr}")
                    print("Używam fallback...")
                    self._create_empty_region()
                else:
                    print("Patch załadowany pomyślnie!")
                    
            except Exception as e:
                print(f"Błąd wywołania worker: {e}")
                self._create_empty_region()
        else:
            print("Nie udało się zbudować worker, używam fallback")
            self._create_empty_region()
    
    def _build_kotlin_worker(self):
        """Buduje Kotlin worker."""
        print("Budowanie Kotlin worker...")
        try:
            if os.name == 'nt':  # Windows
                gradlew = self.jvm_worker / "gradlew.bat"
            else:
                gradlew = self.jvm_worker / "gradlew"
            
            result = subprocess.run(
                [str(gradlew), "build", "-x", "test"],
                capture_output=True,
                text=True,
                cwd=str(self.jvm_worker),
                timeout=120
            )
            
            if result.returncode == 0:
                print("Budowa zakończona sukcesem")
            else:
                print(f"Błąd budowy: {result.stderr}")
                
        except Exception as e:
            print(f"Błąd podczas budowy: {e}")
    
    def _create_empty_region(self):
        """Tworzy pusty region file jako fallback."""
        print("Tworzenie pustego region file (fallback)...")
        
        # Utwórz pusty plik regionu r.0.0.mca
        region_file = self.output_path / "region" / "r.0.0.mca"
        
        # Pusty region file - 8KB nagłówek (pusty)
        with open(region_file, 'wb') as f:
            f.write(bytes(8192))
        
        print(f"Utworzono pusty region: {region_file}")
    
    def _generate_metadata(self):
        """Generuje metadane dla testowej mapy."""
        print("\n--- Generowanie metadanych ---")
        
        metadata = {
            "generator": "EnchantingPlusTestWorldGenerator",
            "version": "1.7.10",
            "created": str(Path(__file__).stat().st_mtime),
            "blocks": {
                "enchanting_table": 4,
                "advanced_table": 4,
                "arcane_inscriber": 3
            },
            "variants": [b["variant"] for b in self.BLOCKS_CONFIG],
            "conversion_target": "Enchanting Infuser 1.18.2",
            "total_blocks": len(self.BLOCKS_CONFIG)
        }
        
        metadata_path = self.output_path / "ep_test_metadata.json"
        with open(metadata_path, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, indent=2, ensure_ascii=False)
        
        print(f"Metadane zapisane do: {metadata_path}")


def generate_test_world(output_path: str = None) -> Path:
    """
    Funkcja pomocnicza do generowania testowej mapy.
    
    Args:
        output_path: Ścieżka do wygenerowanej mapy (opcjonalnie)
        
    Returns:
        Ścieżka do wygenerowanej mapy
    """
    generator = EnchantingPlusTestWorldGenerator(output_path)
    return generator.generate()


def main():
    """Główna funkcja generatora."""
    import sys
    
    output_path = sys.argv[1] if len(sys.argv) > 1 else None
    
    generator = EnchantingPlusTestWorldGenerator(output_path)
    result_path = generator.generate()
    
    print(f"\nTestowa mapa wygenerowana w: {result_path}")


if __name__ == "__main__":
    main()
