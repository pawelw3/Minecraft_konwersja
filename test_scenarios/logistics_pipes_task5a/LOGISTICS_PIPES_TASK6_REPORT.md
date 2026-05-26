# Logistics Pipes Task 6 Report

## Podsumowanie
Uruchomiono headless serwer 1.18.2 na `world_logistics_pipes_task5b`, recznie wykonano funkcje datapacka `logistics_pipes_task5b:apply`, odczekano 180 sekund tickow, zapisano swiat i wykonano restart verification.

## Wynik
- Status: `passed`
- Overall pass: `true`
- First boot: ready, RCON ready
- Datapack apply: `Executed 15 commands from function 'logistics_pipes_task5b:apply'`
- Apply marker: znaleziony
- Tick wait: 180 sekund
- Restart: ready, RCON ready
- Stop: graceful, return code 0

## Walidacja blokow
- Po apply: 13/13 blokow zgodnych, 13/13 block entities z danymi.
- Po tickach: 13/13 blokow zgodnych, 13/13 block entities z danymi.
- Po restarcie: 13/13 blokow zgodnych, 13/13 block entities z danymi.
- Brak relevant errors dla Pretty Pipes / Logistics Pipes datapack / AE2 pattern provider / placeholder.
- Brak `Unknown block`, brak `Skipping BlockEntity`, brak crasha.

## Zweryfikowane targety
- `prettypipes:pipe`
- `prettypipes:item_terminal`
- `prettypipes:pressurizer`
- `ae2:pattern_provider`
- `conversion_placeholders:block_entity_placeholder`

## Pliki
- `test_scenarios/logistics_pipes_task5a/run_task6_headless_tick_restart.py`
- `test_scenarios/logistics_pipes_task5a/logistics_pipes_task6_headless_tick_restart_report.json`
- `test_scenarios/logistics_pipes_task5a/LOGISTICS_PIPES_TASK6_REPORT.md`
- Log first boot: `headless_server/1.18.2/server_logistics_pipes_task6_first_20260526_222119_out.log`
- Log restart: `headless_server/1.18.2/server_logistics_pipes_task6_restart_20260526_222645_out.log`

## Uwagi
- `server.properties` zostal ustawiony na `level-name=world_logistics_pipes_task5b`.
- Backup poprzedniego pliku: `headless_server/1.18.2/server.properties.before_logistics_pipes_task6`.

## Nastepny krok
1. [ ] Przejsc do kolejnego zadania po Task 6 dla Logistics Pipes: albo dopracowanie realnego extractora modulow chassis z mapy, albo rozpoczecie kolejnego moda wedlug planu.
