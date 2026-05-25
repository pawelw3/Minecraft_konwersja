# Thermal Expansion - Inwentarz bloków i TE

## Wersja 1.7.10

### Bloki (jeden blok per kategoria + metadata)
| Kategoria | Blok ID | Metadata | TE ID | Nazwa |
|-----------|---------|----------|-------|-------|
| Machine | `ThermalExpansion:Machine` | 0 | `thermalexpansion.Furnace` | Redstone Furnace |
| Machine | `ThermalExpansion:Machine` | 1 | `thermalexpansion.Pulverizer` | Pulverizer |
| Machine | `ThermalExpansion:Machine` | 2 | `thermalexpansion.Sawmill` | Sawmill |
| Machine | `ThermalExpansion:Machine` | 3 | `thermalexpansion.Smelter` | Induction Smelter |
| Machine | `ThermalExpansion:Machine` | 4 | `thermalexpansion.Crucible` | Magma Crucible |
| Machine | `ThermalExpansion:Machine` | 5 | `thermalexpansion.Transposer` | Fluid Transposer |
| Machine | `ThermalExpansion:Machine` | 6 | `thermalexpansion.Precipitator` | Glacial Precipitator |
| Machine | `ThermalExpansion:Machine` | 7 | `thermalexpansion.Extruder` | Igneous Extruder |
| Machine | `ThermalExpansion:Machine` | 8 | `thermalexpansion.Accumulator` | Aqueous Accumulator |
| Machine | `ThermalExpansion:Machine` | 9 | `thermalexpansion.Assembler` | Cyclic Assembler |
| Machine | `ThermalExpansion:Machine` | 10 | `thermalexpansion.Charger` | Energetic Infuser |
| Machine | `ThermalExpansion:Machine` | 11 | `thermalexpansion.Insolator` | Phytogenic Insolator |
| Dynamo | `ThermalExpansion:Dynamo` | 0 | `thermalexpansion.DynamoSteam` | Steam Dynamo |
| Dynamo | `ThermalExpansion:Dynamo` | 1 | `thermalexpansion.DynamoMagmatic` | Magmatic Dynamo |
| Dynamo | `ThermalExpansion:Dynamo` | 2 | `thermalexpansion.DynamoCompression` | Compression Dynamo |
| Dynamo | `ThermalExpansion:Dynamo` | 3 | `thermalexpansion.DynamoReactant` | Reactant Dynamo |
| Dynamo | `ThermalExpansion:Dynamo` | 4 | `thermalexpansion.DynamoEnervation` | Enervation Dynamo |
| Device | `ThermalExpansion:Device` | 0 | `thermalexpansion.Activator` | Autonomous Activator |
| Device | `ThermalExpansion:Device` | 1 | `thermalexpansion.Breaker` | Terrain Smasher |
| Device | `ThermalExpansion:Device` | 2 | `thermalexpansion.Collector` | Item Collector |
| Device | `ThermalExpansion:Device` | 3 | `thermalexpansion.Nullifier` | Nullifier |
| Device | `ThermalExpansion:Device` | 4 | `thermalexpansion.Buffer` | Item Allocator |
| Cell | `ThermalExpansion:Cell` | 0-4 | `thermalexpansion.Cell` | Energy Cell (tiers) |
| Cache | `ThermalExpansion:Cache` | 0-4 | `thermalexpansion.Cache` | Cache (tiers) |
| Tank | `ThermalExpansion:Tank` | 0-4 | `thermalexpansion.Tank` | Portable Tank (tiers) |
| Strongbox | `ThermalExpansion:Strongbox` | 0-4 | `thermalexpansion.Strongbox` | Strongbox (tiers) |

## Wersja 1.18.2

### Bloki
| Blok ID | BE ID | Nazwa |
|---------|-------|-------|
| `thermal:machine_furnace` | `thermal:machine_furnace` | Redstone Furnace |
| `thermal:machine_pulverizer` | `thermal:machine_pulverizer` | Pulverizer |
| `thermal:machine_sawmill` | `thermal:machine_sawmill` | Sawmill |
| `thermal:machine_smelter` | `thermal:machine_smelter` | Induction Smelter |
| `thermal:machine_crucible` | `thermal:machine_crucible` | Magma Crucible |
| `thermal:machine_insolator` | `thermal:machine_insolator` | Phytogenic Insolator |
| `thermal:machine_centrifuge` | `thermal:machine_centrifuge` | Centrifugal Separator |
| `thermal:machine_press` | `thermal:machine_press` | Multiservo Press |
| `thermal:machine_chiller` | `thermal:machine_chiller` | Fluid Encapsulator |
| `thermal:machine_refinery` | `thermal:machine_refinery` | Fractionating Still |
| `thermal:machine_pyrolyzer` | `thermal:machine_pyrolyzer` | Pyrolyzer |
| `thermal:machine_bottler` | `thermal:machine_bottler` | Bottling Machine |
| `thermal:machine_brewer` | `thermal:machine_brewer` | Alchemical Imbuer |
| `thermal:machine_crystallizer` | `thermal:machine_crystallizer` | Crystallizer |
| `thermal:machine_crafter` | `thermal:machine_crafter` | Sequential Fabricator |
| `thermal:dynamo_stirling` | `thermal:dynamo_stirling` | Stirling Dynamo |
| `thermal:dynamo_compression` | `thermal:dynamo_compression` | Compression Dynamo |
| `thermal:dynamo_magmatic` | `thermal:dynamo_magmatic` | Magmatic Dynamo |
| `thermal:dynamo_numismatic` | `thermal:dynamo_numismatic` | Numismatic Dynamo |
| `thermal:dynamo_lapidary` | `thermal:dynamo_lapidary` | Lapidary Dynamo |
| `thermal:dynamo_disenchantment` | `thermal:dynamo_disenchantment` | Disenchantment Dynamo |
| `thermal:dynamo_gourmand` | `thermal:dynamo_gourmand` | Gourmand Dynamo |

## Porównanie / Mapowanie

| 1.7.10 | 1.18.2 | Uwagi |
|--------|--------|-------|
| Furnace | machine_furnace | Bezpośrednie |
| Pulverizer | machine_pulverizer | Bezpośrednie |
| Sawmill | machine_sawmill | Bezpośrednie |
| Smelter | machine_smelter | Bezpośrednie |
| Crucible | machine_crucible | Bezpośrednie |
| Insolator | machine_insolator | Bezpośrednie |
| Steam Dynamo | dynamo_stirling | Zmiana nazwy |
| Compression Dynamo | dynamo_compression | Bezpośrednie |
| Magmatic Dynamo | dynamo_magmatic | Bezpośrednie |
| Reactant Dynamo | dynamo_numismatic | Lossy: inne paliwo |
| Enervation Dynamo | dynamo_disenchantment | Lossy: inne paliwo |
| Transposer | machine_bottler | Lossy: inna mechanika |
| Precipitator | machine_chiller | Lossy: inna mechanika |
| Extruder | machine_press | Lossy: inna mechanika |
| Accumulator | ??? | Brak odpowiednika |
| Assembler | machine_crafter | Lossy: inna mechanika |
| Charger | ??? | Brak odpowiednika |
| Activator | ??? | Brak odpowiednika |
| Breaker | ??? | Brak odpowiednika |
| Collector | ??? | Brak odpowiednika |
| Nullifier | ??? | Brak odpowiednika (ale vanilla ma /dev/null) |
| Buffer | ??? | Brak odpowiednika |
| Cell/Cache/Tank/Strongbox | thermal:energy_cell etc. | Wymaga dalszej analizy |
