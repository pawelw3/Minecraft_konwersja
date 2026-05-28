# Handoff: Chisel - Zadanie 3

## Podsumowanie sesji

Wykonano trzeci krok implementacji Chisel: konwerter eventow dla dekoracyjnych blokow oraz tile entities. Kod obsluguje dynamiczne numeric ID z map/testow, mapowanie wizualne do Rechiseled/Chipped oraz placeholdery data-rescue dla TE bez odpowiednika.

## Ukonczono

- [x] `ChiselConverter.convert_block()` dla nazwanych blokow `chisel:*`.
- [x] `ChiselConverter.convert_block()` dla numeric ID przez `DynamicChiselIdEntry`.
- [x] `ChiselConverter.convert_tile_entity()` dla Auto Chisel, Present i Carvable Beacon.
- [x] `mappings.py` z polityka wizualnego targetowania Rechiseled/Chipped.
- [x] Integracja TE Chisela z `src/converters/router.py`.
- [x] Testy konwertera i routera.
- [x] Raport `CHISEL_ZADANIE3_KONWERTER.md`.

## Nowe pliki

- `src/converters/chisel/mappings.py`
- `src/converters/chisel/chisel_converter.py`
- `src/converters/chisel/tests/test_chisel_converter.py`
- `src/converters/chisel/CHISEL_ZADANIE3_KONWERTER.md`
- `src/converters/chisel/HANDOFF_CHISEL_ZADANIE3.md`

## Zmodyfikowane pliki

- `src/converters/router.py` - dodano lazy singleton `_chisel()`, detekcje TE Chisela i branch w `convert_te_to_events()`.

## Weryfikacja

- `python -m pytest src\converters\chisel\tests -q`
- Wynik: `14 passed`
- `python -m py_compile src\converters\router.py src\converters\chisel\chisel_converter.py src\converters\chisel\mappings.py`
- Wynik: bez bledow

## Nastepne kroki

1. [ ] Zadanie 4: skan stref glownej mapy bez edycji mapy.
2. [ ] W Zadaniu 4 wygenerowac dynamiczna tabele numeric ID/meta -> rodzina/variant_hint dla Chisel.
3. [ ] Zweryfikowac pokrycie konwertera i wskazac rodziny wymagajace Chipped albo recznego targetu.

