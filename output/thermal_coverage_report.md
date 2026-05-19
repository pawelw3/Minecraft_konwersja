# Raport pokrycia konwertera Thermal Series (Zadanie 4)

## Podsumowanie
- Bloki: 346,817 / 346,817 (100.0%)
- Tile Entities: 3,004 / 3,004 (100.0%)

## Bloki (Block IDs)
| Block ID | Nazwa | Liczba | Obsługiwany | Uwagi |
|----------|-------|--------|-------------|-------|
| 962 | ThermalFoundation:Ore | 342,369 | ✅ |  |
| 3306 | ThermalDynamics:ThermalDynamics_32 | 1,582 | ✅ | sub-block with offset 32 |
| 3304 | ThermalDynamics:ThermalDynamics_0 | 1,107 | ✅ | sub-block with offset 0 |
| 963 | ThermalFoundation:Storage | 672 | ✅ |  |
| 964 | ThermalFoundation:FluidRedstone | 460 | ✅ | fluid block - mapped via FLUID_MAPPINGS |
| 3305 | ThermalDynamics:ThermalDynamics_16 | 189 | ✅ | sub-block with offset 16 |
| 968 | ThermalFoundation:FluidCryotheum | 174 | ✅ | fluid block - mapped via FLUID_MAPPINGS |
| 3456 | ThermalExpansion:FakeAirBarrier | 132 | ✅ | ignored (technical block) |
| 3446 | ThermalExpansion:Tesseract | 54 | ✅ |  |
| 3438 | ThermalExpansion:Machine | 49 | ✅ | multi-meta machine block |
| 3441 | ThermalExpansion:Cell | 12 | ✅ |  |
| 3452 | ThermalExpansion:Sponge | 11 | ✅ | hardcoded sponge mapping |
| 3450 | ThermalExpansion:Glass | 6 | ✅ | hardcoded glass mapping |

## Tile Entities
| TE ID | Liczba | Obsługiwany | Docelowy blok |
|-------|--------|-------------|---------------|
| thermaldynamics.ItemDuct | 1,582 | ✅ | thermal:item_buffer |
| thermaldynamics.FluxDuctSuperConductor | 1,106 | ✅ | thermal:energy_duct |
| thermaldynamics.FluidDuct | 136 | ✅ | thermal:fluid_duct |
| thermalexpansion.Tesseract | 54 | ✅ | mekanism:quantum_entangloporter |
| thermaldynamics.FluidDuctSuper | 53 | ✅ | thermal:fluid_duct_windowed |
| thermalexpansion.Cell | 12 | ✅ | thermal:energy_cell |
| thermalexpansion.Sponge | 11 | ✅ | minecraft:sponge |
| thermalexpansion.Accumulator | 10 | ✅ | thermal:device_water_gen |
| thermalexpansion.Transposer | 10 | ✅ | thermal:machine_bottler |
| thermalexpansion.Pulverizer | 8 | ✅ | thermal:machine_pulverizer |
| thermalexpansion.Crucible | 7 | ✅ | thermal:machine_crucible |
| thermalexpansion.Smelter | 5 | ✅ | thermal:machine_smelter |
| thermalexpansion.Sawmill | 3 | ✅ | thermal:machine_sawmill |
| thermalexpansion.Extruder | 2 | ✅ | thermal:machine_extruder |
| thermalexpansion.Furnace | 2 | ✅ | thermal:machine_furnace |
| thermalexpansion.Precipitator | 1 | ✅ | thermal:machine_chiller |
| thermaldynamics.FluxDuct | 1 | ✅ | thermal:energy_duct |
| thermalexpansion.Assembler | 1 | ✅ | thermal:machine_crafter |

## Luki w mapowaniach

## Kluczowe problemy
1. **ThermalDynamics sub-bloki**: Mapa używa `ThermalDynamics:ThermalDynamics_0/16/32/48/64` zamiast
   `ThermalDynamics:FluxDuct/FluidDuct/ItemDuct`. Konwerter musi dodawać offset do metadata.
2. **Opaque variants**: Wiele ductów ma wersje 'opaque' (np. fluidHardenedOpaque) które nie mają
   bezpośrednich mapowań w 1.18.2 (1.18.2 Thermal Dynamics nie rozróżnia opaque/non-opaque).
3. **Empty/Crafting ducts**: energyReinforcedEmpty, energyResonantEmpty, energySuperCondEmpty,
   transportFrame - to bloki craftingowe/techniczne które powinny być zignorowane lub zmapowane na structure.