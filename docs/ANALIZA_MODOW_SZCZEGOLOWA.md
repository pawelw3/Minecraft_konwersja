# Szczegółowa analiza modów - Konwersja 1.7.10 → 1.18.2

> **STATUS: Analiza na podstawie paczki modpack_1710**
> Data analizy: 2026-01-30

---

## 1. Podsumowanie wykonawcze

### Statystyki paczki modów 1.7.10
| Kategoria | Liczba |
|-----------|--------|
| Mody główne (JAR) | 56 |
| Biblioteki/Core | 12 |
| Content packs (Flan's) | Do sprawdzenia |

### Dostępność na 1.18.2
| Status | Liczba modów | Procent |
|--------|--------------|---------|
| ✅ Dostępny bezpośrednio | 29 | 52% |
| ⚠️ Dostępny jako alternatywa | 15 | 27% |
| ❌ Niedostępny/niepotrzebny | 12 | 21% |

---

## 2. Pełna lista modów z paczki 1.7.10

### 2.1 Mody POMINIĘTE w oryginalnej liście konwersji - Z MAPOWANIEM

| # | Mod z paczki 1.7.10 | Status 1.18.2 | Rozwiązanie / Mapowanie |
|---|---------------------|---------------|------------------------|
| 1 | **Treecapitator** | ❌ Brak portu | **FallingTree** (1.18.2) |
| 2 | **Better Storage** | ❌ Brak portu | **Storage Drawers** + **Sophisticated Storage** + **Iron Chests** |
| 3 | **FastCraft** | ❌ Niepotrzebny | **Rubidium** + **Starlight** + **FerriteCore** |
| 4 | **LiteLoader + Omniscience** | ❌ Brak | Mody Forge (nie LiteLoader) |
| 5 | **Opis** | ❌ Brak portu | **Spark** (profiler) + **Observable** |
| 6 | **Reis Minimap** | ✅ Alternatywa | **JourneyMap** lub **Xaero's Minimap** |
| 7 | **CraftGuide** | ❌ Niepotrzebny | **JEI** |
| 8 | **NoMoreRecipeConflict** | ❌ Niepotrzebny | **Polymorph** (jeśli potrzebny) |
| 9 | **NotEnoughItems (NEI)** | ✅ Alternatywa | **JEI** |
| 10 | **PowerConverters** | ❌ Niepotrzebny | *Nie potrzeba* (FE natywne) |
| 11 | **Statues** | ✅ **JEST PORT!** | **Statues (ShyNieke)** 1.18.2 Forge |
| 12 | **Thaumic Tinkerer** | ❌ Brak TC | **Ars Nouveau** (enchanting) |
| 13 | **WorldEdit** | ✅ Dostępny | **WorldEdit** 1.18.2 |
| 14 | **HelpFixer** | ❌ Niepotrzebny | *Nie potrzeba* |
| 15 | **uuidoffline** | ❌ Serwerowy | *Nie potrzeba* (UUID natywne w 1.18.2) |

### Mody usunięte (16 szt.) - szczegółowe mapowanie

Szczegółowe mapowanie wszystkich 16 modów usuniętych:

| # | Mod 1.7.10 | Docelowy 1.18.2 | Strategia | Uwagi |
|---|------------|-----------------|-----------|-------|
| 1 | **Extra Utilities** | **ExU Reborn** + zestaw modów | B | Hybrydowe |
| 2 | **CustomNPCs** | **Easy NPC** | B | Jeśli potrzebne |
| 3 | **Forestry** | **Productive Bees** + **Create**/**Thermal** | B | Modularnie |
| 4 | **IC2 Nuclear Control** | **CC: Tweaked** monitory | B | Monitoring |
| 5 | **Open Modular Turrets** | **IE turrets** / **K-Turrets** | B | Obrona |
| 6 | **Thaumic Energistics** | **AE2** + **Occultism** | B | Storage magii |
| 7 | **Thaumic Exploration** | **Ars Nouveau** | B | Magia |
| 8 | **Thaumic Horizons** | **Ars Nouveau** | B | Summony |
| 9 | **Thaumic Tinkerer** | **Ars Nouveau** | B | Enchanting |
| 10 | **Statues** | **Statues (ShyNieke)** | A/B | Jest port! |
| 11 | **PowerConverters** | *Nie potrzeba* | - | FE natywne |
| 12 | **CraftGuide** | **JEI** | C | QoL |
| 13 | **NoMoreRecipeConflict** | **Polymorph** | C | QoL |
| 14 | **HelpFixer** | *Nie potrzeba* | - | - |
| 15 | **FastCraft** | **Rubidium**/**Starlight** | C | Optymalizacja |
| 16 | **Opis** | **Spark** | C | Profiler |

### 2.2 Mody OBECNE na liście - weryfikacja dostępności

| # | Mod 1.7.10 | Na liście? | Status 1.18.2 | Weryfikacja |
|---|------------|------------|---------------|-------------|
| 1 | Applied Energistics 2 | ✅ | ✅ AE2 11.7.6 | [CurseForge](https://www.curseforge.com/minecraft/mc-mods/applied-energistics-2) |
| 2 | Armourer's Workshop | ✅ | ✅ 3.2.7-beta | [CurseForge](https://www.curseforge.com/minecraft/mc-mods/armourers-workshop) |
| 3 | Backpack | ✅ | ✅ Sophisticated Backpacks | [CurseForge](https://www.curseforge.com/minecraft/mc-mods/sophisticated-backpacks) |
| 4 | BiblioCraft | ✅ | ⚠️ Alternatywa | Builders Crafts & Additions |
| 5 | Big Reactors | ✅ | ✅ Bigger Reactors 0.6.0 | [CurseForge](https://www.curseforge.com/minecraft/mc-mods/biggerreactors) |
| 6 | Blood Magic | ✅ | ✅ Blood Magic 3.2.6 | [CurseForge](https://www.curseforge.com/minecraft/mc-mods/blood-magic) |
| 7 | BuildCraft | ✅ | ❌ Brak | RFTools Builder + Pretty Pipes |
| 8 | Carpenter's Blocks | ✅ | ❌ Brak | **Własny mod (uproszczony)** |
| 9 | Chisel | ✅ | ✅ Rechiseled | [CurseForge](https://www.curseforge.com/minecraft/mc-mods/rechiseled) |
| 10 | ComputerCraft | ✅ | ✅ CC: Tweaked | [Modrinth](https://modrinth.com/mod/cc-tweaked) |
| 11 | CustomNPCs | ✅ | ❌ Strata | Nieużywane na serwerze |
| 12 | Enchanting Plus | ✅ | ✅ Enchanting Infuser | Do weryfikacji |
| 13 | EnderStorage | ✅ | ✅ EnderStorage | [CurseForge](https://www.curseforge.com/minecraft/mc-mods/ender-storage-1-8) |
| 14 | Extra Utilities | ✅ | ⚠️ Częściowo | Brak pełnego portu 1.18.2 |
| 15 | Flan's Mod | ✅ | ⚠️ Alternatywa | TaCZ + inne |
| 16 | Forestry | ✅ | ❌ Strata | Laguje, usunięty |
| 17 | Forge Essentials | ✅ | ⚠️ Do weryfikacji | Może wymagać innego moda |
| 18 | Growthcraft | ✅ | ⚠️ Do weryfikacji | Może nie mieć wersji 1.18.2 |
| 19 | IC2 | ✅ | ❌ Brak | Mekanism/Thermal |
| 20 | IC2 Nuclear Control | ✅ | ❌ Strata | CC: Tweaked monitory |
| 21 | Jammy Furniture | ✅ | ⚠️ Do weryfikacji | MrCrayfish może zastąpić |
| 22 | Logistics Pipes | ✅ | ⚠️ Alternatywa | Pretty Pipes |
| 23 | Mekanism (+ Gen + Tools) | ✅ | ✅ Mekanism 10.2.5 | [CurseForge](https://www.curseforge.com/minecraft/mc-mods/mekanism) |
| 24 | MrCrayfish Furniture | ✅ | ✅ MrCrayfish Furniture | [CurseForge](https://www.curseforge.com/minecraft/mc-mods/mrcrayfish-furniture-mod) |
| 25 | Open Modular Turrets | ✅ | ❌ Brak | IE turrets / własny mod |
| 26 | Pam's HarvestCraft | ✅ | ✅ Pam's HC 2 | [CurseForge](https://www.curseforge.com/minecraft/mc-mods/pams-harvestcraft-2-food-core) |
| 27 | Placeable Items | ✅ | ⚠️ Do weryfikacji | |
| 28 | ProjectRed | ✅ | ✅ ProjectRed 4.17.0 | [CurseForge](https://www.curseforge.com/minecraft/mc-mods/project-red-core) |
| 29 | Railcraft | ✅ | ⚠️ Railcraft Reborn | Niestabilny! |
| 30 | Reliquary | ✅ | ✅ Reliquary Reincarnations | Do weryfikacji |
| 31 | Thaumcraft | ✅ | ❌ Brak | Ars Nouveau |
| 32 | Thaumic Energistics | ✅ | ❌ Brak | - |
| 33 | Thaumic Exploration | ✅ | ❌ Brak | Ars Nouveau |
| 34 | Thaumic Horizons | ✅ | ❌ Brak | Ars Nouveau |
| 35 | Thermal Dynamics | ✅ | ✅ Thermal Series 9.2.2 | [CurseForge](https://www.curseforge.com/minecraft/mc-mods/thermal-dynamics) |
| 36 | Thermal Expansion | ✅ | ✅ Thermal Series | |
| 37 | Thermal Foundation | ✅ | ✅ Thermal Series | |
| 38 | Traincraft | ✅ | ⚠️ Alternatywa | Create + Steam'n'Rails |
| 39 | Witchery | ✅ | ⚠️ Alternatywa | Occultism |

### 2.3 Biblioteki i zależności (nie wymagają konwersji danych)

| Biblioteka 1.7.10 | Odpowiednik 1.18.2 | Uwagi |
|-------------------|-------------------|-------|
| **bspkrsCore** | *Nie potrzebny* | Tylko dla Treecapitator (zastąpiony FallingTree) |
| **Baubles** | **Curios API** | Sloty na akcesoria |
| **CodeChickenCore** | *(wbudowany w CCL)* | - |
| **CodeChickenLib** | **CodeChicken Lib** | Wymagany przez EnderStorage, ProjectRed |
| **CoFHCore** | **CoFH Core** | Wymagany przez Thermal Series |
| **ForgeMultipart** | **CB Multipart** | Microblocks, wymagany przez ProjectRed |
| **ForgeRelocation** | *Nie potrzebny* | Funkcjonalność w Create |
| **ForgeRelocationFMP** | *Nie potrzebny* | - |
| **GollumCoreLib** | *Nie potrzebny* | - |
| **iChunUtil** | *Nie potrzebny* | - |
| **MobiusCore** | *Nie potrzebny* | Biblioteka dla Opis (zastąpiony Spark) |
| **MrTJPCore** | *(wbudowany w ProjectRed)* | - |
| **Bookshelf** | **Bookshelf** | Nowa wersja, biblioteka dla innych modów |
| **AsieLib** | *Nie potrzebny* | Biblioteka dla Statues 1.7.10 (nowy Statues nie wymaga) |
| **LiteLoader** | *Nie potrzebny* | Loader dla Omniscience |
| **buildcraft-compat** | *Nie potrzebny* | BuildCraft usunięty |

### Mapowanie bibliotek per-mod
| Mod 1.7.10 | Biblioteki 1.7.10 | Biblioteki 1.18.2 |
|------------|-------------------|-------------------|
| ProjectRed | MrTJPCore, ForgeMultipart | CB Multipart, CodeChickenLib |
| EnderStorage | CodeChickenCore, CodeChickenLib | CodeChickenLib |
| Statues | AsieLib | *(brak - nowy mod nie wymaga)* |
| Thermal Series | CoFHCore | CoFH Core |
| Opis | MobiusCore | *(brak - zastąpiony Sparkiem)* |
| Treecapitator | bspkrsCore | *(brak - zastąpiony FallingTree)* |

---

## 3. Szczegółowe mapowanie modów USUNIĘTYCH (16 szt.)

Szczegółowe mapowanie funkcjonalności modów sklasyfikowanych jako "Kompletna strata" z uwzględnieniem alternatyw na 1.18.2.

### 3.0.1 Extra Utilities → Zestaw modów 1.18.2

Extra Utilities nie ma pełnego portu. Funkcjonalności dzielimy na osobne mody:

| Funkcja ExU 1.7.10 | Mod docelowy 1.18.2 | Uwagi |
|--------------------|---------------------|-------|
| **Cursed Earth** (farmy mobów) | **Cursed Earth** | Osobny mod, ta sama funkcja |
| **Angel Block** (blok w powietrzu) | **Angel Block Renewed** / **Angel Block: Restored** | Blok w powietrzu |
| **Mega/Magnum Torch** (blokada spawnu) | **Torchmaster** / **Magnum Torch** | Blokada spawnu mobów w promieniu |
| **Transfer Nodes/Pipes** | **Pipez** / **XNet** | Transport item/fluid/energy |
| **Ender Quarry** | **RFTools Builder** (Quarry Card) | Wydobycie obszarowe |
| **Ender-Thermic Pump** | **Mekanism** / **Create** | Pompy do lawy/wody |
| **Generators** (wiele typów) | **Mekanism Generators** / **Thermal** | Różne generatory energii |
| **Trash Can** | **Trash Cans** mod lub podobny | Kosz na itemy |
| **Sound Muffler** | **Extreme Sound Muffler** | Tłumienie dźwięków |

**Extra Utilities Reborn** - nieoficjalny port części funkcjonalności, można użyć jako uzupełnienie.

### 3.0.2 Forestry → Zestaw modów 1.18.2

Forestry nie ma portu na 1.18.2. Funkcjonalności dzielimy na:

| Funkcja Forestry 1.7.10 | Mod docelowy 1.18.2 | Uwagi |
|-------------------------|---------------------|-------|
| **Pszczoły** (Apiary/Alveary) | **Productive Bees** | System uli, pszczół, produktów |
| **Centrifuge/Squeezer** | **Create** (processing) / **Thermal** | Przetwórstwo produktów pszczelich |
| **Multifarm** | **Create** harvestery / **Industrial Foregoing** | Automatyczne farmy |
| **Backpacki** | **Sophisticated Backpacks** | (już na liście) |
| **Mail** (poczta) | **Ender Mail** (opcjonalnie) | System poczty między graczami |
| **Carpenter** (crafting z płynami) | **Create** (mixing, filling) | Crafting wymagający płynów |

### 3.0.3 IC2 Nuclear Control → Monitoring 1.18.2

IC2 Nuclear Control nie ma portu. Funkcjonalność monitoringu reaktorów:

| Funkcja IC2NC 1.7.10 | Rozwiązanie 1.18.2 | Uwagi |
|----------------------|-------------------|-------|
| **Thermal Monitor** | **CC: Tweaked** + sensory | Komputer + program monitoringu |
| **Industrial Alarm** | **CC: Tweaked** + redstone | Alarmy sterowane komputerem |
| **Howler Alarm** | Redstone + note blocks | Prosty alarm |
| **Energy Monitor** | **CC: Tweaked** + integracje | Peryferia do modów energetycznych |

### 3.0.4 Open Modular Turrets → Alternatywy 1.18.2

OMT nie ma portu na 1.18.2. Opcje zamienników:

| Funkcja OMT 1.7.10 | Mod docelowy 1.18.2 | Uwagi |
|--------------------|---------------------|-------|
| **Turrety obronne** | **Immersive Engineering** | Kilka typów turretek (ograniczony wybór) |
| **Modularne turrety** | **K-Turrets** | Bardziej zbliżone do OMT (modularność) |
| **Ammo/Upgrades** | *Brak bezpośredniego* | Mechaniki mogą się różnić |

### 3.0.5 Thaumcraft + addony → Ars Nouveau + Occultism + Botania

Thaumcraft 4 i wszystkie addony (Energistics, Exploration, Horizons, Tinkerer) nie mają portu na 1.18.2.

| Funkcja TC/addonów | Zamiennik 1.18.2 | Jak odtworzyć |
|--------------------|------------------|---------------|
| **Research/Thaumonomicon** | Ars Nouveau (spell book) | Guidebooki (Patchouli) |
| **Aspekty/Essentia** | Source (Ars), Mana (Botania) | Inne systemy zasobów |
| **Infusion Altar** | Enchanting Apparatus (Ars) | Podobna mechanika craftingu |
| **Golemy/automatyzacja** | Occultism (familiars) | Duchy/zwierzęta pomocnicze |
| **Storage essentii** (Thaumic Energistics) | Occultism storage | Magiczny storage |
| **Różdżki/czary** | Ars Nouveau spells | System czarów |
| **Rytuały** | Ars Nouveau rituals / Occultism | Rytuały przywoławcze |
| **Węzły Vis** | Source Jars (Ars) | Zbiorniki magii |

### 3.0.6 Statues → Statues (ShyNieke) 1.18.2

**JEST PORT** na 1.18.2 Forge:
- **Mod:** Statues (ShyNieke)
- **Dostępność:** Modrinth, CurseForge
- **Uwaga:** To NIE jest ten sam mod co 1.7.10 - NBT się nie przeniesie
- **Strategia:** Mapowanie bloków + ręczna rekonstrukcja danych

---

## 3. Szczegółowe mapowanie elementów

### 3.1 Applied Energistics 2 (rv3-beta-6 → 11.7.6)

#### Bloki - mapowanie ID

| Blok 1.7.10 | ID 1.7.10 | Blok 1.18.2 | ID 1.18.2 |
|-------------|-----------|-------------|-----------|
| ME Controller | appliedenergistics2:tile.BlockController | ME Controller | ae2:controller |
| ME Drive | appliedenergistics2:tile.BlockDrive | ME Drive | ae2:drive |
| ME Chest | appliedenergistics2:tile.BlockChest | ME Chest | ae2:chest |
| ME Interface | appliedenergistics2:tile.BlockInterface | ME Interface | ae2:interface |
| Crafting Unit | appliedenergistics2:tile.BlockCraftingUnit | Crafting Unit | ae2:crafting_unit |
| Crafting Co-Processing Unit | appliedenergistics2:tile.BlockCraftingUnit:1 | Crafting Co-Processing Unit | ae2:crafting_accelerator |
| Crafting Monitor | appliedenergistics2:tile.BlockCraftingMonitor | Crafting Monitor | ae2:crafting_monitor |
| Molecular Assembler | appliedenergistics2:tile.BlockMolecularAssembler | Molecular Assembler | ae2:molecular_assembler |
| Charger | appliedenergistics2:tile.BlockCharger | Charger | ae2:charger |
| Inscriber | appliedenergistics2:tile.BlockInscriber | Inscriber | ae2:inscriber |
| Wireless Access Point | appliedenergistics2:tile.BlockWireless | Wireless Access Point | ae2:wireless_access_point |
| Security Terminal | appliedenergistics2:tile.BlockSecurity | ME Security Terminal | ae2:security_station |
| Quantum Ring | appliedenergistics2:tile.BlockQuantumRing | Quantum Ring | ae2:quantum_ring |
| Quantum Link Chamber | appliedenergistics2:tile.BlockQuantumLinkChamber | Quantum Link Chamber | ae2:quantum_link |
| Spatial Pylon | appliedenergistics2:tile.BlockSpatialPylon | Spatial Pylon | ae2:spatial_pylon |
| Spatial IO Port | appliedenergistics2:tile.BlockSpatialIOPort | Spatial IO Port | ae2:spatial_io_port |
| ME Cable | appliedenergistics2:tile.BlockCableBus | ME Cable | ae2:cable_bus |
| Quartz Growth Accelerator | appliedenergistics2:tile.BlockQuartzGrowthAccelerator | Crystal Growth Accelerator | ae2:quartz_growth_accelerator |
| Energy Acceptor | appliedenergistics2:tile.BlockEnergyAcceptor | Energy Acceptor | ae2:energy_acceptor |
| Energy Cell | appliedenergistics2:tile.BlockEnergyCell | Energy Cell | ae2:energy_cell |
| Dense Energy Cell | appliedenergistics2:tile.BlockDenseEnergyCell | Dense Energy Cell | ae2:dense_energy_cell |
| Vibration Chamber | appliedenergistics2:tile.BlockVibrationChamber | Vibration Chamber | ae2:vibration_chamber |

#### Tile Entity NBT - kluczowe różnice

```
1.7.10 NBT Structure:
{
  "id": "AEBase",
  "x": int, "y": int, "z": int,
  "ForgeData": {...},
  "customName": string,
  "orientation": {
    "forward": int,
    "up": int
  }
}

1.18.2 NBT Structure:
{
  "id": "ae2:controller",
  "x": int, "y": int, "z": int,
  "visual": {...},
  "upgrades": {...}
}
```

#### Itemy - storage cells

| Item 1.7.10 | Item 1.18.2 | Pojemność |
|-------------|-------------|-----------|
| 1k ME Storage Cell | ae2:item_storage_cell_1k | 1,024 bytes |
| 4k ME Storage Cell | ae2:item_storage_cell_4k | 4,096 bytes |
| 16k ME Storage Cell | ae2:item_storage_cell_16k | 16,384 bytes |
| 64k ME Storage Cell | ae2:item_storage_cell_64k | 65,536 bytes |
| (NOWY) 256k ME Storage Cell | ae2:item_storage_cell_256k | 262,144 bytes |

#### Uwagi konwersji AE2
- Zawartość storage cells powinna być zachowana (format podobny)
- Kanały działają identycznie
- Nowe bloki w 1.18.2: Pattern Provider (zastępuje część Interface)
- P2P Tunnels - ten sam koncept, nowe typy

---

### 3.2 Mekanism (9.1.1 → 10.2.5)

#### Bloki - mapowanie

| Blok 1.7.10 | Blok 1.18.2 | Uwagi |
|-------------|-------------|-------|
| Enrichment Chamber | mekanism:enrichment_chamber | Bez zmian |
| Crusher | mekanism:crusher | Bez zmian |
| Energized Smelter | mekanism:energized_smelter | Bez zmian |
| Precision Sawmill | mekanism:precision_sawmill | Bez zmian |
| Osmium Compressor | mekanism:osmium_compressor | Bez zmian |
| Combiner | mekanism:combiner | Bez zmian |
| Purification Chamber | mekanism:purification_chamber | Bez zmian |
| Chemical Injection Chamber | mekanism:chemical_injection_chamber | Bez zmian |
| Metallurgic Infuser | mekanism:metallurgic_infuser | Bez zmian |
| Rotary Condensentrator | mekanism:rotary_condensentrator | Bez zmian |
| Chemical Oxidizer | mekanism:chemical_oxidizer | Bez zmian |
| Chemical Infuser | mekanism:chemical_infuser | Bez zmian |
| Chemical Dissolution Chamber | mekanism:chemical_dissolution_chamber | Bez zmian |
| Chemical Washer | mekanism:chemical_washer | Bez zmian |
| Chemical Crystallizer | mekanism:chemical_crystallizer | Bez zmian |
| Pressurized Reaction Chamber | mekanism:pressurized_reaction_chamber | Bez zmian |
| Electrolytic Separator | mekanism:electrolytic_separator | Bez zmian |
| Digital Miner | mekanism:digital_miner | Bez zmian |
| Teleporter | mekanism:teleporter | Bez zmian |
| Quantum Entangloporter | mekanism:quantum_entangloporter | Bez zmian |
| Solar Neutron Activator | mekanism:solar_neutron_activator | Bez zmian |
| Oredictionificator | mekanism:oredictionificator | Bez zmian |
| Factory (Basic) | mekanism:basic_factory | Nowa nazwa |
| Factory (Advanced) | mekanism:advanced_factory | Nowa nazwa |
| Factory (Elite) | mekanism:elite_factory | Nowa nazwa |
| Factory (Ultimate) | mekanism:ultimate_factory | Nowa nazwa |
| Logistical Sorter | mekanism:logistical_sorter | Bez zmian |
| Formulaic Assemblicator | mekanism:formulaic_assemblicator | Bez zmian |
| Fuelwood Heater | mekanism:fuelwood_heater | Bez zmian |
| Resistive Heater | mekanism:resistive_heater | Bez zmian |
| Seismic Vibrator | mekanism:seismic_vibrator | Bez zmian |
| Fluidic Plenisher | mekanism:fluidic_plenisher | Bez zmian |
| Laser | mekanism:laser | Bez zmian |
| Laser Amplifier | mekanism:laser_amplifier | Bez zmian |
| Laser Tractor Beam | mekanism:laser_tractor_beam | Bez zmian |

#### Transportery

| 1.7.10 | 1.18.2 | Uwagi |
|--------|--------|-------|
| Basic Logistical Transporter | mekanism:basic_logistical_transporter | Tier system |
| Advanced Logistical Transporter | mekanism:advanced_logistical_transporter | |
| Elite Logistical Transporter | mekanism:elite_logistical_transporter | |
| Ultimate Logistical Transporter | mekanism:ultimate_logistical_transporter | |
| Restrictive Transporter | mekanism:restrictive_transporter | |
| Diversion Transporter | mekanism:diversion_transporter | |
| Basic Universal Cable | mekanism:basic_universal_cable | |
| Advanced Universal Cable | mekanism:advanced_universal_cable | |
| Elite Universal Cable | mekanism:elite_universal_cable | |
| Ultimate Universal Cable | mekanism:ultimate_universal_cable | |
| Basic Mechanical Pipe | mekanism:basic_mechanical_pipe | |
| Advanced Mechanical Pipe | mekanism:advanced_mechanical_pipe | |
| Elite Mechanical Pipe | mekanism:elite_mechanical_pipe | |
| Ultimate Mechanical Pipe | mekanism:ultimate_mechanical_pipe | |
| Basic Pressurized Tube | mekanism:basic_pressurized_tube | |
| Advanced Pressurized Tube | mekanism:advanced_pressurized_tube | |
| Elite Pressurized Tube | mekanism:elite_pressurized_tube | |
| Ultimate Pressurized Tube | mekanism:ultimate_pressurized_tube | |
| Basic Thermodynamic Conductor | mekanism:basic_thermodynamic_conductor | |
| Advanced Thermodynamic Conductor | mekanism:advanced_thermodynamic_conductor | |
| Elite Thermodynamic Conductor | mekanism:elite_thermodynamic_conductor | |
| Ultimate Thermodynamic Conductor | mekanism:ultimate_thermodynamic_conductor | |

#### Energia
- 1.7.10: Joules (J) - natywna jednostka Mekanism
- 1.18.2: Joules (J) - bez zmian, ale kompatybilność z FE

#### Tile Entity NBT - przykład

```
1.7.10:
{
  "id": "MekanismTile",
  "x": int, "y": int, "z": int,
  "facing": byte,
  "electricityStored": double,
  "redstone": boolean,
  "items": [...],
  "progress": int
}

1.18.2:
{
  "id": "mekanism:enrichment_chamber",
  "x": int, "y": int, "z": int,
  "componentConfig": {...},
  "ejector": {...},
  "energyContainer": {
    "stored": double
  },
  "items": [...],
  "progress": int
}
```

---

### 3.3 Thermal Series (4.1.5 → 9.2.2)

#### Thermal Expansion - Maszyny

| Maszyna 1.7.10 | Maszyna 1.18.2 | ID 1.18.2 |
|----------------|----------------|-----------|
| Redstone Furnace | Redstone Furnace | thermal:machine_furnace |
| Pulverizer | Pulverizer | thermal:machine_pulverizer |
| Sawmill | Sawmill | thermal:machine_sawmill |
| Smelter (Induction) | Induction Smelter | thermal:machine_smelter |
| Insolator (Phytogenic) | Phytogenic Insolator | thermal:machine_insolator |
| Centrifuge | Centrifugal Separator | thermal:machine_centrifuge |
| Crucible (Magma) | Magma Crucible | thermal:machine_crucible |
| Transposer (Fluid) | Fluid Encapsulator | thermal:machine_bottler |
| Precipitator | Glacial Precipitator | thermal:machine_precipitator |
| Extruder (Igneous) | Igneous Extruder | thermal:machine_extruder |
| Compactor | Multiservo Press | thermal:machine_press |
| Brewer | Alchemical Imbuer | thermal:machine_brewer |
| Fractionating Still | Fractionating Still | thermal:machine_refinery |
| Sequential Fabricator | Sequential Fabricator | thermal:machine_crafter |

#### Thermal Dynamics - Ducty

| Duct 1.7.10 | Duct 1.18.2 | Uwagi |
|-------------|-------------|-------|
| Leadstone Fluxduct | thermal:energy_duct | Uproszczony system tierów |
| Hardened Fluxduct | thermal:energy_duct | |
| Redstone Energy Fluxduct | thermal:energy_duct | |
| Signalum Fluxduct | thermal:energy_duct | |
| Resonant Fluxduct | thermal:energy_duct | |
| Cryo-Stabilized Fluxduct | thermal:energy_duct | |
| Temperate Fluiduct | thermal:fluid_duct | |
| Hardened Fluiduct | thermal:fluid_duct | |
| Itemduct | thermal:item_duct | |
| Impulse Itemduct | thermal:item_duct_fast | |
| Fluctuating Itemduct | thermal:item_duct | Energia w itemduct |
| Structuralduct | thermal:structure_duct | |

#### Energia
- 1.7.10: RF (Redstone Flux)
- 1.18.2: FE (Forge Energy) - kompatybilne 1:1

---

### 3.4 Big Reactors → Bigger Reactors

#### Bloki reaktora

| Blok 1.7.10 | Blok 1.18.2 | ID 1.18.2 |
|-------------|-------------|-----------|
| Reactor Casing | Reactor Casing | biggerreactors:reactor_casing |
| Reactor Glass | Reactor Glass | biggerreactors:reactor_glass |
| Yellorium Fuel Rod | Uranium Fuel Rod | biggerreactors:reactor_fuel_rod |
| Reactor Control Rod | Reactor Control Rod | biggerreactors:reactor_control_rod |
| Reactor Access Port | Reactor Access Port | biggerreactors:reactor_access_port |
| Reactor Power Tap | Reactor Power Tap | biggerreactors:reactor_power_tap |
| Reactor Coolant Port | Reactor Coolant Port | biggerreactors:reactor_coolant_port |
| Reactor Computer Port | Reactor Computer Port | biggerreactors:reactor_computer_port |
| Reactor Redstone Port | Reactor Redstone Port | biggerreactors:reactor_redstone_port |

#### Bloki turbiny

| Blok 1.7.10 | Blok 1.18.2 | ID 1.18.2 |
|-------------|-------------|-----------|
| Turbine Housing | Turbine Casing | biggerreactors:turbine_casing |
| Turbine Glass | Turbine Glass | biggerreactors:turbine_glass |
| Turbine Rotor Shaft | Turbine Rotor Shaft | biggerreactors:turbine_rotor_shaft |
| Turbine Rotor Blade | Turbine Rotor Blade | biggerreactors:turbine_rotor_blade |
| Turbine Rotor Bearing | Turbine Rotor Bearing | biggerreactors:turbine_rotor_bearing |
| Turbine Power Tap | Turbine Power Tap | biggerreactors:turbine_power_tap |
| Turbine Fluid Port | Turbine Fluid Port | biggerreactors:turbine_fluid_port |
| Turbine Computer Port | Turbine Computer Port | biggerreactors:turbine_computer_port |

#### Materiały

| Material 1.7.10 | Material 1.18.2 | Uwagi |
|-----------------|-----------------|-------|
| Yellorium Ingot | Uranium Ingot | Zmiana nazwy |
| Yellorium Dust | Uranium Dust | |
| Yellorium Block | Uranium Block | |
| Cyanite Ingot | Cyanite Ingot | Bez zmian |
| Blutonium Ingot | Plutonium Ingot | Zmiana nazwy |
| Ludicrite Block | Ludicrite Block | Bez zmian |
| Graphite Block | Graphite Block | Bez zmian |

#### Uwagi
- Multibloki zachowują strukturę
- Wewnętrzne chłodziwo i konfiguracja mogą wymagać rekonfiguracji
- Nowy system: Heat Exchanger w 1.18.2

---

### 3.5 BuildCraft → RFTools Builder + Pretty Pipes

#### Mapowanie koncepcyjne

| Funkcjonalność BC | Rozwiązanie 1.18.2 | Mod |
|-------------------|-------------------|-----|
| Quarry | Builder (Quarry Card) | RFTools Builder |
| Builder | Builder | RFTools Builder |
| Filler | Builder (Shape Cards) | RFTools Builder |
| Pipe (items) | Pretty Pipes | Pretty Pipes |
| Pipe (fluids) | Mekanism Pipes / Thermal Ducts | Mekanism / Thermal |
| Pipe (power) | Flux Networks / Cables | Flux Networks / Mekanism |
| Auto Workbench | Crafting Station / ME System | Różne |
| Assembly Table | - | Brak odpowiednika |
| Refinery | Thermal Refinery | Thermal Expansion |
| Engine (Stirling) | Thermal Dynamo | Thermal Expansion |
| Engine (Combustion) | Mekanism Generator | Mekanism Generators |

#### RFTools Builder - Shape Cards

| Funkcja | Shape Card |
|---------|------------|
| Quarry | Quarry Card |
| Clearing | Clearing Quarry Card |
| Building | Shape Card (various shapes) |
| Void | Void Card |
| Pump | Pumping Card |
| Shield | Shield Card |

---

### 3.6 IndustrialCraft 2 → Mekanism/Thermal

#### Mapowanie maszyn

| Maszyna IC2 | Odpowiednik | Mod 1.18.2 |
|-------------|-------------|------------|
| Macerator | Crusher / Pulverizer | Mekanism / Thermal |
| Electric Furnace | Energized Smelter / Redstone Furnace | Mekanism / Thermal |
| Compressor | Osmium Compressor | Mekanism |
| Extractor | Crusher + Enrichment Chamber | Mekanism |
| Canning Machine | - | Brak (Pam's może obsłużyć) |
| Recycler | - | Brak |
| Metal Former | Multiservo Press | Thermal |
| Ore Washing Plant | Chemical Washer | Mekanism |
| Thermal Centrifuge | Centrifugal Separator | Thermal |
| Electrolyzer | Electrolytic Separator | Mekanism |

#### Mapowanie energii

| Jednostka IC2 | Konwersja | Jednostka 1.18.2 |
|---------------|-----------|------------------|
| 1 EU | × 4 | 4 FE (Forge Energy) |

#### Mapowanie kabli

| Kabel IC2 | Odpowiednik | Mod |
|-----------|-------------|-----|
| Copper Cable | Basic Universal Cable | Mekanism |
| Gold Cable | Advanced Universal Cable | Mekanism |
| HV Cable | Elite Universal Cable | Mekanism |
| Glass Fibre Cable | Ultimate Universal Cable | Mekanism |

#### Uwagi
- Transformatory (LV/MV/HV) - nie potrzebne, FE nie ma napięcia
- Baterie/Energy Storage - Mekanism Energy Cubes lub Thermal Cells
- Nuclear Reactor - Bigger Reactors lub Mekanism Fission Reactor

---

### 3.7 Armourer's Workshop (0.48.5 → 3.2.7-beta)

#### Bloki i tile entities

| Blok 1.7.10 | Blok 1.18.2 | Uwagi |
|-------------|-------------|-------|
| Armourer | armourers_workshop:armourer | Główny blok tworzenia |
| Skin Library | armourers_workshop:skin_library | Biblioteka skinów |
| Skinning Table | armourers_workshop:skinning_table | Aplikowanie skinów |
| Dye Table | armourers_workshop:dye_table | Farbowanie |
| Hologram Projector | armourers_workshop:hologram_projector | Podgląd |
| Mannequin | armourers_workshop:mannequin | Manekin |

#### Dane skinów
- Skiny przechowywane w NBT tile entity
- Format może się różnić między wersjami
- Wymaga testowania zachowania danych skinów

#### Strategia
- Większość bloków ma bezpośrednie odpowiedniki
- Kluczowe: zachowanie danych skinów w NBT
- Pliki skinów (.armour) mogą wymagać konwersji formatu

---

### 3.8 Railcraft (9.12.2.0 → Railcraft Reborn)

#### Bloki torów

| Blok 1.7.10 | Blok 1.18.2 | Uwagi |
|-------------|-------------|-------|
| Standard Rail | railcraft:track_flex | Podstawowe tory |
| Reinforced Rail | railcraft:track_flex_reinforced | Wzmocnione |
| High Speed Rail | railcraft:track_flex_hs | Szybkie |
| Electric Rail | railcraft:track_flex_electric | Elektryczne |
| Wooden Rail | railcraft:track_flex_abandoned | Drewniane |

#### Maszyny

| Maszyna 1.7.10 | Maszyna 1.18.2 | Uwagi |
|----------------|----------------|-------|
| Rolling Machine | railcraft:rolling_machine | Walcarka |
| Rock Crusher | railcraft:rock_crusher | Kruszarka |
| Coke Oven | railcraft:coke_oven | Piec koksowniczy |
| Blast Furnace | railcraft:blast_furnace | Wielki piec |
| Steam Turbine | railcraft:steam_turbine | Turbina |
| Tank (multiblock) | railcraft:tank_* | Zbiorniki |

#### Uwagi
- ⚠️ Railcraft Reborn może być niestabilny
- Multibloki wymagają sprawdzenia kompatybilności
- Lokomotywy i wagony mogą mieć inny system

---

### 3.9 Chisel → Rechiseled (2.9.5.11 → Rechiseled 1.1.x)

#### Mapowanie bloków dekoracyjnych

Rechiseled używa innego systemu - zamiast osobnych bloków, ma warianty:

| Kategoria Chisel | Rechiseled | Uwagi |
|------------------|------------|-------|
| Andesite variants | rechiseled:andesite_* | 20+ wariantów |
| Diorite variants | rechiseled:diorite_* | 20+ wariantów |
| Granite variants | rechiseled:granite_* | 20+ wariantów |
| Stone variants | rechiseled:stone_* | 30+ wariantów |
| Cobblestone variants | rechiseled:cobblestone_* | 20+ wariantów |
| Sandstone variants | rechiseled:sandstone_* | 20+ wariantów |
| Obsidian variants | rechiseled:obsidian_* | 15+ wariantów |
| Glowstone variants | rechiseled:glowstone_* | 10+ wariantów |
| Wool variants | rechiseled:*_wool_* | Wszystkie kolory |
| Concrete variants | rechiseled:*_concrete_* | Wszystkie kolory |

#### Strategia konwersji
1. Mapowanie metadata 1.7.10 → variant name 1.18.2
2. Chisel miał ~100 bloków bazowych × ~16 wariantów każdy
3. Rechiseled ma podobną liczbę, ale inne nazewnictwo
4. Wymagana tabela: `chisel:<block>:<meta>` → `rechiseled:<block>_<variant>`

---

### 3.10 Thaumcraft → Ars Nouveau

#### UWAGA: Konwersja koncepcyjna, nie 1:1

| Element Thaumcraft | Odpowiednik Ars Nouveau | Uwagi |
|--------------------|------------------------|-------|
| Wand | Spell Book | Inne podejście |
| Vis | Source | Podobna koncepcja |
| Node | Source Jar / Archwood Forest | Inne źródło |
| Infusion Altar | Enchanting Apparatus | Podobna funkcja |
| Arcane Workbench | Enchanting Apparatus | |
| Research Table | Scribe's Table | |
| Thaumometer | Dominion Wand | Inne zastosowanie |
| Golem | Starbuncle / Drygmy | Automation helpers |

#### Strategia konwersji
- **Bloki strukturalne**: Zamiana na najbliższe vanilla/dekoracyjne
- **Maszyny**: Brak bezpośredniego odpowiednika
- **Itemy w inventory**: Lista zgubiona lub zamiana na Source Gems
- **Golemy**: Zamiana na Starbuncle spawn eggs
- **Aura nodes**: Zamiana na Source Jars (puste)

---

### 3.11 Witchery → Occultism

#### UWAGA: Konwersja koncepcyjna

| Element Witchery | Odpowiednik Occultism | Uwagi |
|------------------|----------------------|-------|
| Altar | Golden Sacrificial Bowl | Rytuały |
| Cauldron | - | Brak odpowiednika |
| Spinning Wheel | - | Brak |
| Distillery | - | Brak |
| Kettle | - | Brak |
| Familiar | Familiar System | Podobny koncept |
| Dimension (Spirit World) | Other Dimension | |

#### Strategia
- Większość bloków Witchery → Placeholder lub usunięcie
- Wyspy Spirit World → Potencjalnie inne rozwiązanie

---

### 3.12 Traincraft → Create + Steam'n'Rails

#### UWAGA: Zupełnie inne podejście w Create

| Element Traincraft | Create | Uwagi |
|--------------------|--------|-------|
| Lokomotywy | Train (Create) | Inne budowanie |
| Wagony | Train Carriages | |
| Tory | Create Tracks | Inne craftowanie |
| Stacje | Train Stations | |

#### Strategia
- **Bloki torów**: Zamiana na Create Tracks lub vanilla Rails
- **Pociągi (entities)**: UTRATA - Create wymaga budowy od nowa
- **Stacje**: Zamiana na bloki dekoracyjne

---

### 3.13 Logistics Pipes → Pretty Pipes

#### Mapowanie rur

| Rura Logistics Pipes | Pretty Pipes | Uwagi |
|---------------------|--------------|-------|
| Basic Logistics Pipe | Pipe + Low Priority Module | |
| Request Logistics Pipe | Pipe + Retrieval Module | |
| Provider Logistics Pipe | Pipe + Extraction Module | |
| Crafting Logistics Pipe | Pipe + Crafting Module | |
| Supplier Logistics Pipe | Pipe + Stack Limiter | |
| Chassis | Pipe + Multiple Modules | |

#### Uwagi
- Pretty Pipes jest prostszy niż Logistics Pipes
- Część funkcjonalności pokrywa AE2 lub Mekanism
- Filtry i sortowanie działają podobnie

---

### 3.14 Carpenter's Blocks (WŁASNY MOD)

#### Bloki do reimplementacji

| Blok | Funkcja | Priorytet |
|------|---------|-----------|
| Carpenter's Block | Customowy kształt/tekstura | WYSOKI |
| Carpenter's Slope | Skosy | WYSOKI |
| Carpenter's Stairs | Schody | ŚREDNI |
| Carpenter's Barrier | Barierki | ŚREDNI |
| Carpenter's Door | Drzwi | WYSOKI |
| Carpenter's Bed | Łóżko | NISKI |
| Carpenter's Button | Przycisk | NISKI |
| Carpenter's Lever | Dźwignia | NISKI |
| Carpenter's Pressure Plate | Płyta naciskowa | NISKI |
| Carpenter's Hatch | Klapa | ŚREDNI |
| Carpenter's Gate | Furtka | ŚREDNI |
| Carpenter's Ladder | Drabina | ŚREDNI |
| Carpenter's Torch | Pochodnia | NISKI |
| Carpenter's Safe | Sejf | ŚREDNI |
| Carpenter's Flower Pot | Doniczka | NISKI |
| Carpenter's Garage Door | Brama garażowa | ŚREDNI |
| Carpenter's Daylight Sensor | Sensor | NISKI |
| Carpenter's Collapsible Block | Składany blok | NISKI |

#### Podejście do własnego modu
1. **Minimum viable**: Block, Slope, Door, Barrier, Stairs
2. Tile Entity przechowujący:
   - ID bloku-tekstury
   - Orientację
   - Wariant kształtu
3. Renderer customowy dla każdego typu
4. Konwersja: zachowanie tekstury i orientacji

---

### 3.15 Flan's Mod → TaCZ + Realism Vehicle

#### Broń (Flan's → TaCZ)

| Element Flan's | TaCZ | Uwagi |
|----------------|------|-------|
| Guns | tacz:* weapons | Inne modele, podobna mechanika |
| Ammo | tacz:ammo_* | |
| Attachments | tacz:attachment_* | Scopy, tłumiki |
| Grenades | tacz:grenade_* | |
| Armor | - | Może vanilla netherite |

#### Pojazdy (Flan's → Realism Vehicle / Create)

| Element Flan's | Rozwiązanie 1.18.2 | Uwagi |
|----------------|-------------------|-------|
| Cars | Realism Vehicle / Create contraptions | |
| Tanks | Create Big Cannons + VS | |
| Planes | Valkyrien Skies + Create | |
| Helicopters | Valkyrien Skies | |
| Boats | Vanilla / Small Ships | |

#### Strategia konwersji
- **Broń w inventory**: Zamiana na najbliższe odpowiedniki TaCZ
- **Pojazdy (entities)**: UTRATA - inne systemy w 1.18.2
- **Workbench**: Zamiana na vanilla crafting table
- **Content Packs**: Wymagają osobnej konwersji/przepisania

#### Content Packs z paczki
Sprawdzić folder `Flan/` na mapie - może zawierać:
- Modern Warfare Pack
- WW2 Pack
- Inne custom packs

---

### 3.16 BiblioCraft → Builders Crafts & Additions

#### Mapowanie bloków

| Blok BiblioCraft | Blok 1.18.2 | Mod | Uwagi |
|------------------|-------------|-----|-------|
| Bookcase | bc_additions:bookshelf_* | BC&A | |
| Potion Shelf | bc_additions:potion_shelf | BC&A | |
| Tool Rack | bc_additions:tool_rack | BC&A | |
| Armor Stand | minecraft:armor_stand | Vanilla | |
| Display Case | - | Brak | Można użyć item frames |
| Desk | bc_additions:desk | BC&A | |
| Table | bc_additions:table | BC&A | |
| Seat | bc_additions:seat | BC&A | |
| Label | - | Brak | Signs jako alternatywa |
| Printing Press | - | Brak | |
| Typesetting Table | - | Brak | |
| Atlas | - | Brak | JourneyMap zamiast |
| Clipboard | - | Brak | |
| Reading Glasses | - | Brak | |

#### Tile Entity - Bookshelf

```
1.7.10 NBT:
{
  "id": "BiblioBookcase",
  "Items": [...],  // 16 slotów na książki
  "facing": byte
}

1.18.2 NBT (BC&A):
{
  "id": "bc_additions:bookshelf",
  "inventory": [...],
  "Facing": string
}
```

---

### 3.17 Better Storage / JABBA → Storage Drawers

#### Mapowanie pojemników

| Blok 1.7.10 | Storage Drawers | Uwagi |
|-------------|-----------------|-------|
| JABBA Barrel | storagedrawers:oak_full_drawers_1 | 1 typ itemu |
| Better Storage Crate | storagedrawers:oak_full_drawers_4 | 4 typy |
| Better Storage Locker | storagedrawers:oak_full_drawers_2 | 2 typy |
| Better Storage Armor Stand | minecraft:armor_stand | Vanilla |
| Better Storage Backpack | sophisticatedbackpacks:backpack | Inny mod |

#### Tile Entity - JABBA Barrel

```
1.7.10 NBT (JABBA):
{
  "id": "JABBA:barrel",
  "item": {id: int, Damage: int},  // Przechowywany item
  "count": long,                   // Ilość (może być > 64)
  "maxItems": int,                 // Max capacity
  "upgrades": [...]                // Upgrady
}

1.18.2 NBT (Storage Drawers):
{
  "id": "storagedrawers:standard_drawers_1",
  "Drawers": [{
    "Item": {id: "minecraft:...", Count: 1},
    "Count": long
  }]
}
```

#### Strategia
- Zachować item type i count
- Upgrady capacity → Storage Upgrades w Storage Drawers
- Void upgrade → nie ma odpowiednika (lub Trash Can)

---

### 3.18 Pam's HarvestCraft → Pam's HarvestCraft 2

#### Struktura Pam's HC 2 (podzielony na moduły)

| Moduł 1.18.2 | Zawartość |
|--------------|-----------|
| Food Core | Jedzenie, przepisy |
| Food Extended | Więcej jedzenia |
| Crops | Uprawy |
| Trees | Drzewa owocowe |

#### Mapowanie upraw

| Uprawa 1.7.10 | Uprawa 1.18.2 | ID |
|---------------|---------------|-----|
| pamharvestcraft:artichokeCrop | pamhc2crops:artichokecropblock | |
| pamharvestcraft:asparagus | pamhc2crops:asparaguscropblock | |
| pamharvestcraft:barley | pamhc2crops:barleycropblock | |
| pamharvestcraft:bean | pamhc2crops:beancropblock | |
| pamharvestcraft:bellpepper | pamhc2crops:bellpeppercropblock | |
| ... | ... | Wszystkie uprawy mają prefix pamhc2crops: |

#### Mapowanie drzew

| Drzewo 1.7.10 | Drzewo 1.18.2 | ID |
|---------------|---------------|-----|
| pamharvestcraft:pamApple | pamhc2trees:apple_sapling | |
| pamharvestcraft:pamCherry | pamhc2trees:cherry_sapling | |
| pamharvestcraft:pamLemon | pamhc2trees:lemon_sapling | |
| ... | ... | |

#### Strategia
- Mapowanie 1:1 dla większości bloków (zmiana namespace)
- Jedzenie w inventory: proste mapowanie ID
- Tile entities (Gardens): mogą wymagać rekonfiguracji

---

### 3.19 Tinkers' Construct (1.7.10 → 3.7.2)

#### UWAGA: Znaczące zmiany między wersjami!

| Element 1.7.10 | Element 1.18.2 | Status |
|----------------|----------------|--------|
| Tool Forge | tconstruct:tinker_station | Zmiana nazwy |
| Tool Station | tconstruct:part_builder | Rozdzielone funkcje |
| Part Builder | tconstruct:part_builder | |
| Stencil Table | tconstruct:part_builder | Wbudowane |
| Smeltery Controller | tconstruct:smeltery_controller | |
| Smeltery Drain | tconstruct:smeltery_drain | |
| Seared Tank | tconstruct:seared_tank | |
| Casting Table | tconstruct:casting_table | |
| Casting Basin | tconstruct:casting_basin | |

#### Materiały - zmiany nazw

| Materiał 1.7.10 | Materiał 1.18.2 |
|-----------------|-----------------|
| Cobalt | tconstruct:cobalt | |
| Ardite | USUNIĘTY | Brak w TiC 3 |
| Manyullyn | tconstruct:manyullyn | |
| Alumite | USUNIĘTY | Brak w TiC 3 |
| Copper | tconstruct:copper | |
| Bronze | tconstruct:bronze | |

#### Narzędzia w inventory
- Format NBT całkowicie zmieniony
- Modyfikatory mają inny system
- **REKOMENDACJA**: Narzędzia TiC zamienić na vanilla lub craftnąć od nowa

#### Smeltery multiblock
- Struktura podobna
- Zawartość (molten metals) może wymagać mapowania fluid IDs

---

### 3.20 Reliquary → Reliquary Reincarnations

#### Mapowanie itemów

| Item 1.7.10 | Item 1.18.2 | Uwagi |
|-------------|-------------|-------|
| Alkahestry Tome | reliquary:alkahestry_tome | |
| Angelic Feather | reliquary:angelic_feather | |
| Emperor's Chalice | reliquary:emperor_chalice | |
| Ender Staff | reliquary:ender_staff | |
| Fortune Coin | reliquary:fortune_coin | |
| Glacial Staff | reliquary:glacial_staff | |
| Hero's Medallion | reliquary:hero_medallion | |
| Infernal Chalice | reliquary:infernal_chalice | |
| Infernal Claws | reliquary:infernal_claws | |
| Infernal Tear | reliquary:infernal_tear | |
| Lantern of Paranoia | reliquary:lantern_of_paranoia | |
| Midas Touchstone | reliquary:midas_touchstone | |
| Phoenix Down | reliquary:phoenix_down | |
| Rod of Lyssa | reliquary:rod_of_lyssa | |
| Sojourner's Staff | reliquary:sojourner_staff | |
| Witherless Rose | reliquary:witherless_rose | |

#### Strategia
- Większość itemów ma bezpośrednie odpowiedniki
- Proste mapowanie ID
- NBT data (np. charges) może wymagać konwersji

---

### 3.21 Backpack → Sophisticated Backpacks

#### Mapowanie plecaków

| Backpack 1.7.10 | Sophisticated Backpacks | Uwagi |
|-----------------|------------------------|-------|
| Small Backpack | sophisticatedbackpacks:backpack | Basic tier |
| Medium Backpack | sophisticatedbackpacks:iron_backpack | |
| Big Backpack | sophisticatedbackpacks:gold_backpack | |
| Workbench Backpack | sophisticatedbackpacks:diamond_backpack + crafting upgrade | |
| Ender Backpack | sophisticatedbackpacks:netherite_backpack | Top tier |

#### Tile Entity (placed backpack)

```
1.7.10 NBT:
{
  "id": "Backpack",
  "Items": [...],
  "color": int
}

1.18.2 NBT:
{
  "id": "sophisticatedbackpacks:backpack",
  "contentsUuid": UUID,
  "inventory": {...}
}
```

#### Strategia
- Zachować zawartość inventory
- Kolor → dyeing w nowej wersji
- Upgrady workbench → osobny upgrade item

---

### 3.22 EnderStorage (1.4.7.38 → 2.9.x)

#### Bloki

| Blok 1.7.10 | Blok 1.18.2 | Uwagi |
|-------------|-------------|-------|
| Ender Chest | enderstorage:ender_chest | |
| Ender Tank | enderstorage:ender_tank | |
| Ender Pouch | enderstorage:ender_pouch | Item |

#### Tile Entity - kolor/częstotliwość

```
1.7.10 NBT:
{
  "id": "EnderStorage:EnderChest",
  "colours": [int, int, int],  // 3 kolory (RGB combination)
  "owner": string
}

1.18.2 NBT:
{
  "id": "enderstorage:ender_chest",
  "frequency": {
    "left": int,
    "middle": int,
    "right": int
  },
  "owner": UUID
}
```

#### Strategia
- Kluczowe: zachowanie kombinacji kolorów (częstotliwość)
- Owner może wymagać konwersji name → UUID
- Zawartość jest współdzielona przez wszystkie chesty z tym samym kolorem

---

### 3.23 ForgeMultipart → CB Multipart

#### Microblocks

| Element 1.7.10 | Element 1.18.2 | Uwagi |
|----------------|----------------|-------|
| Micro Block | cbmicroblock:micro_block | |
| Cover | cbmicroblock:cover | |
| Panel | cbmicroblock:panel | |
| Slab | cbmicroblock:slab | |
| Pillar | cbmicroblock:pillar | |
| Post | cbmicroblock:post | |
| Corner | cbmicroblock:corner | |
| Strip | cbmicroblock:strip | |

#### Tile Entity - multipart

```
1.7.10 NBT:
{
  "id": "savedMultipart",
  "parts": [
    {
      "id": "mcr_face@...",
      "material": int,
      "meta": byte,
      "side": byte
    },
    ...
  ]
}

1.18.2 NBT:
{
  "id": "cbmicroblock:multipart",
  "parts": [
    {
      "type": "cbmicroblock:micro_block",
      "material": "minecraft:stone",
      "size": int,
      "slot": int
    },
    ...
  ]
}
```

#### Strategia
- Mapowanie material ID (int) → block ID (string)
- Zachowanie pozycji części (slot/side)
- Wymaga dokładnej tabeli materiałów

---

### 3.24 Open Modular Turrets (brak portu)

#### Stan: ❌ Kompletna strata

| Blok 1.7.10 | Alternatywa 1.18.2 | Mod |
|-------------|-------------------|-----|
| Turret Base | ie:turret | Immersive Engineering |
| Gun Turret | ie:turret_gun | IE |
| Laser Turret | - | Brak |
| Rocket Turret | - | Brak (Create Big Cannons?) |
| Railgun Turret | - | Brak |
| Grenade Turret | - | Brak |
| Incendiary Turret | - | Brak |
| Teleporter Turret | - | Brak |

#### Strategia
- IE turrets jako częściowy zamiennik
- Większość turretów → placeholder lub usunięcie
- Rozważyć własny uproszczony mod (niski priorytet)

---

### 3.25 Forestry (strata - crashuje)

#### Stan: ❌ Kompletna strata

| System | Alternatywa | Uwagi |
|--------|-------------|-------|
| Pszczoły | Productive Bees | Inny mod |
| Motyle | - | Brak |
| Farmy | Mekanism/Create | |
| Drzewa | Vanilla/BOP | |
| Backpacks | Sophisticated Backpacks | |
| Multifarm | Create farming | |

#### Strategia
- Bloki Forestry → placeholder (air/stone)
- Pszczoły w inventory → utrata (różne systemy)
- Plecaki Forestry → Sophisticated Backpacks (puste)

---

## 4. Mody bez konwersji danych (tylko instalacja)

Te mody nie wymagają konwersji danych świata - wystarczy zainstalować nową wersję:

| Mod | Wersja 1.18.2 | Uwagi |
|-----|---------------|-------|
| JEI (zamiast NEI) | 9.7.x | Nowa instalacja |
| JourneyMap (zamiast Rei's) | 5.8.x | Nowa instalacja |
| Jade (zamiast WAILA) | 5.x | Nowa instalacja |
| WorldEdit | 7.2.x | Nowa instalacja |
| FallingTree (zamiast Treecapitator) | 3.5.x | Nowa instalacja |

---

## 5. Priorytetyzacja konwersji

### Tier 1: Krytyczne (dużo danych na mapie)
1. Applied Energistics 2 - sieci ME
2. Mekanism - maszyny, transport, multibloki
3. Thermal Series - maszyny, ducty, energia
4. Bigger Reactors - reaktory multiblock
5. EnderStorage - ender chesty (współdzielony storage)

### Tier 2: Ważne (średnio danych)
6. Rechiseled (Chisel) - bloki dekoracyjne
7. ProjectRed - redstone, lampy, kable
8. Blood Magic - altar, runy, sygile
9. CC:Tweaked - komputery, programy Lua
10. Railcraft - tory, maszyny
11. Armourer's Workshop - custom skiny

### Tier 3: Storage i transport
12. Storage Drawers (JABBA/Better Storage)
13. Logistics Pipes → Pretty Pipes
14. Backpack → Sophisticated Backpacks
15. ForgeMultipart → CB Multipart

### Tier 4: Funkcjonalne (proste mapowanie)
16. Pam's HarvestCraft - uprawy, drzewa
17. Tinkers' Construct - narzędzia, smeltery
18. Reliquary - magiczne itemy
19. BiblioCraft → Builders Crafts & Additions
20. Furniture mods (MrCrayfish, Jammy)

### Tier 5: Koncepcyjna (nie 1:1)
21. BuildCraft → RFTools + Pretty Pipes
22. IC2 → Mekanism/Thermal
23. Thaumcraft → Ars Nouveau
24. Witchery → Occultism
25. Traincraft → Create + Steam'n'Rails
26. Flan's Mod → TaCZ + Realism Vehicle

### Tier 6: Własne mody / strata
27. Carpenter's Blocks - własny mod
28. Open Modular Turrets - strata/IE
29. Forestry - strata
30. Extra Utilities - częściowa strata

---

## 6. Źródła

- [CurseForge - Applied Energistics 2](https://www.curseforge.com/minecraft/mc-mods/applied-energistics-2)
- [CurseForge - Mekanism](https://www.curseforge.com/minecraft/mc-mods/mekanism)
- [CurseForge - Thermal Expansion](https://www.curseforge.com/minecraft/mc-mods/thermal-expansion)
- [CurseForge - Bigger Reactors](https://www.curseforge.com/minecraft/mc-mods/biggerreactors)
- [CurseForge - Rechiseled](https://www.curseforge.com/minecraft/mc-mods/rechiseled)
- [Modrinth - CC: Tweaked](https://modrinth.com/mod/cc-tweaked)
- [CurseForge - RFTools Builder](https://www.curseforge.com/minecraft/mc-mods/rftools-builder)
- [CurseForge - Blood Magic](https://www.curseforge.com/minecraft/mc-mods/blood-magic)
- [CurseForge - ProjectRed](https://www.curseforge.com/minecraft/mc-mods/project-red-core)
- [CurseForge - Ars Nouveau](https://www.curseforge.com/minecraft/mc-mods/ars-nouveau)
- [CurseForge - Storage Drawers](https://www.curseforge.com/minecraft/mc-mods/storage-drawers)
- [CurseForge - Sophisticated Backpacks](https://www.curseforge.com/minecraft/mc-mods/sophisticated-backpacks)
- [CurseForge - Ad Astra](https://www.curseforge.com/minecraft/mc-mods/ad-astra)
- [CurseForge - Waystones](https://www.curseforge.com/minecraft/mc-mods/waystones)
- [CurseForge - Tinkers' Construct](https://www.curseforge.com/minecraft/mc-mods/tinkers-construct)
- [CurseForge - FallingTree](https://www.curseforge.com/minecraft/mc-mods/falling-tree)

---

*Ostatnia aktualizacja: 2026-01-30*
