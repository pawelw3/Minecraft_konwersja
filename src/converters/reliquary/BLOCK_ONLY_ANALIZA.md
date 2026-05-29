# Block-only analiza: Reliquary

Data: 2026-05-29

## Zakres i zrodla

Reliquary 1.7.10 ma tylko trzy zwykle bloki bez TE. Altar, cauldron i mortar maja TE i zostaja w glownym konwerterze NBT. Docelowa paczka zawiera `reliquary-1.18.2-2.0.19.1161.jar`, wiec te mapowania moga byc bezposrednie po normalizacji nazw.

Zrodla lokalne:
- `src/converters/reliquary/RELIQUARY_BLOCKS_AND_TE.md`
- `mapa_1710/level.dat` FML `ItemData`
- `client_pack_1182/mod_manifest.json`

Dynamiczne ID blokow: `3189..3194` oraz `3460` altar idle.

## Tabela block-only

| numeric_id | registry_name | metadata | source variant | target block | confidence |
|---:|---|---|---|---|---|
| 3192 | `xreliquary:lilypad` | 0 | fertile lily pad | `reliquary:fertile_lily_pad` | high |
| 3193 | `xreliquary:interdiction_torch` | 0 | interdiction torch | `reliquary:interdiction_torch` | high |
| 3194 | `xreliquary:wraith_node` | 0 | wraith node | `reliquary:wraith_node` | high |

## Fallbacki

- If target registry validation fails, `lilypad` can fall back to `minecraft:lily_pad` with warning.
- Interdiction torch and wraith node should use placeholder rather than air, because they represent intentional placed utility blocks.

## Odrzucone / wymagajace review

- `xreliquary:altar`, `apothecary_cauldron`, `apothecary_mortar`, `altar_idle` are TE/NBT or stateful and outside block-only.
- Metadata beyond `0` was not found as meaningful for the three block-only blocks; step 2 should warn for nonzero metadata.

## Handoff decyzji

- Krok 2 can be a tiny static converter mapping namespace `xreliquary` to `reliquary`.
- Confidence is high because both source and target mods are present and names match semantically.
