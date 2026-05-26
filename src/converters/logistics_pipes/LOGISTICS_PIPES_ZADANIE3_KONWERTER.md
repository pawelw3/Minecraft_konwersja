# Logistics Pipes - Zadanie 3: kod konwersji

## Zakres

Dodano pierwszy konwerter Logistics Pipes 1.7.10 -> Pretty Pipes / AE2 / Pipez dla 1.18.2. Konwerter nie probuje odtwarzac calej sieci LP, tylko produkuje eventy zgodne z routerem projektu i zachowuje dane diagnostyczne w NBT/warnings.

## Obslugiwane Tile Entities

| TE 1.7.10 | Cel 1.18.2 | Uwagi |
| --- | --- | --- |
| `logisticspipes.pipes.basic.LogisticsTileGenericPipe` | `prettypipes:pipe`, `prettypipes:item_terminal` albo `pipez:fluid_pipe` | Zalezne od rozpoznanej klasy pipe. |
| `logisticspipes.blocks.crafting.LogisticsCraftingTableTileEntity` | `ae2:pattern_provider` | Shell z zachowanym `conversion_source`; pattern do weryfikacji. |
| `logisticspipes.blocks.powertile.LogisticsPowerJuntionTileEntity` | `prettypipes:pressurizer` | Stare LP power zachowane jako diagnostyka, nie jako lossless FE. |
| `logisticspipes.blocks.powertile.LogisticsRFPowerProviderTileEntity` | `prettypipes:pressurizer` | Wymaga sprawdzenia sasiedztwa sieci. |
| `logisticspipes.blocks.powertile.LogisticsIC2PowerProviderTileEntity` | `prettypipes:pressurizer` | Dodatkowy warning IC2/EU. |
| `LogisticsSoldering/Security/Statistics` | `conversion_placeholders:block_entity_placeholder` | Brak 1:1; oryginalne NBT zostaje zachowane. |

## Kontrakty zaimplementowane z Zadania 2

1. Provider pipe -> `prettypipes:pipe` z `prettypipes:high_extraction_module`.
2. Supplier pipe -> `prettypipes:pipe` z `prettypipes:high_retrieval_module` i warningiem stock target.
3. Crafting pipe -> `prettypipes:pipe` z `prettypipes:high_crafting_module` i warningiem pattern verification.
4. Request pipe/table -> `prettypipes:item_terminal`.
5. Fluid pipes -> `pipez:fluid_pipe`, bo Pretty Pipes core jest item-only.
6. Chassis Mk1..Mk5 -> `prettypipes:pipe`, z limitem 3 modulow i jawnym `LP-W-CHASSIS-OVERFLOW`.
7. Power provider -> `prettypipes:pressurizer` shell z ostrzezeniem `LP-W-POWER-NOT-LOSSLESS`.

## Ograniczenia

- Realne mapy moga miec tylko numeryczne `pipeId`. W takim przypadku konwerter emituje zwykly `prettypipes:pipe` oraz `LP-W-DYNAMIC-PIPE-ID`; dokladne rozpoznanie wymaga pozniejszego lookupu dynamicznych item ID z mapy/modpacka.
- Pretty Pipes `modules` NBT jest minimalnym shellem kompatybilnym z planem konwersji; weryfikacja w grze nalezy do kolejnych zadan.
- Zlozone crafting NBT, fuzzy crafting, fluid crafting, cleanup inventory i supplier pattern target-slot nie sa automatycznie rekonstrukowane.

## Weryfikacja

- `python -m pytest src\converters\logistics_pipes\tests -q` -> 12 passed
- `python src\converters\logistics_pipes\simulations\step2_contract_simulations.py` -> PASS 5/5

