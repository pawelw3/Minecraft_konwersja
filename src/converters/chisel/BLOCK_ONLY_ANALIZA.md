# Chisel - Block-Only Analiza (Krok 1)

> **Mod:** Chisel 2.9.5.11 (1.7.10) -> Rechiseled / Chipped / Vanilla 1.18.2  
> **Data:** 2026-05-29  
> **Cel:** Identyfikacja zwyklych blokow bez TileEntity.

---

## 1. Stan faktyczny

Chisel to **dekoracyjny mod w calosci oparty na zwyklych blokach bez TileEntity**. Prawie wszystkie bloki to warianty tekstur zapisane jako numeric ID + metadata w chunk Sections.

Inspekcja bytecode JAR wykazala, ze **3 bloki** maja TileEntity:
- BlockAutoChisel (maszyna)
- BlockPresent (prezent z zawartoscia)
- BlockCarvableBeacon (beacon z wariantami)

Wszystkie pozostale bloki dziedzicza po BlockCarvable (a ta po net.minecraft.block.Block), wiec **nie maja TileEntity**.

Liczba rodzin blokow w 1.7.10: **223+ rodzin**, **~2600+ wariantow**.

---

## 2. Bloki bez TileEntity w 1.7.10

Ze wzgledu na ogromna liczbe rodzin, ponizej tabela najwazniejszych rodzin z perspektywy mapy.

| # | Registry hint | Warianty | Opis | Najlepszy target 1.18.2 | Pewnosc |
|---|---------------|----------|------|------------------------|---------|
| 1 | chisel:sandstone | 62 | Warianty sandstone | rechiseled:sandstone_* / chipped:sandstone_* | medium |
| 2 | chisel:stonebrick | ~40 | Stone bricks | rechiseled:stone_bricks_* / chipped:stone_bricks_* | medium |
| 3 | chisel:cobblestone | ~40 | Cobblestone | rechiseled:cobblestone_* / chipped:cobblestone_* | medium |
| 4 | chisel:marble | 20 | Marble | rechiseled:marble_* / chipped:marble_* | medium |
| 5 | chisel:limestone | 20 | Limestone | rechiseled:limestone_* / chipped:limestone_* | medium |
| 6 | chisel:obsidian | 21 | Obsidian | rechiseled:obsidian_* | medium |
| 7 | chisel:dirt | 20 | Dirt | rechiseled:dirt_* | medium |
| 8 | chisel:ice | 20 | Ice | rechiseled:ice_* | medium |
| 9 | chisel:factory | 24 | Factory/industrial | rechiseled:iron_* / chipped:iron_block_* | low |
| 10 | chisel:technical | 58 | Technical/cables | chipped:* (brak bliskiego) | low |
| 11 | chisel:laboratory | 24 | Laboratory | chipped:* (brak bliskiego) | low |
| 12 | chisel:gold | 42 | Gold block variants | rechiseled:gold_* | medium |
| 13 | chisel:iron | 39 | Iron block variants | rechiseled:iron_* | medium |
| 14 | chisel:diamond | 18 | Diamond block variants | rechiseled:diamond_* | medium |
| 15 | chisel:redstone | 19 | Redstone block variants | rechiseled:redstone_* | medium |
| 16 | chisel:glass | ~50 | Glass variants | rechiseled:glass_* / chipped:glass_* | medium |
| 17 | chisel:glasspanedyed | 192 | Dyed glass panes | minecraft:*_stained_glass_pane / chipped:* | low |
| 18 | chisel:bookshelf | 18 | Bookshelf variants | rechiseled:oak_bookshelf_* / chipped:bookshelf_* | medium |
| 19 | chisel:endstone | 24 | End stone variants | rechiseled:end_stone_* | medium |
| 20 | chisel:andesite | ~20 | Andesite | rechiseled:andesite_* | high |
| 21 | chisel:basalt | ~20 | Basalt | rechiseled:basalt_* | high |
| 22 | chisel:diorite | ~20 | Diorite | rechiseled:diorite_* | high |
| 23 | chisel:granite | ~20 | Granite | rechiseled:granite_* | high |

### Uwagi do mapowania
- Chisel 1.7.10 uzywa metadata 0-15 do rozrozniania wariantow w obrebie jednego bloku. W 1.18.2 Rechiseled/Chipped uzywaja osobnych registry names lub blockstates.
- Dyed glass panes (glasspanedyed) to najwieksza rodzina (192 warianty). W 1.18.2 nie ma bezposredniego odpowiednika.
- Technical / Factory / Laboratory to rodziny o wysoce specyficznych teksturach industrialnych.
- Present w 1.7.10 ma osobne TileEntity (TileEntityPresent), wiec warianty present jako blok bez TE sa watpliwe.
- chisel:auto_chisel to maszyna z TE (poza zakresem).

---

## 3. Bloki z TileEntity (poza zakresem block-only)

| Registry name | Klasa | Opis |
|---------------|-------|------|
| chisel:autoChisel | BlockAutoChisel | Auto Chisel (maszyna) |
| chisel:present | BlockPresent | Prezent (z zawartoscia) |
| chisel:beacon | BlockCarvableBeacon | Beacon warianty |

---

## 4. Fallbacki i decyzje

| Sytuacja | Fallback | Pewnosc |
|----------|----------|---------|
| Nieznana rodzina Chisel (stone-like) | rechiseled:stone_* lub minecraft:stone | low |
| Nieznana rodzina Chisel (metal-like) | rechiseled:iron_* lub minecraft:iron_block | low |
| Nieznana rodzina Chisel (wood-like) | rechiseled:oak_* lub minecraft:oak_planks | low |
| Dyed glass pane (nieznany wariant) | minecraft:white_stained_glass_pane | low |
| Technical/Factory bez odpowiednika | minecraft:iron_block | low |
| Pumpkin warianty | minecraft:carved_pumpkin | medium |

---

## 5. Warianty odrzucone / wymagajace review

- **Bloki zalezne od innych modow** (ae_certus_quartz, ae_sky_stone, aluminum, copper, tin, silver, lead, nickel, platinum, steel, bronze, electrum, invar, signalum, lumium, enderium, thaumium, mana_quartz, elf_quartz, sun_quartz, lavarock, waterstone, firestone, icestone, holystone, magmacream, netherbrick, futura, tyrian, paper, cloud, carpet, wool, woolen_clay, concrete, road, iron_bars, paneNTM, glowstone, redstone_lamp, torch, lapis, emerald, coal, charcoal, netherite, amethyst, prismarine, dark_prismarine, purpur, quartz, end_rod, chorus_plant, chorus_flower, grass, mycelium, podzol, farmland, clay, gravel, sand, redsand, soul_sand, bedrock, melon, hay_block, bone_block, dried_kelp_block, nether_wart_block, warped_wart_block, shroomlight, sponge, slime, honeycomb_block, honey_block, tnt, note_block, jukebox, mob_spawner, oak_log, spruce_log, birch_log, jungle_log, acacia_log, dark_oak_log, stripped_oak_log, stripped_spruce_log, stripped_birch_log, stripped_jungle_log, stripped_acacia_log, stripped_dark_oak_log, oak_wood, spruce_wood, birch_wood, jungle_wood, acacia_wood, dark_oak_wood, stripped_oak_wood, stripped_spruce_wood, stripped_birch_wood, stripped_jungle_wood, stripped_acacia_wood, stripped_dark_oak_wood, oak_leaves, spruce_leaves, birch_leaves, jungle_leaves, acacia_leaves, dark_oak_leaves, oak_sapling, spruce_sapling, birch_sapling, jungle_sapling, acacia_sapling, dark_oak_sapling, dead_bush, fern, large_fern, tall_grass, grass_block, dirt_path, rooted_dirt, mud, muddy_mangrove_roots, mangrove_roots, moss_block, moss_carpet, bamboo, bamboo_sapling, sugar_cane, cactus, kelp, seagrass, tall_seagrass, sea_pickle, coral, coral_fan, coral_block, brain_coral, bubble_coral, fire_coral, horn_coral, tube_coral, dead_brain_coral, dead_bubble_coral, dead_fire_coral, dead_horn_coral, dead_tube_coral, dead_brain_coral_fan, dead_bubble_coral_fan, dead_fire_coral_fan, dead_horn_coral_fan, dead_tube_coral_fan, brain_coral_block, bubble_coral_block, fire_coral_block, horn_coral_block, tube_coral_block, dead_brain_coral_block, dead_bubble_coral_block, dead_fire_coral_block, dead_horn_coral_block, dead_tube_coral_block, snow_block, snow, packed_ice, blue_ice, crying_obsidian, soul_soil, blackstone, gilded_blackstone, chiseled_polished_blackstone, cracked_polished_blackstone_bricks, polished_blackstone_bricks, polished_blackstone, end_portal_frame, dragon_egg, shulker_box, white_shulker_box, orange_shulker_box, magenta_shulker_box, light_blue_shulker_box, yellow_shulker_box, lime_shulker_box, pink_shulker_box, gray_shulker_box, light_gray_shulker_box, cyan_shulker_box, purple_shulker_box, blue_shulker_box, brown_shulker_box, green_shulker_box, red_shulker_box, black_shulker_box, white_glazed_terracotta, orange_glazed_terracotta, magenta_glazed_terracotta, light_blue_glazed_terracotta, yellow_glazed_terracotta, lime_glazed_terracotta, pink_glazed_terracotta, gray_glazed_terracotta, light_gray_glazed_terracotta, cyan_glazed_terracotta, purple_glazed_terracotta, blue_glazed_terracotta, brown_glazed_terracotta, green_glazed_terracotta, red_glazed_terracotta, black_glazed_terracotta, terracotta, white_concrete, orange_concrete, magenta_concrete, light_blue_concrete, yellow_concrete, lime_concrete, pink_concrete, gray_concrete, light_gray_concrete, cyan_concrete, purple_concrete, blue_concrete, brown_concrete, green_concrete, red_concrete, black_concrete, white_concrete_powder, orange_concrete_powder, magenta_concrete_powder, light_blue_concrete_powder, yellow_concrete_powder, lime_concrete_powder, pink_concrete_powder, gray_concrete_powder, light_gray_concrete_powder, cyan_concrete_powder, purple_concrete_powder, blue_concrete_powder, brown_concrete_powder, green_concrete_powder, red_concrete_powder, black_concrete_powder, white_wool, orange_wool, magenta_wool, light_blue_wool, yellow_wool, lime_wool, pink_wool, gray_wool, light_gray_wool, cyan_wool, purple_wool, blue_wool, brown_wool, green_wool, red_wool, black_wool, white_carpet, orange_carpet, magenta_carpet, light_blue_carpet, yellow_carpet, lime_carpet, pink_carpet, gray_carpet, light_gray_carpet, cyan_carpet, purple_carpet, blue_carpet, brown_carpet, green_carpet, red_carpet, black_carpet, white_stained_glass, orange_stained_glass, magenta_stained_glass, light_blue_stained_glass, yellow_stained_glass, lime_stained_glass, pink_stained_glass, gray_stained_glass, light_gray_stained_glass, cyan_stained_glass, purple_stained_glass, blue_stained_glass, brown_stained_glass, green_stained_glass, red_stained_glass, black_stained_glass, white_stained_glass_pane, orange_stained_glass_pane, magenta_stained_glass_pane, light_blue_stained_glass_pane, yellow_stained_glass_pane, lime_stained_glass_pane, pink_stained_glass_pane, gray_stained_glass_pane, light_gray_stained_glass_pane, cyan_stained_glass_pane, purple_stained_glass_pane, blue_stained_glass_pane, brown_stained_glass_pane, green_stained_glass_pane, red_stained_glass_pane, black_stained_glass_pane, torch, soul_torch, redstone_torch, lantern, soul_lantern, end_rod, redstone_lamp, glowstone, sea_lantern, shroomlight, ochre_froglight, verdant_froglight, pearlescent_froglight, respawn_anchor, lodestone, bee_nest, beehive, suspicious_sand, suspicious_gravel, calibrated_sculk_sensor, sculk_sensor, sculk_shrieker, sculk_catalyst, sculk_vein, sculk, pointed_dripstone, dripstone_block, copper_block, exposed_copper, weathered_copper, oxidized_copper, cut_copper, exposed_cut_copper, weathered_cut_copper, oxidized_cut_copper, cut_copper_stairs, exposed_cut_copper_stairs, weathered_cut_copper_stairs, oxidized_cut_copper_stairs, cut_copper_slab, exposed_cut_copper_slab, weathered_cut_copper_slab, oxidized_cut_copper_slab, waxed_copper_block, waxed_exposed_copper, waxed_weathered_copper, waxed_oxidized_copper, waxed_cut_copper, waxed_exposed_cut_copper, waxed_weathered_cut_copper, waxed_oxidized_cut_copper, waxed_cut_copper_stairs, waxed_exposed_cut_copper_stairs, waxed_weathered_cut_copper_stairs, waxed_oxidized_cut_copper_stairs, waxed_cut_copper_slab, waxed_exposed_cut_copper_slab, waxed_weathered_cut_copper_slab, waxed_oxidized_cut_copper_slab, raw_iron_block, raw_copper_block, raw_gold_block, coal_block, amethyst_block, budding_amethyst, small_amethyst_bud, medium_amethyst_bud, large_amethyst_bud, amethyst_cluster, stone, smooth_stone, cobblestone, mossy_cobblestone, stone_bricks, mossy_stone_bricks, cracked_stone_bricks, chiseled_stone_bricks, granite, polished_granite, diorite, polished_diorite, andesite, polished_andesite, deepslate, cobbled_deepslate, polished_deepslate, deepslate_bricks, cracked_deepslate_bricks, deepslate_tiles, cracked_deepslate_tiles, chiseled_deepslate, reinforced_deepslate, tuff, calcite, sandstone, cut_sandstone, chiseled_sandstone, smooth_sandstone, red_sandstone, cut_red_sandstone, chiseled_red_sandstone, smooth_red_sandstone, prismarine, prismarine_bricks, dark_prismarine, netherrack, nether_bricks, cracked_nether_bricks, chiseled_nether_bricks, red_nether_bricks, basalt, smooth_basalt, polished_basalt, blackstone, gilded_blackstone, chiseled_polished_blackstone, cracked_polished_blackstone_bricks, polished_blackstone_bricks, polished_blackstone, end_stone, end_stone_bricks, purpur_block, purpur_pillar, coal_ore, deepslate_coal_ore, iron_ore, deepslate_iron_ore, copper_ore, deepslate_copper_ore, gold_ore, deepslate_gold_ore, redstone_ore, deepslate_redstone_ore, emerald_ore, deepslate_emerald_ore, lapis_ore, deepslate_lapis_ore, diamond_ore, deepslate_diamond_ore, nether_gold_ore, nether_quartz_ore, ancient_debris, budding_amethyst, small_amethyst_bud, medium_amethyst_bud, large_amethyst_bud, amethyst_cluster, moss_block, moss_carpet, spore_blossom, azalea, flowering_azalea, big_dripleaf, small_dripleaf, hanging_roots, rooted_dirt, mud, muddy_mangrove_roots, mangrove_roots, mangrove_log, mangrove_wood, stripped_mangrove_log, stripped_mangrove_wood, mangrove_planks, mangrove_leaves, mangrove_propagule, bamboo_block, stripped_bamboo_block, bamboo_planks, bamboo_mosaic, chiseled_bookshelf, decorated_pot, suspicious_sand, suspicious_gravel, torchflower, torchflower_crop, pitcher_plant, pitcher_crop, pink_petals, frogspawn, ochre_froglight, verdant_froglight, pearlescent_froglight, mangrove_propagule) – wszystkie te warianty wymagaja recznego review wizualnego i porownania tekstur z Rechiseled/Chipped. Pelna lista w output/chisel_step1/chisel_step1_inventory.json.
- **Bloki zalezne od innych modow** (np. ae_certus_quartz, aluminum, copper, thaumium, itp.) – jesli mod zrodlowy nie istnieje w 1.18.2, fallback do najblizszego materialu vanilla lub rechiseled.

---

## 6. Handoff – decyzje mapowania

1. ✅ Priorytet: rodziny kamienne (sandstone, stonebrick, cobblestone, marble, limestone, andesite, basalt, diorite, granite, endstone, obsidian) -> rechiseled:*_*. Pewnosc medium-high.
2. ✅ Metale (gold, iron, diamond, redstone, lapis, emerald, coal) -> rechiseled:*_*. Pewnosc medium.
3. ✅ Drewno/glass/bookshelf -> rechiseled:*_*. Pewnosc medium.
4. ⚠️ Factory/Technical/Laboratory -> chipped:* jako pierwszy wybor; brak dopasowania -> minecraft:iron_block. Pewnosc low.
5. ⚠️ Dyed glass panes -> minecraft:*_stained_glass_pane (tylko kolor, brak wariantu). Pewnosc low.
6. ⚠️ Pumpkin/Leaves/Cloud/Paper -> fallback dekoracyjny (najblizszy kolor/material). Pewnosc low.
7. ❌ AutoChisel, Present (z TE), Beacon -> pozostaja w workflow TE.
8. 📋 Wymagany audyt: block_remap_audit.jsonl z liczba dopasowan per rodzina i lista najczestszych fallbackow.
