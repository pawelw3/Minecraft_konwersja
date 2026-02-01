# Handoff: AE2 Iteracja 2 - Urealnienie Patternów

## Podsumowanie

Przeanalizowano kody źródłowe AE2 1.7.10 i 1.18.2 dla patternów oraz zaimplementowano poprawny konwerter.

## Analiza kodu źródłowego

### AE2 1.7.10

**Kluczowe klasy:**
- `appeng.items.misc.ItemEncodedPattern` - item encoded pattern
- `appeng.helpers.PatternHelper` - parsowanie i walidacja patternu

**Format NBT:**
```java
NBTTagCompound encodedValue = is.getTagCompound();
NBTTagList inTag = encodedValue.getTagList("in", 10);  // 9 slotow input
NBTTagList outTag = encodedValue.getTagList("out", 10); // output
boolean isCrafting = encodedValue.getBoolean("crafting");
boolean canSubstitute = encodedValue.getBoolean("substitute");
```

**Struktura:**
- Jeden item (`ItemEncodedPattern`) dla wszystkich typów
- Rozróżnienie crafting/processing przez flagę `crafting`
- Inputy: 9 slotów (3x3 crafting grid)
- Outputy: lista (dla processing może być wiele, dla crafting wyznaczane przez recepturę)

### AE2 1.18.2

**Kluczowe klasy:**
- `appeng.crafting.pattern.EncodedPatternItem` - item encoded pattern
- `appeng.crafting.pattern.EncodedCraftingPattern` - record danych crafting
- `appeng.crafting.pattern.EncodedProcessingPattern` - record danych processing
- `appeng.api.ids.AEComponents` - definicje komponentów danych

**Data Components (zamiast bezpośredniego NBT):**
```java
// Dla crafting
DataComponentType<EncodedCraftingPattern> ENCODED_CRAFTING_PATTERN

// Dla processing  
DataComponentType<EncodedProcessingPattern> ENCODED_PROCESSING_PATTERN
```

**Struktura EncodedCraftingPattern:**
```java
public record EncodedCraftingPattern(
    List<ItemStack> inputs,      // 9 slotów
    ItemStack result,            // Wynik
    ResourceLocation recipeId,   // ID receptury (WYMAGANE!)
    boolean canSubstitute,
    boolean canSubstituteFluids
)
```

**Struktura EncodedProcessingPattern:**
```java
public record EncodedProcessingPattern(
    List<GenericStack> inputs,   // GenericStack = item lub fluid
    List<GenericStack> outputs,
    boolean canSubstitute
)
```

**Osobne itemy dla różnych typów:**
- `ae2:crafting_pattern` - crafting table recipes
- `ae2:processing_pattern` - processing (maszyny)
- `ae2:stonecutting_pattern` - stonecutter
- `ae2:smithing_table_pattern` - smithing table

## KLUCZOWY PROBLEM KONWERSYJNY

### Crafting Patterns - Recipe ID

W 1.18.2 `EncodedCraftingPattern` wymaga `recipeId` (ResourceLocation), czyli ID receptury.

W 1.7.10 pattern **nie przechowuje** ID receptury - przechowuje tylko:
- Inputy (9 slotów)
- Flagę `crafting` 
- Wynik jest **wyznaczany dynamicznie** przez znalezienie pasującej receptury

**Oznacza to, że konwersja crafting patterns bez dostępu do RecipeManager świata docelowego jest NIEMOŻLIWA w pełni automatycznie!**

### Rozwiązanie

1. **Processing patterns** - konwertowane bezpośrednio (input/output)
2. **Crafting patterns** - wymagają `recipe_resolver`:
   - Funkcja przyjmująca output i zwracająca ID receptury
   - Jeśli nie znaleziono - ostrzeżenie i placeholder `minecraft:unknown`
   - Wymaga ręcznej korekty po konwersji lub zaawansowanej heurystyki

## Implementacja

### PatternConverter

Nowy plik: `src/converters/ae2/nbt_converters/pattern_converter.py`

**Klasy:**
- `PatternData` - wewnętrzna reprezentacja patternu
- `PatternConverter` - konwersja między formatami

**Metody:**
- `convert_pattern(nbt_1710)` - parsuje NBT 1.7.10 do PatternData
- `convert_to_1182(pattern_data, recipe_resolver)` - konwertuje do formatu 1.18.2

**Przykład użycia:**
```python
converter = PatternConverter()

# Parsowanie
pattern_data = converter.convert_pattern({
    'crafting': False,
    'in': [{'id': 'minecraft:iron', 'Count': 1}],
    'out': [{'id': 'minecraft:steel', 'Count': 1}]
})

# Konwersja
def find_recipe(output):
    # Heurystyka lub lookup w RecipeManager
    return "minecraft:some_recipe"

item_id, component = converter.convert_to_1182(pattern_data, find_recipe)
# item_id = "ae2:processing_pattern"
# component = {'inputs': [...], 'outputs': [...]}
```

### Aktualizacja InterfaceConverter

Zaktualizowano `interface_converter.py` aby używał `PatternConverter`:
- Usunięto własną logikę konwersji patternów
- Dodano delegację do `PatternConverter`

## Testy

Dodano nowe testy w `TestPatternConverter`:
- `test_processing_pattern_parsing` - parsowanie NBT 1.7.10
- `test_crafting_pattern_parsing` - parsowanie NBT 1.7.10
- `test_processing_pattern_conversion` - konwersja do 1.18.2
- `test_crafting_pattern_without_recipe_resolver` - test ostrzeżenia

Wszystkie testy przechodzą: **4/4 OK**

## Pliki zmienione

| Plik | Zmiany |
|------|--------|
| `pattern_converter.py` | NOWY - główna logika konwersji patternów |
| `interface_converter.py` | Użycie PatternConverter |
| `__init__.py` | Eksport PatternConverter i PatternData |
| `test_ae2_converter.py` | 4 nowe testy dla patternów |
| `HANDOFF_ITERACJA_2.md` | Ten plik |

## Ograniczenia i TODO

1. **Crafting patterns wymagają recipe resolver** - bez tego output ma `minecraft:unknown`
2. **Fluidy w processing patterns** - obecnie uproszczone, wymagają GenericStack
3. **Stonecutting/Smithing patterns** - nieobsługiwane (nie było w 1.7.10 AE2)
4. **Substytucje** - w 1.18.2 są dwie flagi (canSubstitute, canSubstituteFluids), w 1.7.10 jedna

## Rekomendacje dla Zadania 4 (Testy na mapie)

1. Dla **processing patterns** - konwersja powinna działać automatycznie
2. Dla **crafting patterns**:
   - Zaimplementować recipe resolver lookup
   - Lub oznaczyć do ręcznej korekty
   - Stworzyć raport "crafting patterns requiring manual review"

---

*Iteracja 2 zakończona: 2026-02-01*
*Status: Patterny urealnione zgodnie z kodem źródłowym AE2*
