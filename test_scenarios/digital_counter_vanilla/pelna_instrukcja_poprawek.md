# Pełna instrukcja poprawek: `circuit_design.json` + `voxel_grid.json` + `debug_redstone.py`

Cel: doprowadzić projekt do stanu **„do wstawienia na mapę”** oraz mieć debugger, który **faktycznie weryfikuje** zachowanie (albo uczciwie deklaruje ograniczenia).

Ta instrukcja jest „patch-planem”: co i gdzie zmienić, w jakiej kolejności, oraz jak sprawdzić, że jest OK.

---

## 0) Definicja „dobrze” (konkret, bez niedomówień)

Uznajemy, że wszystko jest dobrze, jeśli:

1) **Spójny timing** w całym projekcie: `circuit_design.json` ↔ `voxel_grid.json` ↔ `debug_redstone.py`.
2) `voxel_grid.json` jest:
   - budowalny (podparcia, attach, brak kolizji),
   - logicznie spójny (routing odpowiada fizyce),
   - wolny od formatowych „śmieci” (tylko obiekty w `voxels`).
3) Debugger:
   - nie „odgrywa scenariusza” ignorując geometrię,
   - potrafi wykryć błędy budowalności i błędy połączeń,
   - poprawnie liczy **zbocza** (edge) i **scheduled delays** dla elementów, które używasz,
   - generuje czytelny trace i asercje zgodne ze spec.

---

## 1) Poprawki spójności czasu (NIE DA SIĘ IŚĆ DALEJ BEZ TEGO)

### 1.1 Wybierz jedną prawdę o zegarze
Ustal jeden zestaw parametrów:

- `clock_period_game_ticks`: np. **20** (1 sekunda)
- `clock_pulse_game_ticks`: np. **4** (zalecane dla stabilnej aktywacji droppera)
- `clock_type`: impulsowy (OFF→ON→OFF) albo przełączający (toggle)

**Zalecenie:** dla ring countera na dropperach wybierz **impulsowy** zegar:
- okres 20 game ticków,
- impuls 4 game ticki.

> Jeśli koniecznie chcesz impuls 2 ticki, musisz mieć pewność (źródło/test), że w tej wersji dropper zareaguje na tak krótki impuls, albo dodać monostabilny wydłużający impuls.

### 1.2 Zmień `circuit_design.json`
W sekcji zegara ustaw wartości zgodne z decyzją z 1.1. Upewnij się, że nie ma konfliktu typu:
- `pulse_duration_game_ticks = 2`
- i jednocześnie notka „minimum 4 ticks required”.

**Wymagane pola (minimalnie):**
- `period_game_ticks`
- `pulse_duration_game_ticks`
- `signal_shape`: `"pulse"` (albo `"toggle"`)

### 1.3 Zmień `voxel_grid.json` (`expected_behavior`)
W `expected_behavior.timing` wpisz te same wartości:
- okres w game tickach,
- czas impulsu,
- oczekiwany czas na pełny cykl 0–9 (przy 20 tick: ok. 10 s).

Usuń sprzeczne opisy typu „10–12 ticków (0.5–0.6s)” jeśli nie są zgodne z 1.1.

### 1.4 Zmień `debug_redstone.py`
Zamiast hardcodu `tick%20<2`, ustaw:
- okres i impuls z config/spec (z `circuit_design.json` albo stałą konfiguracyjną).

**Minimalny patch:**
- `period = 20`
- `pulse = 4`
- `return (game_tick % period) < pulse`

To nadal nie jest „geometry-based zegar”, ale przynajmniej jest spójny i uczciwy jako „wymuszony clock”.

---

## 2) Semantyka `properties.facing` (napraw to raz, a dobrze)

Masz 3 klasy bloków, dla których `facing` bywa mylony:

1) `dropper` – zwykle `facing` oznacza kierunek, **w który wypycha item**.
2) `comparator` / `repeater` – `facing` zwykle oznacza kierunek **wyjścia** (front).
3) `redstone_torch` (wall torch) – w blockstate 1.13+ `facing` często oznacza kierunek, **w który torch „patrzy”**, czyli jest odwrotny do ściany, do której jest przyczepiony.

### 2.1 Dodaj do `circuit_design.json` sekcję „properties semantics”
Dodaj krótką, jednoznaczną notkę (np. `notes.properties_semantics`), np.:

- `facing` dla repeater/comparator/dropper = kierunek wyjścia/front,
- `facing` dla wall_torch = kierunek, w który torch wskazuje (a attach jest do bloku po przeciwnej stronie).

### 2.2 Sprawdź i popraw torch w `voxel_grid.json`
Torch ma być przyczepiony do `clock_logic_block`. Zrób jedno z dwóch:

**Opcja A (najprościej):** zamień wall torch na torch stojącą na górze bloku (jeśli topologia pozwala), bo jest mniej niejednoznaczna.

**Opcja B:** jeśli zostaje wall torch:
- sprawdź, czy `facing` jest zgodne z twoją semantyką,
- dodaj walidację w debuggerze, że torch ma solidny blok po stronie attach.

---

## 3) `voxel_grid.json`: budowalność i czystość danych

### 3.1 Walidacja współrzędnych
Wykonaj (i dodaj do debuggera, jeśli jeszcze nie ma):
- wykrywanie duplikatów `(x,y,z)`
- raport: lista kolizji z `purpose` dla obu bloków

### 3.2 Podparcie redstone
Reguły:
- `redstone_wire`, `repeater`, `comparator` muszą stać na solid block.

Dodaj w walidatorze:
- jeśli blok to dust/repeater/comparator i `below` nie jest solid → błąd krytyczny.

### 3.3 Attach torch/lever
Dodaj w walidatorze:
- torch nie może być „przyczepiony” do dust/repeater itp.
- musi mieć solidny blok w miejscu attach.

### 3.4 Master switch: decyzja projektowa
W `voxel_grid.json` masz `master_switch`. Podejmij decyzję:

- **A: switch działa** → debugger musi uwzględniać lever i odcinać zegar/bus.
- **B: zawsze-on** → usuń lever i okablowanie switcha z artefaktu, żeby nie myliło.

**Zalecenie:** A (switch działa), bo poprawia debugowalność.

---

## 4) Ring counter (dropper loop): wymagania i edge-case’y

### 4.1 Minimalny impuls dla droppera
Zaktualizuj spec (1.1–1.4): impuls ma być ≥ minimalnego wymaganego czasu (wg źródła/testu).

### 4.2 Comparator output level (nie zakładaj 15)
Comparator czytający droppera daje poziom zależny od zapełnienia (zwykle niski, np. 1).

**W `debug_redstone.py`:**
- nie ustawiaj „powered = True/False” na skróty,
- implementuj funkcję `container_signal(items, capacity)` → 0..15,
- dla testu ring countera wystarczy: 0 itemów → 0, >=1 item → 1 (upraszczając), ale to musi być opisane jako uproszczenie.

---

## 5) Debugger: pełny plan poprawek (bez halucynacji)

> Tu są 2 ścieżki. Wybierz jedną i bądź uczciwy w opisie.

### Ścieżka 1: „Partial validator” (minimum, ale uczciwie)
To jest sensowne, jeśli chcesz szybko weryfikować ten konkretny układ.

#### 5.1 Zmień nagłówek i nazwę trybu
W opisie programu usuń twierdzenia „100% zgodny”. Zastąp:
- „Partial validator for this voxel topology”
- „Clock is injected; bus is assumed contiguous and validated”

#### 5.2 Zegar: wstrzyknięty, ale spójny
Zaimplementuj spójny clock (1.4) + walidację, że `clock_out` jest fizycznie połączony z bus.

#### 5.3 Bus: waliduj łączność zamiast magicznego “purpose”
Zamiast:
- “ustaw wszystkie dropper_power_bus na clock_power”,

zrób:
- graf połączeń dusta na `y=3`,
- BFS/DFS z `clock_out`,
- ustaw power tylko dla dustów, które są w tej samej spójnej składowej.

To nadal uproszczenie (nie liczysz spadku 15→0), ale przynajmniej:
- wykrywasz przerwy w kablu,
- nie zasilasz „telepatycznie”.

#### 5.4 Dropper: rising edge + cooldown
Zaimplementuj:
- dropper reaguje tylko na OFF→ON,
- po aktywacji przenosi item do kolejnego droppera po opóźnieniu (może być stałe, np. 4 game ticks jako uproszczenie, ale opisane).

#### 5.5 Command block: edge-trigger
Impulsowy command block odpala raz na OFF→ON.
- Śledź poprzedni stan zasilania bloku,
- `if prev==0 and now>0: fire`.

#### 5.6 Raport
Wypisz:
- który digit odpalił i w jakim ticku,
- czy sekwencja 0..9 jest ciągła,
- alerty: podwójne odpalenie w jednym kroku, brak kroku, brak postępu.

---

### Ścieżka 2: „Geometry-based simulator” (docelowo poprawne)
To jest większa praca, ale tylko tak masz prawo mówić „zgodne”.

Minimalny zakres dla tego projektu:
1) Moc 0–15 (dust spadek),
2) Propagacja po dust + zasilanie bloków (weak/strong w uproszczeniu),
3) Repeatery i komparatory z scheduled ticks,
4) Torch inverter,
5) Dropper + komparator reading container,
6) Command block edge.

**Wymóg:** kolejka scheduled ticks.

---

## 6) Testy (muszą istnieć, inaczej to nie jest zweryfikowane)

Dodaj (jako testy automatyczne w Pythonie albo jako fixtures):

1) `test_no_duplicate_coordinates`
2) `test_redstone_requires_support`
3) `test_torch_attachment_is_solid`
4) `test_clock_connects_to_bus` (BFS po dust)
5) `test_ring_counter_advances_one_step_per_pulse`
6) `test_command_blocks_fire_on_edges_only`
7) `test_sequence_0_to_9_repeats`

**Definition of Done:** wszystkie przechodzą, a program generuje trace, który pokazuje 10 kroków w ~10 sekund (dla 20-tick period).

---

## 7) Kolejność prac (żeby nie kręcić w kółko)

1) Ujednolić timing (Sekcja 1) – aktualizacja 3 plików.
2) Ustalić semantykę `facing` i poprawić torch (Sekcja 2).
3) Dociągnąć voxel grid do 100% budowalności (Sekcja 3).
4) Poprawić debugger do trybu „Partial validator” (Sekcja 5 – Ścieżka 1) jako minimum.
5) Dodać testy (Sekcja 6).
6) Dopiero jeśli potrzeba: rozbudować do symulatora geometry-based (Ścieżka 2).

---

## 8) Checklist końcowy

- [ ] `circuit_design.json` i `voxel_grid.json` mówią to samo o okresie/impulsie.
- [ ] `debug_redstone.py` używa tych samych parametrów (nie ma “magicznych 2 ticków”).
- [ ] Torch/lever mają legalny attach, walidator to sprawdza.
- [ ] Bus jest zasilany tylko, jeśli jest fizycznie połączony z `clock_out`.
- [ ] Droppery przesuwają item **raz na impuls** (edge).
- [ ] Command blocki odpalają **raz na edge**, a nie „trzymając prąd”.
- [ ] Trace pokazuje pełną sekwencję 0..9, bez luk i bez podwójnych skoków.
- [ ] Testy przechodzą.

