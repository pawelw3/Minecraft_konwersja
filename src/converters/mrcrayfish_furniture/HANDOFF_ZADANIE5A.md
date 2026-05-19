# Handoff: Zadanie 5A - Testowa mapa CFM + konwersja

## Podsumowanie sesji
Zbudowano testowy swiat Minecraft 1.7.10 zawierajacy wszystkie bloki MrCrayfish Furniture Mod
(61 unikalnych typow, 137 instancji) przy uzyciu Kotlin Hephaistos WorldEditor. Uruchomiono
pelna konwersje Pythonowa i zweryfikowano pokrycie wszystkich typow blokow.

## Ukonczono
- [x] Wygenerowanie patch JSON z wszystkimi blokami CFM + TE (164 edycje)
- [x] Aplikacja patcha na testowy swiat via `mc-editkit-worker-1.0-SNAPSHOT.jar`
- [x] Rozszerzenie `mrcrayfish_chunk_parser.py` o skanowanie sekcji blokow (Add array, ID > 255)
- [x] Naprawa dekodowania koordynatow Y/Z w sekcjach blokow (zamiana ly/lz)
- [x] Naprawa wywolania `convert_block()` (zbyt duzo argumentow pozycyjnych)
- [x] Uzupelnienie mapowan w `mrcrayfish_converter.py`:
  - `coffetablewood`/`coffetablestone` (literowka w 1.7.10)
  - `blindon`/`blindoff` -> `oak_blinds`
  - `curtainon`/`curtainoff` -> `oak_curtains`
  - `countersink` -> `kitchen_sink`
  - `ovenoverhead` -> `range_hood`
- [x] Pelny test konwersji: 137 blokow -> 137 eventow (81 remap, 31 placeholder, 25 remove)
- [x] Weryfikacja: zero nieobsluzonych typow blokow

## Nowe pliki
- `test_scenarios/mrcrayfish_task5a/generate_cfm_patch.py` - generator patcha JSON
- `test_scenarios/mrcrayfish_task5a/run_conversion_test.py` - skrypt testowy konwersji
- `test_scenarios/mrcrayfish_task5a/cfm_full_patch.json` - wygenerowany patch
- `test_scenarios/mrcrayfish_task5a/task5a_report.json` - raport JSON z testu
- `output/mrcrayfish_task5a/task5a_report.json` - kopia raportu w output

## Zmodyfikowane pliki
- `src/converters/mrcrayfish_furniture/mrcrayfish_chunk_parser.py`:
  - Dodano `CFM_BLOCK_IDS` (mapowanie numerycznych ID -> nazwy)
  - Dodano `_scan_block_sections()` (skanowanie sekcji blokow z Add array)
  - `analyze_chunk()` teraz obsluguje `scan_blocks=True`
  - Naprawiono dekodowanie koordynatow (lz/ly zamienione)
  - Naprawiono wywolanie `convert_block()` (usunieto zbedny `None`)
- `src/converters/mrcrayfish_furniture/mrcrayfish_converter.py`:
  - Dodano aliasy dla `coffetablewood`/`coffetablestone`
  - Dodano aliasy `blindon`/`blindoff` -> `blinds`
  - Dodano aliasy `curtainon`/`curtainoff` -> `curtains`
  - Dodano `countersink` -> `kitchen_sink` w REPLACEMENT_MAP
  - Dodano `ovenoverhead` -> `range_hood` w RENAMED_MAP

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

## Nastepne kroki
1. [ ] Integracja z systemem eventow 1.18.2 (zapis do mapy docelowej)
2. [ ] Test inventory dla Fridge/Freezer (multiblock 16+16 -> 27+3)
3. [ ] Test kolorow sofy (metadata 0-15 -> per-color blocks)
4. [ ] Weryfikacja w grze (headless server + obserwacja)
