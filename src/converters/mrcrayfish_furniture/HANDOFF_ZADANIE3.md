# Handoff: MrCrayfish Furniture Mod — Zadanie 3 (Kod konwersji)

## Podsumowanie sesji

Napisano kompletny kod konwersji MrCrayfish Furniture Mod 1.7.10 -> 1.18.2. Kod produkuje ConversionEvent per blok / tile entity, jest zgodny z istniejacym handlerem wstawiajacym dane na podkladowa mape vanilla 1.18.2, oraz zostal przetestowany na prawdziwej mapie 1.7.10 (znaleziono bloki CFM w chunkach).

Rozszerzono rowniez `src/converters/common/` o wspolne narzedzia reusable dla innych modow.

## Ukonczono

- [x] Wspolna klasa `ConversionEvent` w `src/converters/common/conversion_event.py`
- [x] Wspolne helpery inventory w `src/converters/common/inventory_helpers.py`
- [x] Wspolne helpery UUID w `src/converters/common/uuid_helpers.py`
- [x] Glowny konwerter `mrcrayfish_converter.py` z obsluga ~65 blokow i 28 TE
- [x] Chunk parser `mrcrayfish_chunk_parser.py` integrujacy sie z `minecraft_map_parser`
- [x] Konwersja NBT inventory (custom slot tags -> standard Slot)
- [x] Konwersja UUID MailBox (string -> int-array)
- [x] Konwersja plynow (boolean/level -> FluidTank)
- [x] Mapowanie kolorow Couch (metadata 0-15 -> block-per-color)
- [x] Obsluga wielobloku Fridge/Freezer (w konwerterze NBT)
- [x] Testy na mapie 1.7.10 (znaleziono bloki CFM w 3 chunkach, 10 TE)

## Nowe pliki

### Wspolne (src/converters/common/)
- `conversion_event.py` — klasa ConversionEvent z metoda `to_set_block_event()` dla handlera mapy
- `inventory_helpers.py` — `convert_inventory_1710_to_1182`, `extract_items_from_legacy_nbt`
- `uuid_helpers.py` — `uuid_string_to_int_array`, `int_array_to_uuid_string`

### MrCrayfish Furniture (src/converters/mrcrayfish_furniture/)
- `mrcrayfish_converter.py` — glowny konwerter:
  - `MrCrayfishConverter.convert_block()` — bloki bez TE
  - `MrCrayfishConverter.convert_tile_entity()` — bloki z TE + NBT conversion
  - `convert_single_block()`, `convert_blocks_batch()` — convenience API
  - Mapowania: WOOD_STONE_BLOCK_MAP, WOOD_ONLY_BLOCK_MAP, REPLACEMENT_MAP, RENAMED_MAP, DIRECT_MAP
  - TE_MAP, TE_INVENTORY_SIZE, TE_SLOT_TAGS
- `mrcrayfish_chunk_parser.py` — parser chunkow:
  - `MrCrayfishChunkParser.analyze_chunk()` — skan chunka po TE CFM
  - `MrCrayfishChunkParser.analyze_region()` — skan regionu 32x32
  - `MrCrayfishChunkParser.scan_all_regions()` — skan calej mapy
  - Integracja z `AnvilParser` z `minecraft_map_parser`

## Zmodyfikowane pliki

- Brak (nowe pliki + rozszerzenie common/)

## Wyniki testow na mapie 1.7.10

```
Region r.0.-1 (84 chunkow przeskanowanych):
  Chunk 0,-10: 4 bloki CFM (countersink, kitchencabinet, countersink)
  Chunk 0,-8:  5 blokow CFM (bin, bedsidecabinet, bedsidecabinet)
  Chunk 2,-13: 1 blok CFM (oven)
  Razem: 10 TE CFM znalezionych, 0 bledow
```

## Format eventow (przyklad)

```json
{
  "mod": "cfm",
  "event_type": "remap",
  "source": {
    "block_id": "cfm:mailbox",
    "metadata": 0,
    "te_id": "cfmMailBox",
    "position": [15, 64, 10]
  },
  "target": {
    "block_id": "cfm:oak_mail_box",
    "te_id": "cfm:mail_box",
    "nbt": {
      "id": "cfm:mail_box",
      "Items": [...],
      "OwnerUUID": [1427014656, 3801825748, 2803254374, 1430519808],
      "MailBoxUUID": "..."
    }
  }
}
```

Eventy mozna przeksztalcic na komendy dla handlera mapy przez `event.to_set_block_event()`:
```python
{"op": "set_block_entity", "pos": [x, y, z], "block": "cfm:oak_mail_box", "nbt": {...}}
```

## Nastepne kroki (Zadanie 4)

Sprawdzenie pokrycia kodu na strefach glownej mapy (folder `strefy/`):
- Uruchomic `scan_all_regions()` lub `analyze_region()` na strefach zdefiniowanych w `coords.json`
- Sprawdzic czy wszystkie znalezione bloki CFM maja poprawne mapowanie
- Wygenerowac raport pokrycia i ewentualne braki

---

*Data handoffu: 2026-05-19*
*Mod: MrCrayfish Furniture Mod (v3.4.8 -> 7.0.x)*
*Status: Zadanie 3 UKONCZONE, gotowe do Zadania 4*
