# HANDOFF: Braki w kodzie konwersji AE2 (do uzupełnienia w Zadaniu 3)

> **Status:** Raport braków do uzupełnienia  
> **Data:** 2026-02-01  
> **Przygotowano po:** Zadaniu 4 (analiza pokrycia)  
> **Cel:** Dokładna lista elementów do implementacji przy powrocie do Zadania 3

---

## Executive Summary

Analiza pokrycia kodu konwersji AE2 wykazała **KRYTYCZNY BRAK**:

| Element | Liczba na mapie | % AE2 | Status pokrycia |
|---------|-----------------|-------|-----------------|
| Bloki podstawowe (Drive, Controller, etc.) | 735 | 32.2% | ✅ Pokryte |
| **BlockCableBus (kable, terminale, części)** | **1,544** | **67.6%** | ❌ **BRAK konwertera** |
| TileChestHungry | 5 | 0.2% | ❓ Prawdopodobnie nie AE2 |
| **RAZEM** | **2,284** | **100%** | **67.6% niepokryte** |

---

## Szczegółowy raport braków

### 1. BlockCableBus (KRYTYCZNE) 🔴

#### Identyfikacja
- **ID 1.7.10:** `BlockCableBus` (w NBT Tile Entity)
- **ID 1.18.2:** `ae2:cable_bus`
- **Liczba instancji na mapie:** 1,544 (67.6% wszystkich TE AE2)
- **Regiony:** Rozproszone we wszystkich instalacjach AE2

#### Obecny stan implementacji
| Komponent | Status | Lokalizacja |
|-----------|--------|-------------|
| Mapowanie bloku | ✅ Zdefiniowane | `block_mappings.py:237-243` |
| Klasa konwertera | ✅ Istnieje | `cable_converter.py:18-78` |
| Rejestracja w AE2Converter | ❌ **BRAK** | `ae2_converter.py:129-167` |

#### Problem techniczny
W `ae2_converter.py` w metodzie `_init_converters()` brakuje wpisu:
```python
'cable_bus': CableConverter(),  # <-- BRAK TEJ LINI
```

Obecnie dla BlockCableBus używany jest `IdentityConverter` (default), który **nie konwertuje struktury multipart**.

#### Struktura NBT 1.7.10 do obsłużenia
```
BlockCableBus NBT:
{
    "id": "BlockCableBus",
    "x": int, "y": int, "z": int,
    "hasRedstone": byte,           # Stan redstone (true/false)
    "def:X": compound,             # Definicja części X (kabel, terminal, itp.)
    "extra:X": compound,           # Dodatkowe dane części X
    # Może zawierać wiele części (multipart)
}
```

Przykłady z mapy:
- `['hasRedstone', 'def:6', 'x', 'y', 'z', 'id', 'extra:6']`
- `['hasRedstone', 'def:6', 'x', 'y', 'z', 'id', 'extra:3', 'def:3', 'extra:6']`

#### Co musi być zaimplementowane

**A. Rejestracja konwertera (PRIORYTET: KRYTYCZNY)**
```python
# ae2_converter.py, metoda _init_converters()
'nbt_converters': {
    # ... istniejące konwertery ...
    'cable_bus': CableConverter(),  # <-- DODAĆ
}
```

**B. Rozszerzenie CableConverter o obsługę multipart (PRIORYTET: WYSOKI)**
Aktualny `CableConverter` obsługuje tylko podstawowe pola. Należy dodać:

1. **Parsowanie części (parts)**
   - Klucze `def:X` gdzie X to numer części
   - Klucze `extra:X` z dodatkowymi danymi
   
2. **Typy części do obsłużenia:**
   - Kable (Glass, Covered, Smart, Dense)
   - Terminale (Crafting Terminal, Pattern Terminal, Interface Terminal)
   - Bus (Import Bus, Export Bus, Storage Bus)
   - Panele (Panel, Illuminated Panel)
   - Akcesoria (Quartz Fiber, Cable Anchor)

3. **Konwersja konfiguracji:**
   - Filtry (filter)
   - Karty upgrade (fuzzy card, inverter card, etc.)
   - Ustawienia (priority, fuzzy mode, etc.)

**C. Mapowanie części 1.7.10 → 1.18.2**
Wiele części zmieniło ID/nazwy między wersjami:
- `PartStorageBus` → `storage_bus`
- `PartImportBus` → `import_bus`
- `PartExportBus` → `export_bus`
- `PartTerminal` → `crafting_terminal`
- `PartPatternTerminal` → `pattern_encoding_terminal`
- itp.

#### Konsekwencje braku konwertera
- ✅ Bloki zostaną przekonwertowane (mapowanie działa)
- ❌ **Utrata konfiguracji** - wszystkie filtry, karty, ustawienia znikną
- ❌ **Utrata połączeń** - części multipart mogą nie zostać poprawnie odtworzone
- ❌ **Sieć ME może nie działać** po konwersji bez ręcznej rekonfiguracji

#### Szacunkowy nakład pracy
- Rejestracja: **5 minut**
- Podstawowa obsługa multipart (bez konfiguracji): **2-3h**
- Pełna obsługa z konwersją filtrów/kart: **8-12h**
- Testowanie: **4-6h**

---

### 2. TileChestHungry (DO WERYFIKACJI) 🟡

#### Identyfikacja
- **ID 1.7.10:** `TileChestHungry`
- **Liczba instancji:** 5 (0.2%)
- **Podejrzenie:** Thaumcraft (Hungry Chest), NIE AE2

#### Analiza
- AE2 ma `BlockChest`/`TileChest` (ME Chest) - to coś innego
- `Hungry Chest` to charakterystyczny blok z Thaumcraft
- Na mapie 1.7.10 jest zainstalowany Thaumcraft

#### Decyzja wymagana
- [ ] Zweryfikować czy to faktycznie Thaumcraft (sprawdzić mod_src 1.7.10)
- [ ] Jeśli Thaumcraft → przekazać do konwertera Thaumcraft
- [ ] Jeśli AE2 → dodać mapowanie (prawdopodobnie `ae2:chest`)

#### Lokalizacja do weryfikacji
```bash
# Sprawdź w kodzie źródłowym 1.7.10:
mod_src/1710/actual_src/1.7.10/AppliedEnergistics2/repo/src/main/java/appeng/tile/
# Czy istnieje TileChestHungry?

# Lub w Thaumcraft:
mod_src/1710/actual_src/1.7.10/Thaumcraft/repo/
```

---

## Lista plików do modyfikacji

### Plik 1: `src/converters/ae2/ae2_converter.py`
**Zmiana:** Dodać rejestrację cable_bus w `_init_converters()`

```python
# Linia ~129-167 (metoda _init_converters)
self.nbt_converters: Dict[str, BaseNBTConverter] = {
    # ... istniejące wpisy ...
    'wireless_ap': WirelessAccessPointConverter(),
    'cable_bus': CableConverter(),  # <-- DODAĆ TUTAJ
    # Default
    'default': IdentityConverter(),
}
```

**Import wymagany:**
```python
# Na górze pliku (~wiersz 48)
from .nbt_converters.cable_converter import CableConverter
```

---

### Plik 2: `src/converters/ae2/nbt_converters/cable_converter.py`
**Zmiana:** Rozszerzyć o obsługę struktury multipart z 1.7.10

**Funkcjonalności do dodania:**

1. **Metoda parsowania części:**
```python
def _parse_parts(self, nbt_1710: Dict) -> List[Dict]:
    """Parsuje części multipart z def:X i extra:X"""
    parts = []
    for key in nbt_1710.keys():
        if key.startswith('def:'):
            part_id = key.split(':')[1]
            part_def = nbt_1710[key]
            part_extra = nbt_1710.get(f'extra:{part_id}', {})
            parts.append({
                'id': part_id,
                'def': part_def,
                'extra': part_extra
            })
    return parts
```

2. **Metoda konwersji części:**
```python
def _convert_part(self, part: Dict) -> Dict:
    """Konwertuje pojedynczą część z 1.7.10 na 1.18.2"""
    part_type = self._identify_part_type(part['def'])
    # ... konwersja typu i konfiguracji
```

3. **Mapowanie typów części:**
```python
PART_MAPPING_1710_TO_1182 = {
    # Kable
    'appeng.parts.networking.PartCable': 'ae2:fluix_cable',
    'appeng.parts.networking.PartDenseCable': 'ae2:dense_cable',
    # Bus
    'appeng.parts.automation.PartImportBus': 'ae2:import_bus',
    'appeng.parts.automation.PartExportBus': 'ae2:export_bus',
    'appeng.parts.automation.PartStorageBus': 'ae2:storage_bus',
    # Terminale
    'appeng.parts.reporting.PartTerminal': 'ae2:crafting_terminal',
    'appeng.parts.reporting.PartPatternTerminal': 'ae2:pattern_encoding_terminal',
    # itp.
}
```

---

### Plik 3: `src/converters/ae2/mappings/item_mappings.py` (opcjonalnie)
**Jeśli** części AE2 są traktowane jako itemy, może być potrzebne mapowanie ID itemów.

---

## Testy wymagane po implementacji

### Test 1: Podstawowa konwersja CableBus
**Cel:** Sprawdzić czy CableBus nie crashuje konwertera
```python
nbt_1710 = {
    'id': 'BlockCableBus',
    'x': 100, 'y': 64, 'z': 100,
    'hasRedstone': False,
    'def:6': {'type': 'cable'},  # uproszczony przykład
}
result = converter.convert(nbt_1710)
assert result.success == True
```

### Test 2: Konwersja z częściami
**Cel:** Sprawdzić czy części są poprawnie parsowane
```python
# CableBus z kablem i terminalem
nbt_1710 = {
    'def:3': {...},  # kabel
    'extra:3': {...},
    'def:6': {...},  # terminal
    'extra:6': {...},
}
# Sprawdź czy obie części zostały wykryte
```

### Test 3: Konwersja filtrów w StorageBus
**Cel:** Sprawdzić czy filtry są zachowane
```python
nbt_1710 = {
    'def:X': {'type': 'storage_bus'},
    'extra:X': {
        'filter': [...],  # lista dozwolonych itemów
        'fuzzyMode': 0,
    }
}
# Sprawdź czy filter został przekonwertowany
```

---

## Checklist przed zamknięciem poprawek

- [ ] `CableConverter` zarejestrowany w `ae2_converter.py`
- [ ] Import `CableConverter` dodany na górze `ae2_converter.py`
- [ ] `CableConverter` parsuje `def:X` i `extra:X`
- [ ] Mapowanie typów części 1.7.10 → 1.18.2 zaimplementowane
- [ ] Konwersja konfiguracji (filtry, karty) zaimplementowana
- [ ] Testy jednostkowe dla CableConverter przechodzą
- [ ] Test na prawdziwym regionie `r.0.0.mca` przechodzi
- [ ] Zweryfikowano `TileChestHungry` (Thaumcraft vs AE2)

---

## Odniesienie do Zadania 3

Zadanie 3 to: **"Napisanie kodu konwersji dla bloków i Tile Entities AE2"**

Do uzupełnienia w ramach Zadania 3:
1. Rejestracja `CableConverter` w `AE2Converter`
2. Rozszerzenie `CableConverter` o obsługę multipart (opcjonalnie - może być częścią Zadania 6)

Decyzja do podjęcia:
- **Opcja A:** Implementacja minimalna (rejestracja) w Zadaniu 3, rozszerzenie w Zadaniu 6
- **Opcja B:** Pełna implementacja CableBus w Zadaniu 3

---

## Dodatkowe uwagi

### Wydajność
Konwersja 1,544 CableBus może być czasochłonna ze względu na:
- Parsowanie wielu części per blok
- Konwersję filtrów (NBT zagnieżdżone)

Rekomendacja: Zaimplementować lazy loading lub caching dla powtarzających się struktur.

### Zależności
Konwersja CableBus może wymagać dostępu do:
- Mapowania ID itemów (dla filtrów)
- Konwertera patternów (jeśli terminal ma patterny)

---

**Raport przygotowany przez:** AI Konwersji AE2  
**Data:** 2026-02-01  
**Wersja:** 1.0 (po analizie Zadania 4)
