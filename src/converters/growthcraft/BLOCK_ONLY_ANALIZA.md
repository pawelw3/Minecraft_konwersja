# Block-only analiza: GrowthCraft

Data: 2026-05-29

## Zakres i zrodla

GrowthCraft ma mieszanke cropow, lin, roslin, bambusa, blokow spozywczych i maszyn z TileEntity. Warstwa block-only jest sensowna dla roslin/dekoracji bez TE, ale bloki cellar/bees/milk/fishtrap z NBT zostaja w dotychczasowym konwerterze.

Zrodla lokalne:
- `mod_src/1710/actual_src/1.7.10/Growthcraft/`
- `mod_src/actual_src/1.18.2/Growthcraft/`
- `src/converters/growthcraft/growthcraft_converter.py`
- `src/converters/growthcraft/mappings/`
- `output/growthcraft_task4/growthcraft_task4_report.md`
- `mapa_1710/level.dat` FML `ItemData`

Dynamiczne ID z `level.dat`: 219 wpisow `Growthcraft*`; bloki terrain glownie `2576..2687`, `3147`, `3154`, `3619..3638`.
Raport mapy znalazl 162 bloki GrowthCraft, ale wszystkie odkryte typy byly TE albo inny mod (`PamFishTrap`).

Uwaga o paczce 1.18.2: lokalny source GrowthCraft 1.18.2 istnieje w `mod_src`, ale `client_pack_1182/mod_manifest.json` nie zawiera obecnie JAR GrowthCraft. Targety `growthcraft_*:*` sa kandydatami po dodaniu moda do paczki; fallbacki vanilla/placeholder sa obowiazkowe w implementacji.

## Tabela block-only

| numeric_id | registry_name | metadata | source variant | target block | confidence |
|---:|---|---|---|---|---|
| 2576 | `Growthcraft:grc.fenceRope` | 0-15 | rope fence segment | `growthcraft:rope_fence` albo `minecraft:oak_fence` fallback | low |
| 2577 | `Growthcraft:grc.ropeBlock` | 0-15 | rope block, orientacja/shape | `growthcraft:rope_block` albo `minecraft:chain` fallback | low |
| 2578 | `Growthcraft:grccore.salt_block` | 0 | salt block | `growthcraft:salt_block` po dodaniu moda; fallback `minecraft:white_concrete` | low |
| 2586 | `Growthcraft|Apples:grc.appleSapling` | 0-15 | apple sapling age/type | `growthcraft_apples:apple_tree_sapling` po dodaniu moda; fallback `minecraft:oak_sapling` | low |
| 2587 | `Growthcraft|Apples:grc.appleLeaves` | 0-15 | apple leaves, decay/check bits | `growthcraft_apples:apple_tree_leaves` po dodaniu moda; fallback `minecraft:oak_leaves` | low |
| 2588 | `Growthcraft|Apples:grc.appleBlock` | 0-15 | apple fruit block | `growthcraft_apples:apple` po dodaniu moda; fallback placeholder | low |
| 2596 | `Growthcraft|Bamboo:grc.bambooBlock` | 0-15 | bamboo block | `growthcraft_bamboo:bamboo_block` po dodaniu moda; fallback `minecraft:bamboo_block` if available or `minecraft:oak_planks` | low |
| 2597 | `Growthcraft|Bamboo:grc.bambooShoot` | 0-15 | bamboo shoot | `growthcraft_bamboo:bamboo_shoot` po dodaniu moda; fallback `minecraft:bamboo` | low |
| 2598 | `Growthcraft|Bamboo:grc.bambooStalk` | 0-15 | bamboo stalk | `growthcraft_bamboo:bamboo_stalk` po dodaniu moda; fallback `minecraft:bamboo` | low |
| 2599 | `Growthcraft|Bamboo:grc.bambooLeaves` | 0-15 | bamboo leaves | `growthcraft_bamboo:bamboo_leaves` po dodaniu moda; fallback `minecraft:jungle_leaves` | low |
| 2600 | `Growthcraft|Bamboo:grc.bambooFence` | 0-15 | bamboo fence | `growthcraft_bamboo:bamboo_fence` po dodaniu moda; fallback `minecraft:oak_fence` | low |
| 2601 | `Growthcraft|Bamboo:grc.bambooFenceRope` | 0-15 | bamboo fence with rope | `growthcraft_bamboo:bamboo_fence` fallback | low |
| 2603 | `Growthcraft|Bamboo:grc.bambooStairs` | 0-7 | bamboo stairs, facing/half | `growthcraft_bamboo:bamboo_stairs` | medium |
| 2604 | `Growthcraft|Bamboo:grc.bambooSingleSlab` | 0-15 | bamboo slab | `growthcraft_bamboo:bamboo_slab` | medium |
| 2605 | `Growthcraft|Bamboo:grc.bambooDoubleSlab` | 0-15 | bamboo double slab | `growthcraft_bamboo:bamboo_block` | medium |
| 2606 | `Growthcraft|Bamboo:grc.bambooDoor` | 0-15 | legacy door halves | `growthcraft_bamboo:bamboo_door` | low |
| 2607 | `Growthcraft|Bamboo:grc.bambooFenceGate` | 0-15 | fence gate facing/open | `growthcraft_bamboo:bamboo_fence_gate` | medium |
| 2608 | `Growthcraft|Bamboo:grc.bambooScaffold` | 0-15 | scaffold | `minecraft:scaffolding` | low |
| 2614 | `Growthcraft|Bees:grc.beeHive` | 0-15 | beehive world block | `minecraft:bee_nest` fallback | low |
| 2629 | `Growthcraft|Grapes:grc.grapeVine0` | 0-15 | grape vine lower/age | `growthcraft_grapes:grape_vine_crop` | medium |
| 2630 | `Growthcraft|Grapes:grc.grapeVine1` | 0-15 | grape vine upper/age | `growthcraft_grapes:grape_vine_crop` | medium |
| 2631 | `Growthcraft|Grapes:grc.grapeLeaves` | 0-15 | grape leaves | `growthcraft_grapes:grape_leaves` fallback review | low |
| 2632 | `Growthcraft|Grapes:grc.grapeBlock` | 0-15 | grape fruit block | `growthcraft_grapes:purple_grape_vine_crop` fallback | low |
| 2641 | `Growthcraft|Hops:grc.hopVine` | 0-15 | hop vine age/height | `growthcraft_hops:hop_vine` | medium |
| 2664 | `Growthcraft|Milk:grcmilk.Thistle` | 0-15 | thistle crop age | `growthcraft_milk:thistle_crop` | medium |
| 2679 | `Growthcraft|Rice:grc.riceBlock` | 0-15 | rice crop age | `growthcraft_rice:rice_crop` | medium |
| 2680 | `Growthcraft|Rice:grc.paddyField` | 0-15 | paddy field / cultivated wet farmland | `growthcraft_rice:cultivated_farmland` | medium |
| 3147 | `Growthcraft|Bamboo:grc.bambooWall` | 0-15 | bamboo wall | `minecraft:bamboo_block` / `minecraft:oak_fence` fallback | low |

## Fallbacki

- Rosliny/cropy: jezeli target GrowthCraft 1.18.2 nie jest zarejestrowany w paczce, fallback do najblizszego vanilla crop/support (`minecraft:wheat`, `minecraft:vine`, `minecraft:scaffolding`) z `confidence=low`.
- Bambusowe dekoracje: `minecraft:bamboo_block`, `minecraft:scaffolding`, `minecraft:oak_fence` zalezne od shape.
- Plyny `*Fluid*` poza zakresem block-only na tym etapie; wymagaja osobnej decyzji fluidowej.

## Odrzucone / wymagajace review

- `fruitPress`, `fruitPresser`, `brewKettle`, `fermentBarrel`, `fermentJar`, `beeBox`, `fishTrap`, `ButterChurn`, `CheesePress`, `CheeseVat`, `Pancheon` to TE/NBT.
- Grape color variants w 1.18.2 sa rozbite na red/purple/white; mapowanie z 1.7.10 metadata wymaga review tekstur i source.
- Drzwi i schody wymagaja dokladnego dekodowania legacy metadata przed implementacja.

## Handoff decyzji

- Krok 2 zaczac od cropow i prostych blokow tylko po rozstrzygnieciu, czy GrowthCraft JAR trafia do paczki; bez tego implementowac tylko fallbacki vanilla/placeholder.
- Bloki TE zostawic w `growthcraft_converter.py`.
