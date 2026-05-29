# Carpenter's Blocks - Block-Only Analiza (Krok 1)

> **Mod:** Carpenter's Blocks 3.3.8.1 (1.7.10) → BlockCarpentry / FramedBlocks 1.18.2  
> **Data:** 2026-05-29  
> **Cel:** Identyfikacja zwykłych bloków bez TileEntity.

---

## 1. Stan faktyczny

Carpenter's Blocks to mod całkowicie oparty na TileEntity. **Każdy blok** moda przechowuje informację o cover block (teksturze bazowej), kolorze, orientacji i innych właściwościach w swoim TileEntity. Bez TE blok nie ma sensu – traciłby całą swoją funkcjonalność.

Inspekcja bytecode JAR potwierdza, że wszystkie klasy bloków dziedziczą po `BlockBase` (lub podobnej klasie bazowej moda), która implementuje `ITileEntityProvider` lub dziedziczy po `BlockContainer`.

---

## 2. Bloki bez TileEntity

**Brak.**

| # | Registry name | Klasa | Opis |
|---|--------------|-------|------|
| — | — | — | — |

---

## 3. Lista bloków z TileEntity (poza zakresem block-only)

| Registry name | Klasa | Opis |
|---------------|-------|------|
| `CarpentersBlocks:blockCarpentersBlock` | `BlockCarpentersBlock` | Podstawowy blok stolarza |
| `CarpentersBlocks:blockCarpentersSlope` | `BlockCarpentersSlope` | Slope (pochyłość) |
| `CarpentersBlocks:blockCarpentersStairs` | `BlockCarpentersStairs` | Schody |
| `CarpentersBlocks:blockCarpentersBarrier` | `BlockCarpentersBarrier` | Bariera |
| `CarpentersBlocks:blockCarpentersButton` | `BlockCarpentersButton` | Przycisk |
| `CarpentersBlocks:blockCarpentersDaylightSensor` | `BlockCarpentersDaylightSensor` | Czujnik światła |
| `CarpentersBlocks:blockCarpentersDoor` | `BlockCarpentersDoor` | Drzwi |
| `CarpentersBlocks:blockCarpentersGate` | `BlockCarpentersGate` | Furtka |
| `CarpentersBlocks:blockCarpentersHatch` | `BlockCarpentersHatch` | Właz |
| `CarpentersBlocks:blockCarpentersLadder` | `BlockCarpentersLadder` | Drabina |
| `CarpentersBlocks:blockCarpentersLever` | `BlockCarpentersLever` | Dźwignia |
| `CarpentersBlocks:blockCarpentersPressurePlate` | `BlockCarpentersPressurePlate` | Płytka naciskowa |
| `CarpentersBlocks:blockCarpentersBed` | `BlockCarpentersBed` | Łóżko |
| `CarpentersBlocks:blockCarpentersCollapsibleBlock` | `BlockCarpentersCollapsibleBlock` | Blok regulowanej wysokości |
| `CarpentersBlocks:blockCarpentersSafe` | `BlockCarpentersSafe` | Sejf |
| `CarpentersBlocks:blockCarpentersFlowerPot` | `BlockCarpentersFlowerPot` | Doniczka |

---

## 4. Decyzja

**Warstwa block-only NIE JEST POTRZEBNA** dla Carpenter's Blocks.

Konwersja tego moda wymaga:
- Odczytu cover block i kolorów z TileEntity (`nbt_converter.py` istnieje)
- Materializacji odpowiednich bloków w 1.18.2 (BlockCarpentry / FramedBlocks)
- Zachowania orientacji i właściwości (door open/close, slope type, itp.)

---

## 5. Handoff

- [ ] Brak bloków do mapowania w warstwie block-only.
- [ ] Wszystkie bloki Carpenter's Blocks wymagają pełnego konwertera TE/NBT.
