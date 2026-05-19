# ProjectRed 1.18.2+ - Analiza Bloków i Block Entities

> **Wersja moda:** 4.17.0+ (NeoForge)
> **Źródło kodu:** `mod_src/118/actual_src/1.18.2/ProjectRed/repo/`
> **Data analizy:** 2026-02-02
> **UWAGA:** Kod w repozytorium używa NeoForge API, więc to może być wersja nowsza (1.20+)

---

## Spis treści
1. [Przegląd modułów](#przegląd-modułów)
2. [Core - Bloki i BlockEntity](#core---bloki-i-blockentity)
3. [Expansion - Bloki i BlockEntity](#expansion---bloki-i-blockentity)
4. [Exploration - Bloki](#exploration---bloki)
5. [Fabrication - Bloki i BlockEntity](#fabrication---bloki-i-blockentity)
6. [Illumination - Bloki i BlockEntity](#illumination---bloki-i-blockentity)

---

## Przegląd modułów

| Moduł | Opis |
|-------|------|
| Core | Rdzeń - Generator Electrotine, podstawowe itemy |
| Expansion | Maszyny, urządzenia, system energii |
| Exploration | Rudy, bloki dekoracyjne |
| Fabrication | IC Workbench, stoły fabrykacji |
| Illumination | Lampy, oświetlenie |
| Integration | Bramki logiczne (multipart) |
| Transmission | Przewody redstone (multipart) |

---

## Core - Bloki i BlockEntity

### electrotine_generator

**BlockEntity:** `ElectrotineGeneratorBlockEntity`

**Plik:** `core/tile/ElectrotineGeneratorBlockEntity.java`

**Funkcjonalność:**
- Generator energii Electrotine
- Przyjmuje paliwo Electrotine i wytwarza energię

**Dane NBT:** (z BasePoweredBlockEntity)
- orientation
- charge, flow (PowerConductor)

---

## Expansion - Bloki i BlockEntity

| Block ID | BlockEntity | Opis |
|----------|-------------|------|
| `project_bench` | ProjectBenchBlockEntity | Stół projektu - zaawansowany crafting |
| `battery_box` | BatteryBoxBlockEntity | Skrzynka baterii - przechowywanie energii |
| `auto_crafter` | AutoCrafterBlockEntity | Automatyczny crafter |
| `charging_bench` | ChargingBenchBlockEntity | Stół ładowania baterii |
| `fire_starter` | FireStarterBlockEntity | Zapalniczka |
| `frame` | - | Blok ramki (bez BlockEntity) |
| `frame_motor` | FrameMotorBlockEntity | Silnik ramek |
| `frame_actuator` | FrameActuatorBlockEntity | Aktuator ramek |
| `transposer` | TransposerBlockEntity | Transposer - przenosi itemy |
| `block_breaker` | BlockBreakerBlockEntity | Łamacz bloków |
| `deployer` | DeployerBlockEntity | Deployer - używa itemów jak gracz |

### Przykład: BatteryBoxBlockEntity

**Plik:** `expansion/tile/BatteryBoxBlockEntity.java`

```java
public class BatteryBoxBlockEntity extends LowLoadPoweredBlockEntity {
    private final SimpleContainer inventory = new SimpleContainer(2);

    @Override
    public void saveAdditional(CompoundTag tag) {
        super.saveAdditional(tag);
        tag.put("inventory", inventory.createTag());
    }

    @Override
    public void load(CompoundTag tag) {
        super.load(tag);
        inventory.fromTag(tag.getList("inventory", Tag.TAG_COMPOUND));
    }
}
```

---

## Exploration - Bloki

### Rudy (Ores)

| Block ID | Opis |
|----------|------|
| `ruby_ore` | Ruda rubinu |
| `deepslate_ruby_ore` | Ruda rubinu (deepslate) |
| `sapphire_ore` | Ruda szafiru |
| `deepslate_sapphire_ore` | Ruda szafiru (deepslate) |
| `peridot_ore` | Ruda perydotu |
| `deepslate_peridot_ore` | Ruda perydotu (deepslate) |
| `tin_ore` | Ruda cyny |
| `deepslate_tin_ore` | Ruda cyny (deepslate) |
| `silver_ore` | Ruda srebra |
| `deepslate_silver_ore` | Ruda srebra (deepslate) |
| `electrotine_ore` | Ruda electrotine |
| `deepslate_electrotine_ore` | Ruda electrotine (deepslate) |

### Bloki dekoracyjne

| Block ID | Opis |
|----------|------|
| `marble` | Marmur |
| `marble_brick` | Cegła marmurowa |
| `basalt` | Bazalt |
| `basalt_cobble` | Bruk bazaltowy |
| `basalt_brick` | Cegła bazaltowa |
| `ruby_block` | Blok rubinu |
| `sapphire_block` | Blok szafiru |
| `peridot_block` | Blok perydotu |
| `electrotine_block` | Blok electrotine |
| `raw_tin_block` | Surowy blok cyny |
| `raw_silver_block` | Surowy blok srebra |
| `tin_block` | Blok cyny |
| `silver_block` | Blok srebra |

### Mury (Walls)

| Block ID |
|----------|
| `marble_wall` |
| `marble_brick_wall` |
| `basalt_wall` |
| `basalt_cobble_wall` |
| `basalt_brick_wall` |
| `ruby_block_wall` |
| `sapphire_block_wall` |
| `peridot_block_wall` |
| `electrotine_block_wall` |

---

## Fabrication - Bloki i BlockEntity

| Block ID | BlockEntity | Opis |
|----------|-------------|------|
| `ic_workbench` | ICWorkbenchBlockEntity | Stół roboczy IC - projektowanie układów |
| `plotting_table` | PlottingTableBlockEntity | Stół plotowania - NOWY |
| `lithography_table` | LithographyTableBlockEntity | Stół litografii - NOWY |
| `packaging_table` | PackagingTableBlockEntity | Stół pakowania - NOWY |

**UWAGA:** W wersji 1.18.2+ proces fabrykacji IC został podzielony na więcej etapów z dedykowanymi stołami.

---

## Illumination - Bloki i BlockEntity

### illumar_smart_lamp

**BlockEntity:** `IllumarSmartLampBlockEntity`

**Funkcjonalność:**
- Inteligentna lampa reagująca na redstone
- 16 kolorów

### BlockLightType (enum)

Różne typy lamp zarejestrowane dynamicznie przez `BlockLightType.registerBlocks()`:
- Lantern
- Fixture
- Fallout Light
- Cage Light
- (i inne)

---

## Źródła

- **Oficjalne repo:** https://github.com/MrTJP/ProjectRed
- **Branch 1.18.x:** https://github.com/MrTJP/ProjectRed/tree/1.18.x
