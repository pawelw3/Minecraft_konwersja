# Sprawdzenie Codex: aktualizacja planu konwersji modow 1.7.10 -> 1.18.2

Data sprawdzenia: 2026-05-18  
Zakres: `docs/mod_mapping_indepth`, dokumenty zbiorcze w `docs/`, lokalne zrodla/JAR-y w `mod_src/` i `modpack_1710/`, plus szybka weryfikacja publicznych stron modow.

## Najwazniejsze wnioski

1. `docs/mod_mapping_indepth/to/konwersja_1710_do_1182_mapowanie_modow_cz1.md` jest zdezaktualizowany przy Armourer's Workshop. Twierdzi, ze brak wydania 1.18.2, a obecne dokumenty zbiorcze i publiczne indeksy potwierdzaja wersje 1.18.2. To trzeba poprawic w planie.
2. Carpenter's Blocks nie wymaga juz zalozenia "piszemy wlasny mod" jako jedynej drogi. Lokalnie istnieja `FramedBlocks` i `BlockCarpentry`; FramedBlocks ma bardzo szeroki zestaw ksztaltow, w tym `framed_collapsible_block`, a BlockCarpentry ma podstawowy zestaw frame/illusion/stairs/slab/door/fence. Wlasny mod zostaje tylko jako fallback dla bardzo specyficznego zachowania Carpenter's, nie jako punkt startowy.
3. Growthcraft trzeba przeniesc z "do weryfikacji" do "czesciowo dostepny jako port/rewrite, ale wymaga mapowania modulow". Lokalnie jest repo `mod_src/actual_src/1.18.2/Growthcraft` z assetami dla `growthcraft`, `growthcraft_apiary`, `growthcraft_apples`, `growthcraft_bamboo`, `growthcraft_cellar`, `growthcraft_milk`, `growthcraft_rice`.
4. Placeable Items ma wydanie 1.18.2. Nie powinien byc w statusie "do weryfikacji"; trzeba sprawdzic tylko, czy stare TE/format pozycji da sie przepisac, czy raczej odtwarzac dekoracje z itemu i orientacji.
5. Railcraft Reborn jest realnym celem dla duzej czesci Railcrafta, a lokalne zrodla 1.18.2 zawieraja tory, sygnaly, detektory, zbiorniki, coke oven, blast furnace, crusher itd. Trzeba jednak traktowac TE/multibloki jako konwersje wysokiego ryzyka.
6. ProjectRed w 1.18.2 ma bardzo dobra ciaglosc dla lamp, rud/materialow, czesci logiki i maszyn, ale w pobranych JAR-ach sa tylko Core/Illumination/Integration. Jesli mapa uzywa Transportation/Mechanical/Expansion/Fabrication, trzeba dobrac komplet modulow 1.18.2 albo mapowac czesc na zamienniki.
7. IC2, BuildCraft i Logistics Pipes nadal nie maja dobrego A->A dla twardego celu Forge 1.18.2. Najrozsadniejszy kierunek z planu pozostaje: IC2 -> Mekanism/Thermal, BuildCraft -> RFTools Builder/Pipez/Pretty Pipes/Create, Logistics Pipes -> Pretty Pipes/Pipez/XNet/AE2.
8. Witchery/Thaumcraft/Traincraft nadal sa konwersja "w duchu", nie migracja. Sa dobre zamienniki klimatu lub funkcji, ale nie nalezy obiecywac przeniesienia progresu, rytualow, badan, bytow ani pojazdow jako tych samych danych.

## Korekty do dokumentow

| Obszar | Obecny problem | Zalecana korekta |
|---|---|---|
| Armourer's Workshop | `cz1` mowi "brak 1.18.2"; dokumenty zbiorcze mowia "jest 3.2.7-beta" | Status: "jest port 1.18.2, konwersja danych skinow/TE trudna". Nie usuwac etapu koncowego, ale zmienic uzasadnienie. |
| Carpenter's Blocks | `PLAN.md` i analiza zakladaja wlasny mod | Status: "najpierw FramedBlocks/BlockCarpentry, wlasny mod tylko dla brakujacych zachowan". |
| Growthcraft | status "do weryfikacji" | Status: "repo 1.18.2 lokalnie obecne, mapowac modulowo; sprawdzic kompatybilnosc runtime i zaleznosci". |
| Placeable Items | status mieszany: ignoruj / do weryfikacji / jest | Status: "jest 1.18.2; konwersja opcjonalna dla dekoracyjnych TE, nie ignorowac w ciemno". |
| Railcraft | miejscami "brak kompletnego Railcrafta" | Status: "Railcraft Reborn istnieje i lokalnie ma szeroki zakres blokow; TE i multibloki osobno". |
| ProjectRed | stare planowanie nie rozdziela modulow | Dopisac warunek instalacji kompletnego zestawu modulow 1.18.2, nie tylko Core/Illumination/Integration. |
| BiblioCraft/Jammy/MrCrayfish | mapowanie miejscami za waskie | Uzywac zestawu: Supplementaries + Handcrafted + Macaw's Furniture + Immersive Paintings + FramedBlocks/BlockCarpentry. |

## Priorytet wedlug realnej konwertowalnosci

### A. Najlepsze A->A lub prawie A->A

Te mody/bloki warto konwertowac najpierw, bo istnieje bezposredni mod 1.18.2 albo bardzo bliski nastepca.

| Mod 1.7.10 | Cel 1.18.2 | Co konwertowac | Ryzyko |
|---|---|---|---|
| Applied Energistics 2 | AE2 11.x | kontrolery, dyski, terminale, kable, storage cells, wzorce | Srednie/wysokie dla sieci i NBT dyskow |
| Mekanism | Mekanism 10.2.5 | maszyny, kable, rury, zbiorniki, energia, gaz | Srednie, duzo zmian NBT |
| Thermal Foundation/Expansion/Dynamics | Thermal Series 9.2.2 | maszyny, conduity/dynamika, energy/fluid/item storage | Srednie/wysokie, zwlaszcza conduity |
| Tinkers' Construct | TiC 3.7.x | stoly, smeltery/foundry, narzedzia jako kompensacja | Wysokie dla narzedzi i materialow |
| Blood Magic | Blood Magic 3.2.x | altar, runy, dekoracje, storage krwi/progres gracza | Wysokie dla progresu |
| EnderStorage | EnderStorage 2.9.x | ender chest i ender tank; lokalne 1.18.2 ma blockstates `ender_chest`, `ender_tank` | Srednie, czestotliwosc/kolory/owner moga miec inny NBT |
| Iron Chests | Iron Chests 1.18.2 | chesty metalowe i inventory | Niskie/srednie |
| Storage Drawers jako cel | Storage Drawers 1.18.2 | JABBA barrel -> drawer/controller/slave | Srednie, pojemnosc i upgrades nie sa 1:1 |
| ProjectRed Illumination/Integration/Core | ProjectRed 4.17 | lampy, rudy, przewody/gates jesli modul docelowy obecny | Srednie/wysokie dla multipart/gates |
| Reliquary | Reliquary 1.18.2 | bloki/itemy, pedestale, alchemy | Srednie |

### B. Dobre zamienniki funkcjonalne

Tu da sie zachowac bryle, funkcje albo inventory, ale nie oczekiwac identycznego moda.

| Mod 1.7.10 | Cel 1.18.2 | Bloki/funkcje do mapowania |
|---|---|---|
| Better Storage | Sophisticated Storage/Backpacks, Iron Chests, Supplementaries | reinforced chest/locker/crate -> storage; backpack -> Sophisticated; locks/keys tylko jako utrata lub lore |
| Backpacks/Eydamos | Sophisticated Backpacks | plecaki i inventory itemow; upgrade'y recznie lub fallback |
| BiblioCraft | Supplementaries + Handcrafted + Immersive Paintings + FramedBlocks | bookcase/shelf/potion shelf -> item shelf/book pile; map/painting frames -> Immersive Paintings/vanilla; tables/chairs -> Handcrafted; furniture paneler -> framed/carpentry |
| Jammy Furniture/MrCrayfish 1.7.10 | Macaw's Furniture + Handcrafted + Supplementaries | meble po typie i drewnie; inventory w szafkach zrzucac do chest/drop listy, jesli brak kompatybilnego storage |
| Carpenter's Blocks | FramedBlocks + BlockCarpentry | block/slope/stairs/slab/door/fence/trapdoor/button/pressure plate; camo material do NBT block entity celu |
| BuildCraft | RFTools Builder + Pipez/Pretty Pipes/Create/XNet | quarry/filler/builder jako RFTools Builder; pipes jako Pipez/Pretty Pipes; tanks/fluid pipes jako Pipez/Mekanism |
| IC2 | Mekanism/Thermal | macerator -> enrichment chamber/pulverizer; compressor/extractor/e-furnace -> Mek/Thermal; cables -> FE cables; EU -> FE z mnoznikiem w planie |
| Logistics Pipes | Pretty Pipes + Pipez + XNet/AE2 | basic/provider/request/crafting/supplier pipes jako moduly Pretty Pipes lub rekonstrukcja sieci |
| Forestry | Productive Bees + Create/Thermal/Farmer's Delight | ule/pszczoły/geny wymagaja osobnego eksportu; maszyny i farmy jako funkcjonalne zamienniki |
| Extra Utilities | Extra Utilities Reborn + Pipez + RFTools + Torchmaster/Angel Block | generatory, angel block, transfer nodes, drums; tylko czesc ma bliski port |
| Open Modular Turrets | K-Turrets/Immersive Engineering/CC:Tweaked | turrety jako nowe bloki bez zachowania dokladnego celu/amunicji |
| PowerConverters | Mekanism/Thermal energy compat | zwykle usunac/przepisac na FE adapter lub kabel |

### C. Jest port/zamiennik, ale konwersja danych jest trudniejsza niz sama dostepnosc

| Mod | Decyzja |
|---|---|
| Armourer's Workshop | Wersja 1.18.2 istnieje. Konwertowac bloki warsztatowe A->A, ale skiny/biblioteki/manekiny traktowac jako osobny projekt migracji formatu. Plan "na koncu" nadal ma sens, lecz nie dlatego, ze nie ma moda. |
| Railcraft | Railcraft Reborn ma szeroki zestaw blokow, w tym tory specjalne, sygnaly, detektory, zbiorniki, coke oven/blast furnace/crusher. Tory/dekoracje sa dobre do mapowania; multibloki, sygnalizacja i routing to etap wysokiego ryzyka. |
| Growthcraft | Lokalny port/rewrite ma duzo modulow. Uprawy i dekoracje konwertowac, fermentacje/booze/fluid tanki sprawdzac przez testowy swiat. |
| Placeable Items | Port 1.18.2 istnieje. Nie ignorowac automatycznie, jesli mapa ma TE z polozonymi itemami; warto wygenerowac liste wystapien i odtworzyc item/orientacje. |
| Statues | Jest Statues na 1.18.2, ale stary mod Asie/Statues i nowy Statues prawdopodobnie maja inny model danych. Zachowac lokalizacje/material, konfiguracje skina zwykle recznie lub przez dedykowany importer. |

### D. Konwersja "w duchu", bez realnego A->A na 1.18.2

| Mod 1.7.10 | Cel | Co zachowac |
|---|---|---|
| Thaumcraft + addony | Ars Nouveau + Occultism + Botania + AE2 | bryly budowli, skrzynie/inventory, dekoracje; research/aspekty/aura praktycznie nowa progresja |
| Witchery | Hexerei + Enchanted: Witchcraft + Occultism | rosliny, kotly/rytualne dekoracje, klimat lokacji; rytualy/curses/familiars jako nowa konfiguracja |
| Traincraft | Create + Create Steam'n'Rails + Little Logistics / Immersive Vehicles | infrastruktura torowa i stacje jako rekonstrukcja; pojazdy raczej screenshot/export i reczne odtworzenie |
| Flan's Mod | TaCZ + Immersive Vehicles / Create | bron/pojazdy jako zamienniki; entity i content packi nie sa kompatybilne |
| IC2 Nuclear Control | CC:Tweaked monitory | zachowac polozenie monitorow i ewentualny opis, programy napisac od nowa |
| Thaumic Energistics | AE2 + Occultism | ME infrastruktura AE2 osobno, essentia storage jako utrata albo rekonstrukcja magicznego storage |

## Bloki i TE, ktore warto liczyc na mapie przed implementacja

Najpierw trzeba wygenerowac faktyczne wystapienia z `mapa_1710`, bo bez tego latwo poswiecic tydzien na blok, ktorego nikt nie postawil.

1. Armourer's Workshop: armourer/workshop, skin library/global library, skinning table, dye table, hologram projector, mannequin, global skin data poza chunkami.
2. Carpenter's Blocks: kazdy typ bloku z camo materialem i shape metadata; szczegolnie slope, stairs, door, barrier/fence, hatch/trapdoor, collapsible block.
3. ProjectRed: multipart wires/gates, lamps, machines, frames, tubes/routing pipes, IC workbench/fabrication tables. Rozdzielic po module.
4. Railcraft: tory specjalne, coke oven/blast furnace/tank multiblocks, loaders/unloaders, detectors/signals, machines typu rock crusher/rolling machine.
5. EnderStorage: kolory/frequency/owner i osobne globalne inventory. Nie wystarczy podmienic blok.
6. AE2: storage cells i spatial/storage data, kontrolery, interface/pattern provider, quantum links, dense/smart cables, security station.
7. Mekanism/Thermal: maszyny z upgrades i energy/fluid/gas tanks; rury/kable jako sieci.
8. BiblioCraft/Jammy/MrCrayfish: bloki z inventory lub wyswietlanymi itemami, np. shelves, cases, desks, seats, lamps, signs, map/painting frames.
9. Growthcraft/Forestry/Witchery/Thaumcraft: uprawy i bloki dekoracyjne osobno od progresji/rytualow/genow/essentii.
10. BuildCraft/Logistics Pipes: pipe networks, gate wire, roboty/landmarki/quarry/filler, request/provider/crafting pipes.

## Szczegoly wybranych sporow

### Armourer's Workshop

`docs/mod_mapping_indepth/to/konwersja_1710_do_1182_mapowanie_modow_cz1.md` zawiera bledny wniosek: "brak wersji Armourer's Workshop na 1.18.2". W dokumentach zbiorczych repo jest juz poprawniejsza informacja: `docs/ANALIZA_MODOW_SZCZEGOLOWA.md` i `docs/LISTA_KONWERSJI_MODOW.md` wymieniaja Armourer's Workshop 1.18.2.

Weryfikacja publiczna: wyniki CurseForge/Modpack Index pokazuja wersje 1.18.2 dla Armourer's Workshop. Wniosek praktyczny:

- bloki warsztatowe mozna planowac jako A->A (`armourer`, `skin_library`, `skinning_table`, `dye_table`, `hologram_projector`, `mannequin`);
- skiny i biblioteki prawdopodobnie wymagaja dedykowanego eksportera/importera, a nie zwyklego `id/meta -> blockstate`;
- etap koncowy jest nadal sensowny, bo skiny sa zlozone i moga byc globalnie zapisane poza samym chunk TE.

### Carpenter's Blocks

Plan "wlasny mod wymagany" jest za mocny. Lokalnie potwierdzone cele:

- `FramedBlocks-5.11.5.jar` oraz zrodla 1.18.2: bardzo szeroka lista blockstates, m.in. `framed_cube`, `framed_slope`, `framed_stairs`, `framed_door`, `framed_button`, `framed_chest`, `framed_collapsible_block`.
- `BlockCarpentry`: lokalne blockstates `frameblock`, `falling_frameblock`, `illusion_block`, `frame_stairs`, `frame_slab`, `frame_door`, `frame_fence`, `frame_trapdoor`, `frame_button`, `frame_pressure_plate`.

Rekomendacja: dla zwyklych pokrywalnych blokow i skosow preferowac FramedBlocks. BlockCarpentry jest dobrym fallbackiem dla prostszego "Carpenter-like" zachowania. Wlasny mod tylko jesli po skanie mapy wyjda czesto uzywane typy, ktorych nie da sie odwzorowac.

### Growthcraft

Stary status "do weryfikacji" jest juz nieaktualny lokalnie. Repo 1.18.2 ma assety:

- `growthcraft` - 15 blockstates;
- `growthcraft_apiary` - 59;
- `growthcraft_apples` - 20;
- `growthcraft_bamboo` - 19;
- `growthcraft_cellar` - 49;
- `growthcraft_milk` - 37;
- `growthcraft_rice` - 5.

Rekomendacja: mapowac modulowo. Uprawy, drzewa, bamboo, rice i proste bloki sa dobrymi kandydatami. Cellar, fermentacja, plyny, cheese/booze/milk wymagaja testowego swiata i sprawdzenia NBT block entity.

### Railcraft

`cz4` ostroznie pisze o braku kompletnego Railcrafta. To warto zaktualizowac: lokalne `RailcraftReborn` ma bardzo szeroki zestaw blockstates, w tym:

- tory: `*_track`, `*_junction_track`, `*_routing_track`, `*_turnout_track`, `*_wye_track`, `*_launcher_track`, `*_locking_track`, itd.;
- sygnaly: `block_signal`, `distant_signal`, `dual_block_signal`, `dual_distant_signal`;
- maszyny/multibloki: `coke_oven_bricks`, `blast_furnace_bricks`, `crusher`, `feed_station`, `cart_dispenser`;
- zbiorniki: `*_iron_tank_wall/gauge/valve`, `*_steel_tank_wall/gauge/valve`;
- dekoracje/rudy/materialy: `abyssal_*`, `quarried_*`, `lead/tin/silver/zinc` ores.

Rekomendacja: tory i bloki strukturalne konwertowac, ale nie obiecywac automatycznej migracji calej sygnalizacji/routingu bez testow.

### ProjectRed

Lokalne JAR-y 1.18.2 zawieraja Core, Illumination i Integration; zrodla maja tez Expansion, Exploration, Fabrication. Blockstates potwierdzaja m.in.:

- Illumination: 16 kolorow lamp plus wersje inverted i smart lamp;
- Exploration: basalt/marble, ruby/sapphire/peridot/silver/tin/electrotine ores/blocks;
- Expansion/Fabrication: `auto_crafter`, `battery_box`, `block_breaker`, `charging_bench`, `deployer`, `frame`, `frame_motor`, `ic_workbench`, `lithography_table`, `plotting_table`.

Rekomendacja: przed implementacja sprawdzic, ktore moduly 1.18.2 beda realnie w paczce. Bez modulow docelowych nie mapowac mechanicznych/fabrycznych blokow w ciemno.

### Placeable Items

Plan ma sprzeczne zapisy: "ignoruj", "do weryfikacji", "jest". Publiczna weryfikacja pokazuje wersje 1.18.2. Wniosek: nie jest to priorytet silnika konwersji, ale jesli mapa ma TE z polozonymi itemami, mozna odzyskac dekoracje.

Minimalna strategia:

1. policzyc TE/bloki Placeable Items w `mapa_1710`;
2. jezeli wystapienia sa nieliczne, zrobic placeholder/screenshot liste;
3. jezeli duzo, napisac prosty mapper item + orientacja -> nowe Placeable Items.

## Zrodla i slady lokalne

Lokalne:

- `docs/mod_mapping_indepth/to/konwersja_1710_do_1182_mapowanie_modow_cz1.md` - zdezaktualizowana informacja o Armourer's Workshop.
- `docs/ANALIZA_MODOW_SZCZEGOLOWA.md` - ma juz wpis Armourer's Workshop 3.2.7-beta i sekcje mapowania.
- `docs/LISTA_KONWERSJI_MODOW.md` - ma liste aktualniejszych zamiennikow, ale nadal kilka "do weryfikacji".
- `mod_src/118/mod_jars/` - pobrane JAR-y 1.18.2: AE2, Mekanism, Thermal, FramedBlocks, ProjectRed Core/Illumination/Integration, EnderStorage itd.
- `mod_src/actual_src/1.18.2/` - dodatkowe zrodla: BlockCarpentry, Growthcraft, Handcrafted, ImmersivePaintings, Supplementaries.
- `mod_src/118/actual_src/1.18.2/RailcraftReborn` - szeroki zakres Railcraft Reborn.

Publiczne sprawdzenia:

- Armourer's Workshop: CurseForge/Modpack Index pokazuja wersje 1.18.2.
- Placeable Items: publiczne indeksy plikow pokazuja `placeableitems-4.7.1.jar` dla 1.18.2.
- Extra Utilities Reborn: CurseForge pokazuje wydania 1.18.2.
- IC2 Classic: CurseForge pokazuje aktywne wydania glownie 1.12.2 i 1.19.2, nie dobry cel 1.18.2.
- Logistics Pipes: CurseForge konczy praktycznie na 1.12.2.
- Forestry: CurseForge jako projekt oryginalny nie ma 1.18.2.
- Railcraft Reborn: Modrinth/CurseForge potwierdzaja nowoczesny Railcraft Reborn; lokalne zrodla sa wazniejsze dla zakresu blokow.
- Enchanted: Witchcraft i Hexerei: publiczne strony potwierdzaja kierunek zamiennikow Witchery dla 1.18.2.

## Rekomendowany nastepny krok techniczny

Napisac raport skanowania mapy wedlug modid/TE, zamiast dalej rozbudowywac mapowania teoretyczne. Minimalny output:

- `modid`, `block_id_1710`, `meta`, `tile_entity_id`, `count`, `sample_positions`;
- osobne flagi: `has_inventory`, `has_fluid`, `has_energy`, `has_owner`, `has_custom_name`, `has_network_data`;
- top 50 blokow modded w kazdej strefie (`billund`, `choroszcz`, `iii_rzesza`, `rzym`, `zsrr`).

Na podstawie tego mozna ustawic realna kolejnosc. Szczegolnie sprawdzilbym najpierw: Carpenter's Blocks, Armourer's Workshop, Railcraft, ProjectRed Mechanical/Transportation, Growthcraft, BiblioCraft/Jammy, EnderStorage.
