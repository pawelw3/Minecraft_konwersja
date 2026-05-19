# Minecraft 1.7.10 — spis funkcjonalności modów (część 2)

Poniżej masz **obszerny opis funkcjonalności** dla kolejnej paczki modów z Twojej listy.  
Cel: szybkie „co to daje” + **lista bloków / tile entities (jeśli występują) / itemów / integracji / configów**.

> Uwaga praktyczna: w 1.7.10 część modów ma **setki wariantów bloków** (np. Chisel), więc wypisuję:
> - **wszystkie „główne” bloki/TE** (czyli rzeczy stawiane jako osobne bloki / maszyny / porty / kontrolery),
> - oraz **kategorie wariantów** + linki do stron z pełnymi listami, gdy wariantów są tysiące.

---

## 1) BiblioCraft v1.11.7 (MC 1.7.10)
**Jar:** `BiblioCraftv1.11.7MC1.7.10.jar`  
**Typ:** dekoracje + „display storage” + druk/książki + meble.

### Główne funkcje
- Estetyczne bloki do ekspozycji i szybkiego dostępu do przedmiotów (książki, narzędzia, zbroje, mikstury).
- System **drukowania i kopiowania książek** (Typesetting + Printing Press).
- Meble i elementy „roleplay”: siedziska, stoły, dzwonek, talerze itp.
- Gadżety/utility: atlas, taśma miernicza, kompas waypoint, książka redstone do sterowania sygnałem.

### Bloki / Tile Entities (w praktyce wiele z nich ma GUI i/lub magazyn — traktuj jako TE)
Lista bloków z wiki FTB (w 1.7.10):  
- **Bookcase** (biblioteczka na książki; interakcja z enchantment table; „Redstone Book” daje sygnał)  
- **Armor Stand** (magazyn/ekspozycja setu zbroi)  
- **Display Case** (gablotka na itemy)  
- **Potion Shelf** (półka na mikstury)  
- **Tool Rack** (wieszak na narzędzia)  
- **Shelf** (półka ekspozycyjna)  
- **Wood Label** (etykiety na skrzynie/inwentarze)  
- **Desk** (pisanie książek)  
- **Typesetting Table** (przygotowanie płyt do druku)  
- **Printing Press** (kopiowanie podpisanych i/lub enchantowanych książek)  
- **Wooden Table / Table** (stół)  
- **Seat + Seat Back** (krzesła/oparcia)  
- **Dinner Plate** (talerz/dekoracja)  
- **Fancy Lantern / Fancy Lamp** (oświetlenie)  
- **Cookie Jar** (słoik na ciasteczka/„anti-theft” motyw)  
- **Disc Rack** (stojak na płyty)  
- **Map Frame** (ramka na mapy)  
- **Desk Bell** (dzwonek)  
- Dodatkowo w „Spotlights” pojawiają się m.in. **Fancy Workbench**, **Fancy Sign**, **Sword Pedestal** (zależnie od wersji/addonów)  

> Źródło listy bloków: FTB Wiki (sekcja „Blocks” + „Spotlights”).  

### Itemy / narzędzia
- **Tape Measure** (+ Tape Measure Reel jako komponent)  
- **Reading Glasses / Tinted Glasses / Monocle** (utility/„mod info” i kosmetyka)  
- **Print Press Chase / Print Press Plate / Enchanted Plate** (druk)  
- **Drafting Compass / Waypoint Compass** (mapy / nawigacja)  
- **Redstone Book** (interakcje z Bookcase/redstone)  
- **Clipboard** (checklista)  
- **Screw Gun**, **Lock and Key** (często creative-only), **Atlas** (książkowa mapa z waypointami)

### Konfig / integracje
- Addony: seria **BiblioWoods** (dodatkowe warianty dla różnych drzew/modów).
- Typowo configi: `config/BiblioCraft.cfg` (różne opcje dot. renderingu/feature).

### Linki referencyjne
- Oficjalna wiki BiblioCraft: https://www.bibliocraftmod.com/wiki/  
- FTB Wiki (BiblioCraft): https://m.ftbwiki.org/BiblioCraft

---

## 2) Big Reactors 0.4.3A
**Jar:** `BigReactors-0.4.3A.jar`  
**Typ:** duże źródła energii RF: **reaktor** + **turbina** (multibloki).

### Główne funkcje
- Budowa wieloblokowych konstrukcji:
  - **Reactor**: paliwo → ciepło → RF (bezpośrednio).
  - **Turbine**: para → turbina → RF (wysoka wydajność).
- Zależność od materiałów i układu wnętrza (pręty paliwowe, kontrolne, chłodzenie, cewki turbiny).

### Bloki / Tile Entities (multibloki i maszyny)
**Części reaktora (Reactor):**
- **Reactor Casing**
- **Reactor Glass**
- **Reactor Controller** (TE / GUI sterujące)
- **Reactor Power Tap** (wyjście energii RF)
- **Reactor Access Port** (wejście/wyjście paliwa/odpadu)
- **Yellorium Fuel Rod** (element wnętrza)
- **Reactor Control Rod** (regulacja)
- **Reactor Redstone Port**
- **Reactor Computer Port**
- **Reactor Coolant Port**
- (czasem spotykane dodatki typu Creative ports w paczkach/testach)

**Części turbiny (Turbine):**
- **Turbine Housing**
- **Turbine Glass**
- **Turbine Controller** (TE / GUI)
- **Turbine Power Port** (RF out)
- **Turbine Fluid Port** (para/woda)
- **Turbine Computer Port**
- **Turbine Rotor Bearing**
- **Turbine Rotor Shaft**
- **Turbine Rotor Blade**

**Inne bloki:**
- **Cyanite Reprocessor** (przetwarzanie/odpad → zasoby)

### Itemy / materiały
- **Ingots:** Yellorium, Cyanite, Graphite Bar, Blutonium  
- **Dusts:** Yellorium, Cyanite, Graphite, Blutonium  
- Buckety z płynami (np. fluid yellorium/cyanite) — zależnie od configu/płynów.

### Integracje
- Integracja z RF (CoFH/TE ekosystem).
- Porty komputerowe zwykle współpracują z ComputerCraft/OpenComputers (zależnie od dodatków/wrapperów).

### Linki referencyjne
- Lista części (FTB Wiki): https://ftb.fandom.com/wiki/Big_Reactors  
- Strona projektu: https://www.big-reactors.com/

---

## 3) Blood Magic 1.3.3-17
**Jar:** `BloodMagic-1.7.10-1.3.3-17.jar`  
**Typ:** magia LP (Life Points) + rytuały + alchemia + „soul network”.

### Główne pojęcia
- **LP / Life Essence**: energia pozyskiwana z poświęceń (gracz/moby).
- **Soul Network**: „konto” LP powiązane z Blood Orb.
- **Blood Altar**: centralna maszyna do transmutacji/przepisów.
- **Rytuały**: struktury z Ritual Stones + Master Ritual Stone/Imperfect Ritual Stone.

### Kluczowe bloki / Tile Entities
**Altar i runy:**
- **Blood Altar** (TE / GUI / single-slot; wielopoziomowe ulepszenia)  
- **Blood Rune** (wiele typów run: pojemność, szybkość, „sacrifice” itd.; są elementem struktury altaru)  

**Rytuały:**
- **Imperfect Ritual Stone**  
- **Master Ritual Stone**  
- **Ritual Stone** (wzory struktur)  

**Inne częste maszyny/bloki (w zależności od wersji/konfigu):**
- bloki wspierające alchemię/spelle (np. stoły/komponenty),  
- elementy „utility” związane z LP i rytuałami.

> Rytuały (lista nazw) — zobacz stronę „Rituals (Blood Magic)”.

### Itemy / narzędzia (rdzeń progresji)
- **Sacrificial Knife** (poświęcanie własnego HP)  
- **Dagger of Sacrifice** (poświęcanie mobów przy ołtarzu)  
- **Blood Orbs** (kolejne tier-y: Weak → Apprentice → Magician → Master …)  
- **Sigils** (szereg zaklęć/utility: mobilność, woda/lawa, magnetyzm, itp.)  
- **Ritual Diviner** (ułatwia budowę rytuałów)  
- Różne komponenty craftingu: „binding”, „reagent”, materiały związane z rytuałami.

### Rytuały (przykładowe — pełna lista w linku)
- Crack of the Fractured Crystal  
- Gathering of the Forsaken Souls  
- Hymn of Syphoning  
- Interdiction Ritual  
- Ritual of Binding / Containment / Regeneration / Magnetism / Speed / Crusher / itd.

### Integracje / uwagi
- Mod bardzo często integrowany z innymi (automation, sieci itemów, questy).
- Progresja zależy mocno od konfiguracji kosztów LP i dostępności surowców.

### Linki referencyjne
- Mod (CurseForge plik 1.3.3-17): https://www.curseforge.com/minecraft/mc-mods/blood-magic/files/2264826  
- FTB Wiki (ogólny opis): https://m.ftbwiki.org/Blood_Magic  
- Blood Altar: https://m.ftbwiki.org/Blood_Altar  
- Lista rytuałów: https://ftb.fandom.com/wiki/Rituals_%28Blood_Magic%29

---

## 4) Bookshelf 1.7.10-1.0.4.172 - UWAGA - konwersja nie wymagana - ignoruj
**Jar:** `Bookshelf-1.7.10-1.0.4.172.jar`  
**Typ:** biblioteka (dependency) dla innych modów.

### Co faktycznie wnosi do gameplayu?
- Zwykle **nic bezpośrednio** (to „library mod”): narzędzia dla modderów (rejestracja contentu, helpery, eventy).
- Jeśli w Twoim packu jest Bookshelf, to znaczy że **jakiś inny mod** go wymaga.

### Bloki/TE/itemy
- Zwykle brak (lub pojedyncze techniczne rzeczy niewidoczne dla gracza) — traktuj jako dependency.

### Linki referencyjne
- CurseForge (plik 1.0.4.172): https://www.curseforge.com/minecraft/mc-mods/bookshelf/files/2272637

---

## 5) BuildCraft 7.1.23 + BuildCraft Compat 7.1.7
**Jar:** `buildcraft-7.1.23.jar` + `buildcraft-compat-7.1.7.jar`  
**Typ:** automatyzacja, transport, energia, maszyny; + addon kompatybilności.

### Główne funkcje BuildCraft
- **Transport** itemów/płynów przez **rury (pipes)** + filtrowanie/sortowanie.
- **Maszyny** do wydobycia i automatyzacji (quarry / mining, pompy, itp. — zależnie od modułów).
- **Energia** (klasycznie silniki) i integracja z RF (w 1.7.10 często spotkasz BC współgrające z RF/TE).
- **Gates / Wires / logic** (warunkowe sterowanie transportem/silnikami).

### Najważniejsze bloki / Tile Entities (BuildCraft)
> BuildCraft ma dużo elementów; poniżej „core” rzeczy, które faktycznie stawia się jako bloki/maszyny.  
> Dokładna dostępność bywa zależna od modułów i configu.

**Transport / rury (Pipes):**
- Rury do itemów (np. Cobblestone/Stone/Iron/Gold/Diamond/Emerald/Obsidian — nazwy i zestaw zależą od wersji)  
- Rury do płynów (Waterproof/Fluid pipes — zależnie od wersji)  
- Elementy „Structure pipe” do wspomagania budów/struktur.

**Maszyny/crafting „late-game” BC:**
- **Assembly Table** (wytwarzanie zaawansowanych komponentów; współpracuje z laserami)  
- (często także Integration Table / Laser / Laser Table zależnie od modułów/konfiguracji)

**Wydobycie/utility:**
- Klasyczne BC bloki typu **Pump**, **Tank**, oraz „mining” urządzenia (np. Quarry/Mining Well) — zależnie od paczki modułów.

**Logika/sterowanie:**
- **Gates** (logiczne sterowanie) + przewody/”pipe wires”.

### Itemy / komponenty (BuildCraft)
- Komponenty do logiki i craftingu: **chipsety**, **wires**, **gates** (często robione przez Assembly Table).  
- Narzędzia/elementy do konfiguracji rur (filtry, itp. — zależnie od wersji).

### BuildCraft Compat (addon)
- „Klej” kompatybilności między BuildCraft a innymi modami.
- Dodatki/fixy (np. wsparcie OreDictionary dla recept Assembly Table w MineTweaker, różne integracje) — patrz changelog.

### Pliki konfiguracyjne
- Zwykle: `config/buildcraft/*.cfg` oraz osobne pliki modułów (transport/factory/builders/energy itd.).

### Linki referencyjne
- BuildCraft 7.1.23 — strona wersji/changelog: https://mod-buildcraft.com/pages/buildinfo/BuildCraft/7.1.23.html  
- Lista bloków/itemów (różne opracowania):  
  - https://minecraftbuildcraft.fandom.com/wiki/IDs  
- BuildCraft Compat 7.1.7 (CurseForge plik + changelog): https://www.curseforge.com/minecraft/mc-mods/buildcraft-compat/files/2503632

---

## 6) Carpenter’s Blocks v3.3.8.1 + CarpentersBlocksCachedResources.zip
**Jar:** `Carpenter's Blocks v3.3.8.1 - MC 1.7.10.jar`  
**Zip:** `carpentersblocks/CarpentersBlocksCachedResources.zip` (cache zasobów/tekstur — **nie mod gameplay**)

### Główne funkcje
- „Ramki” bloków, które można **okładać dowolnym blokiem** (cover) i uzyskać nowe kształty:
  - schody, kliny, dachy, drzwi, bramy, itp.
- Pozwala robić np. **obsydianowe schody**, **szklane skosy**, itd.

### Bloki / Tile Entities
Z FTB Wiki (lista „Blocks”):
- **Carpenter’s Block** (bazowy „frame”)  
- **Carpenter’s Stairs**  
- **Carpenter’s Wedge Slope** (+ inne slope/roof warianty zależnie od wersji)  
- **Carpenter’s Door**  
- **Carpenter’s Gate**  
- **Carpenter’s Ladder**  
- **Carpenter’s Pressure Plate**  
- **Carpenter’s Button**  
- **Carpenter’s Lever**  
- **Carpenter’s Hatch**  
- **Carpenter’s Barrier**  
- **Carpenter’s Torch**  
- **Carpenter’s Daylight Sensor**  
- **Carpenter’s Flower Pot**  
- **Carpenter’s Bed**  
- **Carpenter’s Safe**  
- **Carpenter’s Garage Door**  
- **Carpenter’s Collapsible Block**  
- (oraz „Tile” — elementy systemowe/techniczne)

### Narzędzia
- **Hammer**
- **Chisel** (narzędzia do zmiany wariantów/ustawień)

### Linki referencyjne
- FTB Wiki (Carpenter’s Blocks): https://ftb.fandom.com/wiki/Carpenter%27s_Blocks  
- CurseForge (opis): https://www.curseforge.com/minecraft/mc-mods/carpenters-blocks

---

## 7) Chisel 2.9.5.11
**Jar:** `Chisel-2.9.5.11.jar`  
**Typ:** ogromna liczba **dekoracyjnych wariantów bloków** (tekstury/style) + narzędzia do konwersji.

### Główne funkcje
- **Chisel (tool)**: prawy klik → GUI → zamiana bloku na warianty (często do 24 wariantów na blok).  
- **Auto Chisel (machine)**: automatyzuje proces (zasilanie FE/RF).

### Bloki / Tile Entities
- **Auto Chisel** (TE / GUI; przyjmuje chisel + input + robi output)  
- (sam „Chisel” jest itemem, nie blokiem)

### Itemy
- **Chisel** (narzędzie; bywają wersje: iron/diamond — zależnie od configu/modpacka)

### „Bloki” w sensie wariantów dekoracyjnych
Chisel dodaje **mnóstwo rodzin** (stone, bricks, factory blocks, ornaments, itp.) oraz „chiselowane” warianty wielu vanilla bloków.  
Pełna lista wariantów jest bardzo duża — w praktyce najlepiej przeglądać je w grze (NEI/CraftGuide) lub wg kategorii wiki.

### Linki referencyjne
- Opis Chisel + Auto Chisel: https://m.ftbwiki.org/Chisel  
- Auto Chisel (szczegóły GUI): https://ftb.fandom.com/wiki/Auto_Chisel  
- Plik (CurseForge): https://www.curseforge.com/minecraft/mc-mods/chisel/files/2287442

---

## 8) CodeChickenCore + CodeChickenLib - UWAGA - konwersja nie wymagana - ignoruj
**Jary:**  
- `CodeChickenCore-1.7.10-1.0.7.47-universal.jar`  
- `CodeChickenLib-1.7.10-1.1.3.140-universal.jar`

### Co to jest?
- **Biblioteki/dependency** dla modów ChickenBones (np. EnderStorage, NEI itd. — zależnie od paczki).  
- CCC potrafi nawet **auto-pobrać** wymagane biblioteki (historycznie dot. CCL).

### Gameplay: bloki/TE/itemy?
- Zwykle **nie dodają** nic, co gracz stawia/robi (to techniczne core).  
- Czasem mogą mieć wpisy w configach / logice ASM.

### Linki referencyjne
- CCC (CurseForge): https://www.curseforge.com/minecraft/mc-mods/codechickencore/files/2262089  
- Mechanizm auto-download zależności (opis): https://stickypiston.co/account/knowledgebase/188/1.7.10-Modpack-not-starting-CodeChicken-java.lang.NoClassDefFoundError-codechickenorliborasmorASMInit.html  
- CCL (opis „unofficial”, ale opisuje funkcję biblioteki): https://www.curseforge.com/minecraft/mc-mods/codechickenlib-unofficial

---

## 9) CoFHCore 3.1.4-329 - UWAGA - konwersja nie wymagana - ignoruj
**Jar:** `CoFHCore-[1.7.10]3.1.4-329.jar`  
**Typ:** core/biblioteka dla modów Team CoFH + API (m.in. RF).

### Co wnosi
- W 1.7.10: głównie **wspólny kod i API** (np. Redstone Flux ekosystem), plus sporo opcji konfiguracyjnych dla paczek.
- W nowszych wersjach CoFHCore dodaje więcej „user-facing” rzeczy (komendy/enchanty), ale w 1.7.10 zwykle jest to głównie dependency.

### Bloki/TE/itemy
- Zwykle brak lub minimalne „techniczne” wpisy (większość widocznych rzeczy daje Thermal Foundation/Expansion/Dynamics, nie sam CoFHCore).

### Linki referencyjne
- FTB Wiki (CoFH Core): https://m.ftbwiki.org/CoFH_Core  
- CurseForge (opis): https://www.curseforge.com/minecraft/mc-mods/cofh-core/files/2388750  
- Kontekst RF: https://m.ftbwiki.org/Redstone_Flux

---

## 10) ComputerCraft 1.75
**Jar:** `ComputerCraft1.75.jar`  
**Typ:** komputery + Lua + peryferia + automaty (turtles).

### Główne funkcje
- Programowalne **Computers** i **Turtles** (roboty) w języku **Lua**.
- Peryferia: monitory, drukarki, dyski, modemy, redstone I/O.
- Automatyzacja: wydobycie, budowanie, craftowanie, kontrola redstone.

### Bloki / Tile Entities
Najważniejsze bloki (część ma GUI/inwentarz → TE):
- **Computer** / **Advanced Computer**
- **Turtle** / **Advanced Turtle** (robot; ruch + interakcje z blokami)
- **Disk Drive**
- **Monitor** / **Advanced Monitor** (łączenie w większe ekrany)
- **Printer**
- **Modem** (czasem jako blok/peripheral)
- (inne peryferia zależnie od wersji i dodatków)

### Itemy
- **Floppy Disk** (nośnik programów)
- Narzędzia/upgrade’y turtles (np. pickaxe/axe, crafting, modem, itp. — zależnie od craftów w paczce).

### API / komendy
- Wbudowane API Lua (os, fs, turtle, redstone, peripheral, itp.).  
- Opcjonalnie: **Command Block peripheral** (wyłączone domyślnie; wymaga configu).

### Linki referencyjne
- Monitor (wiki): https://computercraft.info/wiki/Monitor  
- Turtle (FTB wiki): https://ftb.fandom.com/wiki/Turtle_%28ComputerCraft%29  
- Command Block API (wiki mirror): https://mirror2.openshell.no/mirror/computercraft.info/wiki/Command_Block_%28API%29.html

---

## 11) CraftGuide (1.7.10) - UWAGA - konwersja nie wymagana - ignoruj
**Jar:** `CraftGuide-Mod-1.7.10.jar`  
**Typ:** przeglądarka receptur w grze.

### Funkcje
- GUI z listą recept, przewijanie, wyszukiwarka.
- Filtrowanie recept po wejściach/wyjściach (klik w item).
- Działa jako alternatywa dla NEI/JEI w prostych packach (ale ma mniejszą kompatybilność z maszynami-modami).

### Bloki/TE/itemy
- Zwykle: item „CraftGuide”/keybind otwierający GUI (zależnie od configu).
- Brak typowych maszyn/bloków gameplay.

### Linki referencyjne
- CurseForge: https://www.curseforge.com/minecraft/mc-mods/craftguide/files/2459319  
- GitHub (opis projektu): https://github.com/Uristqwerty/CraftGuide  
- Wątek MCForum: https://www.minecraftforum.net/forums/mapping-and-modding-java-edition/minecraft-mods/1277913-craftguide-v1-7-1-1

---

## 12) CustomNPCs 1.7.10d (29oct17) - UWAGA - konwersja nie wymagana - ignoruj
**Jar:** `CustomNPCs_1.7.10d(29oct17).jar`  
**Typ:** tworzenie NPC, questów, dialogów, skryptów + sporo bloków/itemów do map/adventure.

### Główne funkcje
- Kreator NPC: wygląd, ekwipunek, AI, frakcje, role (kupiec, strażnik itd.).
- **Dialogi** i **questy** (warunki, nagrody, lock/unlock, waypointy).
- Skrypty (JS/Lua zależnie od systemu CNPC; w 1.7.10 typowo własny scripting API).
- Narzędzia dla mapmakerów: klonowanie NPC, edycja globalnych recept.

### Bloki / Tile Entities (przykłady najczęstsze)
- **Redstone Block (CNPC)** — reaguje na zasięg gracza/questy/dialogi (konfiguracja NPC Wand).  
- **Waypoint block** — punkty do questów lokalizacyjnych.  
- **Carpentry Bench** — recepty z menu global recipes (mapmaking).  
- Dodatkowe bloki dekoracyjne/utility zależnie od wersji.

### Itemy / narzędzia
- **NPC Wand** (główne narzędzie edycji)  
- **Mob Cloner** (kopiowanie/spawn)  
- Broń/„extra items” (dagger, spear, battleaxe, mace, glaive, scythe, trident itd.)  
- Quest/itemy fabularne (dużo drobnicy do map/adventure)

### Komendy
- Komendy administracyjne CNPC (np. /noppes ...), używane w mapach/questach (wątek MCForum wspomina o /noppes clone).

### Linki referencyjne
- CurseForge (plik 29oct17): https://www.curseforge.com/minecraft/mc-mods/custom-npcs/files/2495406  
- Oficjalne strony/poradniki Noppes (Items): https://www.kodevelopment.nl/minecraft/customnpcs/items/  
- CustomNPCs wiki (community): https://customnpcs.fandom.com/wiki/Customnpcs_Wiki

---

## 13) EJML-core 0.26 (IC2 folder) - UWAGA - konwersja nie wymagana - ignoruj
**Jar:** `ic2/EJML-core-0.26.jar`  
**Typ:** biblioteka matematyczna (dependency).

### Co to robi
- Biblioteka wykorzystywana przez IndustrialCraft² (i czasem inne mod-y) do obliczeń (macierze/numeryka).  
- Nie dodaje gameplay.

### Linki referencyjne
- Dyskusja o brakującej bibliotece (IC2 forum): https://forum.industrial-craft.net/thread/12565-ejml-core-0-26-crash-need-help-adding-library/  
- Logi (MultiMC issue pokazuje „Extracted library EJML-core”): https://github.com/MultiMC/Launcher/issues/2121

---

## 14) Enchanting Plus 4.0.0.74
**Jar:** `EnchantingPlus-1.7.10-4.0.0.74.jar`  
**Typ:** „kontrolowane enchanting” — mniej RNG, więcej wyboru.

### Główne funkcje
- Zaawansowany stół do enchantowania, zwykle pozwalający:
  - wybierać enchanty/poziomy (zależnie od ustawień),
  - zdejmować/przenosić enchanty (mechanika zależna od wersji/konfigu),
  - naprawiać/zarządzać enchantami w bardziej przewidywalny sposób.

### Bloki / Tile Entities
- **Arcane Inscriber** (blok do konwersji Enchanted Book → Enchanted Scroll)  
- (sam „Enchanting Plus Table”/„Advanced Enchantment Table” — główny blok moda; nazwa bywa różna w wiki/modpackach)

### Itemy
- **Enchanted Scroll** (powstaje w Arcane Inscriber)  
- Inne komponenty związane z trybem quest/learn (zależnie od opcji).

### Linki referencyjne
- Arcane Inscriber (FTB wiki): https://m.ftbwiki.org/Arcane_Inscriber  
- Issue/wersja 4.0.0.74 (kontekst): https://github.com/xJon/The-1.7.10-Pack/issues/1165

---

## 15) EnderStorage 1.4.7.38
**Jar:** `EnderStorage-1.7.10-1.4.7.38-universal.jar`  
**Typ:** magazyn cross-dimension przez **kolorowe sieci** (chesty + tanki + pouch).

### Główne funkcje
- **EnderChest** (EnderStorage): połączone skrzynie po **3-kolorowym kodzie** (dye).
- **EnderTank**: analogicznie, ale dla płynów.
- **EnderPouch**: mobilny dostęp do tej samej sieci co chest.

### Bloki / Tile Entities
- **Ender Chest (EnderStorage)** — TE (inventory)
- **Ender Tank** — TE (fluid storage)
- (mod „nadpisuje” też pewne zachowania/ID w zależności od epoki; wiki wspomina o override w vanilla kontekście)

### Itemy
- **Ender Pouch** (synchronizacja koloru z chestem; dostęp mobilny)

### Linki referencyjne
- FTB Wiki (EnderStorage): https://feed-the-beast.fandom.com/wiki/EnderStorage  
- CurseForge (opis): https://www.curseforge.com/minecraft/mc-mods/ender-storage/files/2262092

---

## 16) Extra Utilities 1.2.12
**Jar:** `extrautilities-1.2.12.jar`  
**Typ:** „zestaw narzędzi” — masa losowych, ale bardzo użytecznych bloków/itemów.

### Główne obszary
- Automatyzacja i transport (węzły transferu, rury, filtry).
- Generatory RF (wiele typów) + magazynowanie.
- Wydobycie (Ender Quarry) i pompy (Ender-Thermic Pump).
- „Quality of life” (Angel Block, Builder’s Wand, Watering Can, itd.).
- Mob-farming (Cursed Earth, kolce/spikes, itd.) i różne utility.

### Bloki / Tile Entities — przykłady + „rdzeń”
Z FTB Wiki (występują liczne bloki; część to TE z GUI):
- **Angel Block**
- **Blackout Curtains**
- **Block Update Detector**
- **Chandelier**
- **Compressed Cobblestone** (wiele tierów)
- **Conveyor Belt**
- **Cursed Earth**
- **Ender-Thermic Pump** (TE)
- **Ender Quarry** (TE)
- **Ethereal Glass**
- **Filter Pipe**
- **Generators** (rodzina generatorów RF — wiele wariantów)
- Oraz duży zestaw: beczki, magazyny, węzły transferu, „filing cabinet”, „trash can”, „sound muffler” itd. (pełna lista niżej)

### Itemy — przykłady
- **Builder’s Wand**
- **Watering Can** (+ Reinforced)
- **Sonar Goggles**
- Wiele narzędzi i „random utility” (lasso, bags, upgrades, itd.)

### Gdzie znaleźć pełne listy?
- Strona moda na FTB Wiki ma „listę bloków i itemów” + osobną kategorię z pełnym katalogiem.

### Linki referencyjne
- FTB Wiki (opis + listy): https://m.ftbwiki.org/Extra_Utilities  
- Kategoria (pełny katalog haseł): https://ftb.fandom.com/wiki/Category%3AExtra_Utilities

---

## 17) FastCraft 1.25 - UWAGA - konwersja nie wymagana - ignoruj
**Jar:** `fastcraft-1.25.jar`  
**Typ:** optymalizacja wydajności (client i server), bez zmian gameplay.

### Co robi
- Usprawnienia wydajności (tick, rendering, chunk loading, itp.) bez dodawania bloków/itemów.
- Może wchodzić w interakcje z innymi modami optymalizacyjnymi (np. OptiFine) — czasem plus, czasem minus.

### Bloki/TE/itemy
- Brak.

### Linki referencyjne
- CurseForge (FastCraft 1.25): https://www.curseforge.com/minecraft/mc-mods/fastcraft/files/2522249  
- FTB Wiki (opis): https://ftb.fandom.com/wiki/Fastcraft

---

# Źródła / strony „bazowe”, z których korzystałem
- BiblioCraft (FTB Wiki + oficjalna wiki): https://m.ftbwiki.org/BiblioCraft | https://www.bibliocraftmod.com/wiki/  
- Big Reactors (FTB Wiki + strona): https://ftb.fandom.com/wiki/Big_Reactors | https://www.big-reactors.com/  
- Blood Magic (FTB Wiki + rytuały): https://m.ftbwiki.org/Blood_Magic | https://ftb.fandom.com/wiki/Rituals_%28Blood_Magic%29  
- Carpenter’s Blocks: https://ftb.fandom.com/wiki/Carpenter%27s_Blocks  
- Chisel: https://m.ftbwiki.org/Chisel | Auto Chisel: https://ftb.fandom.com/wiki/Auto_Chisel  
- BuildCraft: https://mod-buildcraft.com/pages/buildinfo/BuildCraft/7.1.23.html | IDs: https://minecraftbuildcraft.fandom.com/wiki/IDs  
- CraftGuide: https://www.curseforge.com/minecraft/mc-mods/craftguide/files/2459319 | https://github.com/Uristqwerty/CraftGuide  
- CustomNPCs: https://www.curseforge.com/minecraft/mc-mods/custom-npcs/files/2495406 | https://www.kodevelopment.nl/minecraft/customnpcs/items/  
- EnderStorage: https://feed-the-beast.fandom.com/wiki/EnderStorage  
- Extra Utilities: https://m.ftbwiki.org/Extra_Utilities  
- FastCraft: https://ftb.fandom.com/wiki/Fastcraft

