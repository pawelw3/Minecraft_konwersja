# Handoff: Zadanie 1 - IndustrialCraft 2 (Inwentaryzacja bloków i Tile Entities)

## Podsumowanie sesji

Wykonano kompletną inwentaryzację moda **IndustrialCraft 2 Experimental 2.2.827** dla Minecraft 1.7.10. Zdekompilowano kod źródłowy z JARa (`industrialcraft-2-2.2.827-experimental.jar`) przy użyciu Vineflower i przeanalizowano wszystkie klasy bloków oraz Tile Entities. Wyniki zapisano w module `src/converters/ic2/mappings/block_inventory.py`.

---

## 1. Informacje ogólne o IC2

### 1.1 IC2 1.7.10
- **Wersja**: 2.2.827-experimental
- **Lokalizacja źródeł**: `modpack_1710/industrialcraft-2-2.2.827-experimental.jar`
- **Kod źródłowy**: zdekompilowany do `/tmp/ic2_decomp` (vineflower)

### 1.2 Docelowe mody 1.18.2
- **Mekanism 10.2.5** — maszyny przetwórcze, kable uniwersalne, magazyny energii
- **Thermal Series 9.2.2** — maszyny, energy cells, ducts
- **Bigger Reactors** — potencjalny zamiennik reaktora jądrowego (do rozstrzygnięcia)

### 1.3 Kluczowa reguła konwersji
- **1 EU → 4 FE (Forge Energy)** — stała reguła dla całego moda

---

## 2. Kategorie bloków IC2

| Kategoria | Liczba bloków | Liczba wariantów (meta) | Uwagi |
|-----------|---------------|------------------------|-------|
| Maszyny (BlockMachine 1/2/3) | 3 block ID | 40 wariantów | Większość ma TileEntityStandardMachine |
| Generatory (BlockGenerator) | 1 block ID | 10 wariantów | TileEntityBaseGenerator i pochodne |
| Generatory ciepła (BlockHeatGenerator) | 1 block ID | 4 warianty | System cieplny IC2 |
| Generatory kinetyczne (BlockKineticGenerator) | 1 block ID | 6 wariantów | Kinetic → EU / EU → Kinetic |
| Kable (BlockCable) | 1 block ID | 14 wariantów | TileEntityCable z NBT |
| Magazyny energii (BlockElectric) | 1 block ID | 8 wariantów | BatBox/MFE/MFSU/CESU + transformatory |
| Chargepady (BlockChargepad) | 1 block ID | 4 warianty | Ładowanie ekwipunku gracza |
| Reaktor | 5 block ID | 5 wariantów | Chamber, Hatch, Port, RedstonePort, Vessel |
| Personalne | 1 block ID | 3 warianty | Safe, Trade-O-Mat, Energy-O-Mat |
| Rudy/Zasoby | 10 block ID | 10 wariantów | Brak TE |
| Dekoracyjne | 10+ block ID | 15+ wariantów | Brak TE |
| Płyny | 11 block ID | 11 wariantów | FluidRegistry bloki |
| Inne specjalne | 10+ block ID | 10+ wariantów | Luminatory, Mining Pipe, TNT, Beczka |

**Razem**: 57+ rejestracji bloków, **85 różnych klas Tile Entity**.

---

## 3. Szczegółowa lista maszyn (BlockMachine)

### BlockMachine (IC2:blockMachine) — meta 0-15

| Meta | Nazwa | TE Class | Funkcja |
|------|-------|----------|---------|
| 0 | Machine Block | — | Blok konstrukcyjny |
| 1 | Iron Furnace | TileEntityIronFurnace | Piec paliwowy |
| 2 | Electric Furnace | TileEntityElectricFurnace | Piec elektryczny |
| 3 | Macerator | TileEntityMacerator | Kruszenie rud |
| 4 | Extractor | TileEntityExtractor | Wydobywanie surowców |
| 5 | Compressor | TileEntityCompressor | Kompresowanie |
| 6 | Canning Machine | TileEntityCanner | Napełnianie puszek |
| 7 | Miner | TileEntityMiner | Automatyczny górnik |
| 8 | Pump | TileEntityPump | Pompa płynów |
| 9 | Magnetizer | TileEntityMagnetizer | Magnetyzowanie płotów |
| 10 | Electrolyzer | TileEntityElectrolyzer | Elektroliza |
| 11 | Recycler | TileEntityRecycler | Recykling → Scrap |
| 12 | Advanced Machine Block | — | Blok konstrukcyjny (adv) |
| 13 | Induction Furnace | TileEntityInduction | Piec indukcyjny (ciepło) |
| 14 | Mass Fabricator | TileEntityMatter | Produkcja UU-Matter |
| 15 | Terraformer | TileEntityTerra | Zmiana biomów |

### BlockMachine2 (IC2:blockMachine2) — meta 0-15

| Meta | Nazwa | TE Class | Funkcja |
|------|-------|----------|---------|
| 0 | Teleporter | TileEntityTeleporter | Teleportacja |
| 1 | Tesla Coil | TileEntityTesla | Porażenie mobów |
| 2 | Crop-Matron | TileEntityCropmatron | Automatyczne uprawy |
| 3 | Thermal Centrifuge | TileEntityCentrifuge | Wirówka termiczna |
| 4 | Metal Former | TileEntityMetalFormer | Formowanie metali |
| 5 | Ore Washing Plant | TileEntityOreWashing | Mycie rud |
| 6 | Pattern Storage | TileEntityPatternStorage | Magazyn wzorów |
| 7 | Scanner | TileEntityScanner | Skanowanie itemów |
| 8 | Replicator | TileEntityReplicator | Replikacja itemów |
| 9 | Solid Canner | TileEntitySolidCanner | Napełnianie stałymi |
| 10 | Fluid Bottler | TileEntityFluidBottler | Nalewanie płynów |
| 11 | Advanced Miner | TileEntityAdvMiner | Zaawansowany górnik |
| 12 | Liquid Heat Exchanger | TileEntityLiquidHeatExchanger | Wymiana ciepła |
| 13 | Fermenter | TileEntityFermenter | Fermentacja biomasy |
| 14 | Fluid Regulator | TileEntityFluidRegulator | Regulacja przepływu |
| 15 | Condenser | TileEntityCondenser | Kondensacja pary |

### BlockMachine3 (IC2:blockMachine3) — meta 0-8

| Meta | Nazwa | TE Class | Funkcja |
|------|-------|----------|---------|
| 0 | Steam Generator | TileEntitySteamGenerator | Produkcja pary |
| 1 | Blast Furnace | TileEntityBlastFurnace | Wytapianie stali |
| 2 | Block Cutting Machine | TileEntityBlockCutter | Cięcie bloków |
| 3 | Solar Distiller | TileEntitySolarDestiller | Destylacja słoneczna |
| 4 | Fluid Distributor | TileEntityFluidDistributor | Rozdział płynów |
| 5 | Sorting Machine | TileEntitySortingMachine | Sortowanie itemów |
| 6 | Item Buffer | TileEntityItemBuffer | Buforowanie itemów |
| 7 | Crop Harvester | TileEntityCropHavester | Zbiór upraw |
| 8 | Lathe | TileEntityLathe | Tokarka |

---

## 4. Generatory energii

### BlockGenerator (IC2:blockGenerator) — meta 0-9

| Meta | Nazwa | TE Class | Typ |
|------|-------|----------|-----|
| 0 | Generator | TileEntityGenerator | Spalanie stałe |
| 1 | Geothermal Generator | TileEntityGeoGenerator | Lawa |
| 2 | Water Mill | TileEntityWaterGenerator | Woda |
| 3 | Solar Panel | TileEntitySolarGenerator | Słońce |
| 4 | Wind Mill | TileEntityWindGenerator | Wiatr |
| 5 | **Nuclear Reactor** | **TileEntityNuclearReactorElectric** | **Reaktor jądrowy** |
| 6 | RT Generator | TileEntityRTGenerator | Izotopy |
| 7 | Semifluid Generator | TileEntitySemifluidGenerator | Płyny |
| 8 | Stirling Generator | TileEntityStirlingGenerator | Ciepło |
| 9 | Kinetic Generator | TileEntityKineticGenerator | Kinetyczna |

### BlockHeatGenerator (IC2:blockHeatGenerator) — meta 0-3

| Meta | Nazwa | TE Class |
|------|-------|----------|
| 0 | Electric Heat Generator | TileEntityElectricHeatGenerator |
| 1 | Fluid Heat Generator | TileEntityFluidHeatGenerator |
| 2 | RT Heat Generator | TileEntityRTHeatGenerator |
| 3 | Solid Heat Generator | TileEntitySolidHeatGenerator |

### BlockKineticGenerator (IC2:blockKineticGenerator) — meta 0-5

| Meta | Nazwa | TE Class |
|------|-------|----------|
| 0 | Electric Kinetic Generator | TileEntityElectricKineticGenerator |
| 1 | Manual Kinetic Generator | TileEntityManualKineticGenerator |
| 2 | Steam Kinetic Generator | TileEntitySteamKineticGenerator |
| 3 | Stirling Kinetic Generator | TileEntityStirlingKineticGenerator |
| 4 | Water Kinetic Generator | TileEntityWaterKineticGenerator |
| 5 | Wind Kinetic Generator | TileEntityWindKineticGenerator |

---

## 5. Kable i okablowanie

### BlockCable (IC2:blockCable) — meta 0-13

| Meta | Nazwa | TE Class | Tier | Uwagi |
|------|-------|----------|------|-------|
| 0 | Insulated Copper Cable | TileEntityCable | LV (32 EU/t) | |
| 1 | Copper Cable | TileEntityCable | LV (32 EU/t) | Nieizolowany, porażenie |
| 2 | Gold Cable | TileEntityCable | MV (128 EU/t) | Nieizolowany, porażenie |
| 3 | Insulated Gold Cable | TileEntityCable | MV (128 EU/t) | |
| 4 | Double Insulated Gold Cable | TileEntityCable | MV (128 EU/t) | |
| 5 | Iron Cable (HV) | TileEntityCable | HV (2048 EU/t) | Nieizolowany, porażenie |
| 6 | Insulated Iron Cable | TileEntityCable | HV (2048 EU/t) | |
| 7 | Double Insulated Iron Cable | TileEntityCable | HV (2048 EU/t) | |
| 8 | Triple Insulated Iron Cable | TileEntityCable | HV (2048 EU/t) | |
| 9 | Glass Fibre Cable | TileEntityCable | EV (8192 EU/t) | Bez strat |
| 10 | Tin Cable | TileEntityCable | ULV (5 EU/t) | |
| 11 | Detector Cable | TileEntityCableDetector | MV | Sygnał redstone |
| 12 | Splitter Cable | TileEntityCableSplitter | MV | Przełączalny |
| 13 | Insulated Tin Cable | TileEntityCable | ULV (5 EU/t) | |

**Kluczowe NBT dla kabli**:
- `cableType` (short) — typ kabla
- `color` (short) — kolor izolacji (0=brak, 1-16=barwniki)
- `foamed` (byte) — 0=normal, 1=piana, 2=ścianka
- `foamColor` (byte) — kolor piany
- `retextureRef*` — dane retextur (opcjonalne)

---

## 6. Magazyny energii i transformatory

### BlockElectric (IC2:blockElectric) — meta 0-7

| Meta | Nazwa | TE Class | Pojemność EU | Tier |
|------|-------|----------|-------------|------|
| 0 | BatBox | TileEntityElectricBatBox | 40 000 | LV |
| 1 | MFE | TileEntityElectricMFE | 4 000 000 | HV |
| 2 | MFSU | TileEntityElectricMFSU | 40 000 000 | EV |
| 3 | LV Transformer | TileEntityTransformerLV | — | LV |
| 4 | MV Transformer | TileEntityTransformerMV | — | MV |
| 5 | HV Transformer | TileEntityTransformerHV | — | HV |
| 6 | EV Transformer | TileEntityTransformerEV | — | EV |
| 7 | CESU | TileEntityElectricCESU | 300 000 | MV |

### BlockChargepad (IC2:blockChargepad) — meta 0-3

| Meta | Nazwa | TE Class | Pojemność EU |
|------|-------|----------|-------------|
| 0 | BatBox Chargepad | TileEntityChargepadBatBox | 40 000 |
| 1 | CESU Chargepad | TileEntityChargepadCESU | 300 000 |
| 2 | MFE Chargepad | TileEntityChargepadMFE | 4 000 000 |
| 3 | MFSU Chargepad | TileEntityChargepadMFSU | 40 000 000 |

**Kluczowe NBT dla storage**:
- `energy` (double) — aktualna energia
- `redstoneMode` (byte) — zachowanie przy redstone
- `active` (boolean) — stan aktywności

---

## 7. Reaktor jądrowy

| Block ID | Nazwa | TE Class | Funkcja |
|----------|-------|----------|---------|
| IC2:blockReactorChamber | Reactor Chamber | TileEntityReactorChamberElectric | Komora (+1 slot) |
| IC2:blockReactorFluidPort | Reactor Fluid Port | TileEntityReactorFluidPort | Port płynów |
| IC2:blockReactorAccessHatch | Reactor Access Hatch | TileEntityReactorAccessHatch | Właz (inventory) |
| IC2:blockReactorRedstonePort | Reactor Redstone Port | TileEntityReactorRedstonePort | Port redstone |
| IC2:blockreactorvessel | Reactor Pressure Vessel | — | Blok ścianki |

**Uwaga**: Główny reaktor to meta=5 w `blockGenerator` (`TileEntityNuclearReactorElectric`).

**Kluczowe NBT reaktora**:
- `heat` (int) — temperatura reaktora
- `energy` (double) — wyprodukowana energia
- `output` (double) — aktualny output
- `Items` / `InvSlots` — inventory komponentów (6×9=54 sloty!)

---

## 8. Bloki personalne

| Block ID | Meta | Nazwa | TE Class |
|----------|------|-------|----------|
| IC2:blockPersonal | 0 | Personal Safe | TileEntityPersonalChest |
| IC2:blockPersonal | 1 | Trade-O-Mat | TileEntityTradeOMat |
| IC2:blockPersonal | 2 | Energy-O-Mat | TileEntityEnergyOMat |

---

## 9. Struktury NBT — kluczowe pola

### TileEntityBlock (bazowa dla wszystkich TE IC2)
- `facing` (short) — orientacja (0-5: down, up, north, south, west, east)
- `active` (boolean) — czy maszyna jest aktywna
- `components` (NBTTagCompound) — komponenty dodatkowe (opcjonalne)

### TileEntityInventory (bazowa dla TE z inventory)
- `Items` (NBTTagList) — stary format inventory (1.7.10 compat)
- `InvSlots` (NBTTagCompound) — nowy format z nazwanymi slotami
  - Każdy `InvSlot` ma swoje NBT z `ItemStack`

### TileEntityStandardMachine (maszyny przetwórcze)
- Dziedziczy z TileEntityElectricMachine → TileEntityInventory → TileEntityBlock
- `progress` (short) — postęp procesu (0-400 typowo)
- `energy` (double) — energia w buforze
- Sloty: `input`, `output`, `discharge`, `charge`, `upgrade`

### TileEntityElectricBlock (storage, chargepady)
- Dziedziczy z TileEntityBlock (bez inventory lub z minimalnym)
- `energy` (double) — aktualna energia
- `redstoneMode` (byte) — tryb redstone
- `active` (boolean)

---

## 10. Utworzone pliki

- `src/converters/ic2/mappings/__init__.py` — inicjalizacja modułu
- `src/converters/ic2/mappings/block_inventory.py` — pełna inwentaryzacja bloków/TE (57 block ID, 85 TE classes)

---

## 11. Następne kroki (Zadanie 2)

1. **Przygotować symulacje funkcjonalności** w Pythonie dla:
   - Procesu przetwórczego (StandardMachine)
   - Sieci EU (Cable, EnergyNet)
   - Reaktora jądrowego (heat balance, komponenty)
   - Storage energii (BatBox/MFE/MFSU)

2. **Zbadać kody źródłowe Mekanism/Thermal 1.18.2** — jakie są odpowiedniki maszyn i jak wyglądają ich NBT

3. **Przygotować tabelę mapowań** `block_mappings.py` z konkretnymi mapowaniami:
   - `IC2:blockMachine:3` → `mekanism:crusher`
   - `IC2:blockMachine:2` → `mekanism:energized_smelter`
   - `IC2:blockGenerator:0` → `mekanism:heat_generator`
   - `IC2:blockCable:0` → `mekanism:basic_universal_cable`
   - `IC2:blockElectric:0` → `mekanism:basic_energy_cube`

---

*Dokument utworzony: 2026-05-19*
*Źródła: Dekompilacja IC2 2.2.827 (vineflower), dokumentacja projektu*
