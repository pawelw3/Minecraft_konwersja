# 05. Plan migracji istniejących konwerterów

## Obecne konwertery

| Konwerter | Lokalizacja | Stan | Priorytet migracji |
|-----------|-------------|------|-------------------|
| BetterStorage | `src/converters/betterstorage/` | Działa | Wysoki (wzorcowy) |
| BloodMagic | `src/converters/bloodmagic/` | Działa | Średni |
| EnderStorage | `src/converters/enderstorage/` | Działa | Średni |
| GrowthCraft | `src/converters/growthcraft/` | Działa | Średni |
| EnchantingPlus | `src/converters/enchantingplus/` | W budowie | Niski |

## Strategia migracji

### Podejście: Stopniowa migracja z backwards compatibility

```
Faza 1: Stwórz nowy system (src/common/)
         ↓
Faza 2: Migruj BetterStorage jako wzorzec
         ↓
Faza 3: Migruj pozostałe konwertery
         ↓
Faza 4: Usuń stary kod
```

**Zasada:** Stary i nowy system działają równolegle podczas migracji.

## Faza 1: Stworzenie infrastruktury

### 1.1 Struktura katalogów

```bash
# Stwórz nową strukturę
mkdir -p src/common/events
mkdir -p src/common/mappings
mkdir -p src/common/nbt
mkdir -p src/common/adapters
```

### 1.2 Pliki do stworzenia

| Plik | Priorytet | Opis |
|------|-----------|------|
| `src/common/__init__.py` | 1 | Package init |
| `src/common/events/types.py` | 1 | Definicje eventów |
| `src/common/events/emitter.py` | 1 | EventEmitter |
| `src/common/events/serializer.py` | 1 | Serializacja JSON |
| `src/common/events/validator.py` | 2 | Walidacja eventów |
| `src/common/adapters/base_adapter.py` | 2 | Bazowa klasa |
| `src/common/mappings/block_registry.py` | 3 | Rejestr bloków |
| `src/common/mappings/item_registry.py` | 3 | Rejestr itemów |

### 1.3 Testy jednostkowe

```python
# tests/common/test_events.py

import pytest
from src.common.events.types import BlockPos, SetBlockEvent
from src.common.events.emitter import EventEmitter

def test_block_pos():
    pos = BlockPos(100, 64, 200)
    assert pos.to_tuple() == (100, 64, 200)
    assert pos.to_chunk() == (6, 12)
    assert pos.to_region() == (0, 0)

def test_event_emitter_basic():
    emitter = EventEmitter("test")
    emitter.set_block(BlockPos(0, 64, 0), "minecraft:stone")
    assert emitter.event_count == 1
    assert emitter.stats["blocks"] == 1

def test_event_serialization():
    emitter = EventEmitter("test")
    emitter.set_block(BlockPos(0, 64, 0), "minecraft:stone", {"variant": "granite"})

    data = emitter.to_dict()
    assert data["version"] == "2.0"
    assert len(data["events"]) == 1
    assert data["events"][0]["op"] == "set_block"
    assert data["events"][0]["block"] == "minecraft:stone"
```

## Faza 2: Migracja BetterStorage (wzorcowa)

### 2.1 Analiza obecnego kodu

**Pliki do przeanalizowania:**
- `src/converters/betterstorage/batch_converter.py` - główny konwerter
- `src/converters/betterstorage/mapping.py` - mapowania bloków
- `src/converters/betterstorage/nbt_converter.py` - konwersja NBT

**Obecny przepływ:**
```python
# Obecnie:
class BatchConverter:
    def convert(self, source_map):
        for block in scan(source_map):
            result = self.convert_block(block)
            # result to własna struktura ConversionResult
        return ConversionReport(...)  # Własny format raportu
```

### 2.2 Nowy adapter

**Plik:** `src/converters/betterstorage/adapter.py`

```python
from src.common.adapters.base_adapter import BaseModAdapter
from src.common.events.types import BlockPos

class BetterStorageAdapter(BaseModAdapter):
    MOD_NAME = "betterstorage"

    # Przenieś mapowania z mapping.py
    BLOCK_MAPPINGS = {...}

    def can_handle_block(self, block_id: str) -> bool:
        return block_id.startswith("betterstorage:")

    def convert_block(self, pos, block_id, metadata, te_nbt):
        # Logika z batch_converter.py
        ...
```

### 2.3 Refaktoryzacja batch_converter.py

**Przed:**
```python
class BatchConverter:
    def convert(self, source_map, target_map):
        results = []
        for block in self.scan_map(source_map):
            result = self.convert_block(block)
            results.append(result)
        self.write_to_map(target_map, results)
        return Report(results)
```

**Po:**
```python
class BatchConverter:
    def __init__(self):
        self.adapter = BetterStorageAdapter()

    def convert(self, source_map, output_events_path):
        for block in self.scan_map(source_map):
            if self.adapter.can_handle_block(block["id"]):
                self.adapter.convert_block(
                    pos=BlockPos.from_tuple(block["pos"]),
                    block_id=block["id"],
                    metadata=block["metadata"],
                    te_nbt=block.get("te_nbt")
                )

        # Zapisz eventy (zamiast zapisywać bezpośrednio na mapę)
        self.adapter.save_events(output_events_path)
        return self.adapter.stats
```

### 2.4 Mapowanie funkcji

| Stara funkcja | Nowa lokalizacja |
|---------------|------------------|
| `BLOCK_MAPPING` dict | `BetterStorageAdapter.BLOCK_MAPPINGS` |
| `convert_block()` | `BetterStorageAdapter.convert_block()` |
| `_convert_items()` | `BetterStorageAdapter._convert_items()` |
| `_handle_overflow()` | `BetterStorageAdapter._handle_overflow()` |
| `ConversionResult` | Usunięte - używamy eventów |

### 2.5 Test migracji

```bash
# Uruchom stary konwerter
python -m src.converters.betterstorage.batch_converter \
    --source maps/1.7.10/test \
    --output old_results.json

# Uruchom nowy adapter
python -m src.converters.betterstorage.run_adapter \
    --source maps/1.7.10/test \
    --output events/betterstorage_events.json

# Porównaj wyniki (ile bloków, jakie typy, etc.)
python scripts/compare_results.py old_results.json events/betterstorage_events.json
```

## Faza 3: Migracja pozostałych konwerterów

### 3.1 BloodMagic

**Specyfika:**
- Złożona logika run mappings
- Soul Network (globalne dane - specjalny event?)
- Altar multiblock structures

**Mapowanie:**
```python
# src/converters/bloodmagic/adapter.py

class BloodMagicAdapter(BaseModAdapter):
    MOD_NAME = "bloodmagic"

    BLOCK_MAPPINGS = {
        "AWWayofTime:Altar": ("bloodmagic:altar", {}),
        "AWWayofTime:bloodRune": ("bloodmagic:blank_rune", {}),
        # ...
    }

    def convert_block(self, pos, block_id, metadata, te_nbt):
        if "Altar" in block_id:
            return self._convert_altar(pos, metadata, te_nbt)
        elif "Rune" in block_id:
            return self._convert_rune(pos, metadata, te_nbt)
        # ...
```

### 3.2 EnderStorage

**Specyfika:**
- Ender Chest z frequency (kolory)
- Ender Tank

**Mapowanie:**
```python
# src/converters/enderstorage/adapter.py

class EnderStorageAdapter(BaseModAdapter):
    MOD_NAME = "enderstorage"

    def convert_block(self, pos, block_id, metadata, te_nbt):
        if "EnderChest" in block_id:
            return self._convert_ender_chest(pos, metadata, te_nbt)
        elif "EnderTank" in block_id:
            return self._convert_ender_tank(pos, metadata, te_nbt)
```

### 3.3 GrowthCraft

**Specyfika:**
- Fermentation barrels
- Bee boxes
- Brewing equipment

```python
# src/converters/growthcraft/adapter.py

class GrowthCraftAdapter(BaseModAdapter):
    MOD_NAME = "growthcraft"

    BLOCK_MAPPINGS = {
        "grc.fermentBarrel": ("minecraft:barrel", {}),
        "grc.beeBox": ("minecraft:beehive", {}),
        # ...
    }
```

### 3.4 Checklist migracji per konwerter

- [ ] Stwórz `adapter.py` dziedziczący po `BaseModAdapter`
- [ ] Przenieś mapowania bloków do `BLOCK_MAPPINGS`
- [ ] Zaimplementuj `can_handle_block()`
- [ ] Zaimplementuj `convert_block()`
- [ ] Przenieś logikę konwersji NBT
- [ ] Dodaj obsługę warnings
- [ ] Napisz testy jednostkowe
- [ ] Przetestuj na danych testowych
- [ ] Porównaj wyniki ze starym konwerterem
- [ ] Zaktualizuj dokumentację

## Faza 4: Usunięcie starego kodu

### 4.1 Po pełnej migracji

```bash
# Pliki do usunięcia/archiwizacji
src/converters/*/old_converter.py  # stare konwertery
src/converters/*/legacy/           # legacy code

# Pliki do zachowania
src/converters/*/adapter.py        # nowe adaptery
src/converters/*/mappings/         # mapowania (jeśli osobno)
```

### 4.2 Deprecation warnings

```python
# W starych plikach dodaj ostrzeżenia
import warnings

def old_convert_function():
    warnings.warn(
        "old_convert_function is deprecated. Use BetterStorageAdapter instead.",
        DeprecationWarning,
        stacklevel=2
    )
    # ... stara logika
```

## Timeline migracji

```
Tydzień 1:
├─ Dzień 1-2: Stworzenie src/common/events/
├─ Dzień 3-4: Stworzenie src/common/adapters/
└─ Dzień 5: Testy jednostkowe

Tydzień 2:
├─ Dzień 1-3: Migracja BetterStorage
├─ Dzień 4: Testy integracyjne BS
└─ Dzień 5: Code review

Tydzień 3:
├─ Dzień 1-2: Migracja BloodMagic
├─ Dzień 3-4: Migracja EnderStorage
└─ Dzień 5: Migracja GrowthCraft

Tydzień 4:
├─ Dzień 1-2: Testy wszystkich adapterów
├─ Dzień 3: Dokumentacja
├─ Dzień 4: Usunięcie starego kodu
└─ Dzień 5: Final review
```

## Metryki sukcesu

| Metryka | Cel |
|---------|-----|
| Pokrycie testami | >80% nowego kodu |
| Kompatybilność | 100% bloków konwertowanych jak wcześniej |
| Wydajność | Generowanie eventów ≤ czas starej konwersji |
| Rozmiar eventów | JSON ≤ 2x rozmiar starego output |

## Rollback plan

W przypadku problemów:
1. Stary kod pozostaje w `src/converters/*/legacy/`
2. Flaga `--use-legacy` uruchamia stary konwerter
3. Możliwość stopniowego rollback per konwerter
