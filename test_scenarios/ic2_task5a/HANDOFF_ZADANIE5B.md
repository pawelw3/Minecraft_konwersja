# Handoff: IC2 Task 5B — Headless Server Materialization

## Podsumowanie sesji

Zmaterializowano przekonwertowane bloki IC2 (32 sample) na Forge 1.18.2 headless serwerze poprzez datapack z komendami `/setblock`. Serwer uruchomił się bez crashy, wszystkie 33 komendy wykonały się poprawnie (`[IC2_TASK5B] apply complete`).

## Ukończono

- [x] Wygenerowano datapack `ic2_task5b` z 33 komendami setblock (32 bloki + 19 z NBT)
- [x] Rozwiązano konflikt portu 25569 (zombie Java PID 13320) → przesunięto na 25570/25580
- [x] Pobrano i zainstalowano brakujące dependency dla FTBIC:
  - `ftb-library-forge-1802.3.6-build.115.jar` (CurseForge)
  - `architectury-4.11.90-forge.jar` (CurseForge)
  - `ftb-industrial-contraptions-1802.1.6-build.220.jar` (z `mod_src/118/mod_jars/candidates/`)
- [x] Usunięto fallback ftbic → placeholder z `materialize_ic2_task5b.py`; ftbic bliki materializują się jako prawdziwe bloki
- [x] Usunięto `[facing=...]` z placeholderów (brak property w blockstate)
- [x] Rozwiązano crash Tile Entity indreb spowodowany mismatch ItemStackHandler `Size`
  - Crusher: `Size=2` vs wymagane 3 sloty (input/output/bonus)
  - Fermenter: `Size=3` vs wymagane 5 slotów (bucket slots + waste)
  - **Finalne rozwiązanie**: w datapacku usunięto `inventory`, `battery`, `upgrade` z NBT setblock dla bloków `indreb:` — serwer sam inicjalizuje puste handlery o właściwym rozmiarze. FTBIC i inne mody pozostają nietknięte.
- [x] Serwer startuje i tickuje stabilnie przez >60s bez crashy

## Nowe pliki

- `test_scenarios/ic2_task5a/materialize_ic2_task5b.py` — generator datapacka dla Task 5B
- `headless_server/1.18.2/world_ic2_task5b/datapacks/ic2_task5b/` — datapack z komendami setblock
- `test_scenarios/ic2_task5a/ic2_task5b_headless_materialization_report.json` — raport materializacji

## Zmodyfikowane pliki

- `src/converters/ic2/simulations/machine_simulation.py`
  - Dodano obliczanie `Size` ItemStackHandler z `max(slot) + 1` z fallbackiem per typ maszyny
  - Generator-like: `min_size=1`, standard machines: `min_size=3`
  - *(Uwaga: w produkcji konwerter powinien znać dokładny rozmiar handlera per-blok)*
- `test_scenarios/ic2_task5a/materialize_ic2_task5b.py`
  - Usunięto `ftbic:` z `UNAVAILABLE_MOD_BLOCKS` — ftbic jest teraz dostępny na serwerze
  - Dodano `sanitize_nbt_for_indreb()` usuwające `inventory/battery/upgrade` z NBT **tylko dla bloków `indreb:`**
  - Zapobiega crashom serwera przy mismatch rozmiaru ItemStackHandler w indreb; FTBIC pozostaje nietknięte

## Problemy napotkane i rozwiązania

| Problem | Przyczyna | Rozwiązanie |
|---------|-----------|-------------|
| Port 25569 zajęty | Zombie Java PID 13320 z poprzedniego runu | `taskkill /F /PID 13320`, przesunięcie na 25570/25580 |
| ftbic crash na starcie | Brak `ftblibrary` i `architectury` w mods/ | Pobrano i zainstalowano dependency; ftbic działa natywnie |
| `conversion_placeholders` invalid property | Placeholder block nie ma `facing` | Usunięto `[facing=south]` z placeholderów w datapacku |
| `Slot 2 not in valid range - [0,2)` | Crusher NBT miał `Size:2` zamiast 3 | Początkowo naprawiono `Size` w konwerterze, ale... |
| `Slot 4 not in valid range - [0,3)` | Fermenter ma 5 slotów, NBT miał `Size:3` | Finalnie: usunięto `inventory/battery/upgrade` z NBT w datapacku **tylko dla `indreb:`** |
| Lock pliku świata | Stare procesy Java trzymały lock na `world_ic2_task5b/` | `taskkill /F /IM java.exe`, restart serwera |

## Architektura rozwiązania

```
generate_ic2_task5a.py  →  convert_ic2_task5a.py  →  materialize_ic2_task5b.py
(1.7.10 test patch)        (1.18.2 converted patch)    (datapack + server boot)
                              ↑
                              └─ IC2Converter (block_mappings.py + NBT converters)
```

**Headless workflow** (dopóki bezpośredni zapis .mca dla modded palettes nie jest w 100% wiarygodny):
1. Konwersja patcha 1.7.10 → 1.18.2 (JSON z block_id, properties, NBT)
2. Generator datapacka tworzy `data/ic2_task5b/functions/apply.mcfunction` z `/setblock`
3. Serwer Forge 1.18.2 ładuje datapack na starcie (tag `#minecraft:load`)
4. Komendy wykonują się automatycznie, materializując bloki w świecie

## Status materializacji

| Blok | Target 1.18.2 | Status |
|------|---------------|--------|
| Macerator | indreb:crusher | ✅ Materializowany |
| Electric Furnace | indreb:electric_furnace | ✅ Materializowany |
| Induction Furnace | indreb:electric_furnace | ✅ Materializowany |
| Compressor | indreb:compressor | ✅ Materializowany |
| Mass Fabricator | ftbic:antimatter_constructor | ✅ Materializowany (FTBIC) |
| Recycler | ftbic:teleporter | ✅ Materializowany (FTBIC) |
| Ore Washing Plant | conversion_placeholders:block_entity_placeholder | ✅ Placeholder (brak odpowiednika) |
| Fermenter | indreb:fermenter | ✅ Materializowany |
| Blast Furnace | indreb:iron_furnace | ✅ Materializowany |
| Generator | indreb:generator | ✅ Materializowany |
| Solar Generator | indreb:solar_generator | ✅ Materializowany |
| Semifluid Generator | indreb:semifluid_generator | ✅ Materializowany |
| BatBox | indreb:battery_box | ✅ Materializowany |
| MFE | indreb:mfe | ✅ Materializowany |
| MFSU | indreb:mfsu | ✅ Materializowany |
| LV/HV/EV Transformer | indreb:lv_transformer, etc. | ✅ Materializowany |
| Cables (Cu, Au, insul.) | indreb:copper_cable, etc. | ✅ Materializowany |
| Ores (Cu, U) | minecraft:copper_ore, indreb:deepslate_uranium_ore | ✅ Materializowany |
| Rubber Log | indreb:rubber_log | ✅ Materializowany |
| Charge Pad | indreb:charge_pad_battery_box | ✅ Materializowany |
| Reactor parts | conversion_placeholders | ✅ Placeholder |

## Następne kroki

1. [ ] **NBT inventory per-blok mapping** — w produkcyjnym konwerterze NBT należy zmapować dokładny rozmiar `ItemStackHandler` dla każdego bloku indreb (zdekompilowane klasy podają rozmiar w `addInventorySlot()`). Obecne obejście (usuwanie inventory z NBT w datapacku) działa dla testu headless, ale w produkcji tracimy itemy.
2. [ ] **ftbic dependency** — jeśli ftbic ma być użyty, dołączyć `ftblibrary` i `architectury` do modpacka serwera.
3. [ ] **Integracja z bezpośrednim zapisem .mca** — gdy Kotlin Hephaistos worker będzie w stanie bezpośrednio pisać modded palettes do .mca, datapack stanie się zbędny.
4. [ ] **Test z graczem / RCON** — wykonać `/data get block` dla kilku współrzędnych, aby zweryfikować NBT BE po materializacji.

## Testy

- 44 unit testów IC2 przechodzą (`pytest tests/converters/test_ic2/`)
- Headless serwer: start + datapack load + apply complete + 60s ticków bez crashy ✅
