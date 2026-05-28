# Handoff: Reliquary - Zadanie 3 (Ukończone)

## Podsumowanie sesji

Ukończono **Zadanie 3** konwersji moda Reliquary: implementacja właściwego konwertera
i podłączenie do routera.

## Ukończono

- [x] `mappings.py` – słowniki ID bloków i TE (1.7.10 → 1.18.2)
- [x] `converter.py` – klasa `ReliquaryConverter` z obsługą 3 TE
- [x] Alkahestry Altar – NBT przepisany identycznie (tylko whitelist kluczy)
- [x] Apothecary Cauldron – delegacja do `CauldronConverter` z symulacji
- [x] Apothecary Mortar – delegacja do `MortarConverter` z symulacji
- [x] `router.py` – wykrywanie TE + lazy singleton + serializer + dispatch
- [x] 30 testów konwertera – wszystkie przechodzą

## Nowe pliki

| Plik | Opis |
|------|------|
| `__init__.py` | Inicjalizacja pakietu |
| `mappings.py` | `TE_ID_TO_BLOCK`, `BLOCK_ID_MAP`, `RELIQUARY_TE_IDS` |
| `converter.py` | `ReliquaryConverter.convert_tile_entity()` |
| `tests/__init__.py` | Inicjalizacja pakietu testów |
| `tests/test_converter.py` | 30 testów pytest (mappings, altar, cauldron, mortar, router) |

## Zmiany w istniejących plikach

### `src/converters/router.py`
- Dodano `_reliquary()` – lazy singleton factory
- Dodano detekcję w `detect_mod()`: `"reliquaryAltar"`, `"reliquaryCauldron"`, `"apothecaryMortar"` → `"reliquary"`
- Dodano `_reliquary_to_events()` – serializer `ConversionResult → Event JSON`
- Dodano blok dispatch `if mod == "reliquary":` w `convert_te_to_events()`

## Kluczowe decyzje implementacyjne

### Alkahestry Altar
Tylko whitelist 3 kluczy (`cycleTime`, `redstoneCount`, `isActive`) – reszta pomijana.
NBT jest strukturalnie identyczny, więc brak osobnego konwertera.

### Apothecary Cauldron
Delegacja do `CauldronConverter` z `simulations/cauldron_sim.py`.
Metadata bloku (liquidLevel) przekazywana jako parametr `metadata` – router już
ją dostarcza jako `metadata=metadata`.

### Apothecary Mortar
Delegacja do `MortarConverter` z `simulations/mortar_sim.py`.
Pełne remapping inventory: Items (top-level) → items.Items (ItemStackHandler).

## Weryfikacja

```
python -m pytest src/converters/reliquary/tests/test_converter.py -v
→ 30 passed

python -m pytest src/converters/reliquary/simulations/test_simulations.py -v
→ 27 passed (regresja czystia)
```

## Następne kroki (Zadanie 4)

Weryfikacja na rzeczywistych danych:
1. Znaleźć świat testowy z blokami Reliquary (lub stworzyć ręcznie)
2. Uruchomić pipeline konwersji na chunku zawierającym TE
3. Sprawdzić output JSON pod kątem poprawności NBT
4. Opcjonalnie: załadować skonwertowany świat w 1.18.2 i sprawdzić czy TE działa

---

**Status:** ✅ Zadanie 3 ukończone  
**Data:** 2026-05-28
