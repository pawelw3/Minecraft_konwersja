# Chisel Task 5A - raport

## Podsumowanie

Zadanie 5A wygenerowalo testowy patch 1.7.10 i przekonwertowalo go do eventow 1.18.2.
Scenariusz obejmuje wszystkie dynamiczne rodziny Chisela z `level.dat` oraz wszystkie realnie zaobserwowane warianty `block/meta` z raportu Zadania 4.
Patch zrodlowy zostal tez nalozony na fizyczna kopie lekkiego swiata 1.7.10: `lightweigh_map_templates/1710/chisel_task5a_world`.

- Probki: 457
- Eventy 1.18.2: 457
- Sukcesy: 457
- Bledy: 0
- Placeholdery TE: 4
- Edycje nalozone na mape 1.7.10: 461

## Zakres probek

- `observed_block_meta`: 312
- `registry_meta0_unobserved`: 141
- `tile_entity`: 4

## Najczestsze targety w scenariuszu

- `minecraft:stone`: 298
- `rechiseled:quartz_block_small_tiles`: 18
- `rechiseled:oak_planks_tiles`: 12
- `rechiseled:stone_tiles`: 11
- `minecraft:white_wool`: 11
- `rechiseled:cobblestone_tiles`: 11
- `minecraft:glass`: 11
- `rechiseled:dirt_tiles`: 9
- `rechiseled:spruce_planks_tiles`: 9
- `rechiseled:diorite_tiles`: 7
- `rechiseled:glowstone_tiles`: 7
- `rechiseled:netherrack_tiles`: 7

## Pliki

- `chisel_task5a_source_patch_1710.json` - patch zrodlowy 1.7.10.
- `chisel_task5a_converted_patch_1182.json` - patch docelowy 1.18.2.
- `chisel_task5a_events_1182.json` - surowe eventy konwertera.
- `chisel_task5a_conversion_report.json` - pelny raport per probka.
- `lightweigh_map_templates/1710/chisel_task5a_world` - zmaterializowana mapa testowa 1.7.10.

## Weryfikacja

- `python -B test_scenarios\chisel_task5a\generate_chisel_task5a.py` - OK.
- `java -jar jvm\worker\build\libs\mc-editkit-worker-1.0-SNAPSHOT.jar --world lightweigh_map_templates\1710\chisel_task5a_world --patch test_scenarios\chisel_task5a\chisel_task5a_source_patch_1710.json` - OK, zapisano region `r.0.0.mca`.
- `python -m pytest src\converters\chisel\tests -q` - 15 passed.
- `python -m py_compile src\converters\chisel\chisel_converter.py src\converters\chisel\mappings.py src\converters\router.py test_scenarios\chisel_task5a\generate_chisel_task5a.py` - OK.

## Wnioski

Konwersja technicznie pokrywa caly scenariusz 5A. Nadal zostaje znane ryzyko wizualne: czesc rodzin bez dokladnego odpowiednika trafia do fallbackow Rechiseled/Chipped albo vanilla.
Nastepny etap powinien materializowac patch na 1.18.2 i zweryfikowac wizualnie najczestsze rodziny: marble, limestone, concrete, stonebricksmooth, factoryblock i technical2.
