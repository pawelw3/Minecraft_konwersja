# Instrukcja: wydajny i poprawny „cleaner” świata Minecraft 1.7.10 (Anvil .mca) w Kotlin/Java

Poniższa specyfikacja opisuje, jak napisać od zera **wydajny i poprawny program czyszczący świat Minecraft 1.7.10** z treści modowej (bloki/TileEntities/Entities), **bez psucia NBT**. Możesz użyć istniejącego kodu jako biblioteki I/O (np. odczyt/zapis chunków), ale kluczowe jest dopisanie pełnej obsługi `Add` (high bits ID) i poprawnego czyszczenia TE/Entities.

---

## 0) Wymagania poprawności (must-have)

1. **Round-trip NBT bez strat**  
   Nie implementuj „placeholderowego” parsera/serializera NBT. Użyj biblioteki NBT, która zachowuje wszystkie tagi (np. Hephaistos lub inna sprawdzona implementacja).

2. **Pełne ID bloku 0..4095 w 1.7.10**  
   W chunkach 1.7.10 bloki są kodowane jako:
   - `Blocks` (4096 bajtów) = **low 8 bitów**
   - opcjonalnie `Add` (2048 bajtów nibble array) = **high 4 bity**
   - `Data` (2048 nibble) = metadata

3. **Cleaner musi usuwać to, co najczęściej powoduje crashe po usunięciu modów**:
   - `TileEntities` (maszyny, przewody itd.)
   - `Entities` (modowe moby/obiekty)
   - wszystkie wymiary: `region/`, `DIM-1/region`, `DIM1/region`, `DIM*/region`

4. **Bezpieczny zapis `.mca`**
   - zapisuj tylko zmodyfikowane chunki,
   - region otwieraj raz na czas przetwarzania,
   - aktualizuj nagłówek offsetów (i najlepiej timestampy).

---

## 1) Architektura programu (proponowany podział)

### Moduł A: Region/Chunk I/O
- `RegionIO`:
  - `readChunkNBT(raf, localChunkX, localChunkZ): NBTCompound?`
  - `writeChunkDirect(raf, localChunkX, localChunkZ, nbt)`

**Wskazówka:** Trzymaj `RandomAccessFile` otwarty dla jednego `.mca` i zamknij po przetworzeniu regionu.

### Moduł B: Block Access (obsługa `Add`)
Utility do:
- odczytu pełnego ID (`Blocks + Add`)
- ustawiania pełnego ID i metadata (aktualizacja `Blocks`, `Add`, `Data`)

### Moduł C: “Cleaner rules” (reguły co jest modowe)
Reguły w pliku konfiguracyjnym (JSON/YAML), np.:
- `removeBlockIds` (lista/range pełnych ID do usunięcia)
- `keepBlockIds` (whitelist)
- `removeTileEntityIds` (blacklist / prefiksy)
- `removeEntityIds` (blacklist / prefiksy)
- `replacementBlock` (np. `air=0` lub `stone=1`)

**Domyślna heurystyka (praktyczna dla 1.7.10):**
- modowy blok: `fullId >= 256`
- modowe TE/Entity: `id` spoza whitelist vanilla lub pasujące do blacklist prefiksów

### Moduł D: `ChunkCleaner`
Funkcja:
- wejście: `NBTCompound root`
- wyjście: `(modified: Boolean, cleanedRoot: NBTCompound, stats)`

Kroki:
1. `Level -> Sections`: iteracja po sekcjach
2. czyszczenie bloków + metadata
3. czyszczenie `TileEntities`
4. czyszczenie `Entities` (opcjonalnie)
5. zwrócenie NBT z zachowaniem reszty tagów

### Moduł E: CLI + raport
Parametry:
- `--world <path>`
- `--dims all|overworld|nether|end|DIM*`
- `--dry-run`
- `--threads N`
- `--rules rules.json`
- `--backup`
- raport: liczba chunków, bloków, TE, Entities.

---

## 2) Poprawna obsługa `Blocks/Add/Data` (rdzeń)

### Mapowanie indeksu w sekcji
Dla sekcji 16×16×16 (Minecraft 1.7.10):
```
index = (y * 16 + z) * 16 + x
```

- `Blocks[index]` = low byte
- `Add` = nibble array: `high = nibble(Add, index)`
- `Data` = nibble array: `meta = nibble(Data, index)`

### Minimalne helpery (Kotlin/pseudokod)

```kotlin
fun getNibble(a: ByteArray, index: Int): Int {
  val i = index shr 1
  val b = a[i].toInt() and 0xFF
  return if ((index and 1) == 0) (b and 0x0F) else ((b shr 4) and 0x0F)
}

fun setNibble(a: ByteArray, index: Int, value: Int) {
  val i = index shr 1
  val b = a[i].toInt() and 0xFF
  val v = value and 0x0F
  val out = if ((index and 1) == 0) ((b and 0xF0) or v)
            else ((b and 0x0F) or (v shl 4))
  a[i] = out.toByte()
}

fun readFullId(blocks: ByteArray, add: ByteArray?, index: Int): Int {
  val low = blocks[index].toInt() and 0xFF
  val high = if (add == null) 0 else getNibble(add, index)
  return low or (high shl 8)
}

fun writeFullId(blocks: ByteArray, add: ByteArray?, index: Int, fullId: Int): ByteArray? {
  blocks[index] = (fullId and 0xFF).toByte()
  val high = (fullId ushr 8) and 0x0F

  if (high == 0) {
    if (add != null) setNibble(add, index, 0)
    return add
  }

  val ensured = add ?: ByteArray(2048)
  setNibble(ensured, index, high)
  return ensured
}
```

**Ważne:** Gdy zamieniasz blok na `air`/vanilla `<256`:
- wyzeruj odpowiadający nibble w `Add`,
- zwykle ustaw `Data` (meta) na `0`, żeby nie zostawiać „resztek”.

---

## 3) Czyszczenie `TileEntities` (kluczowe)

### Dlaczego?
Po usunięciu modów świat często crashuje przez `TileEntities` o nieistniejących klasach/ID. Sama podmiana bloków to za mało.

### Dwie strategie (zalecane razem)

**Strategia 1: usuń TE na pozycjach, gdzie zmieniłeś blok**
- podczas czyszczenia bloków zbierasz set pozycji (x,y,z),
- filtrujesz `Level.TileEntities`, usuwając TE z tych pozycji.

**Strategia 2: usuń TE o modowym `id`**
- jeśli `te.getString("id")` nie jest vanilla (lub pasuje do blacklist), usuń.

Whitelist vanilla trzymaj w `rules.json`, bo różne środowiska (serwery/modpacki) mają różnice.

---

## 4) Czyszczenie `Entities`

Encje są w `Level.Entities` (lista compoundów).
Możesz:
- usuwać encje o `id` spoza whitelist vanilla,
- opcjonalnie usuwać „Item” niosące modowe przedmioty (zależnie od tego jak masz kodowane itemy w NBT 1.7.10).

---

## 5) Zakres świata: wszystkie wymiary i foldery

Cleaner powinien automatycznie znaleźć:
- `<world>/region/*.mca`
- `<world>/DIM-1/region/*.mca`
- `<world>/DIM1/region/*.mca`
- `<world>/DIM*/region/*.mca` (inne wymiary modowe)

Implementacja:
- przejście po katalogach świata,
- jeśli podkatalog pasuje do `DIM-?\d+` i ma `region/`, dodaj do kolejki.

---

## 6) Wydajność (na duże światy)

1. **Przetwarzaj per region**: jeden `.mca` na raz, jeden wątek na plik.
2. **Nie serializuj chunków bez zmian**:
   - najpierw skan sekcji (czy istnieją modowe ID),
   - jeśli brak zmian → pomiń zapis.
3. **Równoległość**:
   - równolegle po regionach (`FixedThreadPool`),
   - nie dziel jednego `.mca` na wiele wątków (unikniesz synchronizacji).
4. **Zarządzanie sektorami** (opcjonalnie „pro”):
   - proste dopisywanie chunków działa, ale może „puchnąć” plik,
   - wersja pro: bitmapa zajętych sektorów i ponowne użycie wolnych.

---

## 7) Integracja z istniejącym kodem (co zwykle trzeba poprawić)

- Jeśli masz funkcje typu `setBlock(...)` oparte wyłącznie o `Blocks` i `Data`, **musisz dopisać obsługę `Add`**.
- Walidatory typu `readBlockAt(...)` też powinny składać pełne ID z `Blocks + Add`.
- Najlepiej wydziel wspólny `BlockCodec` i używaj go w edytorze/validatorze/cleanerze.

---

## 8) Tryby działania (praktyczne w użyciu)

- `dry-run`: tylko statystyki
- `clean`: zapis + backup
- `report`: JSON raport (per region/chunk: bloki/TE/Entities)
- poziomy agresywności:
  - `--blocks-only`
  - `--blocks-and-te`
  - `--full` (bloki + TE + entities + item cleanup)

---

## 9) Testy przed użyciem na prawdziwym świecie

1. Świat testowy:
   - postaw modowe bloki o ID **>255** (żeby sprawdzić `Add`),
   - postaw modowe `TileEntities`,
   - przywołaj modowe `Entities`.

2. Uruchom:
   - `dry-run` i sprawdź wykrywanie,
   - `clean` i sprawdź NBT (np. NBTExplorer):
     - `Add` wyzerowane tam gdzie trzeba,
     - TE usunięte,
     - chunk zachował pozostałe tagi (HeightMap/Biomes/itd.).

3. Odpal świat bez modów:
   - sprawdź logi crashy.

4. (Opcjonalnie) walidacja:
   - rozbuduj validator, by raportował pozostałe modowe TE/Entities.

---

## 10) Minimalny plan implementacji (krok po kroku)

1. `rules.json` + loader reguł.
2. `BlockCodec` (nibble + fullId + meta).
3. `ChunkCleaner.cleanChunk(nbt, rules)`:
   - iteracja po sections i modyfikacja arrays,
   - zbieranie zmienionych pozycji,
   - filtrowanie `TileEntities` i `Entities`,
   - zwrot `(modified, stats)`.
4. `WorldScanner`:
   - znajdź wszystkie `region/` w wymiarach,
   - dla każdego `.mca`: iteruj 32×32 chunków, czytaj → czyść → jeśli modified → zapisz.
5. CLI + log + backup.
6. Popraw walidator pod `Add` (jeśli go używasz).

---
