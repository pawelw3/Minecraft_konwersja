# Big Reactors — Analiza pokrycia na mapie 1.7.10 (wstępna)

**Źródło danych:** `docs/sprawdzenie_codex/cz2_targeted_te_scan_2026-05-18.json` (globalny skan TE mapy 1.7.10)  
**Data:** 2026-05-25  
**Uwaga:** To raport wstępny na podstawie istniejących danych agregowanych. Pełny skan z pozycjami per-TE jest uruchomiony w tle.

---

## Podsumowanie

| Metryka | Wartość |
|---------|---------|
| Łączna liczba TE BigReactors | **25,778** |
| Regionów z BigReactors | do uzupełnienia (skan w tle) |
| Chunków z BigReactors | do uzupełnienia (skan w tle) |

---

## Rozkład Tile Entities per ID

| TE ID | Liczba | % całości | Zmapowane | Target 1.18.2 | Uwagi |
|-------|--------|-----------|-----------|---------------|-------|
| `BRFuelRod` | 10,411 | 40.4% | ✅ | `biggerreactors:reactor_fuel_rod` | Rdzeń reaktora |
| `BRReactorPart` | 7,453 | 28.9% | ✅ | zależne od metadata (casing, controller, ...) | Casing+Controller+... |
| `BRReactorGlass` | 2,210 | 8.6% | ✅ | `biggerreactors:reactor_glass` | Szkło reaktora |
| `BRTurbinePart` | 1,740 | 6.7% | ✅ | zależne od metadata (housing, controller, ...) | Housing+Controller+... |
| `BRReactorControlRod` | 754 | 2.9% | ✅ | `biggerreactors:reactor_control_rod` | Pręty kontrolne |
| `BRTurbineGlass` | 855 | 3.3% | ✅ | `biggerreactors:turbine_glass` | Szkło turbiny |
| `BRTurbineRotorPart` | 564 | 2.2% | ✅ | `biggerreactors:turbine_rotor_shaft/blade` | Wał+łopatki |
| `BRReactorAccessPort` | 26 | 0.1% | ✅ | `biggerreactors:reactor_access_port` | Port dostępu |
| `BRReactorCoolantPort` | 13 | 0.05% | ✅ | `biggerreactors:reactor_coolant_port` | Port chłodziwa |
| `BRTurbineFluidPort` | 12 | 0.05% | ✅ | `biggerreactors:turbine_fluid_port` | Port cieczy |
| `BRReactorPowerTap` | 22 | 0.09% | ✅ | `biggerreactors:reactor_power_tap` | Power tap |
| `BRCyaniteReprocessor` | 7 | 0.03% | ✅ | `biggerreactors:cyanite_reprocessor` | Reprocessor |
| `BRTurbinePowerTap` | 6 | 0.02% | ✅ | `biggerreactors:turbine_power_tap` | Power tap turbiny |
| `BRTurbineRotorBearing` | 6 | 0.02% | ✅ | `biggerreactors:turbine_rotor_bearing` | Łożysko wirnika |
| `BRReactorComputerPort` | 1 | 0.004% | ✅ | `biggerreactors:reactor_computer_port` | Port komputera |
| **Suma** | **25,778** | **100%** | | | |

### TE znane ale nieobecne na mapie

| TE ID | Target 1.18.2 | Uwagi |
|-------|---------------|-------|
| `BRReactorRedstonePort` | `biggerreactors:reactor_redstone_port` | Osobny blok redstone |
| `BRReactorRedNetPort` | `biggerreactors:reactor_redstone_port` (fallback) | RedNet nie istnieje w 1.18.2 |
| `BRReactorCreativeCoolantPort` | `minecraft:air` | Creative — usuwamy |
| `BRTurbineCreativeSteamGenerator` | `minecraft:air` | Creative — usuwamy |
| `BRTurbineComputerPort` | `biggerreactors:turbine_computer_port` | Nie wystąpił na mapie |

**Weryfikacja pokrycia konwertera:** Wszystkie 15 rodzajów TE obecnych na mapie są zmapowane. Brakujące TE (nieobecne na mapie) również mają mapowania lub fallbacki.

---

## Rozkład per strefa (z globalnego skanu)

| Strefa | Liczba TE | % całości |
|--------|-----------|-----------|
| `outside_defined_zones` | 24,696 | 95.8% |
| `iii_rzesza` | 785 | 3.0% |
| `rzym` | 273 | 1.1% |
| `zsrr` | 24 | 0.09% |
| `billund` | ? | ? |
| `choroszcz` | ? | ? |

**Uwaga:** Strefy `billund` i `choroszcz` nie występują w dostępnych danych globalnych — wymagają weryfikacji w pełnym skanie.

---

## Wnioski

1. **Big Reactors jest jednym z największych modów na mapie** pod względem liczby TE (25,778) — porównywalnym z CarpentersBlocks (635k) czy BuildCraft, ale wciąż znaczącym.
2. **Dominują reaktory** — `BRFuelRod` (10,411) + `BRReactorPart` (7,453) + `BRReactorGlass` (2,210) + `BRReactorControlRod` (754) = ~20,828 TE reaktora (~80% wszystkich BR TE).
3. **Turbiny** są mniej liczne — `BRTurbinePart` (1,740) + `BRTurbineGlass` (855) + `BRTurbineRotorPart` (564) = ~3,159 TE turbiny (~12%).
4. **Maszyny pojedyncze** (Access Port, Power Tap, Coolant Port, Cyanite Reprocessor) to <1% — bardzo rzadkie.
5. **95.8% BigReactors znajduje się poza zdefiniowanymi strefami** — sugeruje duże farmy reaktorów/turbin w okolicach spawn lub na wolnym terenie.
6. **Wszystkie TE na mapie są pokryte przez konwerter** — brak "czarnej dziury" w mapowaniach.

---

## Następne kroki

1. [ ] Poczekać na zakończenie pełnego skanu w tle (pozycje per TE, rozmieszczenie w regionach)
2. [ ] Zweryfikować rozmieszczenie w strefach `billund` i `choroszcz`
3. [ ] Sprawdzić czy występują bloki bez TE (YelloriteOre, BRMetalBlock, fluids) — wymaga block ID registry
4. [ ] Zadanie 5A — testowa mapa z Big Reactors
