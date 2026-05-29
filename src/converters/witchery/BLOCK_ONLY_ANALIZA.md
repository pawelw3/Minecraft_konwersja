# Block-only analiza: Witchery

Data: 2026-05-29

## Zakres i zrodla

Witchery has no direct 1.18.2 port in the target pack. Hexerei is installed, but block identity is not 1:1. Block-only should preserve placed ordinary plants, woods, glass, fences, decorative terrain and glyphs with vanilla/Hexerei/placeholder fallbacks. All functional Witchery TE stay in the placeholder/NBT converter.

Zrodla lokalne:
- `src/converters/witchery/WITCHERY_BLOCKS_AND_TE.md`
- `mapa_1710/level.dat` FML `ItemData`
- `client_pack_1182/mod_manifest.json`

Dynamiczne IDs for Witchery blocks are `3661..3988` in the source map.

## Tabela block-only

| numeric_id | registry_name | metadata | source variant | target block | confidence |
|---:|---|---|---|---|---|
| 3663 | `witchery:force` | 0 | force block | placeholder | low |
| 3666 | `witchery:spanishmoss` | 0 | spanish moss | `minecraft:vine` or Hexerei moss review | medium |
| 3671 | `witchery:embermoss` | 0 | ember moss | placeholder or `minecraft:fire` visual review | low |
| 3674 | `witchery:wolfsbane` | 0-7 | crop age | Hexerei/vanilla flower fallback | low |
| 3677 | `witchery:leapinglily` | 0 | leaping lily | `minecraft:lily_pad` | medium |
| 3683 | `witchery:alderwooddoor` | 0-15 | alder door state | `minecraft:oak_door` or Hexerei wood door review | medium |
| 3686 | `witchery:belladonna` | 0-7 | crop age | Hexerei belladonna if exists else flower placeholder | low |
| 3687 | `witchery:shadedglass` | 0 | shaded glass | `minecraft:tinted_glass` | medium |
| 3693 | `witchery:witchwoodslab` | 0-15 | witch wood slab | `minecraft:oak_slab` | medium |
| 3698 | `witchery:rowanwooddoor` | 0-15 | rowan door state | `minecraft:oak_door` or Hexerei wood door review | medium |
| 3707 | `witchery:daylightcollector` | 0 | daylight collector | `minecraft:daylight_detector` | medium |
| 3709 | `witchery:disease` | 0 | disease fluid | explicit air or placeholder fluid review | low |
| 3720 | `witchery:stairswoodrowan` | 0-15 | rowan stairs | `minecraft:oak_stairs` | medium |
| 3721 | `witchery:circleglyphinfernal` | 0-15 | infernal glyph | placeholder flat marker | low |
| 3735 | `witchery:infinityegg` | 0 | infinity egg | `minecraft:dragon_egg` or placeholder | low |
| 3743 | `witchery:circleglyphotherwhere` | 0-15 | otherwhere glyph | placeholder flat marker | low |
| 3747 | `witchery:stockade` | 0-15 | stockade | `minecraft:oak_fence` | medium |
| 3751 | `witchery:bramble` | 0 | bramble | `minecraft:sweet_berry_bush` | medium |
| 3752 | `witchery:pitdirt` | 0 | pit dirt | `minecraft:dirt` | medium |
| 3754 | `witchery:witchsapling` | 0-2 | rowan/alder/hawthorn sapling | `minecraft:oak_sapling` | medium |
| 3756 | `witchery:witchwood` | 0-2 | witch wood planks/log helper in source | `minecraft:oak_planks` or `minecraft:oak_log` review | low |
| 3771 | `witchery:witchleaves` | 0-2 | witch leaves | `minecraft:oak_leaves` | medium |
| 3775 | `witchery:spiritflowing` | 0 | spirit fluid | placeholder fluid review | low |
| 3778 | `witchery:glintweed` | 0 | glint weed | `minecraft:glow_lichen` or placeholder | low |
| 3786 | `witchery:wickerbundle` | 0 | wicker block | `minecraft:hay_block` or bamboo block review | medium |
| 3796 | `witchery:tormentstone` | 0 | torment stone | `minecraft:blackstone` | medium |
| 3800 | `witchery:stairswoodalder` | 0-15 | alder stairs | `minecraft:oak_stairs` | medium |
| 3801 | `witchery:icestockade` | 0-15 | ice stockade | `minecraft:packed_ice` or fence placeholder | low |
| 3808 | `witchery:circleglyphritual` | 0-15 | ritual glyph | placeholder flat marker | low |
| 3824 | `witchery:crittersnare` | 0 | critter snare | placeholder | low |
| 3834 | `witchery:snowbell` | 0-7 | crop age | `minecraft:snow`/flower placeholder | low |
| 3835 | `witchery:wallgen` | 0 | village wall generator | placeholder | low |
| 3844 | `witchery:stairswoodhawthorn` | 0-15 | hawthorn stairs | `minecraft:oak_stairs` | medium |
| 3845 | `witchery:bloodedwool` | 0 | blooded wool | `minecraft:red_wool` | medium |
| 3864 | `witchery:shadedglass_active` | 0 | active shaded glass | `minecraft:tinted_glass` | medium |
| 3875 | `witchery:mandrake` | 0-7 | crop age | Hexerei/flower placeholder | low |
| 3877 | `witchery:wormwood` | 0-7 | crop age | Hexerei/flower placeholder | low |
| 3892 | `witchery:mirrorwall` | 0 | mirror wall | `minecraft:glass` or placeholder | low |
| 3899 | `witchery:perpetualice` | 0-15 | perpetual ice variants | `minecraft:blue_ice` / `minecraft:packed_ice` | medium |
| 3907 | `witchery:garlicplant` | 0-7 | garlic crop | Hexerei garlic if exists else crop placeholder | low |
| 3909 | `witchery:artichoke` | 0-7 | crop age | crop placeholder | low |
| 3930 | `witchery:demonheart` | 0 | demon heart block | placeholder | low |
| 3932 | `witchery:mindrake` | 0-7 | crop age | crop placeholder | low |
| 3939 | `witchery:pitgrass` | 0 | pit grass | `minecraft:grass_block` | medium |
| 3941 | `witchery:lilypad` | 0 | lily pad | `minecraft:lily_pad` | high |
| 3945 | `witchery:witchlog` | 0-2 | rowan/alder/hawthorn log | `minecraft:oak_log` | medium |
| 3951 | `witchery:plantmine` | 0 | plant mine | placeholder | low |
| 3956 | `witchery:brew` | 0 | brew fluid | placeholder fluid review | low |
| 3958 | `witchery:hollowtears` | 0 | hollow tears fluid | placeholder fluid review | low |

## Fallbacki

- Trees/wood: vanilla oak family preserves structure if exact Hexerei wood mapping is not validated.
- Crops/plants: use Hexerei only after target registry validation; otherwise placeholder/vanilla plant with low confidence.
- Shaded glass: `minecraft:tinted_glass`.
- Glyphs and magic blocks: placeholder, not air, because they are intentional ritual layout markers.
- Fluids: special review; explicit air only if accepted as removed technical/magic fluid.

## Odrzucone / wymagajace review

- All blocks listed as functional/decorative TE in `WITCHERY_BLOCKS_AND_TE.md` are outside block-only even if visually simple.
- Cursed redstone blocks, traps with TE, placed item, mirrors, altars, cauldrons, ovens and ritual devices remain placeholder/NBT converter scope.
- Exact Hexerei target registries must be validated before using them.

## Handoff decyzji

- Krok 2 should start with conservative vanilla/placeholder mappings and strong audit warnings.
- Do not emit Hexerei block IDs until a target-registry scan confirms names.
