# Handoff: Witchery – Zadanie 2 (Ukończone)

## ⚠️ UPROSZCZONA KONWERSJA – TYLKO PLACEHOLDERY ⚠️

**Witchery nie ma portu na 1.18.2.**  Niniejsza implementacja jest świadomie
uproszczona: **wszystkie TileEntities Witchery są konwertowane wyłącznie na
bloki placeholder** (`conversion_placeholders:block_entity_placeholder` lub
`inventory_placeholder` gdy TE zawiera przedmioty).

Nie jest wykonywana żadna faktyczna konwersja danych (brak remapowania NBT,
brak mapowania bloków na odpowiedniki, brak translacji itemów).

---

## Podsumowanie sesji

Ukończono **Zadanie 2** konwersji moda Witchery: implementacja pełnego zestawu
plików konwertera + podpięcie do routera.

## Ukończono

- [x] `src/converters/witchery/mappings.py` – 52 TE IDs, mapowania blok, grupy
- [x] `src/converters/witchery/witchery_converter.py` – `WitcheryConverter` (placeholder-only)
- [x] `src/converters/witchery/tests/__init__.py`
- [x] `src/converters/witchery/tests/test_witchery_converter.py` – 71 testów
- [x] `src/converters/router.py` – `_witchery()` factory + `detect_mod()` + dispatch
- [x] Testy: **71 passed**, 0 failed

## Nowe / zmienione pliki

| Plik | Opis |
|------|------|
| `src/converters/witchery/mappings.py` | 52 TE IDs, `TE_ID_TO_BLOCK_REGISTRY`, `TE_ID_TO_GROUP` |
| `src/converters/witchery/witchery_converter.py` | `WitcheryConverter` – placeholder-only |
| `src/converters/witchery/tests/__init__.py` | Init pakietu testów |
| `src/converters/witchery/tests/test_witchery_converter.py` | 71 testów (mappings, router, placeholder, NBT) |
| `src/converters/router.py` | Dodano `_witchery()`, `detect_mod("witchery:*")`, dispatch |

## Architektura konwertera

### mappings.py

```
WITCHERY_TE_IDS       – frozenset 52 TE IDs (prefiks witchery:)
TE_ID_TO_BLOCK_REGISTRY – TE ID → klucz bloku źródłowego 1.7.10
TE_ID_TO_GROUP        – TE ID → grupa (conversion_stage w placeholder)
```

**5 grup** (wartość pola `conversion_stage` w NBT placeholdera):

| Stała | Wartość | Liczba TE |
|---|---|---|
| `GROUP_FUNCTIONAL` | `witchery_functional_inventory` | 12 |
| `GROUP_SPECIAL` | `witchery_special_state` | 9 |
| `GROUP_DECORATIVE` | `witchery_decorative_minimal` | 21 |
| `GROUP_REDSTONE` | `witchery_cursed_redstone` | 7 |
| `GROUP_FLUID` | `witchery_brew_fluid` | 3 |

### witchery_converter.py

```python
WitcheryConverter.convert_tile_entity(te_id, nbt_1710, metadata, position)
  → list[dict]  # zawsze 1 element: placeholder event
```

- **Zachowanie NBT:** pełne oryginalne NBT w `original_nbt`
- **Auto inventory_placeholder:** gdy TE zawiera `Items`, `contents` itp.
- **conversion_stage:** identyfikuje grupę (ułatwia filtrowanie w raportach)
- **Fallback:** nieznane `witchery:*` TE IDs obsługiwane poprawnie

### router.py – zmiany

```python
# detect_mod() – nowy warunek (przed "return unknown"):
if te_id.startswith("witchery:"):
    return "witchery"

# convert_te_to_events() – nowy dispatch:
if mod == "witchery":
    return _witchery().convert_tile_entity(te_id, te_nbt, metadata, global_pos)
```

## Bogata metadane placeholdera

Każdy placeholder event zawiera w `nbt`:

```json
{
  "source_mod": "witchery",
  "source_te_id": "witchery:altar",
  "source_block_id": "witchery:altar",
  "source_metadata": 0,
  "conversion_reason": "no_118_equivalent",
  "conversion_stage": "witchery_functional_inventory",
  "original_nbt": { /* pełne oryginalne NBT */ },
  "attached_items": [ /* jeśli TE miał inwentarz */ ]
}
```

Pole `conversion_stage` umożliwia łatwe filtrowanie w raportach konwersji:
- `witchery_functional_inventory` → maszyny z inwentarzem (do ręcznego odtworzenia)
- `witchery_special_state` → dane gracza/portalu (wymagają szczególnej uwagi)
- `witchery_decorative_minimal` → dekoracje (niska priorytet)

## Weryfikacja

```
python -m pytest src/converters/witchery/tests/test_witchery_converter.py -v
→ 71 passed in 0.34s
```

## ⚠️ Ograniczenia tej implementacji

1. **Brak faktycznej konwersji** – żaden blok Witchery nie zostanie odtworzony
   w świecie 1.18.2 jako funkcjonalny blok; wszystko staje się placeholderem
2. **Brak mapowania bloków bez TE** (~35 bloków dekoracyjnych) – te są obsługiwane
   przez pipeline Amulet na podstawie numerycznych ID bloków, nie przez ten konwerter
3. **Brak translacji itemów** – przedmioty w `original_nbt` mają stare ID
   (np. `witchery:ingredient`) nierozpoznawane przez 1.18.2
4. **Brak implementacji zamiennika** – Hexerei/Enchanted: Witchcraft nie są
   zainstalowane na serwerze 1.18.2; bez ich instalacji placeholdery są finalne

## Następne kroki (opcjonalne Zadanie 3)

Jeśli zdecydowano by o instalacji zamiennika Witchery:

1. Zainstalować Hexerei lub Enchanted: Witchcraft na `headless_server/1.18.2/`
2. Przeanalizować ich bloki i TE IDs
3. Zaimplementować właściwą konwersję dla priorytetowych bloków:
   - Altar → odpowiednik ołtarza
   - Kettle/Cauldron → odpowiednik kotła
   - SpinningWheel/WitchesOven/Distillery → maszyny procesujące
4. Zachować placeholdery dla bloków bez odpowiednika

---

**Status:** ✅ Zadanie 2 ukończone (uproszczona konwersja – tylko placeholdery)  
**Data:** 2026-05-28
