# Lista konwersji modów 1.7.10 → 1.18.2

> **STATUS: ZAKTUALIZOWANY PO ANALIZIE**
> Zweryfikowano na podstawie paczki modpack_1710 i dostępności modów online.
> Data aktualizacji: 2026-01-30

---

## Podsumowanie

### Statystyki paczki 1.7.10
| Kategoria | Liczba |
|-----------|--------|
| Mody główne (JAR) | 56 |
| Biblioteki/Core | 12 |

### Status konwersji
| Kategoria | Liczba modów |
|-----------|--------------|
| ✅ Bezpośrednia aktualizacja (1:1) | 21 |
| ⚠️ Automatyczna konwersja (mapper) | 5 |
| 🔧 Własna implementacja | 1 |
| 🔄 Konwersja "w duchu" | 8 |
| ❌ Kompletna strata / niepotrzebne | 16 |
| 📚 Biblioteki | 16 |
| ➕ Nowe mody 1.18.2 | 23+ |
| ⚡ Mody optymalizacyjne | 14 |

---

## 1. Bezpośrednia aktualizacja (1:1 lub ten sam mod) ✅

Mody z dostępną wersją 1.18.2 (ta sama nazwa lub oficjalny następca).

| # | Mod 1.7.10 | Mod 1.18.2 | Wersja | Źródło |
|---|------------|------------|--------|--------|
| 1 | Applied Energistics 2 | Applied Energistics 2 | 11.7.6 | [CurseForge](https://www.curseforge.com/minecraft/mc-mods/applied-energistics-2) |
| 2 | Armourer's Workshop | Armourer's Workshop | 3.2.7-beta | [CurseForge](https://www.curseforge.com/minecraft/mc-mods/armourers-workshop) |
| 3 | Backpack | Sophisticated Backpacks | 3.20.3 | [CurseForge](https://www.curseforge.com/minecraft/mc-mods/sophisticated-backpacks) |
| 4 | Big Reactors | **Bigger Reactors** / **Extreme Reactors** | 0.6.0 | [CurseForge](https://www.curseforge.com/minecraft/mc-mods/biggerreactors) |
| 5 | Blood Magic | Blood Magic | 3.2.6 | [CurseForge](https://www.curseforge.com/minecraft/mc-mods/blood-magic) |
| 6 | ComputerCraft | CC: Tweaked | 1.101.x | [Modrinth](https://modrinth.com/mod/cc-tweaked) |
| 7 | EnderStorage | EnderStorage | 2.9.x | [CurseForge](https://www.curseforge.com/minecraft/mc-mods/ender-storage-1-8) |
| 8 | Mekanism | Mekanism | 10.2.5 | [CurseForge](https://www.curseforge.com/minecraft/mc-mods/mekanism) |
| 9 | Mekanism Generators | Mekanism Generators | 10.2.5 | [CurseForge](https://www.curseforge.com/minecraft/mc-mods/mekanism-generators) |
| 10 | Mekanism Tools | Mekanism Tools | 10.2.5 | [CurseForge](https://www.curseforge.com/minecraft/mc-mods/mekanism-tools) |
| 11 | MrCrayfish Furniture Mod | MrCrayfish Furniture Mod | 7.0.x | [CurseForge](https://www.curseforge.com/minecraft/mc-mods/mrcrayfish-furniture-mod) |
| 12 | Pam's HarvestCraft | Pam's HarvestCraft 2 | 1.0.x | [CurseForge](https://www.curseforge.com/minecraft/mc-mods/pams-harvestcraft-2-food-core) |
| 13 | ProjectRed (wszystkie moduły) | ProjectRed | 4.17.0 | [CurseForge](https://www.curseforge.com/minecraft/mc-mods/project-red-core) |
| 14 | Railcraft | Railcraft Reborn | 5.x | [CurseForge](https://www.curseforge.com/minecraft/mc-mods/railcraft-reborn) |
| 15 | Reliquary | Reliquary Reincarnations | 1.4.x | [CurseForge](https://www.curseforge.com/minecraft/mc-mods/reliquary-v1-3) |
| 16 | Thermal Dynamics | Thermal Dynamics | 9.2.2 | [CurseForge](https://www.curseforge.com/minecraft/mc-mods/thermal-dynamics) |
| 17 | Thermal Expansion | Thermal Expansion | 9.2.2 | [CurseForge](https://www.curseforge.com/minecraft/mc-mods/thermal-expansion) |
| 18 | Thermal Foundation | Thermal Foundation | 9.2.2 | [CurseForge](https://www.curseforge.com/minecraft/mc-mods/thermal-foundation) |
| 19 | Tinkers' Construct | Tinkers' Construct | 3.7.2 | [CurseForge](https://www.curseforge.com/minecraft/mc-mods/tinkers-construct) |
| 20 | WorldEdit | WorldEdit | 7.2.x | [CurseForge](https://www.curseforge.com/minecraft/mc-mods/worldedit) |

### Uwagi do bezpośredniej aktualizacji

**Railcraft Reborn:** ⚠️ Może być niestabilny - alternatywnie rozważ **Create: Steam 'n' Rails**

**Extreme Reactors vs Bigger Reactors:**
- **Bigger Reactors** - nowszy mod inspirowany Big Reactors
- **Extreme Reactors** - oficjalny port Big Reactors
- Oba dostępne na 1.18.2, wybór zależy od preferencji

**Pam's HarvestCraft 2:** Podzielony na moduły:
- `pamhc2foodcore` - podstawowe jedzenie
- `pamhc2crops` - uprawy
- `pamhc2trees` - drzewa owocowe
- `pamhc2foodextended` - dodatkowe jedzenie

---

## 2. Automatyczna konwersja (wymaga mappera) ⚠️

Mody wymagające konwersji bloków/tile entities na inny mod.

| # | Mod 1.7.10 | Mod 1.18.2 | Złożoność | Uwagi |
|---|------------|------------|-----------|-------|
| 1 | **BiblioCraft** | **Supplementaries** + **FramedBlocks** + **Immersive Paintings** | Średnia | Meble → Supplementaries, tekstury → FramedBlocks, obrazy → Immersive Paintings |
| 2 | **IndustrialCraft 2** | **Mekanism** + **Thermal** | Wysoka | EU→FE (×4), mapowanie maszyn |
| 3 | **BuildCraft** (rury, maszyny) | **Pipez** + **RFTools Builder** | Wysoka | Rury item/fluid/power |
| 4 | **Better Storage** (JABBA) | **Storage Drawers** / **Sophisticated Storage** | Średnia | Beczki/skrzynie → szuflady |
| 5 | **Logistics Pipes** | **Pretty Pipes** / **AE2** / **XNet** | Średnia | Logistyka itemów |
| 6 | **Carpenter's Blocks** | **FramedBlocks** | Wysoka | Bloki "w bloku", kształty |
| 7 | **Chisel** | **Rechiseled** + **Chipped** | Średnia | Warianty dekoracyjne |
| 8 | **Better Storage** (Reinforced Chests) | **Iron Chests** / **Sophisticated Storage** | Średnia | Większe skrzynie |

### Szczegóły automatycznej konwersji

#### Carpenter's Blocks → FramedBlocks
| Element 1.7.10 | Element 1.18.2 | Priorytet |
|----------------|----------------|-----------|
| Carpenter's Block (z cover) | Framed Block (z teksturą) | WYSOKI |
| Carpenter's Slope | Framed Slope | WYSOKI |
| Carpenter's Stairs | Framed Stairs | ŚREDNI |
| Carpenter's Door | Framed Door | WYSOKI |
| Carpenter's Barrier | Framed Fence/Barrier | ŚREDNI |

**Uwaga:** Tekstury (cover) nie przeniosą się automatycznie - wymagany ręczny remap lub placeholdery.

#### Chisel → Rechiseled + Chipped
- **Rechiseled** - główne warianty bloków (stone, bricks, factory)
- **Chipped** - dodatkowe warianty dekoracyjne
- Nie ma 1:1 pokrycia wszystkich wariantów - wymagany mapping "kategoria → najbliższy odpowiednik"

---

## 3. Własna implementacja 🔧

Mody wymagające napisania własnego rozwiązania lub niestandardowego kodu konwersji.

| # | Mod 1.7.10 | Rozwiązanie 1.18.2 | Złożoność | Uwagi |
|---|------------|-------------------|-----------|-------|
| 1 | **Carpenter's Blocks** | **Własny mod uproszczony** | Bardzo wysoka | Block, Slope, Door, Barrier, Stairs |

### Plan własnego modu dla Carpenter's Blocks
**Minimum Viable Product:**
- Block (pokrywanie teksturą)
- Slope (skosy)
- Door (drzwi)
- Barrier (bariery/barierki)
- Stairs (schody)

**Technicznie:**
- Tile Entity przechowujący ID bloku-tekstury + orientację + wariant
- Custom renderer dla każdego typu
- Konwersja NBT: zachowanie tekstury i orientacji

**Alternatywa:** Jeśli własny mod nie jest możliwy, użyć **FramedBlocks** + ręczna rekonstrukcja

---

## 4. Konwersja "w duchu" / Funkcjonalne zamienniki 🔄

Mody zastępowane innymi o zbliżonej tematyce (strategia B).

| # | Mod 1.7.10 | Mod 1.18.2 | Uwagi | Ryzyko utraty danych |
|---|------------|------------|-------|---------------------|
| 1 | **Thaumcraft 4** + addony | **Ars Nouveau** + **Occultism** + **Botania** | Inny system magii - brak portu TC | WYSOKIE |
| 2 | **Witchery** | **Hexerei** / **Enchanted: Witchcraft** | Magia wiedźm - bliski klimat | WYSOKIE |
| 3 | **Flan's Mod** | **TaCZ** + **Immersive Vehicles** | Broń i pojazdy osobno | WYSOKIE (encje) |
| 4 | **Traincraft** | **Create** + **Steam'n'Rails** | Zupełnie inne budowanie pociągów | WYSOKIE (encje) |
| 5 | **BuildCraft** | **Pipez** + **RFTools Builder** + **XNet** | Rury + Quarry + logika | ŚREDNIE |
| 6 | **Treecapitator** | **FallingTree** | Ta sama funkcja | BRAK |
| 7 | **NEI** | **JEI** | Recipes viewer | BRAK |
| 8 | **Rei's Minimap** | **JourneyMap** / **Xaero's** | Minimapa + waypointy | NISKIE (tylko waypointy) |
| 9 | **Extra Utilities** | **ExU Reborn** + zestaw modów | Patrz sekcja 5 | ŚREDNIE |
| 10 | **Forestry** | **Productive Bees** + **Create** | Pszczoły + przetwórstwo | WYSOKIE |
| 11 | **BiblioCraft** | **Supplementaries** + **FramedBlocks** + **Immersive Paintings** | Meble, ramki, obrazy | ŚREDNIE |
| 12 | **Jammy Furniture** | **Macaw's Furniture** / **Handcrafted** | Meble | WYSOKIE |
| 13 | **Railcraft** | **Create: Steam'n'Rails** | Kolej (inna mechanika) | WYSOKIE |

### Szczegóły konwersji "w duchu"

#### Thaumcraft 4 → Ars Nouveau + Occultism + Botania
Thaumcraft 4 **nie ma portu na 1.18.2** (TC6 porzucony). Zamiast tego zestaw:
- **Ars Nouveau** - czary, rytuały, system progresji, enchanting
- **Occultism** - rytuały, summony, familiars, magiczny storage
- **Botania** - mana-tech, automatyzacja "magiczna"

Mapowanie funkcji:
| Thaumcraft | Zamiennik 1.18.2 |
|------------|------------------|
| Research/Thaumonomicon | Guidebooki (Patchouli) |
| Aspekty/Essentia | Source (Ars), Mana (Botania) |
| Infusion Altar | Enchanting Apparatus (Ars) |
| Golemy | Familiars (Occultism), Summony (Ars) |
| Węzły Vis | Source Jars, Mana Pools |

#### Witchery → Hexerei / Enchanted: Witchcraft
- **Hexerei** - bezpośrednio inspirowane Witchery (kociołki, ołtarze, rytuała)
- **Enchanted: Witchcraft** - folklor, wampiry, witch hunters

#### Flan's Mod → TaCZ + Immersive Vehicles
- Broń: **[TaCZ] Timeless and Classics Zero** (1.18.2 Forge)
- Pojazdy: **Immersive Vehicles** (IV) - samochody, pociągi, samoloty
- Opcjonalnie: **Immersive Aircraft** - dodatkowe samoloty

#### Traincraft → Create + Steam'n'Rails
Traincraft nie ma wersji >1.7.10. Zamiast tego:
- **Create** - system kolei w oparciu o kinetic energy
- **Create: Steam 'n' Rails** - rozszerzenie kolejowe (semafory, stacje, więcej torów)
- **Valkyrien Skies 2 + Eureka** - jeśli potrzebne statki/sterowce z bloków

---

## 5. Kompletna strata / Mapowanie na nowe mody ❌

Mody bez bezpośredniego portu - bloki usunięte lub zamienione na placeholdery.  
**Szczegółowe mapowanie funkcjonalności poniżej.**

| # | Mod 1.7.10 | Powód | Mapowanie na 1.18.2 | Strategia |
|---|------------|-------|---------------------|-----------|
| 1 | **Extra Utilities** | ❌ BRAK pełnego portu | **Extra Utilities Reborn** + osobne mody (zestaw) | Hybrydowa |
| 2 | CustomNPCs | Nieużywane | **Easy NPC** (jeśli potrzebne) | B |
| 3 | Forestry | Crashuje, laguje | **Productive Bees** + **Create**/**Thermal**/**Industrial Foregoing** | B |
| 4 | IC2 Nuclear Control | Brak portu | **CC: Tweaked** monitory + peryferia | B |
| 5 | Open Modular Turrets | Brak portu | **Immersive Engineering** turrets / **K-Turrets** | B |
| 6 | Thaumic Energistics | Wymaga Thaumcraft | **AE2** + **Occultism** (storage magii) | B |
| 7 | Thaumic Exploration | Wymaga Thaumcraft | **Ars Nouveau** | B |
| 8 | Thaumic Horizons | Wymaga Thaumcraft | **Ars Nouveau** (summony) | B |
| 9 | Thaumic Tinkerer | Wymaga Thaumcraft | **Ars Nouveau** (enchanting) | B |
| 10 | Statues | Brak portu | **Statues (ShyNieke)** 1.18.2 Forge | B |
| 11 | PowerConverters | Niepotrzebny (FE natywne) | *Nie potrzeba* (wszyscy używają FE) | - |
| 12 | CraftGuide | Zastąpiony przez JEI | **JEI** | C |
| 13 | NoMoreRecipeConflict | Niepotrzebny | **Polymorph** (jeśli potrzebny) | C |
| 14 | HelpFixer | Niepotrzebny | *Nie potrzeba* | - |
| 15 | FastCraft | Niepotrzebny | **Rubidium** + **Starlight** + **FerriteCore** | C |
| 16 | Opis | Brak portu | **Spark** (profiler) + **Observable** | C |

### Szczegółowe mapowanie usuniętych modów

#### Extra Utilities → Zestaw modów 1.18.2
| Funkcja ExU | Mod docelowy 1.18.2 | Uwagi |
|-------------|---------------------|-------|
| Cursed Earth (farmy mobów) | **Cursed Earth** (osobny mod) | Taka sama funkcja |
| Angel Block | **Angel Block Renewed** lub **Angel Block: Restored** | Blok w powietrzu |
| Mega/Magnum Torch | **Torchmaster** lub **Magnum Torch** | Blokada spawnu w promieniu |
| Transfer Nodes/Pipes | **Pipez** lub **XNet** | Transport item/fluid/energy |
| Ender Quarry | **RFTools Builder** (Quarry Card) | Wydobycie obszarowe |
| Generatory RF | **Mekanism Generators** / **Thermal** | Inne generatory |
| Ender-Thermic Pump | **Mekanism** / **Create** | Pompy |

#### BiblioCraft → Zestaw modów 1.18.2

**Uwaga:** BiblioCraft nie ma portu na 1.18.2. Konwersja wymaga zestawu modów.

| Funkcja BiblioCraft | Mod docelowy 1.18.2 | Blok/Element | Uwagi |
|---------------------|---------------------|--------------|-------|
| **Półki meblowe** | **Supplementaries** | `ItemShelfBlock` | Ekspozycja przedmiotów |
| **Regały na książki** | **Supplementaries** | `BookPileBlock` | Stos książek (inna forma) |
| **Zegar** | **Supplementaries** | `ClockBlock` | Wyświetlanie czasu |
| **Latarnia/Lampa** | **Supplementaries** | `WallLanternBlock`, `EndLampBlock` | Oświetlenie |
| **Znak (Fancy Sign)** | **Supplementaries** | `HangingSignBlock` | Wiszący znak |
| **Piedestał** | **Supplementaries** | `PedestalBlock` | Ekspozycja broni |
| **Globus** | **Supplementaries** | `GlobeBlock` | Dekoracja |
| **Worek** | **Supplementaries** | `SackBlock` | Storage |
| **Sejf** | **Supplementaries** | `SafeBlock` | Zabezpieczony storage |
| **Tablica** | **Supplementaries** | `BlackboardBlock` | Rysowanie |
| **Słoik** | **Supplementaries** | `JarBlock` | Na dowolne przedmioty |
| **Meble z teksturami** | **FramedBlocks** | `Framed*Block` | System "coverable blocks" |
| **Customowe obrazy** | **Immersive Paintings** | `PaintingEntity` | Własne obrazy z plików |
| **Stół (Table)** | **BlockCarpentry** / **Handcrafted** | `FrameBlock` / różne | Stoły |
| **Krzesła** | **Handcrafted** | Różne | System siedzeń |

**Nie wymagają konwersji (nieistotne):**
- Typesetting Table / Printing Press - funkcja druku nieistotna
- Tape Measure / Atlas - można zastąpić innymi modami (JourneyMap)
- Redstone Book - funkcja specyficzna dla BC

**Konwersja NBT:**
```java
// FramedBlocks - przykład
BiblioCraft: TileEntityFramedChest
  → frameTexture: String (ID bloku)
  
FramedBlocks: FramedBlockEntity
  → camoState: BlockState (stan bloku jako tekstura)
  
// Immersive Paintings - przykład
BiblioCraft: TileEntityPainting
  → resourceLocation: "bibliocraft:paintings/custom/xxx.png"
  
ImmersivePaintings: PaintingEntity
  → image: String (zarejestrowana nazwa obrazu)
```

#### Forestry → Zestaw modów 1.18.2
| Funkcja Forestry | Mod docelowy 1.18.2 | Uwagi |
|------------------|---------------------|-------|
| Pszczoły (Apiary/Alveary) | **Productive Bees** | System uli i pszczół |
| Maszyny (Centrifuge, Squeezer) | **Create** (processing) / **Thermal** | Przetwórstwo |
| Multifarm | **Create** harvestery / **Industrial Foregoing** | Automatyczne farmy |
| Backpacki | **Sophisticated Backpacks** | (już na liście) |
| Mail | **Ender Mail** (opcjonalnie) | System poczty |

#### Open Modular Turrets → Alternatywy 1.18.2
| Funkcja OMT | Mod docelowy 1.18.2 | Uwagi |
|-------------|---------------------|-------|
| Turrety obronne | **Immersive Engineering** (kilka typów) | Ograniczony wybór |
| Modularne turrety | **K-Turrets** | Bardziej zbliżone do OMT |

#### IC2 Nuclear Control → Monitoring 1.18.2
| Funkcja IC2NC | Mod docelowy 1.18.2 | Uwagi |
|---------------|---------------------|-------|
| Monitory temperatury | **CC: Tweaked** + integracje | Komputery + sensory |
| Alarmy (Howler/Industrial) | **CC: Tweaked** + redstone | Brak bezpośredniego odpowiednika |

#### Statues → Port 1.18.2
- **Statues (ShyNieke)** - dostępny na Forge 1.18.2 (Modrinth)
- NIE jest to ten sam mod, więc NBT się nie przeniesie
- Mapowanie: `statues:statue` → `statues:statue` (inny format danych)

#### Thaumic addony (Energistics/Exploration/Horizons/Tinkerer)
Wszystkie wymagają Thaumcraft który **nie ma portu na 1.18.2**:
- Thaumic Energistics → AE2 do przechowywania, **Occultism** do "magicznego" storage
- Exploration/Horizons/Tinkerer → **Ars Nouveau** (system magii/czarów) + **Botania**



### Mody do weryfikacji na mapie:
- **Growthcraft** - Wymaga sprawdzenia dostępności
- **Jammy Furniture** - Wymaga sprawdzenia dostępności
- **Placeable Items** - Wymaga sprawdzenia dostępności
- **Enchanting Plus** - Wymaga sprawdzenia dostępności

---

## 6. Biblioteki i zależności

### Nie wymagają konwersji danych - tylko instalacja odpowiedników

| Biblioteka 1.7.10 | Odpowiednik 1.18.2 | Uwagi |
|-------------------|-------------------|-------|
| **Baubles** | **Curios API** | Sloty na akcesoria |
| **CodeChickenCore** | *(wbudowany w CCL)* | - |
| **CodeChickenLib** | **CodeChicken Lib** | Wymagany przez EnderStorage |
| **CoFHCore** | **CoFH Core** | Wymagany przez Thermal |
| **ForgeMultipart** | **CB Multipart** | Microblocks, wymagany przez ProjectRed |
| **ForgeRelocation** | - | Nie potrzebny (funkcjonalność w Create) |
| **MrTJPCore** | *(wbudowany w ProjectRed)* | - |
| **Bookshelf** | **Bookshelf** | Biblioteka dla innych modów |
| **bspkrsCore** | - | Nie potrzebny (tylko dla Treecapitator) |
| **GollumCoreLib** | - | Nie potrzebny |
| **iChunUtil** | - | Nie potrzebny |
| **MobiusCore** | - | Nie potrzebny (biblioteka dla Opis) |
| **AsieLib** | - | Nie potrzebny (biblioteka dla Statues 1.7.10) |
| **LiteLoader** | - | Nie potrzebny (loader dla Omniscience) |
| **buildcraft-compat** | - | Nie potrzebny (BC usunięty) |

### Mapowanie bibliotek per-mod
| Mod 1.7.10 | Biblioteki 1.7.10 | Biblioteki 1.18.2 |
|------------|-------------------|-------------------|
| ProjectRed | MrTJPCore, ForgeMultipart | CB Multipart, CodeChickenLib |
| EnderStorage | CodeChickenCore, CodeChickenLib | CodeChickenLib |
| Statues | AsieLib | *(brak - nowy mod Statues nie wymaga)* |
| Thermal Series | CoFHCore | CoFH Core |
| Opis | MobiusCore | *(brak - zastąpiony Sparkiem)* |
| Treecapitator | bspkrsCore | *(brak - zastąpiony FallingTree)* |

---

## 7. Nowe mody 1.18.2 ➕

### Create + Ekosystem (zamiennik Traincraft / BuildCraft)
| Mod | Funkcja | Zastępuje |
|-----|---------|-----------|
| **Create** | Mechanika, kinetic power | BuildCraft maszyny |
| **Create Crafts & Additions** | Energia elektryczna (kompatybilność FE) | - |
| **Create: Steam 'n' Rails** | Pociągi, tory, semafory | Traincraft, Railcraft |
| **Create Big Cannons** | Artyleria | Flan's Mod (częściowo) |
| **Create: Interiors** | Dekoracje | BiblioCraft (częściowo) |
| **Clockwork** | Integracja z Valkyrien Skies | - |

### Valkyrien Skies (statki/pojazdy)
| Mod | Funkcja | Zastępuje |
|-----|---------|-----------|
| **Valkyrien Skies 2** | Fizyka statków/pojazdów z bloków | Traincraft (sterowce) |
| **Eureka** | Sterowce, łodzie podwodne | - |
| **Clockwork** | Integracja z Create | - |

### Immersive Engineering + Pojazdy
| Mod | Funkcja | Zastępuje |
|-----|---------|-----------|
| **Immersive Engineering** | Multibloki, przemysł | BuildCraft, IC2 (częściowo) |
| **Immersive Vehicles (IV)** | Samochody, pociągi, samoloty | Flan's Mod (pojazdy) |
| **Immersive Aircraft** | Dodatkowe samoloty | Flan's Mod (samoloty) |
| **Just Enough Immersive Multiblocks** | Podgląd w JEI | - |

### Magia (zamiennik Thaumcraft + Witchery)
| Mod | Funkcja | Zastępuje |
|-----|---------|-----------|
| **Ars Nouveau** | System magii, czary, rytuały | Thaumcraft (główny zamiennik) |
| **Ars Creo** | Integracja Ars z Create | - |
| **Occultism** | Demony, summony, familiars, storage | Witchery + Thaumic Energistics |
| **Botania** | Mana-tech, automatyzacja "magiczna" | Thaumcraft (automatyzacja) |
| **Hexerei** | Magia wiedźm, kociołki, ołtarze | Witchery (najbliższy klimat) |
| **Enchanted: Witchcraft** | Folklor, wampiry, witch hunters | Witchery (elementy mroczne) |

### Broń (zamiennik Flan's Mod)
| Mod | Funkcja | Zastępuje |
|-----|---------|-----------|
| **[TaCZ] Timeless and Classics Zero** | Broń palna, amunicja, attachmenty | Flan's Mod (broń) |
| **Immersive Vehicles** | System pojazdów + broń montowana | Flan's Mod (pojazdy) |

### Storage (zamiennik Better Storage / JABBA / Forestry)
| Mod | Funkcja | Zastępuje |
|-----|---------|-----------|
| **Storage Drawers** | Szuflady na itemy | JABBA, Better Storage |
| **Sophisticated Storage** | Skrzynie/barrels z upgrade'ami | Better Storage, Forestry crates |
| **Iron Chests** | Większe skrzynie | Better Storage reinforced |

### Meble i dekoracje (zamiennik BiblioCraft / Jammy Furniture)
| Mod | Funkcja | Zastępuje |
|-----|---------|-----------|
| **Supplementaries** | Półki, globusy, latarnie, tablice | BiblioCraft (główne meble) |
| **FramedBlocks** | Bloki przyjmujące wygląd innych bloków | BiblioCraft Framed, Furniture Paneler |
| **BlockCarpentry** | "Coverable blocks" (frames/illusions) | BiblioCraft (alternatywa dla FramedBlocks) |
| **Handcrafted** | Meble, krzesła, stoły, kanapy | BiblioCraft, Jammy Furniture |
| **Immersive Paintings** | Customowe obrazy z plików | BiblioCraft Paintings |
| **Another Furniture** | Proste, spójne meble | BiblioCraft (uzupełnienie) |
| **Chipped** | Warianty dekoracyjne bloków | Chisel (uzupełnienie) |
| **Rechiseled** | Warianty dekoracyjne bloków | Chisel (główny zamiennik) |
| **FramedBlocks** | Bloki "w bloku" (cover system) | Carpenter's Blocks (alternatywa) |

### Dekoracje (zamiennik BiblioCraft / Jammy Furniture)
| Mod | Funkcja | Zastępuje |
|-----|---------|-----------|
| **Supplementaries** | Vanilla+ dekoracje, automatyka | BiblioCraft (funkcjonalność) |
| **Handcrafted** | Meble, wyposażenie wnętrz | BiblioCraft, Jammy Furniture |
| **Macaw's Furniture** | Duży zestaw mebli | Jammy Furniture |
| **Another Furniture** | Proste, spójne meble | MrCrayfish Furniture |
| **Chipped** | Warianty dekoracyjne bloków | Chisel (uzupełnienie) |
| **Rechiseled** | Warianty dekoracyjne bloków | Chisel (główny zamiennik) |

### Transport / Logistyka (zamiennik BuildCraft / Logistics Pipes)
| Mod | Funkcja | Zastępuje |
|-----|---------|-----------|
| **Pipez** | Rury item/fluid/energy | BuildCraft pipes |
| **Pretty Pipes** | Rury z filtrami, request system | Logistics Pipes (uproszczony) |
| **XNet** | Sieć kablowa, routing, logika | BuildCraft gates, LP logic |
| **Integrated Dynamics** | Logika warunkowa, "programowalne" sieci | BuildCraft gates, LP advanced |
| **RFTools Builder** | Builder, Quarry, Shape cards | BuildCraft Builder/Quarry |

### Turrety (zamiennik Open Modular Turrets)
| Mod | Funkcja | Zastępuje |
|-----|---------|-----------|
| **Immersive Engineering** | Kilka typów turretek | OMT (ograniczony wybór) |
| **K-Turrets** | Modularne turrety | OMT (najbliższy odpowiednik) |

### Pszczoły (zamiennik Forestry)
| Mod | Funkcja | Zastępuje |
|-----|---------|-----------|
| **Productive Bees** | System uli, pszczoły, produkty | Forestry (pszczelarstwo) |

### Utility / QoL
| Mod | Funkcja | Zastępuje |
|-----|---------|-----------|
| **Waystones** | Teleportacja, warp stones | Warp Book (z Forestry) |
| **Ender Mail** | System poczty | Forestry Mail |
| **Polymorph** | Rozwiązywanie konfliktów recept | NoMoreRecipeConflict |
| **Torchmaster** | Mega Torch (blokada spawnu) | Extra Utilities |
| **Angel Block Renewed** | Blok w powietrzu | Extra Utilities |
| **Carry On** | Przenoszenie bloków/TE | Better Storage Cardboard Box |
| **Packing Tape** | Pakowanie bloków/TE | Better Storage Cardboard Box |

### Narzędzia / Diagnostic
| Mod | Funkcja | Zastępuje |
|-----|---------|-----------|
| **JEI** | Przegląd receptur | NEI, CraftGuide |
| **JourneyMap** / **Xaero's** | Minimapa, waypointy | Rei's Minimap |
| **Jade** | Tooltips, informacje o blokach | WAILA |
| **FallingTree** | Ścinanie drzew | Treecapitator |
| **Spark** | Profiler, diagnostyka TPS | Opis |
| **Observable** | Wizualizacja "co laguje" | LagGoggles |

### Extra Utilities → Zestaw modów
| Funkcja ExU | Mod 1.18.2 |
|-------------|------------|
| Cursed Earth | **Cursed Earth** (osobny mod) |
| Angel Block | **Angel Block Renewed** |
| Mega Torch | **Torchmaster** |
| Transfer Nodes | **Pipez** / **XNet** |
| Ender Quarry | **RFTools Builder** |
| Generatory | **Mekanism** / **Thermal** |
| Ender-Thermic Pump | **Mekanism** / **Create** |

---

## 8. Mody optymalizacyjne ⚡ (zamiennik FastCraft)

| Mod | Funkcja | Odpowiednik FastCraft |
|-----|---------|----------------------|
| **Rubidium** / **Embeddium** | Renderer (Sodium port dla Forge) | Rendering |
| **Starlight** | Przebudowa silnika oświetlenia | Światło/chunki |
| **FerriteCore** | Redukcja użycia RAM | Pamięć |
| **Entity Culling** | Culling niewidocznych entities | Rendering |
| **Clumps** | Grupowanie XP orbs | Ticki |
| **FastWorkbench** | Szybszy crafting | Crafting |
| **Lazy DataFixerUpper** | Szybszy start | Startup |
| **Smooth Chunk Save** | Optymalizacja zapisu | Zapis świata |
| **Oculus** | Shadery (opcjonalne) | - |

**Zalecany minimalny zestaw:** Rubidium + Starlight + FerriteCore

---

## 9. Mody do IGNOROWANIA w konwersji (konwersja nie wymagana) 📋

Poniższe mody **nie wymagają konwersji danych świata** - są to biblioteki, mody klientowe, narzędzia diagnostyczne lub mody serwerowe, które nie pozostawiają trwałych bloków/TE w chunkach.

| Mod 1.7.10 | Typ | Powód pominięcia | Zamiennik 1.18.2 |
|------------|-----|------------------|------------------|
| **Treecapitator** | Klientowy/QoL | Nie zostawia bloków | **FallingTree** (instalować osobno) |
| **Baubles** | Biblioteka/API | Tylko API slotów | **Curios API** (instalować osobno) |
| **Bookshelf** | Biblioteka | Tylko dependency | **Bookshelf** (nowa wersja) |
| **bspkrsCore** | Biblioteka | Tylko dla Treecapitator | *Nie potrzebna* |
| **CodeChickenCore** | Biblioteka | Wbudowany w CCL | *Nie potrzebna* |
| **CraftGuide** | Klientowy/QoL | Przeglądarka receptur | **JEI** (instalować osobno) |
| **CustomNPCs** | Serwerowy | Nieużywane na mapie | **Easy NPC** (opcjonalnie) |
| **FastCraft** | Optymalizacja | Nie zostawia bloków | **Rubidium + Starlight + FerriteCore** |
| **Forestry** | Pominięty | Crashuje, laguje | *Brak konwersji* |
| **ForgeEssentials** | Serwerowy | Komendy, permisje | Nowsza wersja FE lub inne mody |
| **iChunUtil** | Biblioteka | Dependency iChun | *Nie potrzebna* |
| **LiteLoader** | Loader | Loader dla litemodów | *Nie potrzebny* |
| **MobiusCore** | Biblioteka | Dla Opis | *Nie potrzebna* |
| **MrTJPCore** | Biblioteka | Wbudowany w ProjectRed | *Nie potrzebna* |
| **NEI** | Klientowy/QoL | Przeglądarka itemów | **JEI** (instalować osobno) |
| **NoMoreRecipeConflict** | Klientowy/QoL | Konflikty receptur | **Polymorph** (opcjonalnie) |
| **Opis** | Diagnostyczny | Profiler TPS | **Spark** (instalować osobno) |
| **Placeable Items** | Klientowy/Dekoracja | *Do weryfikacji* | **Placeable Items** (jest na 1.18.2) |
| **PowerConverters** | Techniczny | Niepotrzebny (FE natywne) | *Nie potrzeba* |
| **RadarBro** | Klientowy/QoL | Radar encji | **Xaero's Minimap** (ma Entity Radar) |
| **Rei's Minimap** | Klientowy/QoL | Minimapa | **JourneyMap** / **Xaero's** |
| **uuidoffline** | Serwerowy | Patch UUID offline | *Nie potrzebna* (UUID natywne) |
| **WorldEdit** | Narzędzie | Edycja mapy | **WorldEdit** (instalować osobno) |

> **Legenda:** Mody oznaczone jako "instalować osobno" należy dodać do paczki 1.18.2, ale nie wymagają konwersji danych z mapy 1.7.10.

---

## 10. UWAGI krytyczne do konwersji ⚠️

### UWAGA 1: Armourer's Workshop - NA KOŃCU KOLEJKI
Armourer's Workshop ma wersję 1.18.2 (3.2.7-beta), ale:
- Konwersja jest **skomplikowana** (formaty skinów, NTE)
- Zalecane wykonanie **na samym końcu** po wszystkich innych modach
- Wymaga weryfikacji kompatybilności NBT skinów

### UWAGA 2: Carpenter's Blocks - WŁASNY MOD wymagany
Oprócz FramedBlocks potrzebny **własny mod** dla:
- Collapsible Block (zmienna wysokość 4 wierzchołków)
- Zgodność z oryginalnym Carpenter's Blocks z 1.7.10

### UWAGA 3: Enchanting Plus - DO WERYFIKACJI
Sprawdzić czy **Enchanting Infuser** jest poprawnym zamiennikiem:
- Jeśli TAK → użyć do konwersji
- Jeśli NIE → mapować na **Apotheosis**

### UWAGA 4: Placeable Items - DO WERYFIKACJI
Sprawdzić dostępność i kompatybilność wersji 1.18.2:
- Jeśli jest port → można konwertować
- Jeśli nie ma → dekoracje jako placeholdery

### UWAGA 5: Growthcraft - DO WERYFIKACJI
Sprawdzić dostępność poszczególnych modułów Growthcraft na 1.18.2:
- Core, Cellar, Apple, Bamboo, Bees, Fishtrap, Grapes, Hops, Milk, Rice

### UWAGA 6: Jammy Furniture - DO WERYFIKACJI
Sprawdzić czy na mapie są bloki tego modu:
- Jeśli TAK → mapować na **Macaw's Furniture** lub **Handcrafted**
- Jeśli mało używany → zamiana na placeholdery

---

## 11. Priorytetyzacja etapów konwersji

```
ETAP 0: Infrastruktura
        ├── Parser NBT 1.7.10
        ├── Writer NBT 1.18.2
        ├── Framework testowy
        ├── Narzędzie analizy mapy
        └── Tabela remapów ID (stare → nowe)

ETAP 1: Proste bloki dekoracyjne (NAJŁATWIEJSZY)
        ├── Rechiseled (Chisel) - tylko bloki, brak TE
        └── Chipped (uzupełnienie Chisel)

ETAP 2: Storage i plecaki
        ├── Sophisticated Backpacks (Backpack)
        ├── Storage Drawers (Better Storage/JABBA)
        └── Iron Chests (Better Storage reinforced)

ETAP 3: EnderStorage (kolorowe skrzynie)
        └── Inventory + metadata (kolor) + zawartość

ETAP 4: Thermal Series (tech podstawowy)
        ├── Maszyny (furnace, pulverizer, etc.)
        ├── Dynamo (generatory RF)
        ├── Ducty (item/fluid/energy)
        └── Konwersja RF→FE (1:1)

ETAP 5: Applied Energistics 2
        ├── Sieci ME
        ├── Storage cells (zawartość!)
        ├── P2P tunnels
        └── Crafting system

ETAP 6: Mekanism (tech zaawansowany)
        ├── Maszyny (crusher, enrichment, etc.)
        ├── Cables/Pipes/Tubes
        ├── Multibloki (fission/fusion)
        └── Digital Miner

ETAP 7: Energy (reaktory)
        ├── Bigger Reactors / Extreme Reactors
        └── Multibloki reaktorów

ETAP 8: Magia (Blood Magic)
        ├── Blood Altar
        ├── Runy
        └── Sygile

ETAP 9: Redstone + Komputery
        ├── ProjectRed (wiring, gates, logic)
        ├── CC:Tweaked (komputery, turtles)
        └── CB Multipart (microblocks)

ETAP 10: Konwersja "w duchu" - Tech
        ├── IC2 → Mekanism/Thermal/FTBIC
        ├── BuildCraft → Pipez/XNet/RFTools Builder
        └── Logistics Pipes → Pretty Pipes/XNet/AE2

ETAP 11: Konwersja "w duchu" - Magia
        ├── Thaumcraft → Ars Nouveau + Occultism
        ├── Witchery → Hexerei / Enchanted
        └── Thaumic addony → AE2 + Ars Nouveau

ETAP 12: Meble i dekoracje
        ├── BiblioCraft → Supplementaries + Handcrafted
        ├── Jammy Furniture → Macaw's Furniture
        └── MrCrayfish → MrCrayfish (bezpośredni port)

ETAP 13: Carpenter's Blocks / FramedBlocks
        ├── Własny mod (uproszczony) LUB
        └── FramedBlocks + ręczna rekonstrukcja

ETAP 14: Pojazdy i transport
        ├── Traincraft → Create: Steam'n'Rails
        ├── Flan's Mod → TaCZ + Immersive Vehicles
        └── Statues → Statues (ShyNieke)

ETAP 15: Armourer's Workshop (NA KOŃCU - złożona konwersja skinów)
        ├── Warsztaty, biblioteki, projektory
        ├── Eksport/import skinów
        └── Weryfikacja kompatybilności NBT

ETAP 16: Extra Utilities - hybrydowo
        ├── Cursed Earth → Cursed Earth mod
        ├── Angel Block → Angel Block Renewed
        ├── Mega Torch → Torchmaster
        └── Ender Quarry → RFTools Builder
```

---

## 12. Otwarte pytania

### ✅ Rozwiązane
- [x] Armourer's Workshop - JEST wersja 1.18.2 (3.2.7-beta)
- [x] Extra Utilities - mapowanie na zestaw modów (ExU Reborn + osobne)
- [x] Railcraft Reborn - używamy mimo niestabilności (alternatywa: Create: Steam'n'Rails)
- [x] Statues - JEST port na 1.18.2 (ShyNieke)
- [x] Forestry - mapowanie na Productive Bees + Create/Thermal

### Do weryfikacji na mapie
- [ ] **Carpenter's Blocks** - które bloki są najczęściej używane? (Block, Slope, Door, Stairs?)
- [ ] **IC2** - jakie maszyny są na mapie? (macerator, furnace, nuclear reactor?)
- [ ] **Big Reactors** - czy są multibloki reaktorów/turbin?
- [ ] **AE2** - ile sieci ME jest na mapie? (skala konwersji)
- [ ] **Flan's Mod** - czy są bloki/zawartość na mapie? (broń, pojazdy, workbench'e)
- [ ] **Traincraft** - status torów/pociągów (czy warto konwertować na Create?)
- [ ] **Thaumcraft** - czy są istotne struktury (ołtarze, biblioteki, golemy)?
- [ ] **Extra Utilities** - które bloki są używane? (Cursed Earth, Angel Block, Quarry?)

### Decyzje projektowe
- [ ] **Turrety:** Czy używać Immersive Engineering (ograniczone) czy K-Turrets (bardziej zbliżone)?
- [ ] **Thaumcraft:** Jak obsłużyć research progress? (zrzut do skrzynek + odtworzenie w Ars Nouveau?)
- [ ] **Traincraft:** Czy konwertować tory na Create: Steam'n'Rails czy zostawić jako placeholdery?
- [ ] **Railcraft:** Railcraft Reborn (niestabilny) vs Create: Steam'n'Rails (inna mechanika)?
- [ ] **Carpenter's Blocks:** Własny mod (czasochłonny) vs FramedBlocks + ręczna naprawa?
- [ ] **ExU Quarry:** RFTools Builder (zaawansowany) vs inny mod quarry?

### Do weryfikacji - dostępność modów 1.18.2
- [ ] **Growthcraft** - dostępność wersji 1.18.2 (częściowo dostępne jako osobne mody?)
- [ ] **Jammy Furniture** - dostępność (zastąpione przez Macaw's/Handcrafted)
- [ ] **Placeable Items** - dostępność wersji 1.18.2 (TAK - jest port)

---

## 13. Różnice względem oryginalnej listy Excel

| Zmiana | Opis |
|--------|------|
| Chisel → Rechiseled | Jak w oryginale |
| BuildCraft → Pipez + XNet + RFTools Builder | Rozszerzony zestaw zamienników |
| ✅ Armourer's Workshop | Jest wersja 1.18.2 (3.2.7-beta) |
| ✅ Statues | JEST port na 1.18.2 (ShyNieke) |
| ⚠️ Extra Utilities | Mapowanie na zestaw modów (ExU Reborn + osobne) |
| ⚠️ Forestry | Mapowanie na Productive Bees + Create/Thermal |
| ➕ Tinkers' Construct | Dodany - jest wersja 1.18.2 |
| ➕ Storage Drawers | Dodany jako zamiennik JABBA/Better Storage |
| ➕ Sophisticated Storage | Dodany jako zamiennik Better Storage |
| ➕ Waystones | Dodany jako zamiennik teleportacji |
| ➕ Railcraft Reborn | Dodany do bezpośredniej aktualizacji (z ostrzeżeniem) |
| ➕ FramedBlocks | Dodany jako alternatywa dla Carpenter's Blocks |
| ➕ CB Multipart | Dodany (wymagany przez ProjectRed) |
| ➕ Create + ekosystem | Dodany (zamiennik Traincraft/BuildCraft) |
| ➕ Ars Nouveau + Occultism | Dodany (zamiennik Thaumcraft + Witchery) |
| ➕ TaCZ | Dodany (zamiennik broni z Flan's Mod) |
| ➕ Immersive Vehicles | Dodany (zamiennik pojazdów z Flan's Mod) |
| ➕ Mody ignorowane | Dodana sekcja 22 modów nie wymagających konwersji |
| ➕ UWAGI krytyczne | Dodana sekcja 6 uwag do konwersji |

### Podsumowanie zmian
- **Z 16 modów "do usunięcia"** - większość ma teraz mapowanie na nowe mody
- **Statues** - przeniesiony z "usunięte" do "bezpośredniej aktualizacji" (jest port)
- **Extra Utilities** - rozwinięte szczegółowe mapowanie na zestaw modów
- **Forestry** - rozwinięte mapowanie na Productive Bees + inne
- **Thaumcraft + addony** - dodane szczegółowe mapowanie na Ars Nouveau + Occultism

## 14. Pełna lista modów z paczki modpack_1710

### Mody główne (56)
```
appliedenergistics2-rv3-beta-6.jar
Armourers-Workshop-1.7.10-0.48.5.jar
backpack-2.0.1-1.7.x.jar
Better-Storage-Mod-1.7.10.jar
BiblioCraftv1.11.7MC1.7.10.jar
BigReactors-0.4.3A.jar
BloodMagic-1.7.10-1.3.3-17.jar
buildcraft-7.1.23.jar
Carpenter's Blocks v3.3.8.1.jar
Chisel-2.9.5.11.jar
ComputerCraft1.75.jar
CraftGuide-Mod-1.7.10.jar
CustomNPCs_1.7.10d.jar
EnchantingPlus-1.7.10-4.0.0.74.jar
EnderStorage-1.7.10-1.4.7.38.jar
extrautilities-1.2.12.jar
Flans_Mod-1.7.10-4.10.0.jar
forestry_1.7.10-4.2.16.64.jar
forgeessentials-1.7.10-1.4.4.1187.jar
growthcraft-1.7.10-2.7.2-complete.jar
IC2NuclearControl-2.4.3a.jar
industrialcraft-2-2.2.827-experimental.jar
Jammy-Furniture-Reborn-Mod-1.7.10.jar
logisticspipes-0.9.3.132.jar
Mekanism-1.7.10-9.1.1.jar
MekanismGenerators-1.7.10-9.1.1.jar
MekanismTools-1.7.10-9.1.1.jar
MrCrayfishFurnitureModv3.4.8.jar
NotEnoughItems-1.7.10-1.0.5.120.jar
OpenModularTurrets-1.7.10-2.2.11-245.jar
Pam's HarvestCraft 1.7.10Lb.jar
Placeable-Items-Mod-1.7.10.jar
PowerConverters-1.7.10_3.2.1.jar
ProjectRed-1.7.10-4.7.0pre12.95-Base.jar
ProjectRed-1.7.10-4.7.0pre12.95-Compat.jar
ProjectRed-1.7.10-4.7.0pre12.95-Fabrication.jar
ProjectRed-1.7.10-4.7.0pre12.95-Integration.jar
ProjectRed-1.7.10-4.7.0pre12.95-Lighting.jar
ProjectRed-1.7.10-4.7.0pre12.95-Mechanical.jar
ProjectRed-1.7.10-4.7.0pre12.95-World.jar
Railcraft_1.7.10-9.12.2.0.jar
Reliquary-1.7.10-1.2.1.483.jar
statues-1.7.10-2.1.4.jar
Thaumcraft-1.7.10-4.2.3.5.jar
thaumcraftneiplugin-1.7.10-1.7a.jar
thaumicenergistics-1.0.0.5.jar
ThaumicExploration-1.7.10-1.1-55.jar
thaumichorizons-1.7.10-1.1.9.jar
ThaumicTinkerer-2.5-1.7.10-542.jar
ThermalDynamics-[1.7.10]1.2.1-172.jar
ThermalExpansion-[1.7.10]4.1.5-248.jar
ThermalFoundation-[1.7.10]1.2.6-118.jar
Traincraft-4.3.5_014.jar
witchery-1.7.10-0.24.1.jar
worldedit-forge-mc1.7.10-6.1.1.jar
[1.7.10]Treecapitator-universal-2.0.4.jar
```

### Biblioteki (16)
```
[1.7.10]bspkrsCore-universal-6.15.jar
AsieLib-1.7.10-0.4.8.jar
Baubles-1.7.10-1.0.1.10.jar
Bookshelf-1.7.10-1.0.4.172.jar
buildcraft-compat-7.1.7.jar
CodeChickenCore-1.7.10-1.0.7.47.jar
CodeChickenLib-1.7.10-1.1.3.140.jar
CoFHCore-[1.7.10]3.1.4-329.jar
fastcraft-1.25.jar
ForgeMultipart-1.7.10-1.2.0.345.jar
ForgeRelocation-1.7.10-0.0.1.4.jar
ForgeRelocationFMP-1.7.10-0.0.1.2.jar
GollumCoreLib-2.0.0-1.7.10.jar
iChunUtil-4.2.3.jar
MobiusCore-1.2.5_1.7.10.jar
MrTJPCore-1.7.10-1.1.0.33.jar
```

### Pomocnicze/narzędziowe
```
HelpFixer-1.0.7.jar
liteloader-1.7.10.jar
mod_Omniscience_1.0.1.litemod
NoMoreRecipeConflict-0.31.7.10.jar
Opis-1.2.5_1.7.10.jar
Reis-Minimap-Mod-1.7.10.jar
uuidoffline-1.0.jar
```

---

*Ostatnia aktualizacja: 2026-02-01 (v3 - po analizie mod_mapping_indepth)*
*Spójne z: docs/mod_mapping_indepth/to/konwersja_1710_do_1182_mapowanie_modow_cz*.md*
*Źródła: modpack_1710, CurseForge, Modrinth*
