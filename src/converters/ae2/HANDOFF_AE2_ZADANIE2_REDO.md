# Handoff: AE2 - Zadanie 2 wykonane ponownie

## Podsumowanie sesji

Wykonano od nowa krok 2 dla AE2 jako zestaw malych, deterministycznych symulacji kontraktowych. Nowe symulacje bazuja na reanalizie kroku 1 i lokalnych zrodlach/JAR-ach, a ich celem jest przygotowanie konkretnych wymagan dla kroku 3, czyli kodu konwersji.

## Ukonczono

- [x] Sprawdzono stary krok 2 i uznano, ze byl zbyt ogolny wobec nowych luk z kroku 1.
- [x] Dodano `step2_contract_simulations.py`.
- [x] Wygenerowano raport `AE2_STEP2_SIMULATIONS.md`.
- [x] Wygenerowano wynik maszynowy `AE2_STEP2_SIMULATION_RESULTS.json`.
- [x] Uruchomiono nowe symulacje: 6/6 PASS.
- [x] Uruchomiono dotychczasowe testy AE2: 18/18 OK.

## Nowe pliki

- `src/converters/ae2/simulations/step2_contract_simulations.py`
- `src/converters/ae2/AE2_STEP2_SIMULATIONS.md`
- `src/converters/ae2/AE2_STEP2_SIMULATION_RESULTS.json`

## Zmodyfikowane pliki

- `HANDOFF.md`

## Wyniki symulacji

- `id_and_target_resolution` - PASS.
- `crafting_storage_and_unit_variants` - PASS.
- `interface_to_interface_plus_pattern_provider` - PASS.
- `cable_bus_part_mapping` - PASS.
- `sky_chest_inventory_preservation` - PASS.
- `me_network_channel_budget` - PASS.

## Kontrakty dla kroku 3

1. Surowe NBT ID z mapy (`BlockDrive`, `BlockCableBus`, itd.) musza byc normalizowane do kluczy mapowania.
2. `BlockCraftingStorage` metadata `0..3` musi isc na `ae2:1k_crafting_storage`, `ae2:4k_crafting_storage`, `ae2:16k_crafting_storage`, `ae2:64k_crafting_storage`; bit `4` oznacza formed i nie zmienia rozmiaru.
3. `BlockCraftingUnit` metadata `1` musi isc na `ae2:crafting_accelerator`.
4. Interface z patternami musi tworzyc osobny `ae2:pattern_provider`.
5. CableBus musi zachowywac znane party i ostrzegac o nieznanych.
6. SkyChest musi zachowywac inventory i miec jawnie zarejestrowana obsluge.
7. `BlockGrinder` i `BlockCrank` sa lossy: AE2 11.7.6 JAR nie ma ich blokow docelowych, wiec symulacja przyjmuje fallback `minecraft:grindstone` i `minecraft:lever`.
8. `TileChestHungry` zostaje poza core AE2, prawdopodobnie Thaumcraft/addon.

## Weryfikacja

- `python -B src\converters\ae2\simulations\step2_contract_simulations.py` - OK, 6/6 PASS.
- `python -B -m unittest src.converters.ae2.tests.test_ae2_converter` - OK, 18 testow.

## Nastepne kroki

1. [ ] W kroku 3 poprawic mapowania i resolver zgodnie z kontraktami kroku 2.
2. [ ] Dodac testy konwertera dla surowych NBT ID, wariantow storage i Interface -> Pattern Provider.
3. [ ] Zdecydowac, czy fallbacki `BlockCrank`/`BlockGrinder` zostaja docelowo jako vanilla, czy maja byc oznaczane jako wymagajace recznej kontroli.
