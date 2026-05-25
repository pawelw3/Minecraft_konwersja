# Handoff: IC2 Zadanie 4 — Pokrycie mapy + weryfikacja NBT z kodu źródłowego 1.18.2

## Podsumowanie sesji
Wykonano skanowanie mapy źródłowej, dekompilację modów Tier-1 (indreb, ftbic),
weryfikację NBT shapes i poprawkę symulacji. Korekta 2026-05-20: pierwotny
wniosek "0 bloków/TE IC2" był błędny, bo skaner nie rozpoznawał krótkich
Forge registry ids IC2 (`Macerator`, `Cable`, `TECrop`, ...).

## Ukończono
- [x] Skanowanie mapy `mapa_1710/`
  - Pierwotnie: próbka ~5975 chunków z 1195 regionów, błędnie sklasyfikowana jako 0 TE IC2
  - Korekta: pełny skan `docs/sprawdzenie_codex/cz3_targeted_te_scan_2026-05-18.json`
    znalazł **781 TE IC2** w 665995 chunkach
  - Najczęstsze: `Reactor Chamber` 138, `Solar Panel` 135, `MFSU` 53,
    `Compressor` 52, `Metal Former` 49, `Macerator` 46, `Electric Furnace` 35
- [x] Dekompilacja JARów 1.18.2 (vineflower.jar):
  - `indreb-1.18.2-0.13.0.jar` → `output/ic2_analysis/decompiled/indreb_full/`
  - `ftb-industrial-contraptions-1802.1.6-build.220.jar` → `output/ic2_analysis/decompiled/ftbic/`
- [x] Analiza klas bazowych BE:
  - indreb: `IndRebBlockEntity` (energy int, inventory/battery/upgrade ItemStackHandler)
  - indreb: `BlockEntityStandardMachine` (active bool, progress CompoundTag)
  - indreb: `BlockEntityGenerator` (progress = burn time!)
  - indreb: `BlockEntityTransformer` (transformerMode int)
  - indreb: `BlockEntityCable` (brak override save/load — **brak NBT**)
  - ftbic: `ElectricBlockEntity` (Energy double, Inventory ListTag)
  - ftbic: `MachineBlockEntity` (Progress/MaxProgress double)
- [x] Poprawka symulacji do zgodności z dekompilacją:
  - `machine_simulation.py` — indreb/ftbic branches + `extract_inventory_indreb()`
  - `energy_storage_simulation.py` — indreb (flat energy) / ftbic (Energy double)
  - `cable_simulation.py` — indreb: brak NBT
  - `converter_registry.py` — nowy `TransformerConverter`
  - `block_mappings.py` — transformatory: identity → transformer
- [x] Testy snapshotowe NBT:
  - `TestIndrebNBTShape` (4 testy)
  - `TestFTBICNBTShape` (2 testy)
  - 44/44 testów IC2 pass
- [x] Raport: `output/ic2_analysis/ic2_zadanie4_report.md`

## Nowe pliki
- `output/ic2_analysis/ic2_zadanie4_report.md`
- `output/ic2_analysis/decompiled/indreb_full/` (dekompilacja)
- `output/ic2_analysis/decompiled/ftbic/` (dekompilacja)
- `src/converters/ic2/map_scanner.py` (skrypt skanujący mapę)

## Zmodyfikowane pliki
- `src/converters/ic2/simulations/machine_simulation.py` — indreb/ftbic NBT shapes
- `src/converters/ic2/simulations/energy_storage_simulation.py` — indreb/ftbic energy format
- `src/converters/ic2/simulations/cable_simulation.py` — indreb: no NBT
- `src/converters/ic2/nbt_converters/converter_registry.py` — TransformerConverter
- `src/converters/ic2/mappings/block_mappings.py` — transformer mapping fix
- `src/converters/ic2/tests/test_ic2_converter.py` — nowe testy (transformer, NBT shape)
- `src/converters/ic2/tests/test_ic2_simulations.py` — nowe testy (IndrebNBTShape, FTBICNBTShape)

## Kluczowe odkrycia

### 1. IC2 jest na mapie
Na mapie źródłowej (5GB, 1195 regionów) **są TileEntities IC2**. Poprzedni wniosek
wynikał z błędnego założenia, że IC2 zapisuje TE jako `TileEntity*` class names.
IC2 experimental 2.2.827 zapisuje wiele TE jako krótkie registry ids, np.
`Macerator`, `Cable`, `TECrop`, `MFSU`, `Reactor Chamber`.

### 2. NBT shapes — różnice przed/po poprawkach

| Target | Przed | Po |
|--------|-------|-----|
| indreb maszyna | `energy`, `operatingTicks`, `Items` | `energy`, `active`, `progress:{progress,progressMax}`, `inventory:{Size,Items}` |
| indreb storage | `energyContainer` | flat `energy` |
| indreb cable | jakieś NBT | **brak NBT** |
| indreb transformer | brak NBT | `energy`, `transformerMode` |
| ftbic maszyna | `energy`, `operatingTicks`, `Items` | `Energy`, `Progress`, `MaxProgress`, `Inventory` |

### 3. Inventory slot mapping
`extract_inventory_indreb()` mapuje `InvSlots` IC2 (lokalne indeksy per-kategoria) na globalne sloty
indreb: `input.*` → 0+, `output.*` → kolejne, `battery.*` → `battery` handler, `upgrade.*` → `upgrade` handler.

## Następne kroki
1. **Zadanie 5A** — test E2E na realnych chunkach z głównej mapy zawierających
   `Macerator`, `Cable`, `TECrop`, `Reactor Chamber`.
2. Uzupełnić raporty/pipeline, żeby używały registry ids IC2, a nie tylko nazw klas.

## Otwarte kwestie
- `extract_inventory_indreb` używa uproszczonego mapowania slotów — w maszynach z wieloma
  slotami input/output może wymagać dopracowania.
- Generator progress w indreb to **burn time**, nie crafting progress — mapowanie może być
  nieintuicyjne, ale w praktyce generator zainicjalizuje nowy cykl po załadowaniu paliwa.
- 43 placeholdery bez Tier-1 odpowiednika — do rozważenia przy testowej mapie.
