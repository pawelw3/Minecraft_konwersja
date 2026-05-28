# Analiza moda Traincraft 1.7.10 → Create + Steam'n'Rails 1.18.2 (Zadanie 1)

## 1.7.10 — Bloki

### `tc:distilIdle` / `tc:distilActive`
- **Typ:** Block
- **Klasa Java:** `train.common.blocks.BlockDistil`
- **Opis:** Rafineria (destylacja). Wersja idle (wyłączona) i active (włączona, emituje światło 0.8F). Przetwarza surowce na paliwo.
- **Dowód z kodu (rejestracja):** `TCBlocks.java:29-30` → `GameRegistry.registerBlock(blocks.block, blocks.name())`
- **Tile Entity:** `TileEntityDistil` ("Tile Distil")

### `tc:assemblyTableI` / `tc:assemblyTableII` / `tc:assemblyTableIII`
- **Typ:** Block
- **Klasa Java:** `train.common.blocks.BlockAssemblyTableI/II/III`
- **Opis:** Stoły montażowe (Tier I drewno, Tier II/III kamień). Służą do craftowania części pociągów.
- **Dowód z kodu (rejestracja):** `TCBlocks.java:33-35`
- **Tile Entity:** `TileCrafterTierI/II/III`

### `tc:trainWorkbench`
- **Typ:** Block
- **Klasa Java:** `train.common.blocks.BlockTrainWorkbench`
- **Opis:** Warsztat kolejowy z GUI.
- **Tile Entity:** `TileTrainWbench` ("TileTrainWbench")

### `tc:stopper`
- **Typ:** Block
- **Klasa Java:** `train.common.blocks.BlockStopper`
- **Opis:** Blok zatrzymujący pociągi (kozioł oporowy).
- **Tile Entity:** `TileStopper` ("TileStopper")

### `tc:openFurnaceIdle` / `tc:openFurnaceActive`
- **Typ:** Block
- **Klasa Java:** `train.common.blocks.BlockOpenHearthFurnace`
- **Opis:** Piec hutniczy (Open Hearth Furnace).
- **Tile Entity:** `TileEntityOpenHearthFurnace` ("Tile OpenHearthFurnace")

### `tc:oreTC`
- **Typ:** Block
- **Klasa Java:** `train.common.blocks.BlockOreTC`
- **Opis:** Rudy dodawane przez Traincraft (miedź, stal, itp.).
- **ItemBlock:** `ItemBlockOreTC`

### `tc:lantern`
- **Typ:** Block
- **Klasa Java:** `train.common.blocks.BlockLantern`
- **Opis:** Latarnia kolejowa, emituje światło 0.98F.
- **Tile Entity:** `TileLantern` ("tileLantern")

### `tc:switchStand`
- **Typ:** Block
- **Klasa Java:** `train.common.blocks.BlockSwitchStand`
- **Opis:** Mechaniczna dźwignia zwrotnicy.
- **Tile Entity:** `TileSwitchStand` ("tileSwitchStand")

### `tc:waterWheel` / `tc:windMill`
- **Typ:** Block
- **Klasa Java:** `train.common.blocks.BlockWaterWheel` / `BlockWindMill`
- **Opis:** Koło wodne / wiatrak do generowania energii.
- **Tile Entity:** `TileWaterWheel` ("tileWaterWheel") / `TileWindMill` ("tileWindMill")

### `tc:generatorDiesel`
- **Typ:** Block
- **Klasa Java:** `train.common.blocks.BlockGeneratorDiesel`
- **Opis:** Generator diesla.
- **Tile Entity:** `TileGeneratorDiesel` ("tileGeneratorDiesel")

### `tc:tcRail` ⭐ KLUCZOWY BLOK TORU
- **Typ:** Block
- **Klasa Java:** `train.common.blocks.BlockTCRail`
- **Registry name:** `tc:tcRail`
- **Opis:** Główny blok toru Traincraft. Przechowuje w TileEntity typ toru, orientację, parametry krzywej (r, cx, cy, cz), nachylenie, stan zwrotnicy. Każdy blok tcRail to 1 blok fizyczny (16×16×16), ale wysokość collision to 0.125F. Dla torów wieloblokowych (zakręty, zwrotnice) ten blok jest głównym blokiem, a pozostałe to `tcRailGag`.
- **Dowód z kodu (rejestracja):** `TCBlocks.java:50` → `BlockIDs.tcRail.block = new BlockTCRail()`
- **Tile Entity:** `TileTCRail` ("tileTCRail")
- **Block bounds:** `0.0F, 0.0F, 0.0F, 1.0F, 0.125F, 1.0F`

### `tc:tcRailGag` ⭐ BLOK GAG DLA TORÓW WIELOBLK.
- **Typ:** Block
- **Klasa Java:** `train.common.blocks.BlockTCRailGag`
- **Registry name:** `tc:tcRailGag`
- **Opis:** "Gag block" — niewidzialny blok techniczny zajmujący dodatkowe pozycje w przestrzeni dla torów wieloblokowych (zakręty, zwrotnice, nachylenia). Gdy główny blok toru jest zniszczony, gag jest również usuwany ( przez `originX/Y/Z` w TileTCRailGag). `bbHeight` kontroluje wysokość kolizji (dla pochylenia rośnie od 0.125 do 1.0).
- **Dowód z kodu (rejestracja):** `TCBlocks.java:51`
- **Tile Entity:** `TileTCRailGag` ("tileTCRailGag")

### `tc:bridgePillar`
- **Typ:** Block
- **Klasa Java:** `train.common.blocks.BlockBridgePillar`
- **Opis:** Filar mostu kolejowego.
- **Tile Entity:** `TileBridgePillar` ("tileTCBridgePillar")

### `tc:diesel` / `tc:refinedFuel`
- **Typ:** Block (Fluid)
- **Klasa Java:** `train.common.blocks.BlockTraincraftFluid`
- **Opis:** Bloki płynów (ropa, paliwo).

### MTC Blocks (opcjonalne, jeśli ComputerCraft/OpenComputers)
- `tc:mtcTransmitterSpeed`, `tc:mtcTransmitterMTC`, `tc:mtcATOStopTransmitter`, `tc:mtcReceiverMTC`, `tc:mtcReceiverDestination`, `tc:pdmInstructionBlock`

---

## 1.7.10 — Tile Entities

| Nazwa wyświetlana | Klasa Java | Registry String | Ma prefiks? |
|---|---|---|---|
| Assembly Table I | `TileCrafterTierI` | `"TileCrafterTierI"` | NIE |
| Assembly Table II | `TileCrafterTierII` | `"TileCrafterTierII"` | NIE |
| Assembly Table III | `TileCrafterTierIII` | `"TileCrafterTierIII"` | NIE |
| Train Workbench | `TileTrainWbench` | `"TileTrainWbench"` | NIE |
| Distil | `TileEntityDistil` | `"Tile Distil"` | NIE (spacja!) |
| Open Hearth Furnace | `TileEntityOpenHearthFurnace` | `"Tile OpenHearthFurnace"` | NIE (spacja!) |
| Stopper | `TileStopper` | `"TileStopper"` | NIE |
| Signal | `TileSignal` | `"TileTrainSignal"` | NIE |
| Lantern | `TileLantern` | `"tileLantern"` | NIE (małe litery) |
| Switch Stand | `TileSwitchStand` | `"tileSwitchStand"` | NIE |
| Water Wheel | `TileWaterWheel` | `"tileWaterWheel"` | NIE |
| Wind Mill | `TileWindMill` | `"tileWindMill"` | NIE |
| Diesel Generator | `TileGeneratorDiesel` | `"tileGeneratorDiesel"` | NIE |
| Book | `TileBook` | `"tileBook"` | NIE |
| TC Rail Gag | `TileTCRailGag` | `"tileTCRailGag"` | NIE |
| **TC Rail** ⭐ | `TileTCRail` | `"tileTCRail"` | NIE |
| Bridge Pillar | `TileBridgePillar` | `"tileTCBridgePillar"` | NIE |
| MTC Speed Transmitter | `TileInfoTransmitterSpeed` | `"tileInfoTransmitterSpeed"` | NIE |
| MTC Status Transmitter | `TileInfoTransmitterMTC` | `"tileInfoTransmitterMTC"` | NIE |
| MTC ATO Stop | `TileATOTransmitterStopPoint` | `"tileATOTransmitterStopPoint"` | NIE |
| MTC Receiver | `TileInfoGrabberMTC` | `"tileInfoReceiverMTC"` | NIE |
| MTC Destination Receiver | `TileInfoGrabberDestination` | `"tileInfoReceiverDestination"` | NIE |
| PDM Radio | `TilePDMInstructionRadio` | `"tilePDMInstructionRadio"` | NIE |

**Kluczowe:** Wszystkie tile entities Traincraft są rejestrowane **BEZ prefiksu moda** (`tc:`). W plikach .mca należy szukać dokładnych stringów jak `"tileTCRail"`, `"tileTCRailGag"`, `"Tile Distil"` itp.

---

## 1.7.10 — Typy torów (TrackTypes) i ich fizyczne zajęcie bloków

Zdefiniowane w `ItemTCRail.TrackTypes` (`ItemTCRail.java`):

| Typ | Kategoria | Rozmiar tooltip | Fizyczne bloki (tcRail + tcRailGag) |
|---|---|---|---|
| `SMALL_STRAIGHT` | STRAIGHT | 1×1 | **1** (1 tcRail, 0 gag) |
| `SMALL_ROAD_CROSSING` | STRAIGHT | 1×1 | **1** |
| `SMALL_ROAD_CROSSING_1` | STRAIGHT | 1×1 | **1** |
| `SMALL_ROAD_CROSSING_2` | STRAIGHT | 1×1 | **1** |
| `MEDIUM_STRAIGHT` | STRAIGHT | 1×3 | **3** (1 tcRail + 2 gag w linii) |
| `LONG_STRAIGHT` | STRAIGHT | 1×6 | **6** (2 tcRail + 4 gag) |
| `MEDIUM_TURN` / `MEDIUM_RIGHT_TURN` / `MEDIUM_LEFT_TURN` | TURN | 3×3 | **5** (1 tcRail + 4 gag) |
| `LARGE_TURN` / `LARGE_RIGHT_TURN` / `LARGE_LEFT_TURN` | TURN | 5×5 | **12** (1 tcRail + 11 gag) |
| `VERY_LARGE_TURN` / `VERY_LARGE_RIGHT_TURN` / `VERY_LARGE_LEFT_TURN` | TURN | 10×10 | **25** (1 tcRail + 24 gag) |
| `MEDIUM_SWITCH` / `MEDIUM_RIGHT_SWITCH` / `MEDIUM_LEFT_SWITCH` | SWITCH | 4×4 | **7** (turn: 1 tcRail+2 gag + switch rails: 3 tcRail + straight exit: 1 tcRail) |
| `LARGE_SWITCH` / `LARGE_RIGHT_SWITCH` / `LARGE_LEFT_SWITCH` | SWITCH | 6×6 | **14** (turn: 1 tcRail+8 gag + switch rails: 3 tcRail + straight exit: 2 tcRail) |
| `MEDIUM_PARALLEL_SWITCH` / `MEDIUM_RIGHT_PARALLEL_SWITCH` / `MEDIUM_LEFT_PARALLEL_SWITCH` | SWITCH | 4×11 | **~22** (dwa turny + straight bloki) |
| `TWO_WAYS_CROSSING` | CROSSING | 3×3 | **?** (krzyżowanie dwukierunkowe) |
| `SLOPE_WOOD` / `SLOPE_GRAVEL` / `SLOPE_BALLAST` | SLOPE | 1×6 | **6** (1 tcRail + 5 gag w linii, bbHeight rośnie) |
| `LARGE_SLOPE_*` | SLOPE | 1×12 | **12** (1 tcRail + 11 gag) |
| `VERY_LARGE_SLOPE_*` | SLOPE | 1×18 | **18** (1 tcRail + 17 gag) |

---

## 1.18.2 — Bloki (Create + Steam'n'Rails)

### Create: podstawowe tory

| Registry Name | Klasa Java | Opis |
|---|---|---|
| `create:track` | `TrackBlock` | Główny blok toru. Właściwości: `shape` (TrackShape), `turn` (HAS_BE = czy ma BlockEntity z krzywą Beziera), `waterlogged`. Prosty tor = 1 blok bez BE. Zakręt/łuk = 1 blok + `TrackBlockEntity` z `BezierConnection`. |
| `create:fake_track` | `FakeTrackBlock` | Niewidzialny blok techniczny generowany dynamicznie wzdłuż krzywych torów (zapobiega stawianiu bloków na trasie). Nie zachowuje się w NBT — regeneruje się przy ładowaniu chunka. |
| `create:track_observer` | `TrackObserverBlock` | Blok obserwujący pociągi, emituje redstone. |
| `create:track_station` | `StationBlock` | Stacja kolejowa (do składania/rozłączania pociągów). |
| `create:track_signal` | `SignalBlock` | Sygnalizator kolejowy (entry/cross). |
| `create:small_bogey` / `create:large_bogey` | `StandardBogeyBlock` | Wózki kolejowe. |

### Steam'n'Rails: rozszerzone tory

| Registry Name | Klasa Java | Opis |
|---|---|---|
| `railways:track_oak` / `track_spruce` / `track_birch` / ... (16+) | `CustomTrackBlock` | Tory standardowe z różnych materiałów. Wszystkie dziedziczą z `TrackBlock` i używają `create:track` BE. |
| `railways:track_monorail` | `MonorailTrackBlock` | Tor jednoszynowy. Pełna kolizja (0,0,0 do 16,15,16). |
| `railways:track_*_wide` | `WideGaugeTrackBlock` | Tory szerokotorowe (~90+ wariantów). |
| `railways:track_*_narrow` | `NarrowGaugeTrackBlock` | Tory wąskotorowe (~90+ wariantów). |
| `railways:track_coupler` | `TrackCouplerBlock` | Sprzęgacz/rozłączacz wagonów. |
| `railways:track_switch_andesite` | `TrackSwitchBlock` | Zwrotnica manualna. |
| `railways:track_switch_brass` | `TrackSwitchBlock` | Zwrotnica automatyczna. |
| `railways:buffer` / `buffer_narrow` / `buffer_mono` / `buffer_wide` | `TrackBufferBlock` | Bufory końcowe torów (visual-only, no collision). |
| `railways:generic_crossing` | `GenericCrossingBlock` | Krzyżowanie. |
| `railways:casing_collision` | `CasingCollisionBlock` | Niewidzialny blok pod torami z obudową (casing). |

### Steam'n'Rails: block entities

| Registry Name | Klasa Java | Obsługiwane bloki |
|---|---|---|
| `railways:track_coupler` | `TrackCouplerBlockEntity` | `track_coupler` |
| `railways:track_buffer` | `TrackBufferBlockEntity` | `buffer_wide` |
| `railways:track_buffer_wood_variant` | `WoodVariantTrackBufferBlockEntity` | `buffer`, `buffer_narrow`, `buffer_mono` |
| `railways:track_switch_andesite` | `TrackSwitchBlockEntity` | `track_switch_andesite` |
| `railways:track_switch_brass` | `TrackSwitchBlockEntity` | `track_switch_brass` |
| `railways:generic_crossing` | `GenericCrossingBlockEntity` | `generic_crossing` |
| `railways:casing_collision` | `CasingCollisionBlockEntity` | `casing_collision` |

**Kluczowe:** Tory Steam'n'Rails NIE mają własnego typu BE. Są dodawane do `create:track` BE przez `CRTrackMaterials.addToBlockEntityType()`.

---

## Porównanie 1.7.10 vs 1.18.2

### Filozofia torów

| Aspekt | Traincraft 1.7.10 | Create 1.18.2 + Steam'n'Rails |
|---|---|---|
| **Model fizyczny** | Wieloblokowy: `tcRail` + `tcRailGag` dla każdej pozycji | Single-block + krzywe Beziera w BlockEntity |
| **Zakręt 3×3** | 5 fizycznych bloków (1 tcRail + 4 gag) | 1 blok `TrackBlock` z `turn=true` + `BezierConnection` w BE. Dodatkowo `fake_track` generowane dynamicznie wzdłuż krzywej. |
| **Zakręt 5×5** | 12 fizycznych bloków | 1-2 bloki `TrackBlock` (endpointy) + krzywa Beziera |
| **Zwrotnica** | Multi-blok z `switchActive` w TileTCRail, zmienia typ sąsiednich bloków | Zwrotnica to osobny blok `track_switch_andesite` (1 blok) + logika w graphie torów |
| **Nachylenie (slope)** | 6-18 bloków w linii, `bbHeight` rośnie w gagach | `TrackShape` enum: `AN`, `AS`, `AE`, `AW` (ascending) — 1 blok, brak kolizji (`Shapes.empty()`) |
| **Krzyżowanie** | `TWO_WAYS_CROSSING` — multi-blok | `TrackShape.CR_O`, `CR_D`, `CR_PDX`, `CR_PDZ`, `CR_NDX`, `CR_NDZ` — 1 blok |
| **Redstone** | `previousRedstoneState` w TileTCRail zmienia `switchState` | `TrackObserverBlock` emituje sygnał redstone |

### Konwersja — wyzwania

1. **Wieloblokowość Traincraft → single-block Create:** Zakręty Traincraft zajmujące 5-25 bloków muszą zostać zredukowane do 1-2 bloków `create:track` z `BezierConnection`. Pozostałe bloki (`tcRailGag`) muszą zostać usunięte lub zamienione na inne bloki.

2. **Zwrotnice:** W Traincraft zwrotnica to złożony układ multi-blokowy ze zmiennymi typami sąsiednich bloków (zmiana `SMALL_STRAIGHT` ↔ `MEDIUM_*_TURN`). W Create zwrotnica to osobny blok `track_switch_andesite/brass` (1 blok) + podłączony do niego graf torów.

3. **Nachylenia:** Slope w Traincraft to fizyczny ciąg 6-18 bloków z rosnącą wysokością kolizji. W Create slope to 1 blok z `TrackShape.AE/AW/AN/AS` (bez kolizji — pociąg jedzie po krzywej 3D wewnątrz grafu).

4. **Dane NBT:** Traincraft przechowuje `r`, `cx`, `cy`, `cz`, `slopeAngle`, `switchActive` w TileTCRail. Create przechowuje `Connections` (lista `BezierConnection`) w `TrackBlockEntity`.

5. **Gagi bez NBT zwrotnego:** `tcRailGag` ma tylko `originX/Y/Z`, `bbHeight`, `type` — nie ma pełnej informacji o geometrii. Konwersja musi odczytać główny `tcRail` i na jego podstawie zrekonstruować krzywą.

---

## Źródła z internetu

- Traincraft Wiki (archiwum): https://traincraft.fandom.com/wiki/Tracks — potwierdza typy torów (Small Straight, Medium Straight, Long Straight, Medium/Large/Very Large Turn, Switches, Slopes) oraz ich rozmiary.
- Create Wiki — Trains: https://wiki.createmod.net/users/trains/tracks — opisuje system torów Create: blockstates `shape`, `turn`, krzywe Beziera, `fake_track`.
- Create Steam 'n' Rails Wiki: https://github.com/Layers-of-Railways/Railway/wiki — opisuje dodatkowe tory (narrow, wide, monorail), bufory, zwrotnice.

---

## Pliki źródłowe referencyjne

### Traincraft 1.7.10
- `mod_src/1710/actual_src/1.7.10/Traincraft/repo/src/main/java/train/common/blocks/TCBlocks.java` — rejestracja bloków
- `mod_src/1710/actual_src/1.7.10/Traincraft/repo/src/main/java/train/common/core/CommonProxy.java` — rejestracja TE (linie 69-95)
- `mod_src/1710/actual_src/1.7.10/Traincraft/repo/src/main/java/train/common/blocks/BlockTCRail.java` — blok toru
- `mod_src/1710/actual_src/1.7.10/Traincraft/repo/src/main/java/train/common/blocks/BlockTCRailGag.java` — blok gag
- `mod_src/1710/actual_src/1.7.10/Traincraft/repo/src/main/java/train/common/tile/TileTCRail.java` — TE toru (NBT, switch state)
- `mod_src/1710/actual_src/1.7.10/Traincraft/repo/src/main/java/train/common/tile/TileTCRailGag.java` — TE gagu
- `mod_src/1710/actual_src/1.7.10/Traincraft/repo/src/main/java/train/common/items/ItemTCRail.java` — definicja typów torów i kod stawiania

### Create 1.18.2
- `mod_src/118/actual_src/1.18.2/Create/repo/src/main/java/com/simibubi/create/content/trains/track/TrackBlock.java`
- `mod_src/118/actual_src/1.18.2/Create/repo/src/main/java/com/simibubi/create/content/trains/track/TrackBlockEntity.java`
- `mod_src/118/actual_src/1.18.2/Create/repo/src/main/java/com/simibubi/create/content/trains/track/TrackShape.java`
- `mod_src/118/actual_src/1.18.2/Create/repo/src/main/java/com/simibubi/create/content/trains/track/BezierConnection.java`

### Steam'n'Rails 1.18.2
- `mod_src/118/actual_src/1.18.2/CreateSteamNRails/repo/common/src/main/java/com/railwayteam/railways/registry/CRBlocks.java`
- `mod_src/118/actual_src/1.18.2/CreateSteamNRails/repo/common/src/main/java/com/railwayteam/railways/registry/CRTrackMaterials.java`
- `mod_src/118/actual_src/1.18.2/CreateSteamNRails/repo/common/src/main/java/com/railwayteam/railways/content/custom_tracks/CustomTrackBlock.java`
- `mod_src/118/actual_src/1.18.2/CreateSteamNRails/repo/common/src/main/java/com/railwayteam/railways/content/switches/TrackSwitchBlock.java`
