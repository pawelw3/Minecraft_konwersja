# Handoff: Railcraft Converter (Zadania 1-5A)

## Podsumowanie sesji
Zaimplementowano kompletny konwerter Railcraft 9.12.2.0 → 1.18.2 (hybrydowy Create/IE/Mekanism/Thermal/FramedBlocks). 
Wykonano inwentaryzację 74+ Tile Entity IDs, 135+ mapowań bloków, symulacje NBT, implementację 
konwertera z routerem, skan mapy głównej oraz lightweight testową mapę z konwersją.

## Ukończono
- [x] **Zadanie 1** — Inwentaryzacja bloków/TE Railcraft (`block_inventory.py`, 74 TE IDs)
- [x] **Zadanie 2** — Mapowania bloków (`block_mappings.py`, 135+ entries) + symulacje NBT (`railcraft_simulation.py`) + 38 unit tests
- [x] **Zadanie 3** — Implementacja konwertera (`railcraft_converter.py`) + integracja z routerem + 17 integration tests
- [x] **Zadanie 4** — Skan mapy głównej (`analyze_map_coverage_chunked.py`) → `output/railcraft_task4/map_coverage_railcraft.json`
- [x] **Zadanie 5A (lightweight)** — Testowa mapa w `lightweigh_map_templates/1710/railcraft_test/` z 19 reprezentatywnymi blokami/TE, konwersja + testy mapy

## Wyniki skanu mapy (1195 plików region, 664972 chunków)

| TE ID | Count | Status |
|-------|-------|--------|
| RCHiddenTile | 22278 | ✅ → air (ignored) |
| RCSteelTankWallTile | 5867 | ✅ → Create Fluid Tank |
| RailcraftTrackTile | 2733 | ✅ → Create track |
| RCIronTankWallTile | 2615 | ✅ → Create Fluid Tank |
| RCBlastFurnaceTile | 272 | ✅ → IE Blast Furnace |
| RCSmokerTile | 253 | ✅ → vanilla Smoker |
| RCBoilerTankHighTile | 216 | ✅ → Thermal Dynamo |
| RailcraftTrackTESRTile | 203 | ✅ → Create track |
| RCCokeOvenTile | 183 | ✅ → IE Coke Oven |
| RCRollingMachineTile | 118 | ✅ → Create Mechanical Press |
| RCEngineSteamHobby | 100 | ✅ → Create Steam Engine |
| RCBoilerFireboxLiquidTile | 100 | ✅ → Thermal Dynamo |
| RCStairTile | 65 | ✅ → FramedBlocks framed_stairs |
| RCSlabTile | 55 | ✅ → FramedBlocks framed_slab |
| RCSteelTankGaugeTile | 24 | ✅ → Create Fluid Tank |
| RCRockCrusherTile | 12 | ✅ → Create Crushing Wheel |
| RCSteelTankValveTile | 8 | ✅ → Create Fluid Tank |
| BRCyaniteReprocessor | 7 | ⚠️ Big Reactors (nie Railcraft) |
| RCTileStructureReceiverBox | 6 | ✅ → Comparator |
| RCTileStructureControllerBox | 5 | ✅ → Comparator |
| RCVoidChestTile | 4 | ✅ → Thermal Nullifier |
| RCBoilerFireboxSoildTile | 4 | ✅ → Thermal Dynamo |
| RCDetectorTile | 4 | ✅ → Observer |

**Wszystkie Railcraft TE na mapie są obsługiwane przez konwerter.**

## Testowa mapa (Zadanie 5A lightweight)

Lokalizacja: `lightweigh_map_templates/1710/railcraft_test/`

Bloki wstawione (19 TE):
- Tory: RailcraftTrackTile (reinforced), RailcraftTrackTESRTile (switch)
- Maszyny Alpha: Coke Oven, Blast Furnace, Rolling Machine, Rock Crusher, Smoker
- Maszyny Beta: Steam Engine Hobby, Boiler Tank High, Boiler Firebox Liquid
- Maszyny Gamma/Delta/Epsilon: Steel Tank Wall/Gauge/Valve, Void Chest
- Sygnały: Receiver Box, Controller Box
- Inne: Slab (IRON), Stair (IRON), Residual Heat

Konwersja przetestowana przez `tests/test_map_conversion.py`:
- 19 TE → 19 events
- Wszystkie mapowania zgodne z oczekiwaniami
- Slab/Stair zachowują orientację (bottom/top, facing)

## Testy
- 55 unit tests (simulations + converter + router)
- 1 test konwersji mapy (`test_map_conversion.py`)
- Wszystkie testy przechodzą ✅

## Nowe pliki
- `src/converters/railcraft/mappings/block_inventory.py`
- `src/converters/railcraft/mappings/block_mappings.py`
- `src/converters/railcraft/simulations/railcraft_simulation.py`
- `src/converters/railcraft/railcraft_converter.py`
- `src/converters/railcraft/analyze_map_coverage.py`
- `src/converters/railcraft/analyze_map_coverage_chunked.py`
- `src/converters/railcraft/analyze_map_coverage_range.py`
- `src/converters/railcraft/test_conversion_on_map.py`
- `src/converters/railcraft/tests/test_railcraft_simulations.py` (38 tests)
- `src/converters/railcraft/tests/test_railcraft_converter.py` (17 tests)
- `src/converters/railcraft/tests/test_map_conversion.py` (1 test)

## Zmodyfikowane pliki
- `src/converters/router.py` — dodano `_railcraft()` lazy singleton + branch `mod == "railcraft"`

## Kluczowe decyzje
1. **Railcraft Reborn niedostępny dla 1.18.2** — użyto hybrydowego mapowania na Create + Steam'n'Rails / Immersive Engineering / Mekanism / Thermal / FramedBlocks.
2. **`RCHiddenTile` → `minecraft:air`** — zgodnie z projektowym `IGNORED_BLOCKS.md`.
3. **Schody/płyty Railcraft → FramedBlocks** — zachowanie orientacji, utrata materiału.
4. **Zadanie 5A lightweight** — zamiast wszystkich 135 bloków, przetestowano 19 reprezentatywnych z każdej kategorii.

## Otwarte / do zrobienia później
- [ ] Testy redstone na headless serwerze (przygotować command block test structure)
- [ ] Pełne testowe mapy ze wszystkimi 135+ blokami (jeśli milestone tego wymaga)
- [ ] Weryfikacja w grze czy skonwertowane bloki wyglądają poprawnie

## Następne kroki
1. [ ] Przejść do następnego modu (np. Thermal Series, AE2, Mekanism, IC2) zgodnie z `docs/PLAN.md`
2. [ ] Milestone integracyjny z Railcraft + innymi modami transportu/tech
