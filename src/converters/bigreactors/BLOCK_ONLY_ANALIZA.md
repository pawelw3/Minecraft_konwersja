# Big Reactors - Block-Only Analiza (Krok 1)

> **Mod:** Big Reactors 1.7.10 → Bigger Reactors 1.18.2  
> **Data:** 2026-05-29  
> **Cel:** Identyfikacja zwykłych bloków bez TileEntity.

---

## 1. Stan faktyczny

Big Reactors w 1.7.10 to mod oparty na multiblokach (reaktor, turbina). Praktycznie wszystkie bloki konstrukcyjne mają TileEntity (casing, controller, porty, szkło, fuel rod, itp.).

Inspekcja bytecode JAR wykazała, że tylko **2 bloki** dziedziczą bezpośrednio po `net.minecraft.block.Block` (bez TE):

- `BlockBROre` (Yellorite Ore)
- `BlockBRMetal` (bloki metalu: Yellorium, Cyanite, Graphite, Blutonium, Ludicrite)

Pozostałe bloki (części reaktora, turbiny, urządzenia) dziedziczą po klasach z TileEntity.

---

## 2. Bloki bez TileEntity w 1.7.10

| # | Klasa Java | Registry name | Metadata | Opis | Target 1.18.2 | Pewność |
|---|-----------|---------------|----------|------|---------------|---------|
| 1 | `BlockBROre` | `BigReactors:YelloriteOre` | 0 | Yellorite Ore (generowana ruda) | `biggerreactors:uranium_ore` / `biggerreactors:deepslate_uranium_ore` | **high** |
| 2 | `BlockBRMetal` | `BigReactors:BRMetalBlock` | 0 | Yellorium Block | `biggerreactors:uranium_block` | **high** |
| 3 | `BlockBRMetal` | `BigReactors:BRMetalBlock` | 1 | Cyanite Block | `biggerreactors:cyanite_block` | **high** |
| 4 | `BlockBRMetal` | `BigReactors:BRMetalBlock` | 2 | Graphite Block | `biggerreactors:graphite_block` | **high** |
| 5 | `BlockBRMetal` | `BigReactors:BRMetalBlock` | 3 | Blutonium Block | `biggerreactors:blutonium_block` | **high** |
| 6 | `BlockBRMetal` | `BigReactors:BRMetalBlock` | 4 | Ludicrite Block | `biggerreactors:ludicrite_block` | **high** |

### Uwagi do mapowania
- `Yellorite Ore` w 1.18.2 została przemianowana na `Uranium Ore`. W zależności od Y-level na mapie źródłowej należy wybrać `uranium_ore` (stone) lub `deepslate_uranium_ore` (deepslate). W 1.7.10 nie ma rozróżnienia deepslate, więc domyślnie `uranium_ore`.
- `Yellorium Block` → `uranium_block` (zmiana nazewnictwa w BiggerReactors).
- `Graphite Block` służy jako moderator w reaktorze; w 1.18.2 zachowuje tę samą funkcję.
- Metadata 0-4 dla `BRMetalBlock` to standardowy podział wariantów w Forge 1.7.10.

---

## 3. Bloki z TileEntity (poza zakresem block-only)

Wszystkie pozostałe bloki BR mają TileEntity i są obsługiwane przez konwerter multibloków / TE:
- Reactor Casing, Controller, Control Rod, Power Tap, Access Port, Coolant Port, RedNet Port, Computer Port, Redstone Port
- Reactor Glass, Yellorium Fuel Rod
- Turbine Housing, Controller, Power Tap, Fluid Port, Rotor Bearing, Computer Port
- Turbine Glass, Rotor Shaft, Rotor Blade
- Cyanite Reprocessor
- Creative Coolant Port, Creative Steam Generator

---

## 4. Fallbacki i decyzje

| Sytuacja | Fallback | Pewność |
|----------|----------|---------|
| Nieznana metadata BRMetalBlock | `biggerreactors:graphite_block` | low |
| Yellorite Ore poniżej Y=0 | `biggerreactors:deepslate_uranium_ore` | medium |
| Yellorite Ore powyżej Y=0 | `biggerreactors:uranium_ore` | high |

---

## 5. Warianty odrzucone / wymagające review

- **Ciecze** (`fluidYellorium`, `fluidCyanite`) – są rejestrowane jako bloki fluidów. W 1.18.2 BiggerReactors ma `liquid_uranium` i `liquid_obsidian`, ale konwersja fluidów wymaga osobnej warstwy (nie block-only, bo fluidy mają własny system NBT i level).
- **BRMultiblockCreativePart** – ma TileEntity, więc poza zakresem.

---

## 6. Handoff – decyzje mapowania

1. ✅ `BigReactors:YelloriteOre` → `biggerreactors:uranium_ore` (domyślnie) lub `deepslate_uranium_ore` (jeśli Y<0).
2. ✅ `BigReactors:BRMetalBlock/0` → `biggerreactors:uranium_block`.
3. ✅ `BigReactors:BRMetalBlock/1` → `biggerreactors:cyanite_block`.
4. ✅ `BigReactors:BRMetalBlock/2` → `biggerreactors:graphite_block`.
5. ✅ `BigReactors:BRMetalBlock/3` → `biggerreactors:blutonium_block`.
6. ✅ `BigReactors:BRMetalBlock/4` → `biggerreactors:ludicrite_block`.
7. ❌ Wszystkie części multibloków (reaktor, turbina, maszyny) pozostają w workflow TE.
