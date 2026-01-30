# Konwersja świata: Minecraft 1.7.10 → 1.18.2 — mapowanie modów (część 2)

To jest **mapowanie funkcjonalności** dla modów z pliku: `mod_funkcjonalnosci_1.7.10_cz2.md`
Cel: wskazać, **na jakie mody w 1.18.2 (Forge)** przejść, żeby dało się *odtworzyć* możliwie pełny zestaw bloków / blok-encji (tile entities / block entities) / przedmiotów **bez utraty „treści” mapy**.

> Ważna uwaga (realizm migracji):
> - Jeśli mod **ma wersję na 1.18.2** (ten sam „rodowód”), zwykle da się zachować logikę i NBT w obrębie moda (choć formaty NBT i ID i tak potrafią się zmienić).
> - Jeśli mod **nie istnieje na 1.18.2**, nie ma magicznej konwersji „blok → blok” bez narzędzi/patchy: w praktyce kończy się na:
>   - *zamianie* bloków na inne (remap ID + ewentualnie translacja NBT),
>   - albo *zachowaniu geometrii* przez eksport/replace (schematy, struktury) i ręczne/automatyczne odtworzenie funkcji.
> - W tej liście wprost zaznaczam, gdzie **pełna migracja 1:1 jest realna**, a gdzie to **„odtworzenie funkcji”**.

---

## 1) BiblioCraft (1.7.10) → (brak dobrego portu na 1.18.2)

**Co wnosiło w 1.7.10 (skrót):**
- masa **mebli/dekoracji** (półki, regały, stoły, krzesła, biurka, lampy, ramki/ekspozytory),
- funkcjonalne bloki „wystawiennicze” (np. półki/pojemniki na itemy, stojaki),
- elementy „biblioteczne” (regały, książki/ozdoby),
- często używane w mapach przygodowych (dekor + „propsy”).

**Stan na 1.18.2:**
- Nie ma powszechnie używanego, stabilnego portu BiblioCraft na 1.18.2; istnieją inicjatywy typu **BiblioCraft Legacy**, ale dotyczą nowszych wersji (np. 1.21.x / NeoForge), więc **nie ratują 1.18.2**.

**Rekomendowane „zastępstwa funkcjonalne” (1.18.2):**
- **Supplementaries** – dużo vanilla+ dekoracji, część z automatyzacją i interakcjami (dobre „zastępstwo klimatu”).
- **Handcrafted** – duży pakiet mebli (wnętrza) jako zamiennik meblowania.
- (opcjonalnie) **Chipped / Rechiseled** (patrz sekcja Chisel) do „detalu” bloków.

**Jak mapować treść mapy (praktycznie):**
- Jeśli w świecie masz dużo BiblioCraftowych mebli jako **kluczowe elementy dekoracyjne**:
  - *automatyczny remap* raczej nie da ładnych wyników (inne modele/kolizje),
  - sensowniejsze jest: **zastąpić placeholderami** (np. blokami z FramedBlocks/Chipped) i potem dopasować dekorację.
- Jeżeli BiblioCraft był użyty „funkcyjnie” (np. jako ekspozytory przedmiotów):
  - rozważ zastąpienie **ramkami/stojakami** z Supplementaries lub innymi modami dekoracyjnymi – ale to będzie **rekonstrukcja**, nie migracja NBT.

---

## 2) Big Reactors (1.7.10) → Extreme Reactors (1.18.2)

**Dlaczego to jest dobre mapowanie:**
**Extreme Reactors** to **port Big Reactors** do nowszych wersji.

**Mapowanie funkcji / bloków:**
- Wieloblokowy reaktor (kontroler, obudowy, pręty paliwowe, porty IO) → Extreme Reactors (reaktor)
- Turbina (wieloblok, wał/łopatki, porty) → Extreme Reactors (turbina)
- Paliwa/odpady (Yellorium/Cyanite) → w nowszych wersjach nazewnictwo/recepty mogą się różnić, ale koncept (paliwo/odpady) zostaje.

**Uwagi migracyjne:**
- Nadal **wielobloki** często mają inne wewnętrzne reprezentacje; jeśli chcesz zachować *dokładny kształt konstrukcji*, przygotuj się na:
  - przebudowę (jeśli struktura przestanie być poprawna),
  - lub skrypt/replace (jeśli w reaktorze były ważne ustawienia NBT).

---

## 3) Blood Magic (1.7.10) → Blood Magic (1.18.2)

**Najprostszy przypadek:** Blood Magic ma wersje na 1.18.2.

**Mapowanie funkcji:**
- Ołtarz krwi / runy / rytuały → analogiczne systemy w nowszym BM (mimo zmian balansu)
- Sieć krwi (orb, sigile, alchemia) → zachowane jako koncept

**Uwagi migracyjne:**
- BM to mod mocno NBT-zależny (ołtarze, orby, rytuały) – jeśli zależy Ci na zachowaniu *stanu maszyn*,
  najlepiej migrować świat etapowo (najpierw uruchomić go na możliwie „pośredniej” wersji BM, jeśli istnieje).

---

## 4) Bookshelf (1.7.10) → Bookshelf (1.18.2)

To był **mod-biblioteka**. W 1.18.2 nadal istnieje jako biblioteka dla innych modów.

**Wpływ na mapę:**
- Zwykle **brak własnych bloków/BE w świecie** (albo minimalny), więc to „łatwy” element migracji.

---

## 5) BuildCraft + BuildCraft Compat (1.7.10) → zestaw zamienników (1.18.2)

**Problem:** BuildCraft w klasycznej formie nie jest standardem w 1.18.2, a nawet jeśli istnieją fork/porty, w praktyce ekosystem przeniósł się na inne rozwiązania.

### 5A) Transport (item/fluid) — rury, pompy, ekstrakcja
**Zamienniki:**
- **Pipez** – proste rury item/fluid/energy (plus gazy Mekanism), często wystarcza jako „rury BC”.
- **XNet** – „sieć kablowa” do transportu itemów/płynów/energii i logiki/filtrów (bliżej „inteligentnych” systemów).

### 5B) Quary / wydobycie obszarowe
**Zamiennik:**
- **RFTools Builder** – Builder + karty kształtów (w tym tryby „quarry”), to popularny odpowiednik „BC Quarry”.
  (Wymaga **RFTools Base**).

### 5C) „Gates” / automatyka warunkowa (sygnały, logika)
**Zamienniki:**
- **Integrated Dynamics** – wprost opisuje się jako miks „bundled redstone, BuildCraft gates i AE-style networks”.
- **XNet** (kanały + kontrolery) – też potrafi robić „logikę dystrybucji”.

**Uwagi migracyjne (BuildCraft):**
- Jeżeli w mapie masz **złożone sieci rur BC** z filtrami, silnikami, bramkami:
  - przeniesienie 1:1 raczej nie wyjdzie,
  - ale „treść” (co gdzie płynęło) da się odtworzyć: Pipez/XNet + ewentualnie mechanika z Create/Mekanism (w Twoim packu i tak występują później).

---

## 6) Carpenter’s Blocks (1.7.10) → FramedBlocks (1.18.2)

**Cel funkcjonalny w 1.7.10:**
„blok w blok” (pokrywanie teksturą innego bloku), masę kształtów (schody, skosy, płoty, drzwi itp.), czyli **budowlane mikroszlifowanie**.

**Zamiennik w 1.18.2:**
- **FramedBlocks** – daje wiele kształtów, które mogą „udawać” prawie dowolny blok (bardzo blisko idei Carpenter’s).

**Uwagi migracyjne:**
- To *nie jest* ten sam mod, więc NBT/ID nie będzie zgodny.
- Najlepsza strategia to „zamiana wizualna”:
  - przemapuj Carpenter’s Blocks do odpowiadających kształtów z FramedBlocks,
  - zapis „jaką teksturę udawał” trzeba będzie przetłumaczyć (lub ręcznie poprawić), jeśli zależy Ci na idealnym wyglądzie.

---

## 7) Chisel (1.7.10) → Chipped + Rechiseled (1.18.2)

**Co dawał Chisel:** setki wariantów dekoracyjnych (kamień, drewno, cegły, itp.), często jako osobne bloki/metadata.

**Zamienniki:**
- **Chipped** – bardzo duża liczba wariantów dekoracyjnych.
- **Rechiseled** – warianty dekoracyjne, podobny „duch” Chisel.

**Uwagi migracyjne:**
- Chisel w 1.7.10 często używał *metadata*; w 1.18.2 wszystko jest w „blockstate” – remap jest możliwy, ale:
  - nie ma 1:1 pokrycia wszystkich wariantów,
  - realistycznie robisz mapping „kategoria → najbliższy odpowiednik”.

---

## 8) CodeChickenCore + CodeChickenLib (1.7.10) → CodeChickenLib (1.18.2)

- W praktyce to głównie **biblioteki** pod inne mody.
- **CodeChickenLib** istnieje na nowszych wersjach (w tym linia pod 1.18.2).
- **CodeChickenCore** jako osobny byt jest w nowych wersjach zazwyczaj zbędny (zastąpiony/rozproszony).

**Wpływ na świat:** minimalny (zwykle brak własnych bloków do migracji).

---

## 9) CoFHCore (1.7.10) → CoFH Core + Thermal Series (1.18.2)

W 1.7.10 CoFHCore często był „rdzeniem” dla Thermal i dodatków.

**W 1.18.2:**
- **CoFH Core** nadal istnieje jako core dla Team CoFH.
- Warstwa „contentowa” jest w modułach Thermal (np. **Thermal Foundation** itd.).

**Uwagi migracyjne:**
- Sam CoFHCore zwykle nie stanowi treści mapy; treść jest w Thermal (u Ciebie w cz.5).

---

## 10) ComputerCraft (1.7.10) → CC: Tweaked (1.18.2)

**CC: Tweaked** to fork/continuation ComputerCraft z komputerami, turtle, rednet itd.

**Mapowanie funkcji:**
- Computer / Advanced Computer → CC: Tweaked komputer
- Turtle / Advanced Turtle → CC: Tweaked turtle
- Peripherals (monitor, printer, dyskietki, modemy) → analogiczne peryferia CC:T

**Uwagi migracyjne:**
- Skrypty mogą wymagać poprawek (API się rozwijało), ale idea jest ta sama.
- Bloki/BE raczej nie przeniosą się 1:1 bez remapu ID + konwersji NBT.

---

## 11) CraftGuide (1.7.10) → JEI (1.18.2)

CraftGuide to stary przegląd receptur, dziś standardem jest **Just Enough Items (JEI)**.

**Wpływ na mapę:** praktycznie żaden (to GUI/QoL).

---

## 12) CustomNPCs (1.7.10) → Easy NPC (1.18.2) + (opcjonalnie) system questów

**Problem:** CustomNPCs w stylu Noppes nie ma stabilnego wydania na 1.18.2 (sensownie pojawia się dopiero na nowszych wersjach lub w ogóle brak).

**Zamiennik na 1.18.2:**
- **Easy NPC** (Forge 1.18.2) – pozwala tworzyć NPC z dialogami / interakcjami (pod mapy RPG).

**Czego może brakować względem CustomNPCs:**
- rozbudowane frakcje, skrypty, banki, zaawansowane questy itp. (zależy jak używałeś CNPC).

**Jak odtworzyć „treść” mapy:**
- Jeśli CNPC było „tylko” do postaci i dialogów → Easy NPC zwykle wystarczy.
- Jeśli CNPC było rdzeniem questowania / skryptów:
  - docelowo musisz dołożyć osobny mod na questy (np. linia FTB Quests) i spiąć to dialogami / komendami.
  - To będzie **rekonstrukcja scenariusza**, nie prosta migracja NBT.

---

## 13) EJML-core (w folderze IC2) → (ignoruj na etapie mapowania treści)

To biblioteka matematyczna dorzucona przy IC2, nie treść świata.

---

## 14) Enchanting Plus (1.7.10) → Apotheosis (1.18.2) + (opcjonalnie) Polymorph

**Co dawał Enchanting Plus:** większa kontrola nad enchantami (wybór/zarządzanie, kosztem XP).

**Najbliższy odpowiednik systemowy na 1.18.2:**
- **Apotheosis** (moduł enchantingu) – duża przebudowa enchantowania i narzędzia wokół tego.
  (Jeśli chcesz tylko enchanting – w nowszych wersjach istnieje też „Apothic Enchanting” jako wydzielony moduł, ale dla 1.18.2 najczęściej używa się pełnego Apotheosis).

**Uwaga praktyczna:**
Enchanting Plus to osobny blok/TE, więc bez portu **nie zachowasz** jego stanu/ustawień – ale funkcję „kontrolowanego enchantowania” odtworzysz w Apotheosis.

---

## 15) EnderStorage (1.7.10) → Ender Storage 1.8.+ (1.18.2) + CodeChickenLib

**Jest kontynuacja:** Ender Storage 1.8.+ działa w nowoczesnych wersjach.
**Wymaga CodeChickenLib** (patrz sekcja 8).

**Mapowanie funkcji:**
- kolorowane Ender Chesty / Ender Tanks (linkowane kanały) → analogicznie w EnderStorage 1.8.+

**Uwagi migracyjne:**
- ID bloków na pewno się różnią; jeśli chcesz zachować zawartość „kanałów”,
  musisz przemapować **kolory/kanały** i NBT (zależnie od różnic wersji).

---

## 16) Extra Utilities (1.7.10) → Extra Utilities Reborn (1.18.2) + „standalone” pod konkretne klocki

**Dobra wiadomość:** jest **Extra Utilities Reborn** na 1.18.2 (nieoficjalny port/rekonstrukcja „legacy”).
To jest najbliższa droga do zachowania „klimatu” i części mechanik.

**Ale:** ExU miało bardzo dużo elementów – w mapach zwykle pojawiają się konkretne „must have” bloki. Dlatego proponuję podejście hybrydowe:

### 16A) „Cursed Earth” (farmy mobów)
- Możesz użyć osobnego moda **Cursed Earth** na 1.18.2.
- (alternatywnie) jeśli Extra Utilities Reborn ma własny odpowiednik – wtedy trzymaj się jednego moda.

### 16B) „Angel Block” (budowanie w powietrzu)
- **Angel Block Renewed** (1.18.2)
- **Angel Block: Restored** (1.18.2) – wprost „przywraca Angel Block z Extra Utilities”.

### 16C) „Mega/Magnum Torch” (blokada spawnu w promieniu)
- **Torchmaster** – klasyczna „mega torch” inspiracja ExU.
- **Magnum Torch** – alternatywa „silnych pochodni” na 1.18.2.

### 16D) Transfer Nodes/Pipes, prosty transport
- Jeśli ExU Reborn nie pokryje Twoich potrzeb albo chcesz lepszej kontroli:
  - **Pipez** (patrz sekcja BuildCraft) jako zamiennik „transfer node + pipes”.
  - (bardziej zaawansowane) **XNet**.

**Uwagi migracyjne (Extra Utilities):**
- Jeśli w mapie masz kluczowe mechanizmy ExU (np. Ender Quarry / bardzo specyficzne generatory):
  - sprawdź, co dokładnie pokrywa Extra Utilities Reborn (nie wszystko musi być 1:1),
  - brakujące elementy mapuj na osobne mody „specjalistyczne” (quarry: RFTools Builder; transport: Pipez/XNet; antyspawn: Torchmaster; itp.).

---

## 17) FastCraft (1.7.10) → zestaw modów optymalizacyjnych (1.18.2)

FastCraft w 1.7.10 był „performance core”. W 1.18.2 robisz to zestawem kilku małych modów:

**Proponowany minimalny zestaw (Forge 1.18.2):**
- **Rubidium** (Sodium na Forge) – duży boost renderu/FPS.
- **FerriteCore** – redukcja użycia RAM.
- **Starlight (Forge)** – przebudowa silnika oświetlenia (wydajność + błędy światła).
- (opcjonalnie) **Entity Culling** – nie renderuje niewidocznych encji/BE po stronie klienta.
- (opcjonalnie) **Clumps** – łączy orbsy exp dla mniejszego laga.

**Wpływ na mapę:** to QoL/performance – nie migruje bloków, ale ważne przy uruchamianiu ciężkich map po konwersji.

---

# Checklist pod Twoją konwersję (dla tej części paczki)

1. **Wybierz docelowy loader**: w praktyce „Forge 1.18.2” (większość ww. modów).
2. **Dobierz „rdzeń funkcji”**:
   - Big Reactors → Extreme Reactors
   - Blood Magic → Blood Magic
   - ComputerCraft → CC: Tweaked
   - EnderStorage → Ender Storage + CodeChickenLib
   - Chisel → Chipped + Rechiseled
   - Carpenter’s → FramedBlocks
   - BuildCraft → Pipez + RFTools Builder (+ Integrated Dynamics / XNet)
   - Extra Utilities → Extra Utilities Reborn (+ Torchmaster/Angel Block/Cursed Earth jeśli potrzebne)
3. **Zidentyfikuj w świecie „krytyczne bloki”** (zwłaszcza: BuildCraft, BiblioCraft, CustomNPCs, ExtraUtilities) — to one decydują o tym, ile pracy będzie przy remap/rekonstrukcji.

Jeśli chcesz, w następnym kroku mogę dopisać do tego pliku **„priorytet migracji bloków”**: lista bloków/BE z 1.7.10, które typowo psują się w konwersji i jak je „zabezpieczyć” przed przeniesieniem (eksport, wymiana na placeholdery, itp.).
