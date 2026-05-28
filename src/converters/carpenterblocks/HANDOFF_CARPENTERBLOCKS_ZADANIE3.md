# Handoff: CarpentersBlocks – Zadanie 3 (Mod Java + Materializer)

## Podsumowanie sesji

Wykonano Zadanie 3 dla CarpentersBlocks:
1. Stworzono szkielet moda Java `cuttableblocks` w `jvm/cuttableblocks_mod_1182/`
   z rejestracją wszystkich 18 bloków i jednym `CuttableBlockEntity`.
2. Stworzono `materializer.py` — dedykowany kod konwersji z jawną tabelą
   mapowań CB TileEntity → CuttableBlockEntity oraz generatorem SNBT
   dla komend `/setblock`.

---

## Ukończono

- [x] `jvm/cuttableblocks_mod_1182/` – szkielet moda Forge 1.18.2
- [x] `src/converters/carpenterblocks/materializer.py` – CBMaterializer + dict_to_snbt
- [x] `src/converters/carpenterblocks/tests/test_materializer.py` – 43 testy

---

## Mod Java: struktura

```
jvm/cuttableblocks_mod_1182/
├── build.gradle                                    (Forge 1.18.2-40.2.4, Java 17)
├── settings.gradle
└── src/main/
    ├── java/pl/pawel/cuttableblocks/
    │   ├── CuttableBlocksMod.java                  (MODID="cuttableblocks")
    │   ├── registry/
    │   │   ├── ModBlocks.java                      (18 bloków)
    │   │   ├── ModBlockEntities.java               (1 typ BE: "cuttable")
    │   │   └── ModItems.java                       (18 block items)
    │   └── world/
    │       ├── CuttableBlock.java                  (BaseEntityBlock, RenderShape.ENTITYBLOCK_ANIMATED)
    │       └── CuttableBlockEntity.java            (pełne NBT schema)
    └── resources/assets/cuttableblocks/
        ├── blockstates/{18 plików}.json            (wariant "" → cuttable model)
        ├── models/block/cuttable.json              (cube_all, placeholder oak_planks)
        ├── models/item/{18 plików}.json
        └── lang/en_us.json
```

---

## Kluczowe decyzje architektoniczne

### 1. Jeden BlockEntityType dla 18 bloków
`ModBlockEntities.CUTTABLE` rejestruje jeden `BlockEntityType<CuttableBlockEntity>`,
który obejmuje wszystkie 18 bloków. Semantykę renderowania wyznacza pole `beType` w NBT.

### 2. Geometria w NBT, nie w blockstate
Szkielet moda nie definiuje właściwości blockstate (facing, half, shape, slope_type…)
dla żadnego bloku. Wszystkie dane geometryczne trafiają do pola `geom` (CompoundTag)
w `CuttableBlockEntity`. Renderer będzie czytał z `geom` zamiast z blockstate.

**Zaleta**: prosty blockstate JSON (jeden wariant bez warunków) i brak konieczności
enumeracji 65+ kombinacji dla slope.

### 3. Jawna tabela _CB_BLOCK_TO_BE_TYPE (materializer.py)
Centralny element "osobnego kodu konwersji" — jawna tabela mapowań:
```python
_CB_BLOCK_TO_BE_TYPE = {
    "CarpentersBlocks:blockCarpentersSlope":            "coverable",
    "CarpentersBlocks:blockCarpentersCollapsibleBlock": "collapsible",
    "CarpentersBlocks:blockCarpentersHatch":            "hatch",
    "CarpentersBlocks:blockCarpentersDoor":             "door",
    ...18 wpisów...
}
```
Test `TestBeTypeMapping.test_all_18_blocks_have_be_type` weryfikuje jej kompletność
względem `ALL_CB_BLOCK_IDS_1710`.

### 4. CuttableBlockEntity – kontrakt NBT
Wszystkie pola są opcjonalne z sensownymi wartościami domyślnymi.
Pola specyficzne dla `beType` (np. `quadDepths` dla collapsible) są pomijane
w serializacji gdy mają wartość domyślną (zero/false/empty).

| Pole             | Typ Java     | Typ NBT     | Znaczenie                              |
|------------------|--------------|-------------|----------------------------------------|
| coverMaterial    | String       | TAG_String  | Bazowy materiał pokrycia               |
| sideCovers       | CompoundTag  | TAG_Compound| Pokrycia per-bok {"0":id,...}          |
| sideDyes         | CompoundTag  | TAG_Compound| Barwniki per-bok                       |
| cbDesign         | String       | TAG_String  | Wzór dłuta                             |
| illuminator      | boolean      | TAG_Byte    | Iluminator                             |
| beType           | String       | TAG_String  | Typ semantyczny                        |
| geom             | CompoundTag  | TAG_Compound| Geometria (facing, half, shape, ...)   |
| quadDepths       | int[4]       | TAG_Int[]   | Głębokości kwadrantów (collapsible)    |
| rigid            | boolean      | TAG_Byte    | Sztywność (hatch/door)                 |
| polarityNegative | boolean      | TAG_Byte    | Odwrócona polaryzacja (lever/button)   |
| smoldering       | boolean      | TAG_Byte    | Tlenie (torch)                         |
| plantMaterial    | String       | TAG_String  | Roślina (flower_pot)                   |
| soilMaterial     | String       | TAG_String  | Podłoże (flower_pot)                   |
| cbMetadataRaw    | int          | TAG_Int     | Surowe cbMetadata (multiblock, -1=brak)|

### 5. dict_to_snbt – generator SNBT
Konwertuje Python dict → string SNBT dołączany do komendy `/setblock`.
Obsługuje: bool→`1b`/`0b`, int→liczba, list<int>→`[I;...]`, str→`"..."`, dict→`{...}`.

---

## Nowe pliki

### Java mod (jvm/)
- `jvm/cuttableblocks_mod_1182/build.gradle`
- `jvm/cuttableblocks_mod_1182/settings.gradle`
- `jvm/cuttableblocks_mod_1182/src/main/resources/META-INF/mods.toml`
- `jvm/cuttableblocks_mod_1182/src/main/resources/pack.mcmeta`
- `jvm/cuttableblocks_mod_1182/src/main/java/pl/pawel/cuttableblocks/CuttableBlocksMod.java`
- `jvm/cuttableblocks_mod_1182/src/main/java/pl/pawel/cuttableblocks/registry/ModBlocks.java`
- `jvm/cuttableblocks_mod_1182/src/main/java/pl/pawel/cuttableblocks/registry/ModBlockEntities.java`
- `jvm/cuttableblocks_mod_1182/src/main/java/pl/pawel/cuttableblocks/registry/ModItems.java`
- `jvm/cuttableblocks_mod_1182/src/main/java/pl/pawel/cuttableblocks/world/CuttableBlock.java`
- `jvm/cuttableblocks_mod_1182/src/main/java/pl/pawel/cuttableblocks/world/CuttableBlockEntity.java`
- `jvm/cuttableblocks_mod_1182/src/main/resources/assets/cuttableblocks/models/block/cuttable.json`
- `jvm/cuttableblocks_mod_1182/src/main/resources/assets/cuttableblocks/lang/en_us.json`
- 18x `assets/cuttableblocks/blockstates/{name}.json`
- 18x `assets/cuttableblocks/models/item/{name}.json`

### Python (src/)
- `src/converters/carpenterblocks/materializer.py`
- `src/converters/carpenterblocks/tests/test_materializer.py`
- `src/converters/carpenterblocks/__init__.py` (zaktualizowany)

---

## Stan kodu

### Weryfikacja
```
python -m pytest src/converters/carpenterblocks/tests/ -v  →  150 passed
  (25 test_mappings + 82 test_nbt_converter + 43 test_materializer)
```

Mod Java nie jest jeszcze budowany (Gradle wymaga środowiska Forge) – struktura
plików jest kompletna i poprawna syntaktycznie.

---

## Następne kroki

### Zadanie 4: Testowy świat + materializacja
- [ ] `test_scenarios/carpenterblocks_task4/create_test_world.py`
      — generuje mały świat 1.7.10 z próbką wszystkich 18 typów CB
- [ ] `test_scenarios/carpenterblocks_task4/materialize_carpenterblocks_task4.py`
      — używa `CBMaterializer` do generowania datapaku z komendami setblock
- [ ] Skopiowanie bazy świata 1.18.2 do `headless_server/1.18.2/world_carpenterblocks_task4/`

### Zadanie 5: Build moda + test integracyjny headless
- [ ] Zbudować `cuttableblocks_mod_1182` gradle → `cuttableblocks-1.0.0.jar`
- [ ] Umieścić JAR w `headless_server/1.18.2/mods/`
- [ ] Uruchomić serwer headless z datapaku task4
- [ ] Potwierdzić w logach: rejestracja bloków + załadowanie CuttableBlockEntity

### Zadanie 6+: Renderowanie (poza scope'em skeleton)
- [ ] Dodać blockstate properties do bloków (np. IntegerProperty SLOPE_ID 0..64)
      i przenieść geometrię z NBT z powrotem do blockstate
- [ ] Zaimplementować ISTER (In-world Static Tile Entity Renderer) dla CuttableBlock
- [ ] Renderer czyta `geom` i `coverMaterial` z CuttableBlockEntity

---

## Otwarte pytania

1. **Budowanie moda**: Gradle wymaga Forge MDK environment. Czy budujemy teraz
   czy dopiero przed testem integracyjnym (Zadanie 5)?
2. **Geometria w blockstate vs NBT**: Czy w Zadaniu 6 przenosimy facing/half/shape
   do blockstate (dla vanilla compatibility), czy zostajemy przy NBT-only?
3. **Multiblock (Bed, GarageDoor)**: Tylko `cbMetadataRaw` preserved. Pełna konwersja
   wymaga decyzji o reprezentacji w 1.18.2 (2-blokowa struktura? placeholder?).
