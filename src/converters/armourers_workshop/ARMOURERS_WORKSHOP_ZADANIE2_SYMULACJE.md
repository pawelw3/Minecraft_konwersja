# Armourer's Workshop - Zadanie 2: symulacje kontraktowe

## Podsumowanie

Przygotowano czyste symulacje Python dla nietrywialnych funkcji AW 1.7.10 -> 1.18.2:

- dispatch serializerow `.armour` v12/v13/v20..v25,
- migracja globalnej biblioteki z `armourersWorkshop` do `skin-library`,
- migracja referencji `SkinPointer`/`SkinIdentifier` do domen 1.18.2,
- aliasy partow zachowane przez `SkinPartSerializerV13`.

## Wyniki kontraktow

- `v13_reads_with_1182`: `True`
- `forced_latest_writes_v25`: `True`
- `server_library_uses_ws_namespace`: `True`
- `library_paths_keep_armour_extension`: `True`

## Pliki

- `src/converters/armourers_workshop/simulations/step2_contract_simulations.py`
- `src/converters/armourers_workshop/tests/test_step2_contract_simulations.py`
- `src/converters/armourers_workshop/ARMOURERS_WORKSHOP_ZADANIE2_SIMULATION_RESULTS.json`

## Zrodla z kodu

- `1710_skin_serializer`: Skin.FILE_VERSION = 13 and SkinSerializer.writeToStream writes an int version followed by AW-SKIN-START/PROPS/TYPE/PAINT/PART markers.
- `1182_skin_serializer_dispatch`: SkinSerializer registers v20, v13, v12; readFromStream picks by file version and handles the SKIN header for >=20.
- `1182_v13_part_aliases`: SkinPartSerializerV13 remaps skirt.base -> legs.skirt, bow.base -> bow.frame1 and arrow.base -> bow.arrow.
- `1710_library_dir`: SkinIOUtils.getSkinLibraryDirectory returns user.dir / LibModInfo.ID; this pack has pliki_globalne_serwer_1710/armourersWorkshop.
- `1182_library_dir`: EnvironmentManager.getSkinLibraryDirectory returns root / skin-library; SkinLibraryLoader keeps recursive .armour paths and exposes ws:<path>.
- `1710_skin_pointer`: SkinPointer stores compound tag armourersWorkshop with identifier, lock and SkinDye; SkinIdentifier may contain localId, libraryFile, globalId and skinType.
- `1182_data_domain`: DataDomain uses namespaces fs, rs, ws, db, ln, ks, kv, sp; server library skins use ws:<path>.

## Znaczenie dla Zadania 3

Konwerter nie powinien tylko kopiowac plikow `.armour`. Dla finalnego wyniku
trzeba wczytac v13 przez serializer 1.18.2 i zapisac do latest v25, zachowujac
relatywna sciezke biblioteki oraz aktualizujac referencje do `ws:<path>.armour`.
