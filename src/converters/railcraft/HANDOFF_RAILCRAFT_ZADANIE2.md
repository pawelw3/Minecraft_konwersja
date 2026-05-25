# Handoff: Zadanie 2 - Railcraft (Symulacje funkcjonalności i mapowania)

## Podsumowanie sesji

Wykonano mapowania bloków Railcraft 1.7.10 → strict 1.18.2 zgodnie z decyzją dokumentacji projektu (`docs/sprawdzenie_codex/cz4_analiza_funkcjonalnosci_i_zamiennikow_2026-05-18.md`):

> Dla strict 1.18.2 najlepszy praktyczny kierunek to `Create + Steam'n'Rails`/`Little Logistics` + `Immersive Engineering`/`Mekanism`/`Thermal` per funkcja.

Railcraft Reborn **nie istnieje dla 1.18.2** (dostępny od 1.20.1), więc zastosowano hybrydowe mapowanie funkcjonalne z wysokim ryzykiem utraty danych.

### Wyniki testów
**32/32 testów jednostkowych passed** ✅

---

## 1. Mapowania bloków (`mappings/block_mappings.py`)

### 1.1 Podsumowanie mapowań

| Kategoria | Liczba mapowań | Konwertowane | Placeholdery / Ignorowane |
|-----------|---------------|--------------|---------------------------|
| Tory specjalne (EnumTrack) | 48 | ~28 | ~20 (deprecated + specjalne) |
| Maszyny Alpha | 16 | 7 | 9 (anchory + pułapki + admin) |
| Maszyny Beta | 16 | 10 | 6 (anchory + tanks lossy) |
| Maszyny Gamma | 12 | 8 | 4 (dispensery lossy) |
| Maszyny Delta | 2 | 1 | 1 |
| Maszyny Epsilon | 6 | 2 | 4 |
| Sygnały (EnumSignal) | 14 | 7 | 7 (boxy logiczne lossy) |
| Detektory (EnumDetector) | 17 | 17 | 0 (ale wszystkie lossy) |
| Inne bloki | 4 | 2 | 2 |
| **RAZEM** | **135** | **~82** | **~53** |

**Stopień konwersji: ~60%** (82/135). Reszta to placeholdery lub usunięcia ze względu na:
- Brak odpowiedników w 1.18.2 (anchory, pułapki parowe, engraving bench, force track)
- Inna mechanika (sygnały kolejowe, zaawansowane tory)
- Tory deprecated w 1.7.10 (boarding, holding, lockdown)

### 1.2 Kluczowe mapowania maszyn

| Railcraft 1.7.10 | Target 1.18.2 | Uzasadnienie |
|------------------|---------------|--------------|
| Coke Oven | `immersiveengineering:coke_oven` | IE ma bezpośredni odpowiednik |
| Blast Furnace | `immersiveengineering:blast_furnace` | IE ma bezpośredni odpowiednik |
| Rock Crusher | `create:crushing_wheel` | Funkcja kruszenia rud |
| Rolling Machine | `create:mechanical_press` | Funkcja formowania płyt |
| Steam Oven | `minecraft:smoker` | Funkcja pieczenia |
| Steam Turbine | `thermal:dynamo_stirling` | Funkcja para→energia |
| Boiler (LP/HP) | `thermal:dynamo_stirling` / `compression` | Funkcja para→energia |
| Steam Engines | `create:steam_engine` | Bezpośredni odpowiednik funkcji |
| Iron/Steel Tank | `create:fluid_tank` | Storage płynów |
| Void Chest | `thermal:device_nullifier` | Niszczenie itemów |
| Metals Chest | `ironchest:iron_chest` | Storage metali |
| Sawmill | `create:mechanical_saw` / `thermal:machine_sawmill` | Funkcja piłowania |

### 1.3 Mapowania torów

| Typ toru Railcraft | Target 1.18.2 | Uwagi |
|-------------------|---------------|-------|
| Standard/Switch/Junction/Wye | `create:track` | Create obsługuje zwrotnice automatycznie |
| High Speed / Reinforced / Electric | `create:track` | Lossy: brak boostera/elektryfikacji |
| Wooden / Slow | `minecraft:rail` | Lossy |
| Coupler | `railways:track_coupler` | Steam'n'Rails |
| Control | `minecraft:powered_rail` | Lossy |
| Buffer Stop, Launcher, Priming, Routing, Whistle, Locomotive, Limiter | Placeholder | Brak odpowiednika |

### 1.4 Mapowania logistyki (Loadery/Unloaderzy)

| Railcraft | Target 1.18.2 | Uwagi |
|-----------|---------------|-------|
| Item Loader/Unloader | `create:chute` / `smart_chute` | Lossy: brak integracji z wagonami |
| Fluid Loader/Unloader | `create:fluid_pipe` | Lossy |
| Energy Loader/Unloader (IC2/RF) | `mekanism:basic_universal_cable` | Lossy |
| Cart/Train Dispenser | `minecraft:dispenser` | Lossy |

### 1.5 Mapowania sygnałów

| Railcraft | Target 1.18.2 | Uwagi |
|-----------|---------------|-------|
| Block Signal / Distant Signal | `railways:semaphore` | Steam'n'Rails (lossy: brak parowania) |
| Switch Motor / Routing Motor | `create:clutch` | Lossy |
| Switch Lever | `minecraft:lever` | 1:1 mechanicznie |
| Controller/Receiver/Capacitor/Sequencer/Interlock/Analog Box | `minecraft:comparator` / `repeater` | Bardzo lossy |
| Signal Block Relay | `minecraft:repeater` | Lossy |

### 1.6 Mapowania detektorów

Wszystkie 17 detektorów → `minecraft:observer` (z utratą specyficznej detekcji).

---

## 2. Symulacje konwersji NBT (`simulations/railcraft_simulation.py`)

### 2.1 `convert_track_nbt()`

Obsługuje konwersję TileTrack:
- `trackTag` → `blockstate_props["shape"]`
- Legacy `trackId` → ostrzeżenie `RC-W-TRACK-LEGACY-ID`
- Specjalne funkcje torów → ostrzeżenie `RC-W-TRACK-SPECIAL-LOST`

### 2.2 `convert_machine_inventory_nbt()`

Zachowuje `Items` z formatu 1.7.10 (z ostrzeżeniem o konieczności globalnego remappingu ID itemów).

### 2.3 `convert_multiblock_nbt()`

Dla Coke Oven, Blast Furnace, Boiler, Tanks:
- Zapisuje flagę `master` w `legacy_railcraft`
- Ostrzeżenie `RC-W-MULTIBLOCK` o konieczności ręcznej rekonstrukcji

### 2.4 `convert_signal_nbt()`

- Semafory → `railways:semaphore` (blockstate `rotation`)
- Boxy logiczne → utrata konfiguracji (pary, czasy, interlocking)

### 2.5 `convert_detector_nbt()`

- Wszystkie detektory → `observer` (utrata specyfiki)

### 2.6 `convert_anchor_nbt()`

- Wszystkie anchory → placeholder + ostrzeżenie o utracie chunk loading

---

## 3. Testy (`tests/test_railcraft_simulations.py`)

| Klasa testowa | Testy | Opis |
|---------------|-------|------|
| `TestTrackMappings` | 5 | Mapowania torów (switch, deprecated, electric, buffer, coupler) |
| `TestMachineAlphaMappings` | 5 | Maszyny alpha (coke oven, blast furnace, rock crusher, anchor, rolling machine) |
| `TestMachineBetaMappings` | 3 | Maszyny beta (steam engine, tank, void chest) |
| `TestMachineGammaMappings` | 2 | Logistyka (item loader, energy loader) |
| `TestSignalMappings` | 2 | Sygnały (block signal, switch lever) |
| `TestDetectorMappings` | 1 | Wszystkie detektory → observer |
| `TestOtherMappings` | 1 | Residual Heat → air |
| `TestTrackNBTConversion` | 3 | NBT torów (switch, booster, legacy) |
| `TestInventoryConversion` | 2 | Zachowanie inventory, puste NBT |
| `TestMultiblockConversion` | 1 | Flag master w legacy |
| `TestSignalNBTConversion` | 2 | Ostrzeżenia o utracie sygnałów |
| `TestDetectorNBTConversion` | 1 | Observer + warning |
| `TestAnchorNBTConversion` | 1 | Anchor lost warning |
| `TestEndToEndSimulation` | 3 | E2E: coke oven, hidden tile, unknown block |

**Wynik: 32/32 passed**

---

## 4. Utworzone / zmodyfikowane pliki

### Nowe pliki
- `src/converters/railcraft/mappings/block_mappings.py` — 135 mapowań bloków (~60% konwersji)
- `src/converters/railcraft/simulations/__init__.py`
- `src/converters/railcraft/simulations/railcraft_simulation.py` — symulacje NBT per typ TE
- `src/converters/railcraft/tests/__init__.py`
- `src/converters/railcraft/tests/test_railcraft_simulations.py` — 32 testy jednostkowe

### Pliki z Zadania 1 (bez zmian)
- `src/converters/railcraft/mappings/block_inventory.py`
- `src/converters/railcraft/HANDOFF_RAILCRAFT_ZADANIE1.md`

---

## 5. Otwarte problemy i decyzje do podjęcia

### 5.1 Wymaga decyzji użytkownika
- [ ] **Czy instalować Create: Steam 'n' Rails w paczce 1.18.2?** — Bez tego modu mapowania torów i sygnałów na `railways:*` będą nieprawidłowe.
- [ ] **Czy instalować Immersive Engineering?** — Potrzebny dla Coke Oven i Blast Furnace.
- [ ] **Chunk loadery (Anchory)** — czy dodać mod chunk loaderów do 1.18.2 (np. FTB Chunks), czy zostawić placeholdery?

### 5.2 Wymaga dalszej pracy
- [ ] Weryfikacja blockstates modów docelowych (Create, Steam'n'Rails, IE, Mekanism, Thermal) na podstawie JARów 1.18.2
- [ ] Konwersja ID itemów w inventory (globalny remapping)
- [ ] Obsługa płynów w maszynach (tanks, boilers, fluid loaders)
- [ ] Implementacja głównego konwertera (`railcraft_converter.py`) w Zadaniu 3

---

## 6. Następne kroki (Zadanie 3)

1. **Implementacja głównego konwertera** (`railcraft_converter.py`)
   - Routing per `nbt_converter` z block_mappings
   - Integracja z `common/placeholders.py`
   - Rejestracja w `converters/router.py`

2. **Konwertery NBT per-typ**
   - `nbt_converters/track_converter.py`
   - `nbt_converters/multiblock_converter.py`
   - `nbt_converters/signal_converter.py`

3. **Analiza pokrycia mapy** — sprawdzenie które bloki Railcrafta faktycznie występują na `mapa_1710`

---

*Dokument utworzony: 2026-05-20*
*Źródła: Dekompilacja Railcraft 9.12.2.0, dokumentacja projektu (Codex cz4), CurseForge weryfikacja dostępności modów 1.18.2*
