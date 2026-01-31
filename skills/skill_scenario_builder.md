# SKILL: Projektowanie i weryfikacja maszyn/pipelinów/systemów do wstawienia do Minecrafta (vanilla + mody)

Ten skill ma prowadzić agenta tak, żeby **nie halucynował** zachowania gry, tylko:
- najpierw **pozyskał źródła** (dla fizyki Minecrafta i/lub konkretnych modów),
- zaprojektował układ w sposób **debugowalny**,
- wygenerował artefakty (np. `voxel_grid.json`) **budowalne i spójne**,
- **zweryfikował** działanie (symulacja + testy + kontrolne scenariusze) zanim uzna „jest OK”.

> Docelowy rezultat: układ, który można bezpiecznie wstawić na mapę (schematic/structure) i który zachowuje się zgodnie ze specyfikacją w konkretnej wersji gry/modów.

---

## 0) Zasady nadrzędne (anty-halucynacje)

1) **Wersja jest prawem.** Zawsze pracuj z jawnie podaną wersją:  
   - Minecraft (np. Java 1.7.10 / 1.12.2 / 1.20.x),  
   - Forge/Fabric,  
   - lista modów + ich wersje,  
   - konfiguracje modów, jeśli wpływają na mechanikę.

2) **Nie zgaduj fizyki.** Każde twierdzenie o mechanice (redstone, ticki, kolejność update’ów, zachowanie tile entity) musi mieć źródło albo test.

3) **Jeśli nie jesteś pewny → research + test.**  
   - Research: dokumentacja, wiki, kod źródłowy, issue tracker, changelog.  
   - Test: minimalna mapa testowa + powtarzalny scenariusz.

4) **Oddziel specyfikację od implementacji.**  
   - Spec mówi *co* ma się dziać i *jak to sprawdzimy*.  
   - Voxel/schematic mówi *jak to budujemy*.  
   - Debugger/symulator ma *weryfikować*, a nie „odgrywać”.

5) **Nie nazywaj czegoś “zgodne 1:1”, jeśli nie masz podstaw.**  
   Jeśli nie implementujesz update order / scheduled ticks / poziomów sygnału itd., nazwij to uczciwie:  
   - „scenario runner”, „high-level simulator”, „partial validator”.

---

## 1) Definicje (żeby wszyscy mówili tym samym językiem)

- **Specyfikacja**: opis oczekiwanego zachowania + interfejsy (wejścia/wyjścia) + kryteria akceptacji.
- **Artefakt świata**: struktura do wstawienia (schematic/structure). W tej pracy często: `voxel_grid.json`.
- **Budowalność**: czy w grze da się postawić te bloki w tych miejscach (podparcie redstone, attach torch, kolizje, prawa fizyki).
- **Deterministyczność**: czy układ działa powtarzalnie w danej wersji i konfiguracji (update order!).
- **Debugowalność**: czy da się łatwo diagnozować stany (punkty pomiarowe, logi, wskaźniki, testy regresyjne).

---

## 2) Workflow end-to-end (obowiązkowy)

### Krok A: Ustal “target environment”
1) Minecraft version: `x.y.z`
2) Loader: Forge/Fabric + wersja
3) Mody: lista + wersje + config (jeśli dostępny)
4) Cel: “to ma być…” (np. minutnik 0–9, fabryka stali, sorter lootów, system logistyki)

**Output:** `ENV.md` (lub sekcja w spec).

---

### Krok B: Research (zanim cokolwiek narysujesz)
#### B1. Vanilla (redstone / mechanika świata)
Źródła preferowane:
- oficjalne wiki + techniczne wiki (opis mechanik),
- dekompilacja kodu docelowej wersji (dla 1.7.10 i innych starych – to jest często “source of truth”),
- materiały techniczne (wideo/posty) jako uzupełnienie i przypadki testowe.

#### B2. Mody (tile entities, energia, item/fluid)
Źródła preferowane (w tej kolejności):
1) **Repozytorium mod-a / kod źródłowy** (GitHub/GitLab) i tag danej wersji.
2) **Dokumentacja autora** / wiki mod-a (jeśli utrzymywana).
3) **Issue tracker** (bugi, edge-case’y, różnice wersji).
4) **Changelog** (zmiany w zachowaniu bloków/maszyn).
5) Społeczność (reddit/discord) tylko jako „wskazówka”, którą weryfikujesz testem.

**Zasada:** jeśli coś wpływa na wynik (np. kolejność ticków maszyn, throughput rur, zużycie RF/EU), znajdź to w źródle lub przetestuj.

**Output:** `SOURCES.md` + notatki “reguły implementacyjne”.

---

### Krok C: Specyfikacja układu (behaviour-first)
Spec musi zawierać:
1) **Interfejs**: wejścia/wyjścia (item/fluid/energia/redstone/sygnały sieci)
2) **Stan**: co jest stanem wewnętrznym (np. “1 item krąży w ring counterze”)
3) **Czas**: tick-rate, opóźnienia, throughput, minimalny czas impulsu
4) **Warunki brzegowe**: chunk unload, lag, overflow buforów, brak energii
5) **Kryteria akceptacji** (testowalne!):
   - sekwencja, czas, brak przeskoków, brak utraty itemów,
   - deterministyczność w N powtórzeniach,
   - odporność na restart.

**Output:** `SPEC.md` lub `circuit_design.json`/`machine_design.json` (jeśli masz format).

---

### Krok D: Projekt implementacji (świat / bloki / tile entities)
Dla implementacji:
- wybierz topologię minimalizującą “edge-case’y” (np. w redstone: stabilny clock zamiast “pętli, która może się ustabilizować”),
- unikaj konstrukcji zależnych od “przypadkowego update order” jeśli celem jest niezawodność,
- zaplanuj **punkty pomiarowe** (probes): lampy, comparatory, debug command blocki, „porty testowe”.

**Output:** plan warstw (y-level), mapowanie komponentów na współrzędne.

---

### Krok E: Generacja `voxel_grid.json` (lub innego artefaktu)
**Zasady jakości dla voxel grid:**
1) **Zero kolizji współrzędnych**: żadnych duplikatów `(x,y,z)`.
2) **Zero “śmieciowych wpisów”** w `voxels` (tylko obiekty, bez komentarzy-stringów).
3) **Budowalność**:
   - redstone dust/repeater/comparator zawsze na pełnym bloku,
   - torch/lever mają poprawne attach,
   - tile entities mają kompletne dane (jeśli wymagane).
4) **Semantyka `properties`** opisana i spójna (np. co znaczy `facing`).
5) **Sekcje** w JSON: logicznie grupujące (clock, transport, storage, power, I/O).

**Output:** `voxel_grid.json` + `MANIFEST.md` (krótki opis co jest gdzie).

---

### Krok F: Walidacja statyczna (bez uruchamiania symulacji)
Zrób automatyczny walidator, który:
- wykrywa duplikaty,
- sprawdza podparcie redstone,
- sprawdza reguły attach (torch/lever),
- wykrywa przerwane sieci (np. bus zasilania),
- sprawdza spójność: spec ↔ voxel (np. “mamy 10 wyjść digit_0..9”).

**Output:** raport `lint_report.txt` + brak błędów krytycznych.

---

### Krok G: Symulacja / Debugger (weryfikacja zachowania)
**Minimalna definicja debuggera** (dla układów w świecie):
- bierze voxel grid,
- buduje graf sąsiedztwa i stan świata,
- symuluje sygnały/transfer w czasie (ticki),
- generuje trace i wykrywa odstępstwa od spec.

#### G1. Jeżeli symulujesz redstone:
Musisz (minimum) wspierać:
- poziomy sygnału 0–15,
- propagację po dust (spadek),
- repeater delay w redstone tickach (1–4),
- comparator (tryby, wejścia),
- torch inverter,
- scheduled ticks / kolejka update’ów (choćby minimalnie),
- edge-trigger dla dropper/dispenser/command block (jeśli używasz).

Jeśli tego nie robisz, nie nazywaj tego “redstone accurate”.

#### G2. Jeżeli symulujesz mody:
- użyj źródeł mod-a (kod/issue) do modelu maszyn,
- dodaj parametry konfiguracyjne (np. throughput, EU/RF, internal buffers),
- przewidź “stall” (brak energii, pełny output, blokada rury).

**Output:** `trace.csv` (tick → stany), `assertions.json` (checki), raport.

---

### Krok H: Test w grze (smoke test + regression)
Nawet najlepszy symulator może nie złapać wszystkiego. Dlatego:
- budujesz minimalną mapę testową bazując na udostępnionych szablonach mapy,
- wklejasz schematic, ale uwaga - wstawiony schematic ma być w obszarze który jest kwadratem o wymiarach 250x250 z środkiem w spawnie danej mapy, nie może wystawać poza ten obszar,
- uruchamiasz scenariusze testowe.

**Zestaw minimalny:**
1) test podstawowy (czy działa)
2) test długotrwały (np. 10–30 minut)
3) test restart (wyjście do menu / reload świata)
4) test chunk unload/reload (jeśli dotyczy)
5) test lag (jeśli masz narzędzia)

**Output:** `GAME_TEST_NOTES.md` + wynik pass/fail.

---

### Krok I: Kryteria “gotowe do wstawienia na mapę”
Układ jest „spoko” dopiero gdy:
- spełnia spec + akceptację,
- voxel grid przechodzi walidator,
- trace z symulacji nie ma anomalii,
- smoke test w grze OK.

---

## 3) “Źródła obowiązkowe” — szablon polityki research

W każdym projekcie utrzymuj listę źródeł i przypisz je do elementów:

### Vanilla (redstone / ticki / mechanika)
- wiki mechanik redstone,
- wiki komponentów (dust, repeater, comparator, torch, dropper),
- blok update / scheduled ticks,
- **dla starych wersji**: dekompilacja klasy redstone w tej wersji (1.7.10: wire/repeater/comparator/torch/dropper, World tick queue).

### Mody (maszyny/pipeline)
- repo + tag wersji,
- changelog,
- issue tracker,
- oficjalne wiki/dokumentacja.

**Reguła jakości:** “jeden ważny fakt = jedno źródło albo jeden test”.

---

## 4) Projektowanie “debugowalnych” maszyn/pipelinów (praktyczne wzorce)

1) **Porty diagnostyczne**:  
   - lampy/WSKAŹNIKI dla stanów krytycznych (energia OK, buffer full, stuck),
   - „probe points” dla sygnałów (np. comparator output).

2) **Bufory i separacja etapów**:  
   - oddziel przetwarzanie od transportu (chest/buffer),
   - ułatwia debug: widać, gdzie utknęło.

3) **Deterministyczne zegary i wyzwalanie** (dla redstone):
   - preferuj konstrukcje znane jako stabilne w danej wersji,
   - unikaj konstrukcji “na szczęście”.

4) **Fail-safe**:
   - overflow route (np. void chest) w testach,
   - ograniczniki throughput,
   - watchdog (np. “jeśli brak postępu przez X sekund → alarm”).

5) **Idempotentne kroki**:
   - tak projektuj, żeby powtórzenie kroku nie psuło stanu (ważne przy lag/reload).

---

## 5) Checklista dla agenta (przed “gotowe”)

### 5.1 Checklista źródeł
- [ ] Mam wersje MC/Forge/modów/config.
- [ ] Mam źródła dla każdego kluczowego elementu (vanilla/mod).
- [ ] Mam notatki z regułami (ticki, edge cases).
- [ ] Mam co najmniej 3 testy potwierdzające krytyczne założenia.

### 5.2 Checklista voxel grid
- [ ] brak duplikatów `(x,y,z)`
- [ ] redstone na pełnym bloku
- [ ] torch/lever attach poprawny
- [ ] tile entities mają wymagane dane
- [ ] sekcje i etykiety `purpose` są tylko opisowe
- [ ] routing w spec ≈ routing w voxel

### 5.3 Checklista symulacji
- [ ] symulacja wynika z geometrii, nie z “if purpose contains”
- [ ] mam trace tick-by-tick
- [ ] mam asercje zgodne ze spec
- [ ] wyniki są powtarzalne

### 5.4 Checklista gry
- [ ] działa w świecie docelowym
- [ ] restart/reload nie psuje stanu
- [ ] chunk unload/reload (jeśli dotyczy) OK
- [ ] brak utraty itemów/duplikacji

---

## 6) Szablony (których używamy w każdym projekcie)

### 6.1 SPEC (minimal)
- Cel:
- Wersje:
- Wejścia/wyjścia:
- Warunki:
- Akceptacja:
- Test plan:

### 6.2 SOURCES
Tabela: komponent → link/kod/test → reguły.

### 6.3 TRACE
CSV: tick, sygnały, stany buforów, throughput.

### 6.4 CHANGELOG
Co zmieniono i dlaczego (dla późniejszego utrzymania).

---

## 7) Jak reagować na niepewność (procedura)
Jeśli natrafiasz na element, którego nie jesteś pewien (np. “czy w tej wersji dropper działa na 1‑tick impuls?”):
1) oznacz to jako **open assumption**,
2) zrób research (źródło lub kod),
3) zrób test w grze (minimum setup),
4) dopiero potem implementuj w voxel/debugger.

---

---

## 9) Gdy brakuje źródeł o zachowaniu elementu moda: procedura “evidence by screenshots”

Czasem nie da się znaleźć wiarygodnego źródła (dokumentacji/kodu/changelogu/issue) opisującego **dokładnie** zachowanie konkretnego bloku/maszyny z moda (zwłaszcza w starszych wersjach lub w prywatnych forkach paczek). W takim przypadku **nie wolno zgadywać**.

### 9.1 Zasada
Jeśli po rozsądnym researchu (repo + wiki + issue + changelog) nadal nie masz pewności co do kluczowej reguły działania:
- throughput,
- tick rate,
- warunki aktywacji (np. redstone control, side config),
- zachowanie buforów,
- priorytety wejść/wyjść,
- zachowanie w edge-case (full output, brak energii),

to **proponujesz użytkownikowi** zebranie dowodów w grze: **małe, kontrolowane przykłady + screeny**.

### 9.2 Jak poprosić użytkownika (szablon)
Poproś o:
1) **Wersje**: MC + loader + mod + dodatki + config (jeśli dostępne).  
2) **3–6 mini-setupów** w świecie (każdy jak najmniejszy, tylko to co potrzebne).  
3) Dla każdego setupu:
   - screenshot z góry (layout),
   - screenshot z boku (połączenia),
   - screenshot GUI maszyny (ustawienia stron, redstone mode, filters),
   - screenshot/log z wynikiem po określonym czasie (np. po 60 s),
   - jeśli to ważne: screenshot licznika ticków / zegara / wskaźników energii.

**Zasada “jedna hipoteza = jeden setup”**:  
Jeśli nie wiesz, czy maszyna działa co 1 tick czy co 20 ticków, zrób setup specjalnie pod to.

### 9.3 Minimalne scenariusze testowe do poproszenia (checklista)
Wybierz z listy te, które pasują do elementu:

- **Throughput test**: wejście stałe (np. hopper/chest), wyjście do dużego bufora, mierz ilość po 60 s.
- **Redstone control test**: tryby (ignored/low/high/pulse) i reakcja na 1‑tick impuls.
- **Side config test**: różne strony jako input/output, czy rotacja ma znaczenie.
- **Energy stall test**: brak energii → co się dzieje z inputem/buforem.
- **Full output test**: zablokowany output → czy maszyna przestaje pobierać, buforuje, czy duplikuje/gubi.
- **Chunk boundary/unload test** (jeśli pipeline jest duży): co po przejściu daleko i powrocie.
- **Restart test**: exit to menu/reload świata.

### 9.4 Jak agent ma analizować screeny
Po otrzymaniu screenów:
1) Spisz obserwacje jako **fakty** (co widać) i osobno **wnioski** (interpretacja).
2) Zbuduj tabelę: *setup → hipoteza → wynik → implikacja dla symulatora/voxel grid*.
3) Jeśli wynik jest niejednoznaczny: poproś o **jeden dodatkowy setup** eliminujący alternatywne wyjaśnienia.

### 9.5 Jak włączyć to do projektu
- Dodaj do `SOURCES.md` sekcję **“Empirical evidence”** z linkiem do screenów i opisem testu.
- Dodaj do testów regresyjnych debuggera przypadki odzwierciedlające zaobserwowane zachowanie.
- Oznacz w dokumentacji: “model oparty o obserwacje w grze (screenshots), brak źródła upstream”.

**Cel:** nawet bez oficjalnego źródła, masz **udokumentowaną podstawę** do implementacji i możesz uczciwie powiedzieć, na czym opierasz model.




## 8) Definicja sukcesu tego skilla
Agent jest skuteczny, jeśli:
- regularnie pozyskuje źródła zamiast zgadywać,
- potrafi wytworzyć artefakt “do wstawienia na mapę” bez błędów budowalności,
- ma proces walidacji: lint → symulacja → gra,
- potrafi powiedzieć “nie wiem jeszcze, muszę sprawdzić X w źródłach/testach” i to robi.

