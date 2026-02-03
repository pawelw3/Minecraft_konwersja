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

#### KRYTYCZNE: Wyciąganie DOKŁADNYCH nazw rejestracji z kodu źródłowego

**Nazwy rejestracji tile entities są KLUCZOWE** dla późniejszego wyszukiwania bloków na mapie świata. Mody mogą rejestrować tile entities na różne sposoby:

##### Wzorce rejestracji w 1.7.10:
```java
// Wzorzec 1: Z prefiksem moda (standardowy)
GameRegistry.registerTileEntity(TileEnderChest.class, "EnderStorage:enderChest");

// Wzorzec 2: BEZ prefiksu moda (UWAGA - łatwo przeoczyć!)
GameRegistry.registerTileEntity(TileEntityWoodBlocks.class, "TileEntityWoodBlocks");

// Wzorzec 3: Z kropką zamiast dwukropka
GameRegistry.registerTileEntity(TileChest.class, "betterstorage.reinforcedChest");

// Wzorzec 4: Z spacją w nazwie
GameRegistry.registerTileEntity(TileEnderChest.class, "Ender Chest");
```

##### Wzorce rejestracji w 1.18.2:
```java
// Wzorzec 1: DeferredRegister (standardowy)
public static final RegistryObject<BlockEntityType<MyTileEntity>> MY_TILE =
    BLOCK_ENTITIES.register("my_tile", () -> BlockEntityType.Builder.of(...));

// Wzorzec 2: ResourceLocation
new ResourceLocation("modid", "tile_name");
```

##### Jak znaleźć wszystkie nazwy rejestracji:
1. **Grep po `registerTileEntity`** - znajdź WSZYSTKIE wywołania, nie tylko te z prefiksem moda
2. **Grep po `GameRegistry.register`** - dla bloków i itemów
3. **Sprawdź pliki typu `ModTileEntities.java`, `ModBlocks.java`, `init/`** - często zawierają scentralizowaną rejestrację
4. **Szukaj stringów w cudzysłowach** obok nazw klas TileEntity
5. **UWAGA**: Niektóre mody (np. Jammy Furniture, EnderStorage) rejestrują tile entities **bez prefiksu moda** - te są łatwe do przeoczenia!

##### Lista kontrolna nazw do wyciągnięcia:
Dla każdego elementu moda wyciągnij i zapisz:
- [ ] **Registry name bloku** (np. `"modid:block_name"` lub `"modid.block_name"`)
- [ ] **Registry name tile entity** (może być INNY niż bloku! np. `"TileEntityWoodBlocks"` bez prefiksu)
- [ ] **Registry name itemu** (jeśli różny od bloku)
- [ ] **Alternatywne nazwy** (stare nazwy dla kompatybilności wstecznej)

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
- Sprawdź, czy lista bloków obejmuje wszystko co jest rejestrowane (nie tylko to co ma "łatwy" prefix / pasuje do grepa).
- Oddziel elementy moda od elementów vanilla i zależności (dependency).
- Nie myl:
  - block vs itemblock,
  - TileEntity (1.7.10) vs BlockEntity (1.18.2).

#### KRYTYCZNA walidacja kompletności nazw rejestracji:

**Przed zakończeniem analizy MUSISZ zweryfikować:**

1. **Zlicz wszystkie wywołania rejestracji:**
   ```bash
   # Dla 1.7.10 - policz WSZYSTKIE registerTileEntity
   grep -r "registerTileEntity" --include="*.java" | wc -l

   # Porównaj z liczbą elementów na Twojej liście
   ```

2. **Sprawdź czy nie pominąłeś tile entities bez prefiksu:**
   - Przeszukaj kod pod kątem stringów w cudzysłowach przy `registerTileEntity`
   - UWAGA na wzorce jak `"TileEntity..."` bez `"modid:"`

3. **Zweryfikuj nazwy z wieloma formatami:**
   - Niektóre mody używają `:` (np. `"modid:name"`)
   - Niektóre używają `.` (np. `"modid.name"`)
   - Niektóre nie używają prefiksu w ogóle (np. `"TileEntityWoodBlocks"`)
   - Niektóre mają spacje (np. `"Ender Chest"`)

4. **Cross-check z plikami zasobów:**
   - `assets/modid/lang/*.lang` - nazwy wyświetlane
   - `assets/modid/blockstates/` - lista bloków
   - `assets/modid/models/block/` - modele bloków

5. **Finalna lista MUSI zawierać dla każdego elementu:**
   - Klasę Java (np. `TileEntityWoodBlocks.class`)
   - DOKŁADNY string rejestracji (np. `"TileEntityWoodBlocks"` lub `"modid:name"`)
   - Informację czy ma prefiks moda czy nie

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
- **Registry names (OBOWIĄZKOWE):**
  - Block registry: `"modid:block_name"` lub `"modid.block_name"`
  - TileEntity registry: `"dokładny_string_z_kodu"` (np. `"TileEntityWoodBlocks"` lub `"Ender Chest"`)
  - Item registry: `"modid:item_name"` (jeśli różny od bloku)
  - **Ma prefiks moda:** TAK / NIE (WAŻNE dla wyszukiwania na mapie!)
- **Klasa Java:** `com.example.mod.TileEntityExample`
- **Opis działania:** 3–8 zdań, konkretnie (co robi, jak działa, najważniejsze interakcje)
- **Dowody z internetu:**
  - Źródło: <link> — <1–2 zdania parafrazy co potwierdza>
- **Dowód z kodu (rejestracja):**
  - Plik: `<ścieżka do pliku rejestracji>` (np. `ModTileEntities.java`)
  - Snippet pokazujący DOKŁADNĄ rejestrację:
    ```java
    GameRegistry.registerTileEntity(TileEntityExample.class, "dokładny_string");
    ```
- **Dowód z kodu (logika):**
  - Plik: `<ścieżka>` (source lub dekompilacja)
  - Snippet:
    ```java
    // 5–15 linii kluczowego fragmentu
    ```

## Dlaczego DOKŁADNE nazwy rejestracji są KRYTYCZNE

Nazwy rejestracji są używane do **wyszukiwania bloków na mapie świata Minecraft**. W plikach regionów (.mca) tile entities są zapisane z ich **dokładnymi nazwami rejestracji** jako stringi binarne.

**Przykład problemu:**
- Szukasz na mapie bloków moda "Jammy Furniture"
- Próbujesz szukać `"jammyfurniture:"` - NIE ZNAJDUJESZ NIC
- Okazuje się, że mod rejestruje tile entities jako `"TileEntityWoodBlocks"` BEZ prefiksu
- Dopiero szukanie `"TileEntityWoodBlocks"` znajduje bloki na mapie

**Tabela podsumowująca nazwy (OBOWIĄZKOWA na końcu raportu):**

| Element | Klasa Java | Registry String | Ma prefiks? |
|---------|-----------|-----------------|-------------|
| Wood Table | TileEntityWoodBlocksOne | `"TileEntityWoodBlocks"` | NIE |
| Ender Chest | TileEnderChest | `"Ender Chest"` | NIE (spacja!) |
| Reinforced Chest | TileReinforcedChest | `"betterstorage.reinforcedChest"` | TAK (z kropką) |
| Blood Altar | TileAltar | `"AWWayofTime:AlchemicalWizardrybloodAltar"` | TAK (dwukropek) |

## Kryteria "DONE"
- Są kompletne listy bloków i TE/BE dla **obu** wersji (1.7.10 i 1.18.2).
- Każdy element ma: **opis + min. 1 źródło z internetu + min. 1 snippet kodu**.
- Każdy element ma **DOKŁADNY string rejestracji** wyciągnięty z kodu źródłowego.
- Jest **tabela podsumowująca** wszystkie registry names z informacją o prefiksach.
- Jest czytelne porównanie różnic między wersjami.