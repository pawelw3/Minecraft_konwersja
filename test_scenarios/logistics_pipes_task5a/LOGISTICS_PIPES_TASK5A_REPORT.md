# Logistics Pipes Task 5A Report

## Podsumowanie
Utworzono lekki fixture NBT dla Logistics Pipes zamiast materializowanej mapy MCA. Walidacja przeszla 13/13 probek.

## Zakres fixture
- Realne `pipeId` z `mapa_1710/level.dat`: `8749`, `8750`, `8754`, `8758`, `8762`, `8763`, `8779`, `8780`.
- Solid TileEntities: crafting table, fuzzy crafting table, power junction, security station placeholder.
- Scenariusz nie modyfikuje `mapa_1710/`.

## Targety
- `ae2:pattern_provider`: 2
- `conversion_placeholders:block_entity_placeholder`: 1
- `prettypipes:item_terminal`: 3
- `prettypipes:pipe`: 6
- `prettypipes:pressurizer`: 1

## Wyniki probek
| Status | Probka | Target | Warningi |
| --- | --- | --- | --- |
| `ok` | `basic_transport_pipeid_8780` | `prettypipes:pipe` | - |
| `ok` | `basic_logistics_pipeid_8749` | `prettypipes:pipe` | - |
| `ok` | `supplier_pipeid_8754` | `prettypipes:pipe` | `LP-W-SUPPLIER-STOCK-TARGET` |
| `ok` | `provider_mk2_pipeid_8763` | `prettypipes:pipe` | - |
| `ok` | `chassis_mk4_with_modules` | `prettypipes:pipe` | `LP-W-CHASSIS-OVERFLOW` |
| `ok` | `chassis_mk4_unknown_modules` | `prettypipes:pipe` | `LP-W-CHASSIS-MODULES-UNKNOWN` |
| `ok` | `request_pipeid_8750` | `prettypipes:item_terminal` | `LP-W-REQUEST-TERMINAL` |
| `ok` | `request_table_pipeid_8779` | `prettypipes:item_terminal` | `LP-W-REQUEST-TABLE` |
| `ok` | `remote_orderer_pipeid_8762` | `prettypipes:item_terminal` | `LP-W-REMOTE-ORDERER` |
| `ok` | `crafting_table_basic` | `ae2:pattern_provider` | `LP-W-CRAFTING-TABLE` |
| `ok` | `crafting_table_fuzzy` | `ae2:pattern_provider` | `LP-W-CRAFTING-TABLE`, `LP-W-FUZZY-CRAFTING` |
| `ok` | `power_junction` | `prettypipes:pressurizer` | `LP-W-POWER-NOT-LOSSLESS`, `LP-W-PRESSURIZER-RECOMMENDED` |
| `ok` | `security_station_placeholder` | `conversion_placeholders:block_entity_placeholder` | `LP-W-SECURITY-NO-TARGET` |

## Pliki
- `test_scenarios\logistics_pipes_task5a\logistics_pipes_task5a_source_fixture_1710.json`
- `test_scenarios\logistics_pipes_task5a\logistics_pipes_task5a_converted_patch_1182.json`
- `test_scenarios\logistics_pipes_task5a\logistics_pipes_task5a_events_1182.json`
- `test_scenarios\logistics_pipes_task5a\logistics_pipes_task5a_validation.json`

## Nastepny krok
1. [ ] Zadanie 5B: zmaterializowac ten fixture na swiecie 1.18.2/headless albo przygotowac writer MCA, gdy dostepne bedzie narzedzie sekcji.
