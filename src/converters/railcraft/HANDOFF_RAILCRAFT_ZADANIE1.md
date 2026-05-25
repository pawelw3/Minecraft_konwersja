# Handoff: Zadanie 1 - Railcraft (Inwentaryzacja bloków i Tile Entities)

## Podsumowanie sesji

Wykonano kompletną inwentaryzację moda **Railcraft 9.12.2.0** dla Minecraft 1.7.10. Zdekompilowano kod źródłowy z JARa (`Railcraft_1.7.10-9.12.2.0.jar`) przy użyciu Vineflower i przeanalizowano wszystkie klasy bloków oraz Tile Entities. Wyniki zapisano w module `src/converters/railcraft/mappings/block_inventory.py`.

### Kluczowa decyzja: ignorowanie śladów gracza

**`RCHiddenTile` (Residual Heat / ślad gracza Railcrafta) jest wyłączony z konwersji** zgodnie z wymaganiem użytkownika. Tile entity to pojawia się bardzo często na mapie (analiza strefy Choroszcz wykazała 130/130 TE Railcrafta jako `RCHiddenTile`) i nie zostawia trwałych bloków o wartości funkcjonalnej - jest to efekt wizualny/wewnętrzny moda.

---

## 1. Informacje ogólne o Railcraft

### 1.1 Railcraft 1.7.10
- **Wersja**: 9.12.2.0
- **Lokalizacja źródeł**: `modpack_1710/Railcraft_1.7.10-9.12.2.0.jar`
- **Kod źródłowy**: zdekompilowany do `/tmp/railcraft_decomp` (vineflower)

### 1.2 Docelowe mody 1.18.2
- **Railcraft Reborn 5.x** — bezpośredni port (z uwagą o niestabilności)
- **Create: Steam 'n' Rails** — alternatywa dla torów i systemu sygnałów (inna mechanika)

### 1.3 Strategia konwersji
- Bezpośrednie mapowanie bloków na Railcraft Reborn tam gdzie to możliwe
- Tory specjalne (TileTrack) wymagają mapowania per `trackTag`
- Maszyny wieloblokowe (Coke Oven, Blast Furnace, Boiler, Tanks) wymagają odtworzenia struktury
- Ślady gracza (`RCHiddenTile`) → **IGNOROWANE**

---

## 2. Kategorie bloków Railcraft

| Kategoria | Liczba wariantów | Tile Entity | Uwagi |
|-----------|-----------------|-------------|-------|
| Tory specjalne (EnumTrack) | 48 trackTag | TileTrack / TileTrackTESR | 10 deprecated |
| Maszyny Alpha | 16 meta | 16 różnych TE | World Anchor, Coke Oven, Blast Furnace, Rolling Machine, Rock Crusher itp. |
| Maszyny Beta | 16 meta | 16 różnych TE | Iron/Steel Tank, Boiler, Steam Engines, Chests |
| Maszyny Gamma | 12 meta | 12 różnych TE | Loadery/Unloaderzy itemów, płynów, energii |
| Maszyny Delta | 2 meta | 2 TE | Shunting Wire, Spawner Refill |
| Maszyny Epsilon | 6 meta | 6 TE | Electric Feeder, Flux Transformer, Force Track Emitter, Engraving Bench |
| Sygnały (EnumSignal) | 14 meta | 14 różnych TE | Block Signal, Distant Signal, Switch Motor, Controller Box itp. |
| Detektory (EnumDetector) | 17 meta | TileDetector (1 TE class) | Item, Mob, Player, Train, Routing itp. |
| Bloki estetyczne | 20+ wariantów | Slab/Stair/Post TE | Brick, Cube, Glass, Lantern, Post, Slab, Stair, Wall |
| Rudy | 12 meta | Brak | Sulfur, Saltpeter, Dark Ores, Poor Ores |
| Inne | 5+ | RCHiddenTile, RCFirestoneRechargeTile | Residual Heat (IGNOROWANE) |

**Razem**: 140+ rejestracji bloków, **75 różnych Tile Entity ID**.

---

## 3. Szczegółowa lista maszyn

### 3.1 Maszyny Alpha (railcraft.machine.alpha) — meta 0-15

| Meta | Nazwa | TE ID | Funkcja |
|------|-------|-------|---------|
| 0 | World Anchor | RCWorldAnchorTile | Chunk loading |
| 1 | Steam Turbine | RCSteamTurbineTile | Produkcja energii (IC2 EU / RF) |
| 2 | Personal Anchor | RCPersonalAnchorTile | Chunk loading (personalny) |
| 3 | Steam Oven | RCSteamOvenTile | Piec parowy |
| 4 | Admin Anchor | RCAdminAnchorTile | Chunk loading (admin) |
| 5 | Smoker | RCSmokerTile | Efekt wizualny dymu |
| 6 | Trade Station | RCTradeStationTile | Handel z wioskami |
| 7 | Coke Oven | RCCokeOvenTile | Wieloblok - produkcja koksownicy |
| 8 | Rolling Machine | RCRollingMachineTile | Walcowanie płyt/szyn |
| 9 | Steam Trap (Manual) | RCSteamTrapManualTile | Pułapka parowa |
| 10 | Steam Trap (Auto) | RCSteamTrapAutoTile | Pułapka parowa (auto) |
| 11 | Feed Station | RCFeedStationTile | Karmienie zwierząt |
| 12 | Blast Furnace | RCBlastFurnaceTile | Wieloblok - stal |
| 13 | Passive Anchor | RCPassiveAnchorTile | Chunk loading (pasywny) |
| 14 | Water Tank Siding | RCWaterTankTile | Zbiornik na wodę |
| 15 | Rock Crusher | RCRockCrusherTile | Kruszenie rud |

### 3.2 Maszyny Beta (railcraft.machine.beta) — meta 0-15

| Meta | Nazwa | TE ID | Funkcja |
|------|-------|-------|---------|
| 0 | Iron Tank Wall | RCIronTankWallTile | Wieloblok - ścianka zbiornika |
| 1 | Iron Tank Gauge | RCIronTankGaugeTile | Wieloblok - wskaźnik poziomu |
| 2 | Iron Tank Valve | RCIronTankValveTile | Wieloblok - zawór (I/O) |
| 3 | Low Pressure Boiler Tank | RCBoilerTankLowTile | Wieloblok - kocioł niskiego ciśnienia |
| 4 | High Pressure Boiler Tank | RCBoilerTankHighTile | Wieloblok - kocioł wysokiego ciśnienia |
| 5 | Solid Fueled Firebox | RCBoilerFireboxSoildTile | Wieloblok - palenisko stałe |
| 6 | Liquid Fueled Firebox | RCBoilerFireboxLiquidTile | Wieloblok - palenisko płynne |
| 7 | Hobbyist Steam Engine | RCEngineSteamHobby | Silnik parowy (mały) |
| 8 | Commercial Steam Engine | RCEngineSteamLow | Silnik parowy (średni) |
| 9 | Industrial Steam Engine | RCEngineSteamHigh | Silnik parowy (duży) |
| 10 | Anchor Sentinel | RCAnchorSentinelTile | Rozszerzenie zasięgu anchorów |
| 11 | Void Chest | RCVoidChestTile | Niszczenie itemów |
| 12 | Metals Chest | RCMetalsChestTile | Storage metali |
| 13 | Steel Tank Wall | RCSteelTankWallTile | Wieloblok - ścianka (stal) |
| 14 | Steel Tank Gauge | RCSteelTankGaugeTile | Wieloblok - wskaźnik (stal) |
| 15 | Steel Tank Valve | RCSteelTankValveTile | Wieloblok - zawór (stal) |

### 3.3 Maszyny Gamma (railcraft.machine.gamma) — meta 0-11

| Meta | Nazwa | TE ID | Funkcja |
|------|-------|-------|---------|
| 0 | Item Loader | RCLoaderTile | Ładowanie itemów do wagonów |
| 1 | Item Unloader | RCUnloaderTile | Rozładowywanie itemów |
| 2 | Adv. Item Loader | RCLoaderAdvancedTile | Zaawansowane filtrowanie |
| 3 | Adv. Item Unloader | RCUnloaderAdvancedTile | Zaawansowane filtrowanie |
| 4 | Fluid Loader | RCLoaderTileLiquid | Ładowanie płynów |
| 5 | Fluid Unloader | RCUnloaderTileLiquid | Rozładowywanie płynów |
| 6 | Energy Loader (IC2) | RCLoaderTileEnergy | Ładowanie EU |
| 7 | Energy Unloader (IC2) | RCUnloaderTileEnergy | Rozładowywanie EU |
| 8 | Cart Dispenser | RCMinecartDispenserTile | Wysyłanie wagonów |
| 9 | Train Dispenser | RCTrainDispenserTile | Wysyłanie pociągów |
| 10 | RF Loader | RCLoaderTileRF | Ładowanie RF |
| 11 | RF Unloader | RCUnloaderTileRF | Rozładowywanie RF |

### 3.4 Maszyny Delta (railcraft.machine.delta) — meta 0-1

| Meta | Nazwa | TE ID | Funkcja |
|------|-------|-------|---------|
| 0 | Electric Shunting Wire | RCWireTile | Przewód elektryczny dla torów |
| 1 | Spawner Refill | RCCageTile | Uzupełnianie spawnerów |

### 3.5 Maszyny Epsilon (railcraft.machine.epsilon) — meta 0-5

| Meta | Nazwa | TE ID | Funkcja |
|------|-------|-------|---------|
| 0 | Electric Feeder | RCElectricFeederTile | Zasilanie torów elektrycznych |
| 1 | Admin Electric Feeder | RCElectricFeederAdminTile | Admin zasilanie |
| 2 | Admin Steam Producer | RCAdminSteamProducerTile | Nieskończona para (admin) |
| 3 | Force Track Emitter | RCForceTrackEmitterTile | Emitowanie torów siłowych |
| 4 | Flux Transformer | RCFluxTransformerTile | Konwersja RF ↔ IC2 EU |
| 5 | Engraving Bench | RCEngravingBenchTile | Tworzenie emblematów |

---

## 4. Tory specjalne (TileTrack)

Wszystkie tory Railcrafta używają jednego bloku `railcraft.track` z metadanymi 0-47, ale w NBT TileEntity przechowywany jest `trackTag` (string) określający typ toru.

**Kluczowe NBT torów**:
- `trackTag` (string) — identyfikator toru, np. `"railcraft:track.switch"`
- `trackId` (short) — legacy ID, używane w starszych wersjach zapisu
- Dodatkowe pola zależne od klasy TrackBaseRailcraft (np. kierunek, wysokość, routing)

**Tile Entity IDs**:
- `RailcraftTrackTile` — zwykłe tory
- `RailcraftTrackTESRTile` — tory z renderowaniem TESR (daleki zasięg renderowania)

---

## 5. Sygnały kolejowe (BlockSignalRailcraft)

Blok `railcraft.signal.*` (w rzeczywistości jeden blok z meta 0-13 w zależności od implementacji).

| Meta | Nazwa | TE ID |
|------|-------|-------|
| 0 | Interlock Box | RCTileStructureInterlockBox |
| 1 | Dual-Head Block Signal | RCTileStructureDualHeadBlockSignal |
| 2 | Switch Motor | RCTileStructureSwitchMotor |
| 3 | Block Signal | RCTileStructureBlockSignal |
| 4 | Switch Lever | RCTileStructureSwitchLever |
| 5 | Routing Switch Motor | RCTileStructureSwitchRouting |
| 6 | Sequencer Box | RCTileStructureSequencerBox |
| 7 | Capacitor Box | RCTileStructureCapacitorBox |
| 8 | Receiver Box | RCTileStructureReceiverBox |
| 9 | Controller Box | RCTileStructureControllerBox |
| 10 | Analog Controller Box | RCTileStructureAnalogBox |
| 11 | Distant Signal | RCTileStructureDistantSignal |
| 12 | Dual-Head Distant Signal | RCTileStructureDualHeadDistantSignal |
| 13 | Signal Block Relay | RCTileStructureSignalBox |

---

## 6. Detektory (BlockDetector)

Blok `railcraft.detector` z meta 0-16. Wszystkie warianty używają tej samej klasy TileEntity:
- `RCDetectorTile`

---

## 7. Bloki ignorowane

| Block/TE ID | Powód |
|-------------|-------|
| `RCHiddenTile` (railcraft.residual.heat) | Ślad gracza Railcrafta — efekt wizualny, brak funkcjonalności do przeniesienia |

---

## 8. Struktury NBT — kluczowe pola wspólne

### RailcraftTileEntity (bazowa)
- `x`, `y`, `z` (int) — pozycja
- `id` (string) — TileEntity ID

### TileMachineBase (bazowa dla maszyn)
- `owner` (string / UUID) — właściciel
- `facing` (byte) — orientacja

### TileMultiBlock (maszyny wieloblokowe: Coke Oven, Blast Furnace, Boiler, Tank)
- `master` (boolean) — czy to blok master
- `pattern` / `parts` — dane o strukturze wielobloku

### TileMachineItem (maszyny z inventory)
- `Items` (NBTTagList) — inventory (format 1.7.10)

### TileTrack (tory)
- `trackTag` (string) — typ toru
- `trackId` (short) — legacy ordinal

---

## 9. Utworzone pliki

- `src/converters/railcraft/__init__.py` — inicjalizacja modułu
- `src/converters/railcraft/mappings/__init__.py` — inicjalizacja podmodułu
- `src/converters/railcraft/mappings/block_inventory.py` — pełna inwentaryzacja bloków/TE (140+ bloków, 75 TE ID)

---

## 10. Następne kroki (Zadanie 2)

1. **Przygotować symulacje funkcjonalności** w Pythonie dla:
   - Sieci torów i sygnałów (routing, sterowanie zwrotnicami)
   - Maszyn wieloblokowych (Coke Oven, Blast Furnace, Boiler, Tanks)
   - Systemu anchorów (chunk loading)
   - Loadery/Unloaderzy (automatyzacja transportu)

2. **Zbadać kody źródłowe Railcraft Reborn 1.18.2** — jakie są odpowiedniki bloków i jak wyglądają ich NBT/BlockState

3. **Przygotować tabelę mapowań** `block_mappings.py` z konkretnymi mapowaniami:
   - `railcraft:track.switch` → `railcraft:track_flex` (do weryfikacji w Reborn)
   - `railcraft:machine.alpha.coke.oven` → `railcraft:coke_oven`
   - `railcraft:machine.alpha.blast.furnace` → `railcraft:blast_furnace`
   - `railcraft:machine.alpha.rolling.machine` → `railcraft:rolling_machine`

---

*Dokument utworzony: 2026-05-20*
*Źródła: Dekompilacja Railcraft 9.12.2.0 (vineflower), dokumentacja projektu, analiza strefy Choroszcz*
