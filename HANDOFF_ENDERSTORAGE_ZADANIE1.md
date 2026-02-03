# Handoff: EnderStorage - Zadanie 1

## Podsumowanie sesji

Wykonano analizę wszystkich bloków, tile entities/block entities oraz itemów dodawanych przez mod EnderStorage w wersjach 1.7.10 i 1.18.2. EnderStorage to mod dodający kolorowe, wymienne skrzynie i zbiorniki ender, które dzielą zawartość między wszystkie bloki o tej samej kombinacji kolorów.

## Ukończono

- [x] Inwentaryzacja bloków i TE dla wersji 1.7.10
- [x] Inwentaryzacja bloków i BE dla wersji 1.18.2
- [x] Analiza działania każdego elementu z dowodami z kodu
- [x] Wyszukanie źródeł internetowych (wiki, dokumentacja)
- [x] Porównanie różnic między wersjami

---

## 1.7.10 — Bloki

### BlockEnderStorage (enderstorage:blockEnderStorage)
- **Typ:** Block (BlockContainer)
- **ID:** `EnderStorage:blockEnderStorage`
- **Opis działania:** Główny blok modu działający jako "host" dla dwóch typów tile entities w zależności od metadata. Przechowuje wspólne zachowania dla skrzyń i zbiorników: system kolorów (3 przyciski barwników), system własności (diamond + sneak), obracanie, ray tracing dla precyzyjnych interakcji. Metadata 0 = skrzynia, 1 = zbiornik.
- **Dowody z internetu:**
  - Źródło: https://ftb.fandom.com/wiki/Ender_Storage - "Ender Storage is a mod created by ChickenBones... Ender Chest has 3 wool pads on top. Each can be dyed a different color"
  - Źródło: https://github.com/TheCBProject/EnderStorage/wiki - "EnderStorage is a mod that offers a means to store your items in The END"
- **Dowód z kodu:**
  - Plik: `mod_src/1710/actual_src/1.7.10/EnderStorage/repo/src/codechicken/enderstorage/common/BlockEnderStorage.java`
  - Snippet:
```java
@Override
public TileEntity createNewTileEntity(World world, int metadata) {
    switch (metadata) {
        case 0:
            return new TileEnderChest();
        case 1:
            return new TileEnderTank();
    }
    return null;
}
```

---

## 1.7.10 — Tile Entities

### TileFrequencyOwner (abstract)
- **Typ:** TileEntity (bazowa)
- **Opis działania:** Abstrakcyjna klasa bazowa dla wszystkich tile entities EnderStorage. Przechowuje częstotliwość (freq - int z zakresu 0-4095 reprezentujący 3 kolory) oraz właściciela (owner - String, "global" lub nazwa gracza). Obsługuje podstawową synchronizację NBT i pakietów sieciowych.
- **Dowód z kodu:**
  - Plik: `mod_src/1710/actual_src/1.7.10/EnderStorage/repo/src/codechicken/enderstorage/common/TileFrequencyOwner.java`
  - Snippet:
```java
public abstract class TileFrequencyOwner extends TileEntity
{
    public int freq;
    public String owner = "global";
    private int changeCount;
    
    public void setFreq(int i)
    {
        freq = i;
        reloadStorage();
        markDirty();
        worldObj.markBlockForUpdate(xCoord, yCoord, zCoord);
    }
```

### TileEnderChest
- **Typ:** TileEntity (IInventory)
- **Opis działania:** Kolorowa skrzynia ender z 27 slotami (domyślnie). Animacja otwierania/zamykania (lidAngle), obsługa GUI przez pakiet sieciowy, synchronizacja liczby otwarć dla animacji. Implementuje IInventory poprzez delegację do EnderItemStorage (wspólny backend dla wszystkich skrzyń o tej samej częstotliwości). Przechowuje rotację (0-3) dla kierunku.
- **Dowody z internetu:**
  - Źródło: https://ftb.fandom.com/wiki/Ender_Chest_(Ender_Storage) - "Ender Chests are player-specific... accessed from any Ender Chest of the same colour code"
- **Dowód z kodu:**
  - Plik: `mod_src/1710/actual_src/1.7.10/EnderStorage/repo/src/codechicken/enderstorage/storage/item/TileEnderChest.java`
  - Snippet:
```java
public class TileEnderChest extends TileFrequencyOwner implements IInventory
{
    public double a_lidAngle;
    public double b_lidAngle;
    public int c_numOpen;
    public int rotation;
    private EnderItemStorage storage;
    
    public void updateEntity()
    {
        super.updateEntity();
        if(!worldObj.isRemote && (worldObj.getTotalWorldTime() % 20 == 0 || c_numOpen != storage.getNumOpen()))
        {
            c_numOpen = storage.getNumOpen();
            worldObj.addBlockEvent(xCoord, yCoord, zCoord, EnderStorage.blockEnderChest, 1, c_numOpen);
        }
        b_lidAngle = a_lidAngle;
        a_lidAngle = MathHelper.approachLinear(a_lidAngle, c_numOpen > 0 ? 1 : 0, 0.1);
```

### TileEnderTank
- **Typ:** TileEntity (IFluidHandler)
- **Opis działania:** Kolorowy zbiornik na ciecze z pojemnością 16,000 mB. Obsługuje napełnianie/opróżnianie przez IFluidHandler. Posiada system ciśnieniowy (PressureState) - przy sygnale redstone wyrzuca ciecz do sąsiednich zbiorników/kompatybilnych bloków. Animacja obrotu przy zmianie stanu redstone. Invert redstone dostępny przez kliknięcie przycisku.
- **Dowody z internetu:**
  - Źródło: https://ftb.fandom.com/wiki/Ender_Tank - "Ender Tank is a block from Ender Storage... 16,000 mB capacity"
- **Dowód z kodu:**
  - Plik: `mod_src/1710/actual_src/1.7.10/EnderStorage/repo/src/codechicken/enderstorage/storage/liquid/TileEnderTank.java`
  - Snippet:
```java
public class TileEnderTank extends TileFrequencyOwner implements IFluidHandler
{
    public class PressureState
    {
        public boolean invert_redstone;
        public boolean a_pressure;
        public boolean b_pressure;
        public double a_rotate;
        public double b_rotate;
        
        public void update(boolean client) {
            if (!client) {
                b_pressure = a_pressure;
                a_pressure = worldObj.isBlockIndirectlyGettingPowered(xCoord, yCoord, zCoord) != invert_redstone;
            }
        }
    }
    
    private void ejectLiquid() {
        for (ForgeDirection side : ForgeDirection.VALID_DIRECTIONS) {
            TileEntity t = worldObj.getTileEntity(xCoord + side.offsetX, yCoord + side.offsetY, zCoord + side.offsetZ);
            if (!(t instanceof IFluidHandler)) continue;
            FluidStack liquid = drain(null, 100, false);
            if (liquid == null) continue;
            int qty = ((IFluidHandler)t).fill(side.getOpposite(), liquid, true);
            if (qty > 0) drain(null, qty, true);
        }
    }
```

---

## 1.7.10 — Itemy

### ItemEnderPouch
- **Typ:** Item
- **Opis działania:** Przenośna torba dająca dostęp do kolorowej skrzyni ender. Kliknięcie prawym otwiera GUI skrzyni o tej samej częstotliwości co torba. Shift+kliknięcie na skrzynię synchronizuje kolor torby z kolorem skrzyni. Może być personalizowana (owner).
- **Dowody z internetu:**
  - Źródło: https://ftb.fandom.com/wiki/Ender_Pouch - "The Ender Pouch is a portable storage item... right-clicking with the pouch opens an inventory"
- **Dowód z kodu:**
  - Plik: `mod_src/1710/actual_src/1.7.10/EnderStorage/repo/src/codechicken/enderstorage/storage/item/ItemEnderPouch.java`
  - Snippet:
```java
@Override
public ItemStack onItemRightClick(ItemStack item, World world, EntityPlayer player)
{
    if(world.isRemote || player.isSneaking()) return item;
    
    ((EnderItemStorage) EnderStorageManager.instance(world.isRemote)
            .getStorage(getOwner(item), item.getItemDamage() & 0xFFF, "item"))
            .openSMPGui(player, item.getUnlocalizedName()+".name");
    return item;
}
```

---

## 1.18.2 — Bloki

### BlockEnderChest (enderstorage:ender_chest)
- **Typ:** Block
- **ID:** `enderstorage:ender_chest`
- **Opis działania:** Skrzynia ender jako osobny blok (nie wspólny block ID jak w 1.7.10). Rejestrowana przez DeferredRegister. Posiada własny BlockEntityType. Obsługuje interakcje z barwnikami, diamentem (personalizacja), obracanie.
- **Dowód z kodu:**
  - Plik: `mod_src/118/actual_src/1.18.2/EnderStorage/repo/src/main/java/codechicken/enderstorage/init/EnderStorageModContent.java`
  - Snippet:
```java
public static final RegistryObject<BlockEnderChest> ENDER_CHEST_BLOCK = BLOCKS.register("ender_chest", () -> new BlockEnderChest(blockProps));
public static final RegistryObject<BlockEntityType<TileEnderChest>> ENDER_CHEST_TILE = BLOCK_ENTITY_TYPES.register("ender_chest", () ->
        BlockEntityType.Builder.of(TileEnderChest::new, ENDER_CHEST_BLOCK.get()).build(null)
);
```

### BlockEnderTank (enderstorage:ender_tank)
- **Typ:** Block
- **ID:** `enderstorage:ender_tank`
- **Opis działania:** Zbiornik cieczy jako osobny blok. Podobne zachowanie do wersji 1.7.10 ale z nowym API (CapabilityFluidHandler zamiast IFluidHandler). Obsługuje interakcje z wiaderkami przez FluidUtil.
- **Dowód z kodu:**
  - Plik: `mod_src/118/actual_src/1.18.2/EnderStorage/repo/src/main/java/codechicken/enderstorage/init/EnderStorageModContent.java`
  - Snippet:
```java
public static final RegistryObject<BlockEnderTank> ENDER_TANK_BLOCK = BLOCKS.register("ender_tank", () -> new BlockEnderTank(blockProps));
public static final RegistryObject<BlockEntityType<TileEnderTank>> ENDER_TANK_TILE = BLOCK_ENTITY_TYPES.register("ender_tank", () ->
        BlockEntityType.Builder.of(TileEnderTank::new, ENDER_TANK_BLOCK.get()).build(null)
);
```

---

## 1.18.2 — Block Entities

### TileFrequencyOwner (abstract)
- **Typ:** BlockEntity (bazowa)
- **Opis działania:** Ulepszona wersja klasy bazowej. Używa nowej klasy Frequency (zamiast int freq + String owner). Frequency przechowuje 3 kolory (EnumColour) oraz UUID właściciela (zamiast String). Lepsza obsługa synchronizacji przez nowe API sieciowe (MCDataInput/MCDataOutput).
- **Dowód z kodu:**
  - Plik: `mod_src/118/actual_src/1.18.2/EnderStorage/repo/src/main/java/codechicken/enderstorage/tile/TileFrequencyOwner.java`
  - Snippet:
```java
public abstract class TileFrequencyOwner extends BlockEntity {
    public static final Cuboid6 SELECTION_BUTTON = new Cuboid6(-1 / 16D, 0, -2 / 16D, 1 / 16D, 1 / 16D, 2 / 16D);
    protected Frequency frequency = new Frequency();
    private int changeCount;

    public void setFreq(Frequency frequency) {
        this.frequency = frequency;
        onFrequencySet();
        setChanged();
        BlockState state = level.getBlockState(worldPosition);
        level.sendBlockUpdated(worldPosition, state, state, 3);
        if (!level.isClientSide) {
            sendUpdatePacket();
        }
    }
```

### TileEnderChest
- **Typ:** BlockEntity (Container + IItemHandler capability)
- **Opis działania:** Nowa implementacja z użyciem Capability System (LazyOptional<IItemHandler>). Zamiast implementować IInventory bezpośrednio, deleguje przez InvWrapper. Obsługuje dźwięki otwierania/zamykania z konfiguracją (vanilla vs custom). Tick synchronizuje stan otwarcia i aktualizuje sąsiadów przy zmianie.
- **Dowód z kodu:**
  - Plik: `mod_src/118/actual_src/1.18.2/EnderStorage/repo/src/main/java/codechicken/enderstorage/tile/TileEnderChest.java`
  - Snippet:
```java
public class TileEnderChest extends TileFrequencyOwner {
    public double a_lidAngle;
    public double b_lidAngle;
    public int c_numOpen;
    public int rotation;
    private LazyOptional<IItemHandler> itemHandler = LazyOptional.empty();

    @Override
    public void tick() {
        super.tick();
        if (!level.isClientSide && (level.getGameTime() % 20 == 0 || c_numOpen != getStorage().getNumOpen())) {
            c_numOpen = getStorage().getNumOpen();
            level.blockEvent(getBlockPos(), getBlockState().getBlock(), 1, c_numOpen);
            level.updateNeighborsAt(worldPosition, getBlockState().getBlock());
        }
        b_lidAngle = a_lidAngle;
        a_lidAngle = MathHelper.approachLinear(a_lidAngle, c_numOpen > 0 ? 1 : 0, 0.1);
```

### TileEnderTank
- **Typ:** BlockEntity (IFluidHandler capability)
- **Opis działania:** Zbiornik używający CapabilityFluidHandler (LazyOptional<IFluidHandler>). Posiada CapabilityCache do optymalizacji wyszukiwania sąsiednich zbiorników (unika ciągłego getCapability). System ciśnieniowy podobny do 1.7.10 ale z użyciem nowego API redstone (hasNeighborSignal).
- **Dowód z kodu:**
  - Plik: `mod_src/118/actual_src/1.18.2/EnderStorage/repo/src/main/java/codechicken/enderstorage/tile/TileEnderTank.java`
  - Snippet:
```java
public class TileEnderTank extends TileFrequencyOwner {
    public final EnderTankState liquid_state = new EnderTankState();
    public final PressureState pressure_state = new PressureState();
    private final CapabilityCache capCache = new CapabilityCache();
    private LazyOptional<IFluidHandler> fluidHandler = LazyOptional.empty();

    private void ejectLiquid() {
        IFluidHandler source = getStorage();
        for (Direction side : Direction.BY_3D_DATA) {
            IFluidHandler dest = capCache.getCapabilityOr(CapabilityFluidHandler.FLUID_HANDLER_CAPABILITY, side, EmptyFluidHandler.INSTANCE);
            FluidStack drain = source.drain(100, IFluidHandler.FluidAction.SIMULATE);
            if (!drain.isEmpty()) {
                int qty = dest.fill(drain, IFluidHandler.FluidAction.EXECUTE);
                if (qty > 0) {
                    source.drain(qty, IFluidHandler.FluidAction.EXECUTE);
                }
            }
        }
    }
```

---

## 1.18.2 — Itemy

### ItemEnderPouch
- **Typ:** Item
- **Opis działania:** Przenośna torba z nowym API (InteractionResult). Używa Component do nazw (zamiast String). Synchronizacja z skrzynią przez Frequency (zamiast int damage). Otwiera SimpleMenuProvider zamiast bezpośredniego GUI.
- **Dowód z kodu:**
  - Plik: `mod_src/118/actual_src/1.18.2/EnderStorage/repo/src/main/java/codechicken/enderstorage/item/ItemEnderPouch.java`
  - Snippet:
```java
@Override
public InteractionResultHolder<ItemStack> use(Level world, Player player, InteractionHand hand) {
    ItemStack stack = player.getItemInHand(hand);
    if (player.isCrouching()) {
        return new InteractionResultHolder<>(InteractionResult.PASS, stack);
    }
    if (!world.isClientSide) {
        Frequency frequency = Frequency.readFromStack(stack);
        EnderStorageManager.instance(world.isClientSide).getStorage(frequency, EnderItemStorage.TYPE).openContainer((ServerPlayer) player, new TranslatableComponent(stack.getDescriptionId()));
    }
    return new InteractionResultHolder<>(InteractionResult.SUCCESS, stack);
}
```

---

## Porównanie 1.7.10 vs 1.18.2

### Bloki
| Aspekt | 1.7.10 | 1.18.2 |
|--------|--------|--------|
| Rejestracja | GameRegistry.registerBlock | DeferredRegister |
| ID | Jeden blok z metadatą (0=chest, 1=tank) | Osobne bloki: ender_chest, ender_tank |
| BlockEntity | createNewTileEntity(metadata) | BlockEntityType.Builder |

### Tile/Block Entities
| Aspekt | 1.7.10 | 1.18.2 |
|--------|--------|--------|
| Klasa bazowa | TileEntity | BlockEntity |
| Częstotliwość | int freq (0-4095) | Frequency (3x EnumColour) |
| Właściciel | String owner ("global"/nazwa) | UUID owner |
| NBT | readFromNBT/writeToNBT | load/saveAdditional |
| Sieć | PacketCustom | PacketCustom + MCDataOutput |
| Inventory | IInventory | Container + IItemHandler capability |
| Fluids | IFluidHandler | IFluidHandler capability |
| Capabilities | Brak | LazyOptional system |

### Storage Backend
| Aspekt | 1.7.10 | 1.18.2 |
|--------|--------|--------|
| Klucz | freq + "\|" + owner + "\|" + type | Frequency (z UUID) |
| ItemStack array | ItemStack[] | ItemStack[] |
| Empty stack | null | ItemStack.EMPTY |
| Sync | Własny system | EnderStorageNetwork |

### System Kolorów
| Aspekt | 1.7.10 | 1.18.2 |
|--------|--------|--------|
| Typ | int (0-4095) | EnumColour (3 wartości) |
| Konwersja | getColoursFromFreq() | Bezpośrednio w Frequency |
| NBT | int freq | CompoundTag z left/middle/right |

### Własność (Personal)
| Aspekt | 1.7.10 | 1.18.2 |
|--------|--------|--------|
| Global | owner = "global" | owner = null |
| Personal | owner = playerName | owner = UUID + Component name |
| Item | diamond | Skonfigurowalny (diamond) |

---

## Nowe pliki

Brak nowych plików - wykonano analizę istniejącego kodu.

## Zmodyfikowane pliki

Brak zmodyfikowanych plików - wykonano analizę istniejącego kodu.

---

## Następne kroki

1. [ ] Przygotowanie symulacji działania funkcjonalności EnderStorage (zadanie 2)
   - Symulacja systemu Frequency i kolorów
   - Symulacja współdzielenia inventory między skrzyniami
   - Symulacja transferu cieczy w zbiornikach
   
2. [ ] Napisanie kodu konwersji (zadanie 3)
   - Mapowanie TileEnderChest → TileEnderChest (1.18.2)
   - Mapowanie TileEnderTank → TileEnderTank (1.18.2)
   - Konwersja NBT: int freq → Frequency object
   - Konwersja owner: String → UUID
   - Obsługa EnderPouch
   
3. [ ] Sprawdzenie pokrycia na mapie głównej (zadanie 4)
   - Wyszukanie wszystkich bloków EnderStorage na mapie 1710
   - Weryfikacja czy konwersja pokrywa wszystkie przypadki
   
4. [ ] Testowa mapa i konwersja (zadanie 5)
   - Stworzenie mapy testowej z różnymi kombinacjami kolorów
   - Test konwersji z weryfikacją zawartości
   
5. [ ] Test headless serwer (zadanie 6)
   - Weryfikacja działania po konwersji na serwerze

---

## Źródła zewnętrzne

1. **EnderStorage Wiki** - https://github.com/TheCBProject/EnderStorage/wiki
2. **FTB Wiki - Ender Chest** - https://ftb.fandom.com/wiki/Ender_Chest_(Ender_Storage)
3. **FTB Wiki - Ender Tank** - https://ftb.fandom.com/wiki/Ender_Tank
4. **FTB Wiki - Ender Pouch** - https://ftb.fandom.com/wiki/Ender_Pouch
5. **CurseForge** - https://www.curseforge.com/minecraft/mc-mods/ender-storage-1-8

---

*Data utworzenia: 2026-02-03*
*Zadanie 1 zakończone*
