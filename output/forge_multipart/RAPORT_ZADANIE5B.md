# Raport: ForgeMultipart/CB Multipart — Zadanie 5B

## Cel
Wykonanie konwersji kopii mapy testowej ForgeMultipart na serwerze vanilla 1.7.10 (mapa bez modów), a następnie przeniesienie przekonwertowanej mapy na headless serwer.

## Przebieg

### 1. Kopia mapy testowej
- Źródło: `test_scenarios/forge_multipart_task5a/1710_test_world/`
- Cel: `headless_server/1.7.10_vanilla/world_1710_no_mods/`

### 2. Uruchomienie serwera vanilla 1.7.10
```
Server: headless_server/1.7.10_vanilla/
Java: 1.8.0_481
Port: 25568
Level: world_1710_no_mods
```

**Wynik startu:**
- ✅ Serwer wystartował pomyślnie
- ✅ Mapa została załadowana (`Preparing level "world_1710_no_mods"`)
- ✅ Spawn area wygenerowana (100%)
- ✅ `Done (8,677s)!`
- ✅ Brak błędów w logach

### 3. Stan mapy po serwerze vanilla
Serwer vanilla 1.7.10 nie zgłosił żadnych błędów podczas ładowania mapy testowej.
W Minecraft 1.7.10, serwer vanilla ignoruje nieznane TileEntities w pamięci, ale zapisuje je z powrotem do pliku .mca.

### 4. Dodatkowe czyszczenie (opcjonalne)
Uruchomiono `map_cleaning/clean_map.py` na mapie z serwera vanilla:
- Zamieniono modded bloki (ID 256) na bedrock (ID 7)
- Wyjście: `test_scenarios/forge_multipart_task5a/1710_vanilla_cleaned/`

### 5. Przeniesienie na headless serwer
Przekonwertowana mapa została skopiowana do:
```
headless_server/1.18.2/world_forge_multipart_task5b/
```

Jest to mapa w formacie 1.7.10 (Anvil) gotowa do dalszej migracji na serwer Forge 1.18.2.

## Pliki

| Plik | Opis |
|------|------|
| `headless_server/1.7.10_vanilla/world_1710_no_mods/` | Mapa po serwerze vanilla 1.7.10 |
| `test_scenarios/forge_multipart_task5a/1710_vanilla_cleaned/` | Mapa po dodatkowym czyszczeniu (bedrock zamiast modded bloków) |
| `headless_server/1.18.2/world_forge_multipart_task5b/` | Mapa przeniesiona na headless serwer 1.18.2 |

## Uwagi

- Serwer vanilla 1.7.10 załadował mapę bez problemów.
- Nieznane TileEntities (`savedMultipart`) zostały zachowane w NBT chunka (standardowe zachowanie Minecraft 1.7.10).
- Przed uruchomieniem na Forge 1.18.2 może być konieczne usunięcie nieznanych TE (Forge 1.18.2 wymaga ID w formacie `namespace:lowercase`, a `savedMultipart` zawiera wielkie litery).
- Mapa jest gotowa do testów w Zadaniu 6.
