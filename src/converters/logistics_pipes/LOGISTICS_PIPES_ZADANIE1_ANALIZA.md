# Logistics Pipes - Zadanie 1: bloki, Tile Entities i warstwa zamienna

> Zakres: Logistics Pipes 0.9.3.132 z mapy 1.7.10 oraz planowana warstwa zamienna Pretty Pipes / AE2 / XNet.  
> Data analizy: 2026-05-26.  
> Status: ukonczono krok 1, bez kodu konwersji eventow.

## Zrodla i walidacja

| Wersja | Zrodlo | Status |
|---|---|---|
| 1.7.10 | `modpack_1710/logisticspipes-0.9.3.132.jar` | glowny dowod przez `javap` |
| replacement | `mod_src/118/actual_src/1.18.2/PrettyPipes/repo` | zdekompilowany kod z `mod_src/118/mod_jars/PrettyPipes-1.12.8.jar`, czyli wlasciwy target 1.18.2 Forge |

Zrodla internetowe:

| Zrodlo | Co potwierdza |
|---|---|
| https://www.curseforge.com/minecraft/mc-mods/logistics-pipes/files/4411480 | Logistics Pipes to rozszerzenie rur BuildCraft: dystrybucja itemow, stockkeeping i autocrafting. |
| https://tekkit2.fandom.com/wiki/Logistics_Pipes | Role request/provider/supplier/crafting pipes i Request Table jako interfejsu zamowien. |
| https://www.curseforge.com/minecraft/mc-mods/pretty-pipes | Pretty Pipes to prostszy mod transportu itemow, z modulami i terminalami. |

## 1.7.10 - Bloki

### `LogisticsPipes:logisticsPipeBlock`
- **Typ:** Block
- **Wersja:** 1.7.10
- **Registry names:**
  - Block registry: `"LogisticsPipes:logisticsPipeBlock"`
  - TileEntity registry: `"logisticspipes.pipes.basic.LogisticsTileGenericPipe"`
  - Item registry: pipe-specific items rejestrowane przez `LogisticsBlockGenericPipe.registerPipe(...)`
  - **Ma prefiks moda:** TAK
- **Klasa Java:** `logisticspipes.pipes.basic.LogisticsBlockGenericPipe`
- **Opis dzialania:** Jeden wspolny blok dla wszystkich rur LP. Konkretny typ rury nie wynika z metadata bloku, tylko z obiektu `CoreUnroutedPipe` zapisanego w `LogisticsTileGenericPipe`. Ten blok obsluguje polaczenia, raytrace czesci rury, pluggables/facades BuildCraft oraz aktualizacje renderowania.
- **Dowod z kodu - rejestracja:**
```java
GameRegistry.registerBlock(LogisticsPipeBlock, "logisticsPipeBlock");
registerPipes(side);
```
- **Dowod z kodu - logika:**
```java
public TileEntity createNewTileEntity(World world, int meta) {
    return new LogisticsTileGenericPipe();
}
public static ItemLogisticsPipe registerPipe(Class<? extends CoreUnroutedPipe> pipe) {
    GameRegistry.registerItem(item, item.getUnlocalizedName());
}
```

### `LogisticsPipes:logisticsSolidBlock`
- **Typ:** Block
- **Wersja:** 1.7.10
- **Registry names:**
  - Block registry: `"LogisticsPipes:logisticsSolidBlock"`
  - TileEntity registry: zalezne od metadata, lista w sekcji TE
  - Item registry: `"logisticsSolidBlock"`
  - **Ma prefiks moda:** TAK
- **Klasa Java:** `logisticspipes.blocks.LogisticsSolidBlock`
- **Opis dzialania:** Rodzina blokow uzytkowych LP. Metadata okresla soldering station, power junction, security station, autocrafting/fuzzy crafting table, statistics table oraz providery energii RF/IC2. Blok otwiera GUI dla TE implementujacych `IGuiTileEntity`, ustawia rotacje po postawieniu i tworzy TE przez `createNewTileEntity` na podstawie metadata.
- **Dowod z kodu - rejestracja:**
```java
GameRegistry.registerBlock(LogisticsSolidBlock, LogisticsSolidBlockItem.class, "logisticsSolidBlock");
```
- **Dowod z kodu - logika:**
```java
meta 0 -> new LogisticsSolderingTileEntity()
meta 1 -> new LogisticsPowerJunctionTileEntity()
meta 2 -> new LogisticsSecurityTileEntity()
meta 3/4 -> new LogisticsCraftingTableTileEntity()
meta 5 -> new LogisticsStatisticsTileEntity()
meta 11 -> new LogisticsRFPowerProviderTileEntity()
meta 12 -> new LogisticsIC2PowerProviderTileEntity()
```

## 1.7.10 - Pipe item classes

Wszystkie ponizsze pipe itemy po polozeniu laduja do `LogisticsPipes:logisticsPipeBlock` + `LogisticsTileGenericPipe`; typ zachowania siedzi w klasie pipe.

| Klasa pipe | Rola migracyjna |
|---|---|
| `PipeItemsBasicLogistics` | podstawowy routed pipe |
| `PipeItemsRequestLogistics`, `PipeItemsRequestLogisticsMk2` | request / zamawianie itemow |
| `PipeItemsProviderLogistics`, `PipeItemsProviderLogisticsMk2` | provider / udostepnianie inventory |
| `PipeItemsCraftingLogistics`, `Mk2`, `Mk3` | autocrafting |
| `PipeItemsSatelliteLogistics` | satelita dla craftingu |
| `PipeItemsSupplierLogistics` | utrzymywanie zapasu |
| `PipeLogisticsChassiMk1` - `Mk5` | pipe z modulami |
| `PipeItemsRemoteOrdererLogistics` | zdalne zamowienia |
| `PipeItemsInvSysConnector` | laczenie systemow/inventory |
| `PipeItemsSystemEntranceLogistics`, `PipeItemsSystemDestinationLogistics` | wejscie/wyjscie systemowe |
| `PipeItemsFirewall` | filtr/security routingu |
| `PipeItemsApiaristAnalyser`, `PipeItemsApiaristSink` | integracja Forestry bees |
| `PipeFluidBasic`, `PipeFluidRequestLogistics`, `PipeFluidProvider`, `PipeFluidSatellite`, `PipeItemsFluidSupplier`, `PipeFluidSupplierMk2`, `PipeFluidInsertion`, `PipeFluidExtractor` | fluid routing |
| `PipeBlockRequestTable` | request table jako pipe/block |
| `PipeItemsBasicTransport` | unrouted transport pipe |

## 1.7.10 - Tile Entities

| TE registry string | Klasa Java | Blok/meta | Ma prefiks? | Funkcja | Target hint |
|---|---|---|---|---|---|
| `logisticspipes.pipes.basic.LogisticsTileGenericPipe` | `logisticspipes.pipes.basic.LogisticsTileGenericPipe` | `logisticsPipeBlock`, wszystkie pipe itemy | TAK | kontener wszystkich rur, routing, polaczenia, pluggables, tick pipe'a | `prettypipes:pipe` + moduly lub raport rekonstrukcji |
| `logisticspipes.blocks.LogisticsSolderingTileEntity` | `logisticspipes.blocks.LogisticsSolderingTileEntity` | `logisticsSolidBlock:0` | TAK | soldering/crafting station dla receptur LP | brak 1:1, placeholder/report |
| `logisticspipes.blocks.powertile.LogisticsPowerJuntionTileEntity` | `logisticspipes.blocks.powertile.LogisticsPowerJunctionTileEntity` | `logisticsSolidBlock:1` | TAK | bufor energii LP; uwaga typo `Juntion` w registry | brak 1:1 |
| `logisticspipes.blocks.LogisticsSecurityTileEntity` | `logisticspipes.blocks.LogisticsSecurityTileEntity` | `logisticsSolidBlock:2` | TAK | security station, UUID, ID card, CC/OC permissions | raport/manual |
| `logisticspipes.blocks.crafting.LogisticsCraftingTableTileEntity` | `logisticspipes.blocks.crafting.LogisticsCraftingTableTileEntity` | `logisticsSolidBlock:3/4` | TAK | autocrafting/fuzzy crafting table | AE2 pattern/provider lub Pretty Pipes crafting module |
| `logisticspipes.blocks.stats.LogisticsStatisticsTileEntity` | `logisticspipes.blocks.stats.LogisticsStatisticsTileEntity` | `logisticsSolidBlock:5` | TAK | statystyki sieci | brak 1:1 |
| `logisticspipes.blocks.powertile.LogisticsRFPowerProviderTileEntity` | `logisticspipes.blocks.powertile.LogisticsRFPowerProviderTileEntity` | `logisticsSolidBlock:11` | TAK | RF/CoFH provider energii LP | pressurizer FE jako funkcjonalny zamiennik, nie 1:1 |
| `logisticspipes.blocks.powertile.LogisticsIC2PowerProviderTileEntity` | `logisticspipes.blocks.powertile.LogisticsIC2PowerProviderTileEntity` | `logisticsSolidBlock:12` | TAK | IC2 EU provider energii LP | raport IC2/energy |

Rejestracja TE z kodu:

```java
GameRegistry.registerTileEntity(LogisticsSolderingTileEntity.class, "logisticspipes.blocks.LogisticsSolderingTileEntity");
GameRegistry.registerTileEntity(LogisticsPowerJunctionTileEntity.class, "logisticspipes.blocks.powertile.LogisticsPowerJuntionTileEntity");
GameRegistry.registerTileEntity(LogisticsRFPowerProviderTileEntity.class, "logisticspipes.blocks.powertile.LogisticsRFPowerProviderTileEntity");
GameRegistry.registerTileEntity(LogisticsIC2PowerProviderTileEntity.class, "logisticspipes.blocks.powertile.LogisticsIC2PowerProviderTileEntity");
GameRegistry.registerTileEntity(LogisticsSecurityTileEntity.class, "logisticspipes.blocks.LogisticsSecurityTileEntity");
GameRegistry.registerTileEntity(LogisticsCraftingTableTileEntity.class, "logisticspipes.blocks.crafting.LogisticsCraftingTableTileEntity");
GameRegistry.registerTileEntity(LogisticsTileGenericPipe.class, "logisticspipes.pipes.basic.LogisticsTileGenericPipe");
GameRegistry.registerTileEntity(LogisticsStatisticsTileEntity.class, "logisticspipes.blocks.stats.LogisticsStatisticsTileEntity");
```

## 1.18.2 - Bloki

Lokalny folder `mod_src/118/actual_src/1.18.2/PrettyPipes/repo` zostal naprawiony po analizie: zawiera teraz zdekompilowany kod z JAR-a `PrettyPipes-1.12.8.jar`, czyli wersji Pretty Pipes dla Minecraft 1.18.2 Forge. Poprzedni checkout upstream z build setupem 1.21.1 zostal odlozony do `repo_wrong_1.21_reference/`.

| Registry | Klasa lokalnego checkoutu | Funkcja | Uwaga |
|---|---|---|---|
| `prettypipes:pipe` | `de.ellpeck.prettypipes.pipe.PipeBlock` | baza rur z modulami | glowny cel prostych rur LP |
| `prettypipes:item_terminal` | `de.ellpeck.prettypipes.terminal.ItemTerminalBlock` | terminal request/insertion | cel roli request pipe/table |
| `prettypipes:crafting_terminal` | `de.ellpeck.prettypipes.terminal.CraftingTerminalBlock` | terminal z crafting GUI | tylko czesc roli LP autocraft |
| `prettypipes:pressurizer` | `de.ellpeck.prettypipes.pressurizer.PressurizerBlock` | przyspieszanie rur z FE | nie jest konwersja LP power junction 1:1 |

## 1.18.2 - Block Entities

| BE registry | Klasa lokalnego checkoutu | Funkcja | Uwaga migracyjna |
|---|---|---|---|
| `prettypipes:pipe` | `PipeBlockEntity` | moduly, cover, priority, item cache, active crafts | najblizszy techniczny cel dla rur LP |
| `prettypipes:item_terminal` | `ItemTerminalBlockEntity` | terminal sieci itemow | request layer |
| `prettypipes:crafting_terminal` | `CraftingTerminalBlockEntity` | terminal crafting | request/crafting UI, nie pelny LP autocraft |
| `prettypipes:pressurizer` | `PressurizerBlockEntity` | FE storage/pressurize | opcjonalny element odbudowy |

Dowod rejestracji:

```java
h.register(ResourceLocation.fromNamespaceAndPath(PrettyPipes.ID, "pipe"), Registry.pipeBlock = new PipeBlock(...));
h.register(ResourceLocation.fromNamespaceAndPath(PrettyPipes.ID, "item_terminal"), Registry.itemTerminalBlock = new ItemTerminalBlock(...));
h.register(ResourceLocation.fromNamespaceAndPath(PrettyPipes.ID, "crafting_terminal"), Registry.craftingTerminalBlock = new CraftingTerminalBlock(...));
h.register(ResourceLocation.fromNamespaceAndPath(PrettyPipes.ID, "pressurizer"), Registry.pressurizerBlock = new PressurizerBlock(...));
```

Dowod logiki `PipeBlockEntity`:

```java
public final ItemStackHandler modules = new ItemStackHandler(3);
compound.put("modules", this.modules.serializeNBT(provider));
compound.putInt("priority", this.priority);
this.modules.deserializeNBT(provider, compound.getCompound("modules"));
```

## Porownanie 1.7.10 vs warstwa 1.18.2

| Rola LP 1.7.10 | Dane zrodlowe | Najblizszy cel | Ryzyko |
|---|---|---|---|
| Basic routed pipe | `LogisticsTileGenericPipe` + `PipeItemsBasicLogistics` | `prettypipes:pipe` | srednie, polaczenia do odtworzenia z geometrii |
| Request pipe/table | request pipe / `PipeBlockRequestTable` | `item_terminal` / `crafting_terminal` | wysokie, GUI i requesty nie sa przenoszalne 1:1 |
| Provider pipe | `PipeItemsProviderLogistics`, inventory/filter NBT | `pipe` + extraction/filter module albo AE2 import/export | wysokie |
| Supplier pipe | `PipeItemsSupplierLogistics`, module NBT | retrieval/stack-size/filter module albo XNet | wysokie |
| Crafting pipe/table | `PipeItemsCraftingLogistics*`, `LogisticsCraftingTableTileEntity` | Pretty Pipes crafting module albo AE2 patterns | bardzo wysokie, wymaga rekonstrukcji patternow |
| Chassis/module pipe | `PipeLogisticsChassiMk*`, `ItemModule` NBT | `pipe` z modulami | czesciowo, sloty i typy modulow roznia sie |
| Fluid pipes | `PipeFluid*` | poza Pretty Pipes core; Pipez/Mekanism/Pretty Pipes Fluids | wymaga osobnej decyzji targetu |
| Power providers | power junction/RF/IC2 provider | pressurizer/FE infrastruktura | brak konwersji NBT 1:1 |
| Security/statistics | solid block TE | raport/manual | brak odpowiednika |

## Tabela registry names

| Element | Klasa Java | Registry String | Ma prefiks? |
|---|---|---|---|
| Pipe block | `LogisticsBlockGenericPipe` | `LogisticsPipes:logisticsPipeBlock` | TAK |
| Solid block | `LogisticsSolidBlock` | `LogisticsPipes:logisticsSolidBlock` | TAK |
| Generic pipe TE | `LogisticsTileGenericPipe` | `logisticspipes.pipes.basic.LogisticsTileGenericPipe` | TAK |
| Soldering station TE | `LogisticsSolderingTileEntity` | `logisticspipes.blocks.LogisticsSolderingTileEntity` | TAK |
| Power junction TE | `LogisticsPowerJunctionTileEntity` | `logisticspipes.blocks.powertile.LogisticsPowerJuntionTileEntity` | TAK, z typo |
| RF power provider TE | `LogisticsRFPowerProviderTileEntity` | `logisticspipes.blocks.powertile.LogisticsRFPowerProviderTileEntity` | TAK |
| IC2 power provider TE | `LogisticsIC2PowerProviderTileEntity` | `logisticspipes.blocks.powertile.LogisticsIC2PowerProviderTileEntity` | TAK |
| Security station TE | `LogisticsSecurityTileEntity` | `logisticspipes.blocks.LogisticsSecurityTileEntity` | TAK |
| Crafting table TE | `LogisticsCraftingTableTileEntity` | `logisticspipes.blocks.crafting.LogisticsCraftingTableTileEntity` | TAK |
| Statistics table TE | `LogisticsStatisticsTileEntity` | `logisticspipes.blocks.stats.LogisticsStatisticsTileEntity` | TAK |

## Wnioski dla nastepnego kroku

1. Zadanie 2 powinno symulowac minimum: provider/request flow, supplier stockkeeping, crafting request, chassis module dispatch oraz powered speed/pressurizer difference.
2. Zadanie 3 nie powinno probowac slepego 1:1 NBT. Potrzebny bedzie eksport sieci LP do raportu i generowanie zdarzen rekonstrukcyjnych.
3. Przy kodzie eventow uzywac `mod_src/118/actual_src/1.18.2/PrettyPipes/repo`, bo teraz jest to zdekompilowany kod 1.18.2. Folder `repo_wrong_1.21_reference/` sluzy tylko jako archiwum blednego checkoutu.
