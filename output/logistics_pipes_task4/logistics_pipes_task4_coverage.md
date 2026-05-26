# Logistics Pipes - Zadanie 4: pokrycie stref mapy

Zakres: `strefy/*/coords.json`, mapa `mapa_1710`, tryb tylko-do-odczytu.

## Podsumowanie

- Regiony sprawdzone: 17
- Chunki sprawdzone: 7676
- Tile Entities Logistics Pipes: 215
- Eventy konwersji: 215
- Eventy placeholder: 0
- Puste wyniki routera: 0

## TE i cele

| Typ | Liczba |
| --- | ---: |
| `logisticspipes.pipes.basic.LogisticsTileGenericPipe` | 200 |
| `logisticspipes.blocks.crafting.LogisticsCraftingTableTileEntity` | 9 |
| `logisticspipes.blocks.powertile.LogisticsPowerJuntionTileEntity` | 6 |

## Targety

| Target | Liczba |
| --- | ---: |
| `prettypipes:pipe` | 189 |
| `prettypipes:item_terminal` | 11 |
| `ae2:pattern_provider` | 9 |
| `prettypipes:pressurizer` | 6 |

## Rozpoznanie klas rur

| Klasa pipe | Liczba |
| --- | ---: |
| `PipeItemsBasicTransport` | 91 |
| `PipeItemsBasicLogistics` | 38 |
| `PipeItemsSupplierLogistics` | 28 |
| `PipeItemsProviderLogisticsMk2` | 22 |
| `[non-pipe-te]` | 15 |
| `PipeLogisticsChassiMk4` | 10 |
| `PipeItemsRemoteOrdererLogistics` | 5 |
| `PipeItemsRequestLogistics` | 5 |
| `PipeBlockRequestTable` | 1 |

## Numeryczne pipeId

| pipeId | Liczba |
| --- | ---: |
| `8780` | 91 |
| `8749` | 38 |
| `8754` | 28 |
| `8763` | 22 |
| `8758` | 10 |
| `8762` | 5 |
| `8750` | 5 |
| `8779` | 1 |

## Warningi

| Kod | Liczba |
| --- | ---: |
| `LP-W-SUPPLIER-STOCK-TARGET` | 28 |
| `LP-W-CHASSIS-MODULES-UNKNOWN` | 10 |
| `LP-W-CRAFTING-TABLE` | 9 |
| `LP-W-POWER-NOT-LOSSLESS` | 6 |
| `LP-W-PRESSURIZER-RECOMMENDED` | 6 |
| `LP-W-REMOTE-ORDERER` | 5 |
| `LP-W-REQUEST-TERMINAL` | 5 |
| `LP-W-REQUEST-TABLE` | 1 |

## Per strefa

| Strefa | TE | Converted | Placeholder | Warningi |
| --- | ---: | ---: | ---: | ---: |
| billund | 2 | 2 | 0 | 2 |
| choroszcz | 0 | 0 | 0 | 0 |
| iii_rzesza | 0 | 0 | 0 | 0 |
| rzym | 25 | 25 | 0 | 30 |
| zsrr | 188 | 188 | 0 | 38 |

## Wniosek dla kolejnego kroku

- Wszystkie rury w strefach zostaly rozpoznane po klasie pipe lub dynamicznym `pipeId`.
- Eventy warningowe trzeba zachowac w testach mapy 5A/5B, bo opisuja utrate semantyki LP.