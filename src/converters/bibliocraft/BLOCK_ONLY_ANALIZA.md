# BiblioCraft - Block-Only Analiza (Krok 1)

> **Mod:** BiblioCraft 1.7.10 → Supplementaries / FramedBlocks / ImmersivePaintings / Vanilla 1.18.2  
> **Data:** 2026-05-29  
> **Cel:** Identyfikacja zwykłych bloków bez TileEntity.

---

## 1. Stan faktyczny

BiblioCraft w 1.7.10 dodaje 39 bloków. Większość (ok. 36) ma TileEntity (inventory, tekstury, obrazy, zegary). Inspekcja bytecode JAR wykazała, że tylko **3 bloki** dziedziczą bezpośrednio po `net.minecraft.block.Block` (bez TE):

- `BlockBell`
- `BlockSeat`
- `BlockMapFrame`

Pozostałe bloki dziedziczą po `BlockContainer` (direct lub pośrednio).

---

## 2. Bloki bez TileEntity w 1.7.10

| # | Klasa Java | Registry name | Metadata | Opis | Target 1.18.2 | Pewność |
|---|-----------|---------------|----------|------|---------------|---------|
| 1 | `BlockBell` | `BiblioCraft:bell` | 0 | Dzwon (dekoracyjny) | `minecraft:bell` | **high** |
| 2 | `BlockSeat` | `BiblioCraft:seat` | 0-15 | Siedzisko (wood type) | `minecraft:oak_stairs` lub `supplementaries:seat` | **medium** |
| 3 | `BlockMapFrame` | `BiblioCraft:mapFrame` | 0-15 | Ramka na mapę (wood type) | `supplementaries:frame` lub `minecraft:item_frame` | **medium** |

### Uwagi do mapowania
- **Bell** – BiblioCraft Bell to blok dekoracyjny bez funkcji dźwiękowej (w 1.7.10 vanilla nie ma dzwonu). W 1.18.2 `minecraft:bell` istnieje i ma zupełnie inną mechanikę. Najbezpieczniejszy fallback to `minecraft:bell` (dekoracyjny) lub `supplementaries:globe` (jeśli bardziej dekoracyjny).
- **Seat** – w 1.7.10 metadata określa typ drewna (oak, spruce, itp.). W 1.18.2 brakuje odpowiednika siedziska w Supplementaries (jest `seat`, ale tylko dla niektórych wood types). Fallback: `minecraft:<wood>_stairs` z odpowiednim wood type.
- **MapFrame** – w 1.7.10 ramka na mapę jest blokiem, nie entity. W 1.18.2 `minecraft:item_frame` to entity. `supplementaries:frame` to blok, ale wymaga weryfikacji czy akceptuje mapy.

---

## 3. Bloki z TileEntity (poza zakresem block-only)

Wszystkie pozostałe bloki BiblioCraft mają TileEntity i są obsługiwane przez istniejący konwerter NBT:
- Bookcase, GenericShelf, PotionShelf, WeaponRack, WeaponCase, SwordPedestal, Table, CookieJar, DinnerPlate
- FramedChest, ArmorStand, Painting, Clock, FancySign, Lantern, Lamp
- WritingDesk, TypeMachine, PrintPress, FurniturePaneler, PaintPress, FancyWorkbench, Clipboard, Label
- BlockFramedChest (jedyny Framed* z osobną klasą)

---

## 4. Fallbacki i decyzje

| Sytuacja | Fallback | Pewność |
|----------|----------|---------|
| BiblioCraft Bell | `minecraft:bell` | medium (inna funkcjonalność) |
| BiblioCraft Seat (oak) | `minecraft:oak_stairs` | medium |
| BiblioCraft Seat (spruce) | `minecraft:spruce_stairs` | medium |
| BiblioCraft Seat (birch) | `minecraft:birch_stairs` | medium |
| BiblioCraft Seat (jungle) | `minecraft:jungle_stairs` | medium |
| BiblioCraft Seat (acacia) | `minecraft:acacia_stairs` | medium |
| BiblioCraft Seat (dark oak) | `minecraft:dark_oak_stairs` | medium |
| BiblioCraft MapFrame | `supplementaries:frame` | medium |
| Nieznany wood type Seat | `minecraft:oak_stairs` | low |

---

## 5. Warianty odrzucone / wymagające review

- **Framed bloki** (FramedBookcase, FramedShelf, itp.) – w kodzie 1.7.10 nie ma osobnych klas bloków dla większości Framed*. Są to prawdopodobnie warianty tekstur na istniejących blokach z TE (np. BlockBookcase z custom NBT `customTexture`). Dlatego pozostają w workflow TE.
- **Disc Rack** – nie znaleziono osobnej klasy `BlockDiscRack`; prawdopodobnie jest częścią innego bloku z TE.

---

## 6. Handoff – decyzje mapowania

1. ✅ `bell` → `minecraft:bell` (dekoracyjny fallback, brak dźwięku bez redstone).
2. ✅ `seat` → `minecraft:*_stairs` odpowiedni wood type; jeśli Supplementaries ma `seat`, rozważyć jako alternatywę.
3. ✅ `mapFrame` → `supplementaries:frame` (blok) lub `minecraft:item_frame` (entity – wymaga innego workflow).
4. ❌ Wszystkie pozostałe bloki BC pozostają w konwerterze TE/NBT.
