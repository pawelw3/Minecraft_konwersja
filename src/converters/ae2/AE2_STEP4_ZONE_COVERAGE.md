# AE2 - Krok 4: pokrycie stref glownej mapy

Zakres: `strefy/*/coords.json`, `mapa_1710`, bez edycji mapy. Raport uzywa aktualnych wynikow kroku 1-3 oraz pelnego agregatu `output/ae2_analysis/ae2_block_entities_all.csv`.

## Podsumowanie

- Strefy sprawdzone: 5
- Globalnie znalezione AE2-like Tile Entities: 7925
- Globalnie zmapowane core AE2: 7916
- Globalnie poza core/unmapped: 9 (`TileChestHungry`)
- W zdefiniowanych strefach: 2473
- Poza zdefiniowanymi strefami: 5452
- Symulacje kroku 2: pass (6/6)
- Suchy przebieg konwertera dla core AE2: OK

## Pokrycie po strefach

| Strefa | AE2-like TE | Pelne AE2 | Lossy fallback | Poza core/unmapped | Akceptowane |
| --- | --- | --- | --- | --- | --- |
| billund | 0 | 0 | 0 | 0 | 0.0% |
| choroszcz | 0 | 0 | 0 | 0 | 0.0% |
| iii_rzesza | 1121 | 1121 | 0 | 0 | 100.0% |
| rzym | 86 | 84 | 0 | 2 | 97.7% |
| zsrr | 1266 | 1266 | 0 | 0 | 100.0% |

## Typy AE2 w strefach

| NBT id | Liczba | Target | Kategoria |
| --- | --- | --- | --- |
| BlockCableBus | 1543 | ae2:cable_bus | full_ae2 |
| BlockMolecularAssembler | 252 | ae2:molecular_assembler | full_ae2 |
| BlockDenseEnergyCell | 190 | ae2:dense_energy_cell | full_ae2 |
| BlockDrive | 143 | ae2:drive | full_ae2 |
| BlockController | 79 | ae2:controller | full_ae2 |
| BlockCraftingUnit | 74 | ae2:crafting_unit | full_ae2 |
| BlockInterface | 72 | ae2:interface | full_ae2 |
| BlockSpatialPylon | 39 | ae2:spatial_pylon | full_ae2 |
| BlockCraftingStorage | 33 | ae2:1k_crafting_storage | full_ae2 |
| BlockEnergyCell | 16 | ae2:energy_cell | full_ae2 |
| BlockEnergyAcceptor | 10 | ae2:energy_acceptor | full_ae2 |
| BlockInscriber | 5 | ae2:inscriber | full_ae2 |
| BlockQuartzGrowthAccelerator | 5 | ae2:quartz_growth_accelerator | full_ae2 |
| BlockSecurity | 3 | ae2:security_station | full_ae2 |
| BlockIOPort | 2 | ae2:io_port | full_ae2 |
| BlockCraftingMonitor | 2 | ae2:crafting_monitor | full_ae2 |
| TileChestHungry | 2 | unmapped | non_core_or_unmapped |
| BlockChest | 1 | ae2:chest | full_ae2 |
| BlockCharger | 1 | ae2:charger | full_ae2 |
| BlockSpatialIOPort | 1 | ae2:spatial_io_port | full_ae2 |

## Uwagi

- `full_ae2` oznacza mapowanie na blok `ae2:*` z aktualnym konwerterem NBT.
- `lossy_fallback` oznacza jawna decyzje projektu: `BlockCrank -> minecraft:lever`, `BlockGrinder -> minecraft:grindstone`; nie jest to potwierdzona migracja 1:1.
- `TileChestHungry` pozostaje poza core AE2 i nie blokuje pokrycia AE2 11.7.6.
- Step 4 nie zapisuje do `mapa_1710`; operuje na wygenerowanym CSV z pozycjami i definicjach stref.

## Najwieksze regiony AE2 globalnie

| Region | AE2-like TE |
| --- | --- |
| r.5.1.mca | 3431 |
| r.1.6.mca | 1121 |
| r.-5.-5.mca | 1059 |
| r.-3.-2.mca | 719 |
| r.-5.-4.mca | 207 |
| r.4.1.mca | 189 |
| r.-3.-8.mca | 168 |
| r.-8.7.mca | 85 |
| r.0.0.mca | 85 |
| r.-5.8.mca | 38 |
| r.-4.-6.mca | 24 |
| r.9.1.mca | 15 |
| r.11.1.mca | 6 |
| r.8.6.mca | 6 |
| r.-10.-5.mca | 5 |
| r.-10.0.mca | 5 |
| r.-5.7.mca | 5 |
| r.1.0.mca | 5 |
| r.14.5.mca | 5 |
| r.6.7.mca | 5 |
