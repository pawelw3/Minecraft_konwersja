# Handoff: AE2 Zadanie 3 - Poprawki (Iteracja 1)

## Podsumowanie wprowadzonych poprawek

Wprowadzono poprawki krytyczne (P0) zgodnie z instrukcją:

### 1. Usunięto "wymyślone" pola (`visual`)
- **Problem**: Konwertery dodawały `{'visual': {'rotation': ...}}` które nie istnieje w AE2 1.18.2
- **Rozwiązanie**: 
  - Usunięto wszystkie wystąpienia `visual` z konwerterów
  - Orientacja jest teraz obsługiwana przez **BlockState** (poza NBT BE)
  - Dodano komentarze w kodzie: `# UWAGA: Orientacja jest w BlockState, nie w NBT!`

### 2. Poprawiono przepływ `metadata`
- **Problem**: Metadata nie było przekazywane do konwerterów NBT
- **Rozwiązanie**:
  - Zmieniono sygnaturę `BaseNBTConverter.convert()`:
    ```python
    def convert(self, nbt_1710: Dict[str, Any], block_id: str = None, 
                metadata: int = 0) -> NBTConversionResult
    ```
  - Zaktualizowano wszystkie konwertery (15+ plików)
  - `AE2Converter._convert_nbt()` przekazuje metadata do konwertera

### 3. Urealniono format encoded patterns (usunięto `#c`)
- **Problem**: Używano placeholder `'#c'` dla itemów w patternach
- **Rozwiązanie**:
  - Zastąpiono `'#c'` standardowym `'id'` w `_convert_item_stack_for_pattern()`
  - Dodano TODO do weryfikacji z kodem źródłowym AE2 1.18.2
  - Rozróżnienie crafting vs processing pattern

### 4. Poprawiono `IDResolver`
- **Problem**: `load_from_map()` miał TODO i "zakładał standardowe ID"
- **Rozwiązanie**:
  - Jasna deklaracja: W 1.7.10 z Forge ID są STRINGAMI w NBT chunków
  - Nie ma potrzeby parsowania `level.dat` dla mapowania numerycznego ID
  - Dodano ostrzeżenie o trybie `string_id_only`

## Dodano nowe komponenty

### Warstwa I/O (`world_io/`)
```
world_io/
├── __init__.py
└── block_io.py          # Kontrakty BlockInput1710 / BlockOutput1182
```

**BlockInput1710** - kontrakt wejściowy:
- `block_id: str` - ID bloku (string)
- `metadata: int` - metadata (0-15)
- `x, y, z: int` - pozycja
- `te_nbt: Optional[Dict]` - Tile Entity NBT

**BlockOutput1182** - kontrakt wyjściowy:
- `block_id: str` - ID w 1.18.2
- `blockstate_props: Dict[str, str]` - właściwości BlockState
- `be_nbt: Optional[Dict]` - Block Entity NBT
- `additional_blocks: List[BlockOutput1182]` - dodatkowe bloki

### Rozszerzone testy
Dodano nowe klasy testowe:
- `TestNBTConverters` - testy snapshot NBT (Drive, Storage Cell)
- `TestMetadataFlow` - testy przepływu metadata
- `TestStrictMode` - testy trybu strict z kodami błędów

Łącznie: **14 testów** (wszystkie przechodzą)

## Pliki zmodyfikowane

| Plik | Zmiany |
|------|--------|
| `base_converter.py` | Nowa sygnatura convert(), usunięto 'visual' z IdentityConverter |
| `drive_converter.py` | Usunięto 'visual', dodano dokumentację źródeł |
| `interface_converter.py` | Usunięto '#c', usunięto 'visual', dodano dokumentację |
| `crafting_converter.py` | Usunięto 'visual', poprawiono metadata |
| `storage_cell_converter.py` | Dodano metadata do sygnatury |
| `utility_converters.py` | Usunięto 'visual' z 5 konwerterów |
| `ae2_converter.py` | Przekazywanie metadata, kody błędów |
| `id_resolver.py` | Jasna deklaracja trybu string_id_only |
| `test_ae2_converter.py` | 6 nowych testów (NBT snapshot, metadata, strict) |

## Nowe pliki

| Plik | Opis |
|------|------|
| `world_io/__init__.py` | Eksport warstwy I/O |
| `world_io/block_io.py` | Kontrakty I/O (~250 linii) |
| `HANDOFF_ZADANIE_3_POPRAWKI.md` | Ten plik |

## Kody błędów (wstępne)

Wprowadzono system kodów błędów:
- `AE2C-E-BLOCK-NOT-MAPPED` - brak mapowania bloku
- Format: `AE2C-{E|W}-{COMPONENT}-{DETAIL}`

## Testy

```bash
# Wszystkie testy przechodzą
python -m src.converters.ae2.tests.test_ae2_converter
# Ran 14 tests in 0.001s
# OK
```

## Co zostało do zrobienia (kolejne iteracje)

### Iteracja 2: Urealnienie Interface/Patterns
- Weryfikacja formatu encoded patterns w AE2 1.18.2 (źródła)
- Testy snapshot dla patternów

### Iteracja 3: Urealnienie Storage/Drive
- Weryfikacja kluczy NBT w AE2 1.18.2 (źródła)
- `storage.items` vs `items` itp.

### Iteracja 4: Warstwa I/O świata
- Implementacja parsera MCA (lub integracja z mc_editkit)
- Test integracyjny end-to-end

## Sprawdzenie poprawek

```python
from src.converters.ae2 import AE2Converter
from src.converters.ae2.nbt_converters import DriveConverter

# 1. Brak 'visual' w NBT
conv = DriveConverter()
result = conv.convert({'priority': 5, 'inv': []}, metadata=0)
assert 'visual' not in result.converted_nbt  # OK

# 2. Metadata przekazywana
from src.converters.ae2.nbt_converters import CraftingStorageConverter
cs = CraftingStorageConverter()
result = cs.convert({}, metadata=2)
assert result.converted_nbt['size_variant'] == 2  # OK

# 3. Brak '#c' w patternach
from src.converters.ae2.nbt_converters import InterfaceConverter
intf = InterfaceConverter()
result = intf.convert_to_pattern_provider({
    'patterns': [{'id': 'ae2:encoded_pattern', 'Count': 1, 'tag': {}}]
})
assert '#c' not in str(result.converted_nbt)  # OK
```

---

*Poprawki wprowadzone: 2026-02-01*
*Status: Iteracja 1 (P0) zakończona*
