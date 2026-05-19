# AE2 - Krok 1 wykonany ponownie

Ten dokument zastępuje stary opis `AE2_BLOCKS_AND_TE.md` jako audyt kroku 1.
Powstał z lokalnych źródeł AE2 1.7.10 i 1.18.2, z JAR-ów używanych w projekcie oraz z aktualnej analizy `mapa_1710`.

## Werdykt

Poprzedni krok 1 był wykonany za słabo. Mieszał rejestrowe ID bloków 1.7.10 z faktycznym `id` TileEntity w NBT mapy, a liczniki użycia były nieaktualne.
Po kroku 3 tabela mapowań obsługuje już aliasy surowych NBT ID (`BlockDrive`, `BlockCableBus` itd.), więc ten raport pełni teraz rolę regresyjnego audytu pokrycia.

## Dane wejściowe

- `map_analysis`: `output/ae2_analysis/ae2_analysis_fixed.json`
- `map_csv`: `output/ae2_analysis/ae2_block_entities_all.csv`
- `source_1710`: `mod_src/1710/actual_src/1.7.10/AppliedEnergistics2/repo`
- `source_1182`: `mod_src/118/actual_src/1.18.2/AppliedEnergistics2/repo`
- `jar_1710`: `modpack_1710/appliedenergistics2-rv3-beta-6.jar`
- `jar_1182`: `headless_server/1.18.2/mods/appliedenergistics2-forge-11.7.6.jar`

## Skala na mapie

- Regiony z AE2-like TileEntity: 555
- Łącznie AE2-like TileEntity: 7925
- Pokryte przez obecną tabelę po pełnym prefiksie: 7916
- Niepokryte przez obecną tabelę: 9
- Pokryte logicznie, ale bez aliasu surowego NBT ID: 0

## TileEntity znalezione na mapie

| NBT id | Ilość | Mapowanie | Alias NBT | Cel 1.18.2 | Blok celu | BE celu | Konwerter | Konwerter OK | Uwagi |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| BlockCableBus | 3704 | tak | tak | ae2:cable_bus | tak | tak | cable_bus | tak |  |
| BlockCraftingUnit | 1162 | tak | tak | ae2:crafting_unit | tak | tak | crafting_unit | tak |  |
| BlockCraftingStorage | 833 | tak | tak | ae2:1k_crafting_storage | tak | nie | crafting_storage | tak |  |
| BlockSkyChest | 776 | tak | tak | ae2:sky_stone_chest | tak | tak | sky_chest | tak |  |
| BlockMolecularAssembler | 433 | tak | tak | ae2:molecular_assembler | tak | tak | molecular_assembler | tak |  |
| BlockController | 276 | tak | tak | ae2:controller | tak | tak | controller | tak |  |
| BlockDenseEnergyCell | 276 | tak | tak | ae2:dense_energy_cell | tak | tak | energy_cell | tak |  |
| BlockDrive | 192 | tak | tak | ae2:drive | tak | tak | drive | tak |  |
| BlockInterface | 123 | tak | tak | ae2:interface | tak | tak | interface | tak |  |
| BlockSpatialPylon | 39 | tak | tak | ae2:spatial_pylon | tak | tak | spatial_pylon | tak |  |
| BlockQuantumLinkChamber | 18 | tak | tak | ae2:quantum_link | tak | tak | quantum_link | tak |  |
| BlockEnergyCell | 17 | tak | tak | ae2:energy_cell | tak | tak | energy_cell | tak |  |
| BlockEnergyAcceptor | 16 | tak | tak | ae2:energy_acceptor | tak | tak | energy_acceptor | tak |  |
| BlockInscriber | 12 | tak | tak | ae2:inscriber | tak | tak | inscriber | tak |  |
| BlockQuartzGrowthAccelerator | 10 | tak | tak | ae2:quartz_growth_accelerator | tak | nie | growth_accelerator | tak |  |
| TileChestHungry | 9 | nie | nie | - | nie | nie | - | - | Nie-AE2 albo addon |
| BlockIOPort | 6 | tak | tak | ae2:io_port | tak | tak | io_port | tak |  |
| BlockSecurity | 6 | tak | tak | ae2:security_station | tak | nie | security_station | tak |  |
| BlockCrank | 4 | tak | tak | minecraft:lever | nie | nie | - | - |  |
| BlockGrinder | 4 | tak | tak | minecraft:grindstone | nie | nie | - | - |  |
| BlockCharger | 2 | tak | tak | ae2:charger | tak | tak | charger | tak |  |
| BlockCraftingMonitor | 2 | tak | tak | ae2:crafting_monitor | tak | tak | crafting_monitor | tak |  |
| BlockChest | 1 | tak | tak | ae2:chest | tak | tak | chest | tak |  |
| BlockCondenser | 1 | tak | tak | ae2:condenser | tak | tak | condenser | tak |  |
| BlockSpatialIOPort | 1 | tak | tak | ae2:spatial_io_port | tak | tak | spatial_io_port | tak |  |
| BlockVibrationChamber | 1 | tak | tak | ae2:vibration_chamber | tak | tak | vibration_chamber | tak |  |
| BlockWireless | 1 | tak | tak | ae2:wireless_access_point | tak | tak | wireless_ap | tak |  |

## Źródło 1.7.10 - bloki z TileEntity

| Blok | Tile class | Registry guess | NBT id guess | Plik |
| --- | --- | --- | --- | --- |
| BlockCraftingMonitor | TileCraftingMonitorTile | appliedenergistics2:tile.BlockCraftingMonitor | BlockCraftingMonitor | mod_src/1710/actual_src/1.7.10/AppliedEnergistics2/repo/src/main/java/appeng/block/crafting/BlockCraftingMonitor.java |
| BlockCraftingStorage | TileCraftingStorageTile | appliedenergistics2:tile.BlockCraftingStorage | BlockCraftingStorage | mod_src/1710/actual_src/1.7.10/AppliedEnergistics2/repo/src/main/java/appeng/block/crafting/BlockCraftingStorage.java |
| BlockCraftingUnit | TileCraftingTile | appliedenergistics2:tile.BlockCraftingUnit | BlockCraftingUnit | mod_src/1710/actual_src/1.7.10/AppliedEnergistics2/repo/src/main/java/appeng/block/crafting/BlockCraftingUnit.java |
| BlockMolecularAssembler | TileMolecularAssembler | appliedenergistics2:tile.BlockMolecularAssembler | BlockMolecularAssembler | mod_src/1710/actual_src/1.7.10/AppliedEnergistics2/repo/src/main/java/appeng/block/crafting/BlockMolecularAssembler.java |
| BlockCrank | TileCrank | appliedenergistics2:tile.BlockCrank | BlockCrank | mod_src/1710/actual_src/1.7.10/AppliedEnergistics2/repo/src/main/java/appeng/block/grindstone/BlockCrank.java |
| BlockGrinder | TileGrinder | appliedenergistics2:tile.BlockGrinder | BlockGrinder | mod_src/1710/actual_src/1.7.10/AppliedEnergistics2/repo/src/main/java/appeng/block/grindstone/BlockGrinder.java |
| BlockCellWorkbench | TileCellWorkbench | appliedenergistics2:tile.BlockCellWorkbench | BlockCellWorkbench | mod_src/1710/actual_src/1.7.10/AppliedEnergistics2/repo/src/main/java/appeng/block/misc/BlockCellWorkbench.java |
| BlockCharger | TileCharger | appliedenergistics2:tile.BlockCharger | BlockCharger | mod_src/1710/actual_src/1.7.10/AppliedEnergistics2/repo/src/main/java/appeng/block/misc/BlockCharger.java |
| BlockCondenser | TileCondenser | appliedenergistics2:tile.BlockCondenser | BlockCondenser | mod_src/1710/actual_src/1.7.10/AppliedEnergistics2/repo/src/main/java/appeng/block/misc/BlockCondenser.java |
| BlockInscriber | TileInscriber | appliedenergistics2:tile.BlockInscriber | BlockInscriber | mod_src/1710/actual_src/1.7.10/AppliedEnergistics2/repo/src/main/java/appeng/block/misc/BlockInscriber.java |
| BlockInterface | TileInterface | appliedenergistics2:tile.BlockInterface | BlockInterface | mod_src/1710/actual_src/1.7.10/AppliedEnergistics2/repo/src/main/java/appeng/block/misc/BlockInterface.java |
| BlockLightDetector | TileLightDetector | appliedenergistics2:tile.BlockLightDetector | BlockLightDetector | mod_src/1710/actual_src/1.7.10/AppliedEnergistics2/repo/src/main/java/appeng/block/misc/BlockLightDetector.java |
| BlockPaint | TilePaint | appliedenergistics2:tile.BlockPaint | BlockPaint | mod_src/1710/actual_src/1.7.10/AppliedEnergistics2/repo/src/main/java/appeng/block/misc/BlockPaint.java |
| BlockQuartzGrowthAccelerator | TileQuartzGrowthAccelerator | appliedenergistics2:tile.BlockQuartzGrowthAccelerator | BlockQuartzGrowthAccelerator | mod_src/1710/actual_src/1.7.10/AppliedEnergistics2/repo/src/main/java/appeng/block/misc/BlockQuartzGrowthAccelerator.java |
| BlockSecurity | TileSecurity | appliedenergistics2:tile.BlockSecurity | BlockSecurity | mod_src/1710/actual_src/1.7.10/AppliedEnergistics2/repo/src/main/java/appeng/block/misc/BlockSecurity.java |
| BlockSkyCompass | TileSkyCompass | appliedenergistics2:tile.BlockSkyCompass | BlockSkyCompass | mod_src/1710/actual_src/1.7.10/AppliedEnergistics2/repo/src/main/java/appeng/block/misc/BlockSkyCompass.java |
| BlockVibrationChamber | TileVibrationChamber | appliedenergistics2:tile.BlockVibrationChamber | BlockVibrationChamber | mod_src/1710/actual_src/1.7.10/AppliedEnergistics2/repo/src/main/java/appeng/block/misc/BlockVibrationChamber.java |
| BlockCableBus | TileCableBus | appliedenergistics2:tile.BlockCableBus | BlockCableBus | mod_src/1710/actual_src/1.7.10/AppliedEnergistics2/repo/src/main/java/appeng/block/networking/BlockCableBus.java |
| BlockController | TileController | appliedenergistics2:tile.BlockController | BlockController | mod_src/1710/actual_src/1.7.10/AppliedEnergistics2/repo/src/main/java/appeng/block/networking/BlockController.java |
| BlockCreativeEnergyCell | TileCreativeEnergyCell | appliedenergistics2:tile.BlockCreativeEnergyCell | BlockCreativeEnergyCell | mod_src/1710/actual_src/1.7.10/AppliedEnergistics2/repo/src/main/java/appeng/block/networking/BlockCreativeEnergyCell.java |
| BlockDenseEnergyCell | TileDenseEnergyCell | appliedenergistics2:tile.BlockDenseEnergyCell | BlockDenseEnergyCell | mod_src/1710/actual_src/1.7.10/AppliedEnergistics2/repo/src/main/java/appeng/block/networking/BlockDenseEnergyCell.java |
| BlockEnergyAcceptor | TileEnergyAcceptor | appliedenergistics2:tile.BlockEnergyAcceptor | BlockEnergyAcceptor | mod_src/1710/actual_src/1.7.10/AppliedEnergistics2/repo/src/main/java/appeng/block/networking/BlockEnergyAcceptor.java |
| BlockEnergyCell | TileEnergyCell | appliedenergistics2:tile.BlockEnergyCell | BlockEnergyCell | mod_src/1710/actual_src/1.7.10/AppliedEnergistics2/repo/src/main/java/appeng/block/networking/BlockEnergyCell.java |
| BlockWireless | TileWireless | appliedenergistics2:tile.BlockWireless | BlockWireless | mod_src/1710/actual_src/1.7.10/AppliedEnergistics2/repo/src/main/java/appeng/block/networking/BlockWireless.java |
| BlockQuantumBase | TileQuantumBridge | appliedenergistics2:tile.BlockQuantumBase | BlockQuantumBase | mod_src/1710/actual_src/1.7.10/AppliedEnergistics2/repo/src/main/java/appeng/block/qnb/BlockQuantumBase.java |
| BlockSpatialIOPort | TileSpatialIOPort | appliedenergistics2:tile.BlockSpatialIOPort | BlockSpatialIOPort | mod_src/1710/actual_src/1.7.10/AppliedEnergistics2/repo/src/main/java/appeng/block/spatial/BlockSpatialIOPort.java |
| BlockSpatialPylon | TileSpatialPylon | appliedenergistics2:tile.BlockSpatialPylon | BlockSpatialPylon | mod_src/1710/actual_src/1.7.10/AppliedEnergistics2/repo/src/main/java/appeng/block/spatial/BlockSpatialPylon.java |
| BlockChest | TileChest | appliedenergistics2:tile.BlockChest | BlockChest | mod_src/1710/actual_src/1.7.10/AppliedEnergistics2/repo/src/main/java/appeng/block/storage/BlockChest.java |
| BlockDrive | TileDrive | appliedenergistics2:tile.BlockDrive | BlockDrive | mod_src/1710/actual_src/1.7.10/AppliedEnergistics2/repo/src/main/java/appeng/block/storage/BlockDrive.java |
| BlockIOPort | TileIOPort | appliedenergistics2:tile.BlockIOPort | BlockIOPort | mod_src/1710/actual_src/1.7.10/AppliedEnergistics2/repo/src/main/java/appeng/block/storage/BlockIOPort.java |
| BlockSkyChest | TileSkyChest | appliedenergistics2:tile.BlockSkyChest | BlockSkyChest | mod_src/1710/actual_src/1.7.10/AppliedEnergistics2/repo/src/main/java/appeng/block/storage/BlockSkyChest.java |

## Cel 1.18.2 - BlockEntity z kodu AE2

| BE id | Stała | Klasa | Bloki |
| --- | --- | --- | --- |
| ae2:inscriber | INSCRIBER | InscriberBlockEntity | INSCRIBER |
| ae2:wireless_access_point | WIRELESS_ACCESS_POINT | WirelessAccessPointBlockEntity | WIRELESS_ACCESS_POINT |
| ae2:charger | CHARGER | ChargerBlockEntity | CHARGER |
| ae2:quantum_ring | QUANTUM_BRIDGE | QuantumBridgeBlockEntity | QUANTUM_LINK, QUANTUM_RING |
| ae2:spatial_pylon | SPATIAL_PYLON | SpatialPylonBlockEntity | SPATIAL_PYLON |
| ae2:spatial_io_port | SPATIAL_IO_PORT | SpatialIOPortBlockEntity | SPATIAL_IO_PORT |
| ae2:spatial_anchor | SPATIAL_ANCHOR | SpatialAnchorBlockEntity | SPATIAL_ANCHOR |
| ae2:cable_bus | CABLE_BUS | CableBusBlockEntity | CABLE_BUS |
| ae2:controller | CONTROLLER | ControllerBlockEntity | CONTROLLER |
| ae2:drive | DRIVE | DriveBlockEntity | DRIVE |
| ae2:chest | ME_CHEST | MEChestBlockEntity | ME_CHEST |
| ae2:interface | INTERFACE | InterfaceBlockEntity | INTERFACE |
| ae2:cell_workbench | CELL_WORKBENCH | CellWorkbenchBlockEntity | CELL_WORKBENCH |
| ae2:io_port | IO_PORT | IOPortBlockEntity | IO_PORT |
| ae2:condenser | CONDENSER | CondenserBlockEntity | CONDENSER |
| ae2:energy_acceptor | ENERGY_ACCEPTOR | EnergyAcceptorBlockEntity | ENERGY_ACCEPTOR |
| ae2:crystal_resonance_generator | CRYSTAL_RESONANCE_GENERATOR | CrystalResonanceGeneratorBlockEntity | CRYSTAL_RESONANCE_GENERATOR |
| ae2:vibration_chamber | VIBRATION_CHAMBER | VibrationChamberBlockEntity | VIBRATION_CHAMBER |
| ae2:growth_accelerator | GROWTH_ACCELERATOR | GrowthAcceleratorBlockEntity | GROWTH_ACCELERATOR |
| ae2:energy_cell | ENERGY_CELL | EnergyCellBlockEntity | ENERGY_CELL |
| ae2:dense_energy_cell | DENSE_ENERGY_CELL | EnergyCellBlockEntity | DENSE_ENERGY_CELL |
| ae2:creative_energy_cell | CREATIVE_ENERGY_CELL | CreativeEnergyCellBlockEntity | CREATIVE_ENERGY_CELL |
| ae2:crafting_unit | CRAFTING_UNIT | CraftingBlockEntity | CRAFTING_ACCELERATOR, CRAFTING_UNIT |
| ae2:crafting_storage | CRAFTING_STORAGE | CraftingBlockEntity | CRAFTING_STORAGE_16K, CRAFTING_STORAGE_1K, CRAFTING_STORAGE_256K, CRAFTING_STORAGE_4K, CRAFTING_STORAGE_64K |
| ae2:crafting_monitor | CRAFTING_MONITOR | CraftingMonitorBlockEntity | CRAFTING_MONITOR |
| ae2:pattern_provider | PATTERN_PROVIDER | PatternProviderBlockEntity | PATTERN_PROVIDER |
| ae2:molecular_assembler | MOLECULAR_ASSEMBLER | MolecularAssemblerBlockEntity | MOLECULAR_ASSEMBLER |
| ae2:light_detector | LIGHT_DETECTOR | LightDetectorBlockEntity | LIGHT_DETECTOR |
| ae2:paint | PAINT | PaintSplotchesBlockEntity | PAINT |
| ae2:sky_chest | SKY_CHEST | SkyChestBlockEntity | SKY_STONE_CHEST, SMOOTH_SKY_STONE_CHEST |
| ae2:sky_tank | SKY_STONE_TANK | SkyStoneTankBlockEntity | SKY_STONE_TANK |
| ae2:debug_item_gen | DEBUG_ITEM_GEN | ItemGenBlockEntity | DEBUG_ITEM_GEN |
| ae2:debug_phantom_node | DEBUG_PHANTOM_NODE | PhantomNodeBlockEntity | DEBUG_PHANTOM_NODE |
| ae2:debug_cube_gen | DEBUG_CUBE_GEN | CubeGeneratorBlockEntity | DEBUG_CUBE_GEN |
| ae2:debug_energy_gen | DEBUG_ENERGY_GEN | EnergyGeneratorBlockEntity | DEBUG_ENERGY_GEN |
| ae2:crank | CRANK | CrankBlockEntity | CRANK |
| ae2:mysterious_cube | MYSTERIOUS_CUBE | MysteriousCubeBlockEntity | MYSTERIOUS_CUBE |

## CableBus - rozpoznawane części

| Klasa części 1.7.10 | Typ pośredni |
| --- | --- |
| appeng.parts.automation.PartExportBus | export_bus |
| appeng.parts.automation.PartImportBus | import_bus |
| appeng.parts.automation.PartStorageBus | storage_bus |
| appeng.parts.misc.PartCableAnchor | cable_anchor |
| appeng.parts.misc.PartInvertedToggleBus | inverted_toggle_bus |
| appeng.parts.misc.PartToggleBus | toggle_bus |
| appeng.parts.networking.PartCable | cable |
| appeng.parts.networking.PartDenseCable | dense_cable |
| appeng.parts.networking.PartQuartzFiber | quartz_fiber |
| appeng.parts.p2p.PartP2PTunnel | p2p_tunnel |
| appeng.parts.p2p.PartP2PTunnelFE | p2p_tunnel_fe |
| appeng.parts.p2p.PartP2PTunnelFluid | p2p_tunnel_fluid |
| appeng.parts.p2p.PartP2PTunnelItem | p2p_tunnel_item |
| appeng.parts.p2p.PartP2PTunnelLight | p2p_tunnel_light |
| appeng.parts.p2p.PartP2PTunnelME | p2p_tunnel_me |
| appeng.parts.p2p.PartP2PTunnelRedstone | p2p_tunnel_redstone |
| appeng.parts.reporting.PartConversionMonitor | conversion_monitor |
| appeng.parts.reporting.PartDarkPanel | dark_monitor |
| appeng.parts.reporting.PartInterfaceTerminal | interface_terminal |
| appeng.parts.reporting.PartPanel | panel |
| appeng.parts.reporting.PartPatternTerminal | pattern_encoding_terminal |
| appeng.parts.reporting.PartPatternTerminalEx | pattern_encoding_terminal |
| appeng.parts.reporting.PartSemiDarkPanel | semi_dark_monitor |
| appeng.parts.reporting.PartStorageMonitor | storage_monitor |
| appeng.parts.reporting.PartTerminal | crafting_terminal |

## Luki wykryte w kroku 1

### Brak mapowania dla NBT z mapy

| NBT id | Ilość | Uwagi |
| --- | --- | --- |
| TileChestHungry | 9 | Nie-AE2 albo addon |

### Cel niepotwierdzony w assets 1.18.2

| NBT id | Cel | Ilość |
| --- | --- | --- |
| BlockCrank | minecraft:lever | 4 |
| BlockGrinder | minecraft:grindstone | 4 |

## Wniosek dla kolejnych kroków

Krok 1 jest teraz wystarczająco twardy jako inwentarz regresyjny. Po kroku 3 aliasy surowych `id` TileEntity są obsługiwane; otwarte pozostają tylko świadome fallbacki `BlockCrank`/`BlockGrinder` i nie-core `TileChestHungry`.
