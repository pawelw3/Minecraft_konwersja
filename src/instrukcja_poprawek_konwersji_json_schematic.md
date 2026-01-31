# Instrukcja poprawek: konwersja `voxel_grid.json` → `.schematic` (MC 1.7.10) + wstawianie do świata

Ta instrukcja dotyczy plików:
- `json_to_schematic.py`
- `nbt_writer.py`
- `schematic_to_world.py`
oraz wygenerowanego pliku `digital_counter.schematic`.

Cel: żeby `.schematic` był **poprawny dla Minecraft Java 1.7.10**, a narzędzie do wstawiania nie psuło regionów.

---

## 1) Konwerter `json_to_schematic.py` – poprawki krytyczne

### 1.1 Redstone torch: ID 75 vs 76 (unlit/lit)
W mapowaniu masz:
- `minecraft:redstone_torch` → (75, 0)
- `minecraft:redstone_torch_lit` → (76, 0)

W praktyce w świecie używasz „zwykłego torcha redstone”, który powinien być **lit** w spoczynku.
W 1.7.10 blok ID:
- 75 = unlit redstone torch
- 76 = lit redstone torch

✅ **Poprawka:**
Zmień mapowanie na:
- `minecraft:redstone_torch` → **(76, 0)**  
A jeśli chcesz wspierać unlit, to używaj w JSON osobnej nazwy (np. `minecraft:redstone_torch_unlit` → 75).

**Dlaczego:** inaczej zegar/układ startuje z błędnym stanem.

---

### 1.2 Metadane kierunku: rozdziel mapowania dla różnych bloków
Aktualnie `get_direction_meta()` używa tabeli repeater/comparator także dla dropper/command_block.
To jest niepoprawne dla 1.7.10.

#### 1.2.1 Prawidłowe metadane (1.7.10)
- Repeater/Comparator:  
  `south=0, west=1, north=2, east=3`  ✅ (twoja obecna tabela pasuje dla nich)

- Dropper/Dispenser (i zwykle command block, jeśli używasz direction meta):  
  `down=0, up=1, north=2, south=3, west=4, east=5`  ✅

✅ **Poprawka:**
W `get_direction_meta()` dodaj rozgałęzienie po typie bloku:

- jeśli `block_name in {"minecraft:repeater","minecraft:comparator"}` → użyj mapy 0..3
- jeśli `block_name in {"minecraft:dropper","minecraft:dispenser"}` → użyj mapy 0..5
- jeśli `block_name == "minecraft:command_block"` → sprawdź docelową wersję: w wielu wersjach command block też używa 0..5; dopasuj do świata docelowego i przetestuj.

**Dlaczego:** ring counter na dropperach przestanie „pchać item” w złe strony.

---

### 1.3 Lever: nie ustawiaj powered zawsze
Obecnie dla levera dodajesz bit `0x8` bezwarunkowo (czyli zawsze powered).

✅ **Poprawka:**
Ustaw `powered_bit = 0x8` tylko jeśli `properties.powered == true` (albo równoważne pole w JSON).

**Dlaczego:** master switch ma odpowiadać stanowi w JSON.

---

### 1.4 Unknown block ≠ stone: tryb strict
Obecnie nieznany blok mapujesz na stone:
`BLOCK_ID_MAP.get(name, (1,0))`

To maskuje błędy: konwersja „przechodzi”, ale układ jest popsuty.

✅ **Poprawka (zalecane):**
- Dodaj tryb strict (domyślnie ON): jeśli block nie istnieje w mapie → rzuć wyjątek i wypisz listę brakujących bloków.
- Ewentualnie tryb permissive jako opcja CLI.

**Dlaczego:** w przeciwnym razie będziesz debugował „kamienie znikąd”.

---

## 2) Tile Entities: NBT dla 1.7.10 (itemy, command blocki)

### 2.1 ItemStack w 1.7.10: `id` jako SHORT (numeryczne), nie string
W dropperze zapisujesz `Items[].id` jako TAG_STRING typu `"minecraft:cobblestone"`.
W 1.7.10 to zazwyczaj musi być:
- `id` (TAG_SHORT) = numeryczne ID itemu (np. cobblestone=4)
- `Damage` (TAG_SHORT)
- `Count` (TAG_BYTE)
- `Slot` (TAG_BYTE)

✅ **Poprawka:**
Dodaj mapę nazw→ID dla 1.7.10 (minimum potrzebne):
- `minecraft:cobblestone` → 4
- (plus inne, jeśli używasz)
i zapisuj `id` jako TAG_SHORT.

**Alternatywa:** wymuś w JSON, że itemy są podane jako liczba `id: 4` zamiast `minecraft:cobblestone`.

**Dlaczego:** inaczej dropper będzie pusty po wklejeniu.

---

### 2.2 Command block tile entity: upewnij się, że zapisujesz właściwe pola
Dla 1.7.10 command block TE zwykle potrzebuje:
- `id: "Control"` (TAG_STRING)
- `Command: "..."` (TAG_STRING)
- `x,y,z` (TAG_INT)

✅ **Poprawka:**
Zweryfikuj w grze/źródłach, że twoje pola zgadzają się z 1.7.10.
Jeśli używasz `auto`/`conditional`/`powered` pól z nowszych wersji – usuń je dla 1.7.10.

**Dlaczego:** inaczej command blocki mogą się w ogóle nie zachować jak trzeba.

---

### 2.3 NBT Writer: typy tagów muszą być zgodne
Upewnij się, że `nbt_writer.py`:
- poprawnie pisze TAG_Byte/TAG_Short/TAG_Int/TAG_String,
- poprawnie enkoduje listy tagów (TAG_List) z typem elementów.

✅ **Test:**
Zrób test odczytu NBT w Pythonie (np. `nbtlib`) lub przez narzędzie MCEdit/WorldEdit:
- odczytaj `TileEntities` i sprawdź typ `Items[].id` (musi być short).

---

## 3) `.schematic`: weryfikacja poprawności po konwersji

Dodaj automatyczny test/komendę, która:
1) otwiera `.schematic` jako NBT,
2) sprawdza:
   - root == `Schematic`
   - `Blocks` i `Data` mają długość `Width*Height*Length`
   - że konkretne współrzędne mają oczekiwane ID/meta (np. D0, torch, comparator)
3) sprawdza `TileEntities`:
   - liczba TE odpowiada (10 dropper + 10 command block albo tyle, ile masz)
   - dropper D0 ma `Items` z `id` jako short

✅ **Minimalny zestaw asercji** (dla twojego licznika):
- redstone torch = 76
- dropper D0 facing east = meta 5
- co najmniej 10 command block TE z `id="Control"`

---

## 4) `schematic_to_world.py`: poprawki krytyczne (podwójna kompresja chunków)

### 4.1 Nie kompresuj istniejących chunków drugi raz
W `_load_existing()` wczytujesz payload chunka już skompresowany.
Potem w `save()` robisz `zlib.compress(chunk_data)` ponownie.

✅ **Poprawka (zalecana):**
- Przy odczycie: zdekompresuj do surowych bytes NBT i przechowuj zdekompresowane.
- Przy zapisie: kompresuj **raz**.
- Zachowuj typ kompresji zapisany w regionie (zwykle 2 = zlib).

**Dlaczego:** podwójna kompresja może uszkodzić region i stare chunki.

---

### 4.2 Uwaga na format regionów/level.dat
Upewnij się, że edytujesz właściwy plik regionu (`r.x.z.mca`) dla wersji świata.
1.7.10 używa formatu anvil (`.mca`), ale ważne są offsety i nagłówki.

✅ **Test:**
- zanim zapiszesz, zrób backup regionu,
- po zapisie sprawdź, czy świat otwiera się bez „corrupted chunk”.

---

## 5) Zalecany plan wdrożenia poprawek (kolejność)

1) Napraw `BLOCK_ID_MAP` (torch lit, strict unknown blocks).
2) Rozdziel `get_direction_meta()` według rodzaju bloku.
3) Napraw lever powered bit.
4) Napraw NBT itemów w dropperze (short ID).
5) Zweryfikuj command block TE dla 1.7.10 (id/Command/x/y/z).
6) Dodaj test odczytu `.schematic` i asercje.
7) Napraw `schematic_to_world.py` (uniknij podwójnej kompresji).
8) Wygeneruj nowy `.schematic` i porównaj go z poprzednim.

---

## 6) Definition of Done

Uznajemy, że konwersja jest poprawna, jeśli:

- `.schematic` otwiera się w MCEdit/WorldEdit bez błędów,
- w świecie (1.7.10) droppery są skierowane poprawnie i item startowy jest obecny,
- zegar startuje (torch jest lit) i bus zasila droppery,
- command blocki mają poprawne komendy i reagują na sygnał,
- narzędzie `schematic_to_world.py` nie psuje istniejących regionów (brak podwójnej kompresji).

