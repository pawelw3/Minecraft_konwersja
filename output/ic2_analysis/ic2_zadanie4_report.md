# Raport: IC2 Zadanie 4 - Pokrycie mapy i weryfikacja NBT (indreb/ftbic)

## 1. Skanowanie mapy źródłowej (mapa_1710/)

### Korekta 2026-05-20
Poprzedni wniosek z tej sekcji był błędny. Skaner IC2 rozpoznawał głównie
`TileEntity*` class names, a IC2 experimental 2.2.827 zapisuje wiele
`TileEntities[].id` jako krótkie nazwy rejestracyjne Forge, np. `Macerator`,
`Cable`, `TECrop`, `MFSU`.

### Metodologia po korekcie
- Źródło prawdy: `docs/sprawdzenie_codex/cz3_targeted_te_scan_2026-05-18.json`
  oraz kontrolny skan `output/ic2_scan/ic2_registry_candidate_parsed_tileentities.json`
- Przeskanowano `1195` regionów i `665995` chunków z danymi
- Łącznie przejrzano `2447396` tile entities
- Jeden chunk w `r.-10.2.mca` ma błąd dekompresji (`incomplete or truncated stream`)

### Wynik po korekcie
**IC2 jest obecny na mapie źródłowej jako TileEntities.**

- Znalezionych TileEntities IC2: **781**
- Najważniejsze typy: `Reactor Chamber` 138, `Solar Panel` 135, `MFSU` 53,
  `Compressor` 52, `Metal Former` 49, `Macerator` 46, `Electric Furnace` 35,
  `Nuclear Reactor` 23, `Extractor` 21, `Generator` 18

### Mod obecny na mapie (dla kontekstu)
Spośród 88 unikalnych TE ID na mapie znaleziono m.in.:
- AE2 (BlockCableBus, BlockSkyChest, Bin)
- Railcraft (RCRollingMachineTile, RCSmokerTile)
- Thaumcraft (TileEldritchAltar, TileJar, TileNode, TileMirror)
- Carpenter's Blocks (TileEntityCarpentersBlock)
- BiblioCraft, MrCrayfish's Furniture, BetterStorage, Forestry
- GrowthCraft, Thermal Expansion/Dynamics, ProjectRed
- BuildCraft, ComputerCraft, Traincraft, CustomNPCs
- Armourer's Workshop, Turrets

**Wniosek:** Konwersja IC2 musi być traktowana jako potrzebna dla głównej mapy.
Poprzednie stwierdzenie "IC2 nie jest obecny na mapie" należy odrzucić.

---

## 2. Weryfikacja NBT z kodem źródłowym modów 1.18.2

### 2.1 Dekompilacja
Wykonano dekompilację JARów kandydatów Tier-1:
- `indreb-1.18.2-0.13.0.jar` → `output/ic2_analysis/decompiled/indreb_full/`
- `ftb-industrial-contraptions-1802.1.6-build.220.jar` → `output/ic2_analysis/decompiled/ftbic/`

Narzędzie: vineflower.jar

### 2.2 Kluczowe klasy przeanalizowane

#### indreb
| Klasa | Odpowiedzialność |
|-------|-----------------|
| `IndRebBlockEntity` | Bazowa klasa BE: `energy` (int), `inventory`/`battery`/`upgrade` (ItemStackHandler) |
| `BlockEntityStandardMachine` | Maszyny: `active` (bool), `progress` (CompoundTag) |
| `BlockEntityGenerator` | Generatory: `active`, `progressBurn` (burn time!) |
| `BlockEntityTransformer` | Transformatory: `transformerMode` (int) |
| `BlockEntityBatteryBox` | Storage: dziedziczy po IndRebBlockEntity, ma `battery` |
| `BlockEntityCable` | Kable: **brak override save/load** — brak NBT! |
| `BlockEntityProgress` | Helper: serializuje do `{progress: float, progressMax: float}` |

#### ftbic
| Klasa | Odpowiedzialność |
|-------|-----------------|
| `ElectricBlockEntity` | Bazowa klasa: `Energy` (double), `Inventory` (ListTag), `Burnt` (bool) |
| `MachineBlockEntity` | Maszyny: `MaxProgress` (double), `Progress` (double), `Acceleration` (int) |

### 2.3 Różnice między symulacjami a rzeczywistością (PRZED poprawkami)

| Element | Stara symulacja | indreb rzeczywistość | ftbic rzeczywistość |
|---------|----------------|---------------------|---------------------|
| Energy | flat `energy` (int) lub `energyContainer` | flat `energy` (int) | `Energy` (double, capital E!) |
| Progress maszyny | `operatingTicks` (int) | `progress: {progress, progressMax}` (float) | `Progress` + `MaxProgress` (double) |
| Inventory | `Items` (ListTag) | `inventory: {Size, Items}` (CompoundTag) | `Inventory` (ListTag, byte Slot) |
| Active | w NBT lub blockstate | `active` w NBT | w blockstate (`ElectricBlock.ACTIVE`) |
| Generatory | `operatingTicks` | `progress: {progress, progressMax}` (burn time!) | `Progress` + `MaxProgress` |
| Storage | `energyContainer` | flat `energy` + `battery` | `Energy` + `Inventory` |
| Kable | jakieś NBT | **brak NBT** | — |
| Transformatory | brak NBT (identity) | `energy` + `transformerMode` | — |

### 2.4 Poprawki wprowadzone

Wszystkie symulacje zostały zaktualizowane żeby produkować NBT zgodne z dekompilacją:

1. **`machine_simulation.py`**:
   - Dodano branch `indreb:` → `active`, `energy`, `progress: {progress, progressMax}`, `inventory: {Size, Items}`
   - Dodano branch `ftbic:` → `Energy`, `Progress`, `MaxProgress`, `Inventory`
   - Dodano `extract_inventory_indreb()` z poprawnym mapowaniem slotów (unikalne Slot numbers)

2. **`energy_storage_simulation.py`**:
   - Dodano branch `indreb:` → flat `energy` (int)
   - Dodano branch `ftbic:` → `Energy` (double)
   - Usunięto hardcodowane `energyContainer` dla wszystkich targetów

3. **`cable_simulation.py`**:
   - Dla `indreb:` nie produkujemy żadnego NBT (kable indreb nie zapisują stanu)

4. **`converter_registry.py`**:
   - Dodano `TransformerConverter` produkujący `energy` + `transformerMode`

5. **`block_mappings.py`**:
   - Transformatory: `identity` → `transformer`

### 2.5 Testy snapshotowe NBT

Dodano testy weryfikujące dokładny kształt NBT:
- `TestIndrebNBTShape` (4 testy)
- `TestFTBICNBTShape` (2 testy)

Wszystkie 44 testy IC2 przechodzą.

---

## 3. Pokrycie mapowań (przypomnienie)

| Kategoria | Liczba | % |
|-----------|--------|---|
| Tier-1 real blocks (indreb/ftbic) | 70 | 61.9% |
| Placeholdery | 43 | 38.1% |
| **Razem** | **113** | **100%** |

### Placeholdery (43) - wymagają ręcznej decyzji
- Miner, Magnetizer, Electrolyzer, Terraformer
- Tesla Coil, Crop-Matron
- Thermal Centrifuge, Ore Washing Plant, Pattern Storage, Scanner, Replicator
- Fluid Regulator, Condenser
- Steam Generator, Solar Distiller, Fluid Distributor, Sorting Machine, Item Buffer, Crop Harvester, Lathe
- Water Mill, RT Generator, Stirling Generator, Kinetic Generator
- Electric/Fluid/RT/Solid Heat Generator
- Electric/Manual/Steam/Stirling/Water/Wind Kinetic Generator
- Reactor Chamber/Fluid Port/Access Hatch/Redstone Port/Vessel
- Personal Safe, Trade-O-Mat, Energy-O-Mat

---

## 4. Otwarte kwestie i rekomendacje

### Krytyczne
1. **IC2 jest na mapie** — znaleziono 781 TE IC2, więc konwerter wymaga testu na rzeczywistych danych.
2. **Format TE ID 1.7.10** — realne NBT używa nazw rejestracyjnych (`Macerator`, `Cable`, `TECrop`), nie tylko `TileEntity*`; router i skaner muszą uwzględniać oba formaty.
3. **Sloty inventory** — `extract_inventory_indreb` używa uproszczonego mapowania (`input`→0+, `output`→1+, itp.). W skomplikowanych maszynach z wieloma slotami input/output mapowanie może wymagać dopracowania.
4. **Generator progress** — w indreb `progress` w generatorze to **burn time** (czas spalania), nie crafting progress. Mapowanie `progress` IC2 (które w maszynach to crafting progress) na generator `progressBurn` może być mylące. W praktyce generator po postawieniu i tak zainicjalizuje nowy burn cycle.

### Do rozważenia
4. **ftbic Teleporter** — nasza symulacja zachowuje współrzędne w `legacy_target`, ale ftbic może używać innego systemu (sprawdzić `TeleporterBlockEntity`).
5. **ftbic Nuclear Reactor** — mapowany jako placeholder; `ftbic:nuclear_reactor` istnieje ale struktura reaktora może się różnić od IC2.
6. **Reactor components** — zachowane jako `legacy_ic2_*` — wymagają ręcznej przebudowy.

### Rekomendacja
- Konwerter IC2 jest **potrzebny** w pipeline konwersji mapy.
- Priorytetem jest test E2E na wybranych realnych chunkach z IC2 (`Macerator`, `Cable`, `TECrop`, `Reactor Chamber`).
- Dokumentacja Z1-Z4 powinna rozróżniać nazwy klas TE z kodu od nazw rejestracyjnych zapisanych w NBT mapy.

---

*Raport wygenerowany: 2026-05-19*
*Dekompilacja: vineflower.jar*
*Testy: 44/44 pass*
