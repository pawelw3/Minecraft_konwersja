# Handoff: Thermal Series - Zadanie 2

## Podsumowanie sesji

Wykonano Zadanie 2 dla **Thermal Series**: przygotowano symulacje funkcjonalnosci (maszyny, dynama, ducty), zbadano struktury NBT 1.7.10 przez dekompilacje JARow, stworzono kompletne konwertery NBT oraz mappingi blokow z **fallbackami na Mekanism** tam gdzie Thermal 1.18.2 nie ma odpowiednika.

## Ukonczono

- [x] **Symulacje funkcjonalnosci** w Pythonie:
  - `simulations/machine_simulation.py` — przetwarzanie rud, alloying, procesy maszyn
  - `simulations/dynamo_simulation.py` — generowanie energii (RF/FE), farmy dynam
  - `simulations/duct_simulation.py` — transport energii, plynow, itemow przez sieci
- [x] **Konwertery NBT** dla 1.7.10 -> 1.18.2:
  - `nbt_converters/base_converter.py` — wspolne funkcje (facing, tier, energy, inventory, augments, side_config)
  - `nbt_converters/machine_converter.py` — maszyny (12 typow)
  - `nbt_converters/storage_converter.py` — Cell, Tank, Strongbox, Cache, Workbench
  - `nbt_converters/dynamo_converter.py` — dynama (5 typow)
  - `nbt_converters/duct_converter.py` — ducty + Tesseract -> Quantum Entangloporter
- [x] **Mappingi blokow** z fallbackami na Mekanism:
  - Tesseract -> `mekanism:quantum_entangloporter` (frequency-based teleport energy/fluid/item/gas)
  - Fluid Pump -> `mekanism:electric_pump`
  - Ender Itemduct -> `mekanism:basic_logistical_transporter`
  - Teleport Plate -> `mekanism:teleporter`
  - Reactant Dynamo -> `thermal:dynamo_compression`
  - Enervation Dynamo -> `thermal:dynamo_lapidary`
- [x] **Glowny konwerter** `thermal_converter.py` — klasa `ThermalConverter` z dispatchiem per NBT converter
- [x] **40 testow jednostkowych** — wszystkie przechodza

## Nowe pliki

- `src/converters/thermal/mappings.py` — pelne mappingi 1.7.10 -> 1.18.2 (+ Mekanism fallbacki)
- `src/converters/thermal/thermal_converter.py` — glowny konwerter z dispatchiem
- `src/converters/thermal/simulations/machine_simulation.py`
- `src/converters/thermal/simulations/dynamo_simulation.py`
- `src/converters/thermal/simulations/duct_simulation.py`
- `src/converters/thermal/nbt_converters/base_converter.py`
- `src/converters/thermal/nbt_converters/machine_converter.py`
- `src/converters/thermal/nbt_converters/storage_converter.py`
- `src/converters/thermal/nbt_converters/dynamo_converter.py`
- `src/converters/thermal/nbt_converters/duct_converter.py`
- `src/converters/thermal/tests/test_mappings.py`
- `src/converters/thermal/tests/test_nbt_converters.py`
- `src/converters/thermal/tests/test_simulations.py`
- `src/converters/thermal/HANDOFF_THERMAL_ZADANIE2.md` — ten dokument

## Zmodyfikowane pliki

- `src/converters/thermal/simulations/__init__.py`
- `src/converters/thermal/nbt_converters/__init__.py`
- `src/converters/thermal/tests/__init__.py`
- `src/converters/__init__.py` (utworzony)
- `src/converters/thermal/__init__.py` (utworzony)

## Kluczowe ustalenia

### Fallbacki na Mekanism (decyzja projektowa)

| Element 1.7.10 | Brak w Thermal 1.18.2 | Fallback Mekanism | Uwagi |
|---|---|---|---|
| **Tesseract** | Brak odpowiednika | `mekanism:quantum_entangloporter` | Frequency mapowane na nazwe + kolory. Tryby item/fluid/energy zachowane, gas domyslnie wylaczony. |
| **Fluid Pump** | Brak w TE 1.18.2 devices | `mekanism:electric_pump` | Funkcjonalny odpowiednik (pompuje plyny, zuzywa energie). |
| **Ender Itemduct** | Brak w TD 1.18.2 | `mekanism:basic_logistical_transporter` | Transport itemow z kolorami/frequency. |
| **Teleport Plate** | Brak w TE 1.18.2 | `mekanism:teleporter` | Teleportacja graczy/entity. |

### Pozostale elementy bez odpowiednika (lossy conversion)

| Element 1.7.10 | Konwersja | Uwagi |
|---|---|---|
| Autonomous Activator | `minecraft:dispenser` | Czesciowa strata funkcjonalnosci (dispenser nie kliknie PPM). |
| Terrain Smasher | `thermal:device_nullifier` | Placeholder — breaker nie ma dobrego zamiennika. |
| Reactant Dynamo | `thermal:dynamo_compression` | Inne paliwo, podobna funkcja. |
| Enervation Dynamo | `thermal:dynamo_lapidary` | Gems zamiast energy items. |
| Viaducty (TransportDuct) | `minecraft:rail` | Calkowita strata — transport entity. |
| Plates (Excursion, Impulse, Signal, Translocate) | Vanilla bloki | Calkowita strata — physics plates. |
| Light / LightFalse | Glowstone / Air | Dekoracyjne. |

### NBT — najwazniejsze roznice

| Pole 1.7.10 | Pole 1.18.2 | Uwagi |
|---|---|---|
| `Facing` (byte 0-5) | `facing` (string) | Mapowanie: 0=down, 1=up, 2=north, 3=south, 4=west, 5=east |
| `Type` (byte 0-4) | `type` (string) / blockstate | Tier: 0=basic, 1=hardened, 2=reinforced, 3=resonant, 4=creative |
| `Energy` (int / compound) | `energy` (compound) | RF -> FE 1:1, zachowana wartosc |
| `Items` (NBTTagList) | `Items` (ListTag) | Mapowanie ID itemow thermal:* |
| `Tank` (compound) | `tank` (compound) | FluidName + Amount zachowane |
| `RedstoneControl` (byte) | `redstone_control` (string) | 0=ignored, 1=low, 2=high |
| `SideCache` / `SideConfig` | `side_config` (int array) | 6 elementow, wartosci bez zmian |
| `Augments` (list) | `augments` (ListTag) | Zachowane jako itemy w slotach augment |

### Ryzyka dla kolejnych zadan

1. **Inventory Strongbox -> Item Cell** — Strongbox byl skrzynia (9-45 slotow), Item Cell przechowuje 1 typ itemu. **Lossy conversion** — trzeba zdecydowac czy zachowac tylko 1 typ czy rozrzucic itemy.
2. **Ducty** — najwyzsza objetosc na mapie (~10k TE). Uproszczony system w 1.18.2, konwersja moze wymagac rekonstrukcji polaczen.
3. **Tesseract -> Quantum Entangloporter** — frequency mapping wymaga testowania w praktyce (czy nazwa frequency nie koliduje).
4. **Augmenty** — w 1.18.2 augmenty moga miec inne ID lub nie istniec. Wymaga mapowania itemow.

## Nastepne kroki (Zadanie 3)

1. [ ] **Kod konwersji mapy** — zintegrowac `ThermalConverter` z pipeline'em konwersji chunkow
2. [ ] **Testowa mapa 1.7.10** — utworzyc swiat testowy z reprezentatywnymi blokami Thermal
3. [ ] **Weryfikacja NBT** — porownac output NBT z 1.18.2 Thermal JAR (dekompilacja lub test na serwerze)
4. [ ] **Obsluga Fluid Registry** — mapowanie plynow Thermal Foundation (pyrotheum, cryotheum, etc.)
5. [ ] **Item conversion** — mapowanie itemow Thermal (augments, upgrades, materials) na 1.18.2
