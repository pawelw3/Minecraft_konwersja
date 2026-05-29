"""
Główny skrypt do czyszczenia mapy - uproszczony interfejs.

Przykłady użycia:
    # Wyczyść całą mapę
    python run_cleaning.py
    
    # Wyczyść tylko konkretny region (np. spawn 0,0)
    python run_cleaning.py --region 0,0
    
    # Najpierw przeanalizuj, potem wyczyść
    python run_cleaning.py --analyze-first
    
    # Tylko analiza bez czyszczenia
    python run_cleaning.py --analyze-only
"""
import subprocess
import sys
from pathlib import Path


def run_command(cmd: list, description: str) -> bool:
    """Uruchamia komendę i zwraca sukces/porażkę."""
    print(f"\n{'='*60}")
    print(f"{description}")
    print(f"{'='*60}")
    
    result = subprocess.run(cmd, capture_output=False)
    return result.returncode == 0


def main():
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Czyści mapę Minecraft 1.7.10 z modów, TE i entities",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Przykłady:
  python run_cleaning.py                    # Wyczyść całą mapę
  python run_cleaning.py --region 0,0       # Wyczyść tylko region 0,0
  python run_cleaning.py --analyze-first    # Najpierw analiza, potem czyszczenie
  python run_cleaning.py --analyze-only     # Tylko analiza
        """
    )
    
    parser.add_argument(
        "--region",
        type=str,
        help="Przetwórz tylko konkretny region (format: x,z, np. 0,0 lub -1,-2)"
    )
    parser.add_argument(
        "--analyze-first",
        action="store_true",
        help="Najpierw przeanalizuj mapę przed czyszczeniem"
    )
    parser.add_argument(
        "--analyze-only",
        action="store_true",
        help="Tylko analiza, bez czyszczenia"
    )
    parser.add_argument(
        "--source",
        type=Path,
        default=Path(__file__).parent.parent / "mapa_1710",
        help="Ścieżka do źródłowego świata (domyślnie: ../mapa_1710)"
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path(__file__).parent / "map_1710_no_mods",
        help="Ścieżka do wyjściowego świata (domyślnie: ./map_1710_no_mods)"
    )
    parser.add_argument(
        "--move",
        action="store_true",
        help="Użyj przeniesienia (move) zamiast kopiowania - szybsze i oszczędza miejsce, ALE usuwa źródło!"
    )
    
    args = parser.parse_args()
    
    script_dir = Path(__file__).parent
    
    # Sprawdź czy map-cleaner JAR jest zbudowany
    cleaner_jar = Path(__file__).parent / "jvm" / "build" / "libs" / "map-cleaner-1.0-SNAPSHOT.jar"
    if not cleaner_jar.exists():
        print("UWAGA: map-cleaner JAR nie jest zbudowany!")
        print(f"   Nie znaleziono: {cleaner_jar}")
        print("   Zbuduj go za pomoca:")
        print("   cd map_cleaning\\jvm && .\\gradlew.bat build")
        print()
        response = input("Czy chcesz kontynuowac mimo to? (t/n): ")
        if response.lower() not in ('t', 'tak', 'y', 'yes'):
            sys.exit(1)
    
    # Analiza
    if args.analyze_first or args.analyze_only:
        cmd = [
            sys.executable,
            str(script_dir / "analyze_map.py"),
            "--world", str(args.source)
        ]
        
        if args.region:
            cmd.extend(["--region", args.region])
        
        if not run_command(cmd, "ANALIZA MAPY"):
            print("❌ Analiza nie powiodła się!")
            sys.exit(1)
        
        if args.analyze_only:
            print("\n✅ Analiza zakończona")
            sys.exit(0)
        
        print("\n" + "="*60)
        response = input("Kontynuować czyszczenie? (t/n): ")
        if response.lower() not in ('t', 'tak', 'y', 'yes'):
            print("Przerwano przez użytkownika")
            sys.exit(0)
    
    # Czyszczenie
    cmd = [
        sys.executable,
        str(script_dir / "clean_map.py"),
        "--source", str(args.source),
        "--output", str(args.output)
    ]
    
    if args.region:
        cmd.extend(["--region", args.region])
    
    # Usuń puste stringi z cmd
    cmd = [c for c in cmd if c]
    
    if run_command(cmd, "CZYSZCZENIE MAPY"):
        print("\n" + "="*60)
        print("✅ CZYSZCZENIE ZAKOŃCZONE SUKCESEM!")
        print(f"📁 Wyczyszczona mapa: {args.output}")
        print("="*60)
        sys.exit(0)
    else:
        print("\n" + "="*60)
        print("❌ CZYSZCZENIE NIE POWIODŁO SIĘ!")
        print("="*60)
        sys.exit(1)


if __name__ == "__main__":
    main()
