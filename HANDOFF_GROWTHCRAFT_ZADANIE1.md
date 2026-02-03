# Handoff: Zadanie 1 - GrowthCraft (Analiza bloków i Tile Entities)

## Podsumowanie sesji

Wykonano kompletną analizę moda **GrowthCraft 2.7.2 (complete)** dla Minecraft 1.7.10, obejmującą wszystkie moduły, bloki, tile entities oraz ich struktury NBT. Potwierdzono dostępność **GrowthCraft Community Edition 7.1.1** dla Minecraft 1.18.2, który zawiera wszystkie funkcjonalności w jednym JARze.

---

## 1. Informacje ogólne o GrowthCraft

### 1.1 GrowthCraft 1.7.10
- **Wersja**: 2.7.2 complete
- **Struktura**: Modularna (osobne JARy dla każdego modułu)
- **Lokalizacja źródeł**: `mod_src/1710/actual_src/1.7.10/Growthcraft/repo`

### 1.2 GrowthCraft 1.18.2
- **Wersja**: 7.1.1 (Community Edition)
- **Struktura**: Zintegrowana (wszystko w jednym JARze)
- **Dostępność**: ✅ Dostępny na CurseForge i GitHub
- **Link**: https://www.curseforge.com/minecraft/mc-mods/growthcraft-community-edition

---

## 2. Moduły GrowthCraft 1.7.10

| Moduł | Opis | Dostępność w 1.18.2 |
|-------|------|---------------------|
| **Core** | Rdzeń, bloki podstawowe, rope, paddy | ✅ |
| **Cellar** | Fermentacja, browarnictwo, alkohole | ✅ |
| **Apples** | Jabłka, drzewa, cydr | ✅ |
| **Bamboo** | Bambus, bloki budowlane | ✅ |
| **Bees** | Pszczoły, miód, ule | ✅ |
| **Fishtrap** | Pułapki na ryby | ✅ |
| **Grapes** | Winogrona, winorośle, wino | ✅ |
| **Hops** | Chmiel, ale, piwo | ✅ |
| **Milk** | Mleko, sery, masło, jogurt | ✅ |
| **Rice** | Ryż, sake, uprawy na wodzie | ✅ |

---

## 3. Szczegółowa lista bloków i Tile Entities

### 3.1 Moduł: Core (growthcraft/core)

#### Bloki (bez TE - dekoracyjne/technicze)
| Blok | Klasa | Opis |
|------|-------|------|
| `BlockFenceRope` | Fence z liną | Ogrodzenie do wsparcia pnączy |
| `BlockRope` | Lina | Wsparcie dla pnączy (hops, grapes) |
| `BlockPaddyBase` | Baza ryżu | Bazowy blok dla upraw ryżu |
| `BlockSaltBlock` | Blok soli | Dekoracyjny blok soli |

#### Tile Entities
**Brak własnych TE w module Core** - bazowe klasy dla innych modułów:
- `GrcTileBase` - Bazowa klasa TE
- `GrcTileDeviceBase` - TE z funkcjonalnością
- `GrcTileInventoryBase` - TE z inventory

---

### 3.2 Moduł: Cellar (growthcraft/cellar) - BROWARNICTWO

#### Bloki z Tile Entities

##### 1. Ferment Barrel (Beczka fermentacyjna)
```java
Klasa: growthcraft.cellar.common.block.BlockFermentBarrel
TE:    growthcraft.cellar.common.tileentity.TileEntityFermentBarrel
ID:    "grccellar:ferment_barrel"
```

**Funkcja**: Fermentacja płynów (np. sok → wino, brzeczka → piwo)

**Dane NBT**:
```java
// Z TileEntityFermentBarrel
- "time" (int) - Aktualny czas fermentacji
- "Tank" (NBTTagCompound) - Zawartość zbiornika płynu
- "lid_on" (boolean) - Czy pokrywa jest zamknięta
- "items" (NBTTagList) - Inventory (2 sloty)
  - Slot 0: Item fermentujący (np. drożdże)
```

**Pojemność**: Konfigurowalna (domyślnie 3000 mB)

**Automatyzacja**:
- Input płynu: dowolna strona
- Output płynu: dowolna strona
- Input itemów: slot 0

---

##### 2. Brew Kettle (Kocioł warzelny)
```java
Klasa: growthcraft.cellar.common.block.BlockBrewKettle
TE:    growthcraft.cellar.common.tileentity.TileEntityBrewKettle
ID:    "grccellar:brew_kettle"
```

**Funkcja**: Warzenie brzeczki (składniki + woda + ciepło → brzeczka)

**Dane NBT**:
```java
// Z TileEntityBrewKettle
- "brew_kettle" (NBTTagCompound):
  - "time" (float) - Czas warzenia
  - "time_max" (float) - Maksymalny czas
  - "grain" (float) - Poziom "grain" (stare wersje)
  - "heat_multiplier" (float) - Mnożnik ciepła
- Tanks: 2 zbiorniki (input i output)
- Inventory: 2 sloty (surowce i odpad)
```

**Ciepło**: Wymaga źródła ciepła (ogień, lava, inne mody)

---

##### 3. Fruit Press (Prasa do owoców)
```java
Klasa: growthcraft.cellar.common.block.BlockFruitPress
TE:    growthcraft.cellar.common.tileentity.TileEntityFruitPress
ID:    "grccellar:fruit_press"
```

**Funkcja**: Wyciskanie soku z owoców (jabłka, winogrona)

**Dane NBT**:
```java
// Z TileEntityFruitPress
- "fruit_press" (NBTTagCompound):
  - "time" (int) - Czas prasowania
  - "time_max" (int) - Maksymalny czas
- "Tank" (NBTTagCompound) - Zbiornik soku
- Inventory: 2 sloty (input i odpad)
```

**Automatyzacja**:
- Item input: slot 0 (dowolna strona)
- Item output: slot 1 (boki/dół)
- Fluid output: zbiornik (dowolna strona)

---

##### 4. Culture Jar (Słoik na kultury)
```java
Klasa: growthcraft.cellar.common.block.BlockCultureJar
TE:    growthcraft.cellar.common.tileentity.TileEntityCultureJar
ID:    "grccellar:culture_jar"
```

**Funkcja**: Hodowla drożdży i kultur bakteryjnych

**Dane NBT**:
```java
// Z TileEntityCultureJar
- "yeastgen" (NBTTagCompound):
  - "time" (int) - Czas generowania drożdży
  - "time_max" (int) - Maksymalny czas
- "culture_gen" (NBTTagCompound):
  - "time" (int) - Czas generowania kultury
  - "time_max" (int) - Maksymalny czas
- "heat_component" (NBTTagCompound):
  - "heat_multiplier" (float) - Mnożnik ciepła
- "Tank" - Zbiornik płynu
```

**Tryby pracy**:
- Z ciepłem: produkcja kultur
- Bez ciepła: produkcja drożdży

---

#### Bloki bez TE (płyny)

##### 5. BlockFluidBooze (Blok płynu alkoholowego)
```java
Klasa: growthcraft.cellar.common.block.BlockFluidBooze
```

**Płyny (FluidRegistry)**:
- `grccellar:fluid_booze` - Ogólny alkohol
- Różne typy przez metadata/NBT

---

### 3.3 Moduł: Milk (growthcraft/milk) - MLECZARSTWO

#### Bloki z Tile Entities

##### 1. Cheese Vat (Kadź do sera)
```java
Klasa: growthcraft.milk.common.block.BlockCheeseVat
TE:    growthcraft.milk.common.tileentity.TileEntityCheeseVat
ID:    "grcmilk:cheese_vat"
```

**Funkcja**: Produkcja serów (mleko + podpuszczka → ser)

**Dane NBT** (kompleksowe):
```java
// Z TileEntityCheeseVat
- "progress" (float) - Postęp produkcji
- "progress_max" (int) - Maksymalny postęp
- "vat_state" (String) - Stan: "idle", "preparing_curds", "preparing_cheese", "preparing_ricotta"
- "heat_component" (NBTTagCompound):
  - "heat_multiplier" (float)
- Tanks (4 zbiorniki):
  - Tank 0: "PRIMARY" - Mleko/zsiadłe mleko
  - Tank 1: "RENNET" - Podpuszczka
  - Tank 2: "WASTE" - Odpady (serwatka)
  - Tank 3: "RECIPE" - Składniki receptury
- Inventory: 3 sloty na składniki
```

**Proces**:
1. Dodaj mleko do PRIMARY
2. Dodaj podpuszczkę do RENNET
3. Użyj miecza aby rozpocząć
4. Ogrzewaj
5. Zbierz ser

---

##### 2. Pancheon (Pojemnik do mleka)
```java
Klasa: growthcraft.milk.common.block.BlockPancheon
TE:    growthcraft.milk.common.tileentity.TileEntityPancheon
ID:    "grcmilk:pancheon"
```

**Funkcja**: Separacja mleka (mleko → śmietanka + maślanka)

**Dane NBT**:
```java
// Z TileEntityPancheon (przez device Pancheon)
- 3 zbiorniki po 1000 mB każdy:
  - Tank 0: Input (mleko)
  - Tank 1: Bottom output (maślanka)
  - Tank 2: Top output (śmietanka)
```

**Uwaga**: Całkowita pojemność to 1000 mB (dzielona między zbiorniki)

---

##### 3. Churn (Ubiaczka do masła)
```java
Klasa: growthcraft.milk.common.block.BlockButterChurn
TE:    growthcraft.milk.common.tileentity.TileEntityButterChurn
ID:    "grcmilk:butter_churn"
```

**Funkcja**: Produkcja masła (śmietanka → masło)

**Dane NBT**:
```java
// Z TileEntityButterChurn
- Postęp (time/time_max)
- Inventory na składniki
```

---

##### 4. Cheese Press (Prasa do sera)
```java
Klasa: growthcraft.milk.common.block.BlockCheesePress
TE:    growthcraft.milk.common.tileentity.TileEntityCheesePress
ID:    "grcmilk:cheese_press"
```

**Funkcja**: Prasowanie sera (zsiadłe mleko → blok sera)

---

##### 5. Hanging Curds (Zawieszone zsiadłe mleko)
```java
Klasa: growthcraft.milk.common.block.BlockHangingCurds
TE:    growthcraft.milk.common.tileentity.TileEntityHangingCurds
ID:    "grcmilk:hanging_curds"
```

**Funkcja**: Sączenie zsiadłego mleka

---

### 3.4 Moduł: Bees (growthcraft/bees) - PSZCZELARSTWO

#### Bloki z Tile Entities

##### 1. Bee Box (Ul)
```java
Klasa: growthcraft.bees.common.block.BlockBeeBox
TE:    growthcraft.bees.common.tileentity.TileEntityBeeBox
ID:    "grcbees:bee_box"
```

**Warianty**: Różne drewna (Oak, Spruce, Birch, Jungle, Acacia, Dark Oak, Bamboo, Forestry, Natura, BiomesOPlenty, Thaumcraft, Botania, Nether)

**Funkcja**: Hodowla pszczół, produkcja miodu i plastrów

**Dane NBT** (bardzo ważne):
```java
// Z TileEntityBeeBox
- "bee_box" (NBTTagCompound):
  - "bonus_time" (int) - Czas bonusu (po użyciu barwnika)
  - "bee_count" (int) - Liczba pszczół (niekiedy)
- Inventory: 28 slotów!
  - Slot 0: Pszczoły (ItemBee)
  - Slot 1-27: Plastry miodu (puste i pełne)
- "BeeBox.version" (int) - Wersja danych (3)
```

**Mechanika**:
- Wymaga pszczół w slocie 0
- Produkują puste plastry → pełne plastry
- Sąsiedztwo kwiatów zwiększa produkcję
- Można przyspieszyć barwnikami (różowy/magenta)

---

##### 2. Bee Hive (Dziki rój)
```java
Klasa: growthcraft.bees.common.block.BlockBeeHive
ID:    "grcbees:bee_hive"
```

**Funkcja**: Dziki rój pszczół w świecie (nie ma TE - generuje pszczoły)

---

### 3.5 Moduł: Fishtrap (growthcraft/fishtrap)

#### Blok z Tile Entity

##### 1. Fish Trap (Pułapka na ryby)
```java
Klasa: growthcraft.fishtrap.common.block.BlockFishTrap
TE:    growthcraft.fishtrap.common.tileentity.TileEntityFishTrap
ID:    "grcfishtrap:fish_trap"
```

**Funkcja**: Automatyczne łowienie ryb

**Dane NBT**:
```java
// Z TileEntityFishTrap
- Inventory: 7 slotów
  - Slot 0-5: Łupy (ryby, śmieci)
  - Slot 6: Przynęta
- "items" (NBTTagList) - Kompatybilność wsteczna
```

**Mechanika**:
- Umieść w wodzie
- Dodaj przynętę w slocie 6 (opcjonalnie)
- Automatycznie generuje łupy

---

### 3.6 Moduł: Grapes (growthcraft/grapes)

#### Bloki bez TE (uprawy)

| Blok | Opis |
|------|------|
| `BlockGrapeVine0` | Młoda winorośl |
| `BlockGrapeVine1` | Dorosła winorośl |
| `BlockGrapeLeaves` | Liście winorośli |
| `BlockGrapeBlock` | Blok winogron (owoc) |

**NBT dla upraw**: Standardowe NBT dla roślin (metadata = wiek/rozkwit)

---

### 3.7 Moduł: Hops (growthcraft/hops)

#### Bloki bez TE (uprawy)

| Blok | Opis |
|------|------|
| `BlockHops` | Chmiel (pnącze) |

Wymaga lin/rope do wzrostu w górę.

---

### 3.8 Moduł: Apples (growthcraft/apples)

#### Bloki bez TE (uprawy)

| Blok | Opis |
|------|------|
| `BlockApple` | Jabłko na drzewie |
| `BlockAppleLeaves` | Liście jabłoni |
| `BlockAppleSapling` | Sadzonka jabłoni |

---

### 3.9 Moduł: Bamboo (growthcraft/bamboo)

#### Bloki

| Blok | TE | Opis |
|------|-----|------|
| `BlockBamboo` | ❌ | Blok bambusa |
| `BlockBambooStalk` | ❌ | Łodyga bambusa |
| `BlockBambooShoot` | ❌ | Młody bambus |
| `BlockBambooLeaves` | ❌ | Liście |
| `BlockBambooFence` | ❌ | Płot |
| `BlockBambooFenceGate` | ❌ | Furtka |
| `BlockBambooDoor` | ❌ | Drzwi |
| `BlockBambooSlab` | ❌ | Płyta |
| `BlockBambooStairs` | ❌ | Schody |
| `BlockBambooWall` | ❌ | Ściana |
| `BlockBambooScaffold` | ❌ | Rusztowanie |

---

### 3.10 Moduł: Rice (growthcraft/rice)

#### Bloki

| Blok | TE | Opis |
|------|-----|------|
| `BlockRice` | ❌ | Roślina ryżu |
| `BlockPaddy` | ❌ | Pole ryżowe (wymaga wody) |

---

## 4. Podsumowanie Tile Entities

| Moduł | Tile Entity | Kluczowe NBT | Złożoność konwersji |
|-------|-------------|--------------|---------------------|
| Cellar | TileEntityFermentBarrel | time, Tank, lid_on | Średnia (fluid + item) |
| Cellar | TileEntityBrewKettle | brew_kettle, 2 tanks | Wysoka (ciepło, 2 płyny) |
| Cellar | TileEntityFruitPress | fruit_press, Tank | Średnia |
| Cellar | TileEntityCultureJar | yeastgen, culture_gen | Wysoka (2 tryby pracy) |
| Milk | TileEntityCheeseVat | vat_state, 4 tanks, progress | Bardzo wysoka |
| Milk | TileEntityPancheon | 3 tanks (stack) | Średnia |
| Milk | TileEntityButterChurn | progress | Niska |
| Milk | TileEntityCheesePress | progress | Niska |
| Milk | TileEntityHangingCurds | curd_type, progress | Średnia |
| Bees | TileEntityBeeBox | bee_box, 28 slots | Wysoka (duży inventory) |
| Fishtrap | TileEntityFishTrap | 7 slots | Niska |

---

## 5. Kluczowe wyzwania konwersji

### 5.1 Zmiany między wersjami

#### Zmiana systemu ID
- **1.7.10**: Numeryczne ID z metadata (np. `Block.getIdFromBlock()`)
- **1.18.2**: String ID (`ResourceLocation`)

#### Zmiana systemu płynów
- **1.7.10**: `FluidRegistry` z własnymi nazwami
- **1.18.2**: Nowy system tagów i rejestracji

#### Zmiana NBT
- **1.7.10**: `NBTTagCompound`, `NBTTagList`
- **1.18.2**: `CompoundTag`, `ListTag` (podobne API)

### 5.2 Mapowanie nazw

| 1.7.10 Block ID | 1.18.2 Block ID (szacowane) |
|-----------------|------------------------------|
| `grccellar:ferment_barrel` | `growthcraft:ferment_barrel` |
| `grccellar:brew_kettle` | `growthcraft:brew_kettle` |
| `grccellar:fruit_press` | `growthcraft:fruit_press` |
| `grccellar:culture_jar` | `growthcraft:culture_jar` |
| `grcmilk:cheese_vat` | `growthcraft:cheese_vat` |
| `grcmilk:pancheon` | `growthcraft:pancheon` |
| `grcmilk:butter_churn` | `growthcraft:butter_churn` |
| `grcbees:bee_box` | `growthcraft:bee_box` |
| `grcfishtrap:fish_trap` | `growthcraft:fish_trap` |

---

## 6. Utworzone pliki

- `HANDOFF_GROWTHCRAFT_ZADANIE1.md` - Ten dokument

---

## 7. Następne kroki (Zadanie 2)

1. **Przygotować symulacje funkcjonalności** w Pythonie dla:
   - Procesu fermentacji (FermentBarrel)
   - Procesu warzenia (BrewKettle)
   - Produkcji miodu (BeeBox)
   - Produkcji sera (CheeseVat)

2. **Zbadać kod GrowthCraft 1.18.2** (jeśli dostępny lokalnie) lub pobrać z GitHub

3. **Porównać struktury NBT** między wersjami

---

*Dokument utworzony: 2026-02-03*
*Źródła: Kod źródłowy GrowthCraft 1.7.10, dokumentacja internetowa GrowthCraft CE 7.1.1*
