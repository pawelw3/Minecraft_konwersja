# Handoff: block-only analiza mrcrayfish_furniture do witchery

## Podsumowanie sesji

Wykonano krok 1 workflow `PLAN_KONWERTERY_BLOKOW_BEZ_TILE_ENTITY.md` dla modow alfabetycznie od `mrcrayfish_furniture` do `witchery`, ktore maja katalog konwertera w `src/converters`. To jest etap analizy: raporty ustalaja zakres block-only, dynamiczne ID z `level.dat`, targety, fallbacki i przypadki odrzucone.

## Ukonczono

- [x] Zweryfikowano zakres katalogow: `mrcrayfish_furniture`, `openmodularturrets`, `projectred`, `railcraft`, `reliquary`, `thermal`, `thermal_dynamics`, `traincraft`, `witchery`.
- [x] Sprawdzono `client_pack_1182/mod_manifest.json` dla targetow: ProjectRed, Reliquary, Thermal i Hexerei sa obecne; CFM, Railcraft, K-Turrets i Steam'n'Rails nie zostaly potwierdzone w pliku manifestu.
- [x] Odczytano dynamiczne ID z `mapa_1710/level.dat` przez FML `ItemData`.
- [x] Rozdzielono bloki block-only od TE/multipart/track/network.
- [x] Dodano raporty `BLOCK_ONLY_ANALIZA.md` dla kazdego moda.

## Nowe pliki

- `src/converters/mrcrayfish_furniture/BLOCK_ONLY_ANALIZA.md`
- `src/converters/openmodularturrets/BLOCK_ONLY_ANALIZA.md`
- `src/converters/projectred/BLOCK_ONLY_ANALIZA.md`
- `src/converters/railcraft/BLOCK_ONLY_ANALIZA.md`
- `src/converters/reliquary/BLOCK_ONLY_ANALIZA.md`
- `src/converters/thermal/BLOCK_ONLY_ANALIZA.md`
- `src/converters/thermal_dynamics/BLOCK_ONLY_ANALIZA.md`
- `src/converters/traincraft/BLOCK_ONLY_ANALIZA.md`
- `src/converters/witchery/BLOCK_ONLY_ANALIZA.md`
- `docs/HANDOFF_BLOCK_ONLY_ANALIZA_MRCRAYFISH_TO_WITCHERY_2026-05-29.md`

## Decyzje mapowania

- `reliquary` i `thermal` maja najpewniejszy zakres block-only, bo target mods sa obecne i istnieja lokalne mappingi.
- `openmodularturrets`, `railcraft`, `traincraft` i `witchery` wymagaja ostroznych fallbackow/placeholderow, bo brak bezposredniego target moda albo brak potwierdzonego zamiennika.
- `thermal_dynamics` ma bardzo maly zakres block-only; wiekszosc ductow pozostaje TE/network.
- `projectred` block-only powinien ograniczyc sie do Exploration blocks; multipart i TE pozostaja w dotychczasowym konwerterze.
- `mrcrayfish_furniture` wymaga target-pack decyzji: bez CFM w pliku manifestu nie powinno sie emitowac `cfm:*` bez dodatkowej walidacji.

## Nastepne kroki

1. [ ] Krok 2: zaimplementowac `block_only_converter.py`/mappingi dla modow z raportow, zaczynajac od najwyzszej pewnosci: Reliquary, Thermal, OMT, ProjectRed.
2. [ ] Dodac testy jednostkowe dla znanych numeric ID + metadata.
3. [ ] Zweryfikowac target registry dla ProjectRed/Hexerei oraz ewentualnych `framedblocks:*`/`railways:*`.
4. [ ] Po implementacji uruchomic skupione testy pytest i smoke `map_block()`.
