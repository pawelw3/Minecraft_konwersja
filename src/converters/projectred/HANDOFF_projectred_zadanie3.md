# Handoff: ProjectRed - Zadanie 3 (Kod konwersji bloków i TileEntity)

## Podsumowanie sesji

Wykonano **Zadanie 3** konwersji moda ProjectRed.
Zadanie polegało na napisaniu **kodu konwersji dla bloków i TileEntity/BlockEntity** ProjectRed z wersji 1.7.10 do 1.18.2.

Kod został napisany zgodnie z wytycznymi **SKILL.md**:
- Implementacja oparta na faktycznym kodzie źródłowym (Source mapping w każdym konwerterze)
- Orientacja i warianty w `blockstate_props`, nie w NBT
- Metadata jako parametr wejściowy
- Fail-safe z kodami błędów (PR-E-*, PR-W-*)

---

## Ukończono

- [x] Analiza kodu źródłowego 1.7.10 (readFromNBT/writeToNBT)
- [x] Analiza kodu źródłowego 1.18.2 (load/saveAdditional)
- [x] Stworzenie struktury folderów konwertera
- [x] Napisanie `base_converter.py` z bazową klasą konwertera
- [x] Napisanie `block_mappings.py` z mapowaniem 50+ bloków
- [x] Napisanie konwerterów NBT dla maszyn Expansion (10 konwerterów)
- [x] Napisanie konwerterów NBT dla multipart - bramki i przewody (8 konwerterów)
- [x] Napisanie głównego `projectred_converter.py`
- [x] Napisanie testów (40 testów - wszystkie przechodzą)

---

## Nowe pliki

| Plik | Rozmiar | Opis |
|------|---------|------|
| `src/converters/projectred/__init__.py` | 1.4 KB | Moduł główny |
| `src/converters/projectred/projectred_converter.py` | 12.5 KB | Główny konwerter |
| `src/converters/projectred/mappings/__init__.py` | 0.8 KB | Eksport mapowań |
| `src/converters/projectred/mappings/block_mappings.py` | 10.2 KB | Mapowania bloków |
| `src/converters/projectred/nbt_converters/__init__.py` | 1.6 KB | Eksport konwerterów NBT |
| `src/converters/projectred/nbt_converters/base_converter.py` | 6.8 KB | Bazowa klasa konwertera |
| `src/converters/projectred/nbt_converters/expansion_converters.py` | 14.2 KB | Konwertery maszyn Expansion |
| `src/converters/projectred/nbt_converters/multipart_converters.py` | 13.8 KB | Konwertery bramek i przewodów |
| `src/converters/projectred/tests/__init__.py` | 0.1 KB | Moduł testów |
| `src/converters/projectred/tests/test_projectred_converter.py` | 14.5 KB | Testy jednostkowe |

**Łącznie:** ~76 KB kodu konwersji + testów

---

## Szczegóły implementacji

### Mapowanie bloków (block_mappings.py)

Zaimplementowano mapowanie dla wszystkich bloków ProjectRed z uwzględnieniem metadata:

| Kategoria | Liczba wariantów | Status |
|-----------|------------------|--------|
| machine1 (Expansion) | 2 | 1 usunięty, 1 przeniesiony do Core |
| machine2 (Expansion) | 13 | 4 usunięte, 1 zastąpiony |
| ore (Exploration) | 7 | 1 zastąpiony przez vanilla copper |
| stone (Exploration) | 12 | 1 zastąpiony przez vanilla copper |
| icBlock (Fabrication) | 2 | 1 zastąpiony przez 3 nowe stoły |
| frame (Expansion) | 1 | OK |
| lamp (Illumination) | 16 kolorów | Struktura zmieniona |

### Konwertery NBT (expansion_converters.py)

| Konwerter | 1.7.10 Tagi | 1.18.2 Tagi | Kluczowe zmiany |
|-----------|-------------|-------------|-----------------|
| BatteryBoxConverter | `storage` | `storage`, `vCap`, `iCap`, `chargeFlow` | Dodane pola PowerConductor |
| ChargingBenchConverter | `storage`, `srr` | `storage`, `chargeSlot` | `srr` → `chargeSlot` |
| ElectrotineGeneratorConverter | `storage`, `btime` | `stored`, `burnTime` | Zmiana nazw! |
| FrameMotorConverter | `ch`, `pow` | `powered`, `vCap`, `iCap` | Połączone w `powered` |
| BlockBreakerConverter | (brak) | `queue`, `schedTick`, `side`, `powered`, `active` | Nowe pola w 1.18.2 |
| ProjectBenchConverter | inventory | `plan_inv`, `crafting_inv`, `storage_inv`, `plan_crafting_inv` | Rozdzielone inwentarze |
| AutoCrafterConverter | `cyt1`, `cyt2` | `remaining_work`, `total_work`, `working` | Zmiana systemu timerów |

### Konwertery Multipart (multipart_converters.py)

| Konwerter | Typ części | Kluczowe różnice |
|-----------|-----------|------------------|
| GatePartConverter | pr_sgate, pr_igate, pr_agate, pr_bgate | `subID` w 1.7.10 → typ bloku w 1.18.2 |
| RedwirePartConverter | pr_redwire | Dodane `connMap`, `side` w 1.18.2 |
| BundledCablePartConverter | pr_bundled | `colour` w 1.7.10 → typ bloku w 1.18.2 |

**Kluczowe odkrycie:** W 1.7.10 typ bramki jest w `subID` (Byte) w NBT. W 1.18.2 typ bramki określa sam block ID - nie ma `subID` w NBT!

---

## Testy

Wszystkie 40 testów przechodzi:

```
============================= 40 passed in 0.31s ==============================
```

Pokrycie testów:
- Mapowanie bloków (6 testów)
- BatteryBox (4 testy)
- ChargingBench (2 testy)
- ElectrotineGenerator (2 testy)
- FrameMotor (2 testy)
- GatePart (3 testy)
- Redwire (2 testy)
- BundledCable (2 testy)
- Generowanie ID bramek (3 testy)
- Generowanie ID przewodów (3 testy)
- Integracja (7 testów)
- Przypadki brzegowe (4 testy)

---

## Zmiany NBT między wersjami

### Kluczowe różnice wykryte podczas analizy kodu źródłowego:

1. **BatteryBox:**
   - 1.7.10: `storage` (Integer)
   - 1.18.2: `storage` (int), `vCap` (double), `iCap` (double), `chargeFlow` (int)

2. **ElectrotineGenerator:**
   - 1.7.10: `storage` (Integer), `btime` (Short)
   - 1.18.2: `stored` (int) [zmiana nazwy!], `burnTime` (int) [zmiana nazwy i typu!]

3. **ChargingBench:**
   - 1.7.10: `storage`, `srr` (Byte)
   - 1.18.2: `storage`, `chargeSlot` (byte) [zmiana nazwy!]

4. **FrameMotor/FrameActuator:**
   - 1.7.10: `ch` (Boolean), `pow` (Boolean)
   - 1.18.2: `powered` (boolean), `vCap`, `iCap`, `chargeFlow`

5. **Bramki (GatePart):**
   - 1.7.10: `orient`, `subID`, `shape`, `connMap`, `nolegacy`, `schedTime`
   - 1.18.2: `orient`, `shape`, `connMap`, `schedTime` [BEZ subID!]

---

## Source Mapping

Każdy konwerter zawiera dokładne odniesienia do kodu źródłowego:

```python
class BatteryBoxConverter(BaseNBTConverter):
    """
    Source mapping:
    1.7.10 NBT:
    - storage (Integer): energia przechowywana (0-8000)
    - Inventory: przez saveInv() (opcjonalne)

    1.18.2 NBT:
    - storage (int): energia przechowywana
    - inventory (CompoundTag): inwentarz
    - vCap (double): napięcie kondensatora (z PowerConductor)
    - iCap (double): prąd kondensatora (z PowerConductor)
    - chargeFlow (int): przepływ ładunku
    """

    SOURCE_1710 = "expansion/TileBatteryBox.scala:103-111"
    SOURCE_1182 = "expansion/tile/BatteryBoxBlockEntity.java:53-67"
```

---

## Użycie

```python
from src.converters.projectred import ProjectRedConverter

converter = ProjectRedConverter()

# Konwersja bloku
result = converter.convert_block(
    "ProjRed|Expansion:projectred.expansion.machine2",
    nbt_1710={"storage": 5000},
    metadata=5,  # BatteryBox
    position=(100, 64, 100)
)

print(result.converted.block_id_1182)  # projectred_expansion:battery_box
print(result.converted.nbt_1182)       # {'storage': 5000, 'vCap': 50.0, ...}

# Konwersja bramki
result = converter.convert_multipart(
    "pr_sgate",
    nbt_1710={"orient": 0x23, "subID": 3, "shape": 0, "connMap": 0xF, "schedTime": 0},
    position=(100, 64, 101)
)

print(result.converted.block_id_1182)  # projectred_integration:and_gate
```

---

## Następne kroki (Zadanie 4+)

1. [ ] Integracja z JVM/worker (hephAIstos) dla odczytu/zapisu świata
2. [ ] Weryfikacja na prawdziwej mapie z blokami ProjectRed
3. [ ] Obsługa przypadków specjalnych:
   - IC Printer → 3 nowe stoły (plotting, lithography, packaging)
   - Usunięte bloki → sugestie zamienników
4. [ ] Optymalizacja batch processing dla dużych ilości bloków

---

## Uwagi techniczne

- Kod zgodny z **SKILL.md** - każdy konwerter ma Source mapping
- Orientacja przekazywana w `blockstate_props`, nie w NBT
- Metadata jako parametr wejściowy, nie wyciągana z NBT
- Fail-safe z kodami błędów (PR-E-*, PR-W-*)
- Symulacje z Zadania 2 zachowane w `src/converters/projectred/simulations/`

---

**Status:** Zadanie 3 ukończone - gotowe do przeglądu i akceptacji
**Data:** 2026-02-02
**Testy:** 40/40 passed
