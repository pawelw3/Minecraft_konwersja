# Blood Magic - Block-Only Analiza (Krok 1)

> **Mod:** Blood Magic 1.3.3-17 (1.7.10) → Blood Magic 3.2.6 (1.18.2)  
> **Data:** 2026-05-29  
> **Cel:** Identyfikacja zwykłych bloków bez TileEntity.

---

## 1. Stan faktyczny

Blood Magic w 1.7.10 ma zarówno funkcjonalne bloki z TileEntity (ołtarze, portale, pedestały, forgenie), jak i dekoracyjne/funkcjonalne bloki bez TE (runy, kamienie rytualne, bloki dekoracyjne, źródła światła).

Inspekcja bytecode JAR wykazała **10 klas bloków dziedziczących bezpośrednio po `net.minecraft.block.Block`** (bez TE):

- `BloodRune` (oraz podklasy: `SpeedRune`, `EfficiencyRune`, `RuneOfSacrifice`, `RuneOfSelfSacrifice`)
- `RitualStone`
- `ImperfectRitualStone`
- `BloodStoneBrick`
- `LargeBloodStoneBrick`
- `BlockCrystal` (dekoracyjny kryształ)
- `BlockEnchantmentGlyph`
- `BlockStabilityGlyph`
- `BlockBloodLightSource`

---

## 2. Bloki bez TileEntity w 1.7.10

| # | Klasa Java | Registry name | Metadata | Opis | Target 1.18.2 | Pewność |
|---|-----------|---------------|----------|------|---------------|---------|
| 1 | `BloodRune` | `AWWayofTime:bloodRune` | 0 | Blank Rune | `bloodmagic:blank_rune` | **high** |
| 2 | `BloodRune` | `AWWayofTime:bloodRune` | 1 | Dislocation Rune | `bloodmagic:dislocation_rune` | **high** |
| 3 | `BloodRune` | `AWWayofTime:bloodRune` | 2 | Capacity Rune | `bloodmagic:capacity_rune` | **high** |
| 4 | `BloodRune` | `AWWayofTime:bloodRune` | 3 | Augmented Capacity Rune | `bloodmagic:better_capacity_rune` | **high** |
| 5 | `BloodRune` | `AWWayofTime:bloodRune` | 4 | Orb Capacity Rune | `bloodmagic:orb_rune` | **high** |
| 6 | `BloodRune` | `AWWayofTime:bloodRune` | 5 | Acceleration Rune | `bloodmagic:acceleration_rune` | **high** |
| 7 | `SpeedRune` | `AWWayofTime:speedRune` | 0 | Speed Rune (osobny blok) | `bloodmagic:speed_rune` | **high** |
| 8 | `EfficiencyRune` | `AWWayofTime:efficiencyRune` | 0 | Efficiency Rune | `bloodmagic:efficiency_rune` | **high** |
| 9 | `RuneOfSacrifice` | `AWWayofTime:runeOfSacrifice` | 0 | Sacrifice Rune | `bloodmagic:sacrifice_rune` | **high** |
| 10 | `RuneOfSelfSacrifice` | `AWWayofTime:runeOfSelfSacrifice` | 0 | Self-Sacrifice Rune | `bloodmagic:self_sacrifice_rune` | **high** |
| 11 | `RitualStone` | `AWWayofTime:ritualStone` | 0-? | Ritual Stone | `bloodmagic:ritual_stone` | **medium** |
| 12 | `ImperfectRitualStone` | `AWWayofTime:imperfectRitualStone` | 0 | Imperfect Ritual Stone | `bloodmagic:imperfect_ritual_stone` | **high** |
| 13 | `BloodStoneBrick` | `AWWayofTime:bloodStoneBrick` | 0 | Bloodstone Brick | `bloodmagic:bloodstone_brick` | **high** |
| 14 | `LargeBloodStoneBrick` | `AWWayofTime:largeBloodStoneBrick` | 0 | Large Bloodstone Brick | `bloodmagic:large_bloodstone_brick` | **high** |
| 15 | `BlockCrystal` | `AWWayofTime:crystal` | 0 | Crystal (dekoracyjny) | `bloodmagic:dungeon_crystal` lub `minecraft:amethyst_block` | **low** |
| 16 | `BlockEnchantmentGlyph` | `AWWayofTime:enchantmentGlyph` | 0-? | Enchantment Glyph | `bloodmagic:blank_rune` (fallback) | **low** |
| 17 | `BlockStabilityGlyph` | `AWWayofTime:stabilityGlyph` | 0-? | Stability Glyph | `bloodmagic:blank_rune` (fallback) | **low** |
| 18 | `BlockBloodLightSource` | `AWWayofTime:bloodLight` | 0 | Blood Light Source | `minecraft:torch` lub `bloodmagic:alchemy_lamp` | **low** |

### Uwagi do mapowania
- **Blood Rune metadata** – w 1.7.10 wszystkie runy bazowe są w jednym bloku z metadata. W 1.18.2 każda runa to osobny blok (brak blockstate "type").
- **Ritual Stone** – w 1.7.10 metadata może określać typ (raw, fire, water, earth, air, dusk). W 1.18.2 są osobne bloki lub blockstates. Wymaga weryfikacji czy `ritual_stone` w 1.18.2 ma warianty czy są osobne registry.
- **Crystal, Glyphs, BloodLight** – te bloki są słabo udokumentowane w kodzie źródłowym 1.18.2. Ich mapowanie ma niski poziom pewności i wymaga review wizualnego.

---

## 3. Bloki z TileEntity (poza zakresem block-only)

Wszystkie pozostałe bloki Blood Magic mają TileEntity:
- `Altar` (Blood Altar)
- `MasterStone` (Master Ritual Stone)
- `SoulForge`
- `DemonPortal`
- `Pedestal`, `Plinth`, `Socket`
- `Teleposer`, `AlchemicCalcinator`, `Crucible`, `Belljar`
- `HomHeart`
- `BlockOrientable` i podklasy (`SpellEffect`, `SpellEnhancement`, `SpellModifier`, `SpellParadigm`, `Conduit`, `ReagentConduit`)
- `SchematicSaver`

---

## 4. Fallbacki i decyzje

| Sytuacja | Fallback | Pewność |
|----------|----------|---------|
| Nieznana metadata BloodRune | `bloodmagic:blank_rune` | medium |
| Nieznany typ RitualStone | `bloodmagic:ritual_stone` | medium |
| BlockCrystal bez odpowiednika | `minecraft:amethyst_block` | low |
| Glyphs bez odpowiednika | `bloodmagic:blank_rune` | low |
| BloodLightSource bez odpowiednika | `minecraft:torch` | medium |

---

## 5. Warianty odrzucone / wymagające review

- **BlockCrystal** – nie wiadomo czy w 1.18.2 istnieje dokładny odpowiednik. `bloodmagic:dungeon_crystal` to tylko przypuszczenie.
- **EnchantmentGlyph / StabilityGlyph** – bloki związane z mechanicą Omega (1.7.10). W 1.18.2 system Omega nie istnieje. Fallback dekoracyjny.
- **BloodLightSource** – tymczasowe źródło światła generowane przez rytuały. Może nie występować jako trwały blok na mapie.

---

## 6. Handoff – decyzje mapowania

1. ✅ `AWWayofTime:bloodRune/meta 0-5` → odpowiednie `bloodmagic:*_rune` (osobne bloki w 1.18.2).
2. ✅ `AWWayofTime:speedRune` → `bloodmagic:speed_rune`.
3. ✅ `AWWayofTime:efficiencyRune` → `bloodmagic:efficiency_rune`.
4. ✅ `AWWayofTime:runeOfSacrifice` → `bloodmagic:sacrifice_rune`.
5. ✅ `AWWayofTime:runeOfSelfSacrifice` → `bloodmagic:self_sacrifice_rune`.
6. ✅ `AWWayofTime:ritualStone` → `bloodmagic:ritual_stone` (warianty do doprecyzowania).
7. ✅ `AWWayofTime:imperfectRitualStone` → `bloodmagic:imperfect_ritual_stone`.
8. ✅ `AWWayofTime:bloodStoneBrick` → `bloodmagic:bloodstone_brick`.
9. ✅ `AWWayofTime:largeBloodStoneBrick` → `bloodmagic:large_bloodstone_brick`.
10. ⚠️ `AWWayofTime:crystal` → `minecraft:amethyst_block` (fallback, wymaga review).
11. ⚠️ Glyphs → `bloodmagic:blank_rune` (fallback dekoracyjny).
12. ⚠️ `AWWayofTime:bloodLight` → `minecraft:torch` (fallback świetlny).
13. ❌ Wszystkie maszyny, ołtarze, portale i bloki z inventory pozostają w workflow TE.
