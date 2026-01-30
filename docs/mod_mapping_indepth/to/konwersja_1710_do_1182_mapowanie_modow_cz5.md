# Konwersja mapy Minecraft 1.7.10 → 1.18.2 (Forge) — mapowanie modów (lista `cz5`)

Ten plik opisuje **funkcjonalności** modów z Twojej listy `cz5` (1.7.10) oraz to, **na jakie mody 1.18.2** warto przejść, żeby dało się możliwie sensownie:
- zachować budowle/bloki/TE tam, gdzie to realne,
- zaplanować remapowanie bloków i danych (NBT) tam, gdzie to *nie* jest realne “z automatu”.

> **Uwaga praktyczna (ważne dla Thaumcraft/Witchery/Traincraft):**  
> Jeśli mod **nie ma wersji na 1.18.2**, to jedyną drogą do “bezstratnej” konwersji jest **własny konwerter świata** (mapa bloków + reguły NBT + fallbacki), albo etap “ratunkowy” (wypakowanie zawartości/inwentarzy do skrzyń) i dopiero później podmiana bloków.

---

## Legenda strategii migracji

- **A — ten sam mod / ta sama rodzina** (najlepiej)
- **B — zamiennik funkcjonalny** (wymaga remapów + zwykle utrata/rekonstrukcja NBT)
- **C — klientowe / QoL / narzędzia / serwerowe** (bez treści świata lub minimalnie)

---

# Szybka lista docelowych modów 1.18.2 (dla `cz5`)

**Magia / artefakty:**
- Reliquary → **Reliquary Reincarnations** (1.18.2 Forge) citeturn0search5turn0search8

**Dekoracje / statuy:**
- Statues (Asie) → **Statues (ShyNieke)** (jest na 1.18.2 Forge) citeturn8search1turn8search4  
  (alternatywnie: Statues Classic jest tylko Fabric) citeturn7search1

**“Thaumcraft-owe” systemy (brak portu TC na 1.18.2):**
- Thaumcraft + addon-y → pakiet zamienników:
  - **Ars Nouveau** (system czarów/rytuałów/artefaktów) citeturn3search3turn3search7  
  - **Occultism** (rytuały, summony, familiars, *mega storage*) citeturn3search4turn3search12  
  - **Botania** (mana-tech, automatyzacja, “magiczna technologia”) citeturn3search2  
  (Thaumcraft 6 jest porzucony, więc “oficjalnej” ścieżki do 1.18.2 nie ma.) citeturn0search18turn0search14

**Thermal (Tech):**
- ThermalFoundation/Expansion/Dynamics → **Thermal Foundation / Thermal Expansion / Thermal Dynamics (Thermal Series)** na 1.18.2 citeturn1search2turn1search6turn1search8

**Pociągi/pojazdy:**
- Traincraft → brak wersji >1.7.10; zamienniki:
  - **Create** (+ kolej), plus **Create: Steam ’n’ Rails** (rozszerzenia kolei) citeturn6search2turn6search5turn6search15  
  - Jeśli Traincraft używałeś też “airshipowo”: **Valkyrien Skies 2 + Eureka** (statki/sterowce z bloków) citeturn6search0turn6search1turn6search4turn6search11

**Witchery:**
- Witchery → **Hexerei** (Forge 1.18.2) citeturn2search0  
  oraz/lub **Enchanted: Witchcraft** (wprost inspirowane Witchery) citeturn3search10turn3search14  
  (Bewitchment jest głównie Fabric i też ma 1.18.2, ale jeśli trzymasz się Forge – potraktuj jako opcję poboczną) citeturn2search1turn2search19

**Edycja mapy:**
- WorldEdit → **WorldEdit (Forge/Fabric) 1.18.2** citeturn2search2turn2search11  
  (dla wizualizacji selekcji: WorldEditCUI zależnie od loadera) citeturn5search5turn5search3

**Radar/minimap:**
- RadarBro → **Xaero’s Minimap** (ma Entity Radar) albo **VoxelMap** citeturn5search6turn5search0turn5search9

---

# Mapowanie per-mod (1.7.10 → 1.18.2)

## 1) Reliquary (1.7.10) → Reliquary Reincarnations (1.18.2)

### Funkcjonalności 1.7.10
- “Magiczne graty”: artefakty, relikwie, narzędzia, różne gadżety (głównie **itemy**, mało “światowych” bloków).

### Docelowy mod 1.18.2
- **Reliquary Reincarnations** (Forge 1.18.2) citeturn0search5turn0search3

### Strategia migracji
- **A** (ta sama rodzina)  
- **Ryzyko utraty danych: ŚREDNIE**  
  Itemy mają szansę na remap (nazwa → nazwa), ale format NBT mógł się zmienić.

### Co mapować
- Itemy/artefakty: remap po registry name (część może się nazywać inaczej).
- Jeśli na mapie masz “składowane” relikwie w skrzyniach – tu najłatwiej o zachowanie (bo to tylko NBT itemów).

---

## 2) RadarBro (settings.txt) → minimapa z radarem encji

### Funkcjonalności 1.7.10
- Radar encji (moby/gracze) i konfiguracja po stronie klienta. citeturn5search12turn5search8

### Docelowe mody 1.18.2
- **Xaero’s Minimap** (Entity Radar w opcjach) citeturn5search6turn5search0  
- Alternatywnie: **VoxelMap** citeturn5search9turn5search13

### Strategia migracji
- **C** (klientowe)  
- **Ryzyko utraty danych: brak** (nie ma bloków/TE).

### Co mapować
- Tylko ustawienia (ręcznie) – format configów jest inny.

---

## 3) Statues (1.7.10) → Statues (1.18.2 Forge) / alternatywy

### Funkcjonalności 1.7.10
- Statuy (często “graczowe” / “pokazowe”), elementy dekoracyjne, czasem “showcase”.  

### Docelowe mody 1.18.2
- **Statues (ShyNieke)** – działa na 1.18.2 Forge (wydanie na Modrinth) citeturn8search1turn8search4  
- Alternatywa Fabric: **Statues Classic** (Fabric 1.18.2) citeturn7search1  
- Dodatkowo jako fallback do ekspozycji: **Armor Statues** (ulepsza armor standy) citeturn7search8turn8search12

### Strategia migracji
- **B** (bo to nie jest “ten sam świat danych” co 1.7.10)  
- **Ryzyko utraty danych: ŚREDNIE/WYSOKIE**, zależnie czy statuy mają NBT (skiny/pozy/inwentarze).

### Co mapować
- Bloki “statue/showcase”: zamiana na odpowiedniki (Statues 1.18.2).  
- Jeśli nie da się przenieść NBT (skin/pose): fallback na armor stand + ręczne odtworzenie.

---

## 4) Thaumcraft 4 (1.7.10) + addon-y → “stos zamienników” (brak TC na 1.18.2)

### Co wnosiło 1.7.10 (w uproszczeniu)
- **Badania (research), skanowanie**, wędzidła/koncentratory, “magiczna technologia”.
- **Aspekty / essentia** (przetwarzanie, przechowywanie, transport, aplikowanie).
- **Infuzja**, alchemia, konstrukty/golemy, urządzenia/TE.
- Addon-y (NEI plugin, Thaumic Energistics, Tinkerer, Horizons, Exploration) rozbudowywały te systemy.

### Dlaczego to problem
- Thaumcraft 6 (następca TC4) jest porzucony, a oficjalnego portu na 1.18.2 nie ma. citeturn0search18turn0search14  
- W efekcie: nie ma sensownego “A → A” dla bloków/TE TC i addon-ów.

### Docelowe mody 1.18.2 (proponowany zestaw)
**Rdzeń “thaumcraftowego” gameplay’u na 1.18.2 (Forge):**
- **Ars Nouveau** (czary, rytuały, progresja) citeturn3search3turn3search7  
- **Occultism** (rytuały, summony, familiars, *magiczny storage/automatyzacja*) citeturn3search4turn3search12  
- **Botania** (mana-tech, automatyzacja, “magiczna inżynieria”) citeturn3search2  

> Jeśli zależy Ci na “wiedźmowej” atmosferze z TC/Witchery razem: do tego zestawu bardzo dobrze dokleja się Hexerei (poniżej). citeturn2search0

### Strategia migracji
- **B** (zamiennik funkcjonalny)  
- **Ryzyko utraty danych: WYSOKIE** (brak kompatybilnych bloków/TE).

### Jak mapować funkcjonalności (praktyczna ściąga)
- **Research / księgi / progresja**  
  - TC: research notes, tab, skanowanie →  
  - 1.18.2: in-game guidebooki (Patchouli w modach), zadania/advancementy (zależy od paczki)  
- **Aspekty / essentia (przechowywanie/transport)**  
  - TC + Thaumic Energistics: magazynowanie essentii i aplikacja →  
  - 1.18.2: *zwykle rezygnujesz z “essentia jako płynu”* i przenosisz się na:
    - AE2 jako główny storage itemów/fluidów (z Twojej paczki cz1/cz2)  
    - **Occultism** daje własny duży storage i summony do logistyki citeturn3search4turn3search12  
    - Automatyzacje rytuałów możesz spinać przez AE2 (ludzie automatyzują Occultism przez AE2) citeturn4search2
- **Infusion / ulepszanie przedmiotów**  
  - TC: Infusion Altar →  
  - 1.18.2: Ars Nouveau (urządzenia do craftu/enchantingu), Botania (runy/infuzje w swoim stylu)
- **Golemy / automatyzacja “magiczna”**  
  - TC: golemy →  
  - 1.18.2: Occultism (familiars/spirits do zadań) citeturn3search4, Ars Nouveau (summony)  
- **Węzły/aura/vis**  
  - 1.18.2: zastępujesz “zasobem magicznym” (Source z Ars, Mana z Botanii).

### Co zrobić z blokami TC w świecie (żeby “nie zniknęły”)
- Najbezpieczniejszy workflow:
  1) Konwerter/komenda “ratunkowa”: **zrzuca inwentarze** z arcane/alchemy TE do skrzyń
  2) Remap bloków TC na “placeholdery” (np. decorative blocks) z zachowaniem bryły budowli
  3) Dopiero potem ręcznie/automatycznie odtwarzasz “funkcję” w nowych modach

---

## 5) thaumcraftneiplugin (1.7.10)

### Funkcjonalności 1.7.10
- Integracja Thaumcraft z NEI (podgląd przepisów/research).

### Docelowe 1.18.2
- Jeśli używasz Ars/Occultism/Botania: przepisy i integracje robią się przez JEI + ich własne księgi.  
- **Strategia: C** (narzędzie)  
- **Ryzyko: brak**.

---

## 6) thaumicenergistics / ThaumicExploration / thaumichorizons / ThaumicTinkerer (1.7.10)

### Funkcjonalności 1.7.10
- Rozszerzenia Thaumcraft 4 (essentia management, nowe przedmioty/bloki, nowe mechaniki).

### Docelowe 1.18.2
- Ponieważ brak Thaumcraft na 1.18.2:  
  - Thaumic Energistics → AE2 + (ew.) Occultism/inna magia do “magicznych procesów” citeturn4search12turn3search4  
  - Exploration/Horizons/Tinkerer → funkcje “rozbijasz” między Ars/Occultism/Botania i ewentualnie inne mody (zależnie co było faktycznie użyte na mapie).

### Strategia migracji
- **B**  
- **Ryzyko utraty danych: WYSOKIE** (brak zgodności bloków/TE).

---

## 7) ThermalFoundation / ThermalExpansion / ThermalDynamics (1.7.10) → Thermal Series (1.18.2)

### Funkcjonalności 1.7.10
- **Thermal Foundation**: surowce, narzędzia, materiały.  
- **Thermal Expansion**: maszyny, dynama, przetwórstwo.  
- **Thermal Dynamics**: dukty (item/fluid/energy) + logistyka. citeturn1search4turn1search20

### Docelowe mody 1.18.2
- **Thermal Foundation 1.18.2** citeturn1search2turn1search9  
- **Thermal Expansion 1.18.2** (Thermal Series) citeturn1search5turn1search3  
- **Thermal Dynamics 1.18.2** citeturn1search6turn1search8  

### Strategia migracji
- **A** (ta sama rodzina)  
- **Ryzyko utraty danych: ŚREDNIE/WYSOKIE**  
  Największy problem to:
  - w 1.7.10 dużo “maszyn” było jednym blokiem + metadata,
  - w 1.18.2 wszystko jest na blockstate + inne registry name,
  - NBT (energia, strony, augmenty, zawartość) może wymagać translacji.

### Co mapować (praktycznie)
- **Maszyny/dynamo**: mapowanie “typ maszyny” → “typ maszyny” (pusta/podstawowa), zawartość najlepiej zrzucić do skrzyń i ponownie załadować.
- **Ducty**: item/fluid/energy ducts → nowe ducts; z filtrami/serwos licz się z rekonstrukcją.
- **Surowce**: rudy/ingoty → remap itemów; tu zwykle jest najłatwiej.

---

## 8) Traincraft (1.7.10)

### Funkcjonalności 1.7.10
- Pociągi, wagony, infrastruktura kolejowa i pojazdy.  
- Traincraft oficjalnie wspierał Forge **do 1.7.10**. citeturn1search1

### Docelowe mody 1.18.2
- **Create** (kolej/pociągi) + **Create: Steam ’n’ Rails** (więcej torów/elementów kolejowych) citeturn6search2turn6search5turn6search15  
- Jeżeli zależy Ci na “pojazdach z bloków” (sterowce/łodzie/pływające konstrukcje):  
  - **Valkyrien Skies 2** + addon **Eureka** citeturn6search0turn6search1turn6search4turn6search11

### Strategia migracji
- **B**  
- **Ryzyko utraty danych: WYSOKIE** (encje pojazdów i ich NBT nie będą kompatybilne).

### Co mapować
- Tory/ozdoby kolejowe: mapowanie na tory Create (bryła budowli zostaje, funkcja jest inna).  
- Pociągi/wagony: praktycznie “do odtworzenia” (nie ma mechanicznego 1:1 importu).

---

## 9) uuidoffline (1.7.10)

### Funkcjonalności 1.7.10
- Narzędzie/patch wokół systemu UUID w starych wersjach (zwykle serwery/offline-mode).

### Docelowe 1.18.2
- W 1.18.2 UUID to standard. Najczęściej **nie potrzebujesz odpowiednika**.
- **Strategia: C**  
- **Ryzyko: brak** dla bloków; ewentualnie wpływ na przypisanie właścicieli (jeśli mod/gracze byli w offline-mode).

---

## 10) Witchery (1.7.10)

### Funkcjonalności 1.7.10 (typowo)
- Wiedźmowa magia: rytuały, ołtarze, kręgi, mikstury, familiars, czasem wampiry/wilkołaki, światowe struktury.  
- Sporo bloków/TE.

### Docelowe mody 1.18.2 (Forge)
- **Hexerei** (wprost opisany jako “Witchery and Magic mod”) citeturn2search0  
- **Enchanted: Witchcraft** (inspirowane folklorem/okultyzmem, kierunek Witchery) citeturn3search10turn3search14  
- (Opcjonalnie, jeśli dopuszczasz Fabric): **Bewitchment** citeturn2search1turn2search19

### Strategia migracji
- **B**  
- **Ryzyko utraty danych: WYSOKIE** (inne bloki, inne rytuały, inne NBT).

### Jak mapować funkcjonalności
- Ołtarze/rytuały → rytuały Hexerei / Enchanted (koncepcyjnie podobne, technicznie inne). citeturn2search0turn3search10  
- Kociołki/alchemia → kocioł Hexerei + craft/processing w Enchanted. citeturn2search0turn3search10  
- Familiars → (zależnie od wybranego moda) + alternatywnie Occultism familiars, jeśli i tak bierzesz Occultism do “Thaumcraftowego” zestawu. citeturn3search4  
- Elementy “mroczne” (wampiry itp.) → jeśli Enchanted jest w paczce, ma taki klimat (opis wprost wspomina wampiry/witch hunters). citeturn3search10

### Co zrobić z blokami Witchery na mapie
- Jak przy Thaumcraft: najpierw “ratunek” (zrzut inwentarzy), potem remap na placeholdery/dekoracje + odtworzenie funkcji.

---

## 11) WorldEdit (1.7.10) → WorldEdit (1.18.2)

### Funkcjonalności
- Selekcje, schematy, copy/paste, pędzle, szybka edycja mapy. citeturn2search2turn2search23

### Docelowe w 1.18.2
- **WorldEdit (Forge/Fabric)** citeturn2search11turn2search2  
- (Opcjonalnie) CUI dla selekcji zależnie od loadera citeturn5search3turn5search5

### Strategia migracji
- **C** (narzędzia)  
- **Ryzyko: brak**.

---

# Co dalej (żeby to było “roboczo wykonalne”)

Dla `cz5` największe ryzyka to: **Thaumcraft + addon-y**, **Witchery**, **Traincraft** (brak “A→A”).  
Jeśli chcesz, w kolejnym kroku mogę przygotować:
1) **listę remapów “placeholderowych”** (np. TC/Witchery/Traincraft → konkretne bloki dekoracyjne z 1.18.2, żeby bryły budowli zostały),  
2) albo **plan ratunkowy TE/inwentarzy**: które klasy bloków warto zrzucić do skrzyń i jak je automatycznie opisać (signy/księgi) żeby nic nie zginęło w migracji.
