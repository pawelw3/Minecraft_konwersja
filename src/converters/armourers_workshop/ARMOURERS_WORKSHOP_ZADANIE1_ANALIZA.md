# Armourer's Workshop - Zadanie 1: analiza blokow, TE i modeli

## Podsumowanie

- 1.7.10: wykryto 19 blokow z `ModBlocks.java`.
- 1.7.10: wykryto 13 tile entities rejestrowanych jako `te.<id>`.
- Globalna biblioteka serwera: 146 plikow `.armour`, 2072491 bajtow, 68003 voxel-cubes.
- Parser `.armour`: statusy {'ok': 146}.
- 1.18.2: lokalne artefakty Armourer's Workshop: present.
- Pelna lista maszynowa: `output/armourers_workshop_step1/armourers_workshop_step1_inventory.json`.

## Zrodla internetowe i lokalne

- CurseForge Armourer's Workshop: https://www.curseforge.com/minecraft/mc-mods/armourers-workshop - dokumentacja projektu wskazuje port 1.18.2 3.2.7-beta.
- Minecraft Forum Armourer's Workshop: http://www.minecraftforum.net/forums/mapping-and-modding/minecraft-mods/wip-mods/2309193-wip-alpha-armourers-workshop-weapon-armour-skins - link jest wpisany w `global-skin-database/readme.txt` jako opis globalnej bazy skinow.
- Lokalny source 1.7.10: `mod_src/1710/actual_src/1.7.10/ArmourersWorkshop/repo`.
- Lokalna dokumentacja projektu: `docs/LISTA_KONWERSJI_MODOW.md` i `docs/ANALIZA_MODOW_SZCZEGOLOWA.md` potwierdzaja, ze celem jest Armourer's Workshop 3.2.7-beta, a ryzykiem jest format skinow/modeli.

## 1.7.10 - Bloki

| Field | Block registry | Klasa | TE | Opis |
|---|---|---|---|---|
| `armourLibrary` | `armourersworkshop:block.armourLibrary` | `BlockSkinLibrary` | `te.armourLibrary` | Biblioteka zapisu i odczytu plikow .armour z katalogu serwera/klienta. |
| `armourerBrain` | `armourersworkshop:block.armourerBrain` | `BlockArmourer` | `te.armourerBrain` | Glowny blok budowy skinow; ustawia obszar roboczy i zbiera Equipment Cubes w model. |
| `boundingBox` | `armourersworkshop:block.awBoundingBox6` | `BlockBoundingBox` | `te.awBoundingBox6` | Techniczny blok granicy/modelu uzywany przy skinach blokowych i multiblokach. |
| `colourMixer` | `armourersworkshop:block.colourMixer` | `BlockColourMixer` | `te.colourMixer` | Stol do mieszania kolorow dla narzedzi malarskich. |
| `colourable` | `armourersworkshop:block.colourable` | `BlockColourable` | `te.colourable` | Podstawowy malowalny Equipment Cube uzywany jako voxel modelu. |
| `colourableGlass` | `armourersworkshop:block.colourableGlass` | `BlockColourableGlass` | `-` | Przezroczysty malowalny Equipment Cube. |
| `colourableGlassGlowing` | `armourersworkshop:block.colourableGlassGlowing` | `BlockColourableGlass` | `-` | Przezroczysty malowalny Equipment Cube ze swieceniem. |
| `colourableGlowing` | `armourersworkshop:block.colourableGlowing` | `BlockColourable` | `-` | Malowalny Equipment Cube z efektem swiecenia. |
| `doll` | `armourersworkshop:block.doll` | `BlockDoll` | `-` | Maly wariant manekina. |
| `dyeTable` | `armourersworkshop:block.dyeTable` | `BlockDyeTable` | `te.dyeTable` | Stol do farbowania/edycji kolorow skinow. |
| `globalSkinLibrary` | `armourersworkshop:block.globalSkinLibrary` | `BlockGlobalSkinLibrary` | `te.globalSkinLibrary` | Blok dostepu do globalnej biblioteki skinow; dane modeli sa poza chunkami. |
| `hologramProjector` | `armourersworkshop:block.hologramProjector` | `BlockHologramProjector` | `te.hologramProjector` | Projektor podgladu skinow bez postawienia finalnego modelu. |
| `mannequin` | `armourersworkshop:block.mannequin` | `BlockMannequin` | `te.mannequin` | Manekin pokazujacy skiny/ekwipunek i ustawienia pozy. |
| `miniArmourer` | `armourersworkshop:block.miniArmourer` | `BlockMiniArmourer` | `te.miniArmourer` | Niedokonczony mini wariant Armourera; w 0.48.5 istnieje jako blok/TE, ale nie jest glowna sciezka migracji. |
| `skinnable` | `armourersworkshop:block.skinnable` | `BlockSkinnable` | `te.skinnable` | Blok reprezentujacy zapisany skin blokowy w swiecie. |
| `skinnableChild` | `armourersworkshop:block.skinnableChild` | `BlockSkinnableChild` | `te.skinnableChild` | Blok pomocniczy dla wieloblokowego skina blokowego; linkuje do glownego skinnable. |
| `skinnableChildGlowing` | `armourersworkshop:block.skinnableChildGlowing` | `BlockSkinnableChildGlowing` | `-` | Swiecacy blok pomocniczy wielobloku skinnable. |
| `skinnableGlowing` | `armourersworkshop:block.skinnableGlowing` | `BlockSkinnableGlowing` | `-` | Swiecacy wariant bloku skinnable. |
| `skinningTable` | `armourersworkshop:block.skinningTable` | `BlockSkinningTable` | `te.skinningTable` | Stol nakladania i zdejmowania skinow z itemow. |

Dowod z kodu rejestracji blokow:

```java
armourerBrain = new BlockArmourer();
armourLibrary = new BlockSkinLibrary();
skinnable = new BlockSkinnable();
hologramProjector = new BlockHologramProjector();
```

Plik: `mod_src/1710/actual_src/1.7.10/ArmourersWorkshop/repo/src/main/java/riskyken/armourersWorkshop/common/blocks/ModBlocks.java`.

## 1.7.10 - Tile Entities

| Element | Klasa Java | Registry string | Ma prefiks moda? |
|---|---|---|---|
| `armourLibrary` | `TileEntitySkinLibrary` | `te.armourLibrary` | NIE (`te.` zamiast modid) |
| `armourerBrain` | `TileEntityArmourer` | `te.armourerBrain` | NIE (`te.` zamiast modid) |
| `awBoundingBox6` | `TileEntityBoundingBox` | `te.awBoundingBox6` | NIE (`te.` zamiast modid) |
| `colourMixer` | `TileEntityColourMixer` | `te.colourMixer` | NIE (`te.` zamiast modid) |
| `colourable` | `TileEntityColourable` | `te.colourable` | NIE (`te.` zamiast modid) |
| `dyeTable` | `TileEntityDyeTable` | `te.dyeTable` | NIE (`te.` zamiast modid) |
| `globalSkinLibrary` | `TileEntityGlobalSkinLibrary` | `te.globalSkinLibrary` | NIE (`te.` zamiast modid) |
| `hologramProjector` | `TileEntityHologramProjector` | `te.hologramProjector` | NIE (`te.` zamiast modid) |
| `mannequin` | `TileEntityMannequin` | `te.mannequin` | NIE (`te.` zamiast modid) |
| `miniArmourer` | `TileEntityMiniArmourer` | `te.miniArmourer` | NIE (`te.` zamiast modid) |
| `skinnable` | `TileEntitySkinnable` | `te.skinnable` | NIE (`te.` zamiast modid) |
| `skinnableChild` | `TileEntitySkinnableChild` | `te.skinnableChild` | NIE (`te.` zamiast modid) |
| `skinningTable` | `TileEntitySkinningTable` | `te.skinningTable` | NIE (`te.` zamiast modid) |

Dowod z kodu rejestracji TE:

```java
registerTileEntity(TileEntityArmourer.class, LibBlockNames.ARMOURER_BRAIN);
registerTileEntity(TileEntitySkinnable.class, LibBlockNames.SKINNABLE);
registerTileEntity(TileEntitySkinnableChild.class, LibBlockNames.SKINNABLE_CHILD);
GameRegistry.registerTileEntity(tileEntityClass, "te." + id);
```

To jest krytyczne dla skanu mapy: na mapie nalezy szukac np. `te.skinnable`, `te.skinnableChild`, `te.mannequin`, a nie prefiksu moda.

## Globalne modele 1.7.10 - pliki `.armour`

Modele nie sa tylko w chunkach. AW 0.48.5 zapisuje biblioteke skinow w katalogu serwera, u nas: `pliki_globalne_serwer_1710/armourersWorkshop`. Parser odczytuje wersje pliku, typ skina, properties, liczbe partow, voxel-cubes i markerow bez modyfikowania plikow.

- Kategorie: `{'official': 43, 'private': 36, 'public_root': 67}`
- Typy skinow: `{'armourers:arrow': 1, 'armourers:block': 53, 'armourers:bow': 1, 'armourers:chest': 25, 'armourers:feet': 9, 'armourers:head': 29, 'armourers:legs': 19, 'armourers:outfit': 1, 'armourers:sword': 3, 'armourers:wings': 5}`

| Plik | Typ | Wersja | Cubes | Parts | SHA-256 |
|---|---|---:|---:|---:|---|
| `pliki_globalne_serwer_1710/armourersWorkshop/official/Angel Wings.armour` | `armourers:wings` | 12 | 1156 | 2 | `12112ed8852c0a81...` |
| `pliki_globalne_serwer_1710/armourersWorkshop/official/Arbalest.armour` | `armourers:bow` | 9 | 522 | 3 | `86515efc73a62116...` |
| `pliki_globalne_serwer_1710/armourersWorkshop/official/Arrow.armour` | `armourers:arrow` | 9 | 23 | 1 | `5ee428b2019b8e98...` |
| `pliki_globalne_serwer_1710/armourersWorkshop/official/Barrel.armour` | `armourers:block` | 9 | 934 | 1 | `d822fdc23a9e2eed...` |
| `pliki_globalne_serwer_1710/armourersWorkshop/official/Bat Wings.armour` | `armourers:wings` | 12 | 530 | 2 | `07f91088b6fb25fe...` |
| `pliki_globalne_serwer_1710/armourersWorkshop/official/Butterfly Wings.armour` | `armourers:wings` | 12 | 374 | 2 | `ae0f1c2c4cf7003b...` |
| `pliki_globalne_serwer_1710/armourersWorkshop/official/Chessboard.armour` | `armourers:block` | 9 | 100 | 1 | `932d67a5f6837952...` |
| `pliki_globalne_serwer_1710/armourersWorkshop/official/Dress Shoes.armour` | `armourers:feet` | 11 | 16 | 2 | `db7ff54d2c6e4c65...` |
| `pliki_globalne_serwer_1710/armourersWorkshop/official/Dress Skirt.armour` | `armourers:legs` | 11 | 120 | 1 | `5cc7121c15da7c32...` |
| `pliki_globalne_serwer_1710/armourersWorkshop/official/Dress Top.armour` | `armourers:chest` | 11 | 0 | 0 | `20f96a38f6534abd...` |
| `pliki_globalne_serwer_1710/armourersWorkshop/official/Evil Wings.armour` | `armourers:wings` | 12 | 1202 | 2 | `18663a4ae8fa9881...` |
| `pliki_globalne_serwer_1710/armourersWorkshop/official/Fez.armour` | `armourers:head` | 11 | 12 | 1 | `03007fdad03071b7...` |
| `pliki_globalne_serwer_1710/armourersWorkshop/official/Fox Ears.armour` | `armourers:head` | 11 | 58 | 1 | `be775c368a30433c...` |
| `pliki_globalne_serwer_1710/armourersWorkshop/official/Glass Chair.armour` | `armourers:block` | 11 | 182 | 1 | `bd2cbdc802d3a395...` |
| `pliki_globalne_serwer_1710/armourersWorkshop/official/Glass Table.armour` | `armourers:block` | 11 | 160 | 1 | `ca8e359a45491ebe...` |
| `pliki_globalne_serwer_1710/armourersWorkshop/official/Halo.armour` | `armourers:head` | 11 | 24 | 1 | `bd72433fe7ff1fe8...` |
| `pliki_globalne_serwer_1710/armourersWorkshop/official/Head Bow Left.armour` | `armourers:head` | 11 | 44 | 1 | `439ac66190e330ff...` |
| `pliki_globalne_serwer_1710/armourersWorkshop/official/Head Bow Right.armour` | `armourers:head` | 11 | 44 | 1 | `ea712888ff658c7a...` |
| `pliki_globalne_serwer_1710/armourersWorkshop/official/Lightsaber (Dual).armour` | `armourers:sword` | 11 | 160 | 1 | `03d7e4dcc9c25e38...` |
| `pliki_globalne_serwer_1710/armourersWorkshop/official/Lightsaber.armour` | `armourers:sword` | 11 | 92 | 1 | `483128c10bf02341...` |
| `pliki_globalne_serwer_1710/armourersWorkshop/official/Madoka's Head Bows.armour` | `armourers:head` | 11 | 20 | 1 | `356367e6ef7b0f50...` |
| `pliki_globalne_serwer_1710/armourersWorkshop/official/Madoka's Shoes.armour` | `armourers:feet` | 11 | 168 | 2 | `c5f461551b118a27...` |
| `pliki_globalne_serwer_1710/armourersWorkshop/official/Madoka's Skirt.armour` | `armourers:legs` | 11 | 528 | 3 | `16ba63c36f44282d...` |
| `pliki_globalne_serwer_1710/armourersWorkshop/official/Madoka's Top.armour` | `armourers:chest` | 11 | 686 | 3 | `4e89b5eacef502e1...` |
| `pliki_globalne_serwer_1710/armourersWorkshop/official/Pika Hood.armour` | `armourers:head` | 11 | 358 | 1 | `0a2a8d1434ddc86e...` |
| `pliki_globalne_serwer_1710/armourersWorkshop/official/Pika Pants.armour` | `armourers:legs` | 11 | 288 | 2 | `cd1e0f370f89488a...` |
| `pliki_globalne_serwer_1710/armourersWorkshop/official/Pika Paws.armour` | `armourers:feet` | 11 | 192 | 2 | `0762fb11c51073f0...` |
| `pliki_globalne_serwer_1710/armourersWorkshop/official/Pika T.armour` | `armourers:chest` | 11 | 731 | 3 | `5418588901bf5afb...` |
| `pliki_globalne_serwer_1710/armourersWorkshop/official/Robot Key.armour` | `armourers:chest` | 11 | 52 | 1 | `3f685853b1726ff6...` |
| `pliki_globalne_serwer_1710/armourersWorkshop/official/Sakura's Cat Boots.armour` | `armourers:feet` | 11 | 284 | 2 | `fc03202ce68bd671...` |
| `pliki_globalne_serwer_1710/armourersWorkshop/official/Sakura's Cat Chest.armour` | `armourers:chest` | 11 | 755 | 3 | `82d30353a4aadae2...` |
| `pliki_globalne_serwer_1710/armourersWorkshop/official/Sakura's Cat Ears.armour` | `armourers:head` | 11 | 56 | 1 | `9ea922d715cc90a8...` |
| `pliki_globalne_serwer_1710/armourersWorkshop/official/Sakura's Cat Skirt.armour` | `armourers:legs` | 11 | 1037 | 3 | `c560c7c822153048...` |
| `pliki_globalne_serwer_1710/armourersWorkshop/official/Sakura's Chest.armour` | `armourers:chest` | 1 | 720 | 3 | `d7a8ad7c5110777a...` |
| `pliki_globalne_serwer_1710/armourersWorkshop/official/Sakura's Shoes.armour` | `armourers:feet` | 1 | 168 | 2 | `be789d7fbb3e2c6d...` |
| `pliki_globalne_serwer_1710/armourersWorkshop/official/Sakura's Skirt.armour` | `armourers:legs` | 11 | 877 | 1 | `a03551e7e53ce30b...` |
| `pliki_globalne_serwer_1710/armourersWorkshop/official/Scythe.armour` | `armourers:sword` | 11 | 59 | 1 | `d1bc14f2efb9080a...` |
| `pliki_globalne_serwer_1710/armourersWorkshop/official/Viking Helmet (Blood).armour` | `armourers:head` | 11 | 340 | 1 | `3e7b45394a66bb3d...` |
| `pliki_globalne_serwer_1710/armourersWorkshop/official/Viking Helmet.armour` | `armourers:head` | 11 | 332 | 1 | `ea20a5256eb6b9c8...` |
| `pliki_globalne_serwer_1710/armourersWorkshop/official/Witch's Boots.armour` | `armourers:feet` | 11 | 180 | 2 | `62737de14698c988...` |
| ... | ... | ... | ... | ... | jeszcze 106 plikow w JSON |

Dowod z kodu formatu pliku:

```java
stream.writeInt(Skin.FILE_VERSION);
StreamUtils.writeString(stream, Charsets.US_ASCII, TAG_SKIN_HEADER);
stream.writeUTF(skin.getSkinType().getRegistryName());
SkinPartSerializer.saveSkinPart(skinPart, stream);
```

Plik: `.../common/skin/data/serialize/SkinSerializer.java`. `Skin.FILE_VERSION` w 0.48.5 wynosi `13`; ten numer jest zapisany w pierwszych 4 bajtach kazdego pliku `.armour`.

## 1.18.2 - Bloki

Znaleziono lokalne kandydaty 1.18.2; nastepny przebieg powinien zdekompilowac/przeskanowac registry.

Na podstawie dokumentacji projektu spodziewane docelowe odpowiedniki to m.in. `armourers_workshop:armourer`, `armourers_workshop:skin_library`, `armourers_workshop:skinning_table`, `armourers_workshop:dye_table`, `armourers_workshop:hologram_projector`, `armourers_workshop:mannequin`. Ten raport nie zatwierdza finalnych registry names bez lokalnego JAR/source 3.x.

## 1.18.2 - Block Entities

Brak lokalnego artefaktu 1.18.2 oznacza brak bezpiecznej listy BlockEntityType i brak potwierdzenia formatu danych modeli. Nastepny krok przed konwerterem modeli powinien dodac/dekompilowac JAR Armourer's Workshop 3.2.7-beta i porownac parser zapisu skina 3.x z `SkinSerializer` 0.48.5.

## Porownanie 1.7.10 vs 1.18.2

- Bloki warsztatowe prawdopodobnie maja bezposrednia migracje A -> A, ale registry names i BlockEntityType 3.x musza byc potwierdzone lokalnie.
- Najwieksze ryzyko nie jest w blokach, tylko w modelach: 146 plikow `.armour` z globalnego katalogu serwera plus referencje skinow w TE/playerdata.
- Konwerter docelowy musi traktowac globalna biblioteke jako osobny strumien migracji: najpierw parse/manifest/checksum, potem konwersja formatu 0.48.5 -> 3.x, dopiero na koncu remap TE wskazujacych na te modele.
- `te.skinnable` i `te.skinnableChild` wymagaja szczegolnej ostroznosci, bo skin blokowy moze skladac sie z glownego bloku i child-blockow linkowanych po NBT.

## Kryteria dla nastepnego kroku

1. Dostarczyc lokalny JAR/source Armourer's Workshop 1.18.2 3.x do `mod_src/118`.
2. Uruchomic analogiczny skan rejestracji 1.18.2 i serializerow modelu.
3. Zbudowac test zgodnosci dla kilku plikow `.armour`: head/chest/block/multiblock, z porownaniem properties, cube_count, marker_count i part_types.
