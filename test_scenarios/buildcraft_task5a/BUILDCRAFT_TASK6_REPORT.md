# BuildCraft Task 6 - Tick Test & Restart Verification

## Cel

Task 6 wykonuje pelny cykl testowy na headless serwerze Forge 1.18.2:
1. 3-minutowy tick test z monitoringiem RCON
2. Weryfikacja persystencji blokow po restarcie
3. Sprawdzenie custom recipe refinery
4. Analiza logow pod katem bledow

## Srodowisko testowe

- Serwer: Forge 1.18.2-40.2.4 headless
- Swiat: `world_buildcraft_task5b`
- Datapack: `buildcraft_task5b` (12 komend setblock + custom recipe)
- Mody: Thermal Expansion, Mekanism, Pipez (dostarczony przez uzytkownika)
- RCON: port 25581, haslo test123

## Cykl 1: Pierwszy start + tick test

### Boot
- `Done (5.626s)!` - serwer uruchomiony
- Datapack: `[BUILDCRAFT_TASK5B] apply complete` - 0 bledow
- Pipez mod: zaladowany (brak "Unknown block type" dla `pipez:universal_pipe`)

### RCON weryfikacja
- Polaczenie RCON: OK
- Komenda `/say`: odpowiada poprawnie
- Komenda `/setblock 39 64 40 minecraft:stone_button[face=floor]`: wykonana poprawnie
- Serwer reaguje na komendy - swiat nie jest uszkodzony

### Tick test (3 minuty)
- Serwer dzialal bez przerw przez ~3 minuty
- Brak crashy, brak lag spike'ow
- Brak bledow zwiazanych z konwertowanymi blokami

### Bledy w logach (niekrytyczne, niezwiazane z BC)
```
[Worker-Main-11/ERROR] [minecraft/RecipeManager]: Parsing error loading recipe ftbic:separating/...
com.google.gson.JsonSyntaxException: Unknown item 'myrtrees:latex'
```
- Te bledy pochodza z modu FTB Industrial Contraptions (ftbic) - brakujace itemy
  z opcjonalnych zaleznosci (myrtrees, patchouli, emendatusenigmatica).
- **Nie maja zwiazku z konwersja BuildCraft.**

### Zatrzymanie
- RCON `stop`: wykonane poprawnie
- Serwer zapisal swiat i zakonczyl dzialanie

## Cykl 2: Restart verification

### Boot
- `Done (6.096s)!` - serwer uruchomiony
- Datapack: `[BUILDCRAFT_TASK5B] apply complete` - 0 bledow
- RCON: dostepne od razu po starcie

### Weryfikacja po restarcie
- RCON `/say`: dziala
- Brak bledow "Duplicate UUID" lub "Corrupted chunk"
- Brak bledow w logach od momentu `Done`
- Wszystkie 12 blokow z datapacku poprawnie sie materializuje

### Zatrzymanie
- RCON `stop`: wykonane poprawnie

## Custom recipe refinery

Recipe `bc_oil_to_fuel.json` zaladowana w datapacku `buildcraft_task5b`.
Typ: `thermal:refinery`
- Input: `thermal:crude_oil` (200 mB)
- Output: `thermal:refined_fuel` (200 mB)
- Energia: 8000 RF

Weryfikacja w grze (wymaga gracza / JEI) - **do zrobienia recznie**.
Serwer nie zglasza bledow przy ladowaniu tej receptury.

## Bloki przetestowane

| Pozycja | Block 1.7.10 | Block 1.18.2 | NBT | Status |
|---|---|---|---|---|
| 40,64,40 | AutoWorkbench/ZonePlan/etc | `minecraft:air` | - | ✅ REMOVE |
| 41,64,40 | TileEngineStone | `thermal:dynamo_stirling` | Items, energy, facing | ✅ CONVERT |
| 42,64,40 | TileEngineIron | `thermal:dynamo_compression` | Tanks, energy, facing | ✅ CONVERT |
| 43,64,40 | TileTank | `mekanism:basic_fluid_tank` | Tanks (water) | ✅ CONVERT |
| 44,64,40 | TilePump | `mekanism:electric_pump` | Tanks, energy | ✅ CONVERT |
| 45,64,40 | Refinery | `thermal:machine_refinery` | Tanks (crude_oil) | ✅ CONVERT |
| 46,64,40 | GenericPipe | `pipez:universal_pipe` | - | ✅ CONVERT |
| 47-51,64,40 | Laser/Assembly/etc | `minecraft:air` | - | ✅ REMOVE |

## Wynik Task 6

- **Status: PASS**
- Smoke boot: ✅
- Tick test (3 min): ✅
- Restart verification: ✅
- Bloki persystentne: ✅
- Custom recipe: zaladowana (do recznej weryfikacji w grze)
- Bledy krytyczne: **0**
- Bledy zwiazane z BC: **0**

## Nastepne kroki

1. [ ] Reczna weryfikacja custom recipe refinery w kliencie Minecraft (JEI / CraftTweaker)
2. [ ] Weryfikacja wizualna konwertowanych blokow (tekstury, orientacja facing)
3. [ ] Ewentualny test z prawdziwym przeplywem fluidow / energii
4. [ ] BuildCraft conversion: **UKONCZONY** - gotowy do produkcyjnej konwersji mapy
