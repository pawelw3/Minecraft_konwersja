# 01. Architektura systemu

## Diagram przepływu danych

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              WARSTWA PYTHON                                  │
│                                                                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐    │
│  │ BetterStorage│  │  BloodMagic  │  │ EnderStorage │  │  GrowthCraft │    │
│  │  Converter   │  │  Converter   │  │  Converter   │  │  Converter   │    │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘    │
│         │                 │                 │                 │             │
│         └────────────┬────┴────────────┬────┴────────────┬────┘             │
│                      │                 │                 │                  │
│                      ▼                 ▼                 ▼                  │
│              ┌─────────────────────────────────────────────────┐            │
│              │           EventEmitter (src/common/)            │            │
│              │  - Waliduje eventy                              │            │
│              │  - Serializuje do JSON                          │            │
│              │  - Grupuje po regionach (opcjonalnie)           │            │
│              └─────────────────────────┬───────────────────────┘            │
│                                        │                                    │
└────────────────────────────────────────┼────────────────────────────────────┘
                                         │
                                         ▼
                              ┌─────────────────────┐
                              │   Event JSON File   │
                              │  (ustandaryzowany)  │
                              └──────────┬──────────┘
                                         │
┌────────────────────────────────────────┼────────────────────────────────────┐
│                              WARSTWA JVM                                     │
│                                        │                                     │
│                                        ▼                                     │
│              ┌─────────────────────────────────────────────────┐            │
│              │              EventProcessor.kt                   │            │
│              │  - Parsuje Event JSON                           │            │
│              │  - Waliduje strukturę                           │            │
│              │  - Grupuje operacje po chunkach/regionach       │            │
│              │  - Optymalizuje kolejność operacji              │            │
│              └─────────────────────────┬───────────────────────┘            │
│                                        │                                    │
│                    ┌───────────────────┼───────────────────┐                │
│                    │                   │                   │                │
│                    ▼                   ▼                   ▼                │
│         ┌──────────────────┐ ┌──────────────────┐ ┌──────────────────┐     │
│         │ BlockHandler.kt  │ │ BlockEntityHdlr │ │ EntityHandler.kt │     │
│         │ - setBlock()     │ │ - setBlockEntity │ │ - spawnEntity()  │     │
│         │ - removeBlock()  │ │ - removeBlockEnt │ │ - removeEntity() │     │
│         └────────┬─────────┘ └────────┬─────────┘ └────────┬─────────┘     │
│                  │                    │                    │                │
│                  └────────────────────┼────────────────────┘                │
│                                       │                                     │
│                                       ▼                                     │
│              ┌─────────────────────────────────────────────────┐            │
│              │            WorldEditor1182.kt                    │            │
│              │  - Zarządza plikami regionów (.mca)             │            │
│              │  - Obsługuje format Anvil 1.18.2                │            │
│              │  - Batch commit z transakcyjnością              │            │
│              └─────────────────────────┬───────────────────────┘            │
│                                        │                                    │
│                                        ▼                                    │
│                              ┌──────────────────┐                           │
│                              │  Mapa 1.18.2     │                           │
│                              │  (pliki .mca)    │                           │
│                              └──────────────────┘                           │
└─────────────────────────────────────────────────────────────────────────────┘
```

## Komponenty systemu

### 1. Warstwa Python (src/common/)

```
src/common/
├── events/
│   ├── __init__.py
│   ├── types.py          # Definicje typów eventów (dataclasses)
│   ├── emitter.py        # EventEmitter - główna klasa do produkcji eventów
│   ├── validator.py      # Walidacja eventów przed serializacją
│   └── serializer.py     # Serializacja do JSON
├── mappings/
│   ├── __init__.py
│   ├── block_registry.py # Centralny rejestr mapowań bloków
│   ├── item_registry.py  # Centralny rejestr mapowań itemów
│   └── nbt_helpers.py    # Wspólne funkcje transformacji NBT
└── adapters/
    ├── __init__.py
    └── base_adapter.py   # Bazowa klasa adaptera dla konwerterów
```

### 2. Warstwa JVM (jvm/worker/)

```
jvm/worker/src/main/kotlin/mc/editkit/
├── events/
│   ├── EventProcessor.kt     # Główny procesor eventów
│   ├── EventParser.kt        # Parser JSON -> Event objects
│   ├── EventValidator.kt     # Walidacja eventów
│   └── EventTypes.kt         # Definicje typów eventów (data classes)
├── handlers/
│   ├── BlockHandler.kt       # Obsługa operacji na blokach
│   ├── BlockEntityHandler.kt # Obsługa BlockEntity (TileEntity)
│   ├── EntityHandler.kt      # Obsługa Entity (moby, itemy, etc.)
│   └── HandlerRegistry.kt    # Rejestr handlerów dla różnych operacji
├── world/
│   ├── WorldEditor1710.kt    # Edytor dla formatu 1.7.10 (istniejący)
│   ├── WorldEditor1182.kt    # Edytor dla formatu 1.18.2 (nowy)
│   ├── ChunkManager.kt       # Zarządzanie chunkami (cache, batch)
│   └── RegionManager.kt      # Zarządzanie regionami (.mca)
├── nbt/
│   ├── NbtTransformer.kt     # Transformacje NBT między wersjami
│   └── NbtValidator.kt       # Walidacja struktur NBT
└── Main.kt                   # Entry point z CLI
```

## Zasady podziału odpowiedzialności

### Python odpowiada za:

| Zakres | Opis |
|--------|------|
| Mapowania bloków | `old_block_id` → `new_block_id` |
| Mapowania itemów | `old_item_id:damage` → `new_item_id` |
| Transformacje NBT | Logika konwersji struktur NBT |
| Produkcja eventów | Tworzenie Event JSON z wynikami konwersji |
| Statystyki | Agregacja statystyk konwersji |

### Python NIE robi:

| Zakres | Dlaczego |
|--------|----------|
| Odczyt plików .mca | Wydajność - JVM jest szybszy |
| Zapis plików .mca | Spójność - jeden punkt zapisu |
| Kompresja/dekompresja | JVM ma natywne wsparcie |
| Walidacja chunków | JVM robi to przy zapisie |

### JVM odpowiada za:

| Zakres | Opis |
|--------|------|
| Parsowanie Event JSON | Deserializacja eventów |
| Batch processing | Grupowanie operacji po regionach |
| Odczyt map źródłowych | Format 1.7.10 (jeśli potrzebne) |
| Zapis map docelowych | Format 1.18.2 |
| Walidacja | Sprawdzanie poprawności danych |
| Transakcyjność | Atomowy commit, możliwość rollback |

## Przepływ danych - przykład

```
1. Konwerter BetterStorage (Python):
   - Skanuje mapę 1.7.10 (przez JVM reader lub własny parser)
   - Dla każdego bloku betterstorage:
     - Mapuje block_id: "betterstorage:reinforcedChest" → "minecraft:chest"
     - Transformuje NBT: {Items: [...]} → {Items: [...], Lock: ""}
     - Emituje event: SetBlockEntity(pos, block, nbt)

2. EventEmitter (Python):
   - Zbiera eventy
   - Waliduje (czy block_id istnieje, czy NBT jest poprawne)
   - Serializuje do JSON
   - Zapisuje: events/betterstorage_events.json

3. EventProcessor (JVM):
   - Wczytuje events/betterstorage_events.json
   - Parsuje eventy
   - Grupuje po regionach: {r.0.0: [event1, event2], r.0.1: [event3]}
   - Dla każdego regionu:
     - Otwiera plik .mca
     - Aplikuje eventy
     - Zapisuje zmiany

4. Wynik:
   - Mapa 1.18.2 z przekonwertowanymi blokami
   - Raport: events_applied.json z statystykami
```

## Tryby pracy

### Tryb 1: Pełna konwersja (Python + JVM)

```bash
# Python produkuje eventy
python -m src.pipeline.full_conversion \
    --source maps/1.7.10/world \
    --output events/

# JVM aplikuje eventy
java -jar worker.jar \
    --apply-events events/ \
    --target maps/1.18.2/world
```

### Tryb 2: Tylko generowanie eventów (Python)

```bash
# Dla testowania/debugowania
python -m src.converters.betterstorage \
    --source maps/1.7.10/world \
    --output events/betterstorage.json \
    --dry-run  # nie wywołuje JVM
```

### Tryb 3: Tylko aplikowanie eventów (JVM)

```bash
# Dla re-aplikacji lub testów
java -jar worker.jar \
    --apply-events events/betterstorage.json \
    --target maps/1.18.2/world \
    --validate-only  # opcjonalnie: tylko walidacja bez zapisu
```

## Obsługa błędów

```
┌─────────────────────────────────────────────────────────────────┐
│  Event z błędem                                                  │
│  {                                                               │
│    "op": "set_block_entity",                                    │
│    "pos": [100, 64, 200],                                       │
│    "block": "minecraft:invalid_block",  ← błędny block_id       │
│    "nbt": {...}                                                 │
│  }                                                               │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│  EventProcessor (JVM)                                           │
│  1. Waliduje event → wykrywa błąd                              │
│  2. Loguje błąd do raportu                                     │
│  3. Kontynuuje przetwarzanie (nie przerywa)                    │
│  4. Na końcu: raport z listą błędów                            │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│  Raport końcowy (events_report.json)                           │
│  {                                                               │
│    "total_events": 1500,                                        │
│    "applied": 1498,                                             │
│    "failed": 2,                                                 │
│    "failures": [                                                │
│      {                                                          │
│        "event_index": 42,                                       │
│        "error": "Unknown block: minecraft:invalid_block",       │
│        "pos": [100, 64, 200]                                    │
│      }                                                          │
│    ]                                                            │
│  }                                                               │
└─────────────────────────────────────────────────────────────────┘
```
