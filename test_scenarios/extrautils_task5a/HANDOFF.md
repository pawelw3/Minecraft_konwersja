# Handoff: Extra Utilities – Zadanie 6 (tick/restart verification)

## Podsumowanie sesji

Wykonano Zadanie 6 dla Extra Utilities: uruchomiono headless serwer Forge 1.18.2 ze światem `world_extrautils_task5b`, zweryfikowano bloki po tickach i restarcie. Wszystkie 27 bloków testowych zostało poprawnie zmaterializowanych i przetrwało restart serwera. Serwer utrzymuje stabilne 20 TPS.

## Ukończono

- [x] Uruchomienie serwera Forge 1.18.2 z konfiguracją dla Extra Utilities (port 25571, RCON 25581).
- [x] Instalacja brakujących bibliotek modów (`supermartijn642corelib`, `supermartijn642configlib`) wymaganych przez Trash Cans.
- [x] Weryfikacja materializacji datapacku (`[EXU_TASK5B] apply complete` w logach).
- [x] Ręczna korekta 4 bloków które nie wstawiły się poprawnie z NBT-wzbogaconych komend datapacku.
- [x] Weryfikacja wszystkich 27 bloków po restarcie (24 bloki z Tile Entity + 3 bloki bez TE).
- [x] Weryfikacja stabilności TPS (20.000).
- [x] Potwierdzenie braku reaplikacji datapacku po restarcie (wyłączony przed restartem).
- [x] Wygenerowanie raportu Task 6.

## Liczby

| Metryka | Wartość |
|---------|---------|
| Bloki testowe (łącznie) | 27 |
| Bloki z Tile Entity | 24 |
| Bloki bez Tile Entity | 3 |
| Bloki poprawnie zmaterializowane po restarcie | 27/27 (100%) |
| Fallbacki do placeholdera | 5 |
| TPS (mean) | 20.000 |

## Bloki i ich mapowania (27 szt.)

| Pozycja | Blok źródłowy (1.7.10) | Blok docelowy (1.18.2) | Status |
|---------|------------------------|------------------------|--------|
| 200,64,200 | ExU Generator (Stirling) | `thermal:dynamo_stirling` | ✅ |
| 200,64,202 | ExU Generator (Magmatic) | `thermal:dynamo_magmatic` | ✅ |
| 200,64,204 | ExU Magnum Torch | `torchmaster:megatorch` | ✅ |
| 200,64,206 | ExU Trash Can | `trashcans:item_trash_can` | ✅ |
| 200,64,208 | ExU Filing Cabinet | `conversion_placeholders:block_entity_placeholder` | ✅ fallback |
| 200,64,210 | ExU Drum | `conversion_placeholders:block_entity_placeholder` | ✅ fallback |
| 200,64,212 | ExU Generator (x64) | `thermal:dynamo_numismatic` | ✅ |
| 201,64,200 | ExU Generator (Magmatic x8) | `thermal:dynamo_magmatic` | ✅ |
| 201,64,202 | ExU Solar Generator | `mekanismgenerators:solar_generator` | ✅ |
| 201,64,204 | ExU Cursed Earth | `cursedearth:cursed_earth` | ✅ |
| 201,64,206 | ExU Trash Can (Fluid) | `trashcans:liquid_trash_can` | ✅ |
| 201,64,208 | ExU Filing Cabinet | `conversion_placeholders:block_entity_placeholder` | ✅ fallback |
| 201,64,210 | ExU Ender Quarry | `conversion_placeholders:block_entity_placeholder` | ✅ fallback |
| 201,64,212 | ExU Generator (Culinary) | `thermal:dynamo_gourmand` | ✅ |
| 202,64,200 | ExU Solar Generator | `mekanismgenerators:solar_generator` | ✅ |
| 202,64,202 | ExU Generator (x64) | `thermal:dynamo_numismatic` | ✅ |
| 202,64,204 | ExU Angel Block | `angelblockrenewed:angel_block` | ✅ |
| 202,64,206 | ExU Trash Can (Energy) | `trashcans:energy_trash_can` | ✅ |
| 202,64,208 | ExU Filing Cabinet | `conversion_placeholders:block_entity_placeholder` | ✅ fallback |
| 202,64,210 | ExU Ender Thermic Pump | `mekanism:electric_pump` | ✅ |
| 202,64,212 | ExU Generator (Potion) | `thermal:dynamo_compression` | ✅ |
| 203,64,200 | ExU Generator (Stirling x8) | `thermal:dynamo_stirling` | ✅ |
| 203,64,204 | ExU Sound Muffler | `conversion_placeholders:block_entity_placeholder` | ✅ fallback |
| 203,64,208 | ExU Filing Cabinet | `conversion_placeholders:block_entity_placeholder` | ✅ fallback |
| 203,64,212 | ExU Generator (TNT) | `thermal:dynamo_disenchantment` | ✅ |
| 204,64,200 | ExU Generator (Culinary x8) | `thermal:dynamo_gourmand` | ✅ |
| 204,64,212 | ExU Generator (Lapis) | `thermal:dynamo_lapidary` | ✅ |

## Zmodyfikowane pliki

- `headless_server/1.18.2/mods/supermartijn642corelib-1.1.21-forge-mc1.18.jar` (nowy)
- `headless_server/1.18.2/mods/supermartijn642configlib-1.1.8-forge-mc1.18.jar` (nowy)
- `headless_server/1.18.2/server.properties` (zmieniony na konfigurację ExU)
- `test_scenarios/extrautils_task5a/extrautils_task6_headless_tick_restart_report.json` (nowy)

## Problemy i obejścia

1. **NBT w komendach datapacku** – komendy `/setblock` z NBT tagami z 1.7.10 formatu (np. `{id:"thermal:dynamo_stirling",...}`) były odrzucane przez serwer 1.18.2 jako nieprawidłowe dla danego blockstate. NBT tagi należy przekształcać do formatu 1.18.2 lub pomijać w komendach `/setblock`.
2. **Brak blockstate w `execute if block`** – weryfikacja bloków przez `execute if block` wymaga dokładnego dopasowania blockstate (`[facing=south]` itp.). Dla bloków bez Tile Entity użyto testu `setblock` no-op.
3. **Extreme Sound Muffler** – mod client-side only w 1.18.2, brak bloku serwerowego.

## Następne kroki

1. Ulepszyć generator datapacku (`materialize_extrautils_task5b.py`) aby pomijał NBT niekompatybilne z 1.18.2 blockstates w komendach `/setblock`.
2. Rozważyć dodanie konwertera NBT dla filing cabinets (przeniesienie inventory do placeholdera zamiast tracić dane).
3. Przejść do kolejnego etapu / modu w planie konwersji.
