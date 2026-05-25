# Handoff: BuildCraft – Krok 2 (Ukończony)

## Podsumowanie sesji

Ukończono **Krok 2** konwersji moda BuildCraft z wersji 1.7.10 na ekosystem 1.18.2 (Pipez / RFTools Builder / XNet / Integrated Dynamics).  
Krok polegał na przygotowaniu symulacji działania funkcjonalności BuildCraft – dla każdej kategorii bloków/TE stworzono model konwersji i testy weryfikujące poprawność.

## Decyzje użytkownika zatwierdzone w tej sesji

| # | Decyzja | Implementacja |
|---|---------|---------------|
| 1 | **Dodać Thermal Dynamo Compression do modpacka** | `thermal:dynamo_compression` jest dostępny w `thermal_expansion-1.18.2-9.2.2.24.jar` ✅ (już obecny w mod_src) |
| 2 | **Zrobić custom recepturę oil → fuel** | Stworzono `bc_oil_to_fuel.json` (data pack recipe) + Refinery zawsze konwertowane |
| 3 | **Nie usuwać rur w ogóle** | Wszystkie `GenericPipe` zamieniane na `pipez:universal_pipe` (domyślnie) lub `fluid_pipe` / `energy_pipe` w zależności od kontekstu |

## Ukończono

- [x] Stworzenie folderu `src/converters/buildcraft/simulations/`
- [x] Stworzenie folderu `src/converters/buildcraft/tests/`
- [x] Symulacja **silników** (`engine_simulation.py`):
  - TileEngineWood (Redstone) -> REMOVE
  - TileEngineStone (Stirling) -> `thermal:dynamo_steam`
  - TileEngineIron (Combustion) -> `thermal:dynamo_compression`
  - Konwersja orientacji BC -> facing 1.18.2
  - Konwersja energii MJ -> FE (mnożnik ×10)
  - Konwersja inventory (fuel) i fluid tanks
- [x] Symulacja **maszyn fabrycznych** (`factory_simulation.py`):
  - TileTank -> `mekanism:basic_fluid_tank` (zachowuje płyn)
  - TilePump -> `mekanism:electric_pump` (zachowuje energy + fluid)
  - TileRefinery -> `thermal:machine_refinery` (zawsze, z custom recepturą)
  - Mapowanie nazw płynów BC -> 1.18.2 (oil -> `thermal:crude_oil`, fuel -> `thermal:refined_fuel`, water)
- [x] Symulacja **rur** (`pipe_simulation.py`):
  - **Decyzja: NIE usuwać rur** -> wszystkie zamieniane na Pipez
  - Domyślnie `pipez:universal_pipe`
  - `pipez:fluid_pipe` jeśli sąsiaduje z płynem
  - `pipez:energy_pipe` jeśli sąsiaduje z silnikiem
  - Uwaga: logika gates/wires jest tracona, ale fizyczna infrastruktura zostaje
- [x] Symulacja **specjalnych maszyn** (`assembly_laser_simulation.py`):
  - Assembly Table -> REMOVE (z rekomendacją wydropienia inventory)
  - Integration Table -> REMOVE
  - Laser -> REMOVE (z opcją dekoracyjnego zamiennika)
  - Zone Plan -> REMOVE (z notatką o RFTools Builder jako overkill)
- [x] Custom receptura **oil -> fuel** dla Thermal Refinery:
  - `src/converters/buildcraft/data_pack_recipes/data/buildcraft_conversion/recipes/machines/refinery/bc_oil_to_fuel.json`
  - Format: `thermal:crude_oil` (200 mB) -> `thermal:refined_fuel` (200 mB), 8000 RF
- [x] Pełna suite testów (`tests/test_buildcraft_simulations.py`) – **16 testów, wszystkie zielone**

## Nowe pliki

| Plik | Opis |
|------|------|
| `src/converters/buildcraft/simulations/__init__.py` | Inicjalizacja pakietu symulacji |
| `src/converters/buildcraft/simulations/engine_simulation.py` | Konwersja silników BC -> generatory 1.18.2 |
| `src/converters/buildcraft/simulations/factory_simulation.py` | Konwersja Tank/Pump/Refinery -> Mekanism/Thermal |
| `src/converters/buildcraft/simulations/pipe_simulation.py` | Decyzje architektoniczne dla rur GenericPipe |
| `src/converters/buildcraft/simulations/assembly_laser_simulation.py` | Decyzje dla Assembly Table / Laser / Zone Plan |
| `src/converters/buildcraft/tests/__init__.py` | Inicjalizacja pakietu testów |
| `src/converters/buildcraft/tests/test_buildcraft_simulations.py` | 16 testów jednostkowych (pytest) |
| `src/converters/buildcraft/data_pack_recipes/.../bc_oil_to_fuel.json` | Custom receptura Thermal Refinery oil->fuel |

## Kluczowe decyzje architektoniczne

### Silniki

| Źródło BC | Cel 1.18.2 | Uwagi |
|-----------|-----------|-------|
| Redstone Engine (Wood) | **REMOVE** | Zbyt słaby, brak odpowiednika |
| Stirling Engine (Stone) | `thermal:dynamo_steam` | Zachowuje solid fuel z inventory |
| Combustion Engine (Iron) | `thermal:dynamo_compression` | Zachowuje fuel/water; Compression Dynamo potwierdzony w Thermal 1.18.2 |

**Mnożnik energii:** MJ -> FE = **×10** (konfigurowalny stała `MJ_TO_FE`).

### Maszyny fabryczne

| Źródło BC | Cel 1.18.2 | Uwagi |
|-----------|-----------|-------|
| Tank | `mekanism:basic_fluid_tank` | Zachowuje płyn (water, oil, fuel) |
| Pump | `mekanism:electric_pump` | Zachowuje płyn + energia z battery |
| Refinery | `thermal:machine_refinery` | Zawsze konwertowane; custom receptura `bc_oil_to_fuel.json` dodaje oil->fuel |

### Rury (GenericPipe)

| Warunek | Decyzja | Uwagi |
|---------|---------|-------|
| Domyślnie (wszystkie) | `pipez:universal_pipe` | Decyzja użytkownika: nie usuwać rur |
| Sąsiad z płynem | `pipez:fluid_pipe` | Pump, Tank, Refinery |
| Sąsiad z energią | `pipez:energy_pipe` | Engine |

**Uwaga:** Logika gates/wires oraz itemy w transporcie są **tracone**, ale fizyczna infrastruktura pozostaje.

### Specjalne maszyny

| Źródło BC | Decyzja | Uwagi |
|-----------|---------|-------|
| Assembly Table | **REMOVE** | Wydropić inventory do skrzyni |
| Integration Table | **REMOVE** | Brak odpowiednika |
| Laser | **REMOVE** | Opcjonalnie zastąpić dekoracyjnym blokiem |
| Zone Plan | **REMOVE** | RFTools Builder to overkill |

## Custom receptura oil -> fuel

Plik: `src/converters/buildcraft/data_pack_recipes/data/buildcraft_conversion/recipes/machines/refinery/bc_oil_to_fuel.json`

```json
{
  "type": "thermal:refinery",
  "ingredient": { "fluid": "thermal:crude_oil", "amount": 200 },
  "result": [ { "fluid": "thermal:refined_fuel", "amount": 200 } ],
  "energy": 8000
}
```

**Uwaga:** Thermal Expansion 1.18.2 ma natywnie chain `crude_oil -> light_oil -> refined_fuel`.  
Custom receptura pozwala zachować stare zachowanie BC (1-etapowe oil->fuel) dla graczy przyzwyczajonych do BC.

## Następne kroki (Krok 3)

Zgodnie z planem konwersji (`docs/PLAN.md`), kolejny krok to:

**Krok 3: Kod konwersji (wspólne narzędzia + specyficzne per-mod)**

Do zaimplementowania:
1. **NBT Converter Registry** – system rejestracji konwerterów per TE ID (jak w AE2/IC2)
2. **Block ID mappings** – mapowanie numerycznych ID bloków BC (512-768) na string ID 1.18.2
3. **Konwerter główny** (`buildcraft_converter.py`) – router delegujący do konkretnych konwerterów
4. **NBT Converters per typ:**
   - `engine_converter.py` – Wood/Stone/Iron
   - `factory_converter.py` – Tank/Pump/Refinery
   - `pipe_converter.py` – GenericPipe (REPLACE_UNIVERSAL/FLUID/ENERGY)
   - `special_converter.py` – Assembly/Laser/ZonePlan
5. **Inventory conversion** – konwersja slotów itemów BC (numeryczne ID) na string ID 1.18.2

## Zalecenia przed Krokiem 3

1. **Rozstrzygnąć:** Czy zachować natywne receptury Thermal (crude_oil -> heavy_oil + light_oil) czy nadpisać custom recepturą `bc_oil_to_fuel`?  
   Rekomendacja: Dodaj data pack z custom recepturą jako **opcjonalny** (gracz włącza jeśli chce stare zachowanie BC).

2. **Rozstrzygnąć:** Czy dla rur z gates/wires dodać dodatkowe bloki logiki (np. `pipez:extractor` lub XNet connector) czy po prostu zostawić pusty Pipez?  
   Rekomendacja: Zostawić pusty Pipez - gracz sam doda logikę jeśli potrzebuje.

---

**Status:** ✅ Krok 2 ukończony – wszystkie symulacje przetestowane (16/16 testów zielonych)  
**Data:** 2026-05-24  
**Agent:** AI Konwersji BuildCraft
