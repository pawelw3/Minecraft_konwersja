# Handoff: block-only krok 2 dla modow z blokami bez TE

## Podsumowanie sesji

Zaimplementowano pierwsza wersje warstwy `block_only_converter` dla modow z zakresu `common` -> `mekanism`, ktore maja realne bloki bez TileEntity: Extra Utilities, GrowthCraft, IC2, Jammy Furniture i Mekanism. Dodano wspolny typ `BlockOnlyResult`, centralny router, testy jednostkowe oraz integracje routera z direct terrain writerem dla `tasks/custom_area_1800_574`.

## Ukonczono

- [x] Wspolny interfejs `BlockOnlyResult` w `src/converters/common/block_only.py`.
- [x] Centralny router `src/converters/block_only_router.py`.
- [x] `extrautils/block_only_converter.py` z mapowaniami direct, kolorowymi fallbackami i odrzuceniem blokow z NBT.
- [x] `growthcraft/block_only_converter.py` z bezpiecznymi vanilla fallbackami, bo GrowthCraft nie jest w aktualnym `client_pack_1182/mod_manifest.json`.
- [x] `ic2/block_only_converter.py` dla rud, metal blocks, prostych blokow i kabli jako blockstate-only fallback.
- [x] `jammyfurniture/block_only_converter.py` z filtrowaniem `preserve_inventory=True` i fallbackiem dla target modow nieobecnych w paczce.
- [x] `mekanism/block_only_converter.py` oparty o istniejace `get_block_mapping()` i filtr `has_block_entity=False`.
- [x] Testy jednostkowe dla kazdego moda i routera.
- [x] Podpiecie routera block-only w `tasks/custom_area_1800_574/convert_area_direct.py`.
- [x] Zapis audytu direct block-only do `tasks/custom_area_1800_574/block_remap_audit.jsonl` podczas konwersji.

## Nowe pliki

- `src/converters/common/block_only.py`
- `src/converters/block_only_router.py`
- `src/converters/extrautils/block_only_converter.py`
- `src/converters/growthcraft/block_only_converter.py`
- `src/converters/ic2/block_only_converter.py`
- `src/converters/jammyfurniture/block_only_converter.py`
- `src/converters/mekanism/block_only_converter.py`
- `src/converters/extrautils/tests/test_block_only_converter.py`
- `src/converters/growthcraft/tests/test_block_only_converter.py`
- `src/converters/ic2/tests/test_block_only_converter.py`
- `src/converters/jammyfurniture/tests/test_block_only_converter.py`
- `src/converters/mekanism/tests/test_block_only_converter.py`
- `src/converters/tests/test_block_only_router.py`

## Zmodyfikowane pliki

- `tasks/custom_area_1800_574/convert_area_direct.py`

## Weryfikacja

- `python -m py_compile src\converters\common\block_only.py src\converters\block_only_router.py src\converters\mekanism\block_only_converter.py src\converters\extrautils\block_only_converter.py src\converters\ic2\block_only_converter.py src\converters\growthcraft\block_only_converter.py src\converters\jammyfurniture\block_only_converter.py` -> OK.
- `python -m pytest src\converters\mekanism\tests\test_block_only_converter.py src\converters\extrautils\tests\test_block_only_converter.py src\converters\ic2\tests\test_block_only_converter.py src\converters\growthcraft\tests\test_block_only_converter.py src\converters\jammyfurniture\tests\test_block_only_converter.py src\converters\tests\test_block_only_router.py -q` -> 23 passed.
- `python -m py_compile tasks\custom_area_1800_574\convert_area_direct.py ...` -> OK.
- Smoke import bez uruchamiania konwersji: `map_block(2159,2)` -> `mekanism:tin_ore`, `map_block(2166,8)` -> `minecraft:gray_concrete`, `map_block(1955,0)` -> `angelblockrenewed:angel_block`.

## Nastepne kroki

1. [ ] Uruchomic test na wycinku mapy i sprawdzic, czy modowe bloki bez TE nie spadaja do `minecraft:air`.
2. [ ] Uruchomic test headless na przekonwertowanym wycinku.
3. [ ] Jesli wynik audytu pokaze duzo `requires_event_or_failed_to_air`, dopisac brakujace per-mod fallbacki albo potwierdzic, ze sa pokryte eventami TE.
