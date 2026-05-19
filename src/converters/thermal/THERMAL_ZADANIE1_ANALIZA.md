# Thermal Series - Zadanie 1: bloki, Tile Entities i porownanie 1.7.10 -> 1.18.2

> Zakres: **Thermal Expansion 4.1.5**, **Thermal Foundation 1.2.6**, **Thermal Dynamics 1.2.1** (1.7.10) -> **Thermal Series 9.2.2** (1.18.2)
> Data analizy: 2026-05-19.
> Status: analiza rejestracji i funkcji, bez pisania kodu konwersji.

---

## 1. Informacje ogolne

### 1.1 Thermal Series 1.7.10
- **Thermal Expansion**: 4.1.5-248 — maszyny, dynama, storage, urzadzenia
- **Thermal Foundation**: 1.2.6-118 — rudy, bloki surowcowe, plyny
- **Thermal Dynamics**: 1.2.1-172 — transport energii, plynow, itemow (ducty)
- **Zaleznosci**: CoFHCore

### 1.2 Thermal Series 1.18.2
- **Thermal Expansion**: 9.2.2.24
- **Thermal Foundation**: 9.2.2.58
- **Thermal Dynamics**: 9.2.2.19
- **Zaleznosci**: CoFH Core, Thermal Foundation (baza)

---

## 2. Zrodla i walidacja

| Wersja | Zrodlo | Status |
|---|---|---|
| 1.7.10 | `modpack_1710/ThermalExpansion-[1.7.10]4.1.5-248.jar` | glowny dowod: javap |
| 1.7.10 | `modpack_1710/ThermalFoundation-[1.7.10]1.2.6-118.jar` | glowny dowod: javap |
| 1.7.10 | `modpack_1710/ThermalDynamics-[1.7.10]1.2.1-172.jar` | glowny dowod: javap |
| 1.18.2 | `mod_src/118/mod_jars/thermal_expansion-1.18.2-9.2.2.24.jar` | glowny dowod: blockstates |
| 1.18.2 | `mod_src/118/mod_jars/thermal_foundation-1.18.2-9.2.2.58.jar` | glowny dowod: blockstates |
| 1.18.2 | `mod_src/118/mod_jars/thermal_dynamics-1.18.2-9.2.2.19.jar` | glowny dowod: blockstates |

Zrodla internetowe:
- https://teamcofh.com/docs/thermal-expansion/ — dokumentacja maszyn i dynam
- https://teamcofh.com/docs/thermal-dynamics/ — dokumentacja ductow
- https://teamcofh.com/docs/thermal-foundation/ — dokumentacja surowcow

---

## 3. Thermal Expansion 1.7.10 — bloki i Tile Entities

### 3.1 Bloki z metadata (grupowane registry ID)

#### `ThermalExpansion:Machine` (blockMachine)
| Meta | Nazwa (NAMES[]) | Tile Entity ID | Funkcja | TE klasa |
|---:|---|---|---|---|
| 0 | Furnace | `thermalexpansion.Furnace` | Redstone Furnace — przetapianie itemow | TileFurnace |
| 1 | Pulverizer | `thermalexpansion.Pulverizer` | Pulverizer — kruszenie rud -> pyly | TilePulverizer |
| 2 | Sawmill | `thermalexpansion.Sawmill` | Sawmill — ciecie drewna | TileSawmill |
| 3 | Smelter | `thermalexpansion.Smelter` | Induction Smelter — przetapianie z dodatkami | TileSmelter |
| 4 | Crucible | `thermalexpansion.Crucible` | Magma Crucible — roztapianie itemow w plyny | TileCrucible |
| 5 | Transposer | `thermalexpansion.Transposer` | Fluid Transposer — napelnianie/oproznianie plynow | TileTransposer |
| 6 | Precipitator | `thermalexpansion.Precipitator` | Glacial Precipitator — produkcja lodu/sniegu | TilePrecipitator |
| 7 | Extruder | `thermalexpansion.Extruder` | Igneous Extruder — generowanie blokow kamiennych | TileExtruder |
| 8 | Accumulator | `thermalexpansion.Accumulator` | Aqueous Accumulator — gromadzenie wody | TileAccumulator |
| 9 | Assembler | `thermalexpansion.Assembler` | Sequential Fabricator — auto-crafting | TileAssembler |
| 10 | Charger | `thermalexpansion.Charger` | Energetic Infuser — ladowanie itemow energia | TileCharger |
| 11 | Insolator | `thermalexpansion.Insolator` | Phytogenic Insolator — uprawa roslin | TileInsolator |

#### `ThermalExpansion:Device` (blockDevice)
| Meta | Nazwa (NAMES[]) | Tile Entity ID | Funkcja | TE klasa |
|---:|---|---|---|---|
| 0 | Workbench | `thermalexpansion.Workbench` | Tinker's Workbench (false=nieuzywany) | TileWorkbenchFalse |
| 1 | Pump | `thermalexpansion.Pump` | Fluid Pump — pompowanie plynow | TilePump |
| 2 | Activator | `thermalexpansion.Activator` | Autonomous Activator — symulacja klikania | TileActivator |
| 3 | Breaker | `thermalexpansion.Breaker` | Terrain Smasher — niszczenie blokow | TileBreaker |
| 4 | Collector | `thermalexpansion.Collector` | Vacuumulator — zbieranie dropow | TileCollector |
| 5 | Nullifier | `thermalexpansion.Nullifier` | Item Nullifier — niszczenie itemow | TileNullifier |
| 6 | Buffer | `thermalexpansion.Buffer` | Item Buffer — buforowanie itemow | TileBuffer |
| 7 | Extender | `thermalexpansion.Extender` | Energy Cell (Extender?) — rozdzielanie energii | TileExtender |

#### `ThermalExpansion:Dynamo` (blockDynamo)
| Meta | Nazwa (NAMES[]) | Tile Entity ID | Funkcja | TE klasa |
|---:|---|---|---|---|
| 0 | Steam | `thermalexpansion.DynamoSteam` | Steam Dynamo — generator na pare/wode | TileDynamoSteam |
| 1 | Magmatic | `thermalexpansion.DynamoMagmatic` | Magmatic Dynamo — generator na lawe | TileDynamoMagmatic |
| 2 | Compression | `thermalexpansion.DynamoCompression` | Compression Dynamo — generator na paliwa ciekle | TileDynamoCompression |
| 3 | Reactant | `thermalexpansion.DynamoReactant` | Reactant Dynamo — generator na reakcje chemiczne | TileDynamoReactant |
| 4 | Enervation | `thermalexpansion.DynamoEnervation` | Enervation Dynamo — generator na itemy energetyczne | TileDynamoEnervation |

#### `ThermalExpansion:Cell` (blockCell)
| Meta | Tile Entity ID | Funkcja | TE klasa |
|---:|---|---|---|
| 0-4 (tier) | `thermalexpansion.Cell` | Energy Cell — magazyn RF | TileCell |
| creative | `thermalexpansion.CellCreative` | Creative Energy Cell | TileCellCreative |

#### `ThermalExpansion:Tank` (blockTank)
| Meta | Tile Entity ID | Funkcja | TE klasa |
|---:|---|---|---|
| 0-4 (tier) | `thermalexpansion.Tank` | Portable Tank — magazyn plynow | TileTank |
| creative | `thermalexpansion.TankCreative` | Creative Portable Tank | TileTankCreative |

#### `ThermalExpansion:Strongbox` (blockStrongbox)
| Meta | Tile Entity ID | Funkcja | TE klasa |
|---:|---|---|---|
| 0-4 (tier) | `thermalexpansion.Strongbox` | Strongbox — skrzynia z tierami | TileStrongbox |
| creative | `thermalexpansion.StrongboxCreative` | Creative Strongbox | TileStrongboxCreative |

#### `ThermalExpansion:Cache` (blockCache)
| Meta | Tile Entity ID | Funkcja | TE klasa |
|---:|---|---|---|
| 0-4 (tier) | `thermalexpansion.Cache` | Cache — magazyn 1 typu itemu (stack xN) | TileCache |

#### `ThermalExpansion:Workbench` (blockWorkbench — NOWY, nie mylic z Device)
| Meta | Tile Entity ID | Funkcja | TE klasa |
|---:|---|---|---|
| 0-4 (tier) | `thermalexpansion.NewWorkbench` | Tinker's Workbench (crafting z energia?) | TileWorkbench |
| creative | `thermalexpansion.WorkbenchCreative` | Creative Workbench | TileWorkbenchCreative |

#### `ThermalExpansion:Tesseract` (blockTesseract)
| Meta | Tile Entity ID | Funkcja | TE klasa |
|---:|---|---|---|
| 0 | `thermalexpansion.Tesseract` | Tesseract — teleportacja energii/plynow/itemow | TileTesseract |

#### `ThermalExpansion:Plate` (blockPlate)
| Meta | Tile Entity ID | Funkcja | TE klasa |
|---:|---|---|---|
| 0 | `cofh.thermalexpansion.PlateFrame` | Plate Frame — rama plyty | TilePlateBase |
| 1 | `cofh.thermalexpansion.PlateCharger` | Flux Charger — ladowanie w obszarze | TilePlateCharge |
| 2 | `cofh.thermalexpansion.PlateExcursion` | Excursion Plate — wyrzucanie entity | TilePlateExcursion |
| 3 | `cofh.thermalexpansion.PlateImpulse` | Impulse Plate — przyspieszanie entity | TilePlateImpulse |
| 4 | `cofh.thermalexpansion.PlateSignal` | Reinforced Plate — redstone signal? | TilePlateSignal |
| 5 | `cofh.thermalexpansion.PlateTeleporter` | Teleport Plate — teleportacja | TilePlateTeleporter |
| 6 | `cofh.thermalexpansion.PlateTranslocate` | Translocation Plate — przemieszczanie entity | TilePlateTranslocate |

#### `ThermalExpansion:Light` (blockLight)
| Meta | Tile Entity ID | Funkcja | TE klasa |
|---:|---|---|---|
| 0 | `thermalexpansion.Light` | Glowstone Illuminator — swiatlo | TileLight |
| 1 | `thermalexpansion.LightFalse` | fake light? | TileLightFalse |

#### `ThermalExpansion:Sponge` (blockSponge)
| Meta | Tile Entity ID | Funkcja | TE klasa |
|---:|---|---|---|
| 0 | `thermalexpansion.Sponge` | Sponge — pochlanianie wody | TileSponge |
| 1 | `thermalexpansion.SpongeMagmatic` | Magmatic Sponge — pochlanianie lawy | TileSpongeMagmatic |
| 2 | `thermalexpansion.SpongeCreative` | Creative Sponge | TileSpongeCreative |

### 3.2 Bloki bez Tile Entity (simple/dekoracyjne)

| Registry ID | Klasa | Opis |
|---|---|---|
| `ThermalExpansion:Frame` | BlockFrame | Ramy maszyn (crafting) |
| `ThermalExpansion:Glass` | BlockGlass | Hardened Glass |
| `ThermalExpansion:Rockwool` | BlockRockwool | Wegiel/rockwool (kolory) |
| `ThermalExpansion:AirSignal` | BlockAirSignal | Techniczny (powietrze sygnalizacyjne) |
| `ThermalExpansion:AirLight` | BlockAirLight | Techniczny (powietrze swietlne) |
| `ThermalExpansion:AirForce` | BlockAirForce | Techniczny (powietrze sily?) |
| `ThermalExpansion:AirBarrier` | BlockAirBarrier | Techniczny (bariera powietrzna) |

---

## 4. Thermal Foundation 1.7.10 — bloki

Thermal Foundation **nie ma Tile Entities** w 1.7.10. Wszystkie bloki to bloki proste.

| Registry ID | Klasa | Opis |
|---|---|---|
| `ThermalFoundation:Ore` | BlockOre | Rudy: Copper, Tin, Silver, Lead, Nickel, Platinum, Mithril (meta 0-7) |
| `ThermalFoundation:Storage` | BlockStorage | Bloki surowcowe (meta 0-15) |
| `ThermalFoundation:fluidRedstone` | BlockFluidCoFHBase | Destabilized Redstone (plyn) |
| `ThermalFoundation:fluidGlowstone` | BlockFluidCoFHBase | Energized Glowstone (plyn) |
| `ThermalFoundation:fluidEnder` | BlockFluidCoFHBase | Resonant Ender (plyn) |
| `ThermalFoundation:fluidPyrotheum` | BlockFluidCoFHBase | Blazing Pyrotheum (plyn) |
| `ThermalFoundation:fluidCryotheum` | BlockFluidCoFHBase | Gelid Cryotheum (plyn) |
| `ThermalFoundation:fluidAerotheum` | BlockFluidCoFHBase | Zephyrean Aerotheum (plyn) |
| `ThermalFoundation:fluidPetrotheum` | BlockFluidCoFHBase | Tectonic Petrotheum (plyn) |
| `ThermalFoundation:fluidMana` | BlockFluidCoFHBase | Primal Mana (plyn) |
| `ThermalFoundation:fluidSteam` | BlockFluidCoFHBase | Steam (plyn) |
| `ThermalFoundation:fluidCoal` | BlockFluidCoFHBase | Liquifacted Coal (plyn) |

---

## 5. Thermal Dynamics 1.7.10 — Ducty i Tile Entities

Thermal Dynamics uzywa systemu `blockDuct[]` (tablica blokow) z metadata/subtypami. TE sa rejestrowane per typ ducta.

### 5.1 Rejestracja Tile Entities (z javap)

| Tile Entity ID | Klasa TE | Typ ducta |
|---|---|---|
| `thermaldynamics.FluxDuct` | TileEnergyDuct | Energy Duct (Leadstone) |
| `thermaldynamics.FluxDuctSuperConductor` | TileEnergyDuctSuper | Super-Lamina Fluxduct |
| `thermaldynamics.FluidDuct` | TileFluidDuct | Fluiduct (Temperate) |
| `thermaldynamics.FluidDuctFragile` | TileFluidDuctFragile | Fluiduct (niestandardowy?) |
| `thermaldynamics.FluidDuctFlux` | TileFluidDuctFlux | Flux-Plated Fluiduct |
| `thermaldynamics.FluidDuctSuper` | TileFluidDuctSuper | Super-Laminar Fluiduct |
| `thermaldynamics.ItemDuct` | TileItemDuct | Itemduct |
| `thermaldynamics.ItemDuctEnder` | TileItemDuctEnder | Ender Itemduct |
| `thermaldynamics.ItemDuctFlux` | TileItemDuctFlux | Flux-Plated Itemduct |
| `thermaldynamics.StructuralDuct` | TileStructuralDuct | Structuralduct |
| `thermaldynamics.TransportDuct` | TileTransportDuct | Viaduct (transport entity) |
| `thermaldynamics.TransportDuctLongRange` | TileTransportDuctLongRange | Long-Range Viaduct |
| `thermaldynamics.TransportDuctCrossover` | TileTransportDuctCrossover | Viaduct Crossover |

### 5.2 Itemy zalacznikow (nie bloki, ale wazne dla konwersji)
- `ItemServo` — servo do itemductow
- `ItemFilter` — filtry
- `ItemCover` — cover (maskowanie ductow)
- `ItemRetriever` — retriever
- `ItemRelay` — relay

---

## 6. Thermal Series 1.18.2 — bloki i Block Entities

### 6.1 Thermal Expansion 1.18.2 (blockstates)

W 1.18.2 kazdy blok ma osobny registry ID (brak metadata-groups).

#### Maszyny (machine_*)
| ID 1.18.2 | Odpowiednik 1.7.10 |
|---|---|
| `thermal:machine_furnace` | Redstone Furnace |
| `thermal:machine_pulverizer` | Pulverizer |
| `thermal:machine_sawmill` | Sawmill |
| `thermal:machine_smelter` | Induction Smelter |
| `thermal:machine_insolator` | Phytogenic Insolator |
| `thermal:machine_centrifuge` | Centrifugal Separator (NOWY) |
| `thermal:machine_crucible` | Magma Crucible |
| `thermal:machine_bottler` | Fluid Encapsulator (dawny Transposer) |
| `thermal:machine_chiller` | Glacial Precipitator |
| `thermal:machine_extruder` | Igneous Extruder |
| `thermal:machine_press` | Multiservo Press (dawny Compactor) |
| `thermal:machine_brewer` | Alchemical Imbuer |
| `thermal:machine_refinery` | Fractionating Still |
| `thermal:machine_crafter` | Sequential Fabricator |
| `thermal:machine_crystallizer` | Crystallizer (NOWY) |
| `thermal:machine_pyrolyzer` | Pyrolyzer (NOWY) |

#### Dynama (dynamo_*)
| ID 1.18.2 | Odpowiednik 1.7.10 |
|---|---|
| `thermal:dynamo_stirling` | Steam Dynamo (przemianowany) |
| `thermal:dynamo_compression` | Compression Dynamo |
| `thermal:dynamo_magmatic` | Magmatic Dynamo |
| `thermal:dynamo_numismatic` | NOWY — Numismatic Dynamo (na monety) |
| `thermal:dynamo_lapidary` | NOWY — Lapidary Dynamo (na klejnoty) |
| `thermal:dynamo_gourmand` | NOWY — Gourmand Dynamo (na jedzenie) |
| `thermal:dynamo_disenchantment` | NOWY — Disenchantment Dynamo (na enchanty) |

**Uwaga**: W 1.18.2 dynama uzywaja `dynamo_*` zamiast `Dynamo*`. Niektore dynama z 1.7.10 zmienily nazwy lub zostaly zastapione nowymi.

#### Inne bloki z TE
| ID 1.18.2 | Funkcja |
|---|---|
| `thermal:energy_cell` | Energy Cell (tier w blockstate/NBT) |
| `thermal:fluid_cell` | Fluid Cell (tier w blockstate/NBT) |
| `thermal:item_cell` | Item Cell (NOWY) |
| `thermal:charge_bench` | Flux Charge Bench (dawny plate charger?) |
| `thermal:tinker_bench` | Tinker's Workbench |
| `thermal:device_collector` | Vacuumulator |
| `thermal:device_nullifier` | Nullifier |
| `thermal:device_rock_gen` | Igneous Extruder / Rock Gen |
| `thermal:device_water_gen` | Aqueous Accumulator |
| `thermal:device_tree_extractor` | Tree Extractor (NOWY) |
| `thermal:device_fisher` | Aquatic Entangler (NOWY) |
| `thermal:device_hive_extractor` | Hive Extractor (NOWY) |
| `thermal:device_composter` | Phytogenic Insolator / Composter |
| `thermal:device_potion_diffuser` | Potion Diffuser (NOWY) |
| `thermal:device_magnet_blocker` | Magnet Blocker (NOWY) |
| `thermal:device_soil_infuser` | Soil Infuser (NOWY) |

### 6.2 Thermal Foundation 1.18.2

Thermal Foundation w 1.18.2 ma znacznie wiecej blokow (deepslate ores, nowe surowce, TNT, etc.).

Kluczowe kategorie:
- **Ores**: `thermal:*_ore`, `thermal:deepslate_*_ore` (apatite, cinnabar, lead, nickel, niter, ruby, sapphire, silver, sulfur, tin)
- **Storage blocks**: `thermal:*_block`, `thermal:raw_*_block`
- **Rockwool**: 16 kolorow `thermal:*_rockwool`
- **Glass**: `thermal:obsidian_glass`, `thermal:enderium_glass`, `thermal:lumium_glass`, `thermal:signalum_glass`
- **TNT**: Wiele typow (earth, fire, ice, lightning, slime, etc.)
- **Device frames**: `thermal:machine_frame`, `thermal:energy_cell_frame`, `thermal:fluid_cell_frame`, `thermal:item_cell_frame`

### 6.3 Thermal Dynamics 1.18.2

W 1.18.2 Thermal Dynamics ma uproszczony system ductow.

| ID 1.18.2 | Odpowiednik 1.7.10 |
|---|---|
| `thermal:energy_duct` | Wszystkie Fluxducty (Leadstone->Resonant, Cryo) |
| `thermal:fluid_duct` | Temperate/Hardened Fluiduct |
| `thermal:fluid_duct_windowed` | Fluiduct z okienkiem (NOWY) |
| `thermal:item_buffer` | Item Buffer / Item Duct (zastepuje?) |

**Wazna zmiana**: W 1.18.2 ducty sa czescia `thermal:` namespace, a nie `thermaldynamics:`. System tierow zostal uproszczony (brak rozroznienia Leadstone/Hardened/Redstone/Signalum/Resonant w energy_duct).

---

## 7. Podsumowanie Tile Entities — mapowanie ID

### 7.1 Thermal Expansion — Tile Entity ID 1.7.10 -> 1.18.2

| TE ID 1.7.10 | Blok 1.7.10 | BE ID 1.18.2 | Blok 1.18.2 | Uwagi |
|---|---|---|---|---|
| `thermalexpansion.Furnace` | Machine:0 | `thermal:machine_furnace` | machine_furnace | Bez zmian funkcjonalnych |
| `thermalexpansion.Pulverizer` | Machine:1 | `thermal:machine_pulverizer` | machine_pulverizer | Bez zmian |
| `thermalexpansion.Sawmill` | Machine:2 | `thermal:machine_sawmill` | machine_sawmill | Bez zmian |
| `thermalexpansion.Smelter` | Machine:3 | `thermal:machine_smelter` | machine_smelter | Bez zmian |
| `thermalexpansion.Crucible` | Machine:4 | `thermal:machine_crucible` | machine_crucible | Bez zmian |
| `thermalexpansion.Transposer` | Machine:5 | `thermal:machine_bottler` | machine_bottler | Zmiana nazwy |
| `thermalexpansion.Precipitator` | Machine:6 | `thermal:machine_chiller` | machine_chiller | Zmiana nazwy |
| `thermalexpansion.Extruder` | Machine:7 | `thermal:machine_extruder` | machine_extruder | Bez zmian |
| `thermalexpansion.Accumulator` | Machine:8 | `thermal:device_water_gen` | device_water_gen | Zmiana kategorii (device) |
| `thermalexpansion.Assembler` | Machine:9 | `thermal:machine_crafter` | machine_crafter | Bez zmian nazwy |
| `thermalexpansion.Charger` | Machine:10 | `thermal:charge_bench` / `machine_*` | ? | Rozbity na charge_bench? |
| `thermalexpansion.Insolator` | Machine:11 | `thermal:machine_insolator` | machine_insolator | Bez zmian |
| `thermalexpansion.Pump` | Device:1 | `thermal:device_*` | ? | Brak bezposredniego odpowiednika |
| `thermalexpansion.Activator` | Device:2 | `thermal:device_*` | ? | Brak bezposredniego odpowiednika |
| `thermalexpansion.Breaker` | Device:3 | `thermal:device_*` | ? | Brak bezposredniego odpowiednika |
| `thermalexpansion.Collector` | Device:4 | `thermal:device_collector` | device_collector | Bez zmian |
| `thermalexpansion.Nullifier` | Device:5 | `thermal:device_nullifier` | device_nullifier | Bez zmian |
| `thermalexpansion.Buffer` | Device:6 | `thermal:item_buffer` | item_buffer | Zmiana kategorii |
| `thermalexpansion.Extender` | Device:7 | `thermal:energy_duct` / device | ? | Rozbity |
| `thermalexpansion.DynamoSteam` | Dynamo:0 | `thermal:dynamo_stirling` | dynamo_stirling | Zmiana nazwy |
| `thermalexpansion.DynamoMagmatic` | Dynamo:1 | `thermal:dynamo_magmatic` | dynamo_magmatic | Bez zmian |
| `thermalexpansion.DynamoCompression` | Dynamo:2 | `thermal:dynamo_compression` | dynamo_compression | Bez zmian |
| `thermalexpansion.DynamoReactant` | Dynamo:3 | `thermal:dynamo_*` | ? | Brak bezposredniego |
| `thermalexpansion.DynamoEnervation` | Dynamo:4 | `thermal:dynamo_*` | ? | Brak bezposredniego |
| `thermalexpansion.Cell` | Cell | `thermal:energy_cell` | energy_cell | Tier w NBT/blockstate |
| `thermalexpansion.Tank` | Tank | `thermal:fluid_cell` | fluid_cell | Zmiana nazwy |
| `thermalexpansion.Strongbox` | Strongbox | `thermal:item_cell` | item_cell | Zmiana koncepcji? |
| `thermalexpansion.Cache` | Cache | `thermal:item_cell` | item_cell | Zmiana koncepcji? |
| `thermalexpansion.Tesseract` | Tesseract | — | — | **BRAK w 1.18.2 Thermal** — zastapic Ender Tank/Pouch? |
| `thermalexpansion.NewWorkbench` | Workbench | `thermal:tinker_bench` | tinker_bench | Zmiana nazwy |
| `thermalexpansion.Light` | Light | — | — | Brak odpowiednika? |
| `thermalexpansion.Sponge` | Sponge | — | — | Vanilla sponge + Magma? |

### 7.2 Thermal Dynamics — Tile Entity ID 1.7.10 -> 1.18.2

| TE ID 1.7.10 | Blok 1.7.10 | BE ID 1.18.2 | Blok 1.18.2 | Uwagi |
|---|---|---|---|---|
| `thermaldynamics.FluxDuct` | Energy duct | `thermal:energy_duct` | energy_duct | Uproszczony system |
| `thermaldynamics.FluxDuctSuperConductor` | Super fluxduct | `thermal:energy_duct` | energy_duct | Uproszczony |
| `thermaldynamics.FluidDuct` | Fluiduct | `thermal:fluid_duct` | fluid_duct | Bez zmian |
| `thermaldynamics.FluidDuctSuper` | Super fluiduct | `thermal:fluid_duct` | fluid_duct | Uproszczony |
| `thermaldynamics.ItemDuct` | Itemduct | `thermal:item_buffer` / `thermal:item_duct` | ? | System zmieniony |
| `thermaldynamics.ItemDuctEnder` | Ender itemduct | — | — | Brak odpowiednika? |
| `thermaldynamics.ItemDuctFlux` | Flux-plated | `thermal:item_buffer` | item_buffer | Uproszczony |
| `thermaldynamics.StructuralDuct` | Structural | `thermal:structure_duct` | structure_duct | Nie w blockstates? |
| `thermaldynamics.TransportDuct` | Viaduct | — | — | Brak odpowiednika |

---

## 8. Kluczowe wyzwania konwersji

### 8.1 Zmiany systemowe

| Aspekt | 1.7.10 | 1.18.2 | Wplyw na konwersje |
|---|---|---|---|
| ID blokow | Metadata-groups (np. Machine:0-11) | Osobne registry ID per blok | Wymaga rozbicia metadata na osobne ID |
| TE ID | Krotka nazwa (`thermalexpansion.Furnace`) | Pełny namespace (`thermal:machine_furnace`) | Mapping wymaga prefixow |
| Energia | RF (Redstone Flux) | FE (Forge Energy) | Kompatybilne 1:1, ale nazwa sie zmienia |
| Tier system | Metadata/subtypy (Cell:0-4) | Blockstate `type` / NBT | Nalezy zachowac tier w blockstate |
| Ducty | Wiele typow per tier | Uproszczone | Potencjalna strata rozroznienia tierow |

### 8.2 Bloki bez odpowiednika w 1.18.2 (ryzyko straty)

| Blok/TE 1.7.10 | Dlaczego problematyczny | Sugestia |
|---|---|---|
| **Tesseract** | Nie ma w 1.18.2 Thermal | EnderStorage (juz mapowany) lub Ender Tanks/Pouches |
| **Activator** | Brak w 1.18.2 | Deployer z Create lub Pseudo z innych modow |
| **Breaker** | Brak w 1.18.2 | Breaker z Create / innych modow |
| **Pump (device)** | Brak w 1.18.2 | Pumpy z Create/Mekanism |
| **Reactant Dynamo** | Brak w 1.18.2 | Inne dynamo lub konwersja na Numismatic/Gourmand |
| **Enervation Dynamo** | Brak w 1.18.2 | Inne dynamo |
| **Viaducty** | Brak w 1.18.2 | Ignorowac / Create trains / Ender Pearls |
| **Ender Itemduct** | Brak w 1.18.2 | Zwykly itemduct / Ender Storage |
| **Plates** (Excursion, Impulse, Teleporter, Translocate) | Brak w 1.18.2 | Ignorowac / Supplementaries / inne mody |
| **Light / LightFalse** | Brak w 1.18.2 | Glowstone / lampy z innych modow |

### 8.3 Najwazniejsze ryzyka dla kolejnych zadan

1. **Tesseract** — najwazniejszy element do zastapienia. Tesseract w 1.7.10 teleportuje energie, plyny i itemy miedzy dowolnymi punktami. W 1.18.2 Thermal nie ma odpowiednika.
2. **Ducty** — bardzo duza liczba na mapie (~10k+ TE). System uproszczony, ale trzeba zachowac polaczenia.
3. **Tier system** — Energy Cell, Tank, Strongbox, Cache maja tiry (Basic->Hardened->Reinforced->Resonant->Creative). W 1.18.2 system moze byc inny.
4. **NBT maszyn** — augments, side configuration, redstone control, reconfigurable sides. W 1.18.2 structure moze byc zupelnie inna.
5. **Inventory TE** — Strongbox, Cache, Workbench maja inventory ktore trzeba przeniesc.

---

## 9. Utworzone pliki

- `src/converters/thermal/THERMAL_ZADANIE1_ANALIZA.md` — Ten dokument
- `src/converters/thermal/HANDOFF_THERMAL_ZADANIE1.md` — Handoff sesji

---

## 10. Nastepne kroki (Zadanie 2)

1. Przygotowac symulacje funkcjonalnosci w Pythonie dla:
   - Procesu przetwarzania (Furnace, Pulverizer, Smelter)
   - Generowania energii (Dynamo)
   - Transportu (Ducty)
2. Zbadac struktury NBT 1.7.10 dla kluczowych TE (Cell, Tank, maszyny)
3. Porownac z strukturami NBT 1.18.2 (dekompilacja JARow lub dokumentacja)
4. Zdefiniowac mappingi blockstate (metadata -> block_id + properties)

---

*Dokument utworzony: 2026-05-19*
*Zrodla: JARy Thermal Series 1.7.10 i 1.18.2 (javap), dokumentacja projektu, docs/ANALIZA_MODOW_SZCZEGOLOWA.md*
