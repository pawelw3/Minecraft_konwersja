"""
Skrypt do wykonania konwersji na testowej mapie Enchanting Plus.

Wykonuje:
1. Skanowanie mapy testowej w poszukiwaniu bloków EP
2. Konwersję bloków EP do formatu 1.18.2 (Enchanting Infuser)
3. Generowanie raportu z wynikami konwersji
"""

import sys
from pathlib import Path

# Dodaj src do path
sys.path.insert(0, str(Path(__file__).resolve().parents[3]))

from src.converters.enchantingplus import EPBatchConverter, EPReportGenerator


def run_test_conversion():
    """Wykonuje konwersję na testowej mapie."""
    print("=" * 60)
    print("KONWERSJA TESTOWEJ MAPY ENCHANTING PLUS")
    print("=" * 60)
    
    # Ścieżka do testowej mapy (absolutna)
    project_root = Path(__file__).resolve().parents[3]
    test_world_path = str(project_root / "lightweigh_map_templates" / "1710_modded" / "ep_test_world")
    output_path = str(project_root / "lightweigh_map_templates" / "1710_modded" / "ep_test_world_converted")
    
    print(f"\nŚcieżka źródłowa: {test_world_path}")
    print(f"Ścieżka docelowa: {output_path}")
    
    # Utwórz konwerter
    converter = EPBatchConverter(
        world_path_1710=test_world_path,
        output_path=output_path
    )
    
    # Wyświetl podsumowanie
    print("\n" + "=" * 60)
    print(converter.generate_summary_report())
    print("=" * 60)
    
    # Uruchom konwersję
    print("\n--- Rozpoczynanie konwersji ---")
    
    def progress(percent, message):
        print(f"[{percent:5.1f}%] {message}")
    
    converter.set_progress_callback(progress)
    
    # Konwertuj wszystkie regiony
    result = converter.run_batch_conversion()
    
    # Wyświetl wyniki
    print("\n" + "=" * 60)
    print("WYNIKI KONWERSJI")
    print("=" * 60)
    print(f"Całkowita liczba bloków: {result.stats.total_blocks}")
    print(f"Przekonwertowane: {result.stats.converted_blocks}")
    print(f"Usunięte: {result.stats.removed_blocks}")
    print(f"Nieudane: {result.stats.failed_blocks}")
    print(f"Skuteczność: {result.stats.success_rate:.1f}%")
    print(f"Czas wykonania: {result.stats.duration_seconds:.2f}s")
    
    if result.stats.blocks_by_type:
        print("\nBloki według typu:")
        for block_type, count in result.stats.blocks_by_type.items():
            print(f"  {block_type}: {count}")
    
    # Generuj raporty
    print("\n--- Generowanie raportów ---")
    report_generator = EPReportGenerator(output_path)
    reports = report_generator.generate_full_report(result)
    
    print(f"Raport HTML: {reports.get('html', 'N/A')}")
    print(f"Raport Markdown: {reports.get('markdown', 'N/A')}")
    
    # Zapisz wyniki
    result.save_json(f"{output_path}/conversion_result.json")
    print(f"\nWyniki zapisano w: {output_path}/conversion_result.json")
    
    print("\n" + "=" * 60)
    print("KONWERSJA ZAKOŃCZONA")
    print("=" * 60)
    
    return result


if __name__ == "__main__":
    run_test_conversion()
