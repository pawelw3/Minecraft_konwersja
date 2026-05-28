# Witchery 1.7.10 – Bloki i TileEntities

## Informacje ogólne

| | |
|--|--|
| **Mod ID** | `witchery` |
| **Wersja** | 0.24.1 |
| **Autor** | Emoniph |
| **Port na 1.18.2** | **NIE** – brak w `headless_server/1.18.2/mods/` |
| **Planowany zamiennik** | Hexerei / Enchanted: Witchcraft (wg docs/archive) |
| **Strategia konwersji** | Placeholdery (`conversion_placeholders:block_entity_placeholder`) |

---

## Mechanizm rejestracji TileEntity w 1.7.10

Większość bloków Witchery rozszerza `BlockBaseContainer`. Metoda `func_149663_c(blockName)` wywołuje:

```java
GameRegistry.registerTileEntity(this.clazzTile, blockName);
```

**TE ID zapisywany w NBT** to ostatnia nazwa, z jaką dana klasa TE była zarejestrowana
(pole `classToStringMap` w `TileEntity`). W przypadku klas współdzielonych przez wiele bloków
(np. `TileEntityFetish`) aktualny TE ID może być inny niż nazwa pierwszego bloku.

Wyjątki od reguły domyślnej rejestracji:
- `BlockWitchesOven` – tylko `!burning` rejestruje TE (blok palący = ta sama klasa, ale bez własnego wpisu)
- `BlockDistillery` – tylko `!burning`
- `BlockFumeFunnel` – tylko `!filtered`
- `BlockRefillingChest` – rejestruje TE ręcznie (bezpośrednie wywołanie `GameRegistry`)

---

## Grupy bloków

### Grupa 1: Bloki FUNKCJONALNE z bogatym NBT

Bloki z inwentarzem, stanem przetwarzania lub zapisem gracza.
Wszystkie będą placeholderami z pełnym zachowaniem oryginalnego NBT.

| TE ID (NBT `id`) | Klasa TE | Klucz bloku w 1.7.10 | Opis | Kluczowe pola NBT |
|---|---|---|---|---|
| `witchery:altar` | `TileEntityAltar` | `witchery:altar` | Ołtarz Natury – centrum mocy | `Core` (Coord), `Power` (float), `MaxPower` (float), `PowerScale` (int), `RechargeScale` (int), `RangeScale` (int) |
| `witchery:kettle` | `TileEntityKettle` | `witchery:kettle` | Kocioł warzący napoje | `Items` (8 slotów), `Tank` (FluidTank), `Ruined` (bool), `Powered` (bool), `LiquidColor` (int) |
| `witchery:cauldron` | `TileEntityCauldron` | `witchery:cauldron` | Kocioł rytuałów (brewing) | `Items`, `Fluid` (FluidTank 3000mb), `brewData` (NBTTagCompound), `boiling` (bool), `power` (int) |
| `witchery:spinningwheel` | `TileEntitySpinningWheel` | `witchery:spinningwheel` | Kołowrotek | `Items` (5 slotów), `CookTime` (short), `PowerLevel` (short) |
| `witchery:witchesovenidle` | `TileEntityWitchesOven` | `witchery:witchesovenidle` | Piec czarownicy (obydwa stany bloku) | `Items` (5 slotów), `BurnTime` (short), `CookTime` (short), `CurrentItemBurnTime` (short) |
| `witchery:distilleryidle` | `TileEntityDistillery` | `witchery:distilleryidle` | Destylator (obydwa stany bloku) | `Items` (7 slotów), `CookTime` (short) |
| `witchery:poppetshelf` | `TileEntityPoppetShelf` | `witchery:poppetshelf` | Półka na lalki voodoo | `contents` (9 itemstacków), `customName` (opcjonalnie) |
| `witchery:leechchest` | `TileEntityLeechChest` | `witchery:leechchest` | Skrzynia pijawki (usuwa przedmioty) | Pola z `TileEntityChest` (27 slotów) |
| `witchery:refillingchest` | `TileEntityRefillingChest` | `witchery:refillingchest` | Samouzupełniająca się skrzynia | `WITCLifeTicks` (long) |
| `witchery:silvervat` | `TileEntitySilverVat` | `witchery:silvervat` | Wanna srebrna | `Items` (1 slot), `sides` (int[6]) |
| `witchery:brazier` | `TileEntityBrazier` | `witchery:brazier` | Palenisko rytualne | `Items` (do 9 slotów), `isBurning` (bool), `burnTime` (int) |
| `witchery:bloodcrucible` | `TileEntityBloodCrucible` | `witchery:bloodcrucible` | Kocioł krwi | `bloodLevel` (int 0–20) |

### Grupa 2: Bloki SPECJALNE z nietrywialnym NBT

Bloki z danymi gracza/właściciela lub stanem portalu.

| TE ID (NBT `id`) | Klasa TE | Klucz bloku w 1.7.10 | Opis | Kluczowe pola NBT |
|---|---|---|---|---|
| `witchery:mirrorblock` | `TileEntityMirror` | `witchery:mirrorblock` | Lustro (zniszczalne) | `owner` (UUID/String), `name` (String), `trapped` (bool) |
| `witchery:mirrorblock2` | `TileEntityMirror` | `witchery:mirrorblock2` | Lustro (niezniszczalne) | j.w. |
| `witchery:dreamcatcher` | `TileEntityDreamCatcher` | `witchery:dreamcatcher` | Łapacz snów | `uuid` (String), współrzędne snu |
| `witchery:crystalball` | `TileEntityCrystalBall` | `witchery:crystalball` | Kula kryształowa | `ready` (bool), `rechargeTime` (int) |
| `witchery:coffinblock` | `TileEntityCoffin` | `witchery:coffinblock` | Trumna (2 bloki wysokości) | `open` (bool), stan łóżka |
| `witchery:decurseteleport` | `TileEntityAreaTeleportPullProtect` | `witchery:decurseteleport` | Marker ochrony obszaru (teleport) | `owner` (UUID/String), `Rites` (NBTTagList) |
| `witchery:decursedirected` | `TileEntityAreaCurseProtect` | `witchery:decursedirected` | Marker ochrony obszaru (ochrona) | j.w. |
| `witchery:placeditem` | `TileEntityPlacedItem` | `witchery:placeditem` | Postawiony przedmiot | `Item` (NBTTagCompound – cały ItemStack) |
| `witchery:spiritportal` | `TileEntitySpiritPortal` | `witchery:spiritportal` | Portal spirytualny | stan portalu |

### Grupa 3: Bloki DEKORACYJNE / minimalne TE

Bloki z TileEntity służącym głównie do synchronizacji client-server
lub z minimalnym/pustym NBT.

| TE ID (NBT `id`) | Klasa TE | Klucz bloku w 1.7.10 | Opis |
|---|---|---|---|
| `witchery:fumefunnel` | `TileEntityFumeFunnel` | `witchery:fumefunnel` | Rura dymowa (obydwa stany) |
| `witchery:scarecrow` | `TileEntityFetish` | `witchery:scarecrow` | Strach na wróble |
| `witchery:trent` | `TileEntityFetish` | `witchery:trent` | Bożek Treanta |
| `witchery:witchsladder` | `TileEntityFetish` | `witchery:witchsladder` | Drabina czarownic |
| `witchery:wolfaltar` | `TileEntityStatueWerewolf` | `witchery:wolfaltar` | Ołtarz Wilkołaka |
| `witchery:statueofworship` | `TileEntityStatueOfWorship` | `witchery:statueofworship` | Posąg Bogini |
| `witchery:statuegoddess` | `TileEntityStatueGoddess` | `witchery:statuegoddess` | Posąg Bogini (typ 2) |
| `witchery:alluringskull` | `TileEntityAlluringSkull` | `witchery:alluringskull` | Kuszący trup |
| `witchery:candelabra` | `TileEntityCandelabra` | `witchery:candelabra` | Kandelabr |
| `witchery:chalice` | `witchery:chalice` | `witchery:chalice` | Kielich |
| `witchery:wolfhead` | `TileEntityWolfHead` | `witchery:wolfhead` | Głowa wilka |
| `witchery:glowglobe` | `TileEntityGlowGlobe` | `witchery:glowglobe` | Świecąca kula |
| `witchery:circle` | `TileEntityCircle` | `witchery:circle` | Okrąg rytualny (glyph) |
| `witchery:beartrap` | `TileEntityBeartrap` | `witchery:beartrap` | Pułapka na niedźwiedzia |
| `witchery:wolftrap` | `TileEntityBeartrap` | `witchery:wolftrap` | Pułapka na wilka |
| `witchery:garlicgarland` | `TileEntityGarlicGarland` | `witchery:garlicgarland` | Wieniec czosnkowy |
| `witchery:voidbramble` | `TileEntityVoidBramble` | `witchery:voidbramble` | Jeżyna pustki |
| `witchery:grassper` | `TileEntityGrassper` | `witchery:grassper` | Łapiąca trawa |
| `witchery:bloodrose` | `TileEntityBloodRose` | `witchery:bloodrose` | Różyczka krwi |
| `witchery:barrier` | `TileEntityBarrier` | `witchery:barrier` | Bariera magiczna |
| `witchery:light` | `TileEntityLight` | `witchery:light` | Źródło światła |

### Grupa 4: Bloki REDSTONE / mechaniczne (Cursed)

Zmodyfikowane bloki redstone – wszystkie będą placeholderami.

| TE ID (NBT `id`) | Klucz bloku | Opis |
|---|---|---|
| `witchery:clever` | `witchery:clever` | Przeklęta dźwignia |
| `witchery:cwoodendoor` | `witchery:cwoodendoor` | Przeklęte drewniane drzwi |
| `witchery:cwoodpressureplate` | `witchery:cwoodpressureplate` | Przeklęta płyta drewniana |
| `witchery:cstonepressureplate` | `witchery:cstonepressureplate` | Przeklęta płyta kamienna |
| `witchery:csnowpressureplate` | `witchery:csnowpressureplate` | Przeklęta płyta śnieżna |
| `witchery:cbuttonwood` | `witchery:cbuttonwood` | Przeklęty przycisk drewniany |
| `witchery:cbuttonstone` | `witchery:cbuttonstone` | Przeklęty przycisk kamienny |

### Grupa 5: Bloki PŁYNNE (Brew fluids)

| TE ID (NBT `id`) | Klucz bloku | Opis |
|---|---|---|
| `witchery:brewgas` | `witchery:brewgas` | Gaz naparu |
| `witchery:brewliquid` | `witchery:brewliquid` | Ciekły napar |
| `witchery:slurp` | `witchery:slurp` | Blok bariery cieczy |

---

## Bloki BEZ TileEntity

Bloki Witchery, które NIE mają TileEntity (czyli nie pojawiają się w NBT jako TE):

| Klucz bloku | Opis |
|---|---|
| `witchery:belladonna` | Uprawa belladonny |
| `witchery:mandrake` | Uprawa mandragory |
| `witchery:artichoke` | Uprawa karczocha |
| `witchery:snowbell` | Uprawa śnieżnego dzwonka |
| `witchery:wormwood` | Uprawa piołunu |
| `witchery:mindrake` | Uprawa mindragory |
| `witchery:wolfsbane` | Uprawa tojadu |
| `witchery:garlicplant` | Uprawa czosnku |
| `witchery:witchsapling` | Sadzonka wiedźmiego drzewa |
| `witchery:witchlog` | Kłoda wiedźmiego drzewa |
| `witchery:witchleaves` | Liście wiedźmiego drzewa |
| `witchery:bramble` | Jeżyna |
| `witchery:glintweed` | Mieniąca się trawa |
| `witchery:spanishmoss` | Mech hiszpański |
| `witchery:leapinglily` | Skacząca lilia wodna |
| `witchery:plantmine` | Roślinna mina |
| `witchery:embermoss` | Ognisty mech |
| `witchery:crittersnare` | Sidło na stworzenia |
| `witchery:bloodedwool` | Zakrwawiona wełna |
| `witchery:shadedglass` | Zacieniające szkło |
| `witchery:shadedglass_active` | Zacieniające szkło (aktywne) |
| `witchery:perpetualice` | Wieczny lód i warianty |
| `witchery:planks` | Deski (3 typy drewna) |
| `witchery:stairswoodrowan` i warianty | Schody |
| `witchery:witchwoodslab` | Półblok |
| `witchery:rowanwooddoor` | Drzwi dębowe |
| `witchery:alderwooddoor` | Drzwi olchowe |
| `witchery:wicker_block` | Wiklinowy blok |
| `witchery:stockade` | Palisada |
| `witchery:icestockade` | Lodowa palisada |
| `witchery:mirrorwall` | Ściana lustrzana (dekoracyjna) |
| `witchery:daylightcollector` | Kolektor światła dziennego |
| `witchery:force` | Blok siły |
| `witchery:tormentstone` | Kamień udręki |
| `witchery:pitdirt` | Ziemia dołu |
| `witchery:pitgrass` | Trawa dołu |
| `witchery:demon_heart` | Serce demona |
| `witchery:infinityegg` | Jajo nieskończoności |
| `witchery:circleglyphritual` i warianty | Glify rytualne |
| `witchery:spiritflowing` / `witchery:hollowtears` | Płyny spirytualne |
| `witchery:disease` / `witchery:brew` | Płyn choroba/napar |
| `witchery:wallgen` | Generator murów wiosek |

---

## Strategia konwersji

### Decyzja: Czyste placeholdery

Witchery nie ma portu na 1.18.2. Cały mod będzie konwertowany do
`conversion_placeholders:block_entity_placeholder` z zachowaniem oryginalnego NBT.

Jest to ta sama strategia co dla Open Modular Turrets.

### TE IDs do rozpoznania w `detect_mod()`

```python
_WITCHERY_TE_PREFIXES = ("witchery:",)
```

Wszystkie TE IDs Witchery mają prefiks `witchery:`, co czyni detekcję prostą.

### Priorytety

| Priorytet | Blok | Uzasadnienie |
|---|---|---|
| 1 | Altar, Kettle, Cauldron | Centrum progresji – gracze tu inwestują czas |
| 1 | SpinningWheel, WitchesOven, Distillery | Maszyny z itemami do uratowania |
| 2 | PoppetShelf, PlacedItem | Unikalne przedmioty mogą być w środku |
| 2 | Mirror, DreamCatcher | Stan powiązany z graczem |
| 3 | Dekoracyjne, Redstone | Minimalne NBT, mała strata |

---

## Liczby podsumowujące

| Kategoria | Liczba |
|---|---|
| TileEntities z bogatym NBT (Grupa 1) | 12 |
| TileEntities specjalne (Grupa 2) | 9 |
| TileEntities dekoracyjne/minimalne (Grupa 3) | 21 |
| TileEntities Redstone cursed (Grupa 4) | 7 |
| TileEntities płynne (Grupa 5) | 3 |
| **Łączna liczba TE IDs** | **~52** |
| Bloki bez TileEntity | ~35 |

---

*Analiza na podstawie zdekompilowanego kodu Witchery 0.24.1 (`WitcheryBlocks.java`, `BlockBaseContainer.java`, pliki poszczególnych bloków)*
