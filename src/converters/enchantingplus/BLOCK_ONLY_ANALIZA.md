# Block-only analiza: Enchanting Plus

Data: 2026-05-29

## Zakres i zrodla

Enchanting Plus ma tylko trzy bloki z mapowania projektu i wszystkie sa traktowane jako bloki z TileEntity albo jako celowo usuwany blok funkcjonalny. Nie znaleziono sensownego zakresu dla zwyklych blokow bez TE.

Zrodla lokalne:
- `mod_src/1710/actual_src/1.7.10/EnchantingPlus/`
- `mod_src/118/actual_src/1.18.2/EnchantingInfuser/`
- `src/converters/enchantingplus/mappings/block_mappings.py`
- `src/converters/enchantingplus/enchantingplus_converter.py`
- `mapa_1710/level.dat` FML `ItemData`

Dynamiczne ID z `level.dat`: `2224`, `2225`, `2226` dla blokow; `6604`, `6605`, `8111` dla itemow.

Uwaga o paczce 1.18.2: w `client_pack_1182/mod_manifest.json` nie ma obecnie `EnchantingInfuser` ani `Puzzles Lib`. Targety z istniejacego konwertera sa poprawnymi kandydatami projektowymi, ale przed krokiem 2 wymagaja dodania moda do paczki albo zmiany fallbacku.

## Tabela block-only

| numeric_id | registry_name | metadata | source variant | target block | confidence |
|---:|---|---|---|---|---|
| 2224 | `eplus:advancedEnchantmentTable` | 0-15 | advanced enchanting table, funkcjonalny TE | poza zakresem block-only; TE -> `enchantinginfuser:advanced_enchanting_infuser` po dodaniu moda do paczki | medium |
| 2225 | `eplus:arcane_inscriber` | 0-15 | arcane inscriber, funkcjonalny TE | poza zakresem block-only; obecny konwerter usuwa do `minecraft:air` | medium |
| 2226 | `eplus:enchantment_book` | 0-15 | blok/ksiazka funkcjonalna wg rejestru EP | wymagany review, nie block-only | low |

## Fallbacki

- Brak zalecanego fallbacku block-only.
- Jezeli direct writer znajdzie `eplus:*` bez TE, powinien zapisac audit i przekazac przypadek do istniejacego konwertera EP albo placeholdera funkcjonalnego, nie do dekoracyjnego block-only.

## Odrzucone / wymagajace review

- `advancedEnchantmentTable` i `arcane_inscriber` przenosza semantyke GUI/NBT, wiec nie kwalifikuja sie do tej warstwy.
- `enchantment_book` wymaga potwierdzenia w zdekompilowanym kodzie, czy w ogole wystepuje jako placeable block na mapie.

## Handoff decyzji

- Nie implementowac `block_only_converter.py` dla EP w kroku 2, dopoki skan chunkow nie pokaze realnych blokow `eplus:*` bez TE i dopoki target mod nie bedzie w paczce.
- Dla audytu centralnego routera dodac jasne ostrzezenie: `EP-W-NOT-BLOCK-ONLY`.
