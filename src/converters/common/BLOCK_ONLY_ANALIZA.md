# Block-only analiza: common

Data: 2026-05-29

## Zakres

`src/converters/common/` nie jest modem Minecraft, tylko wspolna biblioteka dla konwerterow. Nie ma wlasnego namespace w FML `ItemData`, nie rejestruje blokow i nie powinien miec per-mod `block_only_converter`.

Zrodla sprawdzone lokalnie:
- `src/converters/common/item_id_resolver.py`
- `src/converters/common/conversion_event.py`
- `src/converters/common/placeholders.py`
- `mapa_1710/level.dat` przez `load_item_id_mapping()`

## Tabela block-only

| numeric_id | registry_name | metadata | source variant | target block | confidence |
|---:|---|---|---|---|---|
| n/a | n/a | n/a | brak blokow moda `common` | n/a | high |

## Fallbacki

Brak fallbackow. `common` powinien udostepnic w kroku 2 tylko wspolny typ wyniku/router helpers, jesli bedzie to wygodne dla innych modow.

## Odrzucone / review

- Nie tworzyc mapowan `common:*`, bo taki namespace nie istnieje w mapie.
- Nie mapowac placeholderow z `common/placeholders.py` w tej warstwie; to targety ratunkowe dla konwerterow TE/NBT.

## Handoff decyzji

- `common` nie wymaga per-mod block-only convertera.
- Potencjalny krok 2 dla `common`: wspolna dataclass `BlockOnlyResult` i/lub helper audytu JSONL, uzywany przez prawdziwe mody.
