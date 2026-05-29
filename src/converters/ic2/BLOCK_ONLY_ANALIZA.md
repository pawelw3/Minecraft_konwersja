# Block-only analiza: IC2

Data: 2026-05-29

## Zakres i zrodla

IC2 ma duzo blokow z TileEntity, ale ma tez istotne bloki bez TE: rudy, rubber wood/leaves/sapling/resin, rubber sheet, fences, scaffold, metal blocks, cables i niektore konstrukcyjne bloki. Kable w targetowym IndReb maja BlockEntity wg raportu dekompilacji, ale zapis NBT jest pusty, wiec moga byc traktowane jako blockstate-only tylko jesli target akceptuje sam blok.

Zrodla lokalne:
- `mod_src/1710/code_from_jar/1.7.10/IC2/decompiled/`
- `output/ic2_analysis/decompiled/indreb_full/`
- `output/ic2_analysis/decompiled/ftbic/`
- `src/converters/ic2/mappings/`
- `output/ic2_analysis/ic2_zadanie4_report.md`
- `mapa_1710/level.dat` FML `ItemData`

Dynamiczne ID z `level.dat`: bloki IC2 `466..521`; IC2 Nuclear Control `3463..3466`.
Raport mapy znalazl 781 TE IC2; block-only ma objac tylko bloki bez NBT.

## Tabela block-only

| numeric_id | registry_name | metadata | source variant | target block | confidence |
|---:|---|---|---|---|---|
| 466 | `IC2:blockOreCopper` | 0 | copper ore | `minecraft:copper_ore` | high |
| 467 | `IC2:blockOreTin` | 0 | tin ore | `indreb:tin_ore` albo `ftbic:tin_ore` | medium |
| 468 | `IC2:blockOreUran` | 0 | uranium ore | `indreb:uranium_ore` albo `ftbic:uranium_ore` | medium |
| 469 | `IC2:blockOreLead` | 0 | lead ore | `thermal:lead_ore` albo `ftbic:lead_ore` | medium |
| 470 | `IC2:blockRubWood` | 0-15 | rubber wood orientation/resin side | `indreb:rubber_log` albo `minecraft:jungle_log` fallback | low |
| 471 | `IC2:blockRubLeaves` | 0-15 | rubber leaves decay/check bits | `indreb:rubber_leaves` albo `minecraft:jungle_leaves` fallback | low |
| 472 | `IC2:blockRubSapling` | 0-15 | rubber sapling growth stage | `indreb:rubber_sapling` albo `minecraft:jungle_sapling` fallback | low |
| 473 | `IC2:blockHarz` | 0-15 | resin spot on rubber tree | `minecraft:air` only if explicitly approved; otherwise placeholder | low |
| 474 | `IC2:blockRubber` | 0 | rubber sheet/block | `indreb:rubber_sheet` or `minecraft:black_wool` fallback | low |
| 475 | `IC2:blockFenceIron` | 0 | iron fence | `minecraft:iron_bars` | medium |
| 476 | `IC2:blockAlloy` | 0 | reinforced stone/alloy construction | `indreb:reinforced_stone` or `minecraft:stone_bricks` fallback | medium |
| 477 | `IC2:blockBasalt` | 0-15 | basalt variants | `minecraft:basalt` / `minecraft:smooth_basalt` | medium |
| 478 | `IC2:blockAlloyGlass` | 0 | reinforced glass | `indreb:reinforced_glass` or `minecraft:glass` fallback | medium |
| 480 | `IC2:blockReinforcedFoam` | 0-15 | hardened construction foam | `minecraft:stone` / `minecraft:white_concrete` fallback | low |
| 481 | `IC2:blockFoam` | 0-15 | wet construction foam | `minecraft:white_concrete_powder` fallback | low |
| 482 | `IC2:blockWall` | 0-15 | construction foam wall/color variants | `minecraft:white_concrete` fallback | low |
| 483 | `IC2:blockScaffold` | 0-15 | wooden scaffold | `minecraft:scaffolding` | medium |
| 484 | `IC2:blockIronScaffold` | 0-15 | iron scaffold | `minecraft:iron_bars` / `minecraft:scaffolding` fallback | low |
| 485 | `IC2:blockMetal` | 0-15 | copper/tin/bronze/uranium/lead/refined iron blocks | matching target metal blocks | medium |
| 486 | `IC2:blockCable` | 0-15 | cable insulation/type | `indreb:*_cable` family | medium |
| 500 | `IC2:blockLuminatorDark` | 0-15 | off luminator | `minecraft:sea_lantern` fallback | low |
| 501 | `IC2:blockLuminator` | 0-15 | on luminator | `minecraft:sea_lantern` fallback | low |
| 502 | `IC2:blockMiningPipe` | 0 | mining pipe | `minecraft:iron_bars` fallback | low |
| 503 | `IC2:blockMiningTip` | 0 | mining pipe tip | `minecraft:iron_block` fallback | low |
| 505 | `IC2:blockITNT` | 0 | industrial TNT | `minecraft:tnt` | medium |
| 506 | `IC2:blockNuke` | 0 | nuke | `minecraft:tnt` with warning | low |
| 507 | `IC2:blockDynamite` | 0-15 | dynamite | `minecraft:tnt` fallback | low |
| 508 | `IC2:blockDynamiteRemote` | 0-15 | remote dynamite | `minecraft:tnt` fallback | low |
| 509 | `IC2:blockCrop` | 0-15 | IC2 crop stick/crop, TE-like crop state | outside block-only unless no TE; placeholder | low |

## Fallbacki

- Ores: prefer vanilla or installed tech target; no `air`.
- Rubber tree parts: prefer IndReb if present; fallback to jungle tree parts with warning.
- Construction foam and colored walls: fallback to concrete/concrete powder, confidence `low`.
- Explosives: fallback to `minecraft:tnt`, warning about altered blast behavior.

## Odrzucone / wymagajace review

- `blockKineticGenerator`, `blockHeatGenerator`, `blockGenerator`, reactor blocks, machines, chargepads, barrels, personal blocks and fluids are not block-only.
- `blockCable` target registry names must be verified in IndReb resources before implementation.
- `blockHarz` may legitimately disappear visually, but `minecraft:air` must be an explicit decision with audit because it is a placed mod block.

## Handoff decyzji

- Krok 2 zaczac od ores and construction/simple blocks (`466..478`, `483..486`, `505..508`).
- Maszyny i reactor components zostaja w obecnym IC2 TE converterze.
