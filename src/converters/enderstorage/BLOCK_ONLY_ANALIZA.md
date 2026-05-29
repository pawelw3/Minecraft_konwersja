# Block-only analiza: EnderStorage

Data: 2026-05-29

## Zakres i zrodla

EnderStorage zapisuje w swiecie glownie Ender Chest i Ender Tank jako TileEntity z czestotliwoscia/ownerem/rotacja. Nie jest to dobry kandydat na zwykly block-only, poza awaryjnym przypadkiem braku TE.

Zrodla lokalne:
- `mod_src/1710/actual_src/1.7.10/EnderStorage/`
- `mod_src/118/actual_src/1.18.2/EnderStorage/`
- `src/converters/enderstorage/mappings/block_mappings.py`
- `output/enderstorage_coverage_report.md`
- `mapa_1710/level.dat` FML `ItemData`

Dynamiczne ID z `level.dat`: `3459` dla `EnderStorage:enderChest`, `10229` dla itemu `enderPouch`.
Raport pokrycia znalazl 39 Ender Chest i 1 Ender Tank, wszystkie jako TE.

Uwaga o paczce 1.18.2: w `client_pack_1182/mod_manifest.json` nie widac obecnie JAR `EnderStorage`. Targety `enderstorage:*` wymagaja dodania moda do paczki albo zamiany na placeholder/alternatywe.

## Tabela block-only

| numeric_id | registry_name | metadata | source variant | target block | confidence |
|---:|---|---|---|---|---|
| 3459 | `EnderStorage:enderChest` | 0 | Ender Chest, wymaga TE frequency/owner/rot | poza zakresem; TE -> `enderstorage:ender_chest` po dodaniu moda do paczki | medium |
| 3459 | `EnderStorage:enderChest` | 1 | Ender Tank, wymaga TE frequency/owner/fluid state | poza zakresem; TE -> `enderstorage:ender_tank` po dodaniu moda do paczki | medium |

## Fallbacki

- Awaryjny brak TE dla meta 0: `enderstorage:ender_chest` tylko jesli mod jest w paczce; inaczej placeholder, confidence `low`, warning o utracie frequency/owner.
- Awaryjny brak TE dla meta 1: `enderstorage:ender_tank` tylko jesli mod jest w paczce; inaczej placeholder, confidence `low`, warning o utracie frequency/owner/fluid.
- Nieznana metadata: `conversion_placeholders:block_entity_placeholder`, confidence `low`.

## Odrzucone / wymagajace review

- `EnderStorage:enderPouch` jest itemem.
- Nie przepychac EnderStorage przez dekoracyjny block-only jako normalnej sciezki, bo strata frequency laczy niepowiazane sieci albo tworzy puste sieci.

## Handoff decyzji

- Krok 2 moze nie tworzyc osobnego block-only konwertera dla EnderStorage; wystarczy w routerze jawnie oznaczyc jako `requires_block_entity`.
- Jesli jednak direct writer wymaga wyniku, wynik musi miec `confidence=low` i audit.
