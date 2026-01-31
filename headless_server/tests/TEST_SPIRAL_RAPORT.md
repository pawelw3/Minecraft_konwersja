# Raport z testu spiralnego Variant B

## Data wykonania
2026-01-31

## Podsumowanie
Test spirali został wykonany z użyciem nowego pakietu `mc_editkit`. Spirala została zbudowana, ale serwer nie załadował poprawnie chunków przez problemy z kompatybilnością formatu NBT.

## Wykonane kroki

### 1. Implementacja mc_editkit
Utworzono kompletny pakiet do edycji światów Minecraft:
- `WorldEditor` API z operacjami `set_block`, `set_command_block`, `paste`
- `AmuletBackend` używający amulet-core
- `BlockRegistry` z mapowaniem bloków 1.7.10
- `Structure` do importu z voxel_grid.json
- CLI do paste i run-test

### 2. Budowa spirali
- Utworzono spiralę o promieniu R=3 (49 chunków)
- Wysokość Y=200 (bezpieczna, poza istniejącymi strukturami)
- Każdy chunk zawiera:
  - Platformę stone 5x5 na Y-1
  - Command block z komendą `/say [PROBE] REACHED cx=X cz=Z step=N`
  - Chunk startowy (0,0) z redstone_block jako źródło zasilania

Log budowy:
```
INFO - set_block(Pos(x=8, y=199, z=8)): 1:0 (stone)
INFO - set_block(Pos(x=8, y=200, z=8)): 152:0 (redstone_block)
INFO - set_command_block(Pos(x=9, y=200, z=8)): /say [PROBE] REACHED cx=1 cz=0 step=1...
...
Spirala zbudowana: 49 chunków
```

### 3. Uruchomienie serwera headless
```
[14:53:41] [Server thread/ERROR]: Couldn't load chunk
java.lang.ArrayIndexOutOfBoundsException
...
[14:53:43] [Server thread/INFO]: Done (4,156s)!
```

Serwer uruchomił się, ale z błędami przy ładowaniu chunków.

## Problemy

### Główny problem: Kompatybilność formatu NBT
`amulet-core` (użyty jako backend) pracuje z formatem "universal" opartym na MC 1.12+.
Przy zapisie do 1.7.10 występują błędy:
- "No output object given" przy konwersji bloków
- Chunki są zapisywane w formacie niezgodnym z 1.7.10
- Serwer rzuca `ArrayIndexOutOfBoundsException` przy ładowaniu chunków

### Skutek
Command blocki nie zostały załadowane przez serwer, więc nie było logów `[PROBE]`.

## Wnioski

### Co działa:
1. ✅ Pakiet `mc_editkit` - architektura, API, CLI
2. ✅ Backend `AmuletBackend` - odczyt i zapis (ale w złym formacie)
3. ✅ `BlockRegistry` - poprawne mapowanie ID bloków
4. ✅ Generowanie spirali - 49 chunków z command blockami

### Co wymaga naprawy:
1. ❌ **Backend zapisu** - potrzebny backend który zapisuje bezpośrednio w formacie 1.7.10 bez konwersji
   - Opcja A: Naprawa/poprawka `PyAnvilEditor`
   - Opcja B: Własna implementacja zapisu NBT dla 1.7.10
   - Opcja C: Użycie WorldEdit przez RCON/komendy

### Rekomendacja
Aby test Variant B zadziałał, należy:
1. Zaimplementować backend który nie konwertuje formatów (direct NBT read/write)
2. Lub użyć WorldEdit na serwerze do wstawienia schematu
3. Lub zbudować strukturę ręcznie w grze

## Pliki

Utworzone pliki:
- `src/mc_editkit/` - pakiet do edycji światów
- `src/mc_editkit/README.md` - dokumentacja
- `src/mc_editkit/tests/test_variant_b_spiral_probe.py` - test spirali

## Status
**TEST NIEKOMPLETNY** - wymiana backendu na kompatybilny z 1.7.10.
