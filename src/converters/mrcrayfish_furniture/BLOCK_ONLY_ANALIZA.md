# Block-only analiza: MrCrayfish Furniture

Data: 2026-05-29

## Zakres i zrodla

MrCrayfish Furniture 1.7.10 zapisuje wiele mebli jako zwykle bloki w `Sections`; czesc z nich ma TE tylko gdy trzyma inventory albo stan urzadzenia. Paczka 1.18.2 nie zawiera CFM/Refurbished Furniture, wiec targety `cfm:*` z lokalnej symulacji sa decyzjami projektowymi do zatwierdzenia albo musza zostac zastapione vanilla/placeholderem w kroku 2.

Zrodla lokalne:
- `src/converters/mrcrayfish_furniture/simulation_block_mappings.py`
- `output/mrcrayfish_task4/mrcrayfish_coverage.md`
- `mapa_1710/level.dat` FML `ItemData`
- `client_pack_1182/mod_manifest.json`

Dynamiczne ID z mapy: bloki CFM `2728..2792`, dodatkowo `2919` stone path, `3201` blender, `3558` computer.

## Tabela block-only

| numeric_id | registry_name | metadata | source variant | target block | confidence |
|---:|---|---|---|---|---|
| 2730 | `cfm:coffetablewood` | 0 | oak coffee table | `cfm:oak_coffee_table` or placeholder | medium |
| 2731 | `cfm:coffetablestone` | 0 | stone coffee table | `cfm:stone_coffee_table` or `minecraft:smooth_stone_slab` | medium |
| 2732 | `cfm:tablewood` | 0 | oak table | `cfm:oak_table` or placeholder | medium |
| 2733 | `cfm:tablestone` | 0 | stone table | `cfm:stone_table` or placeholder | medium |
| 2734 | `cfm:chairwood` | 0 | oak chair | `cfm:oak_chair` or placeholder | medium |
| 2735 | `cfm:chairstone` | 0 | stone chair | `cfm:stone_chair` or placeholder | medium |
| 2738 | `cfm:cabinet` | 0 | wooden cabinet, no inventory TE in block-only path | `cfm:oak_cabinet` or placeholder | medium |
| 2739 | `cfm:couch` | 0-15 | colored couch | `cfm:<color>_sofa` or matching wool fallback | medium |
| 2740/2741 | `cfm:blindon/off` | 0 | blinds state | `cfm:oak_blinds` or placeholder | low |
| 2742/2743 | `cfm:curtainon/off` | 0 | curtains state | `cfm:oak_curtains` or matching wool pane fallback | low |
| 2744 | `cfm:bedsidecabinet` | 0 | bedside cabinet | `cfm:oak_bedside_cabinet` or placeholder | medium |
| 2747 | `cfm:hedge` | 0-3 | hedge wood variant | `minecraft:oak_leaves` / spruce / birch / jungle | medium |
| 2748 | `cfm:birdbath` | 0 | bird bath | `minecraft:cauldron` or placeholder | low |
| 2750 | `cfm:whitefence` | 0 | white picket fence | `cfm:white_picket_fence` or `minecraft:white_wool` fence-shape loss | low |
| 2751 | `cfm:tap` | 0 | tap | placeholder | low |
| 2752 | `cfm:mailbox` | 0 | mailbox | `cfm:oak_mail_box` or placeholder | medium |
| 2756 | `cfm:electricfence` | 0 | electric fence | `minecraft:iron_bars` | medium |
| 2757 | `cfm:doorbell` | 0 | doorbell | `minecraft:stone_button` | medium |
| 2758/2759 | `cfm:firealarmoff/on` | 0 | fire alarm | `minecraft:redstone_lamp` or placeholder | low |
| 2760/2761 | `cfm:ceilinglightoff/on` | 0 | ceiling light | `minecraft:lantern` / `minecraft:glowstone` | medium |
| 2763 | `cfm:toilet` | 0 | toilet | placeholder | low |
| 2764 | `cfm:basin` | 0 | basin | placeholder | low |
| 2765 | `cfm:wallcabinet` | 0 | wall cabinet | `cfm:oak_cabinet` or placeholder | low |
| 2766/2767 | `cfm:bath1/2` | 0 | bath multiblock halves | placeholder | low |
| 2768/2769 | `cfm:showerbottom/top` | 0 | shower multiblock | placeholder | low |
| 2770/2771 | `cfm:showerheadoff/on` | 0 | shower head | placeholder | low |
| 2772 | `cfm:bin` | 0 | bin, inventory when TE exists | `cfm:oak_crate` or placeholder outside TE path | low |
| 2773 | `cfm:present` | 0-15 | present color | `minecraft:<color>_wool` or placeholder | medium |
| 2774 | `cfm:tree` | 0 | decorative tree | `minecraft:oak_sapling` or leaves/log fallback | low |
| 2778 | `cfm:cookiejar` | 0 | cookie jar | placeholder | low |
| 2780 | `cfm:plate` | 0 | plate | placeholder | low |
| 2781 | `cfm:cup` | 0 | cup | placeholder | low |
| 2782 | `cfm:counterdoored` | 0 | kitchen counter | `cfm:white_kitchen_counter` or placeholder | medium |
| 2783 | `cfm:countersink` | 0 | counter sink | placeholder | low |
| 2785 | `cfm:kitchencabinet` | 0 | kitchen cabinet/drawer | `cfm:white_kitchen_drawer` or placeholder | medium |
| 2786 | `cfm:choppingboard` | 0 | chopping board | placeholder | low |
| 2787 | `cfm:barstool` | 0 | bar stool | placeholder | low |
| 2788/2789/2790 | `cfm:hey/nyan/pattern` | 0 | decorative special blocks | placeholder | low |
| 2791 | `cfm:yellowGlow` | 0 | glow block | `minecraft:glowstone` | medium |
| 2792 | `cfm:whiteGlass` | 0 | white glass | `minecraft:white_stained_glass` | high |
| 2919 | `cfm:stonepath` | 0 | stone path | `cfm:rock_path` or `minecraft:stone_pressure_plate` | medium |

## Fallbacki

- If CFM is not installed in the target pack, do not emit `cfm:*` by default; use placeholder or vanilla fallback and audit it.
- Furniture with lost shape but no state should use placeholder instead of `air`.
- Small devices with clear vanilla analogue: doorbell -> button, electric fence -> iron bars, ceiling light -> lantern/glowstone.
- Colored couch/presents can preserve color with wool fallback if exact target block is unavailable.

## Odrzucone / wymagajace review

- Fridge, freezer, oven, dishwasher, washing machine, printer, TV, stereo, microwave, blender and computer have device state or removed functionality; do not treat as safe block-only unless there is no TE at the position and the fallback is explicit.
- `bin`, `wallcabinet`, counters and kitchen cabinet can have inventory in old CFM; block-only converter must skip positions with TE.
- Any `cfm:*` target must be reviewed against installed target mods, because CFM is absent from `client_pack_1182/mod_manifest.json`.

## Handoff decyzji

- Krok 2 should route namespace `cfm` and map only no-TE positions.
- Default unknown CFM block: placeholder with `source_mod=cfm`, never implicit `minecraft:air`.
- Highest impact from coverage: `kitchencabinet`, `bedsidecabinet`, `printer`, `fridge/freezer`; the first two can be block-only only when no TE exists, printer/fridge/freezer remain review/TE/removal cases.
