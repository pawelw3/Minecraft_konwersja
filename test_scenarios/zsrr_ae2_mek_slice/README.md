# ZSRR AE2 + Mekanism 300x300 slice

Builds a small Minecraft 1.7.10 save from `mapa_1710`:

- source block bounds: `x=-2565..-2266`, `z=-2301..-2002`
- output: `lightweigh_map_templates/1710_modded/zsrr_ae2_mek_300`
- spawn: `-2416 72 -2152`
- default gamemode: creative

Run:

```powershell
python -B test_scenarios\zsrr_ae2_mek_slice\build_1710_zsrr_slice.py
```

The crop is chunk-aligned, so the actual terrain included is slightly larger than 300x300.

If the 1.7.10 slice crashes while ticking ComputerCraft tiles, sanitize the
non-target ComputerCraft tiles:

```powershell
python -B test_scenarios\zsrr_ae2_mek_slice\sanitize_1710_slice.py
java -jar jvm\worker\build\libs\mc-editkit-worker-1.0-SNAPSHOT.jar `
  --world lightweigh_map_templates\1710_modded\zsrr_ae2_mek_300 `
  --patch test_scenarios\zsrr_ae2_mek_slice\zsrr_ae2_mek_300_sanitize_1710_patch.json
```

This keeps the source `mapa_1710` untouched and only edits the copied test save.

## 1.18.2 event conversion

Generate streamed vanilla block events for the copied terrain first:

```powershell
python -B test_scenarios\zsrr_ae2_mek_slice\generate_vanilla_block_events_1182.py
```

Generate Event JSON with AE2/Mekanism conversions and placeholder fallback:

```powershell
python -B test_scenarios\zsrr_ae2_mek_slice\convert_zsrr_slice_events_with_fallback.py
```

Apply vanilla blocks first, then BlockEntities. The vanilla event file is JSONL
so the worker streams it instead of loading millions of events at once:

```powershell
java -jar jvm\worker\build\libs\mc-editkit-worker-1.0-SNAPSHOT.jar `
  --apply-events test_scenarios\zsrr_ae2_mek_slice\zsrr_ae2_mek_vanilla_blocks_1182.jsonl `
  --target-world headless_server\1.18.2\world_zsrr_ae2_mek_events
```

Apply the AE2/Mekanism/placeholder layer after terrain so machine blocks replace
the vanilla/background blocks at their original positions:

```powershell
java -jar jvm\worker\build\libs\mc-editkit-worker-1.0-SNAPSHOT.jar `
  --apply-events test_scenarios\zsrr_ae2_mek_slice\zsrr_ae2_mek_slice_events_1182.json `
  --target-world headless_server\1.18.2\world_zsrr_ae2_mek_events
```

Prepared output world:

- `headless_server/1.18.2/world_zsrr_ae2_mek_events`

## 1.7.10 placeholder safety copy

There is also a safer 1.7.10 slice variant where vanilla, AE2 and Mekanism
blocks stay as-is, while every other modded block is replaced by the local
placeholder mod:

- world: `lightweigh_map_templates/1710_modded/zsrr_ae2_mek_300_placeholders_1710`
- placeholder mod source: `jvm/placeholder_mod_1710`
- placeholder JAR: `jvm/placeholder_mod_1710/build/libs/ConversionPlaceholders1710-1.0.0.jar`
- copied for launch into:
  - `modpack_1710/ConversionPlaceholders1710-1.0.0.jar`
  - `headless_server/1.7.10/mods/ConversionPlaceholders1710-1.0.0.jar`
- `level.dat` contains both `FML.ItemData` mappings and a `FML.ModList`
  entry for `conversionplaceholders1710`; without the mod list entry Forge
  1.7.10 may treat the placeholder registry as missing during world remap.
- by default `level.dat` keeps the full 1.7.10 modpack registry and only adds
  `conversionplaceholders1710`; this is required when opening the world in a
  client that still loads the full modpack, because Forge injects loaded mod IDs
  that are missing from the world registry and can overflow block ID `4095`.
- for a truly minimal AE2/Mekanism/placeholder runtime, pass
  `--minimal-registry` to prune stale `FML.ItemData` and `FML.ModList` entries.

Regenerate that world:

```powershell
python -B test_scenarios\zsrr_ae2_mek_slice\build_1710_zsrr_placeholder_world.py
java -jar jvm\worker\build\libs\mc-editkit-worker-1.0-SNAPSHOT.jar `
  --world lightweigh_map_templates\1710_modded\zsrr_ae2_mek_300_placeholders_1710 `
  --patch test_scenarios\zsrr_ae2_mek_slice\zsrr_ae2_mek_300_placeholders_1710_patch.json
```

For a minimal runtime without the removed mods loaded:

```powershell
python -B test_scenarios\zsrr_ae2_mek_slice\build_1710_zsrr_placeholder_world.py --minimal-registry
```

Build the 1.7.10 placeholder mod:

```powershell
new_mod_trial\gradlew.bat -p jvm\placeholder_mod_1710 build --no-daemon --console=plain
```

If an existing placeholder world still contains stale Forge registry data,
clean only its `level.dat`:

```powershell
python -B test_scenarios\zsrr_ae2_mek_slice\prune_1710_placeholder_level_dat.py `
  --world lightweigh_map_templates\1710_modded\zsrr_ae2_mek_300_placeholders_1710
```

If the full client modpack still shows the backup `level.dat` prompt or logs
`Invalid id ... maximum id range exceeded` during `GameData.injectWorldIDMap`,
repair the registry from a known-good client-created 1.7.10 world:

```powershell
python -B test_scenarios\zsrr_ae2_mek_slice\repair_1710_placeholder_registry.py `
  --source-level-dat "$env:APPDATA\.minecraft\saves\New World placeholders\level.dat" `
  --target-world lightweigh_map_templates\1710_modded\zsrr_ae2_mek_300_placeholders_1710
```

Current verified placeholder copy:

- template: `lightweigh_map_templates/1710_modded/zsrr_ae2_mek_300_placeholders_1710`
- headless: `headless_server/1.7.10/zsrr_placeholder_test`
- placeholder blocks: `131296`
- placeholder tile entities: `131296`
- repaired full-client `level.dat`: `8107` `FML.ItemData` entries, `107` `FML.ModList`
  entries, placeholder block/item mapped to ID `4095`, no block mapping above
  `4095`
