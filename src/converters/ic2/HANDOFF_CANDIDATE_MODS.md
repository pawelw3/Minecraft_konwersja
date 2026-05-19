# Handoff: Pobieranie modów kandydackich i specyfikacja Tier-1

## Podsumowanie sesji

Pobrano 7 modów kandydackich dla konwersji IC2 1.7.10 → 1.18.2, zweryfikowano ich blockstates i utworzono pełne alternatywne mapowania Tier-1 (Industrial Reborn + FTBIC). Dodano również dokumentację kandydackich modów Tier-2 do Tier-5.

## Ukończono

- [x] Pobranie 7 modów kandydackich do `mod_src/118/mod_jars/candidates/`:
  - FTB Industrial Contraptions 1802.1.6-build.220 (ftbic)
  - Industrial Reborn 1.18.2-0.13.0 (indreb)
  - Industrial Foregoing 1.18.2-3.3.1.6-10
  - Immersive Engineering 1.18.2-8.4.0-161
  - Modular Routers 1.18.2-9.1.2
  - SecurityCraft 1.18.2-v1.10.1
  - Simply Light 1.18.2-1.4.5-build.43
- [x] Weryfikacja modId z `META-INF/mods.toml` dla wszystkich modów
- [x] Ekstrakcja nazw bloków z `assets/{modid}/blockstates/` (1113+ entries)
- [x] Utworzenie `tier1_alternative_mappings.py` z 97 mapowaniami statycznymi + 16 resource dla każdego z Tier-1 modów
- [x] **Migracja `block_mappings.py` na Tier-1 first**: indreb jako główny target, ftbic jako fallback
- [x] Aktualizacja `block_mappings.py` o komentarze z alternatywami Tier-1/2/3/4/5
- [x] Utworzenie `CANDIDATE_MODS.md` z pełną dokumentacją inwentaryzacji i rekomendacjami
- [x] Weryfikacja pokrycia kluczy: 0 brakujących w INDREB i FTBIC vs bazowe `STATIC_MAPPINGS`
- [x] Wszystkie 20 istniejących testów przechodzą

## Nowe pliki

- `mod_src/118/mod_jars/candidates/ftb-industrial-contraptions-1802.1.6-build.220.jar`
- `mod_src/118/mod_jars/candidates/indreb-1.18.2-0.13.0.jar`
- `mod_src/118/mod_jars/candidates/industrial-foregoing-1.18.2-3.3.1.6-10.jar`
- `mod_src/118/mod_jars/candidates/ImmersiveEngineering-1.18.2-8.4.0-161.jar`
- `mod_src/118/mod_jars/candidates/modular-routers-1.18.2-9.1.2.jar`
- `mod_src/118/mod_jars/candidates/SecurityCraft-1.18.2-v1.10.1.jar`
- `mod_src/118/mod_jars/candidates/simplylight-1.18.2-1.4.5-build.43.jar`
- `src/converters/ic2/mappings/tier1_alternative_mappings.py`
- `src/converters/ic2/CANDIDATE_MODS.md`

## Zmodyfikowane pliki

- `src/converters/ic2/mappings/block_mappings.py` – **przepisano na Tier-1 first** (indreb główny, ftbic fallback); real-block coverage wzrósł z 54.9% do 61.9%

## Kluczowe odkrycia

1. **Industrial Reborn (`indreb`)** to najbliższy 1:1 następca IC2:
   - Ma `luminator`, `reinforced_stone`, `reinforced_glass`, `construction_foam_wall_*` (16 kolorów!)
   - Ma `rubber_log`, `rubber_leaves`, `rubber_sapling`, `rubber_planks`, `resin_sheet`
   - Ma wszystkie kable IC2 (`copper_cable`, `gold_cable`, `hv_cable`, `glass_fibre_cable`)
   - Używa FE – bezproblemowa integracja z Mekanism/Thermal
   - Pokrywa ~75% bloków IC2 jako real-block conversions

2. **FTBIC (`ftbic`)** uzupełnia braki Industrial Reborn:
   - Ma `nuclear_reactor`, `nuclear_reactor_chamber`, `teleporter`, `quarry`, `pump`
   - Ma tierowane maszyny, baterie, kable i solary (LV/MV/HV/EV)
   - Używa własnego systemu Zaps – wymaga konwersji energii przy integracji

3. **`block_mappings.py` po migracji:**
   - Placeholdery: 43 (z 51) – **-8**
   - Tier-1 real blocks: 66 (58.4%)
   - Real-block coverage: **61.9%** (wzrost z 54.9%)

## Następne kroki

1. [x] ~~Zdecydować czy użyć Tier-1A (indreb), Tier-1B (ftbic) czy hybrydy~~ **Zrobione – hybryda w `block_mappings.py`**
2. [ ] Zaimplementować NBT converters dla `indreb` (sprawdzić czy używa tego samego formatu NBT co IC2 czy nowego)
3. [ ] Zaimplementować NBT converters dla `ftbic` (uwzględniając system Zaps)
4. [ ] Przetestować konwersję na testowej mapie z wybranymi Tier-1 modami
5. [ ] Rozważyć dodanie Modular Routers dla Item Buffer, Industrial Foregoing dla Crop Harvester
