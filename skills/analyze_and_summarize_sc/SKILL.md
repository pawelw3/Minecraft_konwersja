---
name: analyze_and_summarize_sc
description: Wypisuje wszystkie bloki oraz tile entities / block entities dodawane przez mod, opisuje ich działanie na podstawie źródeł z internetu + snippetów kodu z mod_src lub dekompilacji. ZAWSZE analizuje kolejno: 1.7.10 → 1.18.2 → porównanie różnic.
argument-hint: "[ścieżka-do-folderu-mod_src]"
disable-model-invocation: true
allowed-tools: Read, Grep, Bash
---

## Cel
Zidentyfikować **wszystkie bloki** oraz **wszystkie tile entities / block entities** dodawane przez mod, a następnie opisać **co robią** wraz z dowodami:
- **źródła z internetu** (link + krótka parafraza),
- **snippety kodu** (z `mod_src` albo z dekompilacji, zależnie od tego co jest dostępne w `mod_src`).

## Krytyczna zasada kolejności (NIE ŁAMAĆ)
Masz obowiązek wykonać analizę **zawsze** w tej kolejności:
1) **Minecraft 1.7.10** (mod w wersji 1.7.10)  
2) **Minecraft 1.18.2** (mod w wersji 1.18.2)  
3) **Porównanie 1.7.10 vs 1.18.2** (różnice)

> Nie wolno pominąć żadnej wersji nawet jeśli tylko jedna ma łatwo dostępny kod źródłowy lub szybciej “znajduje się” skryptami.

## Wejście
- `$ARGUMENTS` = ścieżka do folderu `mod_src` (zawiera source i/lub jar do dekompilacji).
- Jeśli w `mod_src` są podfoldery per wersja (np. `1.7.10/`, `1.18.2/`) – traktuj je osobno.
- Jeśli jest tylko jeden zestaw plików, ale zawiera oba warianty (np. branched / różne paczki) – nadal rozdziel analizę logicznie na 1.7.10 i 1.18.2.

## Procedura (powtórz osobno dla 1.7.10 i dla 1.18.2)
### 1) Inwentaryzacja lokalna: lista bloków + (tile|block) entities
Zbuduj **pełną listę** elementów dodawanych przez mod, opierając się na kodzie i/lub zasobach:
- Szukaj rejestracji bloków i encji blokowych:
  - **1.7.10**: typowo `GameRegistry.registerBlock(...)`, `GameRegistry.registerTileEntity(...)`, klasy `BlockContainer`, `TileEntity`.
  - **1.18.2**: typowo `DeferredRegister`, `RegistryObject`, `BlockEntityType`, klasy `BlockEntity`.
- Uzupełnij z `assets/` (lang, models, blockstates) i (dla nowszych wersji) `data/` (recipes/loot).
- Jeżeli brakuje źródeł: zdekompiluj jar i wykonaj analogiczne wyszukiwania w dekompilowanym kodzie.

Wynik tego kroku: dwie listy per wersja:
- **Bloki**
- **Tile Entities / Block Entities**

### 2) Zrozumienie działania każdego elementu (dowody obowiązkowe)
Dla **każdego** bloku oraz TE/BE:
- Opisz działanie: co robi, jak się używa, interakcje (GUI, tick, redstone, energia, inventory, NBT, itp.).
- Dołącz dowody:
  1) **Internet**: min. 1–2 źródła (link + krótka parafraza tego co potwierdzają).
  2) **Kod**: min. 1 snippet (kilka–kilkanaście linii), z:
     - pełną ścieżką pliku (w `mod_src` lub w dekompilacji),
     - wskazaniem fragmentu odpowiadającego za zachowanie (np. tick, onUse, save/load, capability/inventory).

Jeśli internet jest skąpy: opis opieraj mocniej o kod i jasno to zaznacz.

### 3) Walidacja kompletności (per wersja)
- Sprawdź, czy lista bloków obejmuje wszystko co jest rejestrowane (nie tylko to co ma “łatwy” prefix / pasuje do grepa).
- Oddziel elementy moda od elementów vanilla i zależności (dependency).
- Nie myl:
  - block vs itemblock,
  - TileEntity (1.7.10) vs BlockEntity (1.18.2).

## Porównanie 1.7.10 vs 1.18.2 (po zakończeniu obu analiz)
Zrób sekcję porównawczą:
- **Wspólne**: elementy o tej samej roli/nazwie/ID (w miarę możliwości dopasuj po registry name lub funkcji).
- **Dodane w 1.18.2** / **usunięte po 1.7.10**.
- **Zmiany zachowania**: logika, parametry, NBT, GUI, tick, redstone, energia, receptury.
- **Zmiany techniczne**: rejestracja (stare API vs DeferredRegister), TileEntity → BlockEntity, zmiany nazw/ID.

## Format wyjścia (wymagany)
Wygeneruj raport w markdown w układzie:

- `## 1.7.10 — Bloki`
- `## 1.7.10 — Tile Entities`
- `## 1.18.2 — Bloki`
- `## 1.18.2 — Block Entities`
- `## Porównanie 1.7.10 vs 1.18.2`

Dla każdego elementu użyj tego szablonu:

### <Nazwa / registry id (jeśli znane)>
- **Typ:** Block / TileEntity / BlockEntity
- **Wersja:** 1.7.10 lub 1.18.2
- **Opis działania:** 3–8 zdań, konkretnie (co robi, jak działa, najważniejsze interakcje)
- **Dowody z internetu:**
  - Źródło: <link> — <1–2 zdania parafrazy co potwierdza>
- **Dowód z kodu:**
  - Plik: `<ścieżka>` (source lub dekompilacja)
  - Snippet:
    ```java
    // 5–15 linii kluczowego fragmentu
    ```

## Kryteria “DONE”
- Są kompletne listy bloków i TE/BE dla **obu** wersji (1.7.10 i 1.18.2).
- Każdy element ma: **opis + min. 1 źródło z internetu + min. 1 snippet kodu**.
- Jest czytelne porównanie różnic między wersjami.