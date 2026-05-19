# Modpack 1.7.10 — funkcjonalności modów (część 5)

> Zakres: opis funkcji + lista najważniejszych bloków / TileEntities / przedmiotów oraz integracji dla poniższych pozycji.  
> **Uwaga dot. “wszystkich bloków/ID”**: bez bezpośredniego wglądu do `.jar` (dekompilacja / analiza rejestrów) nie da się **w 100% gwarantować** kompletnej listy *każdego* bloku/TE/ID. Dla dużych modów (Thaumcraft, Thermal, Witchery) poniżej dostajesz bardzo szczegółowy opis + **pełne kategorie** i **metodę wygenerowania kompletnej listy ID** z Twojej instancji (NEI/Opis/dump).  

---

## Jak wygenerować kompletną listę bloków/TE/ID z konkretnej instancji 1.7.10 (polecane)

1. **NEI (NotEnoughItems)**  
   - Wejdź w tryb przeglądania przedmiotów i przechodź po zakładkach (Item Panel).  
   - Użyj wyszukiwania `@modid` (np. `@thaumcraft`) aby wylistować wszystkie rzeczy z moda.  
   - W razie potrzeby: eksport listy przez screenshoty / kopiowanie nazw + automatyczne parsowanie.

2. **Opis (profilowanie/inspekcja)**  
   - Opis nie eksportuje “ID list” wprost, ale świetnie pomaga wykrywać **TileEntity** po nazwach klas / zachowaniu (co “tyka” i ile).  
   - Przy okazji wyłapiesz, które bloki są TE (a które zwykłe bloki).

3. **Dump z konfiguracji / ID-map**  
   - W 1.7.10 wiele modów trzyma mapy ID w configach (lub generuje logi przy starcie).  
   - Szukaj w `.minecraft/config/` po frazach: `block`, `item`, `id`, `I:` / `B:` / `S:`.

4. **Szybki “zrzut rejestru” przez skrypt (gdy masz serwer / dev env)**  
   - Najpewniej: mod/plugin do dumpu `GameData` (Forge) albo mały coremod.  
   - Jeśli będziesz chciał — mogę przygotować gotowy snippet pod 1.7.10 (Forge) generujący plik CSV/JSON z: `registryName`, `unlocalizedName`, `className`, `isTileEntity`, itp.

---

# Lista modów

## 1) Reliquary — `Reliquary-1.7.10-1.2.1.483.jar`
**Typ:** “magiczne gadżety” / przedmioty specjalne + kilka bloków funkcyjnych  
**Idea:** trudniejsze do zdobycia artefakty dające bardzo konkretne przewagi (utility, walka, mobilność, QoL).

### Najważniejsze funkcjonalności
- Zestaw unikatowych **artefaktów** (często z dropów mobów) i “magicznych narzędzi”.
- Przedmioty obronne/utility (odpychanie mobów, przenośne zasoby, przyciąganie łupów, itp.).
- Przedmioty ofensywne (np. broń palna/miotacze/ładunki zależnie od wersji/konfigu).

### Bloki / TileEntities
- **Altar of Light / Altar of Alkahestry** — konwersja *3 redstone* → *1 glowstone block* w czasie i pod dostępem do słońca.  
  - To zwykle **blok działający w czasie** (w praktyce “konsumuje” redstone, “pracuje” i generuje glowstone na górze).
- (W zależności od paczki/wersji) *inne bloki alchemiczne* mogą występować jako osobne stanowiska; kompletna lista najpewniej przez `@xreliquary`/`@reliquary` w NEI.

### Przedmioty (przykłady najbardziej rozpoznawalne)
- **Coin of Fortune** — “magnes” na itemy i XP (teleportuje dropy do gracza).  
- **Interdiction Torch** — odpycha moby w zasięgu (często też deflektuje część pocisków).  
- **Infernal Chalice** — przenośne “magazynowanie lawy” / odporność w lawie kosztem głodu.  
- Różne artefakty / bronie / amulety (pełna lista: NEI `@reliquary`).

### Integracje / uwagi
- W modpackach często wchodzi w interakcje z systemami łupów, EMC, itp. (zależnie od dodatków).  
- Jeśli chcesz **100% listę** bloków/przedmiotów z tej wersji: najlepiej NEI + filtr `@reliquary` oraz spis w pliku.

Źródła (opisy przykładowych itemów i Altar of Light):  
- CurseForge Reliquary Reincarnations (opis itemów)  
- FTB Wiki: Altar of Light (Xeno’s Reliquary)

---

## 2) RadarBro — `RadarBro\settings.txt` - UWAGA - konwersja niewymagana - ignoruj
**To nie jest mod `.jar`, tylko plik ustawień** dla moda RadarBro (GUI radar).

### Co robi RadarBro
- Dodaje **radar na HUD** pokazujący: moby, graczy, sojuszników, wrogów i inne encje.
- Pozwala:
  - włączać/wyłączać ikony poszczególnych kategorii,
  - oznaczać graczy jako **Ally/Enemy** (kolory np. zielony/czerwony),
  - przełączać **Auto Rotation** oraz **Player Names**,
  - zapisywać listy Ally/Enemy i ustawienia do plików w katalogu `.minecraft\mods\RadarBro\`.

### `settings.txt` — typowa zawartość / co zwykle kontroluje
Zależnie od wersji moda, `settings.txt` zwykle trzyma:
- pozycję i skalę radaru,
- włączone warstwy (moby/gracze/encje),
- tryb rotacji,
- widoczność nazw,
- filtry / kolory / przezroczystość,
- listy Ally/Enemy mogą być w osobnych plikach lub w tym samym folderze.

> Jeśli podeślesz ten `settings.txt` (tu w czacie), mogę go od razu **zinterpretować linia po linii** i opisać wszystkie opcje.

Źródła: opis funkcji + lokalizacja plików: MinecraftForum RadarBro.

---

## 3) Statues — `statues-1.7.10-2.1.4.jar`
**Typ:** dekoracje + funkcjonalne “ekspozytory” (Showcase)  
**Zależność:** zwykle **AsieLib** (co masz w paczce).

### Funkcjonalności
- Tworzenie **posągów (Statues)** z wybranych materiałów, z użyciem skina dowolnego gracza (Twojego lub cudzego).
- **Showcase** — blok do **prezentowania i przechowywania** wartościowego przedmiotu (gablotka/ekspozytor).

### Bloki / TileEntities
- **Statue** (różne warianty materiałowe) — najczęściej TE/niestandardowy render.
- **Showcase** — TE (przechowuje item i renderuje go).

### Integracje / uwagi
- Często używany stricte do RP/dekoracji w bazach/hubach serwerowych.
- Pełną listę wariantów materiałowych/statue-types najłatwiej zobaczyć przez NEI `@statues`.

Źródła: Modrinth (opis Statue + Showcase, zależność AsieLib).

---

## 4) Thaumcraft — `Thaumcraft-1.7.10-4.2.3.5.jar`
**Typ:** duży mod magiczny (badania, aspekty, aura/vis, alchemia, infuzja, golemancja)  
**Skala:** bardzo dużo bloków, itemów i mechanik.

### Rdzeń rozgrywki
- **Aspekty (Aspects)**: prymalne i złożone; skanowanie świata i przedmiotów odkrywa wiedzę.  
- **Badania (Research)**: progres w książce, odblokowuje receptury i urządzenia.
- **Vis / Aura Nodes** (w 1.7.10): magia pozyskiwana z otoczenia; zarządzanie aurą i skutkami ubocznymi (np. flux).
- **Alchemia**: przeróbka przedmiotów na essentia, wytwarzanie nowych składników i receptur.
- **Infuzja**: zaawansowane craftingi na ołtarzu infuzyjnym (stabilność, składniki wokół).
- **Golemancja**: tworzenie golema + rdzenie/usprawnienia do automatyzacji.

### Najważniejsze bloki / TileEntities (rdzeń)
Poniżej “must-have” stacje i elementy konstrukcji (zwykle TE):
- **Arcane Worktable** — “arcane crafting” z użyciem Vis z różdżki w GUI.
- **Crucible** — baza alchemii (topienie + essentia).
- **Infusion Altar** (multiblok) — **Runic Matrix**, **Arcane Pedestal**, Arcane Stone/Bricks (konstrukcja wieloblokowa).
- **Alchemical Furnace / Advanced Alchemical Furnace** — przetwarzanie essentii (zależnie od researchu).
- **Warded Jars** / magazynowanie essentii (różne warianty słoików).
- **Nitor** (światło), **Goggles of Revealing** (utility), itp. — część “ikonicznych” elementów.

### Przedmioty / narzędzia / “części”
- **Różdżki (Wands)**: rdzenie, końcówki (caps), focusy (foci).
- **Thaumonomicon** (księga badań).
- Materiały: **shards**, **salts**, **gems**, **cloth**, itp.
- Komponenty do golema: korpusy, rdzenie, dodatki.

### Integracje / dodatki
- W Twojej paczce są dodatki: NEI plugin, Thaumic Energistics, Thaumic Exploration, Thaumic Horizons, Thaumic Tinkerer (i in.).  
  To bardzo rozszerza “ekosystem” Thaumcraft.

### Jak uzyskać kompletną listę bloków/TE
- NEI: filtr `@thaumcraft` (najprostsze).
- W FTB Wiki (kategorie) można podejrzeć masę stron, ale najszybciej i najdokładniej jest NEI w tej instancji.

Źródła: CurseForge Thaumcraft 4.2.3.5 + wiki stron TC (Aspects, Crucible, Arcane Worktable, Infusion Altar).

---

## 5) Thaumcraft NEI Plugin — `thaumcraftneiplugin-1.7.10-1.7a.jar` - UWAGA - konwersja niewymagana - ignoruj
**Typ:** integracja z NEI dla Thaumcraft 4

### Co dodaje
- Lepszą widoczność receptur i informacji Thaumcraft w **NEI**:
  - podglądy receptur specyficznych dla TC (alchemia, infuzja, arcane crafting),
  - podpowiedzi / integrację “magicznych” craftów w panelu NEI,
  - wygodniejsze przeglądanie rzeczy związanych z aspektami i elementami TC (zakres zależy od wersji).

> Najpewniejsza weryfikacja “co dokładnie pokazuje” w tej wersji: w grze otwórz NEI i klikaj zakładki/ikony dodane przez plugin (zwykle pojawia się dodatkowy panel/overlay dla TC).

Źródła: wpisy paczek Technic + opis integracji “Not Enough Items Integration for Thaumcraft 4”.

---

## 6) Thaumic Energistics — `thaumicenergistics-1.0.0.5.jar`
**Typ:** integracja Thaumcraft 4 ↔ Applied Energistics 2 (ME)  
**Cel:** trzymanie i transport **essentii** w ME Network.

### Funkcjonalności (rdzeń)
- **Import/Export essentii** do sieci ME.
- **Essentia Storage** w ME (komórki/składowanie) + możliwość użycia **Thaumcraft jars** jako “extension”.
- Podgląd ilości essentii w sieci (monitory/terminal).
- Interfejsowanie z urządzeniami Thaumcraft używającymi **suction**.
- Integracja z infuzją (np. wsparcie dla urządzeń infuzyjnych / Runic Matrix).
- Możliwość emisji sygnału redstone zależnie od ilości essentii w sieci.

### Bloki / TileEntities (typowe elementy TE)
Nazewnictwo może się lekko różnić zależnie od wersji, ale zwykle obejmuje:
- **Essentia Import Bus / Export Bus**
- **Essentia Storage Bus**
- **Essentia Terminal / Crafting Terminal (Thaumcraft-themed)**
- **Essentia Storage Cells** (przedmioty; współpracują z ME Drive/ME Chest)

Źródła: CurseForge Thaumic Energistics + FTB Wiki.

---

## 7) Thaumic Exploration — `ThaumicExploration-1.7.10-1.1-55.jar`
**Typ:** dodatek do Thaumcraft 4 (zbalansowana zawartość “w stylu TC”)

### Funkcjonalności
- Nowe elementy progresji i “smaczki” Thaumcraft:
  - nowe bloki,
  - nowe rdzenie/elementy różdżek (wand rod / caps zależnie od wersji),
  - enchanty,
  - użyteczne przedmioty,
  - receptury transmutacji i integracje.

### Bloki / TileEntities
- CurseForge i wątki wskazują, że mod zawiera **ok. 6 nowych bloków** (część jako remake starszych TC2).  
- Dokładne nazwy najlepiej zaciągnąć z NEI: `@thaumicexploration` lub `@tce` (modid zależny od wersji).

Źródła: CurseForge + FTB Wiki Thaumic Exploration (opis zakresu zawartości).

---

## 8) Thaumic Horizons — `thaumichorizons-1.7.10-1.1.9.jar`
**Typ:** duży dodatek do Thaumcraft 4 (nowe zastosowania znanych mechanik)

### Funkcjonalności (najważniejsze)
- **Arcane Lenses** do Goggles of Revealing / podobnych:
  - np. night vision, “x-ray” przez 1 warstwę, podgląd stworzeń przez ściany, auto-skanowanie bloków pod celownikiem.
- **Wand Focus: Containment** — zmniejszanie stworzeń i przechowywanie ich w “warded jars”.
- **Biological Alchemy** — przyspieszanie upraw, duplikacja mięsa, przetwarzanie dropów (np. zombie → skóra), itp.
- Systemy związane z **Mob Infusion** (charakterystyczna mechanika moda).

### Bloki / TileEntities (przykładowe kategorie)
- Stacje alchemiczne/biologiczne (różne “laboratoryjne” bloki).
- Słoje/pojemniki/urządzenia do Containment i infusionów.
- Wiele bloków ma własne GUI/stan => bardzo często TE.

### Integracje / uwagi
- Jest to mod “duży”, więc 100% lista: NEI `@thaumichorizons` + ewentualnie spis do pliku.

Źródła: CurseForge opis Thaumic Horizons + FTB Wiki.

---

## 9) Thaumic Tinkerer — `ThaumicTinkerer-2.5-1.7.10-542.jar`
**Typ:** dodatek do Thaumcraft (gadżety, enchanty, narzędzia, automatyzacje, peryferia CC)

> W ekosystemie 1.7.10 najczęściej spotkasz “Thaumic Tinkerer 2” (różne buildy). JAR w paczce to linia 2.5 dla 1.7.10.

### Funkcjonalności (rdzeń)
- **Osmotic Enchanting**: enchantowanie “na wybór”, zamiast losowych enchantów z vanilla table.
- Zestaw nowych enchantów + narzędzia do:
  - zdejmowania enchantów (craft/grid),
  - magazynowania XP (zależnie od wersji).
- Różne “tinker” gadżety Thaumcraft (focusy, utility, mobility, itp.)
- Często: **ComputerCraft peripherals** do części bloków (automatyzacja magii przez CC).

### Najważniejsze bloki / TileEntities
- **Osmotic Enchanter** (TE, GUI)  
  - Wymaga otoczenia **Obsidian Totem** + Nitor (klasyczny setup), oraz różdżki o min. określonych capach.
- (W zależności od wersji) dodatkowe urządzenia/elementy “tinker” — pełna lista: NEI `@thaumictinkerer`.

Źródła: FTB Wiki Thaumic Tinkerer 2 + Osmotic Enchanter.

---

## 10) Thermal Foundation — `ThermalFoundation-[1.7.10]1.2.6-118.jar`
**Typ:** baza surowcowa/świat + materiały dla całej serii Thermal (i modów CoFH)

### Funkcjonalności
- Nowe **rudy** i zasoby (generacja świata): m.in. copper, tin, silver, lead, ferrous/nickel, shiny/platinum, mana infused, itp.  
- Nowe **materiały**: pyły, ingoty, blendy/alliances, elementy do maszyn, komponenty energetyczne.
- Moby serii Thermal (w zależności od wersji): np. blizz/blitz/basalz.

### Bloki / “świat”
- **Ores / Fluid Ores / specjalne kamienie**: destabilized redstone ore, energized netherrack, resonant end stone, oil sand/shale (zależnie od serii/konfigu).
- Pełna lista jest długa — w praktyce NEI `@thermalfoundation` daje 100% z tej instancji.

Źródła: FTB Wiki Thermal Foundation + dokumentacja Team CoFH (lista kategorii rud).

---

## 11) Thermal Expansion — `ThermalExpansion-[1.7.10]4.1.5-248.jar`
**Typ:** główny mod maszynowy serii Thermal (RF), przerób surowców, generacja energii, automatyzacja.

### Funkcjonalności (rdzeń)
- **Maszyny do przeróbki** (ore doubling, smelting, smelting + catalyst, itp.).
- **Dynama** (generatory RF) — kilka typów, różne paliwa.
- **Tiers / Upgrade Kits / Conversion Kits**: maszyny i dynama mają poziomy, wpływ na prędkość, pojemność RF i sloty augmentów.
- **Augments**: modyfikatory działania (wydajność, side-config, specjalne tryby, itp.).
- **Urządzenia (Devices)**: generatory wody/cobble/obsidian, próżniaki, itp. (zależnie od wersji TE4).

### Bloki / TileEntities — (najbardziej klasyczne TE4)
**Maszyny (Machines):**
- Redstone Furnace  
- Pulverizer  
- Sawmill  
- Induction Smelter  
- Phytogenic Insolator  
- Compactor  
- Magma Crucible  
- Fractionating Still  
- Fluid Transposer  
- Energetic Infuser  
- Sequential Fabricator  
(+ zależnie od builda: Centrifugal Separator, itp.)

**Dynama (Dynamo):**
- Ogólnie “6 typów” dynam (różne paliwa; np. magmatic, reactant, numismatic, i inne).

**Devices (często spotykane):**
- **Aqueous Accumulator** (woda bez RF z 2 źródeł + deszcz)
- **Igneous Extruder** (cobble/smooth stone/obsidian; bez RF)
- inne “utility devices” zależnie od paczki/konfigu.

### Integracje
- Współpraca z **Thermal Dynamics** (ducts) i **Thermal Foundation** (materiały).
- Wymaga CoFH Core (masz w paczce).

Źródła: FTB Wiki Thermal Expansion / Thermal Expansion 4 + przykładowe strony maszyn (Pulverizer, Induction Smelter) i device (Igneous Extruder, Aqueous Accumulator).

---

## 12) Thermal Dynamics — `ThermalDynamics-[1.7.10]1.2.1-172.jar`
**Typ:** transport dla serii Thermal (rury/ducts dla itemów, płynów i RF)

### Funkcjonalności
- **Ducts** jako system transportu:
  - **Itemducts** (itemy),
  - **Fluiducts** (płyny),
  - **Fluxducts** (RF).
- Elementy sterujące:
  - **Servo** (ekstrakcja + filtrowanie z/do inventory/tank),
  - elementy routingu i konfiguracji sieci.
- Wspólne mechaniki: kierunki, priorytety, round-robin, filtrowanie, tryby czerwonego kamienia (zależnie od typu duct/servo).

### Bloki / TileEntities
- Same ducty to zwykle bloki z własnym zachowaniem sieciowym (część to TE w sensie “tile logic”).  
- Dodatkowe części: **Structuralduct** (okładziny/covers), różne tier’y ductów.

Źródła: FTB Wiki Thermal Dynamics (opis ducts + kategorie).

---

## 13) Traincraft — `Traincraft-4.3.5_014.jar`
**Typ:** transport (pociągi, wagony, zeppeliny), własne tory i infrastruktura kolejowa

### Funkcjonalności (rdzeń)
- **80+ pojazdów**: lokomotywy, wagony, pojazdy specjalne (w zależności od wersji).
- Integracja z vanilla railami i Railcraft, oraz **własne rozjazdy i łuki** (“big switches and curves”).
- **GUI lokomotyw**:
  - paliwo + woda (parowe), diesel/biofuel (diesle), redstone/baterie (elektryczne),
  - hamulce, cargo itp.
- Sterowanie:
  - `R` — GUI w pojeździe,
  - `W/S` — przyspiesz/zwolnij (w praktyce zależy od mapowania klawiszy),
  - `H` — gwizdek (często).
- Mechanika **overheating** (stany ciepła wpływające na osiągi).
- **Zeppeliny**: latanie sterowane WASD + patrzenie (zależnie od wersji).

### Świat / surowce
- Może dodawać generację: **oil sands / petrol / copper** (konfigurowalne w `Traincraft.cfg`).

### Bloki / “infrastruktura” (często TE)
- **Traincraft Guide** (item/książka) — “oficjalna” instrukcja w grze z recepturami.
- Różne **stoły/stanowiska** do craftingu taboru i torów (np. builder/track-builder zależnie od wersji).
- Tory specjalne, zwrotnice, krzyżownice, sygnalizacja (zakres zależy od builda).

Źródła: CurseForge Traincraft (opis “80+ vehicles”, switches/curves) + oficjalny “quick guide” (kontrole, generacja, config).

---

## 14) UUID offline — `uuidoffline-1.0.jar` - UWAGA - konwersja niewymagana - ignoruj
**Typ:** mały mod “API/naprawczy” dla 1.7.10

### Co robi
- Dostarcza/udostępnia “UUID offline” w środowisku 1.7.10, aby inne mody mogły poprawnie identyfikować graczy po UUID (np. przy trybie offline / specyficznych serwerach / kompatybilności).
- Zwykle nie dodaje bloków ani itemów — to “helper”.

Źródła: CurseForge UUID offline (“UUID needed in 1.7.10? No problem.”).

---

## 15) Witchery — `witchery-1.7.10-0.24.1.jar`
**Typ:** rozbudowana magia “wiedźm” (rytuały, brews, poppets, voodoo, mutacje, infuzje)

### Główne dziedziny (mechaniki)
- **Circle Magic** (rytuały na kręgach, glyphy/kręgi).
- **Voodoo** (poppets, laleczki, powiązania z graczami/mobami).
- **Brews** (mikstury/napary) — wiele typów: liquid/instant/gas/trigger.
- **Infusions** (player/object infusions) — trwałe modyfikacje.
- **Conjurations, Mutations, Symbol Magic** i inne systemy (progres przez składniki naturalne).

### Najważniejsze bloki / TileEntities (start i core)
- **Witches Oven** — podstawowe przetwarzanie składników + “fumes”; często pierwszy krok progresu.
- **Clay Jars** (pojemniki na składniki/fumes, zależnie od wersji).
- **Cauldron / Kettle / Distillery**  
  - **Distillery**: ekstrakcja wyższych tierów essencji, korzysta z mocy pobliskiego **Altar**.
- **Altar** (struktura/“moc” na potrzeby przepisów i rytuałów).
- **Poppet Shelf** (TE)  
  - przechowuje do 9 poppetów aktywnych poza ekwipunkiem; zwykle utrzymuje chunk loaded.

### Przedmioty (kluczowe kategorie)
- **Poppets** (różne typy ochrony/efektów) + narzędzia voodoo.
- Składniki naturalne: zioła, pyły, części mobów, itp.
- Książki/poradniki (zależnie od paczki), talizmany, symbole.

### Moby / świat
- Witchery dodaje własne stworzenia i interakcje (coven witches, byty rytualne, zależnie od progresu).

### Jak uzyskać pełną listę bloków/TE
- NEI: `@witchery` (najpewniejsze).
- W praktyce Witchery ma dziesiątki bloków/przedmiotów — listing “na sucho” bez NEI będzie zawsze ryzykiem pominięć.

Źródła: FTB Wiki Witchery (dziedziny magii), Poppet Shelf, Distillery.

---

## 16) WorldEdit (Forge) — `worldedit-forge-mc1.7.10-6.1.1-dist.jar` - UWAGA - konwersja niewymagana - ignoruj
**Typ:** narzędzie budowlane/admin (edycja świata), komendy i schematy

### Funkcjonalności
- Selekcja regionów (różne tryby): cuboid, sphere, cylinder, poly, itp.
- Operacje na regionach:
  - `//set`, `//replace`, `//walls`, `//overlay`, `//smooth`, itd.
- Clipboard / schematics:
  - `//copy`, `//cut`, `//paste`
  - zapisywanie/ładowanie schematów (format zależny od wersji).
- Generatory:
  - `//sphere`, `//cyl`, narzędzia pędzli (brushes),
  - komendy drzew/lasów (`/tree`, `/forestgen`) — w 6.1.1 dla 1.7.10 wspominane są “tree types” oraz poprawki.
- Narzędzia:
  - `//wand` (różdżka zaznaczania; domyślnie drewniana siekiera),
  - superpickaxe, narzędzia “mask/replace”, itp.

### Integracje / uwagi
- W wydaniu 6.1.1 dla 1.7.10 wzmiankowane są m.in. poprawki i wsparcie dla ForgeMultipart (wg changelogu CurseForge).
- W praktyce: WorldEdit jest “must-have” do budowania, kopiowania struktur, naprawiania terenu i pracy na serwerze.

Źródła: CurseForge WorldEdit 6.1.1 (1.7.10) + wiki komend WorldEdit.

---

# Checklista zależności w Twojej paczce (przydatne)
- **Statues** → zwykle wymaga **AsieLib** (masz w paczce).  
- **Thermal Expansion / Dynamics / Foundation** → wymagają **CoFHCore** (masz w paczce).  
- **Thaumic Energistics** → wymaga **Thaumcraft 4** + **AE2** (AE2 jest w paczce) + często dodatkowych bibliotek zależnie od wersji.

---

## Jeśli chcesz, żebym zrobił “pełne 100% listy bloków/TE” dla tych modów
Najprościej: wrzuć mi (tu) **zrzut NEI** z filtrem `@modid` albo wrzuć **listę eksportowaną** (np. z logu/configu, jeśli masz).  
Wtedy zrobię:
- kompletną tabelę: *block/item*, *registry/unlocalized name*, *czy TileEntity*, *krótki opis*, *zastosowania*, *integracje*, *warianty/metadane*.
