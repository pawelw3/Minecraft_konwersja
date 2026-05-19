# Handoff: Mekanism - Zadanie 2

## Podsumowanie sesji

Wykonano Zadanie 2 dla **Mekanism core**: przygotowano czyste symulacje Python dla nietrywialnych mechanik moda 1.7.10 -> 1.18.2. Symulacje nie dotykaja mapy i bazuja na lokalnych JAR-ach, bo bledne checkouty zrodel Mekanism zostaly usuniete.

## Ukonczono

- [x] Dodano symulacje ore processing x2/x3/x4/x5 dla 1.7.10 i 1.18.2.
- [x] Dodano symulacje Factory: liczba lane'ow, tick progress, `recipeType`, `progress0..N`, target factory ID.
- [x] Dodano symulacje Energy Cube: tier, capacity/output 1.7.10, migracja przez zachowanie fill ratio.
- [x] Dodano symulacje Gas Tank -> Chemical Tank: tier, chemical id, `dumping`.
- [x] Dodano model frequency owner/public z ostrzezeniem `missing_owner_uuid`.
- [x] Dodano symulacje Digital Miner: zakres, inverse mode, filtry i reset `running`.
- [x] Dodano testy porownawcze i smoke testy.

## Nowe pliki

- `src/converters/mekanism/simulations/common.py`
- `src/converters/mekanism/simulations/ore_processing.py`
- `src/converters/mekanism/simulations/factory_simulation.py`
- `src/converters/mekanism/simulations/storage_frequency.py`
- `src/converters/mekanism/simulations/digital_miner.py`
- `src/converters/mekanism/simulations/test_simulations.py`
- `src/converters/mekanism/simulations/README.md`
- `src/converters/mekanism/simulations/__init__.py`
- `src/converters/mekanism/HANDOFF_MEKANISM_ZADANIE2.md`

## Zrodla uzyte w analizie

- `modpack_1710/Mekanism-1.7.10-9.1.1-clienthax.jar`
- `mod_src/118/mod_jars/Mekanism-1.18.2-10.2.5.465.jar`
- `src/converters/mekanism/MEKANISM_ZADANIE1_ANALIZA.md`

## Kluczowe ustalenia dla Zadania 3

Factory musi byc mapowane po `recipeType`, nie tylko po starym TE ID. Stare `UltimateSmeltingFactory` w 1.7.10 odpowiada elite factory z 7 lane'ami, wiec naturalny target to np. `mekanism:elite_smelting_factory`, nie `mekanism:ultimate_smelting_factory`.

`progress0..N` jest stanem per lane. Konwerter powinien przeniesc te wartosci albo jawnie zaraportowac ich utrate.

Gas Tank 1.7.10 trzeba traktowac jako Chemical Tank 1.18.2. Najbezpieczniejszy minimalny transfer to tier, zawartosc `gasTank`, amount/fill ratio oraz `dumping`.

Energy Cube wymaga decyzji o dokladnym przeliczniku J -> target energy/FE. Do czasu potwierdzenia symulacja rekomenduje zachowanie fill ratio.

## Weryfikacja

- `python -m unittest src.converters.mekanism.simulations.test_simulations` - 14 testow OK.
- `python -m src.converters.mekanism.simulations.digital_miner` - OK.
- `python -m src.converters.mekanism.simulations.ore_processing` - OK.
- `python -m src.converters.mekanism.simulations.factory_simulation` - OK.
- `python -m src.converters.mekanism.simulations.storage_frequency` - OK.

## Nastepne kroki

1. [ ] Zadanie 3: napisac kod konwersji dla prostych remapow i specyficznych NBT Mekanism.
2. [ ] W Zadaniu 3 wykorzystac ustalenia z symulacji: `recipeType`, `progress*`, gas -> chemical, fill ratio energii, frequency owner warnings.
3. [ ] Przed pelnym kodem Digital Miner zdekompilowac konkretne klasy `MinerFilter`, bo symulacja obejmuje zachowanie filtrow, ale nie wszystkie warianty serializacji NBT.
