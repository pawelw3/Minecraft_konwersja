# Mekanism Task 6 - headless tick/restart

## Cel

Zadanie 6 uruchamia zmaterializowany swiat `world_mekanism_task5b` na headless serwerze Forge 1.18.2, aktywuje TEST_START przez RCON, czeka 180 sekund tickow, zapisuje swiat, restartuje serwer bez ponownego wykonania datapacka i sprawdza, czy wybrane block entity Mekanism nadal istnieja z poprawnymi ID.

## Wynik

- Status: PASSED.
- Pierwszy start serwera: OK.
- Materializacja datapacka 5B: OK.
- Redstone PASS marker: OK.
- Czas tickow: 180 sekund.
- TPS po tickach: 20.000.
- Restart serwera: OK.
- Datapack `mekanism_task5b` nie wykonal sie ponownie po restarcie: OK.
- Block entity po restarcie:
  - `mekanism:elite_smelting_factory` at `[118, 64, 108]`: OK.
  - `mekanism:advanced_energy_cube` at `[112, 64, 110]`: OK.
- `Failed to load function mekanism_task5b:apply`: brak.

## Artefakty

- Runner: `run_task6_headless_tick_restart.py`
- Raport JSON: `mekanism_task6_headless_tick_restart_report.json`
- Pierwszy start log: `headless_server/1.18.2/server_mekanism_task6_first_20260502_180413_out.log`
- Restart log: `headless_server/1.18.2/server_mekanism_task6_restart_20260502_180834_out.log`

## Naprawy wykryte przez Task 6

- Harness redstone byl zbyt dlugi dla prostego dust busa. Command block zostal przesuniety z `x=120` na `x=114`, dzieki czemu miesci sie w naturalnym zasiegu sygnalu redstone.
- Command block zapisuje komende bez poczatkowego `/`, czyli `say ...`, co jest bezpieczniejsze dla NBT command blocka.
- Runner Task 6 ignoruje stare markery w `latest.log` i czeka na gotowosc z biezacego stdout procesu serwera.
- Timeout RCON zostal zwiekszony do 30 sekund, bo `datapack disable` wykonuje reload i moze trwac dluzej niz 5 sekund.

## Aktualny harness

- Edycje harnessa: 30.
- Patch scalony Mekanism + redstone: 358 edycji.
- Kolizje blokow: 0.
- Datapack materializacji: 253 komendy, w tym 105 edycji block entity NBT.

## Weryfikacja

```powershell
python -B test_scenarios\mekanism_task5a\generate_mekanism_task5a_full.py
python -B test_scenarios\mekanism_task5a\convert_applied_test_world.py --world lightweigh_map_templates\1710_modded\mekanism_task5a_full_world --source-patch test_scenarios\mekanism_task5a\mekanism_task5a_full_source_patch_1710.json --expected-patch test_scenarios\mekanism_task5a\mekanism_task5a_full_converted_patch_1182.json --out-patch test_scenarios\mekanism_task5a\mekanism_task5a_full_realworld_converted_patch_1182.json --report test_scenarios\mekanism_task5a\mekanism_task5a_full_realworld_conversion_report.json
python -B test_scenarios\mekanism_task5a\generate_redstone_harness_patch.py --spec test_scenarios\mekanism_task5a\mekanism_task5a_full_redstone_spec.json --base-patch test_scenarios\mekanism_task5a\mekanism_task5a_full_realworld_converted_patch_1182.json --out test_scenarios\mekanism_task5a\mekanism_task5a_full_redstone_harness_patch_1182.json --merged-out test_scenarios\mekanism_task5a\mekanism_task5a_full_converted_with_redstone_patch_1182.json --report test_scenarios\mekanism_task5a\mekanism_task5a_full_redstone_harness_report.json
python -B test_scenarios\mekanism_task5a\materialize_task5b_headless_datapack.py --overwrite
python -B test_scenarios\mekanism_task5a\run_task6_headless_tick_restart.py --tick-seconds 180
```

## Uwagi

Po tescie Task 6 datapack `file/mekanism_task5b` jest celowo wylaczony w zapisanym swiecie, zeby restart sprawdzal persystencje chunkow zamiast ponownej materializacji. Aby odtworzyc swiat testowy od zera, uruchom ponownie `materialize_task5b_headless_datapack.py --overwrite`.

Log nadal zawiera znany szum `No key old_noise in MapLike[{max_section:20,min_section:-4}]` z bazowego swiata headless. Nie zablokowal on startu, tickow, zapisu ani restartu.
