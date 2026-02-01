# Applied Energistics 2 (AE2) - Pełna lista bloków i Tile Entities

> **Dokumentacja konwersji AE2: 1.7.10 → 1.18.2**  
> **Zadanie 1:** Wypisanie wszystkich bloków i Tile Entities  
> **Data utworzenia:** 2026-02-01  
> **Status:** ✅ Ukończono

---

## Spis treści

1. [Architektura AE2 - przegląd](#1-architektura-ae2---przegląd)
2. [Bloki i Tile Entities - mapowanie 1.7.10 → 1.18.2](#2-bloki-i-tile-entities---mapowanie-1710--1182)
3. [Szczegółowy opis funkcjonalności](#3-szczegółowy-opis-funkcjonalności)
4. [Struktura NBT - kluczowe różnice](#4-struktura-nbt---kluczowe-różnice)
5. [Elementy "part" (części kablowe)](#5-elementy-part-części-kablowe)
6. [Itemy i komponenty](#6-itemy-i-komponenty)

---

## 1. Architektura AE2 - przegląd

### Core Concepts (1.7.10 i 1.18.2)

| Koncepcja | Opis |
|-----------|------|
| **ME Network** | Sieć energetyczna i logistyczna oparta na kanałach (channels) |
| **Channel** | Logiczna "ścieżka" umożliwiająca komunikację między urządzeniami (max 8 per kabel zwykły, 32 dense) |
| **AE Energy** | Energia sieci - w 1.7.10: AE, w 1.18.2: kompatybilność z Forge Energy (FE) |
| **Storage Cell** | Komórki przechowujące itemy/fluidy (1k, 4k, 16k, 64k, 256k w 1.18.2) |
| **Autocrafting** | System automatycznego craftingu z wykorzystaniem Pattern i Crafting CPU |
| **P2P Tunnel** | Tunel Point-to-Point do przesyłania ME/channel/energy/item/fluid/redstone |
| **Spatial Storage** | Magazynowanie przestrzeni 3D (bloki w komórkach) |

---

## 2. Bloki i Tile Entities - mapowanie 1.7.10 → 1.18.2

### 2.1 Core Network Blocks

| Blok 1.7.10 | ID 1.7.10 | Blok 1.18.2 | ID 1.18.2 | Tile Entity | Opis |
|-------------|-----------|-------------|-----------|-------------|------|
| ME Controller | `appliedenergistics2:tile.BlockController` | ME Controller | `ae2:controller` | ✅ | Serce sieci - generuje kanały |
| ME Drive | `appliedenergistics2:tile.BlockDrive` | ME Drive | `ae2:drive` | ✅ | Przechowuje Storage Cells |
| ME Chest | `appliedenergistics2:tile.BlockChest` | ME Chest | `ae2:chest` | ✅ | Skrzynia + storage cell w jednym |
| Energy Acceptor | `appliedenergistics2:tile.BlockEnergyAcceptor` | Energy Acceptor | `ae2:energy_acceptor` | ✅ | Konwertuje energię zewnętrzną na AE |
| Energy Cell | `appliedenergistics2:tile.BlockEnergyCell` | Energy Cell | `ae2:energy_cell` | ✅ | Magazyn energii (podstawowy) |
| Dense Energy Cell | `appliedenergistics2:tile.BlockDenseEnergyCell` | Dense Energy Cell | `ae2:dense_energy_cell` | ✅ | Magazyn energii (gęsty) |
| Creative Energy Cell | - | Creative Energy Cell | `ae2:creative_energy_cell` | ✅ | Nieskończona energia (creative) |

### 2.2 Crafting System Blocks

| Blok 1.7.10 | ID 1.7.10 | Blok 1.18.2 | ID 1.18.2 | Tile Entity | Opis |
|-------------|-----------|-------------|-----------|-------------|------|
| Crafting Unit | `appliedenergistics2:tile.BlockCraftingUnit` | Crafting Unit | `ae2:crafting_unit` | ✅ | Podstawowa jednostka crafting CPU |
| Crafting Co-Processing Unit | `appliedenergistics2:tile.BlockCraftingUnit:1` | Crafting Accelerator | `ae2:crafting_accelerator` | ✅ | Przyspiesza crafting (równoległość) |
| Crafting Storage 1k | `appliedenergistics2:tile.BlockCraftingStorage` | Crafting Unit 1k | `ae2:crafting_unit_1k` | ✅ | CPU + pamięć 1k |
| Crafting Storage 4k | `appliedenergistics2:tile.BlockCraftingStorage:1` | Crafting Unit 4k | `ae2:crafting_unit_4k` | ✅ | CPU + pamięć 4k |
| Crafting Storage 16k | `appliedenergistics2:tile.BlockCraftingStorage:2` | Crafting Unit 16k | `ae2:crafting_unit_16k` | ✅ | CPU + pamięć 16k |
| Crafting Storage 64k | `appliedenergistics2:tile.BlockCraftingStorage:3` | Crafting Unit 64k | `ae2:crafting_unit_64k` | ✅ | CPU + pamięć 64k |
| Crafting Monitor | `appliedenergistics2:tile.BlockCraftingMonitor` | Crafting Monitor | `ae2:crafting_monitor` | ✅ | Wyświetla postęp craftingu |
| Molecular Assembler | `appliedenergistics2:tile.BlockMolecularAssembler` | Molecular Assembler | `ae2:molecular_assembler` | ✅ | Wykonuje receptury craftingowe |
| Pattern Provider (blok) | NIE MA | Pattern Provider | `ae2:pattern_provider` | ✅ | NOWOŚĆ w 1.18.2 - dostarcza pattern do assemblera |

### 2.3 Interface and IO Blocks

| Blok 1.7.10 | ID 1.7.10 | Blok 1.18.2 | ID 1.18.2 | Tile Entity | Opis |
|-------------|-----------|-------------|-----------|-------------|------|
| ME Interface | `appliedenergistics2:tile.BlockInterface` | Interface | `ae2:interface` | ✅ | Interfejs do wymiany itemów z zewnątrz |
| ME IO Port | `appliedenergistics2:tile.BlockIOPort` | IO Port | `ae2:io_port` | ✅ | Transfer między storage cells |
| Pattern Provider | część Interface | Pattern Provider | `ae2:pattern_provider` | ✅ | NOWOŚĆ - dostarcza patterny |

### 2.4 Quantum Network Blocks

| Blok 1.7.10 | ID 1.7.10 | Blok 1.18.2 | ID 1.18.2 | Tile Entity | Opis |
|-------------|-----------|-------------|-----------|-------------|------|
| Quantum Ring | `appliedenergistics2:tile.BlockQuantumRing` | Quantum Ring | `ae2:quantum_ring` | ✅ | Część multibloku quantum bridge |
| Quantum Link Chamber | `appliedenergistics2:tile.BlockQuantumLinkChamber` | Quantum Link Chamber | `ae2:quantum_link` | ✅ | Rdzeń quantum bridge |

### 2.5 Spatial IO Blocks

| Blok 1.7.10 | ID 1.7.10 | Blok 1.18.2 | ID 1.18.2 | Tile Entity | Opis |
|-------------|-----------|-------------|-----------|-------------|------|
| Spatial IO Port | `appliedenergistics2:tile.BlockSpatialIOPort` | Spatial IO Port | `ae2:spatial_io_port` | ✅ | Wejście/wyjście spatial storage |
| Spatial Pylon | `appliedenergistics2:tile.BlockSpatialPylon` | Spatial Pylon | `ae2:spatial_pylon` | ✅ | Część ramy spatial storage |
| Matrix Frame | NIE MA | Matrix Frame | `ae2:matrix_frame` | ❌ | Dekoracyjna ramka |
| Spatial Anchor | NIE MA | Spatial Anchor | `ae2:spatial_anchor` | ✅ | NOWOŚĆ - utrzymuje chunki załadowane |

### 2.6 Utility Blocks

| Blok 1.7.10 | ID 1.7.10 | Blok 1.18.2 | ID 1.18.2 | Tile Entity | Opis |
|-------------|-----------|-------------|-----------|-------------|------|
| Charger | `appliedenergistics2:tile.BlockCharger` | Charger | `ae2:charger` | ✅ | Ładuje certus quartz |
| Inscriber | `appliedenergistics2:tile.BlockInscriber` | Inscriber | `ae2:inscriber` | ✅ | Tworzy procesory i printed circuits |
| Vibration Chamber | `appliedenergistics2:tile.BlockVibrationChamber` | Vibration Chamber | `ae2:vibration_chamber` | ✅ | Generator AE z paliwa stałego |
| Crystal Growth Accelerator | `appliedenergistics2:tile.BlockQuartzGrowthAccelerator` | Crystal Growth Accelerator | `ae2:quartz_growth_accelerator` | ✅ | Przyspiesza wzrost kryształów |
| Condenser | `appliedenergistics2:tile.BlockCondenser` | Matter Condenser | `ae2:condenser` | ✅ | Konwertuje itemy na matter balls/energy |
| Cell Workbench | NIE MA | Cell Workbench | `ae2:cell_workbench` | ✅ | Konfiguracja storage cells |
| Crank | `appliedenergistics2:tile.BlockCrank` | Wooden Crank | `ae2:crank` | ✅ | Ręczne zasilanie grindstone |
| Quartz Grindstone | `appliedenergistics2:tile.BlockGrinder` | Quartz Grindstone | `ae2:grindstone` | ✅ | Mielenie ore → dust |
| Sky Stone Chest | `appliedenergistics2:tile.BlockSkyChest` | Sky Stone Chest | `ae2:sky_stone_chest` | ✅ | Skrzynia ze sky stone |
| Smooth Sky Stone Chest | NIE MA | Smooth Sky Stone Chest | `ae2:smooth_sky_stone_chest` | ✅ | Wariant tekstury |
| Sky Stone Tank | NIE MA | Sky Stone Tank | `ae2:sky_stone_tank` | ✅ | Zbiornik na płyny |
| Tiny TNT | `appliedenergistics2:tile.BlockTinyTNT` | Tiny TNT | `ae2:tiny_tnt` | ✅ | Małe TNT (spatial) |
| Light Detector | `appliedenergistics2:tile.BlockLightDetector` | Light Detector | `ae2:light_detector` | ✅ | Detektor światła (redstone) |
| Mysterious Cube | NIE MA | Mysterious Cube | `ae2:mysterious_cube` | ❌ | Dekoracyjny (struktura meteoru) |
| Quartz Fixture | `appliedenergistics2:tile.BlockQuartzFixture` | Quartz Fixture | `ae2:quartz_fixture` | ❌ | Oświetlenie |
| Matrix Frame | NIE MA | Matrix Frame | `ae2:matrix_frame` | ❌ | Dekoracyjna ramka spatial |
| Crystal Resonance Generator | NIE MA | Crystal Resonance Generator | `ae2:crystal_resonance_generator` | ✅ | NOWOŚĆ - generator AE z kryształów |
| Paint Splotches | NIE MA | Paint | `ae2:paint` | ❌ | Znaczniki kolorów (debug) |

### 2.7 Wireless Network Blocks

| Blok 1.7.10 | ID 1.7.10 | Blok 1.18.2 | ID 1.18.2 | Tile Entity | Opis |
|-------------|-----------|-------------|-----------|-------------|------|
| Wireless Access Point | `appliedenergistics2:tile.BlockWireless` | Wireless Access Point | `ae2:wireless_access_point` | ✅ | Punkt dostępowy wireless |
| ME Security Terminal | `appliedenergistics2:tile.BlockSecurity` | Security Station | `ae2:security_station` | ✅ | Kontrola dostępu do sieci |

### 2.8 Cables and Bus Parts

| Element 1.7.10 | ID 1.7.10 | Element 1.18.2 | ID 1.18.2 | Tile Entity | Opis |
|----------------|-----------|----------------|-----------|-------------|------|
| Cable Bus (block) | `appliedenergistics2:tile.BlockCableBus` | Cable Bus | `ae2:cable_bus` | ✅ | Blok zawierający części kablowe |
| Fluix Cable | część block | Fluix Cable | `ae2:fluix_cable` | ❌ | Podstawowy kabel |
| Covered Cable | część block | Covered Cable | `ae2:covered_cable` | ❌ | Kabel w osłonie |
| Smart Cable | część block | Smart Cable | `ae2:smart_cable` | ❌ | Kabel z wyświetlaniem kanałów |
| Dense Cable | część block | Dense Cable | `ae2:dense_cable` | ❌ | Gęsty kabel (32 ch) |
| Covered Dense Cable | część block | Covered Dense Cable | `ae2:covered_dense_cable` | ❌ | Gęsty w osłonie |
| Smart Dense Cable | część block | Smart Dense Cable | `ae2:smart_dense_cable` | ❌ | Gęsty smart |

---

## 3. Szczegółowy opis funkcjonalności

### 3.1 ME Controller

**Funkcja:** Centralny kontroler sieci ME - generuje kanały dla urządzeń.

**1.7.10:**
- ID: `appliedenergistics2:tile.BlockController`
- Tile Entity: `appeng.tile.networking.TileController`
- Max kanały: 32 per strona
- Może tworzyć struktury wieloblokowe (kontrolery połączone = więcej kanałów)

**1.18.2:**
- ID: `ae2:controller`
- Tile Entity: `appeng.blockentity.networking.ControllerBlockEntity`
- Kluczowe NBT: `visual`, `priority`

**Konwersja:** Bezpośrednia - orientacja i stan multibloku zachowany.

---

### 3.2 ME Drive

**Funkcja:** Przechowuje Storage Cells (itemy i fluidy).

**1.7.10:**
- ID: `appliedenergistics2:tile.BlockDrive`
- Tile Entity: `appeng.tile.storage.TileDrive`
- Sloty: 10 komórek
- NBT: `inv`, `priority`, `fuzzyMode`

**1.18.2:**
- ID: `ae2:drive`
- Tile Entity: `appeng.blockentity.storage.DriveBlockEntity`
- Sloty: 10 komórek
- NBT: `items` (zawartość komórek)

**Konwersja:** Kluczowa - zawartość storage cells musi być zachowana.

---

### 3.3 ME Interface

**Funkcja:** Interfejs do automatycznej wymiany itemów z zewnętrznymi systemami.

**1.7.10:**
- ID: `appliedenergistics2:tile.BlockInterface`
- Tile Entity: `appeng.tile.misc.TileInterface`
- Sloty: 9 config, 9 storage
- Funkcja: Pattern provider + item interface

**1.18.2:**
- ID: `ae2:interface`
- Tile Entity: `appeng.blockentity.misc.InterfaceBlockEntity`
- Sloty: 9 config, 9 storage (zwykły), 36 (część na kablu)
- UWAGA: Pattern provider wydzielony jako osobny blok!

**Konwersja:** 
- Interface → Interface (config + storage)
- Pattern functionality → PatternProvider (nowy blok)

---

### 3.4 Pattern Provider (NOWOŚĆ w 1.18.2)

**Funkcja:** Dostarcza patterny do Molecular Assembler lub innych maszyn.

**1.18.2:**
- ID: `ae2:pattern_provider`
- Tile Entity: `appeng.blockentity.crafting.PatternProviderBlockEntity`
- Sloty: 9 patternów
- Modes: blocking/non-blocking

**Konwersja z 1.7.10:**
- Patterny z Interface muszą zostać przeniesione do Pattern Provider

---

### 3.5 Molecular Assembler

**Funkcja:** Wykonuje crafting na podstawie patternów.

**1.7.10:**
- ID: `appliedenergistics2:tile.BlockMolecularAssembler`
- Tile Entity: `appeng.tile.crafting.TileMolecularAssembler`
- Prędkość: podstawowa
- Wsparcie: do 5 patternów

**1.18.2:**
- ID: `ae2:molecular_assembler`
- Tile Entity: `appeng.blockentity.crafting.MolecularAssemblerBlockEntity`
- Prędkość: podstawowa + akceleratory
- Wsparcie: patterny z Pattern Provider

**Konwersja:** Bezpośrednia, ale wymaga Pattern Provider do działania.

---

### 3.6 Crafting Unit / CPU

**Funkcja:** Oblicza crafting (CPU = mózg autocraftingu).

**1.7.10:**
- Crafting Unit (procesor)
- Crafting Co-Processing Unit (przyspieszenie)
- Crafting Storage (1k/4k/16k/64k) - pamięć dla obliczeń

**1.18.2:**
- Crafting Unit (podstawowa)
- Crafting Accelerator (przyspieszenie)
- Crafting Unit 1k/4k/16k/64k (storage)

**Konwersja:** Mapowanie typów 1:1

---

### 3.7 Charger

**Funkcja:** Ładuje Certus Quartz Crystal → Charged Certus Quartz Crystal.

**1.7.10:**
- ID: `appliedenergistics2:tile.BlockCharger`
- Tile Entity: `appeng.tile.misc.TileCharger`
- Zasilanie: AE lub crank

**1.18.2:**
- ID: `ae2:charger`
- Tile Entity: `appeng.blockentity.misc.ChargerBlockEntity`
- Zasilanie: AE

---

### 3.8 Inscriber

**Funkcja:** Tworzy procesory (calculation, engineering, logic) i printed circuits.

**1.7.10:**
- ID: `appliedenergistics2:tile.BlockInscriber`
- Sloty: 3 input, 1 output, 1 side, 1 top
- NBT: `inv`, `sideInv`, `topInv`

**1.18.2:**
- ID: `ae2:inscriber`
- Sloty: 3 input, 1 output
- NBT: `items` (zawartość)

---

### 3.9 Energy Acceptor

**Funkcja:** Konwertuje energię zewnętrzną (RF/TESLA/EU) na AE.

**1.7.10:**
- ID: `appliedenergistics2:tile.BlockEnergyAcceptor`
- Wsparcie: RF, TESLA, EU

**1.18.2:**
- ID: `ae2:energy_acceptor`
- Wsparcie: Forge Energy (FE)

**Konwersja:** Konwersja energii EU→FE (×4)

---

### 3.10 Quantum Ring / Link Chamber

**Funkcja:** Łączy dwie sieci ME przez dowolną odległość.

**1.7.10:**
- Quantum Ring: struktura 3x3 z pustym środkiem
- Quantum Link Chamber: środek struktury
- Wymaga: Quantum Entangled Singularity (para)

**1.18.2:**
- Struktura identyczna
- Zasada działania: bez zmian

**Konwersja:** Zachować strukturę, NBT połączenia do weryfikacji.

---

### 3.11 Spatial IO

**Funkcja:** Magazynuje obszary przestrzeni 3D w Spatial Storage Cell.

**1.7.10:**
- Spatial IO Port: kontroler
- Spatial Pylon: ramka struktury
- Obszar: zależny od rozmiaru ramy

**1.18.2:**
- Identyczna funkcjonalność
- Dodatkowo: Spatial Anchor (nowy)

---

## 4. Struktura NBT - kluczowe różnice

### 4.1 Ogólna struktura Tile Entity

**1.7.10:**
```nbt
{
  "id": "AEBaseTile",
  "x": int,
  "y": int,
  "z": int,
  "ForgeData": {...},
  "customName": string,
  "orientation": {
    "forward": int,
    "up": int
  },
  "inv": [...],  // inventory
  "priority": int
}
```

**1.18.2:**
```nbt
{
  "id": "ae2:drive",  // lub inny typ
  "x": int,
  "y": int,
  "z": int,
  "items": [...],  // serialized inventory
  "visual": {...},
  "upgrades": {...},
  "config": {...}
}
```

### 4.2 NBT - ME Drive

**1.7.10:**
```nbt
{
  "id": "AEBaseTile",
  "inv": [
    {Slot: 0, id: "appliedenergistics2:item.ItemBasicStorageCell.1k", Count: 1, tag: {...}},
    ...
  ],
  "priority": 0
}
```

**1.18.2:**
```nbt
{
  "id": "ae2:drive",
  "items": [
    {Slot: 0, id: "ae2:item_cell_1k", Count: 1, tag: {...}},
    ...
  ]
}
```

### 4.3 NBT - Storage Cell (zawartość)

**1.7.10:**
```nbt
{
  "StorageCell": {
    "items": [...],
    "itemCount": long
  }
}
```

**1.18.2:**
```nbt
{
  "storage": {
    "items": [...],
    "count": long
  }
}
```

---

## 5. Elementy "Part" (części kablowe)

Elementy montowane na kablach - w 1.7.10 jako część Cable Bus, w 1.18.2 jako osobne "part".

### 5.1 Terminals

| Element 1.7.10 | Element 1.18.2 | Opis |
|----------------|----------------|------|
| Terminal | `ae2:terminal` | Podstawowy terminal (itemy) |
| Crafting Terminal | `ae2:crafting_terminal` | Terminal z crafting grid |
| Pattern Terminal | `ae2:pattern_terminal` | Tworzenie patternów |
| Pattern Access Terminal | `ae2:pattern_access_terminal` | Dostęp do patternów |
| Fluid Terminal | `ae2:fluid_terminal` | Zarządzanie fluidami |
| Interface Terminal | `ae2:interface_terminal` | Zarządzanie interface'ami |
| Extended Pattern Access Terminal | `ae2:extended_pattern_access_terminal` | NOWOŚĆ |

### 5.2 Buses (Import/Export/Storage)

| Element 1.7.10 | Element 1.18.2 | Opis |
|----------------|----------------|------|
| Import Bus | `ae2:import_bus` | Wciąga itemy do sieci |
| Export Bus | `ae2:export_bus` | Wypycha itemy z sieci |
| Storage Bus | `ae2:storage_bus` | Podłącza zewnętrzny storage |
| Fluid Import Bus | `ae2:fluid_import_bus` | Wersja dla fluidów |
| Fluid Export Bus | `ae2:fluid_export_bus` | Wersja dla fluidów |
| Fluid Storage Bus | `ae2:fluid_storage_bus` | Wersja dla fluidów |

### 5.3 Inne części

| Element 1.7.10 | Element 1.18.2 | Opis |
|----------------|----------------|------|
| Level Emitter | `ae2:level_emitter` | Emisja redstone przy poziomie |
| Fluid Level Emitter | `ae2:fluid_level_emitter` | Dla fluidów |
| Annihilation Plane | `ae2:annihilation_plane` | Niszczy bloki → sieć |
| Formation Plane | `ae2:formation_plane` | Wypluwa itemy/bloki |
| Fluid Formation Plane | `ae2:fluid_formation_plane` | Dla fluidów |
| Annihilation Plane (fluid) | `ae2:fluid_annihilation_plane` | Dla fluidów |
| Identity Annihilation Plane | `ae2:identity_annihilation_plane` | Zachowuje NBT |
| Toggle Bus | `ae2:toggle_bus` | Włącza/wyłącza kabel |
| Inverted Toggle Bus | `ae2:inverted_toggle_bus` | Odwrócona logika |
| P2P Tunnel - ME | `ae2:me_p2p_tunnel` | Tunel ME |
| P2P Tunnel - Item | `ae2:item_p2p_tunnel` | Tunel itemów |
| P2P Tunnel - Fluid | `ae2:fluid_p2p_tunnel` | Tunel fluidów |
| P2P Tunnel - Redstone | `ae2:redstone_p2p_tunnel` | Tunel redstone |
| P2P Tunnel - Energy | `ae2:energy_p2p_tunnel` | Tunel energii |
| P2P Tunnel - Light | `ae2:light_p2p_tunnel` | Tunel światła |
| Cable Anchor | `ae2:cable_anchor` | Zakończenie kabla |
| Facade | `ae2:facade` | Maskowanie kabli |
| Quartz Fiber | `ae2:quartz_fiber` | Przesył AE bez kanałów |
| Storage Monitor | `ae2:storage_monitor` | Wyświetla ilość itemu |
| Conversion Monitor | `ae2:conversion_monitor` + umożliwia wypłatę |

---

## 6. Itemy i komponenty

### 6.1 Storage Cells

| Item 1.7.10 | Item 1.18.2 | Pojemność |
|-------------|-------------|-----------|
| Item Storage Cell 1k | `ae2:item_storage_cell_1k` | 1,024 bytes |
| Item Storage Cell 4k | `ae2:item_storage_cell_4k` | 4,096 bytes |
| Item Storage Cell 16k | `ae2:item_storage_cell_16k` | 16,384 bytes |
| Item Storage Cell 64k | `ae2:item_storage_cell_64k` | 65,536 bytes |
| - | `ae2:item_storage_cell_256k` | 262,144 bytes (NOWOŚĆ) |
| Fluid Storage Cell 1k | `ae2:fluid_storage_cell_1k` | 1,024 bytes |
| Fluid Storage Cell 4k | `ae2:fluid_storage_cell_4k` | 4,096 bytes |
| Fluid Storage Cell 16k | `ae2:fluid_storage_cell_16k` | 16,384 bytes |
| Fluid Storage Cell 64k | `ae2:fluid_storage_cell_64k` | 65,536 bytes |
| Fluid Storage Cell 256k | `ae2:fluid_storage_cell_256k` | 262,144 bytes |
| Portable Cell | `ae2:portable_item_cell_1k` | Przenośna komórka |
| - | `ae2:portable_item_cell_4k` | Przenośna (NOWOŚĆ) |
| - | `ae2:portable_item_cell_16k` | Przenośna (NOWOŚĆ) |
| - | `ae2:portable_item_cell_64k` | Przenośna (NOWOŚĆ) |
| - | `ae2:portable_item_cell_256k` | Przenośna (NOWOŚĆ) |
| - | `ae2:portable_fluid_cell_1k` | Przenośna fluid (NOWOŚĆ) |
| View Cell | `ae2:view_cell` | Filtrowanie widoku |
| Spatial Storage Cell 2³ | `ae2:spatial_cell_2` | 2x2x2 |
| Spatial Storage Cell 16³ | `ae2:spatial_cell_16` | 16x16x16 |
| Spatial Storage Cell 128³ | `ae2:spatial_cell_128` | 128x128x128 |

### 6.2 Procesory i komponenty

| Item 1.7.10 | Item 1.18.2 | Użycie |
|-------------|-------------|--------|
| Logic Processor | `ae2:logic_processor` | Crafting komponentów |
| Calculation Processor | `ae2:calculation_processor` | Crafting komponentów |
| Engineering Processor | `ae2:engineering_processor` | Crafting komponentów |
| Printed Logic Circuit | `ae2:printed_logic_processor` | Półprodukt |
| Printed Calculation Circuit | `ae2:printed_calculation_processor` | Półprodukt |
| Printed Engineering Circuit | `ae2:printed_engineering_processor` | Półprodukt |
| Printed Silicon | `ae2:printed_silicon` | Półprodukt |
| Silicon | `ae2:silicon` | Materiał bazowy |

### 6.3 Materiały

| Item 1.7.10 | Item 1.18.2 |
|-------------|-------------|
| Certus Quartz Crystal | `ae2:certus_quartz_crystal` |
| Charged Certus Quartz Crystal | `ae2:charged_certus_quartz_crystal` |
| Certus Quartz Dust | `ae2:certus_quartz_dust` |
| Fluix Crystal | `ae2:fluix_crystal` |
| Fluix Dust | `ae2:fluix_dust` |
| Fluix Pearl | `ae2:fluix_pearl` |
| Sky Stone | `ae2:sky_stone_block` |
| Smooth Sky Stone | `ae2:smooth_sky_stone_block` |
| Sky Stone Dust | `ae2:sky_dust` |
| Matter Ball | `ae2:matter_ball` |
| Singularity | `ae2:singularity` |
| Quantum Entangled Singularity | `ae2:quantum_entangled_singularity` |

### 6.4 Karty ulepszeń (Upgrade Cards)

| Karta 1.7.10 | Karta 1.18.2 | Funkcja |
|--------------|--------------|---------|
| Basic Card | `ae2:basic_card` | Podstawowa (fuzzy, inverter) |
| Advanced Card | `ae2:advanced_card` | Zaawansowana (crafting, capacity) |
| Fuzzy Card | `ae2:fuzzy_card` | Fuzzy matching |
| Inverter Card | `ae2:inverter_card` | Odwrócenie filtru |
| Speed Card | `ae2:speed_card` | Przyspieszenie |
| Capacity Card | `ae2:capacity_card` | Więcej slotów config |
| Crafting Card | `ae2:crafting_card` | Autocrafting w eksporcie |
| Redstone Card | `ae2:redstone_card` | Kontrola redstone |

### 6.5 Narzędzia

| Narzędzie 1.7.10 | Narzędzie 1.18.2 | Funkcja |
|------------------|------------------|---------|
| Network Tool | `ae2:network_tool` | Diagnostyka sieci |
| Memory Card | `ae2:memory_card` | Kopiowanie ustawień |
| Certus Quartz Wrench | `ae2:certus_quartz_wrench` | Obracanie bloków |
| Nether Quartz Wrench | `ae2:nether_quartz_wrench` | Obracanie bloków |
| Matter Cannon | `ae2:matter_cannon` | Broń zużywająca itemy |
| Charged Staff | `ae2:charged_staff` | Narzędzie z ładowaniem |
| Entropy Manipulator | `ae2:entropy_manipulator` | Zmiana stanów bloków |
| Color Applicator | `ae2:color_applicator` | Malowanie kabli |

---

## 7. Analiza kodu źródłowego

### 7.1 Klasy Tile Entities w 1.7.10

| Klasa Tile 1.7.10 | Pakiet | Klasa bazowa | Opis |
|-------------------|--------|--------------|------|
| `TileController` | `appeng.tile.networking` | `AENetworkPowerTile` | ME Controller - serce sieci |
| `TileDrive` | `appeng.tile.storage` | `AENetworkInvTile` | ME Drive - 10 slotów na cell |
| `TileChest` | `appeng.tile.storage` | `AENetworkPowerTile` | ME Chest - 1 slot cell + inventory |
| `TileInterface` | `appeng.tile.misc` | `AENetworkInvTile` | Interface - używa `DualityInterface` |
| `TileIOPort` | `appeng.tile.storage` | `AENetworkInvTile` | IO Port - transfer między cellami |
| `TileCharger` | `appeng.tile.misc` | `AEBaseInvTile` | Ładowanie certus quartz |
| `TileInscriber` | `appeng.tile.misc` | `AEBaseInvTile` | Tworzenie procesorów |
| `TileMolecularAssembler` | `appeng.tile.crafting` | `AENetworkPowerTile` | Autocrafting |
| `TileCraftingTile` | `appeng.tile.crafting` | `AENetworkInvTile` | Crafting CPU Unit |
| `TileCraftingStorageTile` | `appeng.tile.crafting` | `TileCraftingTile` | Crafting CPU ze storage |
| `TileCraftingMonitorTile` | `appeng.tile.crafting` | `TileCraftingTile` | Monitor postępu |
| `TileCondenser` | `appeng.tile.misc` | `AEBaseInvTile` | Kondensacja matter |
| `TileVibrationChamber` | `appeng.tile.misc` | `AEBaseInvTile` | Generator AE |
| `TileQuartzGrowthAccelerator` | `appeng.tile.misc` | `AEBaseTile` | Przyspieszanie wzrostu |
| `TileEnergyCell` | `appeng.tile.networking` | `AENetworkPowerTile` | Magazyn AE |
| `TileDenseEnergyCell` | `appeng.tile.networking` | `TileEnergyCell` | Gęsty magazyn AE |
| `TileCreativeEnergyCell` | `appeng.tile.networking` | `AENetworkPowerTile` | Creative energy |
| `TileEnergyAcceptor` | `appeng.tile.networking` | `AENetworkPowerTile` | Konwersja energii |
| `TileWireless` | `appeng.tile.networking` | `AENetworkPowerTile` | Wireless Access Point |
| `TileSecurity` | `appeng.tile.misc` | `AENetworkInvTile` | Security Terminal |
| `TileCableBus` | `appeng.tile.networking` | `AEBaseTile` | Kabel + części |
| `TileQuantumBridge` | `appeng.tile.qnb` | `AENetworkInvTile` | Quantum Network Bridge |
| `TileSpatialIOPort` | `appeng.tile.spatial` | `AENetworkInvTile` | Spatial IO |
| `TileSpatialPylon` | `appeng.tile.spatial` | `AEBaseTile` | Spatial Pylon |

### 7.2 Struktura dziedziczenia klas 1.7.10

```
TileEntity (Minecraft)
  └── AEBaseTile
       ├── AEBaseInvTile
       │    └── (TileCharger, TileInscriber, TileCondenser, ...)
       ├── AENetworkTile
       │    └── AENetworkInvTile
       │         ├── AENetworkPowerTile
       │         │    ├── TileController
       │         │    ├── TileDrive
       │         │    ├── TileChest
       │         │    ├── TileMolecularAssembler
       │         │    ├── TileEnergyAcceptor
       │         │    ├── TileEnergyCell
       │         │    └── TileWireless
       │         ├── TileInterface
       │         ├── TileIOPort
       │         └── TileCraftingTile
       └── (inne specjalizacje)
```

### 7.3 Kluczowe pola NBT w 1.7.10 (z kodu źródłowego)

#### TileDrive (ME Drive)
```java
// Z: TileDrive.java
@TileEvent(TileEventType.WORLD_NBT_READ)
public void readFromNBT_TileDrive(final NBTTagCompound data) {
    this.isCached = false;
    this.priority = data.getInteger("priority");  // int
}

@TileEvent(TileEventType.WORLD_NBT_WRITE)
public void writeToNBT_TileDrive(final NBTTagCompound data) {
    data.setInteger("priority", this.priority);
}

// Inventory: 10 slotów - klasa bazowa AENetworkInvTile
private final AppEngInternalInventory inv = new AppEngInternalInventory(this, 10);
```

#### TileInterface (Interface)
```java
// Z: TileInterface.java - używa DualityInterface
private final DualityInterface duality = new DualityInterface(this.getProxy(), this);
private ForgeDirection pointAt = ForgeDirection.UNKNOWN;  // Strona "wskazywania"

@TileEvent(TileEventType.WORLD_NBT_WRITE)
public void writeToNBT_TileInterface(final NBTTagCompound data) {
    this.duality.writeToNBT(data);  // Zapisuje patterny i config
}

@TileEvent(TileEventType.WORLD_NBT_READ)
public void readFromNBT_TileInterface(final NBTTagCompound data) {
    this.duality.readFromNBT(data);
}
```

#### AEBaseTile (klasa bazowa)
```java
// Wspólne dla wszystkich TE:
private String customName;  // NBT: "CustomName"
private ForgeDirection forward = ForgeDirection.UNKNOWN;  // Orientacja
private ForgeDirection up = ForgeDirection.UNKNOWN;

// Zapisywane w: writeToNBT_AEBaseTile / readFromNBT_AEBaseTile
```

### 7.4 System Eventów NBT w 1.7.10

AE2 1.7.10 używa adnotacji `@TileEvent` do obsługi NBT:

```java
@TileEvent(TileEventType.WORLD_NBT_READ)
public void readFromNBT_Method(NBTTagCompound data) { ... }

@TileEvent(TileEventType.WORLD_NBT_WRITE)
public void writeToNBT_Method(NBTTagCompound data) { ... }
```

Typy eventów:
- `WORLD_NBT_READ` - odczyt z NBT przy ładowaniu świata
- `WORLD_NBT_WRITE` - zapis do NBT przy zapisywaniu świata
- `NETWORK_READ` - odczyt z pakietu sieciowego
- `NETWORK_WRITE` - zapis do pakietu sieciowego

### 7.5 Różnice w architekturze 1.7.10 vs 1.18.2

| Aspekt | 1.7.10 | 1.18.2 |
|--------|--------|--------|
| **Klasa bazowa Tile** | `AEBaseTile extends TileEntity` | `AEBaseBlockEntity extends BlockEntity` |
| **System NBT** | Adnotacje `@TileEvent` | Metody `saveAdditional()` / `load()` |
| **Inventory** | `AppEngInternalInventory` | `InternalInventory` + `ItemHandler` |
| **Sieć** | `GridProxy` | `IManagedGridNode` |
| **Energia** | Własny system AE | Forge Energy (FE) |
| **Orientacja** | `ForgeDirection` | `Direction` |

---

## 8. Podsumowanie konwersji

### 7.1 Bloki wymagające szczególnej uwagi

| Priorytet | Blok | Uwagi |
|-----------|------|-------|
| 🔴 KRYTYCZNY | ME Drive | Zawartość storage cells |
| 🔴 KRYTYCZNY | ME Chest | Zawartość cell + ewentualnie itemy |
| 🔴 KRYTYCZNY | Interface | Patterny do przeniesienia |
| 🟡 WYSOKI | Quantum Link | Połączenia quantum |
| 🟡 WYSOKI | Spatial IO | Zawartość spatial cells |
| 🟡 WYSOKI | Security Terminal | Uprawnienia graczy |
| 🟢 ŚREDNI | Crafting CPU | Struktury multiblok |
| 🟢 ŚREDNI | Cables/Parts | Konfiguracja, filtry, karty |
| 🟢 NISKI | Dekoracje | Sky stone blocks, itp. |

### 7.2 NOWOŚCI w 1.18.2 do obsłużenia

| Nowość | Opis | Strategia |
|--------|------|-----------|
| Pattern Provider | Wydzielony z Interface | Podzielić Interface na Interface + Pattern Provider |
| Spatial Anchor | Utrzymywanie chunków | Opcjonalnie dodać przy Spatial IO |
| Crystal Resonance Generator | Generator AE | Zastąpić Vibration Chamber tam gdzie pasuje |
| 256k Cells | Większe komórki | Zachować jako 64k lub uaktualnić |
| Extended Pattern Access Terminal | Terminal patternów | Uaktualnić Pattern Access Terminal |

### 7.3 Statystyki

| Kategoria | 1.7.10 | 1.18.2 | Różnica |
|-----------|--------|--------|---------|
| Bloki z TE | ~25 | ~30 | +5 |
| Elementy "part" | ~25 | ~30 | +5 |
| Storage Cell types | 8 | 14 | +6 |
| Narzędzia | 6 | 8 | +2 |

---

*Dokumentacja przygotowana na podstawie:*
- *Kodu źródłowego AE2 1.18.2 ( AppliedEnergistics2/repo )*
- *Archiwalnej dokumentacji AE2 1.7.10 ( https://appliedenergistics.org/ae2-site-archive/ )*
- *Analizy NBT i struktur Tile Entities*

*Plik utworzony przez: Agent AI Konwersji AE2 - Zadanie 1*
