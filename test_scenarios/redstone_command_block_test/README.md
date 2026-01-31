# Testowy Układ Redstone + Command Block

## Przegląd

Testowy przypadek weryfikujący poprawność wstawiania bloków redstone oraz Tile Entities (Command Block) na mapę Minecraft 1.7.10.

## Struktura testu

```
redstone_command_block_test/
├── ENV.md                      # Środowisko testowe
├── README.md                   # Ten plik
├── voxel_grid.json            # Definicja struktury bloków
├── generate_patch.py          # Generator patch JSON
├── redstone_test_patch.json   # Wygenerowany patch
├── verify_te_nbtlib.py        # Weryfikacja (Python/nbtlib)
└── src/
    └── VerifyRedstoneTest.kt  # Weryfikacja (Kotlin/Hephaistos)
```

## Układ testowy

Schemat układu (widok z góry, Y=64):

```
X: 50  51  52  53  54  55  56  57  58  59  60
    |   |   |   |   |   |   |   |   |   |   |
    L - R - R - R - R1- R - R - R - R2- R - C
    
Legenda:
    L  = Lever (dźwignia) - ID 69
    R  = Redstone Dust - ID 55
    R1 = Repeater (delay) - ID 93
    R2 = Repeater (delay) - ID 93
    C  = Command Block - ID 137 (+ Tile Entity)
```

### Współrzędne bloków

| Pozycja | Blok | ID | Meta | Opis |
|---------|------|-----|------|------|
| (50,64,50) | Lever | 69 | 5 | Dźwignia (źródło sygnału) |
| (51-53,64,50) | Redstone | 55 | 15 | Kabel redstone (3 bloki) |
| (54,64,50) | Repeater | 93 | 1 | Opóźnienie 1 tick |
| (55-57,64,50) | Redstone | 55 | 15 | Kabel redstone (3 bloki) |
| (58,64,50) | Repeater | 93 | 1 | Opóźnienie 1 tick |
| (59,64,50) | Redstone | 55 | 15 | Kabel redstone |
| (60,64,50) | Command Block | 137 | 0 | Blok komend + TE |

### Tile Entity (Command Block)

```json
{
  "id": "Control",
  "x": 60,
  "y": 64,
  "z": 50,
  "Command": "/say [TEST_REDSTONE] Układ redstone działa poprawnie! Test PASS.",
  "CustomName": "@",
  "TrackOutput": 1
}
```

## Jak uruchomić test

### 1. Wygenerowanie patcha

```bash
cd test_scenarios/redstone_command_block_test
python generate_patch.py --output redstone_test_patch.json
```

### 2. Wstawienie bloków na mapę

```bash
cd jvm/worker
java -jar build/libs/mc-editkit-worker-1.0-SNAPSHOT.jar \
    --world ../../map_read_write_tests/kimi1 \
    --patch ../../test_scenarios/redstone_command_block_test/redstone_test_patch.json
```

### 3. Weryfikacja

```bash
cd jvm/worker
java -jar build/libs/mc-editkit-worker-1.0-SNAPSHOT.jar \
    --world ../../map_read_write_tests/kimi1 \
    --verify-redstone-test
```

## Oczekiwane zachowanie w grze

Po uruchomieniu serwera Minecraft 1.7.10 z tą mapą:

1. Wejdź na pozycję (50, 64, 50)
2. Znajdź dźwignię (Lever)
3. Kliknij prawym przyciskiem myszy aby ją przełączyć
4. Zaobserwuj konsolę serwera

**Oczekiwany wynik:**
- Sygnał redstone rozchodzi się przez kabel
- Po opóźnieniu w repeaterach dociera do Command Blocka
- W konsoli pojawia się wiadomość:
  ```
  [TEST_REDSTONE] Układ redstone działa poprawnie! Test PASS.
  ```

## Kryteria akceptacji

| Kryterium | Metoda weryfikacji | Status |
|-----------|-------------------|--------|
| Bloki wstawione | Worker `--verify-block` | ✅ PASS |
| Command Block + TE | Worker `--verify-redstone-test` | ✅ PASS |
| Układ działa w grze | Test manualny na serwerze | ⏳ Do wykonania |

## Problemy i rozwiązania

### Znane ograniczenia

1. **Repeater delay** - w tej wersji testu repeatery mają minimalne opóźnienie (1 tick). Dla większego opóźnienia należy dodać więcej repeaterów lub zmienić ich konfigurację.

2. **Orientacja** - wszystkie komponenty są skierowane wzdłuż osi X (wschód). Dźwignia wskazuje na wschód, repeatery przekazują sygnał na wschód.

3. **Podłoga** - pod całym układem znajduje się stone (ID 1) na Y=63.

## Narzędzia

- **Generator patcha**: Python 3.10+
- **Worker**: Kotlin 1.5 + Hephaistos
- **Weryfikacja**: Kotlin/Hephaistos (preferowane) lub Python/nbtlib

## Autor

Wygenerowano automatycznie przez MC EditKit Worker v1.0
