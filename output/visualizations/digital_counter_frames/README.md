# Wizualizacja Cyfrowego Licznika

## Opis
Ten folder zawiera wizualizację krok po kroku działania cyfrowego licznika 4-bitowego (scenariusz testowy `digital_counter_vanilla`).

## Struktura plików

### Główny plik do przeglądania
- **`ANIMATION_VIEWER.html`** - Interaktywna przeglądarka wszystkich klatek z możliwością odtwarzania animacji

### Klatki stanów (20 plików)
Dla każdej cyfry 0-9 są 2 klatki:
- `digit_X_hold.svg` - Stan spoczynku (bez impulsu zegara)
- `digit_X_pulse.svg` - Stan z aktywnym impulsem zegara (przejście do następnej cyfry)

### Klatki przejść (10 plików)
- `transition_X_to_Y.svg` - Schematyczne pokazanie które bity się zmieniają między cyframi

### Podsumowanie
- `00_CYCLE_SUMMARY.svg` - Pełny cykl licznika na osi czasu + schemat blokowy

## Lista plików

| Plik | Opis |
|------|------|
| `00_CYCLE_SUMMARY.svg` | Podsumowanie: oś czasu 0-9 i schemat blokowy |
| `digit_0_hold.svg` | Cyfra 0 - stan spoczynku (0000 bin) |
| `digit_0_pulse.svg` | Cyfra 0 - impuls zegara (przejście do 1) |
| `digit_1_hold.svg` | Cyfra 1 - stan spoczynku (0001 bin) |
| `digit_1_pulse.svg` | Cyfra 1 - impuls zegara (przejście do 2) |
| `digit_2_hold.svg` | Cyfra 2 - stan spoczynku (0010 bin) |
| `digit_2_pulse.svg` | Cyfra 2 - impuls zegara (przejście do 3) |
| `digit_3_hold.svg` | Cyfra 3 - stan spoczynku (0011 bin) |
| `digit_3_pulse.svg` | Cyfra 3 - impuls zegara (przejście do 4) |
| `digit_4_hold.svg` | Cyfra 4 - stan spoczynku (0100 bin) |
| `digit_4_pulse.svg` | Cyfra 4 - impuls zegara (przejście do 5) |
| `digit_5_hold.svg` | Cyfra 5 - stan spoczynku (0101 bin) |
| `digit_5_pulse.svg` | Cyfra 5 - impuls zegara (przejście do 6) |
| `digit_6_hold.svg` | Cyfra 6 - stan spoczynku (0110 bin) |
| `digit_6_pulse.svg` | Cyfra 6 - impuls zegara (przejście do 7) |
| `digit_7_hold.svg` | Cyfra 7 - stan spoczynku (0111 bin) |
| `digit_7_pulse.svg` | Cyfra 7 - impuls zegara (przejście do 8) |
| `digit_8_hold.svg` | Cyfra 8 - stan spoczynku (1000 bin) |
| `digit_8_pulse.svg` | Cyfra 8 - impuls zegara (przejście do 9) |
| `digit_9_hold.svg` | Cyfra 9 - stan spoczynku (1001 bin) |
| `digit_9_pulse.svg` | Cyfra 9 - impuls zegara (przejście do 0 - zapętlenie) |
| `transition_0_to_1.svg` | Przejście: które bity zmieniają 0→1 |
| `transition_1_to_2.svg` | Przejście: które bity zmieniają 1→2 |
| `transition_2_to_3.svg` | Przejście: które bity zmieniają 2→3 |
| `transition_3_to_4.svg` | Przejście: które bity zmieniają 3→4 |
| `transition_4_to_5.svg` | Przejście: które bity zmieniają 4→5 |
| `transition_5_to_6.svg` | Przejście: które bity zmieniają 5→6 |
| `transition_6_to_7.svg` | Przejście: które bity zmieniają 6→7 |
| `transition_7_to_8.svg` | Przejście: które bity zmieniają 7→8 |
| `transition_8_to_9.svg` | Przejście: które bity zmieniają 8→9 |
| `transition_9_to_0.svg` | Przejście: które bity zmieniają 9→0 |

## Jak używać

### Przeglądarka HTML (zalecane)
1. Otwórz `ANIMATION_VIEWER.html` w przeglądarce
2. Użyj przycisków lub strzałek klawiatury (← →) do nawigacji
3. Kliknij "Start" aby odtworzyć animację
4. Kliknij na element osi czasu aby przejść do konkretnej klatki

### Bezpośrednio w przeglądarce/VS Code
Każdy plik `.svg` można otworzyć bezpośrednio - są to zwykłe pliki wektorowe.

## Schemat kolorów

| Kolor | Znaczenie |
|-------|-----------|
| 🔴 Czerwony | Sygnał ON (aktywny redstone) |
| ⚫ Ciemny szary | Sygnał OFF (brak sygnału) |
| 🟢 Zielony | Aktywne wyjście (command block wykonuje komendę) |
| 🟡 Żółty | Podświetlenie / aktywna sekcja |

## Co pokazują wizualizacje?

### Dla każdej cyfry:
1. **Zegar** - czy daje impuls (czerwone = PULS!, szare = oczekuje)
2. **Licznik 4-bit** - stan każdego z 4 bitów (Q0-Q3)
3. **Wartość binarna** - reprezentacja binarna aktualnej cyfry
4. **Dekoder BCD** - która bramka AND jest aktywna (zielona)
5. **Command Blocks** - który block wykonuje `/say X`

### Przejścia pokazują:
- Które bity zmieniają wartość
- Jak zmienia się stan binarny
- Przykład: 5→6 zmienia Q1 z 0 na 1 (0101 → 0110)

## Czas trwania cyklu

Pełny cykl (0→1→2→3→4→5→6→7→8→9→0) trwa **10 sekund**:
- Każda cyfra wyświetlana przez 1 sekundę
- Impuls zegara co 1 sekundę (20 ticków Minecraft)
- Zapętlenie po cyfrze 9 (powrót do 0)

## Zastosowanie

Te wizualizacje służą do:
1. Zrozumienia działania układu przed budową w Minecraft
2. Debugowania - porównania oczekiwanego vs rzeczywistego stanu
3. Dokumentacji - wyjaśnienia jak działa redstone
4. Testowania - weryfikacji czy headless server działa poprawnie

---

**Wygenerowano:** 2026-01-30  
**Skrypt:** `generate_counter_frames.py`
