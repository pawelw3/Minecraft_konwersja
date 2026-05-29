# Block-only analiza: Railcraft

Data: 2026-05-29

## Zakres i zrodla

Railcraft ma mieszanke TE, torow, multiblokow i zwyklych blokow dekoracyjnych. Warstwa block-only powinna objac bloki bez NBT: cube/decor, anvil fallback, lanterns, bricks, posts, walls, glass, ore, firestone recharge, frame, slabs/stairs i niektore proste maszyny z istniejacych mappingow oznaczone `has_block_entity=False`.

Zrodla lokalne:
- `src/converters/railcraft/mappings/block_mappings.py`
- `src/converters/railcraft/mappings/block_inventory.py`
- `mapa_1710/level.dat` FML `ItemData`
- `client_pack_1182/mod_manifest.json`

Railcraft nie jest widoczny w docelowym pliku manifestu, wiec targety ida do Create/vanilla/Thermal/Mekanism albo placeholdera.

## Tabela block-only

| numeric_id | registry_name | metadata | source variant | target block | confidence |
|---:|---|---|---|---|---|
| 1484 | `Railcraft:fluid.creosote` | 0 | creosote fluid | `thermal:creosote` or `minecraft:water` fallback | low |
| 1485 | `Railcraft:fluid.steam` | 0 | steam fluid | `minecraft:air` explicit technical removal | medium |
| 1486 | `Railcraft:cube` | 0 | decorative cube | `minecraft:stone` | medium |
| 1486 | `Railcraft:cube` | 2 | steel cube | `minecraft:iron_block` | medium |
| 1487 | `Railcraft:anvil` | 0 | Railcraft anvil | `minecraft:anvil` | high |
| 1490 | `Railcraft:track` | 0-15 | track family | outside block-only if handled by track converter/event | high |
| 1491 | `Railcraft:track.elevator` | 0 | elevator track | placeholder | low |
| 1492 | `Railcraft:signal` | 4 | switch lever | `minecraft:lever` | medium |
| 1495 | `Railcraft:lantern.stone` | 0 | stone lantern | `minecraft:lantern` | high |
| 1496 | `Railcraft:lantern.metal` | 0 | metal lantern | `minecraft:lantern` | high |
| 1497 | `Railcraft:brick.abyssal` | 0-15 | abyssal brick variants | vanilla stone/blackstone brick fallback | medium |
| 1498 | `Railcraft:brick.bleachedbone` | 0-15 | bleached bone brick variants | `minecraft:bone_block` or quartz fallback | medium |
| 1499 | `Railcraft:brick.bloodstained` | 0-15 | bloodstained brick variants | `minecraft:red_nether_bricks` | medium |
| 1500 | `Railcraft:brick.frostbound` | 0-15 | frostbound brick variants | `minecraft:packed_ice` / `minecraft:blue_ice` | medium |
| 1502 | `Railcraft:brick.quarried` | 0-15 | quarried brick variants | `minecraft:smooth_stone` / stone bricks | medium |
| 1503 | `Railcraft:brick.sandy` | 0-15 | sandy brick variants | `minecraft:sandstone` variants | medium |
| 1504 | `Railcraft:brick.nether` | 0-15 | nether brick variants | `minecraft:nether_bricks` variants | high |
| 1506 | `Railcraft:post.metal` | 0-15 | metal post | `minecraft:iron_bars` | medium |
| 1508 | `Railcraft:wall.alpha` | 0-15 | wall family alpha | matching vanilla wall fallback | medium |
| 1509 | `Railcraft:wall.beta` | 0-15 | wall family beta | matching vanilla wall fallback | medium |
| 1510 | `Railcraft:glass` | 0-15 | reinforced/glass variants | `minecraft:glass` or `thermal:obsidian_glass` | medium |
| 1511 | `Railcraft:detector` | 0-16 | detector blocks | `minecraft:observer` | medium |
| 1513 | `Railcraft:machine.epsilon` | 0-1 | electric feeder/admin feeder | `immersiveengineering:connector_lv` | medium |
| 1516 | `Railcraft:firestone.recharge` | 0 | firestone recharge | placeholder | low |
| 1517 | `Railcraft:frame` | 0 | track kit frame | placeholder | low |
| 1518 | `Railcraft:machine.delta` | 0 | shunting wire | `minecraft:redstone_wire` | medium |
| 1561 | `Railcraft:machine.alpha` | 5 | smoker | `minecraft:campfire` | medium |
| 1610 | `Railcraft:post.metal.platform` | 0-15 | metal platform/post | `minecraft:iron_bars` or iron trapdoor fallback | low |
| 2008 | `Railcraft:ore` | 0 | Railcraft ore | `minecraft:stone` per existing mapping | medium |
| 2201 | `Railcraft:stair` | 0-15 | decorative stairs | `framedblocks:framed_stairs` or vanilla stair fallback | low |
| 3149 | `Railcraft:machine.gamma` | 6-7,10-11 | energy/RF loader simple fallback | `mekanism:basic_universal_cable` | medium |
| 3199 | `Railcraft:post` | 0-15 | wood post | `minecraft:oak_fence` | medium |
| 3541 | `Railcraft:slab` | 0-15 | decorative slab | `framedblocks:framed_slab` or vanilla slab fallback | low |
| 3642 | `Railcraft:brick.infernal` | 0-15 | infernal brick variants | `minecraft:nether_bricks` / blackstone fallback | medium |
| 3995 | `Railcraft:residual.heat` | 0 | hidden residual heat | `minecraft:air` explicit ignored technical block | high |

## Fallbacki

- Decorative brick families: preserve broad material/color with vanilla blocks, because Railcraft target mod is absent.
- Posts/fences/platforms: prefer fence/bars/trapdoor shape over full solid blocks.
- Technical hidden blocks (`residual.heat`, steam): explicit `air` allowed with audit reason.
- Tracks/signals/machines with TE remain owned by existing Railcraft converter.

## Odrzucone / wymagajace review

- Most `machine.alpha/beta/gamma/epsilon`, `signal`, `track`, tanks and multiblocks require TE/event or functional converter.
- `framedblocks:*` target requires target-pack validation before use.
- Fluid blocks should be reviewed; direct fluid-state writing may differ from normal block-only blockstate writing.

## Handoff decyzji

- Krok 2 should reuse `STATIC_MAPPINGS` where `has_block_entity=False`, plus add decorative brick/wall/post tables.
- Do not turn unknown Railcraft blocks into air except `residual.heat` and other explicit technical removals.
