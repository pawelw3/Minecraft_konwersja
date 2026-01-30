# Minecraft 1.7.10 — spis funkcjonalności modów (część 4)

Lista modów z Twojej paczki:

- MrCrayfish’s Furniture Mod v3.4.8 (1.7.10)
- MrTJPCore 1.1.0.33 (1.7.10)
- NoMoreRecipeConflict 0.31 (1.7.10)
- NotEnoughItems (NEI) 1.0.5.120 (1.7.10)
- Open Modular Turrets 2.2.11-245 (1.7.10)
- Opis 1.2.5 (1.7.10)
- Pam’s HarvestCraft 1.7.10Lb
- Placeable Items Mod (1.7.10)
- PowerConverters 3.2.1 (1.7.10)
- ProjectRed 4.7.0pre12.95 (Base/Compat/Fabrication/Integration/Lighting/Mechanical/World)
- Railcraft 9.12.2.0 (1.7.10)
- Rei’s Minimap (1.7.10)

> **Uwaga o “pełnych listach”**: w 1.7.10 część modów ma setki wpisów (np. HarvestCraft / Railcraft / ProjectRed).  
> Tam, gdzie pełna lista jest bardzo długa, podaję **rdzeń** (najważniejsze bloki/TE i systemy) + sugeruję, jak wyciągnąć pełną listę z gry (NEI / dump / wiki).

---

## 1) MrCrayfish’s Furniture Mod v3.4.8 (MC 1.7.10)
**Jar:** `MrCrayfishFurnitureModv3.4.8(1.7.10).jar`

### Co robi
- Duży zestaw **mebli i dekoracji** (w wersjach „Legacy” mod ma **>450 bloków dekoracyjnych i użytkowych**).
- Wiele bloków jest **funkcjonalnych** (GUI, inventory, interakcje), a nie tylko dekoracyjnych.
- Posiada **system poczty** (mail), pozwalający wysyłać itemy do graczy na serwerze / w świecie.  
Źródła/strony:  
- CurseForge (Legacy): https://www.curseforge.com/minecraft/mc-mods/mrcrayfish-furniture-mod  
- Strona autora: https://mrcrayfish.com/mods/cfm  
- Wiki (lista recept / kategorie): https://mrcrayfishs-furniture-mod.fandom.com/wiki/Crafting_Recipes_List

### Najważniejsze bloki (kategorie + przykłady)
> Nazwy z grubsza odpowiadają temu, co widać w NEI i w wiki/receptach. W 1.7.10 mod ma dużo wariantów (np. drewno/kolory).

**Kuchnia / AGD**
- Fridge / Freezer (często jako storage/GUI)
- Oven / Microwave / Dishwasher (funkcje zależne od wersji)
- Kitchen Counter / Drawer / Cabinet
- Kitchen Sink

**Sypialnia**
- Bedside Cabinet
- Szafy/szafki, półki (różne typy)

**Łazienka**
- Toilet
- Bath / Shower (zależnie od wersji)

**Salon / elektronika**
- TV / Radio / komputeropodobne dekoracje (zależnie od builda)
- Lampy / oświetlenie dekoracyjne

**Outdoor / ogród**
- Grill / ogrodowe elementy (zależnie od wersji)
- Płotki, skrzynki, ozdoby

**Poczta**
- Mail Box / Post Box (elementy systemu poczty)

**Siedzenie i stoły**
- Chair / Table / Sofa / Blinds (roleplay + dekor)

### Tile Entities (typowe)
W tej klasie modów TE pojawiają się głównie w blokach:
- z **GUI/inventory** (np. lodówka, szafki, skrzynki, urządzenia),
- z **logiką** (mailbox/postbox, wysyłka/odbiór),
- z **animacją/interakcją** (część urządzeń reaguje PPM).

### Jak zrobić „pełną listę bloków” na 1.7.10
- Najprościej: **NEI → wyszukiwanie** po `cfm` lub po nazwach typu “cabinet”, “sink”, “mail”.  
- Alternatywnie: włączyć tryb kreatywny i przejrzeć zakładkę moda.

---

## 2) MrTJPCore 1.1.0.33
**Jar:** `MrTJPCore-1.7.10-1.1.0.33-universal.jar`

### Co robi
- To **biblioteka / dependency** MrTJP (zestaw wspólnego kodu i API).
- Najczęściej wymagana do uruchomienia **ProjectRed**.  
Źródła:
- FTB Wiki: https://ftb.fandom.com/wiki/MrTJPCore  
- CurseForge: https://www.curseforge.com/minecraft/mc-mods/mrtjpcore

### Bloki / TE / itemy
- W praktyce **brak gameplay** (nie dodaje sensownych bloków do rozgrywki).

---

## 3) NoMoreRecipeConflict 0.31 (1.7.10)
**Jar:** `NoMoreRecipeConflict-0.31.7.10.jar`

### Co robi
- Rozwiązuje konflikty recept: gdy **kilka przedmiotów** ma ten sam układ craftingu, możesz **przełączać wynik** (klawisz / przycisk).
- W nowszych forkach/fixach bywa to nazywane „RecipeConflict Fixer” i ma config `recipehandler.cfg`.  
Źródła:
- MinecraftForum (historyczny wątek): https://www.minecraftforum.net/forums/mapping-and-modding-java-edition/minecraft-mods/wip-mods/1440404-1-1-smp-ssp-no-more-recipe-conflicts-0-3  
- Fork/fixer: https://www.curseforge.com/minecraft/mc-mods/recipeconflict-fixer

### Jak się używa (typowo)
- W craftingu, gdy „coś się dubluje”, wciskasz klawisz (często domyślnie **Num+** albo inny, zależy od konfiguracji) i wynik się zmienia.
- Często działa także na **niestandardowych stołach** (np. Tinkers/Natura), ale zależy od wersji.

### Bloki / TE / itemy
- Zwykle **brak** (to mod logiki craftingu + keybind + GUI).

---

## 4) NotEnoughItems (NEI) 1.0.5.120
**Jar:** `NotEnoughItems-1.7.10-1.0.5.120-universal.jar`  
**Wymaga:** CodeChickenCore (masz w paczce)

### Co robi (rdzeń)
NEI to klasyczne narzędzie do:
- **podglądu recept** (Recipe View),
- **podglądu zastosowań** przedmiotu (Usage View),
- **wyszukiwania itemów**,
- **Item Subsets** (grupy/filtry po modach i typach),
- trybów **Cheat / Creative** (klikanie itemów w panelu, utility przyciski),
- dodatkowych narzędzi typu **bookmarki**, „trash”, „magnet”, „rain” (zależnie od konfiguracji i wersji).  
Źródła:
- CurseForge: https://www.curseforge.com/minecraft/mc-mods/notenoughitems  
- FTB Wiki (opis funkcji): https://m.ftbwiki.org/Not_Enough_Items  
- FTB Wiki (pełniejszy opis): https://feed-the-beast.fandom.com/wiki/Not_Enough_Items

### Bloki / TE / itemy
- NEI z zasady **nie dodaje bloków/TE** do świata; to mod **GUI/overlay**.
- Dodaje elementy interfejsu, konfigurację, keybindy.

### Tip do „pełnych list” z NEI
- NEI jest najlepszym narzędziem, żeby szybko policzyć i przejrzeć **wszystkie itemy i bloki** z modpacka (filtr po modzie i po nazwie).

---

## 5) Open Modular Turrets 2.2.11-245
**Jar:** `OpenModularTurrets-1.7.10-2.2.11-245.jar`

### Co robi
- Dodaje system **wieżyczek obronnych** z modułami, ulepszeniami i dodatkami.
- Turrety są „tierowane” (niski/średni/wysoki tier) i zwykle wymagają:
  - **zasilania (RF)**,
  - **amunicji** lub energii (zależnie od typu wieżyczki),
  - konfiguracji zasięgu/targetów (whitelist/blacklist).  
Źródła:
- CurseForge: https://www.curseforge.com/minecraft/mc-mods/openmodularturrets  
- Opisy i poradniki są głównie w video / społeczności (w 1.7.10 często tak bywa).

### Kluczowe bloki / Tile Entities (rdzeń)
> Dokładne nazwy elementów mogą się różnić, ale architektura moda jest stała.

- **Turret Base** (baza wieżyczki) – fundament pod montaż turreta; zwykle w tierach (low/medium/high).
- **Turret (głowica)** – sama wieżyczka jako blok z logiką (TE): celowanie, zużycie energii, strzał.
- **Dodatki do bazy/wieżyczki** (często jako „addons”): elementy zwiększające zasięg, efekty, zachowanie.

### Typowe typy turretów (przykładowo)
W 1.7.10 w praktyce spotyka się zestaw obejmujący:
- proste turrety „pociskowe” (kamienie/kulki),
- turrety na amunicję (np. „bullet/shotgun”),
- turrety „specjalne” (laser/explosive/teleport itp. – zależnie od wersji i configu).

> Jeśli chcesz „pełną listę turretów i addonów” dla *Twojej* wersji: najpewniej wyciągniesz ją z **NEI** (wyszukaj `turret`, `addon`, `upgrade`, `base`).

### Itemy (rdzeń)
- **Amunicja** (różne typy nabojów / pocisków)
- **Upgrades** (np. dmg/range/rate-of-fire/accuracy)
- **Addons** (np. efekty, targetowanie, utility)
- Elementy konfiguracyjne (np. owner/credentials, jeśli mod to wspiera)

---

## 6) Opis 1.2.5
**Jar:** `Opis-1.2.5_1.7.10.jar`  
**Wymaga:** MobiusCore (masz w paczce wcześniej)

### Co robi
- Narzędzie dla adminów: **profilowanie świata i wykrywanie laga**:
  - listy **Tile Entities** i **Entities** (kto „zjada TPS”),
  - szybka nawigacja / podgląd,
  - w niektórych opisach również minimapopodobny podgląd.  
Źródła:
- CurseForge (opis wersji): https://www.curseforge.com/minecraft/mc-mods/opis/files/2232520  
- FTB Wiki: https://ftb.fandom.com/wiki/OPIS

### Bloki / TE / itemy
- Zwykle **brak** — to mod narzędziowy (GUI, listy obiektów, profiling).

---

## 7) Pam’s HarvestCraft 1.7.10Lb
**Jar:** `Pam's HarvestCraft 1.7.10Lb.jar`

### Co robi (skala)
- Bardzo duży mod farming/cooking:
  - **60+ upraw**, **36 drzew owocowych**, **17 ryb** (wg opisu wydania 1.7.10Lb),
  - proste pszczelarstwo,
  - **1000+ jedzeń/przetworów** i ingredientów.  
Źródło:
- CurseForge (1.7.10Lb): https://www.curseforge.com/minecraft/mc-mods/pams-harvestcraft/files/2270206

### Główne rodziny bloków
**Świat / generacja**
- **Gardens** (różne typy ogrodów, źródła losowych składników),
- **Crops** (bloki roślin),
- **Fruit Trees** (saplings, leaves, owoce),
- (zależnie od wersji) elementy pszczelarstwa.

**Maszyny / stacje**
HarvestCraft ma serię bloków „maszyn” do pozyskiwania składników.
Na wiki są wypisane m.in. (w praktyce wiele z nich to TE z GUI):  
- Apiary  
- Grinder  
- Ground Trap (Animal Trap)  
- Market  
- Presser  
- Shipping Bin  
- Water Trap (Fish Trap)  
- Water Filter  
- Well  
Źródło listy: https://harvestcraftmod.fandom.com/wiki/Machines

> Na tej samej stronie wiki jest też sekcja „Removed” (historyczne: Churn, Oven, Quern itd.).  
> W praktyce: w 1.7.10 spotyka się różne kompilacje — najlepiej potwierdzić w **NEI**, bo to *Twoja paczka* jest źródłem prawdy.

### Tile Entities (typowe)
- Większość maszyn (Market/Presser/Grinder/Trapy/Filter/Shipping Bin) ma:
  - GUI,
  - inventory,
  - czas przetwarzania / logikę dropów → więc typowo jest to **TE**.

### Jak zrobić „pełną listę” (realnie)
- HarvestCraft ma setki foodów — NEI i wyszukiwanie po prefiksach (np. `pamhc2food` nie dotyczy 1.7.10; tu po prostu po nazwach) jest najszybsze.
- W NEI: filtruj po `Pam` / po nazwach składników.

---

## 8) Placeable Items Mod (1.7.10)
**Jar:** `Placeable-Items-Mod-1.7.10.jar`

### Co robi
- Pozwala **stawiać zwykłe itemy jako modele 3D** w świecie (dekoracje).
- Typowo: **SHIFT + PPM** stawia „przedmiot na ziemi/półce”.
- Część postawionych obiektów ma dodatkowe interakcje PPM.  
Źródła:
- CurseForge: https://www.curseforge.com/minecraft/mc-mods/placeable-items  
- MinecraftForum (stary wątek): https://www.minecraftforum.net/forums/mapping-and-modding-java-edition/minecraft-mods/wip-mods/2326849-wip-placeable-items

### Bloki / Tile Entities
- Zwykle dodaje:
  - „**Placed Item**” jako blok/obiekt w świecie,
  - TE do trzymania informacji: *jaki item*, rotacja/pozycja, ewentualnie wariant renderu.

---

## 9) PowerConverters 3.2.1
**Jar:** `PowerConverters-1.7.10_3.2.1.jar`

### Co robi
- Konwersja energii **pomiędzy modami** (różne systemy energii).
- Główny rdzeń to **Energy Bridge** + „przystawki”:
  - **Producer** (produkuje energię danego typu na wyjściu),
  - **Consumer** (pobiera energię danego typu na wejściu).  
Źródło:
- CurseForge: https://www.curseforge.com/minecraft/mc-mods/power-converters3

### Kluczowe bloki / Tile Entities
- **Energy Bridge** (TE) – centralny „hub” konwersji.
- **Energy Consumer** (TE) – pobiera energię z danego systemu.
- **Energy Producer** (TE) – wypuszcza energię do danego systemu.
- Limity: zwykle jest ograniczenie liczby przystawek na jeden bridge (np. do 6).

> Jakie typy energii są wspierane w Twoim modpacku zależy od builda oraz obecnych modów (RF/EU/MJ/itp.). Najpewniej sprawdzisz w NEI po `bridge`, `consumer`, `producer`.

---

## 10) ProjectRed 4.7.0pre12.95 (pakiety)
**Jary:**
- `ProjectRed-...-Base.jar`
- `ProjectRed-...-Compat.jar`
- `ProjectRed-...-Fabrication.jar`
- `ProjectRed-...-Integration.jar`
- `ProjectRed-...-Lighting.jar`
- `ProjectRed-...-Mechanical.jar`
- `ProjectRed-...-World.jar`

### Co robi (ogólnie)
- „Kontynuacja” idei RedPower2: **okablowanie, logika, automatyzacja, transport itemów**, oświetlenie, mechanizmy przesuwne, plus własne elementy.  
Źródło opisu pakietów i modułów:  
- FTB Wiki: https://ftb.fandom.com/wiki/Project_Red

### Zależności (ważne)
- Wymaga **MrTJPCore** (masz).
- Część funkcji silnie opiera się o **ForgeMultipart** (wiele elementów to *parts* w jednej kratce).

### 10A) ProjectRed Base (Core)
**Rola:** biblioteka + podstawowe itemy do craftingu reszty.

**Typowe itemy/surowce**
- Electrotine / Red Alloy / komponenty przewodów
- Szkielety craftingu (płyty, obwody, części narzędzi)

**Bloki/TE**
- Zwykle niewiele „maszyn” – to głównie zasób do craftów.

### 10B) ProjectRed Integration (zwykle: Transmission + Integration)
**Najważniejsze systemy**
- **Przewody** o dużym zasięgu sygnału, różne typy kabli/wires (często jako multipart).
- **Gates / logika redstone** (AND/OR/NAND/NOR, timery, sekwencery, przerzutniki, czujniki itd. – zależnie od zestawu w wersji).

**Bloki / TE**
- Wiele elementów to **multipart parts**, ale nadal mają logikę podobną do TE:
  - bramki (gates) – logika i interakcje,
  - okablowanie (wires) – routing sygnału.

### 10C) ProjectRed Fabrication
**Cel:** projektowanie i budowa własnych „chipów”/układów (zamiast tylko gotowych gate’ów).

**Typowe bloki (TE)**
- Stacje robocze typu **IC Workbench / IC Printer** (nazwy zależne od wersji)
- Elementy do planowania i „wypalania” układów

### 10D) ProjectRed Lighting (Illumination)
**Co dodaje**
- Zestaw lamp i świateł w 16 kolorach, często w wersjach:
  - normalne i „inverted”,
  - różne formy (lamp, fixture, lantern, button light itp.).

**Bloki**
- Głównie bloki oświetleniowe sterowane redstonem.

### 10E) ProjectRed Mechanical (Transportation + Exploration)
**Transportation (logistyka itemów)**
- System **tubów/pipes** do przesyłu itemów.
- Moduły routingu / filtrowania (chip’y, sortery, routery).

**Exploration (świat)**
- Worldgen: **rudy, drzewa, marmur/jaskinie** (zależnie od konfiguracji).
- Materiały: gem’y (ruby/sapphire/peridot) i surowce pod narzędzia.

### 10F) ProjectRed World (Expansion)
**Co dodaje**
- Moduł z mechanikami „większych” konstrukcji i elementami energii/systemów (w zależności od wersji):
  - elementy ram/teleportów,
  - czasem własna energia (Electrotine Power) dla wybranych maszyn.

### 10G) ProjectRed Compat (Compatibility)
**Integracje**
- Kompatybilność z innymi modami (np. ComputerCraft, Thermal Expansion, Tinkers’, Treecapitator, Wireless Redstone – wg wiki).  
Źródło: https://ftb.fandom.com/wiki/Project_Red

### Jak zrobić „pełną listę bloków i części” ProjectRed
- W NEI wyszukaj: `projectred` / `electrotine` / `wire` / `gate` / `tube` / `lamp`.
- Pamiętaj: wiele rzeczy jest jako **multipart part** (niekoniecznie „pełny blok”).

---

## 11) Railcraft 9.12.2.0 (MC 1.7.10)
**Jar:** `Railcraft_1.7.10-9.12.2.0.jar`

### Co robi (filary)
- Ogromne rozszerzenie systemu kolei:
  - dziesiątki **torów (tracks)** o specjalnych funkcjach,
  - nowe **minecart’y** (ładunek/płyny/utility),
  - **sygnalizacja i logika kolejowa**,
  - mocne **multibloki** i maszyny „przemysłowe” pod kolej/logistykę.  
Źródła:
- CurseForge: https://www.curseforge.com/minecraft/mc-mods/railcraft/files/2299713  
- FTB Wiki: https://ftb.fandom.com/wiki/Railcraft  
- FTB Wiki (skrót): https://m.ftbwiki.org/Railcraft

### Kluczowe bloki / Tile Entities (rdzeń)
> Railcraft ma modułowy config (możesz wyłączać części). Poniżej to, co najczęściej jest „sercem” Railcrafta.

**Multibloki (bardzo ważne)**
- **Coke Oven** (multiblok) → Coal Coke + Creosote Oil  
  (używany też do impregnacji drewna i wielu recept).  
  Wiki: https://ftb.fandom.com/wiki/Coke_Oven_(Railcraft)
- **Blast Furnace** (multiblok) → stal i przetwórstwo (często wymagane w progresji modpacków)
- **Boiler / Steam** (różne elementy parowe) → produkcja pary i zasilanie urządzeń
- **Tanks** (np. iron/steel/water tank) → duże magazyny płynów

**Maszyny / urządzenia (TE)**
- **Rolling Machine** (często kluczowa) → craft torów/elementów kolejowych
- **Rock Crusher** → przeróbka kamienia i surowców (zależnie od configu)
- **Loaders/Unloaders** (item/fluid) → załadunek wagonów i stacji
- **Detectors / Track logic** → integracja z redstone

**Tory (Tracks) — przykładowe typy**
- tor przyspieszający / hamujący,
- tor detekcyjny,
- tor przełączający,
- tor „lockdown”/zatrzymujący,
- tor „boarding”/„launcher” (zależnie od modułów).

**Sygnalizacja**
- bloki sygnałów, kontrolery, semafory/światła, logika ruchu (w zależności od configu).

### Itemy (rdzeń)
- Creosote, treated wood, coal coke,
- zestaw części kolejowych: szyny, wzmocnienia, złącza, komponenty wagonów,
- narzędzia serwisowe (w zależności od wersji).

### Jak zrobić „pełną listę”
- Najpewniej: **NEI** (Railcraft ma setki wpisów).
- Dodatkowo: w configu Railcraft możesz sprawdzić, które moduły są włączone – to mocno zmienia listę.

---

## 12) Rei’s Minimap (1.7.10)
**Jar:** `Reis-Minimap-Mod-1.7.10 (1).jar`

### Co robi
- Dodaje minimapę na ekranie (klient).
- Typowe funkcje:
  - **waypointy**,
  - podgląd chunków (w tym często **slime chunks**),
  - szybka nawigacja / marker na mapie.  
Źródła:
- Tekkit Classic Wiki (opis funkcji): https://tekkitclassic.fandom.com/wiki/Rei%27s_Minimap

### Bloki / TE / itemy
- Brak (client-side GUI/HUD).

---

# Szybkie zależności (żeby łatwiej debugować)
- **ProjectRed** → wymaga **MrTJPCore** (+ zwykle ForgeMultipart).
- **NEI** → wymaga **CodeChickenCore** (masz).
- **Opis** → wymaga **MobiusCore** (masz).
- **Open Modular Turrets** w nowszych MC wymaga OMLib, ale dla 1.7.10 w modpackach bywa, że OMLib nie jest wymagany (zależy od builda) — gdyby gra krzyczała o brak, to jest to pierwszy trop.

