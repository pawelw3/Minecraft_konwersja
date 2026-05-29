# Better Storage - Block-Only Analiza (Krok 1)

> **Mod:** Better Storage 1.7.10 → Iron Chests / Sophisticated Storage / Storage Drawers 1.18.2  
> **Data:** 2026-05-29  
> **Cel:** Identyfikacja zwykłych bloków bez TileEntity.

---

## 1. Stan faktyczny

Better Storage w 1.7.10 dodaje wyłącznie bloki z TileEntity. Każdy blok przechowuje inventory, kolory, zamki lub inne dane w NBT. Inspekcja bytecode JAR potwierdza, że wszystkie klasy `Block*` dziedziczą po `BlockContainer` (direct lub pośrednio).

---

## 2. Bloki bez TileEntity

**Brak.**

| # | Registry name | Klasa | TE? | Uwagi |
|---|--------------|-------|-----|-------|
| — | — | — | — | — |

---

## 3. Lista bloków z TileEntity (poza zakresem block-only)

| Registry name | Klasa TE | Opis |
|---------------|----------|------|
| `betterstorage:crate` | `TileEntityCrate` | Crate Pile (inventory w osobnych plikach) |
| `betterstorage:reinforcedChest` | `TileEntityReinforcedChest` | Wzmocniona skrzynia |
| `betterstorage:locker` | `TileEntityLocker` | Szafka |
| `betterstorage:reinforcedLocker` | `TileEntityReinforcedLocker` | Wzmocniona szafka |
| `betterstorage:cardboardBox` | `TileEntityCardboardBox` | Karton (z zużyciem) |
| `betterstorage:craftingStation` | `TileEntityCraftingStation` | Stacja craftingowa |
| `betterstorage:armorStand` | `TileEntityArmorStand` | Stojak na zbroję |
| `betterstorage:backpack` | `TileEntityBackpack` | Plecak (blok) |
| `betterstorage:enderBackpack` | `TileEntityEnderBackpack` | Ender Backpack |
| `betterstorage:present` | `TileEntityPresent` | Prezent |
| `betterstorage:lockableDoor` | `TileEntityLockableDoor` | Drzwi z zamkiem |
| `betterstorage:flintBlock` | `TileEntityFlintBlock` | Blok krzemienia (dekoracyjny, ale ma TE) |

**Uwaga:** `betterstorage:flintBlock` to blok dekoracyjny, ale formalnie posiada `TileEntityFlintBlock`. W praktyce TE jest puste lub minimalne, ale ze względu na spójność lepiej traktować go w workflow TE.

---

## 4. Decyzja

**Warstwa block-only NIE JEST POTRZEBNA** dla Better Storage.

Wszystkie bloki wymagają pełnej konwersji TileEntity (inventory, zamki, kolory, crateId → osobne pliki).

---

## 5. Handoff

- [ ] Brak bloków do mapowania w warstwie block-only.
- [ ] Wszystkie bloki BS wymagają konwertera TE/NBT.
