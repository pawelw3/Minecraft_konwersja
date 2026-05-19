# Handoff: Mekanism - Zadanie 1

## Podsumowanie sesji

Wykonano dogłębne Zadanie 1 dla **Mekanism core**: lista bloków, Tile Entities / Block Entities, registry names oraz porównanie 1.7.10 -> 1.18.2. Analiza celowo nie obejmuje osobnych modów **Mekanism Generators** i **Mekanism Tools**.

## Ukończono

- [x] Zweryfikowano źródła lokalne dla 1.7.10 i 1.18.2.
- [x] Wykryto, że lokalny checkout Mekanism pod ścieżką 1.18.2 był błędną nowszą wersją; po późniejszym cleanupie został usunięty.
- [x] Użyto JAR-a `mod_src/118/mod_jars/Mekanism-1.18.2-10.2.5.465.jar` jako źródła prawdy dla targetu 1.18.2.
- [x] Wyciągnięto dokładne registry stringi Tile Entities 1.7.10 z `CommonProxy` przez `javap`.
- [x] Opisano stare grupy bloków `MachineBlock`, `MachineBlock2`, `MachineBlock3`, `BasicBlock`, `BasicBlock2` wraz z metadata.
- [x] Opisano docelowe rodziny bloków/BE 1.18.2: machines, factories, tanks, bins, multiblocks, transmitters, QIO/SPS.
- [x] Wskazano najważniejsze ryzyka dla kolejnych zadań: factories, frequency/security, gas -> chemical, Digital Miner, multibloki.

## Nowe pliki

- `src/converters/mekanism/MEKANISM_ZADANIE1_ANALIZA.md`
- `src/converters/mekanism/HANDOFF_MEKANISM_ZADANIE1.md`

## Zmodyfikowane pliki

- Brak modyfikacji istniejących plików.

## Kluczowe ustalenia

Tile Entity ID w Mekanism 1.7.10 są bez prefiksu moda, np. `Crusher`, `EnergyCube`, `MekanismTeleporter`, `SalinationController`. To jest krytyczne dla skanowania mapy, bo wyszukiwanie po `Mekanism:` pominie TE.

Mekanism 1.7.10 grupuje wiele bloków w kilka registry ID z metadata, np. `Mekanism:MachineBlock:0` to Enrichment Chamber, a `Mekanism:MachineBlock2:6` to Chemical Dissolution Chamber. Mekanism 1.18.2 ma osobne registry ID, np. `mekanism:enrichment_chamber`, `mekanism:chemical_dissolution_chamber`.

## Następne kroki

1. [ ] Zadanie 2: przygotować symulacje działania dla najważniejszych mechanik Mekanism.
2. [ ] Przed Zadaniem 2 zdobyć/dekompilować dokładne źródła Mekanism **10.2.5 / 1.18.2**, bo obecny folder `actual_src` jest złą wersją.
3. [ ] Priorytet symulacji: ore processing x2-x5, factories, tanks, energy cubes, Digital Miner, frequency blocks.
4. [ ] Osobno później zrobić Zadanie 1 dla `MekanismGenerators` i `MekanismTools`, jeśli mają być konwertowane jako oddzielne unity.
