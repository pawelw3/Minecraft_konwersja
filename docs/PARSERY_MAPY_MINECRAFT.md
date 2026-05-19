# Parsery formatu mapy Minecraft 1.7.10

Dokumentacja trzech modułów z `src/minecraft_map_parser/` obsługujących odczyt i zapis
binarnych danych świata Minecrafta w wersji 1.7.10.

---

## Struktura pliku zapisu świata

Zapis świata (katalog `mapa_1710/`) to hierarchia trzech poziomów zagnieżdżenia:
**region → chunk → sekcja**. Każda warstwa ma swój format binarny.

### Poziom 1 — katalog świata

```
mapa_1710/
├── level.dat          ← dane globalne świata (gzip + NBT)
├── region/
│   ├── r.0.0.mca      ← plik regionu (512×512 bloków)
│   ├── r.-1.0.mca
│   └── ...
├── DIM-1/region/      ← Nether
├── DIM1/region/       ← The End
└── ...                ← wymiary z modów (galacticraft, twilight forest, ...)
```

Współrzędna regionu wynika z położenia bloków: region `r.X.Z.mca` pokrywa bloki
`X*512` do `X*512+511` w osi X oraz `Z*512` do `Z*512+511` w osi Z.

Pomocnicza funkcja `get_region_for_block(block_x, block_z)` w `anvil_parser.py`
oblicza to przez `block_x // 512` (floor division, poprawna dla ujemnych koordynat).

### Poziom 2 — plik regionu (.mca, format Anvil)

Plik `.mca` przechowuje do 1024 chunków (32×32) w dwóch sekcjach nagłówkowych
a następnie danych chunków upakowanych w sektorach po 4096 bajtów.

```
Offset 0x0000  [Nagłówek lokalizacji — 4096 bajtów]
               1024 wpisów × 4 bajty:
               ┌─────────────────────────────┬──────────────┐
               │  offset sektora (3 bajty BE) │ liczba sekto-│
               │                             │ rów (1 bajt) │
               └─────────────────────────────┴──────────────┘
               Wpis = (0, 0) → chunk nie istnieje

Offset 0x1000  [Nagłówek timestampów — 4096 bajtów]
               1024 wpisów × 4 bajty: Unix timestamp ostatniej modyfikacji chunka

Offset 0x2000+ [Dane chunków]
               Każdy chunk zaczyna się na granicy sektora (wielokrotność 4096):
               ┌──────────────────┬───────────────┬─────────────────────────┐
               │ długość (4B, BE) │ kompresja (1B)│ skompresowane dane NBT  │
               └──────────────────┴───────────────┴─────────────────────────┘
               Typ kompresji: 1 = gzip, 2 = zlib (zlib dominuje w 1.7.10)
```

Indeks wpisu dla chunka o lokalnych współrzędnych `(cx, cz)` to `cx + cz * 32`.

### Poziom 3 — chunk

Dane chunka po dekompresji to plik NBT z jednym root tagiem `"" (TAG_Compound)`.
Wewnątrz znajduje się klucz `Level` zawierający:

```
Level (TAG_Compound)
├── xPos (TAG_Int)           ← globalna współrzędna chunka X (chunk = 16 bloków)
├── zPos (TAG_Int)           ← globalna współrzędna chunka Z
├── LastUpdate (TAG_Long)    ← tick ostatniej aktualizacji
├── TerrainPopulated (TAG_Byte)
├── Biomes (TAG_Byte_Array)  ← 256 bajtów, jeden na kolumnę 1×1 bloków
├── HeightMap (TAG_Int_Array)← 256 intów, wysokość dla każdej kolumny XZ
│
├── Sections (TAG_List)      ← lista sekcji 16×16×16 (max 16 sekcji, Y 0-255)
│   └── Section (TAG_Compound)
│       ├── Y (TAG_Byte)     ← indeks sekcji 0-15 (Y = Y_sekcji * 16 w blokach)
│       ├── Blocks (TAG_Byte_Array)   ← 4096 B, dolne 8 bitów ID bloku
│       ├── Add (TAG_Byte_Array)      ← 2048 B, górne 4 bity ID (tylko gdy ID > 255)
│       ├── Data (TAG_Byte_Array)     ← 2048 B, metadata (nibble na blok)
│       ├── BlockLight (TAG_Byte_Array)← 2048 B
│       └── SkyLight (TAG_Byte_Array) ← 2048 B
│
├── TileEntities (TAG_List)  ← bloki ze stanem (skrzynie, piece, maszyny modów)
│   └── TileEntity (TAG_Compound)
│       ├── id (TAG_String)  ← identyfikator typu (np. "Chest", "AEDrive")
│       ├── x, y, z (TAG_Int)← absolutne współrzędne bloku w świecie
│       └── ...              ← pola specyficzne dla danego TE
│
└── Entities (TAG_List)      ← encje (moby, przedmioty, pojazdy)
```

#### Kodowanie ID bloków w 1.7.10 (12-bitowe)

W wersji 1.7.10 Minecraft obsługuje bloki o ID od 0 do 4095 (12 bitów).
Tablica `Blocks` przechowuje tylko dolne 8 bitów. Gdy mod używa ID > 255,
dodatkowo istnieje tablica `Add` (lub `AddBlocks`) — nibble array:

```
full_id = (Add[i // 2] >> (4 if i % 2 else 0) & 0x0F) << 8 | Blocks[i]
```

Indeksowanie bloków wewnątrz sekcji: `i = y * 256 + z * 16 + x`
(najpierw Y, potem Z, potem X).

---

## Format NBT

Named Binary Tag to binarny format serializacji Minecrafta. Każdy tag ma:
**typ** (1 bajt), **nazwę** (long prefixed UTF-8 — 2 bajty długości + bajty),
oraz **payload** zależny od typu.

| ID | Nazwa | Rozmiar payloadu |
|----|-------|-----------------|
| 0 | TAG_End | 0 (znacznik końca TAG_Compound) |
| 1 | TAG_Byte | 1 bajt signed |
| 2 | TAG_Short | 2 bajty BE signed |
| 3 | TAG_Int | 4 bajty BE signed |
| 4 | TAG_Long | 8 bajtów BE signed |
| 5 | TAG_Float | 4 bajty BE IEEE 754 |
| 6 | TAG_Double | 8 bajtów BE IEEE 754 |
| 7 | TAG_Byte_Array | INT(długość) + N bajtów |
| 8 | TAG_String | SHORT(długość) + N bajtów UTF-8 |
| 9 | TAG_List | UBYTE(typ elementów) + INT(N) + N × payload |
| 10 | TAG_Compound | ciąg tagów (każdy z typem i nazwą) + TAG_End |
| 11 | TAG_Int_Array | INT(N) + N × INT |
| 12 | TAG_Long_Array | INT(N) + N × LONG |

Wszystkie liczby wielobajtowe są big-endian (BE). Pliki NBT najczęściej są
skompresowane gzipem (magic bytes `\x1f\x8b`) lub zlibem (`\x78\x9c`/`\x78\x01`/`\x78\xda`).

---

## Moduł 1 — `nbt_parser.py`

Parser odczytu danych NBT z bajtów do obiektów Pythona.

### Klasy i funkcje

#### `NBTTag`

Klasa reprezentująca pojedynczy tag NBT. Przechowuje trzy pola:
`type` (int), `name` (str), `value` (Any — typ zależy od `type`).

Mapowanie typów na wartości Pythona:

| Typ tagu | Wartość `value` |
|----------|----------------|
| TAG_Byte / TAG_Short / TAG_Int / TAG_Long | `int` |
| TAG_Float / TAG_Double | `float` |
| TAG_Byte_Array | `bytes` |
| TAG_String | `str` |
| TAG_List | `list` tagów/wartości |
| TAG_Compound | `dict[str, NBTTag]` |
| TAG_Int_Array | `list[int]` |
| TAG_Long_Array | `list[int]` |

Metody dostępu do TAG_Compound:
- `tag.get("klucz", default)` — jak dict.get, zwraca `.value` NBTTag
- `tag["klucz"]` — przez operator `[]`, wyrzuca KeyError jeśli brak
- `"klucz" in tag` — sprawdzenie obecności klucza

#### `NBTParser`

Wewnętrzna klasa parsera strumieniowego. Trzyma `BytesIO` stream i udostępnia
prywatne metody odczytu poszczególnych typów. Metoda publiczna:

```python
parser = NBTParser(raw_bytes)
root_tag = parser.parse()  # → NBTTag (root)
```

`parse()` odczytuje typ root taga, jego nazwę (zazwyczaj pusty string `""`),
a następnie deleguje do `_read_payload()` który rekurencyjnie przetwarza
struktury zagnieżdżone (TAG_Compound wywołuje `_read_compound()`, który
w pętli czyta kolejne tagi aż do TAG_End).

#### Funkcje modułowe

```python
decompress_nbt(data: bytes) → bytes
```
Automatycznie wykrywa typ kompresji po magic bytes i dekompresuje.
Jeśli dane nie są skompresowane — zwraca je bez zmian.

```python
parse_nbt(data: bytes) → NBTTag
```
Główny punkt wejścia: dekompresja + parsowanie w jednym wywołaniu.

### Przykład użycia

```python
from minecraft_map_parser.nbt_parser import parse_nbt

with open("mapa_1710/level.dat", "rb") as f:
    root = parse_nbt(f.read())

data = root["Data"]             # TAG_Compound
last_played = data["LastPlayed"] # int (milisekundy od epoch)
level_name = data["LevelName"]  # str
```

---

## Moduł 2 — `anvil_parser.py`

Parser plików regionów `.mca` zbudowany na `nbt_parser`. Udostępnia chunki
i ich zawartość (bloki, tile entities, encje, biomy).

### Klasy i funkcje

#### `ChunkData`

Dataclass przechowująca sparsowany chunk: `x` i `z` (globalne współrzędne chunka),
oraz `nbt` (root `NBTTag` z całą zawartością).

Metody:

**`get_sections() → list[dict]`**
Wyciąga listę sekcji `Level.Sections`. Każda sekcja to słownik z kluczami
`Y`, `Blocks`, `Add`, `Data`, `BlockLight`, `SkyLight`. Metoda normalizuje
obiekty `NBTTag` do czystych typów Pythona.

**`get_tile_entities() → list[dict]`**
Zwraca `Level.TileEntities` jako listę słowników — każdy to jeden blok
z tile entity. Metoda wywołuje wewnętrznie `_nbt_to_python()` który rekurencyjnie
konwertuje całe drzewo NBT (TAG_Compound → dict, TAG_List → list, pozostałe → wartość).
Wynik jest już gotowy do pracy w konwerterach modów.

**`get_entities() → list[dict]`**
Analogicznie do powyższej, ale dla `Level.Entities` — moby, przedmioty, pojazdy.
Zwraca surowe dict-y bez pełnej konwersji NBT (NBTTag-i mogą zostać w środku).

**`get_biomes() → bytes | None`**
Zwraca 256 bajtów tablicy biomów (`Level.Biomes`). Każdy bajt = ID biomu
dla kolumny bloków 1×1 w układzie XZ.

**`get_block_ids_from_sections() → list[int]`**
Zbiera unikalne ID wszystkich bloków w chunku (łącznie z blokami 12-bitowymi).
Używa tablic `Blocks` i `Add`/`AddBlocks`. Zwraca posortowaną listę unikalnych ID.
Przydatne do szybkiego sprawdzenia jakie bloki z modów są w danym chunku.

**`get_blocks_at_positions() → dict[(x,y,z), int]`**
Pełna mapa pozycja → ID bloku dla całego chunka. Uwzględnia ID 12-bitowe.
Indeksowanie wewnętrzne sekcji: `i = y_in_section * 256 + z * 16 + x`.
Globalna wysokość bloku: `global_y = section_Y * 16 + y_in_section`.

#### `AnvilParser`

Główna klasa parsera. Wczytuje cały plik `.mca` do pamięci przy inicjalizacji,
parsuje nagłówek lokalizacji i udostępnia metody dostępu do chunków.

```python
parser = AnvilParser("mapa_1710/region/r.0.0.mca")
```

**`get_chunk(chunk_x, chunk_z) → ChunkData | None`**
Pobiera chunk po lokalnych współrzędnych (0–31, 0–31). Oblicza indeks w nagłówku
(`cx + cz * 32`), czyta dane z odpowiedniego offsetu sektora, dekompresuje
(gzip lub zlib), parsuje NBT i zwraca `ChunkData`. Zwraca `None` jeśli chunk
nie istnieje (wpis (0,0) w nagłówku).

**`get_all_chunks() → list[ChunkData]`**
Iteruje przez wszystkie 1024 możliwe pozycje i zwraca listę istniejących chunków.

**`get_region_coordinates() → (int, int)`**
Wyciąga współrzędne regionu z nazwy pliku przez regex `r\.(-?\d+)\.(-?\d+)\.mca`.

#### Funkcje pomocnicze modułu

```python
get_region_for_block(block_x, block_z) → (region_x, region_z)
# blok 800, -300 → region (1, -1)

get_chunk_in_region(block_x, block_z) → (local_cx, local_cz)
# lokalne współrzędne chunka w pliku .mca (0-31)

get_block_in_chunk(block_x, block_z) → (local_x, local_z)
# lokalne współrzędne bloku wewnątrz chunka (0-15)
```

Wszystkie trzy poprawnie obsługują ujemne współrzędne (floor division zamiast truncation).

### Przykład — odczyt tile entities z regionu

```python
from minecraft_map_parser.anvil_parser import AnvilParser

parser = AnvilParser("mapa_1710/region/r.0.0.mca")

for chunk in parser.get_all_chunks():
    for te in chunk.get_tile_entities():
        if te.get("id") == "AEDrive":
            print(f"ME Drive na ({te['x']}, {te['y']}, {te['z']})")
```

### Przykład — zlokalizowanie pliku regionu dla znanych współrzędnych bloku

```python
from minecraft_map_parser.anvil_parser import (
    get_region_for_block, get_chunk_in_region, AnvilParser
)

bx, bz = 1500, -800
rx, rz = get_region_for_block(bx, bz)          # (2, -2)
filepath = f"mapa_1710/region/r.{rx}.{rz}.mca"

parser = AnvilParser(filepath)
cx, cz = get_chunk_in_region(bx, bz)
chunk = parser.get_chunk(cx, cz)
```

---

## Moduł 3 — `nbt_writer.py`

Odwrotność parsera — serializacja struktur Pythona z powrotem do binarnego NBT.
Używany przez konwertery modów do zapisu zmodyfikowanych danych chunków.

### Konwencja typowania

Zamiast opakowania w obiekty `NBTTag`, writer używa krotek `(typ, wartość)`.
Każda wartość to albo prymityw Pythona, albo krotka opakowująca go razem z typem NBT.

Funkcje fabryczne tworzą te krotki:

```python
create_byte(12)               # → (TAG_BYTE, 12)
create_short(300)             # → (TAG_SHORT, 300)
create_int(70000)             # → (TAG_INT, 70000)
create_long(1234567890)       # → (TAG_LONG, 1234567890)
create_string("Chest")        # → (TAG_STRING, "Chest")
create_byte_array(b"\x00\x01")# → (TAG_BYTE_ARRAY, b"\x00\x01")
create_int_array([1, 2, 3])   # → (TAG_INT_ARRAY, [1, 2, 3])
create_list([...])            # → (TAG_LIST, [...])
create_compound({...})        # → (TAG_COMPOUND, {...})
```

Compound to `dict[str, (typ, wartość)]` — klucze to nazwy tagów.

### `NBTWriter`

Klasa z wewnętrznym `BytesIO` streamem. Metody `_write_*` zapisują poszczególne typy.
Metoda publiczna:

```python
writer = NBTWriter()
raw = writer.write(name="", tag_type=TAG_COMPOUND, value={
    "id": create_string("Chest"),
    "x":  create_int(100),
    "y":  create_int(64),
    "z":  create_int(-200),
    "Items": create_list([...]),
})
```

Zapisuje root tag (typ + nazwa + payload) i zwraca bajty. `get_bytes()` zwraca
bieżący stan bufora bez zamykania.

### `write_nbt_gzipped(name, tag_type, value) → bytes`

Wrapper łączący `NBTWriter.write()` z `gzip.compress()`. Używany gdy wynik
ma być zapisany jako plik (np. `level.dat`).

### Obsługa TAG_List w _write_payload

Writer wykrywa typ elementów listy z pierwszego elementu. Jeśli element to krotka
`(typ, wartość)` — używa jej typu. Jeśli nie — zakłada TAG_Compound. Pusta lista
zapisywana jest z typem TAG_End i długością 0.

---

## Przepływ danych w projekcie

Poniższy schemat pokazuje jak trzy parsery współpracują podczas konwersji mapy.

```
                        ODCZYT
                        ──────
mapa_1710/region/r.X.Z.mca
        │
        ▼
   AnvilParser                   ← wczytuje plik, parsuje nagłówek MCA
        │  get_chunk(cx, cz)
        ▼
   bytes (zlib/gzip)
        │  zlib.decompress()
        ▼
   bytes (surowe NBT)
        │  parse_nbt()           ← nbt_parser.py
        ▼
   NBTTag (drzewo)
        │  ChunkData.get_tile_entities()
        ▼
   list[dict]                    ← czyste typy Python, gotowe dla konwerterów
        │
        ▼
   Konwerter modu
   (ae2_converter, betterstorage_converter, ...)


                        ZAPIS
                        ─────
   Konwerter modu
        │  zwraca dict z polami NBT 1.18.2
        ▼
   NBTWriter.write()             ← nbt_writer.py
        │
        ▼
   bytes (surowe NBT)
        │  zlib.compress() lub gzip.compress()
        ▼
   bytes (skompresowane)
        │  zapis do pliku .mca świata 1.18.2
        ▼
wynikowy_swiat/region/r.X.Z.mca
```

Konwertery modów nie korzystają bezpośrednio z `AnvilParser` ani `NBTParser` —
operują na czystych słownikach Pythona, które `ChunkData.get_tile_entities()` dostarcza
po pełnej deserializacji NBT. `NBTWriter` po stronie zapisu przyjmuje te same słowniki
(po przetransformowaniu przez konwerter) i serializuje je z powrotem do formatu binarnego.
