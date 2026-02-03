# Instrukcja dla agenta – POPRAWIONA ANALIZA (BetterStorage 1.7.10 → 1.18.2)

**Status:** Poprawiona wersja po weryfikacji kodu  
**Data weryfikacji:** 2026-02-03  
**Kluczowe zmiany:** ContainerMaterial = kosmetyka, Crate = osobne pliki, IronChests ma tylko 7 typów

---

## 1) POPRAWIONE BŁĘDY Z PIERWOTNEJ ANALIZY

### 1.1. ContainerMaterial jest CZYSTO KOSMETYCZNY ✅ ZWERYFIKOWANO

**Dowód z kodu (`ContainerMaterial.java:82-87`):**
```java
public ResourceLocation getChestResource(boolean large) {
    return new BetterStorageResource("textures/models/chest" + (large ? "_large/" : "/") + name + ".png");
}
public ResourceLocation getLockerResource(boolean large) {
    return new BetterStorageResource("textures/models/locker" + (large ? "_large/" : "/") + name + ".png");
}
```

**Wnioski:**
- ContainerMaterial jest używany TYLKO do tekstur (renderowanie)
- NIE wpływa na pojemność, odporność na wybuchy, ani logikę
- Receptury craftingu używają materiału, ale to tylko sposób wytworzenia

**Pojemność skrzyń w BS (`GlobalConfig.java:136`):**
```java
new IntegerSetting(this, reinforcedColumns, 13).setValidValues(9, 11, 13).setComment(
    "Number of columns in reinforced chests and lockers. Valid values are 9, 11 and 13.");
```

- Wszystkie Reinforced Chests mają 3 wiersze (stałe `getRows() = 3`)
- Pojemność zależy od configu: 27, 33 lub 39 slotów (9×3, 11×3, 13×3)
- **NIE zależy od materiału!**

**Poprawione mapowanie:**
- NIE mapujemy "per materiał"
- Wszystkie Reinforced Chests → ten sam typ Iron Chests (zależnie od pojemności w configu)
- Materiał można zachować jako custom name (opcjonalnie)

---

### 1.2. Iron Chests 1.18.2 - ZWERYFIKOWANE ID ✅

**Dowód z kodu (`IronChestsTypes.java:32-41`):**
```java
public enum IronChestsTypes implements StringRepresentable {
  IRON(54, 9, 184, 222, ...),      // 54 slotów
  GOLD(81, 9, 184, 276, ...),      // 81 slotów
  DIAMOND(108, 12, 238, 276, ...), // 108 slotów
  COPPER(45, 9, 184, 204, ...),    // 45 slotów
  CRYSTAL(108, 12, ...),           // 108 slotów, przezroczysta
  OBSIDIAN(108, 12, ...),          // 108 slotów, wybuchoodporna
  DIRT(1, 1, ...),                 // 1 slot (dirt)
  WOOD(0, 0, ...);                 // Nie używana
```

**Istniejące ID:**
- `ironchest:iron_chest` (54)
- `ironchest:gold_chest` (81)
- `ironchest:diamond_chest` (108)
- `ironchest:copper_chest` (45)
- `ironchest:crystal_chest` (108)
- `ironchest:obsidian_chest` (108)
- `ironchest:dirt_chest` (1)
- `ironchest:trapped_*` (warianty z pułapką)

**NIE ISTNIEJĄ:**
- ~~emerald_chest~~ ❌
- ~~silver_chest~~ ❌
- ~~tin_chest~~ ❌
- ~~zinc_chest~~ ❌
- ~~steel_chest~~ ❌

**Poprawione mapowanie Reinforced Chest → Iron Chests:**

| Pojemność BS | Target Iron Chests | Uzasadnienie |
|--------------|-------------------|--------------|
| 27 slotów (9×3) | copper_chest (45) | Najbliższy większy |
| 33 slotów (11×3) | iron_chest (54) | Najbliższy większy |
| 39 slotów (13×3) | iron_chest (54) | Najbliższy większy |

Materiał (iron/gold/diamond/...) ignorujemy lub zapisujemy w custom name.

---

### 1.3. Crate → Storage Drawers ❌ ZMIANA MECHANIKI

**Problem:** Crate w BS to NIE TO SAMO co Drawers!

**Dane Crate (`CratePileCollection.java:73-88`):**
```java
/** Saves the pile data to file. */
// Gets saved to <world>[/<dimension>]/data/crates/<id>.dat in uncompressed NBT.
public void save(CratePileData pileData) {
    File file = getSaveFile(pileData.id);
    // ... zapis do osobnego pliku
}
```

**Kluczowe różnice:**

| Cecha | BS Crate | Storage Drawers |
|-------|----------|-----------------|
| Zawartość | Wspólna dla stosu (crate pile) | Per-blok |
| Sloty | 18 per crate | 1/2/4 per drawer |
| Stackowanie | Do 64 (standard) | Do 512/1024/... (zależy od upgrade) |
| Mechanika | Losowy dostęp | Per-typ itemu |
| Zapis | Osobny plik `<world>/data/crates/<id>.dat` | W chunk data |

**Poprawione mapowanie Crate:**

Opcja A - Zachowanie zawartości (zalecana):
- Crate → Vanilla Chest / Iron Chests
- Każdy crate z stosu → osobna skrzynia
- Zawartość crate pile rozdzielona proporcjonalnie

Opcja B - Zachowanie kompaktowości:
- Crate → Sophisticated Storage (barrel/chest z dużą pojemnością)
- Wymaga upgrade'ów w 1.18.2

Opcja C - Storage Drawers (świadoma zmiana mechaniki):
- Tylko jeśli akceptujemy zmianę "wieloslotowy → per-typ"
- Wymaga reguły rozdziału itemów per typ

**Plan awaryjny:**
- Wypakować zawartość crate pile do skrzyń obok
- Zostawić tabliczkę z info o oryginalnym układzie

---

### 1.4. Locker → Storage Drawers ❌ NIE

**Locker to kontener wieloslotowy:**
- `TileEntityLocker` dziedziczy po `TileEntityLockable`
- Ma `Items[]` - dowolne itemy w slotach
- Nie sortuje per-typ

**Poprawione mapowanie:**
- Locker / Reinforced Locker → Vanilla Chest / Iron Chests / Barrel
- Locker (pionowy) → Barrel (pionowy) z Sophisticated Storage
- Zachowujemy orientację (N/S/E/W), ignorujemy `mirror` (nie ma odpowiednika)

---

### 1.5. Ender Backpack → Vanilla Ender Chest ✅ ZWERYFIKOWANO

**Dowód (`ItemEnderBackpack.java:35-37`):**
```java
@Override
protected IInventory getBackpackItemsInternal(EntityLivingBase carrier, EntityPlayer player) {
    return new InventoryEnderBackpackEquipped(player.getInventoryEnderChest());
}
```

**Wniosek:** Ender Backpack używa **vanilla** ender chest inventory!

**Poprawione mapowanie:**
- Ender Backpack → `minecraft:ender_chest` (vanilla)
- NIE potrzeba Ender Storage modu
- To tylko "dostęp" do vanilla ender chest, nie osobny storage

---

### 1.6. Crafting Station - NIE sprawdzono NBT jeszcze

To wymaga dalszej weryfikacji w Zadaniu 2.

---

## 2) POPRAWIONE STRUKTURY NBT

### 2.1. Reinforced Chest / Locker (TileEntityLockable)

**NBT w pliku (TileEntityContainer.java:326-348):**
```java
@Override
public void writeToNBT(NBTTagCompound compound) {
    super.writeToNBT(compound);
    if (customTitle != null)
        compound.setString("CustomName", customTitle);
    if (contents != null)
        compound.setTag("Items", NbtUtils.writeItems(contents));
    if (hasComparatorAccessed())
        compound.setBoolean("ComparatorAccessed", true);
    if (acceptsRedstoneSignal())
        compound.setByte("RedstonePower", (byte)redstonePower);
}
```

**Dziedziczone z TileEntityLockable:**
```java
// NBT dodatkowe (materiał, zamek, orientacja)
- Material: String ("iron", "gold", ...)
- Lock: NBTTagCompound (ItemStack)
- orientation: byte (0-5)
```

**Struktura końcowa:**
```nbt
{
  Items: [
    {Slot: 0, id: "minecraft:stone", Count: 64, Damage: 0},
    ...
  ],
  Material: "iron",          // TYLKO kosmetyczne
  Lock: {                    // Opcjonalne
    id: "betterstorage:lock",
    Count: 1,
    tag: {full: true, ench: [...]}
  },
  orientation: 2,            // 0-5 (N/S/E/W/U/D)
  CustomName: "Moja Skrzynia" // Opcjonalne
}
```

### 2.2. Crate - CRUCIAL!

**TileEntityCrate NBT (Tylko ID!):**
```java
@Override
public void writeToNBT(NBTTagCompound compound) {
    super.writeToNBT(compound);
    compound.setInteger("crateId", id);
    // Dane są w osobnym pliku!
    getPileData().save();
}
```

**Dane crate pile (`CratePileCollection.java:74-88`):**
- Ścieżka: `<world>/data/crates/<id>.dat`
- Format: NBT (uncompressed)
- Struktura: Zdefiniowana w `CratePileData.toCompound()`

**Konsekwencje dla konwersji:**
1. Musimy odczytać pliki z `data/crates/`
2. Połączyć dane z `crateId` z TileEntity
3. Rozdzielić zawartość przy konwersji

### 2.3. Cardboard Box

**NBT (`TileEntityCardboardBox.java:106-110`):**
```java
@Override
public void writeToNBT(NBTTagCompound compound) {
    super.writeToNBT(compound);
    if (ItemCardboardBox.getUses() > 0) 
        compound.setInteger("uses", uses);
    if (color >= 0) 
        compound.setInteger("color", color);
}
```

**Struktura:**
```nbt
{
  Items: [...],           // 9 slotów (configurable)
  uses: 5,                // Pozostałe użycia
  color: 16777215         // Kolor RGB (opcjonalny)
}
```

---

## 3) POPRAWIONA TABELA MAPOWANIA

### Bloki

| BS 1.7.10 | Target 1.18.2 | ID 1.18.2 | Mechanika | Ryzyko |
|-----------|---------------|-----------|-----------|--------|
| **Reinforced Chest** | Iron Chests ( Copper/Iron/Diamond ) | `ironchest:*_chest` | Wieloslotowy kontener | Niskie |
| **Reinforced Locker** | Iron Chests / Barrel | `ironchest:*_chest` / `minecraft:barrel` | Wieloslotowy kontener | Niskie |
| **Locker** | Barrel / Chest | `minecraft:barrel` | Wieloslotowy kontener | Niskie |
| **Crate** | Chest / Iron Chests | `minecraft:chest` | Wieloslotowy (zawartość z crate pile!) | **WYSOKIE** |
| **Cardboard Box** | Packing Tape / Carry On | `packingtape:packed` | Przenoszenie TE | Średnie |
| **Crafting Station** | Crafting Station | `craftingstation:crafting_station` | Ten sam mod | Do zweryfikowania |
| **Armor Stand** | Vanilla Armor Stand | `minecraft:armor_stand` | Ekspozycja zbroi | Wypakować itemy! |
| **Ender Backpack** | Vanilla Ender Chest | `minecraft:ender_chest` | Vanilla ender chest | Niskie |
| **Present** | Chest + tabliczka | `minecraft:chest` | Ozdobny | Funkcja ozdobna tracona |
| **Flint Block** | Stone / Deepslate | `minecraft:stone` | Dekoracyjny | Niskie |

### Itemy

| BS 1.7.10 | Target 1.18.2 | Uwagi |
|-----------|---------------|-------|
| **Lock** | Lock & Key (jeśli dostępny) | Funkcjonalność podobna |
| **Key** | Lock & Key (jeśli dostępny) | Funkcjonalność podobna |
| **Keyring** | ❌ Brak | Pominąć |
| **Master Key** | ❌ Brak | Pominąć |
| **Backpack** | Sophisticated Backpacks | Osobne zadanie |
| **Ender Backpack** | ❌ NIE konwertować | To tylko "dostęp", nie item storage |

---

## 4) CHECKLISTA POPRAWIONEJ WERSJI

- [x] ContainerMaterial zweryfikowany jako kosmetyczny (tylko tekstury)
- [x] Pojemność skrzyń zależy od configu (27/33/39), NIE od materiału
- [x] Iron Chests ID zweryfikowane - tylko 7 typów (brak emerald/silver/tin/zinc/steel)
- [x] Crate - zawartość w osobnych plikach (`data/crates/<id>.dat`)
- [x] Crate mapowanie - zmiana mechaniki (wieloslotowy → drawers NIE jest 1:1)
- [x] Ender Backpack - używa vanilla ender chest
- [x] Locker - wieloslotowy kontener, nie drawer

---

## 5) DALSZE KROKI (Zadanie 2)

1. **Symulacja Crate Pile:**
   - Jak odczytać pliki `data/crates/<id>.dat`
   - Jak rozdzielić zawartość przy konwersji na osobne skrzynie

2. **Weryfikacja Crafting Station NBT:**
   - Porównać format NBT 1.7.10 vs 1.18.2
   - Jeśli różne → przygotować konwerter

3. **Testy na mapie testowej:**
   - Postawić każdy typ bloku BS
   - Sprawdzić faktyczne NBT w save
   - Przeprowadzić próbną konwersję

---

## 6) KLUCZOWE PLIKI ŹRÓDŁOWE (dla odniesienia)

**BetterStorage 1.7.10:**
- `net.mcft.copy.betterstorage.tile.ContainerMaterial` - Materiały (kosmetyka)
- `net.mcft.copy.betterstorage.config.GlobalConfig` - Pojemności (reinforcedColumns)
- `net.mcft.copy.betterstorage.tile.crate.CratePileCollection` - Zapis crate pile
- `net.mcft.copy.betterstorage.item.ItemEnderBackpack` - Ender backpack = vanilla

**IronChests 1.18.2:**
- `com.progwml6.ironchest.common.block.IronChestsTypes` - Dostępne typy skrzyń
