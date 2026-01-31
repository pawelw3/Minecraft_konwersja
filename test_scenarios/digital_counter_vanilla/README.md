# Scenariusz Testowy: Digital Counter Vanilla

## Opis
Pierwszy scenariusz testowy sprawdzający zdolność agenta do tworzenia i testowania złożonych układów redstone. **Zaktualizowany do architektury Dropper Ring Counter** - prostszej i bardziej niezawodnej niż poprzednia wersja z licznikiem 4-bit.

## Cel
- Sprawdzić czy agent potrafi zaprojektować układ redstone
- Zweryfikować działanie headless server do testowania
- Ustanowić format i standardy dla przyszłych scenariuszy

## Architektura (NOWA - Dropper Ring Counter)

### Dlaczego zmiana?
Stara architektura (zegar → licznik 4-bit → dekoder BCD) miała problemy:
- Potrzebowała resetu mod-10 (brakowało)
- Dekoder BCD wymagał skomplikowanych bramek AND
- Wiele potencjalnych punktów awarii

**Nowa architektura (10-stanowy ring counter z dropperów):**
- **10 dropperów w pętli** i **1 item krążący**
- Co impuls (~1s) item przesuwa się o 1 pozycję
- Komparator czyta zawartość droppera (0/1 item)
- **Pętla 0–9 jest naturalna**, bez resetu i bez dekodera

### Komponenty:

| Element | Opis | Bloki 1.7.10 |
|---------|------|--------------|
| **Zegar 1Hz** | Torch inverter + repeater loop | stone, redstone_torch, repeater, redstone_wire |
| **Ring Counter** | 10 dropperów w pętli z 1 itemem | dropper (1.5.2+), stone |
| **Komparatory** | 10 komparatorów czyta droppery | comparator (1.5+), stone |
| **Command Blocki** | 10 bloków `/say 0-9` | command_block (1.4+) |

### Potwierdzenie dostępności bloków w 1.7.10:
- ✅ **Dropper** - dodany w 1.5.2 (snapshot 13w03a)
- ✅ **Comparator** - dodany w 1.5 (snapshot 13w01a)
- ✅ **Command Block** - dostępny od 1.4
- ✅ **Repeater** - dostępny od Beta 1.3
- ✅ **Redstone Torch** - dostępny od classic
- ✅ **Stone** - podstawowy blok

## Struktura plików

```
digital_counter_vanilla/
├── schematics/
│   ├── circuit_design.json      # Zwięzła reprezentacja logiczna (ring counter)
│   └── voxel_grid.json          # Siatka voxeli 1x1x1 z poprawnym podparciem
├── test_logs/                   # Logi z testów
├── world_template/              # Szablon świata (region/)
├── docs/                        # Dodatkowa dokumentacja
├── debug_redstone.py            # Narzędzie CLI do debugowania
├── debug_redstone_README.md     # Dokumentacja narzędzia
├── README.md                    # Ten plik
└── test_config.json             # Konfiguracja testu dla headless server
```

## Formaty danych

### `circuit_design.json`
Zwięzła reprezentacja układu zawierająca:
- Komponenty (clock_1hz, ring_counter_10, output_digits)
- Koordynaty 10 dropperów i ich facing (kierunek wyjścia)
- Koordynaty 10 komparatorów i ich facing
- Koordynaty 10 command blocków
- Połączenia między komponentami

### `voxel_grid.json`
Szczegółowa siatka 3D zawierająca:
- **Wymiary**: 15×6×15 (zmniejszone z poprzedniej wersji)
- **Podparcie**: każdy komponent redstone ma stone pod spodem (y-1)
- **Warstwy**:
  - y=0: podparcie (stone) pod droppery, komparatory, command blocki
  - y=1: droppery, komparatory, command blocki
  - y=2: podparcie pod zasilanie dropperów
  - y=3: magistrala zasilająca droppery (redstone_wire) + zegar
- **Sprawdzone**: brak konfliktów współrzędnych, wszystkie bloki mają podparcie

## Topologia układu

### Droppery w pętli (y=1):
```
        D8 (6,1,8) ← D9 (6,1,7)
        ↓                   ↑
    D7 (7,1,8)         D0 (6,1,6) ← start (ma item)
        ↓                   ↑
    D6 (8,1,8)         D1 (7,1,6)
        ↓                   ↑
    D5 (9,1,8) ← D4 (9,1,7) ← D3 (9,1,6)
                ↑
            D2 (8,1,6)
```

Kierunki facing:
- D0→D1: east, D1→D2: east, D2→D3: east
- D3→D4: south, D4→D5: south
- D5→D6: west, D6→D7: west, D7→D8: west
- D8→D9: north, D9→D0: north

### Komparatory (czytają droppery):
- C0: (6,1,5) facing north, czyta D0
- C1: (7,1,5) facing north, czyta D1
- C2: (8,1,5) facing north, czyta D2
- C3: (10,1,6) facing east, czyta D3
- C4: (10,1,7) facing east, czyta D4
- C5: (10,1,8) facing east, czyta D5
- C6: (8,1,9) facing south, czyta D6
- C7: (7,1,9) facing south, czyta D7
- C8: (5,1,8) facing west, czyta D8
- C9: (5,1,7) facing west, czyta D9

### Command Blocki (na wyjściach komparatorów):
- CMD0: (6,1,4) - `/say 0`
- CMD1: (7,1,4) - `/say 1`
- CMD2: (8,1,4) - `/say 2`
- CMD3: (11,1,6) - `/say 3`
- CMD4: (11,1,7) - `/say 4`
- CMD5: (11,1,8) - `/say 5`
- CMD6: (8,1,10) - `/say 6`
- CMD7: (7,1,10) - `/say 7`
- CMD8: (4,1,8) - `/say 8`
- CMD9: (4,1,7) - `/say 9`

### Zegar (y=3):
- Inwerter: stone (1,3,2) + torch (2,3,2) facing west
- Repeatery: R1 (3,3,2) delay 4, R2 (4,3,2) delay 4, R3 (5,3,2) delay 1
- Wyjście: wire (6,3,2)
- Powrót: wire (6,3,3)→(5,3,3)→...→(1,3,3)

### Magistrala zasilania dropperów (y=3):
- Wire nad każdym dropperem: (6,3,6), (7,3,6), ..., (6,3,7)
- Połączone w jedną sieć
- Połączenie od zegara: (6,3,2)→(6,3,3)→(6,3,4)→(6,3,5)→(6,3,6)

## Testowanie

### Na Headless Server
1. Wczytać szablon świata do `headless_server/world/`
2. Upewnić się że w dropperze D0 jest 1 cobblestone
3. Uruchomić serwer z opcją `nogui`
4. Odczytywać logi z `logs/latest.log`
5. Szukać wzorca: `[Server] X` gdzie X to cyfra 0-9
6. Weryfikować sekwencję co 10 sekund

### Kryteria sukcesu
- [ ] Sekwencja 0-9 pojawia się w logach
- [ ] Każda cyfra pojawia się co ~1 sekundę
- [ ] Cykle powtarzają się stabilnie (min. 3 cykle)
- [ ] Brak "pustych" kroków ani podwójnych przeskoków

### Narzędzie debug_redstone.py
```bash
# Domyślna symulacja 12s
python debug_redstone.py

# Pełny cykl 0-9 (11s wystarczy)
python debug_redstone.py -t 11

# Częstsze pomiary
python debug_redstone.py -i 0.1

# Zapisanie historii
python debug_redstone.py -o historia.json
```

## Checklist "perfekcyjności"

1. ✅ **Brak kolizji współrzędnych** - żadna para voxelów nie ma tego samego (x,y,z)
2. ✅ **Podparcie redstone** - każda redstone_wire/repeater/comparator ma stone pod spodem
3. ✅ **Facing dropperów** - każdy dropper wskazuje dokładnie na następny w pętli
4. ✅ **Facing komparatorów** - każdy komparator czyta droppera (tył do droppera)
5. ✅ **Command blocki** - stoją dokładnie na wyjściu komparatora
6. ✅ **Bus zasilania** - na y=3 jest jedna spójna sieć zasilająca wszystkie droppery
7. ✅ **Zegar** - generuje przełączający się sygnał (~20 ticków okres)
8. ✅ **Stan startowy** - 1 item w D0

## Zasady działania

### Jak działa ring counter?
1. **Stan początkowy**: 1 cobblestone w dropperze D0
2. **Impuls zegara**: Wszystkie droppery dostają zasilanie przez bus (y=3)
3. **Przesunięcie itemu**: Dropper z itemem wyrzuca go do następnego droppera (kierunek facing)
4. **Detekcja**: Komparator nad dropperem z itemem daje sygnał wyjściowy
5. **Output**: Command block podłączony do aktywnego komparatora wykonuje `/say X`

### Przykładowy cykl:
```
T=0s: D0 ma item → C0 daje sygnał → CMD0: /say 0
T=1s: Impuls zegara → item przechodzi D0→D1
T=1s: D1 ma item → C1 daje sygnał → CMD1: /say 1
...
T=9s: D9 ma item → C9 daje sygnał → CMD9: /say 9
T=10s: Impuls zegara → item przechodzi D9→D0 (zapętlenie!)
```

## Historia zmian

### Wersja 1 (stara):
- Zegar 1Hz → Licznik 4-bit → Dekoder BCD → Command Blocks
- Problem: brak resetu mod-10, skomplikowany dekoder

### Wersja 2 (obecna):
- Zegar 1Hz → Dropper Ring Counter → Comparators → Command Blocks
- Zalety: naturalna pętla 0-9, prostsza konstrukcja, mniej punktów awarii

---

**Status**: Zaktualizowano do ring countera, wszystkie bloki potwierdzone dla 1.7.10
**Ostatnia aktualizacja**: 2026-01-30
