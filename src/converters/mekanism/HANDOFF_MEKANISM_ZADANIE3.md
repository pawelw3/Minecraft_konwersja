# Handoff: Mekanism - Zadanie 3

## Podsumowanie sesji

Wykonano Zadanie 3 dla **Mekanism core**: dodano kod konwersji blokow i NBT 1.7.10 -> 1.18.2. Implementacja nie modyfikuje mapy; zwraca `ConversionResult` oraz `ConversionEvent`, ktory moze zostac przekazany do pozniejszego handlera wstawiajacego bloki do mapy 1.18.2.

## Ukonczono

- [x] Dodano mapowania `metadata -> registry ID` dla `MachineBlock`, `MachineBlock2`, `MachineBlock3`, `BasicBlock`, `BasicBlock2`, `OreBlock`, `EnergyCube`, `GasTank`.
- [x] Obsluzono TE ID bez prefiksu, np. `EnrichmentChamber`, `EnergyCube`, `GasTank`, `MekanismTeleporter`.
- [x] Factory mapowane sa po `recipeType`, np. stary `UltimateSmeltingFactory` -> `mekanism:elite_*_factory`.
- [x] Dodano konwersje NBT dla maszyn, factory, Energy Cube, Gas Tank -> Chemical Tank, Bin, Digital Miner, frequency/security i multiblokow.
- [x] Dodano eventy konwersji z source/target/warnings/errors.
- [x] Dodano testy jednostkowe konwertera.

## Nowe pliki

- `src/converters/mekanism/__init__.py`
- `src/converters/mekanism/conversion_event.py`
- `src/converters/mekanism/mappings.py`
- `src/converters/mekanism/mekanism_converter.py`
- `src/converters/mekanism/nbt_converters/__init__.py`
- `src/converters/mekanism/nbt_converters/base_converter.py`
- `src/converters/mekanism/nbt_converters/machine_converters.py`
- `src/converters/mekanism/tests/__init__.py`
- `src/converters/mekanism/tests/test_mekanism_converter.py`
- `src/converters/mekanism/HANDOFF_MEKANISM_ZADANIE3.md`

## Zmodyfikowane pliki

- `HANDOFF.md`
- `src/converters/mekanism/nbt_converters/machine_converters.py` po weryfikacji: odcieto import produkcyjny od symulacji.

## Wazne decyzje

Energy Cube zapisuje `energyContainers` z polityka `preserve_legacy_joules_or_fill_ratio`, bo dokladny przelicznik J -> target energy/FE wymaga pozniejszego potwierdzenia.

Digital Miner po konwersji zawsze dostaje `running=false`, a cache `oresToMine`/`replaceMap` nie jest kopiowany jako aktywny stan. Konwerter przenosi ustawienia (`radius`, `minY`, `maxY`, `filters`, `silkTouch`, `inverse`) i daje warning do recalculation.

Multibloki zachowuja dane uzytkowe, ale cache struktury jest pomijany z warningiem, bo target powinien przeliczyc strukture po starcie.

Copper z Mekanism 1.7.10 mapowany jest do vanilla `minecraft:copper_ore` / `minecraft:copper_block`, zgodnie z ustaleniem z Zadania 1, ze Mekanism 10.2.5 core JAR nie pokazuje wlasnych copper ore/block.

## Weryfikacja

- `python -B -m unittest src.converters.mekanism.tests.test_mekanism_converter` - 12 testow OK.
- `python -B -m unittest src.converters.mekanism.tests.test_mekanism_converter src.converters.mekanism.simulations.test_simulations` - 26 testow OK.
- `python -B -m src.converters.mekanism.simulations.storage_frequency` - OK, bez ostrzezen `runpy`.
- `python -B -m src.converters.mekanism.simulations.ore_processing` - OK.

## Nastepne kroki

1. [ ] Zadanie 4: sprawdzic pokrycie dla stref glownej mapy bez edycji mapy.
2. [ ] W Zadaniu 4 zweryfikowac rzeczywiste NBT z mapy dla EnergyCube/GasTank/Bin/Factory/DigitalMiner.
3. [ ] Przed pelnym wsparciem Digital Miner zdekompilowac `MinerFilter` i doprecyzowac warianty serializacji filtrow.
