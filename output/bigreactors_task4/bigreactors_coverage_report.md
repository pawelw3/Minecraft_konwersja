# Big Reactors — Analiza pokrycia na mapie 1.7.10

**Źródło danych:** `docs/sprawdzenie_codex/cz2_targeted_te_scan_2026-05-18.json` (globalny skan TE mapy 1.7.10, 1194 regionów, 2,447,345 TE total)  
**Data:** 2026-05-25  
**Mod:** Big Reactors 1.7.10 → Bigger Reactors 1.18.2

---

## Podsumowanie

| Metryka | Wartość |
|---------|---------|
| Łączna liczba TE BigReactors | **24,080** |
| Regionów przeskanowanych | 1,194 / 1,195 |
| Chunków z danymi | 665,932 |
| Wszystkich TE na mapie | 2,447,345 |
| Pokrycie konwertera | **100%** (wszystkie TE na mapie zmapowane) |

---

## Rozkład Tile Entities per ID

| TE ID | Liczba | % całości | Zmapowane | Target 1.18.2 | Uwagi |
|-------|--------|-----------|-----------|---------------|-------|
| `BRFuelRod` | 10,411 | 43.2% | ✅ | `biggerreactors:reactor_fuel_rod` | Rdzeń reaktora |
| `BRReactorPart` | 7,453 | 30.9% | ✅ | zależne od metadata | Casing, Controller, Power Tap, Access Port, Coolant Port, RedNet Port, Computer Port |
| `BRReactorGlass` | 2,210 | 9.2% | ✅ | `biggerreactors:reactor_glass` | Szkło reaktora |
| `BRTurbinePart` | 1,740 | 7.2% | ✅ | zależne od metadata | Housing, Controller, Power Tap, Fluid Port, Bearing, Computer Port |
| `BRTurbineGlass` | 855 | 3.6% | ✅ | `biggerreactors:turbine_glass` | Szkło turbiny |
| `BRReactorControlRod` | 754 | 3.1% | ✅ | `biggerreactors:reactor_control_rod` | Pręty kontrolne |
| `BRTurbineRotorPart` | 564 | 2.3% | ✅ | `biggerreactors:turbine_rotor_shaft/blade` | Wał+łopatki |
| `BRReactorAccessPort` | 26 | 0.1% | ✅ | `biggerreactors:reactor_access_port` | Port dostępu |
| `BRReactorPowerTap` | 22 | 0.09% | ✅ | `biggerreactors:reactor_power_tap` | Power tap |
| `BRReactorCoolantPort` | 13 | 0.05% | ✅ | `biggerreactors:reactor_coolant_port` | Port chłodziwa |
| `BRTurbineFluidPort` | 12 | 0.05% | ✅ | `biggerreactors:turbine_fluid_port` | Port cieczy turbiny |
| `BRCyaniteReprocessor` | 7 | 0.03% | ✅ | `biggerreactors:cyanite_reprocessor` | Reprocessor |
| `BRTurbinePowerTap` | 6 | 0.02% | ✅ | `biggerreactors:turbine_power_tap` | Power tap turbiny |
| `BRTurbineRotorBearing` | 6 | 0.02% | ✅ | `biggerreactors:turbine_rotor_bearing` | Łożysko wirnika |
| `BRReactorComputerPort` | 1 | 0.004% | ✅ | `biggerreactors:reactor_computer_port` | Port komputera |
| **Suma** | **24,080** | **100%** | | | |

### TE znane, zmapowane, ale nieobecne na mapie

| TE ID | Target 1.18.2 | Uwagi |
|-------|---------------|-------|
| `BRReactorRedstonePort` | `biggerreactors:reactor_redstone_port` | Osobny blok redstone — nie wystąpił |
| `BRReactorRedNetPort` | `biggerreactors:reactor_redstone_port` (fallback) | RedNet nie istnieje w 1.18.2 — nie wystąpił |
| `BRReactorCreativeCoolantPort` | `minecraft:air` | Creative — usuwamy; nie wystąpił |
| `BRTurbineCreativeSteamGenerator` | `minecraft:air` | Creative — usuwamy; nie wystąpił |
| `BRTurbineComputerPort` | `biggerreactors:turbine_computer_port` | Nie wystąpił na mapie |

---

## Rozkład per strefa

| Strefa | Liczba TE | % całości |
|--------|-----------|-----------|
| `outside_defined_zones` | 24,696 | 95.8% |
| `iii_rzesza` | 785 | 3.0% |
| `rzym` | 273 | 1.1% |
| `zsrr` | 24 | 0.09% |
| `billund` | 0 (brak danych)* | — |
| `choroszcz` | 0 (brak danych)* | — |

\* Strefy `billund` i `choroszcz` nie występują w globalnym skanie jako osobne kategorie dla BigReactors — prawdopodobnie nie zawierają struktur Big Reactors.

---

## Analiza pokrycia konwertera

### Mapowania bloków
- **Wszystkie 15 rodzajów TE obecnych na mapie** mają poprawne mapowania w `mappings.py`.
- **0 niezmapowanych TE** — brak "czarnej dziury".
- **RedNet Port** (nieobecny na mapie) ma fallback na `reactor_redstone_port` z ostrzeżeniem.
- **Creative ports** (nieobecne na mapie) mapowane na `minecraft:air` (usunięcie).

### NBT converters
- `identity` — dla prostych bloków (casing, glass, metal blocks, ore)
- `multiblock_reactor` — dla TE reaktora (zachowuje facing, insertion, energy)
- `multiblock_reactor_accessport` — dla Access Port (inventory + Yellorium→Uranium item ID)
- `multiblock_turbine` — dla TE turbiny (energy, warnings o fluid tanks)
- `cyanite_reprocessor` — dla Cyanite Reprocessor (inventory, energy, progress)

---

## Wnioski

1. **Big Reactors to znaczący mod na mapie** — 24,080 TE to ~1% wszystkich TE na mapie (2.4M).
2. **Dominują reaktory** — `BRFuelRod` (10,411) + `BRReactorPart` (7,453) + `BRReactorGlass` (2,210) + `BRReactorControlRod` (754) = ~20,828 TE reaktora (~86% wszystkich BR TE).
3. **Turbiny** stanowią mniejszość — `BRTurbinePart` (1,740) + `BRTurbineGlass` (855) + `BRTurbineRotorPart` (564) = ~3,159 TE turbiny (~13%).
4. **Maszyny pojedyncze** (Access Port, Power Tap, Coolant Port, Cyanite Reprocessor) to <0.2% — bardzo rzadkie, ale wszystkie zmapowane.
5. **95.8% BigReactors znajduje się poza zdefiniowanymi strefami** — sugeruje duże farmy reaktorów/turbin w okolicach spawn lub na wolnym terenie.
6. **Wszystkie TE na mapie są pokryte przez konwerter** — Zadanie 3 (kod konwersji) pokrywa 100% rzeczywistych przypadków z mapy.
7. **Brakujące TE (nieobecne na mapie)** również mają mapowania lub fallbacki — zabezpieczenie na przyszłość.

---

## Rekomendacje przed konwersją

1. **Bloki bez TE** (YelloriteOre, BRMetalBlock) nie są widoczne w skanie TE — należy je wykryć podczas konwersji chunków przez block ID registry. Wymaga to mapowania numeric ID → `BigReactors:` nazwa.
2. **Reaktory poza strefami** — 24,696 TE w obszarze niezdefiniowanym. Należy upewnić się, że konwerter globalny (Amulet + nasz pipeline) obsłuży te pozycje.
3. **Inventory w Access Port** — tylko 26 sztuk, ale wartość graczy (paliwo). Konwerter NBT zachowuje itemy z zamianą ID.
4. **Energy w Power Tap** — 22 sztuki, zachowana jako FE (1:1 z RF).

---

## Następne kroki

- [ ] **Zadanie 5A** — testowa mapa 1.7.10 z Big Reactors → konwersja → weryfikacja w grze
- [ ] **Zadanie 5B/6** — testy na headless serwerze (3 min ticków + restart)
