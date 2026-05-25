# Handoff: Zadanie 5A - Testowa mapa CFM + konwersja + zapis 1.18.2

## Podsumowanie sesji
Zbudowano testowy swiat Minecraft 1.7.10 zawierajacy wszystkie bloki MrCrayfish Furniture Mod
(61 unikalnych typow, 137 instancji) przy uzyciu Kotlin Hephaistos WorldEditor. Uruchomiono
pelna konwersje Pythonowa, zaaplikowano eventy na mape 1.18.2 i zweryfikowano wyniki
w formacie docelowym.

## Ukonczono
- [x] Wygenerowanie patch JSON z wszystkimi blokami CFM + TE (164 edycje)
- [x] Aplikacja patcha na testowy swiat 1.7.10 via `mc-editkit-worker-1.0-SNAPSHOT.jar`
- [x] Rozszerzenie `mrcrayfish_chunk_parser.py` o skanowanie sekcji blokow (Add array, ID > 255)
- [x] Naprawa dekodowania koordynatow Y/Z w sekcjach blokow (zamiana ly/lz)
- [x] Naprawa wywolania `convert_block()` (zbyt duzo argumentow pozycyjnych)
- [x] Uzupelnienie mapowan w `mrcrayfish_converter.py`:
  - `coffetablewood`/`coffetablestone` (literowka w 1.7.10)
  - `blindon`/`blindoff` -> `oak_blinds`
  - `curtainon`/`curtainoff` -> `oak_curtains`
  - `countersink` -> `kitchen_sink`
  - `ovenoverhead` -> `range_hood`
- [x] Stworzenie `item_id_resolver.py` - mapowanie numerycznych ID -> string ID z level.dat
- [x] Integracja resolvera z `inventory_helpers.py` i `mrcrayfish_converter.py`
- [x] Generowanie eventow JSON (`to_set_block_event()`) i zapis do mapy 1.18.2 via `WorldEditor1182`
- [x] Weryfikacja mapy 1.18.2:
  - Block states: 137 blokow w 3 chunkach, poprawne palette (cfm:oak_cabinet, cfm:fridge_light, ...)
  - Block entities: 19 BE (cabinet, fridge, freezer, crate) z poprawnymi ID
  - Inventory: numeryczne ID zamienione na string ID (264 -> minecraft:diamond)
  - Sofa colors: wszystkie 16 kolorow obecne (white..black)
  - Fridge/Freezer: 5 par z inventory, 3 sloty w freezer, 4 w fridge

## Nowe pliki
- `src/converters/common/item_id_resolver.py` - resolver numerycznych ID przedmiotow
- `test_scenarios/mrcrayfish_task5a/generate_cfm_patch.py` - generator patcha JSON
- `test_scenarios/mrcrayfish_task5a/run_conversion_test.py` - skrypt testowy konwersji
- `test_scenarios/mrcrayfish_task5a/apply_to_1182.py` - aplikacja eventow na mape 1.18.2
- `test_scenarios/mrcrayfish_task5a/cfm_full_patch.json` - wygenerowany patch
- `test_scenarios/mrcrayfish_task5a/events_1182.json` - eventy w formacie 1.18.2
- `test_scenarios/mrcrayfish_task5a/task5a_report.json` - raport JSON z testu
- `test_scenarios/mrcrayfish_task5a/target_1182/` - przekonwertowana mapa 1.18.2
- `output/mrcrayfish_task5a/task5a_report.json` - kopia raportu w output

## Zmodyfikowane pliki
- `src/converters/mrcrayfish_furniture/mrcrayfish_chunk_parser.py`:
  - Dodano `CFM_BLOCK_IDS`, `_scan_block_sections()`, parametr `scan_blocks`
  - Naprawiono dekodowanie koordynatow (lz/ly)
  - Parametr `level_dat_path` w konstruktorze
- `src/converters/mrcrayfish_furniture/mrcrayfish_converter.py`:
  - Dodano aliasy dla literowek i stanow on/off
  - Parametr `level_dat_path` w konstruktorze
  - Integracja `item_id_resolver` w konwersji inventory
- `src/converters/common/inventory_helpers.py`:
  - Parametr `item_id_resolver` w `convert_inventory_1710_to_1182()`

## Wyniki testu
| Metryka | Wartosc |
|---------|---------|
| Chunki z CFM | 3 |
| Lacznie blokow CFM | 137 |
| Lacznie eventow | 137 |
| Remap | 81 |
| Placeholder | 31 |
| Remove | 25 |
| Nieobsluzone bloki | 0 |
| Inventory string ID | OK (264 -> minecraft:diamond) |
| Sofa colors (16) | OK |
| Fridge/Freezer pairs | 5 |

## Nastepne kroki
1. [ ] Weryfikacja w grze (headless server 1.18.2 + obserwacja blokow)
2. [ ] Test na fragmencie prawdziwej mapy (np. strefa ZSRR z CFM)
3. [ ] Obsluga pozostalych modow (milestone integracyjny)
