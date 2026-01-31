# Instrukcja poprawek (v2): spójny ring‑counter 0–9 + validator zgodny z testami

Ta instrukcja doprowadza projekt do stanu, w którym:
- `circuit_design.json` **opisuje** ring counter 0–9 (a nie licznik 4‑bit + dekoder),
- `voxel_grid.json` **fizycznie zawiera** ring counter (droppery + komparatory + command blocki) i NIE miesza go z obserwerami/licznikami bitowymi,
- `debug_redstone.py` eksportuje API, którego wymagają `test_validator.py` i testy przechodzą,
- struktura plików zgadza się z tym, co testy importują i skąd czytają dane.

> Obecnie pliki są niespójne: `expected_behavior` i `signal_routing` mówią o ring counterze, ale `sections` nadal zawierają stare elementy (counter_bit*, bcd_decoder) i nawet `minecraft:observer`.

---

## 1) Najpierw: dopasuj repo do testów (ścieżki plików)

`test_validator.py` oczekuje, że voxel grid jest w:
`./schematics/voxel_grid.json`

### Zrób to:
1) Utwórz katalog `schematics/` obok `test_validator.py`.
2) Skopiuj aktualny `voxel_grid.json` do `schematics/voxel_grid.json`.
3) Utrzymuj **to** jako źródło prawdy dla testów.

---

## 2) Popraw `circuit_design.json` – usuń stary licznik i dekoder

Aktualny `circuit_design.json` ma komponenty:
- `counter_4bit`
- `bcd_decoder`
i zegar, który wychodzi na `counter_bit0_clock`.

To NIE pasuje do ring countera.

### 2.1 Zmiany wymagane
1) Usuń komponenty:
- `counter_4bit`
- `bcd_decoder`

2) Dodaj komponent ring counter:
- `ring_counter_10` (dropper_ring)

3) Przepnij połączenia:
- `clock_1hz.output` → `ring_counter_10.clock`
- `ring_counter_10.digit_0..digit_9` → `output_digits.digit_0..digit_9`

### 2.2 Zegar (spójny z testami)
Testy wymagają:
- `CLOCK_PERIOD = 20`
- `CLOCK_PULSE = 4`

Więc w `circuit_design.json` ustaw zegar jako impulsowy:
- `period_ticks: 20`
- `pulse_ticks: 4`
i usuń/zmień opis „repeater_loop 5×4” jeśli nie wynika z realnej geometrii.

**Minimalny przykładowy komponent:**
```json
{
  "id": "clock_1hz",
  "type": "clock_generator",
  "specification": {
    "period_game_ticks": 20,
    "pulse_duration_game_ticks": 4,
    "signal_shape": "pulse",
    "note": "Clock parameters match validator tests"
  },
  "outputs": ["ring_counter_clock"]
}
```

---

## 3) Popraw `voxel_grid.json` – `sections` MUSZĄ odpowiadać ring counterowi

W `voxel_grid.json`:
- `expected_behavior` i `signal_routing` opisują ring counter (D0..D9, C0..C9, CMD0..CMD9),
- ale `sections` nadal zawierają stare rzeczy (counter_bit*, bcd_decoder) oraz `minecraft:observer`.

### 3.1 Usuń stare sekcje
Usuń z `sections` w całości:
- `counter_bit0`
- `counter_bit1`
- `counter_bit2`
- `counter_bit3`
- `bcd_decoder`

(Te sekcje nie pasują do ring countera i psują „gotowość do wstawienia” w MC 1.7.10.)

### 3.2 Dodaj nową sekcję `ring_counter_10`
Dodaj sekcję o ID dokładnie `ring_counter_10` i umieść w niej wszystkie elementy:
- droppery D0..D9 (y=1),
- komparatory C0..C9 (y=1),
- command blocki CMD0..CMD9 (y=1),
- podparcia (stone y=0),
- zasilanie dropperów: stone (y=2) + redstone_wire (y=3) nad każdym dropperem (bus).

#### 3.2.1 Koordynaty dropperów (D0..D9)
| D | (x,y,z) | facing |
|---|---|---|
| D0 | (6,1,6) | east |
| D1 | (7,1,6) | east |
| D2 | (8,1,6) | east |
| D3 | (9,1,6) | south |
| D4 | (9,1,7) | south |
| D5 | (9,1,8) | west |
| D6 | (8,1,8) | west |
| D7 | (7,1,8) | west |
| D8 | (6,1,8) | north |
| D9 | (6,1,7) | north |

**Wymóg:** `facing` wskazuje dokładnie na następny dropper.

Dodaj pod każdym dropperem `minecraft:stone` na (x,0,z).

#### 3.2.2 Bus zasilania dropperów (nad dropperami)
Dla każdego droppera (x,1,z) dodaj:
- `minecraft:stone` na (x,2,z) (`purpose`: `dropper_power_block`)
- `minecraft:redstone_wire` na (x,3,z) (`purpose`: `dropper_power_bus`)

Wire na (x,3,z) muszą tworzyć jedną spójną sieć (połączenia ortogonalne zgodne z pętlą).

#### 3.2.3 Komparatory (C0..C9)
Komparator stoi obok droppera tak, by **wejście** (tył) było przy dropperze.

| C | (x,y,z) | facing (wyjście) | czyta |
|---|---|---|---|
| C0 | (6,1,5) | north | D0 |
| C1 | (7,1,5) | north | D1 |
| C2 | (8,1,5) | north | D2 |
| C3 | (10,1,6) | east | D3 |
| C4 | (10,1,7) | east | D4 |
| C5 | (10,1,8) | east | D5 |
| C6 | (8,1,9) | south | D6 |
| C7 | (7,1,9) | south | D7 |
| C8 | (5,1,8) | west | D8 |
| C9 | (5,1,7) | west | D9 |

Pod każdym komparatorem dodaj `minecraft:stone` na y=0.

#### 3.2.4 Command blocki (CMD0..CMD9)
Command block ma stać na wyjściu komparatora (w kierunku `facing`).

| CMD | (x,y,z) | komenda |
|---|---|---|
| CMD0 | (6,1,4) | `/say 0` |
| CMD1 | (7,1,4) | `/say 1` |
| CMD2 | (8,1,4) | `/say 2` |
| CMD3 | (11,1,6) | `/say 3` |
| CMD4 | (11,1,7) | `/say 4` |
| CMD5 | (11,1,8) | `/say 5` |
| CMD6 | (8,1,10) | `/say 6` |
| CMD7 | (7,1,10) | `/say 7` |
| CMD8 | (4,1,8) | `/say 8` |
| CMD9 | (4,1,7) | `/say 9` |

Pod każdym command blockiem dodaj `minecraft:stone` na y=0.

### 3.3 Zegar – zostaw lub uprość, ale utrzymaj połączenie clock→bus
W `sections.clock_generator` możesz zostawić obecną strukturę, ale musisz zagwarantować:
- istnieje **jednoznaczny punkt** `clock_out` na (6,3,2),
- `signal_routing.paths[0].via` istnieje jako realne `minecraft:redstone_wire` na tych koordynatach,
- `clock_out` jest fizycznie połączony z bus’em (np. do (6,3,6)).

Jeśli nie chcesz ryzykować “facing wall torch”:
- zmień torch na konstrukcję zegara bez wall torch **albo**
- doprecyzuj semantykę `facing` i sprawdzaj attach w walidatorze.

---

## 4) Popraw `debug_redstone.py` – musi spełniać API testów

Testy wymagają, żeby `debug_redstone.py` eksportował:
- `Position`
- `RedstoneValidator`

i żeby `RedstoneValidator` miał:
- `CLOCK_PERIOD == 20`
- `CLOCK_PULSE == 4`
- `blocks: Dict[Position, BlockLike]`
- `errors: List[str]`
- `load_from_voxel_grid(path)`
- `validate_construction()`
- `validate_clock_to_bus_connection() -> bool`
- `tick() -> dict` ze strukturą używaną w testach:
  - `state['digit']` (int 0..9)
  - `state['triggered']` (iterowalna lista/set cyfr odpalonych w tym ticku; może być pusta)

### 4.1 Najprostszy sposób: zrób „wrapper” wokół obecnego kodu
Obecny plik ma klasy `RedstoneState`, `Block`, `ProbePoint`, `RedstoneSimulator`.

Zamiast przebudowywać wszystko od zera, zrób:

1) `@dataclass(frozen=True)` Position(x,y,z) + __hash__.
2) Klasa `RedstoneValidator`, która:
   - parsuje `voxel_grid.json`,
   - buduje `blocks` (mapa Position→Block),
   - wykonuje walidacje,
   - utrzymuje stan ring countera (`current_digit`, `prev_clock_high`),
   - w `tick()` generuje clock (20/4), wykrywa rising edge i przesuwa digit o 1.

### 4.2 Wymagane zachowanie `tick()` (żeby testy przeszły)
- Zegar: `clock_high = (tick % 20) < 4`
- Rising edge: `if not prev_clock_high and clock_high: advance`
- Advance: `current_digit = (current_digit + 1) % 10`
- `triggered` w tym ticku to `[current_digit]` tylko na rising edge, inaczej `[]`.

Zwracany stan:
```python
return {
  "tick": self.game_tick,
  "digit": self.current_digit,
  "triggered": triggered_digits
}
```

To spełnia:
- test „krok +1 per impuls”
- test „odpalanie tylko na edge”
- test „w 220 ticków zobaczysz wszystkie cyfry 0..9”.

### 4.3 Walidacje wymagane przez testy
#### 4.3.1 `validate_construction()`
Ma dopisać błędy do `self.errors` w formacie zawierającym:
- `SUPPORT:` dla redstone bez podparcia
- `ATTACH:` dla torch bez solid attach

Minimalne zasady:
- jeśli blok jest `minecraft:redstone_wire` / `minecraft:comparator` / `minecraft:repeater` i poniżej (x,y-1,z) nie ma solid (`minecraft:stone` lub inny “full block”) → `SUPPORT: ...`
- jeśli blok jest `minecraft:redstone_torch`:
  - sprawdź czy ma obok solidny blok w miejscu attach (zgodnie z twoją semantyką `facing`) → inaczej `ATTACH: ...`

#### 4.3.2 `validate_clock_to_bus_connection()`
Zrób BFS po `minecraft:redstone_wire`:
- start: `clock_out` (znajdź po `purpose == "clock_out"` albo po koordynatach (6,3,2))
- cel: jakikolwiek wire z `purpose == "dropper_power_bus"` (albo konkretnie (6,3,6))
- BFS porusza się w 4 kierunkach (N/S/E/W) po tej samej warstwie y=3.

Zwróć `True/False` i jeśli False, dodaj do `errors` np. `ROUTING: clock not connected to dropper bus`.

---

## 5) Dopasuj `test_validator.py` albo utrzymaj konwencje (rekomendacja: utrzymaj)

Zalecenie: **nie ruszaj testów**. One są dobrą definicją “done” dla validatora.
Zamiast tego dostosuj:
- API w `debug_redstone.py`,
- ścieżki plików (sekcja 1),
- parametry zegara (20/4).

---

## 6) Checklista końcowa (co musi być prawdą, zanim powiesz “jest dobrze”)

- [ ] `schematics/voxel_grid.json` istnieje i zawiera sekcję `ring_counter_10` z dropperami/komparatorami/CMD.
- [ ] W `voxel_grid.json` nie ma `minecraft:observer` ani sekcji `counter_bit*` / `bcd_decoder`.
- [ ] `expected_behavior.timing` ma `clock_period_game_ticks=20` i `clock_pulse_duration_game_ticks=4`.
- [ ] `circuit_design.json` ma `ring_counter_10` i nie ma `counter_4bit` / `bcd_decoder`.
- [ ] `debug_redstone.py` eksportuje `RedstoneValidator` i `Position`.
- [ ] `RedstoneValidator.CLOCK_PERIOD == 20` i `CLOCK_PULSE == 4`.
- [ ] `python test_validator.py` przechodzi bez fail/error.

---

## 7) Minimalny “smoke test” po przejściu testów
Po konwersji voxel→schematic i wklejeniu do świata:
1) włóż 1× cobblestone do D0 (6,1,6),
2) włącz master switch,
3) obserwuj chat: `/say 0..9` co ~1 sekundę.

Jeśli gra nie jest w trybie z włączonymi command blockami, testem alternatywnym jest:
- podmiana CMD na lampy (ale to już inna spec).

