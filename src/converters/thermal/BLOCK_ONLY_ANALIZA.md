# Block-only analiza: Thermal

Data: 2026-05-29

## Zakres i zrodla

Thermal block-only includes Thermal Foundation ores/storage/fluid blocks and Thermal Expansion simple blocks (frames, glass, rockwool, sponge, lights, fake air). Machines, dynamos, cells, tanks, strongboxes, caches, workbenches and tesseracts remain TE/NBT.

Zrodla lokalne:
- `src/converters/thermal/mappings.py`
- `src/converters/thermal/THERMAL_STEP4_COVERAGE.md`
- `mapa_1710/level.dat` FML `ItemData`
- `client_pack_1182/mod_manifest.json`

Docelowa paczka zawiera Thermal Foundation/Expansion/Dynamics 1.18.2.

## Tabela block-only

| numeric_id | registry_name | metadata | source variant | target block | confidence |
|---:|---|---|---|---|---|
| 962 | `ThermalFoundation:Ore` | 0 | copper ore | `thermal:copper_ore` | high |
| 962 | `ThermalFoundation:Ore` | 1 | tin ore | `thermal:tin_ore` | high |
| 962 | `ThermalFoundation:Ore` | 2 | silver ore | `thermal:silver_ore` | high |
| 962 | `ThermalFoundation:Ore` | 3 | lead ore | `thermal:lead_ore` | high |
| 962 | `ThermalFoundation:Ore` | 4 | nickel ore | `thermal:nickel_ore` | high |
| 962 | `ThermalFoundation:Ore` | 5 | platinum ore | `thermal:cinnabar_ore` per existing mapping | medium |
| 962 | `ThermalFoundation:Ore` | 6 | mithril ore | `thermal:sapphire_ore` per existing mapping | medium |
| 963 | `ThermalFoundation:Storage` | 0 | copper block | `thermal:copper_block` | high |
| 963 | `ThermalFoundation:Storage` | 1 | tin block | `thermal:tin_block` | high |
| 963 | `ThermalFoundation:Storage` | 2 | silver block | `thermal:silver_block` | high |
| 963 | `ThermalFoundation:Storage` | 3 | lead block | `thermal:lead_block` | high |
| 963 | `ThermalFoundation:Storage` | 4 | nickel block | `thermal:nickel_block` | high |
| 963 | `ThermalFoundation:Storage` | 5 | platinum block | `thermal:electrum_block` per existing mapping | medium |
| 963 | `ThermalFoundation:Storage` | 6 | mithril block | `thermal:invar_block` per existing mapping | medium |
| 963 | `ThermalFoundation:Storage` | 7 | electrum block | `thermal:electrum_block` | high |
| 963 | `ThermalFoundation:Storage` | 8 | invar block | `thermal:invar_block` | high |
| 963 | `ThermalFoundation:Storage` | 9 | bronze block | `thermal:bronze_block` | high |
| 963 | `ThermalFoundation:Storage` | 10 | signalum block | `thermal:signalum_block` | high |
| 963 | `ThermalFoundation:Storage` | 11 | lumium block | `thermal:lumium_block` | high |
| 963 | `ThermalFoundation:Storage` | 12 | enderium block | `thermal:enderium_block` | high |
| 964 | `ThermalFoundation:FluidRedstone` | 0 | destabilized redstone fluid | `thermal:redstone` fluid/block | low |
| 965 | `ThermalFoundation:FluidGlowstone` | 0 | energized glowstone fluid | `thermal:glowstone` fluid/block | low |
| 968 | `ThermalFoundation:FluidCryotheum` | 0 | cryotheum fluid | `thermal:cryotheum` if present else placeholder | low |
| 971 | `ThermalFoundation:FluidMana` | 0 | mana fluid | `thermal:mana` if present else placeholder | low |
| 972 | `ThermalFoundation:FluidSteam` | 0 | steam fluid | `thermal:steam` or explicit air technical fallback | low |
| 973 | `ThermalFoundation:FluidCoal` | 0 | coal/creosote fluid | `thermal:creosote` | medium |
| 1293 | `ThermalFoundation:FluidEnder` | 0 | resonant ender fluid | `thermal:ender` | low |
| 1414 | `ThermalFoundation:FluidPetrotheum` | 0 | petrotheum fluid | `thermal:petrotheum` if present else placeholder | low |
| 1942 | `ThermalFoundation:FluidPyrotheum` | 0 | pyrotheum fluid | `thermal:pyrotheum` if present else placeholder | low |
| 2015 | `ThermalFoundation:FluidAerotheum` | 0 | aerotheum fluid | `thermal:aerotheum` if present else placeholder | low |
| 3447 | `ThermalExpansion:Plate` | 0 | plate frame | `thermal:machine_frame` | medium |
| 3447 | `ThermalExpansion:Plate` | 2 | excursion plate | `minecraft:piston` | low |
| 3447 | `ThermalExpansion:Plate` | 3 | impulse plate | `minecraft:slime_block` | low |
| 3447 | `ThermalExpansion:Plate` | 4 | signal plate | `minecraft:observer` | low |
| 3447 | `ThermalExpansion:Plate` | 6 | translocation plate | `minecraft:sticky_piston` | low |
| 3448 | `ThermalExpansion:Light` | 0 | glowstone illuminator | `minecraft:glowstone` | medium |
| 3448 | `ThermalExpansion:Light` | 1 | false light technical | `minecraft:air` explicit technical removal | high |
| 3449 | `ThermalExpansion:Frame` | 0 | machine frame | `thermal:machine_frame` | high |
| 3450 | `ThermalExpansion:Glass` | 0 | hardened glass | `thermal:obsidian_glass` | high |
| 3451 | `ThermalExpansion:Rockwool` | 0-15 | colored rockwool | `thermal:<color>_rockwool` | high |
| 3452 | `ThermalExpansion:Sponge` | 0 | sponge | `minecraft:sponge` | high |
| 3452 | `ThermalExpansion:Sponge` | 1 | magmatic sponge | `minecraft:wet_sponge` per existing mapping | medium |
| 3452 | `ThermalExpansion:Sponge` | 2 | creative sponge | `minecraft:sponge` | medium |
| 3453 | `ThermalExpansion:FakeAirSignal` | 0 | technical fake air | `minecraft:air` explicit technical removal | high |
| 3454 | `ThermalExpansion:FakeAirLight` | 0 | technical fake air | `minecraft:air` explicit technical removal | high |
| 3455 | `ThermalExpansion:FakeAirForce` | 0 | technical fake air | `minecraft:air` explicit technical removal | high |
| 3456 | `ThermalExpansion:FakeAirBarrier` | 0 | technical fake air | `minecraft:air` explicit technical removal | high |

## Fallbacki

- Reuse `THERMAL_ORE_BY_META`, `THERMAL_STORAGE_BY_META`, `THERMAL_ROCKWOOL_BY_META` from `mappings.py`.
- Fluids are low-confidence because direct chunk blockstate writing for fluids may need a special fluid/state path.
- Fake air and LightFalse may be explicitly converted to air with audit reason.

## Odrzucone / wymagajace review

- `Machine`, `Device`, `Dynamo`, `Cell`, `Tank`, `Strongbox`, `Cache`, `Workbench`, `Tesseract` are TE-owned.
- `Plate` meta 1 and 5 map to functional BE targets and are outside block-only.
- Platinum/mithril redistribution is intentionally lossy and should be visible in audit.

## Handoff decyzji

- Krok 2 should call existing `get_mapping()` and accept only mappings where `has_block_entity=False`.
- Rockwool and Foundation ore/storage are the safest/highest-value first set.
