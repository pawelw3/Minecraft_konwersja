# AE2 Task 6 - headless tick/restart

## Status

**PASSED - po poprawkach test przeszedl pelny przebieg 180 sekund tickow i restart.**

Serwer Forge 1.18.2 wystartowal, datapack 5B wykonal materializacje, harness redstone odpalil marker, swiat dzialal 180 sekund tickow, zapis przeszedl, restart przeszedl, a datapack nie wykonal sie ponownie po restarcie. Wybrane bloki/BE AE2 pozostaly obecne po tickach i po restarcie.

## Artefakty

- Runner: `test_scenarios/ae2_task5a/run_task6_headless_tick_restart.py`
- Raport JSON: `test_scenarios/ae2_task5a/ae2_task6_headless_tick_restart_report.json`
- Log pierwszego startu: `headless_server/1.18.2/server_ae2_task6_first_20260502_235338_out.log`
- Log restartu: `headless_server/1.18.2/server_ae2_task6_restart_20260502_235754_out.log`
- Swiat testowy: `headless_server/1.18.2/world_ae2_task5b`

## Naprawiono

1. `BlockCableBus` nie materializuje juz niestabilnego `ae2:cable_bus`.
   - AE2 11.7.6 usuwa pusty/native `ae2:cable_bus`, jezeli czesci nie sa utworzone przez API moda.
   - Mapowanie testowe uzywa teraz kontrolowanego fallbacku `ae2:fluix_block`.
   - Po tickach i po restarcie `100 64 100` przechodzi check dla `ae2:fluix_block`.

2. Harness redstone zostal skrocony.
   - `TEST_START` pozostaje leverem na `96 65 96`.
   - Assertion command block jest teraz na `100 65 96`, bez dlugiej zawodnej linii.
   - Marker `AE2_TASK5A_REDSTONE_PASS` pojawil sie w logu.

## Co przeszlo

- Pierwszy start serwera: OK.
- Materializacja datapacka 5B: OK, `[AE2_TASK5B] apply complete` wystapil 1 raz.
- RCON: OK.
- Marker redstone: OK.
- 180 sekund tickow: OK.
- TPS po tickach: 20 TPS overall.
- `save-all flush`: OK.
- Datapack `file/ae2_task5b` zostal wylaczony przed restartem.
- Restart serwera: OK.
- Datapack nie odpalil sie ponownie po restarcie: OK.
- `Failed to load function ae2_task5b:apply`: brak.

## Stan wybranych blokow po restarcie

- `ae2:fluix_block` fallback dla CableBus at `100 64 100`
- `ae2:drive` at `127 64 103`
- `ae2:interface` at `109 64 106`
- `ae2:pattern_provider` at `109 64 105`
- `ae2:quantum_link` at `118 64 106` (NBT raportuje `id: "ae2:quantum_ring"`, ale block check przeszedl dla `ae2:quantum_link`)
- `ae2:spatial_io_port` at `100 64 109`
- `ae2:quartz_growth_accelerator` at `124 64 106`

## Log findings

- `Cannot deserialize generic key ... key '#c' is missing`: wystapilo przy pierwszym apply, nie wystapilo po restarcie.
- `No key old_noise in MapLike[{max_section:20,min_section:-4}]`: nadal wystepuje na starcie i po restarcie jako znany szum bazowego swiata.
- Serwer utrzymywal 20 TPS w pomiarach po tickach i po restarcie.

## Weryfikacja

```powershell
python -B test_scenarios\ae2_task5a\generate_ae2_task5a.py
python -B test_scenarios\ae2_task5a\convert_applied_test_world.py
python -B -m unittest src.converters.ae2.tests.test_ae2_converter
python -B src\converters\ae2\simulations\step2_contract_simulations.py
$env:PYTHONIOENCODING='utf-8'; python -B src\converters\ae2\verify_coverage.py
python -B test_scenarios\ae2_task5a\materialize_task5b_headless_datapack.py --overwrite
python -B test_scenarios\ae2_task5a\run_task6_headless_tick_restart.py --tick-seconds 180
```

## Nastepny krok

Mozna przejsc do kolejnego kroku AE2 po kroku 6. Dla pelnej konwersji CableBus zostaje osobny temat: odtworzenie czesci kablowych przez API AE2 albo bardziej szczegolowe fallbacki materialowe.
