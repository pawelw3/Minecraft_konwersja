# Mekanism - Zadanie 2: symulacje

Zakres: **Mekanism core** 1.7.10 `9.1.1-clienthax` -> 1.18.2 `10.2.5.465`.
Nie obejmuje osobnych modow `MekanismGenerators` i `MekanismTools`.

## Pliki

| Plik | Zakres |
|---|---|
| `ore_processing.py` | Lancuchy ore processing x2/x3/x4/x5 dla 1.7.10 i 1.18.2 |
| `factory_simulation.py` | Factory tier/process count, `recipeType`, `progress0..N`, target block ID |
| `storage_frequency.py` | Energy Cube, Gas Tank -> Chemical Tank, frequency owner/public |
| `digital_miner.py` | Digital Miner range, inverse mode, filters, running reset |
| `test_simulations.py` | Testy porownawcze i smoke testy |

## Zrodla lokalne

- 1.7.10: `modpack_1710/Mekanism-1.7.10-9.1.1-clienthax.jar`
- 1.18.2: `mod_src/118/mod_jars/Mekanism-1.18.2-10.2.5.465.jar`

Istotne wartosci potwierdzone z bytecode:

- `TileEntityFactory`: `BASE_TICKS_REQUIRED = 200`, NBT `recipeType`,
  `recipeTicks`, `progress0`, `progress1`, ...
- `IFactory$RecipeType`: SMELTING=0, ENRICHING=1, CRUSHING=2,
  COMPRESSING=3, COMBINING=4, PURIFYING=5, INJECTING=6, INFUSING=7.
- 1.7.10 factory lanes: BASIC=3, ADVANCED=5, ELITE=7.
- 1.18.2 factory lanes: BASIC=3, ADVANCED=5, ELITE=7, ULTIMATE=9.
- `TileEntityEnergyCube` 1.7.10: BASIC 2M J / 800 out, ADVANCED 8M / 3200,
  ELITE 32M / 12800, ULTIMATE 128M / 51200.
- `TileEntityGasTank` 1.7.10: BASIC 64000, ADVANCED 128000, ELITE 256000,
  ULTIMATE 512000; zapisuje `tier`, `gasTank`, `dumping`.
- `TileEntityDigitalMiner` 1.7.10 zapisuje `radius`, `minY`, `maxY`,
  `doEject`, `doPull`, `running`, `silkTouch`, `inverse`, `filters`.
- `TileEntityDigitalMiner` 1.18.2 zachowuje powyzsze i dodaje
  `inverseReplace`, `replaceStack`.

## Uruchamianie

```powershell
python -m unittest src.converters.mekanism.simulations.test_simulations
```

Mozna tez uruchamiac pojedyncze pliki:

```powershell
python -m src.converters.mekanism.simulations.ore_processing
python -m src.converters.mekanism.simulations.factory_simulation
python -m src.converters.mekanism.simulations.storage_frequency
python -m src.converters.mekanism.simulations.digital_miner
```

## Wnioski dla Zadania 3

1. Factory trzeba mapowac z `recipeType`, nie z samego starego TE ID.
   Stary `UltimateSmeltingFactory` oznacza elite factory 1.7.10, wiec target to
   np. `mekanism:elite_smelting_factory`, nie `ultimate_smelting_factory`.
2. `progress0..N` trzeba przeniesc per lane. Utrata progressu nie niszczy
   itemow, ale potrafi zmienic stan linii produkcyjnej po starcie serwera.
3. Gas Tank 1.7.10 jest semantycznie Chemical Tank w 1.18.2. Konwerter powinien
   migrowac `gasTank` i zachowac `dumping`.
4. Energy Cube najbezpieczniej migrowac przez zachowanie fill ratio, dopoki nie
   zostanie potwierdzony dokladny przelicznik J -> energy/FE dla targetu.
5. Frequency/secuirty z owner name bez UUID powinno generowac warning/event do
   recznej naprawy albo pozniejszego resolvera UUID.
6. Digital Miner uruchomiony w 1.7.10 powinien po konwersji startowac jako
   zatrzymany i z eventem/warningiem do recalculation, bo cache `oresToMine`
   jest pozycjami/chunkami starego swiata.
