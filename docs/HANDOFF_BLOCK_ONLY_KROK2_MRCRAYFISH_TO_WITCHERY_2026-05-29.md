# Handoff: block-only krok 2 mrcrayfish_furniture do witchery

## Podsumowanie sesji

Zaimplementowano krok 2 dla modow z raportow block-only od `mrcrayfish_furniture` do `witchery`. Dodano per-mod `block_only_converter.py`, wlaczono je do centralnego routera i dodano testy jednostkowe dla mapowan, fallbackow oraz odrzucen TE/network.

## Ukonczono

- [x] Dodano block-only converter dla `mrcrayfish_furniture`.
- [x] Dodano block-only converter dla `openmodularturrets`.
- [x] Dodano block-only converter dla `projectred`.
- [x] Dodano block-only converter dla `railcraft`.
- [x] Dodano block-only converter dla `reliquary`.
- [x] Dodano block-only converter dla `thermal`.
- [x] Dodano block-only converter dla `thermal_dynamics`.
- [x] Dodano block-only converter dla `traincraft`.
- [x] Dodano block-only converter dla `witchery`.
- [x] Rozszerzono `src/converters/block_only_router.py`.
- [x] Dodano testy jednostkowe i smoke test routera.

## Nowe pliki

- `src/converters/mrcrayfish_furniture/block_only_converter.py`
- `src/converters/openmodularturrets/block_only_converter.py`
- `src/converters/projectred/block_only_converter.py`
- `src/converters/railcraft/block_only_converter.py`
- `src/converters/reliquary/block_only_converter.py`
- `src/converters/thermal/block_only_converter.py`
- `src/converters/thermal_dynamics/block_only_converter.py`
- `src/converters/traincraft/block_only_converter.py`
- `src/converters/witchery/block_only_converter.py`
- `src/converters/*/tests/test_block_only_converter.py` dla powyzszych modow
- `src/converters/mrcrayfish_furniture/__init__.py`
- `src/converters/railcraft/__init__.py`
- `src/converters/traincraft/__init__.py`
- `src/converters/mrcrayfish_furniture/tests/__init__.py`
- `src/converters/thermal_dynamics/tests/__init__.py`

## Zmodyfikowane pliki

- `src/converters/block_only_router.py`
- `src/converters/tests/test_block_only_router.py`

## Weryfikacja

- `python -m py_compile ...` dla nowych konwerterow i routera: OK.
- Skupione testy nowych konwerterow i routera: `32 passed`.
- Smoke routera dla 9 namespace'ow: OK.

Pelny glob wszystkich testow `test_block_only_converter.py` w repo zostal zatrzymany przez istniejace konflikty importow pytest w starszych katalogach testow bez kompletnego pakietowania (`__init__.py`). Skupiony zestaw dla zmienionego zakresu przeszedl.

## Nastepne kroki

1. [ ] Opcjonalnie uporzadkowac pakietowanie wszystkich starszych katalogow testow block-only, zeby jeden glob pytest dzialal w calym repo.
2. [ ] Uruchomic konwersje wycinka i przejrzec `block_remap_audit.jsonl` pod katem najczestszych fallbackow low-confidence.
