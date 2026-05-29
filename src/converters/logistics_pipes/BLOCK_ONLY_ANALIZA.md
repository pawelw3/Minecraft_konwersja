# Block-only analiza: Logistics Pipes

Data: 2026-05-29

## Zakres i zrodla

Logistics Pipes w swiecie wystepuje glownie jako rury i bloki funkcyjne z TileEntity. Zwykle bloki bez TE praktycznie nie wystepuja jako istotna geometria; direct block-only ma byc tylko awaryjnym zabezpieczeniem przed `air`.

Zrodla lokalne:
- `mod_src/1710/actual_src/1.7.10/LogisticsPipes/`
- `mod_src/118/actual_src/1.18.2/PrettyPipes/`
- `src/converters/logistics_pipes/mappings.py`
- `src/converters/logistics_pipes/logistics_pipes_converter.py`
- `output/logistics_pipes_task4/logistics_pipes_task4_coverage.md`
- `mapa_1710/level.dat` FML `ItemData`

Dynamiczne ID z `level.dat`: `2715` (`logisticsSolidBlock`), `2716` (`logisticsPipeBlock`), item pipe IDs `8749..8780`, `10610`.
Raport pokrycia stref: 215 TE, 0 placeholderow.

## Tabela block-only

| numeric_id | registry_name | metadata | source variant | target block | confidence |
|---:|---|---|---|---|---|
| 2715 | `LogisticsPipes:logisticsSolidBlock` | 0-15 | request table / power junction / solid blocks, TE | outside block-only; existing TE mapping to PrettyPipes/AE2 | high |
| 2716 | `LogisticsPipes:logisticsPipeBlock` | 0-15 | generic pipe container, pipe type in TE/item pipeId | outside block-only; existing TE mapping to `prettypipes:pipe` | high |

## Fallbacki

- Missing TE for `logisticsPipeBlock`: `prettypipes:pipe`, confidence `low`, warning `LP-W-MISSING-PIPE-TE`.
- Missing TE for `logisticsSolidBlock`: `prettypipes:item_terminal` or `conversion_placeholders:block_entity_placeholder`, confidence `low`; choose placeholder if metadata/type unknown.
- Unknown `LogisticsPipes:*`: placeholder, not `air`.

## Odrzucone / wymagajace review

- Pipe class is derived from TE or dynamic item `pipeId`, not terrain metadata alone.
- Crafting table and power junction have functional state and cannot be represented safely by block-only.

## Handoff decyzji

- Nie tworzyc pelnego dekoracyjnego block-only convertera dla LP.
- Centralny router powinien tylko chronownie fallbackowac brakujace TE i wysylac przypadki do audytu.
