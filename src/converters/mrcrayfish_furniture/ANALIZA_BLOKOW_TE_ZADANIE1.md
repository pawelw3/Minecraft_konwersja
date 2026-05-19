# Analiza blokow i Tile Entities – MrCrayfish Furniture Mod

## Cel zadania
Zidentyfikowac wszystkie bloki, tile entities (TE) i ich wlasciwosci w MrCrayfish Furniture Mod w wersjach 1.7.10 oraz 1.18.2, aby zbudowac konwerter mapujacy swiat.

## Zrodla
- **1.7.10 (source):** MrCrayfishFurnitureMod.java, pakiety com.mrcrayfish.furniture.tileentity.*
- **1.18.2 (target):** ModBlocks.java, ModBlockEntities.java, pakiety com.mrcrayfish.furniture.blockentity.*

---

## 1. Rejestracja blokow – porownanie 1.7.10 vs 1.18.2

### 1.1 Bloki zarejestrowane w 1.7.10

W MrCrayfishFurnitureMod.java bloki rejestrowane sa przez:
```
GameRegistry.registerBlock(block, block.func_149739_a().substring(5));
```

| Lp | Nazwa rejestru (ID) | Klasa bloku | Uwagi |
|----|---------------------|-------------|-------|
| 1  | lampon | BlockLampOn | Lampka wlaczona |
| 2  | lampoff | BlockLampOff | Lampka wylaczona |
| 3  | coffetablewood | BlockCoffeeTable | Stolik kawowy (drewno) |
| 4  | coffetablestone | BlockCoffeeTable | Stolik kawowy (kamien) |
| 5  | tablewood | BlockTable | Stol (drewno) |
| 6  | tablestone | BlockTable | Stol (kamien) |
| 7  | chairwood | BlockChair | Krzeslo (drewno) |
| 8  | chairstone | BlockChair | Krzeslo (kamien) |
| 9  | freezer | BlockFreezer | Zamrazarka (dolna czesc lodowki) |
| 10 | fridge | BlockFridge | Lodowka (gorna czesc) |
| 11 | cabinet | BlockCabinet | Szafka |
| 12 | couch | BlockCouch | Sofa (z podtypami kolorow) |
| 13 | blinds | BlockBlinds | Rolety (otwarte) |
| 14 | blindsclosed | BlockBlindsClosed | Rolety (zamkniete) |
| 15 | curtains | BlockCurtains | Zaslony |
| 16 | curtainsoff | BlockCurtainsOff | Zaslony wylaczone |
| 17 | bedsidecabinet | BlockBedsideCabinet | Szafka nocna |
| 18 | oven | BlockOven | Piekarnik |
| 19 | ovenoverhead | BlockOvenOverhead | Okap nad piekarnikiem |
| 20 | microwave | BlockMicrowave | Kuchenka mikrofalowa |
| 21 | computer | BlockComputer | Komputer |
| 22 | printer | BlockPrinter | Drukarka |
| 23 | tv | BlockTV | Telewizor |
| 24 | stereo | BlockStereo | Stereo / radio |
| 25 | washingmachine | BlockWashingMachine | Pralka |
| 26 | dishwasher | BlockDishwasher | Zmywarka |
| 27 | mailbox | BlockMailBox | Skrzynka pocztowa |
| 28 | bin | BlockBin | Kosz na smieci |
| 29 | toaster | BlockToaster | Toster |
| 30 | blender | BlockBlender | Blender |
| 31 | plate | BlockPlate | Talerz |
| 32 | cup | BlockCup | Kubek |
| 33 | counterdoored | BlockCounterDoored | Szafka kuchenna (z drzwiami) |
| 34 | countersink | BlockCounterSink | Zlew kuchenny |
| 35 | kitchencabinet | BlockKitchenCabinet | Szafka kuchenna |
| 36 | choppingboard | BlockChoppingBoard | Deska do krojenia |
| 37 | barstool | BlockBarStool | Stolek barowy |
| 38 | cookiejar | BlockCookieJar | Sloik na ciastka |
| 39 | present | BlockPresent | Prezent |
| 40 | tree | BlockTree | Dekoracyjne drzewko |
| 41 | bath1 | BlockBath | Wanna (czesc 1) |
| 42 | bath2 | BlockBath | Wanna (czesc 2) |
| 43 | showerbottom | BlockShowerBottom | Prysznic (dol) |
| 44 | showertop | BlockShowerTop | Prysznic (gora) |
| 45 | showerheadoff | BlockShowerHeadOff | Glowka prysznicowa (wylaczona) |
| 46 | showerheadon | BlockShowerHeadOn | Glowka prysznicowa (wlaczona) |
| 47 | basin | BlockBasin | Umywalka |
| 48 | wallcabinet | BlockWallCabinet | Szafka scienna |
| 49 | birdbath | BlockBirdBath | Poidlo dla ptakow |
| 50 | stonepath | BlockStonePath | Kamienna sciezka |
| 51 | whitefence | BlockWhiteFence | Bialy plot |
| 52 | tap | BlockTap | Kran |
| 53 | electricfence | BlockElectricFence | Elektryczne ogrodzenie |
| 54 | doorbell | BlockDoorbell | Dzwonek do drzwi |
| 55 | firealarmoff | BlockFireAlarmOff | Alarm przeciwppozarowy (wylaczony) |
| 56 | firealarmon | BlockFireAlarmOn | Alarm przeciwppozarowy (wlaczony) |
| 57 | ceilinglightoff | BlockCeilingLightOff | Swiatlo sufitowe (wylaczone) |
| 58 | ceilinglighton | BlockCeilingLightOn | Swiatlo sufitowe (wlaczone) |
| 59 | toilet | BlockToilet | Toaleta |
| 60 | hedge | BlockHedge | Zywoplot |
| 61 | hey | BlockHey | Dekoracyjny blok Hey |
| 62 | nyan | BlockNyan | Dekoracyjny blok Nyan |
| 63 | pattern | BlockPattern | Wzorzysty blok dekoracyjny |
| 64 | yellowglow | BlockYellowGlow | Zolty blok swiecacy |
| 65 | whiteglass | BlockWhiteGlass | Biale szklo dekoracyjne |

**Liczba blokow:** ~65+

**Uwagi:** Niektore bloki wystepuja w parach on/off. freezer i fridge tworza wieloblok. bath1/bath2 i showerbottom/showertop tworza wielobloki. couch uzywa metadanych dla kolorow (16 kolorow welny).

### 1.2 Bloki zarejestrowane w 1.18.2

W ModBlocks.java uzywany jest DeferredRegister z ResourceLocation.

Przyklady blokow (warianty materialowe i kolorowe):
- Stoly: oak_table, spruce_table, birch_table, jungle_table, acacia_table, dark_oak_table, crimson_table, warped_table, stripped_oak_table, ..., stone_table, granite_table, diorite_table, andesite_table
- Krzesla: oak_chair, spruce_chair, ..., stone_chair, granite_chair, ...
- Stoliki kawowe: oak_coffee_table, ..., stone_coffee_table, ...
- Sofy: white_sofa, orange_sofa, ..., black_sofa (16 kolorow barwnikow)
- Szafki: oak_cabinet, spruce_cabinet, ..., stone_cabinet, granite_cabinet, ...
- Szafki nocne: oak_bedside_cabinet, ...
- Biurka: oak_desk, ..., stone_desk, ...
- Szafki pod biurko: oak_desk_cabinet, ...
- Skrzynki: oak_crate, ...
- Lawki parkowe: oak_park_bench, ...
- Rolety: oak_blinds, ...
- Zaslony: oak_curtains, ...
- Ogrodzenia upgraded: oak_upgraded_fence, oak_upgraded_gate, ...
- Plotki: white_picket_fence, ..., orange_picket_fence, ... (16 kolorow)
- Furtka plotkowa: white_picket_gate, ... (16 kolorow)
- Skrzynki pocztowe: oak_mail_box, ...
- Trampoliny: oak_trampoline, ...
- Coolery: white_cooler, orange_cooler, ... (16 kolorow)
- Grille: white_grill, orange_grill, ... (16 kolorow)
- Deska do nurkowania: oak_diving_board
- Wycieraczki: oak_door_mat, ...
- Blaty kuchenne: white_kitchen_counter, ... (16 kolorow)
- Szuflady kuchenne: white_kitchen_drawer, ... (16 kolorow)
- Zlewy kuchenne: white_kitchen_sink, ... (16 kolorow)
- Kamienna sciezka: rock_path
- Zywoploty: oak_hedge, ... (warianty lisci)
- Lodowki: fridge_light, fridge_dark
- Zamrazarki: freezer_light, freezer_dark

**Liczba blokow:** ~300+ (wliczajac warianty materialow i kolorow)

**Kluczowe roznice:**
- W 1.18.2 kazdy material (oak, spruce, stone, granite, itd.) to osobny blok
- Dodano nowe bloki: crate, desk, desk_cabinet, park_bench, upgraded_fence/gate, picket_fence/gate, trampoline, cooler, grill, diving_board, door_mat, kitchen_counter/drawer/sink, rock_path
- USUNIETE z 1.18.2: Oven, Microwave, Computer, Printer, TV, Stereo, WashingMachine, Dishwasher, Toilet, Basin, Bath, Shower, ShowerHead, WallCabinet, BirdBath, StonePath, Tap, ElectricFence, FireAlarm, CeilingLight, Lamp, Tree, Present, Toaster, Blender, Plate, Cup, ChoppingBoard, BarStool, CookieJar, CounterDoored, CounterSink

---

## 2. Rejestracja Tile Entities / Block Entities – porownanie

### 2.1 Tile Entities w 1.7.10

W MrCrayfishFurnitureMod.java rejestracja przez:
```
GameRegistry.registerTileEntity(TileEntityOven.class, "cfmOven");
```

| Lp | Nazwa TE (ID) | Klasa | Opis |
|----|---------------|-------|------|
| 1  | cfmOven | TileEntityOven | Piekarnik |
| 2  | cfmFridge | TileEntityFridge | Lodowka |
| 3  | cfmCabinet | TileEntityCabinet | Szafka |
| 4  | cfmFreezer | TileEntityFreezer | Zamrazarka |
| 5  | cfmBedsideCabinet | TileEntityBedsideCabinet | Szafka nocna |
| 6  | cfmMailBox | TileEntityMailBox | Skrzynka pocztowa |
| 7  | cfmComputer | TileEntityComputer | Komputer |
| 8  | cfmPrinter | TileEntityPrinter | Drukarka |
| 9  | cfmTV | TileEntityTV | Telewizor |
| 10 | cfmStereo | TileEntityStereo | Stereo |
| 11 | cfmPresent | TileEntityPresent | Prezent |
| 12 | cfmBin | TileEntityBin | Kosz |
| 13 | cfmWallCabinet | TileEntityWallCabinet | Szafka scienna |
| 14 | cfmBath | TileEntityBath | Wanna |
| 15 | cfmBasin | TileEntityBasin | Umywalka |
| 16 | cfmShowerHead | TileEntityShowerHead | Glowka prysznicowa |
| 17 | cfmCookieJar | TileEntityCookieJar | Sloik na ciastka |
| 18 | cfmPlate | TileEntityPlate | Talerz |
| 19 | cfmCouch | TileEntityCouch | Sofa (kolor) |
| 20 | cfmToaster | TileEntityToaster | Toster |
| 21 | cfmChoppingBoard | TileEntityChoppingBoard | Deska do krojenia |
| 22 | cfmBlender | TileEntityBlender | Blender |
| 23 | cfmMicrowave | TileEntityMicrowave | Mikrofalowka |
| 24 | cfmWashingMachine | TileEntityWashingMachine | Pralka |
| 25 | cfmDishwasher | TileEntityDishwasher | Zmywarka |
| 26 | cfmCabinetKitchen | TileEntityCabinetKitchen | Szafka kuchenna |
| 27 | cfmCounterSink | TileEntityCounterSink | Zlew kuchenny |
| 28 | cfmCup | TileEntityCup | Kubek |

**Liczba TE:** 28

### 2.2 Block Entities w 1.18.2

W ModBlockEntities.java:
```
public static final RegistryObject<BlockEntityType<CabinetBlockEntity>> CABINET = register("cabinet", CabinetBlockEntity::new, () -> new Block[]{...});
```

| Lp | Nazwa BE (ID) | Klasa | Obslugiwane bloki |
|----|---------------|-------|-------------------|
| 1  | cfm:cabinet | CabinetBlockEntity | oak_cabinet, spruce_cabinet, ..., stone_cabinet |
| 2  | cfm:bedside_cabinet | BedsideCabinetBlockEntity | oak_bedside_cabinet, ... |
| 3  | cfm:desk_cabinet | DeskCabinetBlockEntity | oak_desk_cabinet, ... |
| 4  | cfm:crate | CrateBlockEntity | oak_crate, ... |
| 5  | cfm:mail_box | MailBoxBlockEntity | oak_mail_box, ... |
| 6  | cfm:trampoline | TrampolineBlockEntity | oak_trampoline, ... |
| 7  | cfm:cooler | CoolerBlockEntity | white_cooler, orange_cooler, ... (16 kolorow) |
| 8  | cfm:grill | GrillBlockEntity | white_grill, ... (16 kolorow) |
| 9  | cfm:door_mat | DoorMatBlockEntity | oak_door_mat, ... |
| 10 | cfm:kitchen_drawer | KitchenDrawerBlockEntity | white_kitchen_drawer, ... (16 kolorow) |
| 11 | cfm:kitchen_sink | KitchenSinkBlockEntity | white_kitchen_sink, ... (16 kolorow) |
| 12 | cfm:fridge | FridgeBlockEntity | fridge_light, fridge_dark |
| 13 | cfm:freezer | FreezerBlockEntity | freezer_light, freezer_dark |

**Liczba BE:** 13

**Kluczowe roznice:**
- W 1.18.2 BE obsluguja wszystkie warianty materialowe jednego typu
- Brak BE w 1.18.2 dla: Oven, Microwave, Computer, Printer, TV, Stereo, WashingMachine, Dishwasher, Bath, Basin, Shower, WallCabinet, Present, Toaster, Blender, Plate, Cup, ChoppingBoard, CookieJar, CounterSink

---

## 3. Szczegolowa analiza Tile Entities – 1.7.10

### 3.1 TileEntityOven (cfmOven)
- Inventory: ISidedInventory, 18 slotow (ItemStack[] ovenItemStacks = new ItemStack[18])
- Mechanika: Wlasny system przepisow Recipes.getOvenRecipeFromInput()
- Czas gotowania: ovenCookTime inkrementowany, currentItemCookTime = 600 ticks
- NBT: Items (lista slotow), BurnTime (czas palenia), CookTime (postep gotowania)

### 3.2 TileEntityFridge (cfmFridge)
- Inventory: IInventory, 16 slotow (fridgeContents[16])
- NBT: fridgeItems (lista slotow z fridgeSlot)

### 3.3 TileEntityCabinet (cfmCabinet)
- Inventory: IInventory, 16 slotow (cabinetContents[16])
- Dzwieki: Otwieranie/zamykanie
- NBT: cabinetItems (lista slotow z cabinetSlot)

### 3.4 TileEntityFreezer (cfmFreezer)
- Inventory: IInventory (kompan dla lodowki)
- Wieloblok: Wymaga fridge bezposrednio nad soba, w przeciwnym razie niszczy sie
- Drops: Wysypuje itemki przy zniszczeniu

### 3.5 TileEntityMicrowave (cfmMicrowave)
- Inventory: ISidedInventory, 1 slot (ItemStack item)
- Mechanika: Szybkie gotowanie – 40 ticks
- NBT: Item (zawartosc), Coooking (boolean), Progress (postep)

### 3.6 TileEntityBlender (cfmBlender)
- Inventory: 4 slotow na skladniki (ingredients[4])
- Mechanika: Mieszanie -> wytwarza 6 napojow, 200 ticks
- NBT: Items, Blending, Progress, DrinkCount, DrinkName, HealAmount, CurrentRed/Green/Blue

### 3.7 TileEntityPrinter (cfmPrinter)
- Inventory: ISidedInventory, 3 sloty (printerItemStacks[3])
- Mechanika: Drukowanie – zuzywa barwnik lub enchanted book jako tusz
- Czas: 1000 ticks (zwykly barwnik) lub 10000 ticks (enchanted book)
- NBT: Items, PrintTime, PrintingTime

### 3.8 TileEntityWashingMachine (cfmWashingMachine)
- Inventory: ISidedInventory, 5 slotow (4 na zbroje + 1 na mydlo)
- Mechanika: Naprawia durability zbroi co 50 ticks (20 w trybie super)
- NBT: Items, Washing, SuperMode, Progress, Remaining

### 3.9 TileEntityDishwasher (cfmDishwasher)
- Inventory: ISidedInventory, 7 slotow (6 na narzedzia + 1 na mydlo)
- Mechanika: Analogiczna do pralki – naprawia narzedzia
- NBT: Items, Washing, SuperMode, Progress, Remaining

### 3.10 TileEntityMailBox (cfmMailBox)
- Inventory: IInventory, 6 slotow (mailBoxContents[6])
- Wlasciciel: UUID ownerUUID, String ownerName
- Blokada: boolean locked
- NBT: mailBoxItems (mailBoxSlot), OwnerUUID, OwnerName, Locked

### 3.11 TileEntityBin (cfmBin)
- Inventory: IInventory, 12 slotow (binContents[12])
- NBT: Items (lista slotow)

### 3.12 TileEntityTV (cfmTV)
- Dane: int channel – numer kanalu TV
- NBT: Channel
- canUpdate() = false

### 3.13 TileEntityStereo (cfmStereo)
- Dane: ItemStack record, int count
- NBT: RecordItem, Record, count

### 3.14 TileEntityComputer (cfmComputer)
- Inventory: IInventory, 1 slot (ItemStack paySlot)
- Dane: int stockNum, boolean isTrading
- NBT: StockNum

### 3.15 TileEntityToaster (cfmToaster)
- Dane: Prosty TE przechowujacy stan opiekania
- NBT: zawiera stan opiekania

### 3.16 TileEntityCounterSink (cfmCounterSink)
- Dane: boolean hasWater / poziom wody
- NBT: zawiera stan wody

### 3.17 TileEntityBasin (cfmBasin)
- Dane: poziom wody
- NBT: zawiera stan wody

### 3.18 TileEntityBath (cfmBath)
- Dane: poziom wody, stan wypelnienia
- NBT: zawiera stan wody

### 3.19 TileEntityCouch (cfmCouch)
- Dane: int colour – kolor sofy (odpowiada kolorom welny)
- NBT: zawiera kolor

### 3.20 Pozostale TE (krotki opis)

| TE | Dane | NBT |
|----|------|-----|
| TileEntityChoppingBoard | Przechowuje noz / skladniki | Items |
| TileEntityPlate | Przechowuje jedzenie na talerzu | Items |
| TileEntityCup | Przechowuje napoj | Items, kolor |
| TileEntityCookieJar | Przechowuje ciastka | Items |
| TileEntityPresent | Przechowuje zawartosc prezentu | Items |
| TileEntityShowerHead | Stan on/off, woda | Stan wody |
| TileEntityWallCabinet | 4-9 slotow (inventory) | Items |

---

## 4. Szczegolowa analiza Block Entities – 1.18.2

### 4.1 BasicLootBlockEntity (bazowa klasa abstrakcyjna)
- Rozszerza: RandomizableContainerBlockEntity, implementuje WorldlyContainer
- Inventory: NonNullList<ItemStack> items
- Otwieranie/zamykanie: ContainerOpenersCounter openersCounter
- NBT: Obsluga przez ContainerHelper.saveAllItems() / loadAllItems()
- Loot tables: Wspiera loot tables (LootTable, LootTableSeed)
- Metody abstrakcyjne: getContainerSize(), getDefaultName(), createMenu()

### 4.2 FridgeBlockEntity (cfm:fridge)
- Rozmiar: 27 slotow (getContainerSize() = 27)
- Menu: MenuType.GENERIC_9x3
- Stan drzwi: onOpen() / onClose() ustawiaja FridgeBlock.OPEN i odtwarzaja dzwiek
- NBT: Standardowe z BasicLootBlockEntity

### 4.3 CabinetBlockEntity (cfm:cabinet)
- Rozmiar: 18 slotow (getContainerSize() = 18)
- Menu: MenuType.GENERIC_9x2
- Stan drzwi: Ustawia CabinetBlock.OPEN
- NBT: Standardowe

### 4.4 FreezerBlockEntity (cfm:freezer)
- Rozmiar: 3 sloty (source, fuel, result)
- Mechanika: Zamrazanie uzywajac recept ModRecipeTypes.FREEZER_SOLIDIFY
- Paliwo: Ice (2000 ticks), Packed Ice (18000), Blue Ice (162000)
- Zmienne: fuelTime, fuelTimeTotal, freezeTime, freezeTimeTotal
- NBT: FreezeTime, FreezeTimeTotal, FuelTime, RecipesUsedSize + RecipeLocation/RecipeAmount

### 4.5 GrillBlockEntity (cfm:grill)
- Inventory: WorldlyContainer
  - fuel – 9 slotow na paliwo
  - grill – 4 sloty na grillowane itemy
- Mechanika: Grillowanie z przerzucaniem (flipped[])
- Zmienne: cookingTimes[4], cookingTotalTimes[4], flipped[4], experience[4], rotations[4]
- Recepty: ModRecipeTypes.GRILL_COOKING
- NBT: Grill, Fuel, RemainingFuel, CookingTimes, CookingTotalTimes, Flipped, Experience, Rotations

### 4.6 MailBoxBlockEntity (cfm:mail_box)
- Rozmiar: 9 slotow
- Rozszerza: BasicLootBlockEntity
- Dane: UUID id, UUID ownerId, String name, String ownerName
- Mechanika: serverTick() pobiera poczte z PostOffice
- NBT: MailBoxUUID, MailBoxName, OwnerName, OwnerUUID

### 4.7 KitchenSinkBlockEntity (cfm:kitchen_sink)
- Rozszerza: FluidHandlerSyncedBlockEntity
- Pojemnosc: FluidAttributes.BUCKET_VOLUME * 10 = 10 000 mB
- NBT: Dane plynu przez FluidTank

### 4.8 TrampolineBlockEntity (cfm:trampoline)
- Dane: int count, DyeColor colour
- Mechanika: updateCount() rekurencyjnie skanuje sasiadow (N/E/S/W) aby zliczyc polaczone trampoliny
- NBT: Count, Color

### 4.9 CoolerBlockEntity (cfm:cooler)
- Rozmiar: 9 slotow
- Menu: MenuType.GENERIC_9x1
- Stan pokrywy: Ustawia CoolerBlock.OPEN
- NBT: Standardowe

### 4.10 DoorMatBlockEntity (cfm:door_mat)
- Dane: String message
- NBT: Message

### 4.11 Pozostale BE (krotki opis)

| BE | Rozmiar | Uwagi |
|----|---------|-------|
| BedsideCabinetBlockEntity | 9 slotow | Analogiczna do Cabinet |
| DeskCabinetBlockEntity | 9 slotow | Analogiczna do Cabinet |
| CrateBlockEntity | 9 slotow | Analogiczna do Cabinet |
| KitchenDrawerBlockEntity | 9 slotow | Analogiczna do Cabinet |

---

## 5. Podsumowanie mapowania blokow 1.7.10 -> 1.18.2

### 5.1 Bezposrednie mapowanie (ten sam lub podobny blok)

| 1.7.10 Block ID | 1.18.2 Block ID | Uwagi |
|-----------------|-----------------|-------|
| tablewood | oak_table / spruce_table / ... | Mapowanie na podstawie metadanych drewna |
| tablestone | stone_table / granite_table / ... | Mapowanie na podstawie metadanych kamienia |
| chairwood | oak_chair / spruce_chair / ... | Jak wyzej |
| chairstone | stone_chair / ... | Jak wyzej |
| coffetablewood | oak_coffee_table / ... | Jak wyzej |
| coffetablestone | stone_coffee_table / ... | Jak wyzej |
| cabinet | oak_cabinet / spruce_cabinet / ... | Mapowanie na podstawie metadanych drewna |
| bedsidecabinet | oak_bedside_cabinet / ... | Jak wyzej |
| fridge | fridge_light / fridge_dark | Do ustalenia mapping jasny/ciemny |
| freezer | freezer_light / freezer_dark | Do ustalenia mapping |
| couch | white_sofa / orange_sofa / ... | Mapowanie metadanych koloru welny -> kolor sofy |
| blinds | oak_blinds / ... | Mapowanie drewna |
| curtains | oak_curtains / ... | Mapowanie drewna |
| mailbox | oak_mail_box / ... | Mapowanie drewna |
| hedge | oak_hedge / ... | Mapowanie typu lisci |
| bin | Brak bezposredniego odpowiednika | Mozna zmapowac na oak_crate lub air |
| stonepath | rock_path | Proste mapowanie |

### 5.2 Bloki wymagajace decyzji (usuniete z 1.18.2)

| 1.7.10 Block ID | Sugerowane mapowanie | Uzasadnienie |
|-----------------|---------------------|--------------|
| oven | air | Brak odpowiednika w 1.18.2 |
| microwave | air | Brak odpowiednika |
| computer | air | Brak odpowiednika |
| printer | air | Brak odpowiednika |
| tv | air | Brak odpowiednika |
| stereo | air | Brak odpowiednika |
| washingmachine | air | Brak odpowiednika |
| dishwasher | air | Brak odpowiednika |
| toilet | air | Brak odpowiednika |
| basin | air | Brak odpowiednika (KitchenSink to osobny blok) |
| bath1 / bath2 | air | Brak odpowiednika |
| showerbottom / showertop | air | Brak odpowiednika |
| showerheadoff / on | air | Brak odpowiednika |
| wallcabinet | oak_cabinet? | Podobna funkcjonalnosc (szafka) |
| birdbath | air | Brak odpowiednika |
| tap | air | Brak odpowiednika |
| electricfence | oak_upgraded_fence? | Podobna funkcja (ogrodzenie) |
| doorbell | air | Brak odpowiednika |
| firealarmoff / on | air | Brak odpowiednika |
| ceilinglightoff / on | air | Brak odpowiednika |
| lampon / lampoff | air | Brak odpowiednika |
| tree | air | Brak odpowiednika |
| present | air | Brak odpowiednika |
| toaster | air | Brak odpowiednika |
| blender | air | Brak odpowiednika |
| plate | air | Brak odpowiednika |
| cup | air | Brak odpowiednika |
| choppingboard | air | Brak odpowiednika |
| barstool | air | Brak odpowiednika |
| cookiejar | air | Brak odpowiednika |
| counterdoored | white_kitchen_counter? | Podobna funkcja (szafka kuchenna) |
| countersink | white_kitchen_sink? | Podobna funkcja (zlew) |
| kitchencabinet | white_kitchen_counter? | Podobna funkcja |
| ovenoverhead | air | Brak odpowiednika |
| whitefence | white_picket_fence? | Podobna funkcja (plot) |
| hey / nyan / pattern / yellowglow / whiteglass | air lub zachowac jako dekoracyjne | Decyzja projektowa |

### 5.3 Mapowanie Tile Entities -> Block Entities

| 1.7.10 TE | 1.18.2 BE | Mapowanie inventory | Uwagi |
|-----------|-----------|---------------------|-------|
| cfmCabinet | cfm:cabinet | 16 -> 18 slotow | Bezposrednie mapowanie |
| cfmFridge | cfm:fridge | 16 -> 27 slotow | Bezposrednie mapowanie |
| cfmFreezer | cfm:freezer | Brak inventory -> 3 sloty | Zmiana architektury |
| cfmBedsideCabinet | cfm:bedside_cabinet | 16 -> 9 slotow | Bezposrednie mapowanie |
| cfmMailBox | cfm:mail_box | 6 -> 9 slotow | Dodatkowo UUID wlasciciela |
| cfmCounterSink | cfm:kitchen_sink | Woda -> FluidTank | Zmiana systemu plynow |
| cfmBin | cfm:crate? | 12 -> 9 slotow | Sugerowane mapowanie |
| cfmWallCabinet | cfm:cabinet? | ~4-9 -> 18 slotow | Sugerowane mapowanie |
| cfmCouch | (brak BE) | kolor -> metadata blockstate | Kolor w blockstate, nie BE |
| cfmOven | (brak BE) | 18 slotow -> utrata | Brak odpowiednika |
| cfmMicrowave | (brak BE) | 1 slot -> utrata | Brak odpowiednika |
| cfmComputer | (brak BE) | 1 slot -> utrata | Brak odpowiednika |
| cfmPrinter | (brak BE) | 3 sloty -> utrata | Brak odpowiednika |
| cfmTV | (brak BE) | channel -> utrata | Brak odpowiednika |
| cfmStereo | (brak BE) | record -> utrata | Brak odpowiednika |
| cfmWashingMachine | (brak BE) | 5 slotow -> utrata | Brak odpowiednika |
| cfmDishwasher | (brak BE) | 7 slotow -> utrata | Brak odpowiednika |
| cfmBlender | (brak BE) | 4 sloty -> utrata | Brak odpowiednika |
| cfmPlate | (brak BE) | itemy -> utrata | Brak odpowiednika |
| cfmCup | (brak BE) | itemy -> utrata | Brak odpowiednika |
| cfmChoppingBoard | (brak BE) | itemy -> utrata | Brak odpowiednika |
| cfmCookieJar | (brak BE) | itemy -> utrata | Brak odpowiednika |
| cfmPresent | (brak BE) | itemy -> utrata | Brak odpowiednika |
| cfmBath | (brak BE) | woda -> utrata | Brak odpowiednika |
| cfmBasin | (brak BE) | woda -> utrata | Brak odpowiednika |
| cfmShowerHead | (brak BE) | woda -> utrata | Brak odpowiednika |
| cfmToaster | (brak BE) | stan -> utrata | Brak odpowiednika |
| cfmCabinetKitchen | cfm:kitchen_drawer? | 16 slotow -> 9 slotow | Sugerowane mapowanie |

---

## 6. NBT – kluczowe tagi do konwersji

### 6.1 Tagi w 1.7.10 (Tile Entities)

| TE | Kluczowe tagi NBT | Opis |
|----|-------------------|------|
| cfmOven | Items, BurnTime, CookTime | Inventory + stan gotowania |
| cfmFridge | fridgeItems | Inventory (16 slotow) |
| cfmCabinet | cabinetItems | Inventory (16 slotow) |
| cfmFreezer | (brak unikalnych tagow) | Zalezny od lodowki |
| cfmBedsideCabinet | (podobne do Cabinet) | Inventory |
| cfmMailBox | mailBoxItems, OwnerUUID, OwnerName, Locked | Inventory + wlasciciel |
| cfmComputer | StockNum | Stan handlu |
| cfmPrinter | Items, PrintTime, PrintingTime | Inventory + drukowanie |
| cfmTV | Channel | Kanal TV |
| cfmStereo | RecordItem, Record, count | Plyta |
| cfmMicrowave | Item, Coooking, Progress | Item + stan |
| cfmBlender | Items, Blending, Progress, DrinkCount, DrinkName, HealAmount, CurrentRed/Green/Blue | Skomplikowany stan |
| cfmWashingMachine | Items, Washing, SuperMode, Progress, Remaining | Zbroja + mydlo |
| cfmDishwasher | Items, Washing, SuperMode, Progress, Remaining | Narzedzia + mydlo |
| cfmBin | Items | Inventory (12 slotow) |
| cfmCouch | Colour | Kolor sofy |
| cfmToaster | (stan opiekania) | Boolean/progress |
| cfmCounterSink | (stan wody) | Boolean |
| cfmBasin | (stan wody) | Boolean/poziom |
| cfmBath | (stan wody) | Boolean/poziom |
| cfmPlate | Items | Jedzenie |
| cfmCup | Items, (kolor) | Napoj |
| cfmChoppingBoard | Items | Noz/skladniki |
| cfmCookieJar | Items | Ciastka |
| cfmPresent | Items | Prezent |
| cfmShowerHead | (stan wody) | Boolean |
| cfmWallCabinet | Items | Inventory |

### 6.2 Tagi w 1.18.2 (Block Entities)

| BE | Kluczowe tagi NBT | Opis |
|----|-------------------|------|
| cfm:cabinet | Items (ContainerHelper) | Inventory (18 slotow) |
| cfm:fridge | Items | Inventory (27 slotow) |
| cfm:freezer | Items, FreezeTime, FreezeTimeTotal, FuelTime, RecipesUsed | 3 sloty + zamrazanie |
| cfm:bedside_cabinet | Items | Inventory (9 slotow) |
| cfm:desk_cabinet | Items | Inventory (9 slotow) |
| cfm:crate | Items | Inventory (9 slotow) |
| cfm:mail_box | Items, MailBoxUUID, MailBoxName, OwnerName, OwnerUUID | 9 slotow + wlasciciel |
| cfm:trampoline | Count, Color | Liczba polaczonych + kolor |
| cfm:cooler | Items | Inventory (9 slotow) |
| cfm:grill | Grill, Fuel, RemainingFuel, CookingTimes, CookingTotalTimes, Flipped, Experience, Rotations | 4+9 slotow + grillowanie |
| cfm:door_mat | Message | Wiadomosc |
| cfm:kitchen_sink | Tank (FluidTank) | Plyn (10 000 mB) |
| cfm:kitchen_drawer | Items | Inventory (9 slotow) |

### 6.3 Kluczowe roznice w NBT

1. **Inventory format:**
   - 1.7.10: Wlasne nazwy list (fridgeItems, cabinetItems) z custom slot tagami (fridgeSlot, cabinetSlot)
   - 1.18.2: Standardowy Items list z Slot tagami (Minecraft standard)

2. **UUID:**
   - 1.7.10: OwnerUUID jako string
   - 1.18.2: OwnerUUID jako int-array (Minecraft 1.16+ standard)

3. **Plyny:**
   - 1.7.10: Prosty boolean / poziom wody
   - 1.18.2: FluidTank z pelnym NBT plynu (FluidName, Amount)

4. **Kolor:**
   - 1.7.10: int colour (0-15)
   - 1.18.2: String Color (nazwa koloru) lub DyeColor enum

---

## 7. Wnioski i rekomendacje dla konwersji

### 7.1 Prosta konwersja (direct mapping)

1. Bloki dekoracyjne: Table, Chair, CoffeeTable, Cabinet, BedsideCabinet, Blinds, Curtains, Hedge, MailBox
   - Wymagana konwersja metadanych drewna/kamienia/koloru na odpowiedni block ID w 1.18.2
   - Wiele blokow z 1.7.10 nie ma metadanych (np. tablewood to tylko oak), wiec domyslne mapowanie na oak_table

2. Fridge + Freezer:
   - 1.7.10: Fridge (gora) + Freezer (dol) tworza wieloblok
   - 1.18.2: Fridge (gora) + Freezer (dol) rowniez tworza wieloblok, ale z osobnymi BE
   - BE Fridge: 16 -> 27 slotow (dodatkowe 11 slotow = puste)
   - BE Freezer: nowy format 3-slotowy (source/fuel/result) – inventory z 1.7.10 Freezer nalezy wyslac do Fridge lub zrzucic na ziemie

3. MailBox:
   - Inventory: 6 -> 9 slotow
   - UUID wlasciciela: string -> int-array
   - Dodatkowe pola w 1.18.2: MailBoxUUID, MailBoxName – wygenerowac nowe UUID i nazwe z OwnerName

### 7.2 Konwersja z utrata danych

Dla blokow usunietych z 1.18.2 nalezy podjac decyzje:

1. Inventory items (Oven, Microwave, Computer, Printer, TV, Stereo, WashingMachine, Dishwasher, Blender, Plate, Cup, ChoppingBoard, CookieJar, Present, WallCabinet, Bin):
   - Opcja A: Zrzucic itemy na ziemie przy konwersji (drop items)
   - Opcja B: Zmapowac na najblizszy odpowiednik (np. Bin -> Crate) i przeniesc itemy
   - Opcja C: Calkowita utrata (items znikaja)

2. Dane niematerialne (TV channel, Stereo record, Couch colour, Computer stockNum, Printer state, etc.):
   - Te dane nie maja odpowiednika w 1.18.2 i zostana utracone

3. Plyny (Basin, Bath, Shower, CounterSink):
   - 1.7.10: Prosty boolean/poziom
   - 1.18.2: Tylko KitchenSink ma BE z FluidTank
   - Decyzja: Zmapowac CounterSink na KitchenSink i przeniesc stan wody?

### 7.3 Decyzje do podjecia przez wlasciciela projektu

1. Czy mapowac bin na crate czy zostawic air?
2. Czy mapowac countersink na kitchen_sink?
3. Czy mapowac wallcabinet na cabinet?
4. Czy mapowac counterdoored / kitchencabinet na kitchen_counter / kitchen_drawer?
5. Co zrobic z itemkami z usunietych blokow (Oven, Microwave, itp.) – drop czy utrata?
6. Czy zachowac dekoracyjne bloki (hey, nyan, pattern, yellowglow, whiteglass) czy zamienic na air?
7. Czy mapowac whitefence na white_picket_fence?
8. Czy mapowac electricfence na oak_upgraded_fence?

### 7.4 Kolejne kroki

1. [Zadanie 2] Zbudowac tabele mappingu blockstate (1.7.10 metadata -> 1.18.2 block ID) dla blokow dekoracyjnych
2. [Zadanie 3] Zaimplementowac konwerter inventory (NBT format 1.7.10 -> 1.18.2)
3. [Zadanie 4] Obsluga wieloblokow (Fridge/Freezer, Bath, Shower)
4. [Zadanie 5] Testowa konwersja malego fragmentu mapy i weryfikacja w swiecie 1.18.2

---

Raport wygenerowany automatycznie na podstawie analizy kodu zrodlowego MrCrayfish Furniture Mod 1.7.10 i 1.18.2.
