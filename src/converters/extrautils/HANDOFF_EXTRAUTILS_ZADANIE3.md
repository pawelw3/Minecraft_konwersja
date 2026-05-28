# Handoff: Extra Utilities - Zadanie 3

## Podsumowanie sesji

Rozszerzono konwerter Extra Utilities o mapowania i konwersję NBT dla pozostałych kluczowych bloków moda. Przeanalizowano pokrycie na mapie (`mapa_1710/region/`) — odkryto że poza generatorami (3x) i AntiMobTorch (267x), na mapie występują także **244x Filing Cabinet** oraz **20x Trash Can**. Wszystkie Filing Cabinets na mapie są puste (`item_no` nie występuje w NBT). Zaimplementowano dedykowany NBT converter dla Filing Cabinet z obsługą inventory. Naprawiono konflikt detekcji modu w routerze (`TileEntityFilingCabinet` było przechwytywane przez Bibliocraft).

## Ukończono

- [x] Skan mapy pod kątem wszystkich TE ExU (próbka 100 regionów)
- [x] Identyfikacja numerycznych block ID: generator=2000(meta2), magnumTorch=1998(meta0), filingCabinet=2216(meta4), trashCan=1988(meta0)
- [x] Rozszerzenie mapowań o: Filing Cabinet, Drum, Ender Quarry, Ender-Thermic Pump
- [x] Implementacja `filing_cabinet_converter.py` — konwersja niestandardowego NBT ExU (`item_no` + `item_*`) na `Items` 1.18.2
- [x] Naprawa `detect_mod()` w routerze — Extra Utilities sprawdzane PRZED Bibliocraft
- [x] Aktualizacja symulacji o obsługę filing_cabinet i placeholderów
- [x] 39 testów jednostkowych (wszystkie przechodzą)
- [x] Weryfikacja E2E przez router

---

## Pokrycie na mapie (stan faktyczny)

| TileEntity | Liczba na mapie | Block ID (num.) | Meta | Status konwersji |
|---|---|---|---|---|
| `TileEntityAntiMobTorch` | 267 | 1998 | 0 | ✅ `torchmaster:mega_torch` |
| `TileEntityFilingCabinet` | 244 | 2216 | 4 | ✅ placeholder + inventory (puste na mapie) |
| `TileEntityTrashCan` | 20 | 1988 | 0 | ✅ `trashcans:item_trash_can` |
| `extrautils:generatorlava` | 3 | 2000 | 2 | ✅ `thermal:dynamo_magmatic` |

**Wszystkie Filing Cabinets w próbce 100 regionów są puste** — NBT nie zawiera `item_no`. Inventory converter jest gotowy na wypadek gdyby itemy występowały w innych regionach.

---

## Nowe mapowania (Zadanie 3)

| Blok ExU 1.7.10 | Target 1.18.2 | NBT Converter | Uwagi |
|---|---|---|---|
| `extrautils:filing` (meta 0-5) | `conversion_placeholders:inventory_placeholder` | `filing_cabinet` | Brak odpowiednika; zachowuje inventory |
| `extrautils:filing` (meta 6-11) | `conversion_placeholders:inventory_placeholder` | `filing_cabinet` | Diamond variant |
| `extrautils:drum` | `conversion_placeholders:block_entity_placeholder` | — | Fluid storage — brak portu |
| `extrautils:enderQuarry` | `conversion_placeholders:block_entity_placeholder` | — | Użyj RFTools Builder + Quarry Card ręcznie |
| `extrautils:enderThermicPump` | `mekanism:electric_pump` | `ender_thermic_pump` | Pompa do lawy/wody |

---

## Konwersja NBT Filing Cabinet

ExU 1.7.10 używa niestandardowego formatu:
```json
{
  "item_no": 3,
  "item_0": {"id": "minecraft:stone", "Count": 1, "Damage": 0, "Size": 64},
  "item_1": {"id": "minecraft:dirt", "Count": 1, "Damage": 0, "Size": 32}
}
```

Konwerter przekształca to na standardowy `Items` list 1.18.2:
```json
[
  {"Slot": 0, "id": "minecraft:stone", "Count": 64},
  {"Slot": 1, "id": "minecraft:dirt", "Count": 32}
]
```

Limit placeholdera to 54 slotów — większe inventory generuje ostrzeżenie `EXU-W-FILING-CABINET-OVERFLOW`, a nadmiarowe itemy są zachowane w `original_nbt`.

---

## Nowe pliki

- `src/converters/extrautils/nbt_converters/filing_cabinet_converter.py`

## Zmodyfikowane pliki

- `src/converters/extrautils/mappings/block_mappings.py`
  - Dodano mapowania: filing (0-11), drum, enderQuarry, enderThermicPump
  - Dodano TE_ID_TO_BLOCK: TileEntityFilingCabinet, extrautils:drum, extrautils:enderquarry, extrautils:enderpump

- `src/converters/extrautils/simulations/extrautils_simulation.py`
  - Dodano obsługę `filing_cabinet` i `conversion_placeholders`

- `src/converters/router.py`
  - Przeniesiono detekcję Extra Utilities PRZED Bibliocraft (linia ~281)
  - Dodano `TileEntityFilingCabinet` do detekcji ExU
  - Usunięto duplikat detekcji ExU z linii ~353

- `src/converters/extrautils/tests/test_extrautils_converter.py`
  - Dodano 12 nowych testów (łącznie 39)

---

## Testy

**39/39 testów przechodzi** (extrautils) + **42/42 testów** (pozostałe w `tests/`).

Weryfikacja E2E Filing Cabinet przez router:
```json
[{
  "op": "set_block_entity",
  "pos": [-186, 76, -188],
  "block": "conversion_placeholders:inventory_placeholder",
  "nbt": {
    "id": "conversion_placeholders:inventory_placeholder",
    "source_mod": "extrautils",
    "source_block_id": "extrautils:filing",
    "conversion_reason": "filing_cabinet_no_1182_equivalent",
    "original_nbt": {"id": "TileEntityFilingCabinet", "x": -186, "y": 76, "z": -188}
  },
  "warnings": ["EXU-W-MAPPING: Filing Cabinet → inventory placeholder..."]
}]
```

---

## Następne kroki

1. [ ] Zadanie 4 — Pełne sprawdzenie pokrycia na mapie głównej
   - Przeskanować WSZYSTKIE regiony (1195 plików .mca) pod kątem block ID 1998, 2000, 1988, 2216
   - Zweryfikować czy nie ma innych bloków ExU (np. cursedEarth, angelBlock, conveyor)
   - Wygenerować raport pokrycia

2. [ ] Zadanie 5 — Testowa mapa i konwersja E2E
   - Stworzyć świat testowy 1.7.10 z generatorami, magnum torch, filing cabinet, trash can
   - Przekonwertować i zweryfikować w grze

3. [ ] Zadanie 6 — Test headless serwer
   - 3 minuty ticków + restart z przekonwertowaną mapą testową

---

*Data utworzenia: 2026-05-27*
*Zadanie 3 zakończone*
