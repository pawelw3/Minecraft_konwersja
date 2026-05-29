# Handoff: block-only analiza common -> mekanism

## Podsumowanie sesji

Wykonano krok 1 z `docs/PLAN_KONWERTERY_BLOKOW_BEZ_TILE_ENTITY.md` dla katalogow konwerterow alfabetycznie od `common` do `mekanism`. Dla kazdego katalogu dodano `BLOCK_ONLY_ANALIZA.md` z dynamicznymi ID z `mapa_1710/level.dat`, decyzja czy mod kwalifikuje sie do block-only oraz fallbackami.

## Ukonczono

- [x] `common` - brak modowego namespace, tylko wspolne helpery.
- [x] `computercraft` - awaryjny block-only tylko dla brakujacych TE.
- [x] `enchantingplus` - poza zakresem block-only, bo bloki sa funkcjonalne/TE.
- [x] `enderstorage` - poza zakresem poza awaryjnymi fallbackami z utrata frequency.
- [x] `extrautils` - kandydaci dekoracyjni i utility, z niskimi/medium confidence fallbackami.
- [x] `forge_multipart` - poza zakresem, wymaga `TileMultipart` NBT.
- [x] `growthcraft` - cropy, bambus, rosliny i proste bloki jako kandydaci.
- [x] `ic2` - rudy, tree parts, construction blocks, scaffolds, kable i proste bloki jako kandydaci.
- [x] `jammyfurniture` - meble bez inventory jako kandydaci, inventory poza block-only.
- [x] `logistics_pipes` - poza zakresem poza awaryjnymi fallbackami.
- [x] `mekanism` - rudy, material blocks, plastik i salt jako kandydaci o najwyzszym priorytecie.

## Nowe pliki

- `src/converters/common/BLOCK_ONLY_ANALIZA.md`
- `src/converters/computercraft/BLOCK_ONLY_ANALIZA.md`
- `src/converters/enchantingplus/BLOCK_ONLY_ANALIZA.md`
- `src/converters/enderstorage/BLOCK_ONLY_ANALIZA.md`
- `src/converters/extrautils/BLOCK_ONLY_ANALIZA.md`
- `src/converters/forge_multipart/BLOCK_ONLY_ANALIZA.md`
- `src/converters/growthcraft/BLOCK_ONLY_ANALIZA.md`
- `src/converters/ic2/BLOCK_ONLY_ANALIZA.md`
- `src/converters/jammyfurniture/BLOCK_ONLY_ANALIZA.md`
- `src/converters/logistics_pipes/BLOCK_ONLY_ANALIZA.md`
- `src/converters/mekanism/BLOCK_ONLY_ANALIZA.md`
- `docs/HANDOFF_BLOCK_ONLY_ANALIZA_COMMON_TO_MEKANISM_2026-05-29.md`

## Zmodyfikowane pliki

- Brak istniejacych plikow zmodyfikowanych.

## Nastepne kroki

1. [ ] Krok 2 dla najwyzszego impaktu: `mekanism`, `extrautils`, `ic2`, `growthcraft`, `jammyfurniture`.
2. [ ] Dodac wspolny `BlockOnlyResult` i centralny router block-only.
3. [ ] Zintegrowac router z direct terrain writerem i audytem `block_remap_audit.jsonl`.
4. [ ] Zweryfikowac target registry names z JAR/resource pack przed podniesieniem confidence do `high`.
