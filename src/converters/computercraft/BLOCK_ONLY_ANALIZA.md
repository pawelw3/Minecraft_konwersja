# Block-only analiza: ComputerCraft

Data: 2026-05-29

## Zakres i zrodla

ComputerCraft 1.7.10 zapisuje bloki jako numeric ID + metadata, ale realne bloki na mapie sa prawie zawsze TileEntity: komputery, monitory, modemy, turtle. Warstwa block-only jest potrzebna tylko jako awaryjne mapowanie dla zwyklego direct terrain writera, gdy blok nie ma TE na danej pozycji albo TE zostalo utracone.

Zrodla lokalne:
- `mod_src/1710/actual_src/1.7.10/ComputerCraft/`
- `mod_src/118/actual_src/1.18.2/CCTweaked/`
- `src/converters/computercraft/mappings.py`
- `output/computercraft_task4/computercraft_coverage_report.json`
- `mapa_1710/level.dat` FML `ItemData`

Dynamiczne ID z `level.dat`: `574..580` dla blokow, `5477..5481` dla itemow.
Raport pokrycia wykryl 4964 TE ComputerCraft i 0 nieobslugiwanych TE.

## Tabela block-only

| numeric_id | registry_name | metadata | source variant | target block | confidence |
|---:|---|---|---|---|---|
| 574 | `ComputerCraft:CC-TurtleExpanded` | 0 | expanded turtle, powinien miec TE | `computercraft:turtle_normal` | medium |
| 575 | `ComputerCraft:command_computer` | 0 | command computer, powinien miec TE | `computercraft:computer_command` | medium |
| 576 | `ComputerCraft:CC-Computer` | 0-7 | normal computer, facing w meta | `computercraft:computer_normal` | medium |
| 576 | `ComputerCraft:CC-Computer` | 8-15 | advanced computer, facing w meta | `computercraft:computer_advanced` | medium |
| 577 | `ComputerCraft:CC-Peripheral` | 0-1,6-9 | wireless modem | `computercraft:wireless_modem_normal` | medium |
| 577 | `ComputerCraft:CC-Peripheral` | 2-5 | disk drive | `computercraft:disk_drive` | medium |
| 577 | `ComputerCraft:CC-Peripheral` | 10 | monitor | `computercraft:monitor_normal` | medium |
| 577 | `ComputerCraft:CC-Peripheral` | 11 | printer | `computercraft:printer` | medium |
| 577 | `ComputerCraft:CC-Peripheral` | 12 | advanced monitor | `computercraft:monitor_advanced` | medium |
| 577 | `ComputerCraft:CC-Peripheral` | 13 | speaker | `computercraft:speaker` | medium |
| 578 | `ComputerCraft:CC-Cable` | 0-5 | wired modem without cable | `computercraft:cable` | medium |
| 578 | `ComputerCraft:CC-Cable` | 6-11 | wired modem with cable | `computercraft:cable` | medium |
| 578 | `ComputerCraft:CC-Cable` | 13 | cable only | `computercraft:cable` | high |
| 579 | `ComputerCraft:CC-Turtle` | 0 | normal turtle, powinien miec TE | `computercraft:turtle_normal` | medium |
| 580 | `ComputerCraft:CC-TurtleAdvanced` | 0 | advanced turtle, powinien miec TE | `computercraft:turtle_advanced` | medium |

## Fallbacki

- Nieznany `ComputerCraft:*` block ID: `computercraft:cable`, confidence `low`, warning `CC-W-BLOCK-ONLY-FALLBACK`.
- Nieznana metadata dla `CC-Peripheral`: `computercraft:cable`, confidence `low`, bo cable jest najmniej destrukcyjnym widocznym elementem sieci.
- Nigdy nie fallbackowac do `minecraft:air` bez jawnego wpisu audytu.

## Odrzucone / wymagajace review

- Wszystkie komputery, turtle, monitory, printery i modemy z TE powinny pozostac w konwerterze TE, bo block-only zgubi programy, label, inventory i stan sieci.
- `diskExpanded`, `pocketComputer`, `printout`, `disk`, `treasureDisk` sa itemami, nie blokami terrain.

## Handoff decyzji

- Krok 2 moze uzyc istniejacej tabeli z `mappings.py`, ale musi zaakceptowac registry names z `level.dat` (`ComputerCraft:CC-*`) i znormalizowac je do lokalnych nazw mapowan.
- Block-only dla ComputerCraft ma byc warstwa awaryjna, nie glowna sciezka konwersji.
