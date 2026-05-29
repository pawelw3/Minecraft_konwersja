# Handoff: Rekonwersja block-only (bloki bez TE)

## Podsumowanie sesji
Wykonano rekonwersję terenu `custom_area_1800_574` z użyciem nowych block-only konwerterów dla 6 modów: ae2, bibliocraft, bigreactors, bloodmagic, buildcraft, chisel. Zachowano playerdata, backpacks, level.dat, datapacks. Nie wykonywano ponownej konwersji skinów Armourer's Workshop (brak ich w świecie docelowym) ani backpacków (już skonwertowane).

## Ukończono
- [x] Naprawiono importy `src.converters` -> `converters` w 6 mod-specific block-only converterach
- [x] Poprawiono BiblioCraft mappings: dodano `bibliocraft:bibliobell`, `bibliocraft:biblioseats`, `bibliocraft:bibliomapframe`
- [x] Poprawiono BuildCraft mappings: dodano `buildcraft|builders:frameblock`
- [x] Zapisano 1148/1148 chunków do 1.18.2 (2 regiony: r.-4.-2.mca, r.-3.-2.mca)
- [x] Zastosowano 131178/131178 eventów modowych przez JVM worker (0 błędów)
- [x] Zachowano wszystkie dane świata poza regionami (playerdata, backpacks, datapacks, poi, entities)

## Wyniki block-only
| Mod | Bloki zamapowane | Przykładowe targety |
|-----|-----------------|---------------------|
| appliedenergistics2 | 1978 | ae2:smooth_sky_stone_block |
| AWWayofTime (BloodMagic) | 240 | bloodmagic:earth/air/water/dusk_ritual_stone |
| BigReactors | 192 | biggerreactors:uranium_block, cyanite_block, graphite_block |
| BiblioCraft | 101 | minecraft:bell, minecraft:*_stairs (seat), minecraft:air (inne) |
| BuildCraft\|Builders | 30 | minecraft:iron_bars (frameBlock) |
| chisel | 310119 | rechiseled:* (family-level mapping) |

Poprzednio `requires_event_or_failed_to_air`: 15714
Teraz `requires_event_or_failed_to_air`: 15583
**Różnica: 131 bloków więcej zostało poprawnie zamapowanych** (głównie BiblioCraft seats/bell + BuildCraft frames).

## Pliki
- Świat docelowy: `tasks/custom_area_1800_574/world`
- Backup starych regionów: `world/region_backup_20260529_190948`
- Audit block-only: `block_remap_audit.jsonl`
- Skrypt rekonwersji: `reconvert_block_only.py`

## Uwagi
- Skin database Armourer's Workshop nie jest obecna w `world/` (ani w podfolderach). Poprzedni handoff wspominał `world/skin-library`, ale folder ten nie istnieje – prawdopodobnie został usunięty w którejś z wcześniejszych konwersji przez `prepare_world()`.
- Bloki z TileEntity (np. AE2 Controller, BiblioCraft Table, BuildCraft Pump) nadal są zamieniane na air i obsługiwane przez eventy `events.jsonl` – to zamierzone.
