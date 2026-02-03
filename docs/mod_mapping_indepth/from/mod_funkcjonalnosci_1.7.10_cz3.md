# Minecraft 1.7.10 — spis funkcjonalności modów (część 3)

Paczka modów z Twojej listy:

- Flan’s Mod 4.10.0
- Forestry 4.2.16.64
- ForgeEssentials 1.4.4.1187 (client companion w nazwie pliku)
- ForgeMultipart 1.2.0.345
- ForgeRelocation 0.0.1.4 + ForgeRelocationFMP 0.0.1.2
- GollumCoreLib 2.0.0
- Growthcraft 2.7.2 (complete)
- HelpFixer 1.0.7
- IC2 Nuclear Control 2.4.3a
- iChunUtil 4.2.3
- IndustrialCraft² Experimental 2.2.827
- Jammy Furniture Reborn (1.7.10)
- LiteLoader 1.7.10
- LogisticsPipes 0.9.3.132
- Mekanism 9.1.1 + MekanismGenerators 9.1.1 + MekanismTools 9.1.1
- MobiusCore 1.2.5
- Omniscience (LiteLoader mod) 1.0.1

> Cel: „co robi” + **bloki / tile entities / itemy / integracje / konfig**.  
> Uwaga: w 1.7.10 niektóre mody mają **setki** wpisów. Tam, gdzie lista jest gigantyczna (np. IC2/Mekanism/Forestry), wypisuję **rdzeń** (to co realnie stawiasz i automatyzujesz) oraz podaję linki do pełnych katalogów.

---

## 1) Flan’s Mod 4.10.0
**Jar:** `Flans_Mod-1.7.10-4.10.0.jar`  
**Typ:** system paczek content (broń, pojazdy, mechy) + tryb drużynowy.

### Główne funkcje
- Dodaje **bronie palne, granaty**, oraz **pojazdy** (samoloty, auta, czołgi) i często **mechy** — ale *konkretna zawartość* zależy od **content packów**. citeturn1search0turn1search3turn0search16  
- System **Teams**: rozgrywka drużynowa / PvP / tryby mapowe (często używane na serwerach). citeturn1search3

### „Bloki” / Tile Entities (core moda)
W samym „core” Flan’s Mod najczęściej pojawiają się (nazewnictwo zależne od paczki, ale idea stała):
- **Workbench’e / stoły craftingu** dla content packów (np. Gun/Vehicle/Part Crafting Table) – GUI do wytwarzania broni i pojazdów.
- **Spawner / box** elementy powiązane z content packami (czasem jako itemy „Vehicle Box”, „Gun Box” itp. – to już zależy od paczki).

> Najważniejsze: 90% „listy itemów” Flan’s Mod = **zawartość paczek** (Modern Weapons, WW2, DayZ, itp.). Na stronie Flan’s Mod jest katalog packów, np. tag „Guns”. citeturn0search16turn1search0

### Itemy (core)
- Narzędzia/komendy do Teams (konfiguracja rozgrywek).
- „Parts” (części) i amunicja – zwykle dostarczane przez content packi.

### Integracje / uwagi
- Bardzo mocno zależny od paczek zawartości (to one definiują setki itemów i statystyki).
- Na serwerach: zwykle wymaga dopasowania paczek po stronie klienta i serwera.

---

## 2) Forestry 4.2.16.64 (MC 1.7.10) - UWAGA - konwersja nie wymagana - ignoruj
**Jar:** `forestry_1.7.10-4.2.16.64.jar`  
**Typ:** rolnictwo/produkcja, pszczelarstwo i hodowla drzew, maszyny, energia, poczta.

### Główne funkcje
- Rozbudowane **farming** + automatyzacja upraw (w tym jedne z większych multibloków „farmowych”). citeturn6search0turn6search6  
- **Bees / beekeeping**: księżniczki, drony, królowe, mutacje, produkty (miód, wosk, pyłki itd.). citeturn6search3turn6search0  
- Maszyny przetwarzające surowce biologiczne (biomass/biofuel, soki, oleje) i elementy logistyczne. citeturn6search9turn6search0

### Kluczowe bloki / Tile Entities (rdzeń)
**Pszczelarstwo**
- **Apiary** (TE / „dom” pszczół; podstawowy blok do pracy królowych i krzyżowania). citeturn6search3  
- **Alveary** (multiblok – „lepsza pasieka”, większe możliwości i moduły) — często core end-game w Forestry. citeturn6search6  
- **Beehives** (dzikie ule – generują księżniczki/drony; różne biomy)

**Maszyny przetwarzania**
- **Carpenter** (TE) — tworzenie przedmiotów z użyciem płynów (np. seed oil, honey, itp.)  
- **Squeezer** (TE) — wyciskanie nasion/roślin → oleje/soki  
- **Fermenter** (TE) — biomasa / fermentacja materii organicznej → Biomass citeturn6search9  
- **Centrifuge** (TE) — odwirowywanie produktów pszczelich/organicznych  
- **Still** (TE) — destylacja płynów (np. Biomass → Biofuel)  
- (zależnie od configu: **Moistener**, **Analyzer / Beealyzer** w łańcuchu pszczelarskim)

**Farming / multibloki**
- **Multifarm** (multiblok) + **Farm blocks / hatches / gearboxes** (zależnie od wersji) — automatyzacja pól, sadów, drzew. citeturn6search6

**Energia**
- **Engines** (np. Peat Engine / Biogas Engine) — generacja energii z paliw biologicznych.

**Poczta i handel**
- **Mailbox / Trade Station / Stamp Collector** (elementy systemu poczty; zależy od wersji i addonów).

### Itemy / narzędzia (przykłady)
- **Beealyzer** (analiza genów pszczół) – zwykle craft w Carpenter. citeturn6search19  
- Ulepszenia do Alveary (frame’ y, wentylacja, heater/cooler itp. — zależnie od wersji)
- Surowce: wosk, miód, propolis, pollen, combs, apiculture gear.

### Integracje / uwagi
- Historycznie projektowany pod kompatybilność z IC2 i BuildCraft (wiele maszyn korzystało z „silników” i rur). citeturn6search0  
- W modpackach często występują addony (Binnie’s Mods, Extra Bees/Trees, itp.) — rozszerzają listy pszczół/drzew.

---

## 3) ForgeEssentials 1.4.4.1187 (server utility)  - UWAGA - konwersja nie wymagana - ignoruj
**Jar:** `forgeessentials-1.7.10-1.4.4.1187-client.jar` (z nazwy: komponent kliencki / companion)  
**Typ:** zestaw narzędzi serwerowych typu „Bukkit/Essentials dla Forge”.

### Główne funkcje
- ForgeEssentials to „suite” narzędzi administracyjnych: **komendy**, **teleport**, **ochrona regionów**, **permissions**, **chat**, **backups**, **economy**, **multiworld** itd. citeturn5search5turn5search19  
- Działa głównie **server-side** (klientowy companion bywa opcjonalny dla wybranych feature, np. CUI do WorldEdit). citeturn5search5

### Moduły (często spotykane)
Z logów/konfiguracji i opisów spotyka się m.in.: Afterlife, Backups, Chat, Commands, Economy, Multiworld, Permissions, PlayerLogger, Protection, Remote, Scripting, SignTools, Teleport, Tickets, WEIntegrationTools, perftools. citeturn5search19

### Konfig / permissions
- System permissions node’ów (można deny/allow grupom) – dokumentacja permission/commands jest w wiki-forkach i plikach list. citeturn0search10turn0search7turn0search14

### Bloki/TE/itemy
- Zwykle **nie** dodaje bloków gameplay (to mod narzędzi serwerowych).

---

## 4) ForgeMultipart 1.2.0.345 (ChickenBones)  - UWAGA - microblocks są bardzo powszechne na mapie i muszą być przekonwertowane perfekcyjnie
**Jar:** `ForgeMultipart-1.7.10-1.2.0.345-universal.jar`  
**Typ:** biblioteka do „wielu rzeczy w jednym bloku” (microblocks / multiparts).

### Funkcje
- Pozwala mieć **kilka elementów w jednej kratce** (np. microblocki, przewody, fasady, itp. – zależnie od modów, które to wykorzystują). citeturn0search2turn0search11  
- Sam ForgeMultipart to **framework**: realny content daje np. CB Multipart / ProjectRed / różne microblock addony.

### Bloki/TE/itemy
- Sama biblioteka nie musi dodawać „fajnych” bloków do kreatywnej zakładki; jest przede wszystkim dependency.

---

## 5) ForgeRelocation + ForgeRelocationFMP - UWAGA - konwersja nie wymagana - ignoruj
**Jary:**  
- `ForgeRelocation-1.7.10-0.0.1.4-universal.jar` citeturn2search0  
- `ForgeRelocationFMP-1.7.10-0.0.1.2-universal.jar` (plugin) citeturn3search0  

**Typ:** wsparcie do **przenoszenia bloków „bezpiecznie”** (zachowanie TE) + integracja z FMP.

### Funkcje
- „Move ALL the blocks!” — biblioteka wykorzystywana przez mody, które przesuwają/relokują bloki z TE. citeturn2search0  
- Plugin FMP dodaje możliwość relokacji elementów w „frames” z ForgeMultipart („Put parts inside frames?”). citeturn3search0  

### Bloki/TE/itemy
- Zwykle brak własnych maszyn; jest dependency/infrastruktura.

---

## 6) GollumCoreLib 2.0.0 (1.7.10)  - UWAGA - konwersja nie wymagana - ignoruj
**Jar:** `GollumCoreLib-2.0.0-1.7.10.jar`  
**Typ:** biblioteka (dependency) dla modów „Smeagol”/GollumTeam.

### Funkcje (z repo)
- Fabryki rejestracji bloków/itemów, logger, version checker, helpery, loader configów adnotacjami, auto-spawner „block entity” itp. citeturn3search5turn3search17  
- W praktyce: **nie gameplay**, tylko core dla innych modów.

---

## 7) Growthcraft 2.7.2 (complete)
**Jar:** `growthcraft-1.7.10-2.7.2-complete.jar`  
**Typ:** pakiet modułów rolniczo-spożywczych (uprawy + przetwórstwo + browarnictwo).

### Moduły (typowo w „complete”)
- **Growthcraft-Core** (rdzeń)  
- **Grapes / Hops / Rice**: winogrona, chmiel, ryż + powiązane mechaniki. citeturn6search2turn1search13  
- **Cellar**: system fermentacji / beczki / alkohol / „tipsy” efekty. citeturn6search8  
- Często także: **Apples**, **Bamboo**, **Bees**, **Milk**, **Fishtrap** (zależnie od kompilacji i configu). citeturn1search13turn6search8

### Kluczowe bloki / Tile Entities (najczęstsze)
**Uprawy i rośliny**
- Krzaki/pnącza: **Grapes**, **Hops vines**, **Rice paddies** (specyficzne zasady sadzenia; np. hops często wymagają „rope/trellis”). citeturn6search10turn6search2  
- **Bamboo**: różne bloki budowlane (scaffolding, fence/wall, charcoal itp.). citeturn1search17  

**Cellar (fermentacja)**
- Rodzina bloków związanych z fermentacją/lejkami/beczkami (np. fermenting barrel + naczynia) – centralny moduł „browarniczy”. citeturn6search8  

### Itemy / produkty
- Jedzenie, napoje, surowce (chmiel/ryż/winogrona → ale/wino/sake itd.).
- Różne „ingredienty” i przetwory.

### Integracje / uwagi
- Typowo „roleplay” + farming; często w modpackach jako źródło jedzenia i buffów.

---

## 8) HelpFixer 1.0.7  - UWAGA - konwersja nie wymagana - ignoruj
**Jar:** `HelpFixer-1.0.7.jar`  
**Typ:** naprawa komendy `/help` na serwerach (modded).

### Funkcje
- Omija błędny kod sortowania komend, dzięki czemu `/help` nie wywala błędu i działa poprawnie. citeturn5search1turn3search2  
- Loguje „offending commands” do logów serwera, żebyś widział co psuje help. citeturn5search1  
- **Server-side only** (w SSP instalujesz „na kliencie”, bo klient = serwer). citeturn5search1  

### Bloki/TE/itemy
- Brak.

---

## 9) IC2 Nuclear Control 2.4.3a
**Jar:** `IC2NuclearControl-2.4.3a.jar`  
**Typ:** monitoring reaktorów IC2 + alarmy i czujniki (redstone).

### Główne funkcje
- Budowa systemu monitoringu temperatury/bezpieczeństwa reaktora IC2. citeturn2search1turn2search5  
- Alarmy przemysłowe (Howler Alarm / Industrial Alarm) do sygnalizacji awarii. citeturn2search1  

### Kluczowe bloki / Tile Entities (przykłady)
- **Thermal Monitor** — monitoruje temperaturę reaktora i wystawia sygnał redstone po przekroczeniu progu (można odwrócić). citeturn2search5  
- Dodatkowe monitory/sensory (energia, stan) – zależnie od wersji; wiki FTB ma przegląd. citeturn2search1

### Itemy
- Elementy do budowy sieci monitoringu (kable/sensory/karty) — zależnie od wersji.

---

## 10) iChunUtil 4.2.3  - UWAGA - konwersja nie wymagana - ignoruj
**Jar:** `iChunUtil-4.2.3.jar`  
**Typ:** biblioteka dla modów iChun (dependency).

### Funkcje
- „Shared library required by a couple of my mods… majority of my mods will require this as a base.” citeturn2search15turn2search7  
- Nie jest to mod gameplay (bez iChun modów typu Morph/PortalGun/Hats itd. nic nie wnosi).

---

## 11) IndustrialCraft² Experimental 2.2.827
**Jar:** `industrialcraft-2-2.2.827-experimental.jar`  
**Typ:** techno-klasyk: EU, generatory, maszyny, kable, reaktory, surowce, crops.

### Główne funkcje (wysoki poziom)
- System energii **EU** (tier’y napięć), **kable i transformatory**, storage (batbox/mfe/mfsu).  
- Maszyny przetwarzania rud (macerator, ore washing, thermal centrifuge, itd.) + automatyzacja. citeturn1search18turn6search12turn6search20  
- **Nuclear reactor** (produkcja energii i ryzyko; rozbudowane komponenty chłodzenia/zarządzania ciepłem).  
- „Crops / cross-breeding” (rolnictwo IC2) + surowce przemysłowe.

### Kluczowe bloki / Tile Entities (rdzeń)
> IC2 ma dziesiątki maszyn; poniżej top „co się stawia w bazie”, a pełne listy są w linkach.

**Maszyny bazowe**
- **Macerator**, **Extractor**, **Compressor**, **Electric Furnace**, **Recycler** citeturn6search4turn1search18  
- **Metal Former**, **Ore Washing Plant**, **Thermal Centrifuge** citeturn1search18  
- **Mass Fabricator / Replicator / Scanner / Pattern Storage** (late game) citeturn1search18  

**Energia / storage**
- **Generators**: Generator, Geothermal, Solar, Wind, Water Mill, Nuclear Reactor citeturn6search4  
- **Storage**: BatBox, MFE, MFSU (i pochodne)  
- **Transformers** (LV/MV/HV) + **kable** (tin/copper/gold/hv) i izolowane warianty. citeturn6search1  

**Reaktor jądrowy (blokowo)**
- **Nuclear Reactor** (korpus) + elementy rozbudowy (komory), a w środku: pręty paliwowe, exchangery, heat vents, plating, etc.  
- Nuclear Control (powyżej) zwykle idzie „w parze” do monitoringu. citeturn2search1  

### Itemy / surowce (przykłady)
- **Machine Casing / Basic Machine Casing** citeturn1search4  
- **Wrench / Electric Wrench**, **Mining Drill**, **NanoSuit/QuantumSuit** (zależnie od wersji)  
- Obwody (Electronic Circuit, Advanced Circuit), baterie, dust/plates.

### Gdzie znaleźć pełne listy bloków?
- IC2 Wiki: kategoria „Blocks” (pełna lista stron). citeturn6search7  
- Strona „Recipes and Resources (experimental)” (kable, komponenty, recepty). citeturn6search1  

---

## 12) Jammy Furniture Reborn (1.7.10)
**Jar:** `Jammy-Furniture-Reborn-Mod-1.7.10.jar`  
**Typ:** dużo mebli + dekoracje + trochę bloków „użytkowych”.

### Główne funkcje
- Duży zestaw bloków dekoracyjnych: krzesła, stoły, sofy, lampy, sprzęty domowe. citeturn7search7turn7search16  
- Część bloków ma funkcje survivalowe (np. storage, „zniszcz itemy”, naprawa zbroi – zależnie od implementacji). citeturn7search7  

### Bloki (przykładowe kategorie)
- Siedziska: **Chair, Arm Chair, Sofa**  
- Kuchnia/AGD: **Fridge, Freezer, Dishwasher, Cooker, Sink, Cupboards**  
- Łazienka: **Bath, Toilet, Bathroom Sink/Cupboard**  
- Dekoracje: **Blinds, Clock, Coat Stand, Lamps, Chimney, TV/Radio**, itd.

> Lista „blocks” często krąży w mirrorach; traktuj je jako *pomocnicze* (nieoficjalne). citeturn7search3turn7search12  
> Najbardziej „pierwotny” trop dla moda to długi wątek MinecraftForum (stara wersja Jammy Furniture, ale tematyka ta sama). citeturn7search16  

### Uwagi kompatybilności
- W 1.7.10 częsty problem: zależność od wersji Forge (wątek support sugeruje, że bywa wrażliwe na nowsze buildy Forge). citeturn7search1

---

## 13) LiteLoader 1.7.10  - UWAGA - konwersja nie wymagana - ignoruj
**Plik:** `liteloader-1.7.10.jar`  
**Typ:** lekki loader do modów klienckich (HUD, minimapy, QoL) – równolegle do Forge.

### Funkcje
- „Lightweight mod loader”, projektowany jako kompatybilny z Forge/FML, głównie do **client-side modów** (HUD/minimapy/chat tools). citeturn4search16turn4search12  
- Dokumentacja instalacji (manual). citeturn4search0  

### Bloki/TE/itemy
- Brak (loader).

---

## 14) LogisticsPipes 0.9.3.132
**Jar:** `logisticspipes-0.9.3.132.jar`  
**Typ:** zaawansowana logistyka na bazie BuildCraft pipes: request/crafting/autocraft.

### Główne funkcje
- Budujesz sieć „logistyczną”, w której możesz:
  - **żądać** konkretnych itemów z magazynu (request),
  - automatycznie **dostarczać** itemy do maszyn,
  - automatycznie **craftować na żądanie** (crafting pipes/modules). citeturn2search2turn6search25  

### Kluczowe bloki / Tile Entities
- **Logistics Request Table** (TE) — GUI do wyciągania itemów z sieci albo uruchamiania autocraftu. citeturn6search25  
- (często w LP są też bloki typu **Power Junction** / „Logistics Power” – zależnie od wersji i konfiguracji)

### Główne rodziny „pipe” (rdzeń)
> LP ma bardzo dużo pipe’ów i modułów; poniżej „te, które tworzą system”.

- **Provider Logistics Pipe** (źródło – mówi sieci „mam X w tej skrzyni”) citeturn2search2  
- **Request Logistics Pipe** (odbiorca – żądania gracza/automaty) citeturn2search2  
- **Supplier Logistics Pipe** (utrzymuje zapas X w danej skrzyni/machine) citeturn2search2  
- **Crafting Logistics Pipe** (autocrafting we współpracy z maszyną/stołem; „jedna recepta na pipe/module”) citeturn6search14turn6search18  
- **Chassis Pipes + Modules** (wkładasz moduły do chassis; routing/filtrowanie/crafting) – core design w LP. citeturn6search18turn2search2  

### Integracje / uwagi
- LP jest addonem na BuildCraft (działa „na rurach”), ale ma własną logikę i GUI. citeturn2search2  
- Do nauki: wiki LP + wiki GTNH ma świeższe podsumowania koncepcyjne (choć to wiki packa). citeturn2search10turn6search22  

---

## 15) Mekanism 9.1.1 (core) + Generators + Tools
**Jary:**
- `Mekanism-1.7.10-9.1.1-clienthax.jar`
- `MekanismGenerators-1.7.10-9.1.1-clienthax.jar`
- `MekanismTools-1.7.10-9.1.1-clienthax.jar`

### 15A) Mekanism (core)
**Typ:** techno „tiered” + przesył energii/itemów/płynów/gazów + bardzo rozbudowane przetwarzanie rud.

#### Główne filary
- Sieci przesyłu:
  - **Universal Cables** (energia),
  - **Mechanical Pipes** (płyny),
  - **Pressurized Tubes** (gazy),
  - **Thermodynamic Conductors** (ciepło),
  - **Logistical Transporters** (itemy z routingiem/kolorami). citeturn1search5  
- Maszyny w tierach (Basic/Advanced/Elite/Ultimate), „Factories” jako wielowariantowe procesory. citeturn1search11turn1search5  
- Bardzo duża lista bloków/maszyn — oficjalna wiki ma kategorie (np. „Blocks” ~100+ stron). citeturn1search2turn1search5  

#### Kluczowe bloki / Tile Entities (rdzeń, które realnie stawiasz)
**Magazyn/energia**
- **Energy Cubes** (tiered storage)  
- **Induction Matrix** (multiblok magazynu energii – zależnie od wersji)  
- **Chargepad** (ładowanie itemów)

**Przetwarzanie rud / chemia**
- **Crusher / Enrichment Chamber / Energized Smelter** (1–2x)  
- **Purification Chamber / Chemical Injection Chamber / Electrolytic Separator** (wyższe procesy; gazy)  
- **Pressurized Reaction Chamber**, **Chemical Dissolution/Washer/Crystallizer** (łańcuch „late” – zależnie od wersji)

**Utility / endgame**
- **Digital Miner**
- **Teleporter**
- **Quantum Entangloporter**
- **Logistical Sorter**
- **Bins** (magazyn 1-typu itemów)

> Pełna lista: kategoria „Blocks” na oficjalnej wiki. citeturn1search2

### 15B) Mekanism Generators 9.1.1
**Typ:** generacja energii dla Mekanism (bez tego modułu potrzebujesz innego źródła energii). citeturn5search13  

**Najważniejsze generatory (z opisu modułu):**
- **Heat Generator**
- **Gas-Burning Generator**
- **Bio-Generator**
- **Solar Generator**
- **Advanced Solar Generator**
- **Wind Generator**
- **Fission Reactor**
- **Fusion Reactor**
- **Turbine** citeturn5search13  

Przykład szczegółu: **Gas-Burning Generator** zużywa palny gaz (np. hydrogen/ethene) do produkcji mocy. citeturn5search17  

### 15C) Mekanism Tools 9.1.1
**Typ:** narzędzia i zbroje z materiałów Mekanism + multitool „paxel”.

- Zestawy **armor/tools/shields** dla m.in.: Bronze, Osmium, Refined Obsidian, Refined Glowstone, Steel, Lapis. citeturn5search6turn5search9  
- **Paxel** = pickaxe+axe+shovel w jednym. citeturn5search6  

---

## 16) MobiusCore 1.2.5 (1.7.10)  - UWAGA - konwersja nie wymagana - ignoruj
**Jar:** `MobiusCore-1.2.5_1.7.10.jar`  
**Typ:** biblioteka ProfMobius (dependency).

### Funkcje
- Core dla modów ProfMobius, m.in. **Opis, JABBA, WAILA, EVOC** (wymagane do uruchomienia). citeturn4search5turn4search2  
- Gameplay: brak (samo MobiusCore).

---

## 17) Omniscience (LiteLoader mod) 1.0.1  - UWAGA - konwersja nie wymagana - ignoruj
**Plik:** `mod_Omniscience_1.0.1_mc1.7.10.litemod`  
**Typ:** mały mod kliencki pod LiteLoader — „widzenie niewidzialnych”.

### Funkcje
- Pozwala widzieć **niewidzialne moby i graczy** jako częściowo przezroczyste. citeturn4search6turn4search14turn4search10  
- Opcje włącz/wyłącz osobno dla entity i playerów. citeturn4search14  

### Bloki/TE/itemy
- Brak (client QoL).

---

# Źródła / strony bazowe (najważniejsze)
- Flan’s Mod (oficjalna strona): citeturn1search0  
- Flan’s Mod (FTB wiki): citeturn1search3  
- Forestry (FTB wiki + konkretne maszyny): citeturn6search0turn6search3turn6search9  
- ForgeEssentials: citeturn5search5turn5search19turn0search10  
- ForgeMultipart / ForgeRelocation / FMP plugin: citeturn0search2turn2search0turn3search0  
- Growthcraft: citeturn6search2turn6search8turn1search17  
- HelpFixer: citeturn5search1turn3search2  
- IC2 Nuclear Control: citeturn2search1turn2search5turn2search9  
- iChunUtil: citeturn2search15turn2search7  
- IndustrialCraft² (FTB wiki + IC2 wiki): citeturn6search20turn6search7turn6search1  
- LiteLoader (oficjalna strona/dokumentacja): citeturn4search16turn4search0  
- LogisticsPipes (FTB wiki + Request Table + Crafting pipe): citeturn2search2turn6search25turn6search14  
- Mekanism (oficjalna wiki + kategoria Blocks): citeturn1search5turn1search2  
- Mekanism Generators (opis feature list): citeturn5search13  
- Mekanism Tools: citeturn5search6turn5search9  
- MobiusCore: citeturn4search5turn4search2  
- Omniscience (LiteLoader mod page + GitHub): citeturn4search14turn4search6turn4search10  
