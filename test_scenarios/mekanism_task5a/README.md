# Mekanism Task 5A

This scenario prepares representative Mekanism 1.7.10 samples for conversion testing without editing the main map.

For the completed full Task 5A run, see `MEKANISM_TASK5A_FULL_REPORT.md`.
For Task 5B headless materialization, see `MEKANISM_TASK5B_REPORT.md`.
For Task 6 tick/restart verification, see `MEKANISM_TASK6_REPORT.md`.

Generated artifacts:

- `mekanism_task5a_source_patch_1710.json` - source patch using dynamic numeric IDs from `mapa_1710/level.dat`.
- `mekanism_task5a_converted_patch_1182.json` - target patch produced by `MekanismConverter`.
- `mekanism_task5a_conversion_report.json` - per-sample conversion results, warnings, and events.
- `mekanism_task5a_redstone_spec.json` - later headless-server redstone integration plan.
- `mekanism_task5a_realworld_converted_patch_1182.json` - target patch produced from the actually written 1.7.10 `.mca` test world.
- `mekanism_task5a_realworld_conversion_report.json` - report comparing real-world conversion with the expected generated target patch.
- `mekanism_task5a_redstone_harness_patch_1182.json` - executable TEST_START redstone bus and command block assertion patch.
- `mekanism_task5a_converted_with_redstone_patch_1182.json` - merged Mekanism conversion + redstone harness patch.
- `mekanism_task5a_redstone_harness_report.json` - harness summary and collision check against the converted Mekanism patch.
- `mekanism_task5b_headless_materialization_report.json` - dedicated 1.18.2 headless world/datapack materialization summary.

Covered real cases from Task 4:

- `QuantumEntangloporter`
- `Bin`
- `DigitalMiner`
- elite factories with different `recipeType`
- `MekanismTeleporter`
- `EnergyCube`
- `PortableTank`
- `GasTank`
- salt, bounding blocks, Obsidian TNT fallback, plastics
- ore/material/multiblock variants

Run:

```powershell
python -B test_scenarios/mekanism_task5a/generate_mekanism_task5a.py
python -B -m unittest src.converters.mekanism.tests.test_mekanism_converter src.converters.mekanism.simulations.test_simulations
```

The source patch is intended for a small 1.7.10 test world copy. The script itself is read-only toward `mapa_1710`; it only reads `level.dat` to resolve dynamic numeric IDs.

Current applied test world:

- `lightweigh_map_templates/1710_modded/mekanism_task5a_world_v2`

Verification:

```powershell
python -B test_scenarios/mekanism_task5a/verify_mekanism_task5a_world.py
```

Expected result:

- `checked_blocks = 22`
- `checked_tile_entities = 11`
- `checked_nested_te_keys = 8`
- `failure_count = 0`

Convert the applied 1.7.10 test world into a 1.18.2 patch:

```powershell
python -B test_scenarios/mekanism_task5a/convert_applied_test_world.py
```

Expected result:

- `checked_blocks = 22`
- `converted_samples = 22`
- `target_edits = 32`
- `read_failures = 0`
- `patch_mismatches = 0`
- `failure_count = 0`

Generate the 1.18.2 redstone integration harness patch:

```powershell
python -B test_scenarios/mekanism_task5a/generate_redstone_harness_patch.py
```

Expected result:

- `harness_edits = 30`
- `merged_edits = 62`
- `block_collision_count = 0`

Full Task 5A run:

```powershell
python -B test_scenarios/mekanism_task5a/generate_mekanism_task5a_full.py
python -B test_scenarios/mekanism_task5a/verify_mekanism_task5a_world.py --world lightweigh_map_templates/1710_modded/mekanism_task5a_full_world --patch test_scenarios/mekanism_task5a/mekanism_task5a_full_source_patch_1710.json --report test_scenarios/mekanism_task5a/mekanism_task5a_full_world_verify_report.json
```

Full run result:

- `samples = 224`
- `source_variants = 178`
- `block_entity_samples = 104`
- `source_edits = 328`
- `target_edits = 328`
- `full_merged_redstone_edits = 358`
- `failure_count = 0`

Task 5B headless materialization:

```powershell
python -B test_scenarios/mekanism_task5a/materialize_task5b_headless_datapack.py --overwrite
```

Current 5B result:

- `target_world = headless_server/1.18.2/world_mekanism_task5b`
- `commands = 253`
- `block_edits = 253`
- `tile_entity_edits = 105`
- server smoke boot reached `Done`
- datapack marker `[MEKANISM_TASK5B] apply complete` present

Task 6 tick/restart:

```powershell
python -B test_scenarios/mekanism_task5a/run_task6_headless_tick_restart.py --tick-seconds 180
```

Current Task 6 result:

- `status = passed`
- redstone PASS marker present
- selected Mekanism block entities retained after 180 seconds and one restart
- datapack disabled before restart, so restart did not reapply materialization
