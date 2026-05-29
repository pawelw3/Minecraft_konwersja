# Block-only analiza: Extra Utilities

Data: 2026-05-29

## Zakres i zrodla

Extra Utilities ma duzo zwyklych blokow bez TE, ale raport pokrycia projektu znalazl na mapie glownie bloki funkcjonalne z TE i nie wykryl dodatkowych blokow ExU w probce. Warstwa block-only jest mimo to potrzebna dla bezpiecznego direct terrain writera, bo `level.dat` zawiera wiele dekoracyjnych/utility registry names.

Zrodla lokalne:
- `mod_src/1710/code_from_jar/1.7.10/ExtraUtilities/decompiled/`
- `src/converters/extrautils/mappings/block_mappings.py`
- `src/converters/extrautils/extrautils_converter.py`
- `output/extrautils_task4/extrautils_coverage_report.md`
- `mapa_1710/level.dat` FML `ItemData`

Dynamiczne ID z `level.dat`: 80 wpisow `ExtraUtilities:*`, z czego bloki terrain sa glownie `1949..2004`, `2189`, `2216`, `2496`, `2569`, `3203`, `3205`.

## Tabela block-only

| numeric_id | registry_name | metadata | source variant | target block | confidence |
|---:|---|---|---|---|---|
| 1955 | `ExtraUtilities:angelBlock` | 0 | Angel Block | `angelblockrenewed:angel_block` | high |
| 1958 | `ExtraUtilities:decorativeBlock1` | 0-15 | decorative block family | `minecraft:stone` fallback | low |
| 1959 | `ExtraUtilities:decorativeBlock2` | 0-15 | decorative block family | `minecraft:stone` fallback | low |
| 1961 | `ExtraUtilities:block_bedrockium` | 0 | Bedrockium Block | `conversion_placeholders:decorative_placeholder` albo `minecraft:netherite_block` | low |
| 1963 | `ExtraUtilities:colorStoneBrick` | 0-15 | colored stone brick | matching `minecraft:*_concrete` by legacy dye meta | medium |
| 1964 | `ExtraUtilities:colorWoodPlanks` | 0-15 | colored planks | matching `minecraft:*_concrete` by legacy dye meta | low |
| 1965 | `ExtraUtilities:color_lightgem` | 0-15 | colored glowstone | matching `minecraft:*_concrete` or `minecraft:glowstone` fallback | low |
| 1966 | `ExtraUtilities:color_stone` | 0-15 | colored stone | matching `minecraft:*_concrete` by legacy dye meta | medium |
| 1967 | `ExtraUtilities:color_quartzBlock` | 0-15 | colored quartz | matching `minecraft:*_concrete` by legacy dye meta | low |
| 1968 | `ExtraUtilities:color_hellsand` | 0-15 | colored soulsand/netherrack family | matching `minecraft:*_concrete` fallback | low |
| 1969 | `ExtraUtilities:color_redstoneLight` | 0-15 | colored redstone lamp/light | matching `minecraft:*_concrete` or `minecraft:redstone_lamp` fallback | low |
| 1972 | `ExtraUtilities:color_blockLapis` | 0-15 | colored lapis block | matching `minecraft:*_concrete` fallback | low |
| 1973 | `ExtraUtilities:color_obsidian` | 0-15 | colored obsidian | matching `minecraft:*_concrete` fallback | low |
| 1974 | `ExtraUtilities:color_blockRedstone` | 0-15 | colored redstone block | matching `minecraft:*_concrete` fallback | low |
| 1975 | `ExtraUtilities:color_blockCoal` | 0-15 | colored coal block | matching `minecraft:*_concrete` fallback | low |
| 1976 | `ExtraUtilities:cobblestone_compressed` | 0-7 | compressed cobblestone tiers | `minecraft:cobblestone` with warning | medium |
| 1977 | `ExtraUtilities:conveyor` | 0-15 | conveyor belt, directional | `minecraft:black_concrete` fallback | low |
| 1987 | `ExtraUtilities:cursedearthside` | 0 | Cursed Earth | `cursedearth:cursed_earth` | high |
| 1988 | `ExtraUtilities:trashcan` | 0-2 | trash cans, may have TE | outside block-only when TE exists; fallback `trashcans:item_trash_can` | medium |
| 1989 | `ExtraUtilities:spike_base` | 0-15 | iron spikes | `minecraft:iron_bars` fallback | low |
| 1990 | `ExtraUtilities:spike_base_diamond` | 0-15 | diamond spikes | `minecraft:iron_bars` fallback | low |
| 1991 | `ExtraUtilities:spike_base_gold` | 0-15 | gold spikes | `minecraft:iron_bars` fallback | low |
| 1992 | `ExtraUtilities:spike_base_wood` | 0-15 | wood spikes | `minecraft:oak_fence` fallback | low |
| 1998 | `ExtraUtilities:magnumTorch` | 0 | Magnum Torch, TE on map | `torchmaster:megatorch` | high |
| 2000 | `ExtraUtilities:generator` | 0-11 | generators, TE | outside block-only when TE exists; existing mapping to Thermal/Mekanism | medium |
| 2001 | `ExtraUtilities:generator.8` | 0-11 | x8 generators, TE | outside block-only when TE exists; existing mapping | medium |
| 2004 | `ExtraUtilities:etherealglass` | 0-15 | Ethereal Glass variants | `minecraft:glass` | low |
| 2189 | `ExtraUtilities:sound_muffler` | 0 | Sound Muffler | `extremesoundmuffler:sound_muffler` | high |
| 2216 | `ExtraUtilities:filing` | 0-11 | Filing Cabinet, TE | outside block-only; placeholder when TE exists | high |
| 2496 | `ExtraUtilities:color_brick` | 0-15 | colored brick | matching `minecraft:*_concrete` fallback | low |
| 3203 | `ExtraUtilities:color_stonebrick` | 0-15 | colored stonebrick | matching `minecraft:*_concrete` fallback | low |
| 3205 | `ExtraUtilities:generator.64` | 0-11 | x64 generators, TE | outside block-only when TE exists; existing mapping | medium |

## Fallbacki

- Kolorowe bloki ExU: zachowac kolor przez legacy dye meta -> concrete, confidence `low/medium` zalezne od rodziny.
- Compressed cobblestone: `minecraft:cobblestone`, warning o utracie tieru.
- Ethereal Glass: `minecraft:glass`, warning o utracie kolizji selektywnej.
- Nieznany `ExtraUtilities:*`: `conversion_placeholders:decorative_placeholder` jesli dostepny, inaczej `minecraft:stone`; nigdy `minecraft:air`.

## Odrzucone / wymagajace review

- Generatory, filing cabinet, drum, quarry, trash can z TE musza zostac w konwerterze TE/NBT.
- `pipes` i `microblocks` nie sa zwyklym block-only; wymagaja wlasnych systemow.
- Decorative families wymagaja wizualnego review tekstur przed uznaniem targetow za `high`.

## Handoff decyzji

- Krok 2 powinien zaczac od rodzin juz w `block_mappings.py` (`magnumTorch`, `cursedearthside`, `angelBlock`, `sound_muffler`, generatory jako fallback awaryjny).
- Dla pozostalych dekoracji dodac kontrolowane fallbacki z audytem i `confidence=low`.
