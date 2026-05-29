# Block-only analiza: Mekanism

Data: 2026-05-29

## Zakres i zrodla

Mekanism ma bardzo duzo blokow bez TE: rudy, bloki materialowe, plastik/kolorowe bloki, salt block, teleporter frame i czesc konstrukcji multiblokow. Maszyny i zbiorniki zostaja w konwerterze TE/NBT.

Zrodla lokalne:
- `mod_src/1710/actual_src/1.7.10/Mekanism/`
- `mod_src/118/actual_src/1.18.2/Mekanism/`
- `src/converters/mekanism/mappings.py`
- `src/converters/mekanism/analyze_map_coverage.py`
- `output/mekanism/mekanism_coverage_report.md`
- `mapa_1710/level.dat` FML `ItemData`

Dynamiczne ID z `level.dat`: Mekanism core block IDs `2154..2171`; Generators `2717..2719`; item/tool IDs outside terrain.
Raport stref znalazl 157492 bloki Mekanism, z czego najwiecej to rudy i plastikowe bloki bez TE.

## Tabela block-only

| numeric_id | registry_name | metadata | source variant | target block | confidence |
|---:|---|---|---|---|---|
| 2154 | `Mekanism:BasicBlock` | 0 | osmium block | `mekanism:block_osmium` | high |
| 2154 | `Mekanism:BasicBlock` | 1 | bronze block | `mekanism:block_bronze` | high |
| 2154 | `Mekanism:BasicBlock` | 2 | refined obsidian block | `mekanism:block_refined_obsidian` | high |
| 2154 | `Mekanism:BasicBlock` | 3 | charcoal block | `mekanism:block_charcoal` | high |
| 2154 | `Mekanism:BasicBlock` | 4 | refined glowstone block | `mekanism:block_refined_glowstone` | high |
| 2154 | `Mekanism:BasicBlock` | 5 | steel block | `mekanism:block_steel` | high |
| 2154 | `Mekanism:BasicBlock` | 6 | bin, TE on map | outside block-only when TE exists | high |
| 2154 | `Mekanism:BasicBlock` | 7 | teleporter frame | `mekanism:teleporter_frame` | high |
| 2154 | `Mekanism:BasicBlock` | 8 | steel casing | `mekanism:steel_casing` | high |
| 2154 | `Mekanism:BasicBlock` | 9-11 | dynamic tank/glass/valve multiblock | outside block-only if BE needed; target mappings exist | medium |
| 2154 | `Mekanism:BasicBlock` | 12 | copper block | `minecraft:copper_block` | high |
| 2154 | `Mekanism:BasicBlock` | 13 | tin block | `mekanism:block_tin` | high |
| 2154 | `Mekanism:BasicBlock` | 14-15 | salination controller/valve | outside block-only when TE/multiblock state exists | high |
| 2155 | `Mekanism:BasicBlock2` | 0 | thermal evaporation block | `mekanism:thermal_evaporation_block` | medium |
| 2155 | `Mekanism:BasicBlock2` | 1 | induction casing | `mekanism:induction_casing` | medium |
| 2155 | `Mekanism:BasicBlock2` | 2 | induction port, TE on map | outside block-only when TE exists | high |
| 2155 | `Mekanism:BasicBlock2` | 3-4 | induction cell/provider family | requires review; likely TE/multiblock | low |
| 2159 | `Mekanism:OreBlock` | 0 | osmium ore | `mekanism:osmium_ore` | high |
| 2159 | `Mekanism:OreBlock` | 1 | copper ore | `minecraft:copper_ore` | high |
| 2159 | `Mekanism:OreBlock` | 2 | tin ore | `mekanism:tin_ore` | high |
| 2160 | `Mekanism:EnergyCube` | 0-4 | energy cube tiers, TE | outside block-only when TE exists | high |
| 2161 | `Mekanism:ObsidianTNT` | 0 | Obsidian TNT removed in Mek 10 | `minecraft:tnt` | medium |
| 2162 | `Mekanism:BoundingBlock` | 0-1 | bounding/helper block | `mekanism:bounding_block` | medium |
| 2163 | `Mekanism:GasTank` | 0 | gas tank, TE | outside block-only when TE exists | high |
| 2164 | `Mekanism:CardboardBox` | 0 | cardboard box, stores captured block | outside block-only; needs NBT | high |
| 2165 | `Mekanism:PlasticBlock` | 0-15 | colored plastic | matching `minecraft:*_concrete` by legacy dye meta | medium |
| 2166 | `Mekanism:SlickPlasticBlock` | 0-15 | colored slick plastic | matching `minecraft:*_concrete` by legacy dye meta | medium |
| 2167 | `Mekanism:GlowPlasticBlock` | 0-15 | colored glowing plastic | matching `minecraft:*_concrete` or glow fallback | low |
| 2168 | `Mekanism:ReinforcedPlasticBlock` | 0-15 | colored reinforced plastic | matching `minecraft:*_concrete` | medium |
| 2169 | `Mekanism:RoadPlasticBlock` | 0-15 | colored road plastic | matching `minecraft:*_concrete` | medium |
| 2170 | `Mekanism:PlasticFence` | 0-15 | colored plastic fence | `minecraft:*_concrete` is shape-loss fallback; better placeholder/fence review | low |
| 2171 | `Mekanism:SaltBlock` | 0 | salt block | `mekanism:block_salt` | high |

## Fallbacki

- Plastic families: use existing `CONCRETE_BY_LEGACY_DYE_META` from `mappings.py`, confidence `medium`; warning that texture/material changes.
- Glow/reinforced/road plastic: same color-preserving concrete fallback, confidence `low/medium`.
- Obsidian TNT: `minecraft:tnt`, warning about behavior loss.
- Unknown Mekanism block: placeholder or `minecraft:stone`, never `air`.

## Odrzucone / wymagajace review

- `MachineBlock*`, `EnergyCube`, `GasTank`, `CardboardBox`, ports/controllers with real TE must remain in TE/NBT converter.
- `BasicBlock2` metas 3-4 and some multiblock internals need source review before high-confidence block-only mapping.
- `MekanismGenerators:*` is outside this Mekanism core report unless a later pass includes generators explicitly.

## Handoff decyzji

- Krok 2 should reuse `get_block_mapping()` and filter `has_block_entity=False`.
- Highest impact first: `OreBlock`, `PlasticBlock`, `SlickPlasticBlock`, `RoadPlasticBlock`, `SaltBlock`, `BasicBlock` materials.
