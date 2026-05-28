# Armourer's Workshop Task 5A - raport

Zakres: deterministyczny fixture mapy 1.7.10 obejmujacy wszystkie znane bloki AW, reprezentatywne TE/NBT oraz globalne pliki `.armour`.

## Podsumowanie

- Samples: 26
- Source names covered: 20 / 20
- Converted: 23
- Placeholder-rescue: 3
- Failed: 0
- Skin library fixture files: 2

## Pokryte source names

- `armourLibrary`
- `armourerBrain`
- `awBoundingBox6`
- `colourMixer`
- `colourable`
- `colourableGlass`
- `colourableGlassGlowing`
- `colourableGlowing`
- `doll`
- `dyeTable`
- `globalSkinLibrary`
- `hologramProjector`
- `mannequin`
- `miniArmourer`
- `outfit_maker`
- `skinnable`
- `skinnableChild`
- `skinnableChildGlowing`
- `skinnableGlowing`
- `skinningTable`

## Wyniki konwersji

- `armour_library_empty` -> `armourers_workshop:skin-library` (converted)
- `global_skin_library_empty` -> `armourers_workshop:skin-library-global` (converted)
- `skinning_table` -> `armourers_workshop:skinning-table` (converted)
- `dye_table` -> `armourers_workshop:dye-table` (converted)
- `colour_mixer` -> `armourers_workshop:colour-mixer` (converted)
- `armourer_brain` -> `armourers_workshop:armourer` (converted)
- `bounding_box` -> `armourers_workshop:bounding-box` (converted)
- `colourable` -> `armourers_workshop:skin-cube` (converted)
- `colourable_glass` -> `armourers_workshop:skin-cube-glass` (converted)
- `colourable_glowing` -> `armourers_workshop:skin-cube-glowing` (converted)
- `colourable_glass_glowing` -> `armourers_workshop:skin-cube-glass-glowing` (converted)
- `hologram_projector` -> `armourers_workshop:hologram-projector` (converted)
- `mannequin_with_items` -> `conversion_placeholders:inventory_placeholder` (placeholder)
- `doll_placeholder` -> `conversion_placeholders:block_entity_placeholder` (placeholder)
- `mini_armourer_placeholder` -> `conversion_placeholders:block_entity_placeholder` (placeholder)
- `outfit_maker` -> `armourers_workshop:outfit-maker` (converted)
- `skinnable_parent_meta_2_south` -> `armourers_workshop:skinnable` (converted)
- `skinnable_child_meta_2_south` -> `armourers_workshop:skinnable` (converted)
- `skinnable_parent_meta_3_west` -> `armourers_workshop:skinnable` (converted)
- `skinnable_child_meta_3_west` -> `armourers_workshop:skinnable` (converted)
- `skinnable_parent_meta_4_north` -> `armourers_workshop:skinnable` (converted)
- `skinnable_child_meta_4_north` -> `armourers_workshop:skinnable` (converted)
- `skinnable_parent_meta_5_east` -> `armourers_workshop:skinnable` (converted)
- `skinnable_child_meta_5_east` -> `armourers_workshop:skinnable` (converted)
- `skinnable_glowing_library` -> `armourers_workshop:skinnable` (converted)
- `skinnable_child_glowing` -> `armourers_workshop:skinnable` (converted)

## Fixture biblioteki skinow

- `official/Barrel.armour` -> `ws:official/Barrel.armour`
- `Biret kap_a_ski.armour` -> `ws:Biret kap_a_ski.armour`

## Warningi unikalne

- `AW-W-SOURCE-NBT-PRESERVED: original TE NBT kept on ConversionEvent for audit.`: 17
- `AW-W-SKINNABLE-SHAPE-DEFAULT: exact Shape/Markers require converted .armour runtime read.`: 4
- `AW-W-SKINNABLE-CHILD-REFERENCE: converted as child Refer offset; parent must also convert.`: 4
- `AW-W-PLACEHOLDER-RESCUE: unsupported AW object preserved for manual/entity-stage conversion.`: 3
- `AW-W-ARMOURER-WORKSPACE-REBUILD: builder area/palette data needs source-backed follow-up.`: 1
- `AW-W-BOUNDING-BOX-RELINK: builder helper bounds need parent/refer validation.`: 1
- `AW-W-HOLOGRAM-INVENTORY-RESCUE: skin item stack conversion is staged after item converter.`: 1
- `AW-W-MANNEQUIN-ENTITY: 1.18.2 target is entity armourers_workshop:mannequin, not a block.`: 1
- `AW-W-DOLL-NO-BLOCK-TARGET: no 1.18.2 block registry equivalent found.`: 1
- `AW-W-MINI-ARMOURER-UNFINISHED: 1.7.10 mini armourer is not the main 1.18.2 builder path.`: 1
- `AW-W-OUTFIT-MAKER-NBT-REVIEW: 1.18.2 has outfit-maker BE, but no 1.7.10 TE sample was found yet.`: 1
- `AW-W-SKINNABLE-GLOWING-PROP: glow should come from SkinProperties after model conversion.`: 1
- `AW-W-SKINNABLE-CHILD-GLOWING-PROP: glow should come from SkinProperties after model conversion.`: 1

## Pliki

- `test_scenarios\armourers_workshop_task5a\armourers_workshop_task5a_source_patch_1710.json`
- `test_scenarios\armourers_workshop_task5a\armourers_workshop_task5a_converted_patch_1182.json`
- `test_scenarios\armourers_workshop_task5a\armourers_workshop_task5a_events_1182.json`
- `test_scenarios\armourers_workshop_task5a\armourers_workshop_task5a_conversion_report.json`
