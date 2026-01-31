"""
CLI dla mc_editkit
"""
import sys
import argparse
import logging
from pathlib import Path

from .world.editor import WorldEditor, edit_world, WorldCopier
from .world.types import Pos
from .structures.structure import Structure
from .blocks.registry import get_registry

def cmd_paste(args):
    """Komenda paste - wstawia strukturę z pliku voxel_grid.json"""
    logging.basicConfig(level=logging.INFO)
    
    print(f"Wczytywanie struktury z {args.voxel}...")
    structure = Structure.from_voxel_grid(args.voxel)
    
    origin = Pos(args.origin[0], args.origin[1], args.origin[2])
    print(f"Wstawianie na pozycję {origin}...")
    
    with edit_world(args.world, backup=True) as editor:
        structure.paste(editor, origin)
    
    print("Gotowe!")
    return 0


def cmd_run_test(args):
    """Komenda run-test - uruchamia test headless"""
    if args.test == "variant_b":
        from .tests.test_variant_b_spiral_probe import main as test_main
        sys.argv = [
            "test_variant_b",
            "--world", args.world,
            "--radius", str(args.radius),
            "--duration", str(args.duration)
        ]
        return test_main()
    else:
        print(f"Nieznany test: {args.test}")
        return 1


def main():
    parser = argparse.ArgumentParser(
        prog='mc_editkit',
        description='Narzędzie do OFFLINE edycji światów Minecraft 1.7.10'
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Dostępne komendy')
    
    # Komenda paste
    paste_parser = subparsers.add_parser('paste', help='Wstawia strukturę z pliku voxel_grid.json')
    paste_parser.add_argument('--world', required=True, help='Ścieżka do świata')
    paste_parser.add_argument('--voxel', required=True, help='Ścieżka do pliku voxel_grid.json')
    paste_parser.add_argument('--origin', nargs=3, type=int, required=True,
                              help='Pozycja wstawienia (x y z)')
    paste_parser.set_defaults(func=cmd_paste)
    
    # Komenda run-test
    test_parser = subparsers.add_parser('run-test', help='Uruchamia test headless')
    test_parser.add_argument('--world', required=True, help='Ścieżka do świata')
    test_parser.add_argument('--test', required=True, choices=['variant_b'],
                            help='Nazwa testu')
    test_parser.add_argument('--radius', type=int, default=3, help='Promień spirali')
    test_parser.add_argument('--duration', type=int, default=120, help='Czas testu')
    test_parser.set_defaults(func=cmd_run_test)
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 1
    
    return args.func(args)


if __name__ == '__main__':
    sys.exit(main())
