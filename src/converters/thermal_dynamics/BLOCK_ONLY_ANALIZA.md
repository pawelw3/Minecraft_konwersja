# Block-only analiza: Thermal Dynamics

Data: 2026-05-29

## Zakres i zrodla

Thermal Dynamics is mostly ducts with tile/block entity state. The only safe block-only candidates are structural ducts and transport/viaduct-like ducts where existing mappings mark `has_block_entity=False`. Energy, fluid and item ducts should remain in the TE/NBT converter.

Zrodla lokalne:
- `src/converters/thermal_dynamics/mappings.py`
- `src/converters/thermal/mappings.py`
- `src/converters/thermal_dynamics/THERMAL_DYNAMICS_STEP5_FULLSCAN.md`
- `mapa_1710/level.dat` FML `ItemData`
- `client_pack_1182/mod_manifest.json`

Dynamiczne ID: `3304..3308` for `ThermalDynamics:ThermalDynamics_0`, `_16`, `_32`, `_48`, `_64`.

## Tabela block-only

| numeric_id | registry_name | metadata | source variant | target block | confidence |
|---:|---|---|---|---|---|
| 3304 | `ThermalDynamics:ThermalDynamics_0` | 0-15 | energy ducts | outside block-only, BE/duct network | high |
| 3305 | `ThermalDynamics:ThermalDynamics_16` | 0-15 | fluid ducts | outside block-only, BE/duct network | high |
| 3306 | `ThermalDynamics:ThermalDynamics_32` | 0-15 | item ducts | outside block-only, BE/duct network | high |
| 3307 | `ThermalDynamics:ThermalDynamics_48` | 0 | structural duct global meta 48 | `thermal:machine_frame` | medium |
| 3307 | `ThermalDynamics:ThermalDynamics_48` | 1 | structural duct global meta 49 | `thermal:machine_frame` | medium |
| 3308 | `ThermalDynamics:ThermalDynamics_64` | 0 | transport/viaduct | `minecraft:rail` | low |
| 3308 | `ThermalDynamics:ThermalDynamics_64` | 1 | long-range viaduct | `minecraft:rail` | low |
| 3308 | `ThermalDynamics:ThermalDynamics_64` | 2 | crossover viaduct | `minecraft:rail` | low |
| 3308 | `ThermalDynamics:ThermalDynamics_64` | 3 | extra transport/structural variant in local mapping | `mekanism:teleporter_frame` or `minecraft:rail` review | low |

## Fallbacki

- Structural ducts: `thermal:machine_frame` per existing Thermal mapping.
- Transport ducts: `minecraft:rail` is shape/function lossy but safe and installed.
- Unknown TD block-only candidate: placeholder, not air.

## Odrzucone / wymagajace review

- Energy/fluid/item ducts are networks and should not be flattened by block-only even if a target block exists.
- `ThermalDynamics_64` meta 3 has inconsistent existing notes; verify source before high-confidence mapping.

## Handoff decyzji

- Krok 2 should be conservative: only `_48` metas 0-1 and `_64` metas 0-2 by default.
- Do not duplicate Thermal TE duct conversion in block-only.
