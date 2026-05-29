# Block-only analiza: ProjectRed

Data: 2026-05-29

## Zakres i zrodla

ProjectRed ma trzy glowne grupy w swiecie: TE, multipart oraz proste bloki Exploration. Block-only dotyczy glownie rud, kamieni, scian i ewentualnej lilii z Exploration. Lampy, maszyny i IC block maja TE; przewody i bramki sa multipartami.

Zrodla lokalne:
- `src/converters/projectred/HANDOFF_projectred_zadanie4.md`
- `src/converters/projectred/mappings/block_mappings.py`
- `mapa_1710/level.dat` FML `ItemData`
- `client_pack_1182/mod_manifest.json`

Docelowa paczka zawiera ProjectRed 1.18.2 core/expansion/exploration/fabrication/illumination/integration/transmission.

## Tabela block-only

| numeric_id | registry_name | metadata | source variant | target block | confidence |
|---:|---|---|---|---|---|
| 3575 | `ProjRed|Exploration:projectred.exploration.ore` | 0 | ruby ore | `projectred_exploration:ruby_ore` | medium |
| 3575 | `ProjRed|Exploration:projectred.exploration.ore` | 1 | sapphire ore | `projectred_exploration:sapphire_ore` | medium |
| 3575 | `ProjRed|Exploration:projectred.exploration.ore` | 2 | peridot ore | `projectred_exploration:peridot_ore` | medium |
| 3575 | `ProjRed|Exploration:projectred.exploration.ore` | 3 | electrotine ore | `projectred_exploration:electrotine_ore` | medium |
| 3576 | `ProjRed|Exploration:projectred.exploration.stone` | 0 | marble | `projectred_exploration:marble` | medium |
| 3576 | `ProjRed|Exploration:projectred.exploration.stone` | 1 | basalt | `projectred_exploration:basalt` | medium |
| 3576 | `ProjRed|Exploration:projectred.exploration.stone` | 2-15 | stone decorative variants | matching PR Exploration decorative block or vanilla stone fallback | low |
| 3577 | `ProjRed|Exploration:projectred.exploration.stonewalls` | 0 | marble wall | `projectred_exploration:marble_wall` or `minecraft:stone_brick_wall` | medium |
| 3577 | `ProjRed|Exploration:projectred.exploration.stonewalls` | 1 | basalt wall | `projectred_exploration:basalt_wall` or `minecraft:blackstone_wall` | medium |
| 3577 | `ProjRed|Exploration:projectred.exploration.stonewalls` | 2-15 | wall decorative variants | PR wall if exists, else vanilla wall fallback | low |
| 3578 | `ProjRed|Exploration:projectred.exploration.lily` | 0 | ore lily / decorative lily | `minecraft:lily_pad` or remove by explicit mapping | low |
| 3579 | `ProjRed|Exploration:projectred.exploration.barrel` | 0 | barrel, likely inventory TE | outside block-only when TE exists | high |

## Fallbacki

- Ores should prefer ProjectRed Exploration targets because the mod is installed.
- If exact namespace differs in 1.18.2, fallback can be matching vanilla/thermal gem ore only after registry validation.
- Lily is known from previous coverage as removed/unsupported; `minecraft:lily_pad` is the no-TE visual fallback.
- Unknown Exploration decorative stones: `minecraft:stone`, `minecraft:polished_blackstone`, or placeholder with audit.

## Odrzucone / wymagajace review

- `projectred.illumination.lamp`, `airousLight`, `machine1`, `machine2`, `icblock` are TE/functional.
- `projectred.exploration.barrel` should stay TE/inventory-owned.
- `ProjRed|Transmission:*` wires and `ProjRed|Integration:*` gates are multipart, outside this workflow.
- Exact 1.18.2 registry namespace for ProjectRed Exploration must be checked in step 2 before hard-coding.

## Handoff decyzji

- Krok 2 should implement Exploration block-only only, not PR multipart.
- Add target-existence validation against the 1.18.2 registry/JAR names because old FML names include module prefixes.
