# Analiza funkcjonalności modów w kontekście mapy 5GB

> **Autor:** Kimi Code CLI  
> **Data:** 2026-05-18  
> **Źródła:** `output/zone_te_discovery.json`, `docs/mod_mapping_indepth/`, weryfikacja online (CF/Modrinth)  
> **Cel:** Określenie najlepszych zamienników 1.18.2 dla funkcjonalności modów 1.7.10 w kontekście faktycznego użycia na mapie 5GB.

---

## 1. Metodologia analizy mapy

Dane pochodzą z pełnego skanu Tile Entities (`output/zone_te_discovery.json`) na mapie źródłowej `mapa_1710/` (5GB, 1323 plików regionów). Skan identyfikuje **Tile Entities (TE)** w chunkach, co daje obiektywny obraz które mody **faktycznie zostawiły trwałe dane** w świecie.

> **Uwaga:** Skan nie wykrywa zwykłych bloków (np. tory, rury, bloki dekoracyjne bez TE) oraz encji (pojazdy, moby). Niektóre mody (Traincraft, Flan's Mod) mogą mieć więcej danych w postaci encji niż TE.

---

## 2. Ranking modów na mapie (wg liczby TE)

| Miejsce | Mod | Liczba TE | % wszystkich | Kategoria docs | Status na 1.18.2 |
|---------|-----|-----------|--------------|----------------|------------------|
| 1 | **ForgeMultipart** (savedMultipart) | 278 036 | ~46,5% | Biblioteka | CB Multipart (A) |
| 2 | **Carpenter's Blocks** | 244 737 | ~40,9% | Własny mod/FramedBlocks | CuttableBlocks + FramedBlocks (B) |
| 3 | **Armourer's Workshop** | 36 929 | ~6,2% | Błąd docs: brak wersji | JEST port 3.2.7-beta (A) |
| 4 | **Railcraft** | 23 203 | ~3,9% | Błąd docs: brak portu | Railcraft Reborn 5.x (A) |
| 5 | **Thaumcraft** | 19 187 | ~3,2% | Ars+Occultism+Botania | Brak portu (B) |
| 6 | **Vanilla** | 12 275 | ~2,1% | Vanilla | Natywne (A) |
| 7 | **Forestry** | 7 710 | ~1,3% | Productive Bees+Create | Growthcraft CE istnieje! (A/B) |
| 8 | **CustomNPCs** | 7 678 | ~1,3% | Easy NPC | Brak portu Noppes (B) |
| 9 | **MrCrayfish Furniture** | 5 467 | ~0,9% | Błąd docs: zamienniki | JEST port v7.0.x (A) |
| 10 | **Thermal Series** | 4 289 | ~0,7% | Thermal Series 9.2.2 | Port (A) |
| 11 | **Extra Utilities** | 3 098 | ~0,5% | ExU Reborn+osobne | Hybryda (B) |
| 12 | **Better Storage** | 3 017 | ~0,5% | Iron Chests+Soph.Storage | Sophisticated Storage (B) |
| 13 | **Applied Energistics 2** | 2 478 | ~0,4% | AE2 11.7.6 | Port (A) |
| 14 | **ProjectRed** | 1 738 | ~0,3% | ProjectRed 4.17.0 | Port (A) |
| 15 | **Mekanism** | 1 734 | ~0,3% | Mekanism 10.2.5 | Port (A) |
| 16 | **Reliquary** | 1 592 | ~0,3% | Reliquary Reincarnations | Port (A) |
| 17 | **ComputerCraft** | 1 460 | ~0,2% | CC:Tweaked 1.101.x | Port (A) |
| 18 | **Witchery** | 1 460 | ~0,2% | Hexerei+Enchanted | Brak portu (B) |
| 19 | **BiblioCraft** | 1 313 | ~0,2% | Supplementaries+Handcrafted | Brak portu (B) |
| 20 | **Open Modular Turrets** | 1 166 | ~0,2% | IE / K-Turrets | K-Turrets (B) |
| 21 | **Big Reactors** | 924 | ~0,15% | Extreme Reactors | Port (A) |
| 22 | **Growthcraft** | 456 | ~0,08% | Błąd docs: zamienniki | Growthcraft CE (A!) |
| 23 | **IC2** | 393 | ~0,07% | Mekanism+Thermal | Mekanism+Thermal (B) |
| 24 | **BuildCraft** | 266 | ~0,04% | Pipez+XNet+RFTools | Pipez+XNet+Create+ID (B) |
| 25 | **Logistics Pipes** | 217 | ~0,04% | Pretty Pipes / AE2 | AE2+Integrated Dynamics (B) |
| 26 | **EnderStorage** | 115 | ~0,02% | EnderStorage 2.9.x | Port (A) |
| 27 | **Pam's HarvestCraft** | 24 | ~0,004% | PHC2 | Reboot (A) |
| 28 | **Thaumic Energistics** | 24 | ~0,004% | AE2+Occultism | AE2+Occultism (B) |
| 29 | **Traincraft** | 9 | ~0,002% | Create+Steam'n'Rails | Create+VS2+Eureka (B) |
| 30 | **PowerConverters** | 10 | ~0,002% | Niepotrzebny | Ignoruj (C) |
| 31 | **Chisel** | 2 | ~0,0003% | Rechiseled+Chipped | Rechiseled+Chipped (B) |
| 32 | **Placeable Items** | 1 | ~0,0002% | Błąd docs: ignoruj | Placeable Items 4.7 (A) |

### Kluczowe wnioski z rankingu

1. **Top 2 mody stanowią ~87% wszystkich TE** na mapie:
   - `savedMultipart` (278k) — ForgeMultipart → **CB Multipart**
   - `TileEntityCarpentersBlock` (242k) — Carpenter's Blocks → **CuttableBlocks + FramedBlocks**

2. **Dokumentacja zawiera krytyczne błędy w 4 największych modach** (po Vanilli):
   - Armourer's Workshop (37k TE): docs twierdzi że nie ma portu → **jest port**
   - Railcraft (23k TE): docs twierdzi że nie ma portu → **jest Railcraft Reborn**
   - MrCrayfish Furniture (5,5k TE): docs sugeruje zamienniki → **jest bezpośredni port**
   - Growthcraft (456 TE): docs sugeruje zamienniki → **jest Growthcraft CE**

3. **Mody z kategorii "A" (bezpośredni port) stanowią ~55% TE** — ich konwersja jest najważniejsza i najbardziej opłacalna.

---

## 3. Analiza per-mod w kontekście mapy

### 3.1 ForgeMultipart — 278 036 TE (~46,5% mapy)

**Co to jest:** Framework do "wielu elementów w jednym bloku" (microbloki, przewody, fasady w jednej kratce).

**Co na mapie:** `savedMultipart` — najliczniejszy TE na mapie. Używany przez ProjectRed (przewody + bramki + lampy), BuildCraft (rury), i inne mody wspierające multipart.

**Najlepszy zamiennik:** **CB Multipart** na 1.18.2.

**Uzasadnienie w kontekście mapy:**
- Bez CB Multipart **278 tysięcy bloków** na mapie straci swoją strukturę (rozsypią się lub znikną).
- CB Multipart to bezpośredni następca ForgeMultipart na nowych wersjach.
- **Wymagane jest perfekcyjne przekonwertowanie** — błąd tutaj zniszczy ogromne obszary mapy.

**Ryzyko:** 🔴 Krytyczne. Błąd w konwersji multipartów = katastrofa mapy.

**Rekomendacja:**
1. Priorytet #1 konwersji.
2. Przygotować dedykowane narzędzie remapujące ForgeMultipart → CB Multipart.
3. Testować na małym wycinku mapy przed uruchomieniem na całości.

---

### 3.2 Carpenter's Blocks — 244 737 TE (~40,9% mapy)

**Co to jest:** Bloki "coverable" — można okleić dowolnym blokiem (schody, skosy, drzwi, bramy, Collapsible Block).

**Co na mapie:** `TileEntityCarpentersBlock` (241 939) + `TileEntityCarpentersGarageDoor` (2506) + `TileEntityCarpentersTorch` (187) + `TileEntityCarpentersSafe` (105).

**Najlepszy zamiennik:** **CuttableBlocks (własny mod) + FramedBlocks**.

**Uzasadnienie w kontekście mapy:**
- W repo już istnieją skompilowane JARy `CuttableBlocks-1.0.0*.jar` (w tym `with_collapsible`).
- FramedBlocks pokrywa standardowe kształty (block, slope, stairs, door, fence, pane, slab).
- CuttableBlocks obsługuje Collapsible Block (zmienna wysokość 4 wierzchołków).
- **Największe wyzwanie:** NBT "cover" (tekstura) wymaga remapowania ID bloku 1.7.10 → blockstate 1.18.2.

**Ryzyko:** 🔴 Krytyczne. 241k bloków bez konwersji = ogromne dziury w budowlach.

**Rekomendacja:**
1. Zweryfikować czy `CuttableBlocks` jest kompatybilny z FramedBlocks (czy można używać obu naraz).
2. Stworzyć mapowanie "cover ID" (najpopularniejsze tekstury używane w Carpenter's Blocks).
3. Przygotować fallback: jeśli tekstura nie istnieje w 1.18.2 → stone_bricks lub podobny neutralny blok.

---

### 3.3 Armourer's Workshop — 36 929 TE (~6,2% mapy)

**Co to jest:** Skinny pancerza, broni, bloków; warsztat, biblioteki skinów, manekiny.

**Co na mapie:** `te.skinnableChild` (21 363), `te.skinnable` (15 043), `te.mannequin` (365), `te.armourLibrary` (103), `te.globalSkinLibrary` (5), `te.skinningTable` (5), `te.hologramProjector` (44), `te.colourMixer` (2), `te.dyeTable` (2).

**Najlepszy zamiennik:** **Armourer's Workshop 3.2.7-beta** (OFICJALNY PORT).

**Uzasadnienie w kontekście mapy:**
- Dokumentacja cz1.md jest **nieaktualna** — port ISTNIEJE na 1.18.2 Forge.
- 37k TE to bardzo dużo — użycie zamiennika (Cosmetic Armor Reworked) oznaczałoby utratę wszystkich skinów, bibliotek i manekinów.
- Konwersja AW → AW daje największą szansę zachowania treści.

**Ryzyko:** 🟠 Wysokie. NBT skinów mogło zmienić format między 0.48.5 (1.7.10) a 3.x (1.18.2).

**Rekomendacja:**
1. Pobrać AW 1.18.2 i przetestować kompatybilność NBT.
2. Jeśli NBT niekompatybilne — przygotować narzędzie eksportu skinów z 1.7.10 i importu do 1.18.2.
3. Zadanie na sam koniec kolejki (złożone NBT).

---

### 3.4 Railcraft — 23 203 TE (~3,9% mapy)

**Co to jest:** Kolej, tory, maszyny kolejowe, multibloki (Coke Oven, Blast Furnace, Boiler).

**Co na mapie:** `tileTCRailGag` (8043), `RCSteelTankWallTile` (5611), `tileTCRail` (4638), `RCIronTankWallTile` (2615), `RailcraftTrackTile` (1098), maszyny (Coke Oven, Blast Furnace, Boiler, Rolling Machine, Rock Crusher, itd.).

**Najlepszy zamiennik:** **Railcraft Reborn 5.x**.

**Uzasadnienie w kontekście mapy:**
- Dokumentacja cz4.md błędnie twierdzi że nie ma portu.
- Railcraft Reborn to najbliższy funkcjonalnie następca (te same koncepty: tory, sygnalizacja, maszyny).
- Create: Steam 'n' Rails to alternatywa, ale zupełnie inna mechanika (kinetic energy zamiast parowej).
- 23k TE to drugi co do wielkości mod (po Carpenter's) — warto zachować oryginalną mechanikę.

**Ryzyko:** 🟠 Wysokie. Docs ostrzega że Railcraft Reborn może być niestabilny. Należy przetestować na headless serwerze.

**Rekomendacja:**
1. Przetestować Railcraft Reborn na headless serwerze z testową mapą (Choroszcz/Rzym).
2. Jeśli niestabilny — przygotować fallback: Create: Steam 'n' Rails + Immersive Engineering (maszyny).
3. Tory (tileTCRail + tileTCRailGag = ~12,7k) wymagają masowego remapowania ID.

---

### 3.5 Thaumcraft 4 + addony — 19 187 TE (~3,2% mapy)

**Co to jest:** Magia, aspekty, essentia, infuzja, golemy, research.

**Co na mapie:** `TileWarded` (18 116 — sprawdzić czy to bloki czy efekty!), `TileMirrorEssentia` (178), `TileJar` (174), `TileNode` (132), `TileArcaneWorkbench` (12), `TileCrucible` (17), `TileInfusionPillar` (24), `TileResearchTable` (10), `thaumicenergistics.*` (24), i wiele innych.

**Najlepszy zamiennik:** **Ars Nouveau + Occultism + Botania + Hexerei**.

**Uzasadnienie w kontekście mapy:**
- Thaumcraft nie ma portu na 1.18.2. Bloki magiczne muszą zostać zamienione na placeholdery.
- `TileWarded` (18k) to zabezpieczone bloki — jeśli to bloki ochronne, mogą zostać usunięte lub zamienione na neutralne.
- Research, essentia, golemy — wszystko do odtworzenia w nowych modach.

**Ryzyko:** 🟠 Wysokie. Duża ilość TE, brak portu = strata danych lub ręczna rekonstrukcja.

**Rekomendacja:**
1. Etap "ratunkowy": wypakować inwentarze z arcane/alchemy TE do skrzyń.
2. Zamienić bloki Thaumcraft na placeholdery dekoracyjne (zachować geometrię budowli).
3. Odtworzyć funkcjonalność w Ars Nouveau (czary/rytuały) + Occultism (summony/storage) + Botania (automatyzacja).

---

### 3.6 Forestry — 7 710 TE (~1,3% mapy)

**Co na mapie:** `forestry.Leaves` (7293), `forestry.Wood` (384), `forestry.Swarm` (17), `forestry.Sapling` (6), `forestry.Escritoire` (3), `forestry.Apiary` (6), `forestry.Fabricator` (1).

**Najlepszy zamiennik:** **Growthcraft CE (jeśli na mapie są bloczki Growthcraft) + Productive Bees + Create**.

**Uzasadnienie w kontekście mapy:**
- Forestry.Leaves (7293) to liście drzew — mogą być zamienione na zwykłe liście vanilla lub liście z innych modów.
- Maszyny (Apiary, Escritoire, Fabricator) tylko 10 TE — niska strata.
- **Istotne:** na mapie jest też Growthcraft (456 TE). Jeśli oba mody rolnicze są używane, Growthcraft CE na 1.18.2 pozwoli zachować część funkcji.

**Rekomendacja:**
1. `forestry.Leaves` → zamiana na vanilla leaves lub liście z Croptopia/Farmer's Delight.
2. `forestry.Apiary` (6) → Productive Bees (ule).
3. Reszta maszyn → Create/Thermal.

---

### 3.7 CustomNPCs — 7 678 TE (~1,3% mapy)

**Co na mapie:** `TileNPCChair` (2247), `TileNPCCouchWood` (2204), `TileNPCTable` (1310), `TileNPCCrate` (814), `TileNPCCandle` (459), `TileNPCLamp` (138), `TileNPCBarrel` (117), `TileNPCShelf` (90), `TileNPCCouchWool` (87), `TileNPCTallLamp` (119), `TileNPCWeaponRack` (44), `TileNPCBanner` (22), `TileNPCWallBanner` (7), `TileNPCBigSign` (10), `TileNPCStool` (8), `TileEntityPortal` (2).

**Najlepszy zamiennik:** **Easy NPC** + **FTB Quests** (jeśli questy) + **Supplementaries/Handcrafted** (meble).

**Uzasadnienie w kontekście mapy:**
- CustomNPCs Noppes nie ma na 1.18.2.
- **Istotne:** spora ilość TE to meble (krzesła, stoły, sofy, lampy) — nie tylko same NPC.
- Meble CustomNPCs można zamienić na Supplementaries / Handcrafted / Macaw's Furniture.
- NPC + questy → Easy NPC (podstawowe) + FTB Quests (zaawansowane).

**Rekomendacja:**
1. Rozdzielić meble (TileNPC*) od funkcjonalności NPC/questów.
2. Meble → mapowanie kategoria→kategoria (chair→chair, table→table).
3. NPC → Easy NPC (ręczna rekonstrukcja).

---

### 3.8 MrCrayfish Furniture — 5 467 TE (~0,9% mapy)

**Co na mapie:** `TableTile` (1530), `cfmCabinetKitchen` (721), `seatTile` (713), `cfmFreezer` (183), `cfmFridge` (183), `cfmPrinter` (182), `cfmCounterSink` (153), `cfmBedsideCabinet` (473), `cfmWashingMachine` (113), `cfmCouch` (109), `cfmOven` (106), `cfmComputer` (105), `cfmMicrowave` (72), `cfmTV` (70), `cfmStereo` (27), `cfmBlender` (25), `cfmBin` (25), `cfmBath` (4), `cfmBasin` (8), `cfmPlate` (3), `cfmToaster` (22), `cfmCup` (9), `cfmWallCabinet` (10), `cfmMailBox` (1), `cfmDishwasher` (21).

**Najlepszy zamiennik:** **MrCrayfish Furniture Mod v7.0.x** (bezpośredni port).

**Uzasadnienie w kontekście mapy:**
- Dokumentacja cz4.md błędnie sugeruje zamienniki (Macaw's, Decocraft).
- **JEST bezpośredni port** na 1.18.2 Forge (v7.0.x-pre).
- 5,5k TE to dużo — użycie zamienników oznaczałoby ręczne odtwarzanie wszystkich mebli.
- Bloki z inwentarzem (lodówka, szafki, mailbox) wymagają wypakowania + remap NBT.

**Rekomendacja:**
1. Użyć bezpośredniego portu MrCrayfish Furniture 1.18.2.
2. Wypakować inwentarze z fridge/freezer/cabinet/mailbox przed konwersją.
3. Przetestować kompatybilność NBT inwentarzy między v3.4.8 a v7.0.x.

---

### 3.9 Thermal Series — 4 289 TE (~0,7% mapy)

**Co na mapie:** `thermaldynamics.ItemDuct` (1984), `thermaldynamics.FluxDuctSuperConductor` (1950), `thermaldynamics.FluidDuct` (136), `thermaldynamics.FluidDuctSuper` (84), maszyny Thermal Expansion (~125 TE).

**Najlepszy zamiennik:** **Thermal Series 9.2.2** (Foundation + Expansion + Dynamics).

**Uzasadnienie w kontekście mapy:**
- Ten sam mod. Dukty (Item/Flux/Fluid) to największa grupa (~4154 TE) — remap ID + blockstates.
- Maszyny (Pulverizer, Furnace, Sawmill, itp.) — remap semantyczny + NBT (augmenty, side-config).

**Rekomendacja:**
1. Dukty → Thermal Dynamics 1.18.2 (prosty remap ID).
2. Maszyny → Thermal Expansion 1.18.2 (NBT do translacji).
3. Servos/filtry → rekonstrukcja (format NBT się zmienił).

---

### 3.10 Extra Utilities — 3 098 TE (~0,5% mapy)

**Co na mapie:** `TileEntityFilingCabinet` (3029), `TileEntityTrashCan` (55), `extrautils:generatorlava` (14).

**Najlepszy zamiennik:** Hybryda per-funkcja.

**Uzasadnienie w kontekście mapy:**
- Filing Cabinet (3029) to **zdecydowana większość** TE ExU na mapie.
- Zamiennik: **Sophisticated Storage** (barrels/chests z sortowaniem i filtrem) lub **Storage Drawers**.
- Trash Can → funkcja kosza (można zastąpić lava lub void upgrade w Sophisticated Storage).
- Generator Lava → Thermal/Mekanism generators.

**Rekomendacja:**
1. Filing Cabinet → Sophisticated Storage barrels/chests (upgrade filter + sort).
2. Reszta → osobne mody (Torchmaster, Angel Block Renewed, Cursed Earth mod, Pipez, RFTools Builder).
3. Extra Utilities Reborn jako opcjonalny dodatek (niekompletny).

---

### 3.11 Better Storage — 3 017 TE (~0,5% mapy)

**Co na mapie:** `container.betterstorage.reinforcedLocker` (1641), `reinforcedChest` (1277), `thaumiumChest` (39), `crate` (25), `locker` (6), `armorStand` (1), `craftingStation` (20), `backpack` (7).

**Najlepszy zamiennik:** **Sophisticated Storage** (główny) + **Iron Chests** (uzupełnienie).

**Uzasadnienie w kontekście mapy:**
- Skrzynie i lockery to magazyny — Sophisticated Storage oferuje najwięcej funkcji (upgrade'y, sortowanie, kompresja).
- Cardboard Box → Carry On (podnoszenie TE) lub Packing Tape.
- Crafting Station → Crafting Station mod (istnieje na 1.18.2).
- Locki i klucze → nieprzenośne; zastąpić SecurityCraft (opcjonalnie) lub zrezygnować.

**Rekomendacja:**
1. Etap ratunkowy: wypakować inwentarze ze wszystkich skrzyń/lockerów.
2. Remap: reinforcedChest → Sophisticated Chest (z upgrade'ami), reinforcedLocker → Sophisticated Barrel.
3. Thaumium Chest → Iron Chests (diamond/gold) lub Sophisticated Storage.

---

### 3.12 Applied Energistics 2 — 2 478 TE (~0,4% mapy)

**Co na mapie:** `BlockCableBus` (1544), `BlockMolecularAssembler` (252), `BlockDenseEnergyCell` (190), `BlockDrive` (144), `BlockController` (80), `BlockInterface` (72), `BlockCraftingUnit` (74), `BlockIOPort` (33), `BlockCraftingStorage` (33), `BlockCraftingMonitor` (33), `BlockEnergyAcceptor` (16), `BlockSkyChest` (7), `BlockCharger` (5), `BlockCellWorkbench` (5), `BlockSpatialPylon` (39), `BlockSpatialIOPort` (5), `BlockInscriber` (5), `BlockQuartzGrowthAccelerator` (5).

**Najlepszy zamiennik:** **Applied Energistics 2 11.7.6**.

**Uzasadnienie w kontekście mapy:**
- Ten sam mod. 2478 TE to rozbudowana sieć ME.
- Najwięcej kabli (1544) — prosty remap ID.
- Molecular Assembler (252), Drive (144), Controller (80) — kluczowe bloki do zachowania.
- NBT storage celli (zawartość dysków!) i patterns (autocraft) — najtrudniejsza część.

**Rekomendacja:**
1. Priorytet: zabezpieczyć zawartość storage celli (eksport do skrzyń jako backup).
2. Konwersja NBT storage cells → nowy format.
3. Patterns (autocraft) → translacja ID itemów w NBT.
4. P2P tunnels, kanały, security — rekonstrukcja.

---

### 3.13 ProjectRed — 1 738 TE (~0,3% mapy)

**Co na mapie:** `tile.projectred.illumination.lamp` (1664), `tile.projectred.expansion.machine1` (18), `tile.projectred.expansion.machine2` (26), `tile.projectred.exploration.lily` (17), `tile.projectred.integration.icblock` (1).

**Najlepszy zamiennik:** **ProjectRed 4.17.0 + CB Multipart**.

**Uzasadnienie w kontekście mapy:**
- Lampy (1664) to zdecydowana większość — prosty remap na ProjectRed Illumination.
- Maszyny (expansion) — sprawdzić co to za maszyny (prawdopodobnie Frame Motor, itp.).
- Fabrication IC (icblock) — tylko 1, ale NBT może być skomplikowane.

**Rekomendacja:**
1. Lampy → ProjectRed Illumination (bezstratnie).
2. Maszyny → ProjectRed Expansion (remap ID).
3. ICblock → weryfikacja czy ProjectRed Fabrication na 1.18.2 obsługuje import projektów.

---

### 3.14 Mekanism — 1 734 TE (~0,3% mapy)

**Co na mapie:** `SalinationTank` (617), `InductionCasing` (304), `AdvancedBoundingBlock` (294), `BoundingBlock` (254), `Bin` (45), `EnergyCube` (22), `LaserAmplifier` (52), `MetallurgicInfuser` (7), `OsmiumCompressor` (1), `QuantumEntangloporter` (41), `DigitalMiner` (18), `MekanismTeleporter` (19), `Teleporter` (5), maszyny processing (~104 TE).

**Najlepszy zamiennik:** **Mekanism 10.2.5 + Generators + Tools**.

**Uzasadnienie w kontekście mapy:**
- Ten sam mod. SalinationTank (617) + InductionCasing (304) to multibloki — wymagają rekonstrukcji.
- BoundingBlock (294+254=548) to techniczne bloki wielobloków — sprawdzić czy nowy Mekanism używa tej samej koncepcji.
- Maszyny processing → semantyczny remap (Crusher→Crusher, itp.).

**Rekomendacja:**
1. Multibloki (Salination, Induction) → rekonstrukcja po remape.
2. Maszyny → remap + NBT (tier, side-config, upgrade).
3. BoundingBlock → weryfikacja czy nowy Mekanism ma analogiczne bloki techniczne.

---

### 3.15 Open Modular Turrets — 1 166 TE (~0,2% mapy)

**Co na mapie:** `laserTurret` (632), `turretBaseFour` (407), `Laser` (64), `railGunTurret` (7), `teleporterTurret` (56).

**Najlepszy zamiennik:** **K-Turrets** (główny) + **Immersive Engineering** (uzupełnienie).

**Uzasadnienie w kontekście mapy:**
- 1166 TE to spora ilość turretów obronnych — użytkownicy polegają na obronie bazy.
- K-Turrets oferuje modularność podobną do OMT (tier-y, amunicja, filtry targetów).
- IE ma tylko 2-3 typy turretek i brak modularności.

**Rekomendacja:**
1. K-Turrets jako główny mod obronny.
2. Turret Base + Turret → odpowiedniki K-Turrets (remap wizualny).
3. Amunicja i upgrade'y nieprzenośne — wypakować do skrzyń lub zostawić jako loot.

---

### 3.16 Pozostałe mody (niskie wykorzystanie)

| Mod | TE | Zamiennik | Uwagi |
|-----|----|-----------|-------|
| **Big Reactors** | 924 | Extreme Reactors | Reactor Part (613) + Glass (160) + Fuel Rod (119) — multibloki do rekonstrukcji. |
| **Witchery** | 1460 | Hexerei + Enchanted + Occultism | Poppet Shelf (1069) to najwięcej — NBT nieprzenośne, ratunek. |
| **BiblioCraft** | 1313 | Supplementaries + Handcrafted | Bookcase (850), Writing Desk (208) — dekoracje do rekonstrukcji. |
| **ComputerCraft** | 1460 | CC:Tweaked | wiredmodem (1254), monitor (196) — remap ID + NBT (dyski, skrypty). |
| **Reliquary** | 1592 | Reliquary Reincarnations | TileCrystal (1329) — sprawdzić czy to blok czy entity. |
| **IC2** | 393 | Mekanism + Thermal | Reactor (19), Solar Panel (82), MFSU (34) — semantyczny remap. |
| **BuildCraft** | 266 | Pipez + XNet + Create + ID | GenericPipe (160) — proste rury, niski priorytet. |
| **Logistics Pipes** | 217 | AE2 + Integrated Dynamics | LogisticsPipe (200) — przejść na AE2 sieć. |
| **EnderStorage** | 115 | EnderStorage 1.8+ | EnderChest (86) + Ender Tank (1) — remap kolorów + NBT. |
| **Growthcraft** | 456 | Growthcraft CE | fermentBarrel (287) — **użyć oryginalnego modu CE!** |
| **Traincraft** | 9 | Create + Steam'n'Rails | Niskie wykorzystanie. Encje pociągów niewykryte. |
| **Placeable Items** | 1 | Placeable Items 4.7 | Niskie wykorzystanie. |

---

## 4. Priorytety konwersji w kontekście mapy 5GB

### 🔴 Priorytet 1 — Krytyczne (błąd = katastrofa mapy)

| # | Mod | Powód | Akcja |
|---|-----|-------|-------|
| 1 | **ForgeMultipart** | 278k TE = 46,5% mapy. Bez CB Multipart wszystko się rozsypie. | Konwersja CB Multipart + test na małym wycinku. |
| 2 | **Carpenter's Blocks** | 245k TE = 41% mapy. Największy mod pod względem budowli. | CuttableBlocks + FramedBlocks + remap coverów. |
| 3 | **Railcraft** | 23k TE + docs mówi że nie ma portu. Railcraft Reborn istnieje! | Test Railcraft Reborn na headless. |

### 🟠 Priorytet 2 — Wysoka strata danych (dużo TE, brak portu lub skomplikowane NBT)

| # | Mod | Powód | Akcja |
|---|-----|-------|-------|
| 4 | **Armourer's Workshop** | 37k TE. Błąd docs — jest port. NBT skinów do weryfikacji. | Test kompatybilności NBT. Zadanie na koniec. |
| 5 | **Thaumcraft + addony** | 19k TE. Brak portu. TileWarded (18k) do sprawdzenia. | Ratunek inwentarzy + placeholdery. |
| 6 | **AE2** | 2478 TE. Storage cells + patterns = najcenniejsze dane graczy. | Backup zawartości + konwersja NBT. |
| 7 | **CustomNPCs** | 7678 TE, ale głównie meble. NPC → odtworzenie. | Podział na meble (Supplementaries) i NPC (Easy NPC). |

### 🟡 Priorytet 3 — Średnia waga (można zastąpić lub zrekonstruować)

| # | Mod | Powód | Akcja |
|---|-----|-------|-------|
| 8 | **MrCrayfish Furniture** | 5467 TE. Jest port v7.0.x! | Użyć portu + wypakować inwentarze. |
| 9 | **Thermal Series** | 4289 TE. Dukty ~4154 TE. | Remap ID dukty → Thermal Dynamics. |
| 10 | **Better Storage** | 3017 TE. Skrzynie/lockery. | Wypakowanie + Sophisticated Storage. |
| 11 | **Extra Utilities** | 3098 TE (głównie Filing Cabinet). | Filing Cabinet → Sophisticated Storage barrels. |
| 12 | **Forestry** | 7710 TE (głównie liście 7293). | Liście → vanilla. Apiary → Productive Bees. |
| 13 | **Witchery** | 1460 TE. Poppet Shelf (1069). | Ratunek + Hexerei/Enchanted. |
| 14 | **BiblioCraft** | 1313 TE. Brak portu. | Supplementaries + Handcrafted. |
| 15 | **Open Modular Turrets** | 1166 TE. Obrona bazy. | K-Turrets (najbliższy funkcjonalnie). |

### 🟢 Priorytet 4 — Niski (łatwa konwersja lub ignorowanie)

| # | Mod | Powód | Akcja |
|---|-----|-------|-------|
| 16 | **ProjectRed** | 1738 TE (głównie lampy 1664). | Lampy → prosty remap. |
| 17 | **Mekanism** | 1734 TE. Ten sam mod. | Semantyczny remap + NBT. |
| 18 | **ComputerCraft** | 1460 TE. CC:Tweaked. | Remap ID + skrypty Lua. |
| 19 | **Reliquary** | 1592 TE. Port istnieje. | Reliquary Reincarnations. |
| 20 | **Big Reactors** | 924 TE. Extreme Reactors. | Multibloki do rekonstrukcji. |
| 21 | **IC2** | 393 TE. Semantyczny remap. | Mekanism/Thermal. |
| 22 | **BuildCraft** | 266 TE. Niskie wykorzystanie. | Pipez + XNet + Create. |
| 23 | **Growthcraft** | 456 TE. **Growthcraft CE istnieje!** | Użyć Growthcraft CE 1.18.2. |
| 24 | **Logistics Pipes** | 217 TE. Przejść na AE2. | AE2 + Integrated Dynamics. |
| 25 | **EnderStorage** | 115 TE. EnderStorage 1.8+. | Remap kolorów + NBT. |
| 26 | **Traincraft** | 9 TE. Niskie wykorzystanie. | Create + Steam'n'Rails. |
| 27 | **Placeable Items** | 1 TE. Port istnieje. | Placeable Items 4.7. |
| 28 | **PowerConverters** | 10 TE. Niepotrzebne. | Ignoruj / usuń. |
| 29 | **Chisel** | 2 TE (autoChisel). | Rechiseled + Chipped. |

---

## 5. Zestawienie najlepszych zamienników vs dokumentacja

| Mod 1.7.10 | Docs sugeruje | **Najlepszy zamiennik (rekomendacja)** | Czemu lepszy? | Czy docs ma błąd? |
|------------|--------------|----------------------------------------|---------------|-------------------|
| Armourer's Workshop | Cosmetic Armor Reworked | **Armourer's Workshop 3.2.7-beta** | Jest oficjalny port! Zachowuje skiny/biblioteki. | 🔴 TAK — błąd krytyczny |
| Railcraft | Create: Steam'n'Rails | **Railcraft Reborn 5.x** | ZACHOWUJE oryginalną mechanikę kolei. Create to zupełnie inny system. | 🔴 TAK — brak wzmianki |
| MrCrayfish Furniture | Macaw's / Decocraft | **MrCrayfish Furniture v7.0.x** | Bezpośredni port = zachowanie 5,5k TE bez rekonstrukcji. | 🟠 TAK — nie wspomina o porcie |
| Growthcraft | Farmer's Delight + Brewin' | **Growthcraft Community Edition** | Oryginalny mod zachowuje fermentację, uprawy, mleczarstwo 1:1. | 🟠 TAK — brak wzmianki |
| Placeable Items | Ignoruj | **Placeable Items 4.7** | Jest port na 1.18.2. Bloki/TE wymagają konwersji, nie ignorowania. | 🟠 TAK — błędna klasyfikacja |
| Carpenter's Blocks | FramedBlocks + własny mod (planowany) | **CuttableBlocks (JUŻ ISTNIEJE!) + FramedBlocks** | CuttableBlocks-1.0.0.jar leży w repo — mod jest gotowy. | 🟡 TAK — nieaktualny status |
| Enchanting Plus | Enchanting Infuser / Apotheosis | **Apotheosis (główny) + Enchanting Infuser (dodatek)** | Apotheosis daje więcej funkcji niż EP (max levely, bossy, bookshelfy). | 🟡 Częściowo — Enchanting Infuser to nie port EP |
| Better Storage | Iron Chests + Sophisticated Storage | **Sophisticated Storage (główny)** | Oferuje najwięcej funkcji Better Storage (upgrade'y, filtry, sortowanie). | 🟡 Częściowo — Iron Chests to uproszczenie |
| IC2 | FTB Industrial Contraptions | **Mekanism + Thermal Expansion** | FTBIC jest słabo rozwinięty. Mekanism+Thermal to dojrzałe zamienniki. | 🟡 Częściowo — FTBIC istnieje ale jest słaby |
| Extra Utilities | Extra Utilities Reborn | **Hybryda per-funkcja** | ExU Reborn niekompletny. Osobne mody (Torchmaster, Angel Block, Cursed Earth, Pipez) dają więcej. | 🟡 Częściowo — hybryda lepsza |
| Logistics Pipes | Pretty Pipes / AE2 | **AE2 + Integrated Dynamics** | AE2 pokrywa storage+autocraft. Integrated Dynamics = programmable logic (najbliżej zaawansowanych LP). | 🟡 Częściowo — ID to ważny dodatek |
| Open Modular Turrets | Immersive Engineering | **K-Turrets (główny) + IE (uzupełnienie)** | K-Turrets ma modularność podobną do OMT (tier-y, amunicja, targetowanie). IE ma tylko 2-3 typy. | 🟡 Częściowo — K-Turrets lepszy |
| Thaumcraft | Ars Nouveau + Occultism + Botania | **Ars Nouveau + Occultism + Botania + Hexerei** | Hexerei dodaje kociołki/alkemię najbliższą Thaumcraft (w połączeniu z Ars/Occultism). | 🟡 Częściowo — Hexerei wzmacnia klimat |
| Witchery | Hexerei / Enchanted | **Hexerei + Enchanted: Witchcraft + Occultism** | Hexerei = bezpośrednio inspirowane Witchery. Enchanted = wampiry/folklor. Occultism = poppets→familiars. | 🟡 Częściowo — zestaw lepszy |
| Traincraft | Create + Steam'n'Rails | **Create + Steam'n'Rails + Valkyrien Skies 2 + Eureka** | VS2+Eureka = fizyka statków/pojazdów z bloków (zamiast sterowców Traincraft). | 🟡 Częściowo — VS2 ważne dla sterowców |
| CustomNPCs | Easy NPC | **Easy NPC + FTB Quests + Supplementaries/Handcrafted** | Meble CustomNPCs (7k TE) to osobna kategoria — warto użyć dedykowanych modów meblowych. | 🟡 Częściowo — meble wymagają osobnego traktowania |
| BuildCraft | Pipez + XNet + RFTools Builder | **Pipez + XNet + RFTools Builder + Create + Integrated Dynamics** | Create = pompy/tanki (najbliżej BC). Integrated Dynamics = programmable logic (najbliżej BC gates). | 🟡 Częściowo — Create i ID to ważne dodatki |
| BiblioCraft | Supplementaries + FramedBlocks + Immersive Paintings | **Supplementaries + Handcrafted + FramedBlocks + Immersive Paintings + Another Furniture** | Handcrafted + Another Furniture dodają stoły/krzesła/sofy najbliższe BiblioCraft. | 🟡 Częściowo — brak Handcrafted w docs |

---

## 6. Finalne rekomendacje przed konwersją

### 6.1 Aktualizacja dokumentacji (pilne)

1. **cz1.md** — poprawić Armourer's Workshop (jest port 1.18.2).
2. **cz3.md** — dodać Growthcraft CE jako dostępny port.
3. **cz4.md** — poprawić: Railcraft Reborn istnieje, MrCrayfish Furniture ma port, Placeable Items do konwersji (nie ignorowania).
4. **PLAN.md / AGENTS.md** — zaktualizować status Carpenter's Blocks (CuttableBlocks już istnieje).

### 6.2 Przygotowanie narzędzi konwersyjnych

1. **Narzędzie remapujące multiparty** (ForgeMultipart → CB Multipart) — priorytet #1.
2. **Narzędzie remapujące covery Carpenter's Blocks** (ID 1.7.10 → blockstate 1.18.2).
3. **Konwerter NBT AE2** (storage cells, patterns, kanały).
4. **Konwerter NBT Mekanism/Thermal** (maszyny, dukty, side-config).

### 6.3 Testy headless

1. **Railcraft Reborn** — test stabilności na serwerze (3 min ticków + restart).
2. **Armourer's Workshop 1.18.2** — test kompatybilności NBT skinów.
3. **Growthcraft CE** — test fermentacji i upraw na testowej mapie.
4. **MrCrayfish Furniture v7.0.x** — test inwentarzy (fridge, mailbox).

### 6.4 Porządkowanie mapy

1. Usunąć pozostałości po nieistniejących modach: `SecretRooms`, `enderio`, `galacticraft`, `hee`, `JABBA`.
2. Sprawdzić czy `TileWarded` (18116) to faktyczne bloki Thaumcraft czy efekty wizualne (jeśli efekty — można usunąć).
3. Zidentyfikować najpopularniejsze "covery" w Carpenter's Blocks (top 20 tekstur) i przygotować dla nich mapping.

---

*Analiza wykonana na podstawie skanu 597 368+ Tile Entities z mapy 1.7.10 (5GB).*
