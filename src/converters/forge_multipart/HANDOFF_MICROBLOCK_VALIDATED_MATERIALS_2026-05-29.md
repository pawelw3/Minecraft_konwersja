# Handoff: ForgeMultipart microblock validated materials

## Podsumowanie sesji
Naprawiono konwerter ForgeMultipart/CBMultipart tak, aby pole `material` w `cb_microblock:*` nie przepuszczalo juz dowolnego skladniowo poprawnego `ResourceLocation`. Przyczyna crasha klienta byla materializacja microblocka z materialem niezarejestrowanym w 1.18.2, np. `chisel:glowstone_4`, co dawalo `MicroblockPart.getMaterial() == null`.

## Ukończono
- [x] Dodano konserwatywna whiteliste bezpiecznych materialow vanilla 1.18.2 dla CBMicroblock.
- [x] Dodano mapowanie starych materialow `chisel:*`, `tile.extrautils:*`, `thermalfoundation:*`, `mekanism:*` oraz legacy `minecraft:*_meta` na bezpieczne bloki 1.18.2.
- [x] Zmieniono `map_microblock_material()`, zeby nieznane, ale skladniowo poprawne ID typu `unknownmod:block` spadaly do `minecraft:stone`.
- [x] Podpieto awaryjny patcher `tasks/custom_area_1800_574/patch_invalid_microblock_materials.py` pod glowna funkcje mapujaca z konwertera.
- [x] Dodano testy regresyjne dla materialow, ktore mogly powodowac crash/render null material.

## Zmodyfikowane pliki
- `src/converters/forge_multipart/mappings.py`
- `src/converters/forge_multipart/tests/test_forge_multipart_converter.py`
- `tasks/custom_area_1800_574/patch_invalid_microblock_materials.py`

## Weryfikacja
- `python -m pytest src\converters\forge_multipart\tests\test_forge_multipart_converter.py -q` -> 25 passed.
- `python -m py_compile src\converters\forge_multipart\mappings.py src\converters\forge_multipart\nbt_converter.py tasks\custom_area_1800_574\patch_invalid_microblock_materials.py` -> OK.
- Skan `tasks/custom_area_1800_574/events.jsonl`: `materials=78676`, `changed_by_mapper=6463`, `unsafe_after_mapping=0`.

## Następne kroki
1. [ ] Uruchomic ponownie konwersje albo patcher na juz wygenerowanym swiecie, zeby zapisac poprawione materialy do `world/region/*.mca`.
2. [ ] Ponownie wejsc klientem na koordynaty crasha `-1445 67 -792` i sprawdzic `latest.log`.
