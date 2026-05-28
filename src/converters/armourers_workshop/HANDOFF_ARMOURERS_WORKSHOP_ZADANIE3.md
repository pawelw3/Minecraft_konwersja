# Handoff: Armourer's Workshop, Zadanie 3

## Podsumowanie sesji

Wykonano kolejny krok dla Armourer's Workshop: dodano pierwszy konwerter eventow i mapowania blokow/BlockEntity 1.7.10 -> 1.18.2. Konwerter rozroznia proste remapy, skinnable z referencjami do modeli oraz przypadki wymagajace placeholdera albo osobnego etapu entity/modeli.

## Ukonczono

- [x] Dodano `src/converters/armourers_workshop/mappings.py` z registry mappingiem opartym o source.
- [x] Dodano `src/converters/armourers_workshop/converter.py`.
- [x] Obsluzono `skinnable` parent: `Skin`, `Refers`, `LinkedPos`.
- [x] Obsluzono `skinnableChild`: `Refer` jako offset do parenta.
- [x] Dodano sidecar event migracji globalnej biblioteki `.armour` do `skin-library`.
- [x] Dodano placeholder rescue dla `mannequin`, `doll`, `miniArmourer`.
- [x] Dodano testy jednostkowe Zadania 3.
- [x] Zaktualizowano eksporty pakietu.

## Nowe pliki

- `src/converters/armourers_workshop/mappings.py`
- `src/converters/armourers_workshop/converter.py`
- `src/converters/armourers_workshop/tests/test_armourers_workshop_converter.py`
- `src/converters/armourers_workshop/ARMOURERS_WORKSHOP_ZADANIE3_KONWERTER.md`
- `src/converters/armourers_workshop/HANDOFF_ARMOURERS_WORKSHOP_ZADANIE3.md`

## Zmodyfikowane pliki

- `src/converters/armourers_workshop/__init__.py`
- `HANDOFF.md`

## Weryfikacja

- `python -m pytest src\converters\armourers_workshop\tests -q` -> `16 passed`.
- `python -m py_compile src\converters\armourers_workshop\converter.py src\converters\armourers_workshop\mappings.py` -> OK.

## Nastepne kroki

1. [ ] Dodac wykonawczy etap binarnej konwersji `.armour`: read v12/v13 przez source 1.18.2, write v25 do `skin-library`.
2. [ ] Zbudowac rescue mapping dla `db:<localId>` na podstawie lokalnej bazy/cache, bo sam localId nie wystarcza do odtworzenia sciezki.
3. [ ] Rozszerzyc konwersje `mannequin` z placeholdera na docelowy spawn entity `armourers_workshop:mannequin`.
4. [ ] Podlaczyc konwerter do routera dopiero po ustaleniu kontraktu eventu biblioteki/modeli.

