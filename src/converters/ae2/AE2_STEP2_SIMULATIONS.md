# AE2 - Krok 2 wykonany ponownie

Ten dokument zastepuje stare podejscie do kroku 2 jako kontrakt symulacyjny oparty o reanalize kroku 1.
Symulacje nie probuja udawac calego AE2. Sprawdzaja najwazniejsze reguly, ktore musza byc prawdziwe przed kodem konwersji.

## Wynik

- Status: PASS
- Symulacje zaliczone: 6/6

## Symulacje

| Nazwa | Status | Ostrzezenia |
| --- | --- | --- |
| id_and_target_resolution | PASS | TileChestHungry is treated as non-core AE2/addon data.; BlockCrank uses a lossy fallback because AE2 11.7.6 JAR has no AE2 target block.; BlockGrinder uses a lossy fallback because AE2 11.7.6 JAR has no AE2 target block. |
| crafting_storage_and_unit_variants | PASS | - |
| interface_to_interface_plus_pattern_provider | PASS | - |
| cable_bus_part_mapping | PASS | Unknown part class unknown.ModPart in def:5 |
| sky_chest_inventory_preservation | PASS | - |
| me_network_channel_budget | PASS | - |

## Kontrakty dla kroku 3

1. Surowe NBT ID z mapy (`BlockDrive`, `BlockCableBus`, itd.) musza byc normalizowane do istniejacych kluczy mapowania.
2. `BlockCraftingStorage` musi mapowac metadata `0..3` na `ae2:1k_crafting_storage`, `ae2:4k_crafting_storage`, `ae2:16k_crafting_storage`, `ae2:64k_crafting_storage`; bit `4` jest stanem formed i nie zmienia rozmiaru.
3. `BlockCraftingUnit` metadata `1` musi przejsc na `ae2:crafting_accelerator`, a nie zwykly crafting unit.
4. Interface z patternami musi utworzyc osobny `ae2:pattern_provider` i przeniesc tam encoded patterns.
5. CableBus musi zachowac znane klasy partow i ostrzegac o nieznanych, zamiast cicho je gubic.
6. SkyChest musi zachowac inventory i miec jawnie zarejestrowana obsluge w konwerterze.

## Szczegoly

### id_and_target_resolution

Status: PASS

Checks:
- BlockCableBus -> appliedenergistics2:tile.BlockCableBus
- BlockCraftingUnit -> appliedenergistics2:tile.BlockCraftingUnit
- BlockCraftingStorage -> appliedenergistics2:tile.BlockCraftingStorage
- BlockSkyChest -> appliedenergistics2:tile.BlockSkyChest
- BlockMolecularAssembler -> appliedenergistics2:tile.BlockMolecularAssembler
- BlockController -> appliedenergistics2:tile.BlockController
- BlockDenseEnergyCell -> appliedenergistics2:tile.BlockDenseEnergyCell
- BlockDrive -> appliedenergistics2:tile.BlockDrive
- BlockInterface -> appliedenergistics2:tile.BlockInterface
- BlockSpatialPylon -> appliedenergistics2:tile.BlockSpatialPylon
- BlockQuantumLinkChamber -> appliedenergistics2:tile.BlockQuantumLinkChamber
- BlockEnergyCell -> appliedenergistics2:tile.BlockEnergyCell
- BlockEnergyAcceptor -> appliedenergistics2:tile.BlockEnergyAcceptor
- BlockInscriber -> appliedenergistics2:tile.BlockInscriber
- BlockQuartzGrowthAccelerator -> appliedenergistics2:tile.BlockQuartzGrowthAccelerator
- BlockIOPort -> appliedenergistics2:tile.BlockIOPort
- BlockSecurity -> appliedenergistics2:tile.BlockSecurity
- BlockCrank -> appliedenergistics2:tile.BlockCrank
- BlockGrinder -> appliedenergistics2:tile.BlockGrinder
- BlockCharger -> appliedenergistics2:tile.BlockCharger
- BlockCraftingMonitor -> appliedenergistics2:tile.BlockCraftingMonitor
- BlockChest -> appliedenergistics2:tile.BlockChest
- BlockCondenser -> appliedenergistics2:tile.BlockCondenser
- BlockSpatialIOPort -> appliedenergistics2:tile.BlockSpatialIOPort
- BlockVibrationChamber -> appliedenergistics2:tile.BlockVibrationChamber
- BlockWireless -> appliedenergistics2:tile.BlockWireless

Warnings:
- TileChestHungry is treated as non-core AE2/addon data.
- BlockCrank uses a lossy fallback because AE2 11.7.6 JAR has no AE2 target block.
- BlockGrinder uses a lossy fallback because AE2 11.7.6 JAR has no AE2 target block.

### crafting_storage_and_unit_variants

Status: PASS

Checks:
- storage meta 0: size=0, formed=False -> ae2:1k_crafting_storage
- storage meta 1: size=1, formed=False -> ae2:4k_crafting_storage
- storage meta 2: size=2, formed=False -> ae2:16k_crafting_storage
- storage meta 3: size=3, formed=False -> ae2:64k_crafting_storage
- storage meta 4: size=0, formed=True -> ae2:1k_crafting_storage
- storage meta 5: size=1, formed=True -> ae2:4k_crafting_storage
- storage meta 6: size=2, formed=True -> ae2:16k_crafting_storage
- storage meta 7: size=3, formed=True -> ae2:64k_crafting_storage
- unit meta 0: accelerator=False -> ae2:crafting_unit
- unit meta 1: accelerator=True -> ae2:crafting_accelerator
- unit meta 2: accelerator=False -> ae2:crafting_unit
- unit meta 3: accelerator=True -> ae2:crafting_accelerator

### interface_to_interface_plus_pattern_provider

Status: PASS

Checks:
- 1.7.10 interface keeps config/storage/pattern inventories separately.
- 1.18.2 conversion keeps storage/config in Interface.
- Encoded patterns move into adjacent Pattern Provider.

### cable_bus_part_mapping

Status: PASS

Checks:
- 0 -> dense_cable
- 1 -> crafting_terminal
- 2 -> import_bus
- 3 -> p2p_tunnel_me
- 4 -> storage_bus

Warnings:
- Unknown part class unknown.ModPart in def:5

### sky_chest_inventory_preservation

Status: PASS

Checks:
- BlockSkyChest -> ae2:sky_stone_chest
- preserved item stacks: 2

### me_network_channel_budget

Status: PASS

Checks:
- normal cable capacity: 8 channels
- dense cable/controller capacity: 32 channels
- devices reached: assembler, drive, interface, terminal
