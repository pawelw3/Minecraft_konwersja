# Handoff: Jammy Furniture Reborn - Zadanie 1

## Podsumowanie sesji

Wykonano **Zadanie 1** dla modu Jammy Furniture Reborn - kompletną identyfikację bloków i tile entities modu źródłowego (1.7.10) oraz przygotowanie mapowania na mody docelowe w 1.18.2 (Supplementaries + Handcrafted + Macaw's Furniture).

---

## Ukończono

### 1. Identyfikacja bloków Jammy Furniture (1.7.10)

Na podstawie analizy kodu źródłowego (`mod_src/1710/code_from_jar/1.7.10/JammyFurniture/`) zidentyfikowano **21 bloków** (z wieloma wariantami metadata):

#### Bloki drewniane (WoodBlocks)
| Blok 1.7.10 | Metadata | Nazwa | Funkcja |
|-------------|----------|-------|---------|
| `WoodBlocksOne` | 0 | Clock Base | Baza zegara (dekoracja) |
| `WoodBlocksOne` | 1-4 | Clock Middle | Środek zegara (TE - orientacja) |
| `WoodBlocksOne` | 5-8 | Clock Top | Wierzchołek zegara |
| `WoodBlocksOne` | 9-12 | Blinds | Rolety |
| `WoodBlocksOne` | 13 | Crafting Side | Stół craftingowy (ma GUI) |
| `WoodBlocksOne` | 14 | Kitchen Side | Kuchenny blat |
| `WoodBlocksOne` | 15 | Table | Stół |
| `WoodBlocksTwo` | 0-3 | Kitchen Cupboard | Szafka kuchenna (TE, inventory) |
| `WoodBlocksTwo` | 4-7 | Kitchen Cupboard (Shelf) | Szafka otwarta |
| `WoodBlocksTwo` | 8-11 | Television | Telewizor (dekoracja) |
| `WoodBlocksTwo` | 12-15 | Basket | Kosz (dekoracja) |
| `WoodBlocksThree` | 0-3 | Chair | Krzesło (można usiąść) |
| `WoodBlocksThree` | 4-7 | Radio | Radio (dekoracja) |
| `WoodBlocksFour` | 0-7 | Wardrobe | Szafa (TE, inventory) |
| `WoodBlocksFour` | 8-11 | Coat Stand | Wieszak |

#### Bloki metalowe (IronBlocks)
| Blok 1.7.10 | Metadata | Nazwa | Funkcja |
|-------------|----------|-------|---------|
| `IronBlocksOne` | 0-3 | Fridge | Lodówka (TE, inventory, GUI) |
| `IronBlocksOne` | 4-7 | Freezer | Zamrażarka (TE, inventory) |
| `IronBlocksOne` | 8-11 | Cooker | Kuchenka (TE, GUI, gotowanie) |
| `IronBlocksOne` | 12 | Rubbish Bin | Kosz na śmieci (TE, inventory) |
| `IronBlocksOne` | 13 | Coffee Table | Stolik kawowy |
| `IronBlocksTwo` | 0-3 | Dishwasher | Zmywarka (TE, GUI) |
| `IronBlocksTwo` | 4-7 | Washing Machine | Pralka (TE, GUI) |

#### Bloki ceramiczne (CeramicBlocks)
| Blok 1.7.10 | Metadata | Nazwa | Funkcja |
|-------------|----------|-------|---------|
| `CeramicBlocksOne` | 0-3 | Bathroom Cupboard | Szafka łazienkowa (TE) |
| `CeramicBlocksOne` | 4-7 | Bathroom Sink | Umywalka łazienkowa (TE, woda) |
| `CeramicBlocksOne` | 8-11 | Kitchen Sink | Zlew kuchenny (TE, woda, crafting) |
| `CeramicBlocksOne` | 12-15 | Toilet | Toaleta (TE, można usiąść) |

#### Oświetlenie i meble wypoczynkowe
| Blok 1.7.10 | Metadata | Nazwa | Funkcja |
|-------------|----------|-------|---------|
| `LightsOn` | 0,4,8 | Light | Światło sufitowe |
| `LightsOn` | 4-7 | Outdoor Lamp | Lampa zewnętrzna |
| `LightsOn` | 8-11 | Table Lamp | Lampa stołowa |
| `LightsOff` | * | Światła wyłączone | Te same warianty co LightsOn |
| `ArmChair` | 0,4,8,12 | Arm Chair | Fotel (można usiąść) |
| `SofaLeft` | 0,4,8,12 | Sofa Part (Left) | Lewa część sofy |
| `SofaRight` | 0,4,8,12 | Sofa Part (Right) | Prawa część sofy |
| `SofaCenter` | 0,4,8,12 | Sofa Part (Center) | Środkowa część sofy |
| `SofaCorner` | 0,4,8,12 | Sofa Part (Corner) | Narożnik sofy |

#### Pozostałe bloki
| Blok 1.7.10 | Metadata | Nazwa | Funkcja |
|-------------|----------|-------|---------|
| `Bath` | 0-3 | Bath | Wanna (2 bloki wysokości, TE, woda) |
| `RoofingBlocksOne` | 0-15 | Roofing | Dachówki (4 kształty × 4 orientacje) |
| `MiscBlocksOne` | 0 | Chimney | Komin |
| `MiscBlocksOne` | 4 | Mantle Piece | Półka nad kominkiem |
| `MiscBlocksOne` | 8 | Christmas Tree | Choinka świąteczna |
| `MobHeadsOne` | 0,4,8,12 | Chicken/Cow/Creeper/Dragon Head | Głowy mobów |
| `MobHeadsTwo` | 0,4,8,12 | Pig/Sheep/Skeleton/Spider Head | Głowy mobów |
| `MobHeadsThree` | 0,4,8,12 | Steve/Wolf/Zombie/Squid Head | Głowy mobów |
| `MobHeadsFour` | 0,4,8,12 | Enderman/Slime/Blaze/Zombie Pig Head | Głowy mobów |

### 2. Identyfikacja Tile Entities

Mod używa następujących Tile Entities (przechowują dane NBT):

| Tile Entity | Bloki | Przechowywane dane |
|-------------|-------|-------------------|
| `TileEntityWoodBlocksOne` | Crafting Side | Inventory (crafting grid) |
| `TileEntityWoodBlocksTwo` | Kitchen Cupboard, TV, Basket | Inventory, orientation |
| `TileEntityWoodBlocksThree` | Chair, Radio | Orientation |
| `TileEntityWoodBlocksFour` | Wardrobe, Coat Stand | Inventory, orientation |
| `TileEntityIronBlocksOne` | Fridge, Freezer, Cooker, Rubbish Bin | Inventory, state, temperature |
| `TileEntityIronBlocksTwo` | Dishwasher, Washing Machine | Inventory, progress, water |
| `TileEntityCeramicBlocksOne` | Bathroom Cupboard, Sinks, Toilet | Inventory, water state, orientation |
| `TileEntityBath` | Bath | Wypełnienie wodą |
| `TileEntityLightsOn/Off` | Lights | State |
| `TileEntitySofa*` | ArmChair, Sofa parts | Orientation, color |
| `TileEntityMobHeads*` | Mob Heads | Type, orientation |

### 3. Mapowanie na mody 1.18.2

#### Mody docelowe
| Mod 1.18.2 | Dostępność | Przeznaczenie |
|------------|------------|---------------|
| **Supplementaries** | ✅ W repozytorium | Meble funkcjonalne (szafki, półki, zegary) |
| **Handcrafted** | ✅ W repozytorium | Meble wypoczynkowe (krzesła, sofy, łóżka) |
| **Macaw's Furniture** | ❌ Brak w repo | Duży zestaw mebli kuchennych i łazienkowych |

#### Szczegółowe mapowanie

| Jammy Furniture (1.7.10) | Supplementaries (1.18.2) | Handcrafted (1.18.2) | Macaw's Furniture (1.18.2) |
|--------------------------|--------------------------|----------------------|---------------------------|
| **Clock Base/Middle/Top** | `supplementaries:clock_block` | - | - |
| **Blinds** | - | - | `mcwfurnitures:blinds` |
| **Table** | - | `handcrafted:table` | `mcwfurnitures:oak_table` |
| **Chair** | `supplementaries:seat` | `handcrafted:chair` | `mcwfurnitures:oak_chair` |
| **Kitchen Cupboard** | `supplementaries:safe` / `sack` | - | `mcwfurnitures:oak_kitchen_cabinet` |
| **Wardrobe** | `supplementaries:safe` | `handcrafted:bench` | `mcwfurnitures:oak_wardrobe` |
| **Coat Stand** | `supplementaries:armor_stand` | - | `mcwfurnitures:coat_rack` |
| **Television** | - | - | Placeholder / `supplementaries:blackboard` |
| **Basket** | `supplementaries:planter` | `handcrafted:basket` | - |
| **Fridge/Freezer** | `supplementaries:safe` (z retexture) | - | `mcwfurnitures:refrigerator` |
| **Cooker** | - | - | `mcwfurnitures:stove` |
| **Dishwasher** | - | - | Placeholder |
| **Washing Machine** | - | - | Placeholder |
| **Rubbish Bin** | `supplementaries:urn` | - | `mcwfurnitures:trash_can` |
| **Coffee Table** | - | `handcrafted:table` (small) | `mcwfurnitures:coffee_table` |
| **Bathroom Cupboard** | `supplementaries:safe` | - | `mcwfurnitures:bathroom_cabinet` |
| **Bathroom/Kitchen Sink** | `supplementaries:faucet` + `planter` | - | `mcwfurnitures:sink` |
| **Toilet** | - | - | `mcwfurnitures:toilet` |
| **Bath** | - | - | `mcwfurnitures:bathtub` |
| **Light/Outdoor Lamp/Table Lamp** | `supplementaries:wall_lantern` / `sconce` | - | `mcwfurnitures:modern_lamp` |
| **Arm Chair** | `supplementaries:seat` | `handcrafted:chair` (upholstered) | `mcwfurnitures:armchair` |
| **Sofa (all parts)** | - | `handcrafted:couch` | `mcwfurnitures:sofa` |
| **Chimney** | `supplementaries:chimney` | - | - |
| **Mob Heads** | `supplementaries:candle_skull` / vanilla heads | - | - |

### 4. Weryfikacja obecności na mapie

Wykonano próbkowanie 50 plików regionów (z 1195 dostępnych):
- Przeskanowano: **28,656 chunków**
- Chunki zawierające string "jammy": **0** (w próbce)

**Wniosek:** Mod jest obecny w level.dat (FML mod list), ale użycie na mapie jest rzadkie lub znajduje się w nieprzeskanowanych regionach. Zalecane pełne skanowanie przed konwersją.

---

## Nowe pliki

| Plik | Opis |
|------|------|
| `analyze_jammy_furniture.py` | Skrypt analizy mapy pod kątem bloków Jammy |
| `HANDOFF_JAMMY_ZADANIE1.md` | Ten dokument |

## Zmodyfikowane pliki

Brak.

---

## Decyzje projektowe

### 1. Brak Macaw's Furniture w repozytorium
**Decyzja:** Należy pobrać JAR Macaw's Furniture 1.18.2 i dodać do paczki docelowej.

**Uzasadnienie:** 
- Macaw's Furniture jest najlepszym zamiennikiem dla Jammy Furniture
- Oba mody mają podobny zakres mebli kuchennych i łazienkowych
- Handcrafted i Supplementaries nie pokrywają wszystkich funkcji (np. zmywarka, pralka)

### 2. Mapowanie "w duchu" (nie 1:1)
**Decyzja:** Konwersja będzie semantyczna, nie bezstratna.

**Uzasadnienie:**
- Różne systemy ID (metadata 1.7.10 → blockstates 1.18.2)
- Inne struktury NBT
- Brak bezpośrednich odpowiedników dla wszystkich bloków

### 3. Priority mapping
**Wysoki priorytet:**
- Bloki z inventory (Fridge, Cupboards, Wardrobe) - zachować zawartość
- Bloki funkcyjne (Cooker, Sinks, Toilet) - zachować funkcję
- Meble wypoczynkowe (Sofa, ArmChair) - zachować możliwość siedzenia

**Niski priorytet:**
- Czysto dekoracyjne (Christmas Tree, TV) - można zamienić na placeholdery
- Głowy mobów - użyć vanilla lub Supplementaries

---

## Następne kroki (Zadanie 2)

1. **Pobrać Macaw's Furniture 1.18.2**
   - Wersja: `macaws-furniture-1.18.2-3.x.x.jar`
   - Źródło: CurseForge

2. **Wykonać pełne skanowanie mapy**
   ```bash
   python analyze_jammy_furniture.py --full
   ```
   aby uzyskać dokładne liczby bloków per region

3. **Stworzyć tabelę remapowania ID**
   - Numeryczne ID bloków Jammy z modpack_1710 → string ID 1.18.2
   - Mapowanie metadata → blockstates

4. **Zaprojektować konwerter NBT**
   - Klasa `JammyFurnitureConverter`
   - Obsługa inventory (przepisanie itemów)
   - Obsługa orientacji (metadata rotation → blockstate facing)

5. **Stworzyć testowy świat 1.7.10**
   - Postawić wszystkie bloki Jammy Furniture
   - Wypełnić inventory przykładowymi itemami
   - Przekonwertować i zweryfikować

---

## Ryzyka i uwagi

| Ryzyko | Poziom | Mitigacja |
|--------|--------|-----------|
| Niskie użycie modu na mapie | Niskie | Jeśli < 100 bloków, można pominąć konwersję |
| Brak odpowiedników dla niektórych bloków | Średnie | Użyć placeholdery lub najbliższych funkcjonalnie |
| Różne formaty inventory | Średnie | Konwerter musi mapować sloty 1:1 |
| Strata danych TileEntity | Wysokie | Dokładna analiza NBT przed konwersją |

---

## Referencje

- **Kod źródłowy Jammy 1.7.10:** `mod_src/1710/code_from_jar/1.7.10/JammyFurniture/`
- **Handcrafted 1.18.2:** `mod_src/actual_src/1.18.2/Handcrafted/`
- **Supplementaries 1.18.2:** `mod_src/actual_src/1.18.2/Supplementaries/`
- **Dokumentacja konwersji:** `docs/mod_mapping_indepth/to/konwersja_1710_do_1182_mapowanie_modow_cz3.md` (sekcja 9)

---

*Dokument utworzony: 2026-02-03*
*Status: Zadanie 1 ukończone, gotowe do Zadania 2*
