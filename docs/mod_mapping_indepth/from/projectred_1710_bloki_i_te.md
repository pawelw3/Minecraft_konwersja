# ProjectRed 1.7.10 - Analiza Bloków i Tile Entities

> **Wersja moda:** 4.7.0pre12.95 (z paczki GTNewHorizons)
> **Źródło kodu:** `mod_src/1710/actual_src/1.7.10/ProjectRed_GTNH/`
> **Data analizy:** 2026-02-02

---

## Spis treści
1. [Przegląd modułów](#przegląd-modułów)
2. [Expansion - Bloki i TileEntity](#expansion---bloki-i-tileentity)
3. [Exploration - Bloki i TileEntity](#exploration---bloki-i-tileentity)
4. [Fabrication - Bloki i TileEntity](#fabrication---bloki-i-tileentity)
5. [Illumination - Bloki i TileEntity](#illumination---bloki-i-tileentity)
6. [Integration - Bramki (Multipart)](#integration---bramki-multipart)
7. [Transmission - Przewody (Multipart)](#transmission---przewody-multipart)
8. [Transportation - Rury (Multipart)](#transportation---rury-multipart)

---

## Przegląd modułów

| Moduł | Mod ID | Opis |
|-------|--------|------|
| Core | `ProjRed|Core` | Rdzeń - podstawowe itemy, Generator Electrotine |
| Expansion | `ProjRed|Expansion` | Maszyny, urządzenia, system energii |
| Exploration | `ProjRed|Exploration` | Rudy, bloki dekoracyjne, narzędzia |
| Fabrication | `ProjRed|Fabrication` | IC Workbench, IC Printer |
| Illumination | `ProjRed|Illumination` | Lampy, oświetlenie |
| Integration | `ProjRed|Integration` | Bramki logiczne (multipart) |
| Transmission | `ProjRed|Transmission` | Przewody redstone (multipart) |
| Transportation | `ProjRed|Transportation` | Rury transportowe (multipart) |

---

## Expansion - Bloki i TileEntity

### Blok: `projectred.expansion.machine1` (BlockMachine)

| Meta | TileEntity | Registry Name | Opis |
|------|------------|---------------|------|
| 0 | `TileInductiveFurnace` | - | Piec indukcyjny - przetwarza rudy używając energii Electrotine |
| 1 | `TileElectrotineGenerator` | - | Generator Electrotine - wytwarza energię z paliwa Electrotine |

### Blok: `projectred.expansion.machine2` (BlockMachine)

| Meta | TileEntity | Registry Name | Opis |
|------|------------|---------------|------|
| 0 | `TileBlockBreaker` | - | Łamacz bloków - niszczy bloki przed sobą na sygnał redstone |
| 1 | `TileItemImporter` | - | Importer itemów - pobiera itemy z kontenerów |
| 2 | `TileBlockPlacer` | - | Stawiacz bloków - umieszcza bloki z inwentarza |
| 3 | `TileFilteredImporter` | - | Filtrowany importer - pobiera tylko określone itemy |
| 4 | `TileFireStarter` | - | Zapalniczka - zapala bloki przed sobą |
| 5 | `TileBatteryBox` | - | Skrzynka baterii - przechowuje energię Electrotine |
| 6 | `TileChargingBench` | - | Stół ładowania - ładuje przedmioty używające baterii |
| 7 | `TileTeleposer` | - | Teleposer - teleportuje bloki/entity za pomocą Ender Pearl |
| 8 | `TileFrameMotor` | - | Silnik ramek - napędza system ramek |
| 9 | `TileFrameActuator` | - | Aktuator ramek - liniowy siłownik dla systemu ramek |
| 10 | `TileProjectBench` | - | Stół projektu - zaawansowany stół craftingowy z pamięcią receptury |
| 11 | `TileAutoCrafter` | - | Automatyczny crafter - automatycznie wykonuje recepty |
| 12 | `TileDiamondBlockBreaker` | - | Diamentowy łamacz bloków (opcjonalny w konfiguracji) |

#### Szczegóły TileBatteryBox

**Plik:** `expansion/TileBatteryBox.scala`

```scala
class TileBatteryBox extends TileMachine with TPoweredMachine with TGuiMachine
    with TInventory with ISidedInventory {

  var powerStored = 0

  override def save(tag: NBTTagCompound) {
    super.save(tag)
    tag.setInteger("pow", powerStored)
    saveInv(tag)
  }

  override def load(tag: NBTTagCompound) {
    super.load(tag)
    powerStored = tag.getInteger("pow")
    loadInv(tag)
  }
}
```

**Dane NBT:**
- `pow` (Integer) - przechowywana energia
- `rot` (Byte) - orientacja
- Inwentarz baterii

#### Szczegóły TileProjectBench

**Plik:** `expansion/TileProjectBench.scala`

**Funkcjonalność:**
- 18-slotowy inwentarz (9 crafting grid + 9 storage)
- Pamięta ostatnią recepturę
- Może automatycznie pobierać składniki z inwentarza

**Dane NBT:**
- Inwentarz (18 slotów)
- `planslot` - zapisana receptura

---

## Exploration - Bloki i TileEntity

### Blok: `projectred.exploration.ore` (BlockOre)

| Meta | Nazwa | Ore Dict | Harvest Level |
|------|-------|----------|---------------|
| 0 | Ruby Ore | oreRuby | 2 |
| 1 | Sapphire Ore | oreSapphire | 2 |
| 2 | Peridot Ore | orePeridot | 2 |
| 3 | Copper Ore | oreCopper | 1 |
| 4 | Tin Ore | oreTin | 1 |
| 5 | Silver Ore | oreSilver | 2 |
| 6 | Electrotine Ore | oreElectrotine | 2 |

### Blok: `projectred.exploration.stone` (BlockDecoratives)

| Meta | Nazwa | Ore Dict |
|------|-------|----------|
| 0 | Marble | blockMarble |
| 1 | Marble Brick | - |
| 2 | Basalt | - |
| 3 | Basalt Cobble | - |
| 4 | Basalt Brick | - |
| 5 | Ruby Block | blockRuby |
| 6 | Sapphire Block | blockSapphire |
| 7 | Peridot Block | blockPeridot |
| 8 | Copper Block | blockCopper |
| 9 | Tin Block | blockTin |
| 10 | Silver Block | blockSilver |
| 11 | Electrotine Block | blockElectrotine |

### Blok: BlockDecorativeWalls

Mury dla wszystkich wariantów DecorativeStoneDefs (każdy ma odpowiednią metadaną).

### Blok: BlockLily → TileLily

Kolorowe lilie (16 kolorów, meta 0-15).

### Blok: BlockBarrel → TileBarrel

**Plik:** `exploration/TileBarrel.scala`

**Funkcjonalność:**
- Przechowuje duże ilości jednego typu itemu
- Wyświetla zawartość na teksturze

**Dane NBT:**
- `item` (ItemStack) - przechowywany item
- `count` (Integer) - ilość

---

## Fabrication - Bloki i TileEntity

### Blok: BlockICMachine

| Meta | TileEntity | Opis |
|------|------------|------|
| 0 | `TileICWorkbench` | Stół roboczy IC - projektowanie układów scalonych |
| 1 | `TileICPrinter` | Drukarka IC - drukowanie zaprojektowanych układów |

#### TileICWorkbench

**Plik:** `fabrication/tileicworkbench.scala`

**Funkcjonalność:**
- Edytor układów scalonych (IC)
- Siatka projektowa do umieszczania bramek, przewodów
- Zapisuje projekt do ItemICBlueprint

**Dane NBT:**
- Zapisany projekt IC (złożona struktura)
- Sloty inwentarza

#### TileICPrinter

**Plik:** `fabrication/tileicprinter.scala`

**Funkcjonalność:**
- Drukuje układy IC z blueprintów
- Wymaga materiałów (plates, chips)

---

## Illumination - Bloki i TileEntity

### Blok: BlockLamp → TileLamp

16 kolorów lamp (meta 0-15), każdy kolor ma wariant inverted.

**Plik:** `illumination/blocks.scala`

```scala
class TileLamp extends InstancedBlockTile {
  var inverted = false
  var powered = false

  override def save(tag: NBTTagCompound) {
    tag.setBoolean("inv", inverted)
    tag.setBoolean("pow", powered)
  }
}
```

### Blok: BlockAirousLight → TileAirousLight

Niewidzialny blok światła używany przez lampy cage/lantern.

**Dane NBT:**
- `src` - pozycja źródłowej lampy

---

## Integration - Bramki (Multipart)

Bramki logiczne są **multipart**, nie standardowymi blokami. Używają ForgeMultipart.

### Typy części multipart:

| Part Type | Klasa | Opis |
|-----------|-------|------|
| `pr_sgate` | ComboGatePart | Bramki kombinacyjne (AND, OR, NOT, NOR, NAND, XOR, XNOR, Buffer, Multiplexer) |
| `pr_igate` | SequentialGatePart | Bramki sekwencyjne (Timer, Counter, Sequencer, Pulse, State Cell) |
| `pr_agate` | ArrayGatePart | Bramki array (Null Cell, Invert Cell, Buffer Cell, AND Cell) |
| `pr_bgate` | BundledGatePart | Bramki bundled (Bus Transceiver, Bus Randomizer, Bus Converter, Bus Input Panel) |
| `pr_tgate` | SequentialGatePartT | Dodatkowe bramki sekwencyjne |

### GateDefinition (wszystkie typy bramek):

| Ordinal | Nazwa | Typ |
|---------|-------|-----|
| 0 | AND | pr_sgate |
| 1 | OR | pr_sgate |
| 2 | NOT | pr_sgate |
| 3 | SRLatch | pr_sgate |
| 4 | ToggleLatch | pr_sgate |
| 5 | TransparentLatch | pr_sgate |
| 6 | NOR | pr_sgate |
| 7 | NAND | pr_sgate |
| 8 | XOR | pr_sgate |
| 9 | XNOR | pr_sgate |
| 10 | Buffer | pr_sgate |
| 11 | Multiplexer | pr_sgate |
| 12 | Repeater | pr_sgate |
| 13 | Timer | pr_igate |
| 14 | Counter | pr_igate |
| 15 | Sequencer | pr_igate |
| 16 | Pulse | pr_igate |
| 17 | Randomizer | pr_sgate |
| 18 | StateCell | pr_igate |
| 19 | Synchronizer | pr_sgate |
| 20 | LightSensor | pr_sgate |
| 21 | RainSensor | pr_sgate |
| 22 | BusTransceiver | pr_bgate |
| 23 | NullCell | pr_agate |
| 24 | InvertCell | pr_agate |
| 25 | BufferCell | pr_agate |
| 26 | Comparator | pr_sgate |
| 27 | ANDCell | pr_agate |
| 28 | BusRandomizer | pr_bgate |
| 29 | BusConverter | pr_bgate |
| 30 | BusInputPanel | pr_bgate |
| 31 | StackingLatch | pr_sgate |
| 32 | SegmentDisplay | pr_bgate |
| 33 | DecRandomizer | pr_sgate |
| 34 | ICGate | pr_icgate (Fabrication) |

---

## Transmission - Przewody (Multipart)

### Typy części multipart:

| Part Type | Opis |
|-----------|------|
| `pr_redwire` | Podstawowy przewód redstone |
| `pr_insulated` | Izolowany przewód (16 kolorów) |
| `pr_bundled` | Przewód bundled (16 kanałów) |
| `pr_framed_redwire` | Ramkowany przewód redstone |
| `pr_framed_insulated` | Ramkowany izolowany przewód |
| `pr_framed_bundled` | Ramkowany przewód bundled |

---

## Transportation - Rury (Multipart)

### Typy części multipart:

| Part Type | Opis |
|-----------|------|
| Pressure Tubes | Rury pneumatyczne do transportu itemów |
| Routing Pipes | Rury z routingiem (podobne do Logistics Pipes) |

---

## Podsumowanie danych NBT

### Klasa bazowa TileMachine

```scala
// Wspólne dane NBT dla wszystkich maszyn:
tag.setByte("rot", orientation)  // orientacja (side + rotation)

// Dla TPoweredMachine:
cond.save(tag)  // dane PowerConductor (charge, flow)

// Dla TileProcessingMachine:
tag.setBoolean("ch", isCharged)
tag.setBoolean("work", isWorking)
tag.setInteger("rem", workRemaining)
tag.setInteger("max", workMax)
```

---

## Źródła

- **Kod źródłowy:** https://github.com/GTNewHorizons/ProjectRed
- **Wiki:** https://projectredwiki.com/wiki/Main_Page
- **CurseForge:** https://www.curseforge.com/minecraft/mc-mods/project-red-base
