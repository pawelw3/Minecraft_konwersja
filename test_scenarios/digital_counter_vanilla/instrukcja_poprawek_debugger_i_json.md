# Duża instrukcja poprawek: projekt minutnika (JSON) + debugger redstone

**Adresat:** agent, który ma poprawić **`circuit_design.json`**, **`voxel_grid.json`** oraz napisać / przepisać **`debug_redstone.py`** tak, żeby:
1) JSON-y opisujące układ były spójne i jednoznaczne,
2) voxel grid był „wprost do wstawienia na mapę” (poprawna budowalność i topologia),
3) debugger przestał „udawać”, a zaczął **weryfikować** układ zgodnie z zasadami redstone dla Minecraft Java (w docelowej wersji: **1.7.10**).

> Ten dokument zakłada, że wcześniej dostałeś instrukcję budowy ring countera z dropperów. Teraz dostajesz pełniejszą listę poprawek + wymagania jakościowe i obowiązkowe źródła.

---

## 0) Pliki wejściowe i aktualny stan (co masz na stole)

Masz trzy pliki, które muszą pozostać wzajemnie zgodne:

- `circuit_design.json` – wysokopoziomowa specyfikacja architektury układu (zegar → ring counter → wyjścia).  
- `voxel_grid.json` – konkretne współrzędne bloków i ich właściwości.  
- `debug_redstone.py` – program, który ma **debugować i weryfikować** układ (nie tylko go „odtwarzać”).

W obecnym stanie:
- `circuit_design.json` deklaruje zegar „torch_inverter_repeater_loop”, ale parametry sugerują okres 20 ticków przy sumie opóźnień 9 (niespójność).  
- `voxel_grid.json` zawiera elementy, które wyglądają na „gotowe do wstawienia”, ale ma kilka problemów wersyjnych/formatowych (m.in. mieszanie 1.7.10 z notką o 1.18.2, oraz wpisy-stringi w tablicy voxel).  
- `debug_redstone.py` nie symuluje redstone z geometrii; w praktyce „odgrywa scenariusz”, a nie weryfikuje fizyki redstone.

---

## 1) Najpierw: obowiązkowe źródła (musisz się z nimi skonfrontować)

**Nie zaczynaj pisać debuggera „zgodnego z redstone”, zanim nie przejdziesz tych źródeł i nie zanotujesz kluczowych reguł.**  
Twoje zadanie: z każdego źródła wypisać *co najmniej* 5 reguł / faktów, które wprost wpływają na implementację.

### 1.1 Redstone tick / repeater delay / czas
- Redstone repeater: opóźnienie w **redstone tickach** (1 redstone tick = 2 game ticki).  
- Zegary redstone i ich typowe konstrukcje (nie każda pętla repeaterów oscyluje).

### 1.2 Dropper/dispenser: „rising edge” i opóźnienie 2 redstone ticki
- Dropper uruchamia się tylko na **zboczu narastającym** (OFF→ON), nie „ciągle gdy zasilony”.  
- Dropper ma opóźnienie aktywacji (~2 redstone ticki) i nie wyrzuca wielu itemów od stałego zasilania.

### 1.3 Comparator: tryby, wejścia, scheduled tick, słaba reakcja na 1‑tick
- Comparator ma zachowanie zależne od trybu.  
- Comparator ma znane niuanse: potrafi „nie zobaczyć” 1‑tick fluktuacji, bo sprawdza wejścia przed scheduled tick.

### 1.4 Update order / scheduled ticks / kolejka update’ów
- Repeatery/komparatory/torch/dispenser/dropper opierają się o mechanikę scheduled ticks.
- Update order jest krytyczny; bez tego nie ma „100% zgodności”.

### 1.5 Źródło prawdy dla 1.7.10
- Jeśli deklarujesz „zgodne z 1.7.10”: musisz przejrzeć (albo przynajmniej mieć notatki z) klas redstone w dekompilowanym 1.7.10:
  - redstone wire
  - repeater (diode)
  - comparator
  - torch
  - dispenser/dropper
  - mechanika scheduled ticks w World/WorldServer

> **Definicja „skonfrontowania się”:** masz notatki + testy wynikające z tych źródeł.  
> Jeśli nie umiesz zrobić testów, to nie nazywaj debuggera „zgodnym z redstone”; nazwij go „scenario runner”.

---

## 2) Poprawki w `circuit_design.json` (specyfikacja musi odpowiadać fizyce)

### 2.1 Napraw niespójność zegara
Masz jednocześnie:
- `period_ticks: 20` (1 sekunda),
- `delays: [4,4,1]`, `total_delay: 9`.

To nie jest ten sam porządek wielkości. Ustal jedno:
- albo zegar ma **okres 20 game ticków** (1s),
- albo ma okres wynikający z konstrukcji (np. 10–12 ticków).

**Wymóg:** `circuit_design.json` ma opisywać *rzeczywisty* przebieg sygnału, jaki generuje `voxel_grid.json`.

**Zadanie agenta:**
1) wybierz docelowy zegar (polecam: stabilny zegar comparatorowy albo torch + repeater, ale potwierdź go testem w grze),
2) opisz go w `specification` jako:
   - *okres w game tickach*,
   - *czas trwania impulsu* w game tickach (ważne dla droppers),
   - *czy sygnał jest impulsowy, czy przełącza stan*.

### 2.2 Ustal i zapisz semantykę „properties”
W 1.7.10 nie było blockstate JSON jak w 1.13+; schematy używają id+metadata, tile entity NBT itd.

Ponieważ używasz własnego JSON formatu, musisz spisać w `circuit_design.json` (np. w `note`):
- czy `properties.facing` ma znaczyć „kierunek wyjścia” czy „kierunek, w który blok jest *przyczepiony*” (torch/lever są zdradliwe),
- jak mapujesz `comparator.mode`, `repeater.delay`, `lever.powered` na dane schematyczne.

**Wymóg:** semantyka jest opisana raz, a potem konsekwentna w `voxel_grid.json` i w debuggerze.

---

## 3) Poprawki w `voxel_grid.json` (musi być perfekcyjny do wstawienia)

### 3.1 Usuń wszystkie wpisy-stringi z tablic `voxels`
Aktualnie w `ring_counter_10.voxels` są linie typu:
- `"=== DROPPERS (y=1) with STONE SUPPORT (y=0) ==="`

To jest OK dla człowieka, ale:
- część parserów/transpilerów do schematic może tego nie tolerować,
- debugger je pomija (bo sprawdza `isinstance(voxel, dict)`), ale to maskuje błędy.

**Zadanie:** usuń je, a komentarze przenieś do `description` lub `note`.

### 3.2 Ujednolić wersję i notki o świecie
W `voxel_grid.json` masz:
- `version: 1.7.10`,
- notkę o „Y=-64 jest dnem świata 1.18.2”.

To jest niepotrzebne i wprowadza błąd mentalny.  
**Zadanie:** usuń/zmień tę notkę na neutralną („origin is arbitrary, relative coordinates”).

### 3.3 Sprawdź budowalność: podparcie i kolizje
Masz checklistę, ale zrób to mechanicznie:
- żadnych duplikatów `(x,y,z)`,
- każdy `redstone_wire`, `repeater`, `comparator` ma pełny blok pod spodem,
- torch i lever mają poprawne „attachment rules” (w MC).

**Wymóg:** walidator (w debuggerze) musi to wykrywać, a nie tylko zakładać.

### 3.4 Dropper ring: zachowanie przy wspólnym zasilaniu (ważne!)
W teorii ring działa tak:
- 1 item w D0
- impuls zasila wszystkie droppere
- item przesuwa się D0→D1 itd.

W praktyce ważne jest:
- **czas impulsu** (czy dropper zdąży zadziałać),
- czy „wspólne zasilanie” nie powoduje niepożądanego zachowania (np. race conditions między dropperami).

**Zadanie:** wprowadź w `expected_behavior` wprost:
- minimalny czas impulsu (np. ≥4 game ticks),
- to, że liczymy przesunięcie o **dokładnie 1** per impuls.

### 3.5 Comparator output level: nie zakładaj 15
Comparator czytający kontener daje poziom 0–15 zależnie od zapełnienia, a 1 item w dropperze zwykle daje **niski poziom** (często 1).  
Jeśli command block wymaga „jakiekolwiek zasilanie”, to OK, ale debugger nie może podbijać do 15.

**Zadanie:** dopisz do `circuit_design.json`/`voxel_grid.json` notkę o spodziewanym poziomie sygnału comparatora (np. 1) i w debuggerze implementuj wzór na sygnał kontenera.

---

## 4) Poprawki w `debug_redstone.py` (największa część)

### 4.1 Zdecyduj, czym ma być program
Masz dwa sensowne tryby:

**Tryb A: Scenario runner (prosty)**
- Nie symuluje redstone z geometrii.
- Odgrywa „clock→ring→digits” i drukuje stany.
- Nazwij to uczciwie: „scenario runner”.

**Tryb B: Validator/simulator (weryfikator)**
- Buduje graf sąsiedztwa z voxel gridu.
- Propaguje moc 0–15 po dust, uwzględnia weak/strong power.
- Ma kolejkę scheduled ticks i symuluje repeater/comparator/torch/dropper.
- Weryfikuje, czy command block rzeczywiście dostaje zasilanie w świecie.

**Wymóg projektu:** skoro celem jest „debugger zgodny z redstone” i weryfikacja voxel gridu, idź w **Tryb B**.

### 4.2 Minimalny zakres symulacji, który MUSISZ zaimplementować
Dla tego konkretnego minutnika wystarczy pełna poprawność dla tych elementów:

1) **Solid block** (stone) – przewodzenie strong/weak power przez blok (na poziomie, który wystarczy dla dust).
2) **Redstone dust** – połączenia (zależne od sąsiadów), spadek mocy, zasilanie sąsiadów.
3) **Repeater** – opóźnienie (1–4 redstone ticks), reset/wzmacnianie, lock (możesz odłożyć lock jeśli nie używasz).
4) **Redstone torch** – inwerter + scheduled tick (torch burnout można pominąć).
5) **Comparator** – reading container, tryb compare/subtract, scheduled tick niuanse.
6) **Dropper** – aktywacja na rising edge + opóźnienie + transfer itemu do przodu (w tej topologii).
7) **Command block** – wykonanie komendy na rising edge (impulse behaviour).

**UWAGA:** jeżeli implementujesz tylko „bool powered”, to nadal nie będzie zgodne. Potrzebujesz mocy 0–15 i choć uproszczonego modelu weak/strong.

### 4.3 Model czasu i kolejki update’ów
**Nie wolno** robić `clock = tick%20<2` i udawać, że to jest repeater.  
Musisz mieć:
- `game_tick` (20/s),
- `scheduled_ticks`: kolejka eventów „za N ticków” dla bloków,
- zasady kiedy blok schedule’uje tick (np. przy zmianie sąsiada / przy zmianie zasilania).

Wersja minimalna:
- gdy wejście repeatera zmienia się OFF→ON, schedule wyjście po `delay*2` game ticks,
- analogicznie comparator,
- torch schedule’uje zmianę po 2 ticks (zależnie od wersji) – w praktyce musisz potwierdzić w źródłach/teście.

### 4.4 Walidator budowalności i spójności
Debugger ma od razu na starcie wypisać błędy:
- redstone bez podparcia,
- torch/lever bez poprawnego attach,
- powtarzające się współrzędne,
- brakujące elementy w krytycznych miejscach (np. przerwana linia bus),
- niespójność `signal_routing.paths.via` vs realne voxele.

### 4.5 Odejście od „purpose-driven truth”
Nie wolno ustawiać stanu bloków przez `if "clock" in purpose`.  
`purpose` jest tylko etykietą dla raportu.

Stan wynika WYŁĄCZNIE z:
- geometrii (sąsiedztwo),
- zasad redstone,
- scheduled ticks.

### 4.6 Testy regresyjne (obowiązkowe)
Dodaj katalog testów (nawet jako JSON/fixtures), minimum:

1) Dust line 15 bloków – spadek mocy (15→0).
2) Repeater delay 1,2,3,4 – poprawny czas w game tickach.
3) Dropper rising edge – trzymając stały sygnał nie wyrzuca wielokrotnie.
4) Comparator „1-tick pulse” – zgodność z niuansem (jeśli implementujesz scheduled tick).
5) Ring counter 10 kroków – zawsze dokładnie 1 przesunięcie per impuls.
6) Walidator: wykrywa wire bez podparcia.

**Definition of Done:** testy przechodzą, a symulator potrafi wykryć przynajmniej 3 klasy błędów w voxel grid.

---

## 5) Uzgodnienie: co jest „poprawnym zachowaniem” minutnika

### 5.1 Sekwencja wyjść
Po włączeniu:
- co ~1s zmienia się aktywny digit,
- output: 0,1,2,3,4,5,6,7,8,9,0,1…

### 5.2 Czas trwania impulsu
Zegar musi dawać impuls co ~20 game ticków, ale:
- impuls powinien być na tyle długi, żeby dropper wykonał akcję (sprawdź w źródłach),
- jednocześnie nie może generować podwójnych zboczy.

### 5.3 Brak „przeskoków”
W ring counterze NIE MOŻE:
- zgubić itemu,
- zrobić dwóch przesunięć na jeden impuls,
- przeskoczyć pozycji.

Jeśli układ w prawdziwym MC ma edge-case (np. przez update order), to:
- albo zmieniasz konstrukcję (dodajesz bufor/opóźnienia),
- albo w debuggerze to wykrywasz i oznaczasz jako „niepewne w tej topologii”.

---

## 6) Co konkretnie masz poprawić w tym wszystkim (task list)

### 6.1 JSON-y
1) `voxel_grid.json`: usuń stringi z `voxels`, ujednolić notki, doprecyzować semantykę `properties`.
2) `circuit_design.json`: dopasuj parametry zegara do realnej konstrukcji, dopisz semantykę properties i spodziewany poziom comparatora.

### 6.2 Debugger
1) Zmień opis/nagłówek: **nie wolno twierdzić “dokładne zachowanie”** bez implementacji update order i scheduled ticks.
2) Zbuduj model świata (mapa bloków + funkcje sąsiedztwa).
3) Zaimplementuj power propagation (0–15) dla dust i przez bloki (minimalnie to, co potrzebne do tego układu).
4) Dodaj scheduled tick queue i model repeater/comparator/torch/dropper.
5) Dodaj walidator budowalności.
6) Dodaj testy regresyjne + raport zgodności.

---

## 7) Format raportu (żeby to było użyteczne)
Debugger powinien umieć wygenerować:
- listę błędów budowalności,
- wykres/trace: w którym ticku zmienił się clock, kiedy dropper eject, kiedy comparator zmienił stan,
- wykrycie niezgodności z `expected_behavior` (np. brakuje „7” w sekwencji).

---

## 8) Źródła (wklejone jako lista linków – do użytku w pracy)
> Linki są w bloku kodu, żeby nie mieszać z opisem.

```text
Redstone Repeater (delay, redstone tick=2 game ticks):
https://minecraft.fandom.com/wiki/Redstone_Repeater

Dropper (rising edge, 2 redstone ticks, no continuous ejection):
https://minecraft.fandom.com/wiki/Dropper

Redstone Comparator (scheduled tick nuance, 1-tick fluctuations):
https://minecraft.fandom.com/wiki/Redstone_Comparator

Block update (general update mechanism):
https://minecraft.fandom.com/wiki/Block_update

Redstone circuits/Clock (clock topologies):
https://minecraft.fandom.com/wiki/Redstone_circuits/Clock

Forge forum threads about updateTick/scheduleUpdate in 1.7.10 (conceptual for scheduled ticks):
https://forums.minecraftforge.net/topic/30206-1710-onneighborblockchange-not-working/
https://forums.minecraftforge.net/topic/27085-1710-block-updatetick-assistance-solved/
```

---

## 9) Akceptacja: kiedy uznamy, że „to jest naprawione”
1) JSON-y są spójne: zegar, ring, routing, expected behavior.
2) `voxel_grid.json` jest czysty (brak stringów w voxels), walidator nie zgłasza błędów.
3) Debugger potrafi:
   - wykryć minimum 3 kategorie błędów budowalności,
   - zasymulować ring counter na podstawie geometrii (a nie `purpose`),
   - odtworzyć sekwencję 0–9 w czasie ~10s (z tolerancją na „~” jeśli zegar nie jest idealnie 20 ticków, ale jest stabilny).
4) Dokumentacja debuggera uczciwie mówi, jaki poziom zgodności jest zaimplementowany (wersja MC, zakres komponentów, znane ograniczenia).
