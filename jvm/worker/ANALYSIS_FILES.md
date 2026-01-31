# Dokumentacja plików analizy redstone

> Dokumentacja plików źródłowych używanych do analizy mapy Minecraft pod kątem elementów redstone.
> Ostatnia aktualizacja: 2026-01-31

## Spis treści
- [Pliki źródłowe](#pliki-źródłowe)
- [Biblioteki zewnętrzne](#biblioteki-zewnętrzne)
- [Wyniki analizy dla kimi1](#wyniki-analizy-dla-kimi1)

---

## Pliki źródłowe

### 1. Main.kt
**Lokalizacja:** `src/main/kotlin/mc/editkit/worker/Main.kt`

**Opis:** Główny punkt wejścia aplikacji CLI. Parsuje argumenty linii komend i wywołuje odpowiednie funkcje analizy.

**Działanie dla kimi1:**
- Wywołuje `analyzeRedstoneCommand()` lub `correctAnalysis()` w zależności od flagi
- Obsługuje komendy: `--analyze-redstone`, `--correct-analysis`, `--wide-analysis`, itp.

**Komendy CLI:**
```bash
java -jar worker.jar --world <ścieżka> --analyze-redstone 2
java -jar worker.jar --world <ścieżka> --correct-analysis
java -jar worker.jar --world <ścieżka> --wide-analysis
```

---

### 2. RedstoneAnalyzer.kt
**Lokalizacja:** `src/main/kotlin/mc/editkit/worker/RedstoneAnalyzer.kt`

**Opis:** Główny analizator elementów redstone. Skanuje chunki w poszukiwaniu bloków z listy REDSTONE_COMPONENTS.

**Kluczowe funkcje:**
- `analyzeChunk(cx, cz)` - analiza pojedynczego chunka
- `analyzeAroundChunkZeroZero(radius)` - analiza chunków wokół (0,0)
- `findRedstoneCircuits()` - znajduje połączone obwody redstone

**Mapowanie ID bloków (Minecraft 1.7.10):**
```kotlin
55  = Redstone Wire
75  = Redstone Torch (off)
76  = Redstone Torch (on)
93  = Redstone Repeater (off)
94  = Redstone Repeater (on)
152 = Block of Redstone
137 = Command Block
```

**Działanie dla kimi1:**
- Sprawdza chunk (0,0) i sąsiednie w promieniu 2 chunków
- Znajduje 36 elementów na poziomie Y=4
- Mapuje ID bloków na nazwy czytelne dla człowieka

---

### 3. ChunkInspector.kt
**Lokalizacja:** `src/main/kotlin/mc/editkit/worker/ChunkInspector.kt`

**Opis:** Szczegółowa inspekcja konkretnych chunków. Wyświetla szczegółowe informacje o blokach w podanych chunkach.

**Analizowane chunki:**
- (0, 0) - centralny chunk
- (-1, -1) - lewy górny
- (0, -1) - górny
- (-1, 0) - lewy

**Działanie dla kimi1:**
```
Chunk (0, 0):   36 elementów redstone, Y=4
Chunk (-1, -1): "Niezapisany (null)" - chunk nie istnieje w regionie
Chunk (0, -1):  "Brak redstone" - chunk istnieje, ale bez redstone
Chunk (-1, 0):  "Brak redstone" - chunk istnieje, ale bez redstone
```

---

### 4. ExtendedInspector.kt
**Lokalizacja:** `src/main/kotlin/mc/editkit/worker/ExtendedInspector.kt`

**Opis:** Analiza chunków w promieniu 2 (-2 do 2) wokół punktu (0,0). Tworzy wizualną mapę chunków.

**Format wyjścia:**
```
     -2 -1  0  1  2
Z-2:  .  .  .  .  .
Z-1:  .  .  .  .  .
Z 0:  .  . 36  .  .
Z 1:  .  .  .  .  .
Z 2:  .  .  .  .  .
```

**Działanie dla kimi1:**
- Sprawdza 25 chunków (5x5)
- Tylko chunk (0,0) zawiera redstone (36 elementów)
- Pozostałe 24 chunki są puste

---

### 5. FullAreaScan.kt
**Lokalizacja:** `src/main/kotlin/mc/editkit/worker/FullAreaScan.kt`

**Opis:** Pełne skanowanie obszaru chunków od -5 do 4 (co odpowiada zakresowi bloków -80 do 80).

**Zakres:**
- Chunki X: -5 do 4
- Chunki Z: -5 do 4
- Bloki: -80 do 80 na każdej osi

**Działanie dla kimi1:**
- Przeszukuje 100 chunków (10x10)
- Znajduje tylko 1 chunk z redstone: (0,0)
- Łącznie: 36 elementów redstone

---

### 6. CorrectAnalysis.kt
**Lokalizacja:** `src/main/kotlin/mc/editkit/worker/CorrectAnalysis.kt`

**Opis:** Poprawiona analiza sprawdzająca **WSZYSTKIE** poziomy Y (0-255), a nie tylko Y=4. Szuka redstone we wszystkich sekcjach NBT chunka.

**Kluczowa różnica:**
- Standardowa analiza: może pomijać niektóre sekcje
- CorrectAnalysis: iteruje po wszystkich sekcjach `Sections` w NBT chunka

**Działanie dla kimi1:**
```
Chunk (0, 0):  36 elementów redstone, tylko Y=4
Chunk (0, -1): Brak redstone
Chunk (-1, 0): Brak redstone
Chunk (-1, -1): Niezapisany (null)
Chunk (1, 0):  Brak redstone
Chunk (0, 1):  Brak redstone
RAZEM: 36 elementów (wszystkie na Y=4)
```

---

### 7. WideAreaAnalysis.kt
**Lokalizacja:** `src/main/kotlin/mc/editkit/worker/WideAreaAnalysis.kt`

**Opis:** Najbardziej kompleksowa analiza - skanuje **WSZYSTKIE** chunki we wszystkich plikach regionów (.mca) w folderze `region/`.

**Algorytm:**
1. Lista wszystkich plików `*.mca` w folderze region
2. Dla każdego regionu (32x32 chunki):
   - Iteracja po localX (0-31) i localZ (0-31)
   - Odczyt chunka przez `region.getChunkData(localX, localZ)`
   - Zliczanie bloków redstone w sekcjach
3. Sumowanie wyników ze wszystkich regionów

**Działanie dla kimi1:**
```
Region r.0.0.mca:   37 elementów redstone
Pozostałe regiony:  0 elementów (błędy odczytu lub puste)

Szczegóły chunków:
- Chunk (0, 0):  36 elementów
- Chunk (0, 10): 1 element

RAZEM: 37 elementów redstone
```

---

### 8. SpiralPatternDetector.kt
**Lokalizacja:** `src/main/kotlin/mc/editkit/worker/SpiralPatternDetector.kt`

**Opis:** Analiza geometryczna układu redstone. Sprawdza czy elementy tworzą kwadratową spiralę.

**Metoda:**
1. Grupowanie elementów po poziomach Y
2. Dla każdego poziomu Y:
   - Obliczenie zakresu X i Z
   - Sprawdzenie "warstw" od zewnątrz do środka
   - Analiza czy krawędzie tworzą zamknięte kwadraty
3. Wizualizacja ASCII mapy układu

**Działanie dla kimi1:**
```
Mapa (X→, Z↓):
      0 1 2 3 4 5 6 7 8 9
Z 0:  T R . R > R . . . >
Z 1:  . . . . . R . . . R
Z 2:  . . . . . R . . . R
...

Wniosek: ❌ Brak regularnej struktury spirali
Znaleziono 9 rozłącznych obwodów (nie spiralę)
```

---

### 9. EditMetadata.kt
**Lokalizacja:** `src/main/kotlin/mc/editkit/worker/EditMetadata.kt`

**Opis:** Zarządzanie metadanymi edycji świata. Służy do śledzenia zmian wprowadzonych przez narzędzie.

**Funkcje:**
- Zapis metadanych do `editkit_metadata.json`
- Śledzenie zmodyfikowanych chunków
- Lista oczekiwanych zmian (bloki, Tile Entities)

**Działanie dla kimi1:**
- Nieaktywne - brak pliku `editkit_metadata.json` w folderze mapy
- Mapa nie była edytowana przez ten tool

---

### 10. WorldValidator.kt
**Lokalizacja:** `src/main/kotlin/mc/editkit/worker/WorldValidator.kt`

**Opis:** Walidacja świata - sprawdza czy edycje zostały poprawnie zapisane. Porównuje stan faktyczny z oczekiwanym.

**Użycie:**
- Pre-flight validation przed uruchomieniem serwera
- Sprawdzenie czy bloki są na właściwych pozycjach
- Weryfikacja Tile Entities

**Działanie dla kimi1:**
- Nie używane bezpośrednio do analizy
- Funkcjonalność przeznaczona dla map edytowanych przez tool

---

### 11. ServerLauncher.kt
**Lokalizacja:** `src/main/kotlin/mc/editkit/worker/ServerLauncher.kt`

**Opis:** Uruchamianie serwera Minecraft z opcjonalną pre-flight validation.

**Funkcje:**
- Przygotowanie `server.properties`
- Uruchomienie serwera z walidacją
- Monitorowanie logów (szukanie "Done" lub błędów)

**Działanie dla kimi1:**
- Nie używane w analizie redstone
- Przydatne do testowania map po edycji

---

### 12. WorldEditor.kt
**Lokalizacja:** `src/main/kotlin/mc/editkit/worker/WorldEditor.kt`

**Opis:** Edytor świata Minecraft. Umożliwia odczyt i zapis regionów MCA, modyfikację bloków i Tile Entities.

**Kluczowe funkcje:**
- `setBlock(x, y, z, id, meta)` - ustawienie bloku
- `setTileEntity(x, y, z, nbt)` - ustawienie Tile Entity
- `commit()` - zapis zmian do plików .mca

**Działanie dla kimi1:**
- Używany pośrednio przez inne klasy do odczytu NBT
- Tryb tylko-do-odczytu w analizie (brak modyfikacji)

---

## Biblioteki zewnętrzne

### Hephaistos 2.2.0
```gradle
implementation("io.github.jglrxavpok.hephaistos:common:2.2.0")
```

**Opis:** Biblioteka do parsowania formatu NBT (Named Binary Tag) i regionów MCA (Minecraft Anvil format).

**Używane klasy:**
- `RegionFile` - obsługa plików .mca
- `NBTCompound` - struktura danych NBT
- `NBTList` - lista tagów NBT
- `NBTReader/NBTWriter` - odczyt/zapis NBT

**Kompatybilność:**
- Minecraft 1.7.10 (format bez DataVersion)
- Wymaga bezpośredniej manipulacji na NBT (nie przez ChunkColumn)

---

## Wyniki analizy dla kimi1

### Podsumowanie wszystkich metod

| Plik/Metoda | Zakres | Znalezione redstone | Szczegóły |
|-------------|--------|---------------------|-----------|
| RedstoneAnalyzer | Chunki -2..2 | 36 elementów | Tylko (0,0), Y=4 |
| ChunkInspector | 4 chunki | 36 elementów | (0,0)=36, reszta=puste/brak |
| ExtendedInspector | 25 chunków | 36 elementów | 1/25 chunków |
| FullAreaScan | 100 chunków | 36 elementów | Zakres -80..80 bloków |
| CorrectAnalysis | 9 chunków, wszystkie Y | 36 elementów | Tylko Y=4 |
| WideAreaAnalysis | Wszystkie regiony | 37 elementów | (0,0)=36, (0,10)=1 |
| SpiralPatternDetector | Geometria | - | NIE spiral - 9 obwodów |

### Rozbieżność ze zrzutami ekranu

**Problem:** Zrzuty ekranu pokazują dużą kwadratową spiralę redstone na poziomie Y=9-10 rozciągającą się na wiele chunków.

**Analiza plików:**
- Data zrzutów: 2026-01-31 19:44:39
- Data regionów: 2026-01-31 19:46:58 (późniejsza)
- Redstone mógł zostać usunięty lub zmieniony między zrzutami a kopią

**Możliwe wyjaśnienia:**
1. Zrzuty pochodzą z innej wersji mapy
2. Redstone został usunięty przed skopiowaniem do `kimi1_new_copy`
3. Mapa była modyfikowana po wykonaniu zrzutów

---

## Autor
Projekt: MC EditKit Worker  
Data utworzenia dokumentacji: 2026-01-31
