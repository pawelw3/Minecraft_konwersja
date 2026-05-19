# Analiza funkcjonalnosci modow 1.7.10 - czesc 3

Data: 2026-05-18  
Zakres: `docs/mod_mapping_indepth/from/mod_funkcjonalnosci_1.7.10_cz3.md` + `docs/mod_mapping_indepth/to/konwersja_1710_do_1182_mapowanie_modow_cz3.md`  
Arkusz zbiorczy: `docs/sprawdzenie_codex/cz1-5_funkcjonalnosci_mapowanie_1182_2026-05-18.xlsx`

## Najwazniejsze korekty

1. **ForgeMultipart / `savedMultipart` to priorytet krytyczny.**  
   Celowany skan TE znalazl `798105` wpisow `savedMultipart`. Najlepszym celem jest `CB Multipart` 1.18.2, ale to wymaga prawdziwego konwertera part list, nie prostego remapu blokow.

2. **Growthcraft CE nie powinien byc wpisany jako pewny port 1.18.2.**  
   CurseForge pokazuje wydania m.in. 1.16.5, 1.19.4 i 1.20.1, ale nie stabilne 1.18.2. Dla celu 1.18.2 najlepszy praktyczny zestaw to `Farmer's Delight` + `Brewin' and Chewin'`, a pszczoly/fishtrap/milk trzeba rozbic per funkcja.

3. **IC2: lepszy cel dla tej paczki to Mekanism + Thermal, nie FTB Industrial Contraptions jako glowny target.**  
   FTBIC istnieje jako IC2-like dla 1.18.2, ale nie jest lokalnie w aktualnym zestawie i wprowadza osobny system energii. Poniewaz projekt ma lokalnie Mekanism/Thermal, sensowniej mapowac IC2 semantycznie do FE-ekosystemu.

4. **LogisticsPipes nie powinno isc tylko w Pipez.**  
   `Pipez` przeniesie transport, ale nie request/crafting. Najlepszy split: `Pretty Pipes` dla ducha request/logistics, `AE2` dla duzych sieci i autocraftingu, `XNet/Integrated Dynamics` dla warunkow/routingu.

5. **Jammy Furniture wymaga weryfikacji ID z jar.**  
   Surowy skan lapal `cfm*`, ale to MrCrayfish Furniture, nie Jammy. Po korekcie zostaje tylko `TileEntityBath` jako kandydat Jammy (`482`), wiec nie nalezy budowac wnioskow o Jammy na `cfmFridge/cfmCabinet`.

6. **Flan's Mod wymaga osobnego skanu encji i inventory.**  
   TE scan nie znalazl pewnych TE Flana, ale pojazdy i bronie moga siedziec jako encje lub itemy content-packow. Najlepszy funkcjonalny target to `TaCZ` dla broni oraz `Immersive Vehicles`/`Immersive Aircraft` dla pojazdow.

## Kontekst mapy 5GB

Wykonano celowany skan `TileEntity.id` po `1195` regionach. Skan przeczytal `665995` chunkow z danymi i `2447396` tile entities. Jeden chunk w `r.-10.2.mca` zwrocil blad dekompresji (`incomplete or truncated stream`), analogicznie do poprzednich analiz.

Po korekcie recznej klasyfikacji:

| Mod / grupa | Dopasowania TE | Najwazniejsze ID |
|---|---:|---|
| ForgeMultipart | 798105 | `savedMultipart` 798105 |
| Forestry | 75621 | `forestry.Leaves` 52443, `forestry.Wood` 16253, `forestry.Swarm` 6389, `forestry.Apiary` 227 |
| Mekanism | 22900 | `SalinationTank` 16608, `InductionCasing` 2781, `ElectricPump` 541 |
| Growthcraft | 1475 | `fermentBarrel` 1106, `brewKettle` 119, `fruitPress/Presser` 104 |
| LogisticsPipes | 912 | `LogisticsTileGenericPipe` 750, `LogisticsCraftingTableTileEntity` 145 |
| IC2 | 771 | `Reactor Chamber` 138, `Solar Panel` 135, `MFSU` 53, `Compressor` 52 |
| Jammy candidate | 482 | `TileEntityBath` 482 |

Ograniczenie: to nadal jest skan TE. Nie obejmuje zwyklych blokow bez TE, itemow w skrzyniach/playerdata ani encji, wiec Flan's Mod, kable IC2, uprawy i czesc dekoracji wymagaja osobnych skanow.

## Decyzje per mod

| Mod 1.7.10 | Najlepszy cel 1.18.2 | Ocena planu |
|---|---|---|
| Flan's Mod | TaCZ + Immersive Vehicles + opcj. Immersive Aircraft | Plan dobry ogolnie, ale potrzebny skan encji/itemow content-packow |
| Forestry | Productive Bees + Create/Thermal/Mekanism + vanilla/modded leaves fallback | Plan dobry, ale na mapie najwiecej jest lisci/drewna, nie maszyn |
| ForgeEssentials | FTB Essentials/LuckPerms/utility server stack | Nie mapowac chunkow |
| ForgeMultipart | CB Multipart | Krytyczny priorytet, musi byc perfekcyjny konwerter `savedMultipart` |
| ForgeRelocation | Brak 1:1; Create tylko jako funkcja podobna | Nie mapowac danych swiata |
| Growthcraft | Farmer's Delight + Brewin' and Chewin' + Productive Bees | Plan z Growthcraft CE jako portem 1.18.2 jest ryzykowny/niepotwierdzony |
| HelpFixer | Brak | Ignorowac |
| IC2 Nuclear Control | CC:Tweaked + redstone/peripherals | Plan poprawny, ale trzeba sprawdzic realne ID w mapie |
| IC2 | Mekanism + Thermal Series; FTBIC tylko opcjonalnie | Lepsze dla tej paczki niz FTBIC jako glowny cel |
| iChunUtil/GollumCoreLib/MobiusCore | dependencies only | Ignorowac |
| Jammy Furniture | Macaw's Furniture + Handcrafted + Supplementaries | Najpierw zweryfikowac ID; `cfm*` to nie Jammy |
| LiteLoader/Omniscience | client QoL, poza mapa | Ignorowac |
| LogisticsPipes | Pretty Pipes + AE2 + XNet/Integrated Dynamics | Lepsze niz samo Pipez |
| Mekanism | Mekanism 10.2.5 + Generators + Tools | Plan poprawny; potrzebny remap NBT i multiblokow |

## Priorytet implementacji

1. `savedMultipart` -> CB Multipart: najwieksza liczba TE w czesci 3 i prawdopodobnie jeden z najwiekszych tematow calej mapy.
2. Mekanism multibloki: `SalinationTank` i `InductionCasing` dominuja, a istnieje juz lokalny raport/konwerter Mekanism.
3. Forestry bloki drzew/lisci + apiary: zachowac krajobraz i pasieki, genetyke traktowac jako strata/kompensata.
4. LogisticsPipes: eksport sieci, crafting table i modules do raportu; automatyczne 1:1 jest malo realne.
5. IC2: rozdzielic maszyny, energy storage, reaktory i cropy; reaktory tylko jako rekonstrukcja funkcjonalna.
6. Growthcraft: ferment barrel/kettle/press mapowac do Brewin' and Chewin'/Farmer's Delight.
7. Flan's Mod: osobny skan encji i inventory, bo TE scan nie odpowiada na pytanie o pojazdy/bronie.

## Zrodla zewnetrzne sprawdzone

- CB Multipart: https://www.curseforge.com/minecraft/mc-mods/cb-multipart
- Productive Bees: https://www.curseforge.com/minecraft/mc-mods/productivebees
- Growthcraft CE: https://www.curseforge.com/minecraft/mc-mods/growthcraft-community-edition
- Brewin' and Chewin': https://www.curseforge.com/minecraft/mc-mods/brewin-and-chewin/files/all?page=1&pageSize=20&version=1.18.2
- FTB Industrial Contraptions: https://modsmc.ru/mod/ftb-industrial-contraptions-forge
- TaCZ: https://www.curseforge.com/minecraft/mc-mods/timeless-and-classics-zero
- Immersive Vehicles: https://www.curseforge.com/minecraft/mc-mods/minecraft-transport-simulator/
- Immersive Aircraft: https://files.xmdhs.com/curseforge/history?id=666014&ver=1.18.2
- Macaw's Furniture: https://www.curseforge.com/minecraft/mc-mods/macaws-furniture
- Pretty Pipes: https://www.curseforge.com/minecraft/mc-mods/pretty-pipes
