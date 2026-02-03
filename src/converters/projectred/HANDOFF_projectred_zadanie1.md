# Handoff: ProjectRed - Zadanie 1 (Analiza bloków i Tile Entities)

## Podsumowanie sesji

Wykonano pełną analizę bloków i Tile Entities moda ProjectRed dla wersji 1.7.10 oraz 1.18.2+. Sklonowano kod źródłowy 1.7.10 z repozytorium GTNewHorizons (oficjalne repo nie ma już brancha 1.7.10). Stworzono dokumentację porównawczą z mapowaniem elementów między wersjami.

## Ukończono

- [x] Znaleziono i sklonowano kod źródłowy 1.7.10 (GTNewHorizons/ProjectRed)
- [x] Przeanalizowano kod źródłowy 1.18.2+ (MrTJP/ProjectRed - branch 1.18.x, faktycznie NeoForge)
- [x] Zidentyfikowano wszystkie bloki i TileEntity dla obu wersji
- [x] Stworzono mapowanie metadanych → block ID
- [x] Zidentyfikowano usunięte/dodane elementy między wersjami
- [x] Stworzono 3 pliki dokumentacji w `docs/mod_mapping_indepth/from/`

## Nowe pliki

- `mod_src/1710/actual_src/1.7.10/ProjectRed_GTNH/` - sklonowane repo GTNewHorizons/ProjectRed
- `docs/mod_mapping_indepth/from/projectred_1710_bloki_i_te.md` - analiza 1.7.10
- `docs/mod_mapping_indepth/from/projectred_1182_bloki_i_be.md` - analiza 1.18.2+
- `docs/mod_mapping_indepth/from/projectred_porownanie_1710_vs_1182.md` - porównanie i mapowanie

## Kluczowe odkrycia

### Zmiany techniczne
- **Scala → Java:** Kod 1.7.10 jest w Scali, 1.18.2+ w Javie
- **Meta → Block IDs:** System metadanych zastąpiony osobnymi blokami
- **Deepslate:** Dodane warianty deepslate dla wszystkich rud

### Usunięte elementy (brak w 1.18.2+)
| Element 1.7.10 | Sugerowany zamiennik |
|----------------|---------------------|
| TileInductiveFurnace | ElectrotineGenerator (Core) |
| TileItemImporter | Pipez / XNet |
| TileBlockPlacer | Deployer |
| TileFilteredImporter | Pipez z filtrami |
| TileTeleposer | - |
| TileDiamondBlockBreaker | BlockBreaker |
| TileICPrinter | Nowy system fabrykacji (3 stoły) |
| BlockLily | Vanilla flowers |
| BlockBarrel | Storage Drawers |
| Copper Ore/Block | Vanilla copper |

### Nowe elementy w 1.18.2+
- `transposer`, `deployer` (Expansion)
- `plotting_table`, `lithography_table`, `packaging_table` (Fabrication)
- `illumar_smart_lamp` (Illumination)
- `raw_tin_block`, `raw_silver_block` (Exploration)
- Warianty deepslate dla wszystkich rud

## Następne kroki (Zadanie 2+)

1. [ ] Przygotować symulacje działania kluczowych maszyn (BatteryBox, PowerConductor)
2. [ ] Napisać kod konwersji dla bloków z metadatą → osobne bloki
3. [ ] Zweryfikować kompatybilność NBT dla multipart (bramki, przewody)
4. [ ] Sprawdzić mapę główną pod kątem użycia usuniętych elementów

## Uwagi dla kolejnych zadań

- **Kod 1.7.10 w Scali** - może być trudniejszy do analizy niż Java
- **Multipart** - bramki i przewody są w ForgeMultipart, nie standardowymi blokami
- **System energii** - ProjectRed ma własny system energii (Electrotine), nie RF/FE
- **ICPrinter zastąpiony** - nowy system fabrykacji wymaga zrozumienia (3 stoły zamiast 1)

## Statystyki

| Kategoria | 1.7.10 | 1.18.2+ |
|-----------|--------|---------|
| Bloki (unique) | ~20 (z meta) | ~50 (osobne) |
| TileEntity/BlockEntity | ~20 | ~15 |
| Multipart types | ~10 | ~10 |
| Moduły | 8 | 7 (brak Transportation?) |
