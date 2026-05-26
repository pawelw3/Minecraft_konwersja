# Chisel - Zadanie 1: analiza blokow i TE

## Podsumowanie

- Chisel 1.7.10: 223 rodzin/feature potwierdzonych z klas JAR lub source.
- Chisel 1.7.10: 38 dodatkowych rodzin texture-only do uzycia przy dopasowaniu wizualnym.
- Chisel 1.7.10: 3 tile entity istotne dla konwersji.
- Rechiseled 1.18.2: 42 rodzin blokow z generated resources.
- Rechiseled 1.18.2: 0 block entities wykrytych w kodzie.
- Pelna, maszynowa lista jest w `output/chisel_step1/chisel_step1_inventory.json`.

## Zrodla internetowe

- CurseForge Chisel: https://www.curseforge.com/minecraft/mc-mods/chisel/chisel - potwierdza charakter moda jako zestawu dekoracyjnych wariantow blokow i narzedzia chisel.
- FTB Wiki Chisel: https://ftbwiki.org/Chisel - opisuje narzedzie Chisel i Auto Chisel jako sposob zamiany blokow na warianty.
- CurseForge Rechiseled: https://www.curseforge.com/minecraft/mc-mods/rechiseled - opisuje Rechiseled jako mod do zamiany blokow na warianty dekoracyjne z connected textures.
- GitHub Rechiseled: https://github.com/SuperMartijn642/Rechiseled - kod zrodlowy docelowego moda uzywany lokalnie w `mod_src/118/.../Rechiseled`.

## 1.7.10 - Bloki

Chisel 2.9.5.11 jest przede wszystkim modem dekoracyjnym. Wiekszosc danych w swiecie to blok numeryczny + metadata, bez TileEntity, wiec pozniejszy konwerter musi skanowac palette/numeric ID, nie tylko TE. `registry_hint` ponizej jest nazwa rodziny/pakietu wariantow, a dokladny numeric ID/meta trzeba pobrac z mapy albo testowego swiata. Tabela pokazuje najwieksze rodziny, a JSON zawiera takze flage zrodla (`jar_class`, `feature_enum`, `source`, `jar_textures`).

| Family | Registry hint | Variants | Texture examples |
|---|---:|---:|---|
| `glasspanedyed` | `chisel:glasspanedyed` | 192 | assets/chisel/textures/blocks/glasspanedyed/black-bubble-side.png, assets/chisel/textures/blocks/glasspanedyed/black-bubble-top.png |
| `glassdyed` | `chisel:glassdyed` | 80 | assets/chisel/textures/blocks/glassdyed/black-bubble.png, assets/chisel/textures/blocks/glassdyed/black-forestry.png |
| `sandstone` | `chisel:sandstone` | 62 | assets/chisel/textures/blocks/sandstone/a0-sandstonepreview-boxcreeper-bottom.png, assets/chisel/textures/blocks/sandstone/a0-sandstonepreview-boxcreeper-side.png |
| `technical` | `chisel:technical` | 58 | assets/chisel/textures/blocks/technical/cables-ctm.png, assets/chisel/textures/blocks/technical/cables.png |
| `gold` | `chisel:gold` | 42 | assets/chisel/textures/blocks/gold/terrain-gold-brick-bottom.png, assets/chisel/textures/blocks/gold/terrain-gold-brick-side.png |
| `present` | `chisel:present` | 41 | assets/chisel/textures/blocks/present/old/giftboxBlack.png, assets/chisel/textures/blocks/present/old/giftboxBlue.png |
| `iron` | `chisel:iron` | 39 | assets/chisel/textures/blocks/iron/terrain-iron-brick-bottom.png, assets/chisel/textures/blocks/iron/terrain-iron-brick-side.png |
| `pumpkin` | `chisel:pumpkin` | 38 | assets/chisel/textures/blocks/pumpkin/pumpkin_face_10_off.png, assets/chisel/textures/blocks/pumpkin/pumpkin_face_10_on.png |
| `marblepillarold` | `chisel:marblepillarold` | 33 | assets/chisel/textures/blocks/marblepillarold/1/a1-stoneornamental-marblebrick-top.png, assets/chisel/textures/blocks/marblepillarold/1/a1-stoneornamental-marblegreek-side.png |
| `marblepillar` | `chisel:marblepillar` | 32 | assets/chisel/textures/blocks/marblepillar/carved-side.png, assets/chisel/textures/blocks/marblepillar/carved-top.png |
| `sandstone_scribbles` | `chisel:sandstone_scribbles` | 32 | assets/chisel/textures/blocks/sandstone-scribbles/scribbles-0-side.png, assets/chisel/textures/blocks/sandstone-scribbles/scribbles-0-top.png |
| `arcane` | `chisel:arcane` | 31 | assets/chisel/textures/blocks/arcane/ArcaneBorder-ctm.png, assets/chisel/textures/blocks/arcane/ArcaneBorder.png |
| `fantasy` | `chisel:fantasy` | 31 | assets/chisel/textures/blocks/fantasy/block-ctm.png, assets/chisel/textures/blocks/fantasy/block.png |
| `temple` | `chisel:temple` | 28 | assets/chisel/textures/blocks/temple/0/a1-stoneornamental-marblebrick-top.png, assets/chisel/textures/blocks/temple/0/default.png |
| `ironpane` | `chisel:ironpane` | 27 | assets/chisel/textures/blocks/ironpane/a1-ironbars-ironclassic.png, assets/chisel/textures/blocks/ironpane/a1-ironbars-ironclassicnew.png |
| `voidstone` | `chisel:voidstone` | 27 | assets/chisel/textures/blocks/voidstone/animated/bevel-ctm.png, assets/chisel/textures/blocks/voidstone/animated/bevel.png |
| `snakestone` | `chisel:snakestone` | 25 | assets/chisel/textures/blocks/snakestone/obsidian/bot-side.png, assets/chisel/textures/blocks/snakestone/obsidian/bot-tip.png |
| `endstone` | `chisel:endstone` | 24 | assets/chisel/textures/blocks/endstone/CheckeredTile.png, assets/chisel/textures/blocks/endstone/EnderFrame-0-ctm.png |
| `factory` | `chisel:factory` | 24 | assets/chisel/textures/blocks/factory/circuit-ctm.png, assets/chisel/textures/blocks/factory/circuit.png |
| `grimstone` | `chisel:grimstone` | 24 | assets/chisel/textures/blocks/grimstone/blocks-rough.png, assets/chisel/textures/blocks/grimstone/blocks.png |
| `laboratory` | `chisel:laboratory` | 24 | assets/chisel/textures/blocks/laboratory/checkertile.png, assets/chisel/textures/blocks/laboratory/clearscreen-ctm.png |
| `holystone` | `chisel:holystone` | 23 | assets/chisel/textures/blocks/holystone/blocks-rough.png, assets/chisel/textures/blocks/holystone/blocks.png |
| `obsidian` | `chisel:obsidian` | 21 | assets/chisel/textures/blocks/obsidian/blocks.png, assets/chisel/textures/blocks/obsidian/chiseled-side.png |
| `templemossy` | `chisel:templemossy` | 21 | assets/chisel/textures/blocks/templemossy/bricks-disarray.png, assets/chisel/textures/blocks/templemossy/bricks-large.png |
| `dirt` | `chisel:dirt` | 20 | assets/chisel/textures/blocks/dirt/bricks+dirt2-ctmv.png, assets/chisel/textures/blocks/dirt/bricks+dirt2-top.png |
| `ice` | `chisel:ice` | 20 | assets/chisel/textures/blocks/ice/a1-ice-light.png, assets/chisel/textures/blocks/ice/a1-netherbrick-ice.png |
| `marble` | `chisel:marble` | 20 | assets/chisel/textures/blocks/marble.png, assets/chisel/textures/blocks/marble/32/a1-stoneornamental-marblebrick-side.png |
| `redstone` | `chisel:redstone` | 19 | assets/chisel/textures/blocks/redstone/a1-blockredstone-redstonechunk.png, assets/chisel/textures/blocks/redstone/a1-blockredstone-redstonezelda.png |
| `bookshelf` | `chisel:bookshelf` | 18 | assets/chisel/textures/blocks/bookshelf/abandoned-ctmh.png, assets/chisel/textures/blocks/bookshelf/abandoned-top.png |
| `diamond` | `chisel:diamond` | 18 | assets/chisel/textures/blocks/diamond/terrain-diamond-bismuth.png, assets/chisel/textures/blocks/diamond/terrain-diamond-cells-v4.png |

## 1.7.10 - Tile Entities

### TileEntityAutoChisel
- **Typ:** TileEntity
- **Klasa Java:** `team.chisel.block.tileentity.TileEntityAutoChisel`
- **Plik:** `modpack_1710/Chisel-2.9.5.11.jar`
- **Opis:** Automatyczna maszyna do chiselowania; ma GUI, inventory i w starszych wersjach sloty upgrade. Registry string wymaga potwierdzenia skanem TE z mapy/JAR dekompilacja.
- **Dowod z kodu:** klasa jest obecna w JAR `Chisel-2.9.5.11.jar`; lista zostala wyciagnieta z `jar tf`/`javap`. Dokladny string rejestracji TE trzeba potwierdzic skanem mapy albo dekompilacja bytecode przy Zadaniu 3.

### TileEntityCarvableBeacon
- **Typ:** TileEntity
- **Klasa Java:** `team.chisel.block.tileentity.TileEntityCarvableBeacon`
- **Plik:** `modpack_1710/Chisel-2.9.5.11.jar`
- **Opis:** Tile entity wariantu beacon; istotna glownie wizualnie/renderingowo. Registry string wymaga potwierdzenia skanem TE z mapy/JAR dekompilacja.
- **Dowod z kodu:** klasa jest obecna w JAR `Chisel-2.9.5.11.jar`; lista zostala wyciagnieta z `jar tf`/`javap`. Dokladny string rejestracji TE trzeba potwierdzic skanem mapy albo dekompilacja bytecode przy Zadaniu 3.

### TileEntityPresent
- **Typ:** TileEntity
- **Klasa Java:** `team.chisel.block.tileentity.TileEntityPresent`
- **Plik:** `modpack_1710/Chisel-2.9.5.11.jar`
- **Opis:** Tile entity prezentu; moze przechowywac dane wariantu/zawartosci prezentu. Registry string wymaga potwierdzenia skanem TE z mapy/JAR dekompilacja.
- **Dowod z kodu:** klasa jest obecna w JAR `Chisel-2.9.5.11.jar`; lista zostala wyciagnieta z `jar tf`/`javap`. Dokladny string rejestracji TE trzeba potwierdzic skanem mapy albo dekompilacja bytecode przy Zadaniu 3.

## 1.18.2 - Bloki

Rechiseled generuje warianty jako osobne blockstates, zwykle z postaciami normalnymi, connecting, slab i stairs. To jest dobry docelowy zamiennik dla rodzin kamiennych/drewnianych/metali Chisela, ale nie kazda tekstura ma odpowiednik 1:1.

| Family | Registry hint | Variants | Texture examples |
|---|---:|---:|---|
| `stone` | `rechiseled:stone_*` | 114 | mod_src/118/actual_src/1.18.2/Rechiseled/repo/src/main/resources/assets/rechiseled/textures/block/stone_big_tiles.png, mod_src/118/actual_src/1.18.2/Rechiseled/repo/src/main/resources/assets/rechiseled/textures/block/stone_bordered.png |
| `acacia` | `rechiseled:acacia_*` | 111 |  |
| `birch` | `rechiseled:birch_*` | 111 |  |
| `crimson` | `rechiseled:crimson_*` | 111 |  |
| `dark_oak` | `rechiseled:dark_oak_*` | 111 |  |
| `jungle` | `rechiseled:jungle_*` | 111 |  |
| `oak` | `rechiseled:oak_*` | 111 | mod_src/118/actual_src/1.18.2/Rechiseled/repo/src/main/resources/assets/rechiseled/textures/block/oak_planks_beams.png, mod_src/118/actual_src/1.18.2/Rechiseled/repo/src/main/resources/assets/rechiseled/textures/block/oak_planks_brick_pattern.png |
| `spruce` | `rechiseled:spruce_*` | 111 |  |
| `warped` | `rechiseled:warped_*` | 111 |  |
| `prismarine_bricks` | `rechiseled:prismarine_bricks_*` | 108 | mod_src/118/actual_src/1.18.2/Rechiseled/repo/src/main/resources/assets/rechiseled/textures/block/prismarine_bricks_beams.png, mod_src/118/actual_src/1.18.2/Rechiseled/repo/src/main/resources/assets/rechiseled/textures/block/prismarine_bricks_brick_pattern.png |
| `cobblestone` | `rechiseled:cobblestone_*` | 105 | mod_src/118/actual_src/1.18.2/Rechiseled/repo/src/main/resources/assets/rechiseled/textures/block/cobblestone_beams.png, mod_src/118/actual_src/1.18.2/Rechiseled/repo/src/main/resources/assets/rechiseled/textures/block/cobblestone_brick_pattern.png |
| `purpur` | `rechiseled:purpur_*` | 105 | mod_src/118/actual_src/1.18.2/Rechiseled/repo/src/main/resources/assets/rechiseled/textures/block/purpur_brick_pattern.png, mod_src/118/actual_src/1.18.2/Rechiseled/repo/src/main/resources/assets/rechiseled/textures/block/purpur_brick_paving.png |
| `lapis` | `rechiseled:lapis_*` | 93 | mod_src/118/actual_src/1.18.2/Rechiseled/repo/src/main/resources/assets/rechiseled/textures/block/lapis_block_bordered.png, mod_src/118/actual_src/1.18.2/Rechiseled/repo/src/main/resources/assets/rechiseled/textures/block/lapis_block_chiseled.png |
| `end` | `rechiseled:end_*` | 90 | mod_src/118/actual_src/1.18.2/Rechiseled/repo/src/main/resources/assets/rechiseled/textures/block/end_stone_blobs.png, mod_src/118/actual_src/1.18.2/Rechiseled/repo/src/main/resources/assets/rechiseled/textures/block/end_stone_brick_pattern.png |
| `obsidian` | `rechiseled:obsidian_*` | 87 | mod_src/118/actual_src/1.18.2/Rechiseled/repo/src/main/resources/assets/rechiseled/textures/block/obsidian_bordered.png, mod_src/118/actual_src/1.18.2/Rechiseled/repo/src/main/resources/assets/rechiseled/textures/block/obsidian_brick_pattern.png |
| `cobbled` | `rechiseled:cobbled_*` | 84 | mod_src/118/actual_src/1.18.2/Rechiseled/repo/src/main/resources/assets/rechiseled/textures/block/cobbled_deepslate_beams.png, mod_src/118/actual_src/1.18.2/Rechiseled/repo/src/main/resources/assets/rechiseled/textures/block/cobbled_deepslate_brick_pattern.png |
| `quartz` | `rechiseled:quartz_*` | 84 | mod_src/118/actual_src/1.18.2/Rechiseled/repo/src/main/resources/assets/rechiseled/textures/block/quartz_block_bordered.png, mod_src/118/actual_src/1.18.2/Rechiseled/repo/src/main/resources/assets/rechiseled/textures/block/quartz_block_brick_paving.png |
| `dirt` | `rechiseled:dirt_*` | 81 | mod_src/118/actual_src/1.18.2/Rechiseled/repo/src/main/resources/assets/rechiseled/textures/block/dirt_blobs.png, mod_src/118/actual_src/1.18.2/Rechiseled/repo/src/main/resources/assets/rechiseled/textures/block/dirt_bricks.png |
| `redstone` | `rechiseled:redstone_*` | 81 | mod_src/118/actual_src/1.18.2/Rechiseled/repo/src/main/resources/assets/rechiseled/textures/block/redstone_block_bordered.png, mod_src/118/actual_src/1.18.2/Rechiseled/repo/src/main/resources/assets/rechiseled/textures/block/redstone_block_brick_bordered.png |
| `iron` | `rechiseled:iron_*` | 78 | mod_src/118/actual_src/1.18.2/Rechiseled/repo/src/main/resources/assets/rechiseled/textures/block/iron_block_bordered.png, mod_src/118/actual_src/1.18.2/Rechiseled/repo/src/main/resources/assets/rechiseled/textures/block/iron_block_chiseled.png |
| `emerald` | `rechiseled:emerald_*` | 75 | mod_src/118/actual_src/1.18.2/Rechiseled/repo/src/main/resources/assets/rechiseled/textures/block/emerald_block_bordered_crosses.png, mod_src/118/actual_src/1.18.2/Rechiseled/repo/src/main/resources/assets/rechiseled/textures/block/emerald_block_bordered_plating.png |
| `dark_prismarine` | `rechiseled:dark_prismarine_*` | 72 | mod_src/118/actual_src/1.18.2/Rechiseled/repo/src/main/resources/assets/rechiseled/textures/block/dark_prismarine_beams.png, mod_src/118/actual_src/1.18.2/Rechiseled/repo/src/main/resources/assets/rechiseled/textures/block/dark_prismarine_brick_paving.png |
| `nether` | `rechiseled:nether_*` | 72 | mod_src/118/actual_src/1.18.2/Rechiseled/repo/src/main/resources/assets/rechiseled/textures/block/nether_bricks_beams.png, mod_src/118/actual_src/1.18.2/Rechiseled/repo/src/main/resources/assets/rechiseled/textures/block/nether_bricks_brick_pattern.png |
| `red_nether` | `rechiseled:red_nether_*` | 72 | mod_src/118/actual_src/1.18.2/Rechiseled/repo/src/main/resources/assets/rechiseled/textures/block/red_nether_bricks_beams.png, mod_src/118/actual_src/1.18.2/Rechiseled/repo/src/main/resources/assets/rechiseled/textures/block/red_nether_bricks_brick_pattern.png |
| `netherite` | `rechiseled:netherite_*` | 66 | mod_src/118/actual_src/1.18.2/Rechiseled/repo/src/main/resources/assets/rechiseled/textures/block/netherite_block_beams.png, mod_src/118/actual_src/1.18.2/Rechiseled/repo/src/main/resources/assets/rechiseled/textures/block/netherite_block_bricks.png |
| `amethyst` | `rechiseled:amethyst_*` | 63 | mod_src/118/actual_src/1.18.2/Rechiseled/repo/src/main/resources/assets/rechiseled/textures/block/amethyst_block_beams.png, mod_src/118/actual_src/1.18.2/Rechiseled/repo/src/main/resources/assets/rechiseled/textures/block/amethyst_block_bordered_diagonal_tiles.png |
| `andesite` | `rechiseled:andesite_*` | 63 | mod_src/118/actual_src/1.18.2/Rechiseled/repo/src/main/resources/assets/rechiseled/textures/block/andesite_brick_pattern.png, mod_src/118/actual_src/1.18.2/Rechiseled/repo/src/main/resources/assets/rechiseled/textures/block/andesite_brick_paving.png |
| `coal` | `rechiseled:coal_*` | 63 | mod_src/118/actual_src/1.18.2/Rechiseled/repo/src/main/resources/assets/rechiseled/textures/block/coal_block_carved.png, mod_src/118/actual_src/1.18.2/Rechiseled/repo/src/main/resources/assets/rechiseled/textures/block/coal_block_chiseled.png |
| `diorite` | `rechiseled:diorite_*` | 63 | mod_src/118/actual_src/1.18.2/Rechiseled/repo/src/main/resources/assets/rechiseled/textures/block/diorite_brick_pattern.png, mod_src/118/actual_src/1.18.2/Rechiseled/repo/src/main/resources/assets/rechiseled/textures/block/diorite_brick_paving.png |
| `gold` | `rechiseled:gold_*` | 63 | mod_src/118/actual_src/1.18.2/Rechiseled/repo/src/main/resources/assets/rechiseled/textures/block/gold_block_beams.png, mod_src/118/actual_src/1.18.2/Rechiseled/repo/src/main/resources/assets/rechiseled/textures/block/gold_block_bordered.png |

## 1.18.2 - Block Entities

Nie wykryto wlasnych block entities Rechiseled w glownym kodzie. Mod opiera konwersje na itemie chisel, GUI/menu i zwyklych blokach/blockstates.


## Porownanie 1.7.10 vs 1.18.2

- Chisel 1.7.10: duzo wariantow jako rodziny blokow z metadata; TE z JAR to Auto Chisel, Present i Carvable Beacon.
- Rechiseled 1.18.2: warianty sa osobnymi registry names i blockstates, czesto maja wersje connecting/slab/stairs.
- Dla konwersji mapy najwazniejszy bedzie wizualny matching: kolor/material rodziny, typ wzoru (bricks, tiles, panel, pillar, ornate, cracked), a dopiero potem nazwa.
- Kandydaci ponizej sa tylko punktem startowym. Finalne mapowanie powinno porownywac tekstury z JAR 1.7.10 do tekstur Rechiseled/Chipped, najlepiej przez histogram koloru + tokeny nazwy.

| Chisel family | Najlepszy kandydat 1.18.2 | Score | Wspolne tokeny |
|---|---|---:|---|
| `ae_certus_quartz` | `rechiseled:quartz_*` | 10 | quartz |
| `ae_sky_stone` | `rechiseled:end_*` | 10 | stone |
| `aluminum` | brak szybkiego kandydata | 0 |  |
| `aluminumblock` | brak szybkiego kandydata | 0 |  |
| `aluminumstairs` | brak szybkiego kandydata | 0 |  |
| `amber` | brak szybkiego kandydata | 0 |  |
| `ancient_stone` | `rechiseled:end_*` | 10 | stone |
| `andesite` | `rechiseled:andesite_*` | 70 | andesite |
| `animations` | brak szybkiego kandydata | 0 |  |
| `antiblock` | `rechiseled:blue_ice_*` | 10 | blue |
| `arcane` | `rechiseled:end_*` | 10 | stone |
| `arcane_stone` | `rechiseled:end_*` | 10 | stone |
| `auto_chisel` | brak szybkiego kandydata | 0 |  |
| `auto_chisel_upgrades` | brak szybkiego kandydata | 0 |  |
| `autochisel` | brak szybkiego kandydata | 0 |  |
| `ball_of_moss` | brak szybkiego kandydata | 0 |  |
| `basalt` | `rechiseled:basalt_*` | 70 | basalt |
| `beacon` | brak szybkiego kandydata | 0 |  |
| `birdstone` | brak szybkiego kandydata | 0 |  |
| `block_charcoal` | brak szybkiego kandydata | 0 |  |
| `block_coal` | `rechiseled:coal_*` | 10 | coal |
| `block_coal_coke` | `rechiseled:coal_*` | 10 | coal |
| `blockbronze` | brak szybkiego kandydata | 0 |  |
| `blockcobalt` | brak szybkiego kandydata | 0 |  |
| `blockcopper` | brak szybkiego kandydata | 0 |  |

## Tabela registry names / prefiksy

| Element | Registry string | Ma prefiks? | Uwagi |
|---|---|---|---|
| Rodziny Chisel 1.7.10 | `chisel:<family>` / numeric ID + metadata | TAK dla modid, ale mapa uzywa ID/meta | Szczegoly w JSON; wymagany skan dynamicznych ID w Zadaniu 3/4 |
| Auto Chisel | `TileEntityAutoChisel` / prawdopodobnie blok `autoChisel` | NIEPEWNE | Wymaga potwierdzenia na mapie przez skan TE |
| Present | `TileEntityPresent` | NIEPEWNE | Wymaga potwierdzenia, czy wystepuje na mapie |
| Carvable Beacon | `TileEntityCarvableBeacon` | NIEPEWNE | Wymaga potwierdzenia, czy wystepuje na mapie |
| Rechiseled blocks | `rechiseled:<blockstate_name>` | TAK | Osobne blockstates dla wariantow |
| Rechiseled block entities | brak wykrytych | - | Docelowo zwykle nie trzeba przenosic BE |

## Kryteria wizualne do Zadania 3

1. Najpierw dopasowuj rodzine materialu: stone do stone, marble/limestone do jasnych kamieni, factory/technical do industrialnych wzorow.
2. Potem dopasowuj pattern: bricks, small tiles, large tiles, panel, pillar, ornate, cracked, road, hazard.
3. Przy remisie wybieraj podobniejsza srednia jasnosc i nasycenie tekstury, nie nazwe.
4. Gdy Rechiseled nie ma bliskiego wariantu, sprawdz Chipped jako drugi target.
