# Konwersja mapy Minecraft 1.7.10 → 1.18.2 (Forge) — mapowanie modów (na razie: lista z `cz4`)

Ta notatka opisuje **jakie funkcjonalności** wnoszą mody z Twojej paczki **1.7.10 (cz4)** oraz **na jakie mody 1.18.2** (lub zestawy modów) można przejść, żeby:
- zachować *możliwie dużo* treści z mapy (bloki / block entities / przedmioty),
- oraz przygotować się do **automatycznego mapowania** ID bloków/NBT tam, gdzie to w ogóle wykonalne.

> **Twarda prawda o “braku utraty treści”**  
> W praktyce **100% zachowanie** bloków/TE z 1.7.10 przy przeskoku do 1.18.2 jest możliwe *tylko* wtedy, gdy:
> 1) mod ma wersję na 1.18.2 **i**  
> 2) ma ścieżkę migracji danych świata (remap starych ID → nowych + konwersja NBT).  
> Dla wielu modów z 1.7.10 (szczególnie starych dekoracyjnych i nieutrzymywanych) **nie istnieje** oficjalna migracja 1.7.10 → 1.18.2, więc potrzebujesz **skryptu/konwertera świata**, który:
> - zamieni stare bloki na nowe odpowiedniki,
> - przetłumaczy NBT w TE (jeśli da się sensownie),
> - albo przynajmniej zabezpieczy zawartość (np. wypakowanie inwentarzy do skrzyń / zapis do plików).

W tym pliku, przy każdym modzie, podaję:
- **Docelowe mody 1.18.2** (najbardziej sensowne zamienniki),
- **Strategię migracji** (A/B/C),
- **Ryzyko utraty danych** (NISKIE / ŚREDNIE / WYSOKIE),
- **Co mapować** (bloki, TE, encje, itemy).

---

## Legenda strategii migracji

- **A — “ten sam mod / ta sama rodzina”**  
  Najlepszy scenariusz. Docelowo używasz tego samego moda (albo oficjalnego następcy) działającego na 1.18.2.  
  *Szansa na automatyczne mapowanie:* najwyższa (ale nadal zależy od tego, czy autor przewidział migrację z tak starej wersji).

- **B — “zamiennik funkcjonalny”**  
  Inny mod zapewnia podobną funkcjonalność, ale **nie rozumie** starych bloków.  
  *Wymagane:* skrypt konwersji świata (mapa bloków + NBT), inaczej bloki znikną / zamienią się w „missing”.

- **C — “klientowe/QoL/diagnostyka”**  
  Mody, które nie wnoszą trwałych bloków/TE do świata (albo wnoszą minimalnie).  
  Migracja polega na zastąpieniu narzędzia innym narzędziem.

---

## Szybka lista docelowych modów 1.18.2 (dla `cz4`)

**Interfejs, QoL, narzędzia:**
- NEI → **JEI** (ew. REI jako alternatywa do przeglądu przepisów)
- NoMoreRecipeConflict → **Polymorph**
- Opis → **spark** (profilowanie), opcjonalnie **Observable** (GUI profilera)
- Rei’s Minimap → **Xaero’s Minimap** albo **JourneyMap**

**Budowanie / dekoracje:**
- MrCrayfishFurniture (1.7.10) → **Macaw’s Furniture** / **Another Furniture** / **Decocraft** (dobór zależny od tego, co masz na mapie)
- Placeable Items → **Placeable Items** (jest na 1.18.2)

**Technika / logistyka / energia:**
- ProjectRed (cały zestaw) → **Project Red (1.18.2 moduły)** + **CB Multipart**
- PowerConverters → w 1.18.2 zwykle zbędne (wszyscy siedzą na FE), ale jeśli musisz “mostkować” systemy, patrz: **RF Converter** (1.18.2)
- Railcraft → brak pełnej ścieżki na 1.18.2 (zależnie od priorytetów: **Create** (+ kolejowe addon-y) / **Little Logistics**; *w pełni wiernego zamiennika Railcraft 1.7.10 na 1.18.2 zazwyczaj nie ma*)

**Obrona / turrety:**
- Open Modular Turrets → brak portu 1.18.2; najbliżej: **Immersive Engineering** (kilka turretek) lub osobne małe mody “turretowe” (np. **K‑Turrets** ma wydanie na 1.18.2)

---

# Mapowanie per-mod (1.7.10 → 1.18.2)

## 1) MrCrayfish’s Furniture Mod v3.4.8 (1.7.10)

### Funkcjonalności 1.7.10 (z grubsza)
- Bardzo dużo **mebli**: kuchnia, salon, sypialnia, ogród, dekoracje.
- Część bloków ma **interakcje** (np. otwierane szafki/inwentarze, urządzenia).
- Często występują **Tile Entities** (np. elementy z GUI/inwentarzem, poczta itp.).

### Docelowe mody 1.18.2 (zamienniki)
**Opcja 1 (styl “vanilla+”, dużo użytecznych mebli):**
- **Macaw’s Furniture** (dużo mebli + warianty drewna, część storage)

**Opcja 2 (proste, spójne dekoracje):**
- **Another Furniture** (vanilla-styled, spójne wymiary)

**Opcja 3 (największa liczba dekoracji):**
- **Decocraft** (tysiące dekoracji; duża rozbieżność w modelach/nazwach)

### Strategia migracji
- **B (zamiennik funkcjonalny)** — w 1.18.2 nie ma “tej samej” linii moda z 1.7.10, więc **bez skryptu mapującego** stracisz bloki.
- **Ryzyko utraty danych: WYSOKIE**, szczególnie dla bloków z inwentarzem / pocztą / stanami.

### Co i jak mapować
- **Bloki dekoracyjne**: mapuj 1:1 na najbliższy odpowiednik (np. “chair” → “chair”, “table” → “table”).  
  Jeśli brak odpowiednika → fallback (np. beczka/szafka z innym modem + znak opisowy).
- **Bloki z inwentarzem** (szafki, lodówki, itp.):  
  - Najbezpieczniej: podczas konwersji **wypakować zawartość** do skrzyń w pobliżu,  
  - potem podmienić blok na “docelowy storage” (np. szafka Macaw’s) już pusty, a loot w skrzyni zachować.
- **Bloki “funkcyjne”** (mailbox, itp.): zwykle wymagają ręcznego rozstrzygnięcia, bo mechaniki różnią się między modami.

---

## 2) MrTJPCore (1.7.10)

### Funkcjonalności 1.7.10
- Biblioteka / dependency (m.in. pod ProjectRed), bez własnych dużych bloków.

### Docelowe w 1.18.2
- W nowoczesnym Project Red rolę zależności pełnią inne biblioteki (typowo **CB Multipart**, **CodeChickenLib** itp.).  
- **MrTJPCore nie jest “celem migracji”** — w 1.18.2 zwykle go nie potrzebujesz jako osobnego moda.

### Strategia migracji
- **C (dependency)**  
- **Ryzyko utraty danych: NISKIE** (sam z siebie nie niesie “treści świata”).

---

## 3) NoMoreRecipeConflict (1.7.10)

### Funkcjonalności 1.7.10
- Rozwiązywanie konfliktów przepisów (to samo wejście → wiele wyjść).

### Docelowe w 1.18.2
- **Polymorph** (GUI wyboru wyniku craftingu, gdy konflikt występuje).

### Strategia migracji
- **C (QoL)**  
- **Ryzyko utraty danych: brak** (nie trzyma bloków w świecie).

---

## 4) NotEnoughItems (NEI) (1.7.10)

### Funkcjonalności 1.7.10
- Przegląd przepisów, wyszukiwarka itemów, cheat-mode, integracje.

### Docelowe w 1.18.2
- **JEI** (najbardziej standardowy na Forge)  
- Alternatywnie: **REI** (jeśli wolisz jego UI)

### Strategia migracji
- **C (QoL)**

---

## 5) Open Modular Turrets (1.7.10)

### Funkcjonalności 1.7.10
- System turretek + amunicja, targetowanie, peryferia; zwykle wiele bloków i TE.

### Docelowe w 1.18.2 (zamienniki)
- **Immersive Engineering**: kilka typów turretek (mniej “modularne”, ale działają)
- **K‑Turrets**: osobny mod turretek (ma wydanie na 1.18.2)

### Strategia migracji
- **B (zamiennik funkcjonalny)**  
- **Ryzyko utraty danych: WYSOKIE** (różne NBT, inna mechanika, inny zestaw bloków).

### Co mapować
- Turret blocks → najbliższe turret blocks (IE / K‑Turrets).  
- Ammo / upgrade-y → zwykle nie do przełożenia 1:1; zalecany fallback: “skrzynia z dropem” + ręczna migracja.

---

## 6) Opis (1.7.10)

### Funkcjonalności 1.7.10
- Diagnostyka: TPS, profile ticków, obciążenia TE/encje.

### Docelowe w 1.18.2
- **spark** (profilowanie)
- Opcjonalnie **Observable** (wizualizacja “co laguje” — duchowy następca LagGoggles)

### Strategia migracji
- **C (narzędzia)**

---

## 7) Pam’s HarvestCraft (1.7.10)

### Funkcjonalności 1.7.10 (w skrócie)
- Ogromny zestaw **upraw, drzew, jedzenia, maszyn kuchennych** (często TE dla narzędzi/stanów).
- Bloki typu: ogrody/krzaki, sady, urządzenia kuchenne, itd.

### Docelowe w 1.18.2
- **Pam’s HarvestCraft 2** (to reboot, nie “ten sam mod”, ale najbliższa oficjalna kontynuacja)  
  Zwykle rozbite na moduły: Food Core / Crops / Trees / Food Extended.

### Strategia migracji
- **B (zamiennik funkcjonalny / reboot)**  
- **Ryzyko utraty danych: WYSOKIE**, bo:
  - nazwy i ID itemów są inne,
  - sporo systemów zostało przebudowanych,
  - TE/NBT nie będą kompatybilne.

### Co mapować
- **Uprawy/krzaki/drzewa**: mapowanie gatunek→gatunek (tam gdzie istnieje), w pozostałych przypadkach fallback (np. na “najbliższy” crop).  
- **Jedzenie**: bardzo dużo pozycji; praktycznie potrzebujesz automatycznego “item remap” + fallback na “Food Core” lub inne mody jedzeniowe, jeśli czegoś brakuje.
- **Maszyny kuchenne / narzędzia**: mapowanie konceptualne (np. “cutting board” → “cutting board”), ale receptury i NBT prawie na pewno inne.

---

## 8) Placeable Items Mod (1.7.10)

### Funkcjonalności 1.7.10
- Pozwala kłaść przedmioty w świecie jako modele 3D (często w formie TE).

### Docelowe w 1.18.2
- **Placeable Items** (jest wydanie na 1.18.2)

### Strategia migracji
- **A/B w praktyce**:
  - Funkcjonalnie jest to “ten sam” typ moda, ale **nie zakładaj kompatybilności NBT** między 1.7.10 a 1.18.2.
- **Ryzyko utraty danych: ŚREDNIE/WYSOKIE** — zależy, jak mod koduje TE (stare → nowe).

### Co mapować
- Obiekty “położone” (TE) → odpowiednik w nowym Placeable Items.  
  Jeśli NBT niezgodne: najlepsza praktyka to zamienić TE na:
  - stojak/ramka/“display block” z innym modem,
  - lub zebrać dane (co było położone) i odtworzyć.

---

## 9) PowerConverters (1.7.10)

### Funkcjonalności 1.7.10
- Mostki między różnymi systemami energii (RF/MJ/EU itp.), zwykle z własnymi blokami/TE.

### Docelowe w 1.18.2
- W 1.18.2 większość tech-modów używa **Forge Energy (FE)**, więc często “konwertery” nie są potrzebne.
- Jeśli jednak chcesz mostkować egzotyczne systemy: **RF Converter** (ma wydanie na 1.18.2).

### Strategia migracji
- **B (zamiennik funkcjonalny)**  
- **Ryzyko utraty danych: ŚREDNIE** (zwykle proste bloki, ale i tak inne NBT).

---

## 10) ProjectRed (Base/Compat/Fabrication/Integration/Lighting/Mechanical/World) (1.7.10)

### Funkcjonalności 1.7.10 (rdzeń)
- **Wiring/Transmission**: przewody, bundled cables, routing sygnałów.
- **Integration**: bramki, logika, sensory, integracja z redstone.
- **Fabrication**: “redstone IC” / układy scalone (płytki, projektowanie).
- **Lighting**: lampki, oświetlenie (często mikro-bloki / multipart).
- **World/Mechanical**: generacja rud/zasobów + elementy mechaniczne (różnie w zależności od paczki).

### Docelowe w 1.18.2
- **Project Red (1.18.2) jako zestaw modułów**:
  - Transmission, Illumination, Integration, Fabrication (+ ewentualnie Exploration/Expansion zależnie od potrzeb)
- **CB Multipart** (w 1.18.2 Project Red intensywnie z niego korzysta)

### Strategia migracji
- **A (ta sama rodzina modów)**, ale z ostrzeżeniem:
  - kompatybilność świata **z 1.7.10** nie jest gwarantowana,
  - natomiast to i tak jest *najlepsza baza* do utrzymania “tego samego rodzaju bloków”.

**Ryzyko utraty danych: ŚREDNIE/WYSOKIE**  
- Najtrudniejsze są: multipart w jednym bloku, custom NBT dla IC/układów, stare metadane.

### Co mapować
- **Przewody / bundled**: 1:1 na Transmission (nowe ID).  
- **Lampy / wskaźniki**: na Illumination.  
- **Gates / logika**: na Integration.  
- **IC/planowanie układów**: na Fabrication (tu ryzyko największe, bo format danych mógł się zmienić).

### Rekomendacja praktyczna
Jeśli na mapie masz dużo instalacji ProjectRed:
1) docelowo koniecznie użyj **Project Red + CB Multipart** na 1.18.2,  
2) przygotuj **tabelę remapów** (stare bloki → nowe registry name) i sprawdź, co Forge zapisuje jako “missing mappings”,  
3) na TE od Fabrication rozważ eksport/import projektów (jeśli mod ma jakąkolwiek formę “schematic/blueprint” w nowszej wersji) — inaczej licz się z ręczną rekonstrukcją.

---

## 11) Railcraft (1.7.10)

### Funkcjonalności 1.7.10 (typowe)
- Zaawansowana kolej: tory, sygnalizacja, rozjazdy, lokomotywy/wozy (zależnie od wersji), maszyny kolejowe.
- Bardzo dużo bloków i TE.

### Docelowe w 1.18.2
W MC 1.18.2 **nie ma powszechnie używanego, kompletnego Railcraft-a** z pełną kompatybilnością świata 1.7.10.
Najbliższe sensowne “zastępstwo funkcjonalne”:
- **Create** (ma system kolei/pociągów w 1.18.2)
- **Create: Steam ’n’ Rails** (rozszerza kolej Create)
- Opcjonalnie: **Little Logistics** (transport “kolejowo-wodny” w stylu lekkiej logistyki)

### Strategia migracji
- **B (zamiennik funkcjonalny)**  
- **Ryzyko utraty danych: WYSOKIE**, bo:
  - inny system kolei,
  - inne bloki,
  - inne encje/TE,
  - brak 1:1 zamienników dla sygnałów/maszyn.

### Co mapować
- Tory/rozjazdy → tory Create (tam gdzie ma sens).  
- Sygnalizacja → semafory/sygnalizacja Create (jeśli używasz Steam ’n’ Rails) lub inny mod sygnalizacji.  
- Maszyny Railcraft (koksowniki, walcarki itp. — jeśli były) → odpowiedniki w Create/Immersive Engineering/innym tech-modzie (to już wykracza poza `cz4`, ale warto uwzględnić w szerszym planie).

---

## 12) Rei’s Minimap (1.7.10)

### Funkcjonalności 1.7.10
- Minimapa, waypointy, opcjonalnie “cave mode”.

### Docelowe w 1.18.2
- **Xaero’s Minimap** (minimapa + waypointy)
- **JourneyMap** (minimapa + mapa pełnoekranowa + web map)

### Strategia migracji
- **C (klientowe)**  
- Waypointy raczej będziesz przenosić ręcznie (formaty danych różne).

---

# Checklist “co dalej” (żeby to dało się realnie zautomatyzować)

1) **Zidentyfikuj, które mody realnie zostawiają bloki/TE na mapie**  
   (dla `cz4` to głównie: MrCrayfishFurniture, OMT, HarvestCraft, PlaceableItems, PowerConverters, ProjectRed, Railcraft).

2) Dla każdego z nich przygotuj:
   - listę starych ID bloków (z 1.7.10),
   - listę docelowych registry names (1.18.2),
   - reguły NBT (co przenieść, co zrzucić do skrzyń).

3) Zrób **dwuetapową konwersję**:
   - etap “ratunkowy”: zabezpiecz inwentarze/unikalne dane (skrzynie/eksport),
   - etap “remap”: zamień bloki na docelowe odpowiedniki.

Jeśli chcesz, w następnym kroku mogę:
- wygenerować **szkielet tabeli remapów** (CSV/JSON) dla `cz4` (np. po 20–50 najbardziej typowych bloków na mod, z fallbackami),
- albo zacząć od **ProjectRed**, bo to jedyny z `cz4`, który ma sensowną szansę na “najmniej bolesną” migrację do 1.18.2.
