# Minecraft 1.7.10 — spis funkcjonalności modów (start)

> Cel: zebrać w jednym miejscu **funkcjonalności** modów z Twojego modpacka 1.7.10, z naciskiem na: **bloki**, **itemy**, **tile entities**, **GUI**, **komendy**, **konfigurację**, **zależności**.  
> Stan: lista przygotowana na podstawie publicznych wiki/dokumentacji. **Bez analizy plików `.jar`** nie da się w 100% zagwarantować pełnej listy *registry names* ani klas TE dla każdej wersji — ale poniżej jest możliwie obszerna, praktyczna rozpiska.  
> Data wygenerowania: 2026-01-30

---

## 1) bspkrsCore (`[1.7.10]bspkrsCore-universal-6.15.jar`)

**Typ:** biblioteka / dependency (rdzeń dla modów bspkrs)  
**Zależności:** wymagany przez m.in. Treecapitator (i inne mody bspkrs)

### Funkcje
- Dostarcza **wspólne klasy** wykorzystywane przez mody autora bspkrs (helpery konfiguracyjne, wspólna infrastruktura).  
- **Nie dodaje** własnych bloków ani contentu (w typowych instalacjach jest tylko dependency).

### Bloki / itemy / encje / TE
- **Bloki:** brak  
- **Itemy:** brak  
- **Encje:** brak  
- **Tile Entities:** brak

### Źródła
- CurseForge (plik 6.15): https://www.curseforge.com/minecraft/mc-mods/bspkrscore/files/2218819  
- GitHub (repo): https://github.com/bspkrs-mods/bspkrsCore

---

## 2) Treecapitator (`[1.7.10]Treecapitator-universal-2.0.4.jar`)

**Typ:** QoL / narzędzie do ścinania drzew  
**Zależności:** wymaga bspkrsCore

### Funkcje (główne)
- **Ścina całe drzewo** po zniszczeniu jednego klocka kłody (log).
- W wersji Forge ma wsparcie dla **drzew z modów**, konfigurowalne wpisami w configu (domyślnie wspiera szereg modów i potrafi skanować Ore Dictionary pod kątem bloków “tree-related”).
- Opcje balansujące, m.in. możliwość spowolnienia ścinania w zależności od wysokości drzewa.

### Kluczowe opcje / zachowania (FAQ)
- `treeHeightDecidesBreakSpeed` – próba ograniczenia “imbalance” przez wydłużenie czasu niszczenia pierwszej kłody (można wyłączyć).
- `destroyLeaves` – niszczenie liści (z typowymi warunkami dot. “natural decay”).
- `requireLeafDecayCheck` – kontrola “czy liście są oznaczone do naturalnego zaniku”; wyłączenie omija problem z niektórymi modowymi logami.

### Pliki konfiguracyjne (wg wiki)
- ModLoader: `<.minecraft>/config/mod_treecapitator.bsprop.cfg`
- Forge: `<.minecraft>/config/TreeCapitator.cfg`

### Bloki / itemy / encje / TE
- **Bloki:** brak (modyfikuje zachowanie ścinania istniejących logów/leaves)
- **Itemy:** brak
- **Encje:** brak
- **Tile Entities:** brak

### GUI / klawisze / komendy
- Brak własnych bloków-UI; wszystko przez **config**.

### Źródła
- CurseForge (plik 2.0.4): https://www.curseforge.com/minecraft/mc-mods/treecapitator/files/2218771  
- Wiki (FAQ/Configuration): https://github.com/bspkrs/Treecapitator/wiki

---

## 3) Applied Energistics 2 (`appliedenergistics2-rv3-beta-6.jar`)

**Typ:** zaawansowana logistyka i magazynowanie (ME network)

### Funkcje (skrót)
- **ME Network**: cyfrowy magazyn przedmiotów, automatyzacja, crafting, kanały (channels), energię (AE) i kontrolery.
- **Terminale**: podgląd/sortowanie magazynu, crafting terminal, pattern terminal itd.
- **Autocrafting**: wzorce (patterns), crafting CPUs, crafting monitors.
- **Import/Export**: bus’y do transferu przedmiotów i płynów, storage buses, level emitters.
- **Integracje**: interfejsy, P2P, quantum bridge (w zależności od wersji/konfiguracji).
- **Materiały**: certus quartz, fluix, sky stone itd.

### Bloki / części / itemy — lista (wg “AE2 Site Archive: Text-List”)
Poniższa lista to **kompletna lista nazw** z archiwalnej dokumentacji AE2 (dla gałęzi z epoki 1.7.10). To miks:
- **bloków** (np. ME Controller, Drive, Charger…),
- **części sieci** (np. Import/Export/Storage Bus, Terminale, P2P…),
- **przedmiotów i komponentów** (np. procesory, komórki, narzędzia, materiały).

**A → C**
- Advanced Card / Advanced Inscriber / Basic Card / Basic Inscriber  
- Cable Anchor / Cable Bus / Cable Bus Facade / Cable Bus Part  
- Certus Quartz Cutting Knife / Certus Quartz Dust / Certus Quartz Pickaxe / Certus Quartz Wrench  
- Charged Certus Quartz Crystal / Chest (ME Chest) / Chorus (P2P Tunnel - Chorus)  
- Color Applicator / Colorless Cable Anchor / Condenser / Crafting Card / Crafting CPU / Crafting Co-Processing Unit / Crafting Monitor  
- Crafting Storage 1k / 4k / 16k / 64k  
- Crafting Terminal / Crafting Unit / Crank

**D → G**
- Dark Illuminated Panel / Dense Cable Anchor  
- Encoded Pattern / Energy Acceptor / Energy Cell / Energy Level Emitter / Energy Terminal  
- Export Bus / Formation Plane  
- Fuzzy Card  
- Growth Accelerator

**I → M**
- Illuminated Panel / Import Bus / Interface / Interface Terminal  
- Inverted Toggle Bus / Item Cell 1k / 4k / 16k / 64k  
- Item Storage Cell / Item View Cell  
- Level Emitter  
- Matter Cannon / ME Chest / ME Controller / ME Drive / ME IO Port  
- ME P2P Tunnel / ME Quantum Ring / ME Security Terminal / ME Terminal / ME Wireless Access Terminal  
- Memory Card / Molecular Assembler / Monitor Bus  
- Network Tool

**P → S**
- P2P Tunnel (ME P2P Tunnel)  
- Pattern Encoder / Pattern Terminal  
- Portable Cell / Precision Export Bus  
- Quartz Axe / Quartz Fiber / Quartz Glass / Quartz Grindstone / Quartz Hoe / Quartz Knife / Quartz Pickaxe / Quartz Shovel / Quartz Sword / Quartz Wrench  
- Quantum Link Chamber / Quantum Ring  
- Redstone Card  
- Spatial IO Port / Spatial Pylon / Spatial Storage Cell / Spatial Storage Cell (Component)  
- Speed Card / Storage Bus / Storage Cell 1k / 4k / 16k / 64k / Storage Monitor / Storage Terminal  
- Sky Stone / Sky Stone Block / Sky Stone Chest / Sky Stone Door / Sky Stone Small Brick / Sky Stone Stairs / Sky Stone Wall  
- Slime P2P Tunnel / Small Quartz Bud / Small Dense Cable Anchor

**T → W**
- Toggle Bus / Transparent Facade  
- Vibration Chamber  
- Wireless Access Point / Wireless Booster / Wireless Receiver / Wireless Terminal

### Tile Entities (praktycznie)
W AE2 “TE / node” mają przede wszystkim: **Controller, Drive, IO Port, Interface (blok), Terminale (niektóre jako bloki), Charger, Vibration Chamber, Spatial IO Port, Quantum Link Chamber/Ring**, itp.  
Części montowane na kablach (bus’y, terminale “na kablu”) to zwykle “party” przypinane do **Cable Bus** (często też jako osobne node’y w sieci).

### Źródła
- AE2 Site Archive — Text-List: https://appliedenergistics.org/ae2-site-archive/Text-List  
- AE2 Site Archive — Block & Item List: https://appliedenergistics.org/ae2-site-archive/Block__Item_List

---

## 4) Armourer’s Workshop (`Armourers-Workshop-1.7.10-0.48.5.jar`)

**Typ:** kosmetyczne skiny pancerza/narzędzi/bloków (nie zmienia statystyk, tylko wygląd)

### Funkcje (główne)
- Tworzenie i nakładanie **skinów** na pancerze / bronie / narzędzia (i w wielu wersjach także na niektóre bloki).
- Edytor/“warsztat” z blokami roboczymi (m.in. **Skinning Table** + narzędzia do malowania).
- System bibliotek skinów (lokalna/globalna) i cache’owania skinów.

### Bloki (najczęściej spotykane w 1.7.10)
> Lista bloków w Armourer’s Workshop bywa dłuższa zależnie od wersji i configu (multibloki, child blocks). Bez analizy JAR podaję **typowe** elementy występujące w 0.48.x.
- Skinning Table (stół do tworzenia/edycji)  
- Armourer / Workshop (blok nakładania i zarządzania skinami)  
- Hologram Projector (podgląd)  
- Global Skin Library / Skin Library (biblioteka skinów)  
- Dye/Colour-related bloki (mieszanie kolorów / farbowanie — nazewnictwo zależne od wersji)

### Komendy / konfiguracja
- Mod posiada zestaw komend administracyjnych (np. w changelogach przewija się `setItemAsSkinnable`).  
- Sporo ustawień jest w plikach konfiguracyjnych (cache skinów, integracje, uprawnienia).

### Tile Entities
- Praktycznie wszystkie “bloki maszynowe” (Skinning Table / library / projector / armourer) są TE ze względu na GUI i przechowywanie danych.

### Źródła
- CurseForge (projekt): https://www.curseforge.com/minecraft/mc-mods/armourers-workshop  
- CurseForge (plik 0.48.5 changelog): https://www.curseforge.com/minecraft/mc-mods/armourers-workshop/files/3005075

---

## 5) AsieLib (`AsieLib-1.7.10-0.4.8.jar`)

**Typ:** biblioteka / dependency

### Funkcje
- Zbiór wspólnych klas autorstwa asie, wykorzystywany przez część jego modów.

### Bloki / itemy / encje / TE
- **Bloki:** brak  
- **Itemy:** brak  
- **Encje:** brak  
- **Tile Entities:** brak  

### Źródła
- Wiki/entry: https://wiki.vexatos.com/wiki/AsieLib

---

## 6) Backpacks (Eydamos) (`backpack-2.0.1-1.7.x.jar`)

**Typ:** przenośny magazyn (itemy-plecaki)

### Funkcje
- Plecaki w **3 rozmiarach**: Small / Middle / Big.
- Materiały do wyższych tierów: **Tanned Leather** i **Bound Leather**.
- System “Frames” i “Pieces” (top/middle/bottom) do craftingu.
- Legacy plecaki: Ender/Workbench.

### Itemy (wg wiki FTB)
- Backpacks: Small / Middle / Big  
- Materiały: Tanned Leather, Bound Leather, Stone Stick, Iron Stick  
- Backpack Pieces: Top, Middle, Bottom  
- Frames: Wooden Frame, Stone Frame, Iron Frame  
- Legacy: Ender Backpack, Workbench Backpack, Big Workbench Backpack

### Bloki / TE / encje
- **Bloki:** brak  
- **Tile Entities:** brak  
- **Encje:** brak

### Źródła
- FTB Wiki: https://ftb.fandom.com/wiki/Backpacks

---

## 7) Baubles (`Baubles-1.7.10-1.0.1.10.jar`)

**Typ:** API + dodatkowe sloty ekwipunku gracza

### Funkcje
- Dodaje osobny ekwipunek **Baubles** otwierany domyślnie klawiszem **B**.
- Sloty (w 1.7.10): **amulet**, **belt**, **2x ring**.
- Ma służyć głównie jako **addon/API** dla innych modów.

### Content
- Baubles praktycznie nie dodaje contentu, poza **Miner’s Ring**.

### Bloki / TE / encje
- **Bloki:** brak  
- **Tile Entities:** brak  
- **Encje:** brak

### Źródła
- FTB Wiki: https://ftb.fandom.com/wiki/Baubles/en

---

## 8) Better Storage (`Better-Storage-Mod-1.7.10 (4).jar`)

**Typ:** storage + zabezpieczenia + kilka “gadżetów”

### Funkcje (skrót)
- Nowe sposoby przechowywania i zabezpieczenia itemów: skrzynie, szafki, skrzynie modułowe.
- System **Locks & Keys** oraz enchantów wpływających na zabezpieczenia.
- Dodatkowe rzeczy niezwiązane stricte ze storage (np. Frienderman, Block of Flint).

### Bloki (wg FTB Wiki – lista nawigacyjna moda)
**Chests (Reinforced)**
- Reinforced Iron / Gold / Diamond / Emerald / Copper / Tin / Silver / Zinc / Steel Chest  
- (czasem warianty specjalne zależne od instalacji)

**Lockers**
- Locker  
- Reinforced Iron / Gold / Diamond / Emerald / Copper / Tin / Silver / Zinc / Steel Locker

**Inne**
- Storage Crate  
- Armor Stand  
- Crafting Station  
- Block of Flint  
- Cardboard Box

### Itemy (wg FTB Wiki – lista nawigacyjna moda)
**Backpacks**
- Backpack, Ender Backpack, Thaumaturge’s Backpack

**Locks & Keys**
- Key, Lock, Keyring, Master Key

**Cardboard**
- Cardboard Sheet  
- Cardboard Armor (Helmet/Chestplate/Leggings/Boots)  
- Cardboard Tools (Sword/Pickaxe/Shovel/Axe/Hoe)

**Inne**
- Drinking Helmet  
- Slime in a Bucket

### Enchanty (wg FTB Wiki)
- Lockpicking, Morphing, Unlocking, Persistence, Security, Shock, Trigger

### Moby/creatures (wg FTB Wiki)
- Frienderman  
- Cluckington

### Tile Entities (praktycznie)
- W zasadzie wszystkie bloki-magazyny (Reinforced Chests, Lockers, Storage Crate, Cardboard Box, Crafting Station, Armor Stand) używają TE do przechowywania zawartości, stanu, locków/UID itp.

### Źródła
- FTB Wiki (mod + listy): https://ftb.fandom.com/wiki/BetterStorage  
- FTB Wiki (Storage Crate): https://m.ftbwiki.org/Storage_Crate  
- FTB Wiki (Reinforced Chest): https://ftb.fandom.com/wiki/Reinforced_Chest_(BetterStorage)  
- FTB Wiki (Locker): https://ftb.fandom.com/wiki/Locker_(BetterStorage)  
- FTB Wiki (Cardboard Box): https://ftb.fandom.com/wiki/Cardboard_Box_(BetterStorage)

---

# Co dalej?

Jeżeli chcesz **naprawdę “pełne” listy** typu:
- wewnętrzne *registry names* bloków/itemów,
- pełna lista **TileEntity** (klasy + nazwy rejestracji),
- lista **encj** i **komend** wykryta automatycznie,

to najszybsza droga to analiza zawartości `.jar` (np. dekompilacja + wyszukiwanie rejestracji `GameRegistry.registerBlock/registerTileEntity` albo generowanie raportu w środowisku dev). Wtedy da się zrobić “twardy” dump per wersja moda z Twojego folderu.
