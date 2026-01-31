# Instrukcja poprawek: błędne mapowanie chunk→region dla wartości ujemnych (powód “redstone tylko w (0,0)”)

## 1) Problem (co jest zepsute)
Analiza chunków z ujemnym `chunkX`/`chunkZ` (np. `0,-1`, `-1,0`, `-1,-1`) trafia do **złego pliku regionu** (`r.0.0.mca` zamiast `r.-1.*.mca`).  
Efekt: narzędzia widzą redstone tylko w chunku `(0,0)` mimo że fizycznie jest też w sąsiednich chunkach ujemnych.

### Przyczyna
W kodzie było wyrażenie w stylu:
- `... (chunkX + 1) shr 5 - 1 ...`

W Kotlinie/Java `shr` (funkcja/infix) + priorytety operatorów powodują, że to bywa parsowane niezgodnie z intencją (praktycznie: robi się przesunięcie o **(5-1)=4** zamiast “(>>5) potem -1”).  
To **psuje floor-division** dla liczb ujemnych.

---

## 2) Wymagane rozwiązanie (najbezpieczniejsze)
Zamiast ręcznych wzorów, użyj **jednego** zestawu funkcji opartych o `Math.floorDiv` i `Math.floorMod`.

Wprowadź plik util (np. `Coords.kt`):

```kotlin
import java.lang.Math

fun regionCoordFromChunk(c: Int): Int = Math.floorDiv(c, 32)
fun localChunkFromChunk(c: Int): Int = Math.floorMod(c, 32)

fun chunkCoordFromBlock(b: Int): Int = Math.floorDiv(b, 16)
fun localBlockFromWorld(b: Int): Int = Math.floorMod(b, 16)
```

### Jak to stosować
Zawsze licz tak:

```kotlin
val chunkX = chunkCoordFromBlock(worldX)
val chunkZ = chunkCoordFromBlock(worldZ)

val regionX = regionCoordFromChunk(chunkX)
val regionZ = regionCoordFromChunk(chunkZ)

val localChunkX = localChunkFromChunk(chunkX)
val localChunkZ = localChunkFromChunk(chunkZ)

val lx = localBlockFromWorld(worldX)
val lz = localBlockFromWorld(worldZ)
```

> To jest odporne na wartości ujemne i eliminuje całą klasę błędów “0 zamiast -1”.

---

## 3) Alternatywa dopuszczalna (minimalny patch)
Jeśli **nie chcesz** zmieniać na `floorDiv/floorMod` w tej iteracji, absolutne minimum to dodanie nawiasów:

```kotlin
val regionX = if (chunkX >= 0) chunkX shr 5 else ((chunkX + 1) shr 5) - 1
val regionZ = if (chunkZ >= 0) chunkZ shr 5 else ((chunkZ + 1) shr 5) - 1
```

⚠️ Ale nadal: preferowane jest rozwiązanie z `floorDiv/floorMod`, bo usuwa duplikację i ryzyko podobnych bugów w innych miejscach.

---

## 4) Gdzie poprawić (w całym projekcie)
Masz duplikację obliczeń `regionX/regionZ/localChunkX/localChunkZ` w wielu plikach.  
**Wszystkie miejsca muszą korzystać z jednej utilki**.

### Zasada refaktoru:
1) **Znajdź wszystkie** wystąpienia liczenia regionu/chunka (frazy typu: `shr 5`, `and 31`, `chunkX + 1`, `regionX = if (chunkX >= 0) ...`).
2) Zastąp je wywołaniem:
   - `regionCoordFromChunk(...)`
   - `localChunkFromChunk(...)`
3) Usuń lokalne kopie helperów (np. `getRegionX()` w data class), żeby nie było dwóch różnych implementacji.

---

## 5) Testy obowiązkowe (żeby to nigdy nie wróciło)

### 5.1 Unit test mapowania chunk→region
Dodaj test, który sprawdza dokładnie te wartości:

| chunk (cx,cz) | region (rx,rz) | local (lcx,lcz) |
|---|---|---|
| (0,0) | (0,0) | (0,0) |
| (0,-1) | (0,-1) | (0,31) |
| (-1,0) | (-1,0) | (31,0) |
| (-1,-1) | (-1,-1) | (31,31) |
| (31,31) | (0,0) | (31,31) |
| (32,0) | (1,0) | (0,0) |
| (-32,0) | (-1,0) | (0,0) |
| (-33,0) | (-2,0) | (31,0) |

### 5.2 Smoke test inspektora
Uruchom inspekcję na mapie z ręcznie zrobioną spiralą i wypisz:
- jaki `region/r.x.z.mca` został otwarty dla chunków:
  - (0,0), (0,-1), (-1,0), (-1,-1)
- jakie `localChunkX/Z` zostały użyte.

**PASS**: dla (-1,0) musi być `regionX=-1`, a nie 0.

---

## 6) Kryterium zakończenia (Definition of Done)
Zmiana jest uznana za poprawną dopiero gdy:
1) Inspektor wykrywa redstone w chunkach:
   - (0,0), (0,-1), (-1,0), (-1,-1) — zgodnie z mapą.
2) Unit test mapowania przechodzi.
3) W logach diagnostycznych widać, że dla chunków ujemnych otwierane są regiony `r.-1.*.mca`.

---
