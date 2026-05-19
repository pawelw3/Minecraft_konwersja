# Analiza funkcjonalnosci modow 1.7.10 - czesc 2

Data: 2026-05-18  
Zakres: `docs/mod_mapping_indepth/from/mod_funkcjonalnosci_1.7.10_cz2.md` + `docs/mod_mapping_indepth/to/konwersja_1710_do_1182_mapowanie_modow_cz2.md`  
Arkusz zbiorczy: `docs/sprawdzenie_codex/cz1-5_funkcjonalnosci_mapowanie_1182_2026-05-18.xlsx`

## Najwazniejsze korekty

1. **Carpenter's Blocks powinien isc najpierw w FramedBlocks, nie w custom moda.**  
   FramedBlocks ma bardzo szeroki zestaw blokow ramowych i zawiera `Framed Collapsible Block`, wiec custom mod powinien zostac dopiero jako plan B dla konkretnych ksztaltow/NBT, ktorych nie da sie zakodowac. To jest najwiekszy priorytet czesci 2, bo skan mapy pokazal `847410` dopasowan Carpenter-like TE.

2. **Big Reactors lepiej mapowac na Bigger Reactors niz domyslnie na Extreme Reactors.**  
   Oba nurty sa realnymi opcjami na 1.18.2, ale w projekcie lokalnie istnieje `mod_src/118/actual_src/1.18.2/BiggerReactors`, wiec dla tej paczki to powinien byc preferowany cel.

3. **CustomNPCs nie powinien byc traktowany jako ignorowany bez osobnego sprawdzenia.**  
   Targeted TE scan znalazl `25673` dopasowania, glownie dekoracyjne bloki NPC: krzesla, sofy, stoly, swiece, skrzynki, lampy. Encje NPC, questy i dialogi trzeba sprawdzic osobno, ale dekoracje na mapie wygladaja na realnie uzyte.

4. **BiblioCraft wymaga splitu funkcjonalnego.**  
   Nie ma sensownego jednego portu 1:1. Najlepszy wynik daje laczenie `Supplementaries`, `Handcrafted`, ewentualnie `Macaw Furniture` i vanilla item/armor frames. Skan celowany znalazl `5402` dopasowania, mimo ze starszy skan wybranych stref raportowal 0.

5. **Enchanting Plus najlepiej mapowac na Enchanting Infuser, nie na samo Apotheosis.**  
   Apotheosis jest dobrym globalnym overhaulem enchanting, ale Enchanting Infuser jest blizszy jednej funkcji Enchanting Plus: kontrolowanemu wyborowi enchantow.

6. **Extra Utilities trzeba rozbic per funkcja.**  
   `Extra Utilities Reborn` istnieje na 1.18.2 i warto go trzymac jako opcje nostalgiczna, ale nie powinien byc jedynym celem. Filing Cabinet, transfer nodes, drums, trash can, quarry, spawn control i generatory maja lepsze zamienniki w roznych modach.

## Kontekst mapy 5GB

Skan byl celowany po `TileEntity.id`, objal `1194/1195` plikow regionu i znalazl `952107` dopasowan do modow z czesci 2. Jeden region nie dal sie zdekompresowac: `r.-10.2.mca` (`incomplete or truncated stream`).

| Mod | Dopasowania TE | Najwazniejsze ID |
|---|---:|---|
| Carpenter's Blocks | 847410 | `TileEntityCarpentersBlock` 839642, `TileEntityCarpentersGarageDoor` 6572 |
| BuildCraft-like | 33330 | `GenericPipe` 2727, `Laser` 1268; uwaga: sa tez nadmiary z Mekanism/Railcraft/LP |
| Big Reactors | 25778 | `BRFuelRod` 10411, `BRReactorPart` 7453, `BRReactorGlass` 2210 |
| CustomNPCs | 25673 | `TileNPCChair` 9308, `TileNPCCouchWood` 5771, `TileNPCTable` 5107 |
| Extra Utilities-like | 8597 | `TileEntityFilingCabinet` 7230, `drum` 838, `TileEntityTrashCan` 172 |
| ComputerCraft | 5522 | `wiredmodem` 4217, `monitor` 694, `computer` 34 |
| BiblioCraft | 5402 | `BookcaseTile` 2184, `GenericShelfTile` 1018, `LampTile` 928 |
| Blood Magic | 303 | `containerAltar` 16 plus kilka altar-like ID; czesc trafien jest z Witchery/Thaumcraft |
| EnderStorage | 86 | `Ender Chest` 83, `Ender Tank` 3 |
| Enchanting Plus | 21 | `eplus:advancedEnchantmentTable` 14 |
| Chisel | 10 | `autoChisel` 3; zwykle bloki Chisela nie sa liczone przez TE scan |

Ograniczenie: wynik nie jest pelnym skanem blokow. Dla Chisel, wielu dekoracji Extra Utilities, Angel Block, Magnum Torch, Cursed Earth itp. potrzebny jest osobny skan palette/numeric ID, bo te bloki zwykle nie maja TE.

## Decyzje per mod

| Mod 1.7.10 | Najlepszy cel 1.18.2 | Ocena planu |
|---|---|---|
| BiblioCraft | Supplementaries + Handcrafted + Macaw Furniture + vanilla frames | Plan z jednym zamiennikiem jest za prosty; split daje lepsze pokrycie |
| Big Reactors | Bigger Reactors | Lepsze dopasowanie do lokalnego modpacka niz Extreme Reactors |
| Blood Magic | Blood Magic 3 | Plan poprawny; wymagany konwerter NBT altarow/rytualow |
| Bookshelf | Bookshelf/dependency only | Ignorowac w konwerterze mapy |
| BuildCraft | Pipez + RFTools Builder + XNet/Integrated Dynamics + Thermal/Mekanism | Plan ogolnie dobry, ale trzeba rozbic rury/quarry/lasery/gates |
| Carpenter's Blocks | FramedBlocks, fallback BlockCarpentry, custom tylko dla brakow | Plan z custom modem jest zbyt szybki; FramedBlocks powinien byc pierwszy |
| Chisel | Rechiseled + Chipped | Plan poprawny; trzeba zrobic skan blokow, nie tylko TE |
| CodeChickenCore/Lib | CodeChickenLib dependency | Nie mapowac jako content |
| CoFHCore | Thermal/FE jako warstwa energii | Nie mapowac jako content |
| ComputerCraft | CC:Tweaked | Plan poprawny; trzeba migrowac `mapa_1710/computer` |
| CraftGuide | JEI | Ignorowac w konwerterze mapy |
| CustomNPCs | Dekoracje: Handcrafted/Macaw/Supplementaries; NPC: Easy NPC + FTB Quests/KubeJS | Nie ignorowac bez skanu encji i danych NPC |
| EJML-core | dependency only | Ignorowac |
| Enchanting Plus | Enchanting Infuser | Lepszy niz Apotheosis jako bezposredni zamiennik funkcji |
| EnderStorage | EnderStorage 1.18.2 | Plan poprawny; zachowac `freq`, `owner`, `rot`, globalne inventory/fluid |
| Extra Utilities | Hybryda: Storage/Functional Storage, Pipez/XNet, RFTools Builder, Torchmaster, Mekanism/Thermal, opcjonalnie ExU Reborn | Nie wybierac jednego moda dla calego Extra Utilities |
| FastCraft | ModernFix/FerriteCore/Starlight/Rubidium/Embeddium wedlug kompatybilnosci | Tylko modpack/runtime, nie konwerter swiata |

## Priorytet implementacji

1. Carpenter's Blocks -> FramedBlocks: najwieksza skala na mapie, potrzebny ekstraktor `cover`, `shape`, `direction`, garage door/safe osobno.
2. Big Reactors -> Bigger Reactors: rozpoznawanie multiblokow reactor/turbine i mapowanie portow/control rods/fuel rods.
3. CustomNPCs dekoracje: szybkie mapowanie mebli moze uratowac duzo widocznej architektury.
4. BuildCraft/Extra Utilities: rozbic po klasach funkcji, bo aktualne liczniki maja nadmiary i mieszaja mody.
5. ComputerCraft: zachowac programy z `mapa_1710/computer`, potem mapowac komputery/monitory/modemy.
6. BiblioCraft/Chisel: dodatkowy blokowy skan palette/ID dla dekoracji bez TE.

## Zrodla zewnetrzne sprawdzone

- Bigger Reactors: https://www.curseforge.com/minecraft/mc-mods/biggerreactors
- Extreme Reactors: https://modrinth.com/mod/extreme-reactors
- Blood Magic 1.18.2: https://www.curseforge.com/minecraft/mc-mods/blood-magic/files?page=1&version=1.18.2
- EnderStorage 1.18.2: https://www.curseforge.com/minecraft/mc-mods/ender-storage-1-8/files/all?page=1&pageSize=20&version=1.18.2
- FramedBlocks: https://www.curseforge.com/minecraft/mc-mods/framedblocks
- BlockCarpentry: https://www.curseforge.com/minecraft/mc-mods/blockcarpentry/files?page=1
- Enchanting Infuser 1.18.2: https://www.curseforge.com/minecraft/mc-mods/enchanting-infuser/files/3896429
- Extra Utilities Reborn: https://www.curseforge.com/minecraft/mc-mods/extra-utilities-reborn
- Pipez: https://www.curseforge.com/minecraft/mc-mods/pipez
- Integrated Dynamics: https://www.curseforge.com/minecraft/mc-mods/Integrated-Dynamics/
