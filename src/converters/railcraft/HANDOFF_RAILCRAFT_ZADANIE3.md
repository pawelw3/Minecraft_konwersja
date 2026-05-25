# Handoff: Zadanie 3 - Railcraft (Implementacja konwertera + integracja z routerem)

## Podsumowanie sesji

Zaimplementowano kompletny konwerter Railcraft 1.7.10 → strict 1.18.2 i zintegrowano go z głównym `converters/router.py`. Konwerter obsługuje wszystkie 74 Tile Entity ID z moda (z Zadania 1) i routing przez TE ID (z Zadania 2).

### Wyniki testów
- **32/32 testów symulacji passed** ✅
- **17/17 testów konwertera + routera passed** ✅
- **Łącznie: 49/49 testów passed**

---

## 1. Implementacja głównego konwertera (`railcraft_converter.py`)

### Klasa `RailcraftConverter`

**Public API:**
- `convert_block(block_id_1710, metadata, nbt_1710, position)` — konwersja po block ID + metadata
- `convert_tile_entity(te_id, nbt_1710, metadata, position)` — konwersja po TileEntity ID (używane przez router)

**Kluczowa funkcja: `_resolve_block_from_te()`**

Mapuje 74 różne TE IDs z powrotem na `(block_id, metadata)`:
- `RailcraftTrackTile` / `RailcraftTrackTESRTile` → `railcraft.track`
- `RCHiddenTile` → `railcraft.residual.heat`
- `RCDetectorTile` → `railcraft.detector`
- `RCTileStructure*` → `railcraft.signal`
- Wszystkie maszyny Alpha/Beta/Gamma/Delta/Epsilon → odpowiedni `railcraft.machine.*` + meta
- `RCSlabTile`, `RCStairTile`, `RCPostEmblemTile` → bloki estetyczne
- Fallback → `railcraft.{te_id}` (produkuje czytelny błąd w logu)

**Obsługa RCHiddenTile (ślady gracza):**
- Konwertowany na `minecraft:air` (usunięcie bloku)
- Zwraca `success=True` z warningiem `RC-W-IGNORED`
- Router generuje event `set_block` z `minecraft:air`

---

## 2. Integracja z routerem (`converters/router.py`)

### Dodane elementy:

1. **Lazy singleton** `_railcraft()` (linia ~136)
2. **Obsługa w `convert_te_to_events()`** (linia ~882)
   ```python
   if mod == "railcraft":
       result = _railcraft().convert_tile_entity(...)
       events = _generic_to_events(result, global_pos)
   ```
3. **Detekcja modu** `detect_mod()` już istniała dla Railcraft (linia ~230):
   ```python
   if te_id.startswith("RC") or te_id.startswith("Railcraft") or te_id == "drum":
       return "railcraft"
   ```

---

## 3. Testy integracyjne routera

| Test | Wejście (TE ID) | Wyjście routera | Opis |
|------|----------------|-----------------|------|
| `test_router_coke_oven` | `RCCokeOvenTile` | `immersiveengineering:coke_oven` + NBT | Poprawna konwersja z eventem `set_block_entity` |
| `test_router_hidden_tile_air` | `RCHiddenTile` | `minecraft:air` | Usunięcie bloku, event `set_block` |
| `test_router_unknown_railcraft_placeholder` | `RCFakeTile` | Placeholder | Fallback dla nieznanego TE |

---

## 4. Utworzone / zmodyfikowane pliki

### Nowe pliki
- `src/converters/railcraft/railcraft_converter.py` — główny konwerter z `_resolve_block_from_te()`
- `src/converters/railcraft/tests/test_railcraft_converter.py` — 17 testów konwertera + routera

### Zmodyfikowane pliki
- `src/converters/router.py` — dodano `_railcraft()` singleton i obsługę `mod == "railcraft"`
- `src/converters/railcraft/simulations/railcraft_simulation.py` — zmieniono `RC-E-IGNORED` → `RC-W-IGNORED` dla RCHiddenTile (żeby router nie fallbackował do placeholdera)

### Pliki z poprzednich zadań (bez zmian)
- `src/converters/railcraft/mappings/block_inventory.py`
- `src/converters/railcraft/mappings/block_mappings.py`
- `src/converters/railcraft/simulations/__init__.py`
- `src/converters/railcraft/tests/test_railcraft_simulations.py`
- `src/converters/railcraft/HANDOFF_RAILCRAFT_ZADANIE1.md`
- `src/converters/railcraft/HANDOFF_RAILCRAFT_ZADANIE2.md`

---

## 5. Otwarte problemy

### 5.1 Wymaga weryfikacji na prawdziwej mapie (Zadanie 4)
- [ ] Sprawdzić pokrycie dla stref głównej mapy (`mapa_1710`)
- [ ] Zweryfikować czy wszystkie TE IDs z mapy są obsługiwane przez `_resolve_block_from_te()`
- [ ] Potencjalny konflikt: w raporcie Codex `tileTCRailGag` / `tileTCRail` były przypisane do "Railcraft", ale to są TE z **Traincrafta** — wymaga rozdzielenia w routerze lub osobnego konwertera Traincraft

### 5.2 Wymaga testów E2E (Zadanie 5A/5B/6)
- [ ] Testowa mapa 1.7.10 z wszystkimi blokami Railcrafta
- [ ] Konwersja i weryfikacja na headless serwerze
- [ ] Test integracyjny z redstone (Railcraft jest na liście modów technicznych)

### 5.3 Wymaga weryfikacji źródeł 1.18.2
- [ ] Pobrać i zweryfikować blockstates Create 1.18.2 (track shape, fluid tank)
- [ ] Pobrać i zweryfikować blockstates Steam'n'Rails 1.18.2 (semaphore, track_coupler)
- [ ] Pobrać i zweryfikować NBT IE 1.18.2 (coke_oven, blast_furnace multiblock)

---

## 6. Następne kroki (Zadanie 4)

1. **Analiza pokrycia mapy** — uruchomienie konwertera na próbce regionów z `mapa_1710` i weryfikacja czy wszystkie Railcraft TE są poprawnie mapowane
2. **Rozdzielenie Traincraft vs Railcraft** — jeśli na mapie są TE `tileTCRail*` (Traincraft), trzeba dodać je do routera jako osobny mod lub przypisać do Railcraft jeśli to rzeczywiście Railcraft
3. **Przygotowanie testowej mapy** (Zadanie 5A) z reprezentatywnym zestawem bloków

---

*Dokument utworzony: 2026-05-20*
*Źródła: Dekompilacja Railcraft 9.12.2.0, dokumentacja projektu, kod routera*
