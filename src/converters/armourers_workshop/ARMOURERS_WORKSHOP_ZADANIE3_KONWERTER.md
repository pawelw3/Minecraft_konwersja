# Armourer's Workshop - Zadanie 3: konwerter eventow

## Podsumowanie

Dodano pierwszy kod konwersji dla Armourer's Workshop 1.7.10 -> 1.18.2. Konwerter mapuje potwierdzone bloki warsztatowe na registry 1.18.2, przenosi bezpieczne minimum BlockEntity NBT i emituje placeholdery dla przypadkow, ktore w 1.18.2 nie sa juz blokami albo wymagaja osobnego etapu.

## Zakres

- `armourLibrary` -> `armourers_workshop:skin-library`.
- `globalSkinLibrary` -> `armourers_workshop:skin-library-global`.
- `skinningTable` -> `armourers_workshop:skinning-table`.
- `dyeTable` -> `armourers_workshop:dye-table`.
- `colourMixer` -> `armourers_workshop:colour-mixer`.
- `armourerBrain` -> `armourers_workshop:armourer`.
- `hologramProjector` -> `armourers_workshop:hologram-projector`.
- Equipment cubes -> `skin-cube*`.
- `skinnable`/`skinnableChild` -> `armourers_workshop:skinnable` z migracja referencji.
- `mannequin`, `doll`, `miniArmourer` -> placeholder rescue, bo nie maja bezpiecznego prostego block targetu.

## Zasady NBT

Konwerter nie wymysla pelnego NBT modeli. Dla `skinnable` przenosi tylko elementy potwierdzone przez source:

- `Skin` jako descriptor z identyfikatorem `ws:<path>.armour`, `ks:<id>` albo `db:<id>`.
- `Refers` jako offsety wzgledem glownego bloku, na podstawie `relatedBlocks`.
- `Refer` dla child blockow, na podstawie `parentX/parentY/parentZ`.
- `LinkedPos` jezeli w 1.7.10 istnieje `linkedBlock`.

`Shape`, `Markers` i `SkinProperties` wymagaja odczytu skonwertowanego pliku `.armour` przez runtime 1.18.2, wiec konwerter dodaje ostrzezenia zamiast zgadywac wartosci.

## Modele globalne

Dodano `build_library_migration_event()`, ktory tworzy sidecar event:

- zrodlo: `pliki_globalne_serwer_1710/armourersWorkshop`,
- cel: `skin-library`,
- odczyt: `SkinSerializerV12`, `SkinSerializerV13`, `SkinSerializerV20`,
- zapis: `SkinSerializerV20`,
- wersja docelowa: v25,
- identyfikatory docelowe: `ws:<path>.armour`.

## Zrodla

- 1.7.10 `LibBlockNames.java` i rejestracja TE jako `te.<id>`.
- 1.18.2 `ModBlocks.java`, `ModBlockEntityTypes.java`, `ModConstants.java`.
- 1.7.10 `TileEntitySkinnable.java`, `TileEntitySkinnableChild.java`, `SkinPointer.java`.
- 1.18.2 `SkinnableBlockEntity.java`, `SkinBlockPlaceContext.java`, `SkinDescriptor.java`, `TagSerializer.java`.

## Weryfikacja

- `python -m pytest src\converters\armourers_workshop\tests -q` -> `16 passed`.
- `python -m py_compile src\converters\armourers_workshop\converter.py src\converters\armourers_workshop\mappings.py` -> OK.

