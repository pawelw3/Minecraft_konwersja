# Handoff: Big Reactors → Bigger Reactors (Zadania 1-3)

## Podsumowanie sesji
Wykonano Zadania 1, 2 i 3 z PLAN.md dla moda Big Reactors (1.7.10) → Bigger Reactors (1.18.2).

## Ukończono
- [x] **Zadanie 1** — Inwentaryzacja bloków i TE/BE:
  - 1.7.10: 11 bloków (w tym 5 z metadata), 19 Tile Entities
  - 1.18.2: ~40 bloków (osobne ID bez metadata), 24 Block Entities
  - Porównanie różnic wersji, tabela mapowań
  - Plik: `ANALYSIS.md`

- [x] **Zadanie 2** — Symulacje funkcjonalności w Pythonie:
  - `reactor_simulation_1710.py` — symulacja reaktora 1.7.10 (radiacja, temperatura, chłodzenie pasywne/aktywne, zużycie paliwa, control rods)
  - `reactor_simulation_1182.py` — symulacja reaktora 1.18.2 (fertility, heat transfer fuel→stack→coolant/ambient, battery/coolant tank)
  - `turbine_simulation_1710.py` — symulacja turbiny 1.7.10 (steam→rotor energy, aerodynamic drag, coil induction, venting)
  - `turbine_simulation_1182.py` — symulacja turbiny 1.18.2 (flow rate, rotor capacity, RPM efficiency curve, coil drag, battery)
  - `cyanite_reprocessor_simulation.py` — symulacja Cyanite Reprocessor (cykl 200 ticks, 2 cyanite + 1B woda → 1 blutonium, energia 2000 RF)
  - **Testy**: 19 testów jednostkowych — wszystkie przechodzą ✅

- [x] **Zadanie 3** — Kod konwersji (mappings + converter + NBT + router):
  - `mappings.py` — kompletne mapowanie 28 par (block_id, metadata) → 1.18.2 block ID
    - Obsługa metadata: BRReactorPart (0-7), BRTurbinePart (0-5), BRTurbineRotorPart (0-1), BRMetalBlock (0-4), BRMultiblockGlass (0-1)
    - Mapowanie materiałów: Yellorium→Uranium, YelloriteOre→uranium_ore
    - Fallback RedNet Port → reactor_redstone_port z ostrzeżeniem
    - Creative ports → minecraft:air (usunięte)
  - `biggerreactors_converter.py` — główna klasa `BiggerReactorsConverter` zgodna ze wzorcem projektowym
  - `nbt_converters/` — 4 konwertery NBT:
    - `identity` — podstawowe pola (x,y,z,id,facing,CustomName)
    - `multiblock_reactor` — zachowuje insertion (control rod), energy (power tap), temperature
    - `multiblock_reactor_accessport` — dodatkowo konwertuje inventory (Yellorium→Uranium item ID)
    - `multiblock_turbine` — zachowuje energy, ostrzeżenie o fluid tanks
    - `cyanite_reprocessor` — inventory, energy (RF→FE), progress (cookTime→progress)
  - Integracja z `src/converters/router.py` — detekcja modu, serializacja eventów
  - **Testy**: 102 testy jednostkowe i integracyjne — wszystkie przechodzą ✅

## Nowe pliki
- `src/converters/bigreactors/ANALYSIS.md`
- `src/converters/bigreactors/mappings.py`
- `src/converters/bigreactors/biggerreactors_converter.py`
- `src/converters/bigreactors/nbt_converters/__init__.py`
- `src/converters/bigreactors/nbt_converters/base_converter.py`
- `src/converters/bigreactors/nbt_converters/multiblock_converter.py`
- `src/converters/bigreactors/nbt_converters/reprocessor_converter.py`
- `src/converters/bigreactors/simulations/__init__.py`
- `src/converters/bigreactors/simulations/reactor_simulation_1710.py`
- `src/converters/bigreactors/simulations/reactor_simulation_1182.py`
- `src/converters/bigreactors/simulations/turbine_simulation_1710.py`
- `src/converters/bigreactors/simulations/turbine_simulation_1182.py`
- `src/converters/bigreactors/simulations/cyanite_reprocessor_simulation.py`
- `src/converters/bigreactors/tests/__init__.py`
- `src/converters/bigreactors/tests/test_simulations.py`
- `src/converters/bigreactors/tests/test_mappings.py`
- `src/converters/bigreactors/tests/test_converter.py`
- `src/converters/bigreactors/tests/test_router_integration.py`

## Zmodyfikowane pliki
- `src/converters/router.py` — dodano:
  - `_bigreactors()` (lazy singleton)
  - `_biggerreactors_to_events()` (serializacja eventów)
  - Detekcję modu `bigreactors` w `detect_mod()`
  - Routing w `convert_te_to_events()`

## Kluczowe decyzje i odkrycia
1. **Kod źródłowy BiggerReactors 1.18.2** w `mod_src/118/actual_src/1.18.2/BiggerReactors/repo/src/` (struktura `repo/src`, nie `repo/BiggerReactors/src`).
2. **TE w 1.7.10 mają nietypowe nazwy**: Wszystkie registry strings TE mają prefiks `BR`, ale **nie** używają pełnego MODID `BigReactors:`. W plikach `.mca` należy szukać dokładnie tych stringów.
3. **Metadata → osobne bloki**: W 1.7.10 `BRReactorPart` z meta 0-7 to w 1.18.2 osobne bloki (`reactor_casing`, `reactor_terminal`, ...).
4. **Yellorium → Uranium**: `YelloriteOre` → `uranium_ore`, `BRMetalBlock/0` → `uranium_block`.
5. **RedNet Port** zmapowano na `reactor_redstone_port` z ostrzeżeniem (MineFactory Reloaded nie istnieje w 1.18.2).
6. **Creative parts** (creative coolant port, creative steam generator) zmapowano na `minecraft:air` — usunięte.
7. **Cyanite Reprocessor** — zmapowany na `biggerreactors:cyanite_reprocessor` z konwersją inventory i progress.
8. **Konwersja NBT inventory** — automatyczna zamiana item ID: `BigReactors:ingotYellorium` → `biggerreactors:uranium_ingot`, itp.
9. **Reactor2** pozostaje eksperymentalny — nie uwzględniony w mapowaniach (target używa klasycznego systemu `reactor_*`).

## Ukończono (Zadanie 4)
- [x] **Analiza pokrycia na mapie 1.7.10** (`mapa_1710/`):
  - Źródło: globalny skan `cz2_targeted_te_scan_2026-05-18.json` (1194 regionów, 2.4M TE)
  - **24,080 TE BigReactors** na mapie, wszystkie zmapowane (100% pokrycia)
  - Rozkład: 86% reaktory, 13% turbiny, <1% maszyny pojedyncze
  - Strefy: 95.8% poza strefami, 3.0% w `iii_rzesza`, 1.1% w `rzym`, 0.09% w `zsrr`
  - Raporty: `output/bigreactors_task4/bigreactors_coverage_report.json` + `.md`

## Ukończono (Zadanie 5A)
- [x] **Testowa mapa + konwersja**:
  - `generate_bigreactors_task5a.py` — 257 edycji (146 bloków + 111 TE)
  - `convert_bigreactors_task5a.py` — konwersja do 1.18.2
  - Wynik: 107/107 bloków skonwertowanych (100%), 0 failures, 13 warnings
  - Testowane: reaktor (casing, control rod, power tap, access port, coolant port, glass, fuel rod, redstone port, computer port)
  - Testowane: turbina (housing, controller, power tap, fluid port, bearing, glass, rotor shaft/blade, computer port)
  - Testowane: Cyanite Reprocessor (inventory, energy, progress)
  - Testowane: mini multibloki (3x3x4 reactor + 3x3x4 turbine)
  - Raport: `test_scenarios/bigreactors_task5a/BIGREACTORS_TASK5A_REPORT.md`

## Następne kroki
1. [ ] **Zadanie 5B** — materializacja na headless serwerze 1.18.2
   - **Wymaga instalacji `BiggerReactors` mod JAR** na serwerze (obecnie brak w `headless_server/1.18.2/mods/`)
2. [ ] **Zadanie 6** — test ticków + restart na headless serwerze z BiggerReactors
