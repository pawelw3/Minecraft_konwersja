# Raport z testu spiralnego (Variant B)

## Data wykonania
2026-01-31

## Cel testu
Sprawdzenie czy command blocki na serwerze 1.7.10 logują wiadomości do konsoli (czatu serwera) zgodnie z instrukcją `test_spiral_probe_variant_b.md`.

## Wykonane kroki

### 1. Generowanie spirali
- Wygenerowano spiralę o promieniu R=3 (49 chunków)
- Kolejność spiralna: (0,0), (1,0), (1,1), (0,1), (-1,1), ...
- Każdy chunk miał mieć platformę stone + command block z komendą `/say [PROBE] REACHED cx=X cz=Z step=N`
- Chunk startowy (0,0) miał mieć redstone_block jako źródło zasilania

### 2. Próby wstawienia bloków do świata

#### Próba 1: Bezpośrednia modyfikacja NBT
- Napisanie skryptu `build_spiral_world.py` do tworzenia nowego świata
- Problem: Chunki nie były poprawnie zapisywane (0 sekcji po zapisie)
- Wynik: FAIL

#### Próba 2: Modyfikacja istniejącego świata przez nbtlib
- Napisanie skryptu `insert_spiral_v2.py` używającego biblioteki nbtlib
- Problem: Problemy z API nbtlib (read-only ByteArray, brak metod serializacji)
- Wynik: FAIL

#### Próba 3: Użycie amulet-core
- Napisanie skryptu `insert_spiral_amulet.py` używającego amulet-core
- Problem: Amulet próbował konwertować bloki z 1.7.10 na 1.12.2 (universal format)
- Błędy translacji bloków: `Error converting block minecraft:stone to universal`
- Po zapisie świata serwer nie mógł załadować chunków (ArrayIndexOutOfBoundsException)
- Wynik: FAIL - uszkodzenie plików regionów

### 3. Przywrócenie oryginalnego świata
- Przywrócono oryginalne pliki regionów z kopii `mapa_1710/`
- Serwer uruchamia się poprawnie

### 4. Analiza istniejących command blocków
W oryginalnym świecie znaleziono 5 command blocków:
- Pozycje: (453, 106, 380), (447, 106, 393), (433, 106, 398), (443, 106, 386), (452, 106, 386)
- Wszystkie są PUSTE (brak komend)
- Prawdopodobnie pozostałości po wcześniejszych testach

## Wnioski

### Co poszło nie tak:
1. **Brak odpowiedniego narzędzia** - Nie ma gotowej biblioteki Python do bezpiecznej edycji światów Minecraft 1.7.10
2. **Problemy z wersjami** - Amulet i inne narzędzia są zoptymalizowane pod nowsze wersje (1.12+)
3. **Złożoność formatu NBT** - Bezpośrednia modyfikacja wymaga dokładnej znajomości struktury chunków

### Co byłoby potrzebne do sukcesu:
1. **WorldEdit jako mod** na serwerze 1.7.10 + wgranie schematu przez konsolę
2. **MCEdit Unified** - edytor wspierający 1.7.10 (niestety przestarzały)
3. **Ręczne zbudowanie** struktury przez gracza na serwerze
4. **Lepsza biblioteka** do edycji chunków (np. dostosowana wersja amulet-core)

### Obecny stan:
- Serwer 1.7.10 działa poprawnie z oryginalnym światem
- Command blocki są włączone w `server.properties` (`enable-command-block=true`)
- Brak gotowej struktury testowej do wykonania testu

## Rekomendacje

Aby wykonać test zgodnie z instrukcją `test_spiral_probe_variant_b.md`, należy:

1. **Opcja A - WorldEdit:**
   - Zainstalować WorldEdit na serwerze 1.7.10
   - Zbudować strukturę ręcznie lub załadować schemat

2. **Opcja B - Ręczne budowanie:**
   - Wejść na serwer jako gracz
   - Zbudować spiralę krok po kroku
   - Ustawić komendy w command blockach

3. **Opcja C - Skrypt zewnętrzny:**
   - Użyć Minecraft Command Block API (np. przez RCON)
   - Ustawić bloki przez komendy `/setblock`

## Pliki wygenerowane
- `headless_server/tests/spiral_chunks_r3.txt` - lista chunków spirali
- `headless_server/tests/generate_spiral_schematic.py` - generator spirali
- `headless_server/tests/build_spiral_world.py` - próba tworzenia świata
- `headless_server/tests/insert_spiral_*.py` - próby wstawienia bloków

---
**Status testu:** NIEKOMPLETNY - wymaga ręcznego zbudowania struktury lub użycia odpowiedniego narzędzia.
