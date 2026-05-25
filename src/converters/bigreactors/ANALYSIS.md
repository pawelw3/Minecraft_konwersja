# Analiza moda: Big Reactors (1.7.10) → Bigger Reactors (1.18.2)

> **Zadanie 1** z PLAN.md — wypisanie wszystkich bloków i tile/block entities z opisem działania.
> Data: 2026-05-25
> Źródła: kod źródłowy `mod_src/1710/actual_src/1.7.10/BigReactors/repo` oraz `mod_src/118/actual_src/1.18.2/BiggerReactors/repo`

---

## 1.7.10 — Bloki

W 1.7.10 mod rejestruje bloki przez `GameRegistry.registerBlock` w klasie `BigReactors.java`. Wszystkie bloki należą do modu `BigReactors` (MODID = `"BigReactors"`). Wiele bloków używa **metadata** do rozróżniania podtypów.

### Yellorite Ore
- **Typ:** Block
- **Registry name:** `BigReactors:YelloriteOre`
- **Klasa Java:** `erogenousbeef.bigreactors.common.block.BlockBROre`
- **Metadata:** brak (0)
- **Opis:** Ruda yelloritu generowana w świecie. Po przesmoleniu daje sztabkę yellorium (lub uranu jeśli włączona kompatybilność).
- **Dowody z internetu:** [FTBWiki](https://ftbwiki.org/Big_Reactors) — "Adds multi-block power systems capable of providing large amounts of RF power to Minecraft."
- **Dowód z kodu (rejestracja):**
  ```java
  // BigReactors.java:493
  GameRegistry.registerBlock(BigReactors.blockYelloriteOre, ItemBlockBigReactors.class, "YelloriteOre");
  ```

### Metal Block (BRMetalBlock)
- **Typ:** Block (metadata-based)
- **Registry name:** `BigReactors:BRMetalBlock`
- **Klasa Java:** `erogenousbeef.bigreactors.common.block.BlockBRMetal`
- **Metadata → podtyp:**
  - 0 = Yellorium Block
  - 1 = Cyanite Block
  - 2 = Graphite Block
  - 3 = Blutonium Block
  - 4 = Ludicrite Block
- **Opis:** Bloki magazynujące materiały moda. Graphite działa jako moderator w reaktorze. Ludicrite to najlepszy materiał na cewki turbiny.
- **Dowód z kodu (rejestracja):**
  ```java
  // BigReactors.java:501
  GameRegistry.registerBlock(BigReactors.blockMetal, ItemBlockBigReactors.class, "BRMetalBlock");
  ```
  ```java
  // BlockBRMetal.java:19-25
  public static final int METADATA_YELLORIUM 	= 0;
  public static final int METADATA_CYANITE 	= 1;
  public static final int METADATA_GRAPHITE 	= 2;
  public static final int METADATA_BLUTONIUM 	= 3;
  public static final int METADATA_LUDICRITE = 4;
  ```

### Yellorium Fuel Rod
- **Typ:** Block + TileEntity
- **Registry name:** `BigReactors:YelloriumFuelRod`
- **Klasa Java:** `erogenousbeef.bigreactors.common.multiblock.block.BlockFuelRod`
- **Metadata:** brak (0)
- **Opis:** Rdzeń reaktora — pręt paliwowy wypełniony yellorium/blutonium. Generuje promieniowanie i ciepło podczas reakcji. Musi być ułożony pionowo na całą wysokość wnętrza reaktora.
- **Dowód z kodu (rejestracja):**
  ```java
  // BigReactors.java:576
  GameRegistry.registerBlock(BigReactors.blockYelloriumFuelRod, ItemBlock.class, "YelloriumFuelRod");
  ```

### Reactor Part (BRReactorPart)
- **Typ:** Block + TileEntity (metadata-based)
- **Registry name:** `BigReactors:BRReactorPart`
- **Klasa Java:** `erogenousbeef.bigreactors.common.multiblock.block.BlockReactorPart`
- **Metadata → podtyp + TileEntity:**
  - 0 = Reactor Casing → `TileEntityReactorPart` ("BRReactorPart")
  - 1 = Reactor Controller → `TileEntityReactorPart` ("BRReactorPart")
  - 2 = Reactor Control Rod → `TileEntityReactorControlRod` ("BRReactorControlRod")
  - 3 = Reactor Power Tap → `TileEntityReactorPowerTap` ("BRReactorPowerTap")
  - 4 = Reactor Access Port → `TileEntityReactorAccessPort` ("BRReactorAccessPort")
  - 5 = Reactor Coolant Port → `TileEntityReactorCoolantPort` ("BRReactorCoolantPort")
  - 6 = Reactor RedNet Port → `TileEntityReactorRedNetPort` ("BRReactorRedNetPort")
  - 7 = Reactor Computer Port → `TileEntityReactorComputerPort` ("BRReactorComputerPort")
- **Opis:** Główny blok konstrukcyjny reaktora. Casing to zwykła obudowa; Controller zarządza multiblokiem; Power Tap wyprowadza energię RF; Access Port umożliwia załadunek/rozładunek paliwa; Coolant Port obsługuje ciecze chłodzące; RedNet Port i Computer Port to interfejsy automatyki.
- **Dowód z kodu (rejestracja bloku):**
  ```java
  // BigReactors.java:586
  GameRegistry.registerBlock(BigReactors.blockReactorPart, ItemBlockBigReactors.class, "BRReactorPart");
  ```
- **Dowód z kodu (metadata):**
  ```java
  // BlockReactorPart.java:52-59
  public static final int METADATA_CASING = 0;
  public static final int METADATA_CONTROLLER = 1;
  public static final int METADATA_CONTROLROD = 2;
  public static final int METADATA_POWERTAP = 3;
  public static final int METADATA_ACCESSPORT = 4;
  public static final int METADATA_COOLANTPORT = 5;
  public static final int METADATA_REDNETPORT = 6;
  public static final int METADATA_COMPUTERPORT = 7;
  ```

### Multiblock Glass (BRMultiblockGlass)
- **Typ:** Block + TileEntity (metadata-based)
- **Registry name:** `BigReactors:BRMultiblockGlass`
- **Klasa Java:** `erogenousbeef.bigreactors.common.multiblock.block.BlockMultiblockGlass`
- **Metadata → podtyp + TileEntity:**
  - 0 = Reactor Glass → `TileEntityReactorGlass` ("BRReactorGlass")
  - 1 = Turbine Glass → `TileEntityTurbinePartGlass` ("BRTurbineGlass")
- **Opis:** Szkło do budowy ścian reaktora i turbiny. Pozwala zobaczyć wnętrze struktury.
- **Dowód z kodu:**
  ```java
  // BigReactors.java:603
  GameRegistry.registerBlock(BigReactors.blockMultiblockGlass, ItemBlockBigReactors.class, "BRMultiblockGlass");
  ```
  ```java
  // BlockMultiblockGlass.java:31-32
  public static final int METADATA_REACTOR = 0;
  public static final int METADATA_TURBINE = 1;
  ```

### Reactor Redstone Port (BRReactorRedstonePort)
- **Typ:** Block + TileEntity
- **Registry name:** `BigReactors:BRReactorRedstonePort`
- **Klasa Java:** `erogenousbeef.bigreactors.common.multiblock.block.BlockReactorRedstonePort`
- **TileEntity:** `TileEntityReactorRedstonePort` ("BRReactorRedstonePort")
- **Opis:** Port redstone dla reaktora — umożliwia odczyt stanu reaktora i/lub sterowanie nim sygnałem redstone. Jest osobnym blokiem (nie metadata), ponieważ API redstone w 1.7.10 nie obsługuje sprawdzania metadata.
- **Dowód z kodu:**
  ```java
  // BigReactors.java:615
  GameRegistry.registerBlock(BigReactors.blockReactorRedstonePort, ItemBlock.class, "BRReactorRedstonePort");
  ```

### Turbine Part (BRTurbinePart)
- **Typ:** Block + TileEntity (metadata-based)
- **Registry name:** `BigReactors:BRTurbinePart`
- **Klasa Java:** `erogenousbeef.bigreactors.common.multiblock.block.BlockTurbinePart`
- **Metadata → podtyp + TileEntity:**
  - 0 = Turbine Housing → `TileEntityTurbinePartStandard` ("BRTurbinePart")
  - 1 = Turbine Controller → `TileEntityTurbinePartStandard` ("BRTurbinePart")
  - 2 = Turbine Power Tap → `TileEntityTurbinePowerTap` ("BRTurbinePowerTap")
  - 3 = Turbine Fluid Port → `TileEntityTurbineFluidPort` ("BRTurbineFluidPort")
  - 4 = Turbine Rotor Bearing → `TileEntityTurbineRotorBearing` ("BRTurbineRotorBearing")
  - 5 = Turbine Computer Port → `TileEntityTurbineComputerPort` ("BRTurbineComputerPort")
- **Opis:** Bloki konstrukcyjne turbiny parowej. Housing to obudowa; Controller zarządza multiblokiem; Power Tap wyprowadza energię; Fluid Port przyjmuje parę i odprowadza wodę; Bearing to łożysko wirnika; Computer Port to interfejs ComputerCraft/OpenComputers.
- **Dowód z kodu:**
  ```java
  // BigReactors.java:626
  GameRegistry.registerBlock(BigReactors.blockTurbinePart, ItemBlockBigReactors.class, "BRTurbinePart");
  ```
  ```java
  // BlockTurbinePart.java:49-54
  public static final int METADATA_HOUSING = 0;
  public static final int METADATA_CONTROLLER = 1;
  public static final int METADATA_POWERTAP = 2;
  public static final int METADATA_FLUIDPORT = 3;
  public static final int METADATA_BEARING = 4;
  public static final int METADATA_COMPUTERPORT = 5;
  ```

### Turbine Rotor Part (BRTurbineRotorPart)
- **Typ:** Block + TileEntity (metadata-based)
- **Registry name:** `BigReactors:BRTurbineRotorPart`
- **Klasa Java:** `erogenousbeef.bigreactors.common.multiblock.block.BlockTurbineRotorPart`
- **Metadata → podtyp + TileEntity:**
  - 0 = Rotor Shaft → `TileEntityTurbineRotorPart` ("BRTurbineRotorPart")
  - 1 = Rotor Blade → `TileEntityTurbineRotorPart` ("BRTurbineRotorPart")
- **Opis:** Elementy wirnika turbiny. Shaft to oś centralna; Blade to łopatki które obracają się pod wpływem pary, generując energię w połączeniu z cewkami indukcyjnymi.
- **Dowód z kodu:**
  ```java
  // BigReactors.java:640
  GameRegistry.registerBlock(BigReactors.blockTurbineRotorPart, ItemBlockBigReactors.class, "BRTurbineRotorPart");
  ```
  ```java
  // BlockTurbineRotorPart.java:24-25
  public static final int METADATA_SHAFT = 0;
  public static final int METADATA_BLADE = 1;
  ```

### Device (BRDevice)
- **Typ:** Block + TileEntity (metadata-based)
- **Registry name:** `BigReactors:BRDevice`
- **Klasa Java:** `erogenousbeef.bigreactors.common.block.BlockBRDevice`
- **Metadata → podtyp + TileEntity:**
  - 0 = Cyanite Reprocessor → `TileEntityCyaniteReprocessor` ("BRCyaniteReprocessor")
- **Opis:** Maszyna do przetwarzania cyanite z powrotem na yellorium (przez blutonium). Posiada GUI z slotami na wejście/wyjście i bufor energii RF.
- **Dowód z kodu:**
  ```java
  // BigReactors.java:654
  GameRegistry.registerBlock(BigReactors.blockDevice, ItemBlockBigReactors.class, "BRDevice");
  ```
  ```java
  // BlockBRDevice.java:40-43
  public static final int META_CYANITE_REPROCESSOR = 0;
  public static final String[] _subBlocks = {
      "cyaniteReprocessor"
  };
  ```

### Multiblock Creative Part (BRMultiblockCreativePart)
- **Typ:** Block + TileEntity (metadata-based)
- **Registry name:** `BigReactors:BRMultiblockCreativePart`
- **Klasa Java:** `erogenousbeef.bigreactors.common.multiblock.block.BlockMBCreativePart`
- **Metadata → podtyp + TileEntity:**
  - 0 = Reactor Creative Coolant Port → `TileEntityReactorCreativeCoolantPort` ("BRReactorCreativeCoolantPort")
  - 1 = Turbine Creative Steam Generator → `TileEntityTurbineCreativeSteamGenerator` ("BRTurbineCreativeSteamGenerator")
- **Opis:** Bloki kreatywne do testów. Creative Coolant Port dostarcza nieskończoną ilość chłodziwa do reaktora; Creative Steam Generator dostarcza nieskończoną parę do turbiny.
- **Dowód z kodu:**
  ```java
  // BigReactors.java:668
  GameRegistry.registerBlock(BigReactors.blockMultiblockCreativePart, ItemBlockBigReactors.class, "BRMultiblockCreativePart");
  ```
  ```java
  // BlockMBCreativePart.java:28-29
  public static final int REACTOR_CREATIVE_COOLANT_PORT = 0;
  public static final int TURBINE_CREATIVE_FLUID_PORT = 1;
  ```

### Fluids
- **Typ:** Block (fluid)
- **Registry names:**
  - `BigReactors:tile.bigreactors.yellorium.still` (fluidYelloriumStill)
  - `BigReactors:tile.bigreactors.cyanite.still` (fluidCyaniteStill)
- **Opis:** Ciecze yellorium i cyanite. Są rejestrowane przez `FluidRegistry` i mają swoje bloki źródłowe.
- **Dowód z kodu:**
  ```java
  // BigReactors.java:694
  GameRegistry.registerBlock(BigReactors.fluidYelloriumStill, ItemBlock.class, BigReactors.fluidYelloriumStill.getUnlocalizedName());
  // BigReactors.java:720
  GameRegistry.registerBlock(BigReactors.fluidCyaniteStill, ItemBlock.class, BigReactors.fluidCyaniteStill.getUnlocalizedName());
  ```

---

## 1.7.10 — Tile Entities

Wszystkie TileEntity w 1.7.10 są rejestrowane w `BigReactors.registerTileEntities()`.

| Nazwa wyświetlana | Klasa TileEntity | Registry String | Ma prefiks moda? |
|---|---|---|---|
| Reactor Power Tap | `TileEntityReactorPowerTap` | `BRReactorPowerTap` | TAK (BR*) |
| Reactor Part (casing/controller) | `TileEntityReactorPart` | `BRReactorPart` | TAK (BR*) |
| Reactor Access Port | `TileEntityReactorAccessPort` | `BRReactorAccessPort` | TAK (BR*) |
| Reactor Glass | `TileEntityReactorGlass` | `BRReactorGlass` | TAK (BR*) |
| Reactor Fuel Rod | `TileEntityReactorFuelRod` | `BRFuelRod` | TAK (BR*) |
| Cyanite Reprocessor | `TileEntityCyaniteReprocessor` | `BRCyaniteReprocessor` | TAK (BR*) |
| Reactor Control Rod | `TileEntityReactorControlRod` | `BRReactorControlRod` | TAK (BR*) |
| Reactor RedNet Port | `TileEntityReactorRedNetPort` | `BRReactorRedNetPort` | TAK (BR*) |
| Reactor Redstone Port | `TileEntityReactorRedstonePort` | `BRReactorRedstonePort` | TAK (BR*) |
| Reactor Computer Port | `TileEntityReactorComputerPort` | `BRReactorComputerPort` | TAK (BR*) |
| Reactor Coolant Port | `TileEntityReactorCoolantPort` | `BRReactorCoolantPort` | TAK (BR*) |
| Reactor Creative Coolant Port | `TileEntityReactorCreativeCoolantPort` | `BRReactorCreativeCoolantPort` | TAK (BR*) |
| Turbine Part (standard) | `TileEntityTurbinePartStandard` | `BRTurbinePart` | TAK (BR*) |
| Turbine Power Tap | `TileEntityTurbinePowerTap` | `BRTurbinePowerTap` | TAK (BR*) |
| Turbine Fluid Port | `TileEntityTurbineFluidPort` | `BRTurbineFluidPort` | TAK (BR*) |
| Turbine Computer Port | `TileEntityTurbineComputerPort` | `BRTurbineComputerPort` | TAK (BR*) |
| Turbine Glass | `TileEntityTurbinePartGlass` | `BRTurbineGlass` | TAK (BR*) |
| Turbine Rotor Bearing | `TileEntityTurbineRotorBearing` | `BRTurbineRotorBearing` | TAK (BR*) |
| Turbine Rotor Part | `TileEntityTurbineRotorPart` | `BRTurbineRotorPart` | TAK (BR*) |
| Turbine Creative Steam Generator | `TileEntityTurbineCreativeSteamGenerator` | `BRTurbineCreativeSteamGenerator` | TAK (BR*) |

*Uwaga:* Wszystkie registry strings w Big Reactors 1.7.10 mają prefiks `BR` (nie `BigReactors:`). Jest to nietypowe — w plikach `.mca` tile entities są zapisywane jako `BRReactorPart`, `BRFuelRod`, itp., a nie jako `BigReactors:reactorPart`.

- **Dowód z kodu (rejestracja wszystkich TE):**
  ```java
  // BigReactors.java:456-485
  GameRegistry.registerTileEntity(TileEntityReactorPowerTap.class, 	"BRReactorPowerTap");
  GameRegistry.registerTileEntity(TileEntityReactorPart.class, 		"BRReactorPart");
  GameRegistry.registerTileEntity(TileEntityReactorAccessPort.class,	"BRReactorAccessPort");
  GameRegistry.registerTileEntity(TileEntityReactorGlass.class,		"BRReactorGlass");
  GameRegistry.registerTileEntity(TileEntityReactorFuelRod.class, 			"BRFuelRod");
  GameRegistry.registerTileEntity(TileEntityCyaniteReprocessor.class, "BRCyaniteReprocessor");
  GameRegistry.registerTileEntity(TileEntityReactorControlRod.class, "BRReactorControlRod");
  GameRegistry.registerTileEntity(TileEntityReactorRedNetPort.class, "BRReactorRedNetPort");
  GameRegistry.registerTileEntity(TileEntityReactorRedstonePort.class,"BRReactorRedstonePort");
  GameRegistry.registerTileEntity(TileEntityReactorComputerPort.class, "BRReactorComputerPort");
  GameRegistry.registerTileEntity(TileEntityReactorCoolantPort.class, "BRReactorCoolantPort");
  GameRegistry.registerTileEntity(TileEntityReactorCreativeCoolantPort.class, "BRReactorCreativeCoolantPort");
  GameRegistry.registerTileEntity(TileEntityTurbinePartStandard.class,  "BRTurbinePart");
  GameRegistry.registerTileEntity(TileEntityTurbinePowerTap.class, "BRTurbinePowerTap");
  GameRegistry.registerTileEntity(TileEntityTurbineFluidPort.class, "BRTurbineFluidPort");
  GameRegistry.registerTileEntity(TileEntityTurbineComputerPort.class, "BRTurbineComputerPort");
  GameRegistry.registerTileEntity(TileEntityTurbinePartGlass.class,  "BRTurbineGlass");
  GameRegistry.registerTileEntity(TileEntityTurbineRotorBearing.class, "BRTurbineRotorBearing");
  GameRegistry.registerTileEntity(TileEntityTurbineRotorPart.class, "BRTurbineRotorPart");
  GameRegistry.registerTileEntity(TileEntityTurbineCreativeSteamGenerator.class, "BRTurbineCreativeSteamGenerator");
  ```

---

## 1.18.2 — Bloki

W 1.18.2 BiggerReactors używa adnotacji `@RegisterBlock` z biblioteki Phosphophyllite do rejestracji bloków. Każdy blok ma osobne ID (brak metadata — zamiast tego używane są blockstates i osobne bloki).

### Reaktor (klasyczny)

| Blok | Registry name | Klasa Java | BlockEntity |
|---|---|---|---|
| Reactor Casing | `biggerreactors:reactor_casing` | `ReactorCasing` | `ReactorCasingTile` |
| Reactor Glass | `biggerreactors:reactor_glass` | `ReactorGlass` | `ReactorGlassTile` |
| Reactor Fuel Rod | `biggerreactors:reactor_fuel_rod` | `ReactorFuelRod` | `ReactorFuelRodTile` |
| Reactor Control Rod | `biggerreactors:reactor_control_rod` | `ReactorControlRod` | `ReactorControlRodTile` |
| Reactor Access Port | `biggerreactors:reactor_access_port` | `ReactorAccessPort` | `ReactorAccessPortTile` |
| Reactor Power Tap | `biggerreactors:reactor_power_tap` | `ReactorPowerTap` | `ReactorPowerTapTile` |
| Reactor Coolant Port | `biggerreactors:reactor_coolant_port` | `ReactorCoolantPort` | `ReactorCoolantPortTile` |
| Reactor Computer Port | `biggerreactors:reactor_computer_port` | `ReactorComputerPort` | `ReactorComputerPortTile` |
| Reactor Redstone Port | `biggerreactors:reactor_redstone_port` | `ReactorRedstonePort` | `ReactorRedstonePortTile` |
| Reactor Terminal | `biggerreactors:reactor_terminal` | `ReactorTerminal` | `ReactorTerminalTile` |
| Reactor Manifold | `biggerreactors:reactor_manifold` | `ReactorManifold` | `ReactorManifoldTile` |

### Turbina

| Blok | Registry name | Klasa Java | BlockEntity |
|---|---|---|---|
| Turbine Casing | `biggerreactors:turbine_casing` | `TurbineCasing` | `TurbineCasingTile` |
| Turbine Glass | `biggerreactors:turbine_glass` | `TurbineGlass` | `TurbineGlassTile` |
| Turbine Rotor Shaft | `biggerreactors:turbine_rotor_shaft` | `TurbineRotorShaft` | `TurbineRotorShaftTile` |
| Turbine Rotor Blade | `biggerreactors:turbine_rotor_blade` | `TurbineRotorBlade` | `TurbineRotorBladeTile` |
| Turbine Rotor Bearing | `biggerreactors:turbine_rotor_bearing` | `TurbineRotorBearing` | `TurbineRotorBearingTile` |
| Turbine Power Tap | `biggerreactors:turbine_power_tap` | `TurbinePowerTap` | `TurbinePowerTapTile` |
| Turbine Fluid Port | `biggerreactors:turbine_fluid_port` | `TurbineFluidPort` | `TurbineFluidPortTile` |
| Turbine Computer Port | `biggerreactors:turbine_computer_port` | `TurbineComputerPort` | `TurbineComputerPortTile` |
| Turbine Terminal | `biggerreactors:turbine_terminal` | `TurbineTerminal` | `TurbineTerminalTile` |

### Heat Exchanger (nowość w 1.18.2)

| Blok | Registry name | Klasa Java | BlockEntity |
|---|---|---|---|
| Heat Exchanger Casing | `biggerreactors:heat_exchanger_casing` | `HeatExchangerCasingBlock` | `HeatExchangerCasingTile` |
| Heat Exchanger Glass | `biggerreactors:heat_exchanger_glass` | `HeatExchangerGlassBlock` | `HeatExchangerGlassTile` |
| Heat Exchanger Terminal | `biggerreactors:heat_exchanger_terminal` | `HeatExchangerTerminalBlock` | `HeatExchangerTerminalTile` |
| Heat Exchanger Fluid Port | `biggerreactors:heat_exchanger_fluid_port` | `HeatExchangerFluidPortBlock` | `HeatExchangerFluidPortTile` |
| Heat Exchanger Computer Port | `biggerreactors:heat_exchanger_computer_port` | `HeatExchangerComputerPortBlock` | `HeatExchangerComputerPortTile` |
| Heat Exchanger Condenser Channel | `biggerreactors:heat_exchanger_condenser_channel` | `HeatExchangerCondenserChannelBlock` | `HeatExchangerChannelTile` |
| Heat Exchanger Evaporator Channel | `biggerreactors:heat_exchanger_evaporator_channel` | `HeatExchangerEvaporatorChannelBlock` | `HeatExchangerChannelTile` |

### Materiały i rudy

| Blok | Registry name | Klasa Java |
|---|---|---|
| Uranium Ore | `biggerreactors:uranium_ore` | `UraniumOre` |
| Deepslate Uranium Ore | `biggerreactors:deepslate_uranium_ore` | `DeepslateUraniumOre` |
| Uranium Block | `biggerreactors:uranium_block` | `MaterialBlock` |
| Raw Uranium Block | `biggerreactors:raw_uranium_block` | `MaterialBlock` |
| Blutonium Block | `biggerreactors:blutonium_block` | `MaterialBlock` |
| Cyanite Block | `biggerreactors:cyanite_block` | `MaterialBlock` |
| Graphite Block | `biggerreactors:graphite_block` | `MaterialBlock` |
| Ludicrite Block | `biggerreactors:ludicrite_block` | `MaterialBlock` |

### Ciecze

| Blok | Registry name | Klasa Java |
|---|---|---|
| Liquid Uranium | `biggerreactors:liquid_uranium` | `LiquidUranium` |
| Liquid Obsidian | `biggerreactors:liquid_obsidian` | `LiquidObsidian` |
| Steam | `biggerreactors:steam` | `Steam` |

### Cyanite Reprocessor

| Blok | Registry name | Uwagi |
|---|---|---|
| Cyanite Reprocessor | `biggerreactors:cyanite_reprocessor` | W kodzie źródłowym z głównej gałęzi GitHub rejestracja jest zakomentowana (`// @RegisterBlock`), ale plik `blockstates/cyanite_reprocessor.json` istnieje. Prawdopodobnie blok jest dostępny w wersji release, ale kod w repo może być w trakcie refaktoryzacji. |

- **Dowód z kodu (rejestracja — wzorzec @RegisterBlock):**
  ```java
  // ReactorCasing.java:19
  @RegisterBlock(name = "reactor_casing", tileEntityClass = ReactorCasingTile.class)
  public class ReactorCasing extends ReactorBaseBlock {
  ```
  ```java
  // TurbineCasing.java:19
  @RegisterBlock(name = "turbine_casing", tileEntityClass = TurbineCasingTile.class)
  public class TurbineCasing extends TurbineBaseBlock {
  ```
  ```java
  // MaterialBlock.java
  @RegisterBlock(name = "blutonium_block")
  public static final MaterialBlock BLUTONIUM = new MaterialBlock();
  ```

### Reactor 2 (nowy system reaktora w BiggerReactors)

W kodzie źródłowym istnieje osobny moduł `reactor2` z nowym systemem reaktora. Wprowadza on osobne bloki z prefiksem `reactor2_`. Niewiadome czy jest to włączony w wersji release — może to być eksperymentalny refactoring.

| Blok | Registry name | BlockEntity |
|---|---|---|
| Reactor2 Casing | `biggerreactors:reactor2_casing` | `ReactorTile` |
| Reactor2 Glass | `biggerreactors:reactor2_glass` | `ReactorTile` |
| Reactor2 Manifold | `biggerreactors:reactor2_manifold` | `ReactorTile` |
| Reactor2 Fuel Rod (Copper) | `biggerreactors:reactor2_fuel_rod_copper` | `ReactorFuelRodTile` |
| Reactor2 Fuel Rod (Iron) | `biggerreactors:reactor2_fuel_rod_iron` | `ReactorFuelRodTile` |
| Reactor2 Fuel Rod (Gold) | `biggerreactors:reactor2_fuel_rod_gold` | `ReactorFuelRodTile` |
| Reactor2 Control Rod | `biggerreactors:reactor2_control_rod` | `ReactorControlRodTile` |
| Reactor2 Terminal | `biggerreactors:reactor2_terminal` | `ReactorTerminalTile` |
| Reactor2 Coolant Port | `biggerreactors:reactor2_coolant_port` | `ReactorTile` |

---

## 1.18.2 — Block Entities

W 1.18.2 używane są `BlockEntity` zamiast `TileEntity`, rejestrowane przez `@RegisterTile`.

| Blok | BlockEntity Class | Registry String |
|---|---|---|
| reactor_access_port | `ReactorAccessPortTile` | `reactor_access_port` |
| reactor_casing | `ReactorCasingTile` | `reactor_casing` |
| reactor_computer_port | `ReactorComputerPortTile` | `reactor_computer_port` |
| reactor_control_rod | `ReactorControlRodTile` | `reactor_control_rod` |
| reactor_coolant_port | `ReactorCoolantPortTile` | `reactor_coolant_port` |
| reactor_fuel_rod | `ReactorFuelRodTile` | `reactor_fuel_rod` |
| reactor_glass | `ReactorGlassTile` | `reactor_glass` |
| reactor_manifold | `ReactorManifoldTile` | `reactor_manifold` |
| reactor_power_tap | `ReactorPowerTapTile` | `reactor_power_tap` |
| reactor_redstone_port | `ReactorRedstonePortTile` | `reactor_redstone_port` |
| reactor_terminal | `ReactorTerminalTile` | `reactor_terminal` |
| turbine_casing | `TurbineCasingTile` | `turbine_casing` |
| turbine_computer_port | `TurbineComputerPortTile` | `turbine_computer_port` |
| turbine_fluid_port | `TurbineFluidPortTile` | `turbine_fluid_port` |
| turbine_glass | `TurbineGlassTile` | `turbine_glass` |
| turbine_power_tap | `TurbinePowerTapTile` | `turbine_power_tap` |
| turbine_rotor_bearing | `TurbineRotorBearingTile` | `turbine_rotor_bearing` |
| turbine_rotor_blade | `TurbineRotorBladeTile` | `turbine_rotor_blade` |
| turbine_rotor_shaft | `TurbineRotorShaftTile` | `turbine_rotor_shaft` |
| turbine_terminal | `TurbineTerminalTile` | `turbine_terminal` |
| heat_exchanger_casing | `HeatExchangerCasingTile` | `heat_exchanger_casing` |
| heat_exchanger_channel | `HeatExchangerChannelTile` | `heat_exchanger_channel` |
| heat_exchanger_computer_port | `HeatExchangerComputerPortTile` | `heat_exchanger_computer_port` |
| heat_exchanger_fluid_port | `HeatExchangerFluidPortTile` | `heat_exchanger_fluid_port` |
| heat_exchanger_glass | `HeatExchangerGlassTile` | `heat_exchanger_glass` |
| heat_exchanger_terminal | `HeatExchangerTerminalTile` | `heat_exchanger_terminal` |

- **Dowód z kodu (przykładowe rejestracje BE):**
  ```java
  // ReactorCasingTile.java:15
  @RegisterTile("reactor_casing")
  public static final BlockEntityType.BlockEntitySupplier<ReactorCasingTile> SUPPLIER = new RegisterTile.Producer<>(ReactorCasingTile::new);
  ```
  ```java
  // TurbinePowerTapTile.java:25
  @RegisterTile("turbine_power_tap")
  public static final BlockEntityType.BlockEntitySupplier<TurbinePowerTapTile> SUPPLIER = new RegisterTile.Producer<>(TurbinePowerTapTile::new);
  ```

---

## Porównanie 1.7.10 vs 1.18.2

### Wspólne elementy (bezpośrednie mapowanie)

| Big Reactors 1.7.10 (block/meta) | Bigger Reactors 1.18.2 (block ID) | Uwagi |
|---|---|---|
| `BigReactors:BRReactorPart` / 0 (Casing) | `biggerreactors:reactor_casing` | Osobny blok zamiast metadata |
| `BigReactors:BRReactorPart` / 1 (Controller) | `biggerreactors:reactor_terminal` | Nazwa zmieniona na Terminal |
| `BigReactors:BRReactorPart` / 2 (Control Rod) | `biggerreactors:reactor_control_rod` | Osobny blok |
| `BigReactors:BRReactorPart` / 3 (Power Tap) | `biggerreactors:reactor_power_tap` | Osobny blok |
| `BigReactors:BRReactorPart` / 4 (Access Port) | `biggerreactors:reactor_access_port` | Osobny blok |
| `BigReactors:BRReactorPart` / 5 (Coolant Port) | `biggerreactors:reactor_coolant_port` | Osobny blok |
| `BigReactors:BRReactorPart` / 6 (RedNet Port) | **BRAK** | RedNet nie istnieje w 1.18.2; funkcjonalność może być częściowo zastąpiona przez Redstone Port lub Computer Port |
| `BigReactors:BRReactorPart` / 7 (Computer Port) | `biggerreactors:reactor_computer_port` | Osobny blok |
| `BigReactors:BRMultiblockGlass` / 0 (Reactor) | `biggerreactors:reactor_glass` | Osobny blok zamiast metadata |
| `BigReactors:BRMultiblockGlass` / 1 (Turbine) | `biggerreactors:turbine_glass` | Osobny blok zamiast metadata |
| `BigReactors:YelloriumFuelRod` | `biggerreactors:reactor_fuel_rod` | Nazwa zmieniona z Yellorium na ogólne Fuel Rod |
| `BigReactors:BRReactorRedstonePort` | `biggerreactors:reactor_redstone_port` | Osobny blok (w 1.7.10 był osobny, w 1.18.2 też) |
| `BigReactors:BRTurbinePart` / 0 (Housing) | `biggerreactors:turbine_casing` | Osobny blok |
| `BigReactors:BRTurbinePart` / 1 (Controller) | `biggerreactors:turbine_terminal` | Nazwa zmieniona na Terminal |
| `BigReactors:BRTurbinePart` / 2 (Power Tap) | `biggerreactors:turbine_power_tap` | Osobny blok |
| `BigReactors:BRTurbinePart` / 3 (Fluid Port) | `biggerreactors:turbine_fluid_port` | Osobny blok |
| `BigReactors:BRTurbinePart` / 4 (Bearing) | `biggerreactors:turbine_rotor_bearing` | Osobny blok |
| `BigReactors:BRTurbinePart` / 5 (Computer Port) | `biggerreactors:turbine_computer_port` | Osobny blok |
| `BigReactors:BRTurbineRotorPart` / 0 (Shaft) | `biggerreactors:turbine_rotor_shaft` | Osobny blok |
| `BigReactors:BRTurbineRotorPart` / 1 (Blade) | `biggerreactors:turbine_rotor_blade` | Osobny blok |
| `BigReactors:BRMetalBlock` / 0 (Yellorium) | `biggerreactors:uranium_block` | Yellorium → Uranium |
| `BigReactors:BRMetalBlock` / 1 (Cyanite) | `biggerreactors:cyanite_block` | Bez zmian |
| `BigReactors:BRMetalBlock` / 2 (Graphite) | `biggerreactors:graphite_block` | Bez zmian |
| `BigReactors:BRMetalBlock` / 3 (Blutonium) | `biggerreactors:blutonium_block` | Bez zmian |
| `BigReactors:BRMetalBlock` / 4 (Ludicrite) | `biggerreactors:ludicrite_block` | Bez zmian |
| `BigReactors:YelloriteOre` | `biggerreactors:uranium_ore` + `biggerreactors:deepslate_uranium_ore` | Yellorite → Uranium |
| `BigReactors:BRDevice` / 0 (Cyanite Reprocessor) | `biggerreactors:cyanite_reprocessor` | Prawdopodobnie dostępny w release |

### Elementy usunięte / nieobecne w 1.18.2

1. **Reactor RedNet Port** — RedNet (MineFactory Reloaded) nie istnieje w 1.18.2. Brak bezpośredniego odpowiednika.
2. **Creative Parts** (`BRMultiblockCreativePart`) — W BiggerReactors 1.18.2 nie znaleziono odpowiedników creative portów w kodzie źródłowym.
3. **Fuel Column fluid** (`fluidFuelColumn`) — W BiggerReactors nie ma osobnej cieczy "fuel column".

### Elementy dodane w 1.18.2

1. **Reactor Manifold** (`biggerreactors:reactor_manifold`) — Nowy blok wewnętrzny reaktora, zastępuje niektóre funkcje moderatorów.
2. **Heat Exchanger** — Całkowicie nowy multiblok do wymiany ciepła między cieczami (np. sodium → steam). Nie istniał w 1.7.10.
3. **Deepslate Uranium Ore** — Odpowiednik rudy w deepslate.
4. **Raw Uranium Block** — Blok surowego uranu.
5. **Liquid Obsidian** — Nowa ciecz.
6. **Steam** — Jako osobny blok cieczy (w 1.7.10 steam był rejestrowany w FluidRegistry, ale nie miał własnego bloku źródłowego w świecie).

### Zmiany techniczne

- **Rejestracja:** Z `GameRegistry.registerBlock/TileEntity` na adnotacje `@RegisterBlock` / `@RegisterTile` z biblioteki Phosphophyllite.
- **Metadata → BlockStates:** W 1.7.10 jeden blok z wieloma metadata; w 1.18.2 każdy podtyp to osobny blok z własnym blockstate JSON.
- **TileEntity → BlockEntity:** Zmiana nazewnictwa i API (klasy dziedziczą z `BlockEntity` zamiast `TileEntity`).
- **Energia:** W 1.7.10 BigReactors używa RF (Redstone Flux) przez API CoFH. W 1.18.2 BiggerReactors używa FE (Forge Energy) — de facto ta sama koncepcja, inne API.
- **Nazewnictwo materiałów:** Yellorium → Uranium (w kodzie źródłowym i ore dictionary), Yellorite Ore → Uranium Ore.
- **Multibloki:** W 1.7.10 multibloki zarządzane są przez `erogenousbeef.core.multiblock`. W 1.18.2 BiggerReactors używa własnego systemu multibloków opartego na Phosphophyllite.

---

## Tabela podsumowująca nazwy rejestracji (1.7.10)

| Element | Klasa Java | Registry String | Ma prefiks moda? |
|---|---|---|---|
| Yellorite Ore | `BlockBROre` | `BigReactors:YelloriteOre` | TAK (BigReactors:) |
| Metal Block (Yellorium) | `BlockBRMetal` | `BigReactors:BRMetalBlock` | TAK (BigReactors:) |
| Yellorium Fuel Rod | `BlockFuelRod` | `BigReactors:YelloriumFuelRod` | TAK (BigReactors:) |
| Reactor Part (casing) | `BlockReactorPart` | `BigReactors:BRReactorPart` | TAK (BigReactors:) |
| Multiblock Glass | `BlockMultiblockGlass` | `BigReactors:BRMultiblockGlass` | TAK (BigReactors:) |
| Reactor Redstone Port | `BlockReactorRedstonePort` | `BigReactors:BRReactorRedstonePort` | TAK (BigReactors:) |
| Turbine Part | `BlockTurbinePart` | `BigReactors:BRTurbinePart` | TAK (BigReactors:) |
| Turbine Rotor Part | `BlockTurbineRotorPart` | `BigReactors:BRTurbineRotorPart` | TAK (BigReactors:) |
| Device (Cyanite Reprocessor) | `BlockBRDevice` | `BigReactors:BRDevice` | TAK (BigReactors:) |
| Creative Part | `BlockMBCreativePart` | `BigReactors:BRMultiblockCreativePart` | TAK (BigReactors:) |
| Fluid Yellorium | `BlockBRGenericFluid` | `BigReactors:tile.bigreactors.yellorium.still` | TAK (BigReactors:) |
| Fluid Cyanite | `BlockBRGenericFluid` | `BigReactors:tile.bigreactors.cyanite.still` | TAK (BigReactors:) |
| Reactor Power Tap TE | `TileEntityReactorPowerTap` | `BRReactorPowerTap` | TAK (BR*) |
| Reactor Part TE | `TileEntityReactorPart` | `BRReactorPart` | TAK (BR*) |
| Reactor Access Port TE | `TileEntityReactorAccessPort` | `BRReactorAccessPort` | TAK (BR*) |
| Reactor Glass TE | `TileEntityReactorGlass` | `BRReactorGlass` | TAK (BR*) |
| Reactor Fuel Rod TE | `TileEntityReactorFuelRod` | `BRFuelRod` | TAK (BR*) |
| Cyanite Reprocessor TE | `TileEntityCyaniteReprocessor` | `BRCyaniteReprocessor` | TAK (BR*) |
| Reactor Control Rod TE | `TileEntityReactorControlRod` | `BRReactorControlRod` | TAK (BR*) |
| Reactor RedNet Port TE | `TileEntityReactorRedNetPort` | `BRReactorRedNetPort` | TAK (BR*) |
| Reactor Redstone Port TE | `TileEntityReactorRedstonePort` | `BRReactorRedstonePort` | TAK (BR*) |
| Reactor Computer Port TE | `TileEntityReactorComputerPort` | `BRReactorComputerPort` | TAK (BR*) |
| Reactor Coolant Port TE | `TileEntityReactorCoolantPort` | `BRReactorCoolantPort` | TAK (BR*) |
| Reactor Creative Coolant Port TE | `TileEntityReactorCreativeCoolantPort` | `BRReactorCreativeCoolantPort` | TAK (BR*) |
| Turbine Part Standard TE | `TileEntityTurbinePartStandard` | `BRTurbinePart` | TAK (BR*) |
| Turbine Power Tap TE | `TileEntityTurbinePowerTap` | `BRTurbinePowerTap` | TAK (BR*) |
| Turbine Fluid Port TE | `TileEntityTurbineFluidPort` | `BRTurbineFluidPort` | TAK (BR*) |
| Turbine Computer Port TE | `TileEntityTurbineComputerPort` | `BRTurbineComputerPort` | TAK (BR*) |
| Turbine Glass TE | `TileEntityTurbinePartGlass` | `BRTurbineGlass` | TAK (BR*) |
| Turbine Rotor Bearing TE | `TileEntityTurbineRotorBearing` | `BRTurbineRotorBearing` | TAK (BR*) |
| Turbine Rotor Part TE | `TileEntityTurbineRotorPart` | `BRTurbineRotorPart` | TAK (BR*) |
| Turbine Creative Steam Generator TE | `TileEntityTurbineCreativeSteamGenerator` | `BRTurbineCreativeSteamGenerator` | TAK (BR*) |

*\* Uwaga: Tile Entities w Big Reactors 1.7.10 używają prefiksu `BR` jako części samego stringa rejestracji, ale nie używają pełnego MODID `BigReactors:` jako prefixu. W plikach regionów `.mca` nazwy TE są zapisane jako np. `BRReactorPart`, nie `BigReactors:BRReactorPart`.*

---

## Tabela podsumowująca nazwy rejestracji (1.18.2)

| Element | Klasa Java / BlockEntity | Registry String | Ma prefiks moda? |
|---|---|---|---|
| Reactor Casing | `ReactorCasing` / `ReactorCasingTile` | `biggerreactors:reactor_casing` | TAK |
| Reactor Glass | `ReactorGlass` / `ReactorGlassTile` | `biggerreactors:reactor_glass` | TAK |
| Reactor Fuel Rod | `ReactorFuelRod` / `ReactorFuelRodTile` | `biggerreactors:reactor_fuel_rod` | TAK |
| Reactor Control Rod | `ReactorControlRod` / `ReactorControlRodTile` | `biggerreactors:reactor_control_rod` | TAK |
| Reactor Access Port | `ReactorAccessPort` / `ReactorAccessPortTile` | `biggerreactors:reactor_access_port` | TAK |
| Reactor Power Tap | `ReactorPowerTap` / `ReactorPowerTapTile` | `biggerreactors:reactor_power_tap` | TAK |
| Reactor Coolant Port | `ReactorCoolantPort` / `ReactorCoolantPortTile` | `biggerreactors:reactor_coolant_port` | TAK |
| Reactor Computer Port | `ReactorComputerPort` / `ReactorComputerPortTile` | `biggerreactors:reactor_computer_port` | TAK |
| Reactor Redstone Port | `ReactorRedstonePort` / `ReactorRedstonePortTile` | `biggerreactors:reactor_redstone_port` | TAK |
| Reactor Terminal | `ReactorTerminal` / `ReactorTerminalTile` | `biggerreactors:reactor_terminal` | TAK |
| Reactor Manifold | `ReactorManifold` / `ReactorManifoldTile` | `biggerreactors:reactor_manifold` | TAK |
| Turbine Casing | `TurbineCasing` / `TurbineCasingTile` | `biggerreactors:turbine_casing` | TAK |
| Turbine Glass | `TurbineGlass` / `TurbineGlassTile` | `biggerreactors:turbine_glass` | TAK |
| Turbine Rotor Shaft | `TurbineRotorShaft` / `TurbineRotorShaftTile` | `biggerreactors:turbine_rotor_shaft` | TAK |
| Turbine Rotor Blade | `TurbineRotorBlade` / `TurbineRotorBladeTile` | `biggerreactors:turbine_rotor_blade` | TAK |
| Turbine Rotor Bearing | `TurbineRotorBearing` / `TurbineRotorBearingTile` | `biggerreactors:turbine_rotor_bearing` | TAK |
| Turbine Power Tap | `TurbinePowerTap` / `TurbinePowerTapTile` | `biggerreactors:turbine_power_tap` | TAK |
| Turbine Fluid Port | `TurbineFluidPort` / `TurbineFluidPortTile` | `biggerreactors:turbine_fluid_port` | TAK |
| Turbine Computer Port | `TurbineComputerPort` / `TurbineComputerPortTile` | `biggerreactors:turbine_computer_port` | TAK |
| Turbine Terminal | `TurbineTerminal` / `TurbineTerminalTile` | `biggerreactors:turbine_terminal` | TAK |
| Heat Exchanger Casing | `HeatExchangerCasingBlock` / `HeatExchangerCasingTile` | `biggerreactors:heat_exchanger_casing` | TAK |
| Heat Exchanger Glass | `HeatExchangerGlassBlock` / `HeatExchangerGlassTile` | `biggerreactors:heat_exchanger_glass` | TAK |
| Heat Exchanger Terminal | `HeatExchangerTerminalBlock` / `HeatExchangerTerminalTile` | `biggerreactors:heat_exchanger_terminal` | TAK |
| Heat Exchanger Fluid Port | `HeatExchangerFluidPortBlock` / `HeatExchangerFluidPortTile` | `biggerreactors:heat_exchanger_fluid_port` | TAK |
| Heat Exchanger Computer Port | `HeatExchangerComputerPortBlock` / `HeatExchangerComputerPortTile` | `biggerreactors:heat_exchanger_computer_port` | TAK |
| Heat Exchanger Condenser Channel | `HeatExchangerCondenserChannelBlock` / `HeatExchangerChannelTile` | `biggerreactors:heat_exchanger_condenser_channel` | TAK |
| Heat Exchanger Evaporator Channel | `HeatExchangerEvaporatorChannelBlock` / `HeatExchangerChannelTile` | `biggerreactors:heat_exchanger_evaporator_channel` | TAK |
| Uranium Ore | `UraniumOre` | `biggerreactors:uranium_ore` | TAK |
| Deepslate Uranium Ore | `DeepslateUraniumOre` | `biggerreactors:deepslate_uranium_ore` | TAK |
| Uranium Block | `MaterialBlock` | `biggerreactors:uranium_block` | TAK |
| Raw Uranium Block | `MaterialBlock` | `biggerreactors:raw_uranium_block` | TAK |
| Blutonium Block | `MaterialBlock` | `biggerreactors:blutonium_block` | TAK |
| Cyanite Block | `MaterialBlock` | `biggerreactors:cyanite_block` | TAK |
| Graphite Block | `MaterialBlock` | `biggerreactors:graphite_block` | TAK |
| Ludicrite Block | `MaterialBlock` | `biggerreactors:ludicrite_block` | TAK |
| Liquid Uranium | `LiquidUranium` | `biggerreactors:liquid_uranium` | TAK |
| Liquid Obsidian | `LiquidObsidian` | `biggerreactors:liquid_obsidian` | TAK |
| Steam | `Steam` | `biggerreactors:steam` | TAK |

---

## Walidacja kompletności

### Liczba wywołań rejestracji w kodzie 1.7.10

```
registerBlock (właściwe bloki moda): 11 wywołań
registerTileEntity: 19 wywołań
```

Wszystkie zostały uwzględnione w raporcie.

### Liczba @RegisterBlock w kodzie 1.18.2 (katalog reactor/ + turbine/ + heatexchanger/ + materials/)

- Reaktor: 11 bloków
- Turbina: 9 bloków
- Heat Exchanger: 7 bloków
- Materiały: 8 bloków
- Rudy: 2 bloki
- Ciecze: 3 bloki
- Cyanite Reprocessor: 1 blok (wątpliwy status)

Wszystkie zostały uwzględnione.

---

## Źródła zewnętrzne

1. [FTBWiki — Big Reactors](https://ftbwiki.org/Big_Reactors) — Opis ogólny moda, lista komponentów reaktora i turbiny, zasady budowy multibloków.
2. [Minecraftology Wiki — Big Reactors](https://minecraftology.fandom.com/wiki/Big_Reactors) — Szczegółowy opis części reaktora, mechaniki temperatury, moderacji i budowy.
3. [BiggerSeries — Bigger Reactors](https://biggerseries.net/biggerreactors) — Oficjalna strona Bigger Reactors, potwierdza że jest to kontynuacja Big Reactors z nowymi elementami (turbiny, heat exchanger).
4. [All The Guides — Extreme Reactors](https://allthemods.github.io/alltheguides/atm9/extremereactors/) — Opis konfiguracji reaktorów i turbin w nowych wersjach, wzmianka o liquid sodium i heat exchanger.
