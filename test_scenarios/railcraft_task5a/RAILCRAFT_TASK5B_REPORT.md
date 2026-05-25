# Railcraft Task 5B – Headless Server Materialization

## Cel

Zmaterializować przekonwertowane bloki Railcraft (66 sample'ów) na Forge 1.18.2 headless serwerze poprzez datapack z komendami `/setblock`.

## Artefakty

- Świat: `headless_server/1.18.2/world_railcraft_task5b`
- Datapack: `headless_server/1.18.2/world_railcraft_task5b/datapacks/railcraft_task5b`
- Funkcja: `data/railcraft_task5b/functions/apply.mcfunction`
- Raport JSON: `test_scenarios/railcraft_task5a/railcraft_task5b_headless_materialization_report.json`
- Konfiguracja serwera: `test_scenarios/railcraft_task5a/server_railcraft_task5b.properties`

## Wynik materializacji

- Source patch: `railcraft_task5a_converted_patch_1182.json`
- Komendy w datapacku: 67
- Edycje bloków: 66
- Edycje block entity NBT: 0
- Fallback blocks (placeholder): 6

## Modu zainstalowane na serwerze

| Mod | Status |
|-----|--------|
| Create | ✅ Zainstalowany (create-1.18.2-0.5.1.c.jar) |
| FramedBlocks | ✅ Zainstalowany (FramedBlocks-5.11.5.jar) |
| Iron Chests | ✅ Zainstalowany (ironchest-1.18.2-13.2.11.jar) |
| Mekanism | ✅ Już był |
| Thermal Series | ✅ Już był |
| conversion_placeholders | ✅ Już był |
| Immersive Engineering | ❌ Brak – fallback na placeholder |
| Steam'n'Rails (railways) | ❌ Brak – fallback na placeholder |

## Problemy napotkane i rozwiązania

| Problem | Przyczyna | Rozwiązanie |
|---------|-----------|-------------|
| Funkcja datapacka się nie ładowała | Placeholder block nie ma property `shape` (track conversions) | W `materialize_railcraft_task5b.py` usunięto blockstate properties dla `conversion_placeholders:*` |
| Funkcja datapacka się nie ładowała | FramedBlocks 5.11.5 nie używa blockstate properties dla slab/stair | W `materialize_railcraft_task5b.py` usunięto blockstate properties dla `framedblocks:*` |

## Smoke boot

Uruchomiono Forge 1.18.2 headless na `world_railcraft_task5b`, datapack wykonany przez RCON `/function railcraft_task5b:apply` i serwer działa stabilnie.

- `Done`: TAK (22.813s)
- RCON ready: TAK (port 25581)
- `[RAILCRAFT_TASK5B] apply complete`: TAK
- `Executed 67 commands`: TAK
- `Failed to load function`: NIE (po naprawie)
- Błędy setblock: BRAK

Znany szum bazowego świata nadal występuje: `No key old_noise in MapLike[{max_section:20,min_section:-4}]`.
Błędy FTBIC związane z brakiem `myrtrees` są niekrytyczne.

## Status

Task 5B zakończony sukcesem. Wszystkie 66 przekonwertowanych bloków Railcraft zostały pomyślnie załadowane na headless serwerze Forge 1.18.2.
