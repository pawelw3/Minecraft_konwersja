# Redstone Circuit Debugger

Narzędzie CLI do debugowania układów redstone w Minecraft. Symuluje dokładne zachowanie redstone z wersji 1.7.10.

## Architektura (NOWA - Dropper Ring Counter)

Ten debugger obsługuje nową architekturę:
- **Zegar 1Hz** (Torch Inverter + Repeater Delay Loop)
- **Dropper Ring Counter** (10 dropperów, 1 item krążący)
- **Komparatory** (10 sztuk, czytają obecność itemu)
- **Command Blocks** (10 sztuk, `/say 0-9`)

### Dlaczego Dropper Ring Counter?

**Stara architektura (4-bit + BCD):**
- Wymagała skomplikowanego dekodera BCD
- Problem z resetem mod-10
- Trudna w debugowaniu

**Nowa architektura (Dropper Ring):**
- Naturalna pętla 0-9 bez dekodera
- Prostsza konstrukcja
- Łatwiejsza do zdebugowania
- Każdy stan widoczny fizycznie (który dropper ma item)

## Wymagania

- Python 3.8+
- Plik `schematics/voxel_grid.json` z definicją układu
- Wszystkie bloki dostępne w Minecraft 1.7.10:
  - Dropper (od 1.5.2) ✅
  - Comparator (od 1.5) ✅
  - Command Block (od 1.4) ✅
  - Repeater, Redstone Torch, Stone ✅

## Użycie

### Podstawowe

```bash
python debug_redstone.py
```

Domyślnie uruchamia symulację na 12 sekund z pomiarami co 0.2s.

### Opcje

```bash
# Skrócona symulacja (5 sekund)
python debug_redstone.py -t 5

# Pełny cykl 0-9 (11 sekund wystarczy)
python debug_redstone.py -t 11

# Częstsze pomiary (co 0.1s)
python debug_redstone.py -i 0.1

# Zapisanie historii do pliku JSON
python debug_redstone.py -o historia.json

# Reprodukowalność - to samo ziarno = te same punkty pomiarowe
python debug_redstone.py -s 12345
```

## Wyjście

### Główny status

```
+--------------------------------------------------------------------+
| Tick    0 |  0.00s | Zegar: [PULS]                            |
+--------------------------------------------------------------------+
| Dropper z itemem: D1 | Cyfra: 1                                  |
| Output:  [CHAT] [Server] 1 <<< NOWA CYFRA!                        |
+--------------------------------------------------------------------+
```

Pokazuje:
- Numer ticku i czas symulacji
- Stan zegara ([PULS] lub [----])
- Który dropper ma item (D0-D9)
- Aktualna cyfra (0-9)
- Wyjście command blocka (symuluje log Minecrafta)

### Tabela punktów pomiarowych

```
[PROBE TABLE] PUNKTY POMIAROWE (20 losowych punktow ukladu):
+------+---------+------------------------------+
| Punkt|  Stan   | Opis                         |
+------+---------+------------------------------+
| P01 | [OFF]  | D3_support                   |
| P02 | [ON]   | D1                           |
| P03 | [OFF]  | C5_reads_D5                  |
| P04 | [OFF]  | cmd_digit_2                  |
...
```

Pokazuje stan (ON/OFF) 20 losowych punktów w układzie:
- Droppery (D0-D9)
- Komparatory (C0-C9)
- Command blocks (cmd_digit_*)
- Magistrala zasilania (bus)
- Elementy zegara

### Statystyki końcowe

```
[STATS] STATYSTYKI SYMULACJI:
--------------------------------------------------
Aktywacje command blockow:
  /say 0: 2 tickow (100ms)
  /say 1: 2 tickow (100ms)
  ...

Rozklad czasowy cyfr:
  Cyfra 0:  38 tickow ( 10.0%) ##
  Cyfra 1:  38 tickow ( 10.0%) ##
  ...
```

## Jak to działa

### Symulacja zegara (Torch-Repeater Loop)

```python
# Okres 20 ticków = 1 sekunda
# Impuls trwa 2 ticki
position_in_cycle = game_tick % 20
clock_output = position_in_cycle < 2
```

Zegar generuje:
- **Puls** (ON) przez 2 ticki (0.1s)
- **Oczekiwanie** (OFF) przez 18 ticków (0.9s)
- Powtarza co 20 ticków (1 sekunda)

### Symulacja Dropper Ring Counter

```python
class DropperRingCounter:
    def tick(self, clock_pulse: bool) -> int:
        if clock_pulse:
            # Znajdź dropper z itemem
            current_pos = self.dropper_states.index(True)
            # Przesuń do następnego (modulo 10)
            next_pos = (current_pos + 1) % 10
            self.dropper_states[current_pos] = False
            self.dropper_states[next_pos] = True
        return self.get_active_digit()
```

**Stan początkowy:** 1 cobblestone w D0
**Cykl:** D0 → D1 → D2 → ... → D9 → D0 (zapętlenie)

### Symulacja komparatorów

Komparator daje sygnał wyjściowy (ON) gdy:
- Dropper, który czyta, ma item (True w `dropper_states`)

```python
comparator_active = (dropper_with_item == comparator_number)
```

### Symulacja command blocków

Command block wykonuje komendę gdy:
- Komparator, do którego jest podłączony, jest aktywny
- Aktywacja trwa przez krótki czas (2 ticki)

```python
if new_digit != prev_digit:
    command_triggered = new_digit  # Wykonaj /say X
else:
    if game_tick % 20 >= 2:
        command_triggered = -1  # Przestań
```

## Zasady redstone w symulacji

| Element | Zachowanie |
|---------|-----------|
| **Game tick** | 0.05s (20 TPS) |
| **Redstone tick** | 2 game ticki (0.1s) |
| **Dropper** | Wyrzuca item przy zboczu narastającym zasilania |
| **Comparator** | Daje sygnał gdy czyta kontener z itemem |
| **Repeater** | Opóźnienie 1-4 ticków redstone |
| **Torch inverter** | NOT gate - odwraca sygnał |

## Pliki wyjściowe

### historia.json

Zapisuje pełną historię stanów:

```json
[
  {
    "tick": 0,
    "time": 0.0,
    "clock": true,
    "digit": 1,
    "dropper_states": [false, true, false, false, false, false, false, false, false, false],
    "triggered": 1,
    "probes": [["P01", false, "D3_support"], ...]
  },
  ...
]
```

## Debugowanie

### Sprawdź czy zegar działa poprawnie

```bash
python debug_redstone.py -t 5 -i 0.05 | findstr "Zegar"
```

Oczekiwane: `[PULS]` co ~20 linii (1 sekunda)

### Sprawdź sekwencję cyfr

```bash
python debug_redstone.py -t 12 | findstr "CHAT"
```

Oczekiwane: 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 0, 1...

### Sprawdź rotację itemu między dropperami

```bash
python debug_redstone.py -t 5 | findstr "Dropper z itemem"
```

Oczekiwane: D0, D1, D2, D3... (zmiana co 1 sekundę)

### Zapisz i przeanalizuj

```bash
python debug_redstone.py -t 12 -o debug.json
# Analiza w Pythonie:
# python -c "import json; d=json.load(open('debug.json')); print([s['digit'] for s in d[:100]])"
```

## Porównanie z Minecraft

| Aspekt | Symulator | Prawdziwy Minecraft |
|--------|-----------|---------------------|
| Tick rate | 20 TPS | 20 TPS |
| Dropper delay | Idealny | Może mieć losowe opóźnienie |
| Comparator | Binarny (0/1) | Analogowy (0-15), tu uproszczony |
| Probkowanie | Co 0.2s (konfigurowalne) | Ciągłe |
| Command blocks | Symulowane | Prawdziwe logi |
| Redstone quirks | Podstawowe | Wszystkie bugi MC |

## Ograniczenia

1. **Simplified comparator** - Symuluje tylko detekcję obecności itemu (0/1), nie siłę sygnału (0-15)
2. **No hopper logic** - Droppery wyrzucają bezpośrednio do następnego (bez sprawdzania czy mieści się item)
3. **Ideal timing** - Brak losowych opóźnień jak w prawdziwym serwerze
4. **Static probes** - Punkty pomiarowe wybierane raz na start

## Zastosowanie

- **Przed budową** - Sprawdź czy układ zadziała jak chcesz
- **Debugowanie** - Porównaj oczekiwane vs rzeczywiste stany
- **Testowanie** - Weryfikacja logiki przed wdrożeniem na serwer
- **Edukacja** - Zrozumienie jak działa redstone

## Porównanie architektur

### Stara (4-bit + BCD):
```
Zegar → [Q0 Q1 Q2 Q3] → Dekoder BCD → 10 wyjść
              ↑
        Licznik 4-bit
```
- Skomplikowany dekoder BCD (bramki AND)
- Problem z resetem mod-10
- Trudny do debugowania

### Nowa (Dropper Ring):
```
Zegar → [D0→D1→...→D9] → Comparatory → 10 wyjść
              ↑
        1 item krążący
```
- Naturalna pętla 0-9
- Prosta konstrukcja
- Łatwa do debugowania (widać gdzie jest item)

---

**Pliki:**
- `debug_redstone.py` - Główny skrypt (wersja dla Dropper Ring Counter)
- `schematics/voxel_grid.json` - Definicja układu (ring counter)
- `debug_redstone_README.md` - Ta dokumentacja

**Wersja**: 2.0 (Dropper Ring Counter)  
**Kompatybilność**: Minecraft 1.7.10+
