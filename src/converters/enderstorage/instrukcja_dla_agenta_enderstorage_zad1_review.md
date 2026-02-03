# Instrukcja dla agenta: co sprawdzić ponownie w raporcie (EnderStorage 1.7.10 ↔ 1.18.2)

Ten dokument ma pomóc doprecyzować **miejsca wymagające ponownej weryfikacji** oraz wskazać **konkretne kroki/plik/miejsca w kodzie**, gdzie raport jest mylący lub potencjalnie błędny.

---

## ✅ POPRAWIONO: Identyfikacja bloku w 1.7.10

### Co było w raporcie (błąd)
W sekcji **„1.7.10 — Bloki"** raport opisywał:
- `### BlockEnderStorage (enderstorage:blockEnderStorage)`
- `ID: EnderStorage:blockEnderStorage`

To sugerowało „nowoczesny" namespaced ID jak w 1.13+.

### Poprawiona wersja
W **Minecraft 1.7.10** zapis świata działa na **numeric block ID + metadata**:

| Element | Wartość |
|---------|---------|
| Rejestracja | `GameRegistry.registerBlock(blockEnderChest, ItemEnderStorage.class, "enderChest")` |
| Unlocalized name | `enderchest` (ustawione przez `setBlockName("enderchest")`) |
| Tile Entity ID (chest) | `Ender Chest` |
| Tile Entity ID (tank) | `Ender Tank` |

**Kluczowe**: W 1.7.10 jest tylko **JEDEN blok** `BlockEnderStorage` obsługujący oba typy przez **metadata**:
- `meta = 0` → `TileEnderChest`
- `meta = 1` → `TileEnderTank`

**Dowód z kodu:**
```java
// EnderStorageProxy.java:24
GameRegistry.registerBlock(blockEnderChest, ItemEnderStorage.class, "enderChest");
blockEnderChest.setBlockName("enderchest");

// BlockEnderStorage.java:54-61
@Override
public TileEntity createNewTileEntity(World world, int metadata) {
    switch (metadata) {
        case 0: return new TileEnderChest();
        case 1: return new TileEnderTank();
    }
    return null;
}
```

---

## ✅ POPRAWIONO: Zachowanie PressureState / redstone w Ender Tank (1.7.10)

### Mechanizm (potwierdzono w kodzie)
**To jest aktywny PUSH (pompa)** - nie tylko przełączanie trybu:

1. **W ticku** (`updateEntity()`): Jeśli `pressure_state.a_pressure == true`, wywoływane jest `ejectLiquid()`
2. **ejectLiquid()**: Aktywnie iteruje po sąsiadach i wypycha ciecz do `IFluidHandler` (max 100 mB na próbę)
3. **PressureState.a_pressure**: Ustawiana na podstawie sygnału redstone (`isBlockIndirectlyGettingPowered`) z opcją inwersji

**Dowód z kodu:**
```java
// TileEnderTank.java:106-114
@Override
public void updateEntity() {
    super.updateEntity();
    pressure_state.update(worldObj.isRemote);
    if (pressure_state.a_pressure)
        ejectLiquid();  // <-- AKTYWNY PUSH
    liquid_state.update(worldObj.isRemote);
}

// TileEnderTank.java:116-130 (ejectLiquid)
private void ejectLiquid() {
    for (ForgeDirection side : ForgeDirection.VALID_DIRECTIONS) {
        TileEntity t = worldObj.getTileEntity(xCoord + side.offsetX, ...);
        if (!(t instanceof IFluidHandler)) continue;
        IFluidHandler c = (IFluidHandler) t;
        FluidStack liquid = drain(null, 100, false);  // Symulacja
        if (liquid == null) continue;
        int qty = c.fill(side.getOpposite(), liquid, true);  // Wypełnienie sąsiada
        if (qty > 0) drain(null, qty, true);  // Faktyczne usunięcie
    }
}
```

**Reguła**: Redstone ON → `a_pressure = true` → w ticku następuje `ejectLiquid()` → aktywne wypychanie do sąsiednich zbiorników/maszyn (max 100mB na kierunek).

---

## ✅ POPRAWIONO: Szczegóły NBT w 1.7.10 oraz konsekwencje migracji

### NBT TileFrequencyOwner (bazowa klasa 1.7.10)

| Klucz | Typ | Opis |
|-------|-----|------|
| `freq` | int (0-4095) | Częstotliwość = (color1 << 8) + (color2 << 4) + color3 |
| `owner` | String | `"global"` lub nazwa gracza (dla prywatnych) |

**Dowód z kodu:**
```java
// TileFrequencyOwner.java:66-78
public void readFromNBT(NBTTagCompound tag) {
    super.readFromNBT(tag);
    freq = tag.getInteger("freq");
    owner = tag.getString("owner");
}

public void writeToNBT(NBTTagCompound tag) {
    super.writeToNBT(tag);
    tag.setInteger("freq", freq);
    tag.setString("owner", owner);
}
```

### Dodatkowe NBT w podklasach

**TileEnderChest:**
| Klucz | Typ | Opis |
|-------|-----|------|
| `rot` | byte (0-3) | Rotacja skrzyni |

**TileEnderTank:**
| Klucz | Typ | Opis |
|-------|-----|------|
| `rot` | byte (0-3) | Rotacja zbiornika |
| `ir` | boolean | Invert redstone (PressureState) |

---

## ✅ POPRAWIONO: NBT w 1.18.2

### Struktura Frequency (1.18.2)

Zamiast `int freq`, w 1.18.2 używany jest obiekt `Frequency` zapisany jako CompoundTag:

| Klucz | Typ | Opis |
|-------|-----|------|
| `Frequency` | CompoundTag | Kontener z kolorami i właścicielem |
| `Frequency.left` | int | Kolor 1 (wool meta) |
| `Frequency.middle` | int | Kolor 2 (wool meta) |
| `Frequency.right` | int | Kolor 3 (wool meta) |
| `Frequency.owner` | UUID | UUID właściciela (opcjonalne) |
| `Frequency.owner_name` | String | Nazwa właściciela (JSON Component) |

**Dowód z kodu:**
```java
// Frequency.java:140-151
protected Frequency read_internal(CompoundTag tagCompound) {
    left = EnumColour.fromWoolMeta(tagCompound.getInt("left"));
    middle = EnumColour.fromWoolMeta(tagCompound.getInt("middle"));
    right = EnumColour.fromWoolMeta(tagCompound.getInt("right"));
    if (tagCompound.hasUUID("owner")) {
        owner = tagCompound.getUUID("owner");
    }
    if (tagCompound.contains("owner_name")) {
        ownerName = Component.Serializer.fromJson(tagCompound.getString("owner_name"));
    }
    return this;
}
```

### TileFrequencyOwner (1.18.2)
```java
// TileFrequencyOwner.java:61-69
@Override
public void load(CompoundTag tag) {
    super.load(tag);
    frequency.set(new Frequency(tag.getCompound("Frequency")));
}

@Override
public void saveAdditional(CompoundTag tag) {
    tag.put("Frequency", frequency.writeToNBT(new CompoundTag()));
}
```

### Dodatkowe NBT w podklasach (1.18.2)

**TileEnderChest:**
| Klucz | Typ | Opis |
|-------|-----|------|
| `rot` | byte (0-3) | Rotacja skrzyni |

**TileEnderTank:**
| Klucz | Typ | Opis |
|-------|-----|------|
| `rot` | byte (0-3) | Rotacja zbiornika |
| `ir` | boolean | Invert redstone |

---

## 📋 Tabela mapowania NBT: 1.7.10 → 1.18.2

| Element | 1.7.10 | 1.18.2 | Uwagi |
|---------|--------|--------|-------|
| **Blok** | Jeden blok, meta 0/1 | Osobne bloki: `ender_chest`, `ender_tank` | Konwersja wymaga rozdzielenia meta na osobne bloki |
| **Freq storage** | `int freq` (0-4095) | `Frequency` object | Konwersja: rozbić int na 3 kolory |
| **Kolory** | Zakodowane w freq | `left`, `middle`, `right` (int) | `colour1 = (freq >> 8) & 0xF` |
| **Właściciel** | `String owner` ("global" \| nazwa) | `UUID owner` + `Component ownerName` | Globalny: null UUID; Personalny: UUID + nazwa |
| **Rotacja** | `byte rot` | `byte rot` | Bez zmian |
| **Invert redstone (tank)** | `boolean ir` | `boolean ir` | Bez zmian |

### Algorytm konwersji częstotliwości (1.7.10 → 1.18.2)

```java
// 1.7.10: int freq (12 bitów: 4+4+4)
int colour1 = (freq >> 8) & 0xF;  // left
int colour2 = (freq >> 4) & 0xF;  // middle  
int colour3 = freq & 0xF;          // right

// 1.18.2: Frequency z EnumColour (wool meta)
Frequency f = new Frequency(
    EnumColour.fromWoolMeta(colour1),
    EnumColour.fromWoolMeta(colour2),
    EnumColour.fromWoolMeta(colour3),
    ownerUUID,      // null dla global, UUID dla personal
    ownerComponent  // null dla global, Component dla personal
);
```

### Algorytm konwersji właściciela (1.7.10 → 1.18.2)

```java
// 1.7.10
String owner = tag.getString("owner");  // "global" lub "PlayerName"

// 1.18.2
if ("global".equals(owner)) {
    frequency.setOwner(null);  // null = global
    frequency.setOwnerName(null);
} else {
    // Wymaga lookup UUID z nazwy gracza (z world save lub offline UUID)
    UUID playerUUID = resolveUUID(owner);  // offline UUID lub z playerdata
    frequency.setOwner(playerUUID);
    frequency.setOwnerName(new TextComponent(owner));
}
```

---

## ✅ POPRAWIONO: 1.18.2 - dowody z kodu

### Rejestracja (DeferredRegister)
**Plik:** `mod_src/118/actual_src/1.18.2/EnderStorage/repo/src/main/java/codechicken/enderstorage/init/EnderStorageModContent.java`

```java
// Linie 44-57
public static final RegistryObject<BlockEnderChest> ENDER_CHEST_BLOCK = BLOCKS.register("ender_chest", () -> new BlockEnderChest(blockProps));
public static final RegistryObject<BlockEnderTank> ENDER_TANK_BLOCK = BLOCKS.register("ender_tank", () -> new BlockEnderTank(blockProps));

public static final RegistryObject<BlockEntityType<TileEnderChest>> ENDER_CHEST_TILE = BLOCK_ENTITY_TYPES.register("ender_chest", () ->
        BlockEntityType.Builder.of(TileEnderChest::new, ENDER_CHEST_BLOCK.get()).build(null)
);
public static final RegistryObject<BlockEntityType<TileEnderTank>> ENDER_TANK_TILE = BLOCK_ENTITY_TYPES.register("ender_tank", () ->
        BlockEntityType.Builder.of(TileEnderTank::new, ENDER_TANK_BLOCK.get()).build(null)
);
```

### Capability System (TileEnderChest)
**Plik:** `mod_src/118/actual_src/1.18.2/EnderStorage/repo/src/main/java/codechicken/enderstorage/tile/TileEnderChest.java`

```java
// Linie 40, 152-159
private LazyOptional<IItemHandler> itemHandler = LazyOptional.empty();

@Nonnull
@Override
public <T> LazyOptional<T> getCapability(@Nonnull Capability<T> cap, @Nullable Direction side) {
    if (!remove && cap == CapabilityItemHandler.ITEM_HANDLER_CAPABILITY) {
        return itemHandler.cast();
    }
    return super.getCapability(cap, side);
}
```

### Ender Pouch - ta sama Frequency
**Plik:** `mod_src/118/actual_src/1.18.2/EnderStorage/repo/src/main/java/codechicken/enderstorage/item/ItemEnderPouch.java`

```java
// Linia 78-79
Frequency frequency = Frequency.readFromStack(stack);
EnderStorageManager.instance(world.isClientSide).getStorage(frequency, EnderItemStorage.TYPE).openContainer(...);
```

Ender Pouch używa dokładnie tej samej klasy `Frequency` co skrzynie (czytana z NBT stacka: `stack.getTag().getCompound("Frequency")`).

---

## ⚠️ Notatka dla konwersji światów (praktyczne ryzyko)

### Największe ryzyka:

1. **Rozdzielenie bloku 1.7.10 na dwa bloki 1.18.2**
   - 1.7.10: `enderChest` (ID numeryczne) z meta 0/1
   - 1.18.2: `enderstorage:ender_chest` i `enderstorage:ender_tank` (osobne blockstates)
   - **Konieczność**: mapowania meta → block ID w zależności od typu

2. **Konwersja właściciela (String → UUID)**
   - Offline UUID: `UUID.nameUUIDFromBytes(("OfflinePlayer:" + name).getBytes())`
   - Dla graczy online: konieczność lookup z `playerdata/` lub mapowania ręcznego

3. **Storage backend (zawartość skrzyń/zbiorników)**
   - W 1.7.10: `EnderStorage/data1.dat` lub `data2.dat` w save
   - W 1.18.2: `data/enderstorage/...`
   - **Konwersja wymaga**: migracji plików storage + konwersji kluczy (freq|owner → Frequency)

---

## ✅ Checklist poprawek (zakończono)

- [x] Poprawiono identyfikację bloku 1.7.10 (numeric ID + meta, nie namespaced ID)
- [x] Dodano informację o jednym bloku z meta dla obu typów (chest/tank)
- [x] Doprecyzowano PressureState: potwierdzono aktywny push w ticku przy redstone
- [x] Dodano tabelę mapowania NBT: 1.7.10 → 1.18.2 (freq/owner/rot/ir)
- [x] Dodano algorytm konwersji częstotliwości (int → 3 kolory)
- [x] Dodano algorytm konwersji właściciela (String → UUID)
- [x] Dla 1.18.2 podano konkretne pliki i linie kodu
- [x] Ujednolicono słownictwo: TileEntity (1.7.10) / BlockEntity (1.18.2)

---

*Data aktualizacji: 2026-02-03*
*Status: Poprawki wprowadzone, dokument gotowy do zadania 2 (symulacje)*
