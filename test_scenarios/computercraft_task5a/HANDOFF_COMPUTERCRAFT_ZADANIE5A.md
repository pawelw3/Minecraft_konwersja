# Handoff: ComputerCraft Zadanie 5A — Testowa mapa + konwersja E2E

## Podsumowanie sesji
Wykonano testową mapę 1.7.10 z 18 blokami/TE ComputerCraft obejmującymi wszystkie typy:
komputery (normal/advanced/command), monitory (normal/advanced, wall/ceiling/floor),
peryferia (disk drive, printer, speaker, wireless modem), kable (wired modem, cable),
oraz żółwie (normal/expanded/advanced z różnymi upgrade'ami).
Zaaplikowano patch przez JVM Hephaistos worker, uruchomiono konwersję Python
(ComputerCraftConverter) i zweryfikowano poprawność wyników. Wszystkie 18 bloków
przekonwertowano bez błędów.

## Ukończono
- [x] Przygotowanie testowej mapy `lightweigh_map_templates/1710_modded/computercraft_task5a_world`
- [x] Generator patcha (`test_scenarios/computercraft_task5a/generate_patch.py`)
- [x] Aplikacja patcha 1.7.10 przez JVM Worker (36 edits)
- [x] Weryfikacja bloków/TE w chunku (AddBlocks + TileEntities poprawne)
- [x] Konwersja przez `ComputerCraftConverter` (18/18 bloków skonwertowanych)
- [x] Weryfikacja blockstate i NBT dla wszystkich typów
- [x] Raport: `test_scenarios/computercraft_task5a/computercraft_task5a_report.json`

## Nowe pliki
- `test_scenarios/computercraft_task5a/generate_patch.py`
- `test_scenarios/computercraft_task5a/convert_test_map.py`
- `test_scenarios/computercraft_task5a/computercraft_task5a_patch.json`
- `test_scenarios/computercraft_task5a/computercraft_task5a_converted_1182.json`
- `test_scenarios/computercraft_task5a/computercraft_task5a_report.json`
- `lightweigh_map_templates/1710_modded/computercraft_task5a_world/`

## Zmodyfikowane pliki
- brak (nowe pliki w nowych folderach)

## Kluczowe odkrycia
1. **ID bloków CC z mapa_1710**: 574–580 (7 entries)
2. **Worker 1.7.10 poprawnie obsługuje `Add` array** dla ID > 255 (np. block 578 = wired modem + cable)
3. **NBT boolean z mapy 1.7.10** jest odczytywany jako int (0/1) — konwerter obsługuje to poprawnie
4. **Wszystkie 18 typów bloków/TE** zostały poprawnie zmapowane na 1.18.2

## Szczegóły konwersji per-typ

| Sample | Source | Target Blockstate | NBT | Status |
|--------|--------|-------------------|-----|--------|
| computer_normal_on | computer:0 | state=on | ComputerId, On | ✅ |
| computer_normal_off | computer:1 | state=off | ComputerId, Label, On | ✅ |
| computer_advanced_on | computer:8 | state=on | ComputerId, On | ✅ |
| command_computer | command_computer:0 | facing=north, state=on | ComputerId, On | ✅ |
| monitor_normal_wall_tl | peripheral:10 | orientation=north, facing=north, state=rd | XIndex, YIndex, Width, Height | ✅ |
| monitor_normal_wall_tr | peripheral:10 | orientation=north, facing=north, state=ld | XIndex, YIndex, Width, Height | ✅ |
| monitor_advanced_ceiling | peripheral:12 | orientation=down, facing=south, state=none | XIndex, YIndex, Width, Height | ✅ |
| monitor_advanced_floor | peripheral:12 | orientation=up, facing=south, state=none | XIndex, YIndex, Width, Height | ✅ |
| disk_drive | peripheral:2 | facing=north, state=empty | — | ✅ |
| printer | peripheral:11 | facing=north, top=false, bottom=false | — | ✅ |
| speaker | peripheral:13 | facing=north | — | ✅ |
| wireless_modem | peripheral:6 | facing=north, on=false | — | ✅ |
| wired_modem_only | cable:0 | cable=false, modem=down_off | — | ✅ |
| wired_modem_with_cable | cable:6 | cable=true, modem=down_off | — | ✅ |
| cable_only | cable:13 | cable=true, modem=none | — | ✅ |
| turtle_normal | turtle:0 | facing=north | Fuel, LeftUpgrade, RightUpgrade | ✅ |
| turtle_expanded | turtle_expanded:0 | facing=south | LeftUpgrade, RightUpgrade | ✅ |
| turtle_advanced | turtle_advanced:0 | facing=west | Colour, LeftUpgrade | ✅ |

## Następne kroki
1. **Zadanie 5B** — uruchomienie headless serwera 1.7.10 z testową mapą (opcjonalnie)
2. **Zadanie 5B/6** — testy integracyjne z redstone (headless serwer 1.18.2)
3. **Zadanie 6** — 3-minutowy tick test na headless serwerze z przekonwertowaną mapą
4. **Milestone** — integracja ComputerCraft z innymi modami (AE2, Mekanism, Thermal, IC2)
