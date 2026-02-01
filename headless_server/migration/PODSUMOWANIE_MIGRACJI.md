# Podsumowanie migracji mapy 1.7.10 -> 1.14.4

## Data wykonania
2026-02-01

## Konfiguracja
- **Serwer:** Minecraft Vanilla 1.14.4
- **Mapa źródłowa:** headless_server\migration\mapa_1710_migration (kopia z 1.7.10)
- **Ścieżka serwera:** headless_server\1.14\server
- **RAM:** 4GB (-Xmx4G -Xms2G)

## Przebieg operacji

### 1. Przygotowanie serwera
- ✅ Pobrano serwer Minecraft 1.14.4 (server.jar 34MB)
- ✅ Skonfigurowano eula.txt (eula=true)
- ✅ Skonfigurowano server.properties (online-mode=false, allow-flight=true)
- ✅ Skopiowano mapę (9208 plików, 767 plików regionów)

### 2. Pierwsza próba uruchomienia
- ❌ Błąd: Wykryto stary katalog `players` z 1.7.10
- 🔧 Rozwiązanie: Usunięcie katalogu `world/players`

### 3. Druga próba uruchomienia
- ✅ Serwer rozpoczął start
- ⚠️ Wykryto 103+ różnych typów Tile Entities z modów
- ❌ Błędy krytyczne podczas konwersji chunków
- ❌ Serwer nie wystartował w pełni (brak "Done" w logach)

## Problemy napotkane podczas migracji

### Błędy krytyczne (FATAL)
```
Non [a-z0-9/._-] character in path of location: minecraft:TileNPCTable
Non [a-z0-9/._-] character in path of location: minecraft:savedMultipart
```
Serwer 1.14 nie może przekonwertować Tile Entities z modów które mają niedozwolone znaki w nazwach (duże litery).

### Nieobsługiwane Tile Entities (wykryto 103+ typów)

#### Mody z największą ilością danych:
1. **CustomNPCs** - TileNPC*, customnpcs.CustomNpc
2. **Carpenter's Blocks** - TileEntityCarpenters*
3. **Bibliocraft** - biblio*, BookcaseTile, WeaponCaseTile
4. **MrCrayfish Furniture** - cfm* (20+ różnych mebli)
5. **Traincraft** - tc.Loco, tc.Passenger, tileTCRail*
6. **Thaumcraft** - TileNode, TileArcaneWorkbench, TileResearchTable
7. **Witchery** - witchery:candelabra, witchery:circle
8. **Thermal Expansion** - thermalexpansion.*, thermaldynamics.*
9. **Mekanism** - MekanismTeleporter
10. **Railcraft** - RCCokeOvenTile, RCHiddenTile, RCSlabTile
11. **Forestry** - forestry.Fabricator
12. **Iron Chests** - TileEntityIronBlocks*
13. **JABBA** - container.betterstorage.*
14. **SecretRooms** - te.skinnable, minecraft:te.skinnable
15. **Decocraft** - te.mannequin, te.armourLibrary, te.hologramProjector

## Rezultat migracji

### ❌ Migracja NIE POWIODŁA SIĘ w pełni

**Powód:** Serwer Vanilla 1.14 nie posiada DataFixerów dla modowych Tile Entities z 1.7.10. Podczas gdy same bloki zostałyby usunięte (zastąpione powietrzem), to Tile Entities zawierające dane (skrzynie, maszyny, NPC) powodują błędy krytyczne które uniemożliwiają załadowanie chunków.

### Co zostało utworzone:
- Folder `poi/` - nowy format Point of Interest (2 pliki .mca)
- Foldery `DIM1/` i `DIM-1/` dla wymiarów
- Folder `datapacks/`

### Co NIE zostało przekonwertowane:
- Główne pliki regionów (767 .mca) - oryginalny format z 1.7.10
- Dane z modów we wszystkich chunkach

## Wnioski i rekomendacje

### Dlaczego vanilla 1.14 nie działa?
Vanilla Minecraft 1.14 ma wbudowane DataFixery które potrafią przekonwertować:
- ✅ Bloki vanilla z 1.7.10 na 1.14
- ✅ Tile Entities vanilla (skrzynie, piece, itp.)
- ❌ NIE przekonwertuje danych z modów

Tile Entities z modów mają niestandardowe ID które nie pasują do formatu `minecraft:lowercase` wymaganego od wersji 1.11+.

### Alternatywne podejścia:

#### Opcja 1: Serwer Forge 1.14.4 + mody
Zainstalować serwer Forge 1.14.4 z odpowiednikami modów z 1.7.10. Mody same obsłużą migrację swoich danych.

#### Opcja 2: Bezpośrednia migracja 1.7.10 -> 1.18.2
Użyć customowego konwertera (np. Chunky, MCEdit, lub napisać własny skrypt) który:
1. Wczyta chunki z 1.7.10
2. Usunie wszystkie tile entities z modów
3. Zachowa tylko bloki vanilla
4. Zapisze w formacie 1.18.2

#### Opcja 3: Świat testowy
Utworzyć mały świat testowy w 1.7.10 tylko z blokami vanilla, przekonwertować go na 1.14, potem na 1.18.2.

## Szczegóły techniczne

### Pełna lista wykrytych Tile Entities z modów:
```
ArmorStandTile
biblioBellTile, biblioClipboardTile, biblioClockTile, biblioTypewriterTile
blockPorkChop
bookBlock, BookcaseTile
breadBlock
Cauldron
cfmBasin, cfmBedsideCabinet, cfmBin, cfmBlender, cfmCabinetKitchen, 
cfmComputer, cfmCouch, cfmCounterSink, cfmDishwasher, cfmFreezer, 
cfmFridge, cfmMicrowave, cfmOven, cfmPlate, cfmPrinter, cfmStereo, 
cfmToaster, cfmTV, cfmWashingMachine
container.betterstorage.reinforcedChest, container.betterstorage.reinforcedLocker
containerAltar
CookieJarTile
customnpcs.CustomNpc
EnchantTable
Ender, EnderChest
forestry.Fabricator
Furnace
Hopper
Item, ItemFrame
LampTile, LanternTile
MekanismTeleporter
MG
MinecartRideable
minecraft:te.mannequin, minecraft:te.skinnable
MobSpawner
pumpkinPieBlock
RCCokeOvenTile, RCHiddenTile, RCSlabTile
RecordPlayer
savedMultipart
seatTile
Sign
Skull
TableTile
tc.Loco, tc.Passenger
te.armourLibrary, te.globalSkinLibrary, te.hologramProjector, te.mannequin, 
te.skinnable, te.skinnableChild
ThaumicHorizons.ScholarChicken
thermaldynamics.FluxDuctSuperConductor
thermalexpansion.Cell, thermalexpansion.Furnace, thermalexpansion.Tesseract
tile.projectred.illumination.lamp|0
tile.saddleStandBlock
TileAlchemyFurnace, TileArcaneWorkbench, TileBlockAnvil, TileChestHungry, 
TileEntityAntiMobTorch, TileEntityArmChair, TileEntityBath, 
TileEntityCarpentersBlock, TileEntityCarpentersGarageDoor, 
TileEntityCarpentersSafe, TileEntityCarpentersTorch, 
TileEntityCeramicBlocksOne, TileEntityFilingCabinet, TileEntityIronBlocksOne, 
TileEntityIronBlocksTwo, TileEntityLightsOff, TileEntitySofaCenter, 
TileEntitySofaLeft, TileEntitySofaRight, TileEntityWoodBlocks, 
TileEntityWoodBlocksFour, TileEntityWoodBlocksTwo
tileLantern
TileLifter
TileMirror
TileNode, TileNodeStabilizer
TileNPCBarrel, TileNPCCandle, TileNPCChair, TileNPCCouchWood, TileNPCTable, 
TileNPCTallLamp, TileNPCWeaponRack
TilePedestal
TileResearchTable
TileSiphon
TileTable
tileTCRail, tileTCRailGag
TileTube
TileWandPedestal
TileWarded
ToolRackTile
Vehicle
WeaponCaseTile
Wheel
witchery:candelabra, witchery:circle
WoodLabelTile
```

### Rozmiar logu:
- 1,482,615 linii
- Głównie ostrzeżenia o nieobsługiwanych tile entities

## Następne kroki

Aby kontynuować migrację, zalecane jest:
1. Użycie **serwera Forge 1.14.4** zamiast vanilla
2. Lub bezpośredni skok do **1.18.2** z użyciem konwertera NBT
3. Lub usunięcie wszystkich tile entities z modów przed migracją (przez skrypt MCEdit/Amulet)
