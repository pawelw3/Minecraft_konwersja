# Block-only analiza: Jammy Furniture

Data: 2026-05-29

## Zakres i zrodla

Jammy Furniture sklada wiele mebli jako zwykle bloki z metadata, czesc z nich ma inventory albo semantyke funkcjonalna. Warstwa block-only jest potrzebna dla widocznych mebli bez TE; wpisy z `preserve_inventory=True` w istniejacym mapowaniu musza zostac poza block-only.

Zrodla lokalne:
- `mod_src/1710/code_from_jar/1.7.10/JammyFurniture/decompiled/`
- `src/converters/jammyfurniture/jammyfurniture_mapping.py`
- `src/converters/jammyfurniture/jammyfurniture_converter.py`
- `mapa_1710/level.dat` FML `ItemData`

Dynamiczne ID z `level.dat`: bloki `2695..2714`, `3159`; itemy/czesci `8731..8736`.

Uwaga o paczce 1.18.2: `client_pack_1182/mod_manifest.json` zawiera `supplementaries`, ale nie zawiera obecnie `Handcrafted` ani Macaw Furniture (`mcwfurnitures`). Targety z tych modow sa kandydatami projektowymi, a implementacja musi miec fallbacki vanilla/placeholder albo wymaga dodania JARow do paczki.

## Tabela block-only

| numeric_id | registry_name | metadata | source variant | target block | confidence |
|---:|---|---|---|---|---|
| 2695 | `JammyFurniture:LightsOn` | 0-15 | lamp variants on | `minecraft:lantern` / `minecraft:glowstone` fallback | low |
| 2696 | `JammyFurniture:LightsOff` | 0-15 | lamp variants off | `minecraft:lantern` fallback | low |
| 2697 | `JammyFurniture:WoodBlocksOne` | 0-12 | clock/blinds/decor wood variants | Supplementaries/Macaw/Handcrafted targets per mapping | medium |
| 2697 | `JammyFurniture:WoodBlocksOne` | 13 | crafting side, functional | outside block-only if inventory/TE exists; `minecraft:crafting_table` fallback | medium |
| 2697 | `JammyFurniture:WoodBlocksOne` | 14-15 | kitchen side/table | Macaw/Handcrafted targets per mapping | medium |
| 2698 | `JammyFurniture:WoodBlocksTwo` | 0-3 | kitchen cupboard, preserve inventory in mapping | outside block-only if inventory exists | high |
| 2698 | `JammyFurniture:WoodBlocksTwo` | 4-15 | shelves/TV/bin variants | Macaw/Handcrafted/Supplementaries targets per mapping | medium |
| 2699 | `JammyFurniture:WoodBlocksThree` | 0-15 | wood furniture family | targets from `jammyfurniture_mapping.py` | medium |
| 2700 | `JammyFurniture:WoodBlocksFour` | 0-15 | wood furniture family | targets from `jammyfurniture_mapping.py` | medium |
| 2701 | `JammyFurniture:IronBlocksOne` | 0-15 | iron/metal appliances | Macaw/vanilla/placeholder targets per mapping | medium |
| 2702 | `JammyFurniture:IronBlocksTwo` | 0-15 | metal appliances | Macaw/vanilla/placeholder targets per mapping | medium |
| 2703 | `JammyFurniture:CeramicBlocksOne` | 0-15 | bath/kitchen ceramic variants | Macaw/vanilla targets per mapping | medium |
| 2704 | `JammyFurniture:RoofingBlocksOne` | 0-15 | roof tiles | `minecraft:brick_slab` / `minecraft:brick_stairs` fallback | low |
| 2705 | `JammyFurniture:MiscBlocksOne` | 0-15 | misc decor | targets from mapping; review per metadata | low |
| 2706-2709 | `JammyFurniture:MobHeadsOne..Four` | 0-15 | decorative heads | `minecraft:skeleton_skull`/placeholder fallback | low |
| 2710 | `JammyFurniture:ArmChair` | 0-15 | armchair orientation/color | `handcrafted:chair` family if installed; placeholder fallback | low |
| 2711 | `JammyFurniture:SofaLeft` | 0-15 | sofa left | `handcrafted:couch` family if installed; placeholder fallback | low |
| 2712 | `JammyFurniture:SofaRight` | 0-15 | sofa right | `handcrafted:couch` family if installed; placeholder fallback | low |
| 2713 | `JammyFurniture:SofaCenter` | 0-15 | sofa center | `handcrafted:couch` family if installed; placeholder fallback | low |
| 2714 | `JammyFurniture:SofaCorner` | 0-15 | sofa corner | `handcrafted:couch` family if installed; placeholder fallback | low |
| 3159 | `JammyFurniture:Bath` | 0-15 | bath | `mcwfurnitures:bath` if installed; `minecraft:cauldron` fallback | low |

## Fallbacki

- Furniture without exact target: `conversion_placeholders:decorative_placeholder` if available, otherwise simple vanilla analog (`cauldron`, `lantern`, `crafting_table`, `brick_stairs`).
- Upholstered furniture: preserve shape more than color; color fallback warning required.
- Mob heads: placeholder preferred over random skull if visual identity matters.

## Odrzucone / wymagajace review

- Wszystkie mappings with `preserve_inventory=True` are outside block-only when TE/inventory is present.
- `LightBulb`, `MantlePieceUnf`, `CeramicPanel*`, `WMDrum`, `BlindPart` are items/parts from `level.dat`, not terrain blocks.
- Exact metadata decoding is already partly encoded in `jammyfurniture_mapping.py`; step 2 should reuse it, not duplicate by hand.

## Handoff decyzji

- Krok 2 powinien wrapowac `JAMMY_FURNITURE_MAPPINGS`, odfiltrowac wpisy `preserve_inventory=True` i sprawdzac target mod against `client_pack_1182/mod_manifest.json`.
- Unknown metadata must fallback with audit, never to `minecraft:air`.
