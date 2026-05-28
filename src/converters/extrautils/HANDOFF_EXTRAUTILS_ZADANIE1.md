# Handoff: Extra Utilities - Zadanie 1

## Podsumowanie sesji

Zaimplementowano pierwszy krok konwersji moda Extra Utilities 1.7.10 → 1.18.2. Na podstawie dekompilacji JAR (`extrautilities-1.2.12.jar`) i danych z mapy (`output/discovered_te_ids.txt`) zidentyfikowano wszystkie bloki, tile entities oraz ich mapowania na mody docelowe. Stworzono strukturę konwertera, mappingi bloków, główną klasę konwertera, testy jednostkowe oraz zintegrowano z routerem.

## Ukończono

- [x] Inwentaryzacja bloków i TE Extra Utilities 1.7.10 (dekompilacja JAR)
- [x] Identyfikacja bloków występujących na mapie (3x generator lava, 267x AntiMobTorch)
- [x] Stworzenie hybrydowych mapowań bloków → mody 1.18.2 (Thermal, Mekanism, Torchmaster, Cursed Earth, Angel Block Renewed, Trash Cans, Extreme Sound Muffler)
- [x] Implementacja `ExtraUtilsConverter` z obsługą `convert_block` i `convert_tile_entity`
- [x] Mapowanie TE ID → (block_id, metadata) dla generatorów i magnum torch
- [x] Integracja z `converters.router` (detekcja modu, serializator, gałąź w `convert_te_to_events`)
- [x] 19 testów jednostkowych (wszystkie przechodzą)
- [x] Weryfikacja end-to-end przez router (generuje poprawne Event JSON)

---

## 1.7.10 — Bloki i Tile Entities (kompletna lista z dekompilacji)

### Generatory (`extrautils:generator`, `extrautils:generator.8`, `extrautils:generator.64`)
Jeden blok z 12 wariantami (metadata 0-11). Warianty x8 i x64 to osobne block ID.

| Meta | Suffix | Nazwa | TE Class | TE ID |
|------|--------|-------|----------|-------|
| 0 | stone | Survivalist | TileEntityGeneratorFurnaceSurvival | extrautils:generatorstone |
| 1 | base | Furnace | TileEntityGeneratorFurnace | extrautils:generatorbase |
| 2 | lava | Lava | TileEntityGeneratorMagma | extrautils:generatorlava |
| 3 | ender | Ender | TileEntityGeneratorEnder | extrautils:generatorender |
| 4 | redflux | Heated Redstone | TileEntityGeneratorRedFlux | extrautils:generatorredflux |
| 5 | food | Culinary | TileEntityGeneratorFood | extrautils:generatorfood |
| 6 | potion | Potions | TileEntityGeneratorPotion | extrautils:generatorpotion |
| 7 | solar | Solar | TileEntityGeneratorSolar | extrautils:generatorsolar |
| 8 | tnt | TNT | TileEntityGeneratorTNT | extrautils:generatortnt |
| 9 | pink | Pink | TileEntityGeneratorPink | extrautils:generatorpink |
| 10 | overclocked | High-temp Furnace | TileEntityGeneratorFurnaceOverClocked | extrautils:generatoroverclocked |
| 11 | nether | Nether Star | TileEntityGeneratorNether | extrautils:generatornether |

### Magnum Torch (`extrautils:magnumTorch`)
- Blok: `extrautils:magnumTorch`
- TE: `TileEntityAntiMobTorch`
- Funkcja: blokada spawnu mobów w promieniu 64+ bloków

### Pozostałe bloki (bez TE lub z innymi TE)
- `extrautils:angelBlock` — Angel Block
- `extrautils:cursedEarth` — Cursed Earth (spawn mobów)
- `extrautils:trashCan` (meta 0=item, 1=fluid, 2=energy) — Trash Can
- `extrautils:soundMuffler` — Sound Muffler
- `extrautils:drum` — Drum (TileEntityDrum, TE id "drum")
- `extrautils:filingCabinet` — Filing Cabinet (TileEntityFilingCabinet)
- `extrautils:enderThermicPump` — Ender-Thermic Pump (TileEntityEnderThermicLavaPump, TE id "enderPump")
- `extrautils:enderQuarry` — Ender Quarry (TileEntityEnderQuarry, TE id "enderQuarry")
- `extrautils:chandelier` — Chandelier
- `extrautils:conveyor` — Conveyor Belt
- `extrautils:BUDBlock` — Block Update Detector (TileEntityBUD)
- `extrautils:spike` / `spikeDiamond` / `spikeGold` / `spikeWood` — Spikes (TileEntityEnchantedSpike)
- `extrautils:peacefultable` — Peaceful Table
- `extrautils:tradingPost` — Trading Post (TileEntityTradingPost)
- `extrautils:timerBlock` — Timer Block
- `extrautils:enderCollector` — Ender Collector (TileEnderCollector)
- `extrautils:enderLily` — Ender Lily
- `extrautils:enderMarker` — Ender Marker
- `extrautils:curtain` — Blackout Curtains
- `extrautils:greenScreen` — Green Screen
- `extrautils:bedrockiumBlock` — Bedrockium
- `extrautils:portal` — Portal (TileEntityPortal)
- Szereg bloków dekoracyjnych (colorBlockData, colorBlockBrick, coloredWood, colorQuartz, itp.)

---

## Mapowania 1.18.2 (hybrydowe)

| Blok/TE ExU 1.7.10 | Mod docelowy 1.18.2 | Block ID 1.18.2 |
|---|---|---|
| Generator lava | Thermal Expansion | `thermal:dynamo_magmatic` |
| Generator stone/base/overclocked | Thermal Expansion | `thermal:dynamo_stirling` |
| Generator ender/nether | Thermal Expansion | `thermal:dynamo_numismatic` |
| Generator redflux | Thermal Expansion | `thermal:dynamo_lapidary` |
| Generator food/pink | Thermal Expansion | `thermal:dynamo_gourmand` |
| Generator potion | Thermal Expansion | `thermal:dynamo_alchemical` |
| Generator solar | Mekanism Generators | `mekanismgenerators:solar_generator` |
| Generator tnt | Thermal Expansion | `thermal:dynamo_disenchantment` |
| Magnum Torch | Torchmaster | `torchmaster:mega_torch` |
| Cursed Earth | Cursed Earth | `cursedearth:cursed_earth` |
| Angel Block | Angel Block Renewed | `angelblockrenewed:angel_block` |
| Trash Can (item) | Trash Cans | `trashcans:item_trash_can` |
| Trash Can (fluid) | Trash Cans | `trashcans:liquid_trash_can` |
| Trash Can (energy) | Trash Cans | `trashcans:energy_trash_can` |
| Sound Muffler | Extreme Sound Muffler | `extremesoundmuffler:sound_muffler` |

---

## Nowe pliki

- `src/converters/extrautils/__init__.py`
- `src/converters/extrautils/extrautils_converter.py` — Główny konwerter
- `src/converters/extrautils/mappings/__init__.py`
- `src/converters/extrautils/mappings/block_mappings.py` — Mapowania bloków i TE
- `src/converters/extrautils/simulations/__init__.py`
- `src/converters/extrautils/simulations/extrautils_simulation.py` — Symulacje konwersji
- `src/converters/extrautils/tests/__init__.py`
- `src/converters/extrautils/tests/test_extrautils_converter.py` — 19 testów

## Zmodyfikowane pliki

- `src/converters/router.py`
  - Dodano `_extrautils()` singleton (linia ~180)
  - Dodano detekcję `extrautils` w `detect_mod()` (linia ~345)
  - Dodano `_extrautils_to_events()` serializator (linia ~640)
  - Dodano gałąź `extrautils` w `convert_te_to_events()` (linia ~1145)

---

## Następne kroki

1. [ ] Zadanie 2 — Symulacje funkcjonalności i konwersja NBT
   - Symulacja generatorów (przepisanie zgromadzonej energii jeśli możliwe)
   - Konwersja NBT dla Drum (płyn), Filing Cabinet (inventory)
   - Konwersja NBT dla Ender Quarry i Ender-Thermic Pump

2. [ ] Zadanie 3 — Rozszerzenie mapowań o pozostałe bloki
   - `extrautils:drum` → `extrautilitiesreborn:drum` lub `create:fluid_tank`
   - `extrautils:filingCabinet` → placeholder (brak dobrego odpowiednika)
   - `extrautils:enderThermicPump` → `mekanism:electric_pump`
   - `extrautils:enderQuarry` → `rftoolsbuilder:builder` + quarry card
   - `extrautils:conveyor` → `create:belt` lub `immersiveengineering:conveyor`
   - Bloki dekoracyjne → `extrautilitiesreborn` lub `chipped`/`rechiseled`

3. [ ] Zadanie 4 — Sprawdzenie pokrycia na mapie głównej
   - Pełne przeszukanie chunków pod kątem wszystkich block ID z namespace `extrautils`
   - Weryfikacja czy mappingi pokrywają 100% wystąpień

4. [ ] Zadanie 5 — Testowa mapa i konwersja E2E
   - Stworzenie świata testowego z generatorami, magnum torch, trash can
   - Konwersja i weryfikacja w grze

5. [ ] Zadanie 6 — Test headless serwer
   - 3 minuty ticków + restart serwera z przekonwertowaną mapą

---

*Data utworzenia: 2026-05-27*
*Zadanie 1 zakończone*
