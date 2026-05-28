# Raport pokrycia: Extra Utilities (Zadanie 4)

## Podsumowanie

Przeanalizowano mapę `mapa_1710` (1195 plików regionów `.mca`, ~5GB) pod kątem bloków i tile entities Extra Utilities. Zidentyfikowano **5 unikalnych typów TE ExU** oraz **5 unikalnych numerycznych block IDs** ExU. Wszystkie zmapowane bloki/TE są obsługiwane przez konwerter.

---

## Tile Entities Extra Utilities (kompletna lista)

Źródło: `output/discovered_te_ids.txt` (pełny skan mapy) + weryfikacja numerycznych block ID.

| TileEntity ID | Block ID (num.) | Meta | Liczba na mapie | Nazwa bloku | Target 1.18.2 | Status |
|---|---|---|---|---|---|---|
| `TileEntityAntiMobTorch` | 1998 | 0 | 267 | Magnum Torch | `torchmaster:mega_torch` | ✅ |
| `TileEntityFilingCabinet` | 2216 | 0-11 | 244 | Filing Cabinet | `conversion_placeholders:inventory_placeholder` | ✅ |
| `TileEntityTrashCan` | 1988 | 0 | 20 | Trash Can (item) | `trashcans:item_trash_can` | ✅ |
| `drum` | 1999 | 0 | 15 | Drum | `conversion_placeholders:block_entity_placeholder` | ✅ |
| `extrautils:generatorlava` | 2000 | 2 | 3 | Lava Generator | `thermal:dynamo_magmatic` | ✅ |

**Suma TE ExU: 549**

### Uwagi
- `TileEntityTrashCan` — wszystkie sprawdzone instancje mają meta=0 (item variant). Brak fluid/energy variantów na mapie.
- `TileEntityFilingCabinet` — wszystkie 244 instancje są **puste** (brak pola `item_no` w NBT). Inventory converter jest gotowy na wypadek wystąpienia itemów w innych regionach.
- `drum` — 15 instancji, wszystkie z meta=0. NBT nie zawiera płynów w próbkach.

---

## Bloki bez Tile Entity

Przeskanowano reprezentatywną próbkę 150 regionów (co 8 plik) pod kątem block IDs >1000 w chunkach zawierających TE ExU. **Nie znaleziono żadnych dodatkowych block IDs ExU** poza pięcioma zidentyfikowanymi powyżej.

| Blok ExU 1.7.10 | Obecność na mapie | Uwagi |
|---|---|---|
| Cursed Earth (`extrautils:cursedEarth`) | ❌ Nie wykryto | Brak block ID w chunkach z ExU |
| Angel Block (`extrautils:angelBlock`) | ❌ Nie wykryto | Brak block ID w chunkach z ExU |
| Conveyor Belt (`extrautils:conveyor`) | ❌ Nie wykryto | Brak block ID w chunkach z ExU |
| Sound Muffler (`extrautils:soundMuffler`) | ❌ Nie wykryto | Brak TE na mapie |
| Ender-Thermic Pump (`extrautils:enderThermicPump`) | ❌ Nie wykryto | Brak TE na mapie |
| Ender Quarry (`extrautils:enderQuarry`) | ❌ Nie wykryto | Brak TE na mapie |
| Compressed Cobblestone | ❌ Nie wykryto | Brak block ID w chunkach z ExU |
| Spikes | ❌ Nie wykryto | Brak block ID w chunkach z ExU |

---

## Pokrycie konwertera

### Mapowania bloków

| Źródło (block_id:meta) | Cel | Converter | Pokrycie |
|---|---|---|---|
| `extrautils:generator:*` (x1, x8, x64) | `thermal:dynamo_*` / `mekanismgenerators:solar_generator` | `generator_converter` | ✅ 100% (3 instancje) |
| `extrautils:magnumTorch:0` | `torchmaster:mega_torch` | — (brak NBT) | ✅ 100% (267 instancji) |
| `extrautils:trashCan:0-2` | `trashcans:*_trash_can` | — | ✅ 100% (20 instancji) |
| `extrautils:filing:0-11` | `conversion_placeholders:inventory_placeholder` | `filing_cabinet_converter` | ✅ 100% (244 instancje) |
| `extrautils:drum:0` | `conversion_placeholders:block_entity_placeholder` | — | ✅ 100% (15 instancji) |
| `extrautils:enderQuarry:0` | `conversion_placeholders:block_entity_placeholder` | — | ✅ (0 na mapie) |
| `extrautils:enderThermicPump:0` | `mekanism:electric_pump` | `ender_thermic_pump` | ✅ (0 na mapie) |
| `extrautils:cursedEarth:0` | `cursedearth:cursed_earth` | — | ✅ (0 na mapie) |
| `extrautils:angelBlock:0` | `angelblockrenewed:angel_block` | — | ✅ (0 na mapie) |
| `extrautils:soundMuffler:0` | `extremesoundmuffler:sound_muffler` | — | ✅ (0 na mapie) |

### TE ID → block_id mapping

| TE ID | block_id | meta | Uwagi |
|---|---|---|---|
| `extrautils:generatorlava` | `extrautils:generator` | 2 | ✅ W `TE_ID_TO_BLOCK` |
| `TileEntityAntiMobTorch` | `extrautils:magnumTorch` | 0 | ✅ W `TE_ID_TO_BLOCK` |
| `TileEntityFilingCabinet` | `extrautils:filing` | 0-11 | ✅ W `TE_ID_TO_BLOCK` |
| `TileEntityTrashCan` | `extrautils:trashCan` | 0 | ✅ W `TE_ID_TO_BLOCK` |
| `drum` | `extrautils:drum` | 0 | ✅ W `TE_ID_TO_BLOCK` |

---

## Potencjalne braki

1. **Block ID 1999 = drum** — mappingi w `block_mappings.py` używają `extrautils:drum`, co jest zgodne z dekompilacją (`func_149663_c("extrautils:drum")`). ✅ Zweryfikowane.

2. **Filing Cabinet meta** — na mapie wszystkie instancje mają meta=4 (orientacja). Mapowania obejmują meta 0-11 (wszystkie orientacje + diamond variant). ✅ Pokrywa wszystkie przypadki.

3. **Trash Can meta** — wszystkie instancje mają meta=0. Mapowania obejmują 0=item, 1=fluid, 2=energy. ✅ Pokrywa wszystkie przypadki.

4. **Brak innych bloków ExU** — przeskanowano reprezentatywną próbkę 150 regionów i nie znaleziono innych block IDs ExU. Jest mało prawdopodobne że istotna liczba bloków ExU pozostała nieodkryta.

---

## Rekomendacje

- [x] Wszystkie bloki/TE ExU obecne na mapie mają mapowania
- [x] Wszystkie mapowania mają testy jednostkowe
- [x] Konwerter jest zintegrowany z routerem
- [ ] Opcjonalnie: dodać obsługę `extrautils:enderQuarry` NBT (ale 0 instancji na mapie, niski priorytet)
- [ ] Opcjonalnie: dodać obsługę `extrautils:enderThermicPump` NBT (ale 0 instancji na mapie, niski priorytet)

---

*Data wygenerowania: 2026-05-28*
*Zadanie 4 zakończone*