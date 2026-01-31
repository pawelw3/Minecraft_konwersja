# Instrukcja dla agenta: spójny edytor mapy OFFLINE w Pythonie + pipeline testów (Minecraft 1.7.10 + mody) — kod w `src/`

Ta instrukcja opisuje **konkretny plan prac**, architekturę kodu i checklisty jakości, aby agent mógł:
- automatycznie **wstawiać duże struktury** (hurtowo) do świata,
- robić **małe lokalne edycje** (pojedyncze bloki/TE),
- wspierać **bloki z modów i TileEntities (TE)**,
- uruchamiać testy **headless** i oceniać wynik po logach (bez proszenia użytkownika o wejście na serwer),
- robić to **koniecznie przez biblioteki Pythona**, bez RCON, bez komend “online”.

> **Zasada nadrzędna:** agent **nie prosi użytkownika o ręczne sprawdzanie**.  
> Jeśli test nie daje jednoznacznego sygnału w konsoli → agent **sam** debugguje, poprawia, restartuje serwer i weryfikuje logi.

---

## 1) Co budujesz: jeden interfejs edycji świata (OFFLINE), zero zależności od serwera

Wszystkie edycje świata wykonujesz **offline** na plikach świata:
- regiony Anvil: `region/r.<rx>.<rz>.mca`
- dane chunków (NBT) wewnątrz regionu
- listy `TileEntities` wewnątrz chunków (NBT)

Masz **jedno API** edycji świata, które działa tak samo dla:
- ogromnych wstawek (paste struktury),
- małych patchy (set pojedynczego bloku/TE).

---

## 2) Wybór biblioteki Pythona do edycji `.mca` (agent MUSI wybrać i uzasadnić)

Agent wybiera **jedną główną bibliotekę** do read/write regionów `.mca` i chunków oraz ma **jedną awaryjną**.

### Opcja A (zalecana jeśli działa stabilnie w write-path): `PyAnvilEditor`
Projekt jest nastawiony na edycję światów/chunków w Pythonie (read/write).
Używaj, jeśli testy round-trip (patrz sekcja 8) przechodzą.

### Opcja B (lekka i prosta): `anvil-parser` + własny zapis regionów (tylko jeśli write jest pewny)
`anvil-parser` jest popularny do parsowania Anvil. Do edycji musisz mieć pewność, że zapis `.mca` jest poprawny
(unikaj “parser-only” jeśli nie masz gwarancji bezpiecznego zapisu).

### Opcja C (historyczna, sprawdzona w praktyce na starych światach): backend MCEdit (`pymclevel`)
To starsza ścieżka. Jeśli środowisko/wersja Pythona pozwala i testy przechodzą, może być solidnym wyjściem.

> **Wymóg:** niezależnie od wyboru, agent **musi** dodać testy, które:
> 1) zapisują zmiany do `.mca`,
> 2) ponownie wczytują świat tą samą biblioteką,
> 3) uruchamiają “smoke boot” serwera 1.7.10 na kopii świata i potwierdzają brak crash.

---

## 3) Struktura repo i modułów (kod ma powstać w `src/`)

Utwórz taki szkielet (nazwy możesz dostosować, ale zachowaj ideę):

```
src/
  mc_editkit/
    __init__.py
    config.py
    logging.py

    blocks/
      __init__.py
      registry.py            # mapowanie bloków (vanilla + mody) -> (id, meta)
      nbt_templates.py       # szablony TE jako NBT (nbtlib/amulet-nbt lub dict->NBT)

    world/
      __init__.py
      types.py               # Pos, ChunkPos, RegionPos, AABB, EditOperation
      batch.py               # grupowanie operacji per region/chunk
      validate.py            # walidacje spójności świata po edycji
      editor.py              # WorldEditor API (interface + fabryka)

      backends/
        __init__.py
        anvil_backend.py     # OFFLINE: jedyna implementacja (wybrana biblioteka Pythona)

    structures/
      __init__.py
      palette.py             # blok+meta+opcjonalny TE
      structure.py           # Structure, paste(), rotate(), mirror()
      io_voxel_grid.py       # import z voxel_grid.json do Structure

    tests/
      __init__.py
      test_smoke_small_paste.py
      test_tileentities_roundtrip.py
      test_variant_b_spiral_probe.py
```

---

## 4) Jedno API edycji świata (kontrakt, którego trzymasz się zawsze)

Zdefiniuj w `world/editor.py` interfejs:

### 4.1 Operacje atomowe
- `set_block(pos, block_id: int, meta: int = 0)`
- `set_tile_entity(pos, te_nbt)`  
  Wymaganie: TE NBT musi zawierać co najmniej `id`, `x`, `y`, `z`.
- `clear_tile_entity(pos)`
- `get_block(pos)` / `get_tile_entity(pos)` (do debug/inspekcji)

### 4.2 Operacje hurtowe
- `paste(structure, origin, *, overwrite=True, include_tile_entities=True)`
- `apply(ops: list[EditOperation])` z batchingiem per region/chunk
- `commit()` / `rollback()` (transakcja na kopii świata)

### 4.3 Wymóg jakości
Każda metoda musi:
- logować (INFO) “co i gdzie zmieniono”,
- walidować współrzędne i zakresy,
- w razie wyjątku zostawić świat w stanie nieuszkodzonym (rollback).

---

## 5) Rejestr bloków: vanilla + mody (1.7.10 = ID + meta)

W 1.7.10 i modach z tamtej epoki używasz:
- **numeric block ID** + **metadata 0–15**.

### 5.1 `blocks/registry.py`
Rejestr ma mapować “nazwę logiczną” na `(id, meta)`:

Przykład:
- `"minecraft:stone"` → `(1, 0)`
- `"minecraft:redstone_wire"` → `(55, 0)`
- `"minecraft:command_block"` → `(137, 0)`
- `"appliedenergistics2:controller"` → `(MOD_ID, META)` *z configu / źródła*

### 5.2 Modowe bloki i TE
Agent **nie zgaduje** ID/mety ani formatu NBT modowych TE.

Jeśli brak pewnych źródeł:
1) agent prosi użytkownika o:
   - listę ID/met (np. z NEI / configów / dumpu),
   - oraz przykładowe struktury w świecie i screeny/eksport NBT (jeśli możliwe),
2) agent utrzymuje “registry.json” z mapowaniem ID/met i schematami TE.

---

## 6) Backend OFFLINE: zasady bezpiecznej edycji regionów

### 6.1 Zasady bezpieczeństwa (MUSI)
- Zawsze pracuj na **kopii świata** (np. `world_copy/`).
- Przed commit zrób backup tylko dotkniętych regionów:
  - skopiuj `region/r.x.z.mca` do `backup/<timestamp>/...`
- Po zapisie wykonaj:
  1) walidację NBT chunków (sekcja 8),
  2) “smoke boot” serwera (sekcja 9).

### 6.2 Patch-based editing (wydajność)
Nie rób milionów `set_block` bezpośrednio do plików w pętli.

Zamiast tego:
1) zbierz operacje do `EditBatch`,
2) pogrupuj po regionach i chunkach,
3) otwórz region raz, zmodyfikuj wszystkie dotknięte chunki, zapisz raz.

### 6.3 Chunk i indeksowanie
Agent ma poprawnie mapować:
- `chunk_x = floor(x / 16)`
- `chunk_z = floor(z / 16)`
- `region_x = floor(chunk_x / 32)`
- `region_z = floor(chunk_z / 32)`
- lokalne współrzędne w chunku: `x & 15`, `z & 15`

Błędy tu = korupcja albo “zmiany w złym miejscu”.

---

## 7) TileEntities (TE): jak je wstawiać i nie crashować serwera

### 7.1 Zasady TE (zawsze)
Jeśli ustawiasz blok z TE (command block, chest, hopper, dropper, modowa maszyna):
1) ustaw blok (ID+meta),
2) dodaj/zmień wpis w `TileEntities` chunku,
3) ustaw w TE:
   - `id` (string),
   - `x,y,z` (int, absolutne w świecie),
   - resztę pól zgodnie z typem.

### 7.2 Command block (do testów headless)
Command block w 1.7.10 ma NBT z polem `Command` (string).
Agent musi ustawiać je offline w TE, nie przez komendy.

### 7.3 Inventory TE (hopper/chest/dropper)
Inventory jest w TE zwykle jako lista `Items`:
- każdy element ma `Slot`, `id`, `Count` (+ czasem `Damage`).

Agent ma dodać test round-trip (sekcja 8.2), bo to jest krytyczne.

### 7.4 Modowe TE
Dla modów agent traktuje TE NBT jako **opaque blob**:
- nie “normalizuje” pól,
- nie usuwa nieznanych tagów,
- nie zmienia typu danych (byte/short/int/string),
bo to typowa przyczyna crashy “ticking tile entity”.

---

## 8) Walidatory i testy (hamulec bezpieczeństwa)

### 8.1 Walidator świata po edycji (OFFLINE)
W `world/validate.py` dodaj:
- sprawdzenie, że wszystkie dotknięte regiony `.mca` da się ponownie otworzyć,
- że wszystkie zmienione chunki mają poprawne NBT,
- że `TileEntities` w chunku to lista compoundów,
- że każdy TE ma `id` i `x,y,z`.

### 8.2 Test: round-trip TE (MUSI)
Test `test_tileentities_roundtrip.py`:
1) utwórz mały patch świata: hopper z itemem + command block z komendą,
2) zapisz,
3) wczytaj ponownie,
4) porównaj NBT TE (co najmniej kluczowe pola).

Jeśli to nie przechodzi → nie wolno używać backendu do produkcyjnych wstawek.

---

## 9) Headless testy: jak agent ocenia PASS/FAIL bez gracza

### 9.1 Zasada
Testy muszą być “self-reporting” do logów serwera:
- command blocki wykonują `/say [PROBE] ...` (lub inny sygnał widoczny w konsoli).

### 9.2 Procedura test-run (agent-run)
1) agent wstawia strukturę offline do kopii świata,
2) uruchamia serwer headless na tej kopii,
3) czyta log stdout / `logs/latest.log`,
4) szuka wzorców:
   - np. `[PROBE] REACHED ... step=...`
5) jeśli brak oczekiwanych wpisów w czasie T → FAIL,
6) agent zatrzymuje serwer i debugguje (nie prosi użytkownika o wejście).

### 9.3 Smoke boot (MUSI po każdej większej edycji)
Po każdej większej edycji agent musi:
- uruchomić serwer na 10–30s,
- sprawdzić, czy nie ma crasha,
- sprawdzić, czy świat się ładuje (brak “ticking tile entity” w logu).

---

## 10) Konkret: test wariant B (spiralny kabel) — zasada implementacji offline

Agent generuje spiralę chunków do promienia R,
buduje:
- start sygnału (np. stałe źródło ON: redstone block),
- kabel redstone + repeatery między checkpointami,
- w każdym chunku command block z TE:
  - `Command: "/say [PROBE] REACHED cx=... cz=... step=..."`.

Agent wstawia to offline do świata, uruchamia serwer i parsuje logi:
- PASS: kroki rosną bez dziur 0..K,
- FAIL: brak `step=0` albo zatrzymanie sekwencji.

---

## 11) Deliverables: co agent ma dostarczyć w repo

1) Kod w `src/mc_editkit/` zgodny z architekturą z sekcji 3.
2) `WorldEditor` API + jedyny backend offline `anvil_backend.py` (wybrana biblioteka Pythona).
3) `blocks/registry.py` + format pliku z mapowaniem bloków modowych.
4) `structures/Structure` + import z `voxel_grid.json`.
5) Testy z sekcji 8–10, uruchamialne w CI.
6) Minimalny CLI:
   - `python -m mc_editkit.cli paste --world <path> --voxel <path> --origin ...`
   - `python -m mc_editkit.cli run-test --world <path> --test variant_b`

---

## 12) Zasady “idiotoodporności” (agent ma je stosować zawsze)

- **Nie edytuj świata produkcyjnego.** Zawsze kopia + backup regionów.
- **Nie proś użytkownika o wejście.** Test ma gadać w logach.
- **Nie zgaduj zachowania modów.** Jeśli brak źródeł → proś o przykłady i dane.
- **Każda większa zmiana = walidacja + smoke-boot serwera.**
- **Nigdy nie “normalizuj” modowych TE bez źródeł.** Traktuj NBT jako opaque.

---
