# BuildCraft Task 5B - Headless Materialization Report

## Cel

Zadanie 5B materializuje wynik BuildCraft 5A w dedykowanym swiecie Forge 1.18.2 headless.
Materializacja odbywa sie przez datapack z funkcja `/setblock`.

## Artefakty

- Swiat: `headless_server/1.18.2/world_buildcraft_task5b`
- Datapack: `headless_server/1.18.2/world_buildcraft_task5b/datapacks/buildcraft_task5b`
- Funkcja: `data/buildcraft_task5b/functions/apply.mcfunction`
- Custom recipe: `data/buildcraft_conversion/recipes/machines/refinery/bc_oil_to_fuel.json`
- Raport JSON: `test_scenarios/buildcraft_task5a/buildcraft_task5b_headless_materialization_report.json`
- Konfiguracja serwera: `test_scenarios/buildcraft_task5a/server_buildcraft_task5b.properties`

## Wynik materializacji

- Source patch: `buildcraft_task5a_converted_patch_1182.json`
- Komendy w datapacku: 12
- Edycje blokow: 12
- Edycje block entity NBT: 5
- `te_without_block`: 0
- Recipe copied: `bc_oil_to_fuel.json` (thermal:refinery crude_oil -> refined_fuel)

## Naprawy wykryte przez 5B

1. **`thermal:dynamo_steam` nie istnieje** w `thermal_expansion-1.18.2-9.2.2.24.jar`.
   Poprawny block ID to **`thermal:dynamo_stirling`**.
   Zmieniono w `src/converters/buildcraft/mappings/block_mappings.py` oraz w patchu 5A.

2. **Numeryczne ID przedmiotow** (`id: 263` = coal) w NBT silnikow:
   Skrypt materializujacy `materialize_buildcraft_task5b.py` zawiera mapping
   `263 -> "minecraft:coal"` i zamienia je przed generowaniem SNBT.

3. **Pipez mod** dodany recznie na serwer (`pipez-1.18.2-1.1.5.jar`).
   Wczesniej plik w `mod_src/` okazal sie CurseForge packiem, nie modem.
   Uzytkownik dostarczyl prawdziwy mod; `pipez:universal_pipe` dziala poprawnie.

## Smoke boot (pierwszy start)

Uruchomiono Forge 1.18.2 headless na `world_buildcraft_task5b`, datapack wykonal sie na starcie.

- `Done`: TAK (5.714s)
- RCON ready: TAK (port 25581)
- `[BUILDCRAFT_TASK5B] apply complete`: TAK
- Bledy setblock: BRAK
- Bledy ladowania funkcji: BRAK

## Restart verification

Uruchomiono ponownie serwer w celu weryfikacji stabilnosci.

- `Done`: TAK (5.108s)
- `[BUILDCRAFT_TASK5B] apply complete`: TAK
- Bledy setblock: BRAK

## Nastepne kroki (Task 6)

1. [ ] Pobrac i zainstalowac prawdziwy mod Pipez 1.18.2 na headless serwer.
2. [ ] Zweryfikowac custom recipe refinery w grze (`/recipe give` lub JEI).
3. [ ] Opcjonalnie: wykonac dluzszy test tickow (3 min) z RCON monitoringiem.
4. [ ] Uaktualnic block_mappings.py jesli znaleziono inne bledne ID.
