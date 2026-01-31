# Specyfikacja: Testowy Układ Redstone + Command Block

## Cel

Weryfikacja poprawności wstawiania bloków redstone oraz Tile Entities (Command Block) na mapę Minecraft 1.7.10 poprzez skonstruowanie prostego układu testowego zakończonego command blockiem logującym na konsolę.

## Wersje i środowisko

| Parametr | Wartość | Źródło |
|----------|---------|--------|
| Minecraft | 1.7.10 | `ENV.md` |
| Forge | 10.13.4.1614 | Świat źródłowy |
| Format zapisu | Anvil (MCA) | Minecraft Wiki |
| Mody | Vanilla + Forge | Brak modów zmieniających redstone |

## Interfejs (wejścia/wyjścia)

### Wejście
- **Aktywacja**: Dźwignia (Lever) na pozycji (50, 64, 50)
- **Sygnał**: Redstone signal level 15

### Wyjście
- **Log**: Wiadomość w konsoli serwera: `[TEST_REDSTONE] Układ redstone działa poprawnie! Test PASS.`
- **Wskaźnik wizualny**: Command Block emituje cząsteczki po wykonaniu komendy (jeśli włączone)

## Stan i dynamika

### Początkowy stan układu
- Dźwignia: wyłączona (off)
- Redstone: nieaktywny
- Command Block: gotowy, SuccessCount = 0

### Sekwencja działania
1. Gracz przełącza dźwignię (on)
2. Sygnał rozchodzi się przez redstone dust (3 bloki) - natychmiast
3. Repeater 1 opóźnia sygnał o 1 tick (0.1s)
4. Sygnał przechodzi przez kolejne 3 bloki redstone
5. Repeater 2 opóźnia sygnał o 1 tick
6. Sygnał aktywuje Command Block
7. Command Block wykonuje komendę `/say ...`
8. Wiadomość pojawia się w konsoli

### Całkowite opóźnienie
- ~0.2s (2 ticki repeaterów) + czas propagacji redstone

## Kryteria akceptacji (testowalne)

| ID | Kryterium | Metoda weryfikacji | Warunek sukcesu |
|----|-----------|-------------------|-----------------|
| A1 | Wszystkie bloki wstawione | Worker `--verify-block` | ID i Meta zgodne z `voxel_grid.json` |
| A2 | Tile Entity utworzone | Worker `--verify-redstone-test` | TE z id="Control" na pozycji (60,64,50) |
| A3 | Pole Command ustawione | Weryfikacja TE | Command zawiera "[TEST_REDSTONE]" |
| A4 | Układ działa w grze | Test E2E na serwerze | Wiadomość w konsoli po przełączeniu dźwigni |
| A5 | Brak kolizji | Walidacja statyczna | Brak duplikatów pozycji w voxel_grid |

## Projekt implementacji

### Warstwy (Y-levels)
- **Y=63**: Podłoga (Stone) - podpora dla komponentów redstone
- **Y=64**: Komponenty redstone (Lever, Redstone, Repeater, Command Block)

### Routing
```
X=50        X=60
 |           |
[ L - R - R - R - ! - R - R - R - ! - R - C ]
     3xR   R1    3xR   R2    R   CB

L  = Lever (69:5)
R  = Redstone (55:15)
R1 = Repeater (93:1) - delay=1 tick
R2 = Repeater (93:1) - delay=1 tick
C  = Command Block (137:0) + TE
!  = Połączenie redstone
```

### Punkty pomiarowe (debug)
| Pozycja | Opis | Oczekiwane |
|---------|------|------------|
| (50,64,50) | Dźwignia | Meta=5 (włączona) |
| (54,64,50) | Repeater 1 | Sygnał po 1 ticku |
| (58,64,50) | Repeater 2 | Sygnał po 2 tickach |
| (60,64,50) | Command Block | Wykonanie komendy |

## Artefakt: voxel_grid.json

Zawiera 22 bloki + 1 Tile Entity:
- 11 bloków stone (podłoga)
- 1 lever
- 8 redstone dust
- 2 repeatery
- 1 command block + TE

Szczegóły w `voxel_grid.json`.

## Walidacja statyczna

Wykonana przez `generate_patch.py`:
- ✅ Brak duplikatów pozycji `(x,y,z)`
- ✅ Redstone na pełnym bloku (stone)
- ✅ Command Block ma przypisane Tile Entity
- ✅ Wszystkie wymagane pola NBT obecne

## Symulacja / Test w grze

### Warunki testu
- Świat: `map_read_write_tests/kimi1`
- Pozycja gracza: okolice (50, 64, 50)
- Tryb: Creative (możliwość przełączania dźwigni)

### Kroki testowe E2E
1. Uruchom serwer 1.7.10 z mapą `kimi1`
2. Połącz się jako gracz
3. Przejdź do pozycji (50, 64, 50)
4. Przełącz dźwignię (prawy przycisk myszy)
5. Sprawdź konsolę serwera

### Oczekiwany wynik E2E
```
[Server thread/INFO]: [TEST_REDSTONE] Układ redstone działa poprawnie! Test PASS.
```

## Źródła

| Element | Źródło | Uwagi |
|---------|--------|-------|
| ID bloków 1.7.10 | Minecraft Wiki | http://minecraft.wiki/ |
| Format NBT chunka | Minecraft Wiki | Anvil format |
| Hephaistos | GitHub | https://github.com/jglrxavpok/Hephaistos |
| Metadata bloków | Dekompilacja MC 1.7.10 | Wartości meta zweryfikowane |

## Historia zmian

| Data | Autor | Zmiana |
|------|-------|--------|
| 2026-01-31 | MC EditKit | Utworzenie specyfikacji i implementacja |

---
*Specyfikacja zgodna ze skill_scenario_builder.md*
