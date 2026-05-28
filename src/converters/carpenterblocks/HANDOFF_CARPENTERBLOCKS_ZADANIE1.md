# Handoff: CarpentersBlocks – Zadanie 1 (Analiza i mapowania)

## Podsumowanie sesji

Wykonano Zadanie 1 dla CarpentersBlocks: przeanalizowano źródła moda 1.7.10,
udokumentowano wszystkie 18 bloków, zbudowano kompletne tablice mapowań geometrii
(65 slope, 28 stairs, 7 slab) oraz napisano skrypt analizy świata 1.7.10.

---

## Ukończono

- [x] Struktura modułu `src/converters/carpenterblocks/` z `__init__.py`
- [x] `mappings/block_ids.py` – 18 bloków CB 1.7.10 → cuttableblocks 1.18.2
- [x] `mappings/geometry.py` – SLOPE_ID_TO_PROPS (65), STAIRS_ID_TO_PROPS (28), SLAB_ID_TO_PROPS (7)
- [x] `analyze_carpenterblocks.py` – skrypt analizy świata 1.7.10 (parser .mca bez zewnętrznych dep.)
- [x] `tests/test_mappings.py` – 25 testów, wszystkie zielone

---

## Kluczowe decyzje architektoniczne

### 1. Target: własny mod `cuttableblocks` 1.18.2
Konwersja 1:1 do własnego moda zamiast FramedBlocks/innego zewnętrznego.
Przestrzeń nazw: `cuttableblocks:`.  
Mod nie istnieje jeszcze w `jvm/` – jego bloki Java będą tworzone w kolejnych
zadaniach (Zadanie 2+) równolegle z implementacją konwertera.

### 2. Geometria slope (65 wariantów) – SlopeProps
`cbMetadata` w TEBase.java = `slopeID` z Slope.java.  
Zmapowane na 4 pola blockstate: `slope_type`, `facing`, `half`, `shape`.  
`half=bottom` gdy `isPositive=false` (DOWN in facings), `half=top` gdy UP.

### 3. Geometria stairs (28 wariantów) – StairsProps
`cbMetadata` = `stairsID` z Stairs.java.  
Odpowiada vanilla stairs facing/half/shape z rozszerzeniem o `shape=side_XX`
dla NORMAL_SIDE (ukośne w poziomie bez odpowiednika w vanilla).

### 4. Slab (cbMetadata 0..6 w blockCarpentersBlock) – SlabProps
`cbMetadata=0` = pełny blok (`type=double`).  
cbMetadata 1..6 = połówki wg DIR_MAP z Slab.java (X/Y/Z, bottom/top).

### 5. Cover materials (cbAttrList)
Każdy blok CB ma listę atrybutów indeksowaną byte-ID:
- `ATTR_COVER[0..6]` – 7 stron + base (6=base = główny materiał bloku)
- `ATTR_DYE[7..13]` – barwniki per strona
- `ATTR_OVERLAY[14..20]` – nakładki per strona
- `ATTR_ILLUMINATOR=21`, `ATTR_PLANT=22`, `ATTR_SOIL=23`, `ATTR_FERTILIZER=24`, `ATTR_UPGRADE=25`

Atrybut cover[6] (base) = material bloku wewnętrznego (kluczowy dla konwersji textury).

---

## Nowe pliki

```
src/converters/carpenterblocks/
├── __init__.py
├── analyze_carpenterblocks.py          # skrypt analizy świata 1.7.10
├── HANDOFF_CARPENTERBLOCKS_ZADANIE1.md
├── mappings/
│   ├── __init__.py
│   ├── block_ids.py                    # 18 bloków + kategorie + ATTR_*
│   └── geometry.py                     # Slope/Stairs/Slab props
└── tests/
    ├── __init__.py
    └── test_mappings.py                # 25 testów
```

---

## Stan kodu

### Weryfikacja
```
python -m pytest src/converters/carpenterblocks/tests -v  →  25 passed
```

### Komendy analizy (gdy dostępny świat 1.7.10)
```
python -m src.converters.carpenterblocks.analyze_carpenterblocks \
    --world <ścieżka_świata_1.7.10> \
    --out analysis/carpenterblocks_analysis.json
```

---

## Następne kroki

### Zadanie 2: Konwerter NBT
- [ ] `nbt_converter.py` – główna klasa `CBBlockConverter`
  - Parsowanie `cbAttrList` → cover material ID 1.18.2
  - Dekodowanie `cbMetadata` → SlopeProps/StairsProps/SlabProps
  - Przekształcenie `cbUniqueId` (1.7.10 Forge mod:item) → 1.18.2 resource location
  - Obsługa `cbDesign` (chisel patterns)
- [ ] Testy jednostkowe konwertera NBT

### Zadanie 3: Mod Java `cuttableblocks` 1.18.2
- [ ] Szkielet moda w `jvm/cuttableblocks_mod_1182/`
- [ ] Rejestracja bloków: `slope`, `stairs`, `block` (slab), `collapsible_block`, ...
- [ ] Blockstate JSON dla slope (65 wariantów) + stairs (28 + 4 side)
- [ ] TEBase 1.18.2 z polem `coverMaterial` (ResourceLocation)

### Zadanie 4: Testowy świat + materializacja
- [ ] Skrypt `create_carpenterblocks_test_map.py` – mały świat z próbką wszystkich typów
- [ ] Skrypt materializujący do 1.18.2 z datapack setblock

### Zadanie 5: Test integracyjny headless
- [ ] Uruchomić headless 1.18.2 z cuttableblocks.jar
- [ ] Potwierdzić placement bloków w logach

---

## Otwarte pytania

1. **Collapsible block**: cbMetadata = bitmaska ścian (6 bitów). Jak renderuje
   `cuttableblocks:collapsible_block`? Czy obsługuje tę samą bitmaskę?
2. **GarageDoor, Bed**: Mają specjalną logikę multi-block. Czy cuttableblocks je
   implementuje, czy mapujemy na placeholder?
3. **cbDesign** (chisel patterns): Czy cuttableblocks ma system wzorów?
   Jeśli nie – cbDesign ignorujemy przy konwersji (zachowujemy w NBT jako metadane).
4. **Cover materials z innych modów**: `cbUniqueId` może wskazywać na blok z moda
   który nie istnieje w 1.18.2 (np. GregTech). Potrzebny fallback.
