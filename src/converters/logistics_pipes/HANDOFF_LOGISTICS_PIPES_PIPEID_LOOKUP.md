# Handoff: Logistics Pipes, pipeId lookup przed Zadaniem 5A

## Podsumowanie sesji
Dodano lookup dynamicznych `pipeId` Logistics Pipes z `mapa_1710/level.dat` FML `ItemData`. Konwerter przestal traktowac 200 rur ze stref jako nieznane i po przeliczeniu Zadania 4 wszystkie rury maja rozpoznana klase pipe.

## Ukonczono
- [x] Odczytano dynamiczne ID itemow z `mapa_1710/level.dat`.
- [x] Dodano `PIPE_ID_TO_PIPE_CLASS` dla Logistics Pipes ID `8749..8780`.
- [x] Rozszerzono konwerter, aby uzywal `pipeId -> pipe class`, gdy NBT nie zawiera klasy.
- [x] Dodano mappingi dla dodatkowych pipe role: remote orderer, satellite, invsys, system entrance/destination, firewall, apiarist.
- [x] Dodano testy regresyjne dla realnych `pipeId` z mapy.
- [x] Przeliczono raport Zadania 4.

## Wynik po przeliczeniu Zadania 4
- TE Logistics Pipes w strefach: 215
- Eventy konwersji: 215
- Placeholdery: 0
- `LP-W-DYNAMIC-PIPE-ID`: 0
- Warningi lacznie: 70

## Rozpoznane rury
| pipeId | Klasa | Liczba |
| --- | --- | ---: |
| `8780` | `PipeItemsBasicTransport` | 91 |
| `8749` | `PipeItemsBasicLogistics` | 38 |
| `8754` | `PipeItemsSupplierLogistics` | 28 |
| `8763` | `PipeItemsProviderLogisticsMk2` | 22 |
| `8758` | `PipeLogisticsChassiMk4` | 10 |
| `8762` | `PipeItemsRemoteOrdererLogistics` | 5 |
| `8750` | `PipeItemsRequestLogistics` | 5 |
| `8779` | `PipeBlockRequestTable` | 1 |

## Nowe/zmienione pliki
- `src/converters/logistics_pipes/mappings.py`
- `src/converters/logistics_pipes/logistics_pipes_converter.py`
- `src/converters/logistics_pipes/analyze_map_coverage.py`
- `src/converters/logistics_pipes/tests/test_logistics_pipes_converter.py`
- `output/logistics_pipes_task4/logistics_pipes_task4_coverage.json`
- `output/logistics_pipes_task4/logistics_pipes_task4_coverage.md`
- `src/converters/logistics_pipes/HANDOFF_LOGISTICS_PIPES_PIPEID_LOOKUP.md`
- `HANDOFF.md`

## Weryfikacja
- `python -m pytest src\converters\logistics_pipes\tests -q` -> 16 passed
- `python src\converters\logistics_pipes\analyze_map_coverage.py` -> 215 TE, 0 placeholderow, 0 bledow
- `python src\converters\logistics_pipes\simulations\step2_contract_simulations.py` -> PASS 5/5

## Nastepne kroki
1. [ ] Zadanie 5A: zbudowac testowa mape 1.7.10 lub fixture mapy z reprezentatywnymi LP TE/rurami.
2. [ ] Uwzglednic w testowej mapie co najmniej: basic transport, basic logistics, supplier, provider mk2, chassis mk4, request, request table, crafting table, power junction.
3. [ ] Osobno zweryfikowac 10 sztuk `PipeLogisticsChassiMk4`, bo maja warning `LP-W-CHASSIS-MODULES-UNKNOWN`.

