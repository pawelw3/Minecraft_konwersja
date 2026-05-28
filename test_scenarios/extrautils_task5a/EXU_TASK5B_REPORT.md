# Extra Utilities Task 5B – raport

Zakres: materializacja przekonwertowanej mapy Extra Utilities na headless serwerze Forge 1.18.2.

## Status

**Zadanie 5B dla Extra Utilities: wykonane.**

## Liczby

- Komendy `/setblock` w datapacku: 27.
- Bloki konwertowane bezpośrednio (mody dostępne na serwerze): 16.
- Bloki fallback do placeholdera (brak modów na serwerze): 11.
- Brakujące mody na headless serwerze: Torchmaster, Cursed Earth, Angel Block Renewed, Trash Cans, Extreme Sound Muffler.
- Tile Entities z NBT w komendach: 19.

## Pobrane mody

Pobrano i zainstalowano 5 brakujących modów na headless serwer 1.18.2:

| Mod | Źródło | Plik |
|-----|--------|------|
| Torchmaster | Modrinth | `torchmaster-18.2.1.jar` |
| Trash Cans | Modrinth | `trashcans-1.0.18-forge-mc1.18.jar` |
| Angel Block Renewed | Modrinth | `angelblockrenewed-forge-1.3-1.18.2.jar` |
| Extreme Sound Muffler | Modrinth | `extremesoundmuffler-3.30_forge-1.18.2.jar` |
| Cursed Earth | CurseForge CDN | `cursedearth.jar` |

**Uwaga:** Extreme Sound Muffler w 1.18.2 to mod **client-side only** — nie rejestruje bloku `extremesoundmuffler:sound_muffler`. Pozostaje fallback do placeholdera.

## Poprawki wykryte i zamknięte

Podczas Task 5B wykryto błędy w mapowaniu:

1. `thermal:dynamo_alchemical` — blok ten **nie istnieje** w Thermal Expansion 1.18.2. Poprawiono mapowanie Potion Generator (meta 6) na `thermal:dynamo_compression` (istniejący dynamo obsługujący płynne paliwa).
2. `torchmaster:mega_torch` — blok w 1.18.2 to `torchmaster:megatorch` (bez underscore). Poprawiono mapowanie Magnum Torch.

## Artefakty

- `test_scenarios/extrautils_task5a/materialize_extrautils_task5b.py` – generator datapacka i kopii świata.
- `test_scenarios/extrautils_task5a/extrautils_task5b_headless_materialization_report.json` – raport materializacji.
- `headless_server/1.18.2/world_extrautils_task5b` – przygotowany świat z datapackiem.
- `headless_server/1.18.2/world_extrautils_task5b/datapacks/extrautils_task5b` – datapack z funkcją `apply.mcfunction`.
- `test_scenarios/extrautils_task5a/server_extrautils_task5b.properties` – template `server.properties`.

## Następne kroki

1. Skopiować `server_extrautils_task5b.properties` do `headless_server/1.18.2/server.properties`.
2. Uruchomić serwer Forge 1.18.2.
3. Zweryfikować w logach `[EXU_TASK5B] apply complete`.
4. Kontynuować Zadaniem 6 – tick/restart verification.
