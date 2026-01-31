# Instrukcja dla agenta: implementacja backendu OFFLINE na Hephaistos (JVM) dla świata Minecraft 1.7.10 (Anvil `.mca`) + test spirali

Ta instrukcja opisuje, jak wdrożyć stabilny backend do edycji świata **Minecraft Java 1.7.10** przez bibliotekę **Hephaistos (NBT + Anvil region)**, bez pisania własnego formatu `.mca` od zera i bez używania `amulet-core`.

Docelowo agent ma:
- umieć wstawiać **duże struktury** i **małe patche** offline do plików świata,
- umieć dodawać/zmieniać **TileEntities** (vanilla + modowe “opaque blob”),
- uruchamiać **test integracyjny** “spirala PROBE REACHED” i oceniać PASS/FAIL po logach.

> W tej wersji dopuszczamy JVM jako “worker”, ale logika sterująca i testy mogą zostać w Pythonie.
> Hephaistos odpowiada za **bezpieczny odczyt/zapis `.mca`** i operacje na NBT.

---

## 0) Dlaczego Hephaistos

Hephaistos jest biblioteką JVM zapewniającą:
- odczyt i zapis **regionów Anvil `.mca`**,
- pracę na **NBT** jako drzewie danych,
- co pozwala nam:
  - uniknąć korupcji plików regionów,
  - wykonywać edycję chunków zgodnie z formatem 1.7.10 (legacy `Blocks`/`Data`/`AddBlocks` w `Sections`).

---

## 1) Architektura: Python steruje, JVM edytuje (bridge)

Najprostsza i najbardziej odporna architektura w Twoim repo:

- **Python**:
  - generuje strukturę/patch (np. spiralę) jako JSON,
  - uruchamia JVM worker (jar) z parametrami:
    - `--world <path>`
    - `--patch <path_to_patch.json>`
  - uruchamia serwer headless i parsuje logi.

- **JVM (Kotlin/Java)**:
  - czyta patch JSON,
  - wykonuje batch edycji regionów/chunków przez Hephaistos,
  - zapisuje zmienione `.mca`,
  - robi walidacje “przed uruchomieniem serwera”.

> To podejście pozwala zachować Twój Pythonowy pipeline, a jednocześnie mieć bardzo bezpieczny write-path `.mca`.

---

## 2) Deliverables (co ma powstać)

### 2.1 Nowy moduł JVM
Dodaj folder (propozycja):
```
jvm/
  build.gradle.kts  (lub pom.xml)
  src/main/kotlin/
    mc_editkit_jvm/
      Main.kt
      patch/
        PatchModels.kt
        PatchParser.kt
      anvil/
        RegionIO.kt
        ChunkEdit.kt
        LegacySectionCodec.kt
        TileEntityEdit.kt
        Validators.kt
```

### 2.2 Warstwa Pythona
W `src/mc_editkit/world/backends/` dodaj backend “bridge”:
- `hephaistos_backend.py` (wywołuje jar i przekazuje patch JSON)

---

## 3) Format patch JSON (kontrakt Python ↔ JVM)

Ustal prosty, jednoznaczny format, aby JVM worker nie musiał znać całego świata Twojego kodu.

### 3.1 Patch (proponowany minimalny format)
```json
{
  "version": 1,
  "edits": [
    {"op":"set_block", "x":0, "y":64, "z":0, "id":1, "meta":0},
    {"op":"set_te", "x":0, "y":64, "z":1, "nbt": {"id":"Control","x":0,"y":64,"z":1,"Command":"/say hi"}}
  ]
}
```

### 3.2 Zasady
- `id` i `meta` są w **legacy 1.7.10** (numeric block id + metadata).
- `nbt` jest obiektem “NBT-like” (przekształcany w JVM do NBT compound).
- dla modowych TE `nbt` jest traktowane jako **opaque** (bez normalizacji).

### 3.3 Batching (opcjonalnie, ale zalecane)
Jeśli patch jest ogromny, możesz dodać:
- `chunks`: listę chunków i zmian w chunku,
ale na start wystarczy “płaska lista edits” + grupowanie po chunku w JVM.

---

## 4) Implementacja JVM: I/O regionów i chunków

### 4.1 Odczyt regionu `.mca`
W Hephaistos użyj ich API do region files (konceptualnie):
- `RegionFile` / `DataSource` (dokładne nazwy klas zależą od wersji biblioteki)

Wymagania:
- otwierasz region file tylko raz na batch,
- dla każdego chunku:
  - czytasz “chunk NBT payload”
  - modyfikujesz
  - zapisujesz z powrotem.

### 4.2 Mapowanie współrzędnych
Implementuj funkcje:
- `chunkX = floorDiv(x, 16)`
- `chunkZ = floorDiv(z, 16)`
- `regionX = floorDiv(chunkX, 32)`
- `regionZ = floorDiv(chunkZ, 32)`
- `localChunkX = chunkX & 31`, `localChunkZ = chunkZ & 31`
- `lx = x & 15`, `lz = z & 15`
- `sectionY = y >> 4`, `ly = y & 15`

> Uwaga: `floorDiv` musi działać poprawnie dla ujemnych wartości.

---

## 5) Implementacja: “set_block” dla 1.7.10 (legacy sections)

W 1.7.10 bloki są w `Level/Sections` jako lista sectionów (każdy ma `Y` oraz tablice):
- `Blocks` (ByteArray 4096) — low 8 bitów ID
- `Data` (ByteArray 2048) — metadata nibble
- `AddBlocks` (ByteArray 2048) — high 4 bity ID (dla ID > 255), może nie istnieć

### 5.1 Indeks w sekcji
Index w 1D:
- `idx = (ly * 16 + lz) * 16 + lx`

Wymóg: napisz test jednostkowy, który sprawdza spójność indeksowania (np. ustaw 3 punkty w sekcji i odczytaj je).

### 5.2 Zapis `Blocks` i `AddBlocks`
Dla `blockId`:
- `low = blockId & 0xFF`
- `high = (blockId >> 8) & 0x0F`

Ustaw:
- `Blocks[idx] = low`
- jeśli `high != 0`:
  - upewnij się, że `AddBlocks` istnieje,
  - w `AddBlocks` ustaw nibble dla `idx` na `high`.

### 5.3 Zapis `Data` (metadata)
Metadata 0–15:
- w `Data` (2048) ustaw nibble dla `idx` na `meta`.

---

## 6) Implementacja: TileEntities (TE)

W chunk NBT (1.7.10) lista TE jest zwykle pod:
- `Level/TileEntities` (List of Compound)

### 6.1 Zasady TE
- TE musi mieć `id` (string) oraz `x,y,z` (int).
- Jeśli wstawiasz TE na pozycję, gdzie już jest TE:
  - replace (usuń stary wpis, dodaj nowy) — deterministycznie.

### 6.2 Command block dla testów
Dla 1.7.10 używaj:
- `id = "Control"`
- `Command = "/say ..."`

### 6.3 Modowe TE
- traktuj jako opaque blob:
  - nie usuwaj nieznanych pól,
  - nie zmieniaj typów tagów.

---

## 7) Tworzenie brakujących chunków/sectionów

Backend musi działać nawet jeśli chunk/section nie istnieje.

### 7.1 Jeśli chunk nie istnieje w regionie
- stwórz “minimalny chunk NBT” zgodny z 1.7.10:
  - `Level/xPos`, `Level/zPos`
  - `Level/Sections` = []
  - `Level/TileEntities` = []
  - inne pola minimalne wymagane przez serwer (najbezpieczniej: skopiuj “szablon chunku” z czystego świata)

> Najprościej: dołącz do repo “template chunk NBT” wyciągnięty z czystego świata 1.7.10 i parametryzuj `xPos/zPos`.

### 7.2 Jeśli section dla `sectionY` nie istnieje
- dodaj compound z `Y = sectionY` oraz tablicami:
  - `Blocks` = 4096 bytes (0)
  - `Data` = 2048 bytes (0)
  - `SkyLight`/`BlockLight` (opcjonalnie, mogą być zerowane; światła serwer może przeliczyć)
  - `AddBlocks` tylko gdy potrzeba.

---

## 8) Walidatory w JVM (zanim odpalisz serwer)

### 8.1 Walidacja region I/O
- po zapisie spróbuj ponownie otworzyć zmienione regiony i odczytać zmienione chunki.

### 8.2 Walidacja TE
- każdy TE w zmienionych chunkach ma `id` i `x,y,z`.
- brak duplikatów TE na tej samej pozycji.

### 8.3 Walidacja “bezpiecznego zakresu”
- worker ma odrzucić edycje poza ustalonym AABB testu (opcjonalnie), aby nie dotykać “brudnych” chunków.

---

## 9) Integracja z Pythonem (backend bridge)

### 9.1 `hephaistos_backend.py`
Backend robi:
1) zapisuje patch do pliku JSON,
2) uruchamia `java -jar mc-editkit-jvm.jar --world <world> --patch <patch.json>`,
3) czyta stdout/stderr i failuje jeśli worker zgłasza błąd walidacji.

### 9.2 Kontrakt błędów
Worker zwraca:
- exit code 0 = OK
- exit code != 0 = FAIL (stdout zawiera “DIAG:” z lokalizacją problemu)

---

## 10) Testy: round-trip i spirala

### 10.1 Test round-trip (must-have)
W Pythonie (lub w JVM) zrób test:
- wstaw stone i command block TE,
- uruchom serwer 1.7.10 headless na 15–30s,
- oczekuj loga `/say [ROUNDTRIP] ok`.

### 10.2 Test spirali (wariant B)
Generator w Pythonie tworzy patch:
- platforma z kamienia na Y=64 w chunkach spirali,
- start: `redstone_block`,
- kabel: dust + repeatery między checkpointami (co 16 bloków),
- w każdym chunku: command block TE z `/say [PROBE] REACHED ... step=n`.

Po wstawieniu:
- odpal serwer 30–120s,
- parsuj logi:
  - PASS: `step=0` i ciąg 0..K bez dziur,
  - FAIL: brak `step=0` lub crash.

---

## 11) Strategia iteracji (żeby nie ugrzęznąć)

1) Zrób JVM worker, który potrafi:
   - otworzyć region, wczytać chunk, zapisać chunk “bez zmian” (smoke).
2) Dodaj `set_block` i przetestuj na 1 blok.
3) Dodaj TE (command block) i przetestuj `/say`.
4) Dopiero potem implementuj “paste dużych struktur” i spiralę.

---

## 12) Co jest “na pewno” poza zakresem tej iteracji
- pełna rekalkulacja oświetlenia (light) offline,
- naprawa heightmapów/biomów,
- optymalizacje wielowątkowe.

Najpierw poprawność i brak crashy.

---
