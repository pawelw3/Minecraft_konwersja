# Block-only analiza: Traincraft

Data: 2026-05-29

## Zakres i zrodla

Traincraft places most important blocks as TE: rails, rail gags, benches, distillery, open furnace, lanterns and bridge pillars were seen in full scan as TileEntities. The safe block-only scope is small: ore, stopper/simple decorative blocks only when no TE exists, and fluids as explicit review.

Zrodla lokalne:
- `src/converters/traincraft/mappings/block_mappings.py`
- `output/traincraft_task4/coverage_traincraft.json`
- `mapa_1710/level.dat` FML `ItemData`
- `client_pack_1182/mod_manifest.json`

Target pack contains Create but no Steam'n'Rails entry was found by manifest search; railways targets must be validated before use.

## Tabela block-only

| numeric_id | registry_name | metadata | source variant | target block | confidence |
|---:|---|---|---|---|---|
| 544 | `tc:assemblyTableI` | 0 | assembly table tier I | outside block-only, TE | high |
| 545 | `tc:assemblyTableII` | 0 | assembly table tier II | outside block-only, TE | high |
| 546 | `tc:assemblyTableIII` | 0 | assembly table tier III | outside block-only, TE | high |
| 547/548 | `tc:distilIdle/Active` | 0 | distillery | outside block-only, TE | high |
| 549 | `tc:trainWorkbench` | 0 | train workbench | outside block-only, TE | high |
| 550 | `tc:stopper` | 0 | stopper | `minecraft:oak_fence` | medium |
| 551/552 | `tc:openFurnaceIdle/Active` | 0 | open hearth furnace | outside block-only, TE | high |
| 553 | `tc:oreTC` | 0-15 | Traincraft ores | `minecraft:iron_ore` fallback per existing mapping | low |
| 554 | `tc:lantern` | 0 | lantern | outside block-only if TE exists; `minecraft:lantern` only for no-TE orphan | low |
| 555 | `tc:waterWheel` | 0 | decorative water wheel | `minecraft:air` explicit removal or placeholder | low |
| 556 | `tc:windMill` | 0 | decorative wind mill | `minecraft:air` explicit removal or placeholder | low |
| 557 | `tc:generatorDiesel` | 0 | diesel generator | outside block-only, functional/TE | high |
| 558 | `tc:tcRailGag` | 0-15 | rail gag | outside block-only, TE/track converter | high |
| 559 | `tc:tcRail` | 0-15 | rail | outside block-only, TE/track converter | high |
| 560 | `tc:bridgePillar` | 0 | bridge pillar | outside block-only if TE exists; `minecraft:oak_log` for no-TE orphan | low |
| 572 | `tc:fluid.diesel` | 0 | diesel fluid | placeholder or explicit air review | low |
| 573 | `tc:fluid.refinedfuel` | 0 | refined fuel fluid | placeholder or explicit air review | low |

## Fallbacki

- `tc:oreTC`: existing mapping uses `minecraft:iron_ore`; confidence low because metadata ore variants are not yet decoded.
- `tc:stopper`: `minecraft:oak_fence` preserves barrier role.
- `waterWheel`/`windMill`: choose placeholder if visual preservation matters; explicit air only if accepted as removed decoration.
- Fluids need special review and should be audited if emitted.

## Odrzucone / wymagajace review

- `tcRail`, `tcRailGag`, `lantern`, `bridgePillar` appear as TE in full scan and should not be generally block-only.
- All benches/machines/generator are TE/functionality.
- Steam'n'Rails/`railways:*` targets must be validated before use.

## Handoff decyzji

- Krok 2 should be minimal: `stopper`, `oreTC`, optional orphan fallback for lantern/bridgePillar only if no TE exists.
- Treat Traincraft rails as existing track converter scope, not this layer.
