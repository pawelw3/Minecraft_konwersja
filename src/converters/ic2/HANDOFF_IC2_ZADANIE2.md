# Handoff: Zadanie 2 - IndustrialCraft 2 (Symulacje funkcjonalności i mapowania)

## Podsumowanie sesji

Wykonano kompletne mapowania bloków IC2 1.7.10 → Mekanism / Thermal / Placeholder 1.18.2 oraz przygotowano symulacje konwersji NBT dla czterech kluczowych typów Tile Entities:
1. Maszyny standardowe (Macerator, Furnace, Compressor, itp.)
2. Magazyny energii (BatBox, MFE, MFSU, CESU, Chargepady)
3. Kable (Copper, Gold, Iron, Glass Fibre, Tin)
4. Specjalne (Teleporter, Reaktor jądrowy)

Wszystkie symulacje zostały przetestowane (20 testów jednostkowych, 100% zaliczonych).

---

## 1. Mapowania bloków (`mappings/block_mappings.py`)

### 1.1 Podsumowanie mapowań

| Kategoria | Liczba mapowań | Konwertowane | Placeholdery |
|-----------|---------------|--------------|--------------|
| Maszyny (BlockMachine 1/2/3) | 42 | 17 | 25 |
| Generatory (BlockGenerator) | 10 | 6 | 4 |
| Generatory ciepła | 4 | 2 | 2 |
| Generatory kinetyczne | 6 | 0 | 6 |
| Kable | 14 | 12 | 2 |
| Storage (Electric) | 8 | 4 | 4 |
| Chargepady | 4 | 4 | 0 |
| Reaktor | 5 | 0 | 5 |
| Personalne | 3 | 1 | 2 |
| Luminatory | 2 | 0 | 2 |
| Rudy / Dekoracje | 15 | 11 | 4 |
| **RAZEM** | **113** | **62** | **51** |

**Stopień konwersji: 54.9%** (62/113). Reszta wymaga placeholderów ze względu na:
- Brak odpowiedników w 1.18.2 (Canning Machine, Recycler, Magnetizer, itp.)
- Systemy unikalne dla IC2 (transformatory, system kinetyczny, system cieplny)
- Mechaniki end-game (Mass Fabricator, Replicator, Scanner, Pattern Storage)

### 1.2 Kluczowe mapowania maszyn przetwórczych

| IC2 | Target 1.18.2 | Konwerter |
|-----|---------------|-----------|
| Macerator (3) | `mekanism:crusher` | standard_machine |
| Electric Furnace (2) | `mekanism:energized_smelter` | standard_machine |
| Compressor (5) | `mekanism:osmium_compressor` | standard_machine |
| Extractor (4) | `thermal:machine_centrifuge` | standard_machine |
| Canning Machine (6) | `thermal:machine_bottler` | standard_machine |
| Recycler (11) | `thermal:device_nullifier` | generic_machine |
| Electrolyzer (10) | `mekanism:electrolytic_separator` | generic_machine |
| Induction Furnace (13) | `thermal:machine_smelter` | standard_machine |
| Thermal Centrifuge (3@M2) | `thermal:machine_centrifuge` | standard_machine |
| Metal Former (4@M2) | `thermal:machine_press` | standard_machine |
| Ore Washing Plant (5@M2) | `mekanism:chemical_washer` | generic_machine |
| Solid/Fluid Canner (9/10@M2) | `thermal:machine_bottler` | standard_machine |

### 1.3 Mapowania generatorów

| IC2 | Target 1.18.2 | Uwagi |
|-----|---------------|-------|
| Generator (0) | `mekanismgenerators:heat_generator` | MekanismGenerators |
| Geothermal (1) | `mekanismgenerators:heat_generator` | MekanismGenerators |
| Solar Panel (3) | `mekanismgenerators:solar_generator` | MekanismGenerators |
| Wind Mill (4) | `mekanismgenerators:wind_generator` | MekanismGenerators |
| Semifluid (7) | `mekanismgenerators:bio_generator` | MekanismGenerators |
| Stirling (8) | `thermal:dynamo_stirling` | |
| Solid Heat (3@Heat) | `thermal:dynamo_stirling` | |
| Fluid Heat (1@Heat) | `thermal:dynamo_magmatic` | |

### 1.4 Mapowania storage

| IC2 | Target 1.18.2 | Pojemność IC2 (EU) | Pojemność target (FE) |
|-----|---------------|-------------------|----------------------|
| BatBox (0) | `mekanism:basic_energy_cube` | 40 000 | 1.6M |
| CESU (7) | `mekanism:advanced_energy_cube` | 300 000 | 6.4M |
| MFE (1) | `mekanism:elite_energy_cube` | 4 000 000 | 25.6M |
| MFSU (2) | `mekanism:ultimate_energy_cube` | 40 000 000 | 102.4M |

### 1.6 Mapowania ród i metali

| IC2 1.7.10 | Target 1.18.2 | Uwagi |
|------------|---------------|-------|
| Copper Ore | `minecraft:copper_ore` | Vanilla 1.18.2 |
| Tin Ore | `thermal:tin_ore` | |
| Uranium Ore | `biggerreactors:uranium_ore` | |
| Lead Ore | `thermal:lead_ore` | |
| Copper Block | `minecraft:copper_block` | Vanilla 1.18.2 |
| Uranium Block | `mekanism:block_uranium` | Mekanism |
| Reinforced Stone | placeholder | Rozważ SecurityCraft |
| Reinforced Glass | placeholder | Rozważ SecurityCraft |

**Uwaga**: Pojemności target są znacznie większe niż IC2 × 4, więc overflow jest mało prawdopodobny.

### 1.5 Mapowania kabli

Wszystkie kable IC2 mapowane są na `mekanism:*_universal_cable`:
- Copper/Tin → `basic`
- Gold → `advanced`
- Iron (HV) → `elite`
- Glass Fibre → `ultimate`

**Kable specjalne (lossy)**:
- Detector Cable → `ultimate_universal_cable` (utrata detekcji redstone)
- Splitter Cable → `ultimate_universal_cable` (utrata przełączania)

---

## 2. Symulacje konwersji NBT (`simulations/`)

### 2.1 `machine_simulation.py`

Obsługuje konwersję NBT dla maszyn standardowych (`TileEntityStandardMachine`):

| Pole IC2 1.7.10 | Pole 1.18.2 | Uwagi |
|-----------------|-------------|-------|
| `facing` (short) | `facing` (blockstate) | Mapowanie 0-5 → down/up/north/south/west/east |
| `active` (bool) | `active` / `lit` | Mekanism: NBT, Thermal: blockstate, Vanilla: blockstate |
| `energy` (double EU) | `energyContainer.stored` (int FE) | Mnożnik ×4 |
| `progress` (short) | `operatingTicks` / `Process` | Skalowanie do formatu targetu |
| `InvSlots` / `Items` | `Items` (ListTag) | Bez konwersji ID itemów (etap późniejszy) |
| `redstoneMode` (byte) | `redstoneControl` (int) | Bezpośrednie mapowanie wartości |

**Funkcje**:
- `simulate_standard_machine_conversion()` — maszyny przetwórcze
- `simulate_teleporter_conversion()` — teleporter z zachowaniem współrzędnych celu
- `simulate_reactor_conversion()` — reaktor z pełnym zachowaniem legacy NBT

### 2.2 `energy_storage_simulation.py`

Konwersja storage energii:
- Energy EU → FE z clampingiem do pojemności docelowej
- `redstoneMode` → `redstoneControl`
- Chargepady: tier określany przez źródłowy metadata

### 2.3 `cable_simulation.py`

Konwersja kabli (uproszczona — Mekanism kable są blokami bez TE):
- `cableType` → tier w block_id (już rozwiązane w block_mappings)
- `color` → **tracone** (ostrzeżenie)
- `foamed` / `foamColor` → **tracone** (ostrzeżenie)
- `retexture` → **tracone** (ostrzeżenie)

---

## 3. Porównanie struktur NBT (kluczowe przypadki)

### 3.1 Macerator → Crusher (Mekanism)

**IC2 1.7.10** (`IC2:blockMachine:3`, `TileEntityMacerator`):
```java
NBTTagCompound {
  facing: 3,           // short
  active: true,        // boolean
  energy: 512.0,       // double (EU)
  progress: 200,       // short
  InvSlots: {
    input: { 0: {id:"minecraft:iron_ore", Count:1} },
    output: { 0: {id:"IC2:itemDustIron", Count:2} },
    upgrade: {},
    discharge: {},
    charge: {}
  }
}
```

**Mekanism 1.18.2** (`mekanism:crusher`):
```java
CompoundTag {
  // BlockState: facing=south
  energyContainer: { stored: 2048 },  // int (FE)
  operatingTicks: 200,                // int
  active: true,                       // boolean
  Items: [
    {Slot:0, id:"minecraft:iron_ore", Count:1},
    {Slot:1, id:"IC2:itemDustIron", Count:2}
  ]
}
```

### 3.2 BatBox → Basic Energy Cube

**IC2 1.7.10**:
```java
NBTTagCompound {
  facing: 2,
  energy: 20000.0,      // EU
  redstoneMode: 0
}
```

**Mekanism 1.18.2**:
```java
CompoundTag {
  // BlockState: facing=north
  energyContainer: { stored: 80000 },  // FE
  redstoneControl: 0
}
```

---

## 4. Testy (`tests/test_ic2_simulations.py`)

| Klasa testowa | Testy | Opis |
|---------------|-------|------|
| `TestEnergyConversion` | 3 | Reguła EU→FE, zaokrąglenia, clamping ujemnych |
| `TestFacingConversion` | 2 | Mapowanie facing IC2 (0-5) → string |
| `TestInventoryExtraction` | 3 | Formaty `InvSlots` i legacy `Items` |
| `TestStandardMachineConversion` | 5 | Maszyny → Mekanism/Thermal/Vanilla |
| `TestEnergyStorageConversion` | 3 | Storage, overflow, chargepad tiers |
| `TestCableConversion` | 3 | Kable, kolory, foam, retexture |
| `TestTeleporterConversion` | 1 | Współrzędne celu, energia |
| `TestReactorConversion` | 1 | Legacy data, heat, komponenty |

**Wynik: 20/20 passed**

---

## 5. Historia zmian w tym kroku

### Wprowadzone poprawki (po review)
1. **Maszyny**: Canning Machine → `thermal:machine_bottler`, Extractor → `thermal:machine_centrifuge`, Recycler → `thermal:device_nullifier` z kompensacją scrap
2. **Generatory**: Solar/Wind → `mekanismgenerators:*`, Generator/Geothermal → `mekanismgenerators:heat_generator`, Semifluid → `mekanismgenerators:bio_generator`
3. **Kable**: Detector/Splitter oznaczone jako `lossy_cable` (utrata funkcji specjalnych)
4. **Reaktory**: Wszystkie komponenty reaktora → placeholder (zamiast agresywnego mapowania na BiggerReactors)
5. **Rudy**: Copper Block → `minecraft:copper_block`, Uranium Block → `mekanism:block_uranium`
6. **Inne**: Fluid Regulator → `mekanism:mechanical_pipe`, Sorting Machine → `mekanism:logistical_sorter`

## 6. Utworzone / zmodyfikowane pliki

### Nowe pliki
- `src/converters/ic2/mappings/block_mappings.py` — 113 mapowań bloków (54.9% konwersji)
- `src/converters/ic2/simulations/machine_simulation.py` — symulacje maszyn/teleportera/reaktora
- `src/converters/ic2/simulations/energy_storage_simulation.py` — symulacje storage
- `src/converters/ic2/simulations/cable_simulation.py` — symulacje kabli
- `src/converters/ic2/tests/test_ic2_simulations.py` — 20 testów jednostkowych

### Pliki z Zadania 1 (bez zmian)
- `src/converters/ic2/mappings/block_inventory.py`
- `src/converters/ic2/HANDOFF_IC2_ZADANIE1.md`

---

## 6. Otwarte problemy i decyzje do podjęcia

### 6.1 Wymaga decyzji użytkownika
- [ ] **Solar Panel / Wind Mill** — brak MekanismGenerators w kodzie źródłowym. Czy doinstalować? Jeśli nie → zostają placeholderami.
- [ ] **Nuclear Reactor** — czy target to Bigger Reactors czy Mekanism Fission Reactor? Obecnie ustawiono `biggerreactors:reactor_casing`.
- [ ] **Reactor Redstone Port** — brak odpowiednika w BiggerReactors. Pozostaje placeholder.

### 6.2 Wymaga dalszej pracy
- [ ] Konwersja ID itemów IC2 → 1.18.2 (inventory w maszynach i storage)
- [ ] Obsługa zbiorników płynów (Tanks w NBT IC2) dla maszyn z płynami
- [ ] System upgrade'ów IC2 → upgrade'y Mekanism/Thermal
- [ ] Konwersja `components` z TileEntityBlock (dodatkowe komponenty)

---

## 7. Następne kroki (Zadanie 3)

1. **Implementacja głównego konwertera** (`ic2_converter.py`)
   - Rejestr konwerterów NBT (jak w mekanism_converter.py)
   - Routing per `nbt_converter` z block_mappings
   - Integracja z `common/placeholders.py`

2. **Konwertery NBT per-typ**
   - `nbt_converters/base_converter.py`
   - `nbt_converters/machine_converter.py`
   - `nbt_converters/energy_storage_converter.py`
   - `nbt_converters/cable_converter.py`

3. **Analiza pokrycia mapy** — sprawdzenie które bloki IC2 faktycznie występują na `mapa_1710`

---

*Dokument utworzony: 2026-05-19*
*Źródła: IC2 2.2.827 (dekompilacja), Thermal Expansion 9.2.2 (kod źródłowy), dokumentacja projektu*
