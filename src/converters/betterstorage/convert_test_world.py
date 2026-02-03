"""
Skrypt konwertujący testową mapę Better Storage z 1.7.10 na 1.18.2.
"""

import json
import shutil
from pathlib import Path
from typing import Dict, List, Any, Optional

from src.converters.betterstorage.batch_converter import BetterStorageBatchConverter, ConversionResult


class TestWorldConverter:
    """Konwerter testowej mapy Better Storage."""
    
    def __init__(self, source_world: str, target_world: str):
        self.source_world = Path(source_world)
        self.target_world = Path(target_world)
        self.converter = BetterStorageBatchConverter(str(self.source_world))
        self.results: List[ConversionResult] = []
        
    def setup_target_world(self):
        """Przygotowuje świat docelowy."""
        if self.target_world.exists():
            shutil.rmtree(self.target_world)
            
        self.target_world.mkdir(parents=True, exist_ok=True)
        (self.target_world / 'region').mkdir(exist_ok=True)
        
        # Kopiuj level.dat jeśli istnieje
        source_level = self.source_world / 'level.dat'
        if source_level.exists():
            shutil.copy(source_level, self.target_world / 'level.dat')
            
    def read_source_chunks(self) -> List[Dict[str, Any]]:
        """Odczytuje chunki ze świata źródłowego."""
        chunks = []
        region_dir = self.source_world / 'region'
        
        if not region_dir.exists():
            print(f"Brak folderu region: {region_dir}")
            return chunks
            
        for mca_file in region_dir.glob('*.mca'):
            print(f"Odczyt regionu: {mca_file.name}")
            # TODO: Implementacja odczytu MCA przez Hephaistos lub Python
            # Na razie używamy prostego podejścia - przetwarzamy metadane
            
        return chunks
        
    def convert_all(self) -> Dict[str, Any]:
        """Wykonuje pełną konwersję mapy."""
        print("=" * 60)
        print("KONWERSJA TESTOWEJ MAPY BETTER STORAGE")
        print("=" * 60)
        print(f"Źródło: {self.source_world}")
        print(f"Cel: {self.target_world}")
        print()
        
        # Przygotuj świat docelowy
        self.setup_target_world()
        print("[OK] Przygotowano swiat docelowy")
        
        # Odczytaj metadane ze świata źródłowego
        metadata_path = self.source_world / 'editkit_metadata.json'
        if metadata_path.exists():
            with open(metadata_path, 'r', encoding='utf-8') as f:
                metadata = json.load(f)
            print(f"[OK] Odczytano metadane: {len(metadata.get('expected_changes', []))} zmian")
        else:
            print("[WARN] Brak metadanych")
            metadata = {}
            
        # Odczytaj patch
        patch_path = self.source_world / 'betterstorage_test_patch.json'
        if patch_path.exists():
            with open(patch_path, 'r', encoding='utf-8') as f:
                patch = json.load(f)
            print(f"[OK] Odczytano patch: {len(patch.get('edits', []))} edycji")
        else:
            print("[WARN] Brak patcha")
            patch = {'edits': []}
            
        # Konwertuj każdy TE
        print("\n--- Konwersja bloków ---")
        
        te_edits = [e for e in patch.get('edits', []) if e['op'] == 'set_te']
        converted_count = 0
        failed_count = 0
        
        conversion_report = {
            'source_world': str(self.source_world),
            'target_world': str(self.target_world),
            'total_te': len(te_edits),
            'converted': [],
            'failed': [],
            'details': []
        }
        
        for edit in te_edits:
            x, y, z = edit['x'], edit['y'], edit['z']
            nbt = edit['nbt']
            te_id = nbt.get('id', 'unknown')
            
            print(f"\nKonwersja: {te_id} at ({x}, {y}, {z})")
            
            # Konwertuj
            result = self.converter.convert_single(te_id, nbt, x, y, z)
            self.results.append(result)
            
            detail = {
                'original_id': te_id,
                'position': {'x': x, 'y': y, 'z': z},
                'target_id': result.target_block,
                'success': result.success,
                'warnings': result.warnings,
                'overflow_count': len(result.overflow)
            }
            
            if result.success:
                converted_count += 1
                print(f"  [OK] {result.target_block}")
                if result.warnings:
                    print(f"  [WARN] Ostrzezenia: {result.warnings}")
                conversion_report['converted'].append(detail)
            else:
                failed_count += 1
                print(f"  [ERR] Blad: {result.error}")
                conversion_report['failed'].append(detail)
                
            conversion_report['details'].append(detail)
            
        # Podsumowanie
        print("\n" + "=" * 60)
        print("PODSUMOWANIE KONWERSJI")
        print("=" * 60)
        print(f"Przekonwertowane: {converted_count}/{len(te_edits)}")
        print(f"Błędy: {failed_count}")
        
        # Statystyki
        stats = self.converter.stats
        print(f"\nStatystyki:")
        print(f"  Całkowity czas: {stats.elapsed_time:.2f}s")
        print(f"  Ostrzeżenia: {stats.warnings}")
        print(f"  Itemy overflow: {stats.overflow_items}")
        
        # Podsumowanie per typ
        print("\nKonwersje per typ:")
        type_counts = {}
        for result in self.results:
            block_type = result.original_block
            type_counts[block_type] = type_counts.get(block_type, 0) + 1
            
        for block_type, count in sorted(type_counts.items()):
            print(f"  {block_type}: {count}")
            
        # Zapisz raport
        report_path = self.target_world / 'conversion_report.json'
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(conversion_report, f, indent=2, ensure_ascii=False)
        print(f"\n[OK] Raport zapisany: {report_path}")
        
        return conversion_report
        
    def generate_118_patch(self) -> Path:
        """Generuje patch dla 1.18.2 w formacie JSON."""
        print("\n--- Generowanie patcha 1.18.2 ---")
        
        patch_118 = {
            'format_version': '1.18.2',
            'edits': [],
            'metadata': {
                'source': 'betterstorage_test_1710',
                'converter': 'BetterStorageConverter',
            }
        }
        
        for result in self.results:
            if not result.success:
                continue
                
            # Dodaj blok
            patch_118['edits'].append({
                'op': 'set_block',
                'x': result.x,
                'y': result.y,
                'z': result.z,
                'block_id': result.target_block,
            })
            
            # Dodaj TE jeśli ma NBT
            if result.nbt:
                patch_118['edits'].append({
                    'op': 'set_te',
                    'x': result.x,
                    'y': result.y,
                    'z': result.z,
                    'nbt': result.nbt,
                })
                
        patch_path = self.target_world / 'patch_1182.json'
        with open(patch_path, 'w', encoding='utf-8') as f:
            json.dump(patch_118, f, indent=2, ensure_ascii=False)
            
        print(f"[OK] Patch 1.18.2 zapisany: {patch_path}")
        print(f"  Edycje: {len(patch_118['edits'])}")
        
        return patch_path


def main():
    """Główna funkcja konwertująca testową mapę."""
    source = 'lightweigh_map_templates/1710/betterstorage_test'
    target = 'lightweigh_map_templates/118/betterstorage_test_converted'
    
    converter = TestWorldConverter(source, target)
    report = converter.convert_all()
    
    # Generuj patch 1.18.2
    converter.generate_118_patch()
    
    print("\n" + "=" * 60)
    print("KONWERSJA ZAKOŃCZONA")
    print("=" * 60)
    print(f"Świat źródłowy: {source}")
    print(f"Świat docelowy: {target}")
    print(f"Raport: {target}/conversion_report.json")


if __name__ == '__main__':
    main()
