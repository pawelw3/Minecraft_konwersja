# Reliquary Task 5B – Raport materializacji

## Podsumowanie

- Status: `world_copy_prepared_with_datapack`
- Target world: `headless_server\1.18.2\world_reliquary_task5b`
- Komendy setblock: 16
- Edycje bloków: 14
- Edycje BlockEntity: 11
- Fallbacki (brak moda): 0

## Uwaga o fallbackach

Reliquary nie jest zainstalowany na headless serwerze. Bloki TE (altar, cauldron, mortar) zmaterializowano jako `conversion_placeholders:block_entity_placeholder` z pełnym NBT 1.18.2. Bloki bez TE (lily_pad, torch, stone) zmapowano na najbliższy odpowiednik vanilla.

## Resolutions per próbka

| Blok źródłowy | Target | Fallback |
|---------------|--------|----------|
| `reliquary:alkahestry_altar` | `reliquary:alkahestry_altar` | ✅ |
| `reliquary:alkahestry_altar` | `reliquary:alkahestry_altar` | ✅ |
| `reliquary:apothecary_cauldron` | `reliquary:apothecary_cauldron` | ✅ |
| `reliquary:apothecary_cauldron` | `reliquary:apothecary_cauldron` | ✅ |
| `reliquary:apothecary_cauldron` | `reliquary:apothecary_cauldron` | ✅ |
| `reliquary:apothecary_cauldron` | `reliquary:apothecary_cauldron` | ✅ |
| `reliquary:apothecary_mortar` | `reliquary:apothecary_mortar` | ✅ |
| `reliquary:apothecary_mortar` | `reliquary:apothecary_mortar` | ✅ |
| `reliquary:apothecary_mortar` | `reliquary:apothecary_mortar` | ✅ |
| `reliquary:apothecary_mortar` | `reliquary:apothecary_mortar` | ✅ |
| `reliquary:apothecary_mortar` | `reliquary:apothecary_mortar` | ✅ |
| `reliquary:fertile_lily_pad` | `reliquary:fertile_lily_pad` | ✅ |
| `reliquary:interdiction_torch` | `reliquary:interdiction_torch` | ✅ |
| `reliquary:wraith_node` | `reliquary:wraith_node` | ✅ |

## Pliki

- `reliquary_task5b_headless_materialization_report.json`
- `server_reliquary_task5b.properties`
- `headless_server/1.18.2/world_reliquary_task5b/datapacks/reliquary_task5b/`

## Następne kroki

1. Uruchomić headless 1.18.2 z `server_reliquary_task5b.properties` jako `server.properties`.
2. Potwierdzić w logu marker `[RELIQUARY_TASK5B] apply complete`.
3. W Zadaniu 6 wykonać tick/restart verification.
4. Po zainstalowaniu JARa Reliquary powtórzyć 5B bez fallbacków.
