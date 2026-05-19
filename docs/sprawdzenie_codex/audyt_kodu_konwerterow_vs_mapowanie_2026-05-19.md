# Audyt kodu konwerterow vs aktualne mapowanie funkcjonalnosci

Data: 2026-05-19  
Zakres: `src/converters/` + nowe mapowanie z `docs/sprawdzenie_codex/cz1-5_funkcjonalnosci_mapowanie_1182_2026-05-18.xlsx` i raportow cz1-cz5.  
Cel: sprawdzic, czy obecne kody konwersji zakladaja dobra konwersje funkcjonalnosc -> funkcjonalnosc.

## Werdykt

Wiekszosc gotowych konwerterow A->A jest zgodna z nowym mapowaniem: AE2, Mekanism, EnderStorage, Blood Magic i Enchanting Plus ida w dobrym kierunku. Najwieksza niezgodnosc dotyczy **Growthcraft**, bo kod nadal konwertuje do `growthcraft_cellar/growthcraft_milk/growthcraft_apiary`, a nowe sprawdzenie uznaje Growthcraft CE za niepewny target dla strict 1.18.2. Druga wazna roznica to **Better Storage**, gdzie kod preferuje Iron Chests, a nowe mapowanie wskazuje Sophisticated Storage jako lepszy glowny odpowiednik funkcji magazynowej.

## Niezgodnosci wymagajace poprawki

| Priorytet | Konwerter | Co zaklada kod | Aktualne mapowanie | Ocena |
|---|---|---|---|---|
| Krytyczne | Growthcraft | Bezposredni target `growthcraft_cellar:*`, `growthcraft_milk:*`, `growthcraft_apiary:*` | Strict 1.18.2: `Farmer's Delight` + `Brewin' and Chewin'` + `Productive Bees`/food addony per funkcja | Kod jest niezgodny z aktualnym wyborem celu |
| Wysokie | Better Storage | Reinforced Chest/Locker -> `ironchest:*`, Locker -> `minecraft:barrel`/Iron Chest | Glowny cel: `Sophisticated Storage`, Iron Chests tylko prosty fallback | Funkcjonalnie dziala, ale nie jest najlepszym mapowaniem |
| Srednie | Better Storage locks | Lock/key -> `lockandkey:*` | W nowszej analizie ostrozniej: SecurityCraft/lore albo reczna migracja owner/lock | Wymaga weryfikacji moda `lockandkey` dla paczki 1.18.2 |
| Srednie | BiblioCraft | Bookcase -> `supplementaries:book_pile`, kilka maszyn druku -> `minecraft:oak_planks`, DiscRack -> `minecraft:jukebox` | Split: Supplementaries + Handcrafted + FramedBlocks + Immersive Paintings + raport/loot dla danych | Ogolny kierunek poprawny, ale kilka targetow jest zbyt stratnych |
| Srednie | Jammy Furniture | Bardzo szerokie mapowanie do `mcwfurnitures:*` | Po skanie cz3 tylko `TileEntityBath` jest pewnym kandydatem Jammy; `cfm*` to MrCrayfish | Kod moze byc poprawny jako osobny konwerter, ale nie powinien byc uruchamiany heurystycznie na `cfm*` |
| Niskie/Srednie | ProjectRed Expansion | ItemImporter/FilteredImporter/Teleposer oznaczone jako usuniete | Core ProjectRed tak, ale usuniete funkcje warto fallbackowac do XNet/Integrated Dynamics/AE2 raportowo | Nie blokuje, ale moze tracic funkcje |

## Szczegoly

### Growthcraft - niezgodne z aktualnym targetem

Kod:
- `src/converters/growthcraft/mappings/__init__.py` mapuje fermentacje i beczki do `growthcraft_cellar:*`, mleczarstwo do `growthcraft_milk:*`, pszczoly do `growthcraft_apiary:*`.
- `src/converters/growthcraft/nbt_converters/fermentation_barrel_converter.py` zwraca `growthcraft_cellar:fermentation_barrel`.
- Testy w `src/converters/growthcraft/tests/` asseruja te same ID.

Problem: po audycie cz3 i porownaniu z Kimi nie traktujemy Growthcraft CE jako pewnego celu strict 1.18.2. Oficjalne pliki nie potwierdzaja stabilnego targetu 1.18.2. Obecny kod jest wiec przywiazany do celu, ktory moze nie istniec w docelowej paczce.

Rekomendowana zmiana:
- albo zamrozic ten konwerter jako wariant `growthcraft_ce_experimental`,
- albo dodac nowy wariant strict 1.18.2:
  - `fermentBarrel` -> `brewinandchewin:keg` albo dekoracyjny/raportowy keg + eksport plynow,
  - `brewKettle`/`fruitPress` -> `farmersdelight`/`create`/`brewinandchewin` per funkcja,
  - `beeBox` -> `productivebees` albo raport genetyki/loot,
  - milk/cheese -> Farmer's Delight/Croptopia/food-addon fallback.

### Better Storage - cel dziala, ale nie jest najlepszym celem funkcjonalnym

Kod:
- `src/converters/betterstorage/mapping.py` mapuje `reinforcedChest`, `reinforcedLocker`, `thaumiumChest` do `ironchest:*`.
- `src/converters/betterstorage/nbt_converter.py` robi to samo w implementacji (`_convert_reinforced_chest`, `_convert_reinforced_locker`).

Nowe mapowanie:
- dla Better Storage glownym celem powinno byc `Sophisticated Storage`, bo lepiej zachowuje funkcje storage/upgrade/organizacji,
- `Iron Chests` ma zostac fallbackiem dla prostego "wieksza skrzynia".

Rekomendowana zmiana:
- dodac tryb targetu, np. `target_profile="sophisticated_storage"` i `target_profile="iron_chests_legacy"`;
- domyslnie:
  - reinforced chest/locker -> `sophisticatedstorage:chest` albo `sophisticatedstorage:barrel` z tier/lore,
  - crate -> nadal osobny loader `data/crates`, ale target raczej `sophisticatedstorage:barrel/chest` niz vanilla chest,
  - lock/key -> eksport owner/lock do lore/raportu, nie pewne `lockandkey:*` bez testu.

### BiblioCraft - zgodny kierunek, ale za duzo stratnych placeholderow

Kod:
- `src/converters/bibliocraft/nbt_converter.py` ma dobry split na `Supplementaries`, `FramedBlocks`, `Immersive Paintings`.
- Jednoczesnie mapuje kilka waznych blokow do `minecraft:oak_planks`: `WritingDesk`, `Typewriter`, `TypesettingTable`, `PrintPress`, `FurniturePaneler`, `PaintPress`.
- `DiscRack` idzie w `minecraft:jukebox`, co zachowuje tylko jeden dysk.
- `Bookcase` idzie w `supplementaries:book_pile`, czyli 16 slotow BiblioCraft -> 4 sloty.

Ocena: to nie jest sprzeczne z mapowaniem, bo BiblioCraft nie ma portu, ale kod powinien byc wyrazniej oznaczony jako **stratny** i powinien generowac skrzynie/loot ratunkowy dla nadmiarowych itemow.

Rekomendowana zmiana:
- dla Bookcase rozważyć `Handcrafted`/shelf albo `Supplementaries item shelf` tam, gdzie wazniejsze jest inventory niz wyglad stosu ksiazek,
- dla PrintPress/Typewriter/WritingDesk eksportowac tekst/ksiazki do raportu i tworzyc chest/loot obok,
- dla DiscRack przenosic nadmiar plyt do pobliskiego kontenera.

### Jammy Furniture - konwerter sam w sobie jest sensowny, ale wymaga bramki uruchomienia

Kod:
- `src/converters/jammyfurniture/jammyfurniture_mapping.py` zaklada bogaty zestaw blokow Jammy -> Macaw/Handcrafted/Supplementaries.
- `src/converters/jammyfurniture/jammyfurniture_converter.py` obsluguje TE Jammy, m.in. `TileEntityBath`.

Nowe mapowanie:
- skan cz3 skorygowal falszywe trafienia: `cfm*` to MrCrayfish, nie Jammy;
- pewnym kandydatem Jammy w skanie byl glownie `TileEntityBath` (`482`).

Ocena: kod moze byc poprawny dla prawdziwych blokow Jammy, ale nie moze byc odpalany na podstawie prefiksow `cfm*` ani starych heurystyk. Dla MrCrayfish trzeba osobny konwerter/target portu `MrCrayfish Furniture 1.18.2`, nie Jammy.

Rekomendowana zmiana:
- dodac warunek wejscia: tylko realne ID Jammy z mapy/jar, nie `cfm*`;
- dla `TileEntityBath` zachowac jako niski/ sredni priorytet;
- osobno przygotowac MrCrayfish Furniture converter, bo cz4 pokazuje 14313 TE MrCrayfish.

### ProjectRed - zgodny glowny target, ale traci niektore funkcje Expansion

Kod:
- `src/converters/projectred/mappings/block_mappings.py` mapuje ProjectRed do ProjectRed 1.18.2 i oznacza kilka blokow jako usuniete (`TileItemImporter`, `TileFilteredImporter`, `TileTeleposer`, `TileInductiveFurnace`, `TileICPrinter`).

Nowe mapowanie:
- ProjectRed + CB Multipart jest poprawnym celem,
- jednak funkcje routingu/automatyki, ktore zniknely, w praktyce powinny miec fallback do `XNet`, `Integrated Dynamics`, AE2 lub raportu rekonstrukcji.

Rekomendowana zmiana:
- dla `TileItemImporter`/`TileFilteredImporter` generowac raport i opcjonalny placeholder `xnet:connector`/`integrateddynamics` zamiast pustego targetu,
- dla `TileICPrinter` zapisac dane projektu/IC do raportu, bo sam `removed=True` ukrywa strate.

## Konwertery zgodne z nowym mapowaniem

| Konwerter | Ocena |
|---|---|
| AE2 | Zgodny. Kod celuje w AE2 11.7.6; lossy fallbacki dla Crank/Grinder/CableBus sa jawnie opisane. |
| Mekanism | Zgodny. Kod celuje w Mekanism 10.2.5 i ma sensowne fallbacki dla usunietych plastic/obsidian TNT/copper. |
| EnderStorage | Zgodny. Kolory/frequency i chest/tank ida do tego samego modu. Uwaga tylko na owner UUID/nazwy graczy. |
| Blood Magic | Zgodny. Ten sam mod, mapowanie altar/run/master stone ma sens. Usuniete bloki sa jawnie ostrzegane. |
| EnchantingPlus | Zgodny z decyzja Codex. Kod uzywa `Enchanting Infuser`, co jest blizsze funkcji kontrolowanego enchantowania niz globalny overhaul Apotheosis. |

## Braki implementacyjne wzgledem aktualnego mapowania

Nie znalazlem aktywnych konwerterow dla kilku funkcji, ktore po nowym audycie sa wazne:

| Mod/funkcja | Status |
|---|---|
| Carpenter's Blocks -> FramedBlocks/CuttableBlocks | Brak aktywnego konwertera w `src/converters`; to najwiekszy brak wzgledem skali mapy. |
| ForgeMultipart -> CB Multipart | Brak pelnego konwertera `savedMultipart`; ProjectRed ma wlasne multipart helpers, ale to nie pokrywa 798105 `savedMultipart`. |
| Railcraft -> strict 1.18.2 fallback | Brak konwertera; decyzja targetu nadal strategiczna. |
| MrCrayfish Furniture -> port 1.18.2 | Brak osobnego konwertera mimo duzej liczby TE. |
| Placeable Items -> Placeable Items 1.18.2 | Brak konwertera; mala skala, ale nie ignorowac. |
| Open Modular Turrets -> K-Turrets | Brak konwertera. |
| Forestry -> Productive Bees/Create/Thermal | Brak konwertera. |
| Thaumcraft/Witchery/Traincraft | Brak konwerterow; zgodnie z mapowaniem najpierw potrzebny eksport danych/placeholdery. |

## Rekomendowana kolejnosc poprawek kodu

1. **Growthcraft**: rozdzielic obecny kod na `Growthcraft CE experimental` i `strict_1182_functional` z Brewin' and Chewin'/Farmer's Delight/Productive Bees.
2. **Better Storage**: przelaczyc domyslny target magazynow na Sophisticated Storage, zostawic Iron Chests jako profil fallback.
3. **BiblioCraft**: dodac ratunkowy output dla itemow/tekstow, ktore nie mieszcza sie w BookPile/Jukebox/oak_planks placeholder.
4. **Jammy/MrCrayfish**: zabezpieczyc Jammy przed `cfm*` i zaczac osobny konwerter MrCrayfish.
5. **ProjectRed**: dodac raport/fallback dla usunietych blokow Expansion.
6. **Dopiero potem** duze brakujace konwertery: Carpenter's/FramedBlocks+CuttableBlocks i ForgeMultipart/CB Multipart.

