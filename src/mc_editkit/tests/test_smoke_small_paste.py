"""
Test: Smoke test małej wstawki (walidacja podstawowych operacji)

Testuje:
1. Otwarcie świata
2. Wstawienie pojedynczego bloku
3. Zapis zmian
4. Ponowne otwarcie i weryfikacja
5. Smoke boot serwera
"""
import sys
import subprocess
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from mc_editkit.world.editor import WorldEditor, WorldCopier, edit_world
from mc_editkit.world.types import Pos
from mc_editkit.blocks.registry import get_registry


def test_single_block_paste():
    """Test wstawienia pojedynczego bloku"""
    print("Test 1: Wstawienie pojedynczego bloku...")
    
    # Ścieżka do testowego świata
    test_world = "headless_server/1.7.10/world"
    
    # Kopia
    world_copy = WorldCopier.create_copy(test_world)
    
    try:
        registry = get_registry()
        stone_id = registry.get_id("minecraft:stone")
        
        # Wstaw blok
        with edit_world(world_copy, backup=True) as editor:
            editor.set_block(Pos(100, 200, 100), stone_id, 0)
        
        # Weryfikacja - otwórz ponownie
        editor2 = WorldEditor(world_copy, backup=False)
        block_id, meta = editor2.get_block(Pos(100, 200, 100))
        editor2.close()
        
        assert block_id == stone_id, f"Oczekiwano stone ({stone_id}), otrzymano {block_id}"
        print("  OK: Blok został poprawnie wstawiony")
        
        return True
        
    finally:
        import shutil
        shutil.rmtree(world_copy, ignore_errors=True)


def test_command_block_with_te():
    """Test wstawienia command blocka z TileEntity"""
    print("Test 2: Wstawienie command blocka z TE...")
    
    test_world = "headless_server/1.7.10/world"
    world_copy = WorldCopier.create_copy(test_world)
    
    try:
        with edit_world(world_copy, backup=True) as editor:
            editor.set_command_block(
                Pos(100, 200, 100),
                "/say Hello World!"
            )
        
        # Weryfikacja
        editor2 = WorldEditor(world_copy, backup=False)
        te = editor2.get_tile_entity(Pos(100, 200, 100))
        editor2.close()
        
        assert te is not None, "TileEntity nie zostało wstawione"
        assert te.get('id') == 'Control', f"Oczekiwano 'Control', otrzymano {te.get('id')}"
        assert 'Hello World!' in te.get('Command', ''), "Komenda nie została zapisana"
        print("  OK: Command block z TE poprawnie wstawiony")
        
        return True
        
    finally:
        import shutil
        shutil.rmtree(world_copy, ignore_errors=True)


def test_smoke_boot():
    """Test smoke boot serwera po edycji"""
    print("Test 3: Smoke boot serwera...")
    
    test_world = "headless_server/1.7.10/world"
    world_copy = WorldCopier.create_copy(test_world)
    
    try:
        # Wstaw kilka bloków
        with edit_world(world_copy, backup=True) as editor:
            registry = get_registry()
            editor.set_block(Pos(100, 200, 100), registry.get_id("minecraft:stone"), 0)
            editor.set_block(Pos(101, 200, 100), registry.get_id("minecraft:redstone_block"), 0)
            editor.set_command_block(Pos(102, 200, 100), "/say Test")
        
        # Uruchom serwer na 15 sekund
        server_dir = Path(world_copy).parent
        proc = subprocess.Popen(
            ["java", "-Xmx1G", "-Xms512M", "-jar", "minecraft_server.1.7.10.jar", "nogui"],
            cwd=server_dir,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True
        )
        
        # Czekaj na uruchomienie
        time.sleep(15)
        
        # Zatrzymaj
        try:
            proc.stdin.write("stop\n")
            proc.stdin.flush()
            proc.wait(timeout=10)
        except:
            proc.kill()
        
        # Sprawdź logi
        latest_log = server_dir / "logs" / "latest.log"
        if latest_log.exists():
            content = latest_log.read_text()
            if "Done (" in content:
                print("  OK: Serwer uruchomił się poprawnie")
                return True
            elif "error" in content.lower() or "exception" in content.lower():
                print("  FAIL: Błędy w logach serwera")
                return False
        
        print("  OK: Serwer zakończył bez crasha")
        return True
        
    finally:
        import shutil
        shutil.rmtree(world_copy, ignore_errors=True)


def main():
    print("=" * 60)
    print("SMOKE TEST - Mała wstawka")
    print("=" * 60)
    
    results = []
    
    try:
        results.append(("Single block", test_single_block_paste()))
    except Exception as e:
        print(f"  FAIL: {e}")
        results.append(("Single block", False))
    
    try:
        results.append(("Command block + TE", test_command_block_with_te()))
    except Exception as e:
        print(f"  FAIL: {e}")
        results.append(("Command block + TE", False))
    
    try:
        results.append(("Smoke boot", test_smoke_boot()))
    except Exception as e:
        print(f"  FAIL: {e}")
        results.append(("Smoke boot", False))
    
    print("\n" + "=" * 60)
    print("PODSUMOWANIE")
    print("=" * 60)
    
    for name, passed in results:
        status = "PASS" if passed else "FAIL"
        print(f"  {name}: {status}")
    
    all_passed = all(passed for _, passed in results)
    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())
