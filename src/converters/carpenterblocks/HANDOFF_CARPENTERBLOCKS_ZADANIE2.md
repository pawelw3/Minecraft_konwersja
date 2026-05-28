# Handoff: CarpentersBlocks – Zadanie 2 (Konwerter NBT)

## Podsumowanie sesji

Wykonano Zadanie 2 dla CarpentersBlocks: zaimplementowano pełny konwerter NBT
`CBBlockConverter` dla wszystkich 18 typów bloków CB 1.7.10 → cuttableblocks 1.18.2
wraz z kompletnym rozwiązaniem materiałów okładkowych i 82 testami jednostkowymi.

---

## Ukończono

- [x] `mappings/cover_materials.py` – ~150+ wpisów materiałów vanilla + `resolve_cover_material()`
- [x] `mappings/__init__.py` – zaktualizowany o eksport `resolve_cover_material`
- [x] `nbt_converter.py` – `CBBlockConverter`, `CBConversionResult`, `parse_te_base`
- [x] `__init__.py` – zaktualizowany o eksport nowych klas
- [x] `tests/test_nbt_converter.py` – 82 testy, wszystkie zielone

---

## Kluczowe decyzje architektoniczne

### 1. Struktura CBConversionResult
Dataclass z polami: `success`, `block_id_1710`, `block_id_1182`, `blockstate_props`
(dict), `nbt_1182` (dict), `errors` (lista CB-E-*), `warnings` (lista CB-W-*).
Metody `add_error(code, msg)` i `add_warning(code, msg)` ustawiają `success=False` przy błędach.

### 2. ParsedTEBase / parse_te_base()
Parsuje `cbAttrList` (lista compound) do `dict[int, ParsedAttr]` indeksowanego po `cbAttribute`.
`ParsedAttr` zawiera: `attr_id`, `cb_unique_id`, `damage`, `resolved_id` (wynik `resolve_cover_material`).
Właściwości: `base_cover` → `ParsedAttr` dla `cbAttribute=6`, `has_illuminator` → bool.

### 3. resolve_cover_material – 4-poziomowy fallback
1. Dokładne `(cb_unique_id, damage)` w `COVER_MATERIAL_MAP`
2. `(cb_unique_id, 0)` jeśli damage≠0
3. `_NO_DAMAGE_MAP` (bloki bez metadata)
4. Heurystyka: jeśli prefix `minecraft:` → zwróć as-is
5. `None` dla materiałów z nieznanych modów → `CB-W-UNKNOWN_MAT`

### 4. _build_base_nbt – wspólna część NBT
Każda konwersja zaczyna od `_build_base_nbt(te, result)` który wstawia:
- `coverMaterial` – z `base_cover.resolved_id` (lub warning `CB-W-NO_COVER`)
- `sideCovers` – dict `{str(i): id}` dla attr 0..5 gdy różnią się od base
- `sideDyes` – dict `{str(i): id}` dla attr 7..13
- `cbDesign` – jeśli niepuste
- `illuminator` – jeśli `has_illuminator`

### 5. Mapowania geometrii na blockstate_props
Każdy typ bloku ma dedykowany `_convert_*` który ustawia `blockstate_props`:
- Slope: `slope_type`, `facing`, `half`, `shape` (ze SLOPE_ID_TO_PROPS)
- Stairs: `facing`, `half`, `shape` (ze STAIRS_ID_TO_PROPS)
- Block/Slab: `type`, `axis` (ze SLAB_ID_TO_PROPS)
- Collapsible: `facing` (ForgeDir 0-5) + `quadDepths` w NBT (lista 4 int 0-16)
- Barrier: `fence_type`, `has_post`
- Gate: `gate_type`, `open_dir`, `facing`, `open`
- Hatch: `hatch_type`, `position`, `open`, `facing`, `rigid` w NBT
- Door: `door_type`, `hinge`, `facing`, `open`, `half`, `rigid` w NBT
- Ladder: `facing`, `ladder_type`
- Lever: `facing`, `powered`, `polarity` w NBT
- Button: `facing`, `powered`
- Pressure plate: `facing`, `powered`
- Torch: `facing`, `lit`, `torch_type`, `smoldering` w NBT
- Daylight sensor: `light_level`, `inverted`, `sensitivity`, `facing`
- Multiblock (Bed/GarageDoor): `CB-W-MULTIBLOCK` + `cbMetadataRaw` w NBT
- Safe: brak props (samo coverMaterial)
- FlowerPot: `plant_id`, `soil_id` ze ATTR_PLANT(22) i ATTR_SOIL(23)

### 6. Kody błędów / ostrzeżeń
| Kod | Znaczenie |
|-----|-----------|
| `CB-E-UNKNOWN_BLOCK` | block_id_1710 nie ma w CB_BLOCK_TO_CB1182 |
| `CB-E-GEOM_OOB` | cbMetadata poza zakresem dla danego typu |
| `CB-W-UNKNOWN_MAT` | resolve_cover_material zwróciło None |
| `CB-W-NO_COVER` | TEBase nie ma ATTR_COVER[6] (base) |
| `CB-W-MULTIBLOCK` | blok jest częścią multi-block (Bed/GarageDoor) |

---

## Nowe pliki

```
src/converters/carpenterblocks/
├── __init__.py                             (zaktualizowany)
├── nbt_converter.py                        (NOWY)
├── mappings/
│   ├── __init__.py                         (zaktualizowany)
│   └── cover_materials.py                  (NOWY)
└── tests/
    └── test_nbt_converter.py               (NOWY)
```

---

## Stan kodu

### Weryfikacja
```
python -m pytest src/converters/carpenterblocks/tests -v  →  107 passed (25 + 82)
```

---

## Następne kroki

### Zadanie 3: Mod Java `cuttableblocks` 1.18.2
- [ ] Szkielet moda w `jvm/cuttableblocks_mod_1182/`
- [ ] Rejestracja bloków: `slope`, `stairs`, `block`, `collapsible_block`, `barrier`,
      `gate`, `hatch`, `door`, `ladder`, `lever`, `button`, `pressure_plate`, `torch`,
      `daylight_sensor`, `safe`, `flower_pot`, `bed`, `garage_door`
- [ ] Blockstate JSON dla slope (65 wariantów), stairs (28+4 side)
- [ ] TileEntity 1.18.2 z polem `coverMaterial` (ResourceLocation) i polami geometrii

### Zadanie 4: Testowy świat + materializacja
- [ ] `create_carpenterblocks_test_map.py` – mały świat z próbką wszystkich 18 typów
- [ ] Skrypt materializujący do 1.18.2 (datapack setblock + NBT)

### Zadanie 5: Test integracyjny headless
- [ ] Uruchomić headless 1.18.2 z `cuttableblocks.jar`
- [ ] Potwierdzić placement bloków i załadowanie TE w logach

---

## Otwarte pytania

1. **GarageDoor, Bed**: Oznaczone CB-W-MULTIBLOCK, `cbMetadataRaw` zachowane.
   Czy cuttableblocks będzie je obsługiwał? Jeśli tak – usunąć warning i dodać
   pełną konwersję w kolejnej sesji.
2. **cbDesign** (chisel patterns): Przechowywane w NBT jako `cbDesign` string.
   Jeśli cuttableblocks nie obsługuje wzorów – można zignorować na etapie materializacji.
3. **Cover materials z innych modów**: resolve_cover_material zwraca None →
   CB-W-UNKNOWN_MAT. Fallback materialny (np. `minecraft:oak_planks`) można
   dodać jako opcję `CBBlockConverter(unknown_mat_fallback="minecraft:oak_planks")`.
