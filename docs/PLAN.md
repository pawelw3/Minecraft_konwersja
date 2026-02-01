# **Plan profesjonalnej konwersji mapy Minecraft 1.7.10 → 1.18.2 (Forge)**

## **Milestones, backlog konwersji, scenariusze testowe i kryteria akceptacji**

Ten plan jest celowo “inżynierski”: kładzie nacisk na **bezpieczeństwo danych**, kontrolę regresji, powtarzalne testy oraz etapowe wdrażanie konwersji per-mod/per-funkcjonalność.

---

## **1\. Cel projektu (co znaczy “udana konwersja”)**

### **1.1 Minimalne kryteria sukcesu (MUST)**

1) Świat 1.18.2 wczytuje się **bez crashy** i bez masowych błędów chunków.  
2) Wszystkie “krytyczne” obszary (bazy, linie kolejowe, hale maszyn) są:  
   - zachowane geometrycznie (bryła, układ),  
   - oraz pozbawione “dziur” po missing blokach.  
3) Zawartości kontenerów/maszyn (inventory) z 1.7.10 **nie giną**  
4) Działa **rdzeń tech** w 1.18.2:  
   - AE2: storage \+ podstawowy autocraft,  
   - Mekanism/Thermal: processing \+ energia,  
   - logistyka (Pipez/XNet/AE2 I/O),  
   - ProjectRed: podstawowe okablowanie \+ bramki,  
   - Create (kolej) jako docelowy system transportu, jeśli Railcraft/Traincraft nie mają portu 1:1.

   ### **1.2 Kryteria sukcesu (SHOULD)**

- Jak najwięcej bloków 1.7.10 mapuje się na “sensowne odpowiedniki”, a nie placeholder \- minimum 99%  
- Najważniejsze instalacje (ME rooms, linie processing, sterownie PR) działają po odtworzeniu konfiguracji.  
- Minimalizacja prac ręcznych przez:  
  - automatyczny remap bloków,  
  - automatyczne generowanie raportów braków.

---

## **2\. Architektura procesu: 3 warstwy migracji**

### **Warstwa A — Ratunek danych (Data Rescue Layer)**

**Cel:** “nic nie ginie”, nawet gdy nie da się od razu przełożyć NBT/BE.

Mechanika \- podczas konwersji poszczególnych modów pełen zapis eventów konwersji oraz pełen raport dla całej mapy co zostało przekonwertowane \- możliwość ratunku danych w przypadku jakichs braków

### **Warstwa B — Remap bloków i BE (Block/BE Remap Layer)**

**Cel:** zachować bryły i “typy” obiektów: skrzynia→skrzynia, maszyna→maszyna, kabel→kabel.

Mechanika:

- tabela mapowań: `oldBlockId/meta/NBT signature` → `newBlockState` \+ reguły NBT.


  ### **Warstwa C — Rekonstrukcja funkcji dla testów(Functional Rebuild Layer)**

**Cel:** odtworzyć działanie z użyciem nowych modów: konfiguracja stron, filtry, kanały, sygnały, pociągi.

Mechanika:

- odtwarzanie ustawień (czasem półautomatyczne):  
  - skrypty “post-process”,  
  - checklisty dla krytycznych instalacji,  
  - testy end-to-end.

---

## **3\. Docelowy “Core Stack” 1.18.2 (konsekwentny zestaw)**

- Docelowy core stack jest opisany w docs, najbardziej szczegółowy zakres w docs\\mod\_mapping\_indepth

---

## **4\. Backlog konwersji — “Unity konwersji”**

Dla każdego moda podziel pracę na takie zadania, które będziesz robił pojedynczo \- po których zakończeniu masz zrobić obszerny [handoff.md](http://handoff.md), który będzie wystarczającym podsumowaniem i odnośnikiem do utworzonych plików, żeby po danym zadaniu można było wyczyścić kontekst i żeby kolejne zadanie agent wykonywał ze świeżym kontekstem. Po zakończeniu danego zadania proś użytkownika o to czy zgadza się na kontynuację. Nie można powracać do zmieniania poprzedniego zadania (chyba że użytkownik na to wyraźnie pozwoli), natomiast na każdym zadaniu możesz odwoływać się do kodu źródłowego moda i w feedback[.md](http://entreaty.md) sugerować że coś powinno być inaczej w związku z tym co przeanalizowałeś w kodzie źródłowym.

1. Wypisanie wszystkich bloków i tile entities dodawanych przez mod i opis tego co robią dane elementy bazując na źródłach z internetu oraz ze snippetami kodu z source code albo z dekompilowanego kodu (w zależności od tego co jest dostępne w folderze mod\_src)  
2. Przygotowanie kilku symulacji działania funkcjonalności moda które nie są trywialne np jakieś elementy maszyn \- w folderze w src z nazwą tego moda \- symulacje mają bazować na dokładnym kodzie źródłowym danego moda. Symulacja nie ma być na mapie tylko w samym pythonie \- dana symulacja ma dotyczyć zarówno modów dla 1.7.10 jak i 1.18.2  
3. Napisanie kodu konwersji \- dla bloków i tile entities dla których działanie i metainformacje są trywialne i analogiczne dla wielu innych modów,  dla których jest prosta konwersja stwórz/wykorzystaj narzędzie w folderze w src, które ma obsługiwać przypadki ogólne między różnymi modami. Dla bardziej specyficznych konwersji dla danego moda rób skrypty w folderze w src z nazwą tego moda. Kod konwersji powinien uwzględniać przede wszystkim dynamiczne id elementów z głównej mapy, oraz dodatkowo dynamiczne id elementów z map testowych.  
4. Sprawdzenie dla stref głównej mapy (folder strefy, mapa w folderze mapa\_1710)czy kod pokrywa pełne \- bez jakichkolwiek edycji tej mapy. Sprawdzenie czy po konwersji symulacje przygotowane w punkcie 3 działałyby dla wersji 1.18.2 \- sprawdzenie zgodnie z kodem źródłowym modów na 1.18.2. Sprawdzenie czy konwertowane symulacje różnią się od symulacji 1.18.2 i analiza czy można to zostawić  
5. Wykonanie testowej mapy w 1.7.10, na której wstawione zostaną wszystkie bloki i BE danego moda, a także różne kombinacje kilku BE z różnymi metainformacjami i stanami tych BE \- na przykład BE które maja możliwość przechowywania itemów mają być wstawione z różnymi itemami w środku. W przypadku wstawiania elementów do Sections w mca wykorzystaj skill: skills/mca-sections. Następnie wykonanie kodu konwersji na tej mapie.  
6. Zrobienie testu na headless serwer z przekonwertowana mapą czy wyskakują jakieś błędy, sprawdzenie stanu mapy po jakimś czasie działania serwera i analiza jak zmienił się stan bloków i BE z konwertowanego moda po upływie jakiegoś czasu np 3 minut \- przy robieniu tych testów wykorzystaj skill: skills/autotest-on-server .

Co około 3-7 tak opracowane mody będzie wykonywany większy test integracyjny obejmujący kilka modów \+ elementy vanilla minecrafta \- tzw. milestone.

---

# **5\. Milestones: plan etapowy \+ scenariusze testowe co 5 unitów \- kolejność dowolna**

## **Milestone — Fundamenty QoL \+ kontenery \+ NBT (Unity 1–5)**

**Unity:**

1) JEI \+ Polymorph  
2) Curios  
3) Plecaki (Sophisticated/Traveler’s)  
4) Placeable Items  
5) Storage bazowy (Iron Chests \+ Sophisticated Storage)

   ### **Testy Milestone 1**

**T1.1 — “NBT round-trip: kontenery”**  
**T1.2 — “Placeable Items showroom”**  
**T1.3 — “Curios slots sanity”**

---

## **Milestone — Thermal \+ transport \+ AE2 (Unity 6–10)**

**Unity:** 6\) Thermal Series  
7\) Pipez  
8\) AE2 (ME storage \+ podstawowy autocraft)  
9\) Locks/Security (Lock\&Key/Locksmith \+ opcj. SecurityCraft)  
10\) Carry/Move BE (Carry On \+ Packing Tape)

---

## **Milestone— Mekanism \+ routing \+ ProjectRed multipart (Unity 11–15)**

**Unity:** 11\) Mekanism  
12\) XNet (lub Integrated Dynamics)  
13\) CC:Tweaked  
14\) ProjectRed \+ CB Multipart  
15\) “LogisticsPipes replacement layer” (AE2+XNet+Pipez; request/supply)

---

# **6\. Scenariusze testowe \- opis przykładowy oddający ideę, scenariusze powinny być właśnie tak bardzo szczegółowe**

## **6.1 Scenariusze Milestone 1**

### **T1.1 — NBT round-trip: kontenery**

- 20 kontenerów (iron chest / sophisticated barrel/chest / vanilla).  
- Wypełnienie: stacki, itemy z NBT, itemy modowe.  
- Weryfikacja: po restarcie 100% zgodność.

  ### **T1.2 — Placeable showroom**

- 30 “położonych” itemów (w tym z NBT).  
- Chunk unload/load \+ restart.

  ### **T1.3 — Curios sanity**

- 5 itemów w slotach Curios.  
- Restart \+ sprawdzenie efektów.

---

## **6.2 Scenariusze Milestone 2**

### **T2.1 — Mini-rafineria Thermal**

- Dynamo → Fluxduct → 2 maszyny → output do storage.  
- 15 min pracy → restart → 15 min pracy.

  ### **T2.2 — ME core \+ autocraft smoke**

- Controller/Drive/Terminal/Import/Export/Interface/Assembler.  
- 2 serie craftów \+ restart pomiędzy.

  ### **T2.3 — Security & ownership**

- 5 bloków z lockami, test dostępu, restart.

  ### **T2.4 — Move BE integrity**

- Przeniesienie: storage, maszyna Thermal, node Pipez (filtry), itd.  
- Weryfikacja NBT albo kontrolowany fallback do vault.

---

## **6.3 Scenariusze Milestone 3 (kluczowe)**

### **T3.1 — 3× ore processing pipeline (Mekanism)**

- 30 min → restart → 30 min, routing przez XNet/Pipez, output do AE2.

  ### **T3.2 — Sterownia ProjectRed (multipart)**

- Kable \+ bramki, sterowanie maszynami, restart \+ chunk unload.

  ### **T3.3 — CC dashboard**

- Monitor \+ sterowanie redstone, restart.

  ### **T3.4 — LP-style routing**

- 5 maszyn → bus → rozdział na 3 magazyny po filtrach, restart.

---

## **6.5 Scenariusze Milestone 4 (długie procesy)**

### **T5.1 — Bee production 60 min**

- 60 min ticków \+ 2 restarty; brak duplikacji produkcji.

  ### **T5.2 — Agro pipeline**

- Farma → zbiór → processing → AE2, restart.

  ### **T5.3 — Decor remap mega**

- 300×300 mozaika dekoracji, remap, brak missing.

  ### **T5.4 — Profiling gate**

- spark: top tickers, TPS porównanie.  
- 

