# Railcraft Task 6 – Headless Tick/Restart Test

## Cel

Sprawdzenie czy przekonwertowane bloki Railcraft są stabilne po 3 minutach ticków i po restarcie serwera Forge 1.18.2.

## Artefakty

- Runner: `test_scenarios/railcraft_task5a/run_task6_headless_tick_restart.py`
- Raport JSON: `test_scenarios/railcraft_task5a/railcraft_task6_headless_tick_restart_report.json`
- Log pierwszego startu: `headless_server/1.18.2/server_railcraft_task6_first_*.log`
- Log restartu: `headless_server/1.18.2/server_railcraft_task6_restart_*.log`

## Przebieg testu

| Faza | Wynik | Szczegóły |
|------|-------|-----------|
| Pierwszy start serwera | ✅ | `Done` w ~22s, RCON ready |
| Manual apply datapacka | ✅ | `Executed 67 commands` |
| Forceload chunków | ✅ | `forceload add 192 192 336 208` |
| Post-apply check | ✅ | 10/10 bloków OK |
| 180 sekund ticków | ✅ | Serwer stabilny |
| After-ticks check | ✅ | 10/10 bloków OK |
| TPS | ✅ | ~20 TPS (Mean tick time ~50ms) |
| `save-all flush` | ✅ | Zapis OK |
| Wyłączenie datapacka | ✅ | `datapack disable file/railcraft_task5b` |
| Restart serwera | ✅ | `Done` w ~6s, RCON ready |
| Post-restart check | ✅ | 10/10 bloków OK |
| Final stop | ✅ | Graceful shutdown |

## Sprawdzone bloki (SUT)

| Nazwa | Pozycja | Oczekiwany blok | Post-apply | After-ticks | After-restart |
|-------|---------|-----------------|------------|-------------|---------------|
| mechanical_press | 212, 64, 200 | create:mechanical_press | ✅ | ✅ | ✅ |
| crushing_wheel | 214, 64, 200 | create:crushing_wheel | ✅ | ✅ | ✅ |
| campfire | 216, 64, 200 | minecraft:campfire | ✅ | ✅ | ✅ |
| smoker | 218, 64, 200 | minecraft:smoker | ✅ | ✅ | ✅ |
| steam_engine | 232, 64, 200 | create:steam_engine | ✅ | ✅ | ✅ |
| fluid_tank | 238, 64, 200 | create:fluid_tank | ✅ | ✅ | ✅ |
| observer | 294, 64, 200 | minecraft:observer | ✅ | ✅ | ✅ |
| comparator | 284, 64, 200 | minecraft:comparator | ✅ | ✅ | ✅ |
| framed_slab | 312, 64, 200 | framedblocks:framed_slab | ✅ | ✅ | ✅ |
| air | 320, 64, 200 | minecraft:air | ✅ | ✅ | ✅ |

## Log findings

- `No key old_noise in MapLike[{max_section:20,min_section:-4}]` — znany szum bazowego świata, niekrytyczny
- `Unknown item 'patchouli:guide_book'` / `emendatusenigmatica:enigmatic_hammer` — brakujące dependency innych modów, niekrytyczne
- `Unidentified mapping from registry minecraft:item` — pojawiło się przy jednym z wcześniejszych runów, nie wystąpiło w finalnym teście
- Datapack nie reaplikował się po restarcie (marker `apply_complete` wystąpił tylko 1 raz)

## Problemy rozwiązane w trakcie Task 6

| Problem | Przyczyna | Rozwiązanie |
|---------|-----------|-------------|
| Chunki niezaładowane przy check | Serwer headless nie ładuje chunków bez gracza | Dodano `/forceload add` + 8s delay przed check |
| `execute if block` bez `run` | W Forge 1.18.2 zwraca `Test passed\n` przez RCON | Użyto oryginalnej komendy bez `run say` |

## Weryfikacja

```powershell
python -B test_scenarios\railcraft_task5a\run_task6_headless_tick_restart.py --tick-seconds 180
```

## Status

**PASSED** — wszystkie 10 sprawdzonych bloków Railcraft przetrwały 180 sekund ticków i restart serwera Forge 1.18.2.
