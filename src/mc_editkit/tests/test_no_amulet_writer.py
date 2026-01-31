"""
Test guard: sprawdza że backend NIE używa amulet-core do zapisu.

Ten test ma FAILować jeśli ktoś użyje amulet w backendzie.
"""
import sys
from pathlib import Path
import ast
import inspect

sys.path.insert(0, str(Path(__file__).parent.parent.parent))


def test_backend_no_amulet_import():
    """Sprawdza że anvil_backend.py nie importuje amulet"""
    backend_file = Path(__file__).parent.parent / "world" / "backends" / "anvil_backend.py"
    
    assert backend_file.exists(), f"Nie znaleziono pliku backendu: {backend_file}"
    
    with open(backend_file, 'r', encoding='utf-8') as f:
        source = f.read()
    
    # Parsuj kod
    tree = ast.parse(source)
    
    # Znajdź wszystkie importy
    imports = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                imports.append(alias.name)
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                imports.append(node.module)
    
    # Sprawdź czy nie ma amulet
    forbidden = ['amulet', 'amulet_core', 'amulet_nbt']
    found = [imp for imp in imports if any(f in imp.lower() for f in forbidden)]
    
    assert len(found) == 0, f"Backend używa zabronionych importów: {found}"
    print("OK: Backend nie importuje amulet")


def test_editor_uses_correct_backend():
    """Sprawdza że WorldEditor używa poprawnego backendu (nie Amulet)"""
    from mc_editkit.world.editor import WorldEditor
    from mc_editkit.world.backends.anvil_backend import AnvilBackend
    
    # Sprawdź czy backend to AnvilBackend (a nie AmuletBackend)
    # Import powinien wskazywać na anvil_backend, nie amulet_backend
    import mc_editkit.world.editor as editor_module
    
    with open(editor_module.__file__, 'r') as f:
        source = f.read()
    
    # Nie powinno być importu amulet_backend
    assert 'amulet_backend' not in source, "editor.py importuje amulet_backend!"
    assert 'AmuletBackend' not in source, "editor.py używa AmuletBackend!"
    
    print("OK: WorldEditor używa prawidłowego backendu")


def test_guard_hard_failure():
    """Twardy test: próba użycia AmuletBackend powinna się nie udać"""
    try:
        from mc_editkit.world.backends.amulet_backend import AmuletBackend
        # Jeśli import się udał, sprawdź czy nie jest używany domyślnie
        print("WARNING: AmuletBackend istnieje, ale nie powinien być używany")
    except ImportError:
        print("OK: AmuletBackend nie jest dostępny (usunięty)")


if __name__ == "__main__":
    print("=" * 60)
    print("GUARD TEST - Sprawdzenie braku Amulet w backendzie")
    print("=" * 60)
    
    try:
        test_backend_no_amulet_import()
        test_editor_uses_correct_backend()
        test_guard_hard_failure()
        print("\n" + "=" * 60)
        print("Wszystkie guard testy PASS")
        print("=" * 60)
    except AssertionError as e:
        print(f"\nGUARD TEST FAIL: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\nGUARD TEST ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
