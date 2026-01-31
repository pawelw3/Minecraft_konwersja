"""
Test: Round-trip TileEntities (walidacja poprawności zapisu/odczytu TE)

Testuje:
1. Wstawienie hoppera z itemem
2. Wstawienie command blocka z komendą
3. Zapis i ponowny odczyt
4. Porównanie NBT TE
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from mc_editkit.world.editor import WorldEditor, edit_world, WorldCopier
from mc_editkit.world.types import Pos
from mc_editkit.blocks.registry import get_registry


def test_hopper_with_item():
    """Test hoppera z itemem w środku"""
    print("Test 1: Hopper z itemem...")
    
    test_world = "headless_server/1.7.10/world"
    world_copy = WorldCopier.create_copy(test_world)
    
    try:
        registry = get_registry()
        hopper_id = registry.get_id("minecraft:hopper")
        
        # Wstaw hopper z itemem
        with edit_world(world_copy, backup=True) as editor:
            pos = Pos(100, 200, 100)
            editor.set_block(pos, hopper_id, 0)
            editor.set_tile_entity(pos, {
                'id': 'Hopper',
                'Items': [
                    {
                        'Slot': 0,
                        'id': 'minecraft:cobblestone',
                        'Count': 1,
                        'Damage': 0
                    }
                ],
                'TransferCooldown': 0
            })
        
        # Odczytaj i weryfikuj
        editor2 = WorldEditor(world_copy, backup=False)
        te = editor2.get_tile_entity(Pos(100, 200, 100))
        editor2.close()
        
        assert te is not None, "TileEntity nie zostało odczytane"
        assert te.get('id') == 'Hopper', f"Oczekiwano 'Hopper', otrzymano {te.get('id')}"
        
        items = te.get('Items', [])
        assert len(items) == 1, f"Oczekiwano 1 item, otrzymano {len(items)}"
        
        item = items[0]
        assert item.get('id') == 'minecraft:cobblestone', f"Niepoprawny item: {item.get('id')}"
        assert item.get('Count') == 1, f"Niepoprawna ilość: {item.get('Count')}"
        
        print("  OK: Hopper z itemem poprawnie zapisany i odczytany")
        return True
        
    finally:
        import shutil
        shutil.rmtree(world_copy, ignore_errors=True)


def test_command_block_roundtrip():
    """Test command blocka - pełny round-trip"""
    print("Test 2: Command block round-trip...")
    
    test_world = "headless_server/1.7.10/world"
    world_copy = WorldCopier.create_copy(test_world)
    
    try:
        test_command = "/say [TEST] Hello from round-trip test!"
        
        # Wstaw
        with edit_world(world_copy, backup=True) as editor:
            pos = Pos(100, 200, 100)
            editor.set_command_block(pos, test_command, custom_name="@Test", track_output=True)
        
        # Odczytaj
        editor2 = WorldEditor(world_copy, backup=False)
        te = editor2.get_tile_entity(Pos(100, 200, 100))
        editor2.close()
        
        assert te is not None, "TileEntity nie zostało odczytane"
        assert te.get('id') == 'Control', f"Oczekiwano 'Control', otrzymano {te.get('id')}"
        assert te.get('Command') == test_command, f"Komenda niezgodna: {te.get('Command')}"
        assert te.get('CustomName') == '@Test', f"CustomName niezgodny: {te.get('CustomName')}"
        
        print("  OK: Command block poprawnie zapisany i odczytany")
        return True
        
    finally:
        import shutil
        shutil.rmtree(world_copy, ignore_errors=True)


def test_multiple_te_in_chunk():
    """Test wielu TE w jednym chunku"""
    print("Test 3: Wiele TE w jednym chunku...")
    
    test_world = "headless_server/1.7.10/world"
    world_copy = WorldCopier.create_copy(test_world)
    
    try:
        with edit_world(world_copy, backup=True) as editor:
            # Wstaw 3 command blocki w jednym chunku
            for i in range(3):
                editor.set_command_block(
                    Pos(100 + i, 200, 100),
                    f"/say Test {i}"
                )
        
        # Weryfikacja
        editor2 = WorldEditor(world_copy, backup=False)
        
        for i in range(3):
            te = editor2.get_tile_entity(Pos(100 + i, 200, 100))
            assert te is not None, f"TE {i} nie zostało odczytane"
            assert f"/say Test {i}" in te.get('Command', ''), f"Komenda {i} niezgodna"
        
        editor2.close()
        
        print("  OK: Wiele TE w chunku poprawnie zapisanych i odczytanych")
        return True
        
    finally:
        import shutil
        shutil.rmtree(world_copy, ignore_errors=True)


def main():
    print("=" * 60)
    print("TEST ROUND-TRIP TILE ENTITIES")
    print("=" * 60)
    
    results = []
    
    try:
        results.append(("Hopper + item", test_hopper_with_item()))
    except Exception as e:
        print(f"  FAIL: {e}")
        import traceback
        traceback.print_exc()
        results.append(("Hopper + item", False))
    
    try:
        results.append(("Command block", test_command_block_roundtrip()))
    except Exception as e:
        print(f"  FAIL: {e}")
        import traceback
        traceback.print_exc()
        results.append(("Command block", False))
    
    try:
        results.append(("Multiple TE", test_multiple_te_in_chunk()))
    except Exception as e:
        print(f"  FAIL: {e}")
        import traceback
        traceback.print_exc()
        results.append(("Multiple TE", False))
    
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
