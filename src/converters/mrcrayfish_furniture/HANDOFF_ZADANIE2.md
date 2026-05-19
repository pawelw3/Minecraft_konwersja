# Handoff: MrCrayfish Furniture Mod — Zadanie 2 (Symulacje funkcjonalnosci)

## Podsumowanie sesji

Przygotowano 5 symulacji w Pythonie pokazujacych dzialanie kluczowych funkcjonalnosci MrCrayfish Furniture Mod w wersjach 1.7.10 i 1.18.2. Symulacje bazuja na dokladnym kodzie zrodlowym obu wersji i pokazuja roznice strukturalne ktore beda mialy wplyw na konwersje.

## Ukonczono

- [x] Symulacja systemow inventory (custom NBT 1.7.10 vs ContainerHelper 1.18.2)
- [x] Symulacja wielobloku Fridge+Freezer (storage-only 1.7.10 vs storage+freezing 1.18.2)
- [x] Symulacja mapowania kolorow Couch/Sofa (metadata 0-15 -> block-per-color)
- [x] Symulacja systemow plynow (boolean/level 1.7.10 -> FluidTank 1.18.2)
- [x] Symulacja mapowan blokow dekoracyjnych (wood/stone variants -> osobne bloki per material)
- [x] Wszystkie symulacje przetestowane i dzialajace

## Nowe pliki

- `src/converters/mrcrayfish_furniture/simulation_inventory_systems.py`
  - ItemStack1710 / ItemStack1182 z roznicami w NBT
  - ContainerHelper1182 (symulacja z 1.18.2)
  - TileEntityFridge1710, TileEntityCabinet1710, TileEntityMailBox1710
  - FridgeBlockEntity1182, CabinetBlockEntity1182, MailBoxBlockEntity1182
  - InventoryConverter z konwersja UUID string -> int-array
  - Konwersja: Fridge 16->27 slots, Cabinet 16->18 slots, MailBox 6->9 slots

- `src/converters/mrcrayfish_furniture/simulation_fridge_freezer.py`
  - FridgeFreezerMultiblock1710 (Fridge 16 slotow + Freezer 16 slotow storage)
  - FridgeFreezerMultiblock1182 (Fridge 27 slotow + Freezer 3 sloty crafting)
  - Konwersja z overflow handlingiem (itemy z Freezer 1.7.10 -> Fridge 1.18.2 sloty 16+)
  - Symulacja ticku zamrazania w FreezerBlockEntity1182

- `src/converters/mrcrayfish_furniture/simulation_couch_color.py`
  - TileEntityCouch1710 (int colour 0-15)
  - SofaBlock1182 (DyeColor, block per color)
  - Pelna tabela mapowania 16 kolorow
  - Curtains/Blinds wood variants (metadata -> wood type)

- `src/converters/mrcrayfish_furniture/simulation_kitchen_fluid.py`
  - TileEntityCounterSink1710 (boolean hasWater)
  - TileEntityBasin1710 (water level 0-8)
  - KitchenSinkBlockEntity1182 (FluidTank 10000 mB)
  - Konwersja boolean -> 5000 mB, level -> liniowe mapowanie na mB
  - Placeholdery dla Bath/Shower

- `src/converters/mrcrayfish_furniture/simulation_block_mappings.py`
  - BlockMappingTable z pelna tabela ~60 blokow 1.7.10
  - Klasyfikacja: remap / placeholder / remove
  - Decyzje projektowe zaimplementowane: Bin->Crate, WallCabinet->Cabinet, CounterDoored->KitchenCounter, KitchenCabinet->KitchenDrawer
  - Statystyki: 21 remap, 15 placeholder, 25 remove

## Zmodyfikowane pliki

- `src/converters/mrcrayfish_furniture/simulation_inventory_systems.py` — dodano brakujace metody set_item (poprawka po testach)

## Kluczowe wnioski dla Zadania 3 (kod konwersji)

### Eventy konwersji (format do wykorzystania w Zadaniu 3)
```python
{"action": "remap", "source_block": "tablewood", "target_block": "cfm:oak_table"}
{"action": "remap", "source_block": "bin", "target_block": "cfm:oak_crate", "extra": {"converted_from": "bin"}}
{"action": "placeholder", "source_block": "basin", "target_block": "minecraft:barrier", "placeholder_data": {...}}
{"action": "remove", "source_block": "oven", "target_block": "minecraft:air", "reason": "removed_in_1182"}
```

### Problemy do rozwiazania w kodzie konwersji
1. **Fridge/Freezer overflow**: Freezer 1.7.10 ma 16 slotow storage, 1.18.2 ma 3 sloty crafting. Itemy z Freezer musza trafic do Fridge (sloty 16-26) lub zostac zrzucone.
2. **UUID format**: MailBox OwnerUUID string -> int-array wymaga konwersji przy kazdym TE.
3. **Inventory slot tag names**: fridgeSlot / cabinetSlot / mailBoxSlot -> standardowy Slot.
4. **Container size mismatches**: Fridge 16->27, Cabinet 16->18, MailBox 6->9. Wieksze pojemnosci = itemy sie mieszcza. Mniejsze = overflow.
5. **Couch color**: metadata 0-15 -> registry name (cfm:<color>_sofa). Brak BE w 1.18.2 dla Couch.
6. **Fluid conversion**: boolean/level -> FluidTank NBT. Tylko CounterSink i Basin maja sensowne mapowanie (na KitchenSink). Reszta lazienki -> placeholdery.

## Decyzje z Zadania 1 (zatwierdzone przez uzytkownika)

1. ✅ Itemy z usunietych blokow: **STRATA** (remove -> air)
2. ✅ Bin -> Crate, WallCabinet -> Cabinet, CounterSink -> KitchenSink: **TAK**
3. ✅ Bloki lazienkowe (Basin, Bath, Shower, Toilet, Tap): **PLACEHOLDERY** (barrier)

## Nastepne kroki (Zadanie 3)

Napisanie kodu konwersji (Python) produkujacego eventy kompatybilne z ogolnym handlerem wstawiajacym dane na podkladowa mape vanilla 1.18.2.

Kod powinien uwzgledniac:
- Dynamiczne ID elementow z glownej mapy (region files .mca)
- Dynamiczne ID z map testowych
- Eventy per-blok i per-TE/BE
- Konwersje NBT inventory, UUID, fluidow, kolorow
- Wielobloki (Fridge/Freezer)
- Placeholdery i remove

---

*Data handoffu: 2026-05-19*
*Mod: MrCrayfish Furniture Mod (v3.4.8 -> 7.0.x)*
*Status: Zadanie 2 UKONCZONE, gotowe do Zadania 3*
