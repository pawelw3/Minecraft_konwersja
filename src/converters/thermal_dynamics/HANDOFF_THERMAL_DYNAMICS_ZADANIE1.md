# Handoff: Thermal Dynamics — Zadanie 1 (Ukończone)

## Podsumowanie sesji

Ukończono **Zadanie 1** konwersji moda Thermal Dynamics z wersji 1.7.10 na 1.18.2.  
Zadanie polegało na wypisaniu wszystkich bloków i Tile Entities dodawanych przez mod oraz opisaniu ich funkcjonalności na podstawie dekompilacji kodu źródłowego obu wersji.

## Ukończono

- [x] Dekompilacja JAR ThermalDynamics 1.7.10 (`modpack_1710/ThermalDynamics-[1.7.10]1.2.1-172.jar`)
- [x] Analiza kodu źródłowego ThermalDynamics 1.18.2 (`mod_src/118/actual_src/1.18.2/ThermalDynamics/repo`)
- [x] Identyfikacja pełnej listy 34 typów ductów w 1.7.10 z offsetami i metadata
- [x] Identyfikacja rejestracji bloków: `ThermalDynamics:thermaldynamics.Duct{offset}` (offset ∈ {0,16,32,48,64})
- [x] Identyfikacja 13 klas Tile Entities w 1.7.10
- [x] Identyfikacja bloków i TE w 1.18.2 (`energy_duct`, `fluid_duct`, `fluid_duct_windowed`, `item_buffer`)
- [x] **Krytyczne odkrycie:** W wersji 1.18.2 (9.2.2.19) **nie ma** bloków:
  - `item_duct` / `item_duct_fast`
  - `structure_duct`
  - `transport_duct` (Viaduct)
- [x] Opracowanie mapowania 1.7.10 → 1.18.2 z uwzględnieniem brakujących odpowiedników
- [x] Opis struktury NBT i załączników (Servo/Filter/Retriever)
- [x] Stworzenie skryptu `analyze_thermal_dynamics.py` do analizy mapy

## Nowe pliki

| Plik | Opis |
|------|------|
| `src/converters/thermal_dynamics/__init__.py` | Inicjalizacja pakietu konwertera |
| `src/converters/thermal_dynamics/THERMAL_DYNAMICS_BLOCKS_AND_TE.md` | Główna dokumentacja kroku 1: pełna lista bloków i TE, mapowanie, NBT, priorytety |
| `src/converters/thermal_dynamics/analyze_thermal_dynamics.py` | Skrypt analizy mapy: rozpoznaje ducty po block_id + metadata, generuje raport JSON |

## Kluczowe wnioski dla kolejnych zadań

### 🔴 Krytyczne problemy wymagające decyzji użytkownika:

1. **Item Ducts (Itemduct / Impulse / Ender / Flux-Plated)** — w TD 1.18.2 v9.2.2 **nie ma bloku item duct**. Konieczna decyzja:
   - Konwersja na inny mod (Pipez, Mekanism)?
   - Placeholder + ręczna rekonstrukcja?
   - Usunięcie + zrzut załączników do skrzyń?

2. **Transport Ducts (Viaducts)** — brak odpowiednika w 1.18.2.

3. **Structural / Light Ducts** — brak odpowiednika w 1.18.2.

### 🟢 Bezproblemowe konwersje:

| Kategoria | Mapowanie | Uwagi |
|-----------|-----------|-------|
| Energy Ducts (6 typów) | `thermal:energy_duct` | Uproszczony system — grid odtworzy się automatycznie |
| Fluid Ducts (8 typów) | `thermal:fluid_duct` / `thermal:fluid_duct_windowed` | Bezpośrednia zamiana |

### 🟡 Wymagające uwagi:

- **Załączniki (Servo, Filter)** — w 1.18.2 istnieją jako itemy (`thermal:servo_attachment`, `thermal:filter_attachment`), ale mechanizm montażu może się różnić.
- **NBT sieci (Grid)** — w 1.7.10 przechowywane w TE, w 1.18.2 grid jest dynamiczny; nie da się przenieść topologii sieci.

## Statystyki

| Kategoria | 1.7.10 | 1.18.2 | Różnica |
|-----------|--------|--------|---------|
| Typy ductów (bloki) | 34 | 3 (+1 buffer) | -30 |
| Klasy Tile Entity | 13 | 4 | -9 |
| Bloki z bezpośrednim mapowaniem | 14 | 14 | — |
| Bloki bez odpowiednika | 20 | — | — |

## Następne kroki (Zadanie 2)

Zgodnie z planem konwersji (`docs/PLAN.md`), kolejne zadanie to:

**Zadanie 2: Przygotowanie symulacji działania funkcjonalności Thermal Dynamics**

Symulacje do przygotowania:
1. Symulacja sieci energetycznej (RF/FE) — transfer energii przez Fluxducts
2. Symulacja sieci fluidów — transfer płynów przez Fluiducts
3. Symulacja sieci itemów — routing Itemducts (najkrótsza ścieżka, round-robin, itp.)
4. Symulacja załączników (Servo — ekstrakcja z inventory, Filter — filtrowanie)

Każda symulacja ma być w czystym Pythonie (bez mapy), bazując na kodzie źródłowym obu wersji moda.

## Zalecenia przed Zadaniem 2

1. **Rozstrzygnąć decyzję** dotyczącą Itemductów — czy konwertować na Pipez/Mekanism, czy stosować placeholdery?
2. Zapoznać się z klasami Tile Entities w 1.18.2:
   - `cofh.thermal.dynamics.block.entity.duct.EnergyDuctBlockEntity`
   - `cofh.thermal.dynamics.block.entity.duct.FluidDuctBlockEntity`
   - `cofh.thermal.dynamics.block.entity.ItemBufferBlockEntity`
3. Sprawdzić czy w nowszej wersji Thermal Dynamics (nowszej niż 9.2.2) pojawiły się item ducty — może wymagać aktualizacji moda docelowego.

---

**Status:** ✅ Zadanie 1 ukończone — gotowe do przeglądu i akceptacji  
**Data:** 2026-05-19  
**Agent:** AI Konwersji Thermal Dynamics
