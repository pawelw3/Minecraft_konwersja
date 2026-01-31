# Raport analizy chunków (-1,-1) do (0,0) – Minecraft 1.7.10 (Anvil .mca)

Data wygenerowania raportu: **2026-01-31**

## 1. Zakres analizy

Przeanalizowano dokładnie **4 chunki** (współrzędne chunków):
- (-1, -1)
- (-1, 0)
- (0, -1)
- (0, 0)

Są to cztery chunki otaczające punkt (0,0) w układzie współrzędnych chunków.

## 2. Źródła danych (wejściowe pliki) i ich identyfikacja

Dane zostały odczytane **wyłącznie** z dostarczonych plików regionów (format Anvil, `.mca`).

| Plik | SHA-256 | Zawiera region (rx,rz) | Zakres chunków (x,z) w regionie |
|---|---|---:|---|
| `r.0.0.mca` | `8a3baaa0127712ce278a18e91f1b3018074b0c4d236f6df75d5a470c09e3addf` | (0,0) | x=0..31, z=0..31 |
| `r.0.-1.mca` | `7959c0f5162ccecc039520899c9e405411114b3cd12171f3e5fe3ea274ee0fbb` | (0,-1) | x=0..31, z=-32..-1 |
| `r.-1.0.mca` | `9d214000cf804842bad1ee23d308a802b55373ea936ceb3a652c561cf9244bea` | (-1,0) | x=-32..-1, z=0..31 |
| `r.-1.-1.mca` | `365bf90297b7194522ea8d132f2370b65a855ab728bbfd95f7f1817591aca0c0` | (-1,-1) | x=-32..-1, z=-32..-1 |

Mapowanie chunk → plik regionu użyte w tej analizie:

| Chunk (x,z) | Plik regionu | Lokalny indeks w regionie (lx,lz) |
|---:|---|---:|
| (-1,-1) | `r.-1.-1.mca` | (31,31) |
| (-1,0) | `r.-1.0.mca` | (31,0) |
| (0,-1) | `r.0.-1.mca` | (0,31) |
| (0,0) | `r.0.0.mca` | (0,0) |

## 3. Metodyka pozyskania danych (skąd dokładnie biorą się liczby)

### 3.1. Odczyt chunków z plików `.mca`

Każdy plik regionu `.mca` zawiera 32×32 chunków. Odczyt odbył się wg standardu Anvil:
- nagłówek 8192 B: tablica lokalizacji (4096 B) + timestampy (4096 B)
- dla wybranego chunka wyliczono indeks `idx = lx + lz*32`
- z tablicy lokalizacji pobrano `offset` (w sektorach 4096 B) i `sectors`
- w `offset*4096` odczytano: `length` (4 B, big-endian), `compression_type` (1 B) i dane skompresowane
- `compression_type=2` oznacza dekompresję **zlib** (w tych plikach użyto zlib)

### 3.2. Parsowanie NBT (Minecraft 1.7.10)

Po dekompresji otrzymuje się strukturę NBT. Dane o bloku pochodzą z:
- `Level/Sections[]` – sekcje 16×16×16 z polami:
  - `Y` – numer sekcji (0..15), gdzie wysokość świata to `Y*16 .. Y*16+15`
  - `Blocks` – tablica 4096 bajtów (ID bloków 0..255)
  - `Add` (opcjonalne) – nible (po 4 bity) rozszerzające ID ponad 255; pełny ID to `Blocks + (Add<<8)`
- brakujące sekcje traktowane są jako wypełnione w całości **Air (ID 0)**

Indeksowanie bloków w sekcji (Anvil):
- `i = x + 16*z + 256*y`, gdzie `x,z,y` są lokalne w obrębie 0..15
- współrzędne świata: `wx = chunk_x*16 + x`, `wz = chunk_z*16 + z`, `wy = section_Y*16 + y`

### 3.3. Zliczanie bloków

Dla każdego chunka zliczono wystąpienia pełnych ID bloków w całej objętości **16×256×16 = 65536** bloków.

### 3.4. Tile Entities (np. tabliczki, bloki modowe)

Informacje o obiektach typu Sign oraz o modowych blokach pochodzą z:
- `Level/TileEntities[]`

W szczególności:
- tabliczka: `id = "Sign"` oraz pola `Text1..Text4`
- elementy Railcraft: `id = "RCHiddenTile"` (występują w tych chunkach) – to potwierdza, że blok ID 703 jest blokiem modowym powiązanym z Railcraft (na podstawie zgodności liczby tile entities i liczby bloków ID 703 w chunkach).

## 4. Wyniki – warstwy terenu (bazowa struktura)

We wszystkich 4 chunkach występuje układ typu **superflat**:
- **y=0**: pełna warstwa **Bedrock (ID 7)** (256 bloków na chunk)
- **y=1..2**: pełne warstwy **Dirt (ID 3)** (512 bloków na chunk)
- **y=3**: prawie pełna warstwa **Grass Block (ID 2)** (z jednym wyjątkiem opisanym poniżej)
- **y≥4**: w większości **Air (ID 0)**, z nielicznymi elementami redstone i blokami modowymi

Wyjątek od idealnej warstwy trawy:
- w chunku **(-1,0)** znajduje się pojedynczy blok **Stone (ID 1)** na pozycji **(-5, 3, 0)**, co oznacza, że w tym miejscu warstwa `y=3` nie jest trawą (Grass ma tam 255 zamiast 256).

## 5. Wyniki – biomy

We wszystkich 4 chunkach tablica `Level/Biomes` ma wartość **ID 1** dla wszystkich 256 pól (16×16), czyli biome **Plains**.

## 6. Wyniki – bloki w poszczególnych chunkach (zliczenia)

### 6.1. Chunk (-1, -1)

| ID | Nazwa (1.7.10 / opis) | Liczba bloków w chunku |
|---:|---|---:|
| 0 | Air | 64498 |
| 2 | Grass Block | 256 |
| 3 | Dirt | 512 |
| 7 | Bedrock | 256 |
| 55 | Redstone Wire | 7 |
| 93 | Redstone Repeater (Off) | 1 |
| 703 | Mod Block ID 703 (tile entity: RCHiddenTile) | 6 |

**Tile entities (źródło: `Level/TileEntities`)**:

| id | liczba |
|---|---:|
| `RCHiddenTile` | 6 |

**Zakresy współrzędnych (bounding box) dla wybranych ID** (wyliczone z pozycji bloków):

| ID | Nazwa | Liczba | min(x,y,z) | max(x,y,z) |
|---:|---|---:|---|---|
| 55 | Redstone Wire | 7 | (-5,4,-4) | (-1,4,-1) |
| 93 | Redstone Repeater (Off) | 1 | (-4,4,-4) | (-4,4,-4) |
| 703 | Mod Block ID 703 (tile entity: RCHiddenTile) | 6 | (-8,9,-5) | (-1,13,-1) |

### 6.2. Chunk (-1, 0)

| ID | Nazwa (1.7.10 / opis) | Liczba bloków w chunku |
|---:|---|---:|
| 0 | Air | 64471 |
| 1 | Stone | 1 |
| 2 | Grass Block | 255 |
| 3 | Dirt | 512 |
| 7 | Bedrock | 256 |
| 55 | Redstone Wire | 24 |
| 93 | Redstone Repeater (Off) | 5 |
| 703 | Mod Block ID 703 (tile entity: RCHiddenTile) | 12 |

**Tile entities (źródło: `Level/TileEntities`)**:

| id | liczba |
|---|---:|
| `RCHiddenTile` | 12 |

**Zakresy współrzędnych (bounding box) dla wybranych ID** (wyliczone z pozycji bloków):

| ID | Nazwa | Liczba | min(x,y,z) | max(x,y,z) |
|---:|---|---:|---|---|
| 55 | Redstone Wire | 24 | (-9,4,1) | (-1,4,10) |
| 93 | Redstone Repeater (Off) | 5 | (-9,4,0) | (-1,4,10) |
| 703 | Mod Block ID 703 (tile entity: RCHiddenTile) | 12 | (-16,9,1) | (-1,13,15) |
| 1 | Stone | 1 | (-5,3,0) | (-5,3,0) |

### 6.3. Chunk (0, -1)

| ID | Nazwa (1.7.10 / opis) | Liczba bloków w chunku |
|---:|---|---:|
| 0 | Air | 64470 |
| 2 | Grass Block | 256 |
| 3 | Dirt | 512 |
| 7 | Bedrock | 256 |
| 55 | Redstone Wire | 11 |
| 93 | Redstone Repeater (Off) | 2 |
| 703 | Mod Block ID 703 (tile entity: RCHiddenTile) | 29 |

**Tile entities (źródło: `Level/TileEntities`)**:

| id | liczba |
|---|---:|
| `RCHiddenTile` | 29 |

**Zakresy współrzędnych (bounding box) dla wybranych ID** (wyliczone z pozycji bloków):

| ID | Nazwa | Liczba | min(x,y,z) | max(x,y,z) |
|---:|---|---:|---|---|
| 55 | Redstone Wire | 11 | (0,4,-4) | (9,4,-1) |
| 93 | Redstone Repeater (Off) | 2 | (2,4,-4) | (7,4,-4) |
| 703 | Mod Block ID 703 (tile entity: RCHiddenTile) | 29 | (0,4,-8) | (15,13,-1) |

### 6.4. Chunk (0, 0)

| ID | Nazwa (1.7.10 / opis) | Liczba bloków w chunku |
|---:|---|---:|
| 0 | Air | 64453 |
| 2 | Grass Block | 256 |
| 3 | Dirt | 512 |
| 7 | Bedrock | 256 |
| 55 | Redstone Wire | 28 |
| 63 | Standing Sign | 1 |
| 76 | Redstone Torch (On) | 1 |
| 93 | Redstone Repeater (Off) | 7 |
| 703 | Mod Block ID 703 (tile entity: RCHiddenTile) | 22 |

**Tile entities (źródło: `Level/TileEntities`)**:

| id | liczba |
|---|---:|
| `RCHiddenTile` | 22 |
| `Sign` | 1 |

**Szczegóły tabliczki (Sign)** (dokładnie z NBT `Text1..Text4`):

- Pozycja: (2, 4, 0)
- Text1: `brakujacy`
- Text2: `redstone`
- Text3: ``
- Text4: ``

**Zakresy współrzędnych (bounding box) dla wybranych ID** (wyliczone z pozycji bloków):

| ID | Nazwa | Liczba | min(x,y,z) | max(x,y,z) |
|---:|---|---:|---|---|
| 55 | Redstone Wire | 28 | (0,4,0) | (9,4,10) |
| 93 | Redstone Repeater (Off) | 7 | (1,4,0) | (9,4,10) |
| 76 | Redstone Torch (On) | 1 | (0,4,0) | (0,4,0) |
| 63 | Standing Sign | 1 | (2,4,0) | (2,4,0) |
| 703 | Mod Block ID 703 (tile entity: RCHiddenTile) | 22 | (0,8,0) | (14,13,11) |

## 7. Dokładne współrzędne „nietypowych” bloków (listy)

Poniższe listy zawierają **pełne współrzędne** dla bloków spoza bazowych warstw (czyli m.in. redstone, repeatery, torch, sign, stone oraz modowe ID 703).

### 7.1. Chunk (-1, -1)

#### ID 55 – Redstone Wire

- (-5, 4, -4)
- (-5, 4, -3)
- (-5, 4, -2)
- (-5, 4, -1)
- (-3, 4, -4)
- (-2, 4, -4)
- (-1, 4, -4)

#### ID 93 – Redstone Repeater (Off)

- (-4, 4, -4)

#### ID 703 – Mod Block ID 703 (tile entity: RCHiddenTile)

- (-8, 13, -3)
- (-8, 13, -2)
- (-4, 9, -2)
- (-4, 9, -1)
- (-2, 9, -2)
- (-1, 9, -5)

### 7.2. Chunk (-1, 0)

#### ID 1 – Stone

- (-5, 3, 0)

#### ID 55 – Redstone Wire

- (-9, 4, 1)
- (-9, 4, 2)
- (-9, 4, 3)
- (-9, 4, 4)
- (-9, 4, 5)
- (-9, 4, 6)
- (-9, 4, 7)
- (-9, 4, 8)
- (-9, 4, 10)
- (-8, 4, 10)
- (-7, 4, 10)
- (-6, 4, 10)
- (-5, 4, 1)
- (-5, 4, 2)
- (-5, 4, 3)
- (-5, 4, 4)
- (-5, 4, 6)
- (-4, 4, 6)
- (-4, 4, 10)
- (-3, 4, 6)
- (-3, 4, 10)
- (-2, 4, 6)
- (-2, 4, 10)
- (-1, 4, 10)

#### ID 93 – Redstone Repeater (Off)

- (-9, 4, 9)
- (-5, 4, 0)
- (-5, 4, 5)
- (-5, 4, 10)
- (-1, 4, 6)

#### ID 703 – Mod Block ID 703 (tile entity: RCHiddenTile)

- (-16, 13, 10)
- (-9, 9, 2)
- (-8, 9, 1)
- (-8, 13, 13)
- (-8, 13, 15)
- (-4, 9, 6)
- (-4, 9, 8)
- (-3, 9, 6)
- (-3, 9, 7)
- (-1, 13, 2)
- (-1, 13, 6)
- (-1, 13, 11)

### 7.3. Chunk (0, -1)

#### ID 55 – Redstone Wire

- (0, 4, -4)
- (1, 4, -4)
- (3, 4, -4)
- (4, 4, -4)
- (5, 4, -4)
- (6, 4, -4)
- (8, 4, -4)
- (9, 4, -4)
- (9, 4, -3)
- (9, 4, -2)
- (9, 4, -1)

#### ID 93 – Redstone Repeater (Off)

- (2, 4, -4)
- (7, 4, -4)

#### ID 703 – Mod Block ID 703 (tile entity: RCHiddenTile)

- (0, 13, -1)
- (1, 9, -6)
- (1, 9, -1)
- (1, 13, -7)
- (1, 13, -5)
- (2, 4, -5)
- (2, 12, -5)
- (2, 13, -2)
- (2, 13, -1)
- (3, 9, -3)
- (3, 10, -1)
- (3, 13, -3)
- (3, 13, -2)
- (4, 9, -2)
- (4, 10, -1)
- (4, 13, -4)
- (5, 6, -2)
- (5, 9, -1)
- (5, 13, -1)
- (6, 13, -4)
- (7, 9, -2)
- (7, 13, -5)
- (9, 9, -3)
- (10, 6, -4)
- (12, 9, -4)
- (13, 4, -4)
- (13, 5, -4)
- (13, 6, -6)
- (15, 6, -8)

### 7.4. Chunk (0, 0)

#### ID 55 – Redstone Wire

- (0, 4, 6)
- (0, 4, 10)
- (1, 4, 0)
- (1, 4, 6)
- (2, 4, 6)
- (2, 4, 10)
- (3, 4, 0)
- (3, 4, 10)
- (4, 4, 6)
- (4, 4, 10)
- (5, 4, 0)
- (5, 4, 1)
- (5, 4, 2)
- (5, 4, 4)
- (5, 4, 5)
- (5, 4, 6)
- (5, 4, 10)
- (6, 4, 10)
- (8, 4, 10)
- (9, 4, 1)
- (9, 4, 2)
- (9, 4, 3)
- (9, 4, 4)
- (9, 4, 6)
- (9, 4, 7)
- (9, 4, 8)
- (9, 4, 9)
- (9, 4, 10)

#### ID 93 – Redstone Repeater (Off)

- (1, 4, 10)
- (3, 4, 6)
- (4, 4, 0)
- (5, 4, 3)
- (7, 4, 10)
- (9, 4, 0)
- (9, 4, 5)

#### ID 76 – Redstone Torch (On)

- (0, 4, 0)

#### ID 63 – Standing Sign

- (2, 4, 0)

#### ID 703 – Mod Block ID 703 (tile entity: RCHiddenTile)

- (0, 9, 8)
- (1, 13, 8)
- (2, 12, 2)
- (2, 12, 11)
- (2, 13, 1)
- (2, 13, 5)
- (2, 13, 6)
- (2, 13, 8)
- (2, 13, 9)
- (3, 12, 0)
- (4, 8, 1)
- (4, 12, 5)
- (4, 13, 0)
- (5, 9, 8)
- (6, 13, 3)
- (7, 8, 8)
- (7, 9, 5)
- (7, 9, 7)
- (8, 8, 9)
- (9, 9, 0)
- (10, 9, 0)
- (14, 13, 0)

## 8. Suma (4 chunki razem)

| ID | Nazwa (1.7.10 / opis) | Liczba bloków (łącznie) |
|---:|---|---:|
| 3 | Dirt | 2048 |
| 7 | Bedrock | 1024 |
| 2 | Grass Block | 1023 |
| 55 | Redstone Wire | 70 |
| 703 | Mod Block ID 703 (tile entity: RCHiddenTile) | 69 |
| 93 | Redstone Repeater (Off) | 15 |
| 1 | Stone | 1 |
| 63 | Standing Sign | 1 |
| 76 | Redstone Torch (On) | 1 |

Dla porządku: łączna liczba bloków Air (ID 0) w 4 chunkach = **257892** (z łącznych 262144 bloków).

## 9. Uwagi interpretacyjne

- Nazwy bloków dla ID ≤ 255 odpowiadają standardowym ID z ery 1.7.x (przed „flatteningiem” z 1.13).
- ID **703** nie jest blokiem vanilla – w danych NBT występują tile entities `RCHiddenTile` w liczbie dokładnie równej liczbie bloków ID 703 w każdym chunku, co jest silną przesłanką, że to blok/ukryty element z moda **Railcraft**.
- Raport nie zgaduje nazw modowych na podstawie zewnętrznych źródeł – opiera się tylko o to, co wprost jest zapisane w NBT.
