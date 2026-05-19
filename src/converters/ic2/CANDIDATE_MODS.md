# Kandydacki mody IC2 → 1.18.2 – Inwentaryzacja i mapowania

## Pobrane mody (zweryfikowane JARy)

Wszystkie mody znajdują się w `mod_src/118/mod_jars/candidates/`.

| Mod | ModId | Wersja | Rozmiar | Źródło |
|-----|-------|--------|---------|--------|
| **FTB Industrial Contraptions** | `ftbic` | 1802.1.6-build.220 | 2.1 MB | CurseForge (fileId 4033023) |
| **Industrial Reborn** | `indreb` | 1.18.2-0.13.0 | 3.0 MB | CurseForge (fileId 4034099) |
| **Industrial Foregoing** | `industrialforegoing` | 1.18.2-3.3.1.6-10 | 4.4 MB | Modrinth |
| **Immersive Engineering** | `immersiveengineering` | 1.18.2-8.4.0-161 | 10.5 MB | Modrinth |
| **Modular Routers** | `modularrouters` | 1.18.2-9.1.2 | 1.1 MB | Modrinth |
| **SecurityCraft** | `securitycraft` | 1.18.2-v1.10.1 | 4.2 MB | Modrinth |
| **Simply Light** | `simplylight` | 1.18.2-1.4.5-build.43 | 536 KB | CurseForge (fileId 4016411) |

---

## Tier 1 – Mody "IC2-like" (bezpośredni duchowy następca)

### 1A. Industrial Reborn (`indreb`) ⭐ REKOMENDOWANY

**Dlaczego:** Używa FE (Forge Energy) – natychmiastowa kompatybilność z Mekanism/Thermal. Ma praktycznie wszystkie bloki IC2 pod tymi samymi lub bardzo podobnymi nazwami.

**Kluczowe bloki (zweryfikowane blockstates):**

| IC2 blok | `indreb` target | Uwagi |
|----------|-----------------|-------|
| Machine Block | `indreb:basic_machine_casing` | 1:1 |
| Advanced Machine Block | `indreb:advanced_machine_casing` | 1:1 |
| Iron Furnace | `indreb:iron_furnace` | 1:1 |
| Electric Furnace | `indreb:electric_furnace` | 1:1 |
| Macerator | `indreb:crusher` | Funkcjonalny odpowiednik |
| Extractor | `indreb:extractor` | 1:1 |
| Compressor | `indreb:compressor` | 1:1 |
| Canning Machine | `indreb:canning_machine` | 1:1 |
| Recycler | `indreb:recycler` | 1:1 |
| Fermenter | `indreb:fermenter` | 1:1 |
| Extruder | `indreb:extruder` | 1:1 |
| Sawmill | `indreb:sawmill` | Dla Block Cutter |
| Generator | `indreb:generator` | 1:1 |
| Geothermal Generator | `indreb:geo_generator` | 1:1 |
| Solar Panel | `indreb:solar_generator` | 1:1 |
| Hybrid Solar | `indreb:hybrid_solar_generator` | Upgrade |
| Quantum Solar | `indreb:quantum_solar_generator` | Upgrade |
| Semifluid Generator | `indreb:semifluid_generator` | 1:1 |
| BatBox | `indreb:battery_box` | 1:1 |
| CESU | `indreb:cesu` | 1:1 |
| MFE | `indreb:mfe` | 1:1 |
| MFSU | `indreb:mfsu` | 1:1 |
| Chargepads (all) | `indreb:charge_pad_*` | 4 warianty |
| LV/MV/HV/EV Transformer | `indreb:*_transformer` | 4 tiery |
| Copper Cable | `indreb:copper_cable` / `insulated` | 1:1 |
| Gold Cable | `indreb:gold_cable` / `insulated` | 1:1 |
| HV Cable | `indreb:hv_cable` / `insulated` | 1:1 |
| Glass Fibre Cable | `indreb:glass_fibre_cable` | 1:1 |
| Luminator | `indreb:luminator` | 🎉 1:1! |
| Reinforced Stone | `indreb:reinforced_stone` | 1:1 |
| Reinforced Glass | `indreb:reinforced_glass` | 1:1 |
| Reinforced Foam | `indreb:reinforced_construction_foam` | 1:1 |
| Construction Foam (colors) | `indreb:construction_foam_wall_*` | Wszystkie 16 kolorów! |
| Rubber Log | `indreb:rubber_log` / `rubber_wood` | 1:1 |
| Rubber Leaves | `indreb:rubber_leaves` | 1:1 |
| Rubber Sapling | `indreb:rubber_sapling` | 1:1 |
| Rubber Planks | `indreb:rubber_planks` | Bonus |
| Resin Sheet | `indreb:resin_sheet` | 1:1 |
| Tin Ore | `indreb:deepslate_tin_ore` | 1:1 |
| Lead Ore | `indreb:deepslate_lead_ore` | 1:1 |
| Uranium Ore | `indreb:deepslate_uranium_ore` | 1:1 |

**Braki w indreb:** Teleporter, Nuclear Reactor, Pump, Tesla Coil, Crop-Matron, Ore Washing Plant, Pattern Storage, Scanner, Replicator, Terraformer, Water/Wind Mill, RT Generator, Kinetic Generators.

---

### 1B. FTB Industrial Contraptions (`ftbic`)

**Dlaczego:** Nowoczesny reboot IC2 z tierowanymi maszynami, solarami i bateriami. Ma unikalne bloki: Nuclear Reactor, Quarry, Teleporter.

**Uwaga:** Używa własnego systemu energii **Zaps** – wymaga konwersji Zaps↔FE przy integracji z innymi modami.

**Kluczowe bloki (zweryfikowane blockstates):**

| IC2 blok | `ftbic` target | Uwagi |
|----------|----------------|-------|
| Machine Block | `ftbic:machine_block` | 1:1 |
| Advanced Machine Block | `ftbic:advanced_machine_block` | 1:1 |
| Iron Furnace | `ftbic:iron_furnace` | 1:1 |
| Electric Furnace | `ftbic:powered_furnace` | 1:1 |
| Induction Furnace | `ftbic:advanced_powered_furnace` | Upgrade |
| Macerator | `ftbic:macerator` | 1:1 |
| Advanced Macerator | `ftbic:advanced_macerator` | Upgrade |
| Compressor | `ftbic:compressor` | 1:1 |
| Advanced Compressor | `ftbic:advanced_compressor` | Upgrade |
| Centrifuge | `ftbic:centrifuge` | Dla Extractor |
| Advanced Centrifuge | `ftbic:advanced_centrifuge` | Dla Thermal Centrifuge |
| Canning Machine | `ftbic:canning_machine` | 1:1 |
| Pump | `ftbic:pump` | 1:1 |
| Recycler | `ftbic:reprocessor` | Funkcjonalny odpowiednik |
| Mass Fabricator | `ftbic:antimatter_constructor` | Duchowy następca |
| Teleporter | `ftbic:teleporter` | 1:1 |
| Quarry | `ftbic:quarry` | Dla Advanced Miner |
| Extruder | `ftbic:extruder` | 1:1 |
| Roller | `ftbic:roller` | Dla Metal Former |
| Generator | `ftbic:basic_generator` | 1:1 |
| Geothermal Generator | `ftbic:geothermal_generator` | 1:1 |
| Wind Mill | `ftbic:wind_mill` | 1:1 |
| Nuclear Reactor | `ftbic:nuclear_reactor` | 🎉 Jest! |
| Reactor Chamber | `ftbic:nuclear_reactor_chamber` | 🎉 Jest! |
| BatBox → LV Battery Box | `ftbic:lv_battery_box` | Tierowany |
| MFE → MV Battery Box | `ftbic:mv_battery_box` | Tierowany |
| MFSU → HV Battery Box | `ftbic:hv_battery_box` | Tierowany |
| EV Battery Box | `ftbic:ev_battery_box` | Bonus tier |
| LV/MV/HV/EV Transformer | `ftbic:*_transformer` | 4 tiery |
| LV/MV/HV/EV/IV Cable | `ftbic:*_cable` | 5 tierów |
| LV/MV/HV/EV Solar Panel | `ftbic:*_solar_panel` | 4 tiery |
| Charge Pad | `ftbic:charge_pad` | Jeden typ |
| Reinforced Stone | `ftbic:reinforced_stone` | 1:1 |
| Reinforced Glass | `ftbic:reinforced_glass` | 1:1 |
| Tin Ore | `ftbic:deepslate_tin_ore` | 1:1 |
| Lead Ore | `ftbic:deepslate_lead_ore` | 1:1 |
| Uranium Ore | `ftbic:deepslate_uranium_ore` | 1:1 |
| Iridium Ore | `ftbic:deepslate_iridium_ore` | Bonus |

**Braki w ftbic:** CESU, Luminator, Construction Foam, Rubber Wood/Leaves/Sapling, Fermenter, Semifluid Generator, Water Mill, RT Generator, Kinetic Generators, Crop-Matron.

---

## Tier 2 – Mekanism / Thermal / Immersive Engineering

### Immersive Engineering (`immersiveengineering`)

Uzupełnia braki Tier-1 w obszarze wielobloków, prasy, kruszarki i rolnictwa.

| IC2 blok | `immersiveengineering` target | Uwagi |
|----------|-------------------------------|-------|
| Blast Furnace | `immersiveengineering:blast_furnace` | Wieloblok |
| Advanced Blast Furnace | `immersiveengineering:advanced_blast_furnace` | Wieloblok |
| Alloy Smelter | `immersiveengineering:alloy_smelter` | Wieloblok |
| Arc Furnace | `immersiveengineering:arc_furnace` | Wieloblok (lepszy niż Induction) |
| Metal Former | `immersiveengineering:metal_press` | Wieloblok |
| Macerator | `immersiveengineering:crusher` | Wieloblok |
| Sawmill | `immersiveengineering:sawmill` | Wieloblok |
| Bottling Machine | `immersiveengineering:bottling_machine` | Wieloblok |
| Fermenter | `immersiveengineering:fermenter` | Wieloblok |
| Assembler | `immersiveengineering:assembler` | Wieloblok |
| Auto Workbench | `immersiveengineering:auto_workbench` | Wieloblok |
| Diesel Generator | `immersiveengineering:generator` | Wieloblok (dla Generator) |
| Water Mill | `immersiveengineering:watermill` | Wieloblok |
| Wind Mill | `immersiveengineering:windmill` | Wieloblok |
| BatBox → Capacitor LV | `immersiveengineering:capacitor_lv` | 1:1 |
| MFE → Capacitor MV | `immersiveengineering:capacitor_mv` | 1:1 |
| MFSU → Capacitor HV | `immersiveengineering:capacitor_hv` | 1:1 |
| Chargepad | `immersiveengineering:charging_station` | 1:1 |
| Pump | `immersiveengineering:fluid_pump` | Wieloblok |
| Coke Oven | `immersiveengineering:coke_oven` | Wieloblok (dla Solid Heat Generator) |

---

## Tier 3 – Create / Industrial Foregoing / RFTools / XNet / Modular Routers

### Industrial Foregoing (`industrialforegoing`)

| IC2 blok | `industrialforegoing` target | Uwagi |
|----------|------------------------------|-------|
| Rubber / Latex | `industrialforegoing:latex_processing_unit` | Produkcja latexu |
| Fluid Extractor | `industrialforegoing:fluid_extractor` | Ekstrakcja płynów |
| Biofuel Generator | `industrialforegoing:biofuel_generator` | Dla Semifluid Generator |
| Miner | `industrialforegoing:block_breaker` + `laser_drill` | Alternatywy |
| Block Placer | `industrialforegoing:block_placer` | Dla budowy |
| Crop Harvester | `industrialforegoing:hydroponic_bed` | Uprawy |
| Crop-Matron | `industrialforegoing:animal_feeder` / `hydroponic_bed` | Automatyka upraw |
| Stonework Factory | `industrialforegoing:material_stonework_factory` | Produkcja kamienia |

### Modular Routers (`modularrouters`)

| IC2 blok | `modularrouters` target | Uwagi |
|----------|-------------------------|-------|
| Item Buffer | `modularrouters:modular_router` | Elastyczny bufor z modułami |

---

## Tier 4 – SecurityCraft / Pipez / Sophisticated Storage

### SecurityCraft (`securitycraft`)

Używany tylko jeśli Tier-1 (indreb/ftbic) nie jest dostępny dla reinforced blocks.

| IC2 blok | `securitycraft` target | Uwagi |
|----------|------------------------|-------|
| Reinforced Stone | `securitycraft:reinforced_stone*` | Wiele wariantów reinforced |
| Reinforced Glass | `securitycraft:reinforced_glass*` | Wiele wariantów reinforced |

---

## Tier 5 – Simply Light / Placeholder

### Simply Light (`simplylight`)

| IC2 blok | `simplylight` target | Uwagi |
|----------|----------------------|-------|
| Luminator | `simplylight:illuminant_block` | Podstawowy blok świetlny |
| Luminator Panel | `simplylight:illuminant_panel` | Płaski panel |
| Edge Light | `simplylight:edge_light` | Krawędziowe światło |
| Lamp Post | `simplylight:lamp_post` | Latarnia |
| Lightbulb | `simplylight:lightbulb` | Żarówka |
| Illuminant Slab | `simplylight:illuminant_slab` | Półka świetlna |
| Kolory | `simplylight:illuminant_*_block` | 16 kolorów + ON/OFF |

---

## Rekomendacja architektoniczna

`block_mappings.py` został już zmigrowany na **Tier-1 first** jako domyślną strategię:
- **Industrial Reborn (`indreb`)** – główny target dla wszystkiego co ma odpowiednik
- **FTB Industrial Contraptions (`ftbic`)** – fallback dla braków indreb (Pump, Wind Mill, Nuclear Reactor, Quarry, Teleporter, Antimatter Constructor, Uranium/Lead blocks)
- **Mekanism / Thermal** – tylko dla `steel_block` (brak w Tier-1)
- **Vanilla** – copper_ore, copper_block, basalt

**Aktualne wyniki (`block_mappings.py`):**
- Liczba mapowań: 113
- Placeholdery: 43 (z 51)
- Tier-1 real blocks: 66 (58.4%)
- Stopień konwersji real-block: **61.9%** (wzrost z 54.9%)

**Oczekiwany stopień konwersji po dalszej migracji NBT i dodaniu Tier-3 (Modular Routers, Industrial Foregoing):** ~70%.

---

## Pliki źródłowe w projekcie

- `src/converters/ic2/mappings/block_mappings.py` – obecne mapowania (Tier-2)
- `src/converters/ic2/mappings/tier1_alternative_mappings.py` – mapowania Tier-1
- `src/converters/ic2/mappings/block_inventory.py` – inwentaryzacja bloków IC2
