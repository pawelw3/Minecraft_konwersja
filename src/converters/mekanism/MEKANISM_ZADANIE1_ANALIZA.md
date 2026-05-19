# Mekanism - Zadanie 1: bloki, Tile Entities i porownanie 1.7.10 -> 1.18.2

> Zakres: **Mekanism core**. Nie obejmuje osobnych modow `MekanismGenerators` i `MekanismTools`, mimo ze sa w paczce 1.7.10 i maja osobne JAR-y.  
> Data analizy: 2026-05-01.  
> Status: analiza rejestracji i funkcji, bez pisania kodu konwersji.

## Zrodla i walidacja

Najwazniejszy wynik walidacyjny: w projekcie nie ma juz lokalnego checkoutu zrodel Mekanism dla 1.18.2; bledny nowszy checkout zostal usuniety. Dlatego jako zrodlo prawdy dla targetu 1.18.2 uzylem JAR-a `mod_src/118/mod_jars/Mekanism-1.18.2-10.2.5.465.jar`.

Lokalne zrodla uzyte jako dowod:

| Wersja | Zrodlo | Status |
|---|---|---|
| 1.7.10 | `modpack_1710/Mekanism-1.7.10-9.1.1-clienthax.jar` | glowny dowod: `javap`, zasoby lang |
| 1.18.2 | `mod_src/118/mod_jars/Mekanism-1.18.2-10.2.5.465.jar` | glowny dowod: `javap`, loot tables |
| Brak lokalnego source 1.18.2 | `mod_src/118/actual_src/1.18.2/Mekanism/repo` | bledny checkout zostal usuniety; uzywac JAR-a 10.2.5.465 albo zdekompilowac go w kolejnym kroku |

Zrodla internetowe:

| Zrodlo | Co potwierdza |
|---|---|
| https://www.curseforge.com/minecraft/mc-mods/mekanism | Mekanism to tech/storage/processing/transport; opisuje maszyny, factory, Digital Miner i transmittery. |
| https://wiki.aidancbrady.com/wiki/Ore_Processing | Oficjalna wiki opisuje lancuch przetwarzania rud: Enrichment, Crusher, Purification, Injection, Dissolution, Washer, Crystallizer. |
| https://wiki.aidancbrady.com/w/index.php?title=Enrichment_Chamber | Oficjalna wiki opisuje Enrichment Chamber jako maszyne energetyczna i factory-compatible. |

## Dowody z kodu

### 1.7.10 - rejestracja blokow

Z `javap -c mekanism.common.MekanismBlocks` na JAR 1.7.10:

```java
GameRegistry.registerBlock(BasicBlock, ItemBlockBasic.class, "BasicBlock");
GameRegistry.registerBlock(BasicBlock2, ItemBlockBasic.class, "BasicBlock2");
GameRegistry.registerBlock(MachineBlock, ItemBlockMachine.class, "MachineBlock");
GameRegistry.registerBlock(MachineBlock2, ItemBlockMachine.class, "MachineBlock2");
GameRegistry.registerBlock(MachineBlock3, ItemBlockMachine.class, "MachineBlock3");
GameRegistry.registerBlock(OreBlock, ItemBlockOre.class, "OreBlock");
GameRegistry.registerBlock(EnergyCube, ItemBlockEnergyCube.class, "EnergyCube");
GameRegistry.registerBlock(ObsidianTNT, "ObsidianTNT");
GameRegistry.registerBlock(BoundingBlock, "BoundingBlock");
GameRegistry.registerBlock(GasTank, ItemBlockGasTank.class, "GasTank");
GameRegistry.registerBlock(CardboardBox, ItemBlockCardboardBox.class, "CardboardBox");
GameRegistry.registerBlock(PlasticBlock, ItemBlockPlastic.class, "PlasticBlock");
GameRegistry.registerBlock(SlickPlasticBlock, ItemBlockPlastic.class, "SlickPlasticBlock");
GameRegistry.registerBlock(GlowPlasticBlock, ItemBlockPlastic.class, "GlowPlasticBlock");
GameRegistry.registerBlock(ReinforcedPlasticBlock, ItemBlockPlastic.class, "ReinforcedPlasticBlock");
GameRegistry.registerBlock(RoadPlasticBlock, ItemBlockPlastic.class, "RoadPlasticBlock");
GameRegistry.registerBlock(PlasticFence, ItemBlockPlastic.class, "PlasticFence");
GameRegistry.registerBlock(SaltBlock, "SaltBlock");
```

Wniosek dla mapy 1.7.10: bloki core sa starymi numeric-id + metadata, z registry stringami typu `Mekanism:MachineBlock` i `Mekanism:BasicBlock`. Konkretna maszyna jest zakodowana w metadata.

### 1.7.10 - rejestracja Tile Entities

Z `javap -c mekanism.common.CommonProxy`:

```java
GameRegistry.registerTileEntity(TileEntityEnrichmentChamber.class, "EnrichmentChamber");
GameRegistry.registerTileEntity(TileEntityOsmiumCompressor.class, "OsmiumCompressor");
GameRegistry.registerTileEntity(TileEntityFactory.class, "SmeltingFactory");
GameRegistry.registerTileEntity(TileEntityTeleporter.class, "MekanismTeleporter");
GameRegistry.registerTileEntity(TileEntityThermalEvaporationController.class, "SalinationController");
GameRegistry.registerTileEntity(TileEntityFluidTank.class, "PortableTank");
GameRegistry.registerTileEntity(TileEntityQuantumEntangloporter.class, "QuantumEntangloporter");
```

Wniosek krytyczny: **Tile Entity ID w 1.7.10 sa bez prefiksu `Mekanism:`**. Konwerter nie moze szukac tylko po `Mekanism:` w NBT `id`.

### 1.18.2 - rejestracja blokow i BE

Z JAR-a 1.18.2:

```text
data/mekanism/loot_tables/blocks/enrichment_chamber.json
data/mekanism/loot_tables/blocks/basic_universal_cable.json
data/mekanism/loot_tables/blocks/chemical_dissolution_chamber.json
data/mekanism/loot_tables/blocks/qio_drive_array.json
```

Z `javap -private mekanism.common.registries.MekanismTileEntityTypes`:

```java
public static final TileEntityTypeRegistryObject<TileEntityEnrichmentChamber> ENRICHMENT_CHAMBER;
public static final TileEntityTypeRegistryObject<TileEntityDigitalMiner> DIGITAL_MINER;
public static final TileEntityTypeRegistryObject<TileEntityDynamicTank> DYNAMIC_TANK;
public static final TileEntityTypeRegistryObject<TileEntityUniversalCable> BASIC_UNIVERSAL_CABLE;
public static final TileEntityTypeRegistryObject<TileEntityFluidTank> BASIC_FLUID_TANK;
public static final TileEntityTypeRegistryObject<TileEntityBin> BASIC_BIN;
```

Wniosek dla mapy 1.18.2: target ma oddzielne registry ID per blok, np. `mekanism:enrichment_chamber`, `mekanism:basic_bin`, `mekanism:ultimate_universal_cable`. To nie jest prosta zmiana namespace; trzeba rozbic stare bloki z metadata na osobne registry ID.

## 1.7.10 - Bloki

### Grupy rejestracji

| Registry bloku | Klasa bloku | ItemBlock | Rola |
|---|---|---|---|
| `Mekanism:BasicBlock` | `mekanism.common.block.BlockBasic` | `ItemBlockBasic` | materialy, Bin, rama teleportera, multibloki |
| `Mekanism:BasicBlock2` | `mekanism.common.block.BlockBasic` | `ItemBlockBasic` | dalsze multibloki: evaporation, induction, boiler, security |
| `Mekanism:MachineBlock` | `mekanism.common.block.BlockMachine` | `ItemBlockMachine` | pierwsza paczka maszyn, meta 0-15 |
| `Mekanism:MachineBlock2` | `mekanism.common.block.BlockMachine` | `ItemBlockMachine` | druga paczka maszyn, meta 0-15 |
| `Mekanism:MachineBlock3` | `mekanism.common.block.BlockMachine` | `ItemBlockMachine` | trzecia paczka maszyn, meta 0-6 |
| `Mekanism:OreBlock` | `mekanism.common.block.BlockOre` | `ItemBlockOre` | rudy Osmium/Copper/Tin |
| `Mekanism:EnergyCube` | `mekanism.common.block.BlockEnergyCube` | `ItemBlockEnergyCube` | magazyn energii, tier w metadata |
| `Mekanism:GasTank` | `mekanism.common.block.BlockGasTank` | `ItemBlockGasTank` | zbiornik gazow, tier w metadata |
| `Mekanism:CardboardBox` | `mekanism.common.block.BlockCardboardBox` | `ItemBlockCardboardBox` | pakuje blok wraz z NBT |
| `Mekanism:ObsidianTNT` | `mekanism.common.block.BlockObsidianTNT` | vanilla-like | mocne TNT z TE |
| `Mekanism:BoundingBlock` | `mekanism.common.block.BlockBounding` | brak specjalnego ItemBlock | pomocniczy blok bounding dla multiblokow/modeli |
| `Mekanism:PlasticBlock` | `mekanism.common.block.BlockPlastic` | `ItemBlockPlastic` | kolorowe bloki dekoracyjne |
| `Mekanism:SlickPlasticBlock` | `BlockPlastic` | `ItemBlockPlastic` | wariant sliski |
| `Mekanism:GlowPlasticBlock` | `BlockPlastic` | `ItemBlockPlastic` | wariant swiecacy |
| `Mekanism:ReinforcedPlasticBlock` | `BlockPlastic` | `ItemBlockPlastic` | wariant odporny |
| `Mekanism:RoadPlasticBlock` | `BlockPlastic` | `ItemBlockPlastic` | droga/szybszy ruch |
| `Mekanism:PlasticFence` | `BlockPlasticFence` | `ItemBlockPlastic` | kolorowa bariera |
| `Mekanism:SaltBlock` | `BlockSalt` | vanilla-like | blok soli |

### `BasicBlock` metadata

| Meta | Display/lang | Funkcja | TE |
|---:|---|---|---|
| 0 | Osmium Block | blok surowca | nie |
| 1 | Bronze Block | blok surowca | nie |
| 2 | Refined Obsidian | blok surowca | nie |
| 3 | Charcoal Block | blok paliwa/surowca | nie |
| 4 | Refined Glowstone | blok surowca | nie |
| 5 | Steel Block | blok surowca | nie |
| 6 | Bin | magazyn jednego typu itemu; tier wynika z ItemBlock/NBT | `Bin` |
| 7 | Teleporter Frame | struktura teleportera | nie |
| 8 | Steel Casing | crafting/multibloki | nie |
| 9 | Dynamic Tank | sciana dynamicznego zbiornika | `DynamicTank` |
| 10 | Structural Glass | szklo multiblokowe | `StructuralGlass` |
| 11 | Dynamic Valve | wejscie/wyjscie dynamicznego zbiornika | `DynamicValve` |
| 12 | Copper Block | blok surowca | nie |
| 13 | Tin Block | blok surowca | nie |
| 14 | Thermal Evaporation Controller | kontroler wiezy evaporation/salination | `SalinationController` |
| 15 | Thermal Evaporation Valve | zawor wiezy evaporation | brak osobnej rejestracji w CommonProxy; klasa istnieje w JAR |

### `BasicBlock2` metadata

| Meta | Display/lang | Funkcja | TE |
|---:|---|---|---|
| 0 | Thermal Evaporation Block | sciana wiezy evaporation | klasa `TileEntityThermalEvaporationBlock`, brak osobnego register stringu w CommonProxy |
| 1 | Induction Casing | obudowa macierzy indukcyjnej | `InductionCasing` |
| 2 | Induction Port | port energii macierzy indukcyjnej | `InductionPort` |
| 3 | Induction Cell | pojemnosc macierzy, tier w ItemBlock/NBT | `InductionCell` |
| 4 | Induction Provider | transfer macierzy, tier w ItemBlock/NBT | `InductionProvider` |
| 5 | Superheating Element | element boiler/superheat | klasa istnieje, brak osobnego register stringu w CommonProxy |
| 6 | Pressure Disperser | element boiler | klasa istnieje, brak osobnego register stringu w CommonProxy |
| 7 | Boiler Casing | obudowa boiler | `BoilerCasing` |
| 8 | Boiler Valve | port boiler | `BoilerValve` |
| 9 | Security Desk | konfiguracja security/frequency | `SecurityDesk` |

### `MachineBlock` metadata

| Meta | Maszyna | Funkcja | TE registry |
|---:|---|---|---|
| 0 | Enrichment Chamber | wzbogacanie, czesto 2x ore/dust pipeline | `EnrichmentChamber` |
| 1 | Osmium Compressor | kompresja z gazem/infuse medium | `OsmiumCompressor` |
| 2 | Combiner | laczy materialy w rudy/bloki wedlug receptur | `Combiner` |
| 3 | Crusher | kruszenie item -> item | `Crusher` |
| 4 | Digital Miner | automatyczne kopanie z filtrami | `DigitalMiner` |
| 5 | Basic Factory | 3 rownolegle operacje; typ zapisany w NBT | `SmeltingFactory` |
| 6 | Advanced Factory | 5 operacji; typ zapisany w NBT | `AdvancedSmeltingFactory` |
| 7 | Elite Factory | 7 operacji; typ zapisany w NBT | `UltimateSmeltingFactory` |
| 8 | Metallurgic Infuser | infuzja chemiczna/redstone/carbon/diamond/obsidian | `MetallurgicInfuser` |
| 9 | Purification Chamber | etap 3x ore z tlenem | `PurificationChamber` |
| 10 | Energized Smelter | elektryczny piec | `EnergizedSmelter` |
| 11 | Teleporter | teleport z czestotliwoscia | `MekanismTeleporter` |
| 12 | Electric Pump | pompowanie wody/lawy; moze filtr/energy | `ElectricPump` |
| 13 | Personal Chest | prywatna skrzynia | `ElectricChest` |
| 14 | Chargepad | ladowanie itemow/gracza | `Chargepad` |
| 15 | Logistical Sorter | filtrowane wypychanie itemow do transporterow | `LogisticalSorter` |

### `MachineBlock2` metadata

| Meta | Maszyna | Funkcja | TE registry |
|---:|---|---|---|
| 0 | Rotary Condensentrator | konwersja fluid <-> gas/chemical | `RotaryCondensentrator` |
| 1 | Chemical Oxidizer | item -> gas/chemical | `ChemicalOxidizer` |
| 2 | Chemical Infuser | dwa gazy -> gaz wynikowy | `ChemicalInfuser` |
| 3 | Chemical Injection Chamber | etap 4x ore z HCl | `ChemicalInjectionChamber` |
| 4 | Electrolytic Separator | fluid -> dwa gazy, np. water -> H/O | `ElectrolyticSeparator` |
| 5 | Precision Sawmill | ciecie drewna z secondary output | `PrecisionSawmill` |
| 6 | Chemical Dissolution Chamber | start 5x ore, ore + acid -> slurry | `ChemicalDissolutionChamber` |
| 7 | Chemical Washer | dirty slurry + water -> clean slurry | `ChemicalWasher` |
| 8 | Chemical Crystallizer | slurry -> crystals | `ChemicalCrystallizer` |
| 9 | Seismic Vibrator | odczyt geologiczny dla Seismic Reader | `SeismicVibrator` |
| 10 | Pressurized Reaction Chamber | item + fluid + gas -> item/gas | `PressurizedReactionChamber` |
| 11 | Fluid Tank | portable/fluid tank, tier w metadata/NBT | `PortableTank` |
| 12 | Fluidic Plenisher | wypelnianie obszaru fluidem | `FluidicPlenisher` |
| 13 | Laser | emiter energii laserowej | `Laser` |
| 14 | Laser Amplifier | bufor i wyzwalanie lasera, redstone | `LaserAmplifier` |
| 15 | Laser Tractor Beam | zbiera dropy po laserze | `LaserTractorBeam` |

### `MachineBlock3` metadata

| Meta | Maszyna | Funkcja | TE registry |
|---:|---|---|---|
| 0 | Quantum Entangloporter | zdalny transfer item/fluid/gas/energy przez frequency | `QuantumEntangloporter` |
| 1 | Solar Neutron Activator | reakcje solarne dla gazow | `SolarNeutronActivator` |
| 2 | Ambient Accumulator | zbiera gaz z atmosfery/biomu | `AmbientAccumulator` |
| 3 | Oredictionificator | normalizacja ore dictionary | `Oredictionificator` |
| 4 | Resistive Heater | energia -> heat | `ResistiveHeater` |
| 5 | Formulaic Assemblicator | autocrafting wedlug formuly | `FormulaicAssemblicator` |
| 6 | Fuelwood Heater | spalanie paliwa -> heat | `FuelwoodHeater` |

### Pozostale bloki z metadata

| Registry | Meta | Display | Funkcja | TE |
|---|---:|---|---|---|
| `Mekanism:OreBlock` | 0 | Osmium Ore | ruda | nie |
| `Mekanism:OreBlock` | 1 | Copper Ore | ruda | nie |
| `Mekanism:OreBlock` | 2 | Tin Ore | ruda | nie |
| `Mekanism:EnergyCube` | 0-4 | Basic/Advanced/Elite/Ultimate/Creative Energy Cube | magazyn energii | `EnergyCube` |
| `Mekanism:GasTank` | 0-3 | Basic/Advanced/Elite/Ultimate Gas Tank | magazyn gazu | `GasTank` |
| `Mekanism:PlasticBlock` i warianty | 0-15 | kolory | dekoracyjne/plastic family | nie |
| `Mekanism:PlasticFence` | 0-15 | kolory | bariera | nie |

## 1.7.10 - Tile Entities

Wszystkie ponizsze registry stringi sa **bez prefiksu moda**.

| Registry string NBT | Klasa Java | Typowy blok/meta |
|---|---|---|
| `EnrichmentChamber` | `mekanism.common.tile.TileEntityEnrichmentChamber` | `MachineBlock:0` |
| `OsmiumCompressor` | `TileEntityOsmiumCompressor` | `MachineBlock:1` |
| `Combiner` | `TileEntityCombiner` | `MachineBlock:2` |
| `Crusher` | `TileEntityCrusher` | `MachineBlock:3` |
| `SmeltingFactory` | `TileEntityFactory` | `MachineBlock:5` |
| `AdvancedSmeltingFactory` | `TileEntityAdvancedFactory` | `MachineBlock:6` |
| `UltimateSmeltingFactory` | `TileEntityEliteFactory` | `MachineBlock:7` |
| `PurificationChamber` | `TileEntityPurificationChamber` | `MachineBlock:9` |
| `EnergizedSmelter` | `TileEntityEnergizedSmelter` | `MachineBlock:10` |
| `MetallurgicInfuser` | `TileEntityMetallurgicInfuser` | `MachineBlock:8` |
| `GasTank` | `TileEntityGasTank` | `GasTank:*` |
| `EnergyCube` | `TileEntityEnergyCube` | `EnergyCube:*` |
| `ElectricPump` | `TileEntityElectricPump` | `MachineBlock:12` |
| `ElectricChest` | `TileEntityPersonalChest` | `MachineBlock:13` |
| `DynamicTank` | `TileEntityDynamicTank` | `BasicBlock:9` |
| `DynamicValve` | `TileEntityDynamicValve` | `BasicBlock:11` |
| `Chargepad` | `TileEntityChargepad` | `MachineBlock:14` |
| `LogisticalSorter` | `TileEntityLogisticalSorter` | `MachineBlock:15` |
| `Bin` | `TileEntityBin` | `BasicBlock:6` |
| `DigitalMiner` | `TileEntityDigitalMiner` | `MachineBlock:4` |
| `ObsidianTNT` | `TileEntityObsidianTNT` | `ObsidianTNT` |
| `RotaryCondensentrator` | `TileEntityRotaryCondensentrator` | `MachineBlock2:0` |
| `MekanismTeleporter` | `TileEntityTeleporter` | `MachineBlock:11` |
| `ChemicalOxidizer` | `TileEntityChemicalOxidizer` | `MachineBlock2:1` |
| `ChemicalInfuser` | `TileEntityChemicalInfuser` | `MachineBlock2:2` |
| `ChemicalInjectionChamber` | `TileEntityChemicalInjectionChamber` | `MachineBlock2:3` |
| `ElectrolyticSeparator` | `TileEntityElectrolyticSeparator` | `MachineBlock2:4` |
| `SalinationController` | `TileEntityThermalEvaporationController` | `BasicBlock:14` |
| `PrecisionSawmill` | `TileEntityPrecisionSawmill` | `MachineBlock2:5` |
| `ChemicalDissolutionChamber` | `TileEntityChemicalDissolutionChamber` | `MachineBlock2:6` |
| `ChemicalWasher` | `TileEntityChemicalWasher` | `MachineBlock2:7` |
| `ChemicalCrystallizer` | `TileEntityChemicalCrystallizer` | `MachineBlock2:8` |
| `SeismicVibrator` | `TileEntitySeismicVibrator` | `MachineBlock2:9` |
| `PressurizedReactionChamber` | `TileEntityPRC` | `MachineBlock2:10` |
| `PortableTank` | `TileEntityFluidTank` | `MachineBlock2:11` |
| `FluidicPlenisher` | `TileEntityFluidicPlenisher` | `MachineBlock2:12` |
| `Laser` | `TileEntityLaser` | `MachineBlock2:13` |
| `LaserAmplifier` | `TileEntityLaserAmplifier` | `MachineBlock2:14` |
| `LaserTractorBeam` | `TileEntityLaserTractorBeam` | `MachineBlock2:15` |
| `SolarNeutronActivator` | `TileEntitySolarNeutronActivator` | `MachineBlock3:1` |
| `AmbientAccumulator` | `TileEntityAmbientAccumulator` | `MachineBlock3:2` |
| `InductionCasing` | `TileEntityInductionCasing` | `BasicBlock2:1` |
| `InductionPort` | `TileEntityInductionPort` | `BasicBlock2:2` |
| `InductionCell` | `TileEntityInductionCell` | `BasicBlock2:3` |
| `InductionProvider` | `TileEntityInductionProvider` | `BasicBlock2:4` |
| `Oredictionificator` | `TileEntityOredictionificator` | `MachineBlock3:3` |
| `StructuralGlass` | `TileEntityStructuralGlass` | `BasicBlock:10` |
| `FormulaicAssemblicator` | `TileEntityFormulaicAssemblicator` | `MachineBlock3:5` |
| `ResistiveHeater` | `TileEntityResistiveHeater` | `MachineBlock3:4` |
| `BoilerCasing` | `TileEntityBoilerCasing` | `BasicBlock2:7` |
| `BoilerValve` | `TileEntityBoilerValve` | `BasicBlock2:8` |
| `SecurityDesk` | `TileEntitySecurityDesk` | `BasicBlock2:9` |
| `QuantumEntangloporter` | `TileEntityQuantumEntangloporter` | `MachineBlock3:0` |
| `FuelwoodHeater` | `TileEntityFuelwoodHeater` | `MachineBlock3:6` |

Uwaga kompletosci: w JAR istnieja klasy `TileEntityThermalEvaporationValve`, `TileEntityThermalEvaporationBlock`, `TileEntitySuperheatingElement`, `TileEntityPressureDisperser`, ale `CommonProxy.registerTileEntities()` z JAR-a 9.1.1 nie pokazuje dla nich osobnych `registerTileEntity` stringow. Przy skanowaniu mapy trzeba sprawdzic realne NBT; prawdopodobnie czesc tych blokow moze dziedziczyc/nie zapisywac osobnego TE albo byc obslugiwana przez logike multibloku.

## 1.18.2 - Bloki

Target 1.18.2 rozbija stare meta-bloki na osobne registry ID. Wszystkie ponizsze sa w namespace `mekanism:`.

### Resource, ore i dekoracyjne

| Registry ID | Rola |
|---|---|
| `block_osmium`, `block_bronze`, `block_refined_obsidian`, `block_charcoal`, `block_refined_glowstone`, `block_steel`, `block_tin`, `block_lead`, `block_uranium`, `block_fluorite` | bloki materialow |
| `block_raw_osmium`, `block_raw_tin`, `block_raw_lead`, `block_raw_uranium` | raw storage blocks dodane po 1.7.10 |
| `osmium_ore`, `tin_ore`, `lead_ore`, `uranium_ore`, `fluorite_ore` | rudy zwykle |
| `deepslate_osmium_ore`, `deepslate_tin_ore`, `deepslate_lead_ore`, `deepslate_uranium_ore`, `deepslate_fluorite_ore` | rudy deepslate |
| `block_salt` | sol |
| `steel_casing`, `teleporter_frame` | crafting/struktury |
| `cardboard_box` | pakowanie blokow z NBT |

### Storage i tiered tanks

| Registry ID | Rola |
|---|---|
| `basic_bin`, `advanced_bin`, `elite_bin`, `ultimate_bin`, `creative_bin` | magazyn jednego typu itemu |
| `basic_energy_cube`, `advanced_energy_cube`, `elite_energy_cube`, `ultimate_energy_cube`, `creative_energy_cube` | magazyn energii FE/Mekanism energy |
| `basic_fluid_tank`, `advanced_fluid_tank`, `elite_fluid_tank`, `ultimate_fluid_tank`, `creative_fluid_tank` | zbiorniki fluidow |
| `basic_chemical_tank`, `advanced_chemical_tank`, `elite_chemical_tank`, `ultimate_chemical_tank`, `creative_chemical_tank` | zbiorniki chemical/gas |
| `personal_chest`, `personal_barrel` | prywatny storage |

### Maszyny

| Registry ID | Rola |
|---|---|
| `enrichment_chamber` | enriching, czesc 2x ore chain |
| `crusher` | crushing |
| `energized_smelter` | smelting |
| `osmium_compressor` | compressing z chemical input |
| `combiner` | combining |
| `metallurgic_infuser` | infusing |
| `purification_chamber` | 3x ore chain |
| `chemical_injection_chamber` | 4x ore chain |
| `chemical_dissolution_chamber` | 5x ore chain start |
| `chemical_washer` | slurry washing |
| `chemical_crystallizer` | slurry crystallizing |
| `chemical_oxidizer` | oxidizing item -> chemical |
| `chemical_infuser` | chemical + chemical -> chemical |
| `electrolytic_separator` | fluid -> chemicals |
| `rotary_condensentrator` | fluid <-> chemical |
| `pressurized_reaction_chamber` | item + fluid + chemical processing |
| `precision_sawmill` | sawmill with secondary output |
| `isotopic_centrifuge` | nuclear/radiation-era chemical processing |
| `nutritional_liquifier` | food -> nutritional paste/fluid |
| `antiprotonic_nucleosynthesizer` | late-game transmutation/processing |
| `pigment_extractor`, `pigment_mixer`, `painting_machine` | pigment/painting system |
| `electric_pump`, `fluidic_plenisher` | fluid world interaction |
| `digital_miner` | automated filtered mining |
| `teleporter` | frequency teleport |
| `quantum_entangloporter` | frequency-based remote transfer |
| `oredictionificator` | tag/ore dictionary normalization |
| `resistive_heater`, `fuelwood_heater` | heat production |
| `seismic_vibrator` | geological scanning |
| `formulaic_assemblicator` | autocrafting |
| `modification_station` | module modification |
| `dimensional_stabilizer` | chunk/dimensional stabilization |
| `radioactive_waste_barrel`, `industrial_alarm` | radiation/storage/alarm |

### Factories

W 1.18.2 factories sa osobnymi blokami per tier i typ. Stare 1.7.10 `MachineBlock` meta 5-7 + NBT typu factory trzeba mapowac na jeden z:

| Tier | Factory registry IDs |
|---|---|
| Basic | `basic_smelting_factory`, `basic_enriching_factory`, `basic_crushing_factory`, `basic_compressing_factory`, `basic_combining_factory`, `basic_purifying_factory`, `basic_injecting_factory`, `basic_infusing_factory`, `basic_sawing_factory` |
| Advanced | analogicznie `advanced_*_factory` |
| Elite | analogicznie `elite_*_factory` |
| Ultimate | analogicznie `ultimate_*_factory` |

Uwaga: 1.7.10 ma Basic/Advanced/Elite factory o przepustowosci 3/5/7. 1.18.2 ma Basic/Advanced/Elite/Ultimate 3/5/7/9. Dla starych Elite prawdopodobnie target to `elite_*_factory`, nie `ultimate_*_factory`, mimo historycznego TE stringu `UltimateSmeltingFactory`.

### Multibloki

| Registry ID | Multiblok |
|---|---|
| `dynamic_tank`, `dynamic_valve`, `structural_glass` | Dynamic Tank |
| `thermal_evaporation_controller`, `thermal_evaporation_valve`, `thermal_evaporation_block` | Thermal Evaporation |
| `induction_casing`, `induction_port`, `basic_induction_cell`, `advanced_induction_cell`, `elite_induction_cell`, `ultimate_induction_cell`, `basic_induction_provider`, `advanced_induction_provider`, `elite_induction_provider`, `ultimate_induction_provider` | Induction Matrix |
| `boiler_casing`, `boiler_valve`, `superheating_element`, `pressure_disperser` | Thermoelectric Boiler |
| `sps_casing`, `sps_port`, `supercharged_coil` | SPS, nowy po 1.7.10 |

### Transportery

| Registry ID | Transfer |
|---|---|
| `basic_universal_cable`, `advanced_universal_cable`, `elite_universal_cable`, `ultimate_universal_cable` | energia |
| `basic_mechanical_pipe`, `advanced_mechanical_pipe`, `elite_mechanical_pipe`, `ultimate_mechanical_pipe` | fluidy |
| `basic_pressurized_tube`, `advanced_pressurized_tube`, `elite_pressurized_tube`, `ultimate_pressurized_tube` | chemicals/gases |
| `basic_logistical_transporter`, `advanced_logistical_transporter`, `elite_logistical_transporter`, `ultimate_logistical_transporter` | itemy |
| `restrictive_transporter`, `diversion_transporter` | specjalne item transportery |

### QIO

`qio_drive_array`, `qio_dashboard`, `qio_importer`, `qio_exporter`, `qio_redstone_adapter` istnieja w 1.18.2, ale nie maja odpowiednika w 1.7.10. Nie sa celem bezposredniej konwersji ze starej mapy, chyba ze jako kompensacja.

## 1.18.2 - Block Entities

W JAR 1.18.2 `MekanismTileEntityTypes` rejestruje BE przez `TileEntityTypeDeferredRegister`; registry ID jest w praktyce zgodne z blokiem, np. `mekanism:enrichment_chamber`, `mekanism:basic_bin`.

### BE wspolne lub naturalne odpowiedniki 1.7.10

| 1.18.2 BE registry | Klasa |
|---|---|
| `mekanism:enrichment_chamber` | `TileEntityEnrichmentChamber` |
| `mekanism:osmium_compressor` | `TileEntityOsmiumCompressor` |
| `mekanism:combiner` | `TileEntityCombiner` |
| `mekanism:crusher` | `TileEntityCrusher` |
| `mekanism:metallurgic_infuser` | `TileEntityMetallurgicInfuser` |
| `mekanism:purification_chamber` | `TileEntityPurificationChamber` |
| `mekanism:energized_smelter` | `TileEntityEnergizedSmelter` |
| `mekanism:teleporter` | `TileEntityTeleporter` |
| `mekanism:electric_pump` | `TileEntityElectricPump` |
| `mekanism:personal_chest` | `TileEntityPersonalChest` |
| `mekanism:chargepad` | `TileEntityChargepad` |
| `mekanism:logistical_sorter` | `TileEntityLogisticalSorter` |
| `mekanism:rotary_condensentrator` | `TileEntityRotaryCondensentrator` |
| `mekanism:chemical_oxidizer` | `TileEntityChemicalOxidizer` |
| `mekanism:chemical_infuser` | `TileEntityChemicalInfuser` |
| `mekanism:chemical_injection_chamber` | `TileEntityChemicalInjectionChamber` |
| `mekanism:electrolytic_separator` | `TileEntityElectrolyticSeparator` |
| `mekanism:precision_sawmill` | `TileEntityPrecisionSawmill` |
| `mekanism:chemical_dissolution_chamber` | `TileEntityChemicalDissolutionChamber` |
| `mekanism:chemical_washer` | `TileEntityChemicalWasher` |
| `mekanism:chemical_crystallizer` | `TileEntityChemicalCrystallizer` |
| `mekanism:seismic_vibrator` | `TileEntitySeismicVibrator` |
| `mekanism:pressurized_reaction_chamber` | `TileEntityPressurizedReactionChamber` |
| `mekanism:fluidic_plenisher` | `TileEntityFluidicPlenisher` |
| `mekanism:laser`, `mekanism:laser_amplifier`, `mekanism:laser_tractor_beam` | laser BE |
| `mekanism:quantum_entangloporter` | `TileEntityQuantumEntangloporter` |
| `mekanism:solar_neutron_activator` | `TileEntitySolarNeutronActivator` |
| `mekanism:oredictionificator` | `TileEntityOredictionificator` |
| `mekanism:resistive_heater`, `mekanism:fuelwood_heater` | heat BE |
| `mekanism:formulaic_assemblicator` | `TileEntityFormulaicAssemblicator` |
| `mekanism:security_desk` | `TileEntitySecurityDesk` |

### BE tiered

| Rodzina | Registry IDs |
|---|---|
| Energy Cube | `basic_energy_cube`, `advanced_energy_cube`, `elite_energy_cube`, `ultimate_energy_cube`, `creative_energy_cube` |
| Fluid Tank | `basic_fluid_tank`, `advanced_fluid_tank`, `elite_fluid_tank`, `ultimate_fluid_tank`, `creative_fluid_tank` |
| Chemical Tank | `basic_chemical_tank`, `advanced_chemical_tank`, `elite_chemical_tank`, `ultimate_chemical_tank`, `creative_chemical_tank` |
| Bin | `basic_bin`, `advanced_bin`, `elite_bin`, `ultimate_bin`, `creative_bin` |
| Induction Cell | `basic_induction_cell`, `advanced_induction_cell`, `elite_induction_cell`, `ultimate_induction_cell` |
| Induction Provider | `basic_induction_provider`, `advanced_induction_provider`, `elite_induction_provider`, `ultimate_induction_provider` |
| Transmitters | all `*_universal_cable`, `*_mechanical_pipe`, `*_pressurized_tube`, `*_thermodynamic_conductor`, `*_logistical_transporter`, plus `restrictive_transporter`, `diversion_transporter` |

### BE nowe wzgledem 1.7.10

`personal_barrel`, `radioactive_waste_barrel`, `industrial_alarm`, `antiprotonic_nucleosynthesizer`, `pigment_extractor`, `pigment_mixer`, `painting_machine`, `sps_casing`, `sps_port`, `supercharged_coil`, `dimensional_stabilizer`, `qio_drive_array`, `qio_dashboard`, `qio_importer`, `qio_exporter`, `qio_redstone_adapter`, `isotopic_centrifuge`, `nutritional_liquifier`, `modification_station`.

## Opis dzialania elementow

### Processing i ore multiplication

Mekanism core opiera sie na lancuchach przetwarzania item/fluid/chemical. Najprostsza sciezka to `Enrichment Chamber` i `Energized Smelter`; bardziej zaawansowane sciezki uzywaja `Crusher`, `Purification Chamber`, `Chemical Injection Chamber`, `Chemical Dissolution Chamber`, `Chemical Washer` i `Chemical Crystallizer`. Oficjalna wiki opisuje poziomy yield od x1 do x5; to oznacza, ze konwersja musi zachowac inventory, progress, energia oraz chemical/fluid tanks, bo maszyny moga stac w srodku linii produkcyjnej.

### Factories

Factory w 1.7.10 nie jest osobnym blokiem per typ receptury; to meta Basic/Advanced/Elite factory plus NBT okreslajacy tryb. W 1.18.2 target ma osobne registry ID typu `basic_smelting_factory`, `advanced_enriching_factory`, `elite_crushing_factory`. Konwersja factory bedzie jednym z trudniejszych miejsc: trzeba odczytac stary typ factory z NBT/TE, a nie tylko metadata bloku.

### Storage

Bins, Energy Cubes, Gas/Chemical Tanks, Fluid Tanks i Personal Chest przechowuja najcenniejsze dane graczy. W 1.7.10 tier czesto wynika z metadata albo item/block NBT; w 1.18.2 tier jest oddzielnym registry ID. `GasTank` 1.7.10 przechodzi semantycznie na `chemical_tank`, bo Mekanism v10 uzywa systemu chemicals zamiast starego gas API.

### Multibloki

Dynamic Tank, Thermal Evaporation, Induction Matrix i Boiler maja bloki strukturalne oraz porty/valves/controllers. Konwersja nie moze traktowac kazdego bloku izolowanie bez walidacji calej struktury, bo BE i cached multiblock data beda sie regenerowac po starcie serwera. Dla takich struktur nalezy zachowac block layout, a dane kontrolera/portu przenosic ostroznie.

### Transport i redstone

Mekanism ma osobne systemy transportu itemow, fluidow, gazow/chemicals, energii i ciepla. W 1.7.10 core JAR analizowany tutaj nie rejestruje transmitterow w `MekanismBlocks`; w 1.18.2 transmittery sa pelnoprawnymi blokami/BE w core. To trzeba dodatkowo zweryfikowac na mapie, bo 1.7.10 transmittery mogly byc w innym module/wersji kodu albo zarejestrowane poza pokazanym `MekanismBlocks`.

### Frequency/security

Teleporter, Quantum Entangloporter, Security Desk i Personal Chest uzywaja danych gracza/frequency. To sa pola wysokiego ryzyka: owner UUID, nazwa ownera, public/private, frequency name, security mode. Tych danych nie wolno zgubic po cichu; jesli format 1.18.2 nie przyjmie starego formatu, konwerter powinien emitowac loss/warning event.

## Porownanie 1.7.10 vs 1.18.2

### Najwazniejsze roznice techniczne

| Obszar | 1.7.10 | 1.18.2 |
|---|---|---|
| Block ID | numeric ID + metadata, registry typu `Mekanism:MachineBlock` | registry ID per blok, np. `mekanism:crusher` |
| TE ID | bez prefiksu: `Crusher`, `EnergyCube`, `MekanismTeleporter` | zwykle `mekanism:<block_id>` |
| Factories | 3 meta/tier bloki + typ w NBT | osobne bloki per tier i recipe type |
| Gas | stare Mekanism gas API | chemical API |
| Energy | Joules/native + integracje EU/RF | FE/Mekanism energy w v10 |
| Ores | Osmium/Copper/Tin | Osmium/Tin/Lead/Uranium/Fluorite + deepslate + raw blocks |
| Transmitters | nie widac w core `MekanismBlocks` JAR 9.1.1 | core block entities dla cables/pipes/tubes/transporters/conductors |

### Naturalne mapowania blokow

| 1.7.10 | 1.18.2 |
|---|---|
| `Mekanism:MachineBlock:0` Enrichment Chamber | `mekanism:enrichment_chamber` |
| `MachineBlock:1` Osmium Compressor | `mekanism:osmium_compressor` |
| `MachineBlock:2` Combiner | `mekanism:combiner` |
| `MachineBlock:3` Crusher | `mekanism:crusher` |
| `MachineBlock:4` Digital Miner | `mekanism:digital_miner` |
| `MachineBlock:8` Metallurgic Infuser | `mekanism:metallurgic_infuser` |
| `MachineBlock:9` Purification Chamber | `mekanism:purification_chamber` |
| `MachineBlock:10` Energized Smelter | `mekanism:energized_smelter` |
| `MachineBlock:11` Teleporter | `mekanism:teleporter` |
| `MachineBlock:12` Electric Pump | `mekanism:electric_pump` |
| `MachineBlock:13` Personal Chest | `mekanism:personal_chest` |
| `MachineBlock:14` Chargepad | `mekanism:chargepad` |
| `MachineBlock:15` Logistical Sorter | `mekanism:logistical_sorter` |
| `MachineBlock2:*` machines | `mekanism:<snake_case_machine_name>` |
| `MachineBlock3:*` machines | `mekanism:<snake_case_machine_name>` |
| `BasicBlock:6` Bin | `mekanism:<tier>_bin` - tier do ustalenia z NBT/meta |
| `EnergyCube:*` | `mekanism:<tier>_energy_cube` |
| `GasTank:*` | `mekanism:<tier>_chemical_tank` |
| `MachineBlock2:11` Fluid Tank | `mekanism:<tier>_fluid_tank` |
| `OreBlock:0/1/2` | `mekanism:osmium_ore`, `mekanism:*` dla copper/tin; copper w Mekanism 10 moze wymagac decyzji, bo target core nie ma copper ore w loot list |

### Elementy dodane w 1.18.2

QIO, SPS, radioactive waste barrel, industrial alarm, pigment/painting machines, dimensional stabilizer, modification station, nutritional liquifier, isotopic centrifuge, antiprotonic nucleosynthesizer, raw resource blocks, deepslate ores, lead/uranium/fluorite resource family.

### Elementy potencjalnie problematyczne/usuniete

| Element 1.7.10 | Problem |
|---|---|
| `GasTank` | target to chemical tank, NBT gazu wymaga migracji nazwy i formatu chemical stack |
| `Factory` | typ factory w NBT, nie w samym block ID |
| `PersonalChest` / `SecurityDesk` | owner/frequency/security |
| `Teleporter` / `QuantumEntangloporter` | frequency i owner data |
| `DigitalMiner` | filtry, radius, replace stack, min/max Y; format v10 rozny |
| multibloki | cached structure data nie powinno byc kopiowane bez walidacji |
| Copper ore/block | Mekanism 1.18.2 JAR 10.2.5 nie pokazuje `copper_ore`/`block_copper` w loot tables; mozliwa migracja do vanilla `minecraft:copper_ore` / `minecraft:copper_block` |

## Tabela registry names krytyczna dla skanowania mapy

| Element | 1.7 block registry | 1.7 meta | 1.7 TE registry | Ma prefiks TE? | 1.18.2 target |
|---|---|---:|---|---|---|
| Enrichment Chamber | `Mekanism:MachineBlock` | 0 | `EnrichmentChamber` | NIE | `mekanism:enrichment_chamber` |
| Crusher | `Mekanism:MachineBlock` | 3 | `Crusher` | NIE | `mekanism:crusher` |
| Digital Miner | `Mekanism:MachineBlock` | 4 | `DigitalMiner` | NIE | `mekanism:digital_miner` |
| Basic Factory | `Mekanism:MachineBlock` | 5 | `SmeltingFactory` | NIE | zalezy od NBT: `mekanism:basic_*_factory` |
| Advanced Factory | `Mekanism:MachineBlock` | 6 | `AdvancedSmeltingFactory` | NIE | zalezy od NBT: `mekanism:advanced_*_factory` |
| Elite Factory | `Mekanism:MachineBlock` | 7 | `UltimateSmeltingFactory` | NIE | zalezy od NBT: `mekanism:elite_*_factory` |
| Metallurgic Infuser | `Mekanism:MachineBlock` | 8 | `MetallurgicInfuser` | NIE | `mekanism:metallurgic_infuser` |
| Teleporter | `Mekanism:MachineBlock` | 11 | `MekanismTeleporter` | NIE | `mekanism:teleporter` |
| Personal Chest | `Mekanism:MachineBlock` | 13 | `ElectricChest` | NIE | `mekanism:personal_chest` |
| Dynamic Tank | `Mekanism:BasicBlock` | 9 | `DynamicTank` | NIE | `mekanism:dynamic_tank` |
| Dynamic Valve | `Mekanism:BasicBlock` | 11 | `DynamicValve` | NIE | `mekanism:dynamic_valve` |
| Thermal Evaporation Controller | `Mekanism:BasicBlock` | 14 | `SalinationController` | NIE | `mekanism:thermal_evaporation_controller` |
| Induction Port | `Mekanism:BasicBlock2` | 2 | `InductionPort` | NIE | `mekanism:induction_port` |
| Quantum Entangloporter | `Mekanism:MachineBlock3` | 0 | `QuantumEntangloporter` | NIE | `mekanism:quantum_entangloporter` |
| Energy Cube | `Mekanism:EnergyCube` | 0-4 | `EnergyCube` | NIE | `mekanism:<tier>_energy_cube` |
| Gas Tank | `Mekanism:GasTank` | 0-3 | `GasTank` | NIE | `mekanism:<tier>_chemical_tank` |
| Fluid Tank | `Mekanism:MachineBlock2` | 11 | `PortableTank` | NIE | `mekanism:<tier>_fluid_tank` |
| Bin | `Mekanism:BasicBlock` | 6 | `Bin` | NIE | `mekanism:<tier>_bin` |

## Wnioski dla kolejnego kroku

1. Przed Zadaniem 2 trzeba zdekompilowac albo znalezc zrodla **dokladnie Mekanism 10.2.5 dla 1.18.2**, bo lokalny checkout source dla Mekanism 1.18.2 nie jest obecnie dostepny.
2. Skaner mapy dla Mekanism 1.7.10 musi szukac TE ID bez prefiksu: `Crusher`, `EnergyCube`, `MekanismTeleporter`, `SalinationController`, itd.
3. Konwerter bedzie musial miec osobna warstwe `metadata -> registry ID`, bo stare bloki sa grupowane w `MachineBlock`, `MachineBlock2`, `MachineBlock3`, `BasicBlock`, `BasicBlock2`.
4. Najwieksze ryzyka NBT: factories, Digital Miner filters, frequency/security, gas/chemical tanks, multiblock cached data.
5. Copper z Mekanism 1.7.10 wymaga decyzji: target Mekanism 10.2.5 JAR nie pokazuje copper resource blocks/ores, wiec najbardziej naturalny target to vanilla copper albo inny mod surowcowy.
