# Mekanism Task 5B - headless materialization

## Cel

Zadanie 5B materializuje pelny wynik 5A w swiecie headless 1.18.2. Poniewaz projekt nie ma jeszcze bezposredniego writera `.mca` dla palety 1.18.2, materializacja odbywa sie przez dedykowany swiat serwera i datapack z funkcja `/setblock`.

## Artefakty

- Swiat: `headless_server/1.18.2/world_mekanism_task5b`
- Datapack: `headless_server/1.18.2/world_mekanism_task5b/datapacks/mekanism_task5b`
- Funkcja: `data/mekanism_task5b/functions/apply.mcfunction`
- Raport JSON: `mekanism_task5b_headless_materialization_report.json`
- Konfiguracja serwera: `server_mekanism_task5b.properties`
- Backup poprzedniej konfiguracji: `headless_server/1.18.2/server.properties.before_mekanism_task5b`

## Wynik materializacji

- Source patch: `mekanism_task5a_full_converted_with_redstone_patch_1182.json`
- Komendy w datapacku: 253
- Edycje blokow: 253
- Edycje block entity NBT: 105
- Edycje patcha scalonego: 358
- `te_without_block`: 0
- Preflight blokow Mekanism przeciw `Mekanism-1.18.2-10.2.0.459.jar`: OK

## Naprawy wykryte przez 5B

- W generatorze datapacka usunieto blockstate properties z blokow `mekanism:*`, bo czesc orientacji konwertera nie jest w tej wersji zarejestrowana jako property bloku.
- `Mekanism:BoundingBlock` meta `1` mapuje teraz do `mekanism:bounding_block`, bo serwer 1.18.2 nie rejestruje `mekanism:advanced_bounding_block` jako poprawnego typu bloku dla komend.

## Smoke boot

Uruchomiono Forge 1.18.2 headless na `world_mekanism_task5b`.

- `Done`: TAK
- `[MEKANISM_TASK5B] apply complete`: TAK
- `Failed to load function mekanism_task5b:apply`: NIE
- Log smoke: `headless_server/1.18.2/server_task5b_smoke_20260502_172422_out.log`

Pozostaje znany szum bazowego swiata: log zawiera `No key old_noise in MapLike[{max_section:20,min_section:-4}]` podczas ladowania chunkow. Nie blokuje to startu serwera ani wykonania datapacka.

## Weryfikacja

```powershell
python -B test_scenarios\mekanism_task5a\generate_mekanism_task5a_full.py
python -B -m unittest src.converters.mekanism.tests.test_mekanism_converter src.converters.mekanism.simulations.test_simulations
python -B test_scenarios\mekanism_task5a\convert_applied_test_world.py --world lightweigh_map_templates\1710_modded\mekanism_task5a_full_world --source-patch test_scenarios\mekanism_task5a\mekanism_task5a_full_source_patch_1710.json --expected-patch test_scenarios\mekanism_task5a\mekanism_task5a_full_converted_patch_1182.json --out-patch test_scenarios\mekanism_task5a\mekanism_task5a_full_realworld_converted_patch_1182.json --report test_scenarios\mekanism_task5a\mekanism_task5a_full_realworld_conversion_report.json
python -B test_scenarios\mekanism_task5a\generate_redstone_harness_patch.py --spec test_scenarios\mekanism_task5a\mekanism_task5a_full_redstone_spec.json --base-patch test_scenarios\mekanism_task5a\mekanism_task5a_full_realworld_converted_patch_1182.json --out test_scenarios\mekanism_task5a\mekanism_task5a_full_redstone_harness_patch_1182.json --merged-out test_scenarios\mekanism_task5a\mekanism_task5a_full_converted_with_redstone_patch_1182.json --report test_scenarios\mekanism_task5a\mekanism_task5a_full_redstone_harness_report.json
python -B test_scenarios\mekanism_task5a\materialize_task5b_headless_datapack.py --overwrite
```

Wyniki:

- 224/224 probki skonwertowane z realnego swiata testowego.
- 0 mismatches wzgledem oczekiwanego patcha.
- 28/28 unit testow Mekanism OK.
- Smoke boot headless OK.

## Nastepny krok

Zadanie 6 zostalo wykonane. Szczegoly: `MEKANISM_TASK6_REPORT.md`.
