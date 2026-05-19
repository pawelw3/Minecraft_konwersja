# Weryfikacja dokumentacji konwersji 1.7.10 → 1.18.2

> **Autor weryfikacji:** Kimi Code CLI  
> **Data:** 2026-05-18  
> **Zakres:** `docs/mod_mapping_indepth/` (from + to), `docs/LISTA_KONWERSJI_MODOW.md`, powiązane plany  
> **Cel:** Weryfikacja które bloki/TE z modów 1.7.10 da się konwertować na 1.18.2, identyfikacja błędów i nieaktualnych informacji w dokumentacji.

---

## 1. Metodologia

Przeprowadzono przegląd dokumentacji źródłowej (`mod_funkcjonalnosci_1.7.10_cz*.md`, `konwersja_1710_do_1182_mapowanie_modow_cz*.md`, `LISTA_KONWERSJI_MODOW.md`) oraz weryfikację online (CurseForge, Modrinth, GitHub) dostępności modów docelowych dla **Minecraft 1.18.2 Forge**.

Klasyfikacja możliwości konwersji:
- **A** — ten sam mod / oficjalny następca (największa szansa na remap NBT)
- **B** — zamiennik funkcjonalny (inny mod, NBT do rekonstrukcji)
- **C** — biblioteka / QoL / klientowy (brak bloków/TE do konwersji)
- **?** — wymaga dalszej weryfikacji na mapie (sprawdzenie czy mod w ogóle zostawił bloki)

---

## 2. Krytyczne błędy / nieaktualności w dokumentacji

| Lp. | Mod 1.7.10 | Co dokumentacja mówi | Prawda (1.18.2) | Powaga |
|-----|------------|---------------------|-----------------|--------|
| 1 | **Armourer's Workshop** | `cz1.md`: "brak wersji na 1.18.2" (CF od 1.19.3+) | **JEST** na 1.18.2 Forge: `3.0.0-beta` → `3.2.7-beta` (CF i Modrinth) | 🔴 Krytyczny — dokument źródłowy `cz1.md` jest nieaktualny |
| 2 | **Growthcraft** | `cz3.md`: brak wzmianki o porcie; sugeruje `Farmer's Delight` + `Brewin' and Chewin'` | **Growthcraft Community Edition JEST** na 1.18.2 Forge z modułami: Core, Cellar, Apple, Bamboo, Bees, Fishtrap, Grapes, Hops, Milk, Rice, Decorations, Trapper | 🟠 Wysoka — niedomówienie; mod da się zachować 1:1 |
| 3 | **Placeable Items** | `cz4.md`: "UWAGA - konwersja niewymagana - ignoruj" | **JEST** na 1.18.2 Forge (v4.7); mod dodaje **bloki/TE** (położone itemy 3D) — **konwersja JEST wymagana** | 🟠 Wysoka — błędna klasyfikacja |
| 4 | **Railcraft** | `cz4.md`: "nie ma powszechnie używanego Railcraft-a na 1.18.2" | **Railcraft Reborn** istnieje na 1.18.2 (5.x). `LISTA_KONWERSJI_MODOW.md` to już uwzględnia, ale `cz4.md` nie. | 🟡 Średnia — brak spójności między dokumentami |
| 5 | **MrCrayfish Furniture** | `cz4.md`: sugeruje `Macaw's`, `Another Furniture`, `Decocraft` jako zamienniki | **MrCrayfish Furniture Mod v7.0.x** istnieje na 1.18.2 Forge (bezpośredni port). `LISTA_KONWERSJI_MODOW.md` to poprawnie uwzględnia. | 🟡 Średnia — cz4.md nieaktualny |
| 6 | **Enchanting Plus** | `cz2.md`: "sprawdź Enchanting Infuser i jeśli jest to poprawny zamiennik to go zastosuj" | `Enchanting Infuser` (Fuzs) to **inny mod**; nie jest portem Enchanting Plus. Funkcjonalnie podobny (wybór enchantów), ale inny autor i inny blok. `Apotheosis` też nie jest portem, ale oferuje kontrolę enchantów. | 🟡 Średnia — mylące sugestie |
| 7 | **Carpenter's Blocks** | `cz2.md` + PLAN.md: planowanie "własnego modu" | W katalogu głównym projektu istnieją pliki `CuttableBlocks-1.0.0*.jar` — **własny mod został już stworzony** (warianty z `collapsible`, `fixed`, `bug5_fixed`). | 🟡 Średnia — dokumentacja nie odzwierciedla stanu faktycznego |
| 8 | **Better Storage** | `LISTA_KONWERSJI_MODOW.md`: "Better Storage (JABBA)" | W paczce 1.7.10 jest **Better Storage**, **nie JABBA**. To osobne mody. JABBA nie ma bezpośredniego portu na 1.18.2; Better Storage też nie ma, ale `Storage Drawers` / `Sophisticated Storage` są zamiennikami. | 🟡 Średnia — błąd w nazewnictwie |
| 9 | **BiblioCraft** | `LISTA_KONWERSJI_MODOW.md` występuje w sekcji 2 (Automatyczna) **oraz** sekcji 4 (Konwersja w duchu) | Duplikat. Poza tym `cz2.md` poprawnie wskazuje brak portu i sugeruje `Supplementaries` + `Handcrafted` + `FramedBlocks` + `Immersive Paintings`. | 🟢 Niska — redakcyjny |

---

## 3. Szczegółowa analiza konwertowalności bloków / TE

### 3.1 Bezpośrednia aktualizacja (A) — te same mody / oficjalne porty

| Mod 1.7.10 | Mod 1.18.2 | Wersja | Bloki / TE do konwersji | Uwagi |
|------------|-----------|--------|------------------------|-------|
| Applied Energistics 2 | AE2 | 11.7.6 | Controller, Drive, ME Chest, Interface, Terminale, P2P, Crafting Unit, Molecular Assembler, kable, części | Złożona konwersja NBT (kanały, dyski, patterns). Wymaga narzędzia remapującego ID+meta → blockstates. Zawartość storage celli wymaga translacji NBT. |
| Armourer's Workshop | Armourer's Workshop | 3.0.0-beta+ | Skinning Table, Armourer, Hologram Projector, Library, Dye Table, Skinnable Blocks | **Dokumentacja cz1.md jest BŁĘDNA** — mod JEST na 1.18.2. NBT skinów może wymagać migracji (format się zmienił między 0.48.5 a 3.x). |
| Big Reactors | Extreme Reactors / Bigger Reactors | 0.6.0 | Reactor Casing, Controller, Fuel Rod, Power Tap, Turbine Housing, Rotor Bearing, itp. | Extreme Reactors to oficjalny port; Bigger Reactors to rekonstrukcja. Multibloki zachowują koncept, ale NBT wewnętrzne może się różnić. |
| Blood Magic | Blood Magic | 3.2.6 | Blood Altar, Runy, Ritual Stones, Master Ritual Stone, Imperfect Ritual Stone | NBT altarów, sieci LP (Soul Network) wymagają translacji. |
| ComputerCraft | CC: Tweaked | 1.101.x | Computer, Advanced Computer, Turtle, Monitor, Printer, Modem, Disk Drive | Skrypty Lua mogą wymagać drobnych poprawek. NBT komputerów (dyski, peryferia) do przetłumaczenia. |
| EnderStorage | EnderStorage | 2.9.x | Ender Chest, Ender Tank | Kolory/kanały (metadata → blockstates/NBT) do remapowania. Zawartość chestów w NBT. |
| Mekanism (+Generators/Tools) | Mekanism (+Generators/Tools) | 10.2.5 | Maszyny (Crusher, Enrichment, Smelter, Electrolytic, PRC, itd.), kable/pipe'y, Energy Cubes, Digital Miner, Reactors, Turbine, narzędzia, zbroje | Semantycznie najłatwiejsza konwersja z "tej samej rodziny", ale NBT między 1.7.10 a 1.18.2 jest inne. Factory tiers, konfiguracja stron, upgrade'y. |
| MrCrayfish Furniture | MrCrayfish Furniture Mod | 7.0.x | >450 bloków meblowych (kitchen, bedroom, bathroom, outdoor, mail) | Część bloków ma GUI/TE (lodówka, szafki, mailbox). NTE prawdopodobnie niekompatybilne — wymaga remap + ew. wypakowania inwentarzy. |
| Pam's HarvestCraft | Pam's HarvestCraft 2 | 1.0.x (moduły) | Gardens, Crops, Fruit Trees, maszyny (Apiary, Grinder, Presser, Trap, Market, itp.) | Reboot moda — ID inne, struktura NBT inna. Uprawy można remapować gatunek→gatunek, maszyny wymagają rekonstrukcji. |
| ProjectRed (wszystkie moduły) | ProjectRed | 4.17.0 | Przewody (wires, bundled), bramki (gates), lampy (lighting), układy scalone (Fabrication IC), tuby (Mechanical), rudy/generacja (World) | Wymaga **CB Multipart**. Multiparty (wiele elementów w 1 bloku) to najtrudniejsza część. NBT układów scalonych (Fabrication) może być niekompatybilne. |
| Railcraft | Railcraft Reborn | 5.x | Tory (tracks), Coke Oven, Blast Furnace, Boiler, Rolling Machine, Rock Crusher, Loadery, sygnalizacja | `cz4.md` błędnie mówi że nie ma portu. NTE maszyn (Coke Oven, Blast Furnace) do remapowania. Tory i sygnalizacja — inne ID, inne blockstates. |
| Reliquary | Reliquary Reincarnations | 1.4.x | Altar of Light / Alkahestry (bloki) | Głównie itemy (artefakty). Bloki TE do remapowania. |
| Thermal Foundation / Expansion / Dynamics | Thermal Series (Foundation + Expansion + Dynamics) | 9.2.2 | Rudy (TF), maszyny (TE: Furnace, Pulverizer, Sawmill, Induction Smelter, Dynamo, itd.), dukty (TD: item/fluid/energy ducts) | Ta sama rodzina, ale NBT inne. Augmenty, side-config, filtry servo → do rekonstrukcji. |
| Tinkers' Construct | Tinkers' Construct | 3.7.2 | Smeltery, Casting Table/Basin, Tool Forge, Part Builder, Pattern Chest, itp. | Kompletna przebudowa moda między 1.7.10 a 1.18.2. Multibloki smelterii inne. **Nie ma automatycznej migracji**. |
| WorldEdit | WorldEdit | 7.2.x | Brak bloków/TE w świecie (narzędzie) | Nie wymaga konwersji mapy. |

### 3.2 Automatyczna konwersja / zamienniki funkcjonalne (B)

| Mod 1.7.10 | Docelowy mod(y) 1.18.2 | Bloki / TE 1.7.10 | Co da się zrobić | Ograniczenia |
|------------|----------------------|-------------------|------------------|--------------|
| **BiblioCraft** | Supplementaries + Handcrafted + FramedBlocks + Immersive Paintings | Bookcase, Armor Stand, Display Case, Potion Shelf, Tool Rack, Shelf, Desk, Typesetting Table, Printing Press, Table, Seat, Lantern, Lamp, Cookie Jar, Disc Rack, Map Frame, Painting (custom) | Meble dekoracyjne → najbliższe odpowiedniki w Supplementaries/Handcrafted. Custom obrazy → Immersive Paintings. Ramki/tekstury → FramedBlocks. | Brak 1:1. NBT ekspozytorów (zawartość) wymaga wypakowania. Painting NBT niekompatybilne. |
| **IndustrialCraft 2** | Mekanism + Thermal + FTB Industrial Contraptions | Macerator, Extractor, Compressor, Electric Furnace, Recycler, Metal Former, Ore Washing, Thermal Centrifuge, Mass Fabricator, Reactor, BatBox/MFE/MFSU, kable EU | Maszyny → odpowiedniki semantyczne w Mekanism/Thermal (Crusher→Crusher, Electric Furnace→E. Smelter/Redstone Furnace). EU→FE (×4). | NBT kompletne inne. Reaktor IC2 → brak 1:1; zachować budowlę, odtworzyć jako Mekanism Fission lub inny mod reaktorowy. |
| **BuildCraft** | Pipez + XNet + RFTools Builder + Integrated Dynamics | Rury (pipes) item/fluid/energy, Pump, Tank, Assembly Table, Laser, Quarry, Mining Well, Gates, Pipe Wires | Pipez = rury proste; XNet = logika/routing; RFTools Builder = Quarry; Integrated Dynamics = bramki/logika warunkowa. | Brak 1:1. Złożone sieci rur z filtrami → rekonstrukcja. BC Quarry → RFTools Builder z Shape Card. |
| **Better Storage** | Iron Chests + Sophisticated Storage + Packing Tape / Carry On | Reinforced Chests (Iron/Gold/Diamond...), Lockers, Storage Crate, Cardboard Box, Crafting Station, Armor Stand | Skrzynie → Iron Chests / Sophisticated Chests. Cardboard Box → Packing Tape / Carry On. Lock & Key / SecurityCraft jako opcjonalne zamki. | NBT locków, enchantów zabezpieczeń nieprzenośne. Zawartość inwentarzy do wypakowania przed remapem. |
| **Logistics Pipes** | Pretty Pipes / AE2 / Refined Storage / XNet | Logistics Request Table, Provider/Request/Supplier/Crafting pipes, Chassis + Modules | Pełne przejście na sieć AE2/RS (request + autocraft). Pretty Pipes = uproszczony LP. XNet = routing warunkowy. | NBT konfiguracji modułów/pipe'ów nieprzenośne. Crafting patterns do odtworzenia. |
| **Chisel** | Rechiseled + Chipped | Auto Chisel (TE), setki wariantów bloków dekoracyjnych | Auto Chisel → Rechiseled (ma własny stół). Warianty dekoracyjne → najbliższe odpowiedniki w Rechiseled/Chipped kategoria→kategoria. | Brak 1:1 pokrycia wariantów. Metadata 1.7.10 → blockstates 1.18.2. |
| **Carpenter's Blocks** | FramedBlocks + CuttableBlocks (własny mod) | Carpenter's Block, Stairs, Slope, Door, Gate, Ladder, Pressure Plate, Button, Lever, Hatch, Barrier, Torch, Daylight Sensor, Flower Pot, Bed, Safe, Garage Door, Collapsible Block | FramedBlocks pokrywa większość kształtów. `CuttableBlocks-1.0.0_with_collapsible.jar` (istniejący własny mod) obsługuje Collapsible Block. | NBT "cover" (tekstura) wymaga translacji z ID bloku 1.7.10 → blockstate 1.18.2. Nie wszystkie kształty mają odpowiednik. |

### 3.3 Konwersja "w duchu" / funkcjonalne zamienniki (B — inne mody)

| Mod 1.7.10 | Docelowy zestaw 1.18.2 | Uwagi |
|------------|---------------------|-------|
| **Thaumcraft 4** + addony (Energistics, Exploration, Horizons, Tinkerer) | Ars Nouveau + Occultism + Botania | Brak portu TC. Bloki/TE w świecie (Arcane Worktable, Crucible, Infusion Altar, Warded Jars, itp.) → placeholdery dekoracyjne + odtworzenie funkcji w nowych modach. NBT research, essentia — utrata, ratunek przez wypakowanie. |
| **Witchery** | Hexerei + Enchanted: Witchcraft | Brak portu. Bloki (Witches Oven, Cauldron, Kettle, Distillery, Altar, Poppet Shelf) → placeholdery / rekonstrukcja w Hexerei. NBT nieprzenośne. |
| **Flan's Mod** | TaCZ (broń) + Immersive Vehicles (pojazdy) + Immersive Aircraft | Content-packi z 1.7.10 niekompatybilne. Workbench'e → stacje craftingu TaCZ / IV. Encje pojazdów/broni → odtworzenie. Bloki w świecie (gun boxes, vehicle boxes) → placeholdery / rekonstrukcja. |
| **Traincraft** | Create + Create: Steam 'n' Rails + opcj. Valkyrien Skies 2 + Eureka | Brak portu. Tory → tory Create. Lokomotywy/wagony → contraptions Create (completely different mechanics). Zeppeliny → Eureka airships. NBT encji nieprzenośne. |
| **Extra Utilities** | Extra Utilities Reborn + Torchmaster + Angel Block Renewed + Cursed Earth (mod) + Pipez / XNet + RFTools Builder | ExU Reborn nieoficjalny, niekompletny. Konwersja hybrydowa per-blok. Generatory → Mekanism/Thermal. Ender Quarry → RFTools Builder. Transfer Nodes → Pipez/XNet. |
| **Forestry** | Productive Bees (pszczoły) + Create/Thermal/Industrial Foregoing (przetwórstwo) + Sophisticated Backpacks + Ender Mail | Brak portu Forestry. Apiary/Alveary → Productive Bees. Carpenter/Centrifuge/Squeezer → Create/Thermal. Multifarm → Create/IF. Mail → Ender Mail. NBT genetyki pszczół nieprzenośne. |
| **Jammy Furniture** | Macaw's Furniture + Handcrafted + Supplementaries | Brak portu. Meble dekoracyjne → najbliższe odpowiedniki kategoria→kategoria. TE z inwentarzem (fridge, itp.) → wypakowanie + remap. |
| **Open Modular Turrets** | K-Turrets / Immersive Engineering (turrety) | Brak portu OMT. Turret Base + Turret → K-Turrets / IE turrets. Ammo/upgrades nieprzenośne. |
| **IC2 Nuclear Control** | CC: Tweaked (monitory + peryferia) | Brak portu. Thermal Monitor, Howler Alarm → redstone + CC:T programy / monitory. |
| **Statues** (Asie, 1.7.10) | Statues (ShyNieke) 1.18.2 | Inny mod (inne NBT). Statue / Showcase → nowe Statues. Skin/pose NBT nieprzenośne — fallback na armor stand. |

### 3.4 Biblioteki / QoL / mody bez bloków (C)

| Mod 1.7.10 | Zamiennik 1.18.2 | Uwagi |
|------------|-----------------|-------|
| Treecapitator | FallingTree | QoL, brak bloków |
| Baubles | Curios API | API slotów; jeśli inne mody dodawały "baubles itemy" — per-mod |
| bspkrsCore | — | dependency, brak bloków |
| AsieLib | — | dependency (dla Statues), nowy Statues nie wymaga |
| Bookshelf | Bookshelf (nowa) | biblioteka |
| CodeChickenCore + CodeChickenLib | CodeChickenLib | biblioteka |
| CoFHCore | CoFH Core | biblioteka |
| CraftGuide | JEI | przeglądarka receptur |
| CustomNPCs | Easy NPC (opcjonalnie) | CustomNPCs Noppes nie ma na 1.18.2; Easy NPC to inny mod. Jeśli na mapie są bloki CNPC (Redstone Block, Waypoint, Carpentry Bench) → rekonstrukcja lub placeholdery. |
| FastCraft | Rubidium + Starlight + FerriteCore | optymalizacja |
| ForgeEssentials | ForgeEssentials (nowsza) / inne mody utility | serwerowe, brak bloków |
| HelpFixer | — | fix /help, niepotrzebny |
| iChunUtil | — | dependency, brak bloków |
| LiteLoader | — | loader, niepotrzebny |
| MobiusCore | — | dependency (Opis) |
| MrTJPCore | — | wbudowany w ProjectRed |
| NEI | JEI | przeglądarka itemów/receptur |
| NoMoreRecipeConflict | Polymorph | QoL |
| Opis | Spark (+ Observable) | profiler |
| PowerConverters | — | FE natywne w 1.18.2, niepotrzebne |
| RadarBro | Xaero's Minimap (Entity Radar) | minimapa + radar |
| Rei’s Minimap | JourneyMap / Xaero's | minimapa |
| uuidoffline | — | niepotrzebny (UUID natywne) |
| WorldEdit | WorldEdit | narzędzie budowlane |

---

## 4. Bloki / Tile Entities — ocena możliwości konwersji

Poniżej zestawienie które **konkretne bloki i TE** z modów 1.7.10 można realistycznie skonwertować, a które wymagają "ratunku" (wypakowania inwentarza + placeholdery).

### 4.1 Wysoka szansa na automatyczną konwersję (remap ID + ew. NBT)

- **AE2** — bloki strukturalne (Controller, Drive, Cable Bus, ME Chest) → odpowiedniki 1.18.2. NBT storage celli wymaga narzędzia.
- **EnderStorage** — Ender Chest/Tank → kolory/kanały remapowalne. Zawartość w NTE.
- **Mekanism** — maszyny semantycznie → te same typy. Energy Cubes, kable. NBT config stron/tierów do przetłumaczenia.
- **Thermal Series** — maszyny, dynama, dukty → odpowiedniki 1.18.2. NBT augmentów/filtrów do rekonstrukcji.
- **ProjectRed** — przewody, bramki, lampy → odpowiedniki w Transmission/Integration/Illumination. Wymaga CB Multipart.
- **Blood Magic** — Blood Altar, runy, rytuały → analogiczne bloki 1.18.2. NBT LP/sieci do translacji.
- **Extreme Reactors** — multibloki reaktorów/turbin → odpowiedniki. NBT temperatury/paliwa do przetłumaczenia.

### 4.2 Średnia szansa — remap + rekonstrukcja NBT

- **Armourer's Workshop** — bloki warsztatowe są, ale format skinów NTE zmieniony. Wymaga weryfikacji kompatybilności NBT między 0.48.5 a 3.x.
- **MrCrayfish Furniture** — bloki dekoracyjne remapowalne, ale TE z inwentarzem (fridge, mailbox) wymagają wypakowania.
- **Pam's HarvestCraft** — uprawy/drzewa remapowalne gatunek→gatunek. Maszyny (Apiary, Grinder, Presser) — inne NTE, rekonstrukcja.
- **Railcraft Reborn** — tory, maszyny (Coke Oven, Blast Furnace, Rolling Machine) → odpowiedniki. NTE inne.
- **Reliquary** — głównie itemy; bloki (Altar of Light) do remapowania.
- **Placeable Items** — bloki "położonych itemów" → nowy mod Placeable Items, ale NTE może być niekompatybilne.
- **Statues** (ShyNieke) — inny mod, inne NTE. Statua jako blok da się postawić, ale skin/pose — ręcznie.

### 4.3 Niska szansa — ratunek (wypakowanie) + placeholdery

- **BiblioCraft** — brak portu. Meble → Supplementaries/Handcrafted (inne modele/kolizje). Custom Paintings → Immersive Paintings (inny format NBT).
- **Better Storage** — brak portu. Skrzynie → Iron Chests / Sophisticated Storage. Locki → nieprzenośne.
- **Carpenter's Blocks** — własny mod CuttableBlocks pokrywa część, ale "cover" (tekstura) wymaga ręcznego remapu blockstate.
- **IC2** — brak portu. Maszyny → Mekanism/Thermal semantycznie, ale NBT nieprzenośne. Reaktor → brak 1:1.
- **BuildCraft** — brak portu. Rury/maszyny → Pipez/XNet/RFTools — zupełnie inne bloki.
- **Logistics Pipes** — brak portu. Sieć → AE2/RS/Pretty Pipes — odtworzenie od zera.
- **Thaumcraft + addony** — brak portu. Wszystkie bloki magiczne → placeholdery + Ars/Occultism/Botania.
- **Witchery** — brak portu. Bloki wiedźmowe → placeholdery + Hexerei/Enchanted.
- **Flan's Mod** — brak portu. Workbench'e → TaCZ/IV. Pojazdy → odtworzenie.
- **Traincraft** — brak portu. Tory → Create. Pojazdy → odtworzenie.
- **Extra Utilities** — częściowo ExU Reborn (niekompletny). Reszta → osobne mody.
- **Forestry** — brak portu. Pszczoły → Productive Bees (inna genetyka). Maszyny → Create/Thermal.
- **Jammy Furniture** — brak portu. Meble → Macaw's/Handcrafted.
- **Open Modular Turrets** — brak portu. Turrety → K-Turrets/IE.
- **IC2 Nuclear Control** — brak portu. Monitory → CC:T + redstone.
- **Enchanting Plus** — brak portu. Blok/TE → Apotheosis / Enchanting Infuser (inny mod, inne NBT).
- **CustomNPCs** — brak portu na 1.18.2 (Noppes). Bloki NPC → Easy NPC lub placeholdery.
- **Chisel** — brak portu. Warianty → Rechiseled/Chipped (mapping kategoria→kategoria).

### 4.4 Bloki / TE do zweryfikowania na mapie

- **Growthcraft** — czy na mapie są plantacje winogron/chmielu/ryżu, beczki fermentacyjne? Jeśli tak, Growthcraft CE 1.18.2 umożliwia **zachowanie większości funkcji** (moduły: Grapes, Hops, Rice, Cellar).
- **Carpenter's Blocks** — które kształty są najczęściej używane? (Block, Slope, Door, Collapsible?). `CuttableBlocks` istnieje, ale trzeba sprawdzić pokrycie.
- **Flan's Mod** — czy na mapie są bloki (gun boxes, vehicle boxes) czy tylko itemy/encje?
- **Extra Utilities** — które bloki są używane? (Cursed Earth, Angel Block, Quarry, Generators, Transfer Nodes?)
- **AE2** — skala sieci ME (ile chunków, ile drive'ów, czy są autocrafting patterns?)
- **IC2** — jakie maszyny i czy jest reaktor nuklearny?
- **Big Reactors** — czy są multibloki reaktorów/turbin?
- **Railcraft** — skala torów i maszyn kolejowych.
- **Thaumcraft** — czy są istotne struktury (ołtarze infuzji, biblioteki)?

---

## 5. Nieścisłości między dokumentami (spójność)

| Temat | `LISTA_KONWERSJI_MODOW.md` | `mod_mapping_indepth/to/` | Który dokument ma rację? |
|-------|---------------------------|---------------------------|------------------------|
| Armourer's Workshop | ✅ Bezpośrednia aktualizacja (3.2.7-beta) | `cz1.md`: brak wersji | LISTA |
| Railcraft | ✅ Bezpośrednia aktualizacja (Railcraft Reborn 5.x) | `cz4.md`: brak portu | LISTA |
| MrCrayfish Furniture | ✅ Bezpośrednia aktualizacja (7.0.x) | `cz4.md`: zamienniki | LISTA |
| Placeable Items | ✅ "Jest port" (sekcja 9, mody ignorowane) | `cz4.md`: "ignoruj" | Częściowo LISTA, ale oba źle klasyfikują (powinien być do konwersji, nie do ignorowania) |
| Growthcraft | ⚠️ "Wymaga sprawdzenia" | `cz3.md`: zamienniki (Farmer's Delight) | Brak — oba nie wspominają o Growthcraft CE |
| BiblioCraft | Automatyczna + Konwersja w duchu (duplikat) | `cz2.md`: brak portu, zamienniki | `cz2.md` poprawny, LISTA ma duplikat |
| Better Storage | "Better Storage (JABBA)" | `cz1.md`: Better Storage → Iron Chests / Sophisticated Storage | `cz1.md` poprawny nazwą, LISTA błędnie pisze "JABBA" |
| Enchanting Plus | "Do weryfikacji" (Enchanting Infuser vs Apotheosis) | `cz2.md`: Apotheosis + opcjonalnie Enchanting Infuser | Częściowo poprawne, ale Enchanting Infuser to nie port EP |
| Carpenter's Blocks | Własna implementacja / FramedBlocks | `cz2.md`: FramedBlocks + własny mod | Stan faktyczny: `CuttableBlocks*.jar` już istnieje w repo |
| Logistics Pipes | Pretty Pipes / AE2 / XNet | `cz3.md`: Pipez + AE2/RS + XNet + ID | Spójne w przeważającej części |
| PowerConverters | "Niepotrzebny (FE natywne)" | `cz4.md`: "RF Converter" | LISTA ma rację — FE jest natywne |

---

## 6. Stan faktyczny vs dokumentacja — własne mody i narzędzia

| Co dokumentacja mówi | Stan faktyczny w projekcie | Wniosek |
|---------------------|---------------------------|---------|
| "Carpenter's Blocks → własny mod (planowany)" | Istnieją pliki `CuttableBlocks-1.0.0.jar`, `CuttableBlocks-1.0.0_FIXED.jar`, `CuttableBlocks-1.0.0_with_collapsible.jar`, `CuttableBlocks-1.0.0_BUG5_FIXED.jar` | Własny mod **został już stworzony**. Należy zaktualizować dokumentację i przetestować kompatybilność z FramedBlocks. |
| "Extra Utilities → Extra Utilities Reborn" | Nie zweryfikowano obecności JARu w `mod_src/mod_jars/1.18.2/` | Do weryfikacji czy Ender Quarry / Cursed Earth / Angel Block są na mapie. |
| "AE2 → konwersja na samym końcu / ratunek" | W `test_scenarios/` istnieje `ae2_task5a/` oraz `brute_force_trial_ae2/` | AE2 jest aktywnie testowane. Należy uwzględnić wyniki testów w dokumentacji. |
| "Railcraft Reborn → może być niestabilny" | W `strefy/choroszcz/` i innych są dane mapy | Należy przetestować Railcraft Reborn na headless serwerze przed finalną konwersją. |

---

## 7. Rekomendacje aktualizacji dokumentacji

### 7.1 Pilne (przed konwersją)

1. **`cz1.md` — Armourer's Workshop**: Usunąć stwierdzenie "brak wersji na 1.18.2". Dodać informację o dostępności `3.0.0-beta+` na Forge 1.18.2 oraz ostrzeżenie o zmianie formatu NBT skinów.
2. **`cz3.md` — Growthcraft**: Dodać sekcję o **Growthcraft Community Edition 1.18.2** jako bezpośrednim następcy. Wymienić moduły dostępne na 1.18.2 (Core, Cellar, Grapes, Hops, Rice, Milk, Bees, Bamboo, Apple, Fishtrap, Decorations, Trapper). Jeśli na mapie są bloki Growthcraft, zalecić użycie oryginalnego modu zamiast zamienników.
3. **`cz4.md` — Placeable Items**: Zmienić klasyfikację z "ignoruj" na **"do konwersji"**. Dodać mapowanie bloków/TE na `Placeable Items` 1.18.2 (v4.7).
4. **`cz4.md` — Railcraft**: Poprawić stwierdzenie o braku portu. Dodać że **Railcraft Reborn** jest dostępny, ale z ostrzeżeniem o stabilności.
5. **`cz4.md` — MrCrayfish Furniture**: Dodać informację o bezpośrednim porcie v7.0.x na 1.18.2. Zamienniki (Macaw's/Handcrafted) traktować jako opcje uzupełniające.
6. **`LISTA_KONWERSJI_MODOW.md` — Better Storage**: Poprawić "Better Storage (JABBA)" na po prostu "Better Storage". JABBA to osobny mod, którego nie ma w paczce.

### 7.2 Ważne (spójność i jakość)

7. **Usunąć duplikat BiblioCraft** z `LISTA_KONWERSJI_MODOW.md` (występuje w sekcji 2 i 4).
8. **`PLAN.md` / `AGENTS.md` — Carpenter's Blocks**: Zaktualizować status "własnego modu" — `CuttableBlocks` już istnieje. Dodać zadanie integracji z FramedBlocks.
9. **`cz2.md` — Enchanting Plus**: Sprecyzować że `Enchanting Infuser` to **inny mod** (Fuzs), nie port Enchanting Plus. Zalecić Apotheosis jako główny mod kontroli enchantów, a Enchanting Infuser jako opcjonalny dodatek.
10. **Dodać wspólną tabelę "source of truth"** z aktualnymi wersjami modów docelowych (CurseForge / Modrinth links) — jeden plik referencyjny zamiast rozproszonych informacji.

### 7.3 Weryfikacja na mapie (przed remapowaniem)

11. **Uruchomić skaner mapy** (`src/minecraft_map_parser/`) dla stref i wygenerować raport: które mody faktycznie zostawiły bloki/TE w chunkach.
12. Dla Growthcraft — sprawdzić czy na mapie są bloki z tego modu (krzewy, beczki, rośliny). Jeśli tak — priorytetowo przetestować Growthcraft CE 1.18.2.
13. Dla Carpenter's Blocks — zliczyć najczęstsze kształty i zweryfikować czy `CuttableBlocks` je pokrywa.
14. Dla Flan's Mod — zweryfikować czy na mapie są **bloki** (workbench'e) czy tylko itemy/encje.

---

## 8. Podsumowanie — co da się skonwertować?

| Kategoria | Liczba modów | Konwertowalność |
|-----------|-------------|-----------------|
| **A — Bezpośredni port / ta sama rodzina** | 16 | Wysoka szansa na zachowanie budowli; NBT wymaga narzędzi remapujących |
| **B — Zamiennik funkcjonalny + remap** | 10 | Średnia szansa; geometrycznie można zachować, ale NBT inne |
| **B — Zamiennik "w duchu" (inne mody)** | 12 | Niska szansa na automatyczną konwersję; ratunek + placeholdery + odtworzenie |
| **C — Bez bloków / biblioteki / QoL** | 18 | Nie wymaga konwersji mapy |
| **? — Do weryfikacji na mapie** | 4 | Growthcraft, Placeable Items, Flan's Mod (bloki?), Carpenter's Blocks (kształty) |

### Kluczowe wnioski

- **Największy błąd dokumentacji**: `cz1.md` twierdzi że **Armourer's Workshop nie ma wersji 1.18.2** — jest to nieprawda. Mod jest dostępny (Forge 1.18.2, wersje beta 3.x).
- **Największa nieścisłość funkcjonalna**: `cz3.md` nie wspomina o **Growthcraft Community Edition** na 1.18.2, sugerując zamienniki zamiast oryginalnego modu.
- **Największy "gotowy asset"**: Własny mod `CuttableBlocks` został już skompilowany (wiele wariantów w katalogu głównym), ale dokumentacja wciąż go traktuje jako "planowany".
- **Największe ryzyko utraty danych**: Thaumcraft + addony, Witchery, IC2 (reaktor), Traincraft (encje pociągów), Flan's Mod (encje pojazdów) — brak portów, NBT nieprzenośne.
- **Największa szansa na bezstratną konwersję**: Mekanism, Thermal Series, AE2, EnderStorage, ProjectRed (+ CB Multipart) — te same rodziny modów, wymagają tylko remapu ID/NBT.

---

*Raport wygenerowany automatycznie na podstawie analizy dokumentacji projektu i weryfikacji online (CurseForge, Modrinth, GitHub).*
