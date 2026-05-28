# Handoff: Armourer's Workshop, Zadanie 2

## Podsumowanie sesji

Wykonano Zadanie 2 dla Armourer's Workshop: przygotowano czyste symulacje kontraktowe w Pythonie dla nietrywialnej migracji modeli i referencji skinow. Symulacje bazuja na source 1.7.10 oraz 1.18.2 i nie dotykaja mapy ani plikow globalnych serwera.

## Ukonczono

- [x] Dodano modul `src/converters/armourers_workshop/simulations/step2_contract_simulations.py`.
- [x] Zasymulowano dispatch serializerow `.armour`: v12, v13 oraz nowy v20/v25.
- [x] Zasymulowano wymuszenie zapisu latest v25 dla plikow wejsciowych v13.
- [x] Zasymulowano migracje biblioteki z `armourersWorkshop` do `skin-library` i identyfikatorow `ws:<path>.armour`.
- [x] Zasymulowano migracje `SkinPointer`/`SkinIdentifier` z 1.7.10 do domen 1.18.2: `ws`, `ks`, `db`.
- [x] Zasymulowano aliasy partow z `SkinPartSerializerV13`: skirt/base, bow/base, arrow/base.
- [x] Dodano testy jednostkowe dla kontraktow Zadania 2.
- [x] Wygenerowano raport i JSON wynikow.

## Wynik

- Kontrakt `v13_reads_with_1182`: `true`.
- Kontrakt `forced_latest_writes_v25`: `true`.
- Kontrakt `server_library_uses_ws_namespace`: `true`.
- Kontrakt `library_paths_keep_armour_extension`: `true`.
- Testy: `10 passed`.

## Nowe pliki

- `src/converters/armourers_workshop/simulations/__init__.py`
- `src/converters/armourers_workshop/simulations/step2_contract_simulations.py`
- `src/converters/armourers_workshop/tests/test_step2_contract_simulations.py`
- `src/converters/armourers_workshop/ARMOURERS_WORKSHOP_ZADANIE2_SYMULACJE.md`
- `src/converters/armourers_workshop/ARMOURERS_WORKSHOP_ZADANIE2_SIMULATION_RESULTS.json`
- `src/converters/armourers_workshop/HANDOFF_ARMOURERS_WORKSHOP_ZADANIE2.md`

## Zmodyfikowane pliki

- `HANDOFF.md`

## Weryfikacja

- `python src\converters\armourers_workshop\simulations\step2_contract_simulations.py` -> OK, wszystkie kontrakty `true`.
- `python -m pytest src\converters\armourers_workshop\tests\test_step2_contract_simulations.py -q` -> `10 passed`.
- `python -m py_compile src\converters\armourers_workshop\simulations\step2_contract_simulations.py src\converters\armourers_workshop\tests\test_step2_contract_simulations.py` -> OK.

## Nastepne kroki

1. [ ] Zadanie 3: przygotowac kod konwersji, przede wszystkim helper read v13 -> write latest v25.
2. [ ] Dla referencji `db:<localId>` przygotowac rescue mapping z lokalnej bazy/cache, bo sam localId nie zawiera sciezki pliku.
3. [ ] Przeskanowac registry blokow i BlockEntityType 1.18.2 przed mapowaniem TE.
