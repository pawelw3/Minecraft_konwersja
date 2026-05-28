# Handoff: Extra Utilities - Zadanie 2

## Podsumowanie sesji

Wykonano Zadanie 2 konwersji Extra Utilities — symulacje funkcjonalności i konwersję NBT. Na podstawie dekompilacji JAR oraz realnych danych z mapy (3x `extrautils:generatorlava`, 267x `TileEntityAntiMobTorch`) zaimplementowano dedykowane NBT converters dla generatorów oraz zaktualizowano symulacje. Wszystkie testy przechodzą (27/27).

## Ukończono

- [x] Wyciągnięcie przykładowych NBT z mapy (`mapa_1710/region/`) dla ExU TE
- [x] Analiza struktury NBT z dekompilacji `extrautilities-1.2.12.jar`
- [x] Stworzenie `nbt_converters/base_converter.py` — rotation→facing, energy RF→FE, fluid tank
- [x] Stworzenie `nbt_converters/generator_converter.py` — pełna konwersja NBT generatora
- [x] Rozszerzenie symulacji o obsługę NBT dla generatorów
- [x] Aktualizacja testów: 27 testów (w tym 8 nowych dla NBT converters)
- [x] Weryfikacja E2E przez router — generuje poprawny Event JSON z NBT i blockstate

---

## Struktura NBT z mapy

### `extrautils:generatorlava` (3 wystąpienia)
```json
{
  "backup": {"x": -88, "y": 50, "z": 903, "id": "extrautils:generatorlava"},
  "Energy": 0,
  "rotation": 3,
  "x": -88, "y": 50, "z": 903,
  "Tank_0": {"Empty": ""},
  "coolDown": 0.0
}
```

### `TileEntityAntiMobTorch` (267 wystąpień)
```json
{
  "x": -221, "y": 67, "z": -350,
  "id": "TileEntityAntiMobTorch"
}
```

---

## Analiza struktury NBT z dekompilacji

### `TileEntityGenerator` (baza dla wszystkich generatorów)
- `storage`: `EnergyStorage(100000)` — RF
- `rotation`: byte 0-3 — orientacja
- `coolDown`: double
- `getTanks()`: `FluidTank[]` — tanki na płyny (np. lava)
- `getInventory()`: `IInventory` — sloty paliwa

### `TileEntityAntiMobTorch`
- Brak własnych pól NBT
- Rejestracja w `EventHandlerServer.magnumTorchRegistry` (globalna lista koordynatów)
- `getHorizontalTorchRangeSquared()`: 16384 dla MagnumTorch, 256 dla Chandelier
- `getVerticalTorchRangeSquared()`: 1024 dla MagnumTorch, 256 dla Chandelier

---

## Konwersja NBT

### Generatory ExU → Thermal Dynamo

| Pole ExU 1.7.10 | Pole 1.18.2 | Uwagi |
|---|---|---|
| `Energy` (int RF) | `energy: {Stored, Capacity}` | 1 RF = 1 FE, Capacity=100000 |
| `rotation` (byte 0-3) | `blockstate: facing` | 0=south, 1=west, 2=north, 3=east |
| `Tank_0` (CompoundTag) | `fuel: {FluidName, Amount}` | Tylko jeśli niepusty |
| `coolDown` (double) | — | **Utracone** — brak odpowiednika |
| `backup` (CompoundTag) | — | **Ignorowane** — kopia zapasowa samego TE |
| `Items` (NBTTagList) | — | **Utracone** — dynama nie mają inventory itemów |

### AntiMobTorch → Torchmaster Mega Torch
- Brak konwersji NBT — zamiana block_id wystarcza

---

## Nowe pliki

- `src/converters/extrautils/nbt_converters/__init__.py`
- `src/converters/extrautils/nbt_converters/base_converter.py` — `convert_rotation_to_facing`, `convert_energy`, `convert_fluid_tank`, `build_base_nbt_1182`
- `src/converters/extrautils/nbt_converters/generator_converter.py` — `convert_generator_nbt`

## Zmodyfikowane pliki

- `src/converters/extrautils/simulations/extrautils_simulation.py`
  - Dodano import `convert_generator_nbt`
  - Rozszerzono logikę o wywołanie dedykowanego konwertera NBT dla generatorów

- `src/converters/extrautils/tests/test_extrautils_converter.py`
  - Dodano 8 nowych testów dla NBT converters
  - Zaktualizowano `test_convert_generator_lava_block` o wariant z realnym NBT

---

## Testy

**27/27 testów przechodzi**, w tym:
- 10 testów mapowań bloków
- 9 testów konwersji bloków/TE (w tym 4 z NBT)
- 5 testów NBT converters (rotation, energy, fluid, generator_nbt_full)
- 3 testy kompletności TE_ID_TO_BLOCK

Weryfikacja E2E przez `converters.router.convert_te_to_events()` generuje:
```json
[{
  "op": "set_block_entity",
  "pos": [-88, 50, 903],
  "block": "thermal:dynamo_magmatic",
  "nbt": {
    "id": "thermal:dynamo_magmatic",
    "x": -88, "y": 50, "z": 903,
    "energy": {"Stored": 0, "Capacity": 100000}
  },
  "blockstate": {"facing": "east"},
  "warnings": ["EXU-W-MAPPING: Lava Generator → Magmatic Dynamo"]
}]
```

---

## Następne kroki

1. [ ] Zadanie 3 — Rozszerzenie mapowań o pozostałe bloki
   - `extrautils:drum` → `extrautilitiesreborn:drum` (konwersja płynu w NBT)
   - `extrautils:filingCabinet` → placeholder / nowy mod storage
   - `extrautils:enderThermicPump` → `mekanism:electric_pump`
   - `extrautils:enderQuarry` → `rftoolsbuilder:builder` + quarry card NBT
   - `extrautils:conveyor` → `create:belt`
   - Bloki dekoracyjne (compressed cobble, spikes, itp.)

2. [ ] Zadanie 4 — Sprawdzenie pokrycia na mapie głównej
   - Przeszukanie wszystkich regionów pod kątem block ID `extrautils:*`
   - Weryfikacja czy mappingi pokrywają 100% wystąpień

3. [ ] Zadanie 5 — Testowa mapa i konwersja E2E
   - Świat testowy z generatorami, magnum torch, drum, trash can
   - Weryfikacja w grze po konwersji

4. [ ] Zadanie 6 — Test headless serwer
   - 3 minuty ticków + restart

---

*Data utworzenia: 2026-05-27*
*Zadanie 2 zakończone*
