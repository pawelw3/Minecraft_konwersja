# ProjectRed - Porównanie 1.7.10 vs 1.18.2+

> **Data analizy:** 2026-02-02

---

## Podsumowanie zmian

### Główne zmiany architektoniczne

1. **Język programowania:** Scala (1.7.10) → Java (1.18.2+)
2. **System metadanych:** Bloki z metadatą → Osobne bloki dla każdego wariantu
3. **Rejestracja:** `GameRegistry.registerBlock()` → `DeferredRegister`
4. **TileEntity → BlockEntity:** Zmiana nazewnictwa zgodna z Minecraft 1.17+
5. **Deepslate variants:** Dodane warianty deepslate dla wszystkich rud

---

## Mapowanie bloków Expansion

### machine1 (1.7.10) → osobne bloki (1.18.2+)

| 1.7.10 (meta) | 1.18.2+ Block ID | Status |
|---------------|------------------|--------|
| `machine1:0` (TileInductiveFurnace) | - | **USUNIĘTY** (funkcja w Electrotine Generator?) |
| `machine1:1` (TileElectrotineGenerator) | `projectred_core:electrotine_generator` | Przeniesiony do Core |

### machine2 (1.7.10) → osobne bloki (1.18.2+)

| 1.7.10 (meta) | 1.18.2+ Block ID | Status |
|---------------|------------------|--------|
| `machine2:0` (TileBlockBreaker) | `projectred_expansion:block_breaker` | OK |
| `machine2:1` (TileItemImporter) | - | **USUNIĘTY** |
| `machine2:2` (TileBlockPlacer) | - | **USUNIĘTY** (zastąpiony przez Deployer?) |
| `machine2:3` (TileFilteredImporter) | - | **USUNIĘTY** |
| `machine2:4` (TileFireStarter) | `projectred_expansion:fire_starter` | OK |
| `machine2:5` (TileBatteryBox) | `projectred_expansion:battery_box` | OK |
| `machine2:6` (TileChargingBench) | `projectred_expansion:charging_bench` | OK |
| `machine2:7` (TileTeleposer) | - | **USUNIĘTY** |
| `machine2:8` (TileFrameMotor) | `projectred_expansion:frame_motor` | OK |
| `machine2:9` (TileFrameActuator) | `projectred_expansion:frame_actuator` | OK |
| `machine2:10` (TileProjectBench) | `projectred_expansion:project_bench` | OK |
| `machine2:11` (TileAutoCrafter) | `projectred_expansion:auto_crafter` | OK |
| `machine2:12` (TileDiamondBlockBreaker) | - | **USUNIĘTY** |

### Nowe bloki w 1.18.2+

| Block ID | Opis |
|----------|------|
| `projectred_expansion:transposer` | Transposer - przenosi itemy |
| `projectred_expansion:deployer` | Deployer - używa itemów jak gracz |
| `projectred_expansion:frame` | Blok ramki (bez BlockEntity) |

---

## Mapowanie bloków Exploration

### Rudy (1.7.10 ore block z meta → 1.18.2+ osobne bloki)

| 1.7.10 (meta) | 1.18.2+ Block ID | Deepslate variant |
|---------------|------------------|-------------------|
| `ore:0` (Ruby) | `projectred_exploration:ruby_ore` | `deepslate_ruby_ore` |
| `ore:1` (Sapphire) | `projectred_exploration:sapphire_ore` | `deepslate_sapphire_ore` |
| `ore:2` (Peridot) | `projectred_exploration:peridot_ore` | `deepslate_peridot_ore` |
| `ore:3` (Copper) | - | **USUNIĘTY** (vanilla copper?) |
| `ore:4` (Tin) | `projectred_exploration:tin_ore` | `deepslate_tin_ore` |
| `ore:5` (Silver) | `projectred_exploration:silver_ore` | `deepslate_silver_ore` |
| `ore:6` (Electrotine) | `projectred_exploration:electrotine_ore` | `deepslate_electrotine_ore` |

### Bloki dekoracyjne (1.7.10 stone block z meta → 1.18.2+ osobne bloki)

| 1.7.10 (meta) | 1.18.2+ Block ID |
|---------------|------------------|
| `stone:0` (Marble) | `projectred_exploration:marble` |
| `stone:1` (Marble Brick) | `projectred_exploration:marble_brick` |
| `stone:2` (Basalt) | `projectred_exploration:basalt` |
| `stone:3` (Basalt Cobble) | `projectred_exploration:basalt_cobble` |
| `stone:4` (Basalt Brick) | `projectred_exploration:basalt_brick` |
| `stone:5` (Ruby Block) | `projectred_exploration:ruby_block` |
| `stone:6` (Sapphire Block) | `projectred_exploration:sapphire_block` |
| `stone:7` (Peridot Block) | `projectred_exploration:peridot_block` |
| `stone:8` (Copper Block) | - | **USUNIĘTY** (vanilla copper block?) |
| `stone:9` (Tin Block) | `projectred_exploration:tin_block` |
| `stone:10` (Silver Block) | `projectred_exploration:silver_block` |
| `stone:11` (Electrotine Block) | `projectred_exploration:electrotine_block` |

### Nowe bloki w 1.18.2+

| Block ID | Opis |
|----------|------|
| `raw_tin_block` | Surowy blok cyny |
| `raw_silver_block` | Surowy blok srebra |

### Usunięte z 1.7.10

| Element | Status |
|---------|--------|
| BlockLily / TileLily | **USUNIĘTY** |
| BlockBarrel / TileBarrel | **USUNIĘTY** |

---

## Mapowanie bloków Fabrication

| 1.7.10 (meta) | 1.18.2+ Block ID | Status |
|---------------|------------------|--------|
| `icBlock:0` (TileICWorkbench) | `projectred_fabrication:ic_workbench` | OK |
| `icBlock:1` (TileICPrinter) | - | **ZASTĄPIONY** przez nowe stoły |

### Nowe bloki w 1.18.2+

| Block ID | Opis |
|----------|------|
| `plotting_table` | Stół plotowania |
| `lithography_table` | Stół litografii |
| `packaging_table` | Stół pakowania |

---

## Mapowanie bloków Illumination

| 1.7.10 | 1.18.2+ | Status |
|--------|---------|--------|
| BlockLamp / TileLamp | BlockLightType (dynamic) | Zmieniona struktura |
| BlockAirousLight / TileAirousLight | - | Prawdopodobnie internal |
| - | `illumar_smart_lamp` | **NOWY** |

---

## Mapowanie Multipart (Integration/Transmission)

Bramki i przewody pozostają jako multipart (CBMultipart → ForgeMultipart).
Typy części powinny być kompatybilne, ale wymagają weryfikacji:

| 1.7.10 Part | 1.18.2+ Part | Status |
|-------------|--------------|--------|
| `pr_sgate` | `pr_sgate` | Prawdopodobnie OK |
| `pr_igate` | `pr_igate` | Prawdopodobnie OK |
| `pr_agate` | `pr_agate` | Prawdopodobnie OK |
| `pr_bgate` | `pr_bgate` | Prawdopodobnie OK |
| `pr_redwire` | `pr_redwire` | Prawdopodobnie OK |
| `pr_insulated` | `pr_insulated` | Prawdopodobnie OK |
| `pr_bundled` | `pr_bundled` | Prawdopodobnie OK |

---

## Zmiany w danych NBT

### Główne zmiany

1. **Orientacja:**
   - 1.7.10: `rot` (Byte) - kombinacja side + rotation
   - 1.18.2+: Prawdopodobnie BlockState properties

2. **Inwentarz:**
   - 1.7.10: Custom save/load z `saveInv(tag)`, `loadInv(tag)`
   - 1.18.2+: `inventory.createTag()`, `inventory.fromTag()`

3. **Energia:**
   - 1.7.10: `cond.save(tag)` - PowerConductor
   - 1.18.2+: Prawdopodobnie podobna struktura (charge, flow)

---

## Rekomendacje dla konwersji

### Priorytet 1: Bezpośrednie mapowanie

Te bloki mają bezpośrednie odpowiedniki:
- BatteryBox
- ChargingBench
- ProjectBench
- AutoCrafter
- FireStarter
- FrameMotor
- FrameActuator
- BlockBreaker
- Rudy (z konwersją meta → block ID)
- Bloki dekoracyjne

### Priorytet 2: Zastąpienie funkcjonalności

| 1.7.10 | Sugerowany zamiennik 1.18.2+ |
|--------|------------------------------|
| TileInductiveFurnace | ElectrotineGenerator + vanilla furnace? |
| TileItemImporter | Pipez / XNet |
| TileBlockPlacer | Deployer |
| TileFilteredImporter | Pipez z filtrami |
| TileTeleposer | ? (może Create?) |
| TileDiamondBlockBreaker | BlockBreaker |

### Priorytet 3: Utrata funkcjonalności

| 1.7.10 | Status |
|--------|--------|
| BlockLily | Brak odpowiednika - konwersja na vanilla flowers? |
| BlockBarrel | Brak odpowiednika - Storage Drawers / Iron Barrels? |
| TileICPrinter | Zastąpiony przez nowy system fabrykacji |

---

## Wymagane dalsze badania

1. **Multipart compatibility** - Czy dane NBT bramek/przewodów są kompatybilne?
2. **BlockLightType** - Dokładne mapowanie typów lamp
3. **Transportation** - Status modułu rur w 1.18.2+
4. **System energii** - Czy PowerConductor jest kompatybilny?
