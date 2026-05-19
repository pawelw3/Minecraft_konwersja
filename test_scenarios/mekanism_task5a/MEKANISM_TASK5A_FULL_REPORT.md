# Mekanism Task 5A - pelny raport

Zakres: **Mekanism core** 1.7.10 -> 1.18.2. Mekanism Generators i Mekanism Tools sa poza tym modulem konwertera.

## Status

**Zadanie 5A dla Mekanism core: wykonane.**

Zgodnie z `docs/PLAN.md` wykonano:

- testowa mape 1.7.10 z blokami i BE Mekanism core,
- kombinacje BE z roznymi metadanymi, tierami, inventory, energia, gazem/fluidem, frequency, cache i factory `recipeType`,
- zapis do `.mca` przez Kotlin/Hephaistos zgodnie z `skills/mca-sections`,
- konwersje kodem konwertera na patch 1.18.2,
- test redstone do pozniejszego odpalenia na headless serwerze zgodnie z `skills/integration_test_with_redstone`.

## Liczby

- Sample w pelnym scenariuszu: 224.
- Unikalne warianty source `block:metadata`: 178.
- Sample z NBT/BE: 104.
- Edycje patcha source 1.7.10: 328.
- Edycje patcha target 1.18.2: 328.
- Edycje patcha scalonego target + redstone: 358.
- Zweryfikowane bloki w realnym `.mca`: 224.
- Zweryfikowane Tile Entities w realnym `.mca`: 104.
- Zweryfikowane zagniezdzone klucze TE: 142.
- Bledy zapisu/odczytu/konwersji: 0.
- Kolizje harnessa redstone z blokami Mekanism: 0.

## Dodatkowe luki wykryte i zamkniete

Pelny scenariusz wykryl bloki obecne w dynamicznym rejestrze `mapa_1710/level.dat`, ktore nie wystapily w strefach kroku 4:

- `Mekanism:CardboardBox`
- `Mekanism:GlowPlasticBlock`
- `Mekanism:ReinforcedPlasticBlock`
- `Mekanism:PlasticFence`
- `Mekanism:MachineBlock3:2` (`AmbientAccumulator`)

Dodano dla nich mapowania w `src/converters/mekanism/mappings.py`.

## Artefakty

- `generate_mekanism_task5a_full.py` - generator pelnego scenariusza 5A.
- `mekanism_task5a_full_source_patch_1710.json` - source patch 1.7.10.
- `mekanism_task5a_full_converted_patch_1182.json` - oczekiwany patch 1.18.2 z konwertera.
- `mekanism_task5a_full_conversion_report.json` - raport konwersji wszystkich probek.
- `mekanism_task5a_full_world_verify_report.json` - read-back realnego `.mca`.
- `mekanism_task5a_full_realworld_converted_patch_1182.json` - patch 1.18.2 wygenerowany z realnie zapisanej mapy.
- `mekanism_task5a_full_realworld_conversion_report.json` - porownanie real-world conversion z oczekiwanym patchem.
- `mekanism_task5a_full_redstone_spec.json` - spec testu redstone.
- `mekanism_task5a_full_redstone_harness_patch_1182.json` - patch harnessa redstone.
- `mekanism_task5a_full_converted_with_redstone_patch_1182.json` - patch scalony.
- `mekanism_task5a_full_redstone_harness_report.json` - raport harnessa.

Mapa testowa:

- `lightweigh_map_templates/1710_modded/mekanism_task5a_full_world`

## Weryfikacja wykonana

```powershell
python -B test_scenarios\mekanism_task5a\generate_mekanism_task5a_full.py
java -jar jvm\worker\build\libs\mc-editkit-worker-1.0-SNAPSHOT.jar --world lightweigh_map_templates\1710_modded\mekanism_task5a_full_world --patch test_scenarios\mekanism_task5a\mekanism_task5a_full_source_patch_1710.json
python -B test_scenarios\mekanism_task5a\verify_mekanism_task5a_world.py --world lightweigh_map_templates\1710_modded\mekanism_task5a_full_world --patch test_scenarios\mekanism_task5a\mekanism_task5a_full_source_patch_1710.json --report test_scenarios\mekanism_task5a\mekanism_task5a_full_world_verify_report.json
python -B test_scenarios\mekanism_task5a\convert_applied_test_world.py --world lightweigh_map_templates\1710_modded\mekanism_task5a_full_world --source-patch test_scenarios\mekanism_task5a\mekanism_task5a_full_source_patch_1710.json --expected-patch test_scenarios\mekanism_task5a\mekanism_task5a_full_converted_patch_1182.json --out-patch test_scenarios\mekanism_task5a\mekanism_task5a_full_realworld_converted_patch_1182.json --report test_scenarios\mekanism_task5a\mekanism_task5a_full_realworld_conversion_report.json
python -B test_scenarios\mekanism_task5a\generate_redstone_harness_patch.py --spec test_scenarios\mekanism_task5a\mekanism_task5a_full_redstone_spec.json --base-patch test_scenarios\mekanism_task5a\mekanism_task5a_full_realworld_converted_patch_1182.json --out test_scenarios\mekanism_task5a\mekanism_task5a_full_redstone_harness_patch_1182.json --merged-out test_scenarios\mekanism_task5a\mekanism_task5a_full_converted_with_redstone_patch_1182.json --report test_scenarios\mekanism_task5a\mekanism_task5a_full_redstone_harness_report.json
python -B -m unittest src.converters.mekanism.tests.test_mekanism_converter src.converters.mekanism.simulations.test_simulations
python -B src\converters\mekanism\analyze_map_coverage.py
```

## Granica 5A

Ten krok konczy sie na pelnej mapie testowej 1.7.10, konwersji tej mapy do patcha 1.18.2 i przygotowanym redstone harness do pozniejszego odpalenia. Fizyczne zapisanie patcha 1.18.2 do swiata i uruchomienie headless serwera nalezy do nastepnych krokow 5B/6.
