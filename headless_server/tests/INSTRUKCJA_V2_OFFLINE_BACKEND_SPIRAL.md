# Instrukcja v2 dla agenta: naprawa OFFLINE edycji świata + test “spirala PROBE REACHED” (Minecraft 1.7.10) — kod w `src/`

Cel na tę iterację jest podwójny i nierozdzielny:

1) **Naprawić kod wstawiania do mapy** tak, aby był zgodny z **Minecraft Java 1.7.10 (Anvil .mca)** i stabilnie zapisywał:
   - bloki (ID + meta),
   - TileEntities (NBT) vanilla i modowe,
   - duże struktury (hurtowo),
   - małe lokalne patche (pojedyncze bloki/TE).

2) **Zrobić działający test integracyjny**: “spiralny kabel” (wariant B), który po uruchomieniu serwera headless wypisze do logów:
   - `/say [PROBE] REACHED cx=<cx> cz=<cz> step=<n>`
   - i pozwoli automatycznie ocenić PASS/FAIL bez udziału gracza.

> Krytyczna zasada: **zero Amulet writerów** (w szczególności `amulet-core`) do zapisu świata 1.7.10.
> Jeśli backend nadal używa Amuleta do write-path → uznaj to za błąd i popraw.

---

## 0) Co masz zrobić najpierw (blokada przed powtórką błędu)

### 0.1 Usuń `amulet-core` z write-path
- Usuń backend typu `AmuletBackend` *albo* oznacz go jako **READ-ONLY** (jeśli chcesz go zachować do analizy), ale nie wolno nim zapisywać świata.
- W `requirements`/`pyproject` nie dodawaj `amulet-core` jako zależności wymaganej do testów.

### 0.2 Dodaj twardy “guard test” (ma FAILować, jeśli Amulet jest użyty)
Dodaj test w `src/mc_editkit/tests/test_no_amulet_writer.py`:

Wymagania:
- test importuje backend offline (`mc_editkit.world.backends.anvil_backend`)
- sprawdza, że:
  - w pliku backendu nie ma importu `amulet` / `amulet_core`,
  - i że `WorldEditorFactory` dla 1.7.10 NIE zwraca implementacji Amulet.

Jeśli guard nie przechodzi → pipeline nie może iść dalej.

---

## 1) Wybór pythonowej biblioteki do edycji regionów `.mca` (MUST)

W tej iteracji wybierz **jedną** bibliotekę Pythona do write-path i zaimplementuj na niej backend:

- **Rekomendacja praktyczna:** zacznij od biblioteki, która deklaruje edycję świata/chunków, np. **PyAnvilEditor** (jeśli w Twoim środowisku działa i daje poprawny zapis).
- Jeśli wybrana biblioteka nie umie bezpiecznie zapisać `.mca` → porzuć ją szybko i przejdź na inną (to ma wyjść w testach round-trip z sekcji 4).

> Nie wolno “ręcznie składać” regionów `.mca` bez biblioteki, jeśli nie masz 100% pewności co do formatu.
> Format regionów jest łatwy do zepsucia.

---

## 2) Docelowa architektura w `src/` (ma już istnieć — tu doprecyzowanie)

Utrzymaj strukturę:

```
src/mc_editkit/
  world/
    editor.py            # WorldEditor API (interface)
    batch.py             # batching operacji per chunk/region
    validate.py          # walidacje po zapisie
    backends/
      anvil_backend.py   # jedyny writer OFFLINE do 1.7.10
  structures/
    io_voxel_grid.py
    structure.py
  blocks/
    registry.py
    nbt_templates.py
  tests/
    test_no_amulet_writer.py
    test_tileentities_roundtrip.py
    test_variant_b_spiral_probe.py
```

---

## 3) Wymagania funkcjonalne backendu OFFLINE (to jest minimalny “Definition of Done”)

Backend `anvil_backend.py` MUSI umieć:

### 3.1 Operacje atomowe
- `set_block(pos, block_id:int, meta:int)`
- `get_block(pos) -> (block_id, meta)`
- `set_tile_entity(pos, te_nbt)`
- `get_tile_entity(pos) -> te_nbt | None`
- `clear_tile_entity(pos)`

### 3.2 Operacje hurtowe
- `apply(EditBatch)` (batch zawiera set_block i set_tile_entity)
- `paste(Structure, origin, overwrite=True, include_tile_entities=True)`

### 3.3 Transakcje i bezpieczeństwo
- Praca **zawsze na kopii świata**.
- Backup tylko dotkniętych plików regionów przed zapisem.
- `commit()` zapisuje regiony, `rollback()` przywraca backup.

### 3.4 Poprawne mapowanie współrzędnych
- `chunk_x = floor(x/16)`, `chunk_z = floor(z/16)`
- `region_x = floor(chunk_x/32)`, `region_z = floor(chunk_z/32)`
- współrzędne lokalne w chunku: `lx = x & 15`, `lz = z & 15`

Błąd tu = zmiany w złym miejscu lub korupcja.

---

## 4) TileEntities (TE): wymagania zgodności 1.7.10

### 4.1 Zasady wspólne
Każdy TE wpisany do chunku musi mieć:
- `id` (string),
- `x,y,z` (int, absolutne),
- poprawny typ tagów (byte/short/int/string — nie zmieniaj typów “bo tak”).

### 4.2 Command block w 1.7.10
Aby test mógł logować headless, command block musi mieć poprawny TE.

W 1.7.x TE ID command blocka jest historycznie **`Control`** (nie “command_block” z nowszych wersji).

Minimalny TE dla command blocka:
- `id: "Control"`
- `x,y,z`
- `Command: "/say ..."`

### 4.3 TE modowe
TE modowe traktuj jako **opaque**:
- nie usuwaj nieznanych pól,
- nie “normalizuj”,
- nie zmieniaj typów danych.

Masz tylko zagwarantować, że:
- TE jest zapisany w `TileEntities`,
- ma poprawne `x,y,z`,
- chunk zapisuje się poprawnie i serwer nie crashuje.

---

## 5) Test round-trip (MUST, zanim odpalisz spiralę)

Dodaj test `test_tileentities_roundtrip.py`:

### 5.1 Scenariusz
1) Skopiuj minimalny świat testowy do `tmp_world/`.
2) Offline wstaw:
   - 1 command block (ID=137) + TE `Control` z komendą `/say [ROUNDTRIP] ok`
   - 1 hopper albo chest z 1 itemem w `Items` (opcjonalnie, ale zalecane)
3) Zapisz region.
4) Odczytaj ponownie ten chunk tą samą biblioteką/backendem.
5) Sprawdź:
   - blok na pozycji ma ID=137,
   - TE istnieje, ma `id="Control"`,
   - `Command` jest identyczny,
   - inventory (jeśli użyte) ma item.

### 5.2 Kryterium
Jeśli round-trip nie przechodzi → nie wolno używać backendu do testów integracyjnych.

---

## 6) Generator spirali (wariant B) — co masz zbudować offline

### 6.1 Zasada testu
Budujesz jedną, ciągłą konstrukcję:
- start sygnału: **redstone_block** (stałe ON, headless),
- kabel: dust + repeatery (wymuszone repeatery, bo 16 bloków między chunkami),
- w każdym chunku: impulse command block podłączony odgałęzieniem, logujący `REACHED`.

### 6.2 Siatka / checkpointy
Dla chunku `(cx,cz)` checkpoint:
- `x = cx*16 + 8`
- `z = cz*16 + 8`
- `y = stałe` (np. 64) + platforma z kamienia

Spirala ma iść co 1 chunk (skok 16 bloków) do promienia `R`:
- smoke: R=3
- docelowo: R=50 (ale dopiero po przejściu smoke)

### 6.3 Redstone segment między checkpointami
Ponieważ 16>15:
- na każdym odcinku między checkpointami MUSI być co najmniej 1 repeater,
- zalecane 2 repeatery na odcinek, żeby nie było “dust gap” na zakrętach.

### 6.4 Command block w każdym chunku
Blok: ID=137 (command block)
TE:
- `id: "Control"`
- `Command: "/say [PROBE] REACHED cx=<cx> cz=<cz> step=<n>"`

Podłączenie:
- odgałęzienie z głównej linii przez repeater → command block (żeby CB nie osłabiał magistrali).

---

## 7) Test integracyjny: uruchom serwer i oceń logi (headless)

Dodaj `test_variant_b_spiral_probe.py`:

### 7.1 Scenariusz
1) Skopiuj świat bazowy do `tmp_world/`.
2) Offline wstaw spiralę R=3 (na start).
3) Uruchom serwer headless na `tmp_world/` na 30–120 sekund.
4) Parsuj `stdout` lub `logs/latest.log`:
   - szukaj linii `[PROBE] REACHED ... step=...`
5) Wyznacz maksymalny step `K`.

### 7.2 PASS/FAIL
- PASS, jeśli:
  - `step=0` pojawia się w ≤30s,
  - kroki 0..K są bez dziur (0,1,2,...,K),
  - serwer nie crashuje.
- FAIL, jeśli:
  - brak `step=0`,
  - serwer crashuje / “Couldn't load chunk”,
  - kroki skaczą lub znikają natychmiast po 0.

### 7.3 Co robisz po FAIL
Nie prosisz użytkownika o wejście.
Automatycznie:
- zapisujesz logi do artefaktu,
- uruchamiasz walidator świata (sekcja 8),
- wskazujesz pierwszą prawdopodobną przyczynę:
  - TE command blocka ma zły `id` / brak `Command`,
  - region file uszkodzony,
  - kabel ma przerwę (walidacja topologii),
  - konstrukcja jest poza spawn-chunkami (przenieś do okolic spawna).

---

## 8) Walidatory “przed serwerem” (żeby nie debugować crashy w ciemno)

Dodaj w `world/validate.py`:

### 8.1 Walidacja regionów
- wszystkie dotknięte `.mca` dają się otworzyć po zapisie,
- wszystkie dotknięte chunki dają się odczytać,
- brak wyjątków w odczycie NBT.

### 8.2 Walidacja TE
- każdy TE ma `id` i `x,y,z`,
- dla command block: `id == "Control"` i ma `Command` string,
- brak duplikatów TE na tej samej pozycji.

### 8.3 Walidacja ciągłości kabla (wariant B)
Szybki check offline:
- repeatery co ≤14 bloków dust,
- facing repeaterów spójny z kierunkiem segmentu,
- CB podłączony (odgałęzienie działa).

---

## 9) Deliverables (co ma powstać w tej iteracji)

1) `src/mc_editkit/world/backends/anvil_backend.py` — realny pythonowy writer `.mca` dla 1.7.10 (bez Amuleta)
2) `src/mc_editkit/tests/test_no_amulet_writer.py`
3) `src/mc_editkit/tests/test_tileentities_roundtrip.py`
4) `src/mc_editkit/tests/test_variant_b_spiral_probe.py`
5) (opcjonalnie) CLI do uruchomienia spirali i walidacji

---

## 10) Minimalna kolejność prac (żeby nie ugrzęznąć)

1) Guard przeciw Amuletowi.
2) `set_block/get_block` offline.
3) TE dla command blocka (`Control`, `Command`) + round-trip test.
4) Spiral R=1 → uruchom serwer → logi.
5) Spiral R=3 → test integracyjny.
6) Dopiero wtedy skalowanie.

---

## 11) Kryterium “gotowe”
Ta iteracja jest zakończona dopiero, gdy:
- `pytest` przechodzi (guard + round-trip + spiral),
- serwer 1.7.10 nie crashuje po wstawce,
- w logach pojawiają się `[PROBE] REACHED` bez udziału gracza.

---
