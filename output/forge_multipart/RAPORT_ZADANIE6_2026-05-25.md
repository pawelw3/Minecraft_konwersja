# ForgeMultipart / CBMultipart - Zadanie 6

## Cel
Uruchomic headless Forge 1.18.2 z przekonwertowana mapa, odczekac 180 sekund tickow, zapisac swiat, zrestartowac serwer i sprawdzic trwalosc multipartow.

## Wynik
- Status: PASS.
- Pierwszy start serwera: OK.
- Datapack 5B wykonany: OK.
- TPS po 180 sekundach: 20.000 overall.
- Pozycje sprawdzone przed tickami: 15/15 `cb_multipart:multipart`, 15/15 BlockEntity.
- Pozycje sprawdzone po 180 sekundach: 15/15 `cb_multipart:multipart`, 15/15 BlockEntity.
- Pozycje sprawdzone po restarcie: 15/15 `cb_multipart:multipart`, 15/15 BlockEntity.

## Pliki
- `test_scenarios/forge_multipart_task5a/run_forge_multipart_task6_headless.py`
- `test_scenarios/forge_multipart_task5a/forge_multipart_task6_headless_report.json`
- `headless_server/1.18.2/server_forge_multipart_task6_first_20260525_031402_out.log`
- `headless_server/1.18.2/server_forge_multipart_task6_restart_20260525_031843_out.log`

## Komenda
- `python test_scenarios\forge_multipart_task5a\run_forge_multipart_task6_headless.py --tick-seconds 180`

## Uwagi
Pierwszy przebieg Task 6 po dopisaniu harnessu mial falszywy FAIL, bo runner sprawdzal dwie pozycje, ktorych nie bylo w evencie testowym. Runner zostal poprawiony tak, aby bral pozycje bezposrednio z `output/forge_multipart/task5a_events_1182.json`; drugi pelny przebieg zakonczyl sie sukcesem.
