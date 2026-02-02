# Handoff: ProjectRed - Zadanie 6 (Testy na headless serwerze)

## Podsumowanie sesji

Wykonano **Zadanie 6** konwersji moda ProjectRed - stworzenie kompletnego systemu automatycznego testowania na headless serwerze Minecraft. System obsługuje workflow: przygotowanie mapy testowej → uruchomienie serwera → testy RCON → analiza logów → raport.

Zadanie obejmowało:
1. Klient RCON do zdalnego sterowania serwerem
2. Parser logów serwera do weryfikacji wyników testów
3. Generator patchów dla struktur testowych
4. Test runner do pełnego workflow automatycznych testów
5. Quick test runner do szybkich testów na uruchomionym serwerze
6. Główny orchestrator testów headless

---

## Ukończono

- [x] Klient RCON (`rcon_client.py`) - pełna implementacja protokołu
- [x] Parser logów (`log_parser.py`) - wykrywanie statusu serwera i markerów testowych
- [x] Generator patchów (`patch_generator.py`) - konwersja struktur JSON na patche
- [x] Test runner (`test_runner.py`) - kompletny workflow automatyczny
- [x] Quick test (`quick_test.py`) - szybkie testy na uruchomionym serwerze
- [x] Orchestrator (`run_headless_test.py`) - główny skrypt testowy
- [x] Patch testowy wygenerowany (345 edits, 70 struktur)
- [x] Dokumentacja HANDOFF

---

## Nowe pliki

| Plik | Opis |
|------|------|
| `src/converters/projectred/test_structures/headless_test/__init__.py` | Moduł testowania headless |
| `src/converters/projectred/test_structures/headless_test/rcon_client.py` | Klient protokołu RCON |
| `src/converters/projectred/test_structures/headless_test/log_parser.py` | Parser logów serwera |
| `src/converters/projectred/test_structures/headless_test/patch_generator.py` | Generator patchów JSON |
| `src/converters/projectred/test_structures/headless_test/test_runner.py` | Automatyczny test runner |
| `src/converters/projectred/test_structures/headless_test/quick_test.py` | Szybki test runner |
| `src/converters/projectred/test_structures/headless_test/run_headless_test.py` | Główny orchestrator |
| `src/converters/projectred/test_structures/headless_test/projectred_test_patch.json` | Wygenerowany patch (345 edits) |

---

## Architektura systemu testowego

```
┌─────────────────────────────────────────────────────────────────┐
│                    run_headless_test.py                          │
│                    (Main Orchestrator)                           │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌───────────────┐    ┌───────────────┐    ┌───────────────┐   │
│  │ STEP 1        │    │ STEP 2        │    │ STEP 3        │   │
│  │ Prepare World │───►│ Start Server  │───►│ Wait Ready    │   │
│  │               │    │               │    │               │   │
│  │ - Copy clean  │    │ - Launch JAR  │    │ - Parse logs  │   │
│  │ - Apply patch │    │ - Configure   │    │ - Connect     │   │
│  └───────────────┘    └───────────────┘    │   RCON        │   │
│                                            └───────────────┘   │
│                                                    │            │
│                                                    ▼            │
│  ┌───────────────┐    ┌───────────────┐    ┌───────────────┐   │
│  │ STEP 6        │    │ STEP 5        │    │ STEP 4        │   │
│  │ Cleanup       │◄───│ Report        │◄───│ Run Tests     │   │
│  │               │    │               │    │               │   │
│  │ - Stop server │    │ - Aggregate   │    │ - Deploy via  │   │
│  │ - Disconnect  │    │ - Save JSON   │    │   RCON        │   │
│  └───────────────┘    └───────────────┘    │ - Activate    │   │
│                                            │ - Verify logs │   │
│                                            └───────────────┘   │
└─────────────────────────────────────────────────────────────────┘

Komponenty:
┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐
│ rcon_client.py  │  │ log_parser.py   │  │patch_generator  │
│                 │  │                 │  │                 │
│ - connect()     │  │ - parse_all()   │  │ - generate()    │
│ - command()     │  │ - find_markers()│  │ - load_structs()│
│ - setblock()    │  │ - server_status │  │ - save_patch()  │
└─────────────────┘  └─────────────────┘  └─────────────────┘
```

---

## Komponenty szczegółowo

### 1. RCON Client (`rcon_client.py`)

Pełna implementacja protokołu RCON (Remote Console) dla Minecraft:

```python
from headless_test.rcon_client import RconClient

# Połączenie
client = RconClient("127.0.0.1", 25575, "password")
client.connect()

# Komendy
client.command("/list")
client.setblock(100, 64, 100, "minecraft:stone", 0)
client.say("Test message")

# Context manager
with RconClient("127.0.0.1", 25575, "pass") as client:
    client.command("/tp @p 0 100 0")
```

### 2. Log Parser (`log_parser.py`)

Parser logów serwera do wykrywania statusu i wyników testów:

```python
from headless_test.log_parser import LogParser

parser = LogParser("logs/latest.log")

# Status serwera
status = parser.get_server_status()
# -> ServerStatus(started=True, rcon_ready=True, errors=[])

# Szukanie markerów testowych
found = parser.find_test_markers(["TEST_AND_GATE_OK", "TEST_OR_GATE_OK"])
# -> {"TEST_AND_GATE_OK": TestMarker(timestamp="12:34:56", ...)}

# Czekanie na markery
found = parser.wait_for_markers(["TEST_TIMER_OK"], timeout=30)
```

### 3. Patch Generator (`patch_generator.py`)

Konwertuje struktury JSON na patche dla Kotlin workera:

```python
from headless_test.patch_generator import generate_projectred_test_patch

# Generowanie patcha ze wszystkich struktur
patch = generate_projectred_test_patch(
    structures_dir="generated/",
    output_path="patch.json",
    start_offset=(600, 70, -100),
    spacing=15
)
# -> 345 edits, 70 structures
```

### 4. Quick Test (`quick_test.py`)

Szybkie testy na już uruchomionym serwerze:

```bash
# Test połączenia
python quick_test.py --action ping

# Deploy prostych testów
python quick_test.py --action deploy

# Pełny test (deploy + verify)
python quick_test.py --action full
```

### 5. Full Orchestrator (`run_headless_test.py`)

Kompletny workflow testowy:

```bash
# Pełny test 1.7.10
python run_headless_test.py --version 1.7.10

# Test 1.18.2 (po konwersji)
python run_headless_test.py --version 1.18.2

# Tylko deploy (bez startu serwera)
python run_headless_test.py --deploy-only

# Tylko testy (serwer już działa)
python run_headless_test.py --test-only
```

---

## Wygenerowany patch

Patch zawiera 345 edycji dla 70 struktur:

| Kategoria | Ilość struktur |
|-----------|---------------|
| Integration tests | 8 |
| Unit tests | 62 |

**Punkty aktywacji testów integracyjnych:**

| Test | Pozycja aktywacji |
|------|-------------------|
| `integration_and_gate` | (600, 71, -100) |
| `integration_bundled_cable` | (622, 71, -100) |
| `integration_comparator` | (645, 71, -100) |
| `integration_insulated_wires` | (668, 71, -100) |
| `integration_lamp_toggle` | (691, 71, -100) |
| `integration_not_gate` | (712, 71, -100) |
| `integration_or_gate` | (733, 71, -100) |
| `integration_timer_gate` | (755, 71, -100) |

---

## Użycie

### Pełny workflow automatyczny:

```bash
cd c:\Users\pawel\Minecraft_konwersja

# 1.7.10 - przed konwersją
python -m src.converters.projectred.test_structures.headless_test.run_headless_test --version 1.7.10

# 1.18.2 - po konwersji
python -m src.converters.projectred.test_structures.headless_test.run_headless_test --version 1.18.2
```

### Szybki test na uruchomionym serwerze:

```bash
# Serwer musi być uruchomiony z RCON:
# - enable-rcon=true
# - rcon.port=25575
# - rcon.password=test123

python -m src.converters.projectred.test_structures.headless_test.quick_test --action full
```

### Generowanie patcha:

```bash
python -m src.converters.projectred.test_structures.headless_test.patch_generator
```

---

## Wymagania

### server.properties:
```properties
enable-rcon=true
rcon.port=25575
rcon.password=test123
enable-command-block=true
online-mode=false
```

### Struktura folderów:
```
headless_server/
├── 1.7.10/
│   ├── minecraft_server.jar (lub forge-*.jar)
│   ├── server.properties
│   ├── logs/latest.log
│   └── world/
└── 1.18.2/
    ├── ...
```

---

## Format raportu testowego

```json
{
  "version": "1.7.10",
  "timestamp": "2026-02-02T15:30:00",
  "tests": [
    {
      "name": "integration_and_gate",
      "passed": true,
      "expected": "TEST_AND_GATE_OK",
      "actual": "[@] TEST_AND_GATE_OK"
    }
  ],
  "summary": {
    "total": 9,
    "passed": 8,
    "failed": 1,
    "success_rate": "88.9%"
  }
}
```

---

## Następne kroki

1. [ ] **Uruchomić pełny test 1.7.10** - zweryfikować że struktury działają przed konwersją
2. [ ] **Wykonać konwersję mapy testowej** - przepuścić przez ProjectRed converter
3. [ ] **Uruchomić test 1.18.2** - zweryfikować działanie po konwersji
4. [ ] **Porównać wyniki** - raport różnic między wersjami
5. [ ] **Obsługa multiparts** - dodać wsparcie dla ForgeMultipart w patchach Kotlin

---

## Uwagi techniczne

### Multiparts (ForgeMultipart)

Bramki i przewody ProjectRed używają CB Multipart. W 1.7.10:
- Block: `forge_microblock` (ID zależne od config)
- TileEntity: `savedMultipart` z listą `parts`

Patch generator tworzy poprawne struktury, ale pełne deployment wymaga:
1. Kotlin worker do modyfikacji .mca
2. Lub ręczne umieszczenie struktury przez gracza + WorldEdit

### RCON a modowe bloki

RCON `/setblock` działa tylko z vanilla blokami. Dla modowych bloków:
- Option A: Kotlin worker (offline)
- Option B: WorldEdit (na serwerze)
- Option C: Ręczne umieszczenie (testowe)

Testy integracyjne używają tylko vanilla bloków (lever, redstone, command_block) co pozwala na pełne testowanie przez RCON.

---

**Status:** Zadanie 6 ukończone - system testowania headless gotowy
**Data:** 2026-02-02
**Nowe pliki:** 8 (moduł headless_test)
**Patch:** 345 edits, 70 struktur, 8 testów integracyjnych
