# Handoff: Armourer's Workshop, Zadanie 1

## Podsumowanie sesji
Rozpoczeto implementacje konwersji Armourer's Workshop od kroku 1: inwentaryzacji blokow, tile entities i globalnych plikow modeli. Ze wzgledu na sposob zapisu AW dodano jawny skan `pliki_globalne_serwer_1710/armourersWorkshop`, bo modele `.armour` sa poza chunkami mapy.

## Ukonczono
- [x] Dodano skrypt analizy `src/converters/armourers_workshop/analyze_step1.py`.
- [x] Skrypt wyciaga bloki i TE 1.7.10 z lokalnego source `ModBlocks.java`/`LibBlockNames.java`.
- [x] Skrypt parsuje manifest globalnych plikow `.armour`: file_version, skin_type, properties, part_count, cube_count, marker_count i checksum SHA-256.
- [x] Pobrano source Armourer's Workshop 1.18.2 `v3.2.7-beta` do `mod_src/118/actual_src/1.18.2/ArmourersWorkshop/repo`.
- [x] Pobrano JAR `armourersworkshop-forge-1.18.2-3.2.7-beta.jar` do `mod_src/118/mod_jars`.
- [x] Odswiezono raport; artefakty 1.18.2 sa teraz wykrywane lokalnie.
- [x] Wykonano krok 1B: porownano serializer modeli 1.7.10 z serializerami 1.18.2.

## Wynik
- 19 blokow 1.7.10.
- 13 tile entities 1.7.10 rejestrowanych jako `te.<id>`.
- 146/146 plikow `.armour` sparsowane poprawnie.
- 68 003 voxel-cubes w globalnej bibliotece modeli.
- Source 1.18.2: tag `v3.2.7-beta`, commit `8387cf3fe1eb4d803acb5f18df043554ab305f4f`.
- JAR 1.18.2: SHA-512 `32675a225bdfa7af3644abcf870e9e237e394ddf27bd8b77e908a225c242bbaf4fca977fc5b39286b1fad59de0abd86a9f5bbbf91989fc280f731da69d7a7d0f`.
- Krok 1B: pliki 1.7.10 maja format v13; AW 1.18.2 ma `SkinSerializerV13`, a nowy zapis powinien isc przez latest serializer v20/v25 do folderu `skin-library`.

## Nowe pliki
- `src/converters/armourers_workshop/__init__.py`
- `src/converters/armourers_workshop/analyze_step1.py`
- `src/converters/armourers_workshop/ARMOURERS_WORKSHOP_ZADANIE1_ANALIZA.md`
- `src/converters/armourers_workshop/ARMOURERS_WORKSHOP_KROK1B_SERIALIZERY.md`
- `src/converters/armourers_workshop/HANDOFF_ARMOURERS_WORKSHOP_ZADANIE1.md`
- `output/armourers_workshop_step1/armourers_workshop_step1_inventory.json`
- `mod_src/118/actual_src/1.18.2/ArmourersWorkshop/repo/`
- `mod_src/118/mod_jars/armourersworkshop-forge-1.18.2-3.2.7-beta.jar`

## Zmodyfikowane pliki
- `HANDOFF.md`
- `src/converters/armourers_workshop/HANDOFF_ARMOURERS_WORKSHOP_ZADANIE1.md`

## Nastepne kroki
1. [ ] Przeskanowac source/JAR 1.18.2 pod registry blokow i BlockEntityType.
2. [ ] Przygotowac helper Java/Kotlin dla read v13 -> write latest v25.
3. [ ] Przygotowac test migracji kilku reprezentatywnych plikow `.armour` przed ruszaniem TE na mapie.
