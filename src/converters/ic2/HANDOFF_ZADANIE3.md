# Handoff: IC2 Zadanie 3 — Kod konwersji (IC2Converter + router integration)

## Podsumowanie sesji
Zaimplementowano główny konwerter IC2 (`IC2Converter`) produkujący `ConversionEvent` JSON dicts
zgodne z handlerem mapy 1.18.2. Konwerter jest zintegrowany z `router.py` (detekcja + dispatch).
Dodano registry konwerterów NBT opakowujących istniejące symulacje (Zadanie 2).
Wszystkie testy przechodzą (36/36 dla IC2, 319/321 ogółem — 2 pre-existing failures w enderstorage).

### Korekta 2026-05-20: registry ids IC2

Pierwotna integracja routera rozpoznawała IC2 tylko przez `TileEntity*` class
names z `block_inventory.py`. Realna mapa używa też krótkich Forge registry ids
(`Macerator`, `Cable`, `TECrop`, `MFSU`, `Reactor Chamber`). Zaktualizowano
`block_mappings.py`, `ic2_converter.py`, `router.py` i testy, żeby obsługiwać
oba formaty oraz nie nadpisywać metadata ogólnym aliasem `Cable`.

## Ukończono
- [x] `src/converters/ic2/ic2_converter.py` — główna klasa `IC2Converter`
  - `convert_block(block_id, metadata, nbt, position)` — główny entrypoint
  - `convert_tile_entity(te_id, nbt, metadata, position)` — lookup TE → block
  - `_resolve_mapping()` — fallback chain: TE id → block inventory → block+metadata
  - `_make_event()` — produkuje `ConversionEvent` zgodny z `common/conversion_event.py`
  - Stats tracking (processed, converted, failed, warnings)
- [x] `src/converters/ic2/nbt_converters/base_converter.py` — `NBTConversionResult` + `BaseIC2NBTConverter`
- [x] `src/converters/ic2/nbt_converters/converter_registry.py` — 10 converterów:
  - `identity` — no-op
  - `standard_machine` — maszyny IC2 (Macerator, Extractor, Compressor, etc.)
  - `generic_machine` — uproszczone maszyny (Pump, Iron Furnace)
  - `generator` — generatory (Generator, Geothermal, Solar, Semifluid)
  - `energy_storage` — BatBox, MFE, MFSU, CESU, chargepady
  - `cable` — kable (indreb)
  - `lossy_cable` — Detector/Splitter → zwykły kabel + warning
  - `teleporter` — Teleporter (ftbic)
  - `reactor_component` — Reactor — legacy NBT preservation
  - `placeholder` — placeholder + zachowanie oryginalnego NBT
- [x] Integracja z `src/converters/router.py`:
  - `detect_mod()` — lazy-loaded IC2 TE id set z `block_inventory.py`
  - `_ic2()` — lazy singleton
  - `_ic2_to_events()` — serializer do Event JSON
  - Branch w `convert_te_to_events()` dla `mod == "ic2"`
- [x] Testy: `src/converters/ic2/tests/test_ic2_converter.py` (16 testów)
  - Podstawowe konwersje (macerator, generator, batbox, cable, transformer)
  - Placeholder handling
  - Unmapped block errors
  - TE-id resolution
  - Stats tracking
  - Router integration (detect_mod + convert_te_to_events)

## Nowe pliki
- `src/converters/ic2/ic2_converter.py`
- `src/converters/ic2/nbt_converters/base_converter.py`
- `src/converters/ic2/nbt_converters/converter_registry.py`
- `src/converters/ic2/tests/test_ic2_converter.py`

## Zmodyfikowane pliki
- `src/converters/router.py` — dodano detekcję IC2, lazy singleton, serializer i dispatch branch

## Architektura

```
router.py (detect_mod → "ic2")
    ↓
_ic2() → IC2Converter()
    ↓
convert_tile_entity(te_id, nbt, metadata, pos)
    ↓
_resolve_mapping()  ← block_mappings.py + block_inventory.py
    ↓
_convert_nbt()  →  converter_registry[name].convert()
    ↓
_make_event()  →  ConversionEvent  →  _ic2_to_events()  →  JSON dict
```

## Pokrycie konwersji (przypomnienie)
- **Tier-1 real blocks**: 61.9% (70/113 static mappings → indreb/ftbic)
- **Placeholdery**: 43 (38.1%)
- **Energy**: 1 EU = 4 FE (stosowane do wartości NBT)
- **Inventory**: Obsługa `InvSlots` i legacy `Items`
- **Facing**: IC2 0-5 → down/up/north/south/west/east (blockstate)

## Następne kroki (Zadanie 4)
1. Sprawdzenie pokrycia kodu dla stref głównej mapy (`strefy/`, `mapa_1710/`)
2. Weryfikacja czy konwertowane symulacje są zgodne z kodem źródłowym modów 1.18.2
   (indreb / ftbic — dekompilacja lub źródła)
3. Analiza różnic między symulacjami a faktycznym zachowaniem 1.18.2
4. Decyzja co zostawić, co poprawić

## Otwarte kwestie
- **NBT shape dla indreb/ftbic**: symulacje używają generycznych pól (`energy`, `active`, `Items`).
  Dokładny format NBT w indreb/ftbic wymaga weryfikacji ze źródeł (Zadanie 4).
- **43 placeholdery**: Miner, Tesla Coil, Crop-Matron, Pattern Storage, Scanner, Replicator,
  Fluid Regulator, Condenser, Kinetic/Heat generators, Reactor components, Personal Safe/Trade-O-Mat,
  Energy-O-Mat — do rozważenia czy da się znaleźć zamienniki.
