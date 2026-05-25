# Handoff: BuildCraft – Krok 3 (Ukończony)

## Podsumowanie sesji

Ukończono **Krok 3** konwersji moda BuildCraft – implementacja kodu konwersji (wspólne narzędzia + specyficzne per-mod).  
Stworzono pełny pipeline konwersji BuildCraft 1.7.10 → 1.18.2 zintegrowany z globalnym routerem (`converters.router`).

## Ukończono

- [x] **Block ID mappings** (`mappings/block_mappings.py`):
  - Mapowanie 11 typów TE BuildCraft -> bloki 1.18.2
  - Akcje: CONVERT (8 typów) lub REMOVE (3 typy + Redstone Engine)
- [x] **NBT Converter Registry** (`nbt_converters/converter_registry.py`):
  - `IdentityConverter` – no-op
  - `RemoveConverter` – dla bloków usuwanych
  - `EngineStoneConverter` – Stirling -> Steam Dynamo
  - `EngineIronConverter` – Combustion -> Compression Dynamo
  - `TankConverter` – Tank -> Basic Fluid Tank
  - `PumpConverter` – Pump -> Electric Pump
  - `RefineryConverter` – Refinery -> Thermal Refinery
  - `PipeConverter` – GenericPipe -> Pipez (universal/fluid/energy)
- [x] **Główny konwerter** (`buildcraft_converter.py`):
  - `BuildCraftConverter.convert_tile_entity()` – główny entry point
  - Obsługa REMOVE (air) i CONVERT (z NBT + blockstate)
  - Statystyki: processed, converted, removed, failed
  - Serializacja do dict (`to_dict()`)
- [x] **Integracja z routerem** (`converters/router.py`):
  - Dodano `detect_mod()` – rozpoznawanie BuildCraft po `buildcraft` w TE ID
  - Dodano `_buildcraft()` – lazy singleton konwertera
  - Dodano `_buildcraft_to_events()` – serializacja do Event JSON
  - Dodano dispatch w `convert_te_to_events()` dla `mod == "buildcraft"`
- [x] **Testy**:
  - 10 testów konwertera (`test_buildcraft_converter.py`) – wszystkie zielone
  - 16 testów symulacji (`test_buildcraft_simulations.py`) – wszystkie zielone
  - **Razem: 26/26 testów ✅**
- [x] **Test end-to-end** przez router:
  - GenericPipe -> `pipez:universal_pipe` ✅
  - TileEngineStone -> `thermal:dynamo_steam` + NBT + facing ✅
  - TileTank -> `mekanism:basic_fluid_tank` + fluids ✅
  - TileAssemblyTable -> `minecraft:air` (REMOVE) ✅

## Nowe pliki

| Plik | Opis |
|------|------|
| `src/converters/buildcraft/mappings/__init__.py` | Inicjalizacja pakietu mapowań |
| `src/converters/buildcraft/mappings/block_mappings.py` | Mapowania TE ID -> bloki 1.18.2 |
| `src/converters/buildcraft/nbt_converters/__init__.py` | Inicjalizacja pakietu NBT converters |
| `src/converters/buildcraft/nbt_converters/base_converter.py` | Klasa bazowa `BaseBuildCraftNBTConverter` |
| `src/converters/buildcraft/nbt_converters/converter_registry.py` | Rejestr konwerterów NBT (8 konwerterów) |
| `src/converters/buildcraft/buildcraft_converter.py` | Główny konwerter `BuildCraftConverter` |
| `src/converters/buildcraft/tests/test_buildcraft_converter.py` | 10 testów jednostkowych konwertera |

## Zmodyfikowane pliki (poza folderem buildcraft/)

| Plik | Zmiana |
|------|--------|
| `src/converters/router.py` | Dodano obsługę BuildCraft w `detect_mod`, lazy loader, serialiser i dispatch |

## Architektura konwertera BuildCraft

```
Router (convert_te_to_events)
    -> detect_mod(te_id) == "buildcraft"
    -> _buildcraft().convert_tile_entity(te_id, nbt_1710, metadata, position)
        -> BuildCraftConverter
            -> get_mapping_for_te_id(te_id) -> BlockMapping
            -> if REMOVE: return air
            -> if CONVERT: _convert_nbt(mapping, nbt_1710) 
                -> get_nbt_converter(mapping.nbt_converter)
                    -> symulacje (engine/factory/pipe/assembly)
                -> NBTConversionResult
            -> BuildCraftBlockConversion
    -> _buildcraft_to_events(BuildCraftBlockConversion) -> Event JSON
```

## Mapowania bloków / TE

| TE ID BuildCraft 1.7.10 | Akcja | Blok 1.18.2 | TE 1.18.2 | Konwerter NBT |
|------------------------|-------|-------------|-----------|---------------|
| `TileEngineWood` | REMOVE | `minecraft:air` | — | `remove` |
| `TileEngineStone` | CONVERT | `thermal:dynamo_steam` | `thermal:tile_dynamo_steam` | `engine_stone` |
| `TileEngineIron` | CONVERT | `thermal:dynamo_compression` | `thermal:tile_dynamo_compression` | `engine_iron` |
| `GenericPipe` | CONVERT | `pipez:universal_pipe` | — | `pipe` |
| `TileTank` | CONVERT | `mekanism:basic_fluid_tank` | `mekanism:tile_basic_fluid_tank` | `tank` |
| `TilePump` | CONVERT | `mekanism:electric_pump` | `mekanism:tile_electric_pump` | `pump` |
| `Refinery` | CONVERT | `thermal:machine_refinery` | `thermal:tile_machine_refinery` | `refinery` |
| `TileAssemblyTable` | REMOVE | `minecraft:air` | — | `remove` |
| `TileIntegrationTable` | REMOVE | `minecraft:air` | — | `remove` |
| `TileLaser` | REMOVE | `minecraft:air` | — | `remove` |
| `TileZonePlan` | REMOVE | `minecraft:air` | — | `remove` |

## Format wyjściowy Event JSON

Przykład (Engine Stone):
```json
{
  "pos": [11, 64, 10],
  "block": "thermal:dynamo_steam",
  "op": "set_block_entity",
  "nbt": {"Items": [...], "energy": 1000},
  "blockstate": {"facing": "north"},
  "warnings": ["Stirling Engine zasilany solid fuel -> Steam Dynamo"]
}
```

## Następne kroki (Krok 4)

Zgodnie z planem konwersji (`docs/PLAN.md`), kolejny krok to:

**Krok 4: Sprawdzenie pokrycia dla stref głównej mapy**

Do zrobienia:
1. Uruchomić `step1_analyze.py` (z kroku 1) na aktualnej mapie, żeby zebrać wszystkie pozycje BuildCraft
2. Dla każdej strefy (billund, choroszcz, iii_rzesza, rzym, zsrr) uruchomić konwerter BuildCraft przez router
3. Wygenerować raport pokrycia: ile TE zostało skonwertowanych, ile usuniętych, ile błędów
4. Zweryfikować czy wszystkie 403 TE BuildCraft mają poprawne mapowania

## Zalecenia przed Krokiem 4

1. **Rozstrzygnąć:** Czy dla rur GenericPipe potrzebujemy analizy sąsiedztwa (neighbors_have_fluid/power)?  
   Obecnie konwerter zawsze daje `pipez:universal_pipe`. Jeśli chcemy `fluid_pipe` / `energy_pipe`, trzeba przekazać informację o sąsiadach do konwertera (wymaga zmiany API `convert_tile_entity`).

2. **Rozstrzygnąć:** Czy konwertować numeryczne ID itemów (np. `id: 263` -> `minecraft:coal`) w inventory silników?  
   Obecnie zostawiamy surowe numeryczne ID. Globalny `item_id_resolver.py` może to rozwiązać.

3. **Rozstrzygnąć:** Czy dodać `BuildCraftConverter` do globalnego pipeline'u konwersji mapy (np. `convert_world.py`)?

---

**Status:** ✅ Krok 3 ukończony – pełny pipeline konwersji BuildCraft działa end-to-end (26/26 testów + router integration)  
**Data:** 2026-05-24  
**Agent:** AI Konwersji BuildCraft
