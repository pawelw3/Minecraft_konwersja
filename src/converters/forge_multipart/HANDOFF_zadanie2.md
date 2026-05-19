# Handoff: ForgeMultipart/CB Multipart — Zadanie 2

## Podsumowanie sesji
Przygotowano symulacje działania kluczowych funkcjonalności ForgeMultipart 1.7.10 i CB Multipart 1.18.2 w czystym Pythonie. Symulacje oparte są na dokładnej dekompilacji JAR 1.7.10 (Vineflower) oraz kodzie źródłowym ProjectRed 1.18.2. Przeprowadzono 4 scenariusze testowe pokazujące serializację NBT, współistnienie wielu partów w jednym block-space oraz mapowanie ID partów między wersjami.

## Ukończono
- [x] Implementacja symulacji API ForgeMultipart 1.7.10 (`fmp_1710.py`)
  - `TMultiPart`, `TileMultipart`, `Microblock` (Face/Hollow/Corner/Edge/Post)
  - `McMetaPart` i vanilla parts (`TorchPart`, `ButtonPart`, `LeverPart`, `RedstoneTorchPart`)
  - `ItemMicroPart`, `MicroMaterialRegistry`, `MultiPartRegistry`
  - NBT write/read zgodne z dekompilacją `func_145841_b` / `createFromNBT`
- [x] Implementacja symulacji API CB Multipart 1.18.2 (`cbm_1182.py`)
  - `MultiPart`, `TileMultipart` (BlockEntity API), odpowiedniki mikrobloków
  - Vanilla parts z namespace `cb_multipart:`
  - `ItemMicroPart`, `MicroMaterialRegistry`, `PartRegistry` (ResourceLocation based)
  - NBT `save_additional` / `load` zgodne z konwencją 1.18.2
- [x] 4 scenariusze testowe (`scenarios.py`):
  1. Pojedynczy FaceMicroblock — serializacja NBT i round-trip w obu wersjach.
  2. Wiele partów w jednym block-space (HollowMicroblock + TorchPart).
  3. Konwersja NBT mikrobloku 1.7.10 → 1.18.2 (mapowanie ID + weryfikacja deserializacji).
  4. Dropy przy niszczeniu blocka (symulacja `getDrops`).
- [x] Weryfikacja uruchomieniowa — wszystkie scenariusze przechodzą w Pythonie.

## Nowe pliki
- `src/converters/forge_multipart/simulations/__init__.py`
- `src/converters/forge_multipart/simulations/fmp_1710.py`
- `src/converters/forge_multipart/simulations/cbm_1182.py`
- `src/converters/forge_multipart/simulations/scenarios.py`

## Zmodyfikowane pliki
- Brak (tylko nowe pliki w folderze `src/converters/forge_multipart/simulations/`)

## Następne kroki
1. **Zadanie 3:** Napisanie kodu konwersji (mappera) dla ForgeMultipart → CB Multipart.
   - Konwersja `TileMultipart` NBT (zmiana `id`, `parts[].id`).
   - Konwersja mikrobloków (shape + material bez zmian, tylko namespace part ID).
   - Konwersja vanilla parts (`mc_torch` → `cb_multipart:torch`, itp.).
   - Produkcja eventów konwersji zgodnych z ogólnym handlerem wstawiania na mapę 1.18.2.
2. **Zadanie 4:** Sprawdzenie pokrycia na strefach głównej mapy i weryfikacja exact stringów rejestracji.

## Kluczowe wnioski z symulacji
- **NBT mikrobloków jest kompatybilny strukturalnie** — klucze `shape` i `material` pozostają identyczne.
- **Główna różnica to namespace part ID:** `mcr_*` → `microblockcbe:*`, `mc_*` → `cb_multipart:*`.
- **TileEntity ID zmienia się z `TileMultipart` (1.7.10) na `cb_multipart:tile_multipart` (1.18.2)** — exact string 1.7.10 wymaga potwierdzenia na mapie.
- **Block ID zmienia się z `ForgeMultipart:block` na `cb_multipart:block`**.
