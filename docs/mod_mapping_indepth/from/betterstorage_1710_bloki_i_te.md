# Better Storage 1.7.10 - Szczegółowa lista bloków i Tile Entities (POPRAWIONA)

> **Mod ID:** `betterstorage`  
> **Wersja:** 1.7.10 (Better-Storage-Mod-1.7.10.jar)  
> **Data analizy:** 2026-02-03  
> **Poprawki:** ContainerMaterial = kosmetyka, Crate = osobne pliki, Pojemność zależy od configu

---

## ⚠️ WAŻNE POPRAWKI PO WERYFIKACJI KODU

### ContainerMaterial jest CZYSTO KOSMETYCZNY
**Dowód:** `ContainerMaterial.java:82-87` - używany TYLKO do:
- `getChestResource()` - tekstury skrzyń
- `getLockerResource()` - tekstur szafek

NIE wpływa na pojemność, odporność na wybuchy ani logikę!

### Pojemność skrzyń zależy od CONFIGU
**Dowód:** `GlobalConfig.java:136`
```java
new IntegerSetting(this, reinforcedColumns, 13).setValidValues(9, 11, 13)
```
- Wszystkie Reinforced Chests/Lockers mają 3 wiersze (stałe `getRows() = 3`)
- Pojemność: 27, 33 lub 39 slotów (9×3, 11×3, 13×3)
- **NIE zależy od materiału!**

### Crate Pile - zawartość w OSOBNYCH PLIKACH
**Dowód:** `CratePileCollection.java:73-88`
```java
// Zapis do <world>/data/crates/<id>.dat
File file = new File(getSaveDirectory(), id + ".dat");
```
- TileEntityCrate przechowuje tylko `crateId`
- Właściwa zawartość w osobnych plikach NBT!

---

## Struktura kodu źródłowego

```
net.mcft.copy.betterstorage/
├── content/
│   ├── BetterStorageTiles.java          # Rejestracja bloków
│   ├── BetterStorageItems.java          # Rejestracja itemów
│   ├── BetterStorageTileEntities.java   # Rejestracja TE
│   └── BetterStorageEntities.java       # Rejestracja encji
├── tile/
│   ├── ContainerMaterial.java           # MATERIAŁY - tylko kosmetyka!
│   ├── TileLockable.java                # Bazowa klasa bloków z zamkami
│   ├── TileContainerBetterStorage.java  # Bazowa klasa kontenerów
│   ├── TileBackpack.java
│   ├── TileCardboardBox.java
│   ├── TileCraftingStation.java
│   ├── TileEnderBackpack.java
│   ├── TileFlintBlock.java
│   ├── TileLocker.java
│   ├── TileLockableDoor.java
│   ├── TilePresent.java
│   ├── TileReinforcedChest.java
│   └── TileReinforcedLocker.java
├── tile/entity/
│   ├── TileEntityBackpack.java
│   ├── TileEntityCardboardBox.java
│   ├── TileEntityContainer.java         # Bazowa klasa TE kontenerów
│   ├── TileEntityCraftingStation.java
│   ├── TileEntityLockable.java          # Bazowa klasa TE z zamkami
│   ├── TileEntityLockableDoor.java
│   ├── TileEntityLocker.java
│   ├── TileEntityPresent.java
│   ├── TileEntityReinforcedChest.java
│   └── TileEntityReinforcedLocker.java
├── tile/crate/
│   ├── TileCrate.java
│   ├── TileEntityCrate.java
│   └── CratePileCollection.java         # ZAPIS CRATE PILE!
├── tile/stand/
│   └── TileEntityArmorStand.java
├── item/
│   ├── ItemBackpack.java
│   ├── ItemCardboard*.java              # Armor, tools, sheet
│   ├── ItemDrinkingHelmet.java
│   ├── ItemEnderBackpack.java           # Używa vanilla ender chest!
│   ├── ItemBucketSlime.java
│   ├── ItemPresentBook.java
│   └── locking/
│       ├── ItemKey.java
│       ├── ItemLock.java
│       ├── ItemKeyring.java
│       └── ItemMasterKey.java
└── config/
    └── GlobalConfig.java                # POJEMNOŚCI SKRZYŃ
```

---

## Bloki (Tiles)

### Lista wszystkich bloków

| Nazwa zmiennej | Klasa | Registry name | TileEntity | Pojemność |
|----------------|-------|---------------|------------|-----------|
| `crate` | `TileCrate` | `betterstorage:crate` | `TileEntityCrate` | 18 (ale wspólne w pile!) |
| `reinforcedChest` | `TileReinforcedChest` | `betterstorage:reinforcedChest` | `TileEntityReinforcedChest` | 27/33/39 (config) |
| `locker` | `TileLocker` | `betterstorage:locker` | `TileEntityLocker` | 36 (12×3) |
| `armorStand` | `TileArmorStand` | `betterstorage:armorStand` | `TileEntityArmorStand` | 4 (zbroja) |
| `backpack` | `TileBackpack` | `betterstorage:backpack` | `TileEntityBackpack` | 27 (config) |
| `enderBackpack` | `TileEnderBackpack` | `betterstorage:enderBackpack` | `TileEntityEnderBackpack` | Vanilla ender chest |
| `cardboardBox` | `TileCardboardBox` | `betterstorage:cardboardBox` | `TileEntityCardboardBox` | 9 (config) |
| `reinforcedLocker` | `TileReinforcedLocker` | `betterstorage:reinforcedLocker` | `TileEntityReinforcedLocker` | 36 |
| `craftingStation` | `TileCraftingStation` | `betterstorage:craftingStation` | `TileEntityCraftingStation` | 9+1 |
| `flintBlock` | `TileFlintBlock` | `betterstorage:flintBlock` | `TileEntityFlintBlock` | - |
| `lockableDoor` | `TileLockableDoor` | `betterstorage:lockableDoor` | `TileEntityLockableDoor` | - |
| `present` | `TilePresent` | `betterstorage:present` | `TileEntityPresent` | 9 |

---

## Tile Entities - Szczegóły

### 1. TileEntityCrate

**Klasa:** `net.mcft.copy.betterstorage.tile.crate.TileEntityCrate`

**Funkcjonalność:**
- Pojedyncza skrzynia: 18 slotów
- Łączy się w stosy (Crate Pile) - wspólne inventory
- Dane przechowywane w OSOBNYM PLIKU!

**NBT w TileEntity (chunk):**
```java
- crateId: int (ID stosu, -1 = nowy/nieprzypisany)
```

**Dane w pliku (`<world>/data/crates/<id>.dat`):**
```java
- items: NBTTagList (wspólna zawartość całego stosu)
- numCrates: int (liczba skrzyń w stosie)
- region: CratePileRegion (obszar stosu)
```

**Konwersja:**
- ❌ NIE na Storage Drawers (inna mechanika)
- ✅ Vanilla Chest / Iron Chests
- Każdy crate → osobna skrzynia
- Zawartość z pliku crate rozdzielona

---

### 2. TileEntityReinforcedChest

**Klasa:** `net.mcft.copy.betterstorage.tile.entity.TileEntityReinforcedChest`

**Funkcjonalność:**
- Wzmocniona skrzynia z materiałem (TYLKO tekstura!)
- Pojemność: 27, 33 lub 39 slotów (zależy od configu `reinforcedColumns`)
- Łączy się w podwójne skrzynie (poziomo)
- Obsługa zamków

**NBT:**
```java
- Items: NBTTagList (zawartość)
- Lock: NBTTagCompound (ItemStack zamka, opcjonalny)
- Material: String ("iron", "gold", "diamond", "emerald", "copper", "tin", "silver", "zinc", "steel")
- orientation: byte (0-5, ForgeDirection)
- CustomName: String (opcjonalne, nazwa z anvil)
```

**Uwaga o materiale:**
- Material jest TYLKO kosmetyczny (tekstury)
- NIE wpływa na pojemność ani wytrzymałość
- Receptury craftingu używają materiału, ale to tylko sposób wytworzenia

---

### 3. TileEntityLocker

**Klasa:** `net.mcft.copy.betterstorage.tile.entity.TileEntityLocker`

**Funkcjonalność:**
- Szafka (pionowa) - 36 slotów
- Łączy się pionowo (2 szafki = podwójna wysokość)
- Drzwi otwierają się w różne strony (`mirror`)

**NBT:**
```java
- Items: NBTTagList (zawartość)
- Lock: NBTTagCompound (opcjonalny)
- orientation: byte
- mirror: boolean (true = drzwi otwierają się w lewo)
- CustomName: String (opcjonalne)
```

---

### 4. TileEntityReinforcedLocker

**Klasa:** `net.mcft.copy.betterstorage.tile.entity.TileEntityReinforcedLocker`

**Funkcjonalność:**
- Wzmocniona szafka z materiałem (kosmetyka!)
- 36 slotów
- Łączy się pionowo

**NBT:**
```java
- Items: NBTTagList
- Lock: NBTTagCompound (opcjonalny)
- Material: String (materiały jak w ReinforcedChest)
- orientation: byte
- mirror: boolean
```

---

### 5. TileEntityCardboardBox

**Klasa:** `net.mcft.copy.betterstorage.tile.entity.TileEntityCardboardBox`

**Funkcjonalność:**
- Przenośne pudełko (można zabrać z zawartością)
- Zużywa się przy każdym przeniesieniu (`uses`)
- Można farbować (`color`)
- Pojemność: 9 slotów (config `cardboardBoxRows`)

**NBT:**
```java
- Items: NBTTagList (9 slotów)
- uses: int (liczba pozostałych użyć, -1 = nieskończoność)
- color: int (kolor RGB farbowania, -1 = brak)
- CustomName: String (opcjonalne)
```

**Mechanika zużywania:**
- Pudełko puste → można zabrać bez zużycia
- Pudełko pełne → zużycie +1
- Po osiągnięciu uses=0 → pudełko się niszczy, zawartość wypada

---

### 6. TileEntityCraftingStation

**Klasa:** `net.mcft.copy.betterstorage.tile.entity.TileEntityCraftingStation`

**Funkcjonalność:**
- Stół rzemieślniczy z trwałym inventory
- 9 slotów crafting + 1 slot wyniku
- Zachowuje zawartość po zamknięciu GUI
- Dostęp do sąsiednich inventory (z tyłu bloku)

**NBT:**
```java
- Items: NBTTagList (10 slotów: 0-8 crafting, 9 wynik)
```

---

### 7. TileEntityArmorStand

**Klasa:** `net.mcft.copy.betterstorage.tile.stand.TileEntityArmorStand`

**Funkcjonalność:**
- Stojak na zbroję
- 4 sloty: hełm, napierśnik, nogawice, buty
- Wyświetla zbroję na modelu 3D
- MA GUI (w przeciwieństwie do vanilla!)

**NBT:**
```java
- Items: NBTTagList (4 sloty)
```

---

### 8. TileEntityBackpack

**Klasa:** `net.mcft.copy.betterstorage.tile.entity.TileEntityBackpack`

**Funkcjonalność:**
- Plecak postawiony jako blok
- 27 slotów inventory (config `backpackRows`)
- Można farbować

**NBT:**
```java
- Items: NBTTagList (27 slotów)
- color: int (kolor)
```

---

### 9. TileEntityEnderBackpack

**Klasa:** `net.mcft.copy.betterstorage.tile.entity.TileEntityEnderBackpack`

**Funkcjonalność:**
- Plecak ender
- Używa VANILLA ender chest inventory (`player.getInventoryEnderChest()`)

**NBT:**
```java
// Brak własnych danych - używa vanilla ender chest
```

**Uwaga:** To tylko "dostęp" do vanilla ender chest, nie osobny storage!

---

### 10. TileEntityPresent

**Klasa:** `net.mcft.copy.betterstorage.tile.entity.TileEntityPresent`

**Funkcjonalność:**
- Ozdobna skrzynia (prezent)
- 9 slotów
- Można farbować (kolor papieru)

**NBT:**
```java
- Items: NBTTagList
- color: int (kolor papieru)
```

---

### 11. TileEntityLockableDoor

**Klasa:** `net.mcft.copy.betterstorage.tile.entity.TileEntityLockableDoor`

**Funkcjonalność:**
- Drzwi z zamkiem

**NBT:**
```java
- Lock: NBTTagCompound (ItemStack zamka)
```

---

### 12. TileEntityFlintBlock

**Klasa:** `net.mcft.copy.betterstorage.tile.entity.TileEntityFlintBlock`

**Funkcjonalność:**
- Blok krzemienia (dekoracyjny)

**NBT:**
```java
// Brak danych
```

---

## ContainerMaterial (KOSMETYCZNY!)

**Plik:** `net.mcft.copy.betterstorage.tile.ContainerMaterial`

**Definicja materiałów:**
```java
public static ContainerMaterial iron    = new ContainerMaterial(0, "iron",    Items.iron_ingot, Blocks.iron_block);
public static ContainerMaterial gold    = new ContainerMaterial(1, "gold",    Items.gold_ingot, Blocks.gold_block);
public static ContainerMaterial diamond = new ContainerMaterial(2, "diamond", Items.diamond,    Blocks.diamond_block);
public static ContainerMaterial emerald = new ContainerMaterial(3, "emerald", Items.emerald,    Blocks.emerald_block);
public static ContainerMaterial copper  = new ContainerMaterial(5, "copper",  "ingotCopper",    "blockCopper");
public static ContainerMaterial tin     = new ContainerMaterial(6, "tin",     "ingotTin",       "blockTin");
public static ContainerMaterial silver  = new ContainerMaterial(7, "silver",  "ingotSilver",    "blockSilver");
public static ContainerMaterial zinc    = new ContainerMaterial(8, "zinc",    "ingotZinc",      "blockZinc");
public static ContainerMaterial steel   = new ContainerMaterial(   "steel",   "ingotSteel",     "blockSteel");
```

**Zastosowanie (TYLKO kosmetyka!):**
- `getChestResource()` - tekstury skrzyń
- `getLockerResource()` - tekstury szafek
- `getReinforcedRecipe()` - receptury craftingu

**NIE wpływa na:**
- ❌ Pojemność (zależy od configu `reinforcedColumns`)
- ❌ Odporność na wybuchy / twardość
- ❌ Logikę zamków

---

## Itemy

### Itemy główne

| Nazwa zmiennej | Klasa | Registry name | Funkcjonalność |
|----------------|-------|---------------|----------------|
| `key` | `ItemKey` | `betterstorage:key` | Otwieranie zamków |
| `lock` | `ItemLock` | `betterstorage:lock` | Zabezpieczanie kontenerów |
| `keyring` | `ItemKeyring` | `betterstorage:keyring` | Storage dla kluczy |
| `masterKey` | `ItemMasterKey` | `betterstorage:masterKey` | Uniwersalny klucz |
| `cardboardSheet` | `ItemCardboardSheet` | `betterstorage:cardboardSheet` | Materiał craftingu |
| `drinkingHelmet` | `ItemDrinkingHelmet` | `betterstorage:drinkingHelmet` | Hełm do picia |
| `slimeBucket` | `ItemBucketSlime` | `betterstorage:bucketSlime` | Slime w wiaderku |
| `presentBook` | `ItemPresentBook` | `betterstorage:presentBook` | Opakowywanie prezentów |
| `itemBackpack` | `ItemBackpack` | `betterstorage:backpack` | Plecak (item) |
| `itemEnderBackpack` | `ItemEnderBackpack` | `betterstorage:enderBackpack` | Plecak ender - **vanilla ender chest!** |

### Cardboard Items

| Nazwa zmiennej | Klasa | Typ |
|----------------|-------|-----|
| `cardboardHelmet` | `ItemCardboardArmor` | ARMOR_HEAD |
| `cardboardChestplate` | `ItemCardboardArmor` | ARMOR_CHEST |
| `cardboardLeggings` | `ItemCardboardArmor` | ARMOR_LEGS |
| `cardboardBoots` | `ItemCardboardArmor` | ARMOR_FEET |
| `cardboardSword` | `ItemCardboardSword` | weapon |
| `cardboardPickaxe` | `ItemCardboardPickaxe` | tool |
| `cardboardShovel` | `ItemCardboardShovel` | tool |
| `cardboardAxe` | `ItemCardboardAxe` | tool |
| `cardboardHoe` | `ItemCardboardHoe` | tool |

---

## Enchanty

**Plik:** `net.mcft.copy.betterstorage.api.BetterStorageEnchantment`

| Enchant | ID | Efekt | Max level | Konwersja 1.18.2 |
|---------|-----|-------|-----------|------------------|
| **Lockpicking** | 171 | Zwiększa szansę na otwarcie bez klucza | 5 | ❌ Brak |
| **Morphing** | 172 | Zmienia wygląd zamka | 1 | ❌ Brak |
| **Unlocking** | 170 | Pozwala otworzyć bez zużycia klucza | 3 | ❌ Brak |
| **Persistence** | 173 | Zwiększa odporność na wybuchy | 3 | ❌ Brak |
| **Security** | 174 | Blokuje otwieranie bez klucza | 1 | ❌ Brak |
| **Shock** | 175 | Poraża przy próbie włamania | 3 | ❌ Brak |
| **Trigger** | 176 | Wyzwala redstone przy włamaniu | 1 | ❌ Brak |

**Wszystkie enchanty BS zostaną utracone przy konwersji!**

---

## Crate Pile - Struktura danych

### Lokalizacja plików
```
<world>/
  data/
    crates/
      0.dat
      1.dat
      2.dat
      ...
```

### Struktura pliku crate (`<id>.dat`)
```nbt
{
  data: {
    items: [
      {id: "minecraft:stone", Count: 64, Damage: 0},
      ...
    ],
    numCrates: int,
    region: {
      minX: int, minY: int, minZ: int,
      maxX: int, maxY: int, maxZ: int
    }
  }
}
```

### Konsekwencje dla konwersji
1. Musimy odczytać WSZYSTKIE pliki z `data/crates/`
2. Połączyć z TileEntity przez `crateId`
3. Rozdzielić zawartość przy konwersji na osobne skrzynie

---

## Podsumowanie statystyk

| Kategoria | Liczba | Uwagi |
|-----------|--------|-------|
| Bloki | 12 | |
| Tile Entities | 12 | |
| Itemy główne | ~20 | |
| Materiały skrzyń | 9 | TYLKO kosmetyka! |
| Enchanty | 7 | Wszystkie tracone |
| Pojemności skrzyń | 3 | 27/33/39 (config) |
| Crate Pile files | N | W osobnych plikach! |
