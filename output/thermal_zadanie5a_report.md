# Zadanie 5A: Testowa mapa Thermal Series + konwersja + testy redstone

## Testowa mapa v3

Lokalizacja: `lightweigh_map_templates/1710_modded/thermal_test_v3/`

Zawiera 4 chunki (135 blokow, 90 Tile Entities):

### Chunk (0,0): Maszyny, urzadzenia, dynamy, storage
- **Maszyny** (meta 0-11): Furnace, Pulverizer, Sawmill, Smelter, Crucible, Transposer, Precipitator, Extruder, Accumulator, Assembler, Charger, Insolator
- **Urzadzenia** (meta 0-7): Workbench, Pump, Activator, Breaker, Collector, Nullifier, Buffer, Extender
- **Dynamy** (meta 0-4): Steam, Magmatic, Compression, Reactant, Enervation
- **Storage z tierami**: Cell (tier 0-4 z itemami), Tank (tier 0-4 z fluidami), Strongbox (z enchanted pickaxe), Cache (z cobblestone), Workbench (z sticks)

### Chunk (1,0): Ducty, specjalne, Foundation
- **Energy ducts**: Leadstone, Hardened, Reinforced, Resonant, SuperCond, puste varianty
- **Fluid ducts**: Basic, Hardened, Flux, Super + opaque varianty
- **Item ducts**: Basic, Fast, Ender, Energy + opaque varianty
- **Structural & Transport** ducts
- **Specjalne**: Tesseract (freq=42), Sponge, Magmatic Sponge, Light, Plate, Frame, Glass
- **Rockwool**: wszystkie 16 kolorow
- **Foundation**: Ore (0-6), Storage (0-12)

### Chunk (0,1): Wariacje stanow
- **Facing**: Furnace z facing 0-5
- **Redstone control**: Pulverizer z RC 0, 1, 2
- **Inventory**: Furnace bez itemow, z iron ore, z sand+coal
- **Cell energy**: rozne poziomy energii (0, 500k, 1M)

### Chunk (1,1): Testy redstone
- **Test 1 (Redstone Control)**: Lever (16,64,16) -> Redstone wire (17-18,64,16) -> Furnace (19,64,16, RC=2/HIGH) -> Command block (20,64,16) loguje "THERMAL_REDSTONE_TEST_1 PASS"
- **Test 2 (Energy Transfer)**: Dynamo (16,64,18) -> Energy Duct (17-18,64,18) -> Furnace (19,64,18) z Energy=0

## Wyniki konwersji

- **Bloki znalezione**: 135
- **Przekonwertowane**: 135 (100%)
- **Bledy**: 0
- **Ostrzezenia**: 4

### Podsumowanie docelowych blokow
| Blok docelowy | Liczba |
|---------------|--------|
| thermal:machine_furnace | 26 |
| thermal:white_rockwool | 16 |
| thermal:copper_block | 13 |
| thermal:energy_duct | 10 |
| thermal:tinker_bench | 9 |
| thermal:energy_cell | 8 |
| thermal:fluid_duct | 8 |
| thermal:item_buffer | 8 |
| thermal:copper_ore | 7 |
| thermal:dynamo_stirling | 6 |
| ... | ... |

## Testy integracyjne z redstone

### Scenariusz T1: Redstone Control Machine
**Cel:** Weryfikacja czy maszyna Thermal reaguje na sygnal redstone po konwersji.

**Setup (1.7.10):**
- Lever at (16, 64, 16) -> Redstone wire -> Furnace at (19, 64, 16)
- Furnace NBT: `RedstoneControl: 2` (HIGH = wymaga sygnalu)
- Command block at (20, 64, 16): `/say THERMAL_REDSTONE_TEST_1 PASS`

**Oczekiwane dzialanie po konwersji (1.18.2):**
- Furnace konwertuje sie na `thermal:machine_furnace`
- Redstone control = 2 (HIGH) -> `redstone_control: "high"`
- Po wlaczeniu levera, maszyna powinna zaczac przetwarzac itemy
- Command block loguje PASS jesli struktura dziala

### Scenariusz T2: Energy Transfer (Dynamo -> Duct -> Machine)
**Cel:** Weryfikacja czy energy duct przesyla energie po konwersji.

**Setup (1.7.10):**
- Dynamo Steam at (16, 64, 18) -> Energy Duct (17-18, 64, 18) -> Furnace at (19, 64, 18)
- Dynamo: `Energy: 0, Fuel: 1000`
- Furnace: `Energy: 0`

**Oczekiwane dzialanie po konwersji (1.18.2):**
- Dynamo -> `thermal:dynamo_stirling`
- Energy Duct -> `thermal:energy_duct`
- Furnace -> `thermal:machine_furnace`
- Po uruchomieniu dynama, energia powinna plyna przez duct do maszyny

## Wykonanie w Zadaniu 6
Testy redstone beda odpalone na headless serwerze 1.18.2 z przekonwertowana mapa.
Szczegoly w `skills/autotest-on-server`.
