# Mapowanie usuniętych modów 1.7.10 → 1.18.2

> **Cel dokumentu:** Szczegółowe mapowanie modów sklasyfikowanych jako "Kompletna strata" lub "Ignorowane" na nowe mody 1.18.2.  
> **Status:** Spójny z `mod_mapping_indepth` (z uwzględnieniem UWAG)

---

## Lista modów IGNOROWANYCH (nie wymagają konwersji)

Mody te **nie zostawiają trwałych bloków/TE** w chunkach i nie wymagają konwersji danych świata:

| # | Mod 1.7.10 | Kategoria | Dlaczego ignorowany | Zamiennik 1.18.2 |
|---|------------|-----------|---------------------|------------------|
| 1 | **Treecapitator** | QoL | Tylko klientowy efekt | FallingTree |
| 2 | **Baubles** | API | Tylko sloty akcesoriów | Curios API |
| 3 | **Bookshelf** | Biblioteka | Dependency innych modów | Bookshelf (nowa wersja) |
| 4 | **bspkrsCore** | Biblioteka | Tylko dla Treecapitator | *Nie potrzebna* |
| 5 | **CodeChickenCore** | Biblioteka | Wbudowany w CCL | *Nie potrzebna* |
| 6 | **CraftGuide** | QoL | Przeglądarka receptur | JEI |
| 7 | **CustomNPCs** | Serwerowy | Nieużywane na mapie | Easy NPC (opcjonalnie) |
| 8 | **FastCraft** | Optymalizacja | Tylko performance | Rubidium + Starlight |
| 9 | **ForgeEssentials** | Serwerowy | Komendy, permisje | Nowsza wersja FE |
| 10 | **iChunUtil** | Biblioteka | Dependency iChun | *Nie potrzebna* |
| 11 | **LiteLoader** | Loader | Loader litemodów | *Nie potrzebny* |
| 12 | **MobiusCore** | Biblioteka | Dla Opis | *Nie potrzebna* |
| 13 | **MrTJPCore** | Biblioteka | Wbudowany w ProjectRed | *Nie potrzebna* |
| 14 | **NEI** | QoL | Przeglądarka itemów | JEI |
| 15 | **NoMoreRecipeConflict** | QoL | Konflikty receptur | Polymorph |
| 16 | **Opis** | Diagnostyka | Profiler TPS | Spark |
| 17 | **RadarBro** | QoL | Radar encji | Xaero's Minimap |
| 18 | **Rei's Minimap** | QoL | Minimapa | JourneyMap / Xaero's |
| 19 | **uuidoffline** | Serwerowy | Patch UUID | *Nie potrzebna* |
| 20 | **WorldEdit** | Narzędzie | Edycja mapy | WorldEdit (nowa wersja) |

**Uwaga:** Mody oznaczone jako "instalować osobno" (FallingTree, JEI, Spark, itp.) należy dodać do paczki 1.18.2, ale nie wymagają konwersji danych z mapy.

---

## Lista 16 usuniętych modów WYMAGAJĄCYCH konwersji/mapowania

---

## Spis treści

1. [Lista 16 usuniętych modów](#lista-16-usuniętych-modów)
2. [Szczegółowe mapowanie per-mod](#szczegółowe-mapowanie-per-mod)
   - Extra Utilities → Zestaw modów
   - Forestry → Productive Bees + Create/Thermal
   - IC2 Nuclear Control → CC:Tweaked
   - Open Modular Turrets → IE/K-Turrets
   - Thaumcraft + addony → Ars Nouveau + Occultism
   - Statues → Statues (ShyNieke)
3. [Podsumowanie strategii](#podsumowanie-strategii)

---

## Lista 16 usuniętych modów

| # | Mod 1.7.10 | Powód usunięcia | Mapowanie 1.18.2 | Strategia |
|---|------------|-----------------|------------------|-----------|
| 1 | **Extra Utilities** | Brak pełnego portu | **ExU Reborn** + osobne mody | B (hybrydowa) |
| 2 | **CustomNPCs** | Nieużywane | **Easy NPC** | B |
| 3 | **Forestry** | Crashuje, laguje | **Productive Bees** + **Create**/**Thermal** | B |
| 4 | **IC2 Nuclear Control** | Brak portu | **CC:Tweaked** monitory | B |
| 5 | **Open Modular Turrets** | Brak portu | **IE turrets** / **K-Turrets** | B |
| 6 | **Thaumic Energistics** | Wymaga Thaumcraft | **AE2** + **Occultism** | B |
| 7 | **Thaumic Exploration** | Wymaga Thaumcraft | **Ars Nouveau** | B |
| 8 | **Thaumic Horizons** | Wymaga Thaumcraft | **Ars Nouveau** | B |
| 9 | **Thaumic Tinkerer** | Wymaga Thaumcraft | **Ars Nouveau** | B |
| 10 | **Statues** | Brak portu | **Statues (ShyNieke)** | A/B |
| 11 | **PowerConverters** | Niepotrzebny (FE) | *Nie potrzeba* | - |
| 12 | **CraftGuide** | Zastąpiony | **JEI** | C |
| 13 | **NoMoreRecipeConflict** | Niepotrzebny | **Polymorph** | C |
| 14 | **HelpFixer** | Niepotrzebny | *Nie potrzeba* | - |
| 15 | **FastCraft** | Niepotrzebny | **Rubidium**/**Starlight** | C |
| 16 | **Opis** | Brak portu | **Spark** | C |

**Legenda strategii:**
- **A** - Ten sam mod / ta sama rodzina
- **B** - Zamiennik funkcjonalny (wymaga remapów)
- **C** - QoL / narzędzia (brak treści świata)

---

## Szczegółowe mapowanie per-mod

### 1. Extra Utilities → Zestaw modów 1.18.2

Extra Utilities nie ma pełnego portu na 1.18.2. Dostępny jest **Extra Utilities Reborn** (nieoficjalny port części funkcjonalności), ale zalecane jest użycie zestawu dedykowanych modów.

| Funkcja ExU 1.7.10 | Mod docelowy 1.18.2 | Szczegóły |
|--------------------|---------------------|-----------|
| **Cursed Earth** | **Cursed Earth** (mod) | Taka sama funkcja - ziemia spawnująca moby |
| **Angel Block** | **Angel Block Renewed** | Blok stawiany w powietrzu |
| **Mega Torch** / **Magnum Torch** | **Torchmaster** | Blokada spawnu mobów w promieniu 64+ bloków |
| **Transfer Nodes** (items) | **Pipez** | Proste rury item/fluid/energy |
| **Transfer Nodes** (advanced) | **XNet** | Zaawansowany routing i filtry |
| **Ender Quarry** | **RFTools Builder** + Quarry Card | Wydobycie obszarowe z kartami kształtów |
| **Ender-Thermic Pump** | **Mekanism** (pompy) / **Create** | Pompy do lawy/wody |
| **Generators** | **Mekanism Generators** / **Thermal** | Różne typy generatorów FE |
| **Trash Can** | **Trash Cans** (mod) / podobny | Usuwanie itemów |
| **Sound Muffler** | **Extreme Sound Muffler** | Tłumienie dźwięków |
| **Bedrockium** | *Brak bezpośredniego* | Można zastąpić innymi "end-game" materiałami |
| **Golden Bag of Holding** | **Sophisticated Backpacks** | Plecaki z dużą pojemnością |
| **Heating/Electric Coils** | **Thermal** / **Mekanism** | Przewody i cewki |

**Zalecany zestaw dla graczy ExU:**
- Extra Utilities Reborn (część blisków i util)
- Torchmaster (anty-spawn)
- Angel Block Renewed (budowanie)
- Pipez (transport)
- RFTools Builder (quarry)

---

### 2. Forestry → Productive Bees + Create/Thermal

Forestry nie ma portu na 1.18.2 ze względu na problemy ze stabilnością.

| Funkcja Forestry 1.7.10 | Mod docelowy 1.18.2 | Szczegóły |
|-------------------------|---------------------|-----------|
| **Apiary** (podstawowa pasieka) | **Productive Bees** (Hive) | System uli z upgrade'ami |
| **Alveary** (zaawansowana pasieka) | **Productive Bees** (advanced hives) | Większe ule z modyfikacjami |
| **Beealyzer** | **Productive Bees** (analyser) | Analiza genów pszczół |
| **Centrifuge** | **Create** (centrifuge) / **Thermal** | Odwirowywanie produktów |
| **Squeezer** | **Create** (mechanical press) | Wyciskanie płynów |
| **Carpenter** | **Create** (automated crafting) | Crafting z płynami |
| **Fermenter** | **Create** (mixing) / **Thermal** | Fermentacja |
| **Still** | **Thermal** (refinery) | Destylacja |
| **Multifarm** | **Create** (harvestery) / **Industrial Foregoing** | Automatyczne farmy |
| **Backpacks** | **Sophisticated Backpacks** | (już na liście konwersji) |
| **Mail** (Mailbox/Trade Station) | **Ender Mail** (opcjonalnie) | System poczty |
| **Engines** (Peat/Biogas) | **Thermal** (dynamos) / **Mekanism** | Generatory energii |

**Zalecany zestaw dla graczy Forestry:**
- Productive Bees (główny system pszczół)
- Create (przetwórstwo i farmy)
- Thermal (uzupełnienie maszyn)
- Sophisticated Backpacks (backpacki)
- Ender Mail (jeśli potrzebna poczta)

---

### 3. IC2 Nuclear Control → CC:Tweaked

IC2 Nuclear Control nie ma portu, ale funkcjonalność monitoringu można odtworzyć za pomocą komputerów.

| Funkcja IC2NC 1.7.10 | Rozwiązanie 1.18.2 | Szczegóły |
|----------------------|-------------------|-----------|
| **Thermal Monitor** | **CC:Tweaked** + program | Komputer + redstone integracja |
| **Industrial Alarm** | **CC:Tweaked** + note blocks/redstone | Alarm aktywowany komputerem |
| **Howler Alarm** | Redstone + dzwonki/blocks | Prosty alarm |
| **Energy Monitor** | **CC:Tweaked** + integracje z modami | Peryferia do odczytu energii |
| **Range Trigger** | **CC:Tweaked** + sensory | Detekcja odległości/obszaru |
| **Remote Monitor** | **CC:Tweaked** monitory | Ekrany wyświetlające dane |

**Implementacja:**
- Napisz program w Lua dla CC:Tweaked
- Użyj adapterów/peryferiów do odczytu danych z reaktorów
- Podłącz wyświetlacze i alarmy redstone

---

### 4. Open Modular Turrets → IE/K-Turrets

OMT nie ma portu na 1.18.2. Dostępne są alternatywy o różnym stopniu zbliżenia.

| Funkcja OMT 1.7.10 | Mod docelowy 1.18.2 | Szczegóły |
|--------------------|---------------------|-----------|
| **Turret Base** (tiered) | **K-Turrets** (bazy) | Podobny system tierów |
| **Ammo system** | **K-Turrets** / **IE** | Różne typy amunicji |
| **Upgrades** (damage/range) | **K-Turrets** (upgrades) | System ulepszeń |
| **Addons** (targeting) | **K-Turrets** (target filters) | Filtrowanie celów |
| **Simple turrets** | **Immersive Engineering** | Podstawowe turrety (ograniczone) |

**Rekomendacja:**
- **K-Turrets** - bardziej zbliżony do OMT (modularność, system amunicji)
- **Immersive Engineering** - jeśli już jest w paczce (kilka prostych turretów)

---

### 5. Thaumcraft + addony → Ars Nouveau + Occultism + Botania

Thaumcraft 4 i wszystkie addony **nie mają portu** na 1.18.2. Wymagana jest konwersja "w duchu" na zestaw modów.

#### Główne zamienniki magii:

| Aspekt TC | Zamiennik 1.18.2 | Jak odtworzyć |
|-----------|------------------|---------------|
| **Research/Thaumonomicon** | **Ars Nouveau** (spell book + wiki) | Patchouli guidebooki |
| **Vis/Essentia** | **Source** (Ars) / **Mana** (Botania) | Zbiorniki magii |
| **Węzły aura** | **Source Jars** / **Mana Pools** | Punkty zasilania |
| **Infusion Altar** | **Enchanting Apparatus** (Ars) | Crafting magiczny |
| **Arcane Workbench** | **Scribe's Table** (Ars) / **Crafting menu** | Crafting czarów |
| **Crucible** | **Melter** (Ars) / inne | Topienie przedmiotów |
| **Golemy** | **Familiars** (Occultism) | Automatyzacja |
| **Alchemy** | **Alchemy** (Ars/Occultism) | Mikstury |
| **Rytuały** | **Ritual Brazier** (Ars) / **Rytuały** (Occultism) | System rytuałów |

#### Mapowanie addonów Thaumcraft:

| Addon 1.7.10 | Funkcja | Zamiennik 1.18.2 |
|--------------|---------|------------------|
| **Thaumic Energistics** | Essentia storage w AE2 | **Occultism storage** (magiczny storage) |
| **Thaumic Exploration** | Nowe itemy/bloki | **Ars Nouveau** + dodatki |
| **Thaumic Horizons** | Mob infusion, lenses | **Ars Nouveau** (summony), **Create** (automatyzacja) |
| **Thaumic Tinkerer** | Osmotic enchanting | **Ars Nouveau enchanting** / **Apotheosis** |

**Zalecany zestaw magiczny:**
- **Ars Nouveau** (główny system magii/czarów)
- **Occultism** (rytuały, summony, storage)
- **Botania** (mana-tech, automatyzacja "magiczna")
- **Hexerei** lub **Enchanted: Witchcraft** (jeśli chcesz klimat Witchery)

---

### 6. Statues → Statues (ShyNieke)

**WAŻNE:** Statues MA PORT na 1.18.2!

| | Informacja |
|--|------------|
| **Mod docelowy** | Statues (by ShyNieke) |
| **Dostępność** | Forge 1.18.2 |
| **Źródła** | Modrinth, CurseForge |
| **Strategia** | A/B (jest port, ale NBT niekompatybilne) |

**Uwagi migracyjne:**
- To NIE jest ten sam mod co w 1.7.10 (inny autor, inny kod)
- Format NBT jest INNY - dane statuł nie przeniosą się automatycznie
- Wymagane mapowanie bloków + ręczna rekonstrukcja poz/skinów

**Mapowanie bloków:**
| Blok 1.7.10 | Blok 1.18.2 | Uwagi |
|-------------|-------------|-------|
| `statues:statue` | `statues:statue` | Inny format NBT |
| `statues:showcase` | `statues:showcase` | Inny format danych |

---

### 7-11. Mody niepotrzebne (strategia C lub brak)

| Mod 1.7.10 | Dlaczego niepotrzebny | Zamiennik (jeśli potrzebny) |
|------------|----------------------|----------------------------|
| **PowerConverters** | FE (Forge Energy) jest natywne w 1.18.2 | *Nie potrzeba* |
| **CraftGuide** | JEI obsługuje przegląd receptur | **JEI** |
| **NoMoreRecipeConflict** | Polymorph obsługuje konflikty | **Polymorph** (opcjonalnie) |
| **HelpFixer** | Naprawiono w Forge 1.18.2 | *Nie potrzeba* |
| **FastCraft** | Nowe optymalizacje | **Rubidium** + **Starlight** + **FerriteCore** |
| **Opis** | Profiler serwerowy | **Spark** (lepszy profiler) |

---

## Podsumowanie strategii

### Strategia A (Ten sam mod)
- **Statues** → Statues (ShyNieke) - jest port, ale NBT niekompatybilne

### Strategia B (Zamienniki funkcjonalne)
- **Extra Utilities** → Zestaw modów (ExU Reborn + Torchmaster + Angel Block + Pipez + RFTools)
- **Forestry** → Productive Bees + Create + Thermal
- **IC2 Nuclear Control** → CC:Tweaked + programy
- **Open Modular Turrets** → K-Turrets lub IE
- **Thaumcraft + addony** → Ars Nouveau + Occultism + Botania
- **CustomNPCs** → Easy NPC (jeśli potrzebne)

### Strategia C (QoL/Narzędzia)
- **CraftGuide** → JEI
- **NoMoreRecipeConflict** → Polymorph
- **FastCraft** → Rubidium + Starlight + FerriteCore
- **Opis** → Spark

### Brak potrzeby zamiennika
- **PowerConverters** - FE natywne
- **HelpFixer** - naprawiono w Forge
- **uuidoffline** - UUID natywne

---

## Checklist konwersji dla usuniętych modów

### Przed konwersją (ratunek danych):
- [ ] **Extra Utilities**: Wypakować Quarry, sprawdzić które generatory są używane
- [ ] **Forestry**: Wyhodować pszczoły do skrzynek, zapisać geny
- [ ] **IC2 Nuclear Control**: Zapisać konfigurację monitoringu (do odtworzenia w CC)
- [ ] **OMT**: Zebrać ammo i turrety do skrzynek
- [ ] **Thaumcraft**: Zrzucić wszystkie inwentarze z ołtarzy, bibliotek, golemów
- [ ] **Statues**: Zrobić screenshoty ważnych statuł (NBT się nie przeniesie)

### Po konwersji (odtworzenie):
- [ ] **Extra Utilities**: Postawić odpowiedniki (Torchmaster, Angel Block, Pipez)
- [ ] **Forestry**: Założyć nowe ule Productive Bees
- [ ] **Thaumcraft**: Rozpocząć nową progresję w Ars Nouveau
- [ ] **Statues**: Postawić nowe statuy i skonfigurować ręcznie

---

*Dokument spójny z `mod_mapping_indepth` - ostatnia aktualizacja: 2026-02-01*
*Zawiera sekcję modów ignorowanych (22 mody nie wymagające konwersji)*
