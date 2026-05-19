# AE2 Task 5B - headless materialization

## Cel

Zadanie 5B materializuje wynik AE2 5A w dedykowanym swiecie Forge 1.18.2 headless. Poniewaz projekt nie opiera sie jeszcze na bezposrednim writerze `.mca` dla palety modded 1.18.2, materializacja odbywa sie przez datapack z funkcja `/setblock`.

## Artefakty

- Swiat: `headless_server/1.18.2/world_ae2_task5b`
- Datapack: `headless_server/1.18.2/world_ae2_task5b/datapacks/ae2_task5b`
- Funkcja: `data/ae2_task5b/functions/apply.mcfunction`
- Raport JSON: `test_scenarios/ae2_task5a/ae2_task5b_headless_materialization_report.json`
- Smoke JSON: `test_scenarios/ae2_task5a/ae2_task5b_smoke_report.json`
- Konfiguracja serwera: `test_scenarios/ae2_task5a/server_ae2_task5b.properties`
- Backup poprzedniej konfiguracji: `headless_server/1.18.2/server.properties.before_ae2_task5b`

## Wynik materializacji

- Source patch: `ae2_task5a_converted_with_redstone_patch_1182.json`
- Komendy w datapacku: 53
- Edycje blokow: 53
- Edycje block entity NBT: 36
- `te_without_block`: 0
- Odrzucone blockstate properties: 36
- Preflight blokow AE2 przeciw `appliedenergistics2-forge-11.7.6.jar`: OK
- `server.properties` wskazuje obecnie `level-name=world_ae2_task5b`

## Naprawy wykryte przez 5B

- `BlockQuartzGrowthAccelerator` musi mapowac do `ae2:quartz_growth_accelerator`. Wczesniejszy target `ae2:growth_accelerator` nie istnieje w JAR-ze AE2 11.7.6 na headless serverze.
- Generator datapacka filtruje blockstate properties wedlug realnych `assets/ae2/blockstates/*.json`. Dzieki temu properties typu `facing=north`, ktore byly semantyczne w patchu konwertera, ale nie sa poprawnym blockstate dla czesci blokow AE2 11.7.6, nie psuja komend `/setblock`.
- Po kroku 6 `BlockCableBus` materializuje sie jako `ae2:fluix_block` fallback. Native `ae2:cable_bus` bez czesci utworzonych przez API AE2 usuwa sie po starcie serwera.
- Harness redstone zostal skrocony do command blocka przy `100 65 96`, bo dluga linia nie byla potrzebna do testu persystencji AE2.

## Smoke boot

Uruchomiono Forge 1.18.2 headless na `world_ae2_task5b`, datapack wykonal sie na starcie i serwer zostal zatrzymany przez RCON.

- `Done`: TAK
- RCON ready: TAK
- `[AE2_TASK5B] applying converted AE2 5A patch`: TAK
- `[AE2_TASK5B] apply complete`: TAK
- `Failed to load function ae2_task5b:apply`: NIE
- Log smoke: `headless_server/1.18.2/server_ae2_task5b_smoke_20260502_231330_out.log`

Znany szum bazowego swiata nadal wystepuje: `No key old_noise in MapLike[{max_section:20,min_section:-4}]`. Log AE2 pokazal tez ostrzezenie `Cannot deserialize generic key ... key '#c' is missing` przy jednej probce pattern/config; nie zatrzymalo to materializacji i powinno zostac obejrzane w kroku 6 przy weryfikacji NBT po tickach.

## Weryfikacja

```powershell
python -B test_scenarios\ae2_task5a\generate_ae2_task5a.py
python -B test_scenarios\ae2_task5a\convert_applied_test_world.py
python -B -m unittest src.converters.ae2.tests.test_ae2_converter
python -B src\converters\ae2\simulations\step2_contract_simulations.py
$env:PYTHONIOENCODING='utf-8'; python -B src\converters\ae2\verify_coverage.py
python -B test_scenarios\ae2_task5a\materialize_task5b_headless_datapack.py --overwrite
```

## Status po kroku 6

Zadanie 6 przeszlo pelny test headless tick/restart po poprawkach CableBus i harnessa redstone. Szczegoly: `test_scenarios/ae2_task5a/AE2_TASK6_REPORT.md`.
