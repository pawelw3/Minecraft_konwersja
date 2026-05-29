# AE2 - Block-Only Analiza (Krok 1)

> **Mod:** Applied Energistics 2 (1.7.10 → 1.18.2)  
> **Data:** 2026-05-29  
> **Cel:** Identyfikacja zwykłych bloków bez TileEntity, które można przepchnąć przez warstwę block-only.

---

## 1. Stan faktyczny

AE2 w 1.7.10 jest modem niemal w całości opartym na TileEntity. Zdecydowana większość jego bloków (ME Controller, ME Drive, Interface, Cable Bus, itp.) przechowuje dane sieci, inventory lub konfigurację w NBT.

Bloki **bez TileEntity** stanowią wyłącznie warstwę dekoracyjną i nie przechowują żadnego stanu runtime.

---

## 2. Bloki bez TileEntity w 1.7.10

| # | Klasa Java | Registry name (przybliżone) | Metadata | Opis | Target 1.18.2 | Pewność |
|---|-----------|------------------------------|----------|------|---------------|---------|
| 1 | `BlockQuartz` | `appliedenergistics2:tile.BlockQuartz` | 0 | Certus Quartz Block | `ae2:quartz_block` | **high** |
| 2 | `BlockQuartzChiseled` | `appliedenergistics2:tile.BlockQuartzChiseled` | 0 | Chiseled Certus Quartz | `ae2:quartz_block` (variant chiseled) | **high** |
| 3 | `BlockQuartzPillar` | `appliedenergistics2:tile.BlockQuartzPillar` | 0-1 | Quartz Pillar (axis) | `ae2:quartz_pillar` | **high** |
| 4 | `BlockQuartzGlass` | `appliedenergistics2:tile.BlockQuartzGlass` | 0 | Quartz Glass | `ae2:quartz_glass` | **high** |
| 5 | `BlockFluix` | `appliedenergistics2:tile.BlockFluix` | 0 | Fluix Block | `ae2:fluix_block` | **high** |
| 6 | `BlockSkyStone` | `appliedenergistics2:tile.BlockSkyStone` | 0-3 | Sky Stone (block/brick/small brick) | `ae2:sky_stone_block` itp. | **high** |
| 7 | `OreQuartz` | `appliedenergistics2:tile.OreQuartz` | 0-1 | Certus Quartz Ore | `ae2:quartz_ore` / `ae2:deepslate_quartz_ore` | **high** |
| 8 | `BlockTinyTNT` | `appliedenergistics2:tile.BlockTinyTNT` | 0 | Tiny TNT | `ae2:tiny_tnt` | **high** |
| 9 | `BlockQuartzTorch` | `appliedenergistics2:tile.BlockQuartzTorch` | 0 | Quartz Torch / Fixture | `ae2:quartz_fixture` | **medium** |
| 10 | `BlockMatrixFrame` | `appliedenergistics2:tile.BlockMatrixFrame` | 0 | Matrix Frame (spatial) | `ae2:matrix_frame` | **high** |
| 11 | `BlockPaint` | `appliedenergistics2:tile.BlockPaint` | 0-15 | Paint Splotches | `ae2:paint` | **medium** |
| 12 | `BlockLightDetector` | `appliedenergistics2:tile.BlockLightDetector` | 0 | Light Detector | `ae2:light_detector` | **medium** |
| 13 | `ChiseledQuartzStairBlock` | `appliedenergistics2:tile.ChiseledQuartzStairs` | 0-7 | Chiseled Quartz Stairs | `ae2:chiseled_quartz_stairs` | **high** |
| 14 | `SkyStoneStairBlock` | `appliedenergistics2:tile.SkyStoneStairs` | 0-7 | Sky Stone Stairs | `ae2:sky_stone_stairs` | **high** |
| 15 | `SkyStoneBrickStairBlock` | `appliedenergistics2:tile.SkyStoneBrickStairs` | 0-7 | Sky Stone Brick Stairs | `ae2:sky_stone_brick_stairs` | **high** |
| 16 | `SkyStoneSmallBrickStairBlock` | `appliedenergistics2:tile.SkyStoneSmallBrickStairs` | 0-7 | Sky Stone Small Brick Stairs | `ae2:sky_stone_small_brick_stairs` | **high** |
| 17 | `QuartzStairBlock` | `appliedenergistics2:tile.QuartzStairs` | 0-7 | Quartz Stairs | `ae2:quartz_stairs` | **high** |
| 18 | `SkyStoneBlockStairBlock` | `appliedenergistics2:tile.SkyStoneBlockStairs` | 0-7 | Sky Stone Block Stairs | `ae2:sky_stone_block_stairs` | **high** |
| 19 | `QuartzPillarStairBlock` | `appliedenergistics2:tile.QuartzPillarStairs` | 0-7 | Quartz Pillar Stairs | `ae2:quartz_pillar_stairs` | **high** |
| 20 | `FluixStairBlock` | `appliedenergistics2:tile.FluixStairs` | 0-7 | Fluix Stairs | `ae2:fluix_stairs` | **high** |

### Uwagi do mapowania
- `BlockSkyStone` w 1.7.10 używa metadata 0-3 do rozróżnienia wariantów (block, brick, small brick, block). W 1.18.2 są osobne registry names lub blockstates.
- `BlockQuartzPillar` w 1.7.10 ma metadata dla orientacji (axis). W 1.18.2 obsługiwane przez blockstate `axis=x/y/z`.
- Schody w 1.7.10 przechowują orientację w metadata 0-7 (standard MC). W 1.18.2 przez blockstates `facing`, `half`, `shape`.
- `BlockPaint` (Paint Splotches) to debug/dekoracyjny blok kolorów. Może nie występować na produkcyjnej mapie.
- `BlockLightDetector` i `BlockQuartzTorch` wymagają weryfikacji czy target 1.18.2 użyje tych samych registry names.

---

## 3. Bloki z TileEntity (poza zakresem block-only)

Wszystkie pozostałe bloki AE2 mają TileEntity i muszą być konwertowane przez główny workflow TE/eventów:
- ME Controller, ME Drive, ME Chest, Energy Acceptor, Energy Cell, Dense Energy Cell
- Crafting Unit, Molecular Assembler, ME Interface, IO Port
- Quantum Ring, Quantum Link Chamber, Spatial IO Port, Spatial Pylon
- Charger, Inscriber, Vibration Chamber, Crystal Growth Accelerator, Condenser
- Cable Bus, Wireless Access Point, Security Terminal
- Sky Stone Chest, Smooth Sky Stone Chest, Sky Stone Tank
- Cell Workbench, Crank, Quartz Grindstone

---

## 4. Fallbacki i decyzje

| Sytuacja | Fallback | Pewność |
|----------|----------|---------|
| Nieznany metadata Sky Stone | `ae2:sky_stone_block` | high |
| Nieznany metadata Quartz | `ae2:quartz_block` | high |
| Paint Splotches nieznany kolor | `minecraft:white_wool` | low (ale rzadkie) |
| Ore w Deepslate | `ae2:deepslate_quartz_ore` (jeśli Y<0) | medium |

---

## 5. Warianty odrzucone / wymagające review

- **Slaby (półpłytki)** – w kodzie AE2 1.7.10 istnieje `AEBaseSlabBlock`, ale nie znaleziono osobnych klas slabów w podpakietach. Wymaga weryfikacji czy AE2 w ogóle rejestruje slab-y w 1.7.10.
- **Mysterious Cube** – struktura meteoru, może być generowana proceduralnie. W 1.18.2 istnieje `ae2:mysterious_cube`, ale występowanie na mapie jest niepewne.

---

## 6. Handoff – decyzje mapowania

1. ✅ Bloki dekoracyjne AE2 (quartz, sky stone, fluix) mapować 1:1 na odpowiedniki 1.18.2.
2. ✅ Rudy certus quartz mapować na `ae2:quartz_ore` (stone) lub `ae2:deepslate_quartz_ore` (deepslate) w zależności od Y.
3. ✅ Schody i płytki (jeśli istnieją) przekazywać z zachowaniem orientacji metadata → blockstates.
4. ❌ Wszystkie maszyny, kontrolery, kable i części kablowe pozostają w workflow TileEntity.
5. ⚠️ Paint Splotches i Matrix Frame – sprawdzić występowanie na mapie; jeśli brak, można pominąć w MVP.
