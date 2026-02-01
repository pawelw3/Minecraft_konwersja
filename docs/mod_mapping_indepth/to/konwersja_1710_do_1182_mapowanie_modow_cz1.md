# Konwersja mapy Minecraft 1.7.10 → 1.18.2 (Forge) — mapowanie modów (lista `cz1`)

Ten dokument robi **to samo**, co wcześniejsze mapowania, ale dla modów z listy `cz1` (start):  
`bspkrsCore`, `Treecapitator`, `Applied Energistics 2`, `Armourer’s Workshop`, `AsieLib`, `Backpacks (Eydamos)`, `Baubles`, `Better Storage`.

**Cel:** wskazać na jakie mody 1.18.2 przejść i jak mapować **funkcjonalności** oraz (gdy to ma sens) **bloki / block entities / itemy**.

---

## Legenda strategii migracji

- **A — ten sam mod / ta sama rodzina** (największa szansa na sensowny remap treści)
- **B — zamiennik funkcjonalny** (wymaga skryptu remapującego + zwykle utrata/rekonstrukcja NBT)
- **C — QoL / dependency / klientowe** (brak trwałej treści świata albo minimalnie)

---

## Szybka lista docelowych modów 1.18.2 (dla `cz1`)

**QoL (drzewa):** 
- Treecapitator → **FallingTree** - UWAGA konwersja niewymagana - ignoruj (1.18.2) *(podobny efekt “ścinasz 1 log i leci drzewo”)* citeturn0search3turn0search7

**ME storage / logistyka:**
- AE2 → **Applied Energistics 2** (Forge 1.18.2) citeturn0search0turn0search4

**Kosmetyka pancerza (zastępstwo za Armourer’s Workshop w 1.18.2):**  - UWAGA - konwersja tego moda niech pójdzie na sam koniec kolejki
- Armourer’s Workshop: **brak wydania na 1.18.2** (na CurseForge podane wersje zaczynają się od 1.19.3+) citeturn1search12turn1search8  
  Zamienniki funkcjonalne:
  - “drugi zestaw pancerza do wyglądu”: **Cosmetic Armor Reworked** citeturn2search2  
  - (jeśli kluczowe jest “modelowanie” i import skinów) — rozważ zmianę celu na 1.19.2+ gdzie Armourer’s Workshop istnieje; przy *twardym* celu 1.18.2 pozostaje workflow eksport → placeholdery → ręczna rekonstrukcja (opis niżej).

**Plecaki:**
- Backpacks (Eydamos) → **Sophisticated Backpacks** citeturn0search2turn0search6  
  Alternatywa: **Traveler’s Backpack** (też 1.18.2) citeturn2search1turn2search14

**Baubles / dodatkowe sloty:** - UWAGA - konwersja nie wymagana - ignoruj
- Baubles → **Curios API** citeturn0search13turn0search1

**Storage + zabezpieczenia (zamienniki za Better Storage):**
- “większe skrzynie”: **Iron Chests** citeturn1search5turn1search1  
- “modułowy storage z upgrade’ami”: **Sophisticated Storage** citeturn2search3turn2search7  
- “zamki/klucze”: **Lock & Key** citeturn3search1turn3search10 lub **Locksmith** citeturn3search2  
- “kartonowe pudełko / przenoszenie TE”: **Packing Tape** citeturn5search1turn4search1 i/lub **Carry On** citeturn2search0turn2search4  
- (jeśli chcesz “security” w stylu bazy): **SecurityCraft** (ma 1.18.2) citeturn3search0turn3search12

---

# Mapowanie per-mod (1.7.10 → 1.18.2)

## 1) bspkrsCore (1.7.10)

### Funkcjonalności 1.7.10
- Biblioteka/dependency dla modów bspkrs (np. Treecapitator).  
- Nie dodaje bloków/TE. *(czysto techniczne)*

### Docelowe 1.18.2
- **Brak potrzeby mapowania** (po prostu tego nie używasz; wybierasz nowe QoL mody).  

### Strategia / ryzyko
- **C**, ryzyko: **brak** (brak treści świata).

---

## 2) Treecapitator (1.7.10)

### Funkcjonalności 1.7.10
- Ścinanie całych drzew po zniszczeniu jednego klocka kłody; konfiguracja “balansu”.

### Docelowe 1.18.2
- **FallingTree** (podobny efekt; różne tryby “fall blocks/items”) citeturn0search7

### Strategia / ryzyko
- **C** (QoL)  
- Ryzyko: **brak** (nie ma bloków/BE do konwersji).

### Co mapować
- Wyłącznie preferencje/ustawienia (ręcznie w configach).

---

## 3) Applied Energistics 2 (AE2) (1.7.10 rv3 beta 6)

### Funkcjonalności 1.7.10 (rdzeń)
- ME Network: cyfrowy magazyn, terminale, auto-crafting, import/export, interfejsy, P2P, kontroler, drive, itp.
- Dużo bloków i “sieciowych” bytów (BE/TE, part-y na kablach).

### Docelowe 1.18.2
- **Applied Energistics 2** (Forge 1.18.2 istnieje) citeturn0search0turn0search4

### Strategia / ryzyko
- **A** (ta sama rodzina)  
- **Ryzyko utraty danych: ŚREDNIE/WYSOKIE** — mimo że to ten sam mod, skok 1.7.10 → 1.18.2 to ogromna przepaść:
  - zmiana systemu ID (stare metadane → blockstates),
  - inne NBT w maszynach (energia, kanały, konfiguracje stron),
  - inne “part-y” na kablach.

### Co mapować (praktycznie)
1) **Struktura budowli AE2 (bloki)**
   - Controller / Drive / Terminale / Assembler itp. → odpowiedniki w AE2 1.18.2 (po typie bloku).
2) **Zawartość dysków / sieci**
   - W 1.7.10 część danych mogła siedzieć w NBT komórek lub w systemowych danych sieci.
   - Najbezpieczniejszy workflow: przed migracją **zmaterializować** zawartość (np. eksport do skrzyń) albo przygotować dump przez narzędzia/komendy (jeśli masz).
3) **Kanały, P2P, ustawienia stron**
   - Prawie na pewno do rekonstrukcji (mapuj “bryłę” i podstawowe bloki, resztę odtwarzasz).

> Jeśli AE2 jest krytyczny na mapie, rozważ najpierw “konwersję ratunkową” samej zawartości (itemy do skrzyń), a dopiero potem remap bloków — bo NBT sieci to najtrudniejsza część.

---

## 4) Armourer’s Workshop (1.7.10)

### Funkcjonalności 1.7.10
- Kosmetyczne skiny pancerza/broni/narzędzi, warsztat, biblioteki skinów, projektory (dużo bloków-TE).

### Docelowe 1.18.2
- **Brak wersji Armourer’s Workshop na 1.18.2** (na CF widoczne wersje od 1.19.3+) citeturn1search12turn1search8

**Zamienniki funkcjonalne na 1.18.2 (nie 1:1):**
- **Cosmetic Armor Reworked** — drugi zestaw pancerza “na wygląd” + chowanie pancerza citeturn2search2  
- Dla “modelowania/skinów” w stylu AW: w samym 1.18.2 Forge najczęściej kończy się na resource-packach + innych modach kosmetycznych (ale nie ma pełnego odpowiednika “Skinning Table + biblioteki” z AW).

### Strategia / ryzyko
- **B** (zamiennik funkcjonalny)  
- **Ryzyko utraty danych: WYSOKIE**, bo:
  - bloki AW w świecie nie będą rozumiane w 1.18.2,
  - format skinów i TE/NBT nie przeniesie się automatem.

### Co robić, żeby “nie stracić treści”
- Jeśli masz na mapie *bloki warsztatów/bibliotek*:
  1) Na 1.7.10 zrób “ratunek”: **eksport/backup skinów** (biblioteki, foldery modowe, cokolwiek udostępnia AW).
  2) W konwerterze świata: remap bloków AW → **placeholdery dekoracyjne** (żeby budowle się nie rozsypały).
  3) W 1.18.2: zapewnij “efekt końcowy” przez Cosmetic Armor Reworked + ręczne odtworzenie wyglądu (zależnie jak trzymałeś skiny).

---

## 5) AsieLib (1.7.10)

### Funkcjonalności 1.7.10
- Biblioteka/dependency dla modów asie (bez własnych bloków/TE).

### Docelowe 1.18.2
- **Nie migrujesz**; w 1.18.2 używasz modów, które mają własne zależności.

### Strategia / ryzyko
- **C**, ryzyko: **brak**.

---

## 6) Backpacks (Eydamos) (1.7.x)

### Funkcjonalności 1.7.10
- Plecaki (3 rozmiary), materiały do craftu, legacy plecaki (ender/workbench).  
- To głównie **itemy** (bez bloków/TE).

### Docelowe 1.18.2
- **Sophisticated Backpacks** (najczęściej wybierany) citeturn0search2turn0search6  
- Alternatywnie: **Traveler’s Backpack** (Curios-integrated) citeturn2search5turn2search14

### Strategia / ryzyko
- **B** (zamiennik funkcjonalny)  
- **Ryzyko utraty danych: ŚREDNIE/WYSOKIE** zależnie od tego, jak plecaki kodowały zawartość:
  - jeśli “w środku” jest NBT-inventory — trzeba to przepisać,
  - jeśli plecak był jak “kontener item” — najbezpieczniej wypakować do skrzyń przed konwersją.

### Co mapować
- Same plecaki → nowe plecaki (zwykle “własny” format NBT, więc częściej robisz:  
  **wypakuj zawartość** → daj nowy pusty plecak + itemy obok).
- Jeśli używałeś “ender backpack”: w 1.18.2 zwykle zastępuje to ender chest / EnderStorage / dodatki — zależnie od paczki.

---

## 7) Baubles (1.7.10)

### Funkcjonalności 1.7.10
- API + dodatkowe sloty (amulet, belt, ringi).  
- Sam mod praktycznie bez contentu (poza drobnicą).

### Docelowe 1.18.2
- **Curios API** (standardowy odpowiednik “extra slots” na Forge) citeturn0search13turn0search1

### Strategia / ryzyko
- **C/B**:
  - **C** dla samego API (świat nic nie traci),
  - **B** jeśli chcesz mapować konkretne “bauble itemy” z innych modów (wtedy per-mod).

---

## 8) Better Storage (1.7.10)

### Funkcjonalności 1.7.10 (rdzeń)
- Storage: reinforced chests, lockers, storage crates.  
- System locków/kluczy + enchanty.  
- Cardboard box do przenoszenia bloków/TE.  
- Crafting Station, Armor Stand (blok), różne “gadżety”.

### Docelowe 1.18.2 (proponowany “zestaw sklejany”)
**Storage:**
- **Iron Chests** (proste “większe skrzynie”) citeturn1search5turn1search1  
- **Sophisticated Storage** (barrels/chests/shulkers + upgrade’y, bardziej “modowe”) citeturn2search3turn2search7  

**Zamki/klucze:**
- **Lock & Key** (bazuje na vanilla lockingu TE) citeturn3search1turn3search10  
- lub **Locksmith** (bardziej “immersyjne” zamki) citeturn3search2  

**Przenoszenie TE (zastępstwo dla Cardboard Box):**
- **Packing Tape** citeturn5search1turn4search1  
- i/lub **Carry On** citeturn2search0turn2search4  

**Crafting Station (trzyma itemy / korzysta z sąsiednich inv):**
- **Crafting Station** citeturn5search0  

**Bezpieczeństwo bazowe (opcjonalnie):**
- **SecurityCraft** (jeśli potrzebujesz “fortyfikacji” i zabezpieczonych bloków) citeturn3search0turn3search12  

### Strategia / ryzyko
- **B** (zamienniki funkcjonalne)  
- **Ryzyko utraty danych: WYSOKIE**, bo:
  - Better Storage nie ma kompatybilnego portu świata,
  - TE/NBT (locki, enchanty, zabezpieczenia, zawartości) są specyficzne.

### Co mapować (praktycznie, żeby uratować treść)
1) **Reinforced Chests / Lockers / Crates**
   - Zanim cokolwiek zmienisz: wykonaj etap “ratunkowy”:
     - skrypt wyciąga zawartość TE do skrzyń (w pobliżu) + podpisuje (np. tabliczką/księgą) co to było.
   - Potem remap bryły:
     - chest → Iron Chest/Sophisticated Chest
     - locker/crate → Sophisticated Storage (barrel/chest) lub Storage Crate-like rozwiązanie
2) **Lock & Key / Security**
   - Format locków i kluczy nie jest przenośny 1:1.
   - Najbardziej realistyczne: odtworzyć “zabezpieczenie” docelowym modem po konwersji.
3) **Cardboard Box**
   - Na 1.18.2 odpowiednik mechaniki dają Packing Tape/Carry On.
   - Same “pudełka” z 1.7.10 jako itemy — raczej do zamiany/fallbacku.

---

# Mini-checklista dla `cz1` (co jest “krytyczne” dla mapy)

1) **AE2**: jeśli masz rozbudowane ME sieci, przygotuj plan ratunkowy na dane (dyski/komórki/NBT).  
2) **Armourer’s Workshop**: jeśli masz stacje/biblioteki na mapie, zrób eksport skinów i placeholdery w świecie (1.18.2 nie ma AW).  
3) **Better Storage**: zaplanuj “wypakowanie inwentarzy” i dopiero potem remap na Iron Chests / Sophisticated Storage + system locków.

Jeśli chcesz, mogę w kolejnym kroku przygotować dla `cz1`:
- szkic **tabeli remapów** (old block → docelowy blockstate) z fallbackami,
- albo “plan ratunkowy NBT/inv” (które TE wypakować i jak je opisać w świecie).
