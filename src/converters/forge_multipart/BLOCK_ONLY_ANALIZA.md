# Block-only analiza: ForgeMultipart / ForgeMicroblock

Data: 2026-05-29

## Zakres i zrodla

ForgeMultipart 1.7.10 nie zapisuje zwyklych blokow dekoracyjnych w prostym formacie ID+metadata. `ForgeMultipart:block` jest kontenerem multipart z TileEntity `TileMultipart`, a ForgeMicroblock itemy/materialy nie sa samodzielnymi blokami terrain. Z tego powodu ta warstwa nie powinna probowac konwertowac FMP jako block-only.

Zrodla lokalne:
- `mod_src/code_from_jar/1.7.10/ForgeMultipart/`
- `mod_src/118/actual_src/1.18.2/CBMultipart/`
- `src/converters/forge_multipart/mappings.py`
- `src/converters/forge_multipart/nbt_converter.py`
- `src/converters/forge_multipart/HANDOFF_MICROBLOCK_VALIDATED_MATERIALS_2026-05-29.md`
- `mapa_1710/level.dat` FML `ItemData`

Dynamiczne ID z `level.dat`: `523` dla `ForgeMultipart:block`; `5442..5446` dla itemow ForgeMicroblock.

## Tabela block-only

| numeric_id | registry_name | metadata | source variant | target block | confidence |
|---:|---|---|---|---|---|
| 523 | `ForgeMultipart:block` | 0-15 | multipart container, wymaga `TileMultipart` NBT | poza zakresem block-only; TE -> CBMultipart events | high |
| 5442 | `ForgeMicroblock:microblock` | item damage/NBT | item microblock | nie jest block terrain | high |
| 5443-5446 | `ForgeMicroblock:saw*` / `stoneRod` | item | narzedzia/materialy | nie jest block terrain | high |

## Fallbacki

- Brak bezpiecznego fallbacku block-only. Dla `ForgeMultipart:block` bez TE tylko jawny placeholder z audytem, np. `conversion_placeholders:block_entity_placeholder`.
- Nie uzywac `minecraft:stone` automatycznie, bo pojedynczy blok FMP moze reprezentowac wiele czesci i materialow.

## Odrzucone / wymagajace review

- Microblock material mapping jest juz obslugiwany w `mappings.py` i musi pozostac czescia konwertera multipart, nie direct block-only.
- Przypadki bez TE oznaczaja uszkodzone dane albo utracony `TileMultipart`.

## Handoff decyzji

- Nie implementowac klasycznego `block_only_converter.py` dla ForgeMultipart.
- Centralny router powinien rozpoznac namespace i zwrocic `requires_block_entity` z bledem audytowym, aby direct writer nie zamienial tego na air.
