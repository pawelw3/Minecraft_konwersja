# Block-only analiza: Open Modular Turrets

Data: 2026-05-29

## Zakres i zrodla

OMT ma mala, jasna grupe zwyklych blokow bez TE: hard walls i fences. Bazy, glowice, expandery i lever maja TileEntity albo sa czescia konwersji funkcjonalnej i nie naleza do warstwy block-only.

Zrodla lokalne:
- `src/converters/openmodularturrets/OMT_BLOCKS_AND_TE.md`
- `mapa_1710/level.dat` FML `ItemData`
- `client_pack_1182/mod_manifest.json`

K-Turrets jest opisany jako zamiennik, ale nie widac go w `client_pack_1182/mod_manifest.json`; block-only musi wiec miec fallback vanilla/placeholder.

## Tabela block-only

| numeric_id | registry_name | metadata | source variant | target block | confidence |
|---:|---|---|---|---|---|
| 4013 | `openmodularturrets:hardWallTierOne` | 0 | hard wall tier 1 | `minecraft:obsidian` | medium |
| 4026 | `openmodularturrets:hardWallTierTwo` | 0 | hard wall tier 2 | `minecraft:obsidian` | medium |
| 4008 | `openmodularturrets:hardWallTierThree` | 0 | hard wall tier 3 | `minecraft:netherite_block` or placeholder | low |
| 4010 | `openmodularturrets:hardWallTierFour` | 0 | hard wall tier 4 | `minecraft:netherite_block` or placeholder | low |
| 4020 | `openmodularturrets:hardWallTierFive` | 0 | hard wall tier 5 | placeholder defensive block | low |
| 4001 | `openmodularturrets:fenceTierOne` | 0 | fence tier 1 | `minecraft:iron_bars` | medium |
| 4029 | `openmodularturrets:fenceTierTwo` | 0 | fence tier 2 | `minecraft:iron_bars` | medium |
| 4016 | `openmodularturrets:fenceTierThree` | 0 | fence tier 3 | `minecraft:iron_bars` | medium |
| 4021 | `openmodularturrets:fenceTierFour` | 0 | fence tier 4 | `minecraft:iron_bars` | medium |
| 4017 | `openmodularturrets:fenceTierFive` | 0 | fence tier 5 | `minecraft:iron_bars` | medium |

## Fallbacki

- Hard wall tiers 1-2: `minecraft:obsidian` preserves defensive intent but not exact tier.
- Hard wall tiers 3-5: placeholder is safer than pretending exact blast resistance; `minecraft:netherite_block` is only visual/material fallback.
- Fences: `minecraft:iron_bars` preserves thin collision/visual role better than full blocks.

## Odrzucone / wymagajace review

- `baseTier*`, turret heads, `expanderPower*`, `expanderInv*`, `leverBlock` are outside block-only.
- K-Turrets targets should not be emitted until the mod is actually present in the 1.18.2 pack.

## Handoff decyzji

- Krok 2 can implement a compact static table for 10 IDs.
- Unknown OMT block in block-only path should be ignored by this converter so the TE/event converter can own it.
