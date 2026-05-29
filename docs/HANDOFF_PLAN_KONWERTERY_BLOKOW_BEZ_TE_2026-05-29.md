# Handoff: Plan konwerterow blokow bez TileEntity

## Podsumowanie sesji
Dodano dokument architektoniczny opisujacy standard dla konwerterow zwyklych blokow modowych bez TileEntity. Plan odpowiada na problem direct-konwersji, ktora gubi bloki modowe zapisane tylko jako numeric ID + metadata w chunk `Sections`.

## Ukończono
- [x] Utworzono `docs/PLAN_KONWERTERY_BLOKOW_BEZ_TILE_ENTITY.md`.
- [x] Opisano 2-krokowy workflow: analiza source kodu oraz implementacja + test headless.
- [x] Opisano integracje z direct terrain writerem i centralnym routerem block-only.
- [x] Opisano audyt `block_remap_audit.jsonl`.
- [x] Wskazano Chisel jako pierwszy kandydat do wdrozenia.

## Nowe pliki
- `docs/PLAN_KONWERTERY_BLOKOW_BEZ_TILE_ENTITY.md`
- `docs/HANDOFF_PLAN_KONWERTERY_BLOKOW_BEZ_TE_2026-05-29.md`

## Następne kroki
1. [ ] Zaimplementowac centralny router block-only.
2. [ ] Zaimplementowac pierwszy `block_only_converter` dla Chisel.
3. [ ] Podpiac router do `tasks/custom_area_1800_574/convert_area_direct.py`.
4. [ ] Wygenerowac audyt blokow modowych bez TE dla wycinka `custom_area_1800_574`.
