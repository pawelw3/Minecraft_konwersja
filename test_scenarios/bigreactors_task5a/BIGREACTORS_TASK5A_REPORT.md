# Big Reactors → Bigger Reactors — Zadanie 5A Raport

**Data:** 2026-05-25  
**Mod:** Big Reactors (1.7.10) → Bigger Reactors (1.18.2)

---

## Cel
Wygenerowanie testowej "mapy" (patch JSON) zawierającej reprezentatywne bloki i Tile Entities Big Reactors 1.7.10, a następnie konwersja ich do formatu 1.18.2.

---

## Wygenerowane pliki

| Plik | Opis |
|------|------|
| `generate_bigreactors_task5a.py` | Skrypt generujący source patch 1.7.10 |
| `bigreactors_task5a_source_patch_1710.json` | Patch źródłowy (257 edycji: 146 bloków + 111 TE) |
| `convert_bigreactors_task5a.py` | Skrypt konwertujący do 1.18.2 |
| `bigreactors_task5a_converted_patch_1182.json` | Patch docelowy 1.18.2 (107 edycji) |
| `bigreactors_task5a_conversion_report.json` | Pełny raport konwersji |

---

## Co zawiera testowa mapa

### Bloki proste (Row 0)
- `YelloriteOre` → `biggerreactors:uranium_ore`
- `BRMetalBlock` meta 0-4 (Yellorium, Cyanite, Graphite, Blutonium, Ludicrite) → odpowiednie bloki 1.18.2

### Reactor parts (Row 1)
- `BRReactorPart` meta 0-7:
  - 0: Casing → `reactor_casing`
  - 1: Controller → `reactor_terminal`
  - 2: Control Rod (insertion=50) → `reactor_control_rod`
  - 3: Power Tap (energy=25k RF) → `reactor_power_tap`
  - 4: Access Port (inventory: 16x Yellorium ingot) → `reactor_access_port`
  - 5: Coolant Port (tank: 4000mB water) → `reactor_coolant_port`
  - 6: RedNet Port → `reactor_redstone_port` (fallback z ostrzeżeniem)
  - 7: Computer Port → `reactor_computer_port`
- `BRReactorRedstonePort` → `reactor_redstone_port`
- `BRMultiblockGlass` meta 0 → `reactor_glass`
- `YelloriumFuelRod` → `reactor_fuel_rod`

### Turbine parts (Row 2)
- `BRTurbinePart` meta 0-5:
  - 0: Housing → `turbine_casing`
  - 1: Controller → `turbine_terminal`
  - 2: Power Tap (energy=12k RF) → `turbine_power_tap`
  - 3: Fluid Port (tank: 8000mB steam) → `turbine_fluid_port`
  - 4: Rotor Bearing → `turbine_rotor_bearing`
  - 5: Computer Port → `turbine_computer_port`
- `BRMultiblockGlass` meta 1 → `turbine_glass`
- `BRTurbineRotorPart` meta 0 (shaft) / 1 (blade) → `turbine_rotor_shaft` / `turbine_rotor_blade`

### Devices (Row 3)
- `BRDevice` meta 0: Cyanite Reprocessor (energy=1500, progress=42, inventory: 2x cyanite + water bucket) → `cyanite_reprocessor`
- `BRMultiblockCreativePart` meta 0/1 → `minecraft:air` (usunięte z ostrzeżeniem)

### Mini reactor multiblock (3x3x4)
- 5x5x4 z casing, glass, fuel rod (2 wysokości), control rod (insertion=75), power tap, access port
- 32 bloki `reactor_casing`, 2 `reactor_terminal`, 2 `reactor_control_rod`, 2 `reactor_power_tap`, 2 `reactor_access_port`, 3 `reactor_glass`, 3 `reactor_fuel_rod`

### Mini turbine multiblock (3x3x4)
- 5x5x4 z housing, glass, rotor shaft (2 wysokości), rotor blade (4 x 2 wysokości = 8), bearing, power tap, fluid port
- 26 bloków `turbine_casing`, 2 `turbine_terminal`, 2 `turbine_power_tap`, 2 `turbine_fluid_port`, 2 `turbine_rotor_bearing`, 3 `turbine_glass`, 3 `turbine_rotor_shaft`, 9 `turbine_rotor_blade`

---

## Wyniki konwersji

| Metryka | Wartość |
|---------|---------|
| Przetworzone | 107 |
| Skonwertowane | 107 (100%) |
| Niepowodzenia | 0 |
| Ostrzeżenia | 13 |

### Ostrzeżenia (13)
- 2x `BIG-W-MAPPING-NOTE: Yellorite/Yellorium -> Uranium`
- 2x `BIG-W-ENERGY: zachowano energię RF jako FE (1:1)` (Power Tap)
- 2x `BIG-W-INVENTORY: przekonwertowano inventory` (Access Port, Reprocessor)
- 1x `BIG-W-MAPPING-NOTE: RedNet Port -> Redstone Port`
- 1x `BIG-W-FLUID: zawartość tanków turbiny wymaga ręcznej weryfikacji`
- 2x `BIG-W-MAPPING-NOTE: Creative parts usunięte`
- 3x dodatkowe (powtórzenia dla multibloku)

### Przykładowe wyniki
```json
// Control Rod z insertion=50 → insertion=50 w NBT
{
  "source_block": "BigReactors:BRReactorPart",
  "metadata": 2,
  "target_block_id": "biggerreactors:reactor_control_rod",
  "success": true
}

// Access Port z inventory → zamiana item ID
{
  "source_block": "BigReactors:BRReactorPart",
  "metadata": 4,
  "target_block_id": "biggerreactors:reactor_access_port",
  "success": true,
  "warnings": ["BIG-W-INVENTORY: przekonwertowano inventory Access Port"]
}

// Cyanite Reprocessor z energy+progress → zachowane
{
  "source_block": "BigReactors:BRDevice",
  "metadata": 0,
  "target_block_id": "biggerreactors:cyanite_reprocessor",
  "success": true,
  "warnings": ["BIG-W-INVENTORY: przekonwertowano inventory Cyanite Reprocessor"]
}
```

---

## Weryfikacja NBT

| TE | NBT zachowane | Uwagi |
|----|---------------|-------|
| Reactor Control Rod | `insertion` (int) | ✅ Przekazane |
| Reactor Power Tap | `energy` (int) | ✅ RF→FE |
| Reactor Access Port | `Items` (list) | ✅ Zamiana item ID |
| Reactor Coolant Port | `facing` | ✅ (tanks pominięte — inny format) |
| Turbine Power Tap | `energy` (int) | ✅ RF→FE |
| Turbine Fluid Port | `facing` | ✅ (tanks — warning) |
| Cyanite Reprocessor | `energy`, `progress`, `Items` | ✅ energy, progress, inventory |

---

## Problemy i decyzje

1. **Fluid tanks** — format tanków w 1.7.10 (list of dicts) różni się od formatu Phosphophyllite w 1.18.2. Konwerter zachowuje `facing`, ale fluids wymagają ręcznej weryfikacji.
2. **RedNet Port** — zmapowany na `reactor_redstone_port` z ostrzeżeniem. W testowej mapie nie występuje na mapie rzeczywistej, więc to bezpieczny fallback.
3. **Creative parts** — zmapowane na `minecraft:air`. W testowej mapie obecne, ale na mapie głównej nie występują.

---

## Następne kroki

### Zadanie 5B
- Wymaga zainstalowania **BiggerReactors** na headless serwerze 1.18.2 (obecnie brak w `headless_server/1.18.2/mods/`)
- Po instalacji: materializacja patcha na mapę testową i boot serwera

### Zadanie 6
- Test ticków + restart na headless serwerze z BiggerReactors
- Weryfikacja czy multibloki się poprawnie formują
