# Armourer's Workshop Task 6 - Raport headless tick/restart

## Podsumowanie

- Status: `passed`
- Overall pass: `true`
- Tick wait: 180 s
- World: `world_armourers_workshop_task5b`

## Wyniki faz

- post-apply checks: `true`
- after-ticks checks: `true`
- after-restart checks: `true`
- apply marker found: `true`
- critical log lines: 0

## Bloki SUT

| Nazwa | Pozycja | Oczekiwany blok | Post-apply | Po restarcie |
|-------|---------|-----------------|-----------|--------------|
| `skin_library` | 160,70,160 | `armourers_workshop:skin-library` | TAK | TAK |
| `skin_library_global` | 163,70,160 | `armourers_workshop:skin-library-global` | TAK | TAK |
| `skinning_table` | 166,70,160 | `armourers_workshop:skinning-table` | TAK | TAK |
| `dye_table` | 169,70,160 | `armourers_workshop:dye-table` | TAK | TAK |
| `colour_mixer` | 172,70,160 | `armourers_workshop:colour-mixer` | TAK | TAK |
| `armourer` | 175,70,160 | `armourers_workshop:armourer` | TAK | TAK |
| `bounding_box` | 178,70,160 | `armourers_workshop:bounding-box` | TAK | TAK |
| `skin_cube` | 181,70,160 | `armourers_workshop:skin-cube` | TAK | TAK |
| `skin_cube_glass` | 160,70,163 | `armourers_workshop:skin-cube-glass` | TAK | TAK |
| `skin_cube_glowing` | 163,70,163 | `armourers_workshop:skin-cube-glowing` | TAK | TAK |
| `skin_cube_glass_glowing` | 166,70,163 | `armourers_workshop:skin-cube-glass-glowing` | TAK | TAK |
| `hologram_projector` | 169,70,163 | `armourers_workshop:hologram-projector` | TAK | TAK |
| `outfit_maker` | 181,70,163 | `armourers_workshop:outfit-maker` | TAK | TAK |
| `mannequin_inv_placeholder` | 172,70,163 | `conversion_placeholders:inventory_placeholder` | TAK | TAK |
| `doll_be_placeholder` | 175,70,163 | `conversion_placeholders:block_entity_placeholder` | TAK | TAK |
| `mini_armourer_be_placeholder` | 178,70,163 | `conversion_placeholders:block_entity_placeholder` | TAK | TAK |
| `skinnable_barrel_south` | 160,70,166 | `armourers_workshop:skinnable` | TAK | TAK |
| `skinnable_noskin_north` | 160,70,169 | `armourers_workshop:skinnable` | TAK | TAK |

## Logi

- Apply marker `[AW_TASK5B] apply complete`: 3x
- Critical log lines: 0
- Unknown block: False
- Skipping BlockEntity: False
- Crash: False

## Pliki

- `run_task6_headless_tick_restart.py`
- `armourers_workshop_task6_headless_tick_restart_report.json`
- `headless_server/1.18.2/server_armourers_workshop_task6_*_out.log`
