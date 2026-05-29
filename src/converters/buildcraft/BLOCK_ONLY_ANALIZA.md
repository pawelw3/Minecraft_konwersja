# BuildCraft - Block-Only Analiza (Krok 1)

> **Mod:** BuildCraft 7.1.23 (1.7.10) → RFTools Builder / Pretty Pipes / Pipez / XNet 1.18.2  
> **Data:** 2026-05-29  
> **Cel:** Identyfikacja zwykłych bloków bez TileEntity.

---

## 1. Stan faktyczny

BuildCraft w 1.7.10 jest modem w znacznej części opartym na TileEntity. Prawie wszystkie maszyny, silniki, rury i interfejsy przechowują dane w NBT (inventory, energia, fluids, konfiguracja rur).

Inspekcja bytecode JAR wykazała, że **4 bloki** dziedziczą bezpośrednio po `net.minecraft.block.Block` (bez TE), poza blokami fluidów:

- `BlockFrame` (ramka quarry)
- `BlockSpring` (źródło ropy/wody)
- `BlockBuildTool` (blok narzędzia – creative/admin)
- `BlockPlainPipe` (rura górnicza – wizualna)

Wszystkie inne bloki BuildCraft dziedziczą po `BlockBuildCraft`, który to dziedziczy po `BlockContainer` (czyli mają TE).

---

## 2. Bloki bez TileEntity w 1.7.10

| # | Klasa Java | Registry name | Metadata | Opis | Target 1.18.2 | Pewność |
|---|-----------|---------------|----------|------|---------------|---------|
| 1 | `BlockFrame` | `BuildCraft|Builders:blockFrame` | 0 | Ramka Quarry (zwykły blok) | `minecraft:iron_bars` lub `minecraft:cobblestone_wall` | **low** |
| 2 | `BlockSpring` | `BuildCraft|Core:spring` | 0-? | Źródło ropy/wody (generowane) | `minecraft:water` / `minecraft:lava` | **low** |
| 3 | `BlockBuildTool` | `BuildCraft|Core:blockBuildTool` | 0 | Build Tool (creative) | `minecraft:air` | **high** |
| 4 | `BlockPlainPipe` | `BuildCraft|Factory:blockPlainPipe` | 0 | Rura górnicza (wizualna) | `minecraft:iron_bars` | **low** |

### Uwagi do mapowania
- **BlockFrame** – ramka quarry to zwykły blok konstrukcyjny generowany tymczasowo przez quarry. Na mapie źródłowej może występować jako pozostałość po przerwanej pracy quarry. Nie ma bezpośredniego odpowiednika w 1.18.2. Fallback: `minecraft:iron_bars` lub `minecraft:cobblestone`.
- **BlockSpring** – źródło ropy/wody generowane przez BuildCraft w świecie. W 1.7.10 metadata określa typ (water, oil). W 1.18.2 nie ma odpowiednika. Można zamienić na `minecraft:water` (jeśli water) lub `minecraft:stone` (jeśli oil, bo fluid oil zazwyczaj nie zostaje jako blok stały).
- **BlockBuildTool** – blok używany wyłącznie w trybie creative / do debugowania. Na mapie produkcyjnej praktycznie nie występuje. Fallback: `minecraft:air`.
- **BlockPlainPipe** – wizualna rura wydobywcza generowana przez Mining Well. Tymczasowy blok. Fallback: `minecraft:iron_bars`.

---

## 3. Bloki z TileEntity (poza zakresem block-only)

Wszystkie pozostałe bloki BuildCraft mają TileEntity:
- Quarry, Builder, Filler, Architect, Blueprint Library, Construction Marker
- Pump, Refinery, AutoWorkbench, Mining Well, Flood Gate, Tank, Hopper
- Wszystkie silniki (Redstone, Stirling, Combustion, Creative)
- Wszystkie rury (transport, fluid, energy, kinesis, structure, void)
- Laser, Assembly Table, Advanced Crafting Table, Integration Table
- Filtered Buffer, Requester, itp.
- Markery (`BlockMarker`, `BlockPathMarker`) – mają TE mimo że są markerami.

---

## 4. Fallbacki i decyzje

| Sytuacja | Fallback | Pewność |
|----------|----------|---------|
| BlockFrame (ramka quarry) | `minecraft:iron_bars` | low |
| BlockSpring (water) | `minecraft:water` | medium |
| BlockSpring (oil) | `minecraft:stone` | low |
| BlockBuildTool | `minecraft:air` | high |
| BlockPlainPipe | `minecraft:iron_bars` | low |

---

## 5. Warianty odrzucone / wymagające review

- **BlockSpring** – jeśli występuje na mapie, oznacza to że gracze mogli użyć go jako nieskończonego źródła. Konwersja na `minecraft:water` traci funkcjonalność nieskończonego źródła. Wymaga review.
- **BlockFrame** – jeśli występuje w dużej ilości, może oznaczać aktywne quarry. Konwersja dekoracyjna może być myląca.
- **Bloki fluidów** (`tile.blockFluid.*`) – rejestrowane przez FluidRegistry. Są to bloki cieczy, które mają własny system (nie custom TE, ale też nie zwykłe bloki stałe). Osobna warstwa dla fluidów.

---

## 6. Handoff – decyzje mapowania

1. ✅ `BuildCraft|Builders:blockFrame` → `minecraft:iron_bars` (fallback dekoracyjny).
2. ✅ `BuildCraft|Core:spring` → `minecraft:water` (jeśli water) / `minecraft:stone` (jeśli oil).
3. ✅ `BuildCraft|Core:blockBuildTool` → `minecraft:air` (blok admin/creative).
4. ✅ `BuildCraft|Factory:blockPlainPipe` → `minecraft:iron_bars` (fallback dekoracyjny).
5. ❌ Wszystkie maszyny, silniki, rury i interfejsy pozostają w workflow TE/eventów.
6. ⚠️ BuildCraft wymaga głębokiej konwersji "w duchu" (pipes → Pipez/XNet, quarry → RFTools Builder). Bloki bez TE są marginalne.
