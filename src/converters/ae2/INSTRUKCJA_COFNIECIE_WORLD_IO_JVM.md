# Instrukcja zmiany podejścia: **World IO** ma zostać po stronie JVM/worker (Kotlin + hephAIstos)

Poniższa notatka dotyczy **tylko jednej kwestii**: warstwy „world IO” (czytanie/zapis świata, regionów `.mca`, sekcji/sections, palet, blockstates, BlockEntities).  
W pozostałych aspektach (logika konwersji AE2, mapowania, transformacje NBT, split Interface → Pattern Provider itd.) kierunek prac pozostaje bez zmian.

---

## 1) Najważniejsza decyzja

**Cofamy się** z pomysłu implementowania parsera/zapisu `.mca` po stronie Pythona.

W projekcie jest już **solidna i dojrzała** część JVM/worker napisana w Kotlinie, korzystająca z **hephAIstos**, która odpowiada za:
- odczyt danych chunków/sections w `.mca`,
- zapis danych chunków/sections w `.mca`,
- budowanie palet i packed blockstates dla nowszych wersji,
- obsługę formatu świata, kompresji i wszystkich niuansów zapisu.

To jest właściwe miejsce na World IO. Python nie powinien tej funkcjonalności dublować.

---

## 2) Przeprosiny za zamieszanie (tylko w tej jednej kwestii)

Przepraszam za zamieszanie związane z sugestią dopisywania „world IO” w Pythonie.  
W tej konkretnej sprawie najlepszym rozwiązaniem jest **wykorzystanie istniejącej, sprawdzonej warstwy IO w JVM/worker**, zamiast budowania równoległego IO od zera.

---

## 3) Co dokładnie agent ma zrobić (konkretne kroki)

### 3.1. Wyłączyć / zatrzymać rozwój parsera `.mca` w Pythonie
- Jeśli istnieje moduł typu `block_io.py` próbujący czytać/zapisywać `.mca`, **nie rozwijamy go dalej** jako parsera świata.
- Pozostawienie go jako stub jest OK, ale lepiej:
  - albo go usunąć z pipeline’u,
  - albo zamienić na prosty adapter (patrz niżej).

### 3.2. Zastąpić „World IO w Pythonie” adapterem do JVM/worker
Python ma dostarczać **czystą logikę transformacji**, a Kotlin ma robić I/O.

Docelowy kontrakt (Python jako „transformer”):

**Wejście (z Kotlin/worker → Python)**:
- `block_id_1710` (string lub numeric + informacja pomocnicza),
- `metadata` (0–15),
- `te_nbt` (TileEntity NBT z 1.7.10 w formie JSON/dict),
- `pos` (`x,y,z`) + ewentualnie kontekst chunk/dimension.

**Wyjście (Python → Kotlin/worker)**:
- `block_id_1182` (np. `ae2:drive`),
- `blockstate_props` (np. `{ "facing": "north", "powered": "false" }`),
- `be_nbt` (BlockEntity NBT 1.18.2 jako JSON/dict),
- `extra_blocks` (opcjonalnie lista dodatkowych bloków do postawienia, np. Pattern Provider),
- `warnings/errors` (lista komunikatów diagnostycznych).

> Kotlin/worker bierze `block_id_1182 + blockstate_props` i zapisuje je jako BlockState do chunków.  
> Python nie zapisuje palet/sections.

### 3.3. Usunąć „wymyślone” pola typu `visual`
Skoro orientacja ma trafiać do **blockstate properties**, Python nie powinien doklejać własnych pól typu `visual.rotation`.
- Usuń to ze wszystkich konwerterów.
- Zamiast tego: zwracaj `blockstate_props`.

### 3.4. Dodać tryb batch (wydajność)
Kotlin/worker powinien wysyłać do Pythona dane **batchami** (np. per chunk), a Python zwraca batch wyników.
- Minimalnie: `convert_block(payload)`.
- Docelowo: `convert_batch([payload1, payload2, ...])`.

---

## 4) Kryteria akceptacji tej zmiany

Zmiana jest uznana za wdrożoną, gdy:

1. W kodzie Pythona **nie ma** implementacji czytania/zapisu `.mca` używanej w głównym pipeline.
2. Python zwraca `blockstate_props` zamiast pól typu `visual`.
3. Kotlin/worker jest jedyną warstwą odpowiedzialną za:
   - odczyt danych z `.mca`,
   - zapis `.mca`,
   - generowanie palet i packed states.
4. Jest prosty test integracyjny: Kotlin bierze kilka bloków/TE → Python konwertuje → Kotlin zapisuje wynik do struktury chunk.

---

## 5) Notatka końcowa

Ta decyzja dotyczy **wyłącznie** warstwy World IO.  
Reszta pracy po stronie Pythona (AE2 mapping + transformacje NBT + logika „extra blocks” + ostrzeżenia) pozostaje jak najbardziej potrzebna i powinna być kontynuowana.
