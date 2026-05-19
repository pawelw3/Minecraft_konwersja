# AE2 - Krok 3 wykonany ponownie

## Zakres

Krok 3 obejmuje kod konwersji blokow i TileEntity AE2 z 1.7.10 do AE2 11.7.6 / Minecraft 1.18.2, zgodnie z kontraktami z kroku 2.

## Zmiany w implementacji

- Dodano normalizacje surowych NBT ID z mapy:
  - `BlockDrive` -> `appliedenergistics2:tile.BlockDrive`
  - `BlockCableBus` -> `appliedenergistics2:tile.BlockCableBus`
  - analogicznie dla pozostalych core AE2 TileEntity.
- Poprawiono targety AE2 11.7.6:
  - `BlockCraftingStorage` -> `ae2:1k_crafting_storage` / `ae2:4k_crafting_storage` / `ae2:16k_crafting_storage` / `ae2:64k_crafting_storage`
  - `BlockQuartzGrowthAccelerator` -> `ae2:quartz_growth_accelerator`
  - `BlockCrank` -> `minecraft:lever` jako lossy fallback
  - `BlockGrinder` -> `minecraft:grindstone` jako lossy fallback
- Poprawiono warianty metadata:
  - `BlockCraftingStorage`: `metadata & 3` wybiera rozmiar, bit `4` oznacza `formed`
  - `BlockCraftingUnit`: `metadata & 1` wybiera `ae2:crafting_accelerator`
- Zarejestrowano obsluge `sky_chest`.
- Dopisano ostrzezenia `AE2C-W-LOSSY-FALLBACK` dla lossy fallbackow.
- Poprawiono sygnatury konwerterow craftingu, ktore musza przyjmowac `metadata`.
- Zaktualizowano `verify_coverage.py`, zeby liczyl canonical mappings bez podwajania aliasow.

## Pokrycie

- Bloki zrodlowe 1.7.10: 30
- Bloki zmapowane: 30
- Pokrycie mapowan: 100%
- Konwertery NBT: 26
- Surowe aliasy NBT z mapy: obslugiwane

## Swiadome fallbacki

- `BlockCrank`: AE2 11.7.6 na headless serverze nie ma odpowiednika AE2, wiec target to `minecraft:lever`.
- `BlockGrinder`: AE2 11.7.6 na headless serverze nie ma odpowiednika AE2, wiec target to `minecraft:grindstone`.
- `TileChestHungry`: nie jest core AE2, zostaje poza tym etapem.

## Weryfikacja

- `python -B -m unittest src.converters.ae2.tests.test_ae2_converter` - OK, 24 testy.
- `python -B src\converters\ae2\simulations\step2_contract_simulations.py` - OK, 6/6 PASS.
- `$env:PYTHONIOENCODING='utf-8'; python -B src\converters\ae2\verify_coverage.py` - OK, 100% coverage.
- `python -B src\converters\ae2\analyze_step1_inventory.py` - OK, alias missing count 0.
