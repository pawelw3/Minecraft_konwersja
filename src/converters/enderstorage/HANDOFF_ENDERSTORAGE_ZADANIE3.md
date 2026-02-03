# Handoff: EnderStorage - Zadanie 3

## Podsumowanie sesji

Wykonano kompletną implementację kodu konwersji NBT dla moda EnderStorage. Konwerter obsługuje wszystkie kluczowe funkcjonalności: mapowanie bloków (skrzynie i zbiorniki), konwersję frequency (int -> EnumColour), konwersję Tile Entities (TileEnderChest i TileEnderTank) oraz obsługę itemów (EnderPouch). Wszystkie testy jednostkowe przechodzą pomyślnie (22 testy).

## Ukończono

- [x] Implementacja kodu konwersji NBT
  - [x] Konwerter `int freq` → `Frequency` object (z 16 kolorami)
  - [x] Konwerter `String owner` → `UUID` (framework gotowy, lookup do zaimplementowania w zadaniu 5)
  - [x] Konwerter `ItemStack[]` (1.7.10) → `ItemStack[]` (1.18.2) z obsługą damage w tag
  
- [x] Mapowanie Tile Entities
  - [x] `TileEnderChest` (1.7.10) → `TileEnderChest` (1.18.2)
  - [x] `TileEnderTank` (1.7.10) → `TileEnderTank` (1.18.2)
  
- [x] Mapowanie bloków
  - [x] `EnderStorage:blockEnderStorage:0` → `enderstorage:ender_chest`
  - [x] `EnderStorage:blockEnderStorage:1` → `enderstorage:ender_tank`
  
- [x] Obsługa Ender Pouch (item)
  - [x] Konwersja damage (freq) → NBT Frequency
  
- [x] Testy jednostkowe konwertera (22 testy, wszystkie PASS)

---

## Nowe pliki

### Struktura projektu

```
src/converters/enderstorage/
├── __init__.py                              # Eksport głównych klas
├── enderstorage_converter.py               # Główny konwerter
├── mappings/
│   └── __init__.py                         # Mapowania bloków, itemów, kolorów
├── nbt_converters/
│   ├── __init__.py                         # Eksport konwerterów NBT
│   ├── base_converter.py                   # Bazowa klasa konwertera
│   ├── chest_converter.py                  # Konwerter TileEnderChest
│   └── tank_converter.py                   # Konwerter TileEnderTank
└── tests/
    ├── __init__.py                         # Eksport testów
    └── test_enderstorage_converter.py      # Testy jednostkowe (22 testy)
```

### Szczegóły plików

| Plik | Linie | Opis |
|------|-------|------|
| `mappings/__init__.py` | 275 | Mapowania bloków, itemów, klasa Frequency, EnumColour |
| `nbt_converters/base_converter.py` | 190 | Bazowa klasa z obsługą ItemStack, inventory, frequency |
| `nbt_converters/chest_converter.py` | 100 | Konwerter skrzyni (freq, rotation, Items) |
| `nbt_converters/tank_converter.py` | 98 | Konwerter zbiornika (freq, pressure_state) |
| `enderstorage_converter.py` | 325 | Główny konwerter z obsługą bloków i itemów |
| `tests/test_enderstorage_converter.py` | 380 | 22 testy jednostkowe |

---

## Kluczowe klasy i funkcje

### 1. Frequency (mappings/__init__.py)

```python
@dataclass
class Frequency:
    left: EnumColour = EnumColour.WHITE
    middle: EnumColour = EnumColour.WHITE  
    right: EnumColour = EnumColour.WHITE
    owner: Optional[uuid.UUID] = None
    
    def to_int(self) -> int: ...
    @classmethod
    def from_int(cls, freq_int: int) -> 'Frequency': ...
    def to_nbt_1182(self) -> Dict[str, any]: ...
```

**Konwersja int (1.7.10) ↔ Frequency (1.18.2):**
```python
# 1.7.10: int freq = (left << 8) | (middle << 4) | right
freq_int = 3803  # RED-GREEN-BLUE

# 1.18.2: Frequency(left=RED, middle=GREEN, right=BLUE)
freq = Frequency.from_int(3803)
# freq.left = EnumColour.RED      # (3803 >> 8) & 0xF = 14
# freq.middle = EnumColour.GREEN  # (3803 >> 4) & 0xF = 13
# freq.right = EnumColour.BLUE    # 3803 & 0xF = 11
```

### 2. EnderStorageConverter (enderstorage_converter.py)

```python
converter = EnderStorageConverter()

# Konwersja bloku skrzyni
result = converter.convert_block(
    block_id="EnderStorage:blockEnderStorage",
    metadata=0,  # 0=chest, 1=tank
    nbt={"freq": 3803, "owner": "global", "rotation": 2}
)

# Konwersja itemu EnderPouch
result = converter.convert_item(
    item_id="EnderStorage:enderPouch",
    damage=3803  # damage = freq w 1.7.10
)
```

### 3. Konwertery NBT

| Konwerter | Źródło | Cel | Kluczowe pola |
|-----------|--------|-----|---------------|
| `EnderChestNBTConverter` | `TileEnderChest` | `enderstorage:ender_chest` | Frequency, rotation, Items |
| `EnderTankNBTConverter` | `TileEnderTank` | `enderstorage:ender_tank` | Frequency, pressure_state |

---

## Formaty NBT

### TileEnderChest

**1.7.10:**
```json
{
  "freq": 1193,
  "owner": "global",
  "rotation": 2,
  "Items": [
    {"Slot": 0, "id": "minecraft:diamond", "Count": 32, "Damage": 0}
  ]
}
```

**1.18.2:**
```json
{
  "id": "enderstorage:ender_chest",
  "Frequency": {
    "left": "yellow",
    "middle": "purple",
    "right": "cyan"
  },
  "rotation": 2,
  "Items": [
    {"Slot": 0, "id": "minecraft:diamond", "Count": 32}
  ],
  "__original_freq": 1193,
  "__original_owner": "global"
}
```

### TileEnderTank

**1.7.10:**
```json
{
  "freq": 100,
  "owner": "global",
  "invert_redstone": false
}
```

**1.18.2:**
```json
{
  "id": "enderstorage:ender_tank",
  "Frequency": {
    "left": "white",
    "middle": "orange",
    "right": "magenta"
  },
  "pressure_state": {
    "invert_redstone": false
  },
  "__original_freq": 100,
  "__original_owner": "global"
}
```

---

## Mapowania bloków

| ID 1.7.10 | Metadata | ID 1.18.2 |
|-----------|----------|-----------|
| `EnderStorage:blockEnderStorage` | 0 | `enderstorage:ender_chest` |
| `EnderStorage:blockEnderStorage` | 1 | `enderstorage:ender_tank` |

## Mapowania itemów

| ID 1.7.10 | ID 1.18.2 |
|-----------|-----------|
| `EnderStorage:enderPouch` | `enderstorage:ender_pouch` |

---

## Testy jednostkowe

### Wyniki testów

```
======================================================================
Ran 22 tests in 0.002s

OK
```

### Lista testów

| Test | Opis |
|------|------|
| `test_int_to_frequency_white` | Konwersja int 0 (WHITE-WHITE-WHITE) |
| `test_int_to_frequency_red_green_blue` | Konwersja RGB (3803) |
| `test_frequency_to_int` | Konwersja Frequency -> int |
| `test_roundtrip_conversion` | Pełna konwersja int -> Frequency -> int |
| `test_frequency_to_nbt_1182` | Format NBT 1.18.2 |
| `test_frequency_from_nbt_1182` | Parsowanie NBT 1.18.2 |
| `test_all_colours` | Wszystkie 16 kolorów |
| `test_chest_block_mapping` | Mapowanie skrzyni |
| `test_tank_block_mapping` | Mapowanie zbiornika |
| `test_enderpouch_item_mapping` | Mapowanie EnderPouch |
| `test_basic_conversion` (chest) | Podstawowa konwersja skrzyni |
| `test_conversion_with_items` | Skrzynia z itemami |
| `test_conversion_with_damage` | Item z damage w tag |
| `test_basic_conversion` (tank) | Podstawowa konwersja zbiornika |
| `test_invert_redstone_conversion` | Stan ciśnieniowy |
| `test_convert_chest_block` | Pełna konwersja bloku skrzyni |
| `test_convert_tank_block` | Pełna konwersja bloku zbiornika |
| `test_convert_block_without_nbt` | Konwersja bez NBT |
| `test_invalid_block` | Obsługa błędnego bloku |
| `test_stats_tracking` | Śledzenie statystyk |
| `test_convert_enderpouch` | Konwersja EnderPouch RGB |
| `test_convert_enderpouch_white` | Konwersja EnderPouch WHITE |

---

## Użycie konwertera

### Podstawowe użycie

```python
from src.converters.enderstorage import EnderStorageConverter

# Utwórz konwerter
converter = EnderStorageConverter()

# Konwertuj blok skrzyni
result = converter.convert_block(
    block_id="EnderStorage:blockEnderStorage",
    metadata=0,
    nbt={
        "freq": 3803,
        "owner": "global",
        "rotation": 2,
        "Items": [
            {"Slot": 0, "id": "minecraft:diamond", "Count": 64}
        ]
    }
)

if result.success:
    print(f"Nowe ID: {result.block_id_1182}")
    print(f"Nowe NBT: {result.nbt_1182}")
```

### Funkcje pomocnicze

```python
from src.converters.enderstorage import (
    convert_enderstorage_te,
    convert_enderstorage_item,
    Frequency,
    EnumColour
)

# Szybka konwersja TE
new_id, new_nbt, warnings = convert_enderstorage_te(
    te_id="EnderStorage:blockEnderStorage",
    nbt={"freq": 100, "owner": "global"},
    metadata=0
)

# Szybka konwersja itemu
new_id, new_nbt, warnings = convert_enderstorage_item(
    item_id="EnderStorage:enderPouch",
    damage=3803
)

# Praca z Frequency
freq = Frequency.from_int(3803)
print(freq.left.name)  # "RED"
```

---

## Ograniczenia i TODO

### Znane ograniczenia

1. **Lookup nazw graczy → UUID**
   - W 1.7.10 owner to String ("global" lub nazwa gracza)
   - W 1.18.2 owner to UUID (lub null dla global)
   - Obecnie zawsze konwertujemy do global (null)
   - **TODO w zadaniu 5**: Implementacja lookupu z `playerdata/`

2. **Ciecze w zbiornikach**
   - Dane cieczy są współdzielone przez backend storage
   - Nie są przechowywane w NBT bloku, tylko w EnderStorageManager
   - Konwersja wymaga dostępu do danych świata (world data)

3. **Rotacja**
   - W 1.7.10: pole `rotation` w NBT (0-3)
   - W 1.18.2: `facing` w BlockState (nie w NBT BE)
   - Konwerter zachowuje rotation w NBT, ale docelowo powinno być w blockstate

---

## Następne kroki (Zadanie 4)

1. [ ] Sprawdzenie pokrycia na mapie głównej
   - Wyszukanie wszystkich bloków EnderStorage na mapie 1710
   - Weryfikacja czy konwersja pokrywa wszystkie przypadki
   - Zliczenie ile jest skrzyń vs zbiorników
   - Sprawdzenie jakie kolory/frequency są używane

2. [ ] Implementacja lookupu nazw graczy → UUID
   - Jeśli na mapie są personalne skrzynie/zbiorniki
   - Wczytanie danych z `playerdata/` lub `usernamecache.json`

3. [ ] Analiza EnderPouch w inventory graczy
   - Wyszukanie EnderPouch w `playerdata/*.dat`
   - Weryfikacja konwersji damage → Frequency NBT

---

## Zmodyfikowane pliki

Brak - wszystkie pliki są nowe.

---

## Testowanie

### Uruchomienie testów

```bash
# Z katalogu głównego projektu
python src/converters/enderstorage/tests/test_enderstorage_converter.py

# Lub używając pytest
pytest src/converters/enderstorage/tests/ -v
```

### Sprawdzenie importów

```python
# Test importów
from src.converters.enderstorage import EnderStorageConverter
from src.converters.enderstorage import EnumColour, Frequency
from src.converters.enderstorage.nbt_converters import EnderChestNBTConverter

print("Wszystkie importy działają!")
```

---

*Data utworzenia: 2026-02-03*  
*Zadanie 3 zakończone - 22 testy PASS*
